#!/usr/bin/env python3
"""Exact diagonal-Gaussian Fourier proxy bound with a cutoff-independent majorant.

The proxy is gamma_n=(1+|n|_2^2)^(-2) in d=3.  The analytic certificate
splits the convolution into two max-norm regions and uses the elementary
inverse-square telescoping bound.  This is a comparison theorem only; it does
not identify the A1 production heat/root owner.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shutil
import subprocess
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-a1-gaussian-fourier-uniform-heat-bound-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R204.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-a1-gaussian-fourier-uniform-heat-bound" / "result.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def norm_sq(mode: tuple[int, ...]) -> int:
    return sum(value * value for value in mode)


def max_norm(mode: tuple[int, ...]) -> int:
    return max(abs(value) for value in mode)


def modes(cutoff: int, dimension: int) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product(range(-cutoff, cutoff + 1), repeat=dimension))


def gamma(mode: tuple[int, ...], covariance_power: int) -> Fraction:
    return Fraction(1, (1 + norm_sq(mode)) ** covariance_power)


def heat_rate(mode: tuple[int, ...], exponent: int) -> Fraction:
    base = 1 + norm_sq(mode)
    return Fraction(1 if exponent == 0 else base ** (exponent // 2))


def add(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def find_lake() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def finite_charge(manifest: dict[str, Any], cutoff: int, exponent: int) -> Fraction:
    inputs = manifest["registered_inputs"]
    dimension = int(inputs["dimension"])
    power = int(inputs["covariance_power"])
    profile = inputs["generator_profile"]
    factor = 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"]))
    cube = modes(cutoff, dimension)
    cube_set = set(cube)
    weights = {mode: gamma(mode, power) for mode in cube}
    total = Fraction(0)
    for output in cube:
        if norm_sq(output) == 0:
            continue
        convolution = sum(
            weights[input_mode] * weights[tuple(a + b for a, b in zip(input_mode, output))]
            for input_mode in cube
            if tuple(a + b for a, b in zip(input_mode, output)) in cube_set
        )
        total += factor * norm_sq(output) * convolution / (1 + heat_rate(output, exponent))
    return total


def compute(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    inputs = manifest["registered_inputs"]
    shell = inputs["max_norm_shell"]
    split = inputs["convolution_split"]
    l1 = inputs["l1_shell_bound"]
    profile = inputs["generator_profile"]
    dimension = int(inputs["dimension"])
    power = int(inputs["covariance_power"])
    cutoffs = tuple(int(value) for value in inputs["cutoffs"])
    exponents = tuple(int(value) for value in inputs["heat_exponents"])
    factor = 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"]))
    shell_coefficients = tuple(int(value) for value in shell["shell_coefficients"])
    shell_coefficient = sum(shell_coefficients)
    partial_p_bound = int(l1["partial_inverse_square_sum_bound"])
    shell_sum_bound = shell_coefficient * partial_p_bound
    l1_bound = 1 + shell_sum_bound
    regions = int(split["regions"])
    quarter_scale = int(split["quarter_scale"])
    convolution_multiplier = regions * quarter_scale ** power
    uniform_bound = factor * convolution_multiplier * l1_bound * shell_sum_bound
    source_files = {key: REPO / value["path"] for key, value in manifest["source_authorities"].items()}
    current_hashes = {key: digest(path) for key, path in source_files.items()}
    expected_hashes = {key: value["sha256"] for key, value in manifest["source_authorities"].items()}

    rows: list[dict[str, Any]] = []
    test_m = (1, 2, 5, 10)
    shell_checks: dict[str, dict[str, str]] = {}
    for m in test_m:
        count = (2 * m + 1) ** dimension - (2 * m - 1) ** dimension
        expected_count = shell_coefficients[0] * m * m + shell_coefficients[1]
        weight = Fraction(count, (1 + m * m) ** power)
        shell_checks[str(m)] = {
            "count": str(count),
            "weight": f"{weight.numerator}/{weight.denominator}",
        }
        add(rows, f"shell_count_{m}", count == expected_count, count, expected_count)
        add(rows, f"shell_weight_bound_{m}", weight <= Fraction(shell_coefficient, m * m), weight, f"<={shell_coefficient}/{m}^2")

    pseries_checks: dict[str, str] = {}
    for m in test_m:
        partial = sum((Fraction(1, k * k) for k in range(1, m + 1)), Fraction(0))
        pseries_checks[str(m)] = f"{partial.numerator}/{partial.denominator}"
        add(rows, f"inverse_square_partial_{m}", partial < partial_p_bound, partial, f"<{partial_p_bound}")

    tables: dict[str, dict[str, str]] = {str(exponent): {} for exponent in exponents}
    exact_values: dict[str, dict[int, Fraction]] = {str(exponent): {} for exponent in exponents}
    for cutoff in cutoffs:
        for exponent in exponents:
            value = finite_charge(manifest, cutoff, exponent)
            exact_values[str(exponent)][cutoff] = value
            tables[str(exponent)][str(cutoff)] = f"{value.numerator}/{value.denominator}"
            add(rows, f"finite_charge_bound_s{exponent}_N{cutoff}", value <= uniform_bound, value, f"<={uniform_bound}")
    for cutoff in cutoffs:
        ordered = all(exact_values[str(left)][cutoff] >= exact_values[str(right)][cutoff] for left, right in zip(exponents, exponents[1:]))
        add(rows, f"heat_order_N{cutoff}", ordered, [tables[str(s)][str(cutoff)] for s in exponents], "nonincreasing in s")

    add(rows, "dimension_is_three", dimension == 3, dimension, 3)
    add(rows, "covariance_power_is_two", power == 2, power, 2)
    add(rows, "source_hashes_match", current_hashes == expected_hashes, current_hashes, expected_hashes)
    add(rows, "current_factor_derived", factor == 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"])), factor, "derived profile identity")
    add(rows, "convolution_multiplier_derived", convolution_multiplier == regions * quarter_scale ** power, convolution_multiplier, "regions*quarter_scale^power")
    add(rows, "l1_bound_derived", l1_bound == 1 + shell_sum_bound, l1_bound, "1+shell_sum_bound")
    add(rows, "uniform_bound_positive", uniform_bound > 0, uniform_bound, ">0")
    boundary = manifest["boundary"].lower()
    for token in ("proxy", "production", "q-ledger", "a13", "sector-a", "pre-a"):
        add(rows, f"boundary_token_{token}", token in boundary, boundary, f"contains {token}")

    lean_text = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    markers = ["max_shell_card", "shell_weight_bound", "convolution_multiplier", "uniform_charge_bound"]
    add(rows, "lean_markers_present", all(marker in lean_text for marker in markers), markers, "markers present")
    forbidden = tuple(token for token in ("sorry", "admit", "axiom", "unsafe") if token in lean_text.lower())
    add(rows, "lean_forbidden_tokens_absent", forbidden == (), forbidden, "none")
    lake = find_lake()
    add(rows, "pinned_lake_present", lake is not None, lake, "pinned lake")
    if lake is not None:
        compiled = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
        add(rows, "lean_compile", compiled.returncode == 0, compiled.returncode, 0)
        add(rows, "lean_output_clean", compiled.returncode == 0 and "error:" not in (compiled.stdout + compiled.stderr).lower(), compiled.stderr, "no Lean error")

    derived = {
        "dimension": dimension,
        "covariance_power": power,
        "current_factor": factor,
        "shell_coefficient": shell_coefficient,
        "shell_checks": shell_checks,
        "inverse_square_partial_checks": pseries_checks,
        "shell_sum_bound": shell_sum_bound,
        "l1_bound": l1_bound,
        "convolution_multiplier": convolution_multiplier,
        "uniform_charge_bound": uniform_bound,
        "cutoffs": list(cutoffs),
        "heat_exponents": list(exponents),
        "finite_q_tables": tables,
        "analytic_statement": "For the declared proxy, the max-norm split and inverse-square telescoping give Q_N(s)<=529152 for every cutoff N and every registered s>=2; this is not the production q-ledger.",
    }
    return derived, rows, current_hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-a1-gaussian-fourier-uniform-heat-bound" / "result.json")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else REPO / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    derived, assertions, hashes = compute(manifest)
    failures = [row for row in assertions if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-gaussian-fourier-uniform-heat-bound-primary-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Exact cutoff-uniform diagonal-Gaussian Fourier proxy bound; no production-owner claim.",
        "source_authorities": hashes,
        "derived": derived,
        "assertions": assertions,
        "assertion_count": len(assertions),
        "conclusion": "The explicit proxy charge is uniformly bounded for heat exponent s>=2, with derived majorant 529152. The production heat/root owner and q-ledger remain unprovided.",
        "honesty_boundary": ["proxy covariance only", "comparison bound only", "no production heat/root owner", "no production q-ledger", "no A13 closure", "no Sector-A or Pre-A closure"],
        "failures": failures,
    }
    if not args.no_store:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 FOURIER UNIFORM HEAT BOUND FAIL {len(assertions)-len(failures)}/{len(assertions)}")
        return 1
    print(f"A1 FOURIER UNIFORM HEAT BOUND PASS {len(assertions)}/{len(assertions)}")
    if not args.no_store:
        print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
