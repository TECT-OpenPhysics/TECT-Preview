#!/usr/bin/env python3
"""Exact integer-state/root enumeration for prospective PAH-v2 revision 2.

Version: 0.1.0. First issued/version issued: 2026-09-11.
This implements the approved integer-state and labelled-channel definitions.
It does not evaluate F, rates, Gibbs weights, B, a projection, or a semigroup.
Standalone self-tests are bounded implementation checks, not an all-regulator
theorem. Regulator numbers in self_test are explicitly tooling test inputs.
"""

import argparse
from dataclasses import dataclass
from itertools import product
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "strategy/pa-hyp/PAH-001-v2-r2.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-definition-freeze/enumerator.json"
SIGNS = (-1, 1)  # Declared direction labels/order; not fitted parameters.
FAMILIES = ("PH", "TR", "LK", "AP")


@dataclass(frozen=True)
class Regulator:
    vertices: int
    edges: tuple
    K: int
    M_s: int
    M_psi: int
    Q: int

    def __post_init__(self):
        ints = (self.vertices, self.K, self.M_s, self.M_psi, self.Q)
        if any(type(x) is not int for x in ints):
            raise ValueError("Integer regulator coordinates required")
        if self.vertices < 2 or self.K < 2 or self.M_s < 1 or self.M_psi < 1:
            raise ValueError("Outside the declared finite coordinate range")
        if not 0 <= self.Q <= self.vertices * self.M_psi:
            raise ValueError("The fixed-Q counting space must be nonempty")
        if type(self.edges) is not tuple:
            raise ValueError("Immutable carried edge tuple required")
        for edge in self.edges:
            if type(edge) is not tuple or len(edge) != 2 or any(type(v) is not int or not 0 <= v < self.vertices for v in edge):
                raise ValueError("Invalid carried edge endpoints")


@dataclass(frozen=True)
class State:
    aperture: tuple
    occupation: tuple
    phase: tuple
    link: tuple


@dataclass(frozen=True)
class Move:
    family: str
    cell: int
    sign: int

    def inverse(self):
        return Move(self.family, self.cell, -self.sign)


def valid_state(reg, state):
    if not isinstance(state, State):
        return False
    coords = ((state.aperture, reg.vertices, reg.M_s + 1),
              (state.occupation, reg.vertices, reg.M_psi + 1),
              (state.phase, reg.vertices, reg.K),
              (state.link, len(reg.edges), reg.K))
    return all(type(xs) is tuple and len(xs) == length and all(type(x) is int and 0 <= x < bound for x in xs)
               for xs, length, bound in coords) and sum(state.occupation) == reg.Q


def states(reg):
    """Lazy exact full set. No quotient or hidden cutoff/budget is imposed."""
    for occ in product(range(reg.M_psi + 1), repeat=reg.vertices):
        if sum(occ) != reg.Q:
            continue
        for ap in product(range(reg.M_s + 1), repeat=reg.vertices):
            for phase in product(range(reg.K), repeat=reg.vertices):
                for links in product(range(reg.K), repeat=len(reg.edges)):
                    yield State(ap, occ, phase, links)


def roots(reg):
    """Each primitive type/cell/sign label appears once, in fixed order."""
    for family in FAMILIES:
        size = reg.vertices if family in ("PH", "AP") else len(reg.edges)
        for cell in range(size):
            for sign in SIGNS:
                yield Move(family, cell, sign)


def apply_move(reg, state, move):
    """Return the exact partial-map value, or None for an invalid move.

    TR uses the simultaneous signed incidence update. For a loop, tail=head
    gives net zero, hence a valid identity incidence; no extra graph is added.
    Invalid final coordinate vectors are omitted, never clipped or reflected.
    """
    if not valid_state(reg, state):
        raise ValueError("Invalid source state")
    if move.family not in FAMILIES or type(move.sign) is not int or move.sign not in SIGNS or type(move.cell) is not int:
        raise ValueError("Invalid root label")
    size = reg.vertices if move.family in ("PH", "AP") else len(reg.edges)
    if not 0 <= move.cell < size:
        raise ValueError("Invalid root cell")
    ap, occ, phase, links = map(list, (state.aperture, state.occupation, state.phase, state.link))
    if move.family == "PH":
        phase[move.cell] = (phase[move.cell] + move.sign) % reg.K
    elif move.family == "LK":
        links[move.cell] = (links[move.cell] + move.sign) % reg.K
    elif move.family == "AP":
        ap[move.cell] += move.sign
    else:
        tail, head = reg.edges[move.cell]
        occ[tail] -= move.sign
        occ[head] += move.sign
    target = State(tuple(ap), tuple(occ), tuple(phase), tuple(links))
    return target if valid_state(reg, target) else None


