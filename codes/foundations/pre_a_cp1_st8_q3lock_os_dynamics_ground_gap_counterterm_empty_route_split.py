#!/usr/bin/env python3
"""Primary exact verifier for the ordered EXP-000790 route split.

The analytic proof is the accompanying certificate.  This executable checks
finite reflection-positive sentinels, the zero-temperature source-cusp
normalization, the complete Aut(Q3)-invariant quartic counterterm closure, the
GNS variance falsifier, and scalar-shift-invariant reference identities.  It
does not numerically prove an infinite-volume dynamics, algebraic ground state,
GNS gap, continuum limit, or physical vacuum.
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
from typing import Any, Iterable

import numpy as np
import sympy as sp


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
PARENT_780 = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split/result.json"
PARENT_781 = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-phase-boundary-route-split/result.json"
PARENT_782 = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split/result.json"
PARENT_789 = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-integrated-pre-a-cp1-st8-q3lock-ground-equal-time-order-gap-continuum-counterterm-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-primary-{SLUG}/result.json"

# Clearly labelled theorem-regression oracles.  Every actual coefficient is
# recomputed below from the Q3 graph and Hessian-trace operation.
TEST_ORACLE_CLOSURE_RANKS = [2, 4, 9, 19, 19]
TEST_ORACLE_ONE_LOOP = {
    "O4": (Fraction(9), Fraction(54), Fraction(195, 2)),
    "O31_d1": (Fraction(0), Fraction(-18), Fraction(-72)),
    "O22_d1": (Fraction(0), Fraction(12), Fraction(71)),
    "O211_1_1_2": (Fraction(0), Fraction(0), Fraction(18)),
    "O211_1_2_1": (Fraction(0), Fraction(0), Fraction(-6)),
    "O22_d2": (Fraction(0), Fraction(0), Fraction(4)),
}


def portable_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def parent_result_passed(payload: dict[str, Any]) -> bool:
    """Accept both historical and current result schemas without trusting prose."""
    summary = payload.get("assertion_summary")
    if isinstance(summary, dict):
        return summary.get("passed") == summary.get("total") and bool(summary.get("total"))
    assertions = payload.get("assertions")
    return (
        payload.get("verdict") == "PASS"
        and isinstance(assertions, dict)
        and assertions.get("passed") == assertions.get("total")
        and bool(assertions.get("total"))
    )


def parent_assertion_detail(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact provenance summary without copying every parent row."""
    summary = payload.get("assertion_summary")
    if not isinstance(summary, dict):
        summary = payload.get("assertions") if isinstance(payload.get("assertions"), dict) else {}
    return {
        "passed": summary.get("passed"),
        "total": summary.get("total"),
        "schema": payload.get("schema"),
        "verdict": payload.get("verdict"),
    }


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


Exponent = tuple[int, ...]
Polynomial = dict[Exponent, Fraction]


def vertices() -> list[tuple[int, int, int]]:
    return [(a, b, c) for a in range(2) for b in range(2) for c in range(2)]


VERTICES = vertices()


def hamming(left: int, right: int) -> int:
    return sum(a != b for a, b in zip(VERTICES[left], VERTICES[right]))


def automorphisms() -> list[tuple[int, ...]]:
    maps: set[tuple[int, ...]] = set()
    for coordinate_permutation in itertools.permutations(range(3)):
        for translation in VERTICES:
            image: list[int] = []
            for value in VERTICES:
                transformed = tuple(value[coordinate_permutation[i]] ^ translation[i] for i in range(3))
                image.append(VERTICES.index(transformed))
            maps.add(tuple(image))
    return sorted(maps)


AUTOMORPHISMS = automorphisms()


def degree_four_monomials() -> list[Exponent]:
    output: list[Exponent] = []
    for bars in itertools.combinations(range(11), 7):
        positions = (-1,) + bars + (11,)
        output.append(tuple(positions[i + 1] - positions[i] - 1 for i in range(8)))
    return output


