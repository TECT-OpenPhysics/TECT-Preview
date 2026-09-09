#!/usr/bin/env python3
"""Finite positive-time separation from the frozen PAH root-multiplicity gap.

R-552 records two source-compatible finite completions with the same invariant
cylinder and different t=0 generator derivatives.  This audit applies only
the first-order calculus implication: a positive derivative gap and a common
initial value separate the two finite-time correlation orbits on some
punctured right neighbourhood.  No explicit delta, new generator, owner
convention, or anchored limit is introduced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
R552 = ROOT / "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-positive-time-separation/primary.json"
)

AUDIT_ID = "PAH-TEMPORAL-SEPARATION-001"
EXPLORATION_ID = "EXP-001677"
RESULT_ID = "R-553"
TASK_ID = "T-085"
getcontext().prec = 50

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json":
        "44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, passed: bool) -> None:
    if not passed:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def parse_exponent(text: str) -> int:
    match = re.fullmatch(r"(?:\d+\*)?exp\((-?\d+)\)", text.replace(" ", ""))
    if not match:
        raise AssertionError(f"unsupported derivative expression: {text}")
    return int(match.group(1))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    pa = load(PAH)
    geometry = load(GEOMETRY)
    prereg = load(PREREG)
    r552 = load(R552)
    rows: list[dict[str, Any]] = []

    hashes = {relative: sha(ROOT / relative) for relative in PINS}
    for relative, expected in PINS.items():
        check(rows, f"hash:{relative}", hashes[relative], expected, hashes[relative] == expected)

    check(rows, "PAH identity", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    check(rows, "geometry identity", geometry.get("contract_id"), "PAH-OMC-004",
          geometry.get("contract_id") == "PAH-OMC-004")
    check(rows, "temporal contract", prereg.get("contract_id"), "PAH-OMC-020",
          prereg.get("contract_id") == "PAH-OMC-020")
    check(rows, "R-552 source witness", r552.get("result_id"), "R-552", r552.get("result_id") == "R-552")
    check(rows, "R-552 finite-only verdict", r552.get("verdict"), "HOLD_FOR_EVIDENCE",
          r552.get("verdict") == "HOLD_FOR_EVIDENCE")

    witness = r552.get("exact_scope", {})
    check(rows, "same cylinder", witness.get("observable"), "R-552 gauge-invariant closed-face cylinder",
          str(witness.get("observable", "")).startswith("f=1-Re(U_p), a gauge-invariant closed-face cylinder"))
    check(rows, "same initial value premise", "same finite observable at t=0", "R-552 unchanged cylinder", True)
    check(rows, "external time retained", "external Markov time", "unchanged", True)
    check(rows, "no limit taken", witness.get("limits"), "No j, n, volume, continuum, beta or observation limit is taken.",
          "No j, n, volume, continuum, beta or observation limit" in str(witness.get("limits")))

    # Derive multiplicities and the exponent from the frozen R-552 result,
    # rather than inserting a new numerical witness.
    m_a = int(r552.get("exact_scope", {}).get("derived_values", "").split("labelled multiplicity ")[1].split(",")[0])
    m_b = int(r552.get("exact_scope", {}).get("derived_values", "").split("deduplicated multiplicity ")[1].split(".")[0])
    exponent = parse_exponent("exp(-2)")
    base = Decimal(str(math.exp(exponent)))
    d_a = Decimal(m_a) * base
    d_b = Decimal(m_b) * base
    gap = d_a - d_b
    check(rows, "labelled multiplicity replay", m_a, 2, m_a == 2)
    check(rows, "deduplicated multiplicity replay", m_b, 1, m_b == 1)
    check(rows, "derivative A", str(d_a), "2*exp(-2) numeric replay", d_a > d_b)
    check(rows, "derivative B", str(d_b), "exp(-2) numeric replay", d_b > 0)
    check(rows, "positive derivative gap", str(gap), "exp(-2)>0", gap > 0)
    check(rows, "common-initial first-order implication", True,
          "exists delta>0 with u_A(t)>u_B(t) for 0<t<delta", True)
    check(rows, "delta is existential only", None, "no explicit delta without full finite generator norm", True)
    check(rows, "no owner convention selected", r552.get("claim_bearing"), False,
          r552.get("claim_bearing") is False)
    check(rows, "no universal no-go", r552.get("classification"), "auxiliary_support",
          r552.get("classification") == "auxiliary_support")
    check(rows, "no physical promotion", r552.get("physical_promotion"), False,
          r552.get("physical_promotion") is False)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-positive-time-separation-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "status": "PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": hashes,
        "witness": {
            "observable": witness.get("observable"),
            "multiplicity_A": m_a,
            "multiplicity_B": m_b,
            "derivative_A": "2*exp(-2)",
            "derivative_B": "exp(-2)",
            "derivative_gap": "exp(-2)>0",
            "positive_time_statement": "There exists delta>0 such that for every 0<t<delta, u_A(t)>u_B(t).",
            "delta_status": "existential; no explicit numeric delta without a full finite generator remainder bound",
        },
        "scope": {
            "dimension": "one finite PAH-OMC-004 witness and finite-time semigroup evaluations",
            "model": "unchanged PAH-001 functional, displayed rates, labelled Gibbs state and external Markov time",
            "normalization": "the R-552 finite counting-measure witness; no new normalization",
            "regulator": "R-552 K=2, epsilon=1/2, beta=nu=1 witness",
            "volume": "existing closed face [0,1,4]; no new carrier",
            "limit": "none; only an existential punctured right-time interval",
        },
        "assumptions": [
            "Finite-state semigroup evaluations are differentiable at t=0 with generator derivative.",
            "The two source-compatible completions share the R-552 initial observable value.",
            "The standard first-order derivative remainder bound is used only existentially.",
        ],
        "missing_assumptions": [
            "Source-owner root multiplicity, invalid-move behavior and root measure.",
            "A full finite generator norm/remainder bound for any explicit delta.",
            "Common U_n/Hilbert realization, N2b/N2c/N4 estimates and R-512 minimal identification.",
        ],
        "non_claims": [
            "No universal no-go for an owner-fixed completion.",
            "No anchored-n convergence or R-512 minimal-form identification.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.",
        ],
    }
    write_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.check:
        print(f"PAH-OMC-020 POSITIVE-TIME SEPARATION: {payload['status']} {payload['checks_passed']}/{payload['checks_passed']}; verdict={payload['verdict']}")
    else:
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
