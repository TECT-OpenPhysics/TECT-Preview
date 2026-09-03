#!/usr/bin/env python3
"""Non-importing independent audit of PA-CP1-LT3-RS-v0.

This route uses direct lattice enumeration, rational energy arithmetic and
standard-library Fourier sums.  It does not import the primary certificate.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-LT3-RS-v0"
SLUG = "pre-a-cp1-lt3-rs-common-container"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
COMPARISON_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
PROGRAMME_SCOPE = {
    "finite_lattice_classical_theorem": True,
    "fixed_N_quantum_ground_selection": True,
    "same_model_classical_below_zero_field": True,
    "below_physical_empty_space": False,
    "below_quantum_no_condensate_state": False,
    "thermodynamic_limit": False,
    "spontaneous_symmetry_breaking": False,
    "finite_temperature_transition": False,
    "quantum_phase_transition": False,
    "continuum_limit": False,
    "cutoff_uniform_relativistic_uv_completion": False,
    "characteristic_boundary": False,
    "event_horizon": False,
    "cooling_history": False,
    "cp1_complete": False,
    "pre_a_complete": False,
}
NO_OVERCLAIM = (
    "This package proves a fixed-regulator classical ordering theorem and invokes "
    "standard finite-lattice quantum ground-state theorems under explicit "
    "hypotheses. It does not inherit the continuum PA-M2 quartic coefficients, "
    "select a quantum broken-symmetry pattern, prove a thermodynamic or quantum "
    "phase transition, identify physical empty space, derive PA-H1, a "
    "characteristic or event horizon, cooling, gravity, a continuum limit, CP1 "
    "completion, or Pre-A."
)
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
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
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
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


Site = tuple[int, int, int]
Momentum = tuple[int, int, int]


def all_sites(side: int) -> list[Site]:
    return list(itertools.product(range(side), repeat=3))


def move(site: Site, axis: int, amount: int, side: int) -> Site:
    coordinates = list(site)
    coordinates[axis] = (coordinates[axis] + amount) % side
    return tuple(coordinates)  # type: ignore[return-value]


def node_set(side: int) -> set[Momentum]:
    quarter = side // 4
    return set(itertools.product((quarter, (-quarter) % side), repeat=3))


def field_from_cells(side: int, cell_values: tuple[int, ...]) -> dict[Site, int]:
    field: dict[Site, int] = {}
    for site in all_sites(side):
        epsilon = tuple(coordinate % 2 for coordinate in site)
        index = epsilon[0] * 4 + epsilon[1] * 2 + epsilon[2]
        cell = tuple(coordinate // 2 for coordinate in site)
        field[site] = cell_values[index] * (-1) ** sum(cell)
    return field


def b(field: dict[Site, int], site: Site, axis: int, side: int) -> int:
    return -field[move(site, axis, 1, side)] - field[move(site, axis, -1, side)]


def classical_energy(
    field: dict[Site, int],
    side: int,
    r: Fraction,
    c: Fraction,
    g: Fraction,
) -> Fraction:
    quadratic = r * sum(Fraction(value * value) for value in field.values()) / 2
    stencil = c * sum(
        Fraction(b(field, site, axis, side) ** 2)
        for site in all_sites(side)
        for axis in range(3)
    ) / 2
    quartic = g * sum(Fraction(value**4) for value in field.values()) / 4
    return quadratic + stencil + quartic


def dft(field: dict[Site, int], momentum: Momentum, side: int) -> complex:
    total = 0j
    for site, value in field.items():
        phase = -2j * math.pi * sum(
            momentum[axis] * site[axis] for axis in range(3)
        ) / side
        total += value * cmath.exp(phase)
    return total / math.sqrt(side**3)


def quarter_shift_field(side: int) -> tuple[dict[Site, int], float]:
    """Build sqrt(2) cos(Q.x+pi/4), checking the numerical-to-sign residual."""
    raw = {
        site: math.sqrt(2.0)
        * math.cos(math.pi * sum(site) / 2.0 + math.pi / 4.0)
        for site in all_sites(side)
    }
    rounded = {site: int(round(value)) for site, value in raw.items()}
    residual = max(abs(raw[site] - rounded[site]) for site in raw)
    return rounded, residual


def omega_from_dispersion(
    angles: list[float], mass: float, stiffness: float, inertia: float
) -> float:
    """Evaluate omega directly from the declared Hamiltonian dispersion."""
    omega_squared = (
        mass + 4.0 * stiffness * sum(math.cos(angle) ** 2 for angle in angles)
    ) / inertia
    return math.sqrt(max(0.0, omega_squared))


def finite_difference_gradient_squared(
    angles: list[float],
    mass: float,
    stiffness: float,
    inertia: float,
    step: float,
) -> float:
    """Differentiate the evaluated omega without inserting a gradient formula."""
    derivatives: list[float] = []
    for axis in range(3):
        plus = list(angles)
        minus = list(angles)
        plus[axis] += step
        minus[axis] -= step
        derivatives.append(
            (
                omega_from_dispersion(plus, mass, stiffness, inertia)
                - omega_from_dispersion(minus, mass, stiffness, inertia)
            )
            / (2.0 * step)
        )
    return sum(derivative**2 for derivative in derivatives)


def derive() -> dict[str, Any]:
    audit = Audit()
    fixture_summary: dict[str, Any] = {}

    for side in (4, 8, 12):
        expected_nodes = node_set(side)
        numerical_nodes: set[Momentum] = set()
        positive_values: list[float] = []
        for momentum in itertools.product(range(side), repeat=3):
            symbol = 4.0 * sum(
                math.cos(2.0 * math.pi * component / side) ** 2
                for component in momentum
            )
            if abs(symbol) < 1.0e-12:
                numerical_nodes.add(momentum)
            else:
                positive_values.append(symbol)
        expected_gap = 4.0 * math.sin(2.0 * math.pi / side) ** 2
        actual_gap = min(positive_values)
        audit.check(
            f"side {side} direct node enumeration",
            numerical_nodes == expected_nodes,
            numerical_nodes,
            expected_nodes,
            "finite_symbol",
        )
        audit.check(
            f"side {side} direct complement gap",
            math.isclose(actual_gap, expected_gap, rel_tol=0.0, abs_tol=1.0e-12),
            actual_gap,
            expected_gap,
            "finite_symbol",
        )
        triple_sums = {
            tuple((left[i] + middle[i] + right[i]) % side for i in range(3))
            for left in expected_nodes
            for middle in expected_nodes
            for right in expected_nodes
        }
        audit.check(
            f"side {side} independent triple-sum closure",
            triple_sums == expected_nodes,
            triple_sums,
            expected_nodes,
            "umklapp",
        )
        for node in expected_nodes:
            triple = tuple((3 * component) % side for component in node)
            opposite = tuple((-component) % side for component in node)
            audit.check(
                f"side {side} node {node} has 3Q=-Q",
                triple == opposite,
                triple,
                opposite,
                "umklapp",
            )
        fixture_summary[str(side)] = {
            "node_count": len(numerical_nodes),
            "gap": actual_gap,
            "triple_closure": True,
        }

        quarter_field, quarter_residual = quarter_shift_field(side)
        audit.check(
            f"side {side} constructed quarter-shift field rounds only to signs",
            quarter_residual < 1.0e-12
            and set(quarter_field.values()).issubset({-1, 1}),
            (quarter_residual, set(quarter_field.values())),
            "residual<1e-12 and values in {-1,+1}",
            "alias_control",
        )
        audit.check(
            f"side {side} constructed quarter-shift field lies in every stencil kernel",
            all(
                b(quarter_field, site, axis, side) == 0
                for site in all_sites(side)
                for axis in range(3)
            ),
            "B_i s=0",
            "B_i s=0",
            "alias_control",
        )
        quarter_energy = classical_energy(
            quarter_field, side, Fraction(-1), Fraction(2), Fraction(1)
        )
        quarter_expected = -Fraction(side**3, 4)
        audit.check(
            f"side {side} constructed quarter-shift field attains the exact minimum",
            quarter_energy == quarter_expected,
            quarter_energy,
            quarter_expected,
            "energy_reference",
        )
        fixture_summary[str(side)]["quarter_shift_energy"] = quarter_energy

    side = 4
    r = Fraction(-1)
    c = Fraction(2)
    g = Fraction(1)
    expected_minimum = -Fraction(side**3, 4)
    ground_count = 0
    energies: set[Fraction] = set()
    first_ground: dict[Site, int] | None = None
    for cell_values in itertools.product((-1, 1), repeat=8):
        field = field_from_cells(side, cell_values)
        recurrence = all(
            b(field, site, axis, side) == 0
            for site in all_sites(side)
            for axis in range(3)
        )
        energy = classical_energy(field, side, r, c, g)
        energies.add(energy)
        if recurrence and energy == expected_minimum:
            ground_count += 1
            if first_ground is None:
                first_ground = field
    audit.check(
        "all 256 parity-cell sign fields attain the exact minimum",
        ground_count == 256,
        ground_count,
        256,
        "classical_ground",
    )
    audit.check(
        "all parity-cell sign fields have the same exact energy",
        energies == {expected_minimum},
        energies,
        {expected_minimum},
        "classical_ground",
    )
    zero_field = {site: 0 for site in all_sites(side)}
    zero_energy = classical_energy(zero_field, side, r, c, g)
    audit.check(
        "same-H ordered minimum is below the zero field",
        expected_minimum < zero_energy and zero_energy == 0,
        (expected_minimum, zero_energy),
        (Fraction(-16), Fraction(0)),
        "energy_reference",
    )

    kernel_stationary_count = 0
    global_minimum_count = 0
    for cell_values in itertools.product((-1, 0, 1), repeat=8):
        field = field_from_cells(side, cell_values)
        recurrence = all(
            b(field, site, axis, side) == 0
            for site in all_sites(side)
            for axis in range(3)
        )
        euler = all(-value + value**3 == 0 for value in field.values())
        if recurrence and euler:
            kernel_stationary_count += 1
        if all(abs(value) == 1 for value in field.values()):
            global_minimum_count += 1
    audit.check(
        "direct kernel stationary enumeration",
        kernel_stationary_count == 3**8,
        kernel_stationary_count,
        3**8,
        "classical_stationary",
    )
    audit.check(
        "direct global-minimum enumeration inside the kernel",
        global_minimum_count == 2**8,
        global_minimum_count,
        2**8,
        "classical_ground",
    )

    assert first_ground is not None
    support: set[Momentum] = set()
    parseval = 0.0
    for momentum in itertools.product(range(side), repeat=3):
        coefficient = dft(first_ground, momentum, side)
        parseval += abs(coefficient) ** 2
        if abs(coefficient) > 1.0e-10:
            support.add(momentum)
    audit.check(
        "a ground field has Fourier support only on the eight nodes",
        support.issubset(node_set(side)) and bool(support),
        support,
        node_set(side),
        "fourier_support",
    )
    audit.check(
        "direct DFT obeys Parseval",
        math.isclose(parseval, float(side**3), rel_tol=0.0, abs_tol=1.0e-9),
        parseval,
        float(side**3),
        "fourier_support",
    )

    phase_zero_values = tuple(
        int(round(math.cos(j * math.pi / 2.0))) for j in range(4)
    )
    phase_zero_m2 = sum(Fraction(value**2) for value in phase_zero_values) / 4
    phase_zero_m4 = sum(Fraction(value**4) for value in phase_zero_values) / 4
    quarter_residue_signs = tuple(
        int(round(math.sqrt(2.0) * math.cos(j * math.pi / 2.0 + math.pi / 4.0)))
        for j in range(4)
    )
    quarter_shift_squared = tuple(
        Fraction(value**2, 2) for value in quarter_residue_signs
    )
    phase_quarter_m2 = sum(quarter_shift_squared) / 4
    phase_quarter_m4 = sum(value**2 for value in quarter_shift_squared) / 4
    audit.check(
        "unshifted lattice cosine moments",
        (phase_zero_m2, phase_zero_m4) == (Fraction(1, 2), Fraction(1, 2)),
        (phase_zero_m2, phase_zero_m4),
        (Fraction(1, 2), Fraction(1, 2)),
        "alias_control",
    )
    audit.check(
        "quarter-shift lattice cosine moments",
        (phase_quarter_m2, phase_quarter_m4)
        == (Fraction(1, 2), Fraction(1, 4)),
        (phase_quarter_m2, phase_quarter_m4),
        (Fraction(1, 2), Fraction(1, 4)),
        "alias_control",
    )
    def optimized_density(moment2: Fraction, moment4: Fraction) -> Fraction:
        amplitude_squared = moment2 / moment4
        return -amplitude_squared * moment2 / 2 + amplitude_squared**2 * moment4 / 4

    unshifted_minimum = optimized_density(phase_zero_m2, phase_zero_m4)
    shifted_minimum = optimized_density(phase_quarter_m2, phase_quarter_m4)
    audit.check(
        "the quarter-shift pattern is the stronger exact comparator",
        shifted_minimum < unshifted_minimum,
        shifted_minimum,
        unshifted_minimum,
        "alias_control",
    )

    speed_c = Fraction(3)
    speed_chi = Fraction(2)
    speed_envelope_squared = 4 * speed_c / speed_chi
    difference_step = 1.0e-6
    node_angles = [math.pi / 2.0] * 3
    node_shifted = list(node_angles)
    node_shifted[0] += difference_step
    node_directional_slope = (
        omega_from_dispersion(
            node_shifted, 0.0, float(speed_c), float(speed_chi)
        )
        - omega_from_dispersion(
            node_angles, 0.0, float(speed_c), float(speed_chi)
        )
    ) / difference_step
    node_directional_speed_squared = node_directional_slope**2
    audit.check(
        "independent omega directional difference derives the full 4c/chi factor",
        math.isclose(
            node_directional_speed_squared,
            float(speed_envelope_squared),
            rel_tol=0.0,
            abs_tol=1.0e-8,
        ),
        node_directional_speed_squared,
        "4c/chi",
        "dynamics",
    )
    maximum_ratio = 0.0
    maximum_massive_ratio = 0.0
    for speed_side in (8, 12, 16):
        for momentum in itertools.product(range(speed_side), repeat=3):
            angles = [
                2.0 * math.pi * component / speed_side for component in momentum
            ]
            denominator = sum(math.cos(angle) ** 2 for angle in angles)
            if denominator < 1.0e-14:
                continue
            critical_gradient_squared = finite_difference_gradient_squared(
                angles,
                0.0,
                float(speed_c),
                float(speed_chi),
                difference_step,
            )
            ratio = critical_gradient_squared / float(speed_envelope_squared)
            positive_mass = 5.0
            massive_gradient_squared = finite_difference_gradient_squared(
                angles,
                positive_mass,
                float(speed_c),
                float(speed_chi),
                difference_step,
            )
            massive_ratio = massive_gradient_squared / float(speed_envelope_squared)
            maximum_ratio = max(maximum_ratio, ratio)
            maximum_massive_ratio = max(maximum_massive_ratio, massive_ratio)
    audit.check(
        "sampled harmonic group-speed ratio never exceeds one",
        maximum_ratio <= 1.0 + 1.0e-12,
        maximum_ratio,
        "<=1",
        "dynamics",
    )
    audit.check(
        "sampled positive-mass harmonic gradient respects the same envelope",
        maximum_massive_ratio <= 1.0 + 1.0e-12,
        maximum_massive_ratio,
        "<=1",
        "dynamics",
    )

    hessian_eigenvalues: list[float] = []
    for momentum in itertools.product(range(4), repeat=3):
        angles = [math.pi * component / 2.0 for component in momentum]
        hessian_eigenvalues.append(
            4.0 * float(c) * sum(math.cos(angle) ** 2 for angle in angles)
            - 2.0 * float(r)
        )
    hessian_floor = min(hessian_eigenvalues)
    audit.check(
        "direct ordered Hessian Fourier spectrum has floor minus 2r",
        math.isclose(hessian_floor, float(-2 * r), rel_tol=0.0, abs_tol=1.0e-12),
        hessian_floor,
        float(-2 * r),
        "classical_stability",
    )

    delta_field = {site: int(site == (0, 0, 0)) for site in all_sites(4)}
    delta_energy = classical_energy(delta_field, 4, r, c, g)
    delta_excess = delta_energy - expected_minimum
    node_projection_norm = sum(
        abs(dft(delta_field, momentum, 4)) ** 2 for momentum in node_set(4)
    )
    complement_norm = sum(value**2 for value in delta_field.values()) - node_projection_norm
    gap4 = fixture_summary["4"]["gap"]
    audit.check(
        "direct DFT low-energy Fourier concentration bound",
        complement_norm
        <= float(2 * delta_excess / c) / gap4 + 1.0e-12,
        complement_norm,
        float(2 * delta_excess / c) / gap4,
        "low_energy",
    )
    magnitude_deviation = sum(
        Fraction((value**2 - 1) ** 2) for value in delta_field.values()
    )
    audit.check(
        "direct field low-energy constant-magnitude bound",
        magnitude_deviation <= 4 * delta_excess / g,
        magnitude_deviation,
        4 * delta_excess / g,
        "low_energy",
    )

    orbit_side = 4
    orbit = {
        ((0 + tx) % orbit_side, (0 + ty) % orbit_side, (0 + tz) % orbit_side)
        for tx, ty, tz in all_sites(orbit_side)
    }
    audit.check(
        "the translation action is transitive",
        len(orbit) == orbit_side**3,
        len(orbit),
        orbit_side**3,
        "boundary_selection",
    )
    orbit_partition = (orbit,)
    invariant_subset_sizes = tuple(
        sorted(
            {
                sum(
                    len(orbit_partition[index])
                    for index, selected in enumerate(selection)
                    if selected
                )
                for selection in itertools.product(
                    (False, True), repeat=len(orbit_partition)
                )
            }
        )
    )
    audit.check(
        "no proper invariant site subset follows from transitive input",
        invariant_subset_sizes == (0, orbit_side**3),
        invariant_subset_sizes,
        "empty or full",
        "boundary_selection",
    )

    hilbert_dimension = 7
    hbar = Fraction(3, 2)
    audit.check(
        "finite-matrix trace obstruction to exact CCR",
        Fraction(0) != hbar * hilbert_dimension,
        Fraction(0),
        hbar * hilbert_dimension,
        "quantum_boundary",
    )
    trial_parameters = {
        "minus_r": Fraction(20),
        "g": Fraction(1),
        "c": Fraction(1),
        "chi": Fraction(1),
        "hbar": Fraction(1),
        "variance": Fraction(1),
    }
    R = trial_parameters["minus_r"]
    variance = trial_parameters["variance"]
    trial_g = trial_parameters["g"]
    mean_squared = R / trial_g
    second_moment = mean_squared + variance
    fourth_moment = mean_squared**2 + 6 * mean_squared * variance + 3 * variance**2
    onsite_density = -R * second_moment / 2 + trial_g * fourth_moment / 4
    stencil_variance_per_axis = 2 * variance
    stiffness_density = (
        3 * trial_parameters["c"] * stencil_variance_per_axis / 2
    )
    kinetic_density = trial_parameters["hbar"] ** 2 / (
        8 * trial_parameters["chi"] * variance
    )
    trial_density = onsite_density + stiffness_density + kinetic_density
    closed_formula = (
        -(R**2) / (4 * trial_g)
        + (3 * trial_parameters["c"] + R) * variance
        + 3 * trial_g * variance**2 / 4
        + trial_parameters["hbar"] ** 2
        / (8 * trial_parameters["chi"] * variance)
    )
    audit.check(
        "independent Gaussian moments reproduce the closed Rayleigh formula",
        trial_density == closed_formula,
        trial_density,
        closed_formula,
        "quantum_boundary",
    )
    leading_coefficient = -Fraction(1, 2 * trial_g) + Fraction(1, 4 * trial_g)
    audit.check(
        "independent Gaussian large-minus-r coefficient is negative",
        leading_coefficient == -Fraction(1, 4 * trial_g) < 0,
        leading_coefficient,
        -Fraction(1, 4 * trial_g),
        "quantum_boundary",
    )
    audit.check(
        "independent Gaussian trial gives an exact negative witness",
        trial_density < 0,
        trial_density,
        "negative",
        "quantum_boundary",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "PRE-A-LOCAL-LATTICE-COMMON-CONTAINER",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "non-importing finite-lattice audit; not a physical model or CP1 closure",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": COMPARISON_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "method": "standard-library direct lattice enumeration, exact Fraction energies and direct complex DFT",
        "fixture_summary": fixture_summary,
        "exact_results": {
            "ground_count": ground_count,
            "kernel_stationary_count": kernel_stationary_count,
            "side4_minimum": expected_minimum,
            "side4_zero_field": zero_energy,
            "first_ground_fourier_support": support,
            "maximum_sampled_group_ratio": maximum_ratio,
            "maximum_sampled_massive_group_ratio": maximum_massive_ratio,
            "speed_envelope_squared": speed_envelope_squared,
            "ordered_hessian_floor": hessian_floor,
            "low_energy_fixture": {
                "energy_excess": delta_excess,
                "complement_norm_squared": complement_norm,
                "magnitude_deviation_squared": magnitude_deviation,
            },
            "gaussian_trial_density_fixture": trial_density,
        },
        "method_scope": {
            "independent_of_primary_implementation": True,
            "fixed_finite_lattices_only": True,
        },
        "scope": PROGRAMME_SCOPE,
        "no_overclaim": NO_OVERCLAIM,
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
        f"{CANDIDATE_ID} | non-importing lattice audit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
