#!/usr/bin/env python3
"""Primary replay for the PAH-OMC-020 minimal dependency ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-minimal-dependency-audit-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-minimal-dependency-audit/primary.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = load(CONTRACT)
    rows: list[dict[str, Any]] = []
    pins = contract["source_pins"]
    actual_pins = {path: sha(ROOT / path) for path in pins}
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc020-minimal-dependency-audit-contract/1.0", contract.get("schema") == "tect/pah-omc020-minimal-dependency-audit-contract/1.0")
    check(rows, "result identity", contract.get("result_id"), "R-556", contract.get("result_id") == "R-556")
    check(rows, "task identity", contract.get("task_id"), "T-086", contract.get("task_id") == "T-086")
    check(rows, "source pins", actual_pins, pins, actual_pins == pins)

    fixed = contract["fixed_scope"]
    check(rows, "unchanged functional", fixed["functional"], "Exactly strategy/pa-hyp/PAH-001-v1.json.", fixed["functional"] == "Exactly strategy/pa-hyp/PAH-001-v1.json.")
    check(rows, "external Markov time", fixed["time"], "External stochastic Markov time on finite compact intervals; no physical-time interpretation.", fixed["time"].startswith("External stochastic Markov time"))
    check(rows, "j-before-n order", fixed["order"], "The registered j-to-infinity limit at fixed n followed by the anchored n limit.", "fixed n" in fixed["order"] and "anchored n" in fixed["order"])
    forbidden = fixed["forbidden"].lower()
    check(rows, "forbidden repair firewall", all(token in forbidden for token in ("new rate", "carrier", "direct-sum", "physical-empty")), True, all(token in forbidden for token in ("new rate", "carrier", "direct-sum", "physical-empty")))

    paths = {path: load(ROOT / path) for path in pins}
    pa001 = paths["strategy/pa-hyp/PAH-001-v1.json"]
    r514 = paths["strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json"]
    r548 = paths["strategy/pa-hyp/PAH-OMC-020-radial-semigroup-consistency-result-v1.json"]
    r555 = paths["strategy/pa-hyp/PAH-OMC-020-ordered-epsilon-bridge-result-v1.json"]
    r552 = paths["strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json"]
    r536 = paths["strategy/pa-hyp/PAH-OMC-020-target-identification-result-v1.json"]
    r539 = paths["strategy/pa-hyp/PAH-OMC-020-N2B-common-space-audit-v1.1-result-v1.json"]
    n2a = paths["strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json"]
    check(rows, "PAH-001 schema", pa001.get("schema"), "tect/pre-a-researcher-hypothesis/1.0", pa001.get("schema") == "tect/pre-a-researcher-hypothesis/1.0")
    check(rows, "ordered bridge result", r555.get("result_id"), "R-555", r555.get("result_id") == "R-555")
    check(rows, "ordered bridge conditional", r555.get("verdict"), "PASS_CONDITIONAL", r555.get("verdict") == "PASS_CONDITIONAL")
    check(rows, "finite J result", r514.get("result_id"), "R-514", r514.get("result_id") == "R-514")
    check(rows, "finite J scope", "fixed-n" in r514.get("closed_scoped_gate", "").lower(), True, "fixed-n" in r514.get("closed_scoped_gate", "").lower())
    check(rows, "radial result", r548.get("result_id"), "R-548", r548.get("result_id") == "R-548")
    check(rows, "radial restriction", "amplitude-only" in json.dumps(r548.get("exact_scope", {})).lower(), True, "amplitude-only" in json.dumps(r548.get("exact_scope", {})).lower())
    root_finding = r552.get("finding", "").lower()
    check(rows, "root owner remains open", r552.get("verdict"), "HOLD_FOR_EVIDENCE", r552.get("verdict") == "HOLD_FOR_EVIDENCE" and "root" in root_finding and "multiplicity" in root_finding)
    check(rows, "common map remains open", r539.get("verdict"), "HOLD_FOR_EVIDENCE", r539.get("verdict") == "HOLD_FOR_EVIDENCE" and "common" in r539.get("finding", "").lower())
    check(rows, "anchored target remains open", r536.get("verdict"), "HOLD_FOR_EVIDENCE", r536.get("verdict") == "HOLD_FOR_EVIDENCE" and "D_n" in r536.get("finding", ""))
    check(rows, "N2a is intake only", n2a.get("status"), "INTAKE_CONTRACT_ONLY", n2a.get("status") == "INTAKE_CONTRACT_ONLY" and n2a.get("provenance", {}).get("source_authorized_packet_present") is False)

    ledger = {row["id"]: row for row in contract["dependency_ledger"]}
    expected_statuses = {
        "ordered_bridge": "CLOSED_CONDITIONAL",
        "fixed_n_J": "CLOSED_RESTRICTED_AND_FINITE_TARGET",
        "root_owner": "OPEN",
        "common_map_form": "OPEN",
        "anchored_D": "OPEN",
        "radial_instantiation": "CLOSED_RESTRICTED",
    }
    check(rows, "ledger identifiers", sorted(ledger), sorted(expected_statuses), sorted(ledger) == sorted(expected_statuses))
    check(rows, "ledger statuses", {key: value.get("status") for key, value in ledger.items()}, expected_statuses, {key: value.get("status") for key, value in ledger.items()} == expected_statuses)
    open_full = [key for key in ("root_owner", "common_map_form", "anchored_D") if ledger[key]["status"] == "OPEN"]
    check(rows, "full-domain open obligations", open_full, ["root_owner", "common_map_form", "anchored_D"], open_full == ["root_owner", "common_map_form", "anchored_D"])
    radial_closed = ledger["radial_instantiation"]["status"] == "CLOSED_RESTRICTED" and ledger["fixed_n_J"]["status"] == "CLOSED_RESTRICTED_AND_FINITE_TARGET"
    check(rows, "radial does not imply full", radial_closed and bool(open_full), True, radial_closed and bool(open_full))
    non_claims = json.dumps(contract["non_claims"]).lower()
    check(rows, "physical firewall", all(token in non_claims for token in ("physical pre-a", "spacetime", "qft", "gravity", "toe")), True, all(token in non_claims for token in ("physical pre-a", "spacetime", "qft", "gravity", "toe")))

    payload = {
        "schema": "tect/pah-omc020-minimal-dependency-audit-primary/1.0",
        "audit_id": "PAH-OMC-020-MINIMAL-DEPENDENCY-AUDIT-PRIMARY-001",
        "result_id": "R-556",
        "task_id": "T-086",
        "status": "HOLD_FOR_EVIDENCE_MINIMAL_DEPENDENCY_LEDGER",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_pins,
        "ledger": {key: value["status"] for key, value in ledger.items()},
        "open_full_domain_obligations": open_full,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "R-555 supplies the exact ordered epsilon implication. R-514 and R-548 supply fixed-n or amplitude-only inputs, but the full PAH route remains held by root-owner uniqueness, a source-authorized common map/form and a full-domain anchored target defect D_n.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_minimal_dependency_audit.py --check",
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 minimal dependency primary replay mismatch")
    print(f"PAH-OMC-020 MINIMAL DEPENDENCY PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
