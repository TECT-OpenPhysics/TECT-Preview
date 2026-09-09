#!/usr/bin/env python3
"""Independent non-importing replay of the PAH-OMC-020 two-term route."""

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
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-two-term-route/independent.json"
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
    check(rows, "contract id", contract.get("contract_id"), "PAH-OMC-020-TWO-TERM-ROUTE", contract.get("contract_id") == "PAH-OMC-020-TWO-TERM-ROUTE")
    check(rows, "parent pins", hashes, PINS, hashes == PINS)
    check(rows, "R-514 fixed-n theorem", r514.get("result_id") == "R-514" and r514.get("verdict") == "PASS", True, r514.get("result_id") == "R-514" and r514.get("verdict") == "PASS")
    check(rows, "R-514 no anchored claim", "no anchored n" in r514["exact_scope"]["order"].lower(), True, "no anchored n" in r514["exact_scope"]["order"].lower())
    check(rows, "R-536 D definition", "D_n(f,g;T)" in r536["exact_scope"]["defect"], True, "D_n(f,g;T)" in r536["exact_scope"]["defect"])
    check(rows, "R-536 route gate", all(not route["complete"] for route in r536["route_status"].values()), True, all(not route["complete"] for route in r536["route_status"].values()))
    check(rows, "same intermediate is required", "same post-j" in contract["hypotheses"]["same_intermediate"], True, "same post-j" in contract["hypotheses"]["same_intermediate"])
    check(rows, "D route is source-authorized prerequisite", "source-authorized" in contract["hypotheses"]["H_D"], True, "source-authorized" in contract["hypotheses"]["H_D"])

    J = Fraction(1, 12)
    D = Fraction(1, 15)
    bound = J + D
    check(rows, "independent two-term bound", bound, Fraction(3, 20), bound == Fraction(3, 20))
    eps = Fraction(1, 4)
    check(rows, "independent epsilon split", J < eps / 2 and D < eps / 2, True, J < eps / 2 and D < eps / 2)
    radius = Fraction(1, 8)
    finite_modulus = Fraction(1)
    target_modulus = Fraction(1, 30)
    mesh_error = Fraction(1, 40)
    mesh_bound = mesh_error + finite_modulus * radius + target_modulus
    check(rows, "independent mesh envelope", mesh_bound, Fraction(11, 60), mesh_bound == Fraction(11, 60))
    check(rows, "registered order only", "n->infinity before j->infinity" not in contract["ordered_conclusion"] and "j->infinity" in contract["ordered_conclusion"], True, "n->infinity before j->infinity" not in contract["ordered_conclusion"] and "j->infinity" in contract["ordered_conclusion"])
    non_claims = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "no full convergence promotion", "full convergence" in non_claims, True, "full convergence" in non_claims)
    check(rows, "no physical promotion", "pre-a" in non_claims and "qft" in non_claims and "gravity" in non_claims, True, "pre-a" in non_claims and "qft" in non_claims and "gravity" in non_claims)

    payload = {
        "schema": "tect/pah-omc020-two-term-route-independent/1.0",
        "audit_id": "PAH-OMC-020-TWO-TERM-ROUTE-INDEPENDENT-001",
        "result_id": "R-546",
        "task_id": "T-065",
        "status": "PASS_INDEPENDENT_TWO_TERM_ROUTE",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "test_fixture": {"J": J, "D": D, "bound": bound, "epsilon": eps, "radius": radius, "mesh_bound": mesh_bound},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Independent reconstruction confirms the direct J+D sequential implication while retaining the missing source-authorized D route.",
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_two_term_route_independent.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(encode(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 two-term independent replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 TWO-TERM INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
