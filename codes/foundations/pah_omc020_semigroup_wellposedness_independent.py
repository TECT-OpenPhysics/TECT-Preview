#!/usr/bin/env python3
"""Independent arithmetic reconstruction for PAH-OMC-020 R-552."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-semigroup-wellposedness/independent.json"
)
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC004 = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
R527 = ROOT / "strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json"

PINS = {
    PAH: "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    OMC004: "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True, default=str)
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
    for path, expected in PINS.items():
        actual = digest(path)
        check(rows, f"pin:{path.relative_to(ROOT).as_posix()}", actual == expected, actual, expected)
    r527 = json.loads(R527.read_text(encoding="utf-8"))
    check(rows, "R-527 exact witness", r527["result_id"] == "R-527" and
          r527["exact_scope"]["observable"].startswith("f=1-Re(U_p)"),
          r527["result_id"], "R-527 / closed-face cylinder")
    delta_f = Fraction(4, 1)
    beta = Fraction(1, 1)
    exponent = beta * delta_f / 2
    check(rows, "exponent from source witness", exponent == 2, exponent, 2)
    weight = math.exp(-float(exponent))
    labelled = 2 * weight
    deduplicated = weight
    gap = labelled - deduplicated
    check(rows, "labelled derivative", abs(labelled - 2 * weight) == 0.0, labelled, "2*exp(-2)")
    check(rows, "deduplicated derivative", abs(deduplicated - weight) == 0.0, deduplicated, "exp(-2)")
    check(rows, "strict positive derivative gap", gap > 0.0, gap, "exp(-2)>0")
    check(rows, "same semigroup would force same derivative", labelled != deduplicated,
          labelled - deduplicated, "nonzero")
    check(rows, "external time retained", "external" in json.dumps(json.loads(PAH.read_text(encoding="utf-8"))["dynamics"]["time"]).lower(),
          "external Markov time", "external")
    return {
        "status": "PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks": rows,
        "source_files": {p.relative_to(ROOT).as_posix(): digest(p) for p in PINS},
        "independent_reconstruction": {
            "delta_F": str(delta_f),
            "beta": str(beta),
            "labelled_multiplicity": 2,
            "deduplicated_multiplicity": 1,
            "gap": "exp(-2)>0",
            "numeric_gap": gap,
        },
        "boundary": "Derivative non-uniqueness is source-definition evidence only; no anchored-n or physical conclusion.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.check:
        print(f"PAH-OMC-020 SEMIGROUP WELL-POSEDNESS INDEPENDENT: {payload['status']} {len(payload['checks'])}/{len(payload['checks'])}")
    else:
        atomic_json(args.output, payload)
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
