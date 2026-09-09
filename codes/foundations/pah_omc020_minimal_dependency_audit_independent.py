#!/usr/bin/env python3
"""Non-importing independent replay for the PAH-OMC-020 dependency ledger."""

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
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-minimal-dependency-audit/independent.json"


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


def assert_row(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = read(CONTRACT)
    rows: list[dict[str, Any]] = []
    pins = contract["source_pins"]
    observed = {name: digest(ROOT / name) for name in pins}
    assert_row(rows, "contract identity", contract.get("contract_id") == "PAH-OMC-020-MINIMAL-DEPENDENCY-AUDIT", contract.get("contract_id"), "PAH-OMC-020-MINIMAL-DEPENDENCY-AUDIT")
    assert_row(rows, "pinned bytes", observed == pins, observed, pins)
    assert_row(rows, "unchanged model", contract["fixed_scope"]["functional"].endswith("PAH-001-v1.json."), contract["fixed_scope"]["functional"], "PAH-001")
    assert_row(rows, "external time firewall", "External stochastic Markov time" in contract["fixed_scope"]["time"], contract["fixed_scope"]["time"], True)
    assert_row(rows, "ordered quantifier", "fixed n" in contract["fixed_scope"]["order"] and "anchored n" in contract["fixed_scope"]["order"], contract["fixed_scope"]["order"], True)

    files = {name: read(ROOT / name) for name in pins}
    r514 = files["strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json"]
    r548 = files["strategy/pa-hyp/PAH-OMC-020-radial-semigroup-consistency-result-v1.json"]
    r555 = files["strategy/pa-hyp/PAH-OMC-020-ordered-epsilon-bridge-result-v1.json"]
    r552 = files["strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json"]
    r536 = files["strategy/pa-hyp/PAH-OMC-020-target-identification-result-v1.json"]
    r539 = files["strategy/pa-hyp/PAH-OMC-020-N2B-common-space-audit-v1.1-result-v1.json"]
    n2a = files["strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json"]
    assert_row(rows, "bridge is conditional", r555.get("result_id") == "R-555" and r555.get("verdict") == "PASS_CONDITIONAL", [r555.get("result_id"), r555.get("verdict")], ["R-555", "PASS_CONDITIONAL"])
    assert_row(rows, "finite target input", r514.get("closed_scoped_gate", "").startswith("Fixed-n"), r514.get("closed_scoped_gate"), "Fixed-n")
    radial_scope = json.dumps(r548.get("exact_scope", {})).lower()
    assert_row(rows, "radial target input", r548.get("verdict") == "PASS_RESTRICTED" and ("amplitude-only" in radial_scope or "h_rad" in radial_scope), [r548.get("verdict"), radial_scope], "PASS_RESTRICTED amplitude-only")
    root_text = r552.get("finding", "").lower()
    assert_row(rows, "root ambiguity", r552.get("verdict") == "HOLD_FOR_EVIDENCE" and "root" in root_text and "multiplicity" in root_text, r552.get("finding"), "HOLD root multiplicity")
    assert_row(rows, "form defect", r536.get("verdict") == "HOLD_FOR_EVIDENCE" and "D_n" in r536.get("finding", ""), r536.get("finding"), "HOLD D_n")
    assert_row(rows, "common-space packet absent", r539.get("verdict") == "HOLD_FOR_EVIDENCE" and "U_n" in r539.get("finding", ""), r539.get("finding"), "HOLD U_n")
    assert_row(rows, "intake does not authorize", n2a.get("status") == "INTAKE_CONTRACT_ONLY" and n2a.get("provenance", {}).get("source_authorized_packet_present") is False, n2a.get("status"), "INTAKE_CONTRACT_ONLY")

    statuses = {row["id"]: row["status"] for row in contract["dependency_ledger"]}
    required_open = {"root_owner", "common_map_form", "anchored_D"}
    assert_row(rows, "full-domain hold", required_open.issubset({key for key, value in statuses.items() if value == "OPEN"}), sorted(key for key, value in statuses.items() if value == "OPEN"), sorted(required_open))
    assert_row(rows, "radial remains restricted", statuses.get("radial_instantiation") == "CLOSED_RESTRICTED", statuses.get("radial_instantiation"), "CLOSED_RESTRICTED")
    non_claims = json.dumps(contract.get("non_claims", [])).lower()
    assert_row(rows, "non-physical scope", all(word in non_claims for word in ("pre-a", "qft", "gravity", "toe")), True, True)

    payload = {
        "schema": "tect/pah-omc020-minimal-dependency-audit-independent/1.0",
        "audit_id": "PAH-OMC-020-MINIMAL-DEPENDENCY-AUDIT-INDEPENDENT-001",
        "result_id": "R-556",
        "task_id": "T-086",
        "status": "HOLD_FOR_EVIDENCE_MINIMAL_DEPENDENCY_LEDGER",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "source_hashes": observed,
        "finding": "An independent replay agrees that the ordered bridge is conditional, the finite/radial inputs are restricted, and three full-domain source obligations remain open.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_minimal_dependency_audit_independent.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = write_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 minimal dependency independent replay mismatch")
    print(f"PAH-OMC-020 MINIMAL DEPENDENCY INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
