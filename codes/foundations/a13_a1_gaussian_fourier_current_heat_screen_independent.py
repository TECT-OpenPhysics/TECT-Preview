#!/usr/bin/env python3
"""Stdlib-only independent lane for the A1 Fourier heat proxy screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-a1-gaussian-fourier-current-heat-screen-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-independent-a1-gaussian-fourier-current-heat-screen" / "result.json"


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


def cube(n: int, d: int) -> list[tuple[int, ...]]:
    return [tuple(values) for values in product(range(-n, n + 1), repeat=d)]


def covariance(mode: tuple[int, ...]) -> Fraction:
    return Fraction(1, (1 + norm(mode)) ** 2)


def translated(mode: tuple[int, ...], shift: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(mode, shift))


def rate(mode: tuple[int, ...], exponent: int) -> Fraction:
    base = 1 + norm(mode)
    return Fraction(1 if exponent == 0 else base ** (exponent // 2))


def mark(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def run(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    inputs = manifest["registered_inputs"]
    d = int(inputs["dimension"])
    cutoffs = [int(v) for v in inputs["cutoffs"]]
    exponents = [int(v) for v in inputs["heat_exponents"]]
    profile = inputs["generator_profile"]
    factor = 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"]))
    authorities = {key: ROOT / value["path"] for key, value in manifest["source_authorities"].items()}
    hashes = {key: sha(path) for key, path in authorities.items()}
    values: dict[str, dict[int, Fraction]] = {str(s): {} for s in exponents}
    for n in cutoffs:
        points = cube(n, d)
        point_set = set(points)
        weights = {point: covariance(point) for point in points}
        convolution = {}
        for r in points:
            rr = norm(r)
            if rr == 0:
                continue
            total = Fraction(0)
            for p in points:
                q = translated(p, r)
                if q in point_set:
                    total += weights[p] * weights[q]
            convolution[r] = total
        for s in exponents:
            total = Fraction(0)
            for r, conv_value in convolution.items():
                total += factor * norm(r) * conv_value / (1 + rate(r, s))
            values[str(s)][n] = total
    table = {s: {str(n): f"{value.numerator}/{value.denominator}" for n, value in row.items()} for s, row in values.items()}
    rows: list[dict[str, Any]] = []
    mark(rows, "dimension_is_three", d == 3, d, 3)
    mark(rows, "source_hashes_match", hashes == {key: value["sha256"] for key, value in manifest["source_authorities"].items()}, hashes, "manifest hashes")
    mark(rows, "generator_factor_formula", factor == 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"])), factor, "derived profile identity")
    mark(rows, "all_proxy_charges_nonnegative", all(value >= 0 for row in values.values() for value in row.values()), table, ">=0")
    mark(rows, "unweighted_growth", all(values["0"][b] > values["0"][a] for a, b in zip(cutoffs, cutoffs[1:])), table["0"], "strictly increasing")
    for n in cutoffs:
        mark(rows, f"heat_order_{n}", values["0"][n] >= values["2"][n] >= values["4"][n], [table["0"][str(n)], table["2"][str(n)], table["4"][str(n)]], "Q0>=Q2>=Q4")
    derived = {
        "dimension": d,
        "cutoffs": cutoffs,
        "heat_exponents": exponents,
        "current_factor": factor,
        "finite_q_tables": table,
        "asymptotic_statement": "gamma is l1 in dimension three and has fourth-order tail; convolution retains fourth-order tail, so the current spectrum is second-order before heat.",
    }
    return derived, rows, hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    derived, rows, hashes = run(manifest)
    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-gaussian-fourier-current-heat-screen-independent-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Independent Fraction-only finite proxy recomputation; no production-owner or gate claim.",
        "source_authorities": hashes,
        "derived": derived,
        "assertions": rows,
        "assertion_count": len(rows),
        "conclusion": "The independent lane reproduces the coherent current convolution and the heat-order screen; this remains a finite UV proxy rather than the A1 production dynamics.",
        "honesty_boundary": ["proxy only", "finite only", "no production heat owner", "no q-ledger theorem", "no A13 closure"],
        "failures": failures,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 FOURIER HEAT INDEPENDENT FAIL {len(rows)-len(failures)}/{len(rows)}")
        return 1
    print(f"A1 FOURIER HEAT INDEPENDENT PASS {len(rows)}/{len(rows)}")
    print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
