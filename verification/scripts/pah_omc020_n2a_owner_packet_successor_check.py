#!/usr/bin/env python3
"""Check the fixed-snapshot successor of the PAH-OMC-020 N2a intake."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json"
SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-snapshot/n2a-successor.json"
)
PARENT_PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json": "b87a2d8d7b0009c9f5bd30695823cb442376939ff18c1d48f1d890ae430fe8c7",
}
REQUIRED_SCOPE = {"functional_and_rates", "finite_spaces", "limit_hilbert_space", "comparison_maps", "time"}
REQUIRED_ACCEPTANCE = {"owner_authority", "common_hilbert_realization", "local_cylinder_recovery", "n2b_liminf", "recovery_limsup", "n2c_n4_boundary_escape", "n2d_minimal_identification", "verification"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def compute() -> dict[str, Any]:
    contract = load(CONTRACT)
    snapshot = load(SNAPSHOT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    raw = CONTRACT.read_bytes()
    check("contract UTF-8 LF", b"\r" not in raw and raw.decode("utf-8").encode("utf-8") == raw, True, b"\r" not in raw and raw.decode("utf-8").encode("utf-8") == raw)
    check("schema", contract.get("schema"), "tect/pah-omc020-n2a-owner-packet-intake/1.1", contract.get("schema") == "tect/pah-omc020-n2a-owner-packet-intake/1.1")
    check("version", contract.get("version"), "1.1.0", contract.get("version") == "1.1.0")
    check("intake-only status", contract.get("status"), "INTAKE_CONTRACT_ONLY", contract.get("status") == "INTAKE_CONTRACT_ONLY")
    provenance = contract.get("provenance", {})
    check("claim and promotion firewalls", {key: provenance.get(key) for key in ("source_authorized_packet_present", "claim_bearing", "active_gate_change", "physical_promotion")}, {"source_authorized_packet_present": False, "claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(provenance.get(key) is False for key in ("source_authorized_packet_present", "claim_bearing", "active_gate_change", "physical_promotion")))
    supersedes = contract.get("supersedes", {})
    check("superseded v1 hash", supersedes.get("sha256"), digest(ROOT / supersedes["path"]), supersedes.get("sha256") == digest(ROOT / supersedes["path"]))
    owner_snapshot = contract.get("owner_snapshot", {})
    check("snapshot identity", owner_snapshot.get("path"), "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json", owner_snapshot.get("path") == "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json")
    check("snapshot hash", owner_snapshot.get("sha256"), digest(SNAPSHOT), owner_snapshot.get("sha256") == digest(SNAPSHOT))
    check("snapshot remains non-authorized", {key: owner_snapshot.get(key) for key in ("status", "authorized_paths", "complete_paths")}, {"status": "FIXED_SEARCH_SNAPSHOT", "authorized_paths": [], "complete_paths": []}, owner_snapshot.get("status") == "FIXED_SEARCH_SNAPSHOT" and owner_snapshot.get("authorized_paths") == [] and owner_snapshot.get("complete_paths") == [])
    parent_hashes: dict[str, str] = {}
    for label, parent in contract.get("parents", {}).items():
        path = ROOT / parent["path"]
        actual = digest(path)
        parent_hashes[parent["path"]] = actual
        check(f"parent hash {label}", actual, parent["sha256"], actual == parent["sha256"])
    check("required parent set", sorted(parent_hashes), sorted(PARENT_PINS), set(parent_hashes) == set(PARENT_PINS))
    check("required parent pins", parent_hashes, PARENT_PINS, parent_hashes == PARENT_PINS)
    check("fixed scope keys", sorted(contract.get("fixed_scope", {})), sorted(REQUIRED_SCOPE), set(contract.get("fixed_scope", {})) == REQUIRED_SCOPE)
    check("acceptance keys", sorted(contract.get("acceptance_conditions", {})), sorted(REQUIRED_ACCEPTANCE), set(contract.get("acceptance_conditions", {})) == REQUIRED_ACCEPTANCE)
    payload = contract.get("required_owner_payload", [])
    check("nine owner fields", len(payload), 9, len(payload) == 9)
    decision = contract.get("decision_rule", {})
    check("decision branches", sorted(decision), ["HOLD_FOR_EVIDENCE", "MAINLINE_ADVANCE", "NEGATIVE_RESULT"], set(decision) == {"HOLD_FOR_EVIDENCE", "MAINLINE_ADVANCE", "NEGATIVE_RESULT"})
    check("current finding is an evidence hold", "does not define U_n" in contract.get("current_finding", ""), True, "does not define U_n" in contract.get("current_finding", ""))
    check("single next question", bool(contract.get("single_next_question", "").strip()), True, bool(contract.get("single_next_question", "").strip()))
    check("snapshot parent agrees", snapshot.get("parent_hashes", {}).get("claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json"), PARENT_PINS["claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json"], snapshot.get("parent_hashes", {}).get("claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json") == PARENT_PINS["claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json"])
    check("physical boundary in non-claims", any("physical Pre-A" in text for text in contract.get("non_claims", [])), True, any("physical Pre-A" in text for text in contract.get("non_claims", [])))
    check("external Markov time boundary", any("Markov time" in text for text in contract.get("non_claims", [])), True, any("Markov time" in text for text in contract.get("non_claims", [])))

    return {
        "schema": "tect/pah-omc020-n2a-owner-packet-successor-check/1.0",
        "audit_id": "PAH-OMC-020-N2A-OWNER-SUCCESSOR-CHECK-001",
        "status": "PASS_FIXED_SNAPSHOT_INTAKE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "source_hashes": {
            "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json": digest(CONTRACT),
            "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json": digest(SNAPSHOT),
            **parent_hashes,
        },
        "finding": "The successor intake pins the current N2b bytes and a fixed candidate manifest. No source-authorized owner packet is present; the contract remains an evidence intake only.",
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
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
            raise SystemExit("fixed-snapshot N2a successor replay mismatch")
    else:
        atomic_write(args.output.resolve(), encoded)
    print(f"PAH-OMC-020 N2A FIXED-SNAPSHOT SUCCESSOR: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
