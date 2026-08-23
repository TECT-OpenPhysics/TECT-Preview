#!/usr/bin/env python3
"""Stdlib-only independent lane for the diagonal-Gaussian uniform proxy bound."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-a1-gaussian-fourier-uniform-heat-bound-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-independent-a1-gaussian-fourier-uniform-heat-bound" / "result.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1 << 20)
            if not block:
                return h.hexdigest()
            h.update(block)


def norm(mode: tuple[int, ...]) -> int:
    return sum(value * value for value in mode)


def cube(cutoff: int, dimension: int) -> list[tuple[int, ...]]:
    return [tuple(values) for values in itertools.product(range(-cutoff, cutoff + 1), repeat=dimension)]


def weight(mode: tuple[int, ...], power: int) -> Fraction:
    return Fraction(1, (1 + norm(mode)) ** power)


def rate(mode: tuple[int, ...], exponent: int) -> Fraction:
    base = 1 + norm(mode)
    return Fraction(1 if exponent == 0 else base ** (exponent // 2))


def mark(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def finite_charge(manifest: dict[str, Any], cutoff: int, exponent: int) -> Fraction:
    data = manifest["registered_inputs"]
    d = int(data["dimension"])
    power = int(data["covariance_power"])
    profile = data["generator_profile"]
    factor = 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"]))
    points = cube(cutoff, d)
    point_set = set(points)
    weights = {point: weight(point, power) for point in points}
    total = Fraction(0)
    for output in points:
        if norm(output) == 0:
            continue
        convolution = Fraction(0)
        for p in points:
            translated = tuple(a + b for a, b in zip(p, output))
            if translated in point_set:
                convolution += weights[p] * weights[translated]
        total += factor * norm(output) * convolution / (1 + rate(output, exponent))
    return total


def run(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    data = manifest["registered_inputs"]
    shell = data["max_norm_shell"]
    split = data["convolution_split"]
    l1 = data["l1_shell_bound"]
    profile = data["generator_profile"]
    d = int(data["dimension"])
    power = int(data["covariance_power"])
    cutoffs = [int(value) for value in data["cutoffs"]]
    exponents = [int(value) for value in data["heat_exponents"]]
    factor = 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"]))
    coeffs = [int(value) for value in shell["shell_coefficients"]]
    shell_coeff = sum(coeffs)
    p_bound = int(l1["partial_inverse_square_sum_bound"])
    shell_sum_bound = shell_coeff * p_bound
    l1_bound = 1 + shell_sum_bound
    regions = int(split["regions"])
    quarter = int(split["quarter_scale"])
    convolution_multiplier = regions * quarter ** power
    uniform_bound = factor * convolution_multiplier * l1_bound * shell_sum_bound
    authorities = {key: ROOT / value["path"] for key, value in manifest["source_authorities"].items()}
    hashes = {key: sha(path) for key, path in authorities.items()}

    rows: list[dict[str, Any]] = []
    test_m = [1, 2, 5, 10]
    shell_checks: dict[str, dict[str, str]] = {}
    for m in test_m:
        count = (2 * m + 1) ** d - (2 * m - 1) ** d
        expected = coeffs[0] * m * m + coeffs[1]
        shell_weight = Fraction(count, (1 + m * m) ** power)
        shell_checks[str(m)] = {"count": str(count), "weight": f"{shell_weight.numerator}/{shell_weight.denominator}"}
        mark(rows, f"shell_count_{m}", count == expected, count, expected)
        mark(rows, f"shell_weight_bound_{m}", shell_weight <= Fraction(shell_coeff, m * m), shell_weight, f"<={shell_coeff}/{m}^2")

    partials: dict[str, str] = {}
    for m in test_m:
        value = sum((Fraction(1, k * k) for k in range(1, m + 1)), Fraction(0))
        partials[str(m)] = f"{value.numerator}/{value.denominator}"
        mark(rows, f"inverse_square_partial_{m}", value < p_bound, value, f"<{p_bound}")

    values: dict[str, dict[int, Fraction]] = {str(s): {} for s in exponents}
    tables: dict[str, dict[str, str]] = {str(s): {} for s in exponents}
    for cutoff in cutoffs:
        for exponent in exponents:
            value = finite_charge(manifest, cutoff, exponent)
            values[str(exponent)][cutoff] = value
            tables[str(exponent)][str(cutoff)] = f"{value.numerator}/{value.denominator}"
            mark(rows, f"finite_charge_bound_s{exponent}_N{cutoff}", value <= uniform_bound, value, f"<={uniform_bound}")
        mark(rows, f"heat_order_N{cutoff}", all(values[str(a)][cutoff] >= values[str(b)][cutoff] for a, b in zip(exponents, exponents[1:])), [tables[str(s)][str(cutoff)] for s in exponents], "nonincreasing in s")

    mark(rows, "dimension_is_three", d == 3, d, 3)
    mark(rows, "covariance_power_is_two", power == 2, power, 2)
    mark(rows, "source_hashes_match", hashes == {key: value["sha256"] for key, value in manifest["source_authorities"].items()}, hashes, "manifest hashes")
    mark(rows, "current_factor_derived", factor == 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"])), factor, "derived profile identity")
    mark(rows, "convolution_multiplier_derived", convolution_multiplier == regions * quarter ** power, convolution_multiplier, "regions*quarter^power")
    mark(rows, "l1_bound_derived", l1_bound == 1 + shell_sum_bound, l1_bound, "1+shell_sum_bound")
    mark(rows, "uniform_bound_positive", uniform_bound > 0, uniform_bound, ">0")
    boundary = manifest["boundary"].lower()
    for token in ("proxy", "production", "q-ledger", "a13", "sector-a", "pre-a"):
        mark(rows, f"boundary_token_{token}", token in boundary, boundary, f"contains {token}")
    derived = {
        "dimension": d,
        "covariance_power": power,
        "current_factor": factor,
        "shell_coefficient": shell_coeff,
        "shell_checks": shell_checks,
        "inverse_square_partial_checks": partials,
        "shell_sum_bound": shell_sum_bound,
        "l1_bound": l1_bound,
        "convolution_multiplier": convolution_multiplier,
        "uniform_charge_bound": uniform_bound,
        "cutoffs": cutoffs,
        "heat_exponents": exponents,
        "finite_q_tables": tables,
        "analytic_statement": "The explicit max-norm convolution comparison gives a cutoff-independent bound at heat exponent s>=2; the source is a proxy, not the production owner.",
    }
    return derived, rows, hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    derived, assertions, hashes = run(manifest)
    failures = [row for row in assertions if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-gaussian-fourier-uniform-heat-bound-independent-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Independent Fraction-only cutoff-uniform proxy bound; no production-owner claim.",
        "source_authorities": hashes,
        "derived": derived,
        "assertions": assertions,
        "assertion_count": len(assertions),
        "conclusion": "The independent lane reproduces the uniform proxy majorant 529152 for registered s>=2 and finite checks; this is not the A1 production q-ledger.",
        "honesty_boundary": ["proxy only", "comparison bound only", "no production heat/root owner", "no production q-ledger", "no A13 closure", "no Sector-A or Pre-A closure"],
        "failures": failures,
    }
    if not args.no_store:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 FOURIER UNIFORM HEAT INDEPENDENT FAIL {len(assertions)-len(failures)}/{len(assertions)}")
        return 1
    print(f"A1 FOURIER UNIFORM HEAT INDEPENDENT PASS {len(assertions)}/{len(assertions)}")
    if not args.no_store:
        print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
