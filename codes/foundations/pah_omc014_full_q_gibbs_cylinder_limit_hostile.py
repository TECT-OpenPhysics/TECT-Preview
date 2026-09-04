#!/usr/bin/env python3
"""Hostile firewall for PAH-OMC-014.

Each attempted shortcut would manufacture the missing cross-Q law or weaken a
declared boundary.  A PASS means every shortcut is rejected; it is not a
claim that the requested limit exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc014-full-q-gibbs-cylinder-limit"
RESULT_ID = "R-494"
EXPLORATION_ID = "EXP-001504"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-014-FULL-Q-GIBBS-CYLINDER-LIMIT-HOSTILE-001"

PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC011 = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json"
R493 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json"


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
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


def run(output: Path = RUN_DIR / "hostile.json") -> dict[str, Any]:
    contract = read(CONTRACT)
    manifest = read(MANIFEST)
    pah = read(PAH)
    omc012 = read(OMC012)
    omc011 = read(OMC011)
    r493 = read(R493)
    firewall = contract["preservation_firewall"]
    checks: list[dict[str, Any]] = []

    def reject(mutation: str, condition: bool, detail: Any) -> None:
        checks.append({"mutation": mutation, "rejected": bool(condition), "detail": detail})

    no_law = contract["exact_scope"]["source_weight_law"].startswith("ABSENT_IN_SOURCE")
    no_global = omc012["status"]["global_normalized_gibbs_measure"].startswith("NOT_DEFINED_BY_PARENT")
    omc011_component_only = "C_sw=540 only as a state-weighted domination input" in omc011.get("exact_scope", {}).get("gibbs_norm", "")
    reject("uniform sector weights", no_law and firewall["no_sector_weight_invention"], "w_Q=1/|Q_n| would be a new source-owned law")
    reject("partition-function proportional weights", no_law and firewall["no_sector_weight_invention"], "w_Q proportional to Z_Q is not declared by PAH-001")
    reject("fitted or observation-tuned weights", firewall["no_cross_q_fitting"] and firewall["no_sector_weight_invention"], "fitting would violate the source contract")
    reject("conditional Gibbs average", firewall["no_conditional_averaging"] and no_global, "conditioning on one Q is not a full-Q probability")
    reject("fixed-Q substitution", no_global and firewall["no_sector_weight_invention"], "one component does not define the disjoint union")
    reject("C_sw as sector probability", firewall["no_csw_as_measure"] and contract["status"]["csw_role"] == "DOMINATION_ONLY", "C_sw=540 is a bound, not a probability law")
    reject("boundary averaging or counterterm", firewall["no_boundary_erasure"] and firewall["no_counterterm"] and "16/9" in contract["exact_scope"]["boundary_input"], "R-484 defect must remain 16/9")
    reject("rate or functional repair", firewall["functional_unchanged"] and firewall["rates_unchanged"], "PAH-001 F_rho and rates are immutable")
    reject("OMC-011 component-only state scope", omc011_component_only and "fixed-Q state space" in omc011.get("exact_scope", {}).get("generator_domain", ""), "OMC-011 is a finite fixed-Q/intertwining input, not a global Gibbs law")
    reject("OMC-013 promotion to global stationarity", r493.get("claim_bearing") is False and "Weak Gibbs-L2 convergence" in " ".join(r493.get("non_claims", [])), "finite componentwise intertwining is reference-only")
    reject("direct-sum norm treated as probability", "direct-sum family norm" in omc012["exact_scope"]["graded_norm"] and "single probability" in omc012["exact_scope"]["graded_norm"], "norm has no sector masses")
    reject("physical promotion", firewall["no_physical_promotion"] and contract["status"]["physical_promotion"] is False, "no physical Pre-A/spacetime/QFT claim")

    failed = [row for row in checks if not row["rejected"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-full-q-gibbs-cylinder-limit-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": contract.get("exploration_id", EXPLORATION_ID),
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "HOSTILE_FIREWALL_REJECTS_UNAUTHORIZED_WEIGHT_REPAIRS",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": {"PAH-001": sha(PAH), "PAH-OMC-012": sha(OMC012), "PAH-OMC-011": sha(OMC011), "R-493-INTEGRATED": sha(R493)},
        "candidate_sector_law": "ABSENT_IN_SOURCE",
        "claim_bearing": False,
        "active_gate_change": False,
        "non_claims": contract["non_claims"],
        "missing_assumptions": contract["missing_assumptions"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; all_shortcuts_rejected={not failed}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "hostile.json")
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
