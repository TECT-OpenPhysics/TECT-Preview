#!/usr/bin/env python3
"""Primary exact certificate for PA-C0B-EQUIVARIANT-CAUSAL-SELECTION-NOGO-v0.

The certificate exhausts the four-event fully permutation-symmetric fixture
and proves a finite-orbit theorem: an invariant strict order cannot compare
two events in the same automorphism orbit.  Hence a deterministic equivariant
selector is empty on a finite vertex-transitive substrate state.  The stronger
ordered-pair-orbit proof is retained for 2-transitive actions.  This is a
conditional C0-B symmetry gate, not a no-go for random sector selection,
smaller-orbit relational substrates, or infinite transitive substrates.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0B-EQUIVARIANT-CAUSAL-SELECTION-NOGO-v0"
SLUG = "pre-a-c0b-equivariant-causal-selection-nogo"
SCHEMA = f"tect/{SLUG}-primary/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-primary-{SLUG}"
    / "result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, col]) for col in range(value.cols)] for row in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, set):
        return sorted([serial(item) for item in value], key=str)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
                "group": group,
            }
        )


def permutation_matrix(permutation: tuple[int, ...]) -> sp.Matrix:
    size = len(permutation)
    matrix = sp.zeros(size)
    for source, target in enumerate(permutation):
        matrix[target, source] = 1
    return matrix


def relation_matrix(size: int, pairs: set[tuple[int, int]]) -> sp.Matrix:
    return sp.Matrix(
        size,
        size,
        lambda row, col: sp.Integer(int((row, col) in pairs)),
    )


def is_strict_partial_order(size: int, pairs: set[tuple[int, int]]) -> bool:
    if any((index, index) in pairs for index in range(size)):
        return False
    for first, middle in pairs:
        for middle_two, last in pairs:
            if middle == middle_two and (first, last) not in pairs:
                return False
    return True


def permute_relation(
    pairs: set[tuple[int, int]], permutation: tuple[int, ...]
) -> set[tuple[int, int]]:
    return {(permutation[left], permutation[right]) for left, right in pairs}


def order_from_marks(marks: tuple[int, ...]) -> set[tuple[int, int]]:
    return {
        (left, right)
        for left in range(len(marks))
        for right in range(len(marks))
        if marks[left] < marks[right]
    }


def derive() -> dict[str, Any]:
    audit = Audit()
    size = 4
    events = tuple(range(size))
    permutations = tuple(itertools.permutations(events))
    off_diagonal = {(left, right) for left in events for right in events if left != right}

    audit.check(
        "S4 permutation count",
        len(permutations) == 24,
        len(permutations),
        24,
        "symmetry",
    )
    matrices = [permutation_matrix(permutation) for permutation in permutations]
    audit.check(
        "permutation matrices preserve the fully symmetric state",
        all(matrix * sp.ones(size, 1) == sp.ones(size, 1) for matrix in matrices),
        all(matrix * sp.ones(size, 1) == sp.ones(size, 1) for matrix in matrices),
        True,
        "symmetry",
    )

    seed = {(0, 1)}
    orbit = set()
    for permutation in permutations:
        orbit |= permute_relation(seed, permutation)
    audit.check(
        "ordered-pair orbit is every off-diagonal pair",
        orbit == off_diagonal,
        orbit,
        off_diagonal,
        "symmetry",
    )
    audit.check(
        "ordered-pair orbit contains every reversed pair",
        all((right, left) in orbit for left, right in orbit),
        all((right, left) in orbit for left, right in orbit),
        True,
        "symmetry",
    )

    # Because the action on ordered distinct pairs is transitive, the only
    # invariant irreflexive relations are empty and the full off-diagonal
    # relation.  The latter is not a strict partial order.
    invariant_irreflexive_relations = [set(), off_diagonal]
    for relation in invariant_irreflexive_relations:
        audit.check(
            f"candidate invariant relation is S4 invariant: size {len(relation)}",
            all(permute_relation(relation, permutation) == relation for permutation in permutations),
            all(permute_relation(relation, permutation) == relation for permutation in permutations),
            True,
            "equivariant_nogo",
        )
    audit.check(
        "full off-diagonal relation is not asymmetric",
        any((right, left) in off_diagonal for left, right in off_diagonal),
        True,
        True,
        "equivariant_nogo",
    )
    audit.check(
        "only invariant strict partial order is empty",
        [relation for relation in invariant_irreflexive_relations if is_strict_partial_order(size, relation)]
        == [set()],
        [relation for relation in invariant_irreflexive_relations if is_strict_partial_order(size, relation)],
        [set()],
        "equivariant_nogo",
    )

    empty_matrix = relation_matrix(size, set())
    full_matrix = relation_matrix(size, off_diagonal)
    audit.check(
        "matrix conjugation fixes the two invariant relations",
        all(matrix * empty_matrix * matrix.T == empty_matrix for matrix in matrices)
        and all(matrix * full_matrix * matrix.T == full_matrix for matrix in matrices),
        True,
        True,
        "equivariant_nogo",
    )

    # The finite theorem needs only vertex transitivity.  C4 rotations give an
    # exact action that is transitive on events but not on ordered pairs.
    rotations = tuple(
        tuple((event + shift) % size for event in events) for shift in events
    )
    vertex_orbit = {permutation[0] for permutation in rotations}
    audit.check(
        "C4 action is vertex-transitive",
        vertex_orbit == set(events),
        vertex_orbit,
        set(events),
        "finite_transitive_nogo",
    )
    c4_pair_orbits = []
    for difference in (1, 2, 3):
        seed_relation = {(0, difference)}
        c4_pair_orbits.append(
            set().union(
                *(permute_relation(seed_relation, permutation) for permutation in rotations)
            )
        )
    audit.check(
        "C4 action is not 2-transitive",
        all(len(pair_orbit) < len(off_diagonal) for pair_orbit in c4_pair_orbits),
        [len(pair_orbit) for pair_orbit in c4_pair_orbits],
        "all smaller than 12",
        "finite_transitive_nogo",
    )
    audit.check(
        "C4 ordered-pair orbit sizes are 4,4,4",
        [len(pair_orbit) for pair_orbit in c4_pair_orbits] == [4, 4, 4]
        and set().union(*c4_pair_orbits) == off_diagonal,
        ([len(pair_orbit) for pair_orbit in c4_pair_orbits], set().union(*c4_pair_orbits)),
        ([4, 4, 4], off_diagonal),
        "finite_transitive_nogo",
    )
    c4_invariant_relations = []
    for mask in range(1 << len(c4_pair_orbits)):
        relation: set[tuple[int, int]] = set()
        for index, pair_orbit in enumerate(c4_pair_orbits):
            if mask & (1 << index):
                relation |= pair_orbit
        c4_invariant_relations.append(relation)
    c4_invariant_orders = [
        relation
        for relation in c4_invariant_relations
        if is_strict_partial_order(size, relation)
    ]
    audit.check(
        "C4 invariant irreflexive relation count is 8",
        len(c4_invariant_relations) == 8
        and all(
            all(permute_relation(relation, permutation) == relation for permutation in rotations)
            for relation in c4_invariant_relations
        ),
        len(c4_invariant_relations),
        8,
        "finite_transitive_nogo",
    )
    audit.check(
        "C4 only invariant strict order is empty",
        c4_invariant_orders == [set()],
        c4_invariant_orders,
        [set()],
        "finite_transitive_nogo",
    )

    # Once the event set splits into two automorphism orbits, an invariant
    # nonempty strict order between the orbits is possible without claiming a
    # dynamical symmetry-breaking process.
    two_orbit_group = ((0, 1, 2, 3), (1, 0, 3, 2))
    two_orbit_order = {
        (lower, upper) for lower in (0, 1) for upper in (2, 3)
    }
    audit.check(
        "two-orbit symmetry-reduction control is invariant and strict",
        is_strict_partial_order(size, two_orbit_order)
        and all(
            permute_relation(two_orbit_order, permutation) == two_orbit_order
            for permutation in two_orbit_group
        ),
        (is_strict_partial_order(size, two_orbit_order), two_orbit_order),
        (True, {(0, 2), (0, 3), (1, 2), (1, 3)}),
        "symmetry_reduction_control",
    )

    # Reversal-invariant deterministic selection has C=C^op.  A nonempty
    # strict order cannot equal its opposite.
    sample_order = {(0, 1), (1, 2), (0, 2)}
    sample_opposite = {(right, left) for left, right in sample_order}
    audit.check(
        "nonempty strict order differs from its opposite",
        is_strict_partial_order(size, sample_order) and sample_order != sample_opposite,
        (is_strict_partial_order(size, sample_order), sample_order == sample_opposite),
        (True, False),
        "reversal_nogo",
    )
    audit.check(
        "strict relation equal to its opposite must be empty",
        all(
            not (relation == {(right, left) for left, right in relation}) or not relation
            for relation in (set(), sample_order, off_diagonal)
            if is_strict_partial_order(size, relation)
        ),
        True,
        True,
        "reversal_nogo",
    )

    # Positive control: distinct relational marks break the full permutation
    # stabilizer and define an equivariant total order.  The marks and their
    # orientation are additional state data, not outputs of the symmetric state.
    marks = (0, 1, 4, 9)
    marked_order = order_from_marks(marks)
    audit.check(
        "distinct clock marks define a strict total order",
        is_strict_partial_order(size, marked_order)
        and len(marked_order) == size * (size - 1) // 2,
        (is_strict_partial_order(size, marked_order), len(marked_order)),
        (True, 6),
        "symmetry_breaking_control",
    )
    marked_stabilizer = [
        permutation
        for permutation in permutations
        if permute_relation(marked_order, permutation) == marked_order
    ]
    audit.check(
        "marked control has trivial stabilizer",
        marked_stabilizer == [(0, 1, 2, 3)],
        marked_stabilizer,
        [(0, 1, 2, 3)],
        "symmetry_breaking_control",
    )
    for index, permutation in enumerate(permutations):
        permuted_marks = [0] * size
        for source, target in enumerate(permutation):
            permuted_marks[target] = marks[source]
        audit.check(
            f"marked-order relabeling equivariance {index}",
            order_from_marks(tuple(permuted_marks))
            == permute_relation(marked_order, permutation),
            order_from_marks(tuple(permuted_marks)),
            permute_relation(marked_order, permutation),
            "symmetry_breaking_control",
        )
    reversed_marks = tuple(-value for value in marks)
    reversed_order = order_from_marks(reversed_marks)
    audit.check(
        "reversing all marks reverses the selected order",
        reversed_order == {(right, left) for left, right in marked_order},
        reversed_order,
        {(right, left) for left, right in marked_order},
        "symmetry_breaking_control",
    )

    # A permutation-invariant random distribution over total orders is not
    # excluded.  It assigns each orientation of any pair probability one half
    # and therefore supplies no deterministic preferred arrow before sampling.
    total_orders = [order_from_marks(permutation) for permutation in permutations]
    audit.check(
        "uniform random-order support contains 24 distinct orders",
        len({frozenset(relation) for relation in total_orders}) == 24,
        len({frozenset(relation) for relation in total_orders}),
        24,
        "random_sector_boundary",
    )
    audit.check(
        "uniform random-order law is invariant under every S4 relabeling",
        all(
            permute_relation(relation, permutation) in total_orders
            for relation in total_orders
            for permutation in permutations
        ),
        True,
        True,
        "random_sector_boundary",
    )
    for left in range(size):
        for right in range(left + 1, size):
            forward_count = sum((left, right) in relation for relation in total_orders)
            backward_count = sum((right, left) in relation for relation in total_orders)
            audit.check(
                f"uniform random total orders have unbiased pair {left}-{right}",
                (forward_count, backward_count) == (12, 12),
                (forward_count, backward_count),
                (12, 12),
                "random_sector_boundary",
            )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "C0B-EQUIVARIANT-CAUSAL-SELECTION-NOGO",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 C0-B symmetry no-go certificate; not a TECT claim, causal-emergence theorem, or cosmology",
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "theorem": {
            "hypothesis": "a finite substrate state plus a deterministic natural equivariant selector of a strict partial order",
            "orbitwise_conclusion": "no two events in the same automorphism orbit are comparable",
            "transitive_conclusion": "if the automorphism group is vertex-transitive, the selected strict partial order is empty",
            "finite_orbit_reason": "a comparison x<C(gx) iterates around the finite order of g to produce x<Cx",
            "two_transitive_corollary": "one selected ordered pair forces the full orbit of ordered distinct pairs, including its reverse, contradicting asymmetry; this corollary does not require finite X",
            "reversal_corollary": "under fixed labels or after declared pullback identification, if a reversal-invariant state must select C and covariance requires the opposite order, then deterministic strict C is empty",
        },
        "exact_results": {
            "fixture_event_count": size,
            "fixture_symmetry_group_size": len(permutations),
            "ordered_pair_orbit_size": len(orbit),
            "invariant_irreflexive_relations": [set(), off_diagonal],
            "invariant_strict_partial_orders": [set()],
            "c4_group_size": len(rotations),
            "c4_vertex_orbit_size": len(vertex_orbit),
            "c4_ordered_pair_orbit_sizes": [len(pair_orbit) for pair_orbit in c4_pair_orbits],
            "c4_invariant_irreflexive_relation_count": len(c4_invariant_relations),
            "c4_invariant_strict_partial_orders": c4_invariant_orders,
            "two_orbit_invariant_strict_order": two_orbit_order,
            "symmetry_broken_marks": marks,
            "symmetry_broken_total_order": marked_order,
            "marked_control_stabilizer_size": len(marked_stabilizer),
            "random_total_order_support_size": len({frozenset(relation) for relation in total_orders}),
            "random_total_order_law_s4_invariant": True,
            "uniform_total_order_pair_probability": Fraction(1, 2),
        },
        "conditional_escape_structure_for_excluded_symmetric_route": [
            "if the finite input is vertex-transitive, a relational state with multiple automorphism orbits, an asymmetric boundary condition, or a probabilistic sector-selection law",
            "if exact fixed-label reversal invariance is imposed, an orientation-bearing state, boundary condition, sector, or non-unique selector",
            "a proof of how any realized order becomes physical",
        ],
        "independent_tect_integration_gates": [
            "an intervention or propagation definition that distinguishes causal influence from mere adjacency",
            "a continuum theorem producing a controlled Lorentz cone and null boundary",
        ],
        "scope": {
            "deterministic_equivariant_comparison_within_finite_automorphism_orbit": False,
            "deterministic_equivariant_nonempty_order_from_finite_transitive_state": False,
            "deterministic_equivariant_nonempty_order_from_2transitive_state": False,
            "reversal_invariant_state_selects_unique_nonempty_arrow": False,
            "extra_asymmetry_or_sector_required_for_excluded_symmetric_input": True,
            "finite_transitive_nogo_extended_to_infinite_transitive_state": False,
            "random_invariant_order_distribution_excluded": False,
            "quotient_set_valued_or_coherent_sector_selector_excluded": False,
            "richer_relational_c0b_model_excluded": False,
            "causal_set_program_invalidated": False,
            "quantum_graphity_program_invalidated": False,
            "gft_tensor_program_invalidated": False,
            "causal_order_derived": False,
            "null_structure_derived": False,
            "c0b_candidate_selected": False,
            "pre_a_complete": False,
        },
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "source": {"path": source.relative_to(REPO), "sha256": sha256(source)},
        "no_overclaim": (
            "This certificate excludes deterministic natural comparison within one finite automorphism orbit, "
            "and fixed-label unique-arrow selection from an exactly reversal-invariant state. It does not extend "
            "the finite transitive theorem to infinite transitive substrates or exclude stochastic symmetry "
            "breaking, relational order parameters, causal sets, graphity, GFT or tensor models, derive a causal "
            "order or null cone, choose a physical C0-B theory, connect PA-H1 to PA-M2, or complete Pre-A."
        ),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"{CANDIDATE_ID} | symmetric causal selection excluded"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
