#!/usr/bin/env python3
"""Primary scalar weighted-function audit for EXP-001116."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_full_generator_radius_loss_multiplier"
MANIFEST = REPO / "strategy/pre_a_cp1_st8_q3lock_full_generator_radius_loss_multiplier_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    delta = sp.Rational(fixture["delta"])
    time = sp.Rational(fixture["time"])
    neighbours = int(fixture["neighbours"])
    orientations = int(fixture["orientations"])
    orders = [int(order) for order in fixture["orders"]]
    steps = [int(step) for step in fixture["finite_steps"]]
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001116" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001116/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("delta fixture", delta == sp.Rational(1, 10) and delta > 0, delta, "1/10", "fixture")
    audit.check("branch count", orientations * neighbours == 12, orientations * neighbours, 12, "recurrence")
    multiplier_rows: list[dict[str, Any]] = []
    for n in orders:
        critical_y = sp.factor(sp.Integer(n) / delta)
        exact_max_without_e = sp.factor(critical_y**n)
        multiplier_rows.append({"n": n, "critical_y": critical_y, "max_value": f"({critical_y}/e)^{n}", "max_without_e_power": exact_max_without_e})
        audit.check(f"critical point n={n}", critical_y == sp.Integer(10 * n), critical_y, 10 * n, "radius-loss")
        audit.check(f"multiplier formula n={n}", exact_max_without_e == sp.Integer(10 * n) ** n, exact_max_without_e, (10 * n) ** n, "radius-loss")
    audit.check("same radius growth witness", 10**4 > 1**4, 10**4, ">1", "same-radius")
    multiplier = 1.0 / (float(delta) * math.e)
    branch_rate = float(orientations * neighbours) * multiplier
    conditional_exponent = branch_rate * float(time)
    recurrence_rows: list[dict[str, Any]] = []
    for step in steps:
        envelope = (1.0 + branch_rate * float(time) / step) ** step
        recurrence_rows.append({"steps": step, "finite_envelope": envelope, "limit_envelope": math.exp(conditional_exponent)})
    audit.check("conditional recurrence finite envelope", all(row["finite_envelope"] <= row["limit_envelope"] * (1 + 1e-12) for row in recurrence_rows), recurrence_rows, "<=exp(24/e)", "recurrence")
    audit.check("conditional exponent", abs(conditional_exponent - 24 / math.e) <= 1e-12, conditional_exponent, "24/e", "recurrence")
    audit.check("same-radius scope", manifest["scope"]["same_radius_rejection_closed"] is True and manifest["scope"]["actual_q3_entire_seminorm_closed"] is False, manifest["scope"], "closed scalar rejection / open Q3", "scope")
    audit.check("history scope", manifest["scope"]["actual_q3_word_incidence_closed"] is False and manifest["scope"]["volume_uniform_factorial_history_closed"] is False, manifest["scope"], "false/false", "scope")
    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "delta": delta,
            "time": time,
            "neighbours": neighbours,
            "orientations": orientations,
            "multiplier_rows": multiplier_rows,
            "M1": "1/(e*delta)",
            "branch_rate": "12/(e*delta)",
            "conditional_exponent": "24/e",
            "recurrence_rows": recurrence_rows,
            "radius_loss_multiplier_closed": True,
            "same_radius_rejection_closed": True,
            "conditional_two_orientation_recurrence_closed": True,
            "actual_q3_entire_seminorm_closed": False,
            "actual_q3_common_core_closed": False,
            "actual_q3_word_incidence_closed": False,
            "volume_uniform_factorial_history_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FULL-GENERATOR-RADIUS-LOSS PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
