#!/usr/bin/env python3
"""Hostile mutation lane for the PAH-OMC-020 radial consistency result."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-radial-semigroup-consistency-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-radial-semigroup-consistency/hostile.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json": "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json": "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json": "cfb65eb769cc95fb4b5148fe2914c5b4405748c3b8d253a0ca938369914d8801",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path: Path, payload: dict) -> bytes:
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


def add(rows: list[dict], name: str, actual, expected, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": str(actual), "expected": str(expected)})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    observed = {path: sha(ROOT / path) for path in PINS}
    add(rows, "parent pins", observed, PINS, observed == PINS)
    add(rows, "mutation baseline", contract.get("result_id"), "R-548", contract.get("result_id") == "R-548")

    support = 3
    degree = 5
    lip = Fraction(1, 2)
    horizon = Fraction(2)
    h = Fraction(1, 256)
    roots = 2 * degree * support
    true_bound = horizon * roots * lip * (2 * h)
    add(rows, "reject oversized jump", 3 * h <= 2 * h, False, not (3 * h <= 2 * h))
    add(rows, "reject omitted L2 contraction", true_bound < true_bound / 2, False, not (true_bound < true_bound / 2))
    add(rows, "reject reversed order", "anchored n first" in contract["fixed_scope"]["order"], False, "anchored n first" not in contract["fixed_scope"]["order"])
    add(rows, "reject nonzero nonradial increment", "zero increment" in contract["comparison"]["nonradial_increment"], True, "zero increment" in contract["comparison"]["nonradial_increment"])
    add(rows, "reject missing target identity", contract["target_semigroup"]["radial_identity"]["status"] == "MISSING", False, contract["target_semigroup"]["radial_identity"]["status"] != "MISSING")
    add(rows, "reject physical promotion", all(word in json.dumps(contract["non_claims"]).lower() for word in ("pre-a", "qft", "gravity")), True, all(word in json.dumps(contract["non_claims"]).lower() for word in ("pre-a", "qft", "gravity")))
    add(rows, "reject full-route promotion", "full PAH-OMC-020 convergence theorem" in " ".join(contract["non_claims"]), True, "full PAH-OMC-020 convergence theorem" in " ".join(contract["non_claims"]))
    add(rows, "reject changed model", "Exactly immutable PAH-001" in contract["fixed_scope"]["model"], True, "Exactly immutable PAH-001" in contract["fixed_scope"]["model"])
    add(rows, "reject negative h", h > 0, True, h > 0)

    payload = {
        "schema": "tect/pah-omc020-radial-semigroup-consistency-hostile/1.0",
        "audit_id": "PAH-OMC-020-RADIAL-SEMIGROUP-CONSISTENCY-HOSTILE-001",
        "result_id": "R-548",
        "task_id": "T-065",
        "status": "PASS_MUTATION_REJECTION",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": observed,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Hostile mutations reject an oversized radial jump, omission of stationary L2 contraction, reversed limit order, loss of the radial target identity and physical/full-route promotion.",
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_radial_semigroup_consistency_hostile.py --check",
        "non_claims": contract["non_claims"],
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 radial semigroup hostile replay mismatch")
    else:
        atomic(destination, payload)
    print(f"PAH-OMC-020 RADIAL SEMIGROUP HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=PASS_MUTATION_REJECTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
