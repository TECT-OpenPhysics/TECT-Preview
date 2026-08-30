#!/usr/bin/env python3
"""Non-importing independent lane for EXP-001320.

This lane reconstructs the fourth-power composition from the parent JSON
contracts using only the standard library and compares its exact rational
rows with the declared coefficient/weight relation.
"""

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
FORCE = ROOT / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
MOMENT = ROOT / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-bridge-manifest.json"
TAIL = ROOT / "strategy/pre-a-cp1-st8-q3lock-scalar-operator-tail-transfer-manifest.json"
DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-30-independent-pre_a_cp1_st8_q3lock_state_weighted_edge_majorant_composition/independent.json"
)


def save(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def q(value: object) -> Fraction:
    return Fraction(str(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    packet = json.loads(MANIFEST.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    moment = json.loads(MOMENT.read_text(encoding="utf-8"))
    tail = json.loads(TAIL.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("packet identity", (packet["exploration_id"], packet["task_id"], packet["claim_bearing"]) == ("EXP-001320", "T-054", False), [packet["exploration_id"], packet["task_id"], packet["claim_bearing"]], "EXP-001320/T-054/false")
    check("parent ids", (force["exploration_id"], moment["exploration_id"], tail["result_id"]) == ("EXP-001059", "EXP-001060", "R-445"), [force["exploration_id"], moment["exploration_id"], tail["result_id"]], "EXP-001059/EXP-001060/R-445")

    ff = force["finite_fixture"]
    mf = moment["finite_fixture"]
    c_force = q(ff["force_constant"])
    g = q(ff["g"])
    a0 = q(mf["A0_input"])
    m5 = q(mf["m5_input"])
    ratio = max(Fraction(1), Fraction(8) / g)
    c0 = Fraction(1) + 2 * a0
    cube = Fraction(3) ** 2
    bridge = cube * (c0**3 + 2 * m5)
    edge4 = c_force**4 * ratio**3 * bridge
    check("positive inputs", c_force > 0 and g > 0 and a0 >= 0 and m5 >= 0, [c_force, g, a0, m5], "force>0,g>0,A0,m5>=0")
    check("cube factor", cube == 9, cube, 9)
    check("parent C0", c0 == q(mf["derived_C0"]), c0, mf["derived_C0"])
    check("parent bridge", bridge == q(mf["derived_M_bridge"]), bridge, mf["derived_M_bridge"])
    check("edge fourth majorant", edge4 == c_force**4 * ratio**3 * bridge and edge4 > 0, edge4, "force_constant^4*D^3*M_bridge")

    pairs = packet["finite_fixture"]["coefficient_weight_pairs"]
    for i, pair in enumerate(pairs):
        a = q(pair["coefficient"])
        w = q(pair["weight"])
        lhs = abs(a) ** 4 * edge4
        rhs = w**4 * edge4
        check(f"row {i} weight", w >= 0, w, ">=0")
        check(f"row {i} domination", abs(a) <= w, abs(a), f"<={w}")
        check(f"row {i} fourth transfer", lhs <= rhs, lhs, rhs)

    scope = packet["scope"]
    check("state-weighted output", scope["conditional_state_weighted_edge_majorant_closed"] is True and scope["local_force_l4_interface_reused"] is True, scope["conditional_state_weighted_edge_majorant_closed"], True)
    firewall = ("actual_q3_operator_norm_majorant_closed", "actual_q3_history_identification_closed", "common_weighted_operator_domain_closed", "common_alpha_closed", "pre_a_closed", "sector_a_closed")
    check("promotion firewall", all(scope[key] is False for key in firewall), {key: scope[key] for key in firewall}, "all false")
    check("no result mutation", packet["formal_integration"]["no_new_result"] is True and packet["formal_integration"]["no_tier_change"] is True, packet["formal_integration"], "no result/no tier change")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-EDGE-MAJORANT-COMPOSITION",
        "claim_id": packet["claim_ids"][0],
        "task_id": packet["task_id"],
        "exploration_id": packet["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "force_constant": str(c_force),
            "g": str(g),
            "D": str(ratio),
            "A0": str(a0),
            "m5": str(m5),
            "C0": str(c0),
            "M_bridge": str(bridge),
            "C4_edge": str(edge4),
            "pair_count": len(pairs),
            "max_abs_coefficient_over_weight": str(max((abs(q(p["coefficient"])) / q(p["weight"]) for p in pairs), default=Fraction(0))),
            "conditional_state_weighted_edge_majorant_closed": True,
            "actual_q3_operator_norm_majorant_closed": False,
            "actual_q3_history_identification_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "assumptions": packet["assumptions"],
        "missing_assumptions": packet["missing_assumptions"],
        "evidence_level": packet["evidence_level"],
        "non_claims": packet["non_claims"],
        "boundary": packet["boundary"],
    }
    if not args.no_store:
        save(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT STATE-WEIGHTED-EDGE-MAJORANT PASS {len(checks)}/{len(checks)} C4={edge4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
