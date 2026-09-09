#!/usr/bin/env python3
"""Hostile mutation checks for PAH-OMC-021 packet-transfer classification."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-021-composite-owner-packet-transfer-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc021-composite-owner-packet-transfer/hostile.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write_json(path: Path, value: dict[str, Any]) -> bytes:
    encoded = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def check(rows: list[dict[str, Any]], name: str, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL"})
    if not ok:
        raise AssertionError(name)


def admissible(candidate: dict[str, Any], pins: dict[str, str]) -> bool:
    statuses = {key: value.get("status") for key, value in candidate["transfer_fields"].items()}
    return (
        candidate["admission_rule"]["current"] == "ADMIT"
        and statuses.get("authority") == "SOURCE_AUTHORIZED"
        and all(statuses.get(key) in ("FINITE_PRESENT", "ASYMPTOTIC_PRESENT") for key in statuses)
        and all(value == pins[key] for key, value in candidate["source_pins"].items())
        and all(token in " ".join(candidate["non_claims"]).lower() for token in ("physical pre-a", "spacetime", "qft", "gravity", "toe"))
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = read(CONTRACT)
    pins = {path: digest(ROOT / path) for path in contract["source_pins"]}
    rows: list[dict[str, Any]] = []
    check(rows, "baseline is not admissible", not admissible(contract, pins))

    authority = copy.deepcopy(contract)
    authority["admission_rule"]["current"] = "ADMIT"
    authority["transfer_fields"]["authority"]["status"] = "SOURCE_AUTHORIZED"
    check(rows, "authority relabel cannot create source authority", not admissible(authority, pins))

    asymptotic = copy.deepcopy(contract)
    asymptotic["admission_rule"]["current"] = "ADMIT"
    asymptotic["transfer_fields"]["authority"]["status"] = "SOURCE_AUTHORIZED"
    for field in ("n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target", "full_domain_J", "anchored_D"):
        asymptotic["transfer_fields"][field]["status"] = "ASYMPTOTIC_PRESENT"
    check(rows, "status-only asymptotic fill cannot create evidence", not admissible(asymptotic, pins))

    hash_mutation = copy.deepcopy(contract)
    hash_mutation["source_pins"]["strategy/pa-hyp/PAH-001-v1.json"] = "0" * 64
    check(rows, "parent hash mutation is rejected", not admissible(hash_mutation, pins))

    physical = copy.deepcopy(contract)
    physical["non_claims"] = ["finite packet admitted as physical Pre-A and QFT evidence"]
    check(rows, "physical firewall erasure is rejected", not admissible(physical, pins))

    finite_only = copy.deepcopy(contract)
    finite_only["admission_rule"]["current"] = "ADMIT"
    finite_only["transfer_fields"]["authority"]["status"] = "SOURCE_AUTHORIZED"
    for field in ("n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target", "full_domain_J", "anchored_D"):
        finite_only["transfer_fields"][field]["status"] = "FINITE_PRESENT"
    finite_only["non_claims"] = contract["non_claims"]
    check(rows, "finite-only substitution remains rejected", not admissible(finite_only, pins))

    wrong_result = copy.deepcopy(contract)
    wrong_result["result_id"] = "R-479"
    check(rows, "result identity drift is rejected", wrong_result.get("result_id") != "R-558")
    check(rows, "all ten fields remain required", len(contract["transfer_fields"]) == 10)
    check(rows, "hold verdict is retained", contract["admission_rule"]["current"] == "HOLD_FOR_EVIDENCE")
    check(rows, "no PAH source edit", read(ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json")["parent"]["sha256"] == pins["strategy/pa-hyp/PAH-001-v1.json"])

    payload = {
        "schema": "tect/pah-omc021-composite-owner-packet-transfer-hostile/1.0",
        "audit_id": "PAH-OMC-021-COMPOSITE-OWNER-PACKET-TRANSFER-HOSTILE-001",
        "result_id": "R-558",
        "task_id": "T-088",
        "status": "PASS_MUTATIONS_REJECTED_HOLD_FOR_EVIDENCE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "source_hashes": pins,
        "mutations_rejected": len(rows),
        "finding": "Hostile mutations cannot turn a finite researcher successor into parent-source authority or manufacture the absent ordered-limit fields.",
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc021_composite_owner_packet_transfer_hostile.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = write_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-021 hostile replay mismatch")
    print(f"PAH-OMC-021 COMPOSITE OWNER PACKET HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
