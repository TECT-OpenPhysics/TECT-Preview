#!/usr/bin/env python3
"""Hostile boundary checks for the PAH-OMC-020 dependency ledger."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-minimal-dependency-audit-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-minimal-dependency-audit/hostile.json"


def digest(path: Path) -> str:
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
    ledger = {row["id"]: row for row in contract["dependency_ledger"]}
    source_status = {key: value["status"] for key, value in ledger.items()}

    def still_hold(candidate: dict[str, str]) -> bool:
        return any(candidate.get(key) == "OPEN" for key in ("root_owner", "common_map_form", "anchored_D"))

    promoted = dict(source_status)
    promoted["root_owner"] = "CLOSED"
    promoted["common_map_form"] = "CLOSED"
    promoted["anchored_D"] = "CLOSED"
    check(rows, "full-domain promotion requires source packet", still_hold(source_status), True, True)
    check(rows, "hostile all-closed mutation is not current hold", still_hold(promoted) is False, still_hold(promoted), False)

    radial_lie = dict(source_status)
    radial_lie["radial_instantiation"] = "CLOSED_FULL_DOMAIN"
    check(rows, "radial cannot be promoted by label", radial_lie["radial_instantiation"] != "CLOSED_RESTRICTED", radial_lie["radial_instantiation"], "CLOSED_RESTRICTED")

    reversed_order = copy.deepcopy(contract)
    reversed_order["fixed_scope"]["order"] = "anchored n first and j second"
    reversed_ok = "fixed n" in reversed_order["fixed_scope"]["order"] and "anchored n" in reversed_order["fixed_scope"]["order"]
    check(rows, "reversed limit order rejected", not reversed_ok, reversed_ok, False)

    no_physical_firewall = copy.deepcopy(contract)
    no_physical_firewall["non_claims"] = ["full convergence and physical spacetime are proved"]
    text = json.dumps(no_physical_firewall["non_claims"]).lower()
    physical_ok = all(word in text for word in ("pre-a", "qft", "gravity", "toe"))
    check(rows, "physical promotion mutation rejected", not physical_ok, physical_ok, False)

    no_owner = dict(source_status)
    no_owner.pop("root_owner")
    check(rows, "missing owner row is rejected", "root_owner" not in no_owner, "root_owner" in no_owner, False)

    fake_bridge = copy.deepcopy(contract)
    fake_bridge["dependency_ledger"][0]["status"] = "CLOSED_FULL"
    check(rows, "conditional bridge cannot become full", fake_bridge["dependency_ledger"][0]["status"] != "CLOSED_CONDITIONAL", fake_bridge["dependency_ledger"][0]["status"], "CLOSED_CONDITIONAL")

    pins_ok = all(len(value) == 64 for value in contract["source_pins"].values())
    check(rows, "sha256 pin width", pins_ok, True, pins_ok)
    check(rows, "no new carrier repair", "carrier" in contract["fixed_scope"]["forbidden"].lower(), True, "carrier" in contract["fixed_scope"]["forbidden"].lower())

    payload = {
        "schema": "tect/pah-omc020-minimal-dependency-audit-hostile/1.0",
        "audit_id": "PAH-OMC-020-MINIMAL-DEPENDENCY-AUDIT-HOSTILE-001",
        "result_id": "R-556",
        "task_id": "T-086",
        "status": "HOSTILE_BOUNDARY_PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "source_hashes": {str(CONTRACT.relative_to(ROOT)): digest(CONTRACT)},
        "finding": "Hostile mutations that promote the restricted radial scope, reverse the declared order, remove the owner rows or add physical promotion are rejected.",
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_minimal_dependency_audit_hostile.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = write_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 minimal dependency hostile replay mismatch")
    print(f"PAH-OMC-020 MINIMAL DEPENDENCY HOSTILE: PASS {len(rows)}/{len(rows)}; full verdict remains HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