def permute_exponent(exponent: Exponent, permutation: tuple[int, ...]) -> Exponent:
    result = [0] * 8
    for source, target in enumerate(permutation):
        result[target] = exponent[source]
    return tuple(result)


def orbit_label(exponent: Exponent) -> str:
    support = [index for index, power in enumerate(exponent) if power]
    powers = sorted((exponent[index] for index in support), reverse=True)
    if powers == [4]:
        return "O4"
    if powers == [3, 1]:
        cubic = next(index for index in support if exponent[index] == 3)
        linear = next(index for index in support if exponent[index] == 1)
        return f"O31_d{hamming(cubic, linear)}"
    if powers == [2, 2]:
        return f"O22_d{hamming(support[0], support[1])}"
    if powers == [2, 1, 1]:
        doubled = next(index for index in support if exponent[index] == 2)
        singles = [index for index in support if exponent[index] == 1]
        a, b = sorted((hamming(doubled, singles[0]), hamming(doubled, singles[1])))
        c = hamming(singles[0], singles[1])
        return f"O211_{a}_{b}_{c}"
    if powers == [1, 1, 1, 1]:
        distances = sorted(hamming(left, right) for left, right in itertools.combinations(support, 2))
        return "O1111_" + "_".join(str(value) for value in distances)
    raise AssertionError(exponent)


def invariant_orbits() -> tuple[list[str], list[list[Exponent]], dict[Exponent, int]]:
    unseen = set(degree_four_monomials())
    labelled: list[tuple[str, list[Exponent]]] = []
    while unseen:
        representative = min(unseen)
        orbit = sorted({permute_exponent(representative, permutation) for permutation in AUTOMORPHISMS})
        label = orbit_label(representative)
        if any(orbit_label(item) != label for item in orbit):
            raise AssertionError(f"nonconstant orbit label {label}")
        labelled.append((label, orbit))
        unseen.difference_update(orbit)
    labelled.sort(key=lambda item: item[0])
    labels = [item[0] for item in labelled]
    orbits = [item[1] for item in labelled]
    lookup = {monomial: index for index, orbit in enumerate(orbits) for monomial in orbit}
    return labels, orbits, lookup


def second_derivative(exponent: Exponent, left: int, right: int) -> tuple[Fraction, Exponent] | None:
    powers = list(exponent)
    if left == right:
        coefficient = powers[left] * (powers[left] - 1)
        if coefficient == 0:
            return None
        powers[left] -= 2
    else:
        coefficient = powers[left] * powers[right]
        if coefficient == 0:
            return None
        powers[left] -= 1
        powers[right] -= 1
    return Fraction(coefficient), tuple(powers)


def orbit_hessians(orbits: list[list[Exponent]]) -> list[dict[tuple[int, int], Polynomial]]:
    result: list[dict[tuple[int, int], Polynomial]] = []
    for orbit in orbits:
        hessian: dict[tuple[int, int], Polynomial] = {}
        for left in range(8):
            for right in range(8):
                polynomial: Polynomial = {}
                for exponent in orbit:
                    derivative = second_derivative(exponent, left, right)
                    if derivative is not None:
                        coefficient, reduced = derivative
                        polynomial[reduced] = polynomial.get(reduced, Fraction(0)) + coefficient
                if polynomial:
                    hessian[(left, right)] = polynomial
        result.append(hessian)
    return result


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for first, first_coefficient in left.items():
        for second, second_coefficient in right.items():
            exponent = tuple(a + b for a, b in zip(first, second))
            output[exponent] = output.get(exponent, Fraction(0)) + first_coefficient * second_coefficient
    return {key: value for key, value in output.items() if value}


def add_scaled(target: Polynomial, source: Polynomial, scale: Fraction) -> None:
    for exponent, coefficient in source.items():
        target[exponent] = target.get(exponent, Fraction(0)) + scale * coefficient
        if target[exponent] == 0:
            del target[exponent]


