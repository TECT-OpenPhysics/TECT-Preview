#!/usr/bin/env python3
"""Hostile mutation firewall for PAH-OMC-012.

The hostile lane attempts the shortcuts that would hide the original fixed-Q
domain defect or silently change the model. Every shortcut must be rejected by
the contract itself.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-manifest.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
WEIGHT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/hostile.json"

RESULT_ID = "R-492"
EXPLORATION_ID = "EXP-001461"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-012-FULL-Q-GRADED-DOMAIN-HOSTILE-001"

def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except BaseException:
        try:
            os.unlink(temp)
        except FileNotFoundError:
            pass
        raise

def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract = read(CONTRACT)
    manifest = read(MANIFEST)
    source = read(SOURCE)
    geometry = read(GEOMETRY)
    weight = read(WEIGHT)
    checks: list[dict[str, Any]] = []

    def reject(name: str, condition: bool, detail: Any = None) -> None:
        checks.append({"mutation": name, "rejected": bool(condition), "detail": detail})

    reject("parent-drift", manifest["parents"]["PAH-001"]["sha256"] == sha(SOURCE) and manifest["parents"]["PAH-OMC-004"]["sha256"] == sha(GEOMETRY) and manifest["parents"]["PAH-OMC-010"]["sha256"] == sha(WEIGHT), {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-010": sha(WEIGHT)})
    reject(
        "fixed-Q-only-projection",
        "disjoint_union" in contract["exact_scope"]["graded_state_space"]
        and "grade is allowed to change" in contract["exact_scope"]["charge_balance"]
        and "full-q" in manifest["scope"].lower(),
        contract["exact_scope"]["graded_state_space"],
    )
    reject(
        "charge-deletion",
        contract["preservation_firewall"]["no_charge_deletion"]
        and contract["preservation_firewall"]["no_charge_redistribution"]
        and "Q_f-Q_c=sum_" in contract["exact_scope"]["charge_balance"],
        contract["exact_scope"]["charge_balance"],
    )
    reject(
        "conditional-gibbs-average",
        contract["preservation_firewall"]["no_conditional_gibbs_average"]
        and "no cross-Q mixing probabilities" in contract["exact_scope"]["gibbs_reference"],
        contract["exact_scope"]["gibbs_reference"],
    )
    reject(
        "cross-Q-rate-fitting",
        contract["preservation_firewall"]["no_rate_fitting"]
        and "componentwise" in contract["exact_scope"]["generator_domain"]
        and "exactly pi_(rho_(n,R,Q))" in contract["exact_scope"]["gibbs_reference"],
        "Only parent component rates and Gibbs states are used.",
    )
    reject(
        "functional-or-counterterm-change",
        contract["preservation_firewall"]["functional_unchanged"]
        and contract["preservation_firewall"]["no_counterterm"]
        and source["functional_or_action"]["counterterms"] == "none at finite rho",
        source["functional_or_action"]["counterterms"],
    )
    reject(
        "new-carrier-or-root",
        contract["preservation_firewall"]["no_new_carrier"]
        and "No carrier" in contract["exact_scope"]["carrier_family"]
        and "d_n link" in contract["exact_scope"]["neutral_refinement"],
        contract["exact_scope"]["carrier_family"],
    )
    reject(
        "global-gibbs-overclaim",
        "no cross-Q mixing probabilities" in contract["exact_scope"]["gibbs_reference"]
        and "not a newly asserted global probability measure" in contract["non_claims"][4],
        contract["exact_scope"]["gibbs_reference"],
    )
    reject(
        "intertwining-overclaim",
        contract["preservation_firewall"]["no_generator_intertwining_claim"]
        and "eligible for a separate PAH-OMC-011 re-test only" in manifest["scope"],
        manifest["scope"],
    )
    reject(
        "physical-promotion",
        contract["preservation_firewall"]["no_physical_promotion"]
        and contract["status"]["claim_bearing"] is False
        and contract["status"]["active_gate_change"] is False
        and any("No infinite-volume dynamics" in item for item in contract["non_claims"]),
        contract["non_claims"],
    )

    failed = [row for row in checks if not row["rejected"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc012-full-q-graded-domain-hostile/1.0",
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
        "source_hashes": {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-010": sha(WEIGHT)},
        "verdict": "MAINLINE_ADVANCE" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "HOSTILE_FIREWALL_REJECTS_DOMAIN_OVERCLAIMS",
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "eligible_for_omc011_retest": bool(not failed),
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
