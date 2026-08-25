#!/usr/bin/env python3
"""Primary exact audit for EXP-001114.

The audit expands the exact scalar Q3 source/neighbor potential with SymPy,
extracts the full all-potential Taylor coefficient, and checks the formal
source-degree filtration for words containing a kinetic derivation.  The
filtration is coefficientwise; it is deliberately not an unbounded-operator
or thermodynamic theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_full_heisenberg_source_degree_filtration"
MANIFEST = REPO / "strategy/pre_a_cp1_st8_q3lock_full_heisenberg_source_degree_filtration_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
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


def source_degree(expr: sp.Expr, source: sp.Symbol) -> int:
    expanded = sp.expand(expr)
    if expanded == 0:
        return -1
    return int(sp.Poly(expanded, source).degree())


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g = sp.Rational(fixture["g"])
    lam = sp.Rational(fixture["lambda"])
    coupling = sp.Rational(fixture["c"])
    G = sp.factor(g + 3 * lam)
    orders = [int(order) for order in fixture["orders"]]
    q, r, a = sp.symbols("q r a")
    declared_delta = G * (q**4 - (q - a) ** 4) / 4 - coupling * a * r
    delta = sp.factor(declared_delta)
    reversed_delta = sp.factor(G * (r**4 - (r - a) ** 4) / 4 - coupling * a * q)
    audit = Audit()

    audit.check("identity", manifest["exploration_id"] == "EXP-001114" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001114/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("onsite coupling", G == sp.Rational(51, 35) and coupling == sp.Rational(2, 3), [G, coupling], ["51/35", "2/3"], "fixture")
    audit.check("delta identity", sp.expand(delta - declared_delta) == 0, delta, "declared Delta", "algebra")
    all_top_coordinate_free = True
    target_rows: list[dict[str, Any]] = []
    reversed_rows: list[dict[str, Any]] = []
    kinetic_rows: list[dict[str, Any]] = []
    for m in orders:
        power = sp.expand(delta**m)
        top_degree = 4 * m
        top_coefficient = sp.factor(sp.Poly(power, a).coeff_monomial(a**top_degree))
        all_top_coordinate_free = all_top_coordinate_free and not top_coefficient.has(q, r) and top_coefficient == (-G / 4) ** m
        target = sp.factor(sp.diff(power, r).subs({q: 0, r: 0}))
        expected = sp.factor(-m * coupling * (-G / 4) ** (m - 1) * a ** (4 * m - 3))
        degree = source_degree(target, a)
        coefficient = sp.factor(sp.Poly(target, a).coeff_monomial(a ** (4 * m - 3)))
        target_rows.append({"m": m, "target": target, "expected": expected, "degree": degree, "coefficient": coefficient, "top_coefficient": top_coefficient})
        audit.check(f"target formula m={m}", target == expected, target, expected, "all-potential")
        audit.check(f"target degree m={m}", degree == 4 * m - 3, degree, 4 * m - 3, "source-degree")
        audit.check(f"target nonzero m={m}", coefficient != 0, coefficient, "nonzero", "source-degree")
        reversed_target = sp.factor(sp.diff(sp.expand(reversed_delta**m), q).subs({q: 0, r: 0}))
        reversed_degree = source_degree(reversed_target, a)
        reversed_coefficient = sp.factor(sp.Poly(reversed_target, a).coeff_monomial(a ** (4 * m - 3)))
        reversed_rows.append({"m": m, "target": reversed_target, "expected": expected, "degree": reversed_degree, "coefficient": reversed_coefficient})
        for kinetic_count in range(1, m + 1):
            potential_count = m - kinetic_count
            bound = 4 * potential_count - 1 if potential_count else -1
            kinetic_rows.append({"m": m, "kinetic_count": kinetic_count, "potential_count": potential_count, "bound": bound, "target_degree": 4 * m - 3})
    audit.check("top source coefficient coordinate-free", all_top_coordinate_free, all_top_coordinate_free, True, "filtration")
    audit.check("orientation agreement", all(row["target"] == row["expected"] and row["degree"] == 4 * row["m"] - 3 and row["coefficient"] != 0 for row in reversed_rows), reversed_rows, "same exact rows", "orientation")
    audit.check("kinetic words cannot reach top degree", all(row["bound"] < row["target_degree"] for row in kinetic_rows), kinetic_rows, "bound < 4*m-3", "filtration")
    derivative_rows: list[dict[str, Any]] = []
    for m in orders:
        power = sp.expand(delta**m)
        q_first = source_degree(sp.diff(power, q), a)
        r_first = source_degree(sp.diff(power, r), a)
        q_second = source_degree(sp.diff(power, q, 2), a)
        r_second = source_degree(sp.diff(power, r, 2), a)
        derivative_rows.append({"m": m, "q_first": q_first, "r_first": r_first, "q_second": q_second, "r_second": r_second})
    audit.check("kinetic coordinate derivatives do not increase source degree", all(row["q_first"] <= 4 * row["m"] - 1 and row["r_first"] <= 4 * row["m"] - 1 and row["q_second"] <= 4 * row["m"] - 1 and row["r_second"] <= 4 * row["m"] - 1 for row in derivative_rows), derivative_rows, "each derivative degree <= 4*m-1", "filtration")
    audit.check("open operator scope", manifest["scope"]["actual_q3_operator_domain_closed"] is False and manifest["scope"]["common_alpha_closed"] is False, manifest["scope"], "false/false", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
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
            "derivative_rows": derivative_rows,
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
    print(f"PRIMARY FULL-HEISENBERG-SOURCE-FILTRATION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
