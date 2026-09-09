#!/usr/bin/env python3
"""Hostile controls for the deterministic PAH-OMC-020 owner inventory."""

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
INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json"
CANDIDATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-inventory-stable/hostile.json"
)


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def complete_marker(obj: dict[str, Any]) -> bool:
    provenance = obj.get("provenance")
    if isinstance(provenance, dict) and provenance.get("source_authorized_packet_present") is True:
        return True
    status = obj.get("status")
    return isinstance(status, str) and status in {"SOURCE_AUTHORIZED_COMPLETE", "OWNER_AUTHORIZED_COMPLETE"}


def compute() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    intake = read(INTAKE)
    candidate = read(CANDIDATE)
    intake_mut = copy.deepcopy(intake)
    intake_mut.setdefault("provenance", {})["source_authorized_packet_present"] = True
    candidate_mut = copy.deepcopy(candidate)
    candidate_mut["status"] = "SOURCE_AUTHORIZED_COMPLETE"
    candidate_mut.setdefault("provenance", {})["source_authorized_packet_present"] = True

    check("baseline intake is not complete", complete_marker(intake), False, not complete_marker(intake))
    check("baseline candidate is not complete", complete_marker(candidate), False, not complete_marker(candidate))
    check("authorization mutation is detected", complete_marker(intake_mut), True, complete_marker(intake_mut))
    check("status mutation is detected", complete_marker(candidate_mut), True, complete_marker(candidate_mut))
    check("candidate source hash is unchanged by audit", hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(), "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e", hashlib.sha256(CANDIDATE.read_bytes()).hexdigest() == "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e")
    check("dynamic fsck output is rejected", "fsck" in json.dumps(candidate).lower(), False, "fsck" not in json.dumps(candidate).lower())
    check("direct-sum shortcut is not introduced", "direct-sum" in json.dumps(candidate).lower(), False, "direct-sum" not in json.dumps(candidate).lower())
    check("model inputs remain frozen", candidate.get("provenance", {}).get("model_change"), False, candidate.get("provenance", {}).get("model_change") is False)

    return {
        "schema": "tect/pah-omc020-owner-inventory-stable-hostile/1.0",
        "audit_id": "PAH-OMC-020-OWNER-INVENTORY-STABLE-HOSTILE-001",
        "task_id": "T-063",
        "status": "PASS_HOSTILE_STABLE_OWNER_INVENTORY_CONTROLS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "finding": "Hostile mutations that assert owner authorization or completed status are detected; the stable inventory does not accept dynamic fsck output or alter PAH model inputs.",
        "non_claims": [
            "No PAH temporal convergence, common-space theorem or universal owner absence theorem.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("hostile stable owner inventory replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=args.output.name + ".", suffix=".tmp", dir=args.output.parent)
        os.close(descriptor)
        temporary = Path(name)
        try:
            temporary.write_bytes(encoded)
            temporary.replace(args.output)
        finally:
            if temporary.exists():
                temporary.unlink()
    print(f"PAH-OMC-020 STABLE OWNER INVENTORY HOSTILE: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
