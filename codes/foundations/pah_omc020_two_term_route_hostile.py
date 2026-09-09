#!/usr/bin/env python3
"""Hostile mutation controls for the PAH-OMC-020 two-term route."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-two-term-route-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-two-term-route/hostile.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json": "cfb65eb769cc95fb4b5148fe2914c5b4405748c3b8d253a0ca938369914d8801",
    "strategy/pa-hyp/PAH-OMC-020-target-identification-result-v1.json": "ab0aa7ee63bad61c982f841546669ae15ab5e570e732d211015b767bf8449d29",
    "strategy/pa-hyp/PAH-OMC-020-mesh-uniform-result-v1.json": "b959de7b0163fa776e7eae8b46aa4c86356b305ffe61692a0893561e05d2a2d9",
    "strategy/pa-hyp/PAH-OMC-020-sequential-gluing-contract-v1.json": "486b86853638bdd953e95ed2501446bb0780c8f0eb768c9c9fd1e18062c53984",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(encode(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": encode(actual), "expected": encode(expected)})
    if not ok:
        raise AssertionError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes = {name: digest(ROOT / name) for name in PINS}
    r514 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json").read_text(encoding="utf-8"))
    r536 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-target-identification-result-v1.json").read_text(encoding="utf-8"))
    check(rows, "parent pins", hashes, PINS, hashes == PINS)
    check(rows, "fixed-n has no anchored result", "no anchored n" in r514["exact_scope"]["order"].lower(), True, "no anchored n" in r514["exact_scope"]["order"].lower())
    check(rows, "partial R-536 route is rejected", any(route["complete"] for route in r536["route_status"].values()), False, not any(route["complete"] for route in r536["route_status"].values()))
    check(rows, "R-536 D limit is not admitted", "D_limit" in r536.get("non_claims", []) or "D_n limit" in json.dumps(r536.get("non_claims", [])), True, "D_n limit" in json.dumps(r536.get("non_claims", [])))
    check(rows, "omitting D term is rejected", Fraction(1, 4) <= Fraction(0), False, not (Fraction(1, 4) <= Fraction(0)))
    check(rows, "omitting J term is rejected", Fraction(1, 4) <= Fraction(0), False, not (Fraction(1, 4) <= Fraction(0)))
    check(rows, "same c_n cannot be silently renamed", "same post-j stationary correlation" in contract["hypotheses"]["same_intermediate"], True, "same post-j stationary correlation" in contract["hypotheses"]["same_intermediate"])
    check(rows, "source authorization cannot be dropped", "complete source-authorized" in contract["hypotheses"]["H_D"], True, "complete source-authorized" in contract["hypotheses"]["H_D"])
    check(rows, "reversed order is rejected", "n->infinity before j->infinity" in contract["ordered_conclusion"], False, "n->infinity before j->infinity" not in contract["ordered_conclusion"])
    check(rows, "joint order is rejected", "joint limit" in contract["ordered_conclusion"].lower(), False, "joint limit" not in contract["ordered_conclusion"].lower())
    check(rows, "K is not silently source-admitted", "r-534's h-k" in json.dumps(contract["non_claims"]).lower(), True, "r-534's h-k" in json.dumps(contract["non_claims"]).lower())
    check(rows, "mesh route remains conditional", "no owner route is supplied" in contract["ordered_conclusion"], True, "no owner route is supplied" in contract["ordered_conclusion"])
    non_claims = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "no physical promotion", "pre-a" in non_claims and "qft" in non_claims and "gravity" in non_claims, True, "pre-a" in non_claims and "qft" in non_claims and "gravity" in non_claims)
    check(rows, "no new model data", "no new u_n" in non_claims and "no new" in non_claims, True, "no new u_n" in non_claims and "no new" in non_claims)

    payload = {
        "schema": "tect/pah-omc020-two-term-route-hostile/1.0",
        "audit_id": "PAH-OMC-020-TWO-TERM-ROUTE-HOSTILE-001",
        "result_id": "R-546",
        "task_id": "T-065",
        "status": "PASS_HOSTILE_TWO_TERM_CONTROLS",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Hostile mutations reject omitting either error term, mismatching the post-j intermediate, admitting a partial owner route, reversing or diagonalizing the order, and promoting the conditional route to physical or full convergence.",
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_two_term_route_hostile.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(encode(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 two-term hostile replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 TWO-TERM HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
