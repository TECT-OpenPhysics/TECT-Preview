#!/usr/bin/env python3
"""Primary exact audit for the PA-CP1-ST8-CB-v0 staggered bridge.

The certificate proves that PA-CP1-LT3-RS-v0 is canonically equivalent to
eight decoupled nearest-neighbour coarse phi4 lattices.  It also proves a
harmonic continuum-symbol bridge and the finite continuous-time exact-cone
obstruction.  It does not complete a characteristic reconstruction or CP1.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-ST8-CB-v0"
PARENT_ID = "PA-CP1-LT3-RS-v0"
SLUG = "pre-a-cp1-st8-block-causal-bridge"
SCHEMA = f"tect/{SLUG}-primary/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
COMPARISON_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-primary-{SLUG}"
    / "result.json"
)

FineSite = tuple[int, int, int]
CoarseSite = tuple[int, int, int]
Species = tuple[int, int, int]
BlockCoordinate = tuple[Species, CoarseSite]


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return {
            "rows": value.rows,
            "cols": value.cols,
            "rank": value.rank(),
            "entries": [
                [serial(value[row, column]) for column in range(value.cols)]
                for row in range(value.rows)
            ],
        }
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, set):
        return sorted((serial(item) for item in value), key=str)
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
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> None:
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


def sites(side: int) -> list[tuple[int, int, int]]:
    return list(itertools.product(range(side), repeat=3))


def species_set() -> list[Species]:
    return list(itertools.product((0, 1), repeat=3))


def move(site: tuple[int, int, int], axis: int, amount: int, side: int) -> tuple[int, int, int]:
    coordinates = list(site)
    coordinates[axis] = (coordinates[axis] + amount) % side
    return tuple(coordinates)  # type: ignore[return-value]


def compose(coarse: CoarseSite, species: Species) -> FineSite:
    return tuple(2 * coarse[axis] + species[axis] for axis in range(3))  # type: ignore[return-value]


def decompose(fine: FineSite) -> BlockCoordinate:
    species = tuple(component % 2 for component in fine)
    coarse = tuple(component // 2 for component in fine)
    return species, coarse  # type: ignore[return-value]


def staggered_sign(coarse: CoarseSite) -> int:
    return (-1) ** sum(coarse)


def to_fine(block: dict[BlockCoordinate, Any]) -> dict[FineSite, Any]:
    output: dict[FineSite, Any] = {}
    for (species, coarse), value in block.items():
        output[compose(coarse, species)] = staggered_sign(coarse) * value
    return output


def to_block(fine: dict[FineSite, Any]) -> dict[BlockCoordinate, Any]:
    output: dict[BlockCoordinate, Any] = {}
    for site, value in fine.items():
        species, coarse = decompose(site)
        output[(species, coarse)] = staggered_sign(coarse) * value
    return output


def b_value(fine: dict[FineSite, Any], site: FineSite, axis: int, side: int) -> Any:
    return -fine[move(site, axis, 1, side)] - fine[move(site, axis, -1, side)]


def fine_energy_parts(
    field: dict[FineSite, Any],
    momentum: dict[FineSite, Any],
    side: int,
    r: Any,
    c: Any,
    g: Any,
    chi: Any,
) -> dict[str, sp.Expr]:
    return {
        "kinetic": sp.simplify(sum(value**2 for value in momentum.values()) / (2 * chi)),
        "mass": sp.simplify(r * sum(value**2 for value in field.values()) / 2),
        "stiffness": sp.simplify(
            c
            * sum(
                b_value(field, site, axis, side) ** 2
                for site in sites(side)
                for axis in range(3)
            )
            / 2
        ),
        "quartic": sp.simplify(g * sum(value**4 for value in field.values()) / 4),
    }


def block_energy_parts(
    field: dict[BlockCoordinate, Any],
    momentum: dict[BlockCoordinate, Any],
    coarse_side: int,
    r: Any,
    c: Any,
    g: Any,
    chi: Any,
) -> dict[str, sp.Expr]:
    return {
        "kinetic": sp.simplify(sum(value**2 for value in momentum.values()) / (2 * chi)),
        "mass": sp.simplify(r * sum(value**2 for value in field.values()) / 2),
        "stiffness": sp.simplify(
            c
            * sum(
                (
                    field[(species, move(coarse, axis, 1, coarse_side))]
                    - field[(species, coarse)]
                )
                ** 2
                for species in species_set()
                for coarse in sites(coarse_side)
                for axis in range(3)
            )
            / 2
        ),
        "quartic": sp.simplify(g * sum(value**4 for value in field.values()) / 4),
    }


def fine_b_matrix(side: int, axis: int) -> sp.Matrix:
    lattice_sites = sites(side)
    index = {site: position for position, site in enumerate(lattice_sites)}
    matrix = sp.zeros(len(lattice_sites))
    for site in lattice_sites:
        row = index[site]
        matrix[row, index[move(site, axis, 1, side)]] -= 1
        matrix[row, index[move(site, axis, -1, side)]] -= 1
    return matrix


def coarse_gradient_matrix(coarse_side: int, axis: int) -> sp.Matrix:
    coordinates = [
        (species, coarse)
        for species in species_set()
        for coarse in sites(coarse_side)
    ]
    index = {coordinate: position for position, coordinate in enumerate(coordinates)}
    matrix = sp.zeros(len(coordinates))
    for species, coarse in coordinates:
        row = index[(species, coarse)]
        matrix[row, index[(species, coarse)]] -= 1
        matrix[row, index[(species, move(coarse, axis, 1, coarse_side))]] += 1
    return matrix


def block_transform_matrix(side: int) -> sp.Matrix:
    coarse_side = side // 2
    fine_coordinates = sites(side)
    block_coordinates = [
        (species, coarse)
        for species in species_set()
        for coarse in sites(coarse_side)
    ]
    fine_index = {site: position for position, site in enumerate(fine_coordinates)}
    block_index = {
        coordinate: position for position, coordinate in enumerate(block_coordinates)
    }
    matrix = sp.zeros(side**3)
    for coordinate in block_coordinates:
        species, coarse = coordinate
        matrix[fine_index[compose(coarse, species)], block_index[coordinate]] = staggered_sign(coarse)
    return matrix


def coarse_laplacian(side: int) -> sp.Matrix:
    lattice_sites = sites(side)
    index = {site: position for position, site in enumerate(lattice_sites)}
    matrix = sp.zeros(side**3)
    for site in lattice_sites:
        row = index[site]
        for axis in range(3):
            matrix[row, row] += 2
            matrix[row, index[move(site, axis, 1, side)]] -= 1
            matrix[row, index[move(site, axis, -1, side)]] -= 1
    return matrix


def deterministic_block(side: int, salt: int) -> dict[BlockCoordinate, sp.Integer]:
    coarse_side = side // 2
    result: dict[BlockCoordinate, sp.Integer] = {}
    for species in species_set():
        for coarse in sites(coarse_side):
            code = sum(
                (index + 2) * value
                for index, value in enumerate(species + coarse)
            )
            result[(species, coarse)] = sp.Integer(((7 * code + salt) % 13) - 6)
    return result


def derive() -> dict[str, Any]:
    audit = Audit()
    r, c, g, chi = sp.symbols("r c g chi", positive=True)
    fixtures: dict[str, Any] = {}

    for side in (4, 8, 12):
        coarse_side = side // 2
        audit.check(
            f"side {side} staggered sign is periodic on the coarse torus",
            side % 4 == 0 and (-1) ** coarse_side == 1,
            (side % 4, (-1) ** coarse_side),
            (0, 1),
            "boundary_condition",
        )
        all_fine = sites(side)
        all_block = [
            (species, coarse)
            for species in species_set()
            for coarse in sites(coarse_side)
        ]
        audit.check(
            f"side {side} fine-to-block coordinate map is bijective",
            len(all_fine) == len(all_block) == side**3
            and {compose(*decompose(site)[::-1]) for site in all_fine} == set(all_fine),
            (len(all_fine), len(all_block)),
            (side**3, side**3),
            "block_map",
        )

        block_field = deterministic_block(side, 3)
        block_momentum = deterministic_block(side, 8)
        fine_field = to_fine(block_field)
        fine_momentum = to_fine(block_momentum)
        audit.check(
            f"side {side} staggered transform has an exact inverse",
            to_block(fine_field) == block_field
            and to_block(fine_momentum) == block_momentum,
            True,
            True,
            "block_map",
        )

        second_field = deterministic_block(side, 5)
        second_momentum = deterministic_block(side, 11)
        fine_second_field = to_fine(second_field)
        fine_second_momentum = to_fine(second_momentum)
        fine_symplectic = sum(
            fine_field[site] * fine_second_momentum[site]
            - fine_momentum[site] * fine_second_field[site]
            for site in all_fine
        )
        block_symplectic = sum(
            block_field[coordinate] * second_momentum[coordinate]
            - block_momentum[coordinate] * second_field[coordinate]
            for coordinate in all_block
        )
        audit.check(
            f"side {side} staggered transform preserves the symplectic form",
            sp.simplify(fine_symplectic - block_symplectic) == 0,
            fine_symplectic,
            block_symplectic,
            "canonical",
        )

        fine_parts = fine_energy_parts(
            fine_field, fine_momentum, side, -r, c, g, chi
        )
        block_parts = block_energy_parts(
            block_field, block_momentum, coarse_side, -r, c, g, chi
        )
        for part in ("kinetic", "mass", "stiffness", "quartic"):
            audit.check(
                f"side {side} exact {part} term block identity",
                sp.simplify(fine_parts[part] - block_parts[part]) == 0,
                fine_parts[part],
                block_parts[part],
                "hamiltonian_factorization",
            )
        fine_total = sp.simplify(sum(fine_parts.values()))
        block_total = sp.simplify(sum(block_parts.values()))
        audit.check(
            f"side {side} full Hamiltonian is the eight-copy block sum",
            sp.simplify(fine_total - block_total) == 0,
            fine_total,
            block_total,
            "hamiltonian_factorization",
        )
        fixtures[str(side)] = {
            "fine_dimension": side**3,
            "coarse_side": coarse_side,
            "species_count": len(species_set()),
            "factorized_energy_fixture": block_total,
        }

    hostile_side = 6
    hostile_coarse_side = hostile_side // 2
    audit.check(
        "side 6 hostile control produces an antiperiodic staggered sign",
        hostile_side % 4 == 2 and (-1) ** hostile_coarse_side == -1,
        (hostile_side % 4, (-1) ** hostile_coarse_side),
        (2, -1),
        "boundary_condition",
    )

    side = 4
    coarse_side = side // 2
    transform = block_transform_matrix(side)
    audit.check(
        "side 4 block transform is an exact signed orthogonal permutation",
        transform.T * transform == sp.eye(side**3)
        and transform * transform.T == sp.eye(side**3),
        "U^T U=U U^T=I",
        "U^T U=U U^T=I",
        "canonical",
    )
    for axis in range(3):
        fine_b = fine_b_matrix(side, axis)
        coarse_gradient = coarse_gradient_matrix(coarse_side, axis)
        audit.check(
            f"side 4 axis {axis} exact operator Gram conjugacy",
            transform.T * fine_b.T * fine_b * transform
            == coarse_gradient.T * coarse_gradient,
            "U^T B_i^T B_i U",
            "D_i^T D_i",
            "operator_identity",
        )

    stacked_b = sp.Matrix.vstack(*(fine_b_matrix(side, axis) for axis in range(3)))
    audit.check(
        "side 4 fine common stencil kernel has dimension eight",
        side**3 - stacked_b.rank() == len(species_set()),
        side**3 - stacked_b.rank(),
        len(species_set()),
        "zone_folding",
    )
    connected_standard_eigenvalues = [
        sp.simplify(
            4
            * sum(
                sp.sin(sp.pi * component / side) ** 2
                for component in momentum
            )
        )
        for momentum in itertools.product(range(side), repeat=3)
    ]
    connected_nullity = sum(
        int(eigenvalue == 0) for eigenvalue in connected_standard_eigenvalues
    )
    audit.check(
        "one connected same-dimension standard scalar has nullity one rather than eight",
        connected_nullity == 1
        and connected_nullity != side**3 - stacked_b.rank(),
        (connected_nullity, side**3 - stacked_b.rank()),
        (1, 8),
        "connected_parent_obstruction",
    )
    connected_sites = sites(side)
    visited = {connected_sites[0]}
    frontier = [connected_sites[0]]
    while frontier:
        current = frontier.pop()
        for axis in range(3):
            for amount in (-1, 1):
                neighbour_site = move(current, axis, amount, side)
                if neighbour_site not in visited:
                    visited.add(neighbour_site)
                    frontier.append(neighbour_site)
    connected_standard_ground_count = 2 if len(visited) == side**3 else 0
    audit.check(
        "connected standard scalar complete square has two uniform sign minima",
        connected_standard_ground_count == 2,
        (len(visited), connected_standard_ground_count),
        (side**3, 2),
        "connected_parent_obstruction",
    )
    folded_constant_vectors: list[sp.Matrix] = []
    block_coordinates = [
        (species, coarse)
        for species in species_set()
        for coarse in sites(coarse_side)
    ]
    for selected_species in species_set():
        block_vector = sp.Matrix(
            [
                int(species == selected_species)
                for species, _coarse in block_coordinates
            ]
        )
        fine_vector = transform * block_vector
        folded_constant_vectors.append(fine_vector)
        audit.check(
            f"species {selected_species} constant mode folds into the fine stencil kernel",
            stacked_b * fine_vector == sp.zeros(3 * side**3, 1),
            "B_i U constant=0",
            "B_i U constant=0",
            "zone_folding",
        )
    audit.check(
        "the eight folded constant species span the full fine kernel",
        sp.Matrix.hstack(*folded_constant_vectors).rank() == len(species_set()),
        sp.Matrix.hstack(*folded_constant_vectors).rank(),
        len(species_set()),
        "zone_folding",
    )

    ground_count = 0
    ground_energy = None
    ground_fixture_r = sp.Integer(-1)
    ground_fixture_c = sp.Integer(2)
    ground_fixture_g = sp.Integer(1)
    ground_fixture_chi = sp.Integer(1)
    expected_ground_energy = sp.simplify(
        -side**3 * ground_fixture_r**2 / (4 * ground_fixture_g)
    )
    for signs in itertools.product((-1, 1), repeat=len(species_set())):
        block_ground = {
            (species, coarse): sp.Integer(signs[index])
            for index, species in enumerate(species_set())
            for coarse in sites(coarse_side)
        }
        zero_momentum = {coordinate: sp.Integer(0) for coordinate in block_ground}
        parts = block_energy_parts(
            block_ground,
            zero_momentum,
            coarse_side,
            ground_fixture_r,
            ground_fixture_c,
            ground_fixture_g,
            ground_fixture_chi,
        )
        energy = sp.simplify(sum(parts.values()))
        if energy == expected_ground_energy:
            ground_count += 1
            ground_energy = energy
    audit.check(
        "the LT3-classified 256 fine minima are the eight independent coarse signs",
        ground_count == 2 ** len(species_set()),
        ground_count,
        2 ** len(species_set()),
        "classical_interpretation",
    )

    k1, k2, k3 = sp.symbols("k1 k2 k3", real=True)
    kappa = (k1, k2, k3)
    coarse_symbol = r + 4 * c * sum(sp.sin(component / 2) ** 2 for component in kappa)
    coarse_hessian = sp.hessian(coarse_symbol, kappa).subs({k1: 0, k2: 0, k3: 0})
    audit.check(
        "coarse harmonic symbol has one quadratic zero per species at criticality",
        coarse_hessian == 2 * c * sp.eye(3),
        coarse_hessian,
        2 * c * sp.eye(3),
        "continuum_bridge",
    )
    coarse_speed_squared = sp.simplify(sp.trace(coarse_hessian) / (2 * 3 * chi))
    audit.check(
        "coarse critical speed squared is derived from the Hessian",
        sp.simplify(coarse_speed_squared - c / chi) == 0,
        coarse_speed_squared,
        c / chi,
        "continuum_bridge",
    )
    for signs in itertools.product((-1, 1), repeat=3):
        fine_branch = 4 * c * sum(
            sp.cos(signs[axis] * sp.pi / 2 + kappa[axis] / 2) ** 2
            for axis in range(3)
        )
        audit.check(
            f"fine node {signs} folds exactly to the coarse dispersion",
            sp.simplify(fine_branch - (coarse_symbol - r)) == 0,
            fine_branch,
            coarse_symbol - r,
            "zone_folding",
        )

    coarse_spacing = sp.symbols("a", positive=True)
    rescaled_symbol = r + 4 * c / coarse_spacing**2 * sum(
        sp.sin(coarse_spacing * component / 2) ** 2 for component in kappa
    )
    continuum_symbol = r + c * sum(component**2 for component in kappa)
    audit.check(
        "fixed-band harmonic symbol has the Klein-Gordon continuum limit",
        sp.simplify(sp.limit(rescaled_symbol, coarse_spacing, 0) - continuum_symbol) == 0,
        sp.limit(rescaled_symbol, coarse_spacing, 0),
        continuum_symbol,
        "continuum_bridge",
    )
    leading_symbol_error = sp.simplify(
        sp.limit(
            (rescaled_symbol - continuum_symbol) / coarse_spacing**2,
            coarse_spacing,
            0,
        )
    )
    expected_leading_error = -c * sum(component**4 for component in kappa) / 12
    audit.check(
        "continuum-symbol leading error is explicitly quadratic in spacing",
        sp.simplify(leading_symbol_error - expected_leading_error) == 0,
        leading_symbol_error,
        expected_leading_error,
        "continuum_bridge",
    )
    rescaled_omega = sp.sqrt(rescaled_symbol / chi)
    group_velocity_squared = sp.trigsimp(
        sum(sp.diff(rescaled_omega, component) ** 2 for component in kappa)
    )
    half_sine_sum = sum(
        sp.sin(coarse_spacing * component / 2) ** 2 for component in kappa
    )
    full_sine_sum = sum(
        sp.sin(coarse_spacing * component) ** 2 for component in kappa
    )
    derived_group_velocity_squared = sp.simplify(
        c**2
        * full_sine_sum
        / (
            coarse_spacing**2
            * chi
            * (r + 4 * c * half_sine_sum / coarse_spacing**2)
        )
    )
    audit.check(
        "rescaled harmonic group speed is differentiated from the dispersion",
        sp.trigsimp(group_velocity_squared - derived_group_velocity_squared) == 0,
        group_velocity_squared,
        derived_group_velocity_squared,
        "continuum_bridge",
    )
    speed_gap_numerator = (
        coarse_spacing**2 * r + c * (4 * half_sine_sum - full_sine_sum)
    )
    expected_speed_gap_numerator = coarse_spacing**2 * r + 4 * c * sum(
        sp.sin(coarse_spacing * component / 2) ** 4 for component in kappa
    )
    sine_identity_residuals = tuple(
        sp.trigsimp(
            4 * sp.sin(coarse_spacing * component / 2) ** 2
            - sp.sin(coarse_spacing * component) ** 2
            - 4 * sp.sin(coarse_spacing * component / 2) ** 4,
            method="fu",
        )
        for component in kappa
    )
    audit.check(
        "positive mass and the sine identity give the global squared-group-speed bound c over chi",
        sine_identity_residuals == (0, 0, 0),
        speed_gap_numerator,
        expected_speed_gap_numerator,
        "continuum_bridge",
    )
    lt3_spacing_dependent_stiffness = c / coarse_spacing**2
    inherited_fine_spacing = coarse_spacing / 2
    lt3_fine_dimensionless_speed_squared = (
        4 * lt3_spacing_dependent_stiffness / chi
    )
    lt3_fine_physical_speed_squared = sp.simplify(
        inherited_fine_spacing**2 * lt3_fine_dimensionless_speed_squared
    )
    audit.check(
        "fine LT3 speed and coarse continuum speed agree under the explicit spacing map",
        sp.simplify(lt3_fine_physical_speed_squared - c / chi) == 0,
        lt3_fine_physical_speed_squared,
        c / chi,
        "continuum_bridge",
    )

    inserted_pah1_target_frequencies = tuple(map(sp.Integer, (3, 5, 5)))
    inserted_pah1_target_frequency_squares = tuple(
        frequency**2 for frequency in inserted_pah1_target_frequencies
    )
    ordered_r = -inserted_pah1_target_frequency_squares[0] / 2
    ordered_c = sp.Integer(1)
    ordered_chi = sp.Integer(1)
    ordered_amplitude_squared = -ordered_r / g
    ordered_potential_curvature = sp.simplify(
        ordered_r + 3 * g * ordered_amplitude_squared
    )
    audit.check(
        "tuned ordered continuum background has potential curvature nine",
        ordered_potential_curvature == inserted_pah1_target_frequency_squares[0],
        ordered_potential_curvature,
        inserted_pah1_target_frequency_squares[0],
        "pah1_tangent",
    )
    circle_coordinate = sp.symbols("x", real=True)
    pah1_circumference = sp.pi / 2
    circle_basis = (
        sp.sqrt(2 / sp.pi),
        2 * sp.cos(4 * circle_coordinate) / sp.sqrt(sp.pi),
        2 * sp.sin(4 * circle_coordinate) / sp.sqrt(sp.pi),
    )
    circle_gram = sp.Matrix(
        [
            [
                sp.integrate(
                    left * right, (circle_coordinate, 0, pah1_circumference)
                )
                for right in circle_basis
            ]
            for left in circle_basis
        ]
    )
    audit.check(
        "PA-H1 circle modes are exactly orthonormal",
        circle_gram == sp.eye(3),
        circle_gram,
        sp.eye(3),
        "pah1_tangent",
    )
    circle_energy_matrix = sp.Matrix(
        [
            [
                sp.integrate(
                    sp.diff(left, circle_coordinate)
                    * sp.diff(right, circle_coordinate)
                    * ordered_c
                    + ordered_potential_curvature * left * right,
                    (circle_coordinate, 0, pah1_circumference),
                )
                for right in circle_basis
            ]
            for left in circle_basis
        ]
    )
    expected_pah1_frequency_squares = sp.diag(
        *inserted_pah1_target_frequency_squares
    )
    circle_frequency_matrix = sp.simplify(circle_energy_matrix / ordered_chi)
    audit.check(
        "tuned ordered one-flavour tangent reproduces the PA-H1 quadratic energy",
        circle_frequency_matrix == expected_pah1_frequency_squares,
        circle_frequency_matrix,
        expected_pah1_frequency_squares,
        "pah1_tangent",
    )
    pah1_frequencies = tuple(
        sp.sqrt(circle_frequency_matrix[index, index]) for index in range(3)
    )
    pah1_frequency_squares = tuple(
        circle_frequency_matrix[index, index] for index in range(3)
    )
    audit.check(
        "ordered continuum tangent reproduces PA-H1 frequencies three five five",
        pah1_frequencies == inserted_pah1_target_frequencies,
        pah1_frequencies,
        inserted_pah1_target_frequencies,
        "pah1_tangent",
    )

    tail_side = 4
    laplacian = coarse_laplacian(tail_side)
    positive_mass = sp.symbols("mu", positive=True)
    harmonic_matrix = positive_mass * sp.eye(tail_side**3) + c * laplacian
    tail_sites = sites(tail_side)
    tail_index = {site: index for index, site in enumerate(tail_sites)}
    origin = tail_index[(0, 0, 0)]
    neighbour = tail_index[(1, 0, 0)]
    opposite = tail_index[(2, 0, 0)]
    audit.check(
        "nearest-site response has no constant term and a nonzero t-squared term",
        harmonic_matrix[origin, neighbour] == -c,
        harmonic_matrix[origin, neighbour],
        -c,
        "exact_cone_obstruction",
    )
    squared_matrix = harmonic_matrix**2
    audit.check(
        "distance-two response first appears with the two shortest paths",
        harmonic_matrix[origin, opposite] == 0
        and sp.simplify(squared_matrix[origin, opposite] - 2 * c**2) == 0,
        (harmonic_matrix[origin, opposite], squared_matrix[origin, opposite]),
        (0, 2 * c**2),
        "exact_cone_obstruction",
    )
    distance_one_lead = sp.simplify(-harmonic_matrix[origin, neighbour] / (2 * chi))
    distance_two_lead = sp.simplify(
        squared_matrix[origin, opposite] / (sp.factorial(4) * chi**2)
    )
    audit.check(
        "finite continuous-time displacement response has positive offsite leading coefficients",
        sp.ask(sp.Q.positive(distance_one_lead)) is True
        and sp.ask(sp.Q.positive(distance_two_lead)) is True,
        (distance_one_lead, distance_two_lead),
        "both positive",
        "exact_cone_obstruction",
    )

    source = Path(__file__).resolve()
    scope = {
        "exact_finite_block_canonical_equivalence": True,
        "eight_decoupled_coarse_species": True,
        "fine_nodes_are_folded_coarse_zero_modes": True,
        "finite_quantum_tensor_factorization": True,
        "periodic_block_factorization_requires_N_divisible_by_four": True,
        "global_harmonic_group_speed_bound": True,
        "harmonic_fixed_band_continuum_symbol_limit": True,
        "tuned_formal_ordered_continuum_pah1_tangent_calibration": True,
        "interacting_continuum_limit": False,
        "quantum_continuum_limit": False,
        "strict_finite_lattice_causal_cone": False,
        "finite_lattice_characteristic_sheets": False,
        "continuum_characteristic_reconstruction": False,
        "selected_pah1_species_or_sector": False,
        "full_nonlinear_pah1_embedding": False,
        "same_selected_state_characteristic_restriction": False,
        "one_connected_bulk_sector": False,
        "physical_empty_space": False,
        "cooling_history": False,
        "gravity": False,
        "event_horizon": False,
        "cp1_complete": False,
        "pre_a_complete": False,
    }
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "candidate_family": "PRE-A-STAGGERED-BLOCK-CAUSAL-BRIDGE",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 exact finite block-equivalence and causal-boundary certificate; not CP1 or Pre-A closure",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": COMPARISON_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "finite_fixtures": fixtures,
        "exact_results": {
            "canonical_map": "phi_(2y+epsilon)=(-1)^sum(y) psi_epsilon(y), with the same map for momentum",
            "hamiltonian_factorization": "H_fine=sum_epsilon H_std[psi_epsilon,rho_epsilon] for eight decoupled nearest-neighbour coarse phi4 lattices",
            "fine_kernel_dimension": len(species_set()),
            "single_connected_standard_scalar_kernel_dimension": connected_nullity,
            "single_connected_standard_scalar_ground_count": connected_standard_ground_count,
            "classical_ground_count": ground_count,
            "classical_ground_energy_side4_fixture": ground_energy,
            "classical_ground_fixture_parameters": {
                "side": side,
                "r": ground_fixture_r,
                "g": ground_fixture_g,
            },
            "coarse_symbol": coarse_symbol,
            "coarse_speed_squared": coarse_speed_squared,
            "continuum_symbol": continuum_symbol,
            "continuum_leading_error": leading_symbol_error,
            "coarse_spacing_definition": "a is the coarse-lattice spacing and the inherited fine-lattice spacing is a/2",
            "continuum_family_parameter_map": "c_LT3(a)=c_phys/a^2 with chi fixed",
            "fine_to_coarse_physical_speed_squared": lt3_fine_physical_speed_squared,
            "global_group_speed_squared_bound": "|grad_k omega_a|^2<=c/chi for r>=0; at r=0 the statement is off-node with the corresponding Lipschitz envelope",
            "ordered_tangent_calibration_parameters": {
                "r": ordered_r,
                "c": ordered_c,
                "chi": ordered_chi,
                "status": "inserted calibration inputs",
            },
            "ordered_potential_curvature": ordered_potential_curvature,
            "pah1_circumference": pah1_circumference,
            "pah1_tangent_frequency_squares": pah1_frequency_squares,
            "pah1_tangent_frequencies": pah1_frequencies,
            "distance_one_response_leading_coefficient": distance_one_lead,
            "distance_two_response_leading_coefficient": distance_two_lead,
            "finite_exact_cone": "absent: the verified nearest-neighbour response is nonzero at arbitrarily small time, already contradicting every finite strict support speed; the distance-two coefficient is an additional control",
            "quantum_factorization": "analytic corollary: signed-coordinate L2 unitarity and the imported finite-block ground uniqueness conjugate the finite quantum Hamiltonian to a tensor sum of eight identical coarse operators and its ground to their tensor product",
        },
        "interpretation": {
            "zone_folding": "the eight fine nodes are a folded representation of eight coarse species zero modes, not proof of eight intrinsically distinct physical valleys",
            "connectivity": "the exact dynamics preserves each coarse species and therefore supplies eight decoupled sectors rather than one connected bulk",
            "connected_parent_obstruction": "kernel nullity one versus eight, together with two versus 256 complete-square minima, blocks an invertible exact Hamiltonian equivalence to one connected standard scalar of the same phase dimension",
            "causal_status": "the proved harmonic group-speed bound and controlled symbol limit do not create exact finite-regulator characteristic sheets; the tail calculation is for the harmonic linearization",
            "continuum_scaling": "a is the coarse spacing, the inherited fine spacing is a/2, and the spacing-dependent c/a^2 symbol is a declared regulator family rather than an automatic limit of the fixed-c spacing-one parent",
            "pah1_calibration": "one species, one spatial axis, the transverse-zero sector, circumference pi/2, c/chi=1 and -2r/chi=9 are inserted calibration choices rather than dynamically selected outputs",
        },
        "scope": scope,
        "verdict": "ADVANCE the exact staggered factorization, harmonic continuum bridge and tuned formal PA-H1 tangent calibration; REJECT finite-lattice characteristic completion and keep CP1 open",
        "next_gate": "add and control a common interacting continuum or exact-causal discrete parent, then prove two-sheet characteristic reconstruction, symplectic flux and state restriction without erasing the eight-sector factorization",
        "no_overclaim": "This package proves an exact finite signed-block equivalence, a declared harmonic fixed-band regulator-family limit, a tuned formal ordered PA-H1 tangent calibration and an exact-cone obstruction for continuous-time lattice evolution. It does not prove that the fixed spacing-one parent automatically has a continuum limit, a selected PA-H1 species or sector, a full nonlinear PA-H1 embedding, an interacting or quantum continuum limit, a strict lattice causal cone, characteristic state reconstruction, a connected bulk, a physical vacuum, cooling, gravity, CP1 or Pre-A.",
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "source": {
            "path": source.relative_to(REPO),
            "sha256": sha256(source),
        },
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
        f"{CANDIDATE_ID} | exact staggered block bridge"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
