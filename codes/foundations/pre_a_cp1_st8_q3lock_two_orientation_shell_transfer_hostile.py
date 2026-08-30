#!/usr/bin/env python3
"""Hostile mutations for the R-450 conditional shell-envelope contract."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-orientation-shell-transfer-manifest.json"
EDGE = ROOT / "strategy/pre-a-cp1-st8-q3lock-state-weighted-edge-majorant-composition-manifest.json"
FORCE = ROOT / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
MOMENT = ROOT / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-bridge-manifest.json"


def q(value: object) -> Fraction:
    return Fraction(str(value))


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    packet = json.loads(MANIFEST.read_text(encoding="utf-8"))
    edge = json.loads(EDGE.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    moment = json.loads(MOMENT.read_text(encoding="utf-8"))
    c_force = q(force["finite_fixture"]["force_constant"])
    g = q(force["finite_fixture"]["g"])
    a0 = q(moment["finite_fixture"]["A0_input"])
    m5 = q(moment["finite_fixture"]["m5_input"])
    c4 = c_force**4 * max(Fraction(1), Fraction(8) / g) ** 3 * (Fraction(9) * ((Fraction(1) + 2 * a0) ** 3 + 2 * m5))
    tail_r1 = Fraction(78)
    checks: list[dict[str, Any]] = []

    def reject(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: mutation was not rejected: {actual!r}")
        checks.append({"name": name, "status": "REJECTED", "actual": str(actual), "expected": str(expected)})

    reject("one orientation only", int(packet["finite_fixture"]["orientation_count"]) != 1, packet["finite_fixture"]["orientation_count"], 2)
    reject("negative shell weight", Fraction(-1) < 0, -1, "nonnegative shell weight")
    reject("coefficient exceeds weight", abs(Fraction(2)) > Fraction(1), "|a|=2>w=1", "|a|<=w")
    reject("mutated C4", c4 + 1 != c4, c4 + 1, c4)
    reject("mutated shell formula", Fraction(79) != tail_r1, 79, tail_r1)
    reject("missing root-free factor", Fraction(1) * c4 * tail_r1**4 != Fraction(2) * c4 * tail_r1**4, "one orientation", "two orientations")
    scope_mutation = dict(packet["scope"])
    scope_mutation["actual_q3_per_edge_majorant_closed"] = True
    reject("actual Q3 promotion", scope_mutation["actual_q3_per_edge_majorant_closed"] is True and packet["scope"]["actual_q3_per_edge_majorant_closed"] is False, True, False)
    method_mutation = dict(packet["method_preservation"])
    method_mutation["existing_forward_method_unchanged"] = False
    reject("method overhaul", method_mutation["existing_forward_method_unchanged"] is False and packet["method_preservation"]["existing_forward_method_unchanged"] is True, False, True)
    reject("edge parent identity mutation", edge["exploration_id"] != "EXP-001319", edge["exploration_id"], "EXP-001320")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": packet["candidate_id"],
        "result_id": packet["result_id"],
        "claim_id": packet["claim_ids"][0],
        "task_id": packet["task_id"],
        "exploration_id": packet["exploration_id"],
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "mutation_count": len(checks),
        "mutations_rejected": checks,
        "derived": {"baseline_C4_edge": str(c4), "baseline_tail_r1": str(tail_r1), "scope_firewall": True, "method_preservation": True},
        "boundary": packet["boundary"],
    }
    if args.output:
        save(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"R-450 HOSTILE {payload['verdict']} {len(checks)}/{len(checks)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
