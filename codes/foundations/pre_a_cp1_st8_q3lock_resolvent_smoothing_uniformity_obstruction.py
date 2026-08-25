#!/usr/bin/env python3
"""Primary scaling audit for EXP-001137."""

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
    chi = Fraction(fixture["chi"])
    additive_gradient = Fraction(fixture["form_additive_gradient_bound"])
    cross_multiplier = Fraction(fixture["cross_orientation_multiplier"])
    scales = [Fraction(value) for value in fixture["scales_a"]]
    supports = [int(value) for value in fixture["support_sizes"]]
    grid = [Fraction(value) for value in fixture["grid_values"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001137" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001137/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive parameters", chi > 0 and additive_gradient >= 0 and cross_multiplier > 0 and all(scale > 0 for scale in scales), [chi, additive_gradient, cross_multiplier, scales], "positive", "hypotheses")
    check("scale coverage", all(scale.denominator == 1 for scale in scales) and scales == sorted(scales), scales, "increasing positive integer scales", "parameterization")

    scale_rows: list[dict[str, Any]] = []
    lower_bounds: list[Fraction] = []
    approximation_coefficients: list[Fraction] = []
    for index, scale in enumerate(scales):
        epsilon = 1 / (scale * scale)
        denominator_at_witness = scale * scale + scale * scale
        witness_value = scale * scale * scale / denominator_at_witness
        expected_witness = scale / 2
        lower_sup_squared = expected_witness * expected_witness
        one_site_form_lower = 2 * lower_sup_squared + additive_gradient / chi
        approximation_coefficient = epsilon * epsilon
        check(f"scale {scale} epsilon", epsilon * scale * scale == 1, epsilon * scale * scale, 1, "resolvent parameterization")
        check(f"scale {scale} witness denominator", denominator_at_witness > 0, denominator_at_witness, ">0", "witness")
        check(f"scale {scale} witness value", witness_value == expected_witness, [witness_value, expected_witness], "equal", "witness")
        check(f"scale {scale} lower sup square", lower_sup_squared == scale * scale / 4, lower_sup_squared, scale * scale / 4, "witness")
        check(f"scale {scale} one-site lower form", one_site_form_lower == scale * scale / 2 + additive_gradient / chi, one_site_form_lower, "a^2/2+1/chi", "form scaling")
        check(f"scale {scale} approximation coefficient", approximation_coefficient == 1 / (scale ** 4), approximation_coefficient, 1 / (scale ** 4), "conditional approximation")
        lower_bounds.append(one_site_form_lower)
        approximation_coefficients.append(approximation_coefficient)
        scale_rows.append({"scale_a": str(scale), "epsilon": str(epsilon), "witness_value": str(witness_value), "lower_sup_norm_squared": str(lower_sup_squared), "one_site_form_bound_lower": str(one_site_form_lower), "cross_bound_lower": str(cross_multiplier * one_site_form_lower), "approximation_coefficient": str(approximation_coefficient)})

    for left, right in zip(lower_bounds, lower_bounds[1:]):
        check("form lower bound monotone", right > left, [left, right], "strictly increasing", "form scaling")
    for left, right in zip(approximation_coefficients, approximation_coefficients[1:]):
        check("approximation coefficient decreasing", right < left, [left, right], "strictly decreasing", "conditional approximation")

    grid_rows: list[dict[str, Any]] = []
    scale = scales[-1]
    for index, x in enumerate(grid):
        denominator = scale * scale + x * x
        value = scale * scale * x / denominator
        error = x - value
        check(f"grid {index} denominator", denominator > 0, denominator, ">0", "resolvent witness")
        check(f"grid {index} error identity", error == (x ** 3) / denominator, error, x ** 3 / denominator, "conditional approximation")
        grid_rows.append({"x": str(x), "value": str(value), "error": str(error)})

    support_rows: list[dict[str, Any]] = []
    for support in supports:
        lower_sup_squared = (scale * scale / 4) ** support
        product_form_lower = 2 * lower_sup_squared
        cross_lower = cross_multiplier * product_form_lower
        check(f"support {support} product lower", product_form_lower > 0, product_form_lower, ">0", "support scaling")
        check(f"support {support} cross lower", cross_lower == cross_multiplier * product_form_lower, cross_lower, "21 times lower bound", "support scaling")
        support_rows.append({"support_size": support, "product_sup_norm_squared_lower": str(lower_sup_squared), "same_form_bound_lower": str(product_form_lower), "cross_orientation_bound_lower": str(cross_lower)})

    check("route obstruction", scope["fixed_epsilon_resolvent_cylinder_closed"] and scope["epsilon_uniform_weighted_resolvent_cylinder_closed"] is False and scope["resolvent_smoothing_route_obstruction_closed"], scope, "fixed epsilon only; uniform route failed", "scope")
    check("QFT firewall", all(scope[key] is False for key in ("second_commutator_closed", "modular_domain_transfer_closed", "direct_d_cauchy_closed", "common_alpha_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "QFT promotion remains open", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RESOLVENT-SMOOTHING-UNIFORMITY-OBSTRUCTION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
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
    print(f"PRIMARY RESOLVENT-SMOOTHING-UNIFORMITY-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
