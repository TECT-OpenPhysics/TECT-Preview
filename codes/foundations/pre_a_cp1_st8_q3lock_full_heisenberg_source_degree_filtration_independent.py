#!/usr/bin/env python3
"""Independent Fraction polynomial audit for EXP-001114.

This lane implements its own sparse rational polynomial arithmetic instead of
importing the SymPy primary lane.  It checks the same coefficient filtration,
including the relabelled source/neighbor orientation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_full_heisenberg_source_degree_filtration"
MANIFEST = REPO / "strategy/pre_a_cp1_st8_q3lock_full_heisenberg_source_degree_filtration_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"
Term = tuple[int, int, int]
Poly = dict[Term, F]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def clean(poly: Poly) -> Poly:
    return {key: value for key, value in poly.items() if value}


def mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for (q1, r1, a1), value1 in left.items():
        for (q2, r2, a2), value2 in right.items():
            key = (q1 + q2, r1 + r2, a1 + a2)
            result[key] = result.get(key, F(0)) + value1 * value2
    return clean(result)


def power(poly: Poly, exponent: int) -> Poly:
    result: Poly = {(0, 0, 0): F(1)}
    for _ in range(exponent):
        result = mul(result, poly)
    return result


def derivative(poly: Poly, variable: int) -> Poly:
    result: Poly = {}
    for key, value in poly.items():
        exponent = key[variable]
        if exponent:
            updated = list(key)
            updated[variable] -= 1
            updated_key = tuple(updated)
            result[updated_key] = result.get(updated_key, F(0)) + value * exponent
    return clean(result)


def swap_qr(poly: Poly) -> Poly:
    return {(r, q, a): value for (q, r, a), value in poly.items()}


def evaluate_qr_zero(poly: Poly) -> dict[int, F]:
    result: dict[int, F] = {}
    for (q, r, a), value in poly.items():
        if q == 0 and r == 0:
            result[a] = result.get(a, F(0)) + value
    return {degree: value for degree, value in result.items() if value}


def source_degree(poly: Poly) -> int:
    return max((key[2] for key, value in poly.items() if value), default=-1)


def coefficient_degree(poly_a: dict[int, F]) -> int:
    return max((degree for degree, value in poly_a.items() if value), default=-1)


def delta_polynomial(G: F, coupling: F) -> Poly:
    return {
        (3, 0, 1): G,
        (2, 0, 2): -F(3, 2) * G,
        (1, 0, 3): G,
        (0, 0, 4): -G / 4,
        (0, 1, 1): -coupling,
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g = F(fixture["g"])
    lam = F(fixture["lambda"])
    coupling = F(fixture["c"])
    G = g + 3 * lam
    orders = [int(order) for order in fixture["orders"]]
    delta = delta_polynomial(G, coupling)
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001114" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001114/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("onsite coupling", G == F(51, 35) and coupling == F(2, 3), [G, coupling], ["51/35", "2/3"], "fixture")
    audit.check("delta polynomial support", set(delta) == {(3, 0, 1), (2, 0, 2), (1, 0, 3), (0, 0, 4), (0, 1, 1)}, sorted(delta), "five declared monomials", "algebra")
    target_rows: list[dict[str, Any]] = []
    reversed_rows: list[dict[str, Any]] = []
    kinetic_rows: list[dict[str, Any]] = []
    for m in orders:
        powered = power(delta, m)
        target_poly = evaluate_qr_zero(derivative(powered, 1))
        expected_degree = 4 * m - 3
        expected_coefficient = -m * coupling * (-G / 4) ** (m - 1)
        target = target_poly.get(expected_degree, F(0))
        target_degree = coefficient_degree(target_poly)
        target_rows.append({"m": m, "target": target, "degree": target_degree, "expected": expected_coefficient})
        audit.check(f"target formula m={m}", target == expected_coefficient and set(target_poly) == {expected_degree}, target_poly, {expected_degree: expected_coefficient}, "all-potential")
        audit.check(f"target degree m={m}", target_degree == expected_degree, target_degree, expected_degree, "source-degree")
        audit.check(f"target nonzero m={m}", target != 0, target, "nonzero", "source-degree")
        swapped_target_poly = evaluate_qr_zero(derivative(power(swap_qr(delta), m), 0))
        reversed_rows.append({"m": m, "target": swapped_target_poly.get(expected_degree, F(0)), "degree": coefficient_degree(swapped_target_poly), "support": sorted(swapped_target_poly)})
        audit.check(f"orientation formula m={m}", swapped_target_poly == {expected_degree: expected_coefficient}, swapped_target_poly, {expected_degree: expected_coefficient}, "orientation")
        for kinetic_count in range(1, m + 1):
            potential_count = m - kinetic_count
            bound = 4 * potential_count - 1 if potential_count else -1
            kinetic_rows.append({"m": m, "kinetic_count": kinetic_count, "potential_count": potential_count, "bound": bound, "target_degree": expected_degree})
    audit.check("kinetic words cannot reach top degree", all(row["bound"] < row["target_degree"] for row in kinetic_rows), kinetic_rows, "bound < 4*m-3", "filtration")
    audit.check("open operator scope", manifest["scope"]["actual_q3_operator_domain_closed"] is False and manifest["scope"]["common_alpha_closed"] is False, manifest["scope"], "false/false", "scope")
    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "G": G,
            "c": coupling,
            "orders": orders,
            "target_rows": target_rows,
            "reversed_rows": reversed_rows,
            "kinetic_rows": kinetic_rows,
            "top_degree_formula": "4*m-3",
            "top_coefficient_formula": "-m*c*(-G/4)^(m-1)",
            "full_taylor_source_degree_closed": True,
            "all_potential_top_coefficient_closed": True,
            "kinetic_degree_gap_closed_formally": True,
            "two_orientation_coefficient_closed": True,
            "actual_q3_operator_domain_closed": False,
            "volume_uniform_factorial_history_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FULL-HEISENBERG-SOURCE-FILTRATION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
