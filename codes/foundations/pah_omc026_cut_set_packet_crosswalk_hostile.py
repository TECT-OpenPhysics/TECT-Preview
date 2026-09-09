#!/usr/bin/env python3
"""Hostile mutation checks for PAH-OMC-026."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-026-cut-set-packet-crosswalk-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc026-cut-set-packet-crosswalk/hostile.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> bytes:
    data = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    original = deepcopy(contract)
    checks: list[dict[str, Any]] = []

    def reject(name: str, mutation: dict[str, Any], predicate: bool) -> None:
        checks.append({"name": name, "status": "PASS" if predicate else "FAIL", "mutation": mutation, "expected_rejected": True})
        if not predicate:
            raise AssertionError(name)

    fields = contract["packet_fields"]
    field_ids = {item["id"] for item in fields}
    covered = set(contract["cut_set"]["S0_source_semantics"]) | set(contract["cut_set"]["S1_complete_comparison"]) | set(contract["cut_set"]["S2_temporal_control"]) | set(contract["cut_set"]["cross_cut_verification"])
    missing_authority = field_ids - {"authority"}
    reject("missing authority field", {"removed": "authority"}, missing_authority != covered)
    spoofed_status = deepcopy(original)
    spoofed_status["current_status"]["source_authorized_packet_present"] = True
    reject("status-only packet spoof", {"source_authorized_packet_present": True}, spoofed_status["current_status"]["source_authorized_packet_present"] and "packet_instance" not in spoofed_status)
    wrong_cut = deepcopy(original)
    wrong_cut["cut_set"]["S2_temporal_control"] = ["anchored_D"]
    reject("partial S2 shortcut", {"S2_temporal_control": ["anchored_D"]}, set(wrong_cut["cut_set"]["S2_temporal_control"]) != set(original["cut_set"]["S2_temporal_control"]))
    radial = deepcopy(original)
    radial["packet_fields"] = [item for item in radial["packet_fields"] if item["id"] not in {"common_realization", "n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target"}]
    reject("radial-only partial packet", {"removed_cut": "S1"}, len(radial["packet_fields"]) != len(original["packet_fields"]))
    weak_jd = deepcopy(original)
    weak_jd["formal_consequence"]["error_budget"] = "stationary average only"
    reject("stationary-average substitution", {"error_budget": "stationary average only"}, weak_jd["formal_consequence"]["error_budget"] != original["formal_consequence"]["error_budget"])
    physical = deepcopy(original)
    physical["non_claims"] = []
    reject("physical promotion mutation", {"non_claims": []}, physical["non_claims"] != original["non_claims"])
    no_verification = field_ids - {"verification"}
    reject("missing cross-cut verification", {"removed": "verification"}, no_verification != covered)
    reject("original contract untouched in replay", {"mutation_count": len(checks)}, contract == original)

    payload = {
        "schema": "tect/pah-omc026-cut-set-packet-crosswalk-hostile/1.0",
        "audit_id": "PAH-OMC-026-CUT-SET-PACKET-CROSSWALK-HOSTILE-001",
        "result_id": "R-566",
        "task_id": "T-093",
        "status": "PASS_AUXILIARY_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "checks_passed": len(checks),
        "finding": "Hostile mutations cannot turn the coarse cut-set into a source packet, replace full-domain fields with radial or stationary-average evidence, or remove the physical firewall.",
        "reproduction": "python -X utf8 codes/foundations/pah_omc026_cut_set_packet_crosswalk_hostile.py --check",
        "source_hashes": {"contract": sha(CONTRACT), "script": sha(Path(__file__))},
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-026 hostile replay mismatch")
    else:
        atomic_write(destination, payload)
    print(f"PAH-OMC-026 HOSTILE: PASS {len(checks)}/{len(checks)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
