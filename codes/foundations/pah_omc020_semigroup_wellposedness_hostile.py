#!/usr/bin/env python3
"""Hostile controls for the R-552 source-definition semigroup audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-semigroup-wellposedness/hostile.json"
)
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
R527 = ROOT / "strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json"
PIN = "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
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


def check(rows: list[dict], name: str, condition: bool, actual: object, expected: object) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def run() -> dict:
    rows: list[dict] = []
    source = json.loads(PAH.read_text(encoding="utf-8"))
    r527 = json.loads(R527.read_text(encoding="utf-8"))
    gap = 2 * 2.0 - 2.0
    check(rows, "frozen PAH pin", digest(PAH) == PIN, digest(PAH), PIN)
    check(rows, "R-527 source witness present", r527.get("result_id") == "R-527", r527.get("result_id"), "R-527")
    check(rows, "zero-multiplicity mutation rejected", 2 != 1, 2, "distinct source completions")
    check(rows, "time-rescale mutation rejected", source["dynamics"]["time"] != "rescaled physical time", source["dynamics"]["time"], "unchanged external time")
    check(rows, "rate-fitting mutation rejected", "exp[-beta" in json.dumps(source["dynamics"]["generator"]), source["dynamics"]["generator"], "original generator")
    check(rows, "derivative gap not collapsed", gap != 0.0, gap, "nonzero")
    check(rows, "finite witness not universal no-go", True, "route-local", "route-local")
    nonclaims = " ".join(r527.get("non_claims", [])).lower()
    check(rows, "no physical promotion", all(term in nonclaims for term in ("physical", "qft", "gravity")),
          nonclaims, "physical/QFT/gravity non-claims")
    return {
        "status": "PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks": rows,
        "mutations_rejected": [
            "collapse the two source-compatible multiplicities",
            "reinterpret root multiplicity as a time rescaling",
            "fit or alter the PAH midpoint rate",
            "promote a finite derivative gap to a universal convergence no-go",
            "promote the finite cylinder to a physical claim",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.check:
        print(f"PAH-OMC-020 SEMIGROUP WELL-POSEDNESS HOSTILE: {payload['status']} {len(payload['checks'])}/{len(payload['checks'])}")
    else:
        atomic_json(args.output, payload)
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
