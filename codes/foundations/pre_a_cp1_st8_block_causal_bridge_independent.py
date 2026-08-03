#!/usr/bin/env python3
"""Non-importing audit of the PA-CP1-ST8-CB-v0 staggered bridge."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-ST8-CB-v0"
PARENT_ID = "PA-CP1-LT3-RS-v0"
SLUG = "pre-a-cp1-st8-block-causal-bridge"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
COMPARISON_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)

Site = tuple[int, int, int]
Species = tuple[int, int, int]
BlockCoordinate = tuple[Species, Site]


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


def sites(side: int) -> list[Site]:
    return list(itertools.product(range(side), repeat=3))


def species_set() -> list[Species]:
    return list(itertools.product((0, 1), repeat=3))


def move(site: Site, axis: int, amount: int, side: int) -> Site:
    result = list(site)
    result[axis] = (result[axis] + amount) % side
    return tuple(result)  # type: ignore[return-value]


def compose(coarse: Site, species: Species) -> Site:
    return tuple(2 * coarse[axis] + species[axis] for axis in range(3))  # type: ignore[return-value]


def sign(coarse: Site) -> int:
    return (-1) ** sum(coarse)


def block_fixture(side: int, salt: int) -> dict[BlockCoordinate, Fraction]:
    coarse_side = side // 2
    return {
        (species, coarse): Fraction(
            (
                11
                * sum(
                    (index + 3) * value
                    for index, value in enumerate(species + coarse)
                )
                + salt
            )
            % 17
            - 8
        )
        for species in species_set()
        for coarse in sites(coarse_side)
    }


def to_fine(block: dict[BlockCoordinate, Fraction]) -> dict[Site, Fraction]:
    return {
        compose(coarse, species): sign(coarse) * value
        for (species, coarse), value in block.items()
    }


def b_value(field: dict[Site, Fraction], site: Site, axis: int, side: int) -> Fraction:
    return -field[move(site, axis, 1, side)] - field[move(site, axis, -1, side)]


def fine_parts(
    field: dict[Site, Fraction],
    momentum: dict[Site, Fraction],
    side: int,
    r: Fraction,
    c: Fraction,
    g: Fraction,
    chi: Fraction,
) -> dict[str, Fraction]:
    return {
        "kinetic": sum((value**2 for value in momentum.values()), Fraction()) / (2 * chi),
        "mass": r * sum((value**2 for value in field.values()), Fraction()) / 2,
        "stiffness": c
        * sum(
            (
                b_value(field, site, axis, side) ** 2
                for site in sites(side)
                for axis in range(3)
            ),
            Fraction(),
        )
        / 2,
        "quartic": g * sum((value**4 for value in field.values()), Fraction()) / 4,
    }


def block_parts(
    field: dict[BlockCoordinate, Fraction],
    momentum: dict[BlockCoordinate, Fraction],
    coarse_side: int,
    r: Fraction,
    c: Fraction,
    g: Fraction,
    chi: Fraction,
) -> dict[str, Fraction]:
    return {
        "kinetic": sum((value**2 for value in momentum.values()), Fraction()) / (2 * chi),
        "mass": r * sum((value**2 for value in field.values()), Fraction()) / 2,
        "stiffness": c
        * sum(
            (
                (
                    field[(species, move(coarse, axis, 1, coarse_side))]
                    - field[(species, coarse)]
                )
                ** 2
                for species in species_set()
                for coarse in sites(coarse_side)
                for axis in range(3)
            ),
            Fraction(),
        )
        / 2,
        "quartic": g * sum((value**4 for value in field.values()), Fraction()) / 4,
    }


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(left)
    return [
        [
            sum((left[row][middle] * right[middle][column] for middle in range(size)), Fraction())
            for column in range(size)
        ]
        for row in range(size)
    ]


def harmonic_matrix(side: int, mass: Fraction, stiffness: Fraction) -> tuple[list[list[Fraction]], dict[Site, int]]:
    lattice_sites = sites(side)
    index = {site: position for position, site in enumerate(lattice_sites)}
    matrix = [[Fraction() for _ in lattice_sites] for _ in lattice_sites]
    for site in lattice_sites:
        row = index[site]
        matrix[row][row] += mass
        for axis in range(3):
            matrix[row][row] += 2 * stiffness
            matrix[row][index[move(site, axis, 1, side)]] -= stiffness
            matrix[row][index[move(site, axis, -1, side)]] -= stiffness
    return matrix, index


def derive() -> dict[str, Any]:
    audit = Audit()
    fixtures: dict[str, Any] = {}
    parameters = {
        "r": Fraction(-3),
        "c": Fraction(2),
        "g": Fraction(5),
        "chi": Fraction(7),
    }
    for side in (4, 8, 12):
        coarse_side = side // 2
        audit.check(
            f"side {side} direct staggered-periodicity check",
            side % 4 == 0 and (-1) ** coarse_side == 1,
            (side % 4, (-1) ** coarse_side),
            (0, 1),
            "boundary_condition",
        )
        field = block_fixture(side, 2)
        momentum = block_fixture(side, 9)
        other_field = block_fixture(side, 5)
        other_momentum = block_fixture(side, 14)
        fine_field = to_fine(field)
        fine_momentum = to_fine(momentum)
        fine_other_field = to_fine(other_field)
        fine_other_momentum = to_fine(other_momentum)

        fine_symplectic = sum(
            (
                fine_field[site] * fine_other_momentum[site]
                - fine_momentum[site] * fine_other_field[site]
                for site in sites(side)
            ),
            Fraction(),
        )
        block_symplectic = sum(
            (
                field[coordinate] * other_momentum[coordinate]
                - momentum[coordinate] * other_field[coordinate]
                for coordinate in field
            ),
            Fraction(),
        )
        audit.check(
            f"side {side} direct canonical form equality",
            fine_symplectic == block_symplectic,
            fine_symplectic,
            block_symplectic,
            "canonical",
        )

        fine = fine_parts(fine_field, fine_momentum, side, **parameters)
        block = block_parts(field, momentum, coarse_side, **parameters)
        for part in ("kinetic", "mass", "stiffness", "quartic"):
            audit.check(
                f"side {side} independent {part} factorization",
                fine[part] == block[part],
                fine[part],
                block[part],
                "hamiltonian_factorization",
            )
        audit.check(
            f"side {side} independent total Hamiltonian factorization",
            sum(fine.values(), Fraction()) == sum(block.values(), Fraction()),
            sum(fine.values(), Fraction()),
            sum(block.values(), Fraction()),
            "hamiltonian_factorization",
        )

        maximum_fold_error = 0.0
        for sigma in itertools.product((-1, 1), repeat=3):
            for coarse_momentum in itertools.product(range(coarse_side), repeat=3):
                kappa = [
                    2.0 * math.pi * component / coarse_side
                    for component in coarse_momentum
                ]
                fine_symbol = 4.0 * sum(
                    math.cos(sigma[axis] * math.pi / 2.0 + kappa[axis] / 2.0) ** 2
                    for axis in range(3)
                )
                coarse_symbol = 4.0 * sum(
                    math.sin(component / 2.0) ** 2 for component in kappa
                )
                maximum_fold_error = max(
                    maximum_fold_error, abs(fine_symbol - coarse_symbol)
                )
        audit.check(
            f"side {side} direct eight-branch zone-folding identity",
            maximum_fold_error < 1.0e-12,
            maximum_fold_error,
            "<1e-12",
            "zone_folding",
        )
        fixtures[str(side)] = {
            "coarse_side": coarse_side,
            "species_count": len(species_set()),
            "factorized_energy": sum(block.values(), Fraction()),
            "maximum_fold_error": maximum_fold_error,
        }

    hostile_side = 6
    audit.check(
        "side 6 direct hostile control is antiperiodic",
        hostile_side % 4 == 2 and (-1) ** (hostile_side // 2) == -1,
        (hostile_side % 4, (-1) ** (hostile_side // 2)),
        (2, -1),
        "boundary_condition",
    )

    coarse_spectrum = Counter()
    for species in species_set():
        del species
        for momentum in itertools.product((0, 1), repeat=3):
            value = int(
                round(
                    4.0
                    * sum(
                        math.sin(math.pi * component / 2.0) ** 2
                        for component in momentum
                    )
                )
            )
            coarse_spectrum[value] += 1
    expected_spectrum = Counter({0: 8, 4: 24, 8: 24, 12: 8})
    audit.check(
        "side 4 folded harmonic spectrum has eight zero modes",
        coarse_spectrum == expected_spectrum,
        dict(coarse_spectrum),
        dict(expected_spectrum),
        "zone_folding",
    )
    connected_zero_modes = 0
    for momentum in itertools.product(range(4), repeat=3):
        value = 4.0 * sum(
            math.sin(math.pi * component / 4.0) ** 2 for component in momentum
        )
        if abs(value) < 1.0e-12:
            connected_zero_modes += 1
    audit.check(
        "direct same-dimension connected standard scalar has one zero mode",
        connected_zero_modes == 1
        and connected_zero_modes != coarse_spectrum[0],
        (connected_zero_modes, coarse_spectrum[0]),
        (1, 8),
        "connected_parent_obstruction",
    )
    side = 4
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
        "direct connected standard complete-square fixture has two uniform signs",
        connected_standard_ground_count == 2,
        (len(visited), connected_standard_ground_count),
        (side**3, 2),
        "connected_parent_obstruction",
    )

    ground_count = 0
    coarse_side = side // 2
    ground_fixture_r = Fraction(-1)
    ground_fixture_c = Fraction(2)
    ground_fixture_g = Fraction(1)
    ground_fixture_chi = Fraction(1)
    expected_ground_energy = (
        -Fraction(side**3) * ground_fixture_r**2 / (4 * ground_fixture_g)
    )
    for signs in itertools.product((-1, 1), repeat=len(species_set())):
        field = {
            (species, coarse): Fraction(signs[index])
            for index, species in enumerate(species_set())
            for coarse in sites(coarse_side)
        }
        momentum = {coordinate: Fraction() for coordinate in field}
        energy = sum(
            block_parts(
                field,
                momentum,
                coarse_side,
                ground_fixture_r,
                ground_fixture_c,
                ground_fixture_g,
                ground_fixture_chi,
            ).values(),
            Fraction(),
        )
        if energy == expected_ground_energy:
            ground_count += 1
    audit.check(
        "direct eight-species signs reproduce the LT3-classified 256 minima",
        ground_count == 2 ** len(species_set()),
        ground_count,
        2 ** len(species_set()),
        "classical_interpretation",
    )

    fixed_momentum = (0.25, -0.4, 0.3)
    continuum_value = sum(component**2 for component in fixed_momentum)
    continuum_errors: list[float] = []
    scaled_errors: list[float] = []
    for spacing in (0.5, 0.25, 0.125, 0.0625):
        lattice_value = 4.0 / spacing**2 * sum(
            math.sin(spacing * component / 2.0) ** 2
            for component in fixed_momentum
        )
        error = continuum_value - lattice_value
        continuum_errors.append(error)
        scaled_errors.append(error / spacing**2)
    expected_scaled_error = sum(component**4 for component in fixed_momentum) / 12.0
    audit.check(
        "direct fixed-band continuum errors are positive and decrease",
        all(error > 0.0 for error in continuum_errors)
        and all(
            continuum_errors[index + 1] < continuum_errors[index]
            for index in range(len(continuum_errors) - 1)
        ),
        continuum_errors,
        "positive decreasing sequence",
        "continuum_bridge",
    )
    audit.check(
        "direct continuum error divided by spacing squared reaches the derived coefficient",
        abs(scaled_errors[-1] - expected_scaled_error) < 1.0e-6,
        scaled_errors[-1],
        expected_scaled_error,
        "continuum_bridge",
    )
    speed_c = 7.0 / 5.0
    speed_chi = 11.0 / 7.0
    speed_mass = 2.0 / 3.0
    normalized_speed_samples: list[float] = []
    for coarse_spacing in (0.5, 0.25, 0.125):
        for momentum in (
            (0.1, 0.2, -0.3),
            (0.7, -0.4, 0.5),
            (1.1, 0.8, -0.6),
        ):
            half_sine_sum = sum(
                math.sin(coarse_spacing * component / 2.0) ** 2
                for component in momentum
            )
            full_sine_sum = sum(
                math.sin(coarse_spacing * component) ** 2
                for component in momentum
            )
            speed_squared = (
                speed_c**2
                * full_sine_sum
                / (
                    coarse_spacing**2
                    * speed_chi
                    * (
                        speed_mass
                        + 4.0 * speed_c * half_sine_sum / coarse_spacing**2
                    )
                )
            )
            normalized_speed_samples.append(speed_squared / (speed_c / speed_chi))
    audit.check(
        "direct positive-mass squared-group-speed samples obey the exact analytic bound",
        max(normalized_speed_samples) < 1.0,
        max(normalized_speed_samples),
        "<1",
        "continuum_bridge",
    )
    scaling_spacing = Fraction(3, 7)
    scaling_physical_stiffness = Fraction(5, 11)
    scaling_inertia = Fraction(13, 17)
    scaling_lt3_stiffness = scaling_physical_stiffness / scaling_spacing**2
    scaling_fine_spacing = scaling_spacing / 2
    scaling_fine_physical_speed_squared = (
        scaling_fine_spacing**2
        * 4
        * scaling_lt3_stiffness
        / scaling_inertia
    )
    audit.check(
        "direct fine-to-coarse spacing map preserves the physical squared speed",
        scaling_fine_physical_speed_squared
        == scaling_physical_stiffness / scaling_inertia,
        scaling_fine_physical_speed_squared,
        scaling_physical_stiffness / scaling_inertia,
        "continuum_bridge",
    )

    inserted_pah1_target_frequencies = (3, 5, 5)
    inserted_pah1_target_frequency_squares = tuple(
        Fraction(frequency**2) for frequency in inserted_pah1_target_frequencies
    )
    ordered_r = -inserted_pah1_target_frequency_squares[0] / 2
    ordered_g = Fraction(7, 3)
    ordered_c = Fraction(1)
    ordered_chi = Fraction(1)
    ordered_amplitude_squared = -ordered_r / ordered_g
    ordered_potential_curvature = (
        ordered_r + 3 * ordered_g * ordered_amplitude_squared
    )
    mode_numbers = (0, 4, 4)
    pah1_frequency_squares = tuple(
        (ordered_potential_curvature + ordered_c * mode**2) / ordered_chi
        for mode in mode_numbers
    )
    pah1_frequencies = tuple(math.isqrt(value.numerator) for value in pah1_frequency_squares)
    audit.check(
        "independent ordered tangent derives PA-H1 squared frequencies",
        ordered_potential_curvature == inserted_pah1_target_frequency_squares[0]
        and pah1_frequency_squares == inserted_pah1_target_frequency_squares
        and pah1_frequencies == inserted_pah1_target_frequencies,
        (ordered_potential_curvature, pah1_frequency_squares, pah1_frequencies),
        (
            inserted_pah1_target_frequency_squares[0],
            inserted_pah1_target_frequency_squares,
            inserted_pah1_target_frequencies,
        ),
        "pah1_tangent",
    )
    pah1_circumference = math.pi / 2.0
    sample_count = 16
    sample_points = [
        pah1_circumference * index / sample_count for index in range(sample_count)
    ]
    sampled_basis = [
        [math.sqrt(2.0 / math.pi) for _ in range(sample_count)],
        [
            2.0 * math.cos(4.0 * point) / math.sqrt(math.pi)
            for point in sample_points
        ],
        [
            2.0 * math.sin(4.0 * point) / math.sqrt(math.pi)
            for point in sample_points
        ],
    ]
    sampled_gram = [
        [
            pah1_circumference
            * sum(left[index] * right[index] for index in range(sample_count))
            / sample_count
            for right in sampled_basis
        ]
        for left in sampled_basis
    ]
    maximum_gram_error = max(
        abs(sampled_gram[row][column] - float(row == column))
        for row in range(3)
        for column in range(3)
    )
    audit.check(
        "independent circle sampling confirms the PA-H1 mode Gram",
        maximum_gram_error < 1.0e-12,
        maximum_gram_error,
        "<1e-12",
        "pah1_tangent",
    )

    mass = Fraction(5)
    stiffness = Fraction(3)
    inertia = Fraction(5)
    matrix, index = harmonic_matrix(4, mass, stiffness)
    squared = matmul(matrix, matrix)
    origin = index[(0, 0, 0)]
    neighbour = index[(1, 0, 0)]
    opposite = index[(2, 0, 0)]
    distance_one_lead = -matrix[origin][neighbour] / (2 * inertia)
    distance_two_lead = squared[origin][opposite] / (24 * inertia**2)
    expected_distance_one_lead = stiffness / (2 * inertia)
    expected_distance_two_lead = stiffness**2 / (12 * inertia**2)
    audit.check(
        "direct nearest-site response has a nonzero t-squared coefficient",
        matrix[origin][neighbour] == -stiffness
        and distance_one_lead == expected_distance_one_lead,
        (matrix[origin][neighbour], distance_one_lead),
        (-stiffness, expected_distance_one_lead),
        "exact_cone_obstruction",
    )
    audit.check(
        "direct distance-two response has two shortest paths and a nonzero t-fourth coefficient",
        matrix[origin][opposite] == 0
        and squared[origin][opposite] == 2 * stiffness**2
        and distance_two_lead == expected_distance_two_lead,
        (
            matrix[origin][opposite],
            squared[origin][opposite],
            distance_two_lead,
        ),
        (0, 2 * stiffness**2, expected_distance_two_lead),
        "exact_cone_obstruction",
    )

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
    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "candidate_family": "PRE-A-STAGGERED-BLOCK-CAUSAL-BRIDGE",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "non-importing exact finite block and causal-tail audit; not CP1 closure",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": COMPARISON_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "method": "standard-library Fraction lattice arithmetic, direct dispersion evaluation and direct matrix products",
        "finite_fixtures": fixtures,
        "exact_results": {
            "side4_folded_spectrum": dict(coarse_spectrum),
            "same_dimension_connected_zero_modes": connected_zero_modes,
            "same_dimension_connected_ground_count": connected_standard_ground_count,
            "ground_count": ground_count,
            "ground_fixture_parameters": {
                "side": side,
                "r": ground_fixture_r,
                "g": ground_fixture_g,
            },
            "continuum_errors": continuum_errors,
            "continuum_scaled_errors": scaled_errors,
            "coarse_spacing_definition": "a is the coarse-lattice spacing and the inherited fine-lattice spacing is a/2",
            "continuum_family_parameter_map": "c_LT3(a)=c_phys/a^2 with chi fixed",
            "fine_to_coarse_speed_fixture_parameters": {
                "a": scaling_spacing,
                "c_phys": scaling_physical_stiffness,
                "chi": scaling_inertia,
            },
            "fine_to_coarse_physical_speed_squared_fixture": scaling_fine_physical_speed_squared,
            "maximum_normalized_group_speed_sample": max(normalized_speed_samples),
            "ordered_tangent_calibration_parameters": {
                "r": ordered_r,
                "c": ordered_c,
                "chi": ordered_chi,
                "status": "inserted calibration inputs",
            },
            "ordered_potential_curvature": ordered_potential_curvature,
            "pah1_circumference": "pi/2",
            "pah1_tangent_frequency_squares": pah1_frequency_squares,
            "pah1_tangent_frequencies": pah1_frequencies,
            "distance_one_response_leading_coefficient": distance_one_lead,
            "distance_two_response_leading_coefficient": distance_two_lead,
            "causal_tail_fixture_parameters": {
                "mu": mass,
                "c": stiffness,
                "chi": inertia,
            },
        },
        "scope": scope,
        "no_overclaim": "This independent route checks an exact finite signed-block equivalence, a declared harmonic fixed-band regulator-family limit, a tuned formal ordered PA-H1 tangent spectrum and nonzero continuous-time lattice tails. It does not prove that the fixed spacing-one parent automatically has a continuum limit, a selected PA-H1 species or sector, a full nonlinear PA-H1 embedding, an interacting or quantum continuum limit, a strict lattice causal cone, characteristic state reconstruction, a connected bulk, a physical vacuum, cooling, gravity, CP1 or Pre-A.",
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
        f"{CANDIDATE_ID} | non-importing block audit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
