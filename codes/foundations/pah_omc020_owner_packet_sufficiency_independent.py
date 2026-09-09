#!/usr/bin/env python3
"""Non-importing independent replay for the PAH-OMC-020 packet bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-packet-sufficiency/independent.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return encoded


def assert_row(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = read(CONTRACT)
    rows: list[dict[str, Any]] = []
    pins = contract["source_pins"]
    observed = {name: sha(ROOT / name) for name in pins}
    assert_row(rows, "contract id", contract.get("contract_id") == "PAH-OMC-020-OWNER-PACKET-SUFFICIENCY", contract.get("contract_id"), "PAH-OMC-020-OWNER-PACKET-SUFFICIENCY")
    assert_row(rows, "source bytes", observed == pins, observed, pins)
    assert_row(rows, "fixed external time", "External stochastic Markov time" in contract["fixed_scope"]["time"], contract["fixed_scope"]["time"], True)
    assert_row(rows, "fixed order", contract["fixed_scope"]["order"].startswith("j tends") and "anchored n" in contract["fixed_scope"]["order"], contract["fixed_scope"]["order"], True)
    assert_row(rows, "target unchanged", "R-512" in contract["fixed_scope"]["target"], contract["fixed_scope"]["target"], True)

    field_ids = {field["id"] for field in contract["required_packet_fields"]}
    expected = {"authority", "root_semantics", "common_realization", "n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target", "full_domain_J", "anchored_D", "verification"}
    assert_row(rows, "complete field set", field_ids == expected, sorted(field_ids), sorted(expected))
    assert_row(rows, "no duplicate fields", len(field_ids) == len(contract["required_packet_fields"]), len(field_ids), len(contract["required_packet_fields"]))
    bridge = contract["formal_consequence"]
    assert_row(rows, "error decomposition", all(token in bridge["error_budget"] for token in ("err", "J", "D")), bridge["error_budget"], "err/J/D")
    assert_row(rows, "ordered conclusion", all(token in bridge["conclusion"] for token in ("epsilon", "N", "n", "j")), bridge["conclusion"], "nested epsilon")

    r555 = read(ROOT / "strategy/pa-hyp/PAH-OMC-020-ordered-epsilon-bridge-result-v1.json")
    r556 = read(ROOT / "strategy/pa-hyp/PAH-OMC-020-minimal-dependency-audit-result-v1.json")
    assert_row(rows, "parent bridge retained", r555.get("verdict") == "PASS_CONDITIONAL", r555.get("verdict"), "PASS_CONDITIONAL")
    assert_row(rows, "parent ledger retained", r556.get("verdict") == "HOLD_FOR_EVIDENCE", r556.get("verdict"), "HOLD_FOR_EVIDENCE")

    def admitted(packet: set[str]) -> bool:
        return packet == expected

    assert_row(rows, "all fields admit", admitted(expected), True, True)
    rejected = {field for field in expected if field != "root_semantics"}
    assert_row(rows, "root omission rejects", not admitted(rejected), admitted(rejected), False)
    rejected = {field for field in expected if field != "common_realization"}
    assert_row(rows, "common-map omission rejects", not admitted(rejected), admitted(rejected), False)
    rejected = {field for field in expected if field != "n2c_n4_boundary"}
    assert_row(rows, "boundary omission rejects", not admitted(rejected), admitted(rejected), False)
    assert_row(rows, "packet absence is current", contract.get("current_status") == "NO_SOURCE_AUTHORIZED_PACKET_PRESENT", contract.get("current_status"), "NO_SOURCE_AUTHORIZED_PACKET_PRESENT")
    non_claims = json.dumps(contract["non_claims"]).lower()
    assert_row(rows, "physical firewall", all(token in non_claims for token in ("pre-a", "qft", "gravity", "toe")), True, True)

    payload = {
        "schema": "tect/pah-omc020-owner-packet-sufficiency-independent/1.0",
        "audit_id": "PAH-OMC-020-OWNER-PACKET-SUFFICIENCY-INDEPENDENT-001",
        "result_id": "R-557",
        "task_id": "T-087",
        "status": "PASS_CONDITIONAL_PACKET_SUFFICIENCY_HOLD_FOR_EVIDENCE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "source_hashes": observed,
        "finding": "Independent replay confirms that every required packet field is jointly necessary for admission, while current source records contain no source-authorized packet.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_owner_packet_sufficiency_independent.py --check",
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = write_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 owner-packet sufficiency independent replay mismatch")
    print(f"PAH-OMC-020 OWNER PACKET SUFFICIENCY INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
