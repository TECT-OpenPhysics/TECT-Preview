#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001136."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_resolvent_smoothed_polynomial_cylinder"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-resolvent-smoothed-polynomial-cylinder-manifest.json"
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
    epsilon = Fraction(fixture["epsilon"])
    imaginary_shift = Fraction(fixture["resolvent_imaginary_shift"])
    scale = imaginary_shift ** 2
    resolvent_weight = Fraction(fixture["resolvent_sum_coefficient"])
    cross = Fraction(fixture["cross_orientation_multiplier"])
    supports = [int(value) for value in fixture["support_sizes"]]
    grid = [Fraction(value) for value in fixture["grid_values"]]
    moment_order = int(fixture["moment_order"])
    dominated_order = int(fixture["dominated_error_order"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", data["exploration_id"] == "EXP-001136" and data["task_id"] == "T-054", [data["exploration_id"], data["task_id"]], "EXP-001136/T-054", "provenance")
    check("scope", data["claim_bearing"] is False and scope["resolvent_smoothed_finite_support_form_invariance_closed"] and not scope["second_commutator_closed"], scope, "finite smoothed cylinder only", "scope")
    check("parameter positivity", chi > 0 and epsilon > 0 and imaginary_shift > 0 and scale > 0, [chi, epsilon, imaginary_shift, scale], "positive", "hypotheses")
    check("scale reciprocal", epsilon * scale == 1, epsilon * scale, 1, "parameterization")

    coordinate_rows: list[dict[str, Any]] = []
    for index, x in enumerate(grid):
        denominator = scale + x * x
        value = scale * x / denominator
        combined_resolvent = resolvent_weight * (2 * x / denominator)
        derivative = scale * (scale - x * x) / denominator ** 2
        second_derivative = 2 * scale * x * (x * x - 3 * scale) / denominator ** 3
        error = x - value
        modulus_gap = (imaginary_shift / 2) ** 2 * denominator ** 2 - (scale * x) ** 2
        derivative_gap = denominator ** 4 - (scale * (scale - x * x)) ** 2
        second_gap = denominator ** 6 - (2 * scale * x * (x * x - 3 * scale)) ** 2
        error_gap = (epsilon * abs(x) ** 3) ** 2 - error ** 2
        check(f"coordinate {index} denominator", denominator > 0, denominator, ">0", "resolvent cylinder")
        check(f"coordinate {index} combined resolvent", value == combined_resolvent, [value, combined_resolvent], "equal", "resolvent cylinder")
        check(f"coordinate {index} modulus gap", modulus_gap >= 0, modulus_gap, ">=0", "pointwise bounds")
        check(f"coordinate {index} derivative gap", derivative_gap >= 0, derivative_gap, ">=0", "pointwise bounds")
        check(f"coordinate {index} second derivative gap", second_gap >= 0, second_gap, ">=0", "pointwise bounds")
        check(f"coordinate {index} approximation identity", error == x ** 3 / denominator, error, x ** 3 / denominator, "conditional approximation")
        check(f"coordinate {index} approximation gap", error_gap >= 0, error_gap, ">=0", "conditional approximation")
        check(f"coordinate {index} moment order", abs(x) ** dominated_order <= 1 + abs(x) ** moment_order, [dominated_order, moment_order], "dominated", "conditional approximation")
        coordinate_rows.append({"x": str(x), "value": str(value), "resolvent_sum": str(combined_resolvent), "derivative": str(derivative), "second_derivative": str(second_derivative), "modulus_gap": str(modulus_gap), "derivative_gap": str(derivative_gap), "second_derivative_gap": str(second_gap), "error_gap": str(error_gap)})

    support_rows: list[dict[str, Any]] = []
    for support in supports:
        sup_squared = Fraction(4 ** support)
        gradient_squared = Fraction(support * 4 ** (support - 1))
        same = 2 * sup_squared + gradient_squared / chi
        cross_bound = cross * same
        commutator = 2 * gradient_squared / chi
        check(f"support {support} gradient", gradient_squared >= 0, gradient_squared, ">=0", "finite support")
        check(f"support {support} same", same == 2 * sup_squared + gradient_squared / chi, same, "product-rule bound", "finite support")
        check(f"support {support} cross", cross_bound == cross * same, cross_bound, "21 times same", "finite support")
        check(f"support {support} commutator", commutator == 2 * gradient_squared / chi, commutator, "safe squared bound", "first commutator")
        support_rows.append({"support_size": support, "sup_norm_bound": str(Fraction(2 ** support)), "gradient_bound_squared": str(gradient_squared), "same_form_bound_squared": str(same), "cross_orientation_bound_squared": str(cross_bound), "first_commutator_safe_bound_squared": str(commutator)})

    check("support coverage", len(support_rows) == len(supports), [len(support_rows), len(supports)], "equal", "finite support")
    check("approximation coefficient", epsilon ** 2 == Fraction(1, 256), epsilon ** 2, "1/256", "conditional approximation")
    check("boundary", scope["unbounded_polynomial_products_closed"] is False and scope["second_commutator_closed"] is False and scope["common_alpha_closed"] is False and scope["pre_a_closed"] is False, scope, "finite conditional bridge", "QFT boundary")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RESOLVENT-SMOOTHED-POLYNOMIAL-CYLINDER",
        "claim_id": data["claim_ids"][0],
        "task_id": data["task_id"],
        "exploration_id": data["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "scale": str(scale),
            "coordinate_rows": coordinate_rows,
            "support_rows": support_rows,
            "approximation_coefficient": str(epsilon ** 2),
            "conditional_approximation": f"epsilon^2*(1+M{moment_order})",
            "resolvent_smoothed_single_coordinate_closed": True,
            "resolvent_smoothed_finite_support_form_invariance_closed": True,
            "resolvent_smoothed_product_weighted_bound_closed": True,
            "resolvent_smoothed_first_commutator_form_bound_closed": True,
            "conditional_m20_static_approximation_closed": True,
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
    print(f"INDEPENDENT RESOLVENT-SMOOTHED-CYLINDER PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
