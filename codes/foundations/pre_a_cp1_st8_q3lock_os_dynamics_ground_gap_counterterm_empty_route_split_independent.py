#!/usr/bin/env python3
"""Independent exact verifier for the ordered EXP-000790 route split.

This implementation deliberately does not import the primary verifier, its
JSON output, a computer-algebra system, or an array package.  It enumerates all
8! vertex permutations to recover Aut(Q3), constructs invariant monomials by
recursive weak composition, and uses :class:`fractions.Fraction` plus a local
row-reduction routine for every exact algebra calculation.

The finite fixtures audit the certificate interfaces; they do not construct a
common infinite-volume dynamics, algebraic ground state, GNS gap, continuum
limit, or physical empty-space state.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Iterator


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-os-dynamics-ground-gap-counterterm-empty-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-ORDERED-OS-DYNAMICS-GROUND-GAP-CONTINUUM-EMPTY-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-PHASEWISE-OS-KMS-ZERO-T-GROUND-CUSP-FULL-Q3-COUNTERTERM-AND-EMPTY-REFERENCE-SPLIT"
EXPLORATION_ID = "EXP-000790"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-INFINITE-VOLUME-DYNAMICS-KMS-GROUND-AND-CONTINUUM-SPLIT"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-RESOLVENT-ALGEBRA-EXACT-POLYNOMIAL-COMMON-ALPHA-CLOSURE"
NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-POSTHOC-DIRECT-SUM-COMMON-DYNAMICS",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-CURRENT-COMMON-DYNAMICS-THEOREM-IMPORT-MISMATCH",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-PARTIAL-QUARTIC-COUNTERTERM-ALL-SCALE-CLOSURE",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-EQUILIBRIUM-PHASE-AS-STRICT-EMPTY-REFERENCE",
)
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260809.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT_RESULTS = (
    (REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split/result.json", "EXP-000780", "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-THERMODYNAMIC-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT-v0", "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-FREE-PERIODIC-SOURCE-PRESSURE-AND-CENTERED-GROUND-ENERGY-DENSITY"),
    (REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-phase-boundary-route-split/result.json", "EXP-000781", "PA-CP1-ST8-Q3LOCK-EUCLIDEAN-DLR-TANGENT-STATE-AND-PHASE-BOUNDARY-ROUTE-SPLIT-v0", "PA-CP1-ST8-Q3LOCK-TEMPERED-EUCLIDEAN-DLR-TANGENT-STATES-AND-LAMBDA0-PHASE-BOUNDARY"),
    (REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split/result.json", "EXP-000782", "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-FKG-INFRARED-CUSP-PHASE-ROUTE-SPLIT-v0", "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-LOW-TEMPERATURE-DLR-PHASE-AND-COLLECTIVE-SOURCE-CUSP"),
    (REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-integrated-pre-a-cp1-st8-q3lock-ground-equal-time-order-gap-continuum-counterterm-route-split/result.json", "EXP-000789", "PA-CP1-ST8-Q3LOCK-GROUND-EQUAL-TIME-ORDER-GAP-CONTINUUM-COUNTERTERM-ROUTE-SPLIT-v0", "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-GROUND-EQUAL-TIME-LRO-APPROXIMATE-DOUBLETS-FULL-GAP-COLLAPSE-AND-CONTINUUM-BASIS-OBSTRUCTION"),
)
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-independent-{SLUG}/result.json"

# Regression oracles copied from the analytic certificate.  Every coefficient,
# dimension, and rank compared with these values is recomputed below from the
# graph and the Hessian-trace operation.
TEST_ORACLE_AUTOMORPHISM_COUNT = 48
TEST_ORACLE_Q3_EDGE_COUNT = 12
TEST_ORACLE_QUARTIC_MONOMIAL_COUNT = 330
TEST_ORACLE_QUARTIC_DIMENSION = 19
TEST_ORACLE_CLOSURE_RANKS = [2, 4, 9, 19, 19]
TEST_ORACLE_QUADRATIC_DISTANCES = [0, 1, 2, 3]
TEST_ORACLE_QUADRATIC_MONOMIAL_COUNT = 36
TEST_ORACLE_BARE_QUADRATIC_RANK = 2
TEST_ORACLE_FULL_QUADRATIC_RANK = 4
TEST_ORACLE_OS_GRAM_RANK = 2
TEST_ORACLE_ONE_LOOP = {
    "O4": (Fraction(9), Fraction(54), Fraction(195, 2)),
    "O31_d1": (Fraction(0), Fraction(-18), Fraction(-72)),
    "O22_d1": (Fraction(0), Fraction(12), Fraction(71)),
    "O211_1_1_2": (Fraction(0), Fraction(0), Fraction(18)),
    "O211_1_2_1": (Fraction(0), Fraction(0), Fraction(-6)),
    "O22_d2": (Fraction(0), Fraction(0), Fraction(4)),
}


Exponent = tuple[int, ...]
Polynomial = dict[Exponent, Fraction]
Vector = list[Fraction]
Permutation = tuple[int, ...]


def portable_sha256(path: Path) -> str:
    """Hash text portably across CRLF/LF checkouts."""

    content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a complete JSON artifact with an atomic same-directory replace."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    """Fail-fast assertion ledger serialized into the result artifact."""

    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def bit_distance(left: int, right: int) -> int:
    """Graph distance on Q3, derived from binary vertex labels."""

    return (left ^ right).bit_count()


Q3_EDGES = frozenset(
    (left, right)
    for left in range(8)
    for right in range(left + 1, 8)
    if bit_distance(left, right) == 1
)


def enumerate_graph_automorphisms() -> list[Permutation]:
    """Recover Aut(Q3) by testing all 8! vertex permutations."""

    output: list[Permutation] = []
    for permutation in itertools.permutations(range(8)):
        image_edges = frozenset(
            tuple(sorted((permutation[left], permutation[right]))) for left, right in Q3_EDGES
        )
        if image_edges == Q3_EDGES:
            output.append(permutation)
    return output


def weak_compositions(total: int, slots: int, prefix: tuple[int, ...] = ()) -> Iterator[Exponent]:
    """Generate all ordered weak compositions recursively."""

    if slots == 1:
        yield prefix + (total,)
        return
    for first in range(total + 1):
        yield from weak_compositions(total - first, slots - 1, prefix + (first,))


def move_exponent(exponent: Exponent, permutation: Permutation) -> Exponent:
    """Push a monomial exponent along a vertex permutation."""

    moved = [0] * len(exponent)
    for source, target in enumerate(permutation):
        moved[target] = exponent[source]
    return tuple(moved)


def quartic_orbit_label(exponent: Exponent) -> str:
    support = [index for index, power in enumerate(exponent) if power]
    powers = sorted((exponent[index] for index in support), reverse=True)
    if powers == [4]:
        return "O4"
    if powers == [3, 1]:
        cubic = next(index for index in support if exponent[index] == 3)
        linear = next(index for index in support if exponent[index] == 1)
        return f"O31_d{bit_distance(cubic, linear)}"
    if powers == [2, 2]:
        return f"O22_d{bit_distance(support[0], support[1])}"
    if powers == [2, 1, 1]:
        doubled = next(index for index in support if exponent[index] == 2)
        singles = [index for index in support if exponent[index] == 1]
        first, second = sorted(bit_distance(doubled, item) for item in singles)
        between = bit_distance(singles[0], singles[1])
        return f"O211_{first}_{second}_{between}"
    if powers == [1, 1, 1, 1]:
        distances = sorted(bit_distance(left, right) for left, right in itertools.combinations(support, 2))
        return "O1111_" + "_".join(str(distance) for distance in distances)
    raise AssertionError(f"unclassified quartic exponent {exponent}")


def partition_quartic_orbits(
    automorphisms: list[Permutation],
) -> tuple[list[str], list[list[Exponent]], dict[Exponent, int]]:
    monomials = list(weak_compositions(4, 8))
    unseen = set(monomials)
    labelled: list[tuple[str, list[Exponent]]] = []
    while unseen:
        seed = min(unseen)
        orbit = sorted({move_exponent(seed, permutation) for permutation in automorphisms})
        labels = {quartic_orbit_label(item) for item in orbit}
        if len(labels) != 1:
            raise AssertionError(f"orbit has inconsistent labels: {sorted(labels)}")
        labelled.append((labels.pop(), orbit))
        unseen.difference_update(orbit)
    labelled.sort(key=lambda item: item[0])
    names = [name for name, _ in labelled]
    orbits = [orbit for _, orbit in labelled]
    lookup = {exponent: index for index, orbit in enumerate(orbits) for exponent in orbit}
    return names, orbits, lookup


def derivative_two(exponent: Exponent, left: int, right: int) -> tuple[Fraction, Exponent] | None:
    reduced = list(exponent)
    if left == right:
        coefficient = reduced[left] * (reduced[left] - 1)
        if coefficient == 0:
            return None
        reduced[left] -= 2
    else:
        coefficient = reduced[left] * reduced[right]
        if coefficient == 0:
            return None
        reduced[left] -= 1
        reduced[right] -= 1
    return Fraction(coefficient), tuple(reduced)


def polynomial_add_scaled(target: Polynomial, source: Polynomial, scale: Fraction) -> None:
    for exponent, coefficient in source.items():
        updated = target.get(exponent, Fraction(0)) + scale * coefficient
        if updated:
            target[exponent] = updated
        elif exponent in target:
            del target[exponent]


def polynomial_product(left: Polynomial, right: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for first, first_coefficient in left.items():
        for second, second_coefficient in right.items():
            exponent = tuple(a + b for a, b in zip(first, second))
            output[exponent] = output.get(exponent, Fraction(0)) + first_coefficient * second_coefficient
    return {exponent: coefficient for exponent, coefficient in output.items() if coefficient}


def invariant_hessians(orbits: list[list[Exponent]]) -> list[list[Polynomial]]:
    """Compute all 64 ordered Hessian entries for each orbit sum."""

    output: list[list[Polynomial]] = []
    for orbit in orbits:
        entries: list[Polynomial] = []
        for left in range(8):
            for right in range(8):
                entry: Polynomial = {}
                for exponent in orbit:
                    derivative = derivative_two(exponent, left, right)
                    if derivative is not None:
                        coefficient, reduced = derivative
                        entry[reduced] = entry.get(reduced, Fraction(0)) + coefficient
                entries.append({key: value for key, value in entry.items() if value})
        output.append(entries)
    return output


def project_quartic(
    polynomial: Polynomial, orbits: list[list[Exponent]], lookup: dict[Exponent, int]
) -> Vector:
    if any(exponent not in lookup for exponent in polynomial):
        raise AssertionError("Hessian trace produced a nonquartic monomial")
    vector: Vector = []
    for orbit in orbits:
        coefficients = {polynomial.get(exponent, Fraction(0)) for exponent in orbit}
        if len(coefficients) != 1:
            raise AssertionError("Hessian trace is not constant on an Aut(Q3) orbit")
        vector.append(coefficients.pop())
    return vector


def build_bilinear_table(
    orbits: list[list[Exponent]], lookup: dict[Exponent, int]
) -> list[list[Vector]]:
    """Tabulate B(P,Q)=sum_(i,j) P_ij Q_ji in the orbit basis."""

    hessians = invariant_hessians(orbits)
    size = len(orbits)
    table = [[[Fraction(0) for _ in range(size)] for _ in range(size)] for _ in range(size)]
    for left in range(size):
        for right in range(left, size):
            polynomial: Polynomial = {}
            for row in range(8):
                for column in range(8):
                    first = hessians[left][8 * row + column]
                    second = hessians[right][8 * column + row]
                    if first and second:
                        polynomial_add_scaled(polynomial, polynomial_product(first, second), Fraction(1))
            vector = project_quartic(polynomial, orbits, lookup)
            table[left][right] = vector
            table[right][left] = vector
    return table


def rref_basis(rows: Iterable[Vector]) -> list[Vector]:
    """Exact reduced-row basis without an external linear-algebra package."""

    pivot_rows: dict[int, Vector] = {}
    for original in rows:
        row = [Fraction(value) for value in original]
        if not any(row):
            continue
        for pivot in sorted(pivot_rows):
            scale = row[pivot]
            if scale:
                row = [value - scale * basis_value for value, basis_value in zip(row, pivot_rows[pivot])]
        if not any(row):
            continue
        new_pivot = next(index for index, value in enumerate(row) if value)
        scale = row[new_pivot]
        row = [value / scale for value in row]
        for pivot, basis_row in list(pivot_rows.items()):
            scale = basis_row[new_pivot]
            if scale:
                pivot_rows[pivot] = [
                    value - scale * new_value for value, new_value in zip(basis_row, row)
                ]
        pivot_rows[new_pivot] = row
    return [pivot_rows[pivot] for pivot in sorted(pivot_rows)]


def bilinear_combine(left: Vector, right: Vector, table: list[list[Vector]]) -> Vector:
    size = len(table)
    output = [Fraction(0)] * size
    for left_index, left_coefficient in enumerate(left):
        if not left_coefficient:
            continue
        for right_index, right_coefficient in enumerate(right):
            if not right_coefficient:
                continue
            scale = left_coefficient * right_coefficient
            output = [
                value + scale * table_value
                for value, table_value in zip(output, table[left_index][right_index])
            ]
    return output


def quadratic_orbits(
    automorphisms: list[Permutation],
) -> tuple[list[int], list[list[Exponent]], dict[Exponent, int]]:
    unseen = set(weak_compositions(2, 8))
    labelled: list[tuple[int, list[Exponent]]] = []
    while unseen:
        seed = min(unseen)
        orbit = sorted({move_exponent(seed, permutation) for permutation in automorphisms})
        support = [index for index, power in enumerate(seed) if power]
        distance = 0 if len(support) == 1 else bit_distance(support[0], support[1])
        labelled.append((distance, orbit))
        unseen.difference_update(orbit)
    labelled.sort(key=lambda item: item[0])
    distances = [distance for distance, _ in labelled]
    orbits = [orbit for _, orbit in labelled]
    lookup = {exponent: index for index, orbit in enumerate(orbits) for exponent in orbit}
    return distances, orbits, lookup


def quartic_laplacian(orbit: list[Exponent]) -> Polynomial:
    polynomial: Polynomial = {}
    for exponent in orbit:
        for coordinate in range(8):
            derivative = derivative_two(exponent, coordinate, coordinate)
            if derivative is not None:
                coefficient, reduced = derivative
                polynomial[reduced] = polynomial.get(reduced, Fraction(0)) + coefficient
    return {key: value for key, value in polynomial.items() if value}


def project_quadratic(
    polynomial: Polynomial, orbits: list[list[Exponent]], lookup: dict[Exponent, int]
) -> Vector:
    if any(exponent not in lookup for exponent in polynomial):
        raise AssertionError("quartic Laplacian produced a nonquadratic monomial")
    row: Vector = []
    for orbit in orbits:
        values = {polynomial.get(exponent, Fraction(0)) for exponent in orbit}
        if len(values) != 1:
            raise AssertionError("quadratic contraction is not invariant")
        row.append(values.pop())
    return row


def distance_matrix(distance: int) -> list[list[Fraction]]:
    return [
        [Fraction(int(bit_distance(left, right) == distance)) for right in range(8)]
        for left in range(8)
    ]


def matrix_product(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[row][mid] * right[mid][column] for mid in range(8)), Fraction(0)) for column in range(8)]
        for row in range(8)
    ]


def distance_algebra(
    automorphisms: list[Permutation], audit: Audit
) -> dict[str, Any]:
    matrices = [distance_matrix(distance) for distance in range(4)]
    flattened = [[entry for row in matrix for entry in row] for matrix in matrices]
    rank = len(rref_basis(flattened))
    audit.check(
        "distance matrices have full quadratic rank",
        rank == TEST_ORACLE_FULL_QUADRATIC_RANK,
        rank,
        TEST_ORACLE_FULL_QUADRATIC_RANK,
        "quadratic",
    )
    invariant = all(
        matrices[distance][permutation[left]][permutation[right]] == matrices[distance][left][right]
        for distance in range(4)
        for permutation in automorphisms
        for left in range(8)
        for right in range(8)
    )
    audit.check("distance matrices are Aut(Q3) invariant", invariant, invariant, True, "quadratic")

    multiplication: dict[str, list[str]] = {}
    for left_distance in range(4):
        for right_distance in range(4):
            product = matrix_product(matrices[left_distance], matrices[right_distance])
            coefficients: list[Fraction] = []
            for distance in range(4):
                representative = next(
                    (left, right)
                    for left in range(8)
                    for right in range(8)
                    if bit_distance(left, right) == distance
                )
                coefficients.append(product[representative[0]][representative[1]])
            reconstructed = [
                [
                    sum(
                        (coefficients[distance] * matrices[distance][row][column] for distance in range(4)),
                        Fraction(0),
                    )
                    for column in range(8)
                ]
                for row in range(8)
            ]
            audit.check(
                f"distance algebra closure A{left_distance}A{right_distance}",
                product == reconstructed,
                product == reconstructed,
                True,
                "quadratic",
            )
            multiplication[f"A{left_distance}A{right_distance}"] = [str(value) for value in coefficients]
    return {"rank": rank, "multiplication_coefficients_A0_to_A3": multiplication}


def counterterm_audit(automorphisms: list[Permutation], audit: Audit) -> dict[str, Any]:
    labels, orbits, lookup = partition_quartic_orbits(automorphisms)
    label_index = {label: index for index, label in enumerate(labels)}
    table = build_bilinear_table(orbits, lookup)

    p_g = [Fraction(0)] * len(labels)
    p_lambda = [Fraction(0)] * len(labels)
    p_g[label_index["O4"]] = Fraction(1, 4)
    p_lambda[label_index["O4"]] = Fraction(3, 4)
    p_lambda[label_index["O31_d1"]] = Fraction(-1, 2)
    p_lambda[label_index["O22_d1"]] = Fraction(1, 2)

    b_gg = bilinear_combine(p_g, p_g, table)
    b_gl = [2 * value for value in bilinear_combine(p_g, p_lambda, table)]
    b_ll = bilinear_combine(p_lambda, p_lambda, table)
    one_loop = {label: (b_gg[index], b_gl[index], b_ll[index]) for index, label in enumerate(labels)}

    basis = rref_basis([p_g, p_lambda])
    closure_ranks = [len(basis)]
    while True:
        generated = [
            bilinear_combine(basis[left], basis[right], table)
            for left in range(len(basis))
            for right in range(left, len(basis))
        ]
        enlarged = rref_basis([*basis, *generated])
        closure_ranks.append(len(enlarged))
        if len(enlarged) == len(basis):
            break
        basis = enlarged

    quadratic_distances, quadratic_basis, quadratic_lookup = quadratic_orbits(automorphisms)
    contraction_rows = [
        project_quadratic(quartic_laplacian(orbit), quadratic_basis, quadratic_lookup) for orbit in orbits
    ]
    lambda_contraction = [
        sum((p_lambda[index] * contraction_rows[index][column] for index in range(len(labels))), Fraction(0))
        for column in range(len(quadratic_basis))
    ]
    bare_quadratic_rank = len(
        rref_basis([contraction_rows[label_index["O4"]], lambda_contraction])
    )
    full_quadratic_rank = len(rref_basis(contraction_rows))

    audit.check(
        "quartic invariant dimension",
        len(labels) == TEST_ORACLE_QUARTIC_DIMENSION,
        len(labels),
        TEST_ORACLE_QUARTIC_DIMENSION,
        "counterterm",
    )
    audit.check(
        "quartic orbit partition",
        sum(len(orbit) for orbit in orbits) == TEST_ORACLE_QUARTIC_MONOMIAL_COUNT,
        sum(len(orbit) for orbit in orbits),
        TEST_ORACLE_QUARTIC_MONOMIAL_COUNT,
        "counterterm",
    )
    audit.check(
        "quartic orbit labels are unique",
        len(labels) == len(set(labels)),
        len(set(labels)),
        len(labels),
        "counterterm",
    )
    audit.check(
        "closure ranks",
        closure_ranks == TEST_ORACLE_CLOSURE_RANKS,
        closure_ranks,
        TEST_ORACLE_CLOSURE_RANKS,
        "counterterm",
    )
    for label, expected in TEST_ORACLE_ONE_LOOP.items():
        actual = one_loop[label]
        audit.check(f"one-loop coefficient {label}", actual == expected, actual, expected, "counterterm")
    unexpected = {
        label: values
        for label, values in one_loop.items()
        if any(values) and label not in TEST_ORACLE_ONE_LOOP
    }
    audit.check("one-loop support complete", not unexpected, unexpected, {}, "counterterm")
    audit.check(
        "quadratic invariant orbit distances",
        quadratic_distances == TEST_ORACLE_QUADRATIC_DISTANCES,
        quadratic_distances,
        TEST_ORACLE_QUADRATIC_DISTANCES,
        "quadratic",
    )
    audit.check(
        "quadratic monomial orbit partition",
        sum(len(orbit) for orbit in quadratic_basis) == TEST_ORACLE_QUADRATIC_MONOMIAL_COUNT,
        sum(len(orbit) for orbit in quadratic_basis),
        TEST_ORACLE_QUADRATIC_MONOMIAL_COUNT,
        "quadratic",
    )
    audit.check(
        "bare Wick quadratic rank",
        bare_quadratic_rank == TEST_ORACLE_BARE_QUADRATIC_RANK,
        bare_quadratic_rank,
        TEST_ORACLE_BARE_QUADRATIC_RANK,
        "quadratic",
    )
    audit.check(
        "full invariant quadratic rank",
        full_quadratic_rank == TEST_ORACLE_FULL_QUADRATIC_RANK,
        full_quadratic_rank,
        TEST_ORACLE_FULL_QUADRATIC_RANK,
        "quadratic",
    )

    return {
        "labels": labels,
        "orbit_sizes": {label: len(orbits[index]) for index, label in enumerate(labels)},
        "one_loop": one_loop,
        "closure_ranks": closure_ranks,
        "bare_quadratic_rank": bare_quadratic_rank,
        "full_quadratic_rank": full_quadratic_rank,
        "quadratic_orbit_sizes": {
            str(distance): len(quadratic_basis[index]) for index, distance in enumerate(quadratic_distances)
        },
    }


def shift_loop(loop: tuple[int, ...], amount: int) -> tuple[int, ...]:
    period = len(loop)
    return tuple(loop[(time + amount) % period] for time in range(period))


def reflect_loop(loop: tuple[int, ...]) -> tuple[int, ...]:
    period = len(loop)
    return tuple(loop[(-time) % period] for time in range(period))


def parity_loop(loop: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(-value for value in loop)


def reflection_fixture(audit: Audit) -> tuple[dict[str, Any], dict[str, Any]]:
    period = 12
    ratio = Fraction(1, 2)
    times = list(range(period // 2 + 1))
    matrix = [
        [ratio ** (left + right) + ratio ** (period - left - right) for right in times]
        for left in times
    ]
    first = [ratio**time for time in times]
    second = [ratio ** (period // 2 - time) for time in times]
    factorized = [
        [first[left] * first[right] + second[left] * second[right] for right in range(len(times))]
        for left in range(len(times))
    ]
    audit.check("thermal RP Gram factorization", matrix == factorized, matrix == factorized, True, "os")
    rank = len(rref_basis(matrix))
    audit.check(
        "thermal RP Gram rank",
        rank == TEST_ORACLE_OS_GRAM_RANK,
        rank,
        TEST_ORACLE_OS_GRAM_RANK,
        "os",
    )
    hostile_indices = (1, 2)
    hostile = [
        [first[left] * first[right] - second[left] * second[right] for right in hostile_indices]
        for left in hostile_indices
    ]
    hostile_determinant = hostile[0][0] * hostile[1][1] - hostile[0][1] * hostile[1][0]
    audit.check(
        "negative reflected factor hostile",
        hostile_determinant < 0,
        hostile_determinant,
        "<0",
        "hostile",
    )

    loop = tuple(time * time - 3 * time for time in range(period))
    shift_a = 3
    shift_b = 5
    relations = {
        "reflection_involution": reflect_loop(reflect_loop(loop)) == loop,
        "translation_group": shift_loop(shift_loop(loop, shift_a), shift_b)
        == shift_loop(loop, shift_a + shift_b),
        "parity_translation_commute": parity_loop(shift_loop(loop, shift_a))
        == shift_loop(parity_loop(loop), shift_a),
        "parity_reflection_commute": parity_loop(reflect_loop(loop)) == reflect_loop(parity_loop(loop)),
        "reflection_translation_inverse": reflect_loop(shift_loop(loop, shift_a))
        == shift_loop(reflect_loop(loop), -shift_a),
    }
    for name, result in relations.items():
        audit.check(name.replace("_", " "), result, result, True, "os_relations")
    return (
        {"period": period, "ratio": str(ratio), "rank": rank, "hostile_det": str(hostile_determinant)},
        relations,
    )


def source_cusp_fixture(audit: Audit) -> dict[str, Any]:
    rho = Fraction(9, 4)
    root_rho = Fraction(3, 2)
    hbar = Fraction(2)
    chi = Fraction(3)
    volume = Fraction(64)
    source = Fraction(2, 5)
    excess = hbar**2 / (4 * chi * volume * rho)
    finite_upper = excess / (8 * volume) - source * root_rho / 8
    limit_upper = -source * root_rho / 8
    audit.check("rho root derived", root_rho**2 == rho, root_rho**2, rho, "ground_cusp")
    audit.check("doublet excess positive", excess > 0, excess, ">0", "ground_cusp")
    audit.check(
        "finite trial density upper tends to cusp line",
        finite_upper - limit_upper == excess / (8 * volume),
        finite_upper - limit_upper,
        excess / (8 * volume),
        "ground_cusp",
    )
    audit.check("cusp right slope", -root_rho / 8 < 0, -root_rho / 8, "<0", "ground_cusp")
    audit.check("cusp left slope", root_rho / 8 > 0, root_rho / 8, ">0", "ground_cusp")
    return {
        "rho_star": str(rho),
        "sqrt_rho_star": str(root_rho),
        "doublet_excess_bound": str(excess),
        "finite_density_upper": str(finite_upper),
        "limit_density_upper": str(limit_upper),
        "right_derivative_upper": str(-root_rho / 8),
        "left_derivative_lower": str(root_rho / 8),
    }


def gns_fixture(audit: Audit) -> dict[str, Any]:
    hbar = Fraction(5, 3)
    chi = Fraction(7, 4)
    sizes = [16, 256, 4096]
    gap_upper_bounds = []
    for size in sizes:
        variance = size * math.isqrt(size)
        gap_upper_bounds.append(hbar**2 * size / (2 * chi * variance))
    audit.check(
        "superlinear variance gap bounds decrease",
        all(left > right for left, right in zip(gap_upper_bounds, gap_upper_bounds[1:])),
        gap_upper_bounds,
        "strictly decreasing",
        "gns",
    )
    audit.check(
        "superlinear variance gap diagnostic small",
        gap_upper_bounds[-1] < Fraction(1, 50),
        gap_upper_bounds[-1],
        "<1/50",
        "gns",
    )

    mass_parameter = Fraction(-2)
    quartic = Fraction(3)
    locking = Fraction(1, 5)
    ordered_amplitude_squared = -mass_parameter / quartic
    levels = [
        -2 * mass_parameter + locking * ordered_amplitude_squared * walsh_level
        for walsh_level in (0, 2, 4, 6)
    ]
    audit.check(
        "ordered tangent minimum",
        min(levels) == -2 * mass_parameter > 0,
        min(levels),
        -2 * mass_parameter,
        "gns",
    )
    coupling = Fraction(7, 10)
    lifted_levels = [level + 2 * coupling * energy for level in levels for energy in (0, 1, 2)]
    audit.check(
        "nonnegative dispersion preserves tangent minimum",
        min(lifted_levels) == -2 * mass_parameter,
        min(lifted_levels),
        -2 * mass_parameter,
        "gns",
    )
    return {
        "variance_sizes": sizes,
        "gap_upper_bounds": [str(value) for value in gap_upper_bounds],
        "ordered_tangent_levels": [str(value) for value in levels],
    }


def reference_fixture(audit: Audit) -> dict[str, Any]:
    beta = 1.0
    weights = [3.0, 2.0, 1.0]
    total_weight = math.fsum(weights)
    rho = [weight / total_weight for weight in weights]
    hamiltonian = [-math.log(weight) for weight in weights]
    sigma = [0.5, 0.25, 0.25]

    def free_energy(state: list[float], energy: list[float]) -> float:
        return math.fsum(probability * value for probability, value in zip(state, energy)) + math.fsum(
            probability * math.log(probability) for probability in state
        ) / beta

    relative_entropy = math.fsum(
        probability * math.log(probability / reference)
        for probability, reference in zip(sigma, rho)
    )
    difference = free_energy(sigma, hamiltonian) - free_energy(rho, hamiltonian)
    audit.check(
        "Gibbs variational relative entropy",
        math.isclose(difference, relative_entropy, rel_tol=0.0, abs_tol=2e-15),
        difference,
        relative_entropy,
        "reference",
    )
    audit.check("Gibbs comparison nonnegative", difference > 0, difference, ">0", "reference")
    scalar_shift = 17.0
    shifted_hamiltonian = [energy + scalar_shift for energy in hamiltonian]
    shifted_difference = free_energy(sigma, shifted_hamiltonian) - free_energy(rho, shifted_hamiltonian)
    audit.check(
        "scalar-shift invariant free-energy difference",
        math.isclose(shifted_difference, difference, rel_tol=0.0, abs_tol=4e-15),
        shifted_difference,
        difference,
        "reference",
    )
    ground_difference = math.fsum(
        probability * energy for probability, energy in zip(sigma, hamiltonian)
    ) - min(hamiltonian)
    audit.check("ground variational comparison", ground_difference >= 0, ground_difference, ">=0", "reference")
    shifted_ground_difference = math.fsum(
        probability * energy for probability, energy in zip(sigma, shifted_hamiltonian)
    ) - min(shifted_hamiltonian)
    audit.check(
        "scalar-shift invariant ground difference",
        math.isclose(shifted_ground_difference, ground_difference, rel_tol=0.0, abs_tol=4e-15),
        shifted_ground_difference,
        ground_difference,
        "reference",
    )
    self_difference = free_energy(rho, hamiltonian) - free_energy(rho, hamiltonian)
    audit.check(
        "equilibrium compared with itself is not strict",
        self_difference == 0.0,
        self_difference,
        0.0,
        "reference",
    )
    return {
        "relative_entropy": relative_entropy,
        "free_energy_difference": difference,
        "ground_trial_difference": ground_difference,
    }


def parent_result_passed(payload: dict[str, Any]) -> tuple[bool, str]:
    """Accept both historical and current assertion-summary schemas."""

    historical = payload.get("assertion_summary")
    if isinstance(historical, dict):
        passed = historical.get("passed")
        total = historical.get("total")
        return passed == total and isinstance(total, int) and total > 0, f"historical {passed}/{total}"
    assertions = payload.get("assertions")
    if isinstance(assertions, dict):
        passed = assertions.get("passed")
        total = assertions.get("total")
        verdict = payload.get("verdict")
        return verdict == "PASS" and passed == total and isinstance(total, int) and total > 0, f"{verdict} {passed}/{total}"
    return False, "unrecognized assertion schema"


def provenance_and_scope_audit(audit: Audit) -> tuple[dict[str, Any], str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("manifest candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "provenance")
    audit.check("manifest result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "provenance")
    audit.check("manifest exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "provenance")
    audit.check("manifest negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], list(NEGATIVE_IDS), "provenance")
    expected_script = str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/")
    audit.check("manifest independent script", manifest["verification"]["independent"] == expected_script, manifest["verification"]["independent"], expected_script, "provenance")

    for path, exploration_id, candidate_id, result_id in PARENT_RESULTS:
        audit.check(f"parent exists {path.parent.name}", path.is_file(), path, "file", "provenance")
        payload = json.loads(path.read_text(encoding="utf-8"))
        passed, detail = parent_result_passed(payload)
        audit.check(f"parent assertions pass {path.parent.name}", passed, detail, "positive complete assertion summary", "provenance")
        audit.check(f"parent exploration {path.parent.name}", payload.get("exploration_id") == exploration_id, payload.get("exploration_id"), exploration_id, "provenance")
        audit.check(f"parent candidate {path.parent.name}", payload.get("candidate_id") == candidate_id, payload.get("candidate_id"), candidate_id, "provenance")
        audit.check(f"parent result {path.parent.name}", payload.get("result_id") == result_id, payload.get("result_id"), result_id, "provenance")

    required_phrases = (
        "phasewise, not common",
        "separable unital commutative C-star algebra",
        "`P3`",
        "`P-star`",
        "post-hoc direct sum",
        "strict zero-temperature source cusp",
        "19-dimensional",
        "necessary, not sufficient",
        "state-vector Poincare gap",
        "finite spatial volume",
        "same Hamiltonian",
        "not physical empty space",
    )
    for phrase in required_phrases:
        audit.check(f"certificate phrase {phrase}", phrase in certificate, phrase in certificate, True, "certificate")

    true_scope = (
        "phasewise_periodic_OS_reconstruction",
        "phasewise_stochastically_positive_beta_KMS",
        "parity_unitary_equivalence",
        "fixed_lattice_zero_temperature_source_cusp",
        "distinct_locally_normal_time_zero_ground_tangent_candidates",
        "full_AutQ3_Z2_quartic_invariant_dimension_19",
        "one_loop_closure_reaches_full_quartic_invariant_space",
        "full_quadratic_invariant_dimension_4",
        "same_H_finite_volume_finite_regulator_reference_identity",
    )
    false_scope = (
        "common_state_independent_real_time_dynamics",
        "common_alpha_KMS_identification",
        "distinct_algebraic_ground_states",
        "broken_sector_GNS_gap",
        "enlarged_counterterm_continuum_limit",
        "physical_empty_space_reference",
        "below_physical_empty_space",
        "C6_advanced",
        "CP1_complete",
        "Sector_A_complete",
        "Pre_A_complete",
    )
    for key in true_scope:
        audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    return manifest, certificate


def build_payload() -> dict[str, Any]:
    audit = Audit()
    automorphisms = enumerate_graph_automorphisms()
    audit.check(
        "Q3 edge count",
        len(Q3_EDGES) == TEST_ORACLE_Q3_EDGE_COUNT,
        len(Q3_EDGES),
        TEST_ORACLE_Q3_EDGE_COUNT,
        "q3",
    )
    audit.check(
        "Q3 automorphism count",
        len(automorphisms) == TEST_ORACLE_AUTOMORPHISM_COUNT,
        len(automorphisms),
        TEST_ORACLE_AUTOMORPHISM_COUNT,
        "q3",
    )
    quartic_monomial_count = sum(1 for _ in weak_compositions(4, 8))
    audit.check(
        "degree-four recursive composition count",
        quartic_monomial_count == TEST_ORACLE_QUARTIC_MONOMIAL_COUNT,
        quartic_monomial_count,
        TEST_ORACLE_QUARTIC_MONOMIAL_COUNT,
        "q3",
    )

    reflection, os_relations = reflection_fixture(audit)
    cusp = source_cusp_fixture(audit)
    counterterm = counterterm_audit(automorphisms, audit)
    algebra = distance_algebra(automorphisms, audit)
    gns = gns_fixture(audit)
    reference = reference_fixture(audit)
    manifest, _ = provenance_and_scope_audit(audit)

    serial_one_loop = {
        label: [str(value) for value in values]
        for label, values in counterterm["one_loop"].items()
        if any(values)
    }
    script_path = str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/")
    return {
        "schema": f"tect/{SLUG}-independent/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": NEXT_GATE,
        "negative_ids": list(NEGATIVE_IDS),
        "claim_bearing": False,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "derived": {
            "reflection_positive_fixture": reflection,
            "zero_temperature_cusp_fixture": cusp,
            "quartic_invariant_labels": counterterm["labels"],
            "quartic_orbit_sizes": counterterm["orbit_sizes"],
            "quartic_closure_ranks": counterterm["closure_ranks"],
            "one_loop_coefficients_g2_gl_l2": serial_one_loop,
            "bare_quadratic_rank": counterterm["bare_quadratic_rank"],
            "full_quadratic_rank": counterterm["full_quadratic_rank"],
            "gns_fixture": gns,
            "reference_fixture": reference,
        },
        "independent_audit": {
            "automorphism_method": "all 8! vertex permutations filtered by Q3 edge preservation",
            "automorphism_count": len(automorphisms),
            "quartic_monomial_method": "recursive weak compositions of degree four into eight slots",
            "linear_algebra": "fractions.Fraction with local reduced-row-basis elimination",
            "quadratic_orbit_sizes": counterterm["quadratic_orbit_sizes"],
            "distance_algebra": algebra,
            "time_reflection_parity_relations": os_relations,
        },
        "scope": manifest["scope"],
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "script": script_path,
        },
        "verdict": "PASS",
        "boundary": manifest["no_overclaim"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    assertions = payload["assertions"]
    print(f"EXP-000790 INDEPENDENT PASS {assertions['passed']}/{assertions['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