def bilinear_orbit_table(
    labels: list[str], orbits: list[list[Exponent]], lookup: dict[Exponent, int]
) -> list[list[list[Fraction]]]:
    hessians = orbit_hessians(orbits)
    size = len(labels)
    table = [[[Fraction(0) for _ in range(size)] for _ in range(size)] for _ in range(size)]
    for left in range(size):
        for right in range(left, size):
            polynomial: Polynomial = {}
            for key in set(hessians[left]).intersection(hessians[right]):
                add_scaled(polynomial, multiply(hessians[left][key], hessians[right][key]), Fraction(1))
            coefficients: list[Fraction | None] = [None] * size
            for exponent, coefficient in polynomial.items():
                orbit_index = lookup[exponent]
                previous = coefficients[orbit_index]
                if previous is None:
                    coefficients[orbit_index] = coefficient
                elif previous != coefficient:
                    raise AssertionError(f"noninvariant bilinear coefficient {labels[orbit_index]}")
            vector = [value if value is not None else Fraction(0) for value in coefficients]
            table[left][right] = vector
            table[right][left] = vector
    return table


def combine_bilinear(
    left: list[Fraction], right: list[Fraction], table: list[list[list[Fraction]]]
) -> list[Fraction]:
    size = len(left)
    output = [Fraction(0) for _ in range(size)]
    for i, a in enumerate(left):
        if not a:
            continue
        for j, b in enumerate(right):
            if not b:
                continue
            for k, coefficient in enumerate(table[i][j]):
                output[k] += a * b * coefficient
    return output


def rational_row_basis(rows: Iterable[list[Fraction]]) -> list[list[Fraction]]:
    rows = [list(row) for row in rows if any(row)]
    if not rows:
        return []
    matrix = sp.Matrix([[sp.Rational(value.numerator, value.denominator) for value in row] for row in rows])
    rref, _ = matrix.rref()
    basis: list[list[Fraction]] = []
    for line in range(rref.rows):
        row = [Fraction(int(value.p), int(value.q)) for value in rref.row(line)]
        if any(row):
            basis.append(row)
    return basis


def counterterm_closure() -> dict[str, Any]:
    labels, orbits, lookup = invariant_orbits()
    label_index = {label: index for index, label in enumerate(labels)}
    table = bilinear_orbit_table(labels, orbits, lookup)
    p_g = [Fraction(0)] * len(labels)
    p_lambda = [Fraction(0)] * len(labels)
    p_g[label_index["O4"]] = Fraction(1, 4)
    p_lambda[label_index["O4"]] = Fraction(3, 4)
    p_lambda[label_index["O31_d1"]] = Fraction(-1, 2)
    p_lambda[label_index["O22_d1"]] = Fraction(1, 2)

    b_gg = combine_bilinear(p_g, p_g, table)
    b_gl = [2 * value for value in combine_bilinear(p_g, p_lambda, table)]
    b_ll = combine_bilinear(p_lambda, p_lambda, table)
    one_loop = {label: (b_gg[index], b_gl[index], b_ll[index]) for index, label in enumerate(labels)}

    basis = rational_row_basis([p_g, p_lambda])
    ranks = [len(basis)]
    while True:
        generated = [combine_bilinear(basis[i], basis[j], table) for i in range(len(basis)) for j in range(i, len(basis))]
        enlarged = rational_row_basis([*basis, *generated])
        ranks.append(len(enlarged))
        if len(enlarged) == len(basis):
            break
        basis = enlarged

    # Laplacians of all invariant quartics, represented by the four quadratic
    # orbit coefficients Q0,Q1,Q2,Q3.
    quadratic_rows: list[list[Fraction]] = []
    for orbit in orbits:
        polynomial: Polynomial = {}
        for exponent in orbit:
            for index in range(8):
                derivative = second_derivative(exponent, index, index)
                if derivative is not None:
                    coefficient, reduced = derivative
                    polynomial[reduced] = polynomial.get(reduced, Fraction(0)) + coefficient
        row = [Fraction(0)] * 4
        representatives: dict[int, Fraction] = {}
        for exponent, coefficient in polynomial.items():
            support = [index for index, power in enumerate(exponent) if power]
            distance = 0 if len(support) == 1 else hamming(support[0], support[1])
            if distance in representatives and representatives[distance] != coefficient:
                raise AssertionError("noninvariant quadratic contraction")
            representatives[distance] = coefficient
        for distance, coefficient in representatives.items():
            row[distance] = coefficient
        quadratic_rows.append(row)
    full_quadratic_rank = len(rational_row_basis(quadratic_rows))
    bare_quadratic_rank = len(rational_row_basis([quadratic_rows[label_index["O4"]],
                                                   [sum(p_lambda[i] * quadratic_rows[i][j] for i in range(len(labels))) for j in range(4)]]))

    return {
        "labels": labels,
        "orbit_sizes": {label: len(orbits[index]) for index, label in enumerate(labels)},
        "one_loop": one_loop,
        "closure_ranks": ranks,
        "full_quadratic_rank": full_quadratic_rank,
        "bare_quadratic_rank": bare_quadratic_rank,
    }


