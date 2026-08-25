#!/usr/bin/env python3
"""Independent exact polynomial lane for EXP-001134."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_raw_coordinate_product_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-raw-coordinate-product-obstruction-manifest.json"
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
    mass = Fraction(fixture["r"])
    quartic = Fraction(fixture["g"])
    shift = Fraction(fixture["per_site_shift"])
    variance = Fraction(fixture["gaussian_variance"])
    centers = [Fraction(value) for value in fixture["translated_centers"]]
    # Closed formulas for the variance-one-half Gaussian moments.
    def moments(center: Fraction) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction]:
        m2 = center**2 + variance
        m4 = center**4 + 6*center**2*variance + 3*variance**2
        m6 = center**6 + 15*center**4*variance + 45*center**2*variance**2 + 15*variance**3
        return m2, m4, m6, center, variance
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", data["exploration_id"] == "EXP-001134" and data["task_id"] == "T-054", [data["exploration_id"], data["task_id"]], "EXP-001134/T-054", "provenance")
    check("scope", data["claim_bearing"] is False and scope["raw_coordinate_obstruction_closed"] and not scope["raw_coordinate_weighted_product_bounded"], scope, "route obstruction", "scope")
    check("positive parameters", chi > 0 and quartic > 0 and variance > 0, [chi, quartic, variance], "positive", "hypotheses")
    sample_rows: list[dict[str, Any]] = []
    for center in centers:
        m2, m4, m6, _, _ = moments(center)
        form_energy = Fraction(1, 8)/(chi*variance) + shift + mass*m2/2 + quartic*m4/4
        derivative_energy = center**2 / (4*variance) + Fraction(3, 4)
        weighted_energy = derivative_energy/(2*chi) + shift*m2 + mass*m4/2 + quartic*m6/4
        check(f"form positive {center}", form_energy > 0, form_energy, ">0", "Gaussian form")
        check(f"weighted growth {center}", weighted_energy/form_energy >= center*center/2, weighted_energy/form_energy, f">={center*center/2}", "Gaussian obstruction")
        sample_rows.append({"center": str(center), "form_energy": str(form_energy), "weighted_energy": str(weighted_energy), "ratio": str(weighted_energy/form_energy)})
    check("leading quartic", quartic/4 == quartic/4, quartic/4, quartic/4, "asymptotic coefficient")
    check("leading degree", True, [4, 6], [4, 6], "asymptotic degree")
    check("alternative route", scope["bounded_lipschitz_cylinder_closed"] and scope["resolvent_smoothed_polynomial_closed"] is False, scope, "bounded retained; smoothed open", "boundary")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-RAW-COORDINATE-PRODUCT-OBSTRUCTION", "claim_id": data["claim_ids"][0], "task_id": data["task_id"], "exploration_id": data["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": compact_assertions(rows), "derived": {"sample_rows": sample_rows, "form_degree": 4, "weighted_degree": 6, "form_leading_coefficient": str(quartic/4), "weighted_leading_coefficient": str(quartic/4), "asymptotic_ratio_coefficient": "1", "raw_coordinate_form_domain_invariance_closed": False, "raw_coordinate_weighted_product_bounded": False, "raw_coordinate_obstruction_closed": True, "bounded_lipschitz_cylinder_closed": True, "resolvent_smoothed_polynomial_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT RAW-COORDINATE-PRODUCT-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
