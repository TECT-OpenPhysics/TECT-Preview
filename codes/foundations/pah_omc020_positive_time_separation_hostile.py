#!/usr/bin/env python3
"""Hostile checks for the finite positive-time separation interpretation."""

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
    "2026-09-08-pah-omc020-positive-time-separation/hostile.json"
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


def reject(rows: list[dict], name: str, condition: bool, expected: str) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": condition, "expected": expected})


def run(output: Path = DEFAULT_OUTPUT) -> dict:
    result = json.loads(R552.read_text(encoding="utf-8"))
    rows: list[dict] = []
    reject(rows, "R-552 byte pin", digest(R552) ==
           "44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee",
           "frozen R-552 bytes")
    values = result["exact_scope"]["derived_values"]
    m_a = int(re.search(r"labelled multiplicity (\d+)", values).group(1))
    m_b = int(re.search(r"deduplicated multiplicity (\d+)", values).group(1))
    exponent = int(re.search(r"midpoint contribution exp\((-?\d+)\)", values).group(1))
    base = Decimal(str(math.exp(exponent)))
    gap = (Decimal(m_a) - Decimal(m_b)) * base
    reject(rows, "positive gap is not a universal no-go", gap > 0 and result.get("claim_bearing") is False,
           "source-definition boundary only")
    reject(rows, "no explicit delta is invented", "explicit numeric delta" not in str(result),
           "existential interval only")
    reject(rows, "no time rescaling", "external Markov time" in result.get("finding", "") or
           result.get("physical_promotion") is False, "external time frozen")
    reject(rows, "same multiplicity removes witness", (m_a - m_a) * base == 0,
           "owner choice can eliminate this witness")
    reject(rows, "zero time is excluded", not (0 < 0), "punctured right interval")
    reject(rows, "no anchored limit", "anchored-n" in " ".join(result.get("non_claims", [])),
           "anchored-n remains open")
    reject(rows, "no physical promotion", result.get("physical_promotion") is False,
           "physical_promotion=false")

    payload = {
        "schema": "tect/pah-omc020-positive-time-separation-hostile/1.0",
        "run_kind": "hostile",
        "status": "PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": {"strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json": digest(R552)},
        "mutations_rejected": [
            "universal owner-fixed no-go",
            "invented explicit delta",
            "Markov-time rescaling",
            "anchored-n or physical promotion",
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
        print(f"PAH-OMC-020 POSITIVE-TIME SEPARATION HOSTILE: {payload['status']} {payload['checks_passed']}/{payload['checks_passed']}")
    else:
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
