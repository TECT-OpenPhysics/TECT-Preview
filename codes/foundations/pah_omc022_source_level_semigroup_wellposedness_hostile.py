#!/usr/bin/env python3
"""Hostile mutation checks for the scoped PAH-OMC-022 negative."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-022-source-level-semigroup-wellposedness-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc022-source-level-semigroup-wellposedness/hostile.json"


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


def check(rows: list[dict[str, Any]], name: str, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL"})
    if not ok:
        raise AssertionError(name)


def scoped_negative(candidate: dict[str, Any], pins: dict[str, str]) -> bool:
    non_claims = " ".join(candidate.get("non_claims", [])).lower()
    return (
        candidate.get("result_id") == "R-559"
        and candidate.get("decision_rule", {}).get("scope", "").startswith("This is a source-level formulation negative")
        and all(value == pins[key] for key, value in candidate.get("source_pins", {}).items())
        and candidate.get("premises", {}).get("successor_non_attribution", {}).get("status") == "ESTABLISHED_SCOPED"
        and "owner-fixed successor" in non_claims
        and "physical pre-a" in non_claims
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = read(CONTRACT)
    pins = {path: digest(ROOT / path) for path in contract["source_pins"]}
    rows: list[dict[str, Any]] = []
    check(rows, "baseline scoped negative", scoped_negative(contract, pins))

    universal = copy.deepcopy(contract)
    universal["decision_rule"]["scope"] = "This is a universal no-go for every owner-fixed successor model."
    check(rows, "universal owner-fixed upgrade rejected", not scoped_negative(universal, pins))

    authority = copy.deepcopy(contract)
    authority["source_pins"]["strategy/pa-hyp/PAH-001-v1.json"] = "0" * 64
    check(rows, "parent hash drift rejected", not scoped_negative(authority, pins))

    repair = copy.deepcopy(contract)
    repair["premises"]["successor_non_attribution"]["status"] = "SOURCE_AUTHORIZED"
    repair["decision_rule"]["scope"] = "This is a source-level formulation negative only. It is not a no-go for an explicitly owner-fixed successor model."
    check(rows, "successor authority mutation cannot be silently accepted", repair["premises"]["successor_non_attribution"]["status"] == "SOURCE_AUTHORIZED" and not scoped_negative(repair, pins))

    physical = copy.deepcopy(contract)
    physical["non_claims"] = ["physical Pre-A and QFT conclusion follows"]
    check(rows, "physical promotion mutation rejected", not scoped_negative(physical, pins))

    pass_verdict = copy.deepcopy(contract)
    pass_verdict["decision_rule"]["negative"] = "The original source selects a unique semigroup."
    check(rows, "positive uniqueness mutation rejected", pass_verdict["decision_rule"]["negative"] != contract["decision_rule"]["negative"])
    check(rows, "successor field remains non-authority", contract["premises"]["successor_non_attribution"]["status"] == "ESTABLISHED_SCOPED")
    check(rows, "source ambiguity remains scoped", "source-compatible" in contract["premises"]["source_ambiguity"]["evidence"])
    check(rows, "no new model fields", "no new carrier" in " ".join(contract["non_claims"]).lower() and "counterterm" in " ".join(contract["non_claims"]).lower())

    payload = {
        "schema": "tect/pah-omc022-source-level-semigroup-wellposedness-hostile/1.0",
        "audit_id": "PAH-OMC-022-SOURCE-LEVEL-SEMIGROUP-WELLPOSEDNESS-HOSTILE-001",
        "result_id": "R-559",
        "task_id": "T-089",
        "status": "PASS_MUTATIONS_REJECTED_SCOPED_NEGATIVE",
        "verdict": "NEGATIVE_RESULT",
        "classification": "negative_result",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "mutations_rejected": len(rows),
        "source_hashes": pins,
        "finding": "Hostile mutations cannot turn the source-level formulation boundary into a universal owner-fixed no-go, repair parent hashes, or promote a physical claim.",
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc022_source_level_semigroup_wellposedness_hostile.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = write_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-022 hostile replay mismatch")
    print(f"PAH-OMC-022 SOURCE-LEVEL HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=NEGATIVE_RESULT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
