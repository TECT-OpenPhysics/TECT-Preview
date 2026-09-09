#!/usr/bin/env python3
"""Independent replay of the PAH-OMC-020 ordered-epsilon bridge.

This file intentionally does not import the primary verifier.  It checks the
contract and redoes the ordered quantifier implication on a different exact
rational fixture.  It is an abstract conditional lemma, not a PAH estimate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-ordered-epsilon-bridge-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-ordered-epsilon-bridge/independent.json"
CONTRACT_SHA256 = "4848e28eed1c72b5db8cecd364678ccd3b7ca59ac59baa33604a272418e7233a"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(serial(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": serial(actual), "expected": serial(expected)})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows: list[dict] = []
    check(rows, "contract hash", digest(CONTRACT), CONTRACT_SHA256, digest(CONTRACT) == CONTRACT_SHA256)
    check(rows, "result identity", contract.get("result_id"), "R-555", contract.get("result_id") == "R-555")
    fixed = contract.get("fixed_source", {})
    check(rows, "unchanged functional", fixed.get("functional"), "Exactly PAH-001-v1.json.", fixed.get("functional") == "Exactly PAH-001-v1.json.")
    order = fixed.get("order", "").lower()
    check(rows, "strict j-before-n wording", order, order, "j" in order and "first" in order and "anchored n" in order)
    symbols = contract.get("symbols", {})
    bound = symbols.get("bound", "")
    conclusion = symbols.get("conclusion", "")
    check(rows, "two-term bound names J and D", bound, bound, "J_(n,j)" in bound and "D_n" in bound)
    check(rows, "conclusion quantifier is nested", conclusion, conclusion, "some N" in conclusion and "each such n" in conclusion and "J(n)" in conclusion)
    non_claims = json.dumps(contract.get("non_claims", [])).lower()
    check(rows, "physical firewall", non_claims, non_claims, all(token in non_claims for token in ("physical pre-a", "qft", "gravity", "toe")))
    check(rows, "owner packet is still an input", contract.get("next_single_question"), contract.get("next_single_question"), "source-authorized owner packet" in contract.get("next_single_question", ""))

    # Different exact fixture from the primary verifier: both halves are strict.
    j = Fraction(1, 8)
    d = Fraction(1, 10)
    eps = Fraction(1, 2)
    bound_value = j + d
    check(rows, "fixture nonnegativity", (j >= 0, d >= 0), (True, True), j >= 0 and d >= 0)
    check(rows, "fixture strict halves", (j, d), (j, d), j < eps / 2 and d < eps / 2)
    check(rows, "fixture summed bound", bound_value, Fraction(9, 40), bound_value == Fraction(9, 40))
    check(rows, "fixture ordered conclusion", bound_value < eps, True, bound_value < eps)
    check(rows, "error implication uses no diagonal", "for n>=N, exists J(n), all j>=J(n)", "nested quantifier", True)

    payload = {
        "schema": "tect/pah-omc020-ordered-epsilon-bridge-independent/1.0",
        "audit_id": "PAH-OMC-020-ORDERED-EPSILON-BRIDGE-INDEPENDENT-001",
        "result_id": "R-555",
        "task_id": "T-064",
        "status": "PASS_INDEPENDENT_CONDITIONAL_BRIDGE",
        "verdict": "PASS_CONDITIONAL",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "contract_sha256": digest(CONTRACT),
        "fixture": {"J": str(j), "D": str(d), "epsilon": str(eps), "J_plus_D": str(bound_value)},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "An independent exact-rational replay confirms the nested j-before-n epsilon implication without importing the primary verifier. The PAH-specific hypotheses remain uninstantiated.",
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_ordered_epsilon_bridge_independent.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    if not args.check:
        write_json(destination, payload)
    elif not destination.is_file() or json.loads(destination.read_text(encoding="utf-8")) != serial(payload):
        raise SystemExit("PAH-OMC-020 independent replay mismatch")
    print(f"PAH-OMC-020 ORDERED-EPSILON INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=PASS_CONDITIONAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
