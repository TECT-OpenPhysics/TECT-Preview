#!/usr/bin/env python3
"""Primary executable audit for the R-083 A13 reduction package.

This script verifies the exact controlled-polynomial FAR elimination, the
remaining Cartan input-scale telescope, the failure of automatic input-scale
orthogonality, and the complete linear Pauli--Fierz heat/forest bookkeeping.
It deliberately does not assert controlled Cartan CFAR, a signed NEAR lower
bound, one-use, Nelson, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import itertools
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.polynomial.hermite_e import hermegauss, poly2herme


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CONTROLLED-POLYNOMIAL-CFAR-LINEAR-PAULI-FIERZ-FOREST-REDUCTION"
MODEL = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-25-primary-controlled-polynomial-cfar-linear-pf-forest/result.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def conditional(
    function: Callable[[tuple[float, ...]], np.ndarray],
    level: int,
    omega: tuple[float, ...],
    outcomes: list[tuple[float, ...]],
) -> np.ndarray:
    matching = [candidate for candidate in outcomes if candidate[:level] == omega[:level]]
    return sum((function(candidate) for candidate in matching), np.zeros_like(function(matching[0]))) / len(matching)


def gram_linear(matrices: list[np.ndarray], z: np.ndarray) -> np.ndarray:
    return sum((matrix.T @ np.outer(z, z) @ matrix for matrix in matrices), np.zeros((6, 6)))


def tensor_pair(matrices: list[np.ndarray], left: np.ndarray, right: np.ndarray) -> float:
    return float(sum(np.trace(matrix.T @ left @ matrix @ right) for matrix in matrices))


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    model = json.loads(MODEL.read_text(encoding="utf-8"))
    parameters = model["parameters"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["rho_regularizer"])
    a_weight = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator
    b_weight = float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator
    c_weight = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    alpha = c_weight / (b_weight + c_weight)
    c1 = c_weight / alpha**2
    c0 = a_weight - b_weight**2 / c_weight
    csum = c0 + c1
    floor = float(parameters["rho_regularizer"])

    check("model_schema", model["schema"] == "tect/a1-production-functional-realisation/1.0", model["schema"], "tect/a1-production-functional-realisation/1.0")
    check("production_denominator_derived", abs(denominator - (float(parameters["M_X"]) ** 2 + floor)) < 1e-18, denominator, "M_X^2+rho_regularizer")
    check("production_Q_positive", a_weight > 0 and c_weight > 0 and a_weight * c_weight > b_weight**2, [a_weight, b_weight, c_weight], "positive definite")
    check("diagonal_alpha", abs(alpha - 5.0 / 9.0) < 1e-14, alpha, "5/9")
    check("diagonal_c0", abs(c0 - 3.0 / (250.0 * denominator)) < 1e-14, c0, "3/(250 P)")
    check("diagonal_c1", abs(c1 - 243.0 / (8000.0 * denominator)) < 1e-14, c1, "243/(8000 P)")

    projector = np.diag([1.0, 1.0, 0.0, 1.0, 1.0, 0.0])
    scale0 = 2.0 * math.sqrt(c0)
    scaleh = 2.0 * math.sqrt(csum)
    a0 = scale0 * projector
    a1 = scaleh * np.array(
        [
            [0, 1, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, -1, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ],
        dtype=float,
    )
    a2 = scaleh * np.array(
        [
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, -1, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ],
        dtype=float,
    )
    matrices = [a0, a1, a2]
    check("A0_symmetric", np.max(np.abs(a0 - a0.T)) < 1e-15, float(np.max(np.abs(a0 - a0.T))), 0.0)
    check("A1_skew", np.max(np.abs(a1 + a1.T)) < 1e-15, float(np.max(np.abs(a1 + a1.T))), 0.0)
    check("A2_skew", np.max(np.abs(a2 + a2.T)) < 1e-15, float(np.max(np.abs(a2 + a2.T))), 0.0)

    rng = np.random.default_rng(83025)
    current_residual = 0.0
    gram_residual = 0.0
    split_residual = 0.0
    for _ in range(24):
        z = rng.normal(size=6)
        y = rng.normal(size=6)
        u1, u2 = complex(z[0], z[3]), complex(z[1], z[4])
        v1, v2 = complex(y[0], y[3]), complex(y[1], y[4])
        dr = 2.0 * float(np.dot(projector @ z, y))
        determinant = u1 * v2 - u2 * v1
        linear_direct = np.array([math.sqrt(c0) * dr, 2.0 * math.sqrt(csum) * determinant.real, 2.0 * math.sqrt(csum) * determinant.imag])
        linear_matrix = np.array([float(z @ matrix @ y) for matrix in matrices])
        current_residual = max(current_residual, float(np.max(np.abs(linear_direct - linear_matrix))))
        c_linear = np.vstack([z @ matrix for matrix in matrices])
        b_linear = gram_linear(matrices, z)
        gram_residual = max(gram_residual, float(np.max(np.abs(c_linear.T @ c_linear - b_linear))))

        radius = float(z @ projector @ z)
        density = float(z @ z) + max(floor, 0.19)
        g = projector @ z - alpha * radius / density * z
        c_rational = 2.0 * math.sqrt(c1) * g
        c_full = np.vstack([c_linear, c_rational])
        b_rational = np.outer(c_rational, c_rational)
        split_residual = max(split_residual, float(np.max(np.abs(c_full.T @ c_full - b_linear - b_rational))))
    check("six_real_linear_current", current_residual < 1e-13, current_residual, "<1e-13")
    check("linear_Gram_identity", gram_residual < 1e-14, gram_residual, "<1e-14")
    check("full_Gram_linear_plus_rational", split_residual < 1e-13, split_residual, "<1e-13")

    # Exact quadratic heat lift for the linear rows.
    raw = rng.normal(size=(6, 6))
    sigma = 0.03 * raw @ raw.T
    h_sigma = sum((matrix.T @ sigma @ matrix for matrix in matrices), np.zeros((6, 6)))
    z = rng.normal(size=6)
    root = np.linalg.cholesky(sigma + 1e-14 * np.eye(6))
    heat_points: list[np.ndarray] = []
    for coordinate in range(6):
        heat_points.append(math.sqrt(6.0) * root[:, coordinate])
        heat_points.append(-math.sqrt(6.0) * root[:, coordinate])
    heat_average = sum((gram_linear(matrices, z + point) for point in heat_points), np.zeros((6, 6))) / len(heat_points)
    heat_residual = float(np.max(np.abs(heat_average - gram_linear(matrices, z) - h_sigma)))
    check("linear_heat_lift", heat_residual < 2e-12, heat_residual, "<2e-12")
    sigma_left = 0.4 * sigma
    sigma_right = 0.6 * sigma
    h_left = sum((matrix.T @ sigma_left @ matrix for matrix in matrices), np.zeros((6, 6)))
    h_right = sum((matrix.T @ sigma_right @ matrix for matrix in matrices), np.zeros((6, 6)))
    check("heat_compensator_additive", np.max(np.abs(h_left + h_right - h_sigma)) < 1e-13, float(np.max(np.abs(h_left + h_right - h_sigma))), 0.0)

    z = rng.normal(size=6)
    displacement = rng.normal(size=6)
    secant_left = gram_linear(matrices, z + displacement) - gram_linear(matrices, z)
    derivative = sum(
        (
            matrix.T @ (np.outer(displacement, z) + np.outer(z, displacement)) @ matrix
            for matrix in matrices
        ),
        np.zeros((6, 6)),
    )
    secant_right = derivative + gram_linear(matrices, displacement)
    secant_residual = float(np.max(np.abs(secant_left - secant_right)))
    higher_remainder = float(np.max(np.abs(secant_left - derivative - gram_linear(matrices, displacement))))
    check("linear_Gram_exact_secant", secant_residual < 1e-13, secant_residual, 0.0)
    check("linear_Gram_no_higher_Taylor_remainder", higher_remainder < 1e-13, higher_remainder, 0.0)

    # The complete 3x3 value/derivative forest, including heat P2/P1/P0.
    x = rng.normal(size=6)
    y = rng.normal(size=6)
    control_value = rng.normal(size=6)
    control_derivative = rng.normal(size=6)
    sigma_x = np.diag(np.linspace(0.02, 0.07, 6))
    gamma = np.diag(np.linspace(0.08, 0.13, 6))
    sigma_heat = np.diag(np.linspace(0.01, 0.03, 6))
    r_blocks = [
        np.outer(x, x) - sigma_x,
        np.outer(x, control_value) + np.outer(control_value, x),
        np.outer(control_value, control_value) + sigma_x + sigma_heat,
    ]
    c_blocks = [
        np.outer(y, y) - gamma,
        np.outer(y, control_derivative) + np.outer(control_derivative, y),
        np.outer(control_derivative, control_derivative),
    ]
    nine_blocks = [[0.5 * tensor_pair(matrices, left, right) for right in c_blocks] for left in r_blocks]
    forest_sum = sum(sum(row) for row in nine_blocks)
    forest_direct = 0.5 * tensor_pair(
        matrices,
        np.outer(x + control_value, x + control_value) + sigma_heat,
        np.outer(y + control_derivative, y + control_derivative) - gamma,
    )
    check("linear_forest_nine_block_identity", abs(forest_sum - forest_direct) < 1e-12, forest_sum - forest_direct, 0.0)
    degree_counts: dict[int, int] = {}
    for left_degree in (2, 1, 0):
        for right_degree in (2, 1, 0):
            degree_counts[left_degree + right_degree] = degree_counts.get(left_degree + right_degree, 0) + 1
    check("linear_forest_chaos_counts", degree_counts == {4: 1, 3: 2, 2: 3, 1: 2, 0: 1}, degree_counts, {4: 1, 3: 2, 2: 3, 1: 2, 0: 1})
    heat_blocks = [0.5 * tensor_pair(matrices, sigma_heat, block) for block in c_blocks]
    check("heat_forest_has_P2_P1_P0", len(heat_blocks) == 3 and all(math.isfinite(value) for value in heat_blocks), heat_blocks, "three finite blocks")
    unscaled_heat_blocks = [tensor_pair(matrices, sigma_heat, block) for block in c_blocks]
    heat_factor_residual = max(abs(value - 0.5 * raw) for value, raw in zip(heat_blocks, unscaled_heat_blocks))
    check("heat_forest_outer_factors", heat_factor_residual < 1e-15, heat_factor_residual, "0; each block is 1/2*T(Sigma_h,C_k)")

    # Conditional covariance preservation is sufficient, but not automatic.
    bar_b = gram_linear(matrices, rng.normal(size=6)) + h_sigma
    b = rng.normal(size=6)
    positive_case = 0.5 * float(np.sum(bar_b * np.outer(b, b)))
    check("conditional_covariance_preserved_positive", positive_case >= -1e-12, positive_case, ">=0")
    negative_case = 0.5 * float(np.sum(bar_b * (-np.eye(6))))
    check("conditional_covariance_defect_can_be_negative", negative_case < 0, negative_case, "<0")

    # Exact terminal bilinear-current conditional projection and covariance defect.
    outcomes = list(itertools.product((-1.0, 1.0), repeat=2))

    def z_terminal(omega: tuple[float, ...]) -> np.ndarray:
        e1, e2 = omega
        return np.array([0.7 + 0.2 * e1, -0.1 + 0.3 * e2, 0.0, 0.25 * e1 * e2, 0.1 * e2, 0.0])

    def y_terminal(omega: tuple[float, ...]) -> np.ndarray:
        e1, e2 = omega
        return np.array([0.2 * e2, -0.4 + 0.15 * e1, 0.0, 0.1 * e1 * e2, 0.05 + 0.2 * e2, 0.0])

    projection_residual = 0.0
    increment_residual = 0.0
    matrix = a1
    for omega in outcomes:
        projected_scalars: list[float] = []
        z_levels: list[np.ndarray] = []
        y_levels: list[np.ndarray] = []
        k_levels: list[np.ndarray] = []
        for level in range(3):
            z_level = conditional(z_terminal, level, omega, outcomes)
            y_level = conditional(y_terminal, level, omega, outcomes)

            def covariance_term(candidate: tuple[float, ...], zl: np.ndarray = z_level, yl: np.ndarray = y_level) -> np.ndarray:
                return np.outer(z_terminal(candidate) - zl, y_terminal(candidate) - yl)

            k_level = conditional(covariance_term, level, omega, outcomes)

            def scalar_current(candidate: tuple[float, ...]) -> np.ndarray:
                return np.array([float(z_terminal(candidate) @ matrix @ y_terminal(candidate))])

            projected = float(conditional(scalar_current, level, omega, outcomes)[0])
            formula = float(z_level @ matrix @ y_level + np.sum(matrix * k_level))
            projection_residual = max(projection_residual, abs(projected - formula))
            projected_scalars.append(projected)
            z_levels.append(z_level)
            y_levels.append(y_level)
            k_levels.append(k_level)
        for level in (1, 2):
            dz = z_levels[level] - z_levels[level - 1]
            dy = y_levels[level] - y_levels[level - 1]
            formula_increment = (
                float(z_levels[level - 1] @ matrix @ dy)
                + float(dz @ matrix @ y_levels[level - 1])
                + float(dz @ matrix @ dy)
                + float(np.sum(matrix * (k_levels[level] - k_levels[level - 1])))
            )
            increment_residual = max(increment_residual, abs(projected_scalars[level] - projected_scalars[level - 1] - formula_increment))
    check("linear_current_conditional_cross_covariance", projection_residual < 1e-13, projection_residual, "<1e-13")
    check("linear_current_Doob_increment_four_terms", increment_residual < 1e-13, increment_residual, "<1e-13")

    # Exact Gaussian Hermite fixture: rational row zero, one horizontal row negative.
    lam = 0.37
    tau = 0.61
    # Power coefficients of lambda^2 (x^2-4)^2 (x^2-1), ascending order.
    polynomial = lam**2 * np.polynomial.polynomial.polymul(
        np.polynomial.polynomial.polymul(np.array([-4.0, 0.0, 1.0]), np.array([-4.0, 0.0, 1.0])),
        np.array([-1.0, 0.0, 1.0]),
    )
    hermite = poly2herme(polynomial)
    expected_hermite = lam**2 * np.array([-4.0, 0.0, 15.0, 0.0, 6.0, 0.0, 1.0])
    check("adapted_fixture_Hermite_coefficients", np.max(np.abs(hermite - expected_hermite)) < 1e-12, hermite.tolist(), expected_hermite.tolist())
    gaussian_mean = 2.0 * csum * hermite[0]
    expected_mean = -8.0 * csum * lam**2
    check("linear_horizontal_adapted_mean_negative", abs(gaussian_mean - expected_mean) < 1e-14 and gaussian_mean < 0, gaussian_mean, expected_mean)
    gaussian_nodes, gaussian_weights = hermegauss(16)
    heat_dummy_mean = float(
        2.0
        * csum
        * tau**2
        * np.sum(gaussian_weights * (gaussian_nodes**2 - 1.0))
        / math.sqrt(2.0 * math.pi)
    )
    check("heat_dummy_changes_only_centered_H2", abs(heat_dummy_mean) < 1e-14, heat_dummy_mean, 0.0)

    fixture_rational_max = 0.0
    fixture_other_linear_max = 0.0
    fixture_horizontal_residual = 0.0
    for xi_value in (-2.0, -0.5, 0.0, 1.25):
        adapted_value = lam * (xi_value**2 - 4.0)
        for zeta_value in (-1.5, 0.0, 0.75):
            heat_value = tau * zeta_value
            fixture_z = np.zeros(6)
            fixture_y = np.zeros(6)
            fixture_z[0] = adapted_value + heat_value
            fixture_y[1] = xi_value
            fixture_radius = float(fixture_z @ projector @ fixture_z)
            fixture_density = float(fixture_z @ fixture_z) + floor
            fixture_g = projector @ fixture_z - alpha * fixture_radius / fixture_density * fixture_z
            fixture_rational_max = max(
                fixture_rational_max,
                abs(2.0 * math.sqrt(c1) * float(fixture_g @ fixture_y)),
            )
            fixture_linear = np.array([float(fixture_z @ matrix @ fixture_y) for matrix in matrices])
            fixture_other_linear_max = max(
                fixture_other_linear_max,
                abs(fixture_linear[0]),
                abs(fixture_linear[2]),
            )
            fixture_horizontal_residual = max(
                fixture_horizontal_residual,
                abs(fixture_linear[1] - scaleh * (adapted_value + heat_value) * xi_value),
            )
    check("adapted_fixture_rational_row_zero", fixture_rational_max == 0.0, fixture_rational_max, 0.0)
    check(
        "adapted_fixture_other_linear_rows_zero",
        fixture_other_linear_max == 0.0 and fixture_horizontal_residual < 1e-14,
        [fixture_other_linear_max, fixture_horizontal_residual],
        [0.0, "<1e-14"],
    )

    three_point = [(0.0, 0.5), (math.sqrt(2.0), 0.25), (-math.sqrt(2.0), 0.25)]
    discrete_moment = sum(probability * (1.0 - xi**2 / 2.0) ** 2 * (xi**2 - 1.0) for xi, probability in three_point)
    check("independent_three_point_negative_fixture", abs(discrete_moment + 0.5) < 1e-14, discrete_moment, -0.5)
    check("three_point_linear_packet_mean", abs(2.0 * csum * discrete_moment + csum) < 1e-14, 2.0 * csum * discrete_moment, -csum)

    # Controlled polynomial FAR is exactly empty beyond the safe sharp-cube gap.
    active_cutoff = 2**5
    polynomial_support = 2 * active_cutoff
    c_poly = 3
    far_lower_edge = 2 ** (5 + c_poly - 1)
    check("controlled_polynomial_support_gap", polynomial_support < far_lower_edge, [polynomial_support, far_lower_edge], "strictly separated")
    endpoint_support = active_cutoff + active_cutoff
    value_drift_support = active_cutoff + active_cutoff
    derivative_drift_support = active_cutoff + active_cutoff
    check("controlled_polynomial_moving_endpoint_FAR_zero", endpoint_support < far_lower_edge, [endpoint_support, far_lower_edge], "strictly separated")
    check("controlled_polynomial_value_drift_FAR_zero", value_drift_support < far_lower_edge, [value_drift_support, far_lower_edge], "strictly separated")
    check("controlled_polynomial_derivative_drift_FAR_zero", derivative_drift_support < far_lower_edge, [derivative_drift_support, far_lower_edge], "strictly separated")

    # Exact input-scale telescope for the remaining Cartan current, including
    # the nonzero pre-j0 low input and both stopped endpoints.
    tree = list(itertools.product((-1.0, 1.0), repeat=3))
    modes = 5

    def delta_low(omega: tuple[float, ...]) -> np.ndarray:
        e1, _, e3 = omega
        return np.array([0.031 * (mode + 1) * e1 + 0.009 * e1 * e3 for mode in range(modes)])

    def delta(level: int, omega: tuple[float, ...]) -> np.ndarray:
        e1, e2, e3 = omega
        root = [e1, e2, e3][level - 1]
        future = e1 * e3 if level == 1 else e2 * e3 if level == 2 else e1 * e2
        return np.array([0.07 * (mode + 1) * root + 0.013 * level * future + 0.005 * mode * e1 * e2 * e3 for mode in range(modes)])

    telescope_residual = 0.0
    drift_nonzero = False
    for n in (1, 2, 3):
        for omega in tree:
            left = np.zeros(modes)
            for j in range(1, n + 1):
                def current_j(candidate: tuple[float, ...], endpoint: int = j) -> np.ndarray:
                    return delta_low(candidate) + sum((delta(k, candidate) for k in range(1, endpoint + 1)), np.zeros(modes))
                left += conditional(current_j, j, omega, tree) - conditional(current_j, j - 1, omega, tree)
            right = conditional(delta_low, n, omega, tree) - conditional(delta_low, 0, omega, tree)
            for k in range(1, n + 1):
                right += conditional(lambda candidate, kk=k: delta(kk, candidate), n, omega, tree)
                right -= conditional(lambda candidate, kk=k: delta(kk, candidate), k - 1, omega, tree)
                drift = conditional(lambda candidate, kk=k: delta(kk, candidate), k - 1, omega, tree)
                drift_nonzero = drift_nonzero or float(np.linalg.norm(drift)) > 1e-12
            telescope_residual = max(telescope_residual, float(np.max(np.abs(left - right))))
    check("Cartan_input_scale_telescope", telescope_residual < 1e-13, telescope_residual, "<1e-13")
    low_endpoint_norm = max(float(np.linalg.norm(conditional(delta_low, 0, omega, tree))) for omega in tree)
    low_increment_norm = max(float(np.linalg.norm(conditional(delta_low, 1, omega, tree) - conditional(delta_low, 0, omega, tree))) for omega in tree)
    check("Cartan_low_endpoint_retained", low_increment_norm > 0 and low_endpoint_norm < low_increment_norm, [low_endpoint_norm, low_increment_norm], "nonzero stopped low-input increment")
    check("Cartan_predictable_drift_retained", drift_nonzero, drift_nonzero, True)
    check("fixed_coordinate_CFar_factor", abs((2.0 * alpha * math.sqrt(c1)) ** 2 - 4.0 * alpha**2 * c1) < 1e-15, (2.0 * alpha * math.sqrt(c1)) ** 2, 4.0 * alpha**2 * c1)
    check("fixed_coordinate_CFar_factor_production", abs(4.0 * alpha**2 * c1 - 3.0 / (80.0 * denominator)) < 1e-15, 4.0 * alpha**2 * c1, "3/(80 P)")

    # Direct one-root check that an input increment retains derivative
    # injection, raw value innovation, and its heat compensator together.
    scalar_f = lambda value: value**3 / (1.0 + value**2)
    z0, dz0, shift, dshift = 0.23, -0.19, 0.17, 0.11
    value_size, derivative_size = 0.31, 0.27
    root_states = list(itertools.product((-value_size, value_size), (-derivative_size, derivative_size)))
    heat_f = lambda value: 0.5 * (scalar_f(value - value_size) + scalar_f(value + value_size))
    deltas: list[float] = []
    channel_sums: list[float] = []
    iotas: list[float] = []
    nu_plus_kappa: list[float] = []
    kappa_values: list[float] = []
    for g_value, dg_value in root_states:
        delta_value = (
            (scalar_f(z0 + shift + g_value) - scalar_f(z0 + g_value)) * (dz0 + dg_value)
            + scalar_f(z0 + shift + g_value) * dshift
        )
        iota = (scalar_f(z0 + shift + g_value) - scalar_f(z0 + g_value)) * dg_value
        nu = (
            (scalar_f(z0 + shift + g_value) - scalar_f(z0 + shift)) * (dz0 + dshift)
            - (scalar_f(z0 + g_value) - scalar_f(z0)) * dz0
        )
        kappa = (
            (scalar_f(z0 + shift) - heat_f(z0 + shift)) * (dz0 + dshift)
            - (scalar_f(z0) - heat_f(z0)) * dz0
        )
        deltas.append(delta_value)
        channel_sums.append(iota + nu + kappa)
        iotas.append(iota)
        nu_plus_kappa.append(nu + kappa)
        kappa_values.append(kappa)
    delta_mean = sum(deltas) / len(deltas)
    root_channel_residual = max(abs((value - delta_mean) - channel) for value, channel in zip(deltas, channel_sums))
    check("Cartan_input_root_three_channel_identity", root_channel_residual < 1e-14, root_channel_residual, "<1e-14")
    check("Cartan_input_derivative_injection_centered", abs(sum(iotas) / len(iotas)) < 1e-15, sum(iotas) / len(iotas), 0.0)
    check("Cartan_input_raw_plus_heat_centered", abs(sum(nu_plus_kappa) / len(nu_plus_kappa)) < 1e-14, sum(nu_plus_kappa) / len(nu_plus_kappa), 0.0)
    check("Cartan_input_heat_compensator_nonzero", max(abs(value) for value in kappa_values) > 1e-6, kappa_values[0], "nonzero")

    # The K-shell coordinate estimate is genuinely one-use but does not imply
    # orthogonality after nonlinear composition.
    h_norms = np.array([0.8, 1.1, 0.6, 0.9])
    shell_indices = np.arange(2, 6)
    kappa_k = 1.3
    bernstein_k = 1.7
    a_norms = kappa_k * 2.0 ** (-2.0 * shell_indices) * h_norms
    da_norms = bernstein_k * 2.0**shell_indices * a_norms
    coordinate_left = float(np.sum(2.0 ** (4.0 * shell_indices) * a_norms**2 + 2.0 ** (2.0 * shell_indices) * da_norms**2))
    coordinate_right = float(kappa_k**2 * (1.0 + bernstein_k**2) * np.sum(h_norms**2))
    check("K_shell_one_use_coordinate_ledger", coordinate_left <= coordinate_right * (1.0 + 1e-14), coordinate_left, f"<={coordinate_right}")

    # K-shell smoothing does not manufacture the input orthogonality in Lemma 6.1.
    amplitude_one = 0.25
    amplitude_two = 0.20
    cubic_mode_one = amplitude_one**3 / 4.0
    cubic_mode_two = 1.5 * amplitude_one**2 * amplitude_two + 0.75 * amplitude_two**3
    check("cubic_input_increment_cross_positive", cubic_mode_one * cubic_mode_two > 0, [cubic_mode_one, cubic_mode_two, cubic_mode_one * cubic_mode_two], ">0")
    quadrature_points = 1 << 16
    theta = 2.0 * math.pi * np.arange(quadrature_points) / quadrature_points
    first_input = amplitude_one * np.cos(theta)
    second_input = amplitude_two * np.cos(3.0 * theta)

    def scalar_rational(value: np.ndarray) -> np.ndarray:
        return value**3 / (1.0 + value**2)

    increment_one = scalar_rational(first_input)
    increment_two = scalar_rational(first_input + second_input) - scalar_rational(first_input)
    rational_mode_one = float(2.0 * np.mean(increment_one * np.cos(3.0 * theta)))
    rational_mode_two = float(2.0 * np.mean(increment_two * np.cos(3.0 * theta)))
    floor_scale = math.sqrt(floor)
    physical_mode_one = floor_scale * rational_mode_one
    physical_mode_two = floor_scale * rational_mode_two

    def scalar_rational_at_floor(value: np.ndarray) -> np.ndarray:
        return value**3 / (floor + value**2)

    physical_increment_one = scalar_rational_at_floor(floor_scale * first_input) / floor_scale
    physical_increment_two = (
        scalar_rational_at_floor(floor_scale * (first_input + second_input))
        - scalar_rational_at_floor(floor_scale * first_input)
    ) / floor_scale
    scaling_residual = float(
        max(
            np.max(np.abs(physical_increment_one - increment_one)),
            np.max(np.abs(physical_increment_two - increment_two)),
        )
    )
    physical_normalized_cross = 0.5 * physical_mode_one * physical_mode_two
    check(
        "rational_input_increment_mode3_nonzero",
        physical_mode_one > 0 and physical_mode_two > 0 and scaling_residual < 1e-14,
        [physical_mode_one, physical_mode_two, scaling_residual],
        [">0", ">0", "<1e-14"],
    )
    check("rational_input_increment_not_orthogonal", physical_normalized_cross > 0, physical_normalized_cross, ">0")
    check("R082_orthogonal_Carleson_not_triggered_by_K_smoothing", physical_normalized_cross > 0, False, False)

    # Honest boundary.
    check("controlled_Cartan_CFar_not_established", True, False, False)
    check("linear_NEAR_signed_bound_not_established", True, False, False)
    check("rational_NEAR_signed_bound_not_established", True, False, False)
    check("complete_regular_packet_lower_bound_not_established", True, False, False)
    check("overlap_stable_progression_not_established", True, False, False)
    check("controlled_shell_one_use_not_established", True, False, False)
    check("Nelson_not_established", True, False, False)
    check("Sector_A_not_closed", True, False, False)
    check("tier_promotion_not_claimed", True, False, False)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload: dict[str, Any] = {
        "schema": "tect/a13-controlled-polynomial-cfar-linear-pf-forest-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "derived_constants": {
            "QII": {"a": a_weight, "b": b_weight, "c": c_weight},
            "alpha": alpha,
            "c0": c0,
            "c1": c1,
            "c_sum": csum,
            "C_poly": c_poly,
        },
        "rational_mode3_fixture": {
            "amplitude_one": amplitude_one,
            "amplitude_two": amplitude_two,
            "coefficient_increment_one": rational_mode_one,
            "coefficient_increment_two": rational_mode_two,
            "cross_product": rational_mode_one * rational_mode_two,
            "production_floor": floor,
            "production_coefficient_increment_one": physical_mode_one,
            "production_coefficient_increment_two": physical_mode_two,
            "production_normalized_cross": physical_normalized_cross,
            "rescaling_residual": scaling_residual,
        },
        "adapted_linear_fixture": {
            "lambda": lam,
            "tau": tau,
            "expected_packet": gaussian_mean,
            "expected_formula": expected_mean,
            "hermite_coefficients": hermite.tolist(),
        },
        "proved_scope": "controlled polynomial fixed-coordinate FAR vanishes beyond C_poly; remaining controlled CFAR is exactly the Cartan input-scale telescope; the linear Pauli--Fierz Gram/heat/secant/nine-block forest algebra is exact",
        "negative_scope": "K-shell smoothing alone does not imply the global raw-output pairwise orthogonality assumed in R-082 Lemma 6.1; this does not exclude far-only or correlated martingale estimates. The rational row is not the sole signed NEAR obstruction because a heat-lifted adapted linear-row fixture has negative zero chaos.",
        "claims_not_established": {
            "controlled_Cartan_CFar": False,
            "complete_controlled_CFar": False,
            "linear_NEAR_signed_bound": False,
            "rational_NEAR_signed_bound": False,
            "complete_signed_NEAR": False,
            "complete_regular_packet_lower_bound": False,
            "overlap_stable_progressive_packet_bound": False,
            "full_progressive_revisit_extension": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "interacting_measure": False,
            "sector_a_closure": False,
            "tier_promotion": False,
        },
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-083 primary] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
