#!/usr/bin/env python3
"""Primary synthesis verifier for the scoped PAH-OMC-022 source negative."""

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
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc022-source-level-semigroup-wellposedness/primary.json"


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
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc022-source-level-semigroup-wellposedness-contract/1.0", contract.get("schema") == "tect/pah-omc022-source-level-semigroup-wellposedness-contract/1.0")
    check(rows, "task identity", contract.get("task_id"), "T-089", contract.get("task_id") == "T-089")
    check(rows, "result identity", contract.get("result_id"), "R-559", contract.get("result_id") == "R-559")
    check(rows, "source pins", actual_pins, pins, actual_pins == pins)

    pa001 = load(ROOT / "strategy/pa-hyp/PAH-001-v1.json")
    r552 = load(ROOT / "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json")
    r553 = load(ROOT / "strategy/pa-hyp/PAH-OMC-020-positive-time-separation-result-v1.json")
    r558 = load(ROOT / "strategy/pa-hyp/PAH-OMC-021-composite-owner-packet-transfer-result-v1.json")
    r557 = load(ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-result-v1.json")
    check(rows, "immutable PAH schema", pa001.get("schema"), "tect/pre-a-researcher-hypothesis/1.0", pa001.get("schema") == "tect/pre-a-researcher-hypothesis/1.0")
    check(rows, "R-552 source ambiguity", r552.get("verdict"), "HOLD_FOR_EVIDENCE", r552.get("verdict") == "HOLD_FOR_EVIDENCE" and "does not select one finite stationary semigroup" in r552.get("finding", ""))
    check(rows, "R-552 derivative distinction", "different generator values" in r552.get("finding", "") and "derivatives" in r552.get("exact_scope", {}).get("semigroup_derivative", ""), True, "different generator values" in r552.get("finding", "") and "derivatives" in r552.get("exact_scope", {}).get("semigroup_derivative", ""))
    check(rows, "R-553 positive-time separation", r553.get("verdict"), "HOLD_FOR_EVIDENCE", r553.get("verdict") == "HOLD_FOR_EVIDENCE" and "positive-time" in json.dumps(r553.get("finding", {})).lower())
    field_status = r558.get("field_status", {})
    check(rows, "successor authority ineligible", field_status.get("authority"), "SOURCE_OWNER_INELIGIBLE", field_status.get("authority") == "SOURCE_OWNER_INELIGIBLE")
    check(rows, "successor finite only", field_status.get("root_semantics"), "FINITE_PRESENT", field_status.get("root_semantics") == "FINITE_PRESENT" and field_status.get("common_realization") == "FINITE_PRESENT")
    check(rows, "successor does not close ordered fields", all(field_status.get(field) == "ASYMPTOTIC_MISSING" for field in ("n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target", "full_domain_J", "anchored_D")), True, all(field_status.get(field) == "ASYMPTOTIC_MISSING" for field in ("n1_recovery", "n2b_form", "n2c_n4_boundary", "n2d_target", "full_domain_J", "anchored_D")))
    check(rows, "R-557 remains conditional", r557.get("verdict"), "HOLD_FOR_EVIDENCE", r557.get("verdict") == "HOLD_FOR_EVIDENCE" and r557.get("claim_bearing") is False)
    check(rows, "source-level negative rule", contract["decision_rule"]["scope"], "This is a source-level formulation negative only. It is not a no-go for an explicitly owner-fixed successor model.", contract["decision_rule"]["scope"] == "This is a source-level formulation negative only. It is not a no-go for an explicitly owner-fixed successor model.")
    check(rows, "no universal owner-fixed no-go", all(token in " ".join(contract["non_claims"]).lower() for token in ("every owner-fixed successor", "r-512 limit")), True, all(token in " ".join(contract["non_claims"]).lower() for token in ("every owner-fixed successor", "r-512 limit")))
    check(rows, "no physical promotion", all(token in " ".join(contract["non_claims"]).lower() for token in ("physical pre-a", "spacetime", "qft", "gravity", "toe")), True, all(token in " ".join(contract["non_claims"]).lower() for token in ("physical pre-a", "spacetime", "qft", "gravity", "toe")))

    payload = {
        "schema": "tect/pah-omc022-source-level-semigroup-wellposedness-primary/1.0",
        "audit_id": "PAH-OMC-022-SOURCE-LEVEL-SEMIGROUP-WELLPOSEDNESS-PRIMARY-001",
        "result_id": "R-559",
        "task_id": "T-089",
        "status": "PASS_SCOPED_SOURCE_LEVEL_NEGATIVE",
        "verdict": "NEGATIVE_RESULT",
        "classification": "negative_result",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_pins,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Immutable PAH-001 does not select one unique finite stationary semigroup: R-552 supplies two source-compatible generators with distinct derivatives and R-553 supplies positive-time separation. R-558 shows the available finite completion is a non-source-authorized successor, so it cannot repair the original-source proposition retroactively.",
        "scope_boundary": "Negative only for the source-level uniqueness/well-posedness of the original PAH-001 proposition; no owner-fixed successor convergence no-go is claimed.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc022_source_level_semigroup_wellposedness.py --check",
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-022 primary replay mismatch")
    print(f"PAH-OMC-022 SOURCE-LEVEL PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=NEGATIVE_RESULT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