def reflection_fixture(audit: Audit) -> dict[str, Any]:
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
        [first[i] * first[j] + second[i] * second[j] for j in range(len(times))]
        for i in range(len(times))
    ]
    audit.check("thermal RP Gram factorization", matrix == factorized, matrix, "u u^T+r^(N/2)v v^T", "os")
    rational_matrix = sp.Matrix([[sp.Rational(value.numerator, value.denominator) for value in row] for row in matrix])
    audit.check("thermal RP Gram rank", rational_matrix.rank() == 2, rational_matrix.rank(), 2, "os")
    hostile = sp.Matrix(
        [
            [
                sp.Rational((first[i] * first[j] - second[i] * second[j]).numerator,
                            (first[i] * first[j] - second[i] * second[j]).denominator)
                for j in (1, 2)
            ]
            for i in (1, 2)
        ]
    )
    audit.check("negative reflected factor hostile", hostile.det() < 0, hostile.det(), "<0", "hostile")
    return {"period": period, "ratio": str(ratio), "rank": rational_matrix.rank(), "hostile_det": str(hostile.det())}


def source_cusp_fixture(audit: Audit) -> dict[str, Any]:
    rho = Fraction(9, 4)
    root_rho = Fraction(3, 2)
    hbar = Fraction(2)
    chi = Fraction(3)
    volume = Fraction(64)
    source = Fraction(2, 5)
    excess = hbar**2 / (4 * chi * volume * rho)
    density_upper = excess / (8 * volume) - source * root_rho / 8
    limit_upper = -source * root_rho / 8
    audit.check("rho root derived", root_rho**2 == rho, root_rho**2, rho, "ground_cusp")
    audit.check("doublet excess positive", excess > 0, excess, ">0", "ground_cusp")
    audit.check("finite trial density upper tends to cusp line", density_upper > limit_upper, density_upper - limit_upper, excess / (8 * volume), "ground_cusp")
    audit.check("cusp right slope", -root_rho / 8 < 0, -root_rho / 8, "<0", "ground_cusp")
    audit.check("cusp left slope", root_rho / 8 > 0, root_rho / 8, ">0", "ground_cusp")
    return {
        "rho_star": str(rho),
        "sqrt_rho_star": str(root_rho),
        "doublet_excess_bound": str(excess),
        "finite_density_upper": str(density_upper),
        "limit_density_upper": str(limit_upper),
        "right_derivative_upper": str(-root_rho / 8),
        "left_derivative_lower": str(root_rho / 8),
    }


