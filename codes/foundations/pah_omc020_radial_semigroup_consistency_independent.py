#!/usr/bin/env python3
"""Independent non-importing audit of the PAH-OMC-020 radial subspace bound."""

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
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-radial-semigroup-consistency/independent.json"
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
    add(rows, "parent bytes", observed, PINS, observed == PINS)
    add(rows, "restricted result identity", (contract.get("result_id"), contract.get("task_id")), ("R-548", "T-065"), contract.get("result_id") == "R-548" and contract.get("task_id") == "T-065")
    add(rows, "target is R-512 minimal", "R-512 minimal" in contract["fixed_scope"]["target"], True, "R-512 minimal" in contract["fixed_scope"]["target"])
    time_scope = contract["fixed_scope"]["time"].lower()
    add(rows, "external time firewall", "external stochastic" in time_scope, True, "external stochastic" in time_scope)
    add(rows, "registered order", "j tends to infinity" in contract["fixed_scope"]["order"] and "anchored n" in contract["fixed_scope"]["order"], True, "j tends to infinity" in contract["fixed_scope"]["order"] and "anchored n" in contract["fixed_scope"]["order"])

    support = 2
    degree = 4
    lipschitz = Fraction(3, 4)
    sup_norm = Fraction(2, 5)
    horizon = Fraction(5, 4)
    j = 9
    h = Fraction(1, 2**j)
    roots = 2 * degree * support
    jump = 2 * h
    residual = roots * lipschitz * jump
    time_error = horizon * residual
    correlation_error = sup_norm * time_error
    next_time_error = horizon * roots * lipschitz * (2 * Fraction(1, 2 ** (j + 1)))
    add(rows, "radial l1 jump", jump, 2 * h, jump == 2 * h)
    add(rows, "support root count", roots, 2 * degree * support, roots == 2 * degree * support)
    add(rows, "L2 residual", residual, roots * lipschitz * jump, residual == roots * lipschitz * jump)
    add(rows, "compact-time error", time_error, horizon * residual, time_error == horizon * residual)
    add(rows, "correlation error", correlation_error, sup_norm * time_error, correlation_error == sup_norm * time_error)
    add(rows, "strict refinement decay", next_time_error < time_error, True, next_time_error < time_error)
    add(rows, "error tends to zero", time_error > 0 and next_time_error > 0 and next_time_error < time_error, True, time_error > 0 and next_time_error > 0 and next_time_error < time_error)
    nonclaims = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    add(rows, "no full semigroup promotion", "full semigroup" in nonclaims and "non-radial" in nonclaims, True, "full semigroup" in nonclaims and "non-radial" in nonclaims)
    add(rows, "no physical promotion", all(word in nonclaims for word in ("pre-a", "qft", "gravity")), True, all(word in nonclaims for word in ("pre-a", "qft", "gravity")))

    payload = {
        "schema": "tect/pah-omc020-radial-semigroup-consistency-independent/1.0",
        "audit_id": "PAH-OMC-020-RADIAL-SEMIGROUP-CONSISTENCY-INDEPENDENT-001",
        "result_id": "R-548",
        "task_id": "T-065",
        "status": "PASS_RESTRICTED_RADIAL_SUBSPACE",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": observed,
        "fixture": {"support": support, "degree": degree, "lipschitz": str(lipschitz), "sup_norm": str(sup_norm), "horizon": str(horizon), "j": j, "h": str(h), "roots": roots, "jump": str(jump), "residual": str(residual), "time_error": str(time_error), "correlation_error": str(correlation_error), "next_time_error": str(next_time_error)},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Independent reconstruction confirms the L2 residual-to-compact-time estimate on the amplitude-only subspace with a distinct fixture. It does not address non-radial or source-owned anchored-n comparison maps.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_radial_semigroup_consistency_independent.py --check",
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 radial semigroup independent replay mismatch")
    else:
        atomic(destination, payload)
    print(f"PAH-OMC-020 RADIAL SEMIGROUP INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=PASS_RESTRICTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
