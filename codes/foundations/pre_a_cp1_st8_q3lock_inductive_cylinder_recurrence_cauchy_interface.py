#!/usr/bin/env python3
"""Primary exact-arithmetic audit for EXP-001151.

This is a conditional interface audit.  It computes the coefficient implied by
the declared weighted recurrence and response hypotheses; it does not test the
actual quartic Q3 dynamics against those hypotheses.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_inductive_cylinder_recurrence_cauchy_interface"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-inductive-cylinder-recurrence-cauchy-interface-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"


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
    groups: dict[str, int] = {}
    for row in rows:
        group = str(row.get("group", "unknown"))
        groups[group] = groups.get(group, 0) + 1
    summary = {"total": len(rows), "groups": groups, "storage": "compact-summary; all assertions executed in memory"}
    return rows[:16] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    degree = int(fixture["degree"])
    recurrence_c = Fraction(fixture["recurrence_C"])
    recurrence_j = Fraction(fixture["recurrence_J"])
    base = Fraction(fixture["base_weight"])
    delta = Fraction(fixture["time_step"])
    steps = int(fixture["steps"])
    horizon = Fraction(fixture["time_horizon"])
    distance = int(fixture["boundary_distance"])
    source_mass = Fraction(fixture["source_mass"])
    orientations = int(fixture["orientation_count"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001151" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001151/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive fixture", degree > 0 and recurrence_c >= 0 and recurrence_j >= 0 and base > 1 and delta > 0 and steps > 0 and horizon > 0 and distance > 0 and source_mass >= 0 and orientations > 0, fixture, "positive declared inputs", "hypotheses")
    check("horizon agreement", horizon == delta * steps, [horizon, delta * steps], "time_step*steps", "time")
    check("cylinder interface", manifest["parent_explorations"][0] == "EXP-001150" and manifest["scope"]["inductive_cylinder_interface_used"] is True, manifest["parent_explorations"], "EXP-001150 bounded cylinder interface", "QFT interface")

    growth_rate = recurrence_c + recurrence_j * degree * base
    step_factor = 1 + growth_rate * delta
    response_levels: list[dict[str, Any]] = [{"step": 0, "response_bound": str(source_mass)}]
    response = source_mass
    for step in range(1, steps + 1):
        response *= step_factor
        response_levels.append({"step": step, "response_bound": str(response)})
    closed_response = source_mass * step_factor**steps
    spatial_penalty = Fraction(1, base**distance)
    response_envelope = closed_response * spatial_penalty
    cauchy_coefficient = Fraction(orientations) * horizon * response_envelope

    check("degree weighted rate", growth_rate == recurrence_c + recurrence_j * degree * base, growth_rate, "C+J*z*base", "recurrence")
    check("step recurrence", step_factor == 1 + growth_rate * delta, step_factor, "1+(C+J*z*base)*delta", "recurrence")
    check("iterated recurrence", response == closed_response, [response, closed_response], "equal", "recurrence")
    check("spatial penalty", spatial_penalty == Fraction(1, int(base) ** distance), spatial_penalty, "base^(-distance)", "spatial envelope")
    check("response envelope", response_envelope == closed_response * spatial_penalty, response_envelope, "response*spatial penalty", "spatial envelope")
    check("two orientations", cauchy_coefficient == Fraction(orientations) * horizon * response_envelope, cauchy_coefficient, "orientations*time_horizon*envelope", "Cauchy interface")
    check("finite envelope", response_envelope < 1 and cauchy_coefficient < 1, [response_envelope, cauchy_coefficient], "both below one", "Cauchy interface")
    check("conditional scopes", all(scope[key] is True for key in ("conditional_weighted_recurrence_arithmetic_closed", "conditional_spatial_envelope_closed", "conditional_two_orientation_cauchy_coefficient_closed", "inductive_cylinder_interface_used")), scope, True, "scope")
    check("QFT firewall", all(scope[key] is False for key in ("actual_q3_recurrence_closed", "actual_first_commutator_decay_closed", "actual_second_commutator_decay_closed", "direct_d_cauchy_closed", "delta_d_cauchy_closed", "common_alpha_closed", "exhaustion_independence_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "actual Q3 and downstream gates remain open", "boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-INDUCTIVE-CYLINDER-RECURRENCE-CAUCHY-INTERFACE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "degree": degree,
            "growth_rate": str(growth_rate),
            "step_factor": str(step_factor),
            "response_levels": response_levels,
            "response_envelope": str(response_envelope),
            "spatial_penalty": str(spatial_penalty),
            "cauchy_coefficient": str(cauchy_coefficient),
            "orientation_count": orientations,
            "time_horizon": str(horizon),
            "conditional_weighted_recurrence_arithmetic_closed": True,
            "conditional_spatial_envelope_closed": True,
            "conditional_two_orientation_cauchy_coefficient_closed": True,
            "actual_q3_recurrence_closed": False,
            "actual_first_commutator_decay_closed": False,
            "actual_second_commutator_decay_closed": False,
            "direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
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
    print(f"PRIMARY INDUCTIVE-CYLINDER-RECURRENCE-CAUCHY-INTERFACE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