def gns_fixture(audit: Audit) -> dict[str, Any]:
    hbar = Fraction(5, 3)
    chi = Fraction(7, 4)
    sizes = [16, 256, 4096]
    upper_bounds: list[Fraction] = []
    for size in sizes:
        variance = size * int(math.isqrt(size))
        upper_bounds.append(hbar**2 * size / (2 * chi * variance))
    audit.check("superlinear variance gap bounds decrease", all(a > b for a, b in zip(upper_bounds, upper_bounds[1:])), upper_bounds, "strictly decreasing", "gns")
    audit.check("superlinear variance gap diagnostic small", upper_bounds[-1] < Fraction(1, 50), upper_bounds[-1], "<1/50", "gns")

    r = Fraction(-2)
    g = Fraction(3)
    coupling = Fraction(7, 10)
    locking = Fraction(1, 5)
    x_squared = -r / g
    levels = [-2 * r + locking * x_squared * ell for ell in (0, 2, 4, 6)]
    audit.check("ordered tangent minimum", min(levels) == -2 * r > 0, min(levels), -2 * r, "gns")
    lifted_levels = [level + 2 * coupling * energy for level in levels for energy in (0, 1, 2)]
    audit.check("nonnegative dispersion preserves tangent minimum", min(lifted_levels) == -2 * r, min(lifted_levels), -2 * r, "gns")
    return {"variance_sizes": sizes, "gap_upper_bounds": [str(value) for value in upper_bounds], "ordered_tangent_levels": [str(value) for value in levels]}


