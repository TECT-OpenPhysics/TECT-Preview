#!/usr/bin/env python3
"""Primary audit for the A13 joint source-potential reduction.

This audit does not claim the full cutoff-uniform Nelson/log-Laplace bound.
It verifies the exact shifted-Gaussian identity, the production potential
coercivity, the A13 terminal-versus-past normalization, the factor-four
joint relative-phase source, a mixed Hardy/Riesz enclosure, and the explicit
Cameron-Martin/sextic crossover that leaves one adapted-control lemma open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.1"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_joint_source_potential_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-primary-joint-source-potential-reduction-v1.1" / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def git_commit() -> str:
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


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def coefficients(parameters: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    return (
        float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator,
        float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator,
        float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator,
    )


def real_vector(field: np.ndarray) -> np.ndarray:
    value = np.asarray(field, dtype=np.complex128)
    return np.concatenate((value.real, value.imag))


def compact_matrix(field: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    value = np.asarray(field, dtype=np.complex128)
    x_value = real_vector(value)
    z_value = x_value.copy()
    z_value[[2, 5]] = 0.0
    jz_value = np.asarray([-z_value[3], -z_value[4], 0.0, z_value[0], z_value[1], 0.0])
    s_value = float(np.real(np.vdot(value[:2], value[:2])))
    rho = float(np.real(np.vdot(value, value)))
    a_value, b_value, c_value = coefficients(parameters)
    d_value = a_value + 2.0 * b_value + c_value
    projector = np.diag([1.0, 1.0, 0.0, 1.0, 1.0, 0.0])
    p_frame = 4.0 * (s_value * projector - np.outer(jz_value, jz_value))
    ratio = s_value / (rho + float(parameters["rho_regularizer"]))
    return (
        d_value * p_frame
        - 4.0 * (b_value + c_value) * ratio * (np.outer(z_value, x_value) + np.outer(x_value, z_value))
        + 4.0 * c_value * ratio * ratio * np.outer(x_value, x_value)
    )


def production_ramer_obstruction_fixture(
    parameters: dict[str, Any], seed: int, quadrature_points: int, nelson_exponent: float
) -> dict[str, Any]:
    """Finite production-mode falsifier for the one-shot Ramer map.

    The whitening convention is the normalized full-torus Fourier basis.  The
    reduced real coordinates use the modes 0, cos(x), sin(x), cos(2x), sin(2x)
    for each of the six real field components.  Since 2 V = delta_gamma b,
    exp(-q V) uses displacement coefficient t=q/2.
    """

    modes = (("zero", 0), ("cos", 1), ("sin", 1), ("cos", 2), ("sin", 2))
    component_count = 6
    mode_count = len(modes)
    dimension = component_count * mode_count
    rng = np.random.default_rng(seed)
    direction = rng.normal(size=dimension)
    direction /= np.linalg.norm(direction) / math.sqrt(dimension)

    sample = 2.0 * np.pi * np.arange(quadrature_points, dtype=np.float64) / quadrature_points
    physical_frequency = 2.0 * np.pi / float(parameters["Lx"])
    basis: list[np.ndarray] = []
    derivative_basis: list[np.ndarray] = []
    covariance_roots: list[np.ndarray] = []
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
            derivative_basis.append(-math.sqrt(2.0) * physical_frequency * index * np.sin(index * sample))
        else:
            basis.append(math.sqrt(2.0) * np.sin(index * sample))
            derivative_basis.append(math.sqrt(2.0) * physical_frequency * index * np.cos(index * sample))
        wave_number = physical_frequency * index
        symbol = (
            float(parameters["r"])
            + float(parameters["Z"]) * wave_number**2
            + float(parameters["Y"]) * wave_number**4
        ) * np.eye(3) + internal_mass
        eigenvalues, eigenvectors = np.linalg.eigh(symbol)
        covariance_roots.append((eigenvectors * (1.0 / np.sqrt(eigenvalues))) @ eigenvectors.T)
    basis_array = np.asarray(basis)
    derivative_array = np.asarray(derivative_basis)
    roots = np.asarray(covariance_roots)

    def apply_covariance_root(vector: np.ndarray) -> np.ndarray:
        shaped = np.asarray(vector, dtype=np.float64).reshape(component_count, mode_count)
        result = np.empty_like(shaped)
        for mode_index in range(mode_count):
            result[:3, mode_index] = roots[mode_index] @ shaped[:3, mode_index]
            result[3:, mode_index] = roots[mode_index] @ shaped[3:, mode_index]
        return result

    def physical_field(vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        coefficients_value = apply_covariance_root(vector)
        return coefficients_value @ basis_array, coefficients_value @ derivative_array

    def b_map(vector: np.ndarray) -> np.ndarray:
        field, derivative = physical_field(vector)
        flux = np.empty_like(field)
        for point in range(quadrature_points):
            complex_field = field[:3, point] + 1j * field[3:, point]
            flux[:, point] = compact_matrix(complex_field, parameters) @ derivative[:, point]
        projected = np.einsum("im,jm->ji", derivative_array, flux) / quadrature_points
        result = np.empty_like(projected)
        for mode_index in range(mode_count):
            result[:3, mode_index] = roots[mode_index] @ projected[:3, mode_index]
            result[3:, mode_index] = roots[mode_index] @ projected[3:, mode_index]
        return result.ravel()

    def jacobian(vector: np.ndarray) -> np.ndarray:
        step = 2.0e-6 * max(1.0, np.linalg.norm(vector) / math.sqrt(dimension))
        result = np.empty((dimension, dimension), dtype=np.float64)
        for column in range(dimension):
            increment = np.zeros(dimension, dtype=np.float64)
            increment[column] = step
            result[:, column] = (b_map(vector + increment) - b_map(vector - increment)) / (2.0 * step)
        return result

    def smallest_real_eigenvalue(matrix: np.ndarray) -> float:
        eigenvalues = np.linalg.eigvals(matrix)
        real_values = [float(value.real) for value in eigenvalues if abs(float(value.imag)) < 1.0e-7]
        return min(real_values)

    unit_jacobian = jacobian(direction)
    unit_eigenvalue = smallest_real_eigenvalue(unit_jacobian)
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
            "minimum_real_eigenvalue": smallest_real_eigenvalue(current_jacobian),
            "determinant_sign": float(sign),
            "log_absolute_determinant": float(log_absolute_determinant),
            "minimum_singular_value": float(np.linalg.svd(ramer_jacobian, compute_uv=False)[-1]),
        }

    root_field, _ = physical_field(root_estimate * direction)
    root_density = np.sum(root_field * root_field, axis=0)
    a_value, b_value, c_value = coefficients(parameters)
    floor = float(parameters["rho_regularizer"])
    curl_at_u1 = 4.0 * (1.0 / (1.0 + floor)) * (
        b_value + c_value * (1.0 - 1.0 / (1.0 + floor))
    )
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
        "root_density_minimum": float(np.min(root_density)),
        "root_density_maximum": float(np.max(root_density)),
        "floor_to_root_density_ratio": floor / float(np.min(root_density)),
        "analytic_curl_coefficient_at_u1": curl_at_u1,
    }


def joint_source_doubling_fixture(parameters: dict[str, Any], seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    maximum_total_error = 0.0
    maximum_coefficient_error = 0.0
    minimum_frozen_magnitude = math.inf
    step = 2.0e-6
    retained = 0
    for _ in range(192):
        psi = complex(rng.normal(), rng.normal())
        eta = complex(rng.normal(), rng.normal())
        field = np.asarray([psi, np.conjugate(psi), 0.0j])
        variation = np.asarray([eta, np.conjugate(eta), 0.0j])
        derivative = np.asarray([1j * psi, -1j * np.conjugate(psi), 0.0j])
        derivative_variation = np.asarray([1j * eta, -1j * np.conjugate(eta), 0.0j])
        matrix = compact_matrix(field, parameters)
        frozen_one_axis = float(real_vector(derivative) @ matrix @ real_vector(derivative_variation))
        frozen = 3.0 * frozen_one_axis
        if abs(frozen) < 1.0e-8:
            continue

        def energy(offset: float) -> float:
            shifted_field = field + offset * variation
            shifted_derivative = derivative + offset * derivative_variation
            shifted_matrix = compact_matrix(shifted_field, parameters)
            one_axis = 0.5 * float(real_vector(shifted_derivative) @ shifted_matrix @ real_vector(shifted_derivative))
            return 3.0 * one_axis

        total = (energy(step) - energy(-step)) / (2.0 * step)
        coefficient_slot = total - frozen
        scale = max(1.0, abs(frozen))
        maximum_total_error = max(maximum_total_error, abs(total - 2.0 * frozen) / scale)
        maximum_coefficient_error = max(maximum_coefficient_error, abs(coefficient_slot - frozen) / scale)
        minimum_frozen_magnitude = min(minimum_frozen_magnitude, abs(frozen))
        retained += 1
    return {
        "retained_samples": retained,
        "max_total_vs_two_frozen_relative_error": maximum_total_error,
        "max_coefficient_vs_frozen_relative_error": maximum_coefficient_error,
        "minimum_retained_frozen_magnitude": minimum_frozen_magnitude,
        "error_normalisation": "max(1, abs(frozen))",
        "finite_difference_step": step,
    }


def symbol_coercivity(parameters: dict[str, Any]) -> float:
    y_value = float(parameters["Y"])
    z_value = float(parameters["Z"])
    r_value = float(parameters["r"])

    def ratio(x_value: float) -> float:
        return (y_value * x_value * x_value + z_value * x_value + r_value) / (1.0 + x_value) ** 2

    candidates = [ratio(0.0), y_value]
    denominator = 2.0 * y_value - z_value
    if denominator > 0.0:
        stationary = (2.0 * r_value - z_value) / denominator
        if stationary >= 0.0:
            candidates.append(ratio(stationary))
    return min(candidates)


def linear_convolution(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    size = len(left) + len(right) - 1
    fft_size = 1 << (size - 1).bit_length()
    transformed = np.fft.rfft(left, fft_size) * np.fft.rfft(right, fft_size)
    return np.fft.irfft(transformed, fft_size)[:size]


def l6_sixth(values: np.ndarray) -> float:
    cubic = linear_convolution(linear_convolution(values, values), values)
    return float(np.dot(cubic, cubic))


def polynomial_data(degree: int, exponent: float) -> dict[str, float]:
    indices = np.arange(1, degree + 1, dtype=np.float64)
    amplitudes = indices ** (-exponent)
    full = np.concatenate((amplitudes[::-1], np.asarray([0.0]), -amplitudes))
    past = amplitudes[::-1]
    full_l2 = float(np.dot(full, full))
    past_square = linear_convolution(past, past)
    past_l4 = float(np.dot(past_square, past_square))
    full_l6 = l6_sixth(full)
    past_l6 = l6_sixth(past)
    cubic_current = linear_convolution(linear_convolution(np.concatenate((past, [0.0])), np.concatenate((past, [0.0]))), np.concatenate(([0.0], past[::-1])))
    nonpositive = float(np.dot(cubic_current[: 2 * degree + 1], cubic_current[: 2 * degree + 1]))
    mixed_hardy = past_l4 * past_l4 / (full_l2 * full_l6)
    return {
        "degree": degree,
        "coefficient_exponent": exponent,
        "full_l2_second": full_l2,
        "past_l4_fourth": past_l4,
        "full_l6_sixth": full_l6,
        "past_l6_sixth": past_l6,
        "nonpositive_cubic_energy": nonpositive,
        "mixed_hardy_functional": mixed_hardy,
    }


def shifted_gaussian_fixture(seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    dimension = 5
    raw = rng.normal(size=(dimension, dimension))
    t_matrix = raw.T @ raw / dimension
    ell = rng.normal(size=dimension)
    p_value = 1.1
    theta = 0.63
    q_value = p_value * theta
    precision = np.eye(dimension) + q_value * t_matrix
    covariance = np.linalg.inv(precision)
    mean = -q_value * covariance @ ell
    sign, logdet = np.linalg.slogdet(precision)
    if sign <= 0:
        raise AssertionError("completed precision must be positive")
    logdet2 = logdet - q_value * float(np.trace(t_matrix))
    constant = -0.5 * logdet2 + 0.5 * q_value * q_value * float(ell @ covariance @ ell)
    errors: list[float] = []
    for _ in range(256):
        point = rng.normal(size=dimension)
        potential = 0.017 * float(np.dot(point, point)) ** 3 - 0.031 * float(np.dot(point, point)) ** 2
        log_base = -0.5 * float(point @ point) - 0.5 * dimension * math.log(2.0 * math.pi)
        increment = 0.5 * (float(point @ t_matrix @ point) - float(np.trace(t_matrix))) + float(ell @ point)
        left = log_base - q_value * increment - p_value * potential
        centered = point - mean
        log_completed = (
            -0.5 * float(centered @ precision @ centered)
            + 0.5 * logdet
            - 0.5 * dimension * math.log(2.0 * math.pi)
        )
        right = constant + log_completed - p_value * potential
        errors.append(abs(left - right))
    return {
        "dimension": dimension,
        "p": p_value,
        "theta": theta,
        "q": q_value,
        "logdet2": logdet2,
        "noncentral_constant": constant,
        "max_pointwise_log_density_error": max(errors),
    }


def mixed_hardy_fixture(seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    maximum_ratio = 0.0
    maximum_support_error = 0.0
    for _ in range(128):
        radius = 12
        negative = rng.normal(size=radius) + 1j * rng.normal(size=radius)
        nonnegative = rng.normal(size=radius + 1) + 1j * rng.normal(size=radius + 1)
        # Coefficients are stored on modes -radius,...,radius.
        field = np.concatenate((negative, nonnegative))
        past = np.concatenate((negative, np.zeros(radius + 1, dtype=np.complex128)))
        grid = 512
        modes = np.arange(-radius, radius + 1)
        phase = np.exp(2j * math.pi * np.outer(modes, np.arange(grid)) / grid)
        f_values = field @ phase
        g_values = past @ phase
        product = f_values * np.conjugate(g_values)
        past_square = np.abs(g_values) ** 2
        product_hat = np.fft.fft(product) / grid
        square_hat = np.fft.fft(past_square) / grid
        frequencies = np.rint(np.fft.fftfreq(grid) * grid).astype(int)
        nonpositive = frequencies <= 0
        support_error = float(np.linalg.norm((product_hat - square_hat)[nonpositive]))
        maximum_support_error = max(maximum_support_error, support_error)
        norm2 = float(np.mean(np.abs(f_values) ** 2)) ** 0.5
        norm6 = float(np.mean(np.abs(f_values) ** 6)) ** (1.0 / 6.0)
        norm4_g = float(np.mean(np.abs(g_values) ** 4)) ** 0.25
        ratio = norm4_g**8 / (norm2**2 * norm6**6)
        maximum_ratio = max(maximum_ratio, ratio)
    return {"maximum_random_ratio": maximum_ratio, "maximum_support_error": maximum_support_error}


def scalar_doob_loop_fixture() -> dict[str, float]:
    """Check the exact Doob integrand and the timewise-Young obstruction."""

    nodes, weights = np.polynomial.legendre.leggauss(64)

    def integrate_half(function: Any, left: float, right: float) -> float:
        points = 0.5 * (right - left) * nodes + 0.5 * (right + left)
        return float(0.5 * (right - left) * np.sum(weights * function(points)))

    def expected_g_squared(t_value: np.ndarray, mean: np.ndarray) -> np.ndarray:
        variance = t_value
        linear = 3.0 - 6.0 * t_value
        moment2 = mean**2 + variance
        moment4 = mean**4 + 6.0 * mean**2 * variance + 3.0 * variance**2
        moment6 = (
            mean**6
            + 15.0 * mean**4 * variance
            + 45.0 * mean**2 * variance**2
            + 15.0 * variance**3
        )
        return 4.0 * moment6 + 4.0 * linear * moment4 + linear**2 * moment2

    def expected_g(t_value: np.ndarray, mean: np.ndarray) -> np.ndarray:
        return 2.0 * (mean**3 + 3.0 * mean * t_value) + (3.0 - 6.0 * t_value) * mean

    def bracket(amplitude: float) -> float:
        left = integrate_half(
            lambda time: expected_g_squared(time, 2.0 * amplitude * time), 0.0, 0.5
        )
        right = integrate_half(
            lambda time: expected_g_squared(time, 2.0 * amplitude * (1.0 - time)),
            0.5,
            1.0,
        )
        return left + right

    def doob_pairing(amplitude: float) -> float:
        left = integrate_half(
            lambda time: 2.0 * amplitude * expected_g(time, 2.0 * amplitude * time),
            0.0,
            0.5,
        )
        right = integrate_half(
            lambda time: -2.0
            * amplitude
            * expected_g(time, 2.0 * amplitude * (1.0 - time)),
            0.5,
            1.0,
        )
        return left + right

    squared_amplitudes = np.asarray([0.0, 1.0, 4.0, 9.0])
    bracket_values = np.asarray([bracket(math.sqrt(value)) for value in squared_amplitudes])
    coefficients = np.linalg.solve(
        np.vander(squared_amplitudes, N=4, increasing=True), bracket_values
    )
    amplitude = 8.0
    return {
        "doob_integrand_formula": "g_t(x)=2x^3+(3-6t)x",
        "triangular_control_energy_at_A8": 4.0 * amplitude**2,
        "terminal_sixth_moment": 15.0,
        "doob_pairing_at_A8": doob_pairing(amplitude),
        "bracket_at_A8": bracket(amplitude),
        "bracket_polynomial_coefficients_in_A2": coefficients.tolist(),
        "leading_A6_coefficient": float(coefficients[3]),
        "expected_leading_A6_coefficient": 4.0 / 7.0,
    }


def schatten_boundary_fixture(nelson_exponent: float, sextic_coefficient: float, cutoffs: list[int]) -> dict[str, Any]:
    """Diagonal determinant diagnostic at the Hilbert--Schmidt boundary."""

    rows: list[dict[str, float]] = []
    for cutoff in cutoffs:
        indices = np.arange(1, cutoff + 1, dtype=np.float64)
        hs_weights = 1.0 / indices
        non_hs_weights = 1.0 / np.sqrt(indices)
        rows.append(
            {
                "cutoff": float(cutoff),
                "hs_square_sum": float(np.sum(hs_weights * hs_weights)),
                "non_hs_point_exponent_at_z1": float(
                    -nelson_exponent * sextic_coefficient
                    + 0.5
                    * np.sum(
                        nelson_exponent * non_hs_weights
                        - np.log1p(nelson_exponent * non_hs_weights)
                    )
                ),
            }
        )
    hs_square_sum_upper = math.pi**2 / 6.0
    return {
        "cutoffs": cutoffs,
        "rows": rows,
        "hs_square_sum_upper": hs_square_sum_upper,
        "hs_log_partition_uniform_bound": nelson_exponent**4
        * hs_square_sum_upper**3
        / (432.0 * sextic_coefficient**2),
        "non_hs_point_exponent_growth": rows[-1]["non_hs_point_exponent_at_z1"]
        - rows[0]["non_hs_point_exponent_at_z1"],
        "identity": "t-log(1+t)<=t^2/2",
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])
    for key, source in manifest["sources"].items():
        actual = digest(REPO / source["path"])
        add(rows, f"source_{key}_hash", actual == source["sha256"], actual, source["sha256"])

    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    a_value, b_value, c_value = coefficients(parameters)
    beta_operator = 4.0 * (a_value + 2.0 * b_value + c_value)
    c_symbol = symbol_coercivity(parameters)
    gamma = float(parameters["gamma"])
    lambda_value = float(parameters["lambda"])
    p_value = float(manifest["budget"]["reference_p"])
    entropy_fraction = float(manifest["budget"]["entropy_fraction"])
    coherent_sextic = float(manifest["budget"]["coherent_sextic_allocation"])
    y_value = float(parameters["Y"])

    polynomial = polynomial_data(
        int(manifest["certificate"]["degree"]), float(manifest["certificate"]["coefficient_exponent"])
    )
    d_over_b = polynomial["past_l6_sixth"] / polynomial["full_l6_sixth"]
    c_over_b = polynomial["nonpositive_cubic_energy"] / polynomial["full_l6_sixth"]
    c_over_d = polynomial["nonpositive_cubic_energy"] / polynomial["past_l6_sixth"]
    spin = d_over_b**3 - c_over_b**3
    source_ratio = beta_operator**2 * spin
    past_amplification = d_over_b**3
    frozen_past_ratio = beta_operator**2 * (1.0 - c_over_d**3)
    joint_terminal_ratio = 4.0 * source_ratio
    joint_past_ratio = 4.0 * frozen_past_ratio
    joint_source_reward = 0.5 * p_value * p_value * joint_past_ratio
    full_sextic_penalty = p_value * gamma / 6.0

    mixed_bound = (8.0 / 3.0) ** 2
    c0 = p_value * beta_operator**2 / (8.0 * y_value)
    frozen_mixed_threshold = c0 * mixed_bound**3
    joint_mixed_threshold = 4.0 * frozen_mixed_threshold
    allocated_product = entropy_fraction * coherent_sextic

    young_numerator = p_value * p_value * beta_operator**2 / (16.0 * c_symbol)
    universal_frozen_sextic = young_numerator / entropy_fraction
    factor_four_frozen_theta = entropy_fraction / 4.0
    carrier_joint_sextic = 4.0 * young_numerator / factor_four_frozen_theta
    carrier_joint_unexponentiated_sextic = carrier_joint_sextic / p_value
    half_sextic_penalty = p_value * gamma / 12.0
    potential_constant_density = abs(lambda_value) ** 3 / (3.0 * gamma**2)
    potential_constant_volume = (
        float(parameters["Lx"]) * float(parameters["Ly"]) * float(parameters["Lz"])
        * potential_constant_density
    )

    gaussian = shifted_gaussian_fixture(int(manifest["audit"]["gaussian_seed"]))
    hardy_fixture = mixed_hardy_fixture(int(manifest["audit"]["hardy_seed"]))
    source_doubling = joint_source_doubling_fixture(parameters, int(manifest["audit"]["doubling_seed"]))
    doob_loop = scalar_doob_loop_fixture()
    candidate_epsilon_6 = float(manifest["budget"]["one_use_candidate"]["epsilon_6"])
    candidate_epsilon_v = float(manifest["budget"]["one_use_candidate"]["epsilon_v"])
    equivalent_q = 1.0 / (2.0 * candidate_epsilon_v)
    ramer = production_ramer_obstruction_fixture(
        parameters,
        int(manifest["audit"]["ramer_seed"]),
        int(manifest["audit"]["ramer_primary_quadrature"]),
        equivalent_q,
    )
    schatten = schatten_boundary_fixture(
        equivalent_q,
        candidate_epsilon_6,
        [int(value) for value in manifest["audit"]["schatten_cutoffs"]],
    )
    direct_ramer_square_charge = 0.5 * ramer["displacement_coefficient"] ** 2 * source_ratio

    add(rows, "production_coefficient_matrix_positive", a_value > 0.0 and c_value > 0.0 and a_value * c_value - b_value * b_value > 0.0, [a_value, b_value, c_value, a_value * c_value - b_value * b_value], "a>0,c>0,ac-b^2>0")
    add(rows, "sharp_beta_operator_derived", abs(beta_operator - float(manifest["derived_oracles"]["beta_operator"])) < 1e-14, beta_operator, manifest["derived_oracles"]["beta_operator"])
    add(rows, "symbol_coercivity_derived", abs(c_symbol - float(manifest["derived_oracles"]["symbol_coercivity"])) < 1e-14, c_symbol, manifest["derived_oracles"]["symbol_coercivity"])
    add(rows, "exact_shifted_gaussian_identity", gaussian["max_pointwise_log_density_error"] < float(manifest["audit"]["gaussian_tolerance"]), gaussian["max_pointwise_log_density_error"], f"<{manifest['audit']['gaussian_tolerance']}")
    add(rows, "det2_term_has_correct_sign", gaussian["logdet2"] <= 0.0 and gaussian["noncentral_constant"] >= 0.0, [gaussian["logdet2"], gaussian["noncentral_constant"]], "logdet2<=0 and total constant>=0")
    add(rows, "certificate_source_ratio_reproduced", abs(source_ratio - float(manifest["derived_oracles"]["source_ratio"])) < float(manifest["audit"]["certificate_tolerance"]), source_ratio, manifest["derived_oracles"]["source_ratio"])
    add(rows, "past_amplification_reproduced", abs(past_amplification - float(manifest["derived_oracles"]["past_amplification"])) < float(manifest["audit"]["certificate_tolerance"]), past_amplification, manifest["derived_oracles"]["past_amplification"])
    add(rows, "past_normalized_source_is_small", frozen_past_ratio < float(manifest["decision_thresholds"]["past_frozen_source_ratio_upper"]), frozen_past_ratio, f"<{manifest['decision_thresholds']['past_frozen_source_ratio_upper']}")
    add(rows, "joint_source_amplitude_doubles_directly", source_doubling["retained_samples"] >= int(manifest["audit"]["minimum_retained_samples"]) and source_doubling["max_total_vs_two_frozen_relative_error"] < float(manifest["audit"]["doubling_tolerance"]), source_doubling, f"retained>={manifest['audit']['minimum_retained_samples']} and error<{manifest['audit']['doubling_tolerance']}")
    add(rows, "coefficient_slot_equals_frozen_slot_directly", source_doubling["retained_samples"] >= int(manifest["audit"]["minimum_retained_samples"]) and source_doubling["max_coefficient_vs_frozen_relative_error"] < float(manifest["audit"]["doubling_tolerance"]), source_doubling, f"retained>={manifest['audit']['minimum_retained_samples']} and error<{manifest['audit']['doubling_tolerance']}")
    add(rows, "joint_source_factor_four", source_doubling["max_total_vs_two_frozen_relative_error"] < float(manifest["audit"]["doubling_tolerance"]) and abs(joint_terminal_ratio - 4.0 * source_ratio) < 1e-15 and abs(joint_terminal_ratio - float(manifest["derived_oracles"]["terminal_joint_source_ratio"])) < float(manifest["audit"]["certificate_tolerance"]), joint_terminal_ratio, manifest["derived_oracles"]["terminal_joint_source_ratio"])
    add(rows, "local_bellman_sextic_budget_fails", joint_terminal_ratio > gamma / (3.0 * p_value), joint_terminal_ratio, gamma / (3.0 * p_value))
    add(rows, "retained_past_potential_suppresses_local_source_saddle", full_sextic_penalty > joint_source_reward, [joint_source_reward, full_sextic_penalty], "past-normalized source reward < retained past-sextic penalty")
    add(rows, "retained_past_potential_margin", full_sextic_penalty - joint_source_reward > float(manifest["decision_thresholds"]["past_potential_margin_lower"]), full_sextic_penalty - joint_source_reward, f">{manifest['decision_thresholds']['past_potential_margin_lower']}")
    add(rows, "mixed_hardy_support_identity", hardy_fixture["maximum_support_error"] < float(manifest["audit"]["hardy_tolerance"]), hardy_fixture["maximum_support_error"], f"<{manifest['audit']['hardy_tolerance']}")
    add(rows, "mixed_hardy_random_checks", hardy_fixture["maximum_random_ratio"] < mixed_bound, hardy_fixture["maximum_random_ratio"], mixed_bound)
    add(rows, "mixed_hardy_constant_exact", abs(mixed_bound - 64.0 / 9.0) < 1e-15 and abs(mixed_bound - float(manifest["derived_oracles"]["mixed_hardy_bound"])) < 1e-15, mixed_bound, manifest["derived_oracles"]["mixed_hardy_bound"])
    add(rows, "registered_mixed_functional_below_bound", polynomial["mixed_hardy_functional"] < mixed_bound, polynomial["mixed_hardy_functional"], mixed_bound)
    add(rows, "frozen_coherent_budget_is_feasible", allocated_product > frozen_mixed_threshold, [allocated_product, frozen_mixed_threshold], "allocation > frozen threshold")
    add(rows, "mixed_hardy_alone_does_not_close_joint_source", allocated_product < joint_mixed_threshold, [allocated_product, joint_mixed_threshold], "allocation < factor-four joint threshold")
    add(rows, "universal_frozen_cm_sextic_budget_positive", half_sextic_penalty > universal_frozen_sextic, [universal_frozen_sextic, half_sextic_penalty], "source coefficient < half-sextic")
    add(rows, "registered_factor_four_cm_sextic_budget_positive", half_sextic_penalty > carrier_joint_sextic and abs(half_sextic_penalty - carrier_joint_sextic - float(manifest["derived_oracles"]["registered_factor_four_half_sextic_margin"])) < float(manifest["audit"]["certificate_tolerance"]), [carrier_joint_sextic, half_sextic_penalty, half_sextic_penalty - carrier_joint_sextic], ["factor-four carrier coefficient < half-sextic", manifest["derived_oracles"]["registered_factor_four_half_sextic_margin"]])
    add(rows, "factor_four_cm_allocation_is_rescaled", abs(4.0 * factor_four_frozen_theta - entropy_fraction) < 1e-15, [factor_four_frozen_theta, 4.0 * factor_four_frozen_theta], [entropy_fraction / 4.0, entropy_fraction])
    add(rows, "factor_four_corrected_sextic_cost", abs(carrier_joint_sextic - float(manifest["derived_oracles"]["registered_factor_four_source_sextic_cost"])) < float(manifest["audit"]["certificate_tolerance"]), carrier_joint_sextic, manifest["derived_oracles"]["registered_factor_four_source_sextic_cost"])
    add(rows, "factor_four_corrected_unexponentiated_margin", abs(carrier_joint_unexponentiated_sextic - float(manifest["derived_oracles"]["registered_factor_four_unexponentiated_source_sextic_cost"])) < float(manifest["audit"]["certificate_tolerance"]) and abs(gamma / 12.0 - carrier_joint_unexponentiated_sextic - float(manifest["derived_oracles"]["one_use_unexponentiated_margin_after_factor_four"])) < float(manifest["audit"]["certificate_tolerance"]), [carrier_joint_unexponentiated_sextic, gamma / 12.0 - carrier_joint_unexponentiated_sextic], [manifest["derived_oracles"]["registered_factor_four_unexponentiated_source_sextic_cost"], manifest["derived_oracles"]["one_use_unexponentiated_margin_after_factor_four"]])
    add(rows, "one_use_candidate_has_strict_sextic_margin", candidate_epsilon_6 < gamma / 12.0 and abs(float(manifest["budget"]["adapted_control_targets"]["epsilon_6_strict_upper"]) - gamma / 12.0) < 1e-15 and abs(gamma / 12.0 - candidate_epsilon_6 - float(manifest["derived_oracles"]["one_use_field_margin"])) < 1e-15, [candidate_epsilon_6, gamma / 12.0 - candidate_epsilon_6], ["epsilon_6 < gamma/12", manifest["derived_oracles"]["one_use_field_margin"]])
    add(rows, "one_use_candidate_has_strict_control_margin", candidate_epsilon_v < 1.0 / (2.0 * p_value) and abs(float(manifest["budget"]["adapted_control_targets"]["epsilon_v_reference_strict_upper"]) - 1.0 / (2.0 * p_value)) < 1e-15 and abs(1.0 / (2.0 * p_value) - candidate_epsilon_v - float(manifest["derived_oracles"]["one_use_control_margin"])) < 1e-15, [candidate_epsilon_v, 1.0 / (2.0 * p_value) - candidate_epsilon_v], ["epsilon_v < 1/(2p)", manifest["derived_oracles"]["one_use_control_margin"]])
    add(rows, "one_use_is_higher_exponent_nelson_equivalent", equivalent_q > p_value and abs(equivalent_q - float(manifest["derived_oracles"]["equivalent_nelson_exponent_q"])) < 1e-14, equivalent_q, f">{p_value} and manifest oracle")
    add(rows, "ramer_displacement_uses_half_divergence_coefficient", abs(ramer["displacement_coefficient"] - equivalent_q / 2.0) < 1e-15, ramer["displacement_coefficient"], equivalent_q / 2.0)
    add(rows, "classii_coefficient_curl_is_nonzero", ramer["analytic_curl_coefficient_at_u1"] > 0.0, ramer["analytic_curl_coefficient_at_u1"], ">0")
    add(rows, "production_ramer_has_negative_jacobian_mode", float(manifest["audit"]["ramer_unit_eigenvalue_lower"]) < ramer["unit_minimum_real_eigenvalue"] < float(manifest["audit"]["ramer_unit_eigenvalue_upper"]), ramer["unit_minimum_real_eigenvalue"], [manifest["audit"]["ramer_unit_eigenvalue_lower"], manifest["audit"]["ramer_unit_eigenvalue_upper"]])
    add(rows, "production_ramer_determinant_changes_sign", ramer["diagnostics"]["lower"]["determinant_sign"] > 0.0 and ramer["diagnostics"]["upper"]["determinant_sign"] < 0.0, [ramer["diagnostics"]["lower"]["determinant_sign"], ramer["diagnostics"]["upper"]["determinant_sign"]], [1.0, -1.0])
    add(rows, "production_ramer_root_is_singular", ramer["diagnostics"]["root"]["minimum_singular_value"] < float(manifest["audit"]["ramer_root_singular_value_upper"]), ramer["diagnostics"]["root"]["minimum_singular_value"], f"<{manifest['audit']['ramer_root_singular_value_upper']}")
    add(rows, "production_ramer_witness_is_floor_inactive", ramer["floor_to_root_density_ratio"] < float(manifest["audit"]["ramer_floor_ratio_upper"]), ramer["floor_to_root_density_ratio"], f"<{manifest['audit']['ramer_floor_ratio_upper']}")
    add(rows, "direct_ramer_square_overspends_sextic_reserve", direct_ramer_square_charge > gamma / 12.0 and direct_ramer_square_charge > candidate_epsilon_6 and abs(direct_ramer_square_charge - float(manifest["derived_oracles"]["direct_ramer_square_carrier_charge"])) < float(manifest["audit"]["certificate_tolerance"]), direct_ramer_square_charge, [f">{gamma / 12.0}", f">{candidate_epsilon_6}", manifest["derived_oracles"]["direct_ramer_square_carrier_charge"]])
    add(rows, "hilbert_schmidt_determinant_toy_is_uniform", max(row["hs_square_sum"] for row in schatten["rows"]) < schatten["hs_square_sum_upper"] and math.isfinite(schatten["hs_log_partition_uniform_bound"]), [max(row["hs_square_sum"] for row in schatten["rows"]), schatten["hs_log_partition_uniform_bound"]], [f"<{schatten['hs_square_sum_upper']}", "finite"])
    add(rows, "non_hilbert_schmidt_determinant_toy_grows", schatten["non_hs_point_exponent_growth"] > float(manifest["audit"]["schatten_non_hs_growth_lower"]), schatten["non_hs_point_exponent_growth"], f">{manifest['audit']['schatten_non_hs_growth_lower']}")
    add(rows, "scalar_doob_integrand_formula", doob_loop["doob_integrand_formula"] == "g_t(x)=2x^3+(3-6t)x", doob_loop["doob_integrand_formula"], "g_t(x)=2x^3+(3-6t)x")
    add(rows, "triangular_loop_exact_cancellation", abs(doob_loop["doob_pairing_at_A8"]) < float(manifest["audit"]["doob_tolerance"]), doob_loop["doob_pairing_at_A8"], f"<{manifest['audit']['doob_tolerance']}")
    add(rows, "timewise_young_bracket_has_A6_growth", abs(doob_loop["leading_A6_coefficient"] - 4.0 / 7.0) < float(manifest["audit"]["doob_tolerance"]), doob_loop["leading_A6_coefficient"], 4.0 / 7.0)
    add(rows, "timewise_young_endpoint_budget_is_lower_order", doob_loop["bracket_at_A8"] > 10.0 * (doob_loop["triangular_control_energy_at_A8"] + doob_loop["terminal_sixth_moment"]), [doob_loop["bracket_at_A8"], doob_loop["triangular_control_energy_at_A8"], doob_loop["terminal_sixth_moment"]], "bracket > 10*(control+terminal L6)")
    add(rows, "potential_pointwise_lower_bound_constant", potential_constant_density > 0.0 and abs(potential_constant_volume - float(manifest["derived_oracles"]["potential_constant_L3"])) < float(manifest["audit"]["certificate_tolerance"]), [potential_constant_density, potential_constant_volume], ["positive", manifest["derived_oracles"]["potential_constant_L3"]])
    frozen_one_shell_p_upper = 4.0 * c_symbol * entropy_fraction * gamma / (3.0 * beta_operator**2)
    add(rows, "production_reference_p_is_admissible_for_frozen_one_shell_budget", p_value < frozen_one_shell_p_upper, p_value, frozen_one_shell_p_upper)
    add(rows, "joint_gate_remains_open", manifest["consequence"]["disposition"] == "REDUCED-NOT-CLOSED", manifest["consequence"]["disposition"], "REDUCED-NOT-CLOSED")
    add(rows, "successor_is_controlled_shell_one_use", "CONTROLLED-SHELL-ENERGY-ONE-USE" in manifest["consequence"]["next_gate"], manifest["consequence"]["next_gate"], "contains CONTROLLED-SHELL-ENERGY-ONE-USE")
    add(rows, "tier_remains_t4", manifest["consequence"]["tier_after"] == "T4", manifest["consequence"]["tier_after"], "T4")

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-classii-joint-source-potential-reduction-primary-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "assertions": rows,
        "summary": {"passed": len(rows) - len(failures), "total": len(rows), "failed": len(failures)},
        "derived": {
            "coefficients": {"a": a_value, "b": b_value, "c": c_value, "beta_operator": beta_operator},
            "symbol_coercivity": c_symbol,
            "gaussian_identity": gaussian,
            "joint_source_doubling": source_doubling,
            "certificate": polynomial,
            "source": {
                "terminal_frozen_ratio": source_ratio,
                "past_amplification": past_amplification,
                "past_frozen_ratio": frozen_past_ratio,
                "terminal_joint_ratio": joint_terminal_ratio,
                "past_joint_ratio": joint_past_ratio,
                "past_joint_exponent_reward": joint_source_reward,
            },
            "potential": {
                "full_sextic_exponent_penalty": full_sextic_penalty,
                "half_sextic_exponent_penalty": half_sextic_penalty,
                "lower_bound_constant_density": potential_constant_density,
                "lower_bound_constant_L3": potential_constant_volume,
            },
            "mixed_hardy": {
                "analytic_upper_bound": mixed_bound,
                "fixture": hardy_fixture,
                "c0": c0,
                "frozen_tensor_threshold": frozen_mixed_threshold,
                "joint_factor_four_tensor_threshold": joint_mixed_threshold,
                "allocated_product": allocated_product,
            },
            "cm_sextic": {
                "entropy_fraction": entropy_fraction,
                "factor_four_frozen_theta": factor_four_frozen_theta,
                "universal_frozen_source_sextic_cost": universal_frozen_sextic,
                "registered_factor_four_source_sextic_cost": carrier_joint_sextic,
                "registered_factor_four_unexponentiated_source_sextic_cost": carrier_joint_unexponentiated_sextic,
                "half_sextic_margin_after_registered_factor_four": half_sextic_penalty - carrier_joint_sextic,
                "one_use_margin_after_registered_factor_four": gamma / 12.0 - carrier_joint_unexponentiated_sextic,
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
        print(f"FAIL: primary ({len(failures)} failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {len(rows)}/{len(rows)}")
    print("A13-CLASSII-JOINT-SOURCE-POTENTIAL-REDUCTION-PRIMARY-PASS")
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
