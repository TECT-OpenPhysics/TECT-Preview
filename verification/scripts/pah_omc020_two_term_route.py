#!/usr/bin/env python3
"""Primary finite crosswalk for the PAH-OMC-020 two-term route."""

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
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-two-term-route/primary.json"
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


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": serial(actual), "expected": serial(expected)})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    actual_hashes = {path: digest(ROOT / path) for path in PINS}
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc020-two-term-route-contract/1.0", contract.get("schema") == "tect/pah-omc020-two-term-route-contract/1.0")
    check(rows, "contract identity", contract.get("result_id"), "R-546", contract.get("result_id") == "R-546")
    check(rows, "parent hashes", actual_hashes, PINS, actual_hashes == PINS)

    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r514 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json").read_text(encoding="utf-8"))
    r536 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-target-identification-result-v1.json").read_text(encoding="utf-8"))
    r545 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-mesh-uniform-result-v1.json").read_text(encoding="utf-8"))
    r534 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-sequential-gluing-contract-v1.json").read_text(encoding="utf-8"))
    check(rows, "PAH packet unchanged", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    order = prereg["scope"]["regulator_order"].lower()
    check(rows, "registered order", "first j" in order and "anchored n" in order, True, "first j" in order and "anchored n" in order)
    check(rows, "external Markov time", "external" in contract["scope"]["time"].lower() and "markov" in contract["scope"]["time"].lower(), True, "external" in contract["scope"]["time"].lower() and "markov" in contract["scope"]["time"].lower())
    check(rows, "R-514 positive fixed-n result", (r514.get("result_id"), r514.get("verdict")), ("R-514", "PASS"), r514.get("result_id") == "R-514" and r514.get("verdict") == "PASS")
    check(rows, "R-514 fixed-n scope", "fixed n" in r514["exact_scope"]["order"].lower() and "no anchored n" in r514["exact_scope"]["order"].lower(), True, "fixed n" in r514["exact_scope"]["order"].lower() and "no anchored n" in r514["exact_scope"]["order"].lower())
    check(rows, "R-514 defines c_n source", "Q_n(t)" in r514["exact_scope"]["target"], True, "Q_n(t)" in r514["exact_scope"]["target"])
    check(rows, "R-536 defect source", r536["exact_scope"]["defect"].startswith("D_n(f,g;T)"), True, r536["exact_scope"]["defect"].startswith("D_n(f,g;T)"))
    check(rows, "R-536 owner route absent", r536["route_status"]["form_route"]["complete"] is False and r536["route_status"]["path_route"]["complete"] is False, False, r536["route_status"]["form_route"]["complete"] is False and r536["route_status"]["path_route"]["complete"] is False)
    check(rows, "R-536 conditional only", r536.get("conditional"), True, r536.get("conditional") is True)
    check(rows, "R-534 retains K boundary", "K_nm" in json.dumps(r534["symbols"]), True, "K_nm" in json.dumps(r534["symbols"]))
    check(rows, "R-545 mesh route retained", r545.get("result_id"), "R-545", r545.get("result_id") == "R-545")
    check(rows, "same c_n hypothesis explicit", "same post-j stationary correlation" in contract["hypotheses"]["same_intermediate"], True, "same post-j stationary correlation" in contract["hypotheses"]["same_intermediate"])
    check(rows, "complete owner route required", "complete source-authorized" in contract["hypotheses"]["H_D"], True, "complete source-authorized" in contract["hypotheses"]["H_D"])

    J = Fraction(3, 100)
    D = Fraction(1, 20)
    bound = J + D
    check(rows, "nonnegative errors", J >= 0 and D >= 0, True, J >= 0 and D >= 0)
    check(rows, "two-term formula", bound, Fraction(2, 25), bound == Fraction(2, 25))
    eps = Fraction(1, 5)
    check(rows, "epsilon budget", J < eps / 2 and D < eps / 2, True, J < eps / 2 and D < eps / 2)
    mesh_error = Fraction(1, 100)
    mesh_bound = mesh_error + Fraction(1, 10) + Fraction(1, 20)
    check(rows, "mesh consequence envelope", mesh_bound, Fraction(4, 25), mesh_bound == Fraction(4, 25))
    check(rows, "no reversed order", "n->infinity before j->infinity" not in contract["ordered_conclusion"], True, "n->infinity before j->infinity" not in contract["ordered_conclusion"])
    non_claims = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "owner and physical firewalls", "owner route" in non_claims and "qft" in non_claims and "gravity" in non_claims, True, "owner route" in non_claims and "qft" in non_claims and "gravity" in non_claims)

    payload = {
        "schema": "tect/pah-omc020-two-term-route-primary/1.0",
        "audit_id": "PAH-OMC-020-TWO-TERM-ROUTE-PRIMARY-001",
        "result_id": "R-546",
        "task_id": "T-065",
        "status": "PASS_CONDITIONAL_TWO_TERM_ROUTE",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_hashes,
        "test_fixture": {"J": J, "D": D, "bound": bound, "epsilon": eps, "mesh_error": mesh_error, "mesh_bound": mesh_bound},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "R-514 and R-536 use the same post-j correlation c_n, so a complete source-authorized R-536 route would reduce the full ordered compact-time error to J_(n,j)+D_n. The route is conditional because the owner packet is absent.",
        "assumptions": contract["hypotheses"],
        "missing_assumptions": [contract["hypotheses"]["H_D"], "R-536 form/path owner route completion"],
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_two_term_route.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 two-term primary replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 TWO-TERM PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
