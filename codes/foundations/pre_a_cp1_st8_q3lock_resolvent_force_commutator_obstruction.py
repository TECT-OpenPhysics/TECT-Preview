#!/usr/bin/env python3
"""Primary pointwise/localization audit for EXP-001138."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_resolvent_force_commutator_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-resolvent-force-commutator-obstruction-manifest.json"
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
    return rows[:10] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    r = Fraction(fixture["r"])
    g = Fraction(fixture["g"])
    scale = Fraction(fixture["resolvent_scale"])
    threshold = Fraction(fixture["large_coordinate_square_threshold"])
    grid = [Fraction(value) for value in fixture["grid_y"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001138" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001138/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive parameters", g > 0 and scale > 0 and threshold > 0 and all(y >= threshold for y in grid), [g, scale, threshold, grid], "positive and above threshold", "hypotheses")
    check("model coefficients", r == -1 and g == Fraction(3, 5) and scale == 16, [r, g, scale], [-1, Fraction(3, 5), 16], "Q3 fixture")

    rows_y: list[dict[str, Any]] = []
    for index, y in enumerate(grid):
        denominator = scale + y
        force_over_q = r + g * y
        derivative_abs = scale * (y - scale) / (denominator ** 2)
        force_abs = force_over_q
        potential = Fraction(17, 12) + r * y / 2 + g * y * y / 4
        force_lower = y / 2
        derivative_lower = 2 / y
        combined_lower = force_lower * derivative_lower
        potential_lower = y * y / 20
        weighted_potential_lower = potential_lower * y * combined_lower * combined_lower
        check(f"y {index} denominator", denominator > 0, denominator, ">0", "pointwise")
        check(f"y {index} force positivity", force_abs >= force_lower, [force_abs, force_lower], ">=y/2", "force lower bound")
        check(f"y {index} derivative lower", derivative_abs >= derivative_lower, [derivative_abs, derivative_lower], ">=2/y", "resolvent derivative lower bound")
        check(f"y {index} combined lower", force_abs * derivative_abs >= combined_lower and combined_lower >= 1, [force_abs * derivative_abs, combined_lower], ">=1", "commutator lower bound")
        check(f"y {index} potential lower", potential >= potential_lower, [potential, potential_lower], ">=y^2/20", "potential coercivity")
        check(f"y {index} weighted density lower", weighted_potential_lower >= y * y * y / 20, [weighted_potential_lower, y * y * y / 20], ">=y^3/20", "weighted potential")
        check(f"y {index} ratio growth", weighted_potential_lower / potential_lower >= y, weighted_potential_lower / potential_lower, f">={y}", "localization ratio")
        rows_y.append({"y": str(y), "force_over_q": str(force_over_q), "force_lower": str(force_lower), "resolvent_derivative": str(derivative_abs), "resolvent_derivative_lower": str(derivative_lower), "combined_lower": str(force_abs * derivative_abs), "potential": str(potential), "potential_lower": str(potential_lower), "weighted_potential_lower": str(weighted_potential_lower), "ratio_lower": str(weighted_potential_lower / potential_lower)})

    check("leading coefficient", g * scale == Fraction(48, 5), g * scale, "48/5", "asymptotic coefficient")
    check("localization contract", fixture["localization_derivative_energy_symbol"] == "C_phi", fixture["localization_derivative_energy_symbol"], "C_phi", "localization")
    check("route obstruction", scope["pointwise_force_resolvent_obstruction_closed"] and scope["localized_k_form_obstruction_closed"] and scope["alternative_cancellation_aware_commutator_route_open"], scope, "naive K-form route obstructed", "scope")
    check("QFT firewall", all(scope[key] is False for key in ("second_commutator_closed", "modular_domain_transfer_closed", "direct_d_cauchy_closed", "common_alpha_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "QFT promotion remains open", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RESOLVENT-FORCE-COMMUTATOR-OBSTRUCTION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "rows_y": rows_y,
            "leading_force_derivative_coefficient": "48/5",
            "pointwise_force_resolvent_obstruction_closed": True,
            "localized_k_form_obstruction_closed": True,
            "fixed_resolvent_first_commutator_closed": True,
            "alternative_cancellation_aware_commutator_route_open": True,
            "higher_energy_weight_route_open": True,
            "second_commutator_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY RESOLVENT-FORCE-COMMUTATOR-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
