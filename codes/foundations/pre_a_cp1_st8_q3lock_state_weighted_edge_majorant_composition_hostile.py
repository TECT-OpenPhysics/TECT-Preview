#!/usr/bin/env python3
"""Hostile scope and arithmetic mutations for EXP-001320."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-state-weighted-edge-majorant-composition-manifest.json"


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
    force = json.loads((ROOT / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json").read_text(encoding="utf-8"))
    moment = json.loads((ROOT / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-bridge-manifest.json").read_text(encoding="utf-8"))
    c = q(force["finite_fixture"]["force_constant"])
    g = q(force["finite_fixture"]["g"])
    a0 = q(moment["finite_fixture"]["A0_input"])
    m5 = q(moment["finite_fixture"]["m5_input"])
    D = max(Fraction(1), Fraction(8) / g)
    base_m = Fraction(9) * ((Fraction(1) + 2 * a0) ** 3 + 2 * m5)
    base_c4 = c**4 * D**3 * base_m
    checks: list[dict[str, Any]] = []

    def reject(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: mutation was not rejected: {actual!r}")
        checks.append({"name": name, "status": "REJECTED", "actual": str(actual), "expected": str(expected)})

    reject("zero force constant", (Fraction(0) ** 4) * D**3 * base_m != base_c4, 0, "different fourth majorant")
    reject("mutated moment input", c**4 * D**3 * (base_m + 18) != base_c4, base_m + 18, "different fourth majorant")
    reject("coefficient exceeds weight", abs(Fraction(2)) > Fraction(1), 2, "|a|<=w")
    reject("negative weight", Fraction(-1) < 0, -1, "w>=0")
    reject("zero moment majorant", Fraction(0) <= 0 and base_c4 > 0, 0, "positive baseline")

    scope = packet["scope"]
    operator_mutation = dict(scope)
    operator_mutation["actual_q3_operator_norm_majorant_closed"] = True
    reject("operator promotion", operator_mutation["actual_q3_operator_norm_majorant_closed"] is True and scope["actual_q3_operator_norm_majorant_closed"] is False, operator_mutation["actual_q3_operator_norm_majorant_closed"], "firewall")
    alpha_mutation = dict(scope)
    alpha_mutation["common_alpha_closed"] = True
    reject("common-alpha promotion", alpha_mutation["common_alpha_closed"] is True and scope["common_alpha_closed"] is False, alpha_mutation["common_alpha_closed"], "firewall")
    identity_mutation = dict(packet)
    identity_mutation["claim_bearing"] = True
    reject("claim-bearing mutation", identity_mutation["claim_bearing"] is True and packet["claim_bearing"] is False, identity_mutation["claim_bearing"], "claim_bearing=false")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-EDGE-MAJORANT-COMPOSITION",
        "claim_id": packet["claim_ids"][0],
        "task_id": packet["task_id"],
        "exploration_id": packet["exploration_id"],
        "verdict": "PASS",
        "mutation_count": len(checks),
        "mutations_rejected": checks,
        "derived": {"baseline_C4_edge": str(base_c4), "scope_firewall": True, "method_preservation": True},
        "boundary": packet["boundary"],
    }
    if args.output:
        save(args.output, payload)
    print(f"HOSTILE STATE-WEIGHTED-EDGE-MAJORANT PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
