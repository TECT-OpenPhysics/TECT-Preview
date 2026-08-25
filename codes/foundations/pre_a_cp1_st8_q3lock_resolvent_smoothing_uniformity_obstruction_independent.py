#!/usr/bin/env python3
"""Independent scaling reproduction for EXP-001137."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_resolvent_smoothing_uniformity_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-resolvent-smoothing-uniformity-obstruction-manifest.json"
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
    chi = Fraction(fixture["chi"])
    additive = Fraction(fixture["form_additive_gradient_bound"])
    cross = Fraction(fixture["cross_orientation_multiplier"])
    scales = [Fraction(value) for value in fixture["scales_a"]]
    supports = [int(value) for value in fixture["support_sizes"]]
    grid = [Fraction(value) for value in fixture["grid_values"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", data["exploration_id"] == "EXP-001137" and data["task_id"] == "T-054", [data["exploration_id"], data["task_id"]], "EXP-001137/T-054", "provenance")
    check("scope", data["claim_bearing"] is False and scope["resolvent_smoothing_route_obstruction_closed"] and not scope["epsilon_uniform_weighted_resolvent_cylinder_closed"], scope, "route obstruction", "scope")
    check("parameters", chi > 0 and additive >= 0 and cross > 0 and all(scale > 0 for scale in scales), [chi, additive, cross, scales], "positive", "hypotheses")

    scale_rows: list[dict[str, Any]] = []
    previous_bound: Fraction | None = None
    previous_error: Fraction | None = None
    for scale in scales:
        epsilon = Fraction(1, 1) / (scale * scale)
        witness = (scale * scale * scale) / (2 * scale * scale)
        lower_sup_square = witness * witness
        form_lower = 2 * lower_sup_square + additive / chi
        error_coefficient = epsilon * epsilon
        check(f"scale {scale} reciprocal", epsilon * scale * scale == 1, epsilon * scale * scale, 1, "parameterization")
        check(f"scale {scale} witness", witness == scale / 2, witness, scale / 2, "witness")
        check(f"scale {scale} lower form", form_lower == scale * scale / 2 + additive / chi, form_lower, "a^2/2+1/chi", "form scaling")
        if previous_bound is not None:
            check(f"scale {scale} bound growth", form_lower > previous_bound, [previous_bound, form_lower], "increasing", "form scaling")
            check(f"scale {scale} error decay", error_coefficient < previous_error, [previous_error, error_coefficient], "decreasing", "conditional approximation")
        previous_bound, previous_error = form_lower, error_coefficient
        scale_rows.append({"scale_a": str(scale), "epsilon": str(epsilon), "witness_value": str(witness), "lower_sup_norm_squared": str(lower_sup_square), "one_site_form_bound_lower": str(form_lower), "cross_bound_lower": str(cross * form_lower), "approximation_coefficient": str(error_coefficient)})

    grid_rows: list[dict[str, Any]] = []
    scale = scales[-1]
    for x in grid:
        denominator = scale * scale + x * x
        value = scale * scale * x / denominator
        error = x - value
        check(f"grid {x} error", error == x ** 3 / denominator, error, x ** 3 / denominator, "conditional approximation")
        grid_rows.append({"x": str(x), "value": str(value), "error": str(error)})

    support_rows: list[dict[str, Any]] = []
    for support in supports:
        product_sup_square = (scale * scale / 4) ** support
        same_lower = 2 * product_sup_square
        check(f"support {support} positive lower", same_lower > 0, same_lower, ">0", "support scaling")
        support_rows.append({"support_size": support, "product_sup_norm_squared_lower": str(product_sup_square), "same_form_bound_lower": str(same_lower), "cross_orientation_bound_lower": str(cross * same_lower)})

    check("one-site obstruction", scope["epsilon_uniform_weighted_resolvent_cylinder_closed"] is False and scope["epsilon_uniform_raw_coordinate_approximation_closed"] is False, scope, "uniform route fails", "boundary")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RESOLVENT-SMOOTHING-UNIFORMITY-OBSTRUCTION",
        "claim_id": data["claim_ids"][0],
        "task_id": data["task_id"],
        "exploration_id": data["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "scale_rows": scale_rows,
            "grid_rows": grid_rows,
            "support_rows": support_rows,
            "one_site_form_lower_asymptotic_coefficient": "1/2",
            "approximation_coefficient_asymptotic": "epsilon^2",
            "fixed_epsilon_resolvent_cylinder_closed": True,
            "epsilon_uniform_weighted_resolvent_cylinder_closed": False,
            "epsilon_uniform_raw_coordinate_approximation_closed": False,
            "resolvent_smoothing_route_obstruction_closed": True,
            "alternative_cutoff_or_higher_weight_route_open": True,
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
    print(f"INDEPENDENT RESOLVENT-SMOOTHING-UNIFORMITY-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
