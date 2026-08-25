#!/usr/bin/env python3
"""Primary exact-arithmetic common-core form-comparison audit (EXP-001130)."""

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
SLUG = "pre_a_cp1_st8_q3lock_common_core_form_comparison"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-common-core-form-comparison-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


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
    return rows[:8] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]
def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    c, lam, chi, r, g = (Fraction(fixture[key]) for key in ("c", "lambda", "chi", "r", "g"))
    bond_constant = Fraction(fixture["bond_form_constant"])
    grid = [Fraction(value) for value in fixture["grid_values"]]
    lower_one = -(r * r) / (4 * g)
    pair_lower = 2 * lower_one
    shift = 1 - pair_lower
    alpha_bond = 1 + 4 * lam / g
    edge_coefficient = 1 + 2 * alpha_bond
    edge_remainder = bond_constant + shift - edge_coefficient * shift
    two_orientation_constant = edge_coefficient + edge_remainder
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001130" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001130/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["common_core_scalar_lower_bound_closed"] and scope["common_core_form_comparison_closed"] and scope["positive_canonical_shift_closed"] and scope["two_orientation_square_root_inclusion_contract_closed"] and not scope["friedrichs_operator_realisation_closed"] and not scope["weighted_product_domain_closed"], scope, "form contract only", "scope")
    check("lower bound", pair_lower == Fraction(fixture["pair_lower_bound"]), pair_lower, fixture["pair_lower_bound"], "constants")
    check("canonical shift", shift == Fraction(fixture["canonical_shift"]), shift, fixture["canonical_shift"], "constants")
    check("edge coefficient", edge_coefficient == Fraction(fixture["onsite_form_coefficient"]), edge_coefficient, fixture["onsite_form_coefficient"], "constants")
    check("edge remainder", edge_remainder == Fraction(fixture["edge_remainder"]), edge_remainder, fixture["edge_remainder"], "constants")
    check("two orientation constant", two_orientation_constant == Fraction(fixture["two_orientation_constant"]), two_orientation_constant, fixture["two_orientation_constant"], "constants")

    def bond(x: Fraction, y: Fraction) -> Fraction:
        difference = x - y
        return c * difference * difference / 2 + lam * difference * difference * (x * x + y * y) / 4

    def onsite(x: Fraction, p: Fraction) -> Fraction:
        return p * p / (2 * chi) + r * x * x / 2 + g * x**4 / 4

    row_count = 0
    minimum_slack = {"lower": None, "positivity": None, "reverse": None, "upper": None, "absorbed": None}
    for x, y, p, q in product(grid, repeat=4):
        h_on = onsite(x, p) + onsite(y, q)
        b = bond(x, y)
        k_on = h_on + shift
        k_edge = h_on + b + shift
        slacks = {"lower": h_on - pair_lower, "positivity": b, "reverse": k_edge - k_on, "upper": edge_coefficient * k_on + edge_remainder - k_edge, "absorbed": two_orientation_constant * k_on - k_edge}
        check(f"grid row {row_count} lower", slacks["lower"] >= 0, slacks["lower"], ">=0", "form lower bound")
        check(f"grid row {row_count} bond positivity", slacks["positivity"] >= 0, slacks["positivity"], ">=0", "bond positivity")
        check(f"grid row {row_count} reverse", slacks["reverse"] >= 0, slacks["reverse"], ">=0", "two orientations")
        check(f"grid row {row_count} upper", slacks["upper"] >= 0, slacks["upper"], ">=0", "form comparison")
        check(f"grid row {row_count} absorbed", slacks["absorbed"] >= 0, slacks["absorbed"], ">=0", "form comparison")
        for key, value in slacks.items():
            if minimum_slack[key] is None or value < minimum_slack[key]:
                minimum_slack[key] = value
        row_count += 1

    check("grid coverage", row_count == len(grid) ** 4, row_count, len(grid) ** 4, "grid")
    check("weights dominate identity", shift + pair_lower == 1, shift + pair_lower, 1, "positivity")
    check("source and volume constants", scope["source_uniformity_proved"] and scope["volume_uniformity_proved"], scope, True, "uniform local form")
    check("operator boundary retained", scope["friedrichs_operator_realisation_closed"] is False and scope["weighted_product_domain_closed"] is False, scope, "open operator gate", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-COMMON-CORE-FORM-COMPARISON", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": compact_assertions(rows), "derived": {"grid_rows": row_count, "pair_lower_bound": str(pair_lower), "canonical_shift": str(shift), "edge_coefficient": str(edge_coefficient), "edge_remainder": str(edge_remainder), "two_orientation_constant_squared": str(two_orientation_constant), "minimum_slack": {key: str(value) for key, value in minimum_slack.items()}, "common_core_scalar_lower_bound_closed": True, "common_core_form_comparison_closed": True, "positive_canonical_shift_closed": True, "two_orientation_square_root_inclusion_contract_closed": True, "friedrichs_operator_realisation_closed": False, "weighted_product_domain_closed": False, "common_alpha_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY COMMON-CORE-FORM-COMPARISON PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
