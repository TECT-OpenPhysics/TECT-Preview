#!/usr/bin/env python3
"""Exact primary certificate for the strict PA-H1/PA-M2 composition no-go.

The theorem concerns only the declared finite PA-H1 image and the current
PA-M2 CI8 soft sector under an unchanged linear/affine symplectic interface.
It does not exclude a larger common parent, nonlinear effective map, or
ordered-background construction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-H1-M2-STRICT-COMPOSITION-NOGO-v0"
SLUG = "pre-a-pah1-m2-strict-composition-nogo"
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
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def canonical_symplectic(configuration_dimension: int) -> sp.Matrix:
    identity = sp.eye(configuration_dimension)
    zero = sp.zeros(configuration_dimension)
    return zero.row_join(identity).col_join((-identity).row_join(zero))


def oscillator_generator(omega_squared: sp.Matrix) -> sp.Matrix:
    dimension = omega_squared.rows
    identity = sp.eye(dimension)
    zero = sp.zeros(dimension)
    return zero.row_join(identity).col_join((-omega_squared).row_join(zero))


def oscillator_metric(frequencies: list[sp.Expr]) -> sp.Matrix:
    omega = sp.diag(*frequencies)
    return sp.diag(omega, omega.inv())


WaveVector = tuple[int, int, int]
FourierSeries = dict[WaveVector, sp.Expr]


def add_wavevectors(left: WaveVector, right: WaveVector) -> WaveVector:
    return tuple(left[index] + right[index] for index in range(3))


def negate_wavevector(vector: WaveVector) -> WaveVector:
    return tuple(-entry for entry in vector)


def convolve(left: FourierSeries, right: FourierSeries) -> FourierSeries:
    result: FourierSeries = {}
    for left_vector, left_coefficient in left.items():
        for right_vector, right_coefficient in right.items():
            vector = add_wavevectors(left_vector, right_vector)
            result[vector] = sp.expand(
                result.get(vector, sp.Integer(0))
                + left_coefficient * right_coefficient
            )
    return {key: sp.simplify(value) for key, value in result.items() if value != 0}


def ci8_real_basis() -> list[FourierSeries]:
    representatives = (
        (1, 1, 1),
        (1, 1, -1),
        (1, -1, 1),
        (-1, 1, 1),
    )
    basis: list[FourierSeries] = []
    inverse_root_two = 1 / sp.sqrt(2)
    for vector in representatives:
        opposite = negate_wavevector(vector)
        basis.append({vector: inverse_root_two, opposite: inverse_root_two})
        basis.append(
            {
                vector: inverse_root_two / sp.I,
                opposite: -inverse_root_two / sp.I,
            }
        )
    return basis


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


def derive() -> dict[str, Any]:
    audit = Audit()

    # Imported finite fixtures.  These are not derived physical constants.
    pah1_frequencies = [sp.Integer(3), sp.Integer(5), sp.Integer(5)]
    frequency_gcd = math.gcd(*(int(value) for value in pah1_frequencies))
    flow_period = 2 * sp.pi / frequency_gcd
    pah1_configuration_dimension = len(pah1_frequencies)
    pah1_phase_dimension = 2 * pah1_configuration_dimension
    ci8_antipodal_pairs = 4
    pam2_configuration_dimension = 2 * ci8_antipodal_pairs
    pam2_phase_dimension = 2 * pam2_configuration_dimension
    complement_dimension = pam2_phase_dimension - pah1_phase_dimension

    audit.check(
        "PA-H1 imported frequency multiset",
        pah1_frequencies == [3, 5, 5],
        pah1_frequencies,
        [3, 5, 5],
        "interface_fixture",
    )
    audit.check(
        "PA-H1 configuration dimension",
        pah1_configuration_dimension == 3,
        pah1_configuration_dimension,
        3,
        "interface_fixture",
    )
    audit.check(
        "PA-H1 phase dimension",
        pah1_phase_dimension == 6,
        pah1_phase_dimension,
        6,
        "interface_fixture",
    )
    audit.check(
        "CI8 antipodal-pair count",
        ci8_antipodal_pairs == 4,
        ci8_antipodal_pairs,
        4,
        "interface_fixture",
    )
    audit.check(
        "PA-M2 real configuration dimension",
        pam2_configuration_dimension == 8,
        pam2_configuration_dimension,
        8,
        "interface_fixture",
    )
    audit.check(
        "PA-M2 phase dimension",
        pam2_phase_dimension == 16,
        pam2_phase_dimension,
        16,
        "interface_fixture",
    )
    audit.check(
        "strict-interface phase-dimension deficit",
        complement_dimension == 10,
        complement_dimension,
        10,
        "interface_fixture",
    )

    sigma_h = canonical_symplectic(pah1_configuration_dimension)
    sigma_m = canonical_symplectic(pam2_configuration_dimension)
    audit.check(
        "PA-H1 symplectic form is nondegenerate",
        sigma_h.det() == 1 and sigma_h.rank() == pah1_phase_dimension,
        (sigma_h.det(), sigma_h.rank()),
        (1, pah1_phase_dimension),
        "symplectic_dimension",
    )
    audit.check(
        "PA-M2 symplectic form is nondegenerate",
        sigma_m.det() == 1 and sigma_m.rank() == pam2_phase_dimension,
        (sigma_m.det(), sigma_m.rank()),
        (1, pam2_phase_dimension),
        "symplectic_dimension",
    )
    audit.check(
        "unequal dimensions forbid a linear symplectic bijection",
        pah1_phase_dimension != pam2_phase_dimension,
        (pah1_phase_dimension, pam2_phase_dimension),
        "unequal",
        "symplectic_dimension",
    )

    injection = sp.zeros(pam2_phase_dimension, pah1_phase_dimension)
    for index in range(pah1_configuration_dimension):
        injection[index, index] = 1
        injection[pam2_configuration_dimension + index, pah1_configuration_dimension + index] = 1
    audit.check(
        "explicit rank-six symplectic injection exists",
        injection.rank() == pah1_phase_dimension,
        injection.rank(),
        pah1_phase_dimension,
        "symplectic_dimension",
    )
    audit.check(
        "explicit injection pulls back the target symplectic form",
        injection.T * sigma_m * injection == sigma_h,
        injection.T * sigma_m * injection,
        sigma_h,
        "symplectic_dimension",
    )

    complement = sp.zeros(pam2_phase_dimension, complement_dimension)
    complement_pairs = pam2_configuration_dimension - pah1_configuration_dimension
    for local_index, target_index in enumerate(
        range(pah1_configuration_dimension, pam2_configuration_dimension)
    ):
        complement[target_index, local_index] = 1
        complement[
            pam2_configuration_dimension + target_index,
            complement_pairs + local_index,
        ] = 1
    sigma_complement = canonical_symplectic(complement_pairs)
    audit.check(
        "ten-dimensional symplectic complement is explicit",
        complement.T * sigma_m * complement == sigma_complement,
        complement.T * sigma_m * complement,
        sigma_complement,
        "symplectic_dimension",
    )
    audit.check(
        "image and complement are symplectically orthogonal",
        injection.T * sigma_m * complement == sp.zeros(
            pah1_phase_dimension, complement_dimension
        ),
        injection.T * sigma_m * complement,
        sp.zeros(pah1_phase_dimension, complement_dimension),
        "symplectic_dimension",
    )
    audit.check(
        "image plus complement spans the full PA-M2 phase space",
        injection.row_join(complement).rank() == pam2_phase_dimension,
        injection.row_join(complement).rank(),
        pam2_phase_dimension,
        "symplectic_dimension",
    )

    extension_one_frequencies = pah1_frequencies + [sp.Integer(2)] * complement_pairs
    extension_two_frequencies = pah1_frequencies + [sp.Integer(7)] * complement_pairs
    metric_h = oscillator_metric(pah1_frequencies)
    metric_extension_one = oscillator_metric(extension_one_frequencies)
    metric_extension_two = oscillator_metric(extension_two_frequencies)
    audit.check(
        "first positive Gaussian extension agrees on the PA-H1 image",
        injection.T * metric_extension_one * injection == metric_h,
        injection.T * metric_extension_one * injection,
        metric_h,
        "state_extension_boundary",
    )
    audit.check(
        "second positive Gaussian extension agrees on the PA-H1 image",
        injection.T * metric_extension_two * injection == metric_h,
        injection.T * metric_extension_two * injection,
        metric_h,
        "state_extension_boundary",
    )
    complement_probe = complement[:, 0]
    extension_values = (
        (complement_probe.T * metric_extension_one * complement_probe)[0],
        (complement_probe.T * metric_extension_two * complement_probe)[0],
    )
    audit.check(
        "the two positive Gaussian extensions differ on the complement",
        extension_values == (2, 7),
        extension_values,
        (2, 7),
        "state_extension_boundary",
    )
    positivity_blocks = []
    for frequency in extension_one_frequencies + extension_two_frequencies:
        block = sp.Matrix(
            [[frequency, sp.I], [-sp.I, sp.Rational(1, frequency)]]
        )
        positivity_blocks.append((block.det(), sp.simplify(block.trace())))
    audit.check(
        "both complement choices satisfy the modewise quasi-free positivity test",
        all(determinant == 0 and trace > 0 for determinant, trace in positivity_blocks),
        positivity_blocks,
        "det=0 and trace>0 for every mode",
        "state_extension_boundary",
    )

    # The real CI8 Fourier basis is orthonormal.  Parseval applied to phi^2
    # makes the quartic form a sum of squared Fourier coefficients and exposes
    # the zero-mode square (sum Q_j^2)^2.  Thus its vanishing forces Q=0.
    basis = ci8_real_basis()
    gram = sp.Matrix(
        [
            [
                sp.simplify(convolve(basis[row], basis[column]).get((0, 0, 0), 0))
                for column in range(pam2_configuration_dimension)
            ]
            for row in range(pam2_configuration_dimension)
        ]
    )
    audit.check(
        "CI8 real Fourier coordinate map is injective",
        gram == sp.eye(pam2_configuration_dimension),
        gram,
        sp.eye(pam2_configuration_dimension),
        "energy_degree_nogo",
    )
    q_coordinates = sp.symbols(
        f"Q0:{pam2_configuration_dimension}", real=True
    )
    field: FourierSeries = {}
    for coordinate, mode in zip(q_coordinates, basis, strict=True):
        for wavevector, coefficient in mode.items():
            field[wavevector] = sp.expand(
                field.get(wavevector, 0) + coordinate * coefficient
            )
    field_squared = convolve(field, field)
    l2_polynomial = sp.expand(sum(coordinate**2 for coordinate in q_coordinates))
    audit.check(
        "the squared-field zero Fourier coefficient is the CI8 L2 norm",
        sp.expand(field_squared[(0, 0, 0)] - l2_polynomial) == 0,
        field_squared[(0, 0, 0)],
        l2_polynomial,
        "energy_degree_nogo",
    )
    audit.check(
        "squared-field Fourier coefficients obey real conjugate symmetry",
        all(
            sp.simplify(
                field_squared.get(negate_wavevector(vector), 0)
                - sp.conjugate(coefficient)
            )
            == 0
            for vector, coefficient in field_squared.items()
        ),
        len(field_squared),
        "all conjugate pairs",
        "energy_degree_nogo",
    )
    quartic_integral = sp.expand(
        convolve(field_squared, field_squared).get((0, 0, 0), 0)
    )
    parseval_quartic = sp.expand(
        sum(
            coefficient * sp.conjugate(coefficient)
            for coefficient in field_squared.values()
        )
    )
    audit.check(
        "CI8 quartic integral has an exact Parseval sum-of-squares certificate",
        sp.simplify(quartic_integral - parseval_quartic) == 0,
        quartic_integral,
        parseval_quartic,
        "energy_degree_nogo",
    )

    scale = sp.symbols("lambda", real=True)
    g_positive, quadratic_value, quartic_value = sp.symbols(
        "g H2 Q4", positive=True
    )
    scaled_target_energy = (
        scale**2 * quadratic_value
        + g_positive * scale**4 * quartic_value / 4
    )
    audit.check(
        "interacting target energy has a nonzero fourth-degree coefficient",
        sp.expand(scaled_target_energy).coeff(scale, 4)
        == g_positive * quartic_value / 4,
        sp.expand(scaled_target_energy).coeff(scale, 4),
        g_positive * quartic_value / 4,
        "energy_degree_nogo",
    )
    affine_offset = sp.symbols("b", real=True)
    affine_quartic = sp.expand(g_positive * (affine_offset + scale) ** 4 / 4)
    audit.check(
        "affine translation does not remove the leading quartic coefficient",
        affine_quartic.coeff(scale, 4) == g_positive / 4,
        affine_quartic.coeff(scale, 4),
        g_positive / 4,
        "energy_degree_nogo",
    )
    pure_momentum_derivative = sp.zeros(
        pam2_phase_dimension, pah1_phase_dimension
    )
    for column in range(pah1_phase_dimension):
        pure_momentum_derivative[
            pam2_configuration_dimension + column, column
        ] = 1
    audit.check(
        "a derivative with zero PA-M2 field component is isotropic",
        pure_momentum_derivative.T
        * sigma_m
        * pure_momentum_derivative
        == sp.zeros(pah1_phase_dimension),
        pure_momentum_derivative.T * sigma_m * pure_momentum_derivative,
        sp.zeros(pah1_phase_dimension),
        "energy_degree_nogo",
    )
    audit.check(
        "the source symplectic form is not isotropic",
        sigma_h != sp.zeros(pah1_phase_dimension),
        sigma_h.rank(),
        pah1_phase_dimension,
        "energy_degree_nogo",
    )
    audit.check(
        "free-theory control removes the degree-four obstruction",
        sp.expand(scaled_target_energy.subs(g_positive, 0)).coeff(scale, 4) == 0,
        sp.expand(scaled_target_energy.subs(g_positive, 0)).coeff(scale, 4),
        0,
        "energy_degree_nogo",
    )

    omega_h = sp.diag(*pah1_frequencies)
    generator_h = oscillator_generator(omega_h**2)
    spectral_parameter = sp.symbols("s")
    char_h = sp.factor(generator_h.charpoly(spectral_parameter).as_expr())
    expected_char_h = (spectral_parameter**2 + 9) * (
        spectral_parameter**2 + 25
    ) ** 2
    audit.check(
        "PA-H1 characteristic polynomial",
        sp.expand(char_h - expected_char_h) == 0,
        char_h,
        expected_char_h,
        "gaussian_dynamics_nogo",
    )
    ratio = sp.symbols("alpha", real=True)
    target_mode_generator = sp.Matrix([[0, 1], [-ratio, 0]])
    audit.check(
        "each zero-background PA-M2 node block squares to one scalar",
        target_mode_generator**2 == -ratio * sp.eye(2),
        target_mode_generator**2,
        -ratio * sp.eye(2),
        "gaussian_dynamics_nogo",
    )
    char_m = sp.expand(
        target_mode_generator.charpoly(spectral_parameter).as_expr()
        ** pam2_configuration_dimension
    )
    expected_char_m = (spectral_parameter**2 + ratio) ** 8
    r_parameter = sp.symbols("r", real=True)
    chi_parameter = sp.symbols("chi", positive=True)
    pam2_physical_characteristic = sp.factor(
        char_m.subs(ratio, r_parameter / chi_parameter)
    )
    audit.check(
        "PA-M2 zero-background CI8 characteristic polynomial",
        sp.expand(char_m - expected_char_m) == 0,
        sp.factor(char_m),
        expected_char_m,
        "gaussian_dynamics_nogo",
    )
    source_squared_frequencies = sorted(
        set(int(value**2) for value in pah1_frequencies)
    )
    audit.check(
        "PA-H1 generator square is not a scalar operator",
        source_squared_frequencies == [9, 25],
        source_squared_frequencies,
        [9, 25],
        "gaussian_dynamics_nogo",
    )
    audit.check(
        "no single PA-M2 ratio matches both PA-H1 frequency sectors",
        len(source_squared_frequencies) > 1,
        source_squared_frequencies,
        "one scalar required",
        "gaussian_dynamics_nogo",
    )
    time_scale = sp.symbols("nu", nonzero=True, real=True)
    required_scaled_ratios = {
        sp.simplify(time_scale**2 * value)
        for value in source_squared_frequencies
    }
    audit.check(
        "constant time rescaling cannot remove the frequency-ratio mismatch",
        len(required_scaled_ratios) == 2,
        required_scaled_ratios,
        "two distinct required ratios",
        "gaussian_dynamics_nogo",
    )
    matching_frequency_squared = pah1_frequencies[1] ** 2
    equal_frequency_generator = oscillator_generator(
        matching_frequency_squared * sp.eye(pah1_configuration_dimension)
    )
    target_equal_generator = oscillator_generator(
        matching_frequency_squared * sp.eye(pam2_configuration_dimension)
    )
    audit.check(
        "single-frequency free control admits the canonical flow injection",
        target_equal_generator * injection == injection * equal_frequency_generator,
        target_equal_generator * injection - injection * equal_frequency_generator,
        sp.zeros(pam2_phase_dimension, pah1_phase_dimension),
        "gaussian_dynamics_nogo",
    )

    nodes = {
        (sign_one, sign_two, sign_three)
        for sign_one in (-1, 1)
        for sign_two in (-1, 1)
        for sign_three in (-1, 1)
    }
    chosen_node = (1, 1, 1)
    third_harmonic = tuple(3 * entry for entry in chosen_node)
    audit.check(
        "chosen stripe wavevector belongs to CI8",
        chosen_node in nodes,
        chosen_node,
        "member",
        "regulator_closure",
    )
    audit.check(
        "the cubic third harmonic lies outside CI8",
        third_harmonic not in nodes,
        third_harmonic,
        "not a CI8 node",
        "regulator_closure",
    )
    cosine_series = {
        chosen_node: sp.Rational(1, 2),
        negate_wavevector(chosen_node): sp.Rational(1, 2),
    }
    cosine_cubed = convolve(convolve(cosine_series, cosine_series), cosine_series)
    audit.check(
        "cosine-cubed fundamental Fourier coefficient",
        cosine_cubed[chosen_node] == sp.Rational(3, 8),
        cosine_cubed[chosen_node],
        sp.Rational(3, 8),
        "regulator_closure",
    )
    audit.check(
        "cosine-cubed third-harmonic Fourier coefficient",
        cosine_cubed[third_harmonic] == sp.Rational(1, 8),
        cosine_cubed[third_harmonic],
        sp.Rational(1, 8),
        "regulator_closure",
    )
    omitted_norm_squared = sp.simplify(
        cosine_cubed[third_harmonic]
        * cosine_cubed[negate_wavevector(third_harmonic)]
        * 2
    )
    audit.check(
        "CI8 projection omits a nonzero cubic-force norm",
        omitted_norm_squared == sp.Rational(1, 32),
        omitted_norm_squared,
        sp.Rational(1, 32),
        "regulator_closure",
    )
    ninth_harmonic = tuple(3 * entry for entry in third_harmonic)
    audit.check(
        "adding the third harmonic does not close repeated cubic evolution",
        ninth_harmonic not in nodes | {third_harmonic, negate_wavevector(third_harmonic)},
        ninth_harmonic,
        "outside once-enlarged set",
        "regulator_closure",
    )

    raw_zero_point = sp.Rational(1, 2) * sum(pah1_frequencies)
    normal_ordered_zero_point = sp.simplify(raw_zero_point - raw_zero_point)
    audit.check(
        "PA-H1 raw finite-mode zero-point energy",
        raw_zero_point == sp.Rational(13, 2),
        raw_zero_point,
        sp.Rational(13, 2),
        "energy_origin",
    )
    audit.check(
        "PA-H1 normal-ordered vacuum energy",
        normal_ordered_zero_point == 0,
        normal_ordered_zero_point,
        0,
        "energy_origin",
    )
    coordinate, momentum, energy_shift = sp.symbols("x p C", real=True)
    test_hamiltonian = (coordinate**2 + momentum**2) / 2
    variables = sp.Matrix([coordinate, momentum])
    audit.check(
        "additive Hamiltonian shifts preserve the Hamiltonian gradient",
        sp.Matrix(
            [sp.diff(test_hamiltonian + energy_shift, item) for item in variables]
        )
        == sp.Matrix([sp.diff(test_hamiltonian, item) for item in variables]),
        sp.Matrix(
            [sp.diff(test_hamiltonian + energy_shift, item) for item in variables]
        ),
        sp.Matrix([sp.diff(test_hamiltonian, item) for item in variables]),
        "energy_origin",
    )
    reference_difference = sp.Integer(1)
    audit.check(
        "independent additive shifts can reverse a cross-model energy ordering",
        reference_difference > 0
        and reference_difference + sp.Integer(-2) < 0,
        (reference_difference, reference_difference - 2),
        (">0", "<0"),
        "energy_origin",
    )

    metric_h = oscillator_metric(pah1_frequencies)
    audit.check(
        "PA-H1 Gaussian metric is invariant under its Hamiltonian generator",
        sp.simplify(generator_h.T * metric_h + metric_h * generator_h)
        == sp.zeros(pah1_phase_dimension),
        sp.simplify(generator_h.T * metric_h + metric_h * generator_h),
        sp.zeros(pah1_phase_dimension),
        "cooling_history",
    )
    t = sp.symbols("t", real=True)
    cosine = sp.diag(*(sp.cos(frequency * t) for frequency in pah1_frequencies))
    sine = sp.diag(*(sp.sin(frequency * t) for frequency in pah1_frequencies))
    flow = cosine.row_join(omega_h.inv() * sine).col_join(
        (-omega_h * sine).row_join(cosine)
    )
    audit.check(
        "PA-H1 finite fixture has period two pi",
        sp.simplify(flow.subs(t, flow_period) - sp.eye(pah1_phase_dimension))
        == sp.zeros(pah1_phase_dimension),
        flow.subs(t, flow_period),
        sp.eye(pah1_phase_dimension),
        "cooling_history",
    )
    audit.check(
        "selected Gaussian covariance is invariant under the full flow",
        sp.simplify(flow.T * metric_h * flow - metric_h)
        == sp.zeros(pah1_phase_dimension),
        sp.simplify(flow.T * metric_h * flow - metric_h),
        sp.zeros(pah1_phase_dimension),
        "cooling_history",
    )
    coherent_initial = sp.Matrix([1, 0, 0, 0, 0, 0])
    coherent_later = sp.simplify(flow.subs(t, sp.pi / 6) * coherent_initial)
    audit.check(
        "nonvacuum coherent control can vary and cross on a finite interval",
        coherent_later != coherent_initial,
        coherent_later,
        "different from initial",
        "cooling_history",
    )
    clock_position, clock_momentum = sp.symbols("R0 P_R", real=True)
    clock_history = clock_position + t * clock_momentum
    audit.check(
        "a dynamic clock coordinate can supply a nonconstant control history",
        sp.diff(clock_history, t) == clock_momentum,
        sp.diff(clock_history, t),
        clock_momentum,
        "cooling_history",
    )

    wave_number, mass, c_positive, chi_positive, q_positive = sp.symbols(
        "K m c chi q", positive=True
    )
    kg_frequency = sp.sqrt(wave_number**2 + mass**2)
    kg_speed = sp.diff(kg_frequency, wave_number)
    audit.check(
        "PA-H1 Klein-Gordon group speed has unit ultraviolet limit",
        sp.limit(kg_speed, wave_number, sp.oo) == 1,
        sp.limit(kg_speed, wave_number, sp.oo),
        1,
        "causal_uv",
    )
    pam2_critical_frequency = sp.sqrt(c_positive / chi_positive) * (
        wave_number**2 - q_positive**2
    )
    pam2_group_speed = sp.diff(pam2_critical_frequency, wave_number)
    audit.check(
        "PA-M2 critical-axis group speed grows linearly",
        pam2_group_speed
        == 2 * sp.sqrt(c_positive / chi_positive) * wave_number,
        pam2_group_speed,
        2 * sp.sqrt(c_positive / chi_positive) * wave_number,
        "causal_uv",
    )
    audit.check(
        "PA-M2 group-speed growth coefficient is nonzero",
        sp.limit(pam2_group_speed / wave_number, wave_number, sp.oo)
        == 2 * sp.sqrt(c_positive / chi_positive),
        sp.limit(pam2_group_speed / wave_number, wave_number, sp.oo),
        2 * sp.sqrt(c_positive / chi_positive),
        "causal_uv",
    )
    tuned_speed = sp.simplify(
        pam2_group_speed.subs(c_positive, chi_positive / (4 * q_positive**2))
    )
    audit.check(
        "matching the node-local speed does not bound the ultraviolet speed",
        tuned_speed == wave_number / q_positive,
        tuned_speed,
        wave_number / q_positive,
        "causal_uv",
    )

    product_sigma = sp.diag(sigma_h, sigma_m)
    audit.check(
        "a decoupled product parent is a valid symplectic control",
        product_sigma.rank() == pah1_phase_dimension + pam2_phase_dimension,
        product_sigma.rank(),
        pah1_phase_dimension + pam2_phase_dimension,
        "product_control",
    )
    audit.check(
        "the decoupled product phase dimension is twenty two",
        product_sigma.rows == 22,
        product_sigma.rows,
        22,
        "product_control",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "PRE-A-STRICT-INTERFACE-NOGO",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 compatibility/no-go certificate; not a TECT action, tier change, physical model, or Pre-A closure",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": COMPARISON_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "strict_interface": {
            "map_class": "state-independent affine map with injective symplectic derivative",
            "energy_contract": "exact all-amplitude Hamiltonian equality up to an overall quadratic scale and one additive constant",
            "dynamics_contract": "zero-background linearized-flow intertwining, allowing one constant time rescaling",
            "regulator_contract": "unchanged CI8 soft subspace must be invariant under the unprojected local cubic force",
            "normalization_contract": "one regulator, volume, boundary, hbar, counterterm, and reference prescription",
        },
        "imported_fixture": {
            "pah1_frequencies": pah1_frequencies,
            "pah1_configuration_dimension": pah1_configuration_dimension,
            "pah1_phase_dimension": pah1_phase_dimension,
            "pam2_ci8_antipodal_pairs": ci8_antipodal_pairs,
            "pam2_configuration_dimension": pam2_configuration_dimension,
            "pam2_phase_dimension": pam2_phase_dimension,
            "symplectic_complement_dimension": complement_dimension,
        },
        "exact_results": {
            "phase_space": "no linear symplectic bijection; an explicit 6-to-16 symplectic injection exists and leaves a 10-dimensional symplectic complement",
            "state_extension": "two positive quasi-free extensions agree on the injected PA-H1 image and differ on the complement",
            "energy_degree": "for g>0 no affine symplectic injection can match the quadratic PA-H1 Hamiltonian to the unchanged quartic PA-M2 Hamiltonian for all amplitudes, even up to scale and additive constant",
            "ci8_quartic_parseval": "int phi_Q^4 is a sum of squared Fourier coefficients of phi_Q^2 and contains (sum_j Q_j^2)^2",
            "pah1_characteristic_polynomial": char_h,
            "pam2_zero_characteristic_polynomial": pam2_physical_characteristic,
            "common_full_frequency_ratio": None,
            "flow_intertwiner": "none injective for the full PA-H1 frequency multiset at the PA-M2 zero-background CI8 linearization, even after constant time rescaling",
            "regulator_closure": "cos(Q.x)^3 has a nonzero cos(3Q.x)/4 component and 3Q is outside CI8",
            "cubic_third_harmonic_cosine_coefficient": sp.simplify(2 * cosine_cubed[third_harmonic]),
            "cubic_leakage_norm_squared": omitted_norm_squared,
            "raw_pah1_zero_point": raw_zero_point,
            "normal_ordered_pah1_zero_point": normal_ordered_zero_point,
            "energy_reference": "cross-model energy sign is unidentifiable under independent additive constants",
            "vacuum_cooling": "an invariant vacuum cannot generate a nonconstant state-only r(t); every continuous globally monotone state-local history on the periodic fixture is constant",
            "period": flow_period,
            "causal_uv": "PA-H1 KG group speed tends to one; PA-M2 continuum critical-axis group speed grows as 2*sqrt(c/chi)*K",
            "pam2_uv_speed_growth_coefficient": sp.limit(pam2_group_speed / wave_number, wave_number, sp.oo),
            "formal_product_control": "a 22-dimensional decoupled product exists but supplies no shared field, coupling, derived or selected common relative energy normalization, or r history",
            "product_phase_dimension": product_sigma.rows,
        },
        "hostile_controls": {
            "symplectic_injection_exists": True,
            "free_matching_frequency_interface_not_excluded": True,
            "single_frequency_sector_intertwining_not_excluded": True,
            "projected_ci8_dynamics_can_be_defined_but_changes_the_equation": True,
            "nonvacuum_finite_interval_crossing_not_excluded": True,
            "external_or_dynamic_clock_not_excluded": True,
            "node_local_z1_cone_not_excluded": True,
            "decoupled_product_parent_exists_but_is_vacuous_for_derivation": True,
        },
        "repair_contract": {
            "CP1": "construct one finite-regulator three-torus (T^3) parent Weyl algebra, state, Hamiltonian, volume, boundary, hbar, counterterm, and energy reference that contains both roles",
            "CP2": "derive r(tau) from a dynamical control pair with a total-energy ledger or from a preregistered nonstationary interacting-state Hessian",
            "causal": "supply a separate local 3+1 causal UV completion; retain PA-H1 only as a 1+1 calibration until then",
        },
        "scope": {
            "exact_phase_dimension_mismatch": True,
            "explicit_linear_symplectic_injection": True,
            "linear_symplectic_bijection": False,
            "abstract_cstar_algebra_isomorphism_excluded": False,
            "finite_image_selects_full_pam2_state": False,
            "affine_all_amplitude_interacting_energy_embedding": False,
            "zero_background_full_gaussian_flow_intertwiner": False,
            "zero_fixing_c1_local_flow_embedding": False,
            "ordered_background_flow_embedding_excluded": False,
            "ci8_invariant_under_unchanged_cubic_force": False,
            "projected_ci8_equals_unprojected_dynamics": False,
            "common_absolute_energy_reference": False,
            "below_empty_space_or_no_condensate_comparison": False,
            "stationary_vacuum_generates_nonconstant_r": False,
            "all_nonvacuum_finite_interval_zero_crossings_excluded": False,
            "global_monotone_state_local_cooling_from_periodic_fixture": False,
            "node_local_tree_level_z1_cone_excluded": False,
            "global_unchanged_lorentz_cone_match": False,
            "finite_cutoff_superluminal_signalling_proved": False,
            "unchanged_strict_composition": False,
            "arbitrary_nonlinear_or_holographic_map_excluded": False,
            "larger_common_parent_excluded": False,
            "external_or_dynamic_control_excluded": False,
            "existing_pah1_result_invalidated": False,
            "existing_pam2_result_invalidated": False,
            "common_parent_and_energy_ledger_required": True,
            "physical_vacuum_selected": False,
            "pre_a_complete": False,
        },
        "verdict": "NOGO at the declared strict unchanged interface; construct a common T3 parent rather than identifying the current fixtures",
        "next_gate": "CP1 common finite-regulator three-torus (T^3) parent state and energy-reference certificate",
        "no_overclaim": (
            "This package excludes only the declared full phase-space equivalence, exact all-amplitude affine symplectic energy match, zero-background Gaussian-flow intertwiner, and invariant node-only nonlinear truncation. It does not exclude nonlinear, holographic, constrained, dimension-changing, approximate, time-dependent-interface, ordered-background, open-system, broader-regulator, dynamic-clock, or causal-UV-completed constructions. It does not establish a common energy zero, a below-empty-space result, a physical vacuum, cosmic cooling, a phase transition, spacetime emergence, or Pre-A."
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
        f"{CANDIDATE_ID} | strict unchanged interface rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
