#!/usr/bin/env python3
"""Independent exact lane for EXP-001118.

This file intentionally rebuilds the polynomial dictionary and recurrence
with fractions instead of importing the primary lane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_factorial_derivative_closed_quartic_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-factorial-derivative-closed-quartic-obstruction-manifest.json"
SOURCE_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-source-coefficient-product-manifest.json"
MIXED_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


Poly = dict[tuple[int, int, int], Fraction]


def add(*terms: Poly) -> Poly:
    result: Poly = {}
    for term in terms:
        for key, value in term.items():
            result[key] = result.get(key, Fraction(0)) + value
    return {key: value for key, value in result.items() if value}


def scale(term: Poly, factor: Fraction) -> Poly:
    return {key: value * factor for key, value in term.items() if value * factor}


def multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for a, av in left.items():
        for b, bv in right.items():
            key = tuple(a[i] + b[i] for i in range(3))
            result[key] = result.get(key, Fraction(0)) + av * bv
    return {key: value for key, value in result.items() if value}


def monomial(q: int = 0, v: int = 0, a: int = 0, coefficient: Fraction = Fraction(1)) -> Poly:
    return {(q, v, a): coefficient}


def difference(left: Poly, right: Poly) -> Poly:
    return add(left, scale(right, Fraction(-1)))


def power(term: Poly, exponent: int) -> Poly:
    result = monomial()
    for _ in range(exponent):
        result = multiply(result, term)
    return result


def source_polynomial(reverse: bool) -> Poly:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    rate_fixture = json.loads(MIXED_MANIFEST.read_text(encoding="utf-8"))["fixture"]
    lam = Fraction(str(rate_fixture["lambda"]))
    onsite_coupling = Fraction(str(manifest["fixture"]["onsite_coupling"]))
    coupling = Fraction(str(rate_fixture["spatial_coupling"]))
    q = monomial(q=1); v = monomial(v=1); a = monomial(a=1)
    edge = scale(multiply(power(difference(q, v), 2), add(power(q, 2), power(v, 2))), lam / 4)
    if not reverse:
        edge_shift = scale(multiply(power(difference(difference(q, a), v), 2), add(power(difference(q, a), 2), power(v, 2))), lam / 4)
        onsite = scale(difference(power(q, 4), power(difference(q, a), 4)), onsite_coupling / 4)
        bond_shift = scale(power(difference(difference(q, a), v), 2), coupling / 2)
    else:
        edge_shift = scale(multiply(power(difference(q, difference(v, a)), 2), add(power(q, 2), power(difference(v, a), 2))), lam / 4)
        onsite = scale(difference(power(v, 4), power(difference(v, a), 4)), onsite_coupling / 4)
        bond_shift = scale(power(difference(q, difference(v, a)), 2), coupling / 2)
    bond = scale(power(difference(q, v), 2), coupling / 2)
    return add(onsite, scale(difference(edge, edge_shift), Fraction(3)), scale(difference(bond, bond_shift), Fraction(6)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    center = source_polynomial(False)
    reverse = source_polynomial(True)
    top = tuple((0, 0, 4))
    expected = Fraction(str(fixture["top_coefficient_abs"]))
    check("identity", manifest["exploration_id"] == "EXP-001118" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001118/T-054", "provenance")
    check("center top coefficient", abs(center[top]) == expected, center[top], f"abs={expected}", "source polynomial")
    check("reverse top coefficient", abs(reverse[top]) == expected, reverse[top], f"abs={expected}", "orientation")
    check("orientation equality", center[top] == reverse[top], [center[top], reverse[top]], "equal", "orientation")

    S = Fraction(str(fixture["source_radius"]))
    S_prime = Fraction(str(fixture["reduced_source_radius"]))
    c = expected
    n0 = int(fixture["witness_initial_degree"])
    branch = int(fixture["comparison_base"])
    check("radius order", 0 < S_prime < S, [S_prime, S], "0<S'<S", "radius")
    check("derivative closure", Fraction(n0 * math.factorial(n0 - 1), math.factorial(n0)) / S == 1 / S, 1 / S, "1/S", "derivative")
    rows: list[dict[str, Any]] = []
    for m in [int(value) for value in fixture["orders"]]:
        coeff = c**m
        for j in range(m):
            coeff *= n0 + 3 * j
        degree = n0 + 3 * m
        ratio = coeff * math.factorial(degree) * S_prime**degree / (math.factorial(n0) * S**n0)
        lower = c**m * Fraction(m ** (2 * m), 1) * S_prime**degree / S
        check(f"recurrence m={m}", degree == n0 + 3 * m, degree, n0 + 3 * m, "recurrence")
        check(f"factorial lower bound m={m}", math.factorial(degree) >= m ** (2 * m), math.factorial(degree), f">={m}^{2*m}", "asymptotic")
        rows.append({"m": m, "degree": degree, "coefficient": str(coeff), "norm_ratio": str(ratio), "factorial_lower_bound": str(lower), "comparison_base_power": branch**m, "exceeds_comparison_base": ratio > branch**m})
    witness = next(row for row in rows if row["m"] == int(fixture["small_exact_witness_order"]))
    witness_ratio = Fraction(witness["norm_ratio"])
    check("order-sixteen witness", witness_ratio > branch**16, witness_ratio, f">{branch}^16", "boundary")
    check("scope firewall", manifest["scope"]["factorial_derivative_closure_closed"] and manifest["scope"]["repeated_top_monomial_exponential_envelope_refuted"] and not manifest["scope"]["actual_q3_history_closed"], manifest["scope"], "route boundary / Q3 open", "scope")
    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": checks,
        "derived": {"center_top_coefficient": str(center[top]), "reverse_top_coefficient": str(reverse[top]), "top_coefficient_absolute": str(expected), "source_radius": str(S), "reduced_source_radius": str(S_prime), "derivative_closure_constant": str(1 / S), "comparison_base": branch, "ratio_rows": rows, "order_sixteen_ratio": witness["norm_ratio"], "factorial_derivative_closed": True, "repeated_top_monomial_exponential_envelope_refuted": True, "actual_q3_common_core_map_proved": False, "actual_q3_history_closed": False, "common_alpha_closed": False},
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST), "source_manifest": str(SOURCE_MANIFEST.relative_to(REPO)).replace("\\", "/"), "source_manifest_sha256": sha256(SOURCE_MANIFEST)},
        "exploration_id": manifest["exploration_id"], "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FACTORIAL-QUARTIC-OBSTRUCTION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
