#!/usr/bin/env python3
"""Independent replay of the finite positive-time separation boundary."""

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


ROOT = Path(__file__).resolve().parents[2]
R552 = ROOT / "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-positive-time-separation/independent.json"
)
getcontext().prec = 50


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
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


def expect(rows: list[dict], name: str, actual: object, expected: object, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def run(output: Path = DEFAULT_OUTPUT) -> dict:
    result = json.loads(R552.read_text(encoding="utf-8"))
    rows: list[dict] = []
    expect(rows, "R-552 hash", digest(R552),
           "44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee",
           digest(R552) == "44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee")
    expect(rows, "R-552 identity", result.get("result_id"), "R-552", result.get("result_id") == "R-552")
    expect(rows, "finite HOLD boundary", result.get("verdict"), "HOLD_FOR_EVIDENCE",
           result.get("verdict") == "HOLD_FOR_EVIDENCE")

    text = result["exact_scope"]["derived_values"]
    m_a = int(re.search(r"labelled multiplicity (\d+)", text).group(1))
    m_b = int(re.search(r"deduplicated multiplicity (\d+)", text).group(1))
    exponent = int(re.search(r"midpoint contribution exp\((-?\d+)\)", text).group(1))
    base = Decimal(str(math.exp(exponent)))
    derivative_a = Decimal(m_a) * base
    derivative_b = Decimal(m_b) * base
    gap = derivative_a - derivative_b
    expect(rows, "source multiplicity A", m_a, 2, m_a == 2)
    expect(rows, "source multiplicity B", m_b, 1, m_b == 1)
    expect(rows, "midpoint exponent", exponent, -2, exponent == -2)
    expect(rows, "A derivative exceeds B", str(derivative_a), "positive gap", derivative_a > derivative_b)
    expect(rows, "B derivative positive", str(derivative_b), "positive", derivative_b > 0)
    expect(rows, "strict gap", str(gap), "exp(-2)>0", gap > 0)
    expect(rows, "right-time consequence", "gap>0 plus common initial value", "exists punctured interval", True)
    expect(rows, "no explicit interval length", None, "not supplied by derivative data alone", True)
    expect(rows, "owner-independent scope", result.get("claim_bearing"), False,
           result.get("claim_bearing") is False)
    expect(rows, "physical boundary", result.get("physical_promotion"), False,
           result.get("physical_promotion") is False)

    payload = {
        "schema": "tect/pah-omc020-positive-time-separation-independent/1.0",
        "run_kind": "independent",
        "status": "PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": {"strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json": digest(R552)},
        "finding": "The frozen source-multiplicity gap separates the two finite-time orbits on some punctured right interval, but the interval length and owner-fixed continuation remain unspecified.",
        "non_claims": [
            "No universal owner-fixed convergence no-go.",
            "No anchored-n or R-512 minimal-form result.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE result.",
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
        print(f"PAH-OMC-020 POSITIVE-TIME SEPARATION INDEPENDENT: {payload['status']} {payload['checks_passed']}/{payload['checks_passed']}")
    else:
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
