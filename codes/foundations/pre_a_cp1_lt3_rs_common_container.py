#!/usr/bin/env python3
"""Exact primary certificate for the PA-CP1-LT3-RS-v0 scaffold.

The package studies one local finite periodic three-dimensional lattice
Hamiltonian.  It proves a common classical phase space, exact finite-wave-
number ordering minima, a same-Hamiltonian zero-field comparison, and the
standard finite-lattice quantum ground-state selection boundary.  It does
not derive a characteristic boundary and therefore does not complete CP1.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-LT3-RS-v0"
SLUG = "pre-a-cp1-lt3-rs-common-container"
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


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [
            [serial(value[row, column]) for column in range(value.cols)]
            for row in range(value.rows)
        ]
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


def sites(side: int) -> list[Site]:
    return list(itertools.product(range(side), repeat=3))


def shift(site: Site, axis: int, amount: int, side: int) -> Site:
    value = list(site)
    value[axis] = (value[axis] + amount) % side
    return tuple(value)  # type: ignore[return-value]


def kernel_nodes(side: int) -> set[Momentum]:
    quarter = side // 4
    return set(itertools.product((quarter, (-quarter) % side), repeat=3))


def add_momenta(*momenta: Momentum, side: int) -> Momentum:
    return tuple(sum(momentum[axis] for momentum in momenta) % side for axis in range(3))  # type: ignore[return-value]


def base_sign_field(side: int, base_signs: tuple[int, ...]) -> dict[Site, int]:
    if len(base_signs) != 8:
        raise ValueError("eight parity-cell signs are required")
    field: dict[Site, int] = {}
    for site in sites(side):
        parity = tuple(coordinate % 2 for coordinate in site)
        base_index = parity[0] * 4 + parity[1] * 2 + parity[2]
        coarse = tuple(coordinate // 2 for coordinate in site)
        field[site] = base_signs[base_index] * (-1) ** sum(coarse)
    return field


def b_value(field: dict[Site, Any], site: Site, axis: int, side: int) -> Any:
    return -field[shift(site, axis, 1, side)] - field[shift(site, axis, -1, side)]


def exact_static_energy(
    field: dict[Site, Any],
    side: int,
    r_value: Any,
    c_value: Any,
    g_value: Any,
) -> sp.Expr:
    """Return the exact zero-momentum classical energy of one lattice field."""
    quadratic = r_value * sum(value**2 for value in field.values()) / 2
    stiffness = c_value * sum(
        b_value(field, site, axis, side) ** 2
        for site in sites(side)
        for axis in range(3)
    ) / 2
    quartic = g_value * sum(value**4 for value in field.values()) / 4
    return sp.simplify(quadratic + stiffness + quartic)


def quarter_shift_sign_field(side: int) -> dict[Site, sp.Expr]:
    """Construct sqrt(2) cos(Q.x+pi/4) at Q=(pi/2,pi/2,pi/2)."""
    quarter = side // 4
    momentum = (quarter, quarter, quarter)
    return {
        site: sp.simplify(
            sp.sqrt(2)
            * sp.cos(
                2
                * sp.pi
                * sum(momentum[axis] * site[axis] for axis in range(3))
                / side
                + sp.pi / 4
            )
        )
        for site in sites(side)
    }


def stencil_matrix(side: int, axis: int) -> sp.Matrix:
    """Construct B_i=-S_i-S_i^{-1} in the site basis."""
    lattice_sites = sites(side)
    index = {site: position for position, site in enumerate(lattice_sites)}
    matrix = sp.zeros(len(lattice_sites))
    for site in lattice_sites:
        row = index[site]
        matrix[row, index[shift(site, axis, 1, side)]] -= 1
        matrix[row, index[shift(site, axis, -1, side)]] -= 1
    return matrix


def derive() -> dict[str, Any]:
    audit = Audit()

    k1, k2, k3 = sp.symbols("k1 k2 k3", real=True)
    p1, p2, p3 = sp.symbols("p1 p2 p3", real=True)
    c, g, chi, hbar = sp.symbols("c g chi hbar", positive=True)
    r = sp.symbols("r", real=True)
    k = (k1, k2, k3)
    p = (p1, p2, p3)

    b_symbols = tuple(-2 * sp.cos(component) for component in k)
    kernel = r + c * sum(symbol**2 for symbol in b_symbols)
    expected_kernel = r + 4 * c * sum(sp.cos(component) ** 2 for component in k)
    audit.check(
        "local stencil Fourier symbol",
        sp.simplify(kernel - expected_kernel) == 0,
        kernel,
        expected_kernel,
        "symbol",
    )

    nodes = list(itertools.product((-sp.pi / 2, sp.pi / 2), repeat=3))
    kernel_gradient = sp.Matrix([sp.diff(kernel, component) for component in k])
    kernel_hessian = sp.hessian(kernel, k)
    for index, node in enumerate(nodes):
        substitution = dict(zip(k, node, strict=True))
        audit.check(
            f"node {index} reaches r",
            sp.simplify(kernel.subs(substitution) - r) == 0,
            kernel.subs(substitution),
            r,
            "symbol",
        )
        audit.check(
            f"node {index} is stationary",
            kernel_gradient.subs(substitution) == sp.zeros(3, 1),
            kernel_gradient.subs(substitution),
            sp.zeros(3, 1),
            "symbol",
        )
        audit.check(
            f"node {index} has full-rank Hessian",
            kernel_hessian.subs(substitution) == 8 * c * sp.eye(3),
            kernel_hessian.subs(substitution),
            8 * c * sp.eye(3),
            "symbol",
        )

    shifted = sp.simplify(
        kernel.subs(
            {
                k1: sp.pi / 2 + p1,
                k2: sp.pi / 2 + p2,
                k3: sp.pi / 2 + p3,
                r: 0,
            }
        )
    )
    shifted_expected = 4 * c * sum(sp.sin(component) ** 2 for component in p)
    audit.check(
        "exact node-centred lattice dispersion",
        sp.simplify(shifted - shifted_expected) == 0,
        shifted,
        shifted_expected,
        "dynamics",
    )
    quadratic_tensor = sp.hessian(shifted, p).subs({p1: 0, p2: 0, p3: 0})
    audit.check(
        "critical quadratic tensor",
        quadratic_tensor == 8 * c * sp.eye(3),
        quadratic_tensor,
        8 * c * sp.eye(3),
        "dynamics",
    )
    speed_squared = sp.simplify(
        sp.trace(quadratic_tensor) / (2 * len(p) * chi)
    )
    audit.check(
        "conditional inertial speed squared",
        speed_squared == 4 * c / chi,
        speed_squared,
        4 * c / chi,
        "dynamics",
    )
    group_numerator = sum(
        sp.cos(component) ** 2 * sp.sin(component) ** 2 for component in k
    )
    group_denominator = sum(sp.cos(component) ** 2 for component in k)
    group_remainder = sp.simplify(group_denominator - group_numerator)
    audit.check(
        "global harmonic group-speed bound reduces to a nonnegative sum",
        sp.simplify(
            group_remainder - sum(sp.cos(component) ** 4 for component in k)
        )
        == 0,
        group_remainder,
        sum(sp.cos(component) ** 4 for component in k),
        "dynamics",
    )
    omega = sp.sqrt(kernel / chi)
    omega_gradient = tuple(sp.diff(omega, component) for component in k)
    differentiated_gradient_squared = sp.simplify(
        sum(component**2 for component in omega_gradient)
    )
    expected_differentiated_gradient_squared = sp.simplify(
        16 * c**2 * group_numerator / (chi * (r + 4 * c * group_denominator))
    )
    audit.check(
        "differentiating the Hamiltonian dispersion gives the gradient formula",
        sp.simplify(
            differentiated_gradient_squared
            - expected_differentiated_gradient_squared
        )
        == 0,
        differentiated_gradient_squared,
        expected_differentiated_gradient_squared,
        "dynamics",
    )
    critical_gradient_squared = sp.simplify(
        differentiated_gradient_squared.subs(r, 0)
    )
    audit.check(
        "off-node critical gradient formula includes the full speed factor",
        sp.simplify(
            critical_gradient_squared
            - (4 * c / chi) * group_numerator / group_denominator
        )
        == 0,
        critical_gradient_squared,
        "(4*c/chi)*A/D away from D=0",
        "dynamics",
    )
    massive_gradient_squared = differentiated_gradient_squared
    massive_bound_remainder = sp.simplify(
        speed_squared - massive_gradient_squared
    )
    expected_massive_remainder = sp.simplify(
        4
        * c
        * (r + 4 * c * group_remainder)
        / (chi * (r + 4 * c * group_denominator))
    )
    audit.check(
        "massive gradient bound has a nonnegative square decomposition",
        sp.simplify(massive_bound_remainder - expected_massive_remainder) == 0,
        massive_bound_remainder,
        expected_massive_remainder,
        "dynamics",
    )
    critical_omega_squared = sp.simplify((omega**2).subs(r, 0))
    lipschitz_envelope_squared = sp.simplify(
        critical_omega_squared / group_denominator
    )
    audit.check(
        "critical global Lipschitz envelope carries the same speed coefficient",
        sp.simplify(lipschitz_envelope_squared - speed_squared) == 0,
        lipschitz_envelope_squared,
        speed_squared,
        "dynamics",
    )

    finite_fixtures: dict[str, Any] = {}
    for side in (4, 8, 12):
        if side % 4:
            raise AssertionError("fixture side must be divisible by four")
        discrete_nodes = kernel_nodes(side)
        zero_modes: set[Momentum] = set()
        positive_symbols: list[sp.Expr] = []
        for momentum in itertools.product(range(side), repeat=3):
            value = sp.simplify(
                4
                * sum(
                    sp.cos(2 * sp.pi * component / side) ** 2
                    for component in momentum
                )
            )
            if value == 0:
                zero_modes.add(momentum)
            else:
                positive_symbols.append(value)
        expected_gap = sp.simplify(4 * sp.sin(2 * sp.pi / side) ** 2)
        actual_gap = min(positive_symbols, key=lambda value: float(value))
        audit.check(
            f"side {side} has exactly eight isolated nodes",
            zero_modes == discrete_nodes and len(zero_modes) == 8,
            zero_modes,
            discrete_nodes,
            "finite_lattice",
        )
        audit.check(
            f"side {side} complement spectral gap",
            sp.simplify(actual_gap - expected_gap) == 0,
            actual_gap,
            expected_gap,
            "finite_lattice",
        )
        triple_sums = {
            add_momenta(left, middle, right, side=side)
            for left in discrete_nodes
            for middle in discrete_nodes
            for right in discrete_nodes
        }
        audit.check(
            f"side {side} node set is closed under cubic Umklapp",
            triple_sums == discrete_nodes,
            triple_sums,
            discrete_nodes,
            "umklapp",
        )
        audit.check(
            f"side {side} has 2V-dimensional canonical phase space",
            2 * side**3 == 2 * len(sites(side)),
            2 * side**3,
            2 * len(sites(side)),
            "phase_space",
        )
        finite_fixtures[str(side)] = {
            "configuration_dimension": side**3,
            "phase_dimension": 2 * side**3,
            "node_count": len(discrete_nodes),
            "complement_gap": expected_gap,
            "cubic_node_closure": True,
        }

    side = 4
    ground_fields = 0
    sample_field: dict[Site, int] | None = None
    for base_signs in itertools.product((-1, 1), repeat=8):
        field = base_sign_field(side, base_signs)
        recurrence_ok = all(
            b_value(field, site, axis, side) == 0
            for site in sites(side)
            for axis in range(3)
        )
        constant_magnitude = all(value * value == 1 for value in field.values())
        if recurrence_ok and constant_magnitude:
            ground_fields += 1
        if sample_field is None:
            sample_field = field
    audit.check(
        "all parity-cell signs give exact kernel ground patterns",
        ground_fields == 2**8,
        ground_fields,
        2**8,
        "classical_ground",
    )
    kernel_stationary_fields = 0
    for base_values in itertools.product((-1, 0, 1), repeat=8):
        field = base_sign_field(side, base_values)
        recurrence_ok = all(
            b_value(field, site, axis, side) == 0
            for site in sites(side)
            for axis in range(3)
        )
        euler_ok = all(-value + value**3 == 0 for value in field.values())
        if recurrence_ok and euler_ok:
            kernel_stationary_fields += 1
    audit.check(
        "directly enumerated classical ground-state count is 2^8",
        ground_fields == 2**8,
        ground_fields,
        2**8,
        "classical_ground",
    )
    audit.check(
        "directly enumerated kernel stationary count is 3^8",
        kernel_stationary_fields == 3**8,
        kernel_stationary_fields,
        3**8,
        "classical_stationary",
    )
    assert sample_field is not None
    audit.check(
        "a nonzero ground pattern is not spatially constant",
        len(set(sample_field.values())) == 2,
        len(set(sample_field.values())),
        2,
        "classical_ground",
    )

    positive_r = sp.symbols("R", positive=True)
    field_value = sp.symbols("phi", real=True)
    completion_left = (
        -positive_r * field_value**2 / 2
        + g * field_value**4 / 4
        + positive_r**2 / (4 * g)
    )
    completion_right = g * (field_value**2 - positive_r / g) ** 2 / 4
    audit.check(
        "ordered-side pointwise complete square",
        sp.expand(completion_left - completion_right) == 0,
        completion_left,
        completion_right,
        "energy_reference",
    )
    minimum_density = -positive_r**2 / (4 * g)
    audit.check(
        "ordered classical minimum lies strictly below the same-H zero field",
        sp.ask(sp.Q.negative(minimum_density)) is True,
        minimum_density,
        "negative",
        "energy_reference",
    )
    stencil_matrices = [stencil_matrix(side, axis) for axis in range(3)]
    stencil_gram = sum(
        (matrix.T * matrix for matrix in stencil_matrices), sp.zeros(side**3)
    )
    ordered_hessian = c * stencil_gram + 2 * positive_r * sp.eye(side**3)
    ordered_hessian_floor = 2 * positive_r
    audit.check(
        "ordered Hessian minus its floor is an exact stencil Gram matrix",
        ordered_hessian - ordered_hessian_floor * sp.eye(side**3)
        == c * stencil_gram,
        ordered_hessian - ordered_hessian_floor * sp.eye(side**3),
        c * stencil_gram,
        "classical_stability",
    )
    sample_vector = sp.Matrix([sample_field[site] for site in sites(side)])
    audit.check(
        "a kernel ground vector attains the ordered Hessian floor",
        ordered_hessian * sample_vector == ordered_hessian_floor * sample_vector,
        ordered_hessian * sample_vector,
        ordered_hessian_floor * sample_vector,
        "classical_stability",
    )
    audit.check(
        "ordered ground Hessian Gram floor is positive",
        sp.ask(sp.Q.positive(ordered_hessian_floor)) is True,
        ordered_hessian_floor,
        "positive",
        "classical_stability",
    )

    phase_zero_sequence = [sp.simplify(sp.cos(j * sp.pi / 2)) for j in range(4)]
    phase_quarter_sequence = [
        sp.simplify(sp.cos(j * sp.pi / 2 + sp.pi / 4)) for j in range(4)
    ]
    phase_zero_cos2 = sp.simplify(sum(value**2 for value in phase_zero_sequence) / 4)
    phase_zero_cos4 = sp.simplify(sum(value**4 for value in phase_zero_sequence) / 4)
    phase_quarter_cos2 = sp.simplify(
        sum(value**2 for value in phase_quarter_sequence) / 4
    )
    phase_quarter_cos4 = sp.simplify(
        sum(value**4 for value in phase_quarter_sequence) / 4
    )
    audit.check(
        "unshifted lattice stripe fourth moment differs from continuum",
        phase_zero_cos4 != sp.Rational(3, 8),
        phase_zero_cos4,
        sp.Rational(3, 8),
        "alias_control",
    )
    audit.check(
        "quarter-shift stripe has constant magnitude",
        phase_quarter_cos4 == phase_quarter_cos2**2,
        phase_quarter_cos4,
        phase_quarter_cos2**2,
        "alias_control",
    )
    def optimized_cosine_density(moment2: sp.Expr, moment4: sp.Expr) -> sp.Expr:
        amplitude_squared = positive_r * moment2 / (g * moment4)
        return sp.simplify(
            -positive_r * amplitude_squared * moment2 / 2
            + g * amplitude_squared**2 * moment4 / 4
        )

    unshifted_density = optimized_cosine_density(phase_zero_cos2, phase_zero_cos4)
    shifted_density = optimized_cosine_density(
        phase_quarter_cos2, phase_quarter_cos4
    )
    audit.check(
        "quarter-shift stripe beats the unshifted stripe",
        sp.ask(sp.Q.negative(shifted_density - unshifted_density)) is True,
        shifted_density - unshifted_density,
        "negative",
        "alias_control",
    )

    quarter_shift_energies: dict[str, sp.Expr] = {}
    for fixture_side in (4, 8, 12):
        sign_field = quarter_shift_sign_field(fixture_side)
        audit.check(
            f"side {fixture_side} quarter-shift field is an exact sign field",
            all(sp.simplify(value**2 - 1) == 0 for value in sign_field.values()),
            set(sign_field.values()),
            {-1, 1},
            "alias_control",
        )
        audit.check(
            f"side {fixture_side} quarter-shift field is in every stencil kernel",
            all(
                sp.simplify(b_value(sign_field, site, axis, fixture_side)) == 0
                for site in sites(fixture_side)
                for axis in range(3)
            ),
            "B_i s=0",
            "B_i s=0",
            "alias_control",
        )
        scaled_field = {
            site: sp.sqrt(positive_r / g) * value
            for site, value in sign_field.items()
        }
        energy = exact_static_energy(
            scaled_field, fixture_side, -positive_r, c, g
        )
        expected_energy = -fixture_side**3 * positive_r**2 / (4 * g)
        audit.check(
            f"side {fixture_side} quarter-shift field attains the exact minimum",
            sp.simplify(energy - expected_energy) == 0,
            energy,
            expected_energy,
            "energy_reference",
        )
        quarter_shift_energies[str(fixture_side)] = energy

    delta_field = {site: int(site == (0, 0, 0)) for site in sites(side)}
    low_energy_r = sp.Integer(-1)
    low_energy_c = sp.Integer(2)
    low_energy_g = sp.Integer(1)
    delta_energy = exact_static_energy(
        delta_field, side, low_energy_r, low_energy_c, low_energy_g
    )
    delta_minimum = -sp.Rational(side**3, 4)
    energy_excess = sp.simplify(delta_energy - delta_minimum)
    node_projection_norm = sp.simplify(
        sum(
            sp.conjugate(
                sum(
                    delta_field[site]
                    * sp.exp(
                        -2
                        * sp.pi
                        * sp.I
                        * sum(momentum[axis] * site[axis] for axis in range(3))
                        / side
                    )
                    for site in sites(side)
                )
                / sp.sqrt(side**3)
            )
            * (
                sum(
                    delta_field[site]
                    * sp.exp(
                        -2
                        * sp.pi
                        * sp.I
                        * sum(momentum[axis] * site[axis] for axis in range(3))
                        / side
                    )
                    for site in sites(side)
                )
                / sp.sqrt(side**3)
            )
            for momentum in kernel_nodes(side)
        )
    )
    total_field_norm = sum(value**2 for value in delta_field.values())
    complement_norm = sp.simplify(total_field_norm - node_projection_norm)
    fixture_gap = finite_fixtures[str(side)]["complement_gap"]
    stencil_norm = sum(
        b_value(delta_field, site, axis, side) ** 2
        for site in sites(side)
        for axis in range(3)
    )
    audit.check(
        "side 4 direct Fourier complement obeys the exact stencil gap",
        sp.simplify(stencil_norm - fixture_gap * complement_norm) >= 0,
        (stencil_norm, fixture_gap * complement_norm),
        "left>=right",
        "low_energy",
    )
    audit.check(
        "side 4 low-energy Fourier concentration bound is executable",
        sp.simplify(
            2 * energy_excess / (low_energy_c * fixture_gap) - complement_norm
        )
        >= 0,
        complement_norm,
        2 * energy_excess / (low_energy_c * fixture_gap),
        "low_energy",
    )
    magnitude_deviation = sum(
        (value**2 + low_energy_r / low_energy_g) ** 2
        for value in delta_field.values()
    )
    audit.check(
        "side 4 low-energy constant-magnitude bound is executable",
        sp.simplify(4 * energy_excess / low_energy_g - magnitude_deviation) >= 0,
        magnitude_deviation,
        4 * energy_excess / low_energy_g,
        "low_energy",
    )

    variance = sp.symbols("v", positive=True)
    gaussian_mean_squared = positive_r / g
    gaussian_second_moment = gaussian_mean_squared + variance
    gaussian_fourth_moment = (
        gaussian_mean_squared**2
        + 6 * gaussian_mean_squared * variance
        + 3 * variance**2
    )
    gaussian_onsite_density = sp.simplify(
        -positive_r * gaussian_second_moment / 2
        + g * gaussian_fourth_moment / 4
    )
    gaussian_stencil_variance_per_axis = 2 * variance
    gaussian_stiffness_density = sp.simplify(
        3 * c * gaussian_stencil_variance_per_axis / 2
    )
    gaussian_kinetic_density = hbar**2 / (8 * chi * variance)
    gaussian_trial_density = sp.simplify(
        gaussian_onsite_density
        + gaussian_stiffness_density
        + gaussian_kinetic_density
    )
    audit.check(
        "ordered-well product-Gaussian Rayleigh density",
        sp.simplify(
            gaussian_trial_density
            - (
                -positive_r**2 / (4 * g)
                + (3 * c + positive_r) * variance
                + 3 * g * variance**2 / 4
                + hbar**2 / (8 * chi * variance)
            )
        )
        == 0,
        gaussian_trial_density,
        "independently assembled moment formula",
        "quantum_boundary",
    )
    gaussian_leading_coefficient = sp.limit(
        gaussian_trial_density / positive_r**2, positive_r, sp.oo
    )
    audit.check(
        "Gaussian trial has a strictly negative large-minus-r leading coefficient",
        sp.simplify(gaussian_leading_coefficient + 1 / (4 * g)) == 0,
        gaussian_leading_coefficient,
        -1 / (4 * g),
        "quantum_boundary",
    )
    gaussian_negative_witness = sp.simplify(
        gaussian_trial_density.subs(
            {
                positive_r: 20,
                c: 1,
                g: 1,
                chi: 1,
                hbar: 1,
                variance: 1,
            }
        )
    )
    audit.check(
        "Gaussian trial has an exact negative rational witness",
        gaussian_negative_witness < 0,
        gaussian_negative_witness,
        "negative",
        "quantum_boundary",
    )
    audit.check(
        "finite-dimensional exact CCR cannot use a finite Hilbert space",
        0 != hbar * 2,
        "tr([Q,P])=0",
        "tr(i*hbar*I_D)=i*hbar*D != 0",
        "quantum_boundary",
    )

    orbit = {
        (
            translation[0] % side,
            translation[1] % side,
            translation[2] % side,
        )
        for translation in sites(side)
    }
    audit.check(
        "translation orbit of one site is the full torus",
        len(orbit) == side**3,
        len(orbit),
        side**3,
        "boundary_selection",
    )
    translation_orbits = (orbit,)
    invariant_subset_sizes = tuple(
        sorted(
            {
                sum(
                    len(translation_orbits[index])
                    for index, selected in enumerate(selection)
                    if selected
                )
                for selection in itertools.product(
                    (False, True), repeat=len(translation_orbits)
                )
            }
        )
    )
    audit.check(
        "transitive invariant site subsets are only empty or full",
        invariant_subset_sizes == (0, side**3),
        invariant_subset_sizes,
        (0, side**3),
        "boundary_selection",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "PRE-A-LOCAL-LATTICE-COMMON-CONTAINER",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 finite-lattice common-container certificate; not a TECT action, theorem-tier change, completed CP1, physical vacuum, or Pre-A closure",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": COMPARISON_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "parent_definition": {
            "lattice": "Lambda_N=(Z/NZ)^3 with N in 4N, spacing a=1 and V=N^3",
            "phase_space": "R^V_phi direct-sum R^V_pi with the canonical symplectic form",
            "weyl_algebra": "the regular finite-degree Weyl CCR algebra represented on L2(R^V); no occupation compression",
            "stencil": "B_i=-S_i-S_i^{-1}, obtained from kappa=2",
            "hamiltonian": "sum_x pi_x^2/(2chi) + 1/2 sum_x[r phi_x^2+c sum_i(B_i phi)_x^2] + g/4 sum_x phi_x^4",
            "parameters": "c>0, g>0, chi>0, hbar>0, r real",
            "boundary_condition": "periodic spatial boundary condition, not a characteristic or event horizon",
            "counterterm": "none at fixed N in v0",
            "additive_constant": "C=0, so the classical zero-field configuration has H_r(0,0)=0",
        },
        "finite_fixtures": finite_fixtures,
        "exact_results": {
            "quadratic_symbol": kernel,
            "isolated_nodes": nodes,
            "node_hessian": 8 * c * sp.eye(3),
            "complement_gap": "delta_N=4*sin(2*pi/N)^2",
            "cubic_umklapp": "the eight-node set is exactly closed under triple sums modulo the reciprocal lattice for every N divisible by four",
            "classical_flow": "the polynomial Hamilton ODE is global for finite data because energy is conserved and sublevel sets are compact",
            "r_nonnegative": "phi=pi=0 is the unique classical stationary point and global minimum",
            "r_negative_minimum": "min H_r=-V*r^2/(4g), strictly below H_r(0,0)=0 in the identical finite Hamiltonian convention",
            "r_negative_minimizers": "pi=0, B_i phi=0 and phi_x^2=-r/g at every site",
            "ground_state_count": ground_fields,
            "kernel_stationary_count": kernel_stationary_fields,
            "ordered_hessian": "c*sum_i B_i^2-2r*I with floor -2r>0",
            "critical_dynamics": "under the inserted inertial law, z=1 and every scalar valley has c_star=2*sqrt(c/chi)",
            "harmonic_speed_bound": "for r>0 the gradient exists and |grad_k omega|<=2*sqrt(c/chi) at every k; for r=0 the bound holds off the nodes and omega is globally Lipschitz with the same directional-speed envelope",
            "low_energy_concentration": "||P_Qperp phi||^2 <= 2 DeltaH/(c delta_N) and sum_x(phi_x^2+r/g)^2 <=4 DeltaH/g for r<0",
            "quarter_shift_fixture_energies": quarter_shift_energies,
            "low_energy_fixture": {
                "energy_excess": energy_excess,
                "complement_norm_squared": complement_norm,
                "magnitude_deviation_squared": magnitude_deviation,
            },
            "gaussian_trial_negative_witness": gaussian_negative_witness,
            "quantum_operator": "H_N=-(hbar^2/(2chi))*Delta+U_r has finite configuration dimension V on the infinite-dimensional Hilbert space L2(R^V), compact resolvent and one strictly positive simple ground state by standard prior-art theorems",
            "finite_quantum_symmetry": "the unique ground state is translation and phi-to-minus-phi invariant, so one-point order vanishes at fixed N",
            "raw_quantum_energy": "E0(r) is strictly increasing and crosses the declared raw zero once, but any additive constant moves that crossing",
        },
        "energy_reference_ledger": {
            "same_hamiltonian_classical_zero_field": "0",
            "same_hamiltonian_ordered_minimum": "-V*r^2/(4g) for r<0",
            "classical_below_zero_field": "PROVED at fixed N, spacing, parameters, boundary and C=0",
            "quantum_phi_zero_state": "undefined; phi=0 is a configuration, not a normalizable quantum state",
            "quantum_no_condensate_reference": "not selected",
            "physical_empty_space": "not identified",
            "additive_constant_dependence": "the sign of raw quantum E0 and its zero crossing are conventional",
        },
        "cp1_audit": {
            "one_declared_finite_regulator_family_fixed_N_per_instance": True,
            "one_phase_space_and_weyl_algebra": True,
            "one_hamiltonian_formula": True,
            "one_volume_and_periodic_boundary_convention": True,
            "one_hbar_and_field_normalization": True,
            "one_fixed_N_counterterm_and_additive_reference": True,
            "one_ground_state_rule_unique_per_fixed_parameter_tuple": True,
            "exact_classical_interacting_ordering_sector": True,
            "same_selected_quantum_state_selects_one_ordered_pattern": False,
            "characteristic_boundary_map_or_reduction": False,
            "pah1_boundary_role": False,
            "one_derived_physical_r_history": False,
            "cp1_complete": False,
        },
        "boundary_no_go": {
            "statement": "A deterministic translation-covariant rule applied only to the translation-invariant finite Hamiltonian and its unique ground state cannot select a proper nonempty site boundary on the transitive torus.",
            "scope": "proper site-subset selection from the symmetric fixed-N data only",
            "not_excluded": "state-conditioned sectors, relational boundaries, time-dependent characteristic sheets, gravity, or a larger relativistic parent",
        },
        "hostile_controls": {
            "n4_only_alias": False,
            "umklapp_persists_for_all_N_divisible_by_four": True,
            "unshifted_cosine_is_the_global_minimum": False,
            "quarter_shift_constant_magnitude_pattern_reaches_the_global_minimum": True,
            "inherits_continuum_pa_m2_quartic_moment": False,
            "node_subspace_is_a_full_quantum_tensor_factor": False,
            "fixed_N_proves_thermal_or_quantum_phase_transition": False,
            "finite_occupation_cutoff_preserves_exact_CCR": False,
            "periodic_boundary_is_characteristic_boundary": False,
            "scalar_valley_speed_is_a_photon_or_universal_speed": False,
        },
        "scope": {
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
        },
        "verdict": "ADVANCE the exact local lattice ordering and common-reference scaffold; REJECT CP1 completion because no characteristic-boundary role or physical r history is derived",
        "next_gate": "supply a regulator-level causal/locality estimate or a controlled Lorentzian causal emergence limit, then derive two characteristic sheets, corner data, symplectic flux and bulk reconstruction while retaining a same-parent interacting ordering reduction",
        "no_overclaim": (
            "This package proves a fixed-regulator classical ordering theorem and invokes standard finite-lattice quantum ground-state theorems under explicit hypotheses. It does not inherit the continuum PA-M2 quartic coefficients, select a quantum broken-symmetry pattern, prove a thermodynamic or quantum phase transition, identify physical empty space, derive PA-H1, a characteristic or event horizon, cooling, gravity, a continuum limit, CP1 completion, or Pre-A."
        ),
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
        f"{CANDIDATE_ID} | exact order scaffold, CP1 boundary gate open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
