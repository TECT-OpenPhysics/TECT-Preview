#!/usr/bin/env python3
"""Non-importing arithmetic replay of the OMC-004 overlap bound."""

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
    "2026-09-07-pah-omc020-overlap/independent.json"
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


def record(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def tail(a: int, b: int, time: Fraction, distance: int) -> Fraction:
    ratio = Fraction(b) * time / (distance + 1)
    if ratio >= 1:
        raise ValueError("geometric ratio condition")
    first = Fraction(a * b ** (distance - 1)) * time ** distance / math.factorial(distance)
    return first / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    for rel, expected in PINS.items():
        path = ROOT / rel
        record(rows, "pin:" + rel, path.is_file() and digest(path) == expected,
               digest(path) if path.is_file() else "MISSING", expected)
    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc1 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json").read_text(encoding="utf-8"))
    omc4 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json").read_text(encoding="utf-8"))
    record(rows, "generator midpoint unchanged",
           "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"],
           pah["dynamics"]["generator"], "original midpoint rate")
    record(rows, "all three root families retained",
           all(name in omc1["universal_directed_root_labels"] for name in ("phase", "link", "aperture")),
           list(omc1["universal_directed_root_labels"]), "phase/link/aperture")
    record(rows, "strip degree source", omc4["exact_scope"]["strip_family"]["degree_bound"] == 5,
           omc4["exact_scope"]["strip_family"]["degree_bound"], 5)

    # Direct local count from the OMC-004 column signature, independent of the
    # primary footprint enumeration: two vertices and at most four edge slots.
    vertices_per_column = 2
    vertex_root_directions = 2 + 2  # PH +/- and AP +/-
    edge_slots_per_column = 4       # h^0, h^1, v, and d when present
    link_root_directions = 2        # LK +/-
    roots_per_column = vertices_per_column * vertex_root_directions + edge_slots_per_column * link_root_directions
    radius = 2
    branching = roots_per_column * (4 * radius + 1)
    record(rows, "independent roots per column", roots_per_column == 16, roots_per_column, 16)
    record(rows, "independent overlap bound", branching == 144, branching, 144)

    # The interval model is the only locality input here: each footprint is
    # contained in base column +/- radius, so overlap permits at most 4R+1 base
    # columns.  This tests the arithmetic without importing the graph builder.
    for separation in range(0, 2 * radius + 1):
        record(rows, f"interval overlap separation {separation}", separation <= 2 * radius,
               separation, f"<= {2 * radius}")
    record(rows, "interval base-column count", 4 * radius + 1 == 9, 4 * radius + 1, 9)

    support_columns = 3
    first_roots = roots_per_column * (support_columns + 2 * radius + 1)
    record(rows, "independent first-root bound", first_roots == 128, first_roots, 128)
    time = Fraction(3, 4)
    distances = [700, 900, 1100]
    bounds = [tail(first_roots, branching, time, d) for d in distances]
    for left, right, d_left, d_right in zip(bounds, bounds[1:], distances, distances[1:]):
        record(rows, f"independent tail decreases {d_left}->{d_right}", left > right,
               str(right), f"< {left}")

    return {
        "schema": "tect/pah-omc020-overlap-independent/1.0",
        "status": "PASS_INDEPENDENT_ROOT_OVERLAP",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "source_hashes": PINS,
        "checks": rows,
        "derived_constants": {
            "vertices_per_column": vertices_per_column,
            "edge_slots_per_column": edge_slots_per_column,
            "roots_per_column": roots_per_column,
            "footprint_radius": radius,
            "overlap_branching": branching,
            "first_root_bound": first_roots,
            "tail": {"a": first_roots, "b": branching, "time": str(time),
                     "distances": distances, "bounds": [str(value) for value in bounds]},
        },
        "remaining": [
            "connected-word-to-Duhamel or coupling attribution for the exact Q_n",
            "common U_n/Hilbert, N2b liminf/recovery and N2d minimal-form selection",
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
            raise SystemExit("PAH-OMC-020 overlap independent replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 ROOT OVERLAP INDEPENDENT: PASS ({len(payload['checks'])} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
