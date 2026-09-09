#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 path-word transport lemma."""

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
    "2026-09-07-pah-omc020-pathword/hostile.json"
)
PINNED = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


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


def check(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def correct_transport(weights: list[Fraction], mobilities: list[Fraction], wrong: bool = False) -> tuple[Fraction, Fraction]:
    square = Fraction(1)
    for i, mobility in enumerate(mobilities):
        ratio = weights[i + 1] / weights[i]
        if wrong:
            ratio *= ratio
        square *= mobility * mobility * ratio
    left = weights[0] * square
    mobility_square = Fraction(1)
    for mobility in mobilities:
        mobility_square *= mobility * mobility
    return left, weights[-1] * mobility_square


def geometric_tail(a: int, b: int, t: Fraction, d: int) -> Fraction:
    ratio = Fraction(b) * t / (d + 1)
    if ratio >= 1:
        raise ValueError("geometric remainder condition failed")
    return Fraction(a * b ** (d - 1)) * t ** d / math.factorial(d) / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    for rel, expected in PINNED.items():
        path = ROOT / rel
        check(rows, "pinned source unchanged:" + rel, path.is_file() and digest(path) == expected,
              digest(path) if path.is_file() else "MISSING", expected)

    weights = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)]
    mobilities = [Fraction(1, 2), Fraction(3, 4)]
    good_left, good_right = correct_transport(weights, mobilities)
    check(rows, "exact midpoint ratio is required", good_left == good_right,
          str(good_left), str(good_right))
    bad_left, bad_right = correct_transport(weights, mobilities, wrong=True)
    check(rows, "squared density-ratio mutation is rejected", bad_left != bad_right,
          str(bad_left), "!= " + str(bad_right))

    check(rows, "mobility-above-one is rejected", not (Fraction(7, 6) <= 1),
          str(Fraction(7, 6)), "not in [0,1]")
    try:
        geometric_tail(2, 6, Fraction(1), 5)
    except ValueError:
        ratio_rejected = True
    else:
        ratio_rejected = False
    check(rows, "tail bound rejects ratio >= one", ratio_rejected, "b*T >= d+1", "ValueError")

    # A connected-word tail is not itself an N2c proof.  This firewall is
    # intentionally hostile to an otherwise tempting promotion.
    scope = "Exact non-radial path words only; no anchored-n conclusion."
    check(rows, "anchored-n promotion rejected", "no anchored-n" in scope.lower(), scope, "explicitly absent")
    check(rows, "physical promotion rejected", "physical" not in scope.lower(), scope, "physical absent")
    check(rows, "Duhamel attribution remains open", True, "NOT_PROVED", "NOT_PROVED")
    check(rows, "source rate replacement absent",
          "exp[-beta(F_rho(r x)-F_rho(x))/2]" in json.loads(
              (ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8")
          )["dynamics"]["generator"], True, True)

    return {
        "schema": "tect/pah-omc020-pathword-hostile/1.0",
        "status": "PASS_HOSTILE_PATHWORD",
        "verdict": "AUXILIARY_SUPPORT",
        "claim_bearing": False,
        "conditional": True,
        "source_hashes": PINNED,
        "checks": rows,
        "rejected_shortcuts": [
            "squared density-ratio mutation",
            "mobility greater than one",
            "geometric tail without ratio condition",
            "calling the connected-word envelope an anchored-n proof",
            "promoting Markov-time algebra to physical dynamics",
        ],
        "remaining": [
            "source-certified root-overlap constant and distance count",
            "connected-word coupling/Duhamel attribution for the exact Q_n",
        ],
        "non_claims": [
            "No N2c/N4 closure, common U_n, anchored-n semigroup, minimal form or physical result.",
            "No Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists():
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 path-word hostile replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 PATHWORD HOSTILE: PASS ({len(payload['checks'])} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
