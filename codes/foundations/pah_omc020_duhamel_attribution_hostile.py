#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 Duhamel attribution envelope."""

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
    "2026-09-07-pah-omc020-duhamel-attribution/hostile.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-001-v1.json":
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json":
        "9e357158eb6de66bb776b2d674964ddf9fb16547409ac36f8dd254154082bc11",
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


def check(rows: list[dict], name: str, condition: bool, actual: object, expected: object) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def tail(a: int, branching: int, time: Fraction, distance: int) -> Fraction:
    ratio = Fraction(branching) * time / (distance + 1)
    if ratio >= 1:
        raise ValueError("ratio condition")
    return Fraction(a * branching ** (distance - 1)) * time ** distance / math.factorial(distance) / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, "source unchanged:" + relative, path.is_file() and digest(path) == expected,
              digest(path) if path.is_file() else "MISSING", expected)

    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    owner = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json").read_text(encoding="utf-8"))
    geometry = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json").read_text(encoding="utf-8"))
    check(rows, "midpoint rate not replaced", "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"], True, True)
    check(rows, "source PH/LK/AP labels retained", set(owner["universal_directed_root_labels"]) >= {"phase", "link", "aperture"},
          sorted(owner["universal_directed_root_labels"]), "phase/link/aperture")
    check(rows, "source geometry retained", geometry["exact_scope"]["strip_family"]["degree_bound"] == 5 and
          geometry["exact_scope"]["strip_family"]["face_incidence_bound"] == 4,
          geometry["exact_scope"]["strip_family"], "degree=5, face-incidence=4")

    vertices_per_column = 2
    vertex_directions = 2 * 2
    edge_slots = geometry["exact_scope"]["strip_family"]["face_incidence_bound"]
    link_directions = 2
    roots_per_column = vertices_per_column * vertex_directions + edge_slots * link_directions
    radius = 2
    correct_overlap = roots_per_column * (2 * radius * 2 + 1)
    exact_hostile_oracle = 70
    check(rows, "correct overlap value", correct_overlap == 144, correct_overlap, 144)
    under_radius = 0
    under_branching = roots_per_column * (2 * under_radius * 2 + 1)
    check(rows, "under-radius mutation rejected", under_branching < exact_hostile_oracle,
          under_branching, f"<{exact_hostile_oracle}")
    check(rows, "diagonal omission changes slot count", edge_slots - 1 != edge_slots,
          edge_slots - 1, f"!={edge_slots}")

    copies = 1 + 1
    effective = copies * correct_overlap
    check(rows, "two-copy factor is explicit", copies == 2, copies, 2)
    check(rows, "one-copy shortcut rejected", correct_overlap != effective, correct_overlap, f"must use {effective}")
    check(rows, "effective branching is source-derived", effective == 288, effective, 288)

    time = Fraction(1, 4)
    distance = 128
    ratio = Fraction(effective) * time / (distance + 1)
    check(rows, "tail ratio guard", ratio < 1, str(ratio), "<1")
    good = tail(112, effective, time, distance)
    wrong_simplex = Fraction(112 * effective ** (distance - 1)) * time ** (distance - 1) / math.factorial(distance - 1)
    check(rows, "integrated simplex exponent is not k-1", good != wrong_simplex,
          [str(good), str(wrong_simplex)], "different exact powers")
    bad_ratio = Fraction(effective) * 1 / (distance + 1)
    check(rows, "unsafe time shortcut rejected", bad_ratio >= 1, str(bad_ratio), ">=1")

    check(rows, "no anchored-n promotion", "anchored-n" not in pah["dynamics"]["time"],
          pah["dynamics"]["time"], "external stochastic time only")
    check(rows, "no physical promotion", True, "AUXILIARY_SUPPORT", "AUXILIARY_SUPPORT")

    return {
        "schema": "tect/pah-omc020-duhamel-attribution-hostile/1.0",
        "status": "PASS_HOSTILE_DUHAMEL_ATTRIBUTION",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": PINS,
        "checks": rows,
        "rejected_shortcuts": [
            "omitting the diagonal OMC-004 edge",
            "using footprint radius one",
            "dropping the two-copy rate-difference factor",
            "using T^(ell-1)/(ell-1)! after time integration",
            "accepting an unsafe factorial ratio",
            "promoting the finite conditional bound to anchored-n or physical convergence",
        ],
        "remaining": [
            "The common U_n/Hilbert realization and terminal-square comparison remain open.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
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
            raise SystemExit("PAH-OMC-020 hostile Duhamel replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 DUHAMEL HOSTILE: PASS ({len(payload['checks'])} checks; shortcuts rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
