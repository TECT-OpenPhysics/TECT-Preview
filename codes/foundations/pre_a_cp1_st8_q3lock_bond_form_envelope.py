#!/usr/bin/env python3
"""Primary exact-arithmetic scalar bond-form envelope audit (EXP-001129)."""

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
SLUG = "pre_a_cp1_st8_q3lock_bond_form_envelope"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-bond-form-envelope-manifest.json"
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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    c, lam, chi, r, g = (Fraction(fixture[key]) for key in ("c", "lambda", "chi", "r", "g"))
    alpha = Fraction(fixture["alpha_bond"])
    onsite_factor = Fraction(fixture["onsite_factor"])
    constant = Fraction(fixture["bond_constant"])
    grid = [Fraction(value) for value in fixture["grid_values"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001129" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001129/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["scalar_bond_form_envelope_closed"] and scope["source_uniform_scalar_constant_closed"] and scope["volume_uniform_local_form_constant_closed"] and not scope["endpoint_to_edge_operator_inclusion_closed"], scope, "scalar form only", "scope")

    def bond(x: Fraction, y: Fraction) -> Fraction:
        difference = x - y
        return c * difference * difference / 2 + lam * difference * difference * (x * x + y * y) / 4

    def upper_coordinate(x: Fraction, y: Fraction) -> Fraction:
        return c * (x * x + y * y) + lam * (x**4 + y**4)

    def auxiliary(x: Fraction, p: Fraction) -> Fraction:
        return p * p / (2 * chi) + g * x**4 / 4

    def onsite(x: Fraction, p: Fraction) -> Fraction:
        return p * p / (2 * chi) + r * x * x / 2 + g * x**4 / 4

    check("coefficient alpha", alpha == 1 + 4 * lam / g, alpha, 1 + 4 * lam / g, "coefficients")
    check("onsite factor", onsite_factor == 2, onsite_factor, 2, "coefficients")
    square_constant = r * r / (4 * (g / 4))
    check("bond constant", constant == alpha * onsite_factor * square_constant + 2 * c * c / g, constant, alpha * onsite_factor * square_constant + 2 * c * c / g, "coefficients")

    row_count = 0
    maximum_slack = {"coordinate": Fraction(0), "auxiliary": Fraction(0), "onsite": Fraction(0), "full": Fraction(0)}
    for x, y, px, py in product(grid, grid, grid, grid):
        b = bond(x, y)
        coordinate = upper_coordinate(x, y)
        aux_bound = alpha * (auxiliary(x, px) + auxiliary(y, py)) + 2 * c * c / g
        onsite_bound = onsite_factor * (onsite(x, px) + onsite(y, py)) + 2 * square_constant
        full_bound = alpha * onsite_factor * (onsite(x, px) + onsite(y, py)) + constant
        slacks = {"coordinate": coordinate - b, "auxiliary": aux_bound - coordinate, "onsite": onsite_bound - (auxiliary(x, px) + auxiliary(y, py)), "full": full_bound - b}
        check(f"grid row {row_count} coordinate", slacks["coordinate"] >= 0, slacks["coordinate"], ">=0", "polynomial domination")
        check(f"grid row {row_count} auxiliary", slacks["auxiliary"] >= 0, slacks["auxiliary"], ">=0", "polynomial domination")
        check(f"grid row {row_count} onsite", slacks["onsite"] >= 0, slacks["onsite"], ">=0", "square completion")
        check(f"grid row {row_count} full", slacks["full"] >= 0, slacks["full"], ">=0", "full envelope")
        for key, slack in slacks.items():
            if slack > maximum_slack[key]:
                maximum_slack[key] = slack
        row_count += 1

    check("grid coverage", row_count == len(grid) ** 4, row_count, len(grid) ** 4, "grid")
    check("exact envelope constants", constant == Fraction(304, 45) and alpha == Fraction(5, 3), [constant, alpha], [Fraction(304, 45), Fraction(5, 3)], "coefficients")
    check("scope remains form-level", not scope["quadratic_form_common_core_lift_closed"] and not scope["endpoint_to_edge_operator_inclusion_closed"], scope, "open operator gate", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-BOND-FORM-ENVELOPE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"grid_rows": row_count, "alpha_bond": str(alpha), "onsite_factor": str(onsite_factor), "bond_constant": str(constant), "maximum_slack": {key: str(value) for key, value in maximum_slack.items()}, "scalar_bond_form_envelope_closed": True, "source_uniform_scalar_constant_closed": True, "volume_uniform_local_form_constant_closed": True, "quadratic_form_common_core_lift_closed": False, "endpoint_to_edge_operator_inclusion_closed": False, "common_alpha_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY BOND-FORM-ENVELOPE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
