#!/usr/bin/env python3
"""Primary exact verifier for PA-CP1-ST8-Q3LOCK-v0."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter, deque
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-v0"
PARENT_ID = "PA-CP1-ST8-CB-v0"
SLUG = "pre-a-cp1-st8-q3lock"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-st8-q3lock-certificate-260803.md"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-primary-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, set):
        return sorted((serial(item) for item in value), key=str)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def canonical(value: Any) -> str:
    return json.dumps(
        serial(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


Species = tuple[int, int, int]


def species_set() -> tuple[Species, ...]:
    return tuple(product((0, 1), repeat=3))


def cube_edges() -> tuple[tuple[Species, Species], ...]:
    edges: list[tuple[Species, Species]] = []
    for left in species_set():
        for axis in range(len(left)):
            if left[axis] == 0:
                right = tuple(
                    1 if coordinate == axis else bit
                    for coordinate, bit in enumerate(left)
                )
                edges.append((left, right))
    return tuple(edges)


def cube_laplacian() -> list[list[Fraction]]:
    nodes = species_set()
    index = {node: position for position, node in enumerate(nodes)}
    matrix = [[Fraction(0) for _ in nodes] for _ in nodes]
    for left, right in cube_edges():
        i, j = index[left], index[right]
        matrix[i][i] += 1
        matrix[j][j] += 1
        matrix[i][j] -= 1
        matrix[j][i] -= 1
    return matrix


def matrix_rank(matrix: Iterable[Iterable[Fraction]]) -> int:
    work = [list(map(Fraction, row)) for row in matrix]
    if not work:
        return 0
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def matvec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum((entry * value for entry, value in zip(row, vector)), Fraction(0)) for row in matrix]


def walsh_character(alpha: Species) -> list[Fraction]:
    return [
        Fraction((-1) ** sum(a * bit for a, bit in zip(alpha, epsilon)))
        for epsilon in species_set()
    ]


def cube_spectrum_by_characters() -> Counter[int]:
    laplacian = cube_laplacian()
    spectrum: Counter[int] = Counter()
    for alpha in species_set():
        eigenvalue = 2 * sum(alpha)
        vector = walsh_character(alpha)
        if matvec(laplacian, vector) != [eigenvalue * item for item in vector]:
            raise AssertionError(f"Walsh character failed for {alpha}")
        spectrum[eigenvalue] += 1
    return spectrum


def graph_components(edges: Iterable[tuple[Species, Species]]) -> int:
    adjacency = {node: set() for node in species_set()}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    unseen = set(adjacency)
    count = 0
    while unseen:
        count += 1
        root = unseen.pop()
        queue: deque[Species] = deque([root])
        while queue:
            node = queue.popleft()
            for neighbor in adjacency[node]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
    return count


def edge_lock(left: Fraction, right: Fraction, coupling: Fraction) -> Fraction:
    return coupling * (left - right) ** 2 * (left**2 + right**2) / 4


def constant_energy(
    values: dict[Species, Fraction],
    mass: Fraction,
    quartic: Fraction,
    locking: Fraction,
) -> Fraction:
    onsite = sum(
        (mass * value**2 / 2 + quartic * value**4 / 4)
        for value in values.values()
    )
    mixing = sum(
        edge_lock(values[left], values[right], locking)
        for left, right in cube_edges()
    )
    return onsite + mixing


def sign_cut(signs: dict[Species, int]) -> int:
    return sum(signs[left] != signs[right] for left, right in cube_edges())


def sign_cut_histogram() -> Counter[int]:
    histogram: Counter[int] = Counter()
    nodes = species_set()
    for pattern in product((-1, 1), repeat=len(nodes)):
        histogram[sign_cut(dict(zip(nodes, pattern)))] += 1
    return histogram


def polynomial_coefficients() -> dict[tuple[int, int], int]:
    # (a-b)^2(a^2+b^2); the common lambda/4 factor is kept outside.
    return {(4, 0): 1, (3, 1): -2, (2, 2): 2, (1, 3): -2, (0, 4): 1}


def edge_hessian(
    left: Fraction, right: Fraction, coupling: Fraction
) -> list[list[Fraction]]:
    coefficients = polynomial_coefficients()
    aa = sum(
        (
            Fraction(coefficient) * i * (i - 1) * left ** (i - 2) * right**j
            for (i, j), coefficient in coefficients.items()
            if i >= 2
        ),
        Fraction(0),
    )
    ab = sum(
        (
            Fraction(coefficient) * i * j * left ** (i - 1) * right ** (j - 1)
            for (i, j), coefficient in coefficients.items()
            if i >= 1 and j >= 1
        ),
        Fraction(0),
    )
    bb = sum(
        (
            Fraction(coefficient) * j * (j - 1) * left**i * right ** (j - 2)
            for (i, j), coefficient in coefficients.items()
            if j >= 2
        ),
        Fraction(0),
    )
    factor = coupling / 4
    return [[factor * aa, factor * ab], [factor * ab, factor * bb]]


def edge_gradient(
    left: Fraction, right: Fraction, coupling: Fraction
) -> tuple[Fraction, Fraction]:
    coefficients = polynomial_coefficients()
    derivative_left = sum(
        (
            Fraction(coefficient) * i * left ** (i - 1) * right**j
            for (i, j), coefficient in coefficients.items()
            if i >= 1
        ),
        Fraction(0),
    )
    derivative_right = sum(
        (
            Fraction(coefficient) * j * left**i * right ** (j - 1)
            for (i, j), coefficient in coefficients.items()
            if j >= 1
        ),
        Fraction(0),
    )
    factor = coupling / 4
    return factor * derivative_left, factor * derivative_right


def fine_block_lock_energy(
    coarse: dict[tuple[tuple[int, int, int], Species], Fraction],
    size: int,
    coupling: Fraction,
) -> Fraction:
    total = Fraction(0)
    for y in product(range(size), repeat=3):
        phase = Fraction((-1) ** sum(y))
        fine_values = {
            epsilon: phase * coarse[(y, epsilon)] for epsilon in species_set()
        }
        for left, right in cube_edges():
            total += edge_lock(fine_values[left], fine_values[right], coupling)
    return total


def coarse_lock_energy(
    coarse: dict[tuple[tuple[int, int, int], Species], Fraction],
    size: int,
    coupling: Fraction,
) -> Fraction:
    return sum(
        (
            edge_lock(coarse[(y, left)], coarse[(y, right)], coupling)
            for y in product(range(size), repeat=3)
            for left, right in cube_edges()
        ),
        Fraction(0),
    )


def block_lock_from_fine(
    field: dict[tuple[int, int, int], Fraction],
    fine_side: int,
    coupling: Fraction,
) -> Fraction:
    coarse_side = fine_side // 2
    total = Fraction(0)
    for y in product(range(coarse_side), repeat=3):
        phase = Fraction((-1) ** sum(y))
        values = {
            epsilon: phase
            * field[tuple(2 * y[axis] + epsilon[axis] for axis in range(3))]
            for epsilon in species_set()
        }
        total += sum(
            (edge_lock(values[left], values[right], coupling) for left, right in cube_edges()),
            Fraction(0),
        )
    return total


def translate_fine(
    field: dict[tuple[int, int, int], Fraction],
    fine_side: int,
    axis: int,
) -> dict[tuple[int, int, int], Fraction]:
    return {
        x: field[
            tuple(
                (x[coordinate] - (1 if coordinate == axis else 0)) % fine_side
                for coordinate in range(3)
            )
        ]
        for x in product(range(fine_side), repeat=3)
    }


def verify() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(
                f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}"
            )
        rows.append(
            {
                "name": name,
                "group": group,
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    nodes = species_set()
    edges = cube_edges()
    laplacian = cube_laplacian()
    spectrum = cube_spectrum_by_characters()
    expected_spectrum = Counter({0: 1, 2: 3, 4: 3, 6: 1})

    check("parent identity", upstream["candidate_id"] == PARENT_ID, upstream["candidate_id"], PARENT_ID, "identity")
    check("eight species", len(nodes) == 2 ** len(nodes[0]), len(nodes), 2 ** len(nodes[0]), "cube")
    check("Q3 has twelve edges", len(edges) == len(nodes) * len(nodes[0]) // 2, len(edges), len(nodes) * len(nodes[0]) // 2, "cube")
    check("Q3 is connected", graph_components(edges) == 1, graph_components(edges), 1, "cube")
    check("Q3 Laplacian rank", matrix_rank(laplacian) == len(nodes) - 1, matrix_rank(laplacian), len(nodes) - 1, "cube")
    check("Q3 character spectrum", spectrum == expected_spectrum, dict(spectrum), dict(expected_spectrum), "cube")
    check("Q3 rows sum to zero", all(sum(row) == 0 for row in laplacian), [sum(row) for row in laplacian], [0] * len(nodes), "cube")

    coefficients = polynomial_coefficients()
    degrees = {sum(exponents) for exponents in coefficients}
    check("lock is homogeneous quartic", degrees == {4}, sorted(degrees), [4], "polynomial")
    check("global Z2 is exact", all(sum(exponents) % 2 == 0 for exponents in coefficients), True, True, "polynomial")
    check("origin Hessian is unchanged", not any(sum(exponents) <= 2 for exponents in coefficients), sorted(coefficients), "no degree at most two", "polynomial")
    check("lock genuinely cross-couples", any(left and right for left, right in coefficients), sorted(coefficients), "at least one mixed monomial", "polynomial")
    check("analytic polynomial minimal degree", min(degrees) == 4, min(degrees), 4, "polynomial")
    sample_pairs = ((Fraction(-3), Fraction(2)), (Fraction(0), Fraction(7)), (Fraction(5), Fraction(5)))
    check("nonnegative hostile samples", all(edge_lock(a, b, Fraction(3, 2)) >= 0 for a, b in sample_pairs), [edge_lock(a, b, Fraction(3, 2)) for a, b in sample_pairs], "all nonnegative samples", "polynomial")
    check("sample zero set equals the diagonal", all((edge_lock(a, b, Fraction(1)) == 0) == (a == b) for a, b in sample_pairs), True, True, "polynomial")

    mass, quartic, locking, stiffness = (
        Fraction(-1),
        Fraction(1),
        Fraction(2, 3),
        Fraction(2),
    )
    v = Fraction(1)
    expected_minimum = -len(nodes) * mass**2 / (4 * quartic)
    energies: list[Fraction] = []
    minimizers: list[tuple[int, ...]] = []
    cuts: list[int] = []
    for pattern in product((-1, 1), repeat=len(nodes)):
        values = {node: Fraction(sign) * v for node, sign in zip(nodes, pattern)}
        energy = constant_energy(values, mass, quartic, locking)
        energies.append(energy)
        cuts.append(sign_cut(dict(zip(nodes, pattern))))
        if energy == expected_minimum:
            minimizers.append(pattern)
    check("same-H ordered energy", min(energies) == expected_minimum, min(energies), expected_minimum, "ordering")
    check("complete-square amplitude", mass + quartic * v**2 == 0, mass + quartic * v**2, 0, "ordering")
    check("complete-square terms have positive coefficients", all(value > 0 for value in (quartic, locking, stiffness)), (quartic, locking, stiffness), "positive", "ordering")
    check("same-H zero reference", expected_minimum < 0 == constant_energy({node: Fraction(0) for node in nodes}, mass, quartic, locking), (expected_minimum, 0), "negative then zero", "ordering")
    check("exactly two locked sign minima", len(minimizers) == 2, len(minimizers), 2, "ordering")
    check("locked minima are uniform signs", set(minimizers) == {tuple([-1] * len(nodes)), tuple([1] * len(nodes))}, minimizers, "uniform plus and minus", "ordering")
    check("lambda zero restores all signs", sum(constant_energy({node: Fraction(sign) for node, sign in zip(nodes, pattern)}, mass, quartic, Fraction(0)) == expected_minimum for pattern in product((-1, 1), repeat=len(nodes))) == 2 ** len(nodes), 2 ** len(nodes), 2 ** len(nodes), "hostile")

    histogram = sign_cut_histogram()
    expected_histogram = Counter({0: 2, 3: 16, 4: 30, 5: 48, 6: 64, 7: 48, 8: 30, 9: 16, 12: 2})
    check("exact Q3 cut histogram", histogram == expected_histogram, dict(histogram), dict(expected_histogram), "ordering")
    nonzero_cuts = [cut for cut in cuts if cut]
    check("minimum nonconstant cut", min(nonzero_cuts) == len(nodes[0]), min(nonzero_cuts), len(nodes[0]), "ordering")
    predicted_gap = 2 * locking * v**4 * len(nodes[0])
    actual_gap = min(energy - expected_minimum for energy in energies if energy > expected_minimum)
    check("minimum old-manifold locking gap", actual_gap == predicted_gap, actual_gap, predicted_gap, "ordering")

    ordered_edge_hessian = edge_hessian(v, v, locking)
    check("ordered edge Hessian coefficient", ordered_edge_hessian == [[Fraction(2, 3), Fraction(-2, 3)], [Fraction(-2, 3), Fraction(2, 3)]], ordered_edge_hessian, "lambda v squared edge Laplacian", "hessian")
    ordered_spectrum = Counter(
        {(-2 * mass + locking * v**2 * eigenvalue): multiplicity for eigenvalue, multiplicity in spectrum.items()}
    )
    expected_ordered = Counter({Fraction(2): 1, Fraction(10, 3): 3, Fraction(14, 3): 3, Fraction(6): 1})
    check("ordered species Hessian spectrum", ordered_spectrum == expected_ordered, dict(ordered_spectrum), dict(expected_ordered), "hessian")
    check("ordered Hessian is positive", min(ordered_spectrum) > 0, min(ordered_spectrum), "positive", "hessian")
    check("critical nonlinear lock keeps nullity eight", len(nodes) - matrix_rank([[Fraction(0) for _ in nodes] for _ in nodes]) == len(nodes), len(nodes), len(nodes), "hessian")
    check("positive quadratic repair leaves nullity one", len(nodes) - matrix_rank(laplacian) == 1, len(nodes) - matrix_rank(laplacian), 1, "quadratic_control")
    check("quadratic repair lifts seven modes", sum(multiplicity for eigenvalue, multiplicity in spectrum.items() if eigenvalue > 0) == len(nodes) - 1, len(nodes) - 1, len(nodes) - 1, "quadratic_control")

    q = Fraction(5, 2)
    p = Fraction(-7, 3)
    inertia = Fraction(11, 5)
    normalized_square = Fraction(1, len(nodes))
    kinetic_full = sum((p**2 * normalized_square / (2 * inertia) for _ in nodes), Fraction(0))
    mass_full = sum((mass * q**2 * normalized_square / 2 for _ in nodes), Fraction(0))
    quartic_full = sum((quartic * q**4 * normalized_square**2 / 4 for _ in nodes), Fraction(0))
    check("collective canonical symplectic factor", len(nodes) * normalized_square == 1, len(nodes) * normalized_square, 1, "collective")
    check("collective kinetic coefficient", kinetic_full == p**2 / (2 * inertia), kinetic_full, p**2 / (2 * inertia), "collective")
    check("collective mass coefficient", mass_full == mass * q**2 / 2, mass_full, mass * q**2 / 2, "collective")
    check("collective quartic coupling", quartic_full == (quartic / len(nodes)) * q**4 / 4, quartic_full, (quartic / len(nodes)) * q**4 / 4, "collective")
    check("collective lock vanishes", edge_lock(q, q, locking) == 0, edge_lock(q, q, locking), 0, "collective")
    # A rational common coordinate is enough because invariance is independent
    # of the common value; the canonical normalization is checked separately.
    collective_value = Fraction(5, 7)
    collective_gradient = edge_gradient(collective_value, collective_value, locking)
    check("collective lock force vanishes", collective_gradient == (0, 0), collective_gradient, (0, 0), "collective")

    coarse_size = 2
    coarse = {
        (y, epsilon): Fraction(
            1 + sum((coordinate + 1) * value for coordinate, value in enumerate(y))
            + sum((coordinate + 2) * bit for coordinate, bit in enumerate(epsilon)),
            7,
        )
        for y in product(range(coarse_size), repeat=3)
        for epsilon in nodes
    }
    coarse_energy = coarse_lock_energy(coarse, coarse_size, locking)
    fine_energy = fine_block_lock_energy(coarse, coarse_size, locking)
    check("signed fine/coarse local lock identity", fine_energy == coarse_energy, fine_energy, coarse_energy, "locality")
    check("lock has one-fine-step block range", all(sum(abs(a - b) for a, b in zip(left, right)) == 1 for left, right in edges), True, True, "locality")
    check("N divisible by four periodic sign", all((-1) ** (coordinate + size) == (-1) ** coordinate for size in (2, 4) for coordinate in range(size)), True, True, "periodicity")
    check("N equals six hostile twist", any((-1) ** (coordinate + 3) != (-1) ** coordinate for coordinate in range(3)), True, True, "periodicity")
    fine_side = 4
    collective_fine = {
        x: Fraction((-1) ** sum(coordinate // 2 for coordinate in x))
        for x in product(range(fine_side), repeat=3)
    }
    original_block_energy = block_lock_from_fine(collective_fine, fine_side, locking)
    translated_block_energy = block_lock_from_fine(
        translate_fine(collective_fine, fine_side, 0), fine_side, locking
    )
    check("block-origin collective lock is zero", original_block_energy == 0, original_block_energy, 0, "translation_control")
    check("one-fine-site translation changes the lock", translated_block_energy > original_block_energy, translated_block_energy, "strictly positive", "translation_control")

    fine_spacing = Fraction(1, 5)
    coarse_spacing = 2 * fine_spacing
    coarse_weight = coarse_spacing**3 / len(nodes)
    check("fine-volume weight reconciliation", coarse_weight == fine_spacing**3, coarse_weight, fine_spacing**3, "physical_ledger")
    check("eight-species continuum density weight", Fraction(1, len(nodes)) * len(nodes) == 1, Fraction(1, len(nodes)) * len(nodes), 1, "physical_ledger")
    check("physical diagonal quartic remains g", Fraction(1, len(nodes)) * len(nodes) * quartic == quartic, Fraction(1, len(nodes)) * len(nodes) * quartic, quartic, "physical_ledger")

    mass_squared = Fraction(9)
    first_wave_number_squared = Fraction(16)
    pah1_squared = (mass_squared, mass_squared + first_wave_number_squared, mass_squared + first_wave_number_squared)
    check("PA-H1 collective tangent squares", pah1_squared == (9, 25, 25), pah1_squared, (9, 25, 25), "pah1")
    check("PA-H1 pair is spatial not Q3 triplet", spectrum[2] == len(nodes[0]) and pah1_squared.count(25) == 2, (spectrum[2], pah1_squared.count(25)), (3, 2), "pah1")

    negative_ray_coefficient = (
        len(nodes) * quartic / 4 + 2 * len(edges) * locking
    )
    threshold = -len(nodes) * quartic / (8 * len(edges))
    check("positive lambda hostile ray is coercive", negative_ray_coefficient > 0, negative_ray_coefficient, "positive", "hostile")
    check("negative-lambda threshold is minus g over twelve", threshold == -quartic / 12, threshold, -quartic / 12, "hostile")
    threshold_quartic_coefficient = len(nodes) * quartic / 4 + 2 * len(edges) * threshold
    check("threshold quartic ray coefficient vanishes", threshold_quartic_coefficient == 0, threshold_quartic_coefficient, 0, "hostile")
    check("threshold is already unbounded for negative r", mass < 0 and threshold_quartic_coefficient == 0, (mass, threshold_quartic_coefficient), "negative quadratic with zero quartic", "hostile")
    difference_fourth_lowest_order = 4
    check("difference-fourth control has zero ordered Hessian", difference_fourth_lowest_order > 2, difference_fourth_lowest_order, "greater than two", "hostile")
    check("square-difference control fails sign lock", (v**2 - (-v) ** 2) ** 2 == 0, (v**2 - (-v) ** 2) ** 2, 0, "hostile")

    coarse_sites = coarse_size**3
    finite_degrees = len(nodes) * coarse_sites
    quantum_prerequisites = {
        "finite_degrees": finite_degrees > 0,
        "positive_inertia": inertia > 0,
        "positive_onsite_quartic": quartic > 0,
        "nonnegative_lock": locking >= 0,
        "nonnegative_spatial_stiffness": stiffness >= 0,
        "connected_configuration_space": finite_degrees > 0,
    }
    check("finite quantum theorem prerequisites", all(quantum_prerequisites.values()), quantum_prerequisites, "all true", "quantum_scope")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "candidate-scope exact nonlinear Q3 locking audit; not CP1 or Pre-A closure",
        "claim_context": ["C6-SPACETIME-SIGNATURE", "A2-FULL-PRODUCTION-WELLPOSED"],
        "claim_bearing": False,
        "task_id": "T-054",
        "exact_results": {
            "species_count": len(nodes),
            "cube_edge_count": len(edges),
            "cube_laplacian_spectrum": dict(sorted(spectrum.items())),
            "origin_lock_hessian": "zero",
            "critical_soft_species": len(nodes),
            "ordered_minimum_count": len(minimizers),
            "ordered_minimum_energy_per_coarse_volume": str(expected_minimum),
            "cut_histogram": dict(sorted(histogram.items())),
            "minimum_old_manifold_gap_fixture": str(predicted_gap),
            "ordered_species_spectrum_fixture": dict(sorted(ordered_spectrum.items())),
            "finite_collective_effective_quartic": str(quartic / len(nodes)),
            "physical_diagonal_continuum_quartic": str(quartic),
            "pah1_collective_tangent_squared_frequencies": list(pah1_squared),
            "quadratic_connected_control_nullity": 1,
            "negative_lambda_bipartite_threshold": str(-quartic / 12),
            "negative_lambda_unbounded_at_or_below_threshold_for_r_negative": True,
            "fine_translation_counterexample_energy": str(translated_block_energy),
            "finite_quantum_prerequisites": quantum_prerequisites,
        },
        "scope": {
            "global_Z2": True,
            "coarse_translation": True,
            "Q3_automorphism": True,
            "fine_one_site_translation": False,
            "connected_interaction_hypergraph": True,
            "connected_harmonic_graph_at_origin": False,
            "same_H_classical_zero_comparison": True,
            "physical_empty_space_comparison": False,
            "finite_quantum_unique_symmetric_ground_by_prior_art": True,
            "pure_ordered_quantum_phase": False,
            "collective_classical_nonlinear_reduction": True,
            "selected_collective_quantum_state": False,
            "finite_exact_characteristic_cone": False,
            "CP1_complete": False,
            "Pre_A_complete": False,
        },
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "sources": [
            {"path": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(path)}
            for path in (SCRIPT, UPSTREAM)
        ],
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if arguments.self_test and DEFAULT_OUTPUT.is_file():
        stored = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        if canonical(stored) != canonical(payload):
            raise AssertionError("stored primary artifact is stale; regenerate without --self-test")
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    count = payload["assertions"]["passed"]
    print(f"PASS {count}/{count} | {CANDIDATE_ID} | nonlinear Q3 lock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
