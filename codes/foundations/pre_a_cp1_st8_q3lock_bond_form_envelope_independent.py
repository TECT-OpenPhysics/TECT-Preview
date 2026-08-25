#!/usr/bin/env python3
"""Independent exact-arithmetic lane for EXP-001129."""

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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    c = Fraction(fixture["c"])
    lam = Fraction(fixture["lambda"])
    chi = Fraction(fixture["chi"])
    mass = Fraction(fixture["r"])
    quartic = Fraction(fixture["g"])
    alpha = Fraction(fixture["alpha_bond"])
    factor = Fraction(fixture["onsite_factor"])
    constant = Fraction(fixture["bond_constant"])
    grid = tuple(Fraction(value) for value in fixture["grid_values"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001129" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001129/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["scalar_bond_form_envelope_closed"] and scope["source_uniform_scalar_constant_closed"] and not scope["endpoint_to_edge_operator_inclusion_closed"], scope, "scalar form only", "scope")

    def bond_value(x: Fraction, y: Fraction) -> Fraction:
        d = x - y
        return c * d * d / 2 + lam * d * d * (x * x + y * y) / 4

    def coordinate_majorant(x: Fraction, y: Fraction) -> Fraction:
        return c * (x * x + y * y) + lam * (x**4 + y**4)

    def auxiliary_value(x: Fraction, momentum: Fraction) -> Fraction:
        return momentum * momentum / (2 * chi) + quartic * x**4 / 4

    def onsite_value(x: Fraction, momentum: Fraction) -> Fraction:
        return momentum * momentum / (2 * chi) + mass * x * x / 2 + quartic * x**4 / 4

    square_constant = mass * mass / quartic
    check("coefficient alpha", alpha == 1 + 4 * lam / quartic, alpha, 1 + 4 * lam / quartic, "coefficients")
    check("onsite factor", factor == 2, factor, 2, "coefficients")
    check("square completion constant", square_constant == Fraction(5, 3), square_constant, Fraction(5, 3), "coefficients")
    derived_constant = alpha * factor * square_constant + 2 * c * c / quartic
    check("bond constant", constant == derived_constant, constant, derived_constant, "coefficients")

    row_count = 0
    minimum_slack = {"coordinate": None, "auxiliary": None, "onsite": None, "full": None}
    for x, y, momentum_x, momentum_y in product(grid, repeat=4):
        b = bond_value(x, y)
        coordinate = coordinate_majorant(x, y)
        auxiliary_bound = alpha * (auxiliary_value(x, momentum_x) + auxiliary_value(y, momentum_y)) + 2 * c * c / quartic
        auxiliary_pair = auxiliary_value(x, momentum_x) + auxiliary_value(y, momentum_y)
        onsite_bound = factor * (onsite_value(x, momentum_x) + onsite_value(y, momentum_y)) + factor * square_constant
        full_bound = alpha * factor * (onsite_value(x, momentum_x) + onsite_value(y, momentum_y)) + constant
        slack = {"coordinate": coordinate - b, "auxiliary": auxiliary_bound - coordinate, "onsite": onsite_bound - auxiliary_pair, "full": full_bound - b}
        check(f"grid row {row_count} coordinate", slack["coordinate"] >= 0, slack["coordinate"], ">=0", "polynomial domination")
        check(f"grid row {row_count} auxiliary", slack["auxiliary"] >= 0, slack["auxiliary"], ">=0", "polynomial domination")
        check(f"grid row {row_count} onsite", slack["onsite"] >= 0, slack["onsite"], ">=0", "square completion")
        check(f"grid row {row_count} full", slack["full"] >= 0, slack["full"], ">=0", "full envelope")
        for key, value in slack.items():
            if minimum_slack[key] is None or value < minimum_slack[key]:
                minimum_slack[key] = value
        row_count += 1

    check("grid coverage", row_count == len(grid) ** 4, row_count, len(grid) ** 4, "grid")
    check("exact constants", alpha == Fraction(5, 3) and constant == Fraction(304, 45), [alpha, constant], [Fraction(5, 3), Fraction(304, 45)], "coefficients")
    check("operator gate remains open", scope["quadratic_form_common_core_lift_closed"] is False and scope["endpoint_to_edge_operator_inclusion_closed"] is False, scope, "open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-BOND-FORM-ENVELOPE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"grid_rows": row_count, "alpha_bond": str(alpha), "onsite_factor": str(factor), "bond_constant": str(constant), "minimum_slack": {key: str(value) for key, value in minimum_slack.items()}, "scalar_bond_form_envelope_closed": True, "source_uniform_scalar_constant_closed": True, "volume_uniform_local_form_constant_closed": True, "quadratic_form_common_core_lift_closed": False, "endpoint_to_edge_operator_inclusion_closed": False, "common_alpha_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT BOND-FORM-ENVELOPE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
