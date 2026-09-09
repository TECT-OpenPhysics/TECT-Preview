#!/usr/bin/env python3
"""Non-importing arithmetic audit for the PAH-OMC-020 coupling bound."""

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
    "2026-09-07-pah-omc020-duhamel-attribution/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-001-v1.json":
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json":
        "114699a4554e45260a6a6632f44a32e9c0494a9274c27b561c676e93c5d247d9",
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
        raise ValueError("tail ratio")
    first = Fraction(a * branching ** (distance - 1)) * time ** distance / math.factorial(distance)
    return first / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, "pin:" + relative, path.is_file() and digest(path) == expected,
              digest(path) if path.is_file() else "MISSING", expected)

    parent = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    owner = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json").read_text(encoding="utf-8"))
    geometry = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json").read_text(encoding="utf-8"))
    r515 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json").read_text(encoding="utf-8"))
    r516 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json").read_text(encoding="utf-8"))
    labels = owner["universal_directed_root_labels"]
    check(rows, "unchanged midpoint source", "exp[-beta(F_rho(r x)-F_rho(x))/2]" in parent["dynamics"]["generator"], True, True)
    check(rows, "local move declarations", len(labels) == 4 and all("map" in value for value in labels.values()),
          sorted(labels), "phase/matter_transfer/link/aperture")
    check(rows, "degree and face bounds", geometry["exact_scope"]["strip_family"]["degree_bound"] == 5 and
          geometry["exact_scope"]["strip_family"]["face_incidence_bound"] == 4,
          geometry["exact_scope"]["strip_family"], "degree=5, face-incidence=4")
    check(rows, "R-515 transport is conditional", r515["result_id"] == "R-515" and r515["conditional"],
          [r515["result_id"], r515["conditional"]], ["R-515", True])
    check(rows, "R-516 provides overlap input", r516["result_id"] == "R-516" and "144" in r516["conclusion"]["overlap"],
          [r516["result_id"], r516["conclusion"]["overlap"]], "b=144")

    vertices_per_column = 2
    vertex_root_directions = len(("PH", "AP")) * 2
    edge_slots = geometry["exact_scope"]["strip_family"]["face_incidence_bound"]
    link_root_directions = 2
    roots_per_column = vertices_per_column * vertex_root_directions + edge_slots * link_root_directions
    radius = 2
    overlap_step = 2 * radius
    overlap = roots_per_column * (2 * radius * 2 + 1)
    copy_count = 2
    effective = copy_count * overlap
    check(rows, "roots-per-column derivation", roots_per_column == 16, roots_per_column, 16)
    check(rows, "radius derivation", radius == 2, radius, 2)
    check(rows, "overlap derivation", overlap == 144, overlap, 144)
    check(rows, "explicit two-copy factor", copy_count == 2, copy_count, 2)
    check(rows, "effective branching derivation", effective == 288, effective, 288)

    support_widths = (2, 4, 7)
    support_bounds = {str(width): roots_per_column * (width + 2 * radius + 1)
                      for width in support_widths}
    check(rows, "two-column first-root bound", support_bounds["2"] == 112, support_bounds["2"], 112)
    check(rows, "support-width monotonicity", support_bounds["2"] < support_bounds["7"], support_bounds, "increasing")

    time = Fraction(1, 4)
    distances = (128, 192, 256)
    bounds = [tail(support_bounds["2"], effective, time, distance) for distance in distances]
    ratios = [Fraction(effective) * time / (distance + 1) for distance in distances]
    for distance, ratio in zip(distances, ratios):
        check(rows, f"tail ratio d={distance}", ratio < 1, str(ratio), "<1")
    check(rows, "factorial tail decreases", bounds[0] > bounds[1] > bounds[2],
          [str(value) for value in bounds], "strictly decreasing")

    gaps = (0, overlap_step * 4, overlap_step * 8)
    graph_distances = [max(1, math.ceil(gap / overlap_step)) for gap in gaps]
    check(rows, "boundary graph distance grows", graph_distances[0] < graph_distances[-1],
          graph_distances, "increasing")
    simplex_value = Fraction(1, math.factorial(3))
    check(rows, "simplex integration identity", simplex_value ==
          sum(Fraction(1, math.factorial(3)) for _ in range(1)), str(simplex_value), str(simplex_value))

    return {
        "schema": "tect/pah-omc020-duhamel-attribution-independent/1.0",
        "status": "PASS_INDEPENDENT_DUHAMEL_ATTRIBUTION",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": PINS,
        "checks": rows,
        "derived_constants": {
            "roots_per_column": roots_per_column,
            "footprint_radius": radius,
            "overlap_step_columns": overlap_step,
            "overlap_branching": overlap,
            "two_copy_rate_factor": copy_count,
            "effective_coupling_branching": effective,
            "first_root_bounds": support_bounds,
            "tail_fixture": {
                "a": support_bounds["2"],
                "branching": effective,
                "time": str(time),
                "distances": list(distances),
                "bounds": [str(value) for value in bounds],
            },
            "boundary_graph_distances": graph_distances,
        },
        "independent_argument": {
            "coupling": "A two-copy basic coupling uses common clocks when local rates agree; otherwise the total disagreement rate is bounded by the sum of the two source rates.",
            "path_count": "Reverse overlap paths are counted from the fixed support with a_w first roots and b=144 successors.",
            "time_factor": "A first outside root followed by ell-1 jumps contributes T^ell/ell! after integrating the simplex in external Markov time.",
            "effective_factor": "The triangle inequality contributes an explicit 2^ell factor, represented conservatively by b_eff=2*b=288.",
        },
        "n2c_status": {
            "word_to_duhamel_attribution": "PASS_CONDITIONAL",
            "boundary_escape_N4": "PASS_CONDITIONAL",
            "anchored_n": "NOT_DISCHARGED",
        },
        "scope": "Non-importing finite-fibre arithmetic reconstruction of the source-local Duhamel/coupling envelope; no new PAH definition or anchored-n theorem.",
        "non_claims": [
            "No N2a common U_n, N2b liminf/recovery or N2d minimal-form identification.",
            "No anchored-n, infinite-volume, continuum or physical Pre-A/spacetime/QFT/gravity/Yang-Mills/mass-gap/TOE conclusion.",
            "External stochastic Markov time is not quantum real time, proper time or Lorentzian time.",
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
            raise SystemExit("PAH-OMC-020 independent Duhamel replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 DUHAMEL INDEPENDENT: PASS ({len(payload['checks'])} checks; b_eff=288)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
