#!/usr/bin/env python3
"""Primary exact-polynomial obstruction audit for EXP-001134."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_raw_coordinate_product_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-raw-coordinate-product-obstruction-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def add_poly(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    return [(left[index] if index < len(left) else Fraction(0)) + (right[index] if index < len(right) else Fraction(0)) for index in range(size)]


def scale_poly(poly: list[Fraction], factor: Fraction) -> list[Fraction]:
    return [value * factor for value in poly]


def mul_poly(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            result[i + j] += first * second
    return result


def moment_poly(order: int, variance: Fraction) -> list[Fraction]:
    result = [Fraction(0)] * (order + 1)
    for centered_order in range(order + 1):
        if centered_order % 2:
            continue
        double_factorial = 1
        for value in range(1, centered_order, 2):
            double_factorial *= value
        result[order - centered_order] += Fraction(comb(order, centered_order) * double_factorial) * variance ** (centered_order // 2)
    return result


def evaluation(poly: list[Fraction], center: Fraction) -> Fraction:
    return sum(coefficient * center ** index for index, coefficient in enumerate(poly))


def leading(poly: list[Fraction]) -> tuple[int, Fraction]:
    for index in range(len(poly) - 1, -1, -1):
        if poly[index] != 0:
            return index, poly[index]
    return 0, Fraction(0)


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
    mass = Fraction(fixture["r"])
    quartic = Fraction(fixture["g"])
    shift = Fraction(fixture["per_site_shift"])
    variance = Fraction(fixture["gaussian_variance"])
    centers = [Fraction(value) for value in fixture["translated_centers"]]
    m2, m4, m6 = (moment_poly(order, variance) for order in (2, 4, 6))
    kinetic = Fraction(1, 8) / (chi * variance)
    e0 = add_poly([kinetic + shift], add_poly(scale_poly(m2, mass / 2), scale_poly(m4, quartic / 4)))
    d2 = add_poly([Fraction(1)], add_poly(scale_poly(m2, -1 / (2 * variance)), scale_poly(mul_poly([Fraction(0), Fraction(1)], m2), Fraction(0))))
    # D=1 + R*x/(2v) - x^2/(2v); expand E[D^2] directly in moments.
    d2 = add_poly([Fraction(1)], scale_poly(m2, -1 / variance))
    d2 = add_poly(d2, scale_poly(mul_poly([Fraction(0), Fraction(1)], m1 := moment_poly(1, variance)), Fraction(0)))
    # The explicit coefficient form is stable and avoids symbolic/numeric integration.
    d2 = add_poly([Fraction(1)], scale_poly(m2, -1 / variance))
    d2 = add_poly(d2, scale_poly(mul_poly([Fraction(0), Fraction(1)], m2), Fraction(1, 4) / (variance * variance)))
    d2 = add_poly(d2, scale_poly(m3 := moment_poly(3, variance), -1 / (2 * variance * variance)))
    d2 = add_poly(d2, scale_poly(m4, 1 / (4 * variance * variance)))
    # Terms containing the translated center are represented by multiplication in R.
    d2 = add_poly([Fraction(1)], scale_poly(m2, -1 / variance))
    d2 = add_poly(d2, scale_poly(mul_poly([Fraction(0), Fraction(1)], m1), 1 / variance))
    d2 = add_poly(d2, scale_poly(mul_poly([Fraction(0), Fraction(0), Fraction(1)], m2), 1 / (4 * variance * variance)))
    d2 = add_poly(d2, scale_poly(mul_poly([Fraction(0), Fraction(1)], m3), -1 / (2 * variance * variance)))
    d2 = add_poly(d2, scale_poly(m4, 1 / (4 * variance * variance)))
    weighted = add_poly(scale_poly(d2, Fraction(1, 2 * chi)), add_poly(scale_poly(m4, mass / 2), add_poly(scale_poly(m6, quartic / 4), scale_poly(m2, shift))))
    e0_degree, e0_lead = leading(e0)
    weighted_degree, weighted_lead = leading(weighted)
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001134" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001134/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("Gaussian variance", variance > 0 and chi > 0 and quartic > 0, [variance, chi, quartic], "positive", "hypotheses")
    check("form degree", e0_degree == 4 and weighted_degree == 6, [e0_degree, weighted_degree], [4, 6], "degree obstruction")
    check("leading coefficient", e0_lead == quartic / 4 and weighted_lead == quartic / 4, [e0_lead, weighted_lead], quartic / 4, "degree obstruction")
    check("asymptotic ratio coefficient", weighted_lead / e0_lead == 1, weighted_lead / e0_lead, 1, "degree obstruction")
    sample_rows: list[dict[str, Any]] = []
    for center in centers:
        denominator = evaluation(e0, center)
        numerator = evaluation(weighted, center)
        check(f"sample denominator {center}", denominator > 0, denominator, ">0", "Gaussian form")
        check(f"sample ratio growth {center}", numerator / denominator >= center * center / 2, numerator / denominator, f">={center*center/2}", "Gaussian obstruction")
        sample_rows.append({"center": str(center), "form_energy": str(denominator), "weighted_energy": str(numerator), "ratio": str(numerator / denominator)})
    check("route obstruction", scope["raw_coordinate_form_domain_invariance_closed"] is False and scope["raw_coordinate_weighted_product_bounded"] is False and scope["raw_coordinate_obstruction_closed"] is True, scope, "raw coordinate route failed", "boundary")
    check("alternative firewall", scope["bounded_lipschitz_cylinder_closed"] and scope["resolvent_smoothed_polynomial_closed"] is False, scope, "bounded class retained; smoothed route open", "boundary")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-RAW-COORDINATE-PRODUCT-OBSTRUCTION", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": compact_assertions(rows), "derived": {"form_degree": e0_degree, "weighted_degree": weighted_degree, "form_leading_coefficient": str(e0_lead), "weighted_leading_coefficient": str(weighted_lead), "asymptotic_ratio_coefficient": str(weighted_lead / e0_lead), "sample_rows": sample_rows, "raw_coordinate_form_domain_invariance_closed": False, "raw_coordinate_weighted_product_bounded": False, "raw_coordinate_obstruction_closed": True, "bounded_lipschitz_cylinder_closed": True, "resolvent_smoothed_polynomial_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY RAW-COORDINATE-PRODUCT-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
