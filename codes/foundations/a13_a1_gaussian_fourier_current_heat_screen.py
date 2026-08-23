#!/usr/bin/env python3
"""Primary exact finite screen for the diagonal-Gaussian A1 current proxy.

The calculation is deliberately a proxy: it uses the fourth-order covariance
envelope gamma_n=(1+|n|^2)^(-2), the registered three-generator profile, and
test heat rates lambda_s(r).  It does not claim to be the full A1 Gibbs law or
the missing A13 production owner.
"""

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
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-a1-gaussian-fourier-current-heat-screen-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-a1-gaussian-fourier-current-heat-screen" / "result.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def modes(cutoff: int, dimension: int) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product(range(-cutoff, cutoff + 1), repeat=dimension))


def norm_sq(mode: tuple[int, ...]) -> int:
    return sum(value * value for value in mode)


def add_mode(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def gamma(mode: tuple[int, ...]) -> Fraction:
    return Fraction(1, (1 + norm_sq(mode)) ** 2)


def heat_rate(mode: tuple[int, ...], exponent: int) -> Fraction:
    base = 1 + norm_sq(mode)
    if exponent == 0:
        return Fraction(1)
    return Fraction(base ** (exponent // 2))


def add_assertion(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def source_paths(data: dict[str, Any]) -> dict[str, Path]:
    return {
        key: REPO / value["path"] for key, value in data["source_authorities"].items()
    }


def compute(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    inputs = manifest["registered_inputs"]
    dimension = int(inputs["dimension"])
    cutoffs = tuple(int(value) for value in inputs["cutoffs"])
    exponents = tuple(int(value) for value in inputs["heat_exponents"])
    profile = inputs["generator_profile"]
    factor = 2 * int(profile["cross_channels"]) + 2 * int(profile["diagonal_channels"])
    source_files = source_paths(manifest)
    current_hashes = {key: digest(path) for key, path in source_files.items()}
    expected_hashes = {key: value["sha256"] for key, value in manifest["source_authorities"].items()}

    tables: dict[str, dict[str, str]] = {str(exponent): {} for exponent in exponents}
    exact_values: dict[str, dict[int, Fraction]] = {str(exponent): {} for exponent in exponents}
    for cutoff in cutoffs:
        cube = modes(cutoff, dimension)
        cube_set = set(cube)
        covariance = {mode: gamma(mode) for mode in cube}
        convolution: dict[tuple[int, ...], Fraction] = {}
        for output in cube:
            if norm_sq(output) == 0:
                continue
            convolution[output] = sum(
                covariance[input_mode] * covariance[add_mode(input_mode, output)]
                for input_mode in cube
                if add_mode(input_mode, output) in cube_set
            )
        for exponent in exponents:
            total = Fraction(0)
            for output, value in convolution.items():
                total += Fraction(factor * norm_sq(output), 1 + heat_rate(output, exponent)) * value
            exact_values[str(exponent)][cutoff] = total
            tables[str(exponent)][str(cutoff)] = f"{total.numerator}/{total.denominator}"

    rows: list[dict[str, Any]] = []
    add_assertion(rows, "dimension_is_three", dimension == 3, dimension, 3)
    add_assertion(rows, "source_hashes_match", current_hashes == expected_hashes, current_hashes, expected_hashes)
    add_assertion(rows, "current_factor_identity", factor == 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"])), factor, "derived profile identity")
    add_assertion(rows, "current_factor_positive", factor > 0, factor, ">0")
    for exponent in exponents:
        values = exact_values[str(exponent)]
        add_assertion(rows, f"q_nonnegative_s{exponent}", all(value >= 0 for value in values.values()), tables[str(exponent)], ">=0")
        if exponent == 0:
            ordered = all(values[right] > values[left] for left, right in zip(cutoffs, cutoffs[1:]))
            add_assertion(rows, "unweighted_screen_strict_growth", ordered, tables[str(exponent)], "strictly increasing over registered cutoffs")
    for cutoff in cutoffs:
        q0 = exact_values["0"][cutoff]
        q2 = exact_values["2"][cutoff]
        q4 = exact_values["4"][cutoff]
        add_assertion(rows, f"heat_order_cutoff_{cutoff}", q0 >= q2 >= q4, [tables["0"][str(cutoff)], tables["2"][str(cutoff)], tables["4"][str(cutoff)]], "Q(s=0)>=Q(s=2)>=Q(s=4)")
    add_assertion(rows, "proxy_scope_is_explicit", "proxy" in manifest["interpretation"]["uv_claim"].lower() and "not the full" in manifest["interpretation"]["uv_claim"].lower(), manifest["interpretation"]["uv_claim"], "proxy and not full A1 Gibbs")

    derived = {
        "dimension": dimension,
        "cutoffs": list(cutoffs),
        "heat_exponents": list(exponents),
        "current_factor": factor,
        "finite_q_tables": tables,
        "asymptotic_statement": "For the proxy gamma in d=3, gamma is l1 with fourth-order tail; the convolution is O(<r>^-4), so the current spectrum is O(<r>^-2) before heat and gains the factor (1+lambda_r)^-1 after heat.",
        "threshold_statement": "The finite screen is consistent with no-heat growth and summability once the heat rate grows at least quadratically; the quartic case is the A1-style UV test. This is not a production theorem.",
    }
    return derived, rows, current_hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else REPO / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    derived, assertions, source_hashes = compute(manifest)
    failures = [row for row in assertions if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-gaussian-fourier-current-heat-screen-primary-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Exact finite diagonal-Gaussian fourth-order UV proxy for the A1 three-generator current; no production-owner claim.",
        "source_authorities": source_hashes,
        "derived": derived,
        "assertions": assertions,
        "assertion_count": len(assertions),
        "conclusion": "The proxy current has an exact coherent output convolution. The unweighted finite charge grows over registered cutoffs, while quadratic and quartic heat-rate screens are smaller; this identifies the heat-rate assumption as load-bearing but does not identify the A1 production heat/root owner.",
        "honesty_boundary": ["proxy covariance only", "finite cutoff only", "no A1 production heat owner", "no cutoff-uniform q-ledger theorem", "no A13 closure", "no continuum or real-time result"],
        "failures": failures,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 FOURIER HEAT SCREEN FAIL {len(assertions)-len(failures)}/{len(assertions)}")
        return 1
    print(f"A1 FOURIER HEAT SCREEN PASS {len(assertions)}/{len(assertions)}")
    print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
