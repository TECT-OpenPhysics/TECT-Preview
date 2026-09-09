#!/usr/bin/env python3
"""Non-importing replay of the PAH-OMC-020 path-word transport lemma.

The implementation deliberately reconstructs the product cancellation and
factorial tail with different names and fixtures.  It does not import the
primary verifier and it keeps the connected-word-to-Duhamel step explicitly
conditional.
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
    "2026-09-07-pah-omc020-pathword/independent.json"
)

PINS = {
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


def record(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def transport_row(densities: list[Fraction], mobilities: list[Fraction]) -> tuple[Fraction, Fraction]:
    if len(densities) != len(mobilities) + 1:
        raise ValueError("invalid word")
    if any(x <= 0 for x in densities) or any(x < 0 or x > 1 for x in mobilities):
        raise ValueError("invalid positivity or mobility")
    squared = Fraction(1)
    for idx, mobility in enumerate(mobilities):
        squared *= mobility * mobility * densities[idx + 1] / densities[idx]
    mobility_square = Fraction(1)
    for mobility in mobilities:
        mobility_square *= mobility * mobility
    return densities[0] * squared, densities[-1] * mobility_square


def tail(a: int, b: int, t: Fraction, d: int) -> Fraction:
    ratio = Fraction(b) * t / (d + 1)
    if not (a > 0 and b > 0 and t >= 0 and d >= 1 and ratio < 1):
        raise ValueError("tail hypotheses")
    first = Fraction(a * b ** (d - 1)) * t ** d / math.factorial(d)
    return first / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    for rel, expected in PINS.items():
        path = ROOT / rel
        record(rows, "pin:" + rel, path.is_file() and digest(path) == expected,
               digest(path) if path.is_file() else "MISSING", expected)
    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    record(rows, "source keeps inverse-pair mobility",
           pah["dynamics"]["mobility_rule"]["symmetry"] == "m_r(x)=m_(r^(-1))(r x)",
           pah["dynamics"]["mobility_rule"]["symmetry"], "inverse-pair mobility")

    # Independent four-state cyclic fixture; all numbers are test inputs.
    weights = [Fraction(7, 20), Fraction(5, 20), Fraction(4, 20), Fraction(4, 20)]
    mobility_word = [Fraction(1, 2), Fraction(3, 5), Fraction(2, 3)]
    total_left = Fraction(0)
    total_right = Fraction(0)
    for start in range(len(weights)):
        densities = [weights[(start + offset) % len(weights)] for offset in range(len(mobility_word) + 1)]
        left, right = transport_row(densities, mobility_word)
        record(rows, f"independent cyclic cancellation {start}", left == right,
               str(left), str(right))
        total_left += left
        total_right += right
    record(rows, "independent stationary mass bound", total_left <= sum(weights),
           str(total_left), f"<= {sum(weights)}")
    record(rows, "independent terminal mass bound", total_right <= sum(weights),
           str(total_right), f"<= {sum(weights)}")

    # Check the factorial ratio with a different contract fixture.
    a, b, t = 4, 6, Fraction(3, 4)
    distances = [10, 14, 18]
    bounds = []
    for distance in distances:
        bound = tail(a, b, t, distance)
        ratio = Fraction(b) * t / (distance + 1)
        for k in range(distance, distance + 4):
            current = Fraction(a * b ** (k - 1)) * t ** k / math.factorial(k)
            following = Fraction(a * b ** k) * t ** (k + 1) / math.factorial(k + 1)
            record(rows, f"independent ratio d={distance},k={k}", following <= ratio * current,
                   str(following / current), f"<= {ratio}")
        bounds.append(bound)
    record(rows, "independent factorial bounds decrease", bounds[0] > bounds[1] > bounds[2],
           [str(value) for value in bounds], "strictly decreasing")

    return {
        "schema": "tect/pah-omc020-pathword-independent/1.0",
        "status": "PASS_INDEPENDENT_PATHWORD",
        "verdict": "AUXILIARY_SUPPORT",
        "claim_bearing": False,
        "conditional": True,
        "source_hashes": PINS,
        "checks": rows,
        "independent_reconstruction": {
            "transport": "stationary density times squared midpoint-rate product telescopes to terminal density times mobility-square product",
            "tail": "connected count a*b^(k-1) times exact simplex t^k/k! has geometric ratio b*t/(k+1)",
            "fixture": {"a": a, "branching": b, "time": str(t), "distances": distances,
                        "bounds": [str(value) for value in bounds]},
        },
        "remaining": [
            "source-certified n-uniform root-overlap branching constant",
            "source-valid coupling or Duhamel attribution from connected words to N2c",
        ],
        "non_claims": [
            "No anchored-n semigroup convergence, common U_n, Mosco liminf or minimal-form selection.",
            "No infinite-volume, continuum, physical Pre-A, spacetime, QFT, gravity, Yang-Mills, mass-gap or TOE conclusion.",
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
            raise SystemExit("PAH-OMC-020 path-word independent replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 PATHWORD INDEPENDENT: PASS ({len(payload['checks'])} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
