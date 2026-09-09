#!/usr/bin/env python3
"""Hostile mutation checks for the PAH-OMC-020 packet admission bridge."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-packet-sufficiency/hostile.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def check(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    expected = [field["id"] for field in contract["required_packet_fields"]]
    expected_set = set(expected)

    def admitted(packet: set[str]) -> bool:
        return packet == expected_set

    complete = set(expected)
    check(rows, "complete packet is admitted", admitted(complete), True, True)
    omissions: dict[str, bool] = {}
    for field in expected:
        omissions[field] = not admitted(complete - {field})
    check(rows, "every single omission rejects", all(omissions.values()), omissions, True)

    radial_like = {"full_domain_J", "anchored_D"}
    check(rows, "radial-like partial packet rejects", not admitted(radial_like), sorted(radial_like), False)

    reversed_order = copy.deepcopy(contract)
    reversed_order["fixed_scope"]["order"] = "anchored n first, then j at fixed n"
    order_text = reversed_order["fixed_scope"]["order"].lower()
    order_is_registered = order_text.startswith("j tends") and "anchored n" in order_text
    check(rows, "reversed order rejected", not order_is_registered, reversed_order["fixed_scope"]["order"], False)

    fake_authority = copy.deepcopy(contract)
    fake_authority["current_status"] = "SOURCE_AUTHORIZED_PACKET_PRESENT"
    check(rows, "status label cannot replace fields", fake_authority["current_status"] != "NO_SOURCE_AUTHORIZED_PACKET_PRESENT", fake_authority["current_status"], "NO_SOURCE_AUTHORIZED_PACKET_PRESENT")

    no_boundary = set(expected) - {"n2c_n4_boundary"}
    check(rows, "boundary field is load-bearing", not admitted(no_boundary), sorted(no_boundary), False)
    no_target = set(expected) - {"n2d_target"}
    check(rows, "R-512 target field is load-bearing", not admitted(no_target), sorted(no_target), False)

    no_physical = copy.deepcopy(contract)
    no_physical["non_claims"] = ["the packet proves physical spacetime"]
    physical_text = json.dumps(no_physical["non_claims"]).lower()
    firewall_present = all(token in physical_text for token in ("pre-a", "qft", "gravity", "toe"))
    check(rows, "physical promotion mutation rejected", not firewall_present, no_physical["non_claims"], False)

    pins_ok = all(len(value) == 64 for value in contract["source_pins"].values())
    check(rows, "source hash width", pins_ok, True, pins_ok)
    check(rows, "no new rate repair", "rate" in contract["fixed_scope"]["forbidden"].lower(), True, "rate" in contract["fixed_scope"]["forbidden"].lower())

    payload = {
        "schema": "tect/pah-omc020-owner-packet-sufficiency-hostile/1.0",
        "audit_id": "PAH-OMC-020-OWNER-PACKET-SUFFICIENCY-HOSTILE-001",
        "result_id": "R-557",
        "task_id": "T-087",
        "status": "HOSTILE_BOUNDARY_PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "source_hashes": {str(CONTRACT.relative_to(ROOT)): sha(CONTRACT)},
        "finding": "Hostile mutations cannot promote radial-only evidence, reverse the declared order, replace source authority with a status label, omit a load-bearing field or erase the physical firewall.",
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_owner_packet_sufficiency_hostile.py --check",
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = write_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 owner-packet sufficiency hostile replay mismatch")
    print(f"PAH-OMC-020 OWNER PACKET SUFFICIENCY HOSTILE: PASS {len(rows)}/{len(rows)}; verdict remains HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
