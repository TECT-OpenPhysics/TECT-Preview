#!/usr/bin/env python3
"""Non-importing bitmask audit for PA-C0B-EQUIVARIANT-CAUSAL-SELECTION-NOGO-v0."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0B-EQUIVARIANT-CAUSAL-SELECTION-NOGO-v0"
SLUG = "pre-a-c0b-equivariant-causal-selection-nogo"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)


def encode(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, F):
        return str(value)
    if isinstance(value, set):
        return sorted([encode(item) for item in value], key=str)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relation_pairs(size: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(size)
        for right in range(size)
        if left != right
    )


def mask_to_relation(mask: int, pairs: tuple[tuple[int, int], ...]) -> set[tuple[int, int]]:
    return {pair for index, pair in enumerate(pairs) if mask & (1 << index)}


def is_strict_partial_order(size: int, relation: set[tuple[int, int]]) -> bool:
    for index in range(size):
        if (index, index) in relation:
            return False
    for left in range(size):
        for middle in range(size):
            if (left, middle) not in relation:
                continue
            for right in range(size):
                if (middle, right) in relation and (left, right) not in relation:
                    return False
    return True


def permute(
    relation: set[tuple[int, int]], permutation: tuple[int, ...]
) -> set[tuple[int, int]]:
    return {(permutation[left], permutation[right]) for left, right in relation}


def opposite(relation: set[tuple[int, int]]) -> set[tuple[int, int]]:
    return {(right, left) for left, right in relation}


def order_from_marks(marks: tuple[int, ...]) -> set[tuple[int, int]]:
    return {
        (left, right)
        for left in range(len(marks))
        for right in range(len(marks))
        if marks[left] < marks[right]
    }


def derive() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": encode(actual),
                "expected": encode(expected),
                "group": group,
            }
        )

    size = 4
    pairs = relation_pairs(size)
    permutations = tuple(itertools.permutations(range(size)))
    all_relations = [
        mask_to_relation(mask, pairs) for mask in range(1 << len(pairs))
    ]
    strict_orders = [
        relation for relation in all_relations if is_strict_partial_order(size, relation)
    ]
    invariant_relations = [
        relation
        for relation in all_relations
        if all(permute(relation, permutation) == relation for permutation in permutations)
    ]
    invariant_orders = [
        relation for relation in invariant_relations if is_strict_partial_order(size, relation)
    ]
    self_opposite_orders = [
        relation for relation in strict_orders if relation == opposite(relation)
    ]

    check(
        "independent ordered off-diagonal pair count",
        len(pairs) == 12,
        len(pairs),
        12,
        "enumeration",
    )
    check(
        "independent relation enumeration count",
        len(all_relations) == 4096,
        len(all_relations),
        4096,
        "enumeration",
    )
    # 219 is a labelled-four-element-poset enumeration oracle, not a physical
    # input or a theorem coefficient.
    check(
        "independent strict partial-order enumeration oracle",
        len(strict_orders) == 219,
        len(strict_orders),
        219,
        "enumeration",
    )
    full_off_diagonal = set(pairs)
    check(
        "independent invariant irreflexive relations",
        invariant_relations == [set(), full_off_diagonal],
        invariant_relations,
        [set(), full_off_diagonal],
        "equivariant_nogo",
    )
    check(
        "independent only invariant strict order is empty",
        invariant_orders == [set()],
        invariant_orders,
        [set()],
        "equivariant_nogo",
    )
    check(
        "independent only self-opposite strict order is empty",
        self_opposite_orders == [set()],
        self_opposite_orders,
        [set()],
        "reversal_nogo",
    )

    seed = {(0, 1)}
    orbit = set()
    for permutation in permutations:
        orbit |= permute(seed, permutation)
    check(
        "independent seed ordered-pair orbit",
        orbit == full_off_diagonal,
        orbit,
        full_off_diagonal,
        "equivariant_nogo",
    )

    rotations = tuple(
        tuple((event + shift) % size for event in range(size))
        for shift in range(size)
    )
    vertex_orbit = {permutation[0] for permutation in rotations}
    check(
        "independent C4 action is vertex-transitive",
        vertex_orbit == set(range(size)),
        vertex_orbit,
        set(range(size)),
        "finite_transitive_nogo",
    )
    c4_pair_orbits = []
    for difference in (1, 2, 3):
        seed_relation = {(0, difference)}
        pair_orbit: set[tuple[int, int]] = set()
        for permutation in rotations:
            pair_orbit |= permute(seed_relation, permutation)
        c4_pair_orbits.append(pair_orbit)
    check(
        "independent C4 action is not 2-transitive",
        [len(pair_orbit) for pair_orbit in c4_pair_orbits] == [4, 4, 4],
        [len(pair_orbit) for pair_orbit in c4_pair_orbits],
        [4, 4, 4],
        "finite_transitive_nogo",
    )
    c4_invariant_relations = [
        relation
        for relation in all_relations
        if all(permute(relation, permutation) == relation for permutation in rotations)
    ]
    c4_invariant_orders = [
        relation
        for relation in c4_invariant_relations
        if is_strict_partial_order(size, relation)
    ]
    check(
        "independent C4 invariant irreflexive relation count",
        len(c4_invariant_relations) == 8,
        len(c4_invariant_relations),
        8,
        "finite_transitive_nogo",
    )
    check(
        "independent C4 only invariant strict order is empty",
        c4_invariant_orders == [set()],
        c4_invariant_orders,
        [set()],
        "finite_transitive_nogo",
    )
    two_orbit_group = ((0, 1, 2, 3), (1, 0, 3, 2))
    two_orbit_order = {
        (lower, upper) for lower in (0, 1) for upper in (2, 3)
    }
    check(
        "independent two-orbit control is invariant and strict",
        is_strict_partial_order(size, two_orbit_order)
        and all(
            permute(two_orbit_order, permutation) == two_orbit_order
            for permutation in two_orbit_group
        ),
        (is_strict_partial_order(size, two_orbit_order), two_orbit_order),
        (True, {(0, 2), (0, 3), (1, 2), (1, 3)}),
        "symmetry_reduction_control",
    )

    marks = (0, 1, 4, 9)
    marked_order = order_from_marks(marks)
    check(
        "independent marked relation is a total strict order",
        marked_order in strict_orders and len(marked_order) == 6,
        (marked_order in strict_orders, len(marked_order)),
        (True, 6),
        "symmetry_breaking_control",
    )
    marked_stabilizer = [
        permutation
        for permutation in permutations
        if permute(marked_order, permutation) == marked_order
    ]
    check(
        "independent marked control has trivial stabilizer",
        marked_stabilizer == [(0, 1, 2, 3)],
        marked_stabilizer,
        [(0, 1, 2, 3)],
        "symmetry_breaking_control",
    )
    equivariant_checks = []
    for permutation in permutations:
        permuted_marks = [0] * size
        for source, target in enumerate(permutation):
            permuted_marks[target] = marks[source]
        equivariant_checks.append(
            order_from_marks(tuple(permuted_marks)) == permute(marked_order, permutation)
        )
    check(
        "independent marked selector is relabeling equivariant",
        all(equivariant_checks),
        equivariant_checks,
        [True] * len(permutations),
        "symmetry_breaking_control",
    )
    check(
        "independent sign reversal reverses marked order",
        order_from_marks(tuple(-value for value in marks)) == opposite(marked_order),
        order_from_marks(tuple(-value for value in marks)),
        opposite(marked_order),
        "symmetry_breaking_control",
    )

    total_orders = [order_from_marks(permutation) for permutation in permutations]
    check(
        "independent random-order support contains 24 distinct orders",
        len({frozenset(relation) for relation in total_orders}) == 24,
        len({frozenset(relation) for relation in total_orders}),
        24,
        "random_sector_boundary",
    )
    check(
        "independent random-order law is S4 invariant",
        all(
            permute(relation, permutation) in total_orders
            for relation in total_orders
            for permutation in permutations
        ),
        True,
        True,
        "random_sector_boundary",
    )
    pair_counts: dict[str, tuple[int, int]] = {}
    for left in range(size):
        for right in range(left + 1, size):
            forward = sum((left, right) in relation for relation in total_orders)
            backward = sum((right, left) in relation for relation in total_orders)
            pair_counts[f"{left}-{right}"] = (forward, backward)
    check(
        "independent uniform random total-order distribution is pair-unbiased",
        all(counts == (12, 12) for counts in pair_counts.values()),
        pair_counts,
        "every unordered pair has counts (12,12)",
        "random_sector_boundary",
    )

    source = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "independent exhaustive bitmask audit of a T0 C0-B symmetry no-go",
        "shared_exact_results": {
            "fixture_event_count": size,
            "symmetry_group_size": len(permutations),
            "relation_count": len(all_relations),
            "strict_partial_order_count": len(strict_orders),
            "ordered_pair_orbit_size": len(orbit),
            "invariant_irreflexive_relation_count": len(invariant_relations),
            "invariant_strict_partial_orders": invariant_orders,
            "self_opposite_strict_partial_orders": self_opposite_orders,
            "c4_group_size": len(rotations),
            "c4_vertex_orbit_size": len(vertex_orbit),
            "c4_ordered_pair_orbit_sizes": [len(pair_orbit) for pair_orbit in c4_pair_orbits],
            "c4_invariant_relation_count": len(c4_invariant_relations),
            "c4_invariant_strict_partial_orders": c4_invariant_orders,
            "two_orbit_invariant_strict_order": two_orbit_order,
            "marked_total_order": marked_order,
            "marked_control_stabilizer_size": len(marked_stabilizer),
            "random_total_order_support_size": len({frozenset(relation) for relation in total_orders}),
            "random_total_order_law_s4_invariant": True,
            "uniform_pair_probability": F(1, 2),
            "pre_a_complete": False,
        },
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
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "source": {"path": source.relative_to(REPO), "sha256": sha256(source)},
        "no_overclaim": (
            "This exhaustive audit checks the labelled four-event fixture and the reversal boundary. It excludes "
            "only deterministic equivariant order selection from the fully symmetric state. It does not exclude "
            "random or relational C0-B models, derive a causal order or null cone, select a theory, or complete Pre-A."
        ),
    }


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
        f"independent {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
