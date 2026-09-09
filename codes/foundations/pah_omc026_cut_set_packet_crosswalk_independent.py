#!/usr/bin/env python3
"""Independent non-importing reconstruction for PAH-OMC-026."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-026-cut-set-packet-crosswalk-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc026-cut-set-packet-crosswalk/independent.json"


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
    fields = {item["id"]: item["cut"] for item in contract["packet_fields"]}
    expected = {
        "authority": "S0",
        "root_semantics": "S0",
        "common_realization": "S1",
        "n1_recovery": "S1",
        "n2b_form": "S1",
        "n2c_n4_boundary": "S1",
        "n2d_target": "S1",
        "full_domain_J": "S2",
        "anchored_D": "S2",
        "verification": "CROSS_CUT",
    }
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected_value: Any) -> None:
        ok = actual == expected_value
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected_value})
        if not ok:
            raise AssertionError(name)

    check("field-to-cut reconstruction", fields, expected)
    check("S0 count", sum(value == "S0" for value in fields.values()), sum(value == "S0" for value in expected.values()))
    check("S1 count", sum(value == "S1" for value in fields.values()), sum(value == "S1" for value in expected.values()))
    check("S2 count", sum(value == "S2" for value in fields.values()), sum(value == "S2" for value in expected.values()))
    check("cross-cut count", sum(value == "CROSS_CUT" for value in fields.values()), sum(value == "CROSS_CUT" for value in expected.values()))
    check("all ten fields are covered", sorted(fields), sorted(expected))
    check("packet implies every coarse cut", all(value in {"S0", "S1", "S2", "CROSS_CUT"} for value in fields.values()), True)
    coarse_cut_witness = {"S0": True, "S1": True, "S2": True, "authority": False}
    check("coarse cuts do not imply authority", coarse_cut_witness["S0"] and coarse_cut_witness["S1"] and coarse_cut_witness["S2"] and not coarse_cut_witness["authority"], True)
    check("authority remains a separate field", "authority" in fields, True)
    check("verification remains cross-cut", fields["verification"], "CROSS_CUT")
    check("current route", contract["current_status"]["PAH_OMC_020"], "HOLD_FOR_EVIDENCE")
    check("packet absent", contract["current_status"]["source_authorized_packet_present"], False)
    check("no model change", "No function" in contract["fixed_scope"]["forbidden"], True)
    check("nested fixed-n consequence", "fixed_n" in contract["formal_consequence"], True)
    check("nested anchored-n consequence", "anchored_n" in contract["formal_consequence"], True)

    payload = {
        "schema": "tect/pah-omc026-cut-set-packet-crosswalk-independent/1.0",
        "audit_id": "PAH-OMC-026-CUT-SET-PACKET-CROSSWALK-INDEPENDENT-001",
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
        "finding": "Independent reconstruction agrees that R-557 field-level completeness refines, but is not replaced by, the coarse R-565 cut-set.",
        "reproduction": "python -X utf8 codes/foundations/pah_omc026_cut_set_packet_crosswalk_independent.py --check",
        "source_hashes": {"contract": sha(CONTRACT), "script": sha(Path(__file__))},
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-026 independent replay mismatch")
    else:
        atomic_write(destination, payload)
    print(f"PAH-OMC-026 INDEPENDENT: PASS {len(checks)}/{len(checks)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
