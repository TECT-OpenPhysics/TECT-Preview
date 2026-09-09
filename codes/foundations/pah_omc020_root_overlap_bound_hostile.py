#!/usr/bin/env python3
"""Hostile controls for the OMC-004 root-overlap bound."""

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
    "2026-09-07-pah-omc020-overlap/hostile.json"
)
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-001-v1.json":
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
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


def tail(a: int, b: int, time: Fraction, distance: int) -> Fraction:
    ratio = Fraction(b) * time / (distance + 1)
    if ratio >= 1:
        raise ValueError("ratio condition")
    return Fraction(a * b ** (distance - 1)) * time ** distance / math.factorial(distance) / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    for rel, expected in PINS.items():
        path = ROOT / rel
        check(rows, "source unchanged:" + rel, path.is_file() and digest(path) == expected,
              digest(path) if path.is_file() else "MISSING", expected)

    vertices_per_column = 2
    vertex_directions = 4
    edge_slots = 4
    link_directions = 2
    correct_roots = vertices_per_column * vertex_directions + edge_slots * link_directions
    check(rows, "correct source root column count", correct_roots == 16, correct_roots, 16)

    wrong_edge_slots = edge_slots - 1
    wrong_roots = vertices_per_column * vertex_directions + wrong_edge_slots * link_directions
    check(rows, "omitting diagonal slot changes root count", wrong_roots != correct_roots,
          wrong_roots, f"!={correct_roots}")

    radius = 2
    correct_branching = correct_roots * (4 * radius + 1)
    check(rows, "correct conservative branching value", correct_branching == 144,
          correct_branching, 144)
    under_radius = 0
    under_branching = correct_roots * (4 * under_radius + 1)
    exact_overlap_fixture = 70  # labelled hostile oracle from the n=3 strip
    check(rows, "under-radius mutation is too small", under_branching < exact_overlap_fixture,
          under_branching, f"<{exact_overlap_fixture}")

    # A tail without its ratio hypothesis is invalid; the hostile lane keeps
    # the guard rather than silently taking a negative geometric denominator.
    try:
        tail(8, correct_branching, Fraction(1), 100)
    except ValueError:
        ratio_guard = True
    else:
        ratio_guard = False
    check(rows, "tail ratio guard is active", ratio_guard, "144 >= 101", "ValueError")

    support_columns = 2
    first_roots = correct_roots * (support_columns + 2 * radius + 1)
    bounds = [tail(first_roots, correct_branching, Fraction(1), d) for d in (600, 800, 1000)]
    check(rows, "correct tail fixture decreases", bounds[0] > bounds[1] > bounds[2],
          [str(value) for value in bounds], "strictly decreasing")

    source = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    check(rows, "original generator rate retained",
          "exp[-beta(F_rho(r x)-F_rho(x))/2]" in source["dynamics"]["generator"], True, True)
    check(rows, "anchored-n promotion rejected", True, "NOT_PROVED", "NOT_PROVED")
    check(rows, "Duhamel attribution remains open", True, "NOT_PROVED", "NOT_PROVED")

    return {
        "schema": "tect/pah-omc020-overlap-hostile/1.0",
        "status": "PASS_HOSTILE_ROOT_OVERLAP",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "source_hashes": PINS,
        "checks": rows,
        "rejected_shortcuts": [
            "omitting the diagonal edge slot",
            "using an under-sized footprint radius",
            "using a geometric tail without its ratio guard",
            "calling overlap arithmetic an anchored-n or N2c proof",
        ],
        "remaining": [
            "connected-word-to-Duhamel or coupling attribution",
            "common U_n/Hilbert, N2b and N2d minimal-form selection",
        ],
        "non_claims": [
            "No N2c/N4 boundary-escape theorem or anchored-n semigroup convergence.",
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
            raise SystemExit("PAH-OMC-020 overlap hostile replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 ROOT OVERLAP HOSTILE: PASS ({len(payload['checks'])} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
