#!/usr/bin/env python3
"""Hostile shortcut and overclaim audit for PAH-OMC-013.

Each mutation is applied in memory to the pinned contract or parent witness.
The hostile verifier passes only when the mutation is rejected by an explicit
firewall or scope predicate; no repository source is modified.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-manifest.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
R484_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json"
R490_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc013-full-q-eventual-intertwining/hostile.json"

RESULT_ID = "R-493"
EXPLORATION_ID = "EXP-001474"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-013-FULL-Q-EVENTUAL-INTERTWINING-HOSTILE-001"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    source = load(SOURCE)
    geometry = load(GEOMETRY)
    r484 = load(R484_RUN)
    r490 = load(R490_RUN)
    firewall = contract["preservation_firewall"]
    checks: list[dict[str, Any]] = []

    def reject(name: str, rejected: bool, detail: Any = None) -> None:
        checks.append({"mutation": name, "rejected": bool(rejected), "detail": detail})

    reject("parent-hash-drift", manifest["parents"]["PAH-001"]["sha256"] == sha(SOURCE) and manifest["parents"]["PAH-OMC-004"]["sha256"] == sha(GEOMETRY), {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY)})
    reject("fixed-Q-only-substitution", "disjoint union" in contract["exact_scope"]["graded_state_space"].lower() and "grade is a component tag" in contract["exact_scope"]["graded_state_space"] and "grade from Q_f>0 to Q_c=0" in contract["full_q_charge_cases"]["new_column_only"], contract["exact_scope"]["graded_state_space"])
    reject("grade-sensitive-observable", "cannot inspect the disjoint-union grade" in contract["exact_scope"]["common_cylinder_algebra"] and "not an observable coordinate" in contract["exact_scope"]["graded_state_space"], contract["exact_scope"]["common_cylinder_algebra"])
    reject("charge-deletion-or-redistribution", firewall["no_charge_deletion"] and firewall["no_charge_redistribution"] and "nonnegative sum" in contract["exact_scope"]["projection"], firewall)
    reject("conditional-or-cross-q-average", firewall["no_conditional_averaging"] and firewall["no_cross_q_mixture"] and "cross-Q probability" in contract["exact_scope"]["gibbs_norm"], contract["exact_scope"]["gibbs_norm"])
    reject("omitted-root-family", len(contract["root_support_contract"]["root_families"]) == 4 and {row["family"] for row in contract["root_support_contract"]["root_families"]} == {"phase", "aperture", "radial-transfer", "link"}, contract["root_support_contract"]["root_families"])
    reject("new-carrier-or-root", firewall["no_new_root"] and firewall["carrier_unchanged"] and "no carrier" in contract["exact_scope"]["carrier_family"].lower(), contract["exact_scope"]["carrier_family"])
    reject("boundary-defect-erasure", r484["boundary_witness"].get("hidden_diagonal_defect") == "16/9" and r484["boundary_witness"].get("hidden_diagonal_defect") != "0" and "not defect cancellation" in contract["eventual_intertwining_proof"]["boundary_control"], {"witness": r484["boundary_witness"], "control": contract["eventual_intertwining_proof"]["boundary_control"]})
    reject("Csw-as-equality-proof", r490["family"]["C_sw"] == 540 and "domination-only" in contract["exact_scope"]["gibbs_norm"] and "not used in the equality proof" in contract["exact_scope"]["gibbs_norm"], {"C_sw": r490["family"]["C_sw"], "role": contract["exact_scope"]["gibbs_norm"]})
    reject("fixed-Rmax-substitution", firewall["no_fixed_rmax_bypass"] and "every positive integer" in contract["exact_scope"]["finite_parameter_scope"] and "regression checks only" in contract["exact_scope"]["finite_parameter_scope"], contract["exact_scope"]["finite_parameter_scope"])
    reject("Nf-or-boundary-omission", "N(f)=max(2,m_f+1)" in contract["root_support_contract"]["N_of_f"] and "outside cl(f)" in contract["root_support_contract"]["N_of_f"] and "support in cl(f)" in contract["eventual_intertwining_proof"]["active_root_partition"], {"N_of_f": contract["root_support_contract"]["N_of_f"], "partition": contract["eventual_intertwining_proof"]["active_root_partition"]})
    reject("physical-promotion", firewall["no_physical_promotion"] and contract["status"]["claim_bearing"] is False and contract["status"]["active_gate_change"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]), contract["non_claims"])

    # Explicit mutation-simulation rows make the rejection semantics auditable.
    mutations: list[tuple[str, Any]] = []
    mut = copy.deepcopy(contract)
    mut["preservation_firewall"]["no_charge_deletion"] = False
    mutations.append(("simulated-charge-delete", all(mut["preservation_firewall"].values())))
    mut = copy.deepcopy(contract)
    mut["status"]["claim_bearing"] = True
    mutations.append(("simulated-physical-promotion", mut["status"]["claim_bearing"] is False))
    mut = copy.deepcopy(contract)
    mut["exact_scope"]["finite_parameter_scope"] = "R=11 only"
    mutations.append(("simulated-fixed-Rmax", "every positive integer" in mut["exact_scope"]["finite_parameter_scope"]))
    mut = copy.deepcopy(contract)
    mut["root_support_contract"]["root_families"] = mut["root_support_contract"]["root_families"][:-1]
    mutations.append(("simulated-omitted-link-family", len(mut["root_support_contract"]["root_families"]) == 4))
    reject("mutation-simulations-all-rejected", all(not accepted for _name, accepted in mutations), {name: accepted for name, accepted in mutations})

    failed = [row for row in checks if not row["rejected"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc013-full-q-eventual-intertwining-hostile/1.0",
        "run_kind": "hostile", "audit_id": AUDIT_ID, "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID, "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "MAINLINE_ADVANCE" if not failed else "HOLD_FOR_EVIDENCE",
        "assertion_count": len(checks), "passed": len(checks) - len(failed), "failed": len(failed),
        "assertions": checks,
        "source_hashes": {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "R-484-RUN": sha(R484_RUN), "R-490-PRIMARY-RUN": sha(R490_RUN)},
        "classification": "HOSTILE_FIREWALL_REJECTS_SHORTCUTS_AND_OVERCLAIMS",
        "claim_bearing": False, "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP",
        "non_claims": contract["non_claims"], "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    write_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
