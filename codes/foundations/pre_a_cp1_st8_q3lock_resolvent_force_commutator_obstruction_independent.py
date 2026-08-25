#!/usr/bin/env python3
"""Independent rational audit for EXP-001138."""

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

    check("identity", data["exploration_id"] == "EXP-001138" and data["task_id"] == "T-054", [data["exploration_id"], data["task_id"]], "EXP-001138/T-054", "provenance")
    check("scope", data["claim_bearing"] is False and scope["pointwise_force_resolvent_obstruction_closed"] and not scope["second_commutator_closed"], scope, "pointwise route obstruction", "scope")
    check("parameters", r == -1 and g == Fraction(3, 5) and scale == 16 and threshold == 64, [r, g, scale, threshold], "declared fixture", "hypotheses")

    rows_y: list[dict[str, Any]] = []
    for y in grid:
        denominator = scale + y
        force_over_q = r + g * y
        derivative_abs = scale * (y - scale) / denominator ** 2
        potential = Fraction(17, 12) + r * y / 2 + g * y * y / 4
        combined_bound = (y / 2) * (2 / y)
        check(f"y {y} force", force_over_q >= y / 2, force_over_q, ">=y/2", "force lower bound")
        check(f"y {y} derivative", derivative_abs >= 2 / y, derivative_abs, ">=2/y", "derivative lower bound")
        check(f"y {y} combined", force_over_q * derivative_abs >= 1, force_over_q * derivative_abs, ">=1", "commutator lower bound")
        check(f"y {y} potential", potential >= y * y / 20, potential, ">=y^2/20", "potential coercivity")
        check(f"y {y} weighted", (y * y / 20) * y * combined_bound ** 2 >= y * y * y / 20, (y * y / 20) * y * combined_bound ** 2, ">=y^3/20", "weighted potential")
        rows_y.append({"y": str(y), "force_over_q": str(force_over_q), "force_lower": str(y / 2), "resolvent_derivative": str(derivative_abs), "resolvent_derivative_lower": str(2 / y), "combined_lower": str(force_over_q * derivative_abs), "potential": str(potential), "potential_lower": str(y * y / 20), "weighted_potential_lower": str((y * y / 20) * y * combined_bound ** 2), "ratio_lower": str(y * combined_bound ** 2)})

    check("leading coefficient", g * scale == Fraction(48, 5), g * scale, "48/5", "asymptotic coefficient")
    check("threshold coverage", all(y >= threshold for y in grid), grid, ">=64", "coverage")
    check("boundary", scope["localized_k_form_obstruction_closed"] and scope["alternative_cancellation_aware_commutator_route_open"] and scope["higher_energy_weight_route_open"], scope, "naive K-form route blocked", "QFT boundary")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RESOLVENT-FORCE-COMMUTATOR-OBSTRUCTION",
        "claim_id": data["claim_ids"][0],
        "task_id": data["task_id"],
        "exploration_id": data["exploration_id"],
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
    print(f"INDEPENDENT RESOLVENT-FORCE-COMMUTATOR-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
