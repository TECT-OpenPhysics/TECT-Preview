#!/usr/bin/env python3
"""Primary audit for transfer of the PAH-OMC-001 finite owner packet into R-557."""

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
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc021-composite-owner-packet-transfer/primary.json"


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
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc021-composite-owner-packet-transfer-contract/1.0", contract.get("schema") == "tect/pah-omc021-composite-owner-packet-transfer-contract/1.0")
    check(rows, "task identity", contract.get("task_id"), "T-088", contract.get("task_id") == "T-088")
    check(rows, "result identity", contract.get("result_id"), "R-558", contract.get("result_id") == "R-558")
    check(rows, "source pins", actual_pins, pins, actual_pins == pins)

    pa001 = load(ROOT / "strategy/pa-hyp/PAH-001-v1.json")
    omc001 = load(ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json")
    audit = load(ROOT / "strategy/pa-hyp/owner-morphism-audit-v1.json")
    r557 = load(ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-result-v1.json")
    omc_text = json.dumps(omc001, sort_keys=True).lower()
    audit_text = json.dumps(audit, sort_keys=True).lower()

    check(rows, "immutable parent hash", omc001.get("parent", {}).get("sha256"), pins["strategy/pa-hyp/PAH-001-v1.json"], omc001.get("parent", {}).get("sha256") == pins["strategy/pa-hyp/PAH-001-v1.json"])
    provenance = omc001.get("provenance", {})
    source_owner_eligible = provenance.get("external_source") is True or provenance.get("physical_authority") is True
    check(rows, "composite is not parent source authority", source_owner_eligible, False, source_owner_eligible is False)
    check(rows, "researcher successor provenance", provenance.get("constructed_hypothesis"), True, provenance.get("constructed_hypothesis") is True)
    check(rows, "parent preservation firewall", all(omc001.get("preservation_firewall", {}).get(key) is True for key in ("functional_unchanged", "move_families_unchanged", "regulator_unchanged", "limit_order_unchanged")), True, all(omc001.get("preservation_firewall", {}).get(key) is True for key in ("functional_unchanged", "move_families_unchanged", "regulator_unchanged", "limit_order_unchanged")))
    check(rows, "finite root labels", sorted(omc001.get("universal_directed_root_labels", {})), ["aperture", "link", "matter_transfer", "phase"], sorted(omc001.get("universal_directed_root_labels", {})) == ["aperture", "link", "matter_transfer", "phase"])
    duplicate = omc001.get("invalid_and_duplicate_conventions", {})
    check(rows, "duplicate and invalid conventions", all(key in duplicate for key in ("invalid_partial_move", "parallel_edges", "K_equals_2", "channel_counting")), True, all(key in duplicate for key in ("invalid_partial_move", "parallel_edges", "K_equals_2", "channel_counting")))
    common = omc001.get("generator_and_projection", {})
    root_space = omc001.get("directed_root_hilbert_space", {})
    check(rows, "finite common realization", all(key in common for key in ("finite_common_invariant_core", "generator", "candidate_projection")) and all(key in root_space for key in ("space", "inner_product", "definition_B", "factorization_target")), True, all(key in common for key in ("finite_common_invariant_core", "generator", "candidate_projection")) and all(key in root_space for key in ("space", "inner_product", "definition_B", "factorization_target")))
    check(rows, "R-479 finite verification", audit.get("finite_common_dynamics_verdict"), "MAINLINE_ADVANCE", audit.get("finite_common_dynamics_verdict") == "MAINLINE_ADVANCE" and bool(audit.get("files")) and bool(audit.get("runs")) and bool(audit.get("lean", {}).get("declarations")))

    missing_signatures = {
        "n1_recovery": ("recovery sequence" not in omc_text and "n1_recovery" not in omc_text),
        "n2b_form": ("mosco" not in omc_text and "weak-liminf" not in omc_text),
        "n2c_n4_boundary": ("boundary escape" not in omc_text and "n2c" not in omc_text and "n4" not in omc_text),
        "n2d_target": ("r-512" not in omc_text and "minimal closed-form target" not in omc_text),
        "full_domain_J": ("j(n,j)" not in omc_text and "full-domain j" not in audit_text),
        "anchored_D": ("d(n)" not in omc_text and "anchored target defect" not in audit_text),
    }
    for field, absent in missing_signatures.items():
        check(rows, f"{field} absent from finite composite", absent, True, absent)
        check(rows, f"{field} contract status", contract["transfer_fields"][field]["status"], "ASYMPTOTIC_MISSING", contract["transfer_fields"][field]["status"] == "ASYMPTOTIC_MISSING")

    check(rows, "R-557 requires all ten fields", len(contract["transfer_fields"]), 10, len(contract["transfer_fields"]) == 10)
    check(rows, "R-557 remains conditional", r557.get("verdict"), "HOLD_FOR_EVIDENCE", r557.get("verdict") == "HOLD_FOR_EVIDENCE")
    check(rows, "no physical promotion", all(value is False for value in (r557.get("claim_bearing"), r557.get("physical_promotion"))), True, all(value is False for value in (r557.get("claim_bearing"), r557.get("physical_promotion"))))
    statuses = {field: value["status"] for field, value in contract["transfer_fields"].items()}
    check(rows, "current admission hold", contract["admission_rule"]["current"], "HOLD_FOR_EVIDENCE", contract["admission_rule"]["current"] == "HOLD_FOR_EVIDENCE")
    check(rows, "finite-only fields do not close packet", statuses["authority"] == "SOURCE_OWNER_INELIGIBLE" and statuses["n1_recovery"] == "ASYMPTOTIC_MISSING" and statuses["anchored_D"] == "ASYMPTOTIC_MISSING", True, statuses["authority"] == "SOURCE_OWNER_INELIGIBLE" and statuses["n1_recovery"] == "ASYMPTOTIC_MISSING" and statuses["anchored_D"] == "ASYMPTOTIC_MISSING")
    non_claims = " ".join(contract["non_claims"]).lower()
    check(rows, "physical firewall", all(token in non_claims for token in ("physical pre-a", "spacetime", "qft", "gravity", "toe")), True, all(token in non_claims for token in ("physical pre-a", "spacetime", "qft", "gravity", "toe")))

    payload = {
        "schema": "tect/pah-omc021-composite-owner-packet-transfer-primary/1.0",
        "audit_id": "PAH-OMC-021-COMPOSITE-OWNER-PACKET-TRANSFER-PRIMARY-001",
        "result_id": "R-558",
        "task_id": "T-088",
        "status": "PASS_COMPOSITE_FINITE_FIELDS_ONLY_HOLD_FOR_EVIDENCE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_pins,
        "field_status": statuses,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "PAH-OMC-001 transfers exact finite root semantics and common finite realization for the composite model, but it is not source authority for PAH-001 and supplies none of the ordered asymptotic N1/N2b/N2c-N4/N2d/J/D fields required by R-557.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc021_composite_owner_packet_transfer.py --check",
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-021 composite owner packet primary replay mismatch")
    print(f"PAH-OMC-021 COMPOSITE OWNER PACKET PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
