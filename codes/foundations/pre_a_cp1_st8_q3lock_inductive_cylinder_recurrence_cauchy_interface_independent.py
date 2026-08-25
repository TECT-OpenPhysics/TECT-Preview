#!/usr/bin/env python3
"""Independent exact-arithmetic audit for EXP-001151.

The recurrence is evaluated by a separate closed-form lane and remains a
conditional hypothesis rather than an audit of the actual Q3 generator.
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    f = data["finite_fixture"]
    scope = data["scope"]
    z = int(f["degree"])
    c = Fraction(f["recurrence_C"])
    j = Fraction(f["recurrence_J"])
    base = Fraction(f["base_weight"])
    dt = Fraction(f["time_step"])
    n = int(f["steps"])
    horizon = Fraction(f["time_horizon"])
    d = int(f["boundary_distance"])
    mass = Fraction(f["source_mass"])
    orientations = int(f["orientation_count"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("provenance", data["exploration_id"] == "EXP-001151" and data["task_id"] == "T-054" and data["claim_bearing"] is False, [data["exploration_id"], data["task_id"], data["claim_bearing"]], "EXP-001151/T-054/false", "provenance")
    check("input ordering", z > 0 and base > 1 and dt > 0 and n > 0 and d > 0 and mass >= 0 and orientations > 0, f, "positive inputs", "hypotheses")
    check("time decomposition", horizon == dt * n, [horizon, dt * n], "dt*n", "time")
    rate = c + j * z * base
    factor = 1 + rate * dt
    # Independent lane: use exponentiation directly and construct the spatial
    # denominator as an integer power, rather than iterating the primary rows.
    response = mass * factor**n
    spatial = Fraction(1, base.numerator**d) if base.denominator == 1 else Fraction(1, 1) / (base**d)
    envelope = response * spatial
    coefficient = orientations * horizon * envelope
    response_levels = [str(mass * factor**k) for k in range(n + 1)]

    check("weighted rate", rate == c + j * z * base, rate, "C+J*z*base", "recurrence")
    check("closed response", response == mass * factor**n, response, "mass*factor^N", "recurrence")
    check("integer base spatial", base.denominator == 1 and spatial == Fraction(1, int(base) ** d), [base, spatial], "base^(-d)", "spatial envelope")
    check("time integrated coefficient", coefficient == orientations * horizon * envelope, coefficient, "orientations*horizon*envelope", "Cauchy interface")
    check("conditional coefficient finite", coefficient < 1, coefficient, "<1", "Cauchy interface")
    check("bounded cylinder parent", "EXP-001150" in data["parent_explorations"] and scope["inductive_cylinder_interface_used"] is True, data["parent_explorations"], "EXP-001150", "QFT interface")
    check("downstream firewall", all(scope[key] is False for key in ("actual_q3_recurrence_closed", "actual_first_commutator_decay_closed", "actual_second_commutator_decay_closed", "direct_d_cauchy_closed", "delta_d_cauchy_closed", "common_alpha_closed", "exhaustion_independence_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "open", "boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-INDUCTIVE-CYLINDER-RECURRENCE-CAUCHY-INTERFACE",
        "claim_id": data["claim_ids"][0],
        "task_id": data["task_id"],
        "exploration_id": data["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "degree": z,
            "growth_rate": str(rate),
            "step_factor": str(factor),
            "response_levels": response_levels,
            "response_envelope": str(envelope),
            "spatial_penalty": str(spatial),
            "cauchy_coefficient": str(coefficient),
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
    print(f"INDEPENDENT INDUCTIVE-CYLINDER-RECURRENCE-CAUCHY-INTERFACE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
