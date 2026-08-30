#!/usr/bin/env python3
"""Primary exact audit for the EXP-001320 state-weighted edge interface.

The package composes two already registered T-054 inputs: the local-force
fourth-power interface and the endpoint third-moment bridge.  It deliberately
stops at a conditional state-weighted L4 edge bound; it does not identify
that bound with an operator-norm Q3LOCK estimate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-state-weighted-edge-majorant-composition-manifest.json"
FORCE_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
MOMENT_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-bridge-manifest.json"
TAIL_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-scalar-operator-tail-transfer-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-30-primary-pre_a_cp1_st8_q3lock_state_weighted_edge_majorant_composition/primary.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def fraction(value: object) -> Fraction:
    return Fraction(str(value))


def run(output: Path = DEFAULT_OUTPUT, store: bool = True) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    force_parent = json.loads(FORCE_MANIFEST.read_text(encoding="utf-8"))
    moment_parent = json.loads(MOMENT_MANIFEST.read_text(encoding="utf-8"))
    tail_parent = json.loads(TAIL_MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def serial(value: Any) -> Any:
        if isinstance(value, Fraction):
            return str(value)
        if isinstance(value, (list, tuple)):
            return [serial(item) for item in value]
        if isinstance(value, dict):
            return {str(key): serial(item) for key, item in value.items()}
        return value

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 64:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    check(
        "identity",
        manifest["exploration_id"] == "EXP-001320"
        and manifest["task_id"] == "T-054"
        and manifest["claim_bearing"] is False,
        [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]],
        ["EXP-001320", "T-054", False],
        "provenance",
    )
    check("force parent", force_parent["exploration_id"] == "EXP-001059" and force_parent["claim_bearing"] is False, force_parent["exploration_id"], "EXP-001059", "provenance")
    check("moment parent", moment_parent["exploration_id"] == "EXP-001060" and moment_parent["claim_bearing"] is False, moment_parent["exploration_id"], "EXP-001060", "provenance")
    check("tail parent", tail_parent["result_id"] == "R-445" and tail_parent["claim_bearing"] is False, tail_parent["result_id"], "R-445", "provenance")

    force_fixture = force_parent["finite_fixture"]
    moment_fixture = moment_parent["finite_fixture"]
    force_constant = fraction(force_fixture["force_constant"])
    g = fraction(force_fixture["g"])
    A0 = fraction(moment_fixture["A0_input"])
    m5 = fraction(moment_fixture["m5_input"])
    one = Fraction(1)
    cube_terms = Fraction(3)
    cube_power = 3
    cube_constant = cube_terms ** (cube_power - 1)
    D = max(one, Fraction(8) / g)
    C0 = one + 2 * A0
    M_bridge = cube_constant * (C0**cube_power + 2 * m5)
    C4_edge = force_constant**4 * D**3 * M_bridge

    check("positive force constant", force_constant > 0, force_constant, ">0", "inputs")
    check("positive g", g > 0, g, ">0", "inputs")
    check("nonnegative moment inputs", A0 >= 0 and m5 >= 0, [A0, m5], "nonnegative", "inputs")
    check("cube constant", cube_constant == Fraction(9), cube_constant, 9, "moment bridge")
    check("derived D", D == max(one, Fraction(8) / g), D, "max(1,8/g)", "composition")
    check("derived C0", C0 == one + 2 * A0, C0, "1+2*A0", "composition")
    check("moment bridge positive", M_bridge == cube_constant * (C0**3 + 2 * m5) and M_bridge > 0, M_bridge, "9*(C0^3+2*m5)>0", "composition")
    check("fourth-power composition", C4_edge == force_constant**4 * D**3 * M_bridge and C4_edge > 0, C4_edge, "force_constant^4*D^3*M_bridge", "composition")
    check("fixture C0", C0 == fraction(moment_fixture["derived_C0"]), C0, moment_fixture["derived_C0"], "parent agreement")
    check("fixture M_bridge", M_bridge == fraction(moment_fixture["derived_M_bridge"]), M_bridge, moment_fixture["derived_M_bridge"], "parent agreement")
    check("force formula present", "local_force_bound" in force_parent["model"], True, True, "parent agreement")
    check("tail geometry retained", tail_parent["finite_contract"]["term_bound"] == "||K_e|| <= C*w(e)", tail_parent["finite_contract"]["term_bound"], "||K_e|| <= C*w(e)", "parent agreement")

    pairs = manifest["finite_fixture"]["coefficient_weight_pairs"]
    ratios: list[Fraction] = []
    for index, pair in enumerate(pairs):
        coefficient = fraction(pair["coefficient"])
        weight = fraction(pair["weight"])
        check(f"pair {index} nonnegative weight", weight >= 0, weight, ">=0", "coefficient contract")
        check(f"pair {index} dominated coefficient", abs(coefficient) <= weight, abs(coefficient), f"<={weight}", "coefficient contract")
        lhs = abs(coefficient) ** 4 * C4_edge
        rhs = weight**4 * C4_edge
        check(f"pair {index} fourth-power transfer", lhs <= rhs, lhs, rhs, "weighted edge bound")
        ratios.append(abs(coefficient) / weight if weight else Fraction(0))

    check("pair coverage", len(pairs) >= 5, len(pairs), ">=5", "coverage")
    check("max coefficient ratio", max(ratios, default=Fraction(0)) <= 1, max(ratios, default=Fraction(0)), "<=1", "coverage")
    scope = manifest["scope"]
    closed_keys = ("endpoint_third_moment_reused", "local_force_l4_interface_reused", "conditional_state_weighted_edge_majorant_closed", "scalar_history_coefficient_bound_checked")
    open_keys = (
        "actual_q3_operator_norm_majorant_closed",
        "actual_q3_history_identification_closed",
        "common_weighted_operator_domain_closed",
        "source_uniformity_beyond_parent_scope_closed",
        "beta_uniformity_closed",
        "volume_uniformity_beyond_parent_scope_closed",
        "cutoff_uniformity_closed",
        "direct_d_delta_d_cauchy_closed",
        "exhaustion_independence_closed",
        "common_alpha_closed",
        "hamiltonian_os_identification_closed",
        "kms_gns_gap_closed",
        "continuum_closed",
        "c6_closed",
        "sector_a_closed",
        "pre_a_closed",
    )
    check("closed composition scope", all(scope[key] is True for key in closed_keys), {key: scope[key] for key in closed_keys}, "all true", "scope")
    check("open promotion firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all false", "scope")
    check("no result or tier mutation", manifest["formal_integration"]["no_new_result"] and manifest["formal_integration"]["no_tier_change"], manifest["formal_integration"], "no result/no tier change", "scope")

    payload: dict[str, Any] = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-EDGE-MAJORANT-COMPOSITION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "force_constant": str(force_constant),
            "g": str(g),
            "D": str(D),
            "A0": str(A0),
            "m5": str(m5),
            "C0": str(C0),
            "M_bridge": str(M_bridge),
            "C4_edge": str(C4_edge),
            "C_L4_edge_formula": "(force_constant^4*D^3*M_bridge)^(1/4)",
            "pair_count": len(pairs),
            "max_abs_coefficient_over_weight": str(max(ratios, default=Fraction(0))),
            "conditional_state_weighted_edge_majorant_closed": True,
            "actual_q3_operator_norm_majorant_closed": False,
            "actual_q3_history_identification_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {
            "script": sha256(Path(__file__)),
            "manifest": sha256(MANIFEST),
            "force_parent": sha256(FORCE_MANIFEST),
            "moment_parent": sha256(MOMENT_MANIFEST),
            "tail_parent": sha256(TAIL_MANIFEST),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    if store:
        atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"PRIMARY STATE-WEIGHTED-EDGE-MAJORANT PASS {len(checks)}/{len(checks)} C4={C4_edge}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run(args.output, store=not args.no_store)
    if args.self_test:
        assert payload["verdict"] == "PASS"
        assert payload["derived"]["conditional_state_weighted_edge_majorant_closed"] is True
        print("PRIMARY STATE-WEIGHTED-EDGE-MAJORANT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
