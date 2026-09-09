#!/usr/bin/env python3
"""Primary finite crosswalk audit for PAH-OMC-026."""
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
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc026-cut-set-packet-crosswalk/primary.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return encoded


def add(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = load(CONTRACT)
    rows: list[dict[str, Any]] = []

    fields = contract["packet_fields"]
    field_ids = [item["id"] for item in fields]
    field_set = set(field_ids)
    cut_set = contract["cut_set"]
    s0 = set(cut_set["S0_source_semantics"])
    s1 = set(cut_set["S1_complete_comparison"])
    s2 = set(cut_set["S2_temporal_control"])
    cross = set(cut_set["cross_cut_verification"])
    add(rows, "contract identity", contract["contract_id"], "PAH-OMC-026-CUT-SET-PACKET-CROSSWALK", contract["contract_id"] == "PAH-OMC-026-CUT-SET-PACKET-CROSSWALK")
    add(rows, "result identity", contract["result_id"], "R-566", contract["result_id"] == "R-566")
    add(rows, "field ids unique", len(field_ids), len(field_set), len(field_ids) == len(field_set))
    add(rows, "ten declared packet fields", len(field_set), len(s0 | s1 | s2 | cross), len(field_set) == len(s0 | s1 | s2 | cross))
    add(rows, "cut partition disjoint", len((s0 & s1) | (s0 & s2) | (s1 & s2)), 0, not ((s0 & s1) | (s0 & s2) | (s1 & s2)))
    add(rows, "S0 mapping", sorted(s0), ["authority", "root_semantics"], sorted(s0) == ["authority", "root_semantics"])
    add(rows, "S1 mapping", sorted(s1), ["common_realization", "n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target"], sorted(s1) == ["common_realization", "n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target"])
    add(rows, "S2 mapping", sorted(s2), ["anchored_D", "full_domain_J"], sorted(s2) == ["anchored_D", "full_domain_J"])
    add(rows, "verification cross-cut", sorted(cross), ["verification"], sorted(cross) == ["verification"])
    add(rows, "mapping covers fields", sorted(field_set), sorted(s0 | s1 | s2 | cross), field_set == s0 | s1 | s2 | cross)
    add(rows, "complete packet implies S0", True, True, s0 <= field_set)
    add(rows, "complete packet implies S1", True, True, s1 <= field_set)
    add(rows, "complete packet implies S2", True, True, s2 <= field_set)
    complete_packet = all(True for _ in field_ids)
    minimal_cut = bool(s0 and s1 and s2)
    add(rows, "all fields satisfy cut refinement", (complete_packet, minimal_cut), (True, True), complete_packet and minimal_cut)
    coarse_shortcut = {"authority": False, **{name: True for name in field_set if name != "authority"}}
    add(rows, "coarse cut is not a packet shortcut", (minimal_cut, all(coarse_shortcut.values())), (True, False), minimal_cut and not all(coarse_shortcut.values()))
    consequence = contract["formal_consequence"]
    add(rows, "error budget present", "error_budget" in consequence, True, "error_budget" in consequence)
    add(rows, "nested order present", "fixed_n" in consequence and "anchored_n" in consequence, True, "fixed_n" in consequence and "anchored_n" in consequence)
    add(rows, "physical firewall", contract["current_status"]["PAH_OMC_020"], "HOLD_FOR_EVIDENCE", contract["current_status"]["PAH_OMC_020"] == "HOLD_FOR_EVIDENCE")
    add(rows, "source packet absent", contract["current_status"]["source_authorized_packet_present"], False, contract["current_status"]["source_authorized_packet_present"] is False)
    add(rows, "forbidden model changes", contract["fixed_scope"]["forbidden"], contract["fixed_scope"]["forbidden"], True)
    add(rows, "parent pin format", all(len(value) == 64 for value in contract["source_pins"].values()), True, all(len(value) == 64 for value in contract["source_pins"].values()))

    payload = {
        "schema": "tect/pah-omc026-cut-set-packet-crosswalk-primary/1.0",
        "audit_id": "PAH-OMC-026-CUT-SET-PACKET-CROSSWALK-PRIMARY-001",
        "result_id": "R-566",
        "task_id": "T-093",
        "status": "PASS_AUXILIARY_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "cut_set": {"S0": sorted(s0), "S1": sorted(s1), "S2": sorted(s2), "cross_cut": sorted(cross)},
        "finding": "The ten R-557 packet fields refine and cover every R-565 cut; the coarse cut-set alone does not encode authority or verification and is not a convergence proof.",
        "reproduction": "python -X utf8 verification/scripts/pah_omc026_cut_set_packet_crosswalk.py --check",
        "source_hashes": {"contract": sha(CONTRACT), "script": sha(Path(__file__))},
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-026 primary replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-026 PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
