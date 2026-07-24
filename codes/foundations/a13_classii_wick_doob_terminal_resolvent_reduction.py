#!/usr/bin/env python3
"""Primary audit for the A13 Wick--Doob/terminal-resolvent reduction.

This executable checks exact finite-dimensional identities and the production
frame estimates used by R-070.  It does not prove the non-pp balanced
linear-frame model attribution, the remaining rational-frame/cross-square
inequality, finite-energy one-use, or the Nelson estimate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import hashlib
import itertools
import json
import math
import os
import sys
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "codes" / "foundations"))
import a13_classii_endpoint_lifted_schur_causal_grouping_reduction as endpoint  # noqa: E402

CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-24-primary-wick-doob-terminal-resolvent-reduction/result.json"
)

# Test inputs and numerical tolerances, not derived model outputs.
RANDOM_SEED = 26072470
RANDOM_CASES = 240
GH_ORDER = 5
GH_ORDER_FINE = 7
CORRELATED_GH_ORDER = 7
CORRELATED_GH_ORDER_FINE = 9
CORRELATED_BACKGROUND = 0.8
CORRELATED_RHO = 0.35
FOURIER_GRID = 256
FOURIER_GRID_FINE = 512
KAPPA_NUMERATOR = 1
KAPPA_DENOMINATOR = 10
IDENTITY_TOL = 2.0e-10
BOUND_TOL = 3.0e-10
SCALAR_FLOOR = 0.37
DIAGNOSTIC_THRESHOLD = 0.5
DIAGNOSTIC_AMPLITUDE = 1.7
DIAGNOSTIC_P = 1.1


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name, suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def add(
    rows: list[dict[str, Any]],
    name: str,
    passed: bool,
    actual: Any,
    expected: Any,
) -> None:
    rows.append(
        {"name": name, "pass": bool(passed), "actual": actual, "expected": expected}
    )


def production_frame_audit() -> dict[str, float]:
    _, q_matrix, floor = endpoint.production_data()
    constants = endpoint.constants(q_matrix)
    generators = endpoint.real_generators()
    rng = np.random.default_rng(RANDOM_SEED)
    max_split = 0.0
    max_cross = 0.0
    max_endpoint_identity = 0.0
    max_linear_split = 0.0
    max_linear_remainder = 0.0
    max_symmetric_cartan_split = 0.0
    max_cartan_channel = 0.0
    max_defect_ratio = 0.0
    min_defect_margin = math.inf
    for _ in range(RANDOM_CASES):
        z = rng.normal(size=6)
        a = 0.2 * rng.normal(size=6)
        gaussian_derivative = rng.normal(size=6)
        control_derivative = rng.normal(size=6)
        b = 0.3 * rng.normal(size=6)
        frames_0, derivatives, _ = endpoint.frame_jet(z, floor, direction=a)
        frames_1, _, _ = endpoint.frame_jet(z + a, floor)
        assert derivatives is not None
        c_0 = endpoint.current_vectors(frames_0, control_derivative)
        c_1 = endpoint.current_vectors(frames_1, control_derivative + b)
        g_0 = endpoint.current_vectors(frames_0, gaussian_derivative)
        g_1 = endpoint.current_vectors(frames_1, gaussian_derivative)
        delta_c = c_1 - c_0
        delta_g = g_1 - g_0
        raw = 0.5 * endpoint.q_square(c_1 + g_1, q_matrix)
        raw -= 0.5 * endpoint.q_square(c_0 + g_0, q_matrix)
        control = 0.5 * endpoint.q_square(c_1, q_matrix)
        control -= 0.5 * endpoint.q_square(c_0, q_matrix)
        gaussian = 0.5 * endpoint.q_square(g_1, q_matrix)
        gaussian -= 0.5 * endpoint.q_square(g_0, q_matrix)
        cross = endpoint.q_inner(c_0, q_matrix, delta_g)
        cross += endpoint.q_inner(g_0, q_matrix, delta_c)
        cross += endpoint.q_inner(delta_c, q_matrix, delta_g)
        endpoint_cross = endpoint.q_inner(c_1, q_matrix, g_1)
        endpoint_cross -= endpoint.q_inner(c_0, q_matrix, g_0)
        max_split = max(max_split, abs(raw - control - gaussian - cross))
        max_cross = max(max_cross, abs(cross - endpoint_cross))

        same_control_1 = endpoint.current_vectors(frames_1, control_derivative)
        delta_same_control = same_control_1 - c_0
        linear_control = endpoint.current_vectors(derivatives, control_derivative)
        nonlinear_control = delta_same_control - linear_control
        current_full = endpoint.q_inner(g_0, q_matrix, delta_same_control)
        current_linear = endpoint.q_inner(g_0, q_matrix, linear_control)
        current_nonlinear = endpoint.q_inner(g_0, q_matrix, nonlinear_control)
        max_linear_split = max(
            max_linear_split,
            abs(current_full - current_linear - current_nonlinear),
        )
        pp_channel = float(q_matrix[0, 0] * np.dot(g_0[:, 0], linear_control[:, 0]))
        max_linear_remainder = max(
            max_linear_remainder, abs(current_linear - pp_channel)
        )
        denominator = float(z @ z + floor)
        for index, symmetric in enumerate(generators):
            p_value = frames_0[index][:, 0]
            v_value = frames_0[index][:, 1]
            dp_value = derivatives[index][:, 0]
            dv_value = derivatives[index][:, 1]
            p_current = float(p_value @ gaussian_derivative)
            v_current = float(v_value @ gaussian_derivative)
            direct_linear = float(
                np.asarray([p_current, v_current])
                @ q_matrix
                @ np.asarray(
                    [
                        float(dp_value @ control_derivative),
                        float(dv_value @ control_derivative),
                    ]
                )
            )
            q_value = float(z @ (symmetric @ z) / denominator)
            k_p = 2.0 * symmetric
            k_v = 2.0 * (symmetric - q_value * np.eye(6))
            k_v -= (
                np.outer(v_value, z) + np.outer(z, v_value)
            ) / denominator
            p_symmetric = float(a @ k_p @ control_derivative)
            v_symmetric = float(a @ k_v @ control_derivative)
            d_rho_a = 2.0 * float(z @ a)
            d_rho_c = 2.0 * float(z @ control_derivative)
            d_m_a = 2.0 * float((symmetric @ z) @ a)
            d_m_c = 2.0 * float((symmetric @ z) @ control_derivative)
            d_omega = (d_rho_a * d_m_c - d_rho_c * d_m_a) / denominator
            symmetric_part = float(
                q_matrix[0, 0] * p_current * p_symmetric
                + q_matrix[0, 1]
                * (p_current * v_symmetric + v_current * p_symmetric)
                + q_matrix[1, 1] * v_current * v_symmetric
            )
            cartan_part = 0.5 * float(
                (q_matrix[0, 1] * p_current + q_matrix[1, 1] * v_current)
                * d_omega
            )
            max_symmetric_cartan_split = max(
                max_symmetric_cartan_split,
                abs(direct_linear - symmetric_part - cartan_part),
            )
            max_cartan_channel = max(max_cartan_channel, abs(cartan_part))

        local = endpoint.local_terms(
            z,
            a,
            gaussian_derivative,
            np.zeros(6),
            q_matrix,
            floor,
        )
        identity = float(local["raw"])
        identity -= float(local["tangent_endpoint"])
        identity -= float(local["jacobi"])
        identity -= float(local["curvature"])
        max_endpoint_identity = max(max_endpoint_identity, abs(identity))
        scale = float(a @ a) * float(gaussian_derivative @ gaussian_derivative)
        curvature = abs(float(local["curvature"]))
        if scale > 0.0:
            max_defect_ratio = max(max_defect_ratio, curvature / scale)
        min_defect_margin = min(
            min_defect_margin, constants["c_global"] * scale - curvature
        )
    return {
        "max_polarization_residual": max_split,
        "max_cross_endpoint_residual": max_cross,
        "max_endpoint_lift_identity_residual": max_endpoint_identity,
        "max_frame_linearization_split_residual": max_linear_split,
        "max_weighted_offdiagonal_linear_remainder": max_linear_remainder,
        "max_symmetric_cartan_split_residual": max_symmetric_cartan_split,
        "max_cartan_channel_magnitude": max_cartan_channel,
        "max_endpoint_defect_ratio": max_defect_ratio,
        "minimum_endpoint_defect_margin": min_defect_margin,
        "c_star": constants["c_global"],
    }


def controls(
    shell: int, xi_history: list[float], d_history: list[float]
) -> tuple[float, float]:
    if shell == 0:
        return 0.17, -0.09
    if shell == 1:
        return (
            0.06 + 0.04 * xi_history[0] - 0.03 * d_history[0],
            -0.02 + 0.05 * xi_history[0] + 0.01 * d_history[0],
        )
    return (
        -0.03
        + 0.02 * xi_history[0]
        - 0.01 * xi_history[1]
        + 0.015 * d_history[0]
        - 0.012 * d_history[1],
        0.025
        - 0.018 * xi_history[0]
        + 0.011 * xi_history[1]
        + 0.014 * d_history[0]
        + 0.009 * d_history[1],
    )


def scalar_path(
    xis: list[float], derivatives: list[float], derivative_variances: list[float]
) -> dict[str, float]:
    terminal_value = sum(xis)
    accumulated_value = 0.0
    accumulated_control_derivative = 0.0
    accumulated_gaussian_derivative = 0.0
    covariance = 0.0
    raw_sum = 0.0
    wick_sum = 0.0
    trace_sum = 0.0
    injection_sum = 0.0
    fresh_wick_residual_sum = 0.0
    initial_raw = 0.0
    initial_wick = 0.0
    for shell, derivative in enumerate(derivatives):
        a, b = controls(shell, xis[:shell], derivatives[:shell])
        z_0 = terminal_value + accumulated_value
        z_1 = z_0 + a
        coefficient_0 = z_0 * z_0 + SCALAR_FLOOR
        coefficient_1 = z_1 * z_1 + SCALAR_FLOOR
        g = accumulated_gaussian_derivative
        c_0 = accumulated_control_derivative
        c_1 = c_0 + b
        if shell == 0:
            initial_raw = 0.5 * coefficient_0 * (g + c_0) ** 2
            initial_wick = 0.5 * coefficient_0 * ((g + c_0) ** 2 - covariance)
        raw_control = 0.5 * (coefficient_1 * c_1**2 - coefficient_0 * c_0**2)
        raw_gaussian = 0.5 * (coefficient_1 - coefficient_0) * g**2
        raw_cross = coefficient_1 * c_1 * g - coefficient_0 * c_0 * g
        raw_increment = raw_control + raw_gaussian + raw_cross
        wick_gaussian = 0.5 * (coefficient_1 - coefficient_0) * (g**2 - covariance)
        wick_increment = raw_control + wick_gaussian + raw_cross
        trace_increment = 0.5 * (coefficient_1 - coefficient_0) * covariance
        raw_sum += raw_increment
        wick_sum += wick_increment
        trace_sum += trace_increment
        injection_sum += 0.5 * coefficient_1 * derivative_variances[shell]
        post_wick = 0.5 * coefficient_1 * ((g + c_1) ** 2 - covariance)
        next_wick = 0.5 * coefficient_1 * (
            (g + c_1 + derivative) ** 2
            - covariance
            - derivative_variances[shell]
        )
        fresh_wick_residual_sum += next_wick - post_wick
        accumulated_value += a
        accumulated_control_derivative = c_1
        accumulated_gaussian_derivative += derivative
        covariance += derivative_variances[shell]
    final_z = terminal_value + accumulated_value
    final_coefficient = final_z * final_z + SCALAR_FLOOR
    terminal_raw = 0.5 * final_coefficient * (
        accumulated_gaussian_derivative + accumulated_control_derivative
    ) ** 2
    terminal_wick = 0.5 * final_coefficient * (
        (accumulated_gaussian_derivative + accumulated_control_derivative) ** 2
        - covariance
    )
    return {
        "raw_sum": raw_sum,
        "wick_sum": wick_sum,
        "trace_sum": trace_sum,
        "fresh_wick_residual_sum": fresh_wick_residual_sum,
        "terminal_raw_minus_injection": terminal_raw - initial_raw - injection_sum,
        "terminal_wick_difference": terminal_wick - initial_wick,
    }


def scalar_wick_doob_at_order(order: int) -> dict[str, float]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    nodes = math.sqrt(2.0) * nodes
    weights = weights / math.sqrt(math.pi)
    value_variances = [0.45, 0.30, 0.20]
    derivative_variances = [0.70, 0.40, 0.25]
    totals = {
        "raw_sum": 0.0,
        "wick_sum": 0.0,
        "trace_sum": 0.0,
        "fresh_wick_residual_sum": 0.0,
        "terminal_raw_minus_injection": 0.0,
        "terminal_wick_difference": 0.0,
    }
    for indices in itertools.product(range(order), repeat=6):
        xis = [
            math.sqrt(value_variances[index]) * float(nodes[indices[index]])
            for index in range(3)
        ]
        derivatives = [
            math.sqrt(derivative_variances[index])
            * float(nodes[indices[index + 3]])
            for index in range(3)
        ]
        weight = float(np.prod([weights[index] for index in indices]))
        path = scalar_path(xis, derivatives, derivative_variances)
        for key in totals:
            totals[key] += weight * path[key]
    totals["raw_terminal_residual"] = (
        totals["raw_sum"] - totals["terminal_raw_minus_injection"]
    )
    totals["wick_terminal_residual"] = (
        totals["wick_sum"] - totals["terminal_wick_difference"]
    )
    totals["trace_restoration_residual"] = (
        totals["raw_sum"] - totals["wick_sum"] - totals["trace_sum"]
    )
    return totals


def scalar_wick_doob_audit() -> dict[str, float]:
    coarse = scalar_wick_doob_at_order(GH_ORDER)
    fine = scalar_wick_doob_at_order(GH_ORDER_FINE)
    keys = tuple(coarse)
    result = dict(fine)
    result["coarse_order"] = float(GH_ORDER)
    result["fine_order"] = float(GH_ORDER_FINE)
    result["resolution_envelope"] = max(abs(fine[key] - coarse[key]) for key in keys)
    return result


def dyadic_hardy_audit() -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 1)
    shell_count = 12
    start = 4
    scales = 2.0 ** np.arange(start, start + shell_count)
    control_norms = np.abs(rng.normal(size=shell_count))
    c_k = 1.3
    a_squared = (c_k * scales ** (-2.0) * control_norms) ** 2
    past_squared = np.asarray([float(np.sum(a_squared[:index])) for index in range(shell_count)])
    lhs = float(np.sum(scales ** (-2.0) * past_squared))
    rhs_finite = float(
        np.sum(
            [
                a_squared[index] * np.sum(scales[index + 1 :] ** (-2.0))
                for index in range(shell_count)
            ]
        )
    )
    adjacent_ratio = float(scales[1] / scales[0])
    tail_ratio = adjacent_ratio ** (-2.0)
    geometric_tail_factor = tail_ratio / (1.0 - tail_ratio)
    rhs_infinite = float(
        c_k**2
        * geometric_tail_factor
        * np.sum(scales ** (-6.0) * control_norms**2)
    )
    return {
        "lhs": lhs,
        "finite_fubini_rhs": rhs_finite,
        "infinite_geometric_bound": rhs_infinite,
        "fubini_residual": lhs - rhs_finite,
        "bound_margin": rhs_infinite - lhs,
        "adjacent_scale_ratio": adjacent_ratio,
        "geometric_tail_factor": geometric_tail_factor,
    }


def resolvent_audit() -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 2)
    max_identity = 0.0
    min_trace_margin = math.inf
    for _ in range(RANDOM_CASES):
        dimension = 5
        matrix = rng.normal(size=(dimension, dimension))
        t_matrix = matrix.T @ matrix / dimension
        xi = rng.normal(size=dimension)
        shift = rng.normal(size=dimension)
        p_value = 0.2 + 1.8 * rng.random()
        identity = np.eye(dimension)
        r_matrix = np.linalg.inv(identity + p_value * t_matrix)
        s_matrix = t_matrix @ r_matrix
        left = 0.5 * (xi + shift) @ t_matrix @ (xi + shift)
        left -= 0.5 * np.trace(t_matrix)
        left += 0.5 / p_value * float(shift @ shift)
        positive_vector = shift + p_value * r_matrix @ t_matrix @ xi
        positive_matrix = t_matrix + identity / p_value
        right = 0.5 * (xi @ s_matrix @ xi - np.trace(s_matrix))
        right -= 0.5 * p_value * np.trace(t_matrix @ t_matrix @ r_matrix)
        right += 0.5 * positive_vector @ positive_matrix @ positive_vector
        max_identity = max(max_identity, abs(float(left - right)))
        trace_term = float(np.trace(t_matrix @ t_matrix @ r_matrix))
        hs_squared = float(np.sum(t_matrix * t_matrix))
        min_trace_margin = min(min_trace_margin, hs_squared - trace_term)
    return {
        "max_completion_residual": max_identity,
        "minimum_hilbert_schmidt_trace_margin": min_trace_margin,
    }


def adapted_centering_diagnostic() -> dict[str, float]:
    threshold = DIAGNOSTIC_THRESHOLD
    amplitude = DIAGNOSTIC_AMPLITUDE
    p_value = DIAGNOSTIC_P
    density = math.exp(-0.5 * threshold**2) / math.sqrt(2.0 * math.pi)
    probability = math.erf(threshold / math.sqrt(2.0))
    truncated_second = probability - 2.0 * threshold * density
    direct = 0.5 * amplitude**2 * (truncated_second - probability)
    formula = -threshold * density * amplitude**2
    resolvent_direct = direct / (1.0 + p_value * amplitude**2)
    resolvent_formula = formula / (1.0 + p_value * amplitude**2)
    return {
        "threshold": threshold,
        "amplitude": amplitude,
        "p": p_value,
        "direct_centered_expectation": direct,
        "formula_centered_expectation": formula,
        "resolvent_direct": resolvent_direct,
        "resolvent_formula": resolvent_formula,
    }


def correlated_covariance_at_order(order: int) -> float:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    nodes = math.sqrt(2.0) * nodes
    weights = weights / math.sqrt(math.pi)
    background = CORRELATED_BACKGROUND
    correlation = CORRELATED_RHO
    total = 0.0
    for index, x_value in enumerate(nodes):
        for other_index, independent in enumerate(nodes):
            derivative = correlation * x_value
            derivative += math.sqrt(1.0 - correlation**2) * independent
            total += float(weights[index] * weights[other_index]) * (
                (background + x_value) ** 2 * derivative
            )
    return total


def correlated_covariance_diagnostic() -> dict[str, float]:
    background = CORRELATED_BACKGROUND
    correlation = CORRELATED_RHO
    coarse = correlated_covariance_at_order(CORRELATED_GH_ORDER)
    fine = correlated_covariance_at_order(CORRELATED_GH_ORDER_FINE)
    expected = 2.0 * background * correlation
    return {
        "quadrature": fine,
        "coarse_quadrature": coarse,
        "resolution_envelope": abs(fine - coarse),
        "formula": expected,
        "correlation": correlation,
        "coarse_order": CORRELATED_GH_ORDER,
        "fine_order": CORRELATED_GH_ORDER_FINE,
    }


def spectral_derivative(values: np.ndarray, order: int) -> np.ndarray:
    count = values.size
    frequencies = np.fft.fftfreq(count, d=1.0 / count)
    multiplier = (1j * frequencies) ** order
    return np.fft.ifft(multiplier * np.fft.fft(values)).real


def p_column_at_grid(grid: int, q11: float) -> tuple[float, float]:
    x_value = 2.0 * math.pi * np.arange(grid) / grid
    # Resonant nonzero anchor: U=A=sin(x) makes both sides exactly q11/2.
    # A phase-orthogonal fixture would pass even after a sign error.
    u_value = np.sin(x_value)
    a_value = np.sin(x_value)
    u_square = u_value**2
    a_square = a_value**2
    left = q11 * float(
        np.mean(spectral_derivative(u_square, 1) * spectral_derivative(a_square, 1))
    )
    right = -q11 * float(np.mean(spectral_derivative(u_square, 2) * a_square))
    return left, right


def exact_p_column_audit() -> dict[str, float]:
    _, q_matrix, _ = endpoint.production_data()
    q11 = float(q_matrix[0, 0])
    coarse_left, coarse_right = p_column_at_grid(FOURIER_GRID, q11)
    left, right = p_column_at_grid(FOURIER_GRID_FINE, q11)
    analytic_oracle = q11 / 2.0
    kappa = KAPPA_NUMERATOR / KAPPA_DENOMINATOR
    theta = (1.0 + 2.0 * kappa) / 3.0
    exponent_x = (1.0 + theta) / 2.0
    exponent_y = (1.0 - theta) / 6.0
    model_exponent = 1.0 / (1.0 - exponent_x - exponent_y)
    return {
        "integration_by_parts_left": left,
        "integration_by_parts_right": right,
        "analytic_oracle": analytic_oracle,
        "residual": left - right,
        "q11": q11,
        "coarse_grid": FOURIER_GRID,
        "fine_grid": FOURIER_GRID_FINE,
        "resolution_envelope": max(
            abs(left - coarse_left), abs(right - coarse_right)
        ),
        "kappa": kappa,
        "theta": theta,
        "x_exponent": exponent_x,
        "y_exponent": exponent_y,
        "model_moment_exponent": model_exponent,
    }


def main() -> int:
    production = production_frame_audit()
    wick = scalar_wick_doob_audit()
    hardy = dyadic_hardy_audit()
    resolvent = resolvent_audit()
    adapted = adapted_centering_diagnostic()
    correlated = correlated_covariance_diagnostic()
    p_column = exact_p_column_audit()
    kappa_oracle = Fraction(KAPPA_NUMERATOR, KAPPA_DENOMINATOR)
    theta_oracle = (1 + 2 * kappa_oracle) / 3
    x_exponent_oracle = (1 + theta_oracle) / 2
    y_exponent_oracle = (1 - theta_oracle) / 6
    moment_oracle = 1 / (1 - x_exponent_oracle - y_exponent_oracle)
    rows: list[dict[str, Any]] = []
    add(
        rows,
        "production_current_and_frame_linearization",
        production["max_polarization_residual"] < IDENTITY_TOL
        and production["max_frame_linearization_split_residual"] < IDENTITY_TOL
        and production["max_symmetric_cartan_split_residual"] < IDENTITY_TOL
        and production["max_cartan_channel_magnitude"] > 1.0e-6
        and production["max_weighted_offdiagonal_linear_remainder"] > 1.0e-6,
        production,
        "polarization, DeltaM=DM[A]+E, and symmetric--Cartan split exact; "
        "Cartan and weighted off-diagonal linear channels nonzero",
    )
    add(rows, "production_mixed_endpoint_identity", production["max_cross_endpoint_residual"] < IDENTITY_TOL, production["max_cross_endpoint_residual"], IDENTITY_TOL)
    add(rows, "endpoint_lift_identity", production["max_endpoint_lift_identity_residual"] < IDENTITY_TOL, production["max_endpoint_lift_identity_residual"], IDENTITY_TOL)
    add(rows, "endpoint_defect_two_sided_bound", production["minimum_endpoint_defect_margin"] > -BOUND_TOL, production, "margin >= 0")
    add(rows, "raw_terminal_minus_injection", abs(wick["raw_terminal_residual"]) < IDENTITY_TOL, wick["raw_terminal_residual"], 0.0)
    add(rows, "wick_doob_terminalization", abs(wick["wick_terminal_residual"]) < IDENTITY_TOL, wick["wick_terminal_residual"], 0.0)
    add(rows, "raw_wick_trace_restoration", abs(wick["trace_restoration_residual"]) < IDENTITY_TOL, wick["trace_restoration_residual"], 0.0)
    add(rows, "fresh_wick_step_centers", abs(wick["fresh_wick_residual_sum"]) < IDENTITY_TOL and wick["resolution_envelope"] < IDENTITY_TOL, wick, "centered; coarse/fine envelope < tolerance")
    add(rows, "adapted_fixture_nontrivial", abs(wick["wick_sum"]) > 1.0e-4, wick["wick_sum"], "nonzero")
    add(rows, "dyadic_hardy_fubini", abs(hardy["fubini_residual"]) < IDENTITY_TOL, hardy["fubini_residual"], 0.0)
    add(rows, "dyadic_hardy_bound", hardy["bound_margin"] > -BOUND_TOL, hardy["bound_margin"], ">=0")
    add(rows, "terminal_resolvent_completion", resolvent["max_completion_residual"] < IDENTITY_TOL, resolvent["max_completion_residual"], IDENTITY_TOL)
    add(rows, "resolvent_trace_hs_bound", resolvent["minimum_hilbert_schmidt_trace_margin"] > -BOUND_TOL, resolvent["minimum_hilbert_schmidt_trace_margin"], ">=0")
    add(rows, "adapted_centering_formula", abs(adapted["direct_centered_expectation"] - adapted["formula_centered_expectation"]) < IDENTITY_TOL, adapted, "direct=formula")
    add(rows, "adapted_centering_is_negative", adapted["formula_centered_expectation"] < 0.0, adapted["formula_centered_expectation"], "<0")
    add(rows, "adapted_resolvent_formula", abs(adapted["resolvent_direct"] - adapted["resolvent_formula"]) < IDENTITY_TOL, adapted, "direct=formula")
    add(rows, "adapted_resolvent_remains_negative", adapted["resolvent_formula"] < 0.0, adapted["resolvent_formula"], "<0")
    add(rows, "correlated_value_derivative_drift", abs(correlated["quadrature"] - correlated["formula"]) < IDENTITY_TOL and correlated["resolution_envelope"] < IDENTITY_TOL and abs(correlated["quadrature"]) > 1.0e-3, correlated, "2*z0*rho, nonzero; coarse/fine envelope < tolerance")
    add(rows, "weighted_p_column_integration_by_parts", abs(p_column["residual"]) < IDENTITY_TOL and abs(p_column["integration_by_parts_left"] - p_column["analytic_oracle"]) < IDENTITY_TOL and abs(p_column["integration_by_parts_right"] - p_column["analytic_oracle"]) < IDENTITY_TOL and p_column["resolution_envelope"] < IDENTITY_TOL and p_column["analytic_oracle"] > 1.0e-6, p_column, "nonzero q11/2 oracle; q11-weighted identity; coarse/fine envelope < tolerance")
    add(rows, "cartan_control_x_exponent", abs(p_column["x_exponent"] - float(x_exponent_oracle)) < IDENTITY_TOL, p_column["x_exponent"], str(x_exponent_oracle))
    add(rows, "cartan_control_y_exponent", abs(p_column["y_exponent"] - float(y_exponent_oracle)) < IDENTITY_TOL, p_column["y_exponent"], str(y_exponent_oracle))
    add(rows, "cartan_model_fifth_moment", abs(p_column["model_moment_exponent"] - float(moment_oracle)) < IDENTITY_TOL, p_column["model_moment_exponent"], str(moment_oracle))
    passed = all(row["pass"] for row in rows)
    payload = {
        "schema": "tect/a13-wick-doob-terminal-resolvent-primary/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {
            "random_seed": RANDOM_SEED,
            "random_cases": RANDOM_CASES,
            "gauss_hermite_order": GH_ORDER,
            "gauss_hermite_fine_order": GH_ORDER_FINE,
            "correlated_gauss_hermite_orders": [
                CORRELATED_GH_ORDER,
                CORRELATED_GH_ORDER_FINE,
            ],
            "fourier_grids": [FOURIER_GRID, FOURIER_GRID_FINE],
            "kappa": f"{KAPPA_NUMERATOR}/{KAPPA_DENOMINATOR}",
            "identity_tolerance": IDENTITY_TOL,
            "bound_tolerance": BOUND_TOL,
        },
        "computed": {
            "production_frame": production,
            "scalar_wick_doob": wick,
            "dyadic_hardy": hardy,
            "terminal_resolvent": resolvent,
            "adapted_centering": adapted,
            "correlated_covariance": correlated,
            "exact_p_column": p_column,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": (
            "The exact Wick--Doob terminalization, trace restoration, covariance-tail "
            "bookkeeping, retained resolvent, adapted-centering no-go, exact weighted "
            "p-p integration by parts, and the nonzero remaining frame linearization "
            "are verified. The non-pp balanced linear-frame model attribution, full "
            "QII-weighted rational-frame/cross-square residual, finite-energy "
            "extension, one-use, and Nelson theorem remain open."
        ),
    }
    atomic_json(OUT, payload)
    if not passed:
        for row in rows:
            if not row["pass"]:
                print(f"FAIL {row['name']}: {row['actual']} expected {row['expected']}")
        return 1
    print(
        f"{RESULT_ID}-PRIMARY-PASS: {len(rows)}/{len(rows)}; "
        f"Wick residual={wick['wick_terminal_residual']:.3e}; "
        f"adapted resolver={adapted['resolvent_formula']:.9g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
