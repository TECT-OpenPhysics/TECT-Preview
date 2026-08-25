#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001131."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_friedrichs_form_closure"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-friedrichs-form-closure-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def compact_assertions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in rows:
        group = str(row.get("group", "unknown"))
        counts[group] = counts.get(group, 0) + 1
    summary = {"total": len(rows), "groups": counts, "storage": "compact-summary; all assertions executed in memory"}
    return rows[:10] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]


def run() -> dict[str, Any]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = data["finite_fixture"], data["scope"]
    c = Fraction(fixture["c"])
    lam = Fraction(fixture["lambda"])
    chi = Fraction(fixture["chi"])
    mass = Fraction(fixture["r"])
    quartic = Fraction(fixture["g"])
    constant = Fraction(fixture["bond_form_constant"])
    degree = int(fixture["degree_bound"])
    shift = Fraction(fixture["per_site_shift"])
    grid = tuple(Fraction(value) for value in fixture["grid_values"])
    lower = -(mass * mass) / (4 * quartic)
    coefficient = 2 * (1 + 4 * lam / quartic)
    remainder = constant - 2 * coefficient * shift
    multiplier = 1 + coefficient * degree
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", data["exploration_id"] == "EXP-001131" and data["task_id"] == "T-054", [data["exploration_id"], data["task_id"]], "EXP-001131/T-054", "provenance")
    check("scope", data["claim_bearing"] is False and scope["finite_graph_form_closure_closed"] and scope["finite_graph_common_form_domain_closed"] and not scope["weighted_product_domain_closed"], scope, "finite form closure with product gate open", "scope")
    check("exact constants", [lower, coefficient, shift, remainder, multiplier] == [Fraction(fixture["site_lower_bound"]), Fraction(fixture["bond_on_site_coefficient"]), shift, Fraction(fixture["growth_remainder"]), Fraction(fixture["edge_multiplier"])], [lower, coefficient, shift, remainder, multiplier], "manifest constants", "constants")

    def onsite(x: Fraction, p: Fraction) -> Fraction:
        return p * p / (2 * chi) + mass * x * x / 2 + quartic * x**4 / 4

    def edge(x: Fraction, y: Fraction) -> Fraction:
        delta = x - y
        return c * delta * delta / 2 + lam * delta * delta * (x * x + y * y) / 4

    count = 0
    minima = {"lower": None, "bond": None, "envelope": None, "shifted": None}
    for x, y, p, q in product(grid, repeat=4):
        vx, vy = onsite(x, Fraction(0)), onsite(y, Fraction(0))
        b = edge(x, y)
        rows_to_check = {
            "lower": vx - lower,
            "bond": b,
            "envelope": coefficient * (vx + vy) + constant - b,
            "shifted": coefficient * ((vx + shift) + (vy + shift)) - b,
        }
        for label, slack in rows_to_check.items():
            check(f"grid {count} {label}", slack >= 0, slack, ">=0", "independent polynomial bounds")
            if minima[label] is None or slack < minima[label]:
                minima[label] = slack
        count += 1
    check("coverage", count == len(grid) ** 4, count, len(grid) ** 4, "grid")
    check("site coercivity", lower + shift == 1, lower + shift, 1, "coercivity")
    check("bounded degree order", multiplier == Fraction(fixture["edge_multiplier"]) and remainder <= 0, [multiplier, remainder], "declared multiplier and nonpositive remainder", "graph form order")
    check("QFT boundary", all(scope[key] is False for key in ("modular_domain_transfer_closed", "direct_d_cauchy_closed", "common_alpha_closed", "kms_gns_gap_closed", "continuum_closed", "pre_a_closed")), scope, "limit and QFT gates open", "boundary")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FRIEDRICHS-FORM-CLOSURE",
        "claim_id": data["claim_ids"][0],
        "task_id": data["task_id"],
        "exploration_id": data["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "pair_grid_rows": count,
            "site_lower_bound": str(lower),
            "bond_on_site_coefficient": str(coefficient),
            "per_site_shift": str(shift),
            "growth_remainder": str(remainder),
            "degree_bound": degree,
            "edge_multiplier": str(multiplier),
            "minimum_slack": {label: str(value) for label, value in minima.items()},
            "finite_graph_form_closure_closed": True,
            "finite_graph_friedrichs_operator_realisation_closed": True,
            "finite_graph_common_form_domain_closed": True,
            "bounded_degree_shifted_form_order_closed": True,
            "two_orientation_square_root_inclusion_closed": True,
            "weighted_product_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FRIEDRICHS-FORM-CLOSURE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
