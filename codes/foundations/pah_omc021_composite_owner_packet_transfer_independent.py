#!/usr/bin/env python3
"""Non-importing independent replay for PAH-OMC-021."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-021-composite-owner-packet-transfer-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc021-composite-owner-packet-transfer/independent.json"


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


def row(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    ok = actual == expected
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = read(CONTRACT)
    omc = read(ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json")
    audit = read(ROOT / "strategy/pa-hyp/owner-morphism-audit-v1.json")
    pa001 = read(ROOT / "strategy/pa-hyp/PAH-001-v1.json")
    rows: list[dict[str, Any]] = []
    pins = contract["source_pins"]
    row(rows, "independent parent pin", omc["parent"]["sha256"], pins["strategy/pa-hyp/PAH-001-v1.json"])
    row(rows, "independent PAH pin", digest(ROOT / "strategy/pa-hyp/PAH-001-v1.json"), pins["strategy/pa-hyp/PAH-001-v1.json"])
    row(rows, "independent OMC pin", digest(ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"), pins["strategy/pa-hyp/PAH-OMC-001-v1.json"])
    row(rows, "contract result", contract.get("result_id"), "R-558")
    row(rows, "successor is constructed", omc["provenance"]["constructed_hypothesis"], True)
    row(rows, "successor lacks external authority", omc["provenance"]["external_source"], False)
    row(rows, "source functional preserved", omc["preservation_firewall"]["functional_unchanged"], True)
    row(rows, "root families complete", set(omc["universal_directed_root_labels"]) == {"phase", "matter_transfer", "link", "aperture"}, True)
    row(rows, "finite core and B domain", "finite_common_invariant_core" in omc["generator_and_projection"] and "domain_B" in omc["directed_root_hilbert_space"], True)
    row(rows, "finite audit passed", audit["finite_common_dynamics_verdict"], "MAINLINE_ADVANCE")
    row(rows, "finite audit remains stage two hold", audit["overall_programme_state"], "HOLD_FOR_EVIDENCE_AT_STAGE_2")
    row(rows, "no N1 recovery", "recovery sequence" in json.dumps(omc).lower(), False)
    row(rows, "no N2b Mosco packet", "mosco" in json.dumps(omc).lower(), False)
    row(rows, "no N2c boundary escape", "boundary escape" in json.dumps(omc).lower(), False)
    row(rows, "no N2d R-512 target", "r-512" in json.dumps(omc).lower(), False)
    row(rows, "no full J or D fields", any(token in json.dumps(omc).lower() for token in ("j(n,j)", "d(n)", "anchored target defect")), False)
    row(rows, "parent schema unchanged", pa001.get("schema"), "tect/pre-a-researcher-hypothesis/1.0")
    row(rows, "hold verdict", contract["admission_rule"]["current"], "HOLD_FOR_EVIDENCE")
    fields = contract["transfer_fields"]
    row(rows, "finite field count", sum(value["status"] == "FINITE_PRESENT" for value in fields.values()), 2)
    row(rows, "asymptotic missing count", sum(value["status"] == "ASYMPTOTIC_MISSING" for value in fields.values()), 6)
    row(rows, "authority ineligible count", sum(value["status"] == "SOURCE_OWNER_INELIGIBLE" for value in fields.values()), 1)
    row(rows, "verification finite-only", fields["verification"]["status"], "FINITE_PRESENT_NOT_SUFFICIENT")
    row(rows, "physical firewall", all(token in " ".join(contract["non_claims"]).lower() for token in ("physical pre-a", "spacetime", "qft", "gravity", "toe")), True)
    payload = {
        "schema": "tect/pah-omc021-composite-owner-packet-transfer-independent/1.0",
        "audit_id": "PAH-OMC-021-COMPOSITE-OWNER-PACKET-TRANSFER-INDEPENDENT-001",
        "result_id": "R-558",
        "task_id": "T-088",
        "status": "PASS_COMPOSITE_FINITE_FIELDS_ONLY_HOLD_FOR_EVIDENCE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "source_hashes": {path: digest(ROOT / path) for path in pins},
        "field_status": {field: value["status"] for field, value in fields.items()},
        "finding": "Independent reconstruction agrees that PAH-OMC-001 contributes only finite composite definitions; the six asymptotic fields and source authority required by R-557 remain absent.",
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc021_composite_owner_packet_transfer_independent.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = write_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-021 independent replay mismatch")
    print(f"PAH-OMC-021 COMPOSITE OWNER PACKET INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
