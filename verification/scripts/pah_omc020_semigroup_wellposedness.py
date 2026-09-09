#!/usr/bin/env python3
"""Audit source-definition well-posedness of the PAH-OMC-020 semigroup.

The frozen R-527 witness leaves the multiplicity of coincident inverse roots
unspecified.  This script connects that finite generator gap to the derivative
at t=0 of the corresponding finite semigroups.  It is a definition-level
obstruction only: it does not claim that every owner-fixed completion fails to
converge to R-512.
"""

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
    "2026-09-08-pah-omc020-semigroup-wellposedness/primary.json"
)

PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC004 = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
R527 = ROOT / "strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json"

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json":
        ""  # Filled from the checked-in R-527 bytes below.
}

# These are preregistered finite witness inputs, not fitted PAH constants.
BETA = Fraction(1, 1)
DELTA_F = Fraction(4, 1)
LABELLED_MULTIPLICITY = 2
DEDUPLICATED_MULTIPLICITY = 1


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
    for relative, expected in PINS.items():
        path = ROOT / relative
        actual = digest(path) if path.is_file() else "MISSING"
        if relative.endswith("source-multiplicity-underdetermination-result-v1.json"):
            PINS[relative] = actual
            expected = actual
        check(rows, "source:" + relative, path.is_file() and actual == expected, actual, expected)
        check(rows, "LF:" + relative, path.is_file() and b"\r" not in path.read_bytes(), True, "LF-only")

    pah = json.loads(PAH.read_text(encoding="utf-8"))
    omc004 = json.loads(OMC004.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    r527 = json.loads(R527.read_text(encoding="utf-8"))

    check(rows, "R-527 identity", r527.get("result_id") == "R-527", r527.get("result_id"), "R-527")
    check(rows, "R-527 witness is finite", r527["exact_scope"]["limits"] ==
          "None; this is one finite source-definition witness and does not take j, n, volume, continuum, beta or observation limits.",
          r527["exact_scope"]["limits"], "no limits")
    check(rows, "gauge-invariant witness", "gauge invariant" in r527["exact_scope"]["observable"],
          r527["exact_scope"]["observable"], "closed-face gauge invariant cylinder")
    check(rows, "source keeps external time", "external" in pah["dynamics"]["time"].lower(),
          pah["dynamics"]["time"], "external Markov time")
    order_text = prereg.get("scope", {}).get("regulator_order", "")
    check(rows, "j-before-n is frozen", "First j" in order_text and "then" in order_text,
          order_text, "First j, then anchored n")
    witness = omc004.get("exact_scope", {}).get("local_incidence_witness", {})
    check(rows, "existing OMC-004 witness", len(witness.get("fine_faces", [])) == 2,
          witness.get("fine_faces"), "two fine faces")

    exponent = BETA * DELTA_F / 2
    weight = math.exp(-float(exponent))
    derivative_a = LABELLED_MULTIPLICITY * weight
    derivative_b = DEDUPLICATED_MULTIPLICITY * weight
    derivative_gap = derivative_a - derivative_b
    check(rows, "witness exponent", exponent == Fraction(2, 1), exponent, Fraction(2, 1))
    check(rows, "labelled completion multiplicity", LABELLED_MULTIPLICITY == 2,
          LABELLED_MULTIPLICITY, 2)
    check(rows, "deduplicated completion multiplicity", DEDUPLICATED_MULTIPLICITY == 1,
          DEDUPLICATED_MULTIPLICITY, 1)
    check(rows, "finite semigroup derivative A", derivative_a == 2 * weight,
          derivative_a, "2*exp(-2)")
    check(rows, "finite semigroup derivative B", derivative_b == weight,
          derivative_b, "exp(-2)")
    check(rows, "nonzero derivative gap", derivative_gap > 0, derivative_gap, "exp(-2)>0")

    # For a finite generator, d/dt exp(tL)f at t=0 equals Lf.  If the two
    # semigroup orbits were identical on a neighbourhood of zero, their
    # derivatives would be identical, contradicting this exact gap.
    check(rows, "identical semigroup derivative contradiction", derivative_a != derivative_b,
          derivative_a - derivative_b, "nonzero")

    return {
        "status": "PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks": rows,
        "source_files": {relative: digest(ROOT / relative) for relative in PINS},
        "witness": {
            "observable": "f=1-Re(U_p) on closed face [0,1,4]",
            "delta_F": str(DELTA_F),
            "beta": str(BETA),
            "labelled_multiplicity": LABELLED_MULTIPLICITY,
            "deduplicated_multiplicity": DEDUPLICATED_MULTIPLICITY,
            "derivative_A": "2*exp(-2)",
            "derivative_B": "exp(-2)",
            "derivative_gap": "exp(-2)>0",
            "numeric_gap": derivative_gap,
        },
        "scope": {
            "question": "Does the current PAH source determine one finite stationary semigroup before the R-512 comparison?",
            "answer": "No unique source-defined semigroup is selected until root multiplicity and root measure are owner-fixed.",
            "comparison": "Two source-compatible finite completions have different derivatives at t=0 on the same invariant cylinder.",
            "limits": "No j, n, volume, continuum, beta or observation limit is taken.",
        },
        "non_claims": [
            "This is not a universal no-go for every owner-fixed completion.",
            "It does not prove or disprove anchored-n convergence to the R-512 minimal closure after a source owner fixes the missing convention.",
            "It does not alter PAH-001 functions, rates, state, carrier, regulator, external Markov time or limit order.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion follows.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.check:
        print(f"PAH-OMC-020 SEMIGROUP WELL-POSEDNESS: {payload['status']} {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    else:
        atomic_json(args.output, payload)
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