def reference_fixture(audit: Audit) -> dict[str, Any]:
    beta = 1.0
    weights = np.array([3.0, 2.0, 1.0])
    rho = weights / weights.sum()
    hamiltonian = -np.log(weights)
    sigma = np.array([0.5, 0.25, 0.25])

    def free_energy(state: np.ndarray, energy: np.ndarray) -> float:
        return float(np.dot(state, energy) + np.dot(state, np.log(state)) / beta)

    relative_entropy = float(np.dot(sigma, np.log(sigma / rho)))
    difference = free_energy(sigma, hamiltonian) - free_energy(rho, hamiltonian)
    audit.check("Gibbs variational relative entropy", math.isclose(difference, relative_entropy, rel_tol=0.0, abs_tol=2e-15), difference, relative_entropy, "reference")
    audit.check("Gibbs comparison nonnegative", difference > 0, difference, ">0", "reference")
    shift = 17.0
    shifted_difference = free_energy(sigma, hamiltonian + shift) - free_energy(rho, hamiltonian + shift)
    audit.check("scalar-shift invariant free-energy difference", math.isclose(shifted_difference, difference, rel_tol=0.0, abs_tol=4e-15), shifted_difference, difference, "reference")
    ground_difference = float(np.dot(sigma, hamiltonian) - np.min(hamiltonian))
    audit.check("ground variational comparison", ground_difference >= 0, ground_difference, ">=0", "reference")
    shifted_ground_difference = float(np.dot(sigma, hamiltonian + shift) - np.min(hamiltonian + shift))
    audit.check("scalar-shift invariant ground difference", math.isclose(shifted_ground_difference, ground_difference, rel_tol=0.0, abs_tol=4e-15), shifted_ground_difference, ground_difference, "reference")
    audit.check("equilibrium compared with itself is not strict", math.isclose(free_energy(rho, hamiltonian) - free_energy(rho, hamiltonian), 0.0), 0.0, 0.0, "reference")
    return {"relative_entropy": relative_entropy, "free_energy_difference": difference, "ground_trial_difference": ground_difference}


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("Q3 automorphism count", len(AUTOMORPHISMS) == 48, len(AUTOMORPHISMS), 48, "q3")
    audit.check("degree-four monomial count", len(degree_four_monomials()) == 330, len(degree_four_monomials()), 330, "q3")
    rp = reflection_fixture(audit)
    cusp = source_cusp_fixture(audit)
    counterterm = counterterm_closure()
    audit.check("quartic invariant dimension", len(counterterm["labels"]) == 19, len(counterterm["labels"]), 19, "counterterm")
    audit.check("quartic orbit partition", sum(counterterm["orbit_sizes"].values()) == 330, sum(counterterm["orbit_sizes"].values()), 330, "counterterm")
    audit.check("closure ranks", counterterm["closure_ranks"] == TEST_ORACLE_CLOSURE_RANKS, counterterm["closure_ranks"], TEST_ORACLE_CLOSURE_RANKS, "counterterm")
    for label, expected in TEST_ORACLE_ONE_LOOP.items():
        actual = counterterm["one_loop"][label]
        audit.check(f"one-loop coefficient {label}", actual == expected, actual, expected, "counterterm")
    unexpected = {label: values for label, values in counterterm["one_loop"].items() if any(values) and label not in TEST_ORACLE_ONE_LOOP}
    audit.check("one-loop support complete", not unexpected, unexpected, {}, "counterterm")
    audit.check("bare Wick quadratic rank", counterterm["bare_quadratic_rank"] == 2, counterterm["bare_quadratic_rank"], 2, "counterterm")
    audit.check("full invariant quadratic rank", counterterm["full_quadratic_rank"] == 4, counterterm["full_quadratic_rank"], 4, "counterterm")

    gns = gns_fixture(audit)
    reference = reference_fixture(audit)

    parents = (
        (PARENT_780, "EXP-000780", "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-THERMODYNAMIC-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT-v0", "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-FREE-PERIODIC-SOURCE-PRESSURE-AND-CENTERED-GROUND-ENERGY-DENSITY"),
        (PARENT_781, "EXP-000781", "PA-CP1-ST8-Q3LOCK-EUCLIDEAN-DLR-TANGENT-STATE-AND-PHASE-BOUNDARY-ROUTE-SPLIT-v0", "PA-CP1-ST8-Q3LOCK-TEMPERED-EUCLIDEAN-DLR-TANGENT-STATES-AND-LAMBDA0-PHASE-BOUNDARY"),
        (PARENT_782, "EXP-000782", "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-FKG-INFRARED-CUSP-PHASE-ROUTE-SPLIT-v0", "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-LOW-TEMPERATURE-DLR-PHASE-AND-COLLECTIVE-SOURCE-CUSP"),
        (PARENT_789, "EXP-000789", "PA-CP1-ST8-Q3LOCK-GROUND-EQUAL-TIME-ORDER-GAP-CONTINUUM-COUNTERTERM-ROUTE-SPLIT-v0", "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-GROUND-EQUAL-TIME-LRO-APPROXIMATE-DOUBLETS-FULL-GAP-COLLAPSE-AND-CONTINUUM-BASIS-OBSTRUCTION"),
    )
    for path, exploration_id, candidate_id, result_id in parents:
        audit.check(f"parent exists {path.parent.name}", path.is_file(), path, "file", "provenance")
        parent = json.loads(path.read_text(encoding="utf-8"))
        audit.check(
            f"parent assertions pass {path.parent.name}",
            parent_result_passed(parent),
            parent_assertion_detail(parent),
            "all recorded assertions pass",
            "provenance",
        )
        audit.check(
            f"parent exploration {path.parent.name}",
            parent.get("exploration_id") == exploration_id,
            parent.get("exploration_id"),
            exploration_id,
            "provenance",
        )
        audit.check(
            f"parent candidate {path.parent.name}",
            parent.get("candidate_id") == candidate_id,
            parent.get("candidate_id"),
            candidate_id,
            "provenance",
        )
        audit.check(
            f"parent result {path.parent.name}",
            parent.get("result_id") == result_id,
            parent.get("result_id"),
            result_id,
            "provenance",
        )

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

    serial_one_loop = {
        label: [str(value) for value in values]
        for label, values in counterterm["one_loop"].items()
        if any(values)
    }
    return {
        "schema": f"tect/{SLUG}-primary/0.1",
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
            "reflection_positive_fixture": rp,
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
        "scope": manifest["scope"],
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
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
    summary = payload["assertions"]
    print(f"EXP-000790 PRIMARY PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
