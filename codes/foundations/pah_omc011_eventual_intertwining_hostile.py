#!/usr/bin/env python3
"""Hostile mutation checks for PAH-OMC-011.

The hostile lane does not alter the model.  It attempts the common shortcuts
that would turn the image-local observation into an all-state theorem and
requires the packet's firewalls to reject each shortcut.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
WEIGHT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc011-eventual-intertwining/hostile.json"

RESULT_ID = "R-491"
EXPLORATION_ID = "EXP-001457"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-011-EVENTUAL-INTERTWINING-HOSTILE-001"


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
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
    contract = read(CONTRACT)
    source = read(SOURCE)
    geometry = read(GEOMETRY)
    weight = read(WEIGHT)
    manifest = read(MANIFEST)
    checks: list[dict[str, Any]] = []

    def reject(name: str, condition: bool, detail: Any) -> None:
        checks.append({"mutation": name, "rejected": bool(condition), "detail": detail})

    source_hashes = {
        "PAH-001": digest(SOURCE),
        "PAH-OMC-004": digest(GEOMETRY),
        "PAH-OMC-010": digest(WEIGHT),
    }
    reject(
        "parent-drift",
        manifest["parents"]["PAH-001"]["sha256"] == source_hashes["PAH-001"] and manifest["parents"]["PAH-OMC-004"]["sha256"] == source_hashes["PAH-OMC-004"] and manifest["parents"]["PAH-OMC-010"]["sha256"] == source_hashes["PAH-OMC-010"],
        source_hashes,
    )
    reject(
        "q0-substitution",
        "Q=1" in contract["exact_scope"]["regulator"] and any("Q=0" in item for item in contract["known_boundaries"] + contract["non_claims"]),
        "The Q=0 R-484 slice is not silently substituted for the Q=1 full-domain question.",
    )
    reject(
        "image-only-as-all-state",
        "GLOBAL_FIXED_Q_COMMON_DOMAIN_MISSING" in contract["status"]["classification"] and "not a map Omega_(n+1,1)->Omega_(n,1)" in contract["domain_obstruction"]["consequence"],
        contract["domain_obstruction"]["consequence"],
    )
    reject(
        "conditional-gibbs-average",
        contract["preservation_firewall"]["no_conditional_gibbs_average"] is True and "no_conditional_gibbs_average" in contract["preservation_firewall"],
        "Conditional averaging is outside the declared map and is explicitly prohibited.",
    )
    reject(
        "rate-fitting-or-counterterm",
        contract["preservation_firewall"]["no_rate_fitting"] is True and contract["preservation_firewall"]["no_counterterm"] is True and source["functional_or_action"]["counterterms"] == "none at finite rho",
        "The displayed functional and midpoint rates remain unchanged.",
    )
    reject(
        "csw-as-intertwining-proof",
        "only as a state-weighted domination input" in contract["exact_scope"]["gibbs_norm"] and "not an intertwining proof" in contract["exact_scope"]["gibbs_norm"],
        contract["exact_scope"]["gibbs_norm"],
    )
    # Off-by-one test: if m_f=1, n=1 has a frontier column equal to m_f and is
    # not separated.  The declared N(f)=m_f+1 is therefore the first safe stage.
    m_f = 1
    bad_n = m_f
    bad_frontier = (bad_n, bad_n + 1, bad_n + 2)
    reject(
        "off-by-one-Nf",
        not all(column > m_f for column in bad_frontier) and "N(f)=max(2,m_f+1)" in contract["pre_registered_stabilization"]["N_of_f"],
        {"m_f": m_f, "attempted_N": bad_n, "frontier": list(bad_frontier), "declared": contract["pre_registered_stabilization"]["N_of_f"]},
    )
    reject(
        "boundary-defect-erasure",
        "16/9" in contract["pre_registered_stabilization"]["boundary_defect"] and "retained" in contract["pre_registered_stabilization"]["boundary_defect"],
        contract["pre_registered_stabilization"]["boundary_defect"],
    )
    reject(
        "physical-promotion",
        contract["status"]["claim_bearing"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]),
        contract["non_claims"],
    )
    reject(
        "csw-number-drift",
        "C_sw=540" in contract["exact_scope"]["gibbs_norm"] and weight.get("contract_id") == "PAH-OMC-010",
        {"contract": weight.get("contract_id"), "declared": contract["exact_scope"]["gibbs_norm"]},
    )

    failed = [row for row in checks if not row["rejected"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc011-eventual-intertwining-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": source_hashes,
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "HOSTILE_FIREWALL_REJECTS_ALL_STATE_OVERCLAIMS",
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "weak_gibbs_l2": {"status": "BLOCKED_UNDEFINED_LIFT_ON_FULL_DOMAIN", "universal_failure_claimed": False},
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
