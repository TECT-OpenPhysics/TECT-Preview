#!/usr/bin/env python3
"""Non-importing audit for the A13 joint source-potential reduction.

This route uses alias-free physical-grid quadrature, one-dimensional
Gauss-Hermite integration, and independent Fourier-support fixtures.  It does
not import the primary audit or its numerical outputs.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import platform
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.1"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_joint_source_potential_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-independent-joint-source-potential-reduction-v1.1" / "result.json"


def file_hash(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def commit_id() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def record(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})


def coefficient_values(parameters: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    alpha = float(parameters["alpha_X"])
    beta = float(parameters["beta_X"])
    return (
        float(parameters["cJJ"]) * alpha * alpha / denominator,
        float(parameters["cJK"]) * alpha * beta / denominator,
        float(parameters["cKK"]) * beta * beta / denominator,
    )


def pauli_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def current_map(field: np.ndarray, tangent: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    rho = float(np.real(np.vdot(field, field)))
    safe = rho + float(parameters["rho_regularizer"])
    a_value, b_value, c_value = coefficient_values(parameters)
    drho = 2.0 * float(np.real(np.vdot(field, tangent)))
    output = np.zeros(3, dtype=np.complex128)
    for generator in pauli_generators():
        transformed = generator @ field
        moment = float(np.real(np.vdot(field, transformed)))
        current = 2.0 * float(np.real(np.vdot(transformed, tangent)))
        covariant = current - (moment / safe) * drho
        p_vector = 2.0 * transformed
        v_vector = 2.0 * (transformed - (moment / safe) * field)
        output += (a_value * current + b_value * covariant) * p_vector
        output += (b_value * current + c_value * covariant) * v_vector
    return output


def production_ramer_obstruction_independent(
    parameters: dict[str, Any], seed: int, quadrature_points: int, nelson_exponent: float
) -> dict[str, Any]:
    """Independent Pauli-current/quadrature falsifier for a one-shot Ramer map."""

    modes = (("zero", 0), ("cos", 1), ("sin", 1), ("cos", 2), ("sin", 2))
    dimension = 30
    rng = np.random.default_rng(seed)
    direction = rng.normal(size=dimension)
    direction /= np.linalg.norm(direction) / math.sqrt(dimension)
    sample = 2.0 * np.pi * np.arange(quadrature_points, dtype=np.float64) / quadrature_points
    alpha = 2.0 * np.pi / float(parameters["Lx"])
    basis: list[np.ndarray] = []
    derivative_basis: list[np.ndarray] = []
    roots: list[np.ndarray] = []
    z0 = np.asarray(parameters["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    internal_mass = np.diag(np.asarray(parameters["family_masses"], dtype=np.float64))
    internal_mass += float(parameters["k_lock"]) * (np.eye(3) - projector)
    for kind, index in modes:
        if kind == "zero":
            basis.append(np.ones(quadrature_points, dtype=np.float64))
            derivative_basis.append(np.zeros(quadrature_points, dtype=np.float64))
        elif kind == "cos":
            basis.append(math.sqrt(2.0) * np.cos(index * sample))
            derivative_basis.append(-math.sqrt(2.0) * alpha * index * np.sin(index * sample))
        else:
            basis.append(math.sqrt(2.0) * np.sin(index * sample))
            derivative_basis.append(math.sqrt(2.0) * alpha * index * np.cos(index * sample))
        wave_number = alpha * index
        symbol = (
            float(parameters["r"])
            + float(parameters["Z"]) * wave_number**2
            + float(parameters["Y"]) * wave_number**4
        ) * np.eye(3) + internal_mass
        eigenvalues, eigenvectors = np.linalg.eigh(symbol)
        roots.append((eigenvectors * (1.0 / np.sqrt(eigenvalues))) @ eigenvectors.T)
    basis_array = np.asarray(basis)
    derivative_array = np.asarray(derivative_basis)
    root_array = np.asarray(roots)

    def whiten(vector: np.ndarray) -> np.ndarray:
        shaped = np.asarray(vector, dtype=np.float64).reshape(6, 5)
        result = np.empty_like(shaped)
        for mode_index in range(5):
            result[:3, mode_index] = root_array[mode_index] @ shaped[:3, mode_index]
            result[3:, mode_index] = root_array[mode_index] @ shaped[3:, mode_index]
        return result

    def physical_field(vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        coefficient = whiten(vector)
        return coefficient @ basis_array, coefficient @ derivative_array

    def b_map(vector: np.ndarray) -> np.ndarray:
        field, derivative = physical_field(vector)
        flux = np.empty_like(field)
        for point in range(quadrature_points):
            complex_field = field[:3, point] + 1j * field[3:, point]
            complex_derivative = derivative[:3, point] + 1j * derivative[3:, point]
            complex_flux = current_map(complex_field, complex_derivative, parameters)
            flux[:3, point] = complex_flux.real
            flux[3:, point] = complex_flux.imag
        projection = np.einsum("im,jm->ji", derivative_array, flux) / quadrature_points
        result = np.empty_like(projection)
        for mode_index in range(5):
            result[:3, mode_index] = root_array[mode_index] @ projection[:3, mode_index]
            result[3:, mode_index] = root_array[mode_index] @ projection[3:, mode_index]
        return result.ravel()

    def jacobian(vector: np.ndarray) -> np.ndarray:
        step = 2.0e-6 * max(1.0, np.linalg.norm(vector) / math.sqrt(dimension))
        result = np.empty((dimension, dimension), dtype=np.float64)
        for column in range(dimension):
            increment = np.zeros(dimension, dtype=np.float64)
            increment[column] = step
            result[:, column] = (b_map(vector + increment) - b_map(vector - increment)) / (2.0 * step)
        return result

    def minimum_real_eigenvalue(matrix: np.ndarray) -> float:
        spectrum = np.linalg.eigvals(matrix)
        real_spectrum = [float(value.real) for value in spectrum if abs(float(value.imag)) < 1.0e-7]
        return min(real_spectrum)

    unit_eigenvalue = minimum_real_eigenvalue(jacobian(direction))
    displacement_coefficient = nelson_exponent / 2.0
    root_estimate = math.sqrt(-1.0 / (displacement_coefficient * unit_eigenvalue))
    diagnostics: dict[str, Any] = {}
    for name, scale in (
        ("lower", 0.98 * root_estimate),
        ("root", root_estimate),
        ("upper", 1.02 * root_estimate),
    ):
        current_jacobian = jacobian(scale * direction)
        ramer_jacobian = np.eye(dimension) + displacement_coefficient * current_jacobian
        sign, log_absolute_determinant = np.linalg.slogdet(ramer_jacobian)
        diagnostics[name] = {
            "scale": scale,
            "minimum_real_eigenvalue": minimum_real_eigenvalue(current_jacobian),
            "determinant_sign": float(sign),
            "log_absolute_determinant": float(log_absolute_determinant),
            "minimum_singular_value": float(np.linalg.svd(ramer_jacobian, compute_uv=False)[-1]),
        }
    root_field, _ = physical_field(root_estimate * direction)
    density = np.sum(root_field * root_field, axis=0)
    _a_value, b_value, c_value = coefficient_values(parameters)
    floor = float(parameters["rho_regularizer"])
    ratio = 1.0 / (1.0 + floor)
    curl_at_u1 = 4.0 * ratio * (b_value + c_value * (1.0 - ratio))
    return {
        "seed": seed,
        "quadrature_points": quadrature_points,
        "dimension": dimension,
        "direction_norm": float(np.linalg.norm(direction)),
        "nelson_exponent": nelson_exponent,
        "displacement_coefficient": displacement_coefficient,
        "unit_minimum_real_eigenvalue": unit_eigenvalue,
        "root_estimate": root_estimate,
        "diagnostics": diagnostics,
        "root_density_minimum": float(np.min(density)),
        "root_density_maximum": float(np.max(density)),
        "floor_to_root_density_ratio": floor / float(np.min(density)),
        "analytic_curl_coefficient_at_u1": curl_at_u1,
    }


def direct_source_doubling(parameters: dict[str, Any], seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    maximum_total_error = 0.0
    maximum_coefficient_error = 0.0
    step = 1.5e-6
    retained = 0
    for _ in range(160):
        psi = complex(rng.normal(), rng.normal())
        eta = complex(rng.normal(), rng.normal())
        field = np.asarray([psi, np.conjugate(psi), 0.0j])
        variation = np.asarray([eta, np.conjugate(eta), 0.0j])
        derivative = np.asarray([1j * psi, -1j * np.conjugate(psi), 0.0j])
        derivative_variation = np.asarray([1j * eta, -1j * np.conjugate(eta), 0.0j])
        frozen = 3.0 * float(np.real(np.vdot(derivative, current_map(field, derivative_variation, parameters))))
        if abs(frozen) < 1.0e-8:
            continue

        def energy(offset: float) -> float:
            shifted_field = field + offset * variation
            shifted_derivative = derivative + offset * derivative_variation
            return 1.5 * float(np.real(np.vdot(shifted_derivative, current_map(shifted_field, shifted_derivative, parameters))))

        total = (energy(step) - energy(-step)) / (2.0 * step)
        coefficient = total - frozen
        scale = max(1.0, abs(frozen))
        maximum_total_error = max(maximum_total_error, abs(total - 2.0 * frozen) / scale)
        maximum_coefficient_error = max(maximum_coefficient_error, abs(coefficient - frozen) / scale)
        retained += 1
    return {
        "retained_samples": retained,
        "max_total_vs_two_frozen_relative_error": maximum_total_error,
        "max_coefficient_vs_frozen_relative_error": maximum_coefficient_error,
        "error_normalisation": "max(1, abs(frozen))",
        "finite_difference_step": step,
    }


def scalar_symbol_coercivity(parameters: dict[str, Any]) -> float:
    y_value = float(parameters["Y"])
    z_value = float(parameters["Z"])
    r_value = float(parameters["r"])
    polynomial = np.polynomial.Polynomial([r_value, z_value, y_value])
    denominator = np.polynomial.Polynomial([1.0, 2.0, 1.0])
    derivative_numerator = polynomial.deriv() * denominator - polynomial * denominator.deriv()
    candidates = [0.0]
    for root in derivative_numerator.roots():
        if abs(root.imag) < 1e-12 and root.real >= 0.0:
            candidates.append(float(root.real))
    values = [(y_value * x * x + z_value * x + r_value) / (1.0 + x) ** 2 for x in candidates]
    values.append(y_value)
    return min(values)


def alias_free_certificate(degree: int, exponent: float, beta_operator: float) -> dict[str, float]:
    minimum_grid = 6 * degree + 1
    grid = 1 << (minimum_grid - 1).bit_length()
    modes = np.arange(1, degree + 1, dtype=np.float64)
    amplitudes = modes ** (-exponent)
    full_hat = np.zeros(grid, dtype=np.complex128)
    past_hat = np.zeros(grid, dtype=np.complex128)
    full_hat[1 : degree + 1] = -amplitudes
    full_hat[-degree:] = amplitudes[::-1]
    past_hat[-degree:] = amplitudes[::-1]
    full = np.fft.ifft(full_hat) * grid
    past = np.fft.ifft(past_hat) * grid
    full_l2 = float(np.mean(np.abs(full) ** 2))
    past_l4 = float(np.mean(np.abs(past) ** 4))
    full_l6 = float(np.mean(np.abs(full) ** 6))
    past_l6 = float(np.mean(np.abs(past) ** 6))
    cubic = past * np.abs(past) ** 2
    cubic_hat = np.fft.fft(cubic) / grid
    signed_modes = np.rint(np.fft.fftfreq(grid) * grid).astype(np.int64)
    nonpositive = float(np.sum(np.abs(cubic_hat[signed_modes <= 0]) ** 2))
    d_over_b = past_l6 / full_l6
    c_over_b = nonpositive / full_l6
    spin = d_over_b**3 - c_over_b**3
    return {
        "degree": degree,
        "grid": grid,
        "alias_free_minimum": minimum_grid,
        "full_l2_second": full_l2,
        "past_l4_fourth": past_l4,
        "full_l6_sixth": full_l6,
        "past_l6_sixth": past_l6,
        "nonpositive_cubic_energy": nonpositive,
        "mixed_hardy_functional": past_l4 * past_l4 / (full_l2 * full_l6),
        "spin_functional": spin,
        "source_ratio": beta_operator * beta_operator * spin,
    }


def log_weighted_sum(values: np.ndarray, weights: np.ndarray) -> float:
    maximum = float(np.max(values))
    return maximum + math.log(float(np.sum(weights * np.exp(values - maximum))))


def gauss_hermite_identity(order: int) -> dict[str, float]:
    nodes, raw_weights = np.polynomial.hermite.hermgauss(order)
    weights = raw_weights / math.sqrt(math.pi)
    standard = math.sqrt(2.0) * nodes
    p_value = 1.1
    theta = 0.61
    q_value = p_value * theta
    t_value = 0.37
    ell = -0.29
    precision = 1.0 + q_value * t_value
    covariance = 1.0 / precision
    mean = -q_value * covariance * ell

    def potential(value: np.ndarray) -> np.ndarray:
        return 0.009 * value**6 - 0.013 * value**4

    increment = 0.5 * t_value * (standard**2 - 1.0) + ell * standard
    left = log_weighted_sum(-q_value * increment - p_value * potential(standard), weights)
    completed = mean + math.sqrt(covariance) * standard
    logdet2 = math.log(precision) - q_value * t_value
    constant = -0.5 * logdet2 + 0.5 * q_value * q_value * ell * ell * covariance
    right = constant + log_weighted_sum(-p_value * potential(completed), weights)
    return {"order": order, "left": left, "right": right, "absolute_error": abs(left - right), "constant": constant}


def exact_scalar_doob_loop() -> dict[str, Any]:
    """Independent rational-polynomial audit of the triangular-loop no-go."""

    Polynomial = dict[tuple[int, int], Fraction]

    def add_poly(*values: Polynomial) -> Polynomial:
        result: Polynomial = {}
        for value in values:
            for key, coefficient in value.items():
                result[key] = result.get(key, Fraction(0)) + coefficient
        return {key: coefficient for key, coefficient in result.items() if coefficient}

    def scale_poly(value: Polynomial, scalar: Fraction) -> Polynomial:
        return {key: scalar * coefficient for key, coefficient in value.items()}

    def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
        result: Polynomial = {}
        for (a_left, t_left), c_left in left.items():
            for (a_right, t_right), c_right in right.items():
                key = (a_left + a_right, t_left + t_right)
                result[key] = result.get(key, Fraction(0)) + c_left * c_right
        return {key: coefficient for key, coefficient in result.items() if coefficient}

    def power(value: Polynomial, exponent: int) -> Polynomial:
        result: Polynomial = {(0, 0): Fraction(1)}
        for _ in range(exponent):
            result = multiply(result, value)
        return result

    def integrate(value: Polynomial, left: Fraction, right: Fraction) -> dict[int, Fraction]:
        result: dict[int, Fraction] = {}
        for (a_power, t_power), coefficient in value.items():
            integral = coefficient * (right ** (t_power + 1) - left ** (t_power + 1)) / (t_power + 1)
            result[a_power] = result.get(a_power, Fraction(0)) + integral
        return result

    variance: Polynomial = {(0, 1): Fraction(1)}
    linear: Polynomial = {(0, 0): Fraction(3), (0, 1): Fraction(-6)}

    def half(mean: Polynomial, control_sign: Fraction, left: Fraction, right: Fraction) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
        moment2 = add_poly(power(mean, 2), variance)
        moment4 = add_poly(
            power(mean, 4),
            scale_poly(multiply(power(mean, 2), variance), Fraction(6)),
            scale_poly(power(variance, 2), Fraction(3)),
        )
        moment6 = add_poly(
            power(mean, 6),
            scale_poly(multiply(power(mean, 4), variance), Fraction(15)),
            scale_poly(multiply(power(mean, 2), power(variance, 2)), Fraction(45)),
            scale_poly(power(variance, 3), Fraction(15)),
        )
        bracket = add_poly(
            scale_poly(moment6, Fraction(4)),
            scale_poly(multiply(linear, moment4), Fraction(4)),
            multiply(power(linear, 2), moment2),
        )
        expected_g = add_poly(
            scale_poly(power(mean, 3), Fraction(2)),
            scale_poly(multiply(mean, variance), Fraction(6)),
            multiply(linear, mean),
        )
        pairing = scale_poly(expected_g, Fraction(2) * control_sign)
        return integrate(bracket, left, right), integrate(pairing, left, right)

    left_bracket, left_pairing = half(
        {(1, 1): Fraction(2)}, Fraction(1), Fraction(0), Fraction(1, 2)
    )
    right_bracket, right_pairing = half(
        {(1, 0): Fraction(2), (1, 1): Fraction(-2)},
        Fraction(-1),
        Fraction(1, 2),
        Fraction(1),
    )
    bracket = {
        exponent: left_bracket.get(exponent, Fraction(0))
        + right_bracket.get(exponent, Fraction(0))
        for exponent in set(left_bracket) | set(right_bracket)
    }
    pairing = {
        exponent: left_pairing.get(exponent, Fraction(0))
        + right_pairing.get(exponent, Fraction(0))
        for exponent in set(left_pairing) | set(right_pairing)
    }
    return {
        "bracket_coefficients": {
            str(key): [value.numerator, value.denominator]
            for key, value in sorted(bracket.items())
        },
        "pairing_coefficients": {
            str(key): [value.numerator, value.denominator]
            for key, value in sorted(pairing.items())
            if value
        },
        "leading_A6_coefficient": float(bracket[6]),
        "expected_formula": "21/2 + (78/5) A^2 + 6 A^4 + (4/7) A^6",
    }


def hardy_support_fixture(seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    maximum_ratio = 0.0
    maximum_error = 0.0
    for _ in range(96):
        radius = 10
        grid = 512
        modes = np.arange(-radius, radius + 1)
        coefficients = rng.normal(size=len(modes)) + 1j * rng.normal(size=len(modes))
        past_coefficients = coefficients.copy()
        past_coefficients[modes >= 0] = 0.0
        phase = np.exp(2j * math.pi * np.outer(modes, np.arange(grid)) / grid)
        field = coefficients @ phase
        past = past_coefficients @ phase
        product_hat = np.fft.fft(field * np.conjugate(past)) / grid
        square_hat = np.fft.fft(np.abs(past) ** 2) / grid
        frequencies = np.rint(np.fft.fftfreq(grid) * grid).astype(int)
        nonpositive = frequencies <= 0
        maximum_error = max(maximum_error, float(np.linalg.norm((product_hat - square_hat)[nonpositive])))
        norm2_squared = float(np.mean(np.abs(field) ** 2))
        norm6_sixth = float(np.mean(np.abs(field) ** 6))
        past_l4_fourth = float(np.mean(np.abs(past) ** 4))
        ratio = past_l4_fourth * past_l4_fourth / (norm2_squared * norm6_sixth)
        maximum_ratio = max(maximum_ratio, ratio)
    return {"maximum_support_error": maximum_error, "maximum_ratio": maximum_ratio}


def independent_schatten_boundary(nelson_exponent: float, sextic_coefficient: float, cutoffs: list[int]) -> dict[str, Any]:
    """Loop/fsum derivation independent of the primary vectorized fixture."""

    rows: list[dict[str, float]] = []
    for cutoff in cutoffs:
        hs_square_sum = math.fsum(1.0 / (index * index) for index in range(1, cutoff + 1))
        point_exponent = -nelson_exponent * sextic_coefficient + 0.5 * math.fsum(
            nelson_exponent / math.sqrt(index)
            - math.log1p(nelson_exponent / math.sqrt(index))
            for index in range(1, cutoff + 1)
        )
        rows.append(
            {
                "cutoff": float(cutoff),
                "hs_square_sum": hs_square_sum,
                "non_hs_point_exponent_at_z1": point_exponent,
            }
        )
    upper = math.pi**2 / 6.0
    return {
        "cutoffs": cutoffs,
        "rows": rows,
        "hs_square_sum_upper": upper,
        "hs_log_partition_uniform_bound": nelson_exponent**4 * upper**3 / (432.0 * sextic_coefficient**2),
        "non_hs_point_exponent_growth": rows[-1]["non_hs_point_exponent_at_z1"]
        - rows[0]["non_hs_point_exponent_at_z1"],
        "identity": "t-log(1+t)<=t^2/2",
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for key, authority in manifest["authority"].items():
        actual = file_hash(REPO / authority["path"])
        record(rows, f"independent_authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])
    own = manifest["sources"]["independent"]
    actual_own_hash = file_hash(REPO / own["path"])
    record(rows, "independent_source_hash", actual_own_hash == own["sha256"], actual_own_hash, own["sha256"])

    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    a_value, b_value, c_value = coefficient_values(parameters)
    beta_operator = 4.0 * (a_value + 2.0 * b_value + c_value)
    c_symbol = scalar_symbol_coercivity(parameters)
    gamma = float(parameters["gamma"])
    lambda_value = float(parameters["lambda"])
    p_value = float(manifest["budget"]["reference_p"])
    entropy_fraction = float(manifest["budget"]["entropy_fraction"])
    coherent_sextic = float(manifest["budget"]["coherent_sextic_allocation"])
    certificate = alias_free_certificate(
        int(manifest["certificate"]["degree"]), float(manifest["certificate"]["coefficient_exponent"]), beta_operator
    )
    gaussian = gauss_hermite_identity(int(manifest["independent_audit"]["hermite_order"]))
    hardy = hardy_support_fixture(int(manifest["independent_audit"]["hardy_seed"]))
    source_doubling = direct_source_doubling(parameters, int(manifest["independent_audit"]["doubling_seed"]))

    d_over_b = certificate["past_l6_sixth"] / certificate["full_l6_sixth"]
    c_over_d = certificate["nonpositive_cubic_energy"] / certificate["past_l6_sixth"]
    past_amplification = d_over_b**3
    frozen_past_ratio = beta_operator**2 * (1.0 - c_over_d**3)
    joint_terminal_ratio = 4.0 * certificate["source_ratio"]
    joint_past_reward = 0.5 * p_value * p_value * 4.0 * frozen_past_ratio
    full_sextic_penalty = p_value * gamma / 6.0
    half_sextic_penalty = p_value * gamma / 12.0
    young_numerator = p_value * p_value * beta_operator**2 / (16.0 * c_symbol)
    universal_frozen_cost = young_numerator / entropy_fraction
    factor_four_frozen_theta = entropy_fraction / 4.0
    factor_four_cost = 4.0 * young_numerator / factor_four_frozen_theta
    factor_four_unexponentiated_cost = factor_four_cost / p_value
    mixed_bound = 64.0 / 9.0
    c0 = p_value * beta_operator**2 / (8.0 * float(parameters["Y"]))
    frozen_threshold = c0 * mixed_bound**3
    joint_threshold = 4.0 * frozen_threshold
    allocated_product = entropy_fraction * coherent_sextic
    lower_constant_density = abs(lambda_value) ** 3 / (3.0 * gamma**2)
    lower_constant_volume = (
        float(parameters["Lx"]) * float(parameters["Ly"]) * float(parameters["Lz"])
        * lower_constant_density
    )
    rho_critical = 2.0 * (abs(lambda_value) / 4.0) / (3.0 * (gamma / 12.0))
    lower_at_critical = lambda_value * rho_critical**2 / 4.0 + gamma * rho_critical**3 / 12.0
    doob_loop = exact_scalar_doob_loop()
    candidate_epsilon_6 = float(manifest["budget"]["one_use_candidate"]["epsilon_6"])
    candidate_epsilon_v = float(manifest["budget"]["one_use_candidate"]["epsilon_v"])
    equivalent_q = 1.0 / (2.0 * candidate_epsilon_v)
    frozen_one_shell_p_upper = 4.0 * c_symbol * entropy_fraction * gamma / (3.0 * beta_operator**2)
    ramer = production_ramer_obstruction_independent(
        parameters,
        int(manifest["audit"]["ramer_seed"]),
        int(manifest["independent_audit"]["ramer_quadrature"]),
        equivalent_q,
    )
    schatten = independent_schatten_boundary(
        equivalent_q,
        candidate_epsilon_6,
        [int(value) for value in manifest["audit"]["schatten_cutoffs"]],
    )
    direct_ramer_square_charge = 0.5 * ramer["displacement_coefficient"] ** 2 * certificate["source_ratio"]

    record(rows, "independent_beta_operator", abs(beta_operator - float(manifest["derived_oracles"]["beta_operator"])) < 1e-14, beta_operator, manifest["derived_oracles"]["beta_operator"])
    record(rows, "independent_symbol_coercivity", abs(c_symbol - float(manifest["derived_oracles"]["symbol_coercivity"])) < 1e-13, c_symbol, manifest["derived_oracles"]["symbol_coercivity"])
    record(rows, "alias_free_grid_strict", certificate["grid"] > certificate["alias_free_minimum"], certificate["grid"], f">{certificate['alias_free_minimum']}")
    record(rows, "grid_source_ratio_reproduced", abs(certificate["source_ratio"] - float(manifest["derived_oracles"]["source_ratio"])) < float(manifest["independent_audit"]["certificate_tolerance"]), certificate["source_ratio"], manifest["derived_oracles"]["source_ratio"])
    record(rows, "grid_past_amplification_reproduced", abs(past_amplification - float(manifest["derived_oracles"]["past_amplification"])) < float(manifest["independent_audit"]["certificate_tolerance"]), past_amplification, manifest["derived_oracles"]["past_amplification"])
    record(rows, "gauss_hermite_joint_identity", gaussian["absolute_error"] < float(manifest["independent_audit"]["hermite_tolerance"]), gaussian["absolute_error"], f"<{manifest['independent_audit']['hermite_tolerance']}")
    record(rows, "joint_source_amplitude_doubles_independent", source_doubling["retained_samples"] >= int(manifest["independent_audit"]["minimum_retained_samples"]) and source_doubling["max_total_vs_two_frozen_relative_error"] < float(manifest["independent_audit"]["doubling_tolerance"]), source_doubling, f"retained>={manifest['independent_audit']['minimum_retained_samples']} and error<{manifest['independent_audit']['doubling_tolerance']}")
    record(rows, "coefficient_slot_equals_frozen_slot_independent", source_doubling["retained_samples"] >= int(manifest["independent_audit"]["minimum_retained_samples"]) and source_doubling["max_coefficient_vs_frozen_relative_error"] < float(manifest["independent_audit"]["doubling_tolerance"]), source_doubling, f"retained>={manifest['independent_audit']['minimum_retained_samples']} and error<{manifest['independent_audit']['doubling_tolerance']}")
    record(rows, "joint_source_factor_four_independent", source_doubling["max_total_vs_two_frozen_relative_error"] < float(manifest["independent_audit"]["doubling_tolerance"]) and abs(joint_terminal_ratio - 4.0 * certificate["source_ratio"]) < 1e-15 and abs(joint_terminal_ratio - float(manifest["derived_oracles"]["terminal_joint_source_ratio"])) < float(manifest["independent_audit"]["certificate_tolerance"]), joint_terminal_ratio, manifest["derived_oracles"]["terminal_joint_source_ratio"])
    record(rows, "local_bellman_budget_fails_independent", joint_terminal_ratio > gamma / (3.0 * p_value), joint_terminal_ratio, gamma / (3.0 * p_value))
    record(rows, "retained_past_potential_suppresses_local_saddle", full_sextic_penalty > joint_past_reward, [joint_past_reward, full_sextic_penalty], "past-normalized reward < retained past-sextic penalty")
    record(rows, "hardy_support_identity_independent", hardy["maximum_support_error"] < float(manifest["independent_audit"]["hardy_tolerance"]), hardy["maximum_support_error"], f"<{manifest['independent_audit']['hardy_tolerance']}")
    record(rows, "hardy_random_ratio_below_64_over_9", hardy["maximum_ratio"] < mixed_bound and abs(mixed_bound - float(manifest["derived_oracles"]["mixed_hardy_bound"])) < 1e-15, [hardy["maximum_ratio"], mixed_bound], [f"<{mixed_bound}", manifest["derived_oracles"]["mixed_hardy_bound"]])
    record(rows, "certificate_mixed_functional_below_64_over_9", certificate["mixed_hardy_functional"] < mixed_bound, certificate["mixed_hardy_functional"], mixed_bound)
    record(rows, "frozen_tensor_budget_feasible", allocated_product > frozen_threshold, [allocated_product, frozen_threshold], "allocation > threshold")
    record(rows, "joint_tensor_budget_not_closed_by_mixed_bound", allocated_product < joint_threshold, [allocated_product, joint_threshold], "allocation < factor-four threshold")
    record(rows, "frozen_cm_sextic_margin_independent", half_sextic_penalty > universal_frozen_cost, [universal_frozen_cost, half_sextic_penalty], "cost < half-sextic")
    record(rows, "factor_four_carrier_cm_sextic_margin_independent", half_sextic_penalty > factor_four_cost and abs(half_sextic_penalty - factor_four_cost - float(manifest["derived_oracles"]["registered_factor_four_half_sextic_margin"])) < float(manifest["independent_audit"]["certificate_tolerance"]), [factor_four_cost, half_sextic_penalty, half_sextic_penalty - factor_four_cost], ["cost < half-sextic", manifest["derived_oracles"]["registered_factor_four_half_sextic_margin"]])
    record(rows, "factor_four_theta_quarter_independent", 4.0 * factor_four_frozen_theta == entropy_fraction, [factor_four_frozen_theta, 4.0 * factor_four_frozen_theta], [entropy_fraction / 4.0, entropy_fraction])
    record(rows, "corrected_factor_four_cost_independent", abs(factor_four_cost - float(manifest["derived_oracles"]["registered_factor_four_source_sextic_cost"])) < float(manifest["independent_audit"]["certificate_tolerance"]), factor_four_cost, manifest["derived_oracles"]["registered_factor_four_source_sextic_cost"])
    record(rows, "corrected_factor_four_unexponentiated_margin_independent", abs(factor_four_unexponentiated_cost - float(manifest["derived_oracles"]["registered_factor_four_unexponentiated_source_sextic_cost"])) < float(manifest["independent_audit"]["certificate_tolerance"]) and abs(gamma / 12.0 - factor_four_unexponentiated_cost - float(manifest["derived_oracles"]["one_use_unexponentiated_margin_after_factor_four"])) < float(manifest["independent_audit"]["certificate_tolerance"]), [factor_four_unexponentiated_cost, gamma / 12.0 - factor_four_unexponentiated_cost], [manifest["derived_oracles"]["registered_factor_four_unexponentiated_source_sextic_cost"], manifest["derived_oracles"]["one_use_unexponentiated_margin_after_factor_four"]])
    record(rows, "bd_equivalent_exponent_independent", equivalent_q > p_value and abs(equivalent_q - float(manifest["derived_oracles"]["equivalent_nelson_exponent_q"])) < 1e-14, equivalent_q, f">{p_value} and manifest oracle")
    record(rows, "ramer_half_divergence_coefficient_independent", abs(ramer["displacement_coefficient"] - equivalent_q / 2.0) < 1e-15, ramer["displacement_coefficient"], equivalent_q / 2.0)
    record(rows, "classii_curl_nonzero_independent", ramer["analytic_curl_coefficient_at_u1"] > 0.0, ramer["analytic_curl_coefficient_at_u1"], ">0")
    record(rows, "production_ramer_negative_mode_independent", float(manifest["audit"]["ramer_unit_eigenvalue_lower"]) < ramer["unit_minimum_real_eigenvalue"] < float(manifest["audit"]["ramer_unit_eigenvalue_upper"]), ramer["unit_minimum_real_eigenvalue"], [manifest["audit"]["ramer_unit_eigenvalue_lower"], manifest["audit"]["ramer_unit_eigenvalue_upper"]])
    record(rows, "production_ramer_sign_change_independent", ramer["diagnostics"]["lower"]["determinant_sign"] > 0.0 and ramer["diagnostics"]["upper"]["determinant_sign"] < 0.0, [ramer["diagnostics"]["lower"]["determinant_sign"], ramer["diagnostics"]["upper"]["determinant_sign"]], [1.0, -1.0])
    record(rows, "production_ramer_root_singular_independent", ramer["diagnostics"]["root"]["minimum_singular_value"] < float(manifest["audit"]["ramer_root_singular_value_upper"]), ramer["diagnostics"]["root"]["minimum_singular_value"], f"<{manifest['audit']['ramer_root_singular_value_upper']}")
    record(rows, "production_ramer_floor_inactive_independent", ramer["floor_to_root_density_ratio"] < float(manifest["audit"]["ramer_floor_ratio_upper"]), ramer["floor_to_root_density_ratio"], f"<{manifest['audit']['ramer_floor_ratio_upper']}")
    record(rows, "direct_ramer_square_overspend_independent", direct_ramer_square_charge > gamma / 12.0 and direct_ramer_square_charge > candidate_epsilon_6 and abs(direct_ramer_square_charge - float(manifest["derived_oracles"]["direct_ramer_square_carrier_charge"])) < float(manifest["independent_audit"]["certificate_tolerance"]), direct_ramer_square_charge, [f">{gamma / 12.0}", f">{candidate_epsilon_6}", manifest["derived_oracles"]["direct_ramer_square_carrier_charge"]])
    record(rows, "hilbert_schmidt_toy_uniform_independent", max(row["hs_square_sum"] for row in schatten["rows"]) < schatten["hs_square_sum_upper"] and math.isfinite(schatten["hs_log_partition_uniform_bound"]), [max(row["hs_square_sum"] for row in schatten["rows"]), schatten["hs_log_partition_uniform_bound"]], [f"<{schatten['hs_square_sum_upper']}", "finite"])
    record(rows, "non_hilbert_schmidt_toy_grows_independent", schatten["non_hs_point_exponent_growth"] > float(manifest["audit"]["schatten_non_hs_growth_lower"]), schatten["non_hs_point_exponent_growth"], f">{manifest['audit']['schatten_non_hs_growth_lower']}")
    record(rows, "bd_field_margin_independent", candidate_epsilon_6 < gamma / 12.0 and abs(float(manifest["budget"]["adapted_control_targets"]["epsilon_6_strict_upper"]) - gamma / 12.0) < 1e-15 and abs(gamma / 12.0 - candidate_epsilon_6 - float(manifest["derived_oracles"]["one_use_field_margin"])) < 1e-15, gamma / 12.0 - candidate_epsilon_6, manifest["derived_oracles"]["one_use_field_margin"])
    record(rows, "bd_control_margin_independent", candidate_epsilon_v < 1.0 / (2.0 * p_value) and abs(float(manifest["budget"]["adapted_control_targets"]["epsilon_v_reference_strict_upper"]) - 1.0 / (2.0 * p_value)) < 1e-15 and abs(1.0 / (2.0 * p_value) - candidate_epsilon_v - float(manifest["derived_oracles"]["one_use_control_margin"])) < 1e-15, 1.0 / (2.0 * p_value) - candidate_epsilon_v, manifest["derived_oracles"]["one_use_control_margin"])
    record(rows, "doob_loop_exact_rational_formula", doob_loop["bracket_coefficients"] == {"0": [21, 2], "2": [78, 5], "4": [6, 1], "6": [4, 7]}, doob_loop["bracket_coefficients"], {"0": [21, 2], "2": [78, 5], "4": [6, 1], "6": [4, 7]})
    record(rows, "doob_loop_pairing_cancels_exactly", doob_loop["pairing_coefficients"] == {}, doob_loop["pairing_coefficients"], {})
    record(rows, "doob_loop_leading_four_sevenths", doob_loop["leading_A6_coefficient"] == 4.0 / 7.0, doob_loop["leading_A6_coefficient"], 4.0 / 7.0)
    record(rows, "potential_optimizer_exact", abs(lower_at_critical + lower_constant_density) < 1e-14, lower_at_critical, -lower_constant_density)
    record(rows, "potential_volume_constant_reproduced", abs(lower_constant_volume - float(manifest["derived_oracles"]["potential_constant_L3"])) < 1e-12, lower_constant_volume, manifest["derived_oracles"]["potential_constant_L3"])
    record(rows, "production_reference_p_is_admissible_for_frozen_one_shell_budget_independent", p_value < frozen_one_shell_p_upper, p_value, frozen_one_shell_p_upper)
    record(rows, "gate_disposition_is_reduced_not_closed", manifest["consequence"]["disposition"] == "REDUCED-NOT-CLOSED", manifest["consequence"]["disposition"], "REDUCED-NOT-CLOSED")
    record(rows, "tier_boundary_is_t4", manifest["consequence"]["tier_after"] == "T4", manifest["consequence"]["tier_after"], "T4")

    source_text = (REPO / own["path"]).read_text(encoding="utf-8")
    syntax = ast.parse(source_text)
    imported_modules: list[str] = []
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    forbidden = [name for name in imported_modules if "a13_classii_joint_source_potential_reduction" in name]
    record(rows, "independent_route_nonimporting", not forbidden, forbidden, [])

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-classii-joint-source-potential-reduction-independent-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit_id(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": file_hash(manifest_path),
        "method": ["alias-free FFT quadrature", "Gauss-Hermite completed measure", "independent Fourier-support audit"],
        "assertions": rows,
        "summary": {"passed": len(rows) - len(failures), "total": len(rows), "failed": len(failures)},
        "derived": {
            "beta_operator": beta_operator,
            "symbol_coercivity": c_symbol,
            "certificate": certificate,
            "gaussian_identity": gaussian,
            "joint_source_doubling": source_doubling,
            "hardy_fixture": hardy,
            "source": {
                "past_amplification": past_amplification,
                "past_frozen_ratio": frozen_past_ratio,
                "terminal_joint_ratio": joint_terminal_ratio,
                "past_joint_exponent_reward": joint_past_reward,
            },
            "potential": {
                "full_sextic_exponent_penalty": full_sextic_penalty,
                "half_sextic_exponent_penalty": half_sextic_penalty,
                "lower_bound_constant_L3": lower_constant_volume,
            },
            "mixed_hardy": {
                "analytic_upper_bound": mixed_bound,
                "frozen_tensor_threshold": frozen_threshold,
                "joint_factor_four_tensor_threshold": joint_threshold,
                "allocated_product": allocated_product,
            },
            "cm_sextic": {
                "factor_four_frozen_theta": factor_four_frozen_theta,
                "universal_frozen_source_sextic_cost": universal_frozen_cost,
                "registered_factor_four_source_sextic_cost": factor_four_cost,
                "registered_factor_four_unexponentiated_source_sextic_cost": factor_four_unexponentiated_cost,
                "frozen_source_reference_p_upper_at_registered_theta": frozen_one_shell_p_upper,
            },
            "one_use_equivalence": {
                "epsilon_6": candidate_epsilon_6,
                "epsilon_v": candidate_epsilon_v,
                "equivalent_nelson_exponent_q": equivalent_q,
                "sextic_margin": gamma / 12.0 - candidate_epsilon_6,
                "control_margin": 1.0 / (2.0 * p_value) - candidate_epsilon_v,
            },
            "scalar_doob_loop": doob_loop,
            "nonfrozen_ramer": ramer,
            "direct_ramer_square_carrier_charge": direct_ramer_square_charge,
            "schatten_boundary": schatten,
        },
        "consequence": manifest["consequence"],
    }
    atomic_json(output_path, payload)
    if failures:
        print(f"FAIL: independent ({len(failures)} failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {len(rows)}/{len(rows)}")
    print("A13-CLASSII-JOINT-SOURCE-POTENTIAL-REDUCTION-INDEPENDENT-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    return run(arguments.manifest.resolve(), arguments.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
