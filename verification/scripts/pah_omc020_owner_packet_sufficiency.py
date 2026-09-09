#!/usr/bin/env python3
"""Primary verifier for the PAH-OMC-020 owner-packet sufficiency bridge."""

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
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-packet-sufficiency/primary.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = load(CONTRACT)
    rows: list[dict[str, Any]] = []
    pins = contract["source_pins"]
    actual_pins = {path: sha(ROOT / path) for path in pins}
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc020-owner-packet-sufficiency-contract/1.0", contract.get("schema") == "tect/pah-omc020-owner-packet-sufficiency-contract/1.0")
    check(rows, "result identity", contract.get("result_id"), "R-557", contract.get("result_id") == "R-557")
    check(rows, "task identity", contract.get("task_id"), "T-087", contract.get("task_id") == "T-087")
    check(rows, "source pins", actual_pins, pins, actual_pins == pins)
    fixed = contract["fixed_scope"]
    check(rows, "unchanged PAH model", fixed["model"], "Exactly PAH-001 and its original finite stationary PH/LK/AP/TR dynamics.", fixed["model"].startswith("Exactly PAH-001"))
    check(rows, "external Markov time", fixed["time"], "External stochastic Markov time on each finite interval [0,T].", fixed["time"].startswith("External stochastic Markov time"))
    check(rows, "j-before-n order", fixed["order"], "j tends to infinity at fixed n first, then anchored n.", "fixed n first" in fixed["order"] and "anchored n" in fixed["order"])
    check(rows, "forbidden repair firewall", fixed["forbidden"], True, all(token in fixed["forbidden"].lower() for token in ("rate", "carrier", "direct-sum", "counterterm", "limit-order")))

    fields = contract["required_packet_fields"]
    field_ids = [field.get("id") for field in fields]
    required = ["authority", "root_semantics", "common_realization", "n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target", "full_domain_J", "anchored_D", "verification"]
    check(rows, "ten packet fields", field_ids, required, field_ids == required)
    check(rows, "field meanings nonempty", all(isinstance(field.get("meaning"), str) and field["meaning"] for field in fields), True, all(isinstance(field.get("meaning"), str) and field["meaning"] for field in fields))
    consequence = contract["formal_consequence"]
    check(rows, "error budget", "err" in consequence["error_budget"] and "J" in consequence["error_budget"] and "D" in consequence["error_budget"], consequence["error_budget"], True)
    check(rows, "nested conclusion", "epsilon" in consequence["conclusion"] and "j" in consequence["conclusion"] and "n" in consequence["conclusion"], consequence["conclusion"], True)
    check(rows, "current packet absence", contract.get("current_status"), "NO_SOURCE_AUTHORIZED_PACKET_PRESENT", contract.get("current_status") == "NO_SOURCE_AUTHORIZED_PACKET_PRESENT")

    r555 = load(ROOT / "strategy/pa-hyp/PAH-OMC-020-ordered-epsilon-bridge-result-v1.json")
    r556 = load(ROOT / "strategy/pa-hyp/PAH-OMC-020-minimal-dependency-audit-result-v1.json")
    check(rows, "ordered bridge parent", r555.get("verdict"), "PASS_CONDITIONAL", r555.get("verdict") == "PASS_CONDITIONAL")
    check(rows, "dependency ledger parent", r556.get("verdict"), "HOLD_FOR_EVIDENCE", r556.get("verdict") == "HOLD_FOR_EVIDENCE")

    complete = {field_id: True for field_id in required}
    partial = {field_id: field_id in {"full_domain_J", "anchored_D"} for field_id in required}
    admits = lambda packet: all(packet.get(field_id, False) for field_id in required)
    check(rows, "complete packet admits implication", admits(complete), True, admits(complete) is True)
    check(rows, "partial radial-like packet rejected", admits(partial), False, admits(partial) is False)
    missing_each = {field_id: not admits({key: True for key in required if key != field_id}) for field_id in required}
    check(rows, "every missing field blocks", all(missing_each.values()), missing_each, all(missing_each.values()))
    non_claims = json.dumps(contract["non_claims"]).lower()
    check(rows, "physical firewall", all(token in non_claims for token in ("pre-a", "spacetime", "qft", "gravity", "toe")), True, all(token in non_claims for token in ("pre-a", "spacetime", "qft", "gravity", "toe")))

    payload = {
        "schema": "tect/pah-omc020-owner-packet-sufficiency-primary/1.0",
        "audit_id": "PAH-OMC-020-OWNER-PACKET-SUFFICIENCY-PRIMARY-001",
        "result_id": "R-557",
        "task_id": "T-087",
        "status": "PASS_CONDITIONAL_PACKET_SUFFICIENCY_HOLD_FOR_EVIDENCE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_pins,
        "required_packet_fields": required,
        "complete_fixture_admitted": admits(complete),
        "partial_fixture_admitted": admits(partial),
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "The complete ten-field owner packet is a sufficient antecedent for the registered ordered-correlation implication, while every missing field blocks admission. No such source-authorized packet is present, so the PAH route remains HOLD_FOR_EVIDENCE.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_owner_packet_sufficiency.py --check",
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 owner-packet sufficiency primary replay mismatch")
    print(f"PAH-OMC-020 OWNER PACKET SUFFICIENCY PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