def incidences(reg, state):
    for move in roots(reg):
        target = apply_move(reg, state, move)
        if target is not None:
            yield move, target


def self_test():
    # Small coordinate-only unit fixtures; no PAH physical/research carrier
    # evidence, no functional/rate fitting, and no all-regulator inference.
    fixtures = (
        Regulator(2, ((0, 1),), 2, 1, 1, 1),
        Regulator(2, ((1, 0),), 3, 1, 1, 1),
        Regulator(2, ((0, 0), (0, 1), (0, 1)), 2, 1, 1, 0),
    )
    rows = []
    for reg in fixtures:
        full_states = tuple(states(reg))
        labels = tuple(roots(reg))
        assert len(set(full_states)) == len(full_states)
        assert len(set(labels)) == len(labels)
        count = 0
        for x in full_states:
            assert valid_state(reg, x)
            for r, y in incidences(reg, x):
                count += 1
                assert apply_move(reg, y, r.inverse()) == x
                assert sum(y.occupation) == reg.Q
                if r.family == "TR":
                    assert (y.aperture, y.phase, y.link) == (x.aperture, x.phase, x.link)
                if r.family in ("PH", "LK") and reg.K == 2:
                    assert r != r.inverse() and apply_move(reg, x, r.inverse()) == y
            for v in range(reg.vertices):
                if x.aperture[v] == 0:
                    assert apply_move(reg, x, Move("AP", v, -1)) is None
                if x.aperture[v] == reg.M_s:
                    assert apply_move(reg, x, Move("AP", v, 1)) is None
                if x.occupation[v] == 0:
                    assert apply_move(reg, x, Move("PH", v, 1)) != x
        # Aperture labels remain distinct independent of any epsilon value:
        # epsilon affects displayed evaluation, not this approved state set.
        assert any(x.aperture[0] != y.aperture[0]
                   and (x.occupation, x.phase, x.link) == (y.occupation, y.phase, y.link)
                   for x in full_states for y in full_states)
        rows.append({"vertices": reg.vertices, "edges": reg.edges, "K": reg.K,
                     "M_s": reg.M_s, "M_psi": reg.M_psi, "Q": reg.Q,
                     "states_checked": len(full_states), "root_labels": len(labels),
                     "valid_incidences_checked": count})
    return rows


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    assert sha(Path(__file__)) == spec["exact_move_enumerator"]["sha256"]
    for path, expected in spec["source_pins"].items():
        assert sha(ROOT / path) == expected, path
    # Specification and enumerator are pinned BEFORE the unit checks below.
    result = {
        "schema": "tect/pah-v2-enumerator-unit-check/1.0",
        "scope": "BOUNDED_IMPLEMENTATION_UNIT_CHECKS_ONLY",
        "spec_sha256": sha(SPEC), "enumerator_sha256": sha(Path(__file__)),
        "status": "PASS", "fixtures": self_test(),
        "all_finite_theorem_verified": False,
        "detailed_balance_projection_BstarB_verified": False,
        "independent_hostile_mathematical_verification": "NOT_RUN",
        "Lean": "NOT_RUN",
        "non_claims": "No finite-general theorem, refinement, limit, physical Pre-A, QFT, gravity or TOE claim.",
    }
    # Normalize tuples to their JSON list representation for stable replay.
    result = json.loads(json.dumps(result))
    if args.check:
        assert json.loads(args.output.read_text(encoding="utf-8")) == result
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, ensure_ascii=True, sort_keys=True, indent=2)
            stream.write("\n")
    print("PAH-V2-ENUMERATOR: PASS (bounded unit checks only; general finite theorem NOT_VERIFIED)")


if __name__ == "__main__":
    main()
