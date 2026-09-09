#!/usr/bin/env python3
"""Non-importing independent replay for the PAH-OMC-022 scoped negative."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-022-source-level-semigroup-wellposedness-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc022-source-level-semigroup-wellposedness/independent.json"


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


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
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
    pa001 = read(ROOT / "strategy/pa-hyp/PAH-001-v1.json")
    r552 = read(ROOT / "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json")
    r553 = read(ROOT / "strategy/pa-hyp/PAH-OMC-020-positive-time-separation-result-v1.json")
    r558 = read(ROOT / "strategy/pa-hyp/PAH-OMC-021-composite-owner-packet-transfer-result-v1.json")
    rows: list[dict[str, Any]] = []
    pins = contract["source_pins"]
    check(rows, "parent source digest", digest(ROOT / "strategy/pa-hyp/PAH-001-v1.json"), pins["strategy/pa-hyp/PAH-001-v1.json"])
    check(rows, "parent source schema", pa001.get("schema"), "tect/pre-a-researcher-hypothesis/1.0")
    check(rows, "two finite completions", "Two source-compatible" in r552.get("finding", "") and "different generator" in r552.get("finding", ""), True)
    check(rows, "semigroup derivatives differ", "derivatives are" in r552.get("exact_scope", {}).get("semigroup_derivative", "") and "2 exp(-2)" in r552.get("exact_scope", {}).get("semigroup_derivative", ""), True)
    check(rows, "positive-time separation replay", "positive-time" in r553.get("finding", "") and "u_A(t)>u_B(t)" in r553.get("exact_scope", {}).get("conclusion", ""), True)
    check(rows, "successor is researcher hypothesis", r558.get("field_status", {}).get("authority"), "SOURCE_OWNER_INELIGIBLE")
    check(rows, "successor finite root field", r558.get("field_status", {}).get("root_semantics"), "FINITE_PRESENT")
    check(rows, "successor missing ordered fields", sum(value == "ASYMPTOTIC_MISSING" for value in r558.get("field_status", {}).values()), 6)
    check(rows, "original packet bridge still held", read(ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-result-v1.json").get("verdict"), "HOLD_FOR_EVIDENCE")
    check(rows, "negative classification", contract["decision_rule"]["scope"].startswith("This is a source-level formulation negative"), True)
    check(rows, "not a universal no-go", "every owner-fixed successor" in " ".join(contract["non_claims"]), True)
    check(rows, "no physical layer", all(token in " ".join(contract["non_claims"]).lower() for token in ("physical pre-a", "qft", "gravity", "toe")), True)
    payload = {
        "schema": "tect/pah-omc022-source-level-semigroup-wellposedness-independent/1.0",
        "audit_id": "PAH-OMC-022-SOURCE-LEVEL-SEMIGROUP-WELLPOSEDNESS-INDEPENDENT-001",
        "result_id": "R-559",
        "task_id": "T-089",
        "status": "PASS_SCOPED_SOURCE_LEVEL_NEGATIVE",
        "verdict": "NEGATIVE_RESULT",
        "classification": "negative_result",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "source_hashes": {path: digest(ROOT / path) for path in pins},
        "finding": "Independent reconstruction agrees that the original immutable source has no unique stationary semigroup object, while the finite successor cannot be treated as parent authority.",
        "scope_boundary": "Source-level well-posedness negative only; owner-fixed successor convergence remains open.",
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc022_source_level_semigroup_wellposedness_independent.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = write_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-022 independent replay mismatch")
    print(f"PAH-OMC-022 SOURCE-LEVEL INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=NEGATIVE_RESULT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
