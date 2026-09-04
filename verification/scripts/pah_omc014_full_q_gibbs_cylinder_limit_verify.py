#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-014 source-input HOLD packet.

The integrated lane reruns the two independent source audits and the hostile
firewall.  It deliberately does not manufacture a sector law or calculate a
global limit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc014-full-q-gibbs-cylinder-limit"
PRIMARY = ROOT / "codes/foundations/pah_omc014_full_q_gibbs_cylinder_limit.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc014_full_q_gibbs_cylinder_limit_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc014_full_q_gibbs_cylinder_limit_hostile.py"
RESULT_ID = "R-494"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-014-FULL-Q-GIBBS-CYLINDER-LIMIT-INTEGRATED-001"


def load(path: Path) -> Any:
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


def run_script(script: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    payload = load(output) if output.is_file() else {}
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
        "verification": payload.get("verification"),
        "verdict": payload.get("verdict"),
        "payload": payload,
    }


def run(output: Path = RUN_DIR / "integrated.json") -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    rows: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    current_contract = sha(CONTRACT)
    current_manifest = sha(MANIFEST)
    parent_hashes: dict[str, str] = {}
    for name, entry in manifest.get("parents", {}).items():
        path = ROOT / entry["path"]
        parent_hashes[name] = sha(path)
        check(f"parent hash {name}", entry.get("sha256") == parent_hashes[name], entry.get("sha256"), parent_hashes[name])
    check("contract hash pin", manifest.get("contract", {}).get("sha256") == current_contract, manifest.get("contract", {}).get("sha256"), current_contract)
    check("manifest identity", manifest.get("manifest_id") == "PAH-OMC-014-MANIFEST" and manifest.get("result_id") == RESULT_ID and manifest.get("task_id") == TASK_ID, {"manifest": manifest.get("manifest_id"), "result": manifest.get("result_id"), "task": manifest.get("task_id")}, "OMC-014/R-494/T-054")
    check("hold/non-bearing status", manifest.get("status") == "HOLD_FOR_EVIDENCE" and manifest.get("claim_bearing") is False and manifest.get("active_gate_change") is False and manifest.get("physical_promotion") is False, {k: manifest.get(k) for k in ("status", "claim_bearing", "active_gate_change", "physical_promotion")}, "HOLD/non-bearing/no gate change")
    check("contract status firewall", contract.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and contract.get("status", {}).get("omega_status") == "NOT_DEFINED" and contract.get("status", {}).get("weak_cylinder_limit") == "NOT_TESTABLE", contract.get("status"), "HOLD/omega undefined/limit not testable")
    check("parent mutation firewall", manifest.get("no_parent_mutation") is True and all(value is True for value in contract.get("preservation_firewall", {}).values()), {"no_parent_mutation": manifest.get("no_parent_mutation"), "preservation": contract.get("preservation_firewall")}, "all true")

    primary = run_script(PRIMARY, RUN_DIR / "primary.json")
    independent = run_script(INDEPENDENT, RUN_DIR / "independent.json")
    hostile = run_script(HOSTILE, RUN_DIR / "hostile.json")
    expected_exp = contract.get("exploration_id")
    for label, item in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        payload = item["payload"]
        check(f"{label} subprocess", item["returncode"] == 0 and item["verification"] == "PASS", {k: item.get(k) for k in ("returncode", "verification", "verdict")}, "PASS/HOLD_FOR_EVIDENCE")
        check(f"{label} identity", payload.get("result_id") == RESULT_ID and payload.get("exploration_id") == expected_exp and payload.get("task_id") == TASK_ID, {k: payload.get(k) for k in ("result_id", "exploration_id", "task_id")}, {"result_id": RESULT_ID, "exploration_id": expected_exp, "task_id": TASK_ID})
        check(f"{label} retains source absence", payload.get("candidate_sector_law") == "ABSENT_IN_SOURCE" and payload.get("verdict") == "HOLD_FOR_EVIDENCE", {"candidate_sector_law": payload.get("candidate_sector_law"), "verdict": payload.get("verdict")}, "ABSENT_IN_SOURCE/HOLD_FOR_EVIDENCE")
    check("cross-lane verification", all(item["verification"] == "PASS" for item in (primary, independent, hostile)), [item["verification"] for item in (primary, independent, hostile)], "PASS/PASS/PASS")
    check("cross-lane verdict remains HOLD", all(item["verdict"] == "HOLD_FOR_EVIDENCE" for item in (primary, independent, hostile)), [item["verdict"] for item in (primary, independent, hostile)], "HOLD_FOR_EVIDENCE")
    check("no global omega was evaluated", contract["status"]["projective_consistency"] == "NOT_TESTABLE" and contract["status"]["positivity_normalization"] == "NOT_TESTABLE" and contract["status"]["stationarity"] == "NOT_TESTABLE", contract["status"], "all not testable")
    check("R-484 and C_sw boundaries retained", contract["status"]["r484_boundary_defect"] == "RETAINED_16_OVER_9" and contract["status"]["csw_role"] == "DOMINATION_ONLY", {"R484": contract["status"]["r484_boundary_defect"], "C_sw": contract["status"]["csw_role"]}, "16/9 retained/domination-only")
    check("physical non-claim", contract["status"]["physical_promotion"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]), contract["non_claims"], True)

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-full-q-gibbs-cylinder-limit-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": expected_exp,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "HOLD_FOR_EVIDENCE_SOURCE_OWNER_FULL_Q_WEIGHT_LAW_ABSENT",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"PAH-OMC-014": current_contract, "PAH-OMC-014-MANIFEST": current_manifest, **parent_hashes},
        "runs": {"primary": primary, "independent": independent, "hostile": hostile},
        "candidate_sector_law": "ABSENT_IN_SOURCE",
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "weak_cylinder_limit": "NOT_TESTABLE",
        "positivity_normalization": "NOT_TESTABLE",
        "stationarity": "NOT_TESTABLE",
        "claim_bearing": False,
        "active_gate_change": False,
        "non_claims": contract["non_claims"],
        "missing_assumptions": contract["missing_assumptions"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; source_law={payload['candidate_sector_law']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "integrated.json")
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
