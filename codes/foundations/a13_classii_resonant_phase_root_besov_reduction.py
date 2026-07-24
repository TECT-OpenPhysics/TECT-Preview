#!/usr/bin/env python3
"""Primary audit for the A13 resonant phase-root/Besov reduction.

The executable checks two exact production-frame diagnostics: a frozen
high-high-to-low nonlinear-secant resonance with no bare separation gain, and a smooth
strict-past phase feedback whose terminal Wick expectation is negative.  It
also verifies exact local phase covariance, the Cameron--Martin scaling which
prevents the registered finite-mode witnesses from becoming coercivity
counterexamples, and the exponent ledger for the viable Besov one-use route.

This is a route reduction.  It does not construct the adapted translated
Taylor one-form, prove terminal coercivity, or prove Nelson.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

import a13_classii_phase_kernel_causal_diagonal_reduction as r072
import a6_classii_uv_power_counting as uv

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RESONANT-PHASE-ROOT-BESOV-REDUCTION"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-24-primary-resonant-phase-root-besov-reduction/result.json"

# Regression inputs and tolerances only.
QUADRATURE_POINTS = 1 << 15
GAUSS_HERMITE_ORDERS = (48, 96)
QUADRATURE_CASES = ((5, 2, 0.35), (9, 3, 0.8), (17, 5, 1.2))
PHASE_SAMPLES = (0.0, 0.17, 0.43, 0.91, 1.37)
RANDOM_SEED = 24077413
RANDOM_CASES = 96
IDENTITY_TOL = 3.0e-11
QUADRATURE_TOL = 2.0e-10
NONZERO_TOL = 1.0e-10
BESOV_KAPPA = 1.0 / 10.0
PHASE_FEEDBACK_AMPLITUDE = 2.0 / 5.0
CM_TEST_ETA = 3.0 / 20.0
CM_FREQUENCIES = (4, 8, 16, 32, 64)
COVARIANCE_CUTOFFS = (4, 8, 16, 32, 64)
COVARIANCE_REFERENCE_CUTOFF = 192


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


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def coefficient_matrix(frames: list[np.ndarray], q_matrix: np.ndarray) -> np.ndarray:
    return sum((frame @ q_matrix @ frame.T for frame in frames), np.zeros((6, 6)))


def phase_rotation(theta_doublet: float, theta_singlet: float) -> np.ndarray:
    rotation = np.eye(6)
    for real_index, imaginary_index, theta in (
        (0, 3, theta_doublet),
        (1, 4, theta_doublet),
        (2, 5, theta_singlet),
    ):
        cosine = math.cos(theta)
        sine = math.sin(theta)
        rotation[real_index, real_index] = cosine
        rotation[real_index, imaginary_index] = -sine
        rotation[imaginary_index, real_index] = sine
        rotation[imaginary_index, imaginary_index] = cosine
    return rotation


def frozen_principal(q_matrix: np.ndarray, floor: float, mass_denominator: float) -> dict[str, Any]:
    e1 = np.eye(6)[0]
    e2 = np.eye(6)[1]
    frames = r072.frame_jet(e1, floor)[0]
    w = np.stack([frame.T @ e2 for frame in frames])
    hessian_half = [np.zeros((6, 2)) for _ in range(3)]
    hessian_half[0][:, 1] = -4.0 * e2 / (1.0 + floor)
    contraction = float(sum(e2 @ hessian_half[index] @ q_matrix @ w[index] for index in range(3)))
    q_sum = float(q_matrix[0, 1] + q_matrix[1, 1])
    q_sum_expected = 27.0 / (1600.0 * mass_denominator)
    contraction_expected = -27.0 / (200.0 * mass_denominator * (1.0 + floor))

    step = 2.0e-4
    plus = r072.frame_jet(e1 + step * e2, floor)[0]
    minus = r072.frame_jet(e1 - step * e2, floor)[0]
    numerical_half = [(plus[r] - 2.0 * frames[r] + minus[r]) / (2.0 * step**2) for r in range(3)]
    numerical_generator_contractions = [
        float(e2 @ numerical_half[r] @ q_matrix @ w[r]) for r in range(3)
    ]
    numerical_contraction = float(sum(numerical_generator_contractions))
    other_generator_projection = max(
        abs(numerical_generator_contractions[r]) for r in (1, 2)
    )
    return {
        "mass_denominator": mass_denominator,
        "q12_plus_q22": q_sum,
        "q12_plus_q22_expected": q_sum_expected,
        "analytic_contraction": contraction,
        "analytic_expected": contraction_expected,
        "finite_difference_contraction": numerical_contraction,
        "finite_difference_error": abs(numerical_contraction - contraction),
        "finite_difference_generator_contractions": numerical_generator_contractions,
        "other_generator_projection": other_generator_projection,
        "sigma_x_current": w[0].tolist(),
        "half_hessian_sigma_x_e2": hessian_half[0][:, 1].tolist(),
    }


def secant_formula(q_matrix: np.ndarray, floor: float, k_value: int, n_value: int, amplitude: float) -> dict[str, float]:
    if not k_value > n_value > 0:
        raise ValueError("the separated witness requires k>n>0")
    def periodic_integral(point_count: int) -> float:
        grid = 2.0 * math.pi * np.arange(point_count) / point_count
        high = amplitude * np.cos(k_value * grid)
        low_squared = np.cos(n_value * grid) ** 2
        multiplier = high**2 / (1.0 + floor + high**2)
        return float(np.mean(multiplier * low_squared))

    coarse_integral = periodic_integral(QUADRATURE_POINTS // 2)
    integral = periodic_integral(QUADRATURE_POINTS)
    closed_integral = 0.5 * (1.0 - math.sqrt((1.0 + floor) / (1.0 + floor + amplitude**2)))
    q_sum = float(q_matrix[0, 1] + q_matrix[1, 1])
    direct = -8.0 * q_sum * integral
    closed = -4.0 * q_sum * (1.0 - math.sqrt((1.0 + floor) / (1.0 + floor + amplitude**2)))
    return {
        "k": float(k_value),
        "n": float(n_value),
        "amplitude": amplitude,
        "quadrature_integral": integral,
        "closed_integral": closed_integral,
        "integral_error": abs(integral - closed_integral),
        "quadrature_refinement_error": abs(integral - coarse_integral),
        "direct_branch": direct,
        "closed_branch": closed,
        "branch_error": abs(direct - closed),
        "zero_mode_multiplier": 2.0 * closed_integral,
    }


def separation_audit(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    rows = [secant_formula(q_matrix, floor, *case) for case in QUADRATURE_CASES]
    amplitude = QUADRATURE_CASES[1][2]
    same_amplitude = [secant_formula(q_matrix, floor, k_value, 3, amplitude) for k_value in (7, 13, 29, 61)]
    values = np.asarray([row["direct_branch"] for row in same_amplitude])
    small_amplitude = secant_formula(q_matrix, floor, 37, 3, 1.0e-2)
    q_sum = float(q_matrix[0, 1] + q_matrix[1, 1])
    principal_limit = -8.0 * q_sum / (1.0 + floor)
    retained_variance_ratio = float(same_amplitude[0]["zero_mode_multiplier"] ** 2)
    return {
        "rows": rows,
        "same_amplitude_rows": same_amplitude,
        "separation_spread": float(np.max(values) - np.min(values)),
        "small_amplitude_row": small_amplitude,
        "small_amplitude_ratio": small_amplitude["direct_branch"] / small_amplitude["amplitude"] ** 2,
        "principal_quarter_limit": principal_limit / 4.0,
        "retained_low_mode_variance_ratio": retained_variance_ratio,
    }


def phase_feedback(q_matrix: np.ndarray, floor: float, mass_denominator: float) -> dict[str, Any]:
    e1 = np.eye(6)[0]
    e4 = np.eye(6)[3]
    values = []
    for theta in PHASE_SAMPLES:
        rotated = phase_rotation(theta, 0.0) @ e1
        matrix = coefficient_matrix(r072.frame_jet(rotated, floor)[0], q_matrix)
        values.append(float(e4 @ matrix @ e4))
    sine_squared = np.sin(np.asarray(PHASE_SAMPLES)) ** 2
    nonzero = sine_squared > 1.0e-12
    ratios = np.asarray(values)[nonzero] / sine_squared[nonzero]
    lambda_formula = 3.0 * (113.0 * floor**2 + 136.0 * floor + 48.0) / (
        2000.0 * mass_denominator * (1.0 + floor) ** 2
    )
    amplitude = PHASE_FEEDBACK_AMPLITUDE
    exact_expectation = -lambda_formula * amplitude**2 / (3.0 * math.sqrt(3.0))

    def gaussian_quadrature(order: int) -> float:
        nodes, weights = np.polynomial.hermite.hermgauss(order)
        xi_values = math.sqrt(2.0) * nodes
        integrand = []
        for xi in xi_values:
            theta = math.asin(amplitude * math.exp(-0.5 * float(xi) ** 2))
            rotated = phase_rotation(theta, 0.0) @ e1
            matrix = coefficient_matrix(r072.frame_jet(rotated, floor)[0], q_matrix)
            coefficient_value = float(e4 @ matrix @ e4)
            integrand.append(0.5 * coefficient_value * (float(xi) ** 2 - 1.0))
        return float(np.dot(weights, np.asarray(integrand)) / math.sqrt(math.pi))

    quadrature_values = {
        str(order): gaussian_quadrature(order) for order in GAUSS_HERMITE_ORDERS
    }
    quadrature_high = quadrature_values[str(GAUSS_HERMITE_ORDERS[-1])]
    gaussian_moments = {
        "E_exp_minus_xi2": 1.0 / math.sqrt(3.0),
        "E_xi2_exp_minus_xi2": 1.0 / (3.0 * math.sqrt(3.0)),
    }
    return {
        "angles": list(PHASE_SAMPLES),
        "quadratic_values": values,
        "lambda_ratios": ratios.tolist(),
        "lambda_spread": float(np.max(ratios) - np.min(ratios)),
        "lambda_formula": lambda_formula,
        "base_kernel_value": values[0],
        "feedback_amplitude": amplitude,
        "gaussian_moments": gaussian_moments,
        "exact_wick_expectation": exact_expectation,
        "quadrature_wick_expectations": quadrature_values,
        "quadrature_refinement_error": abs(
            quadrature_values[str(GAUSS_HERMITE_ORDERS[-1])]
            - quadrature_values[str(GAUSS_HERMITE_ORDERS[0])]
        ),
        "quadrature_formula_error": abs(quadrature_high - exact_expectation),
    }


def local_phase_covariance(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED)
    j_doublet, j_singlet = r072.phase_generators()
    frame_error = 0.0
    current_error = 0.0
    matrix_error = 0.0
    counterterm_error = 0.0
    kernel_error = 0.0
    for _ in range(RANDOM_CASES):
        value = rng.normal(size=6)
        derivative = rng.normal(size=6)
        theta_doublet, theta_singlet = rng.normal(size=2)
        dtheta_doublet, dtheta_singlet = rng.normal(size=2)
        rotation = phase_rotation(theta_doublet, theta_singlet)
        frames = r072.frame_jet(value, floor)[0]
        rotated_frames = r072.frame_jet(rotation @ value, floor)[0]
        for left, right in zip(rotated_frames, frames):
            frame_error = max(frame_error, float(np.linalg.norm(left - rotation @ right)))
            for phase in (j_doublet, j_singlet):
                kernel_error = max(kernel_error, float(np.linalg.norm(right.T @ phase @ value)))
        transformed_derivative = rotation @ (
            derivative + dtheta_doublet * (j_doublet @ value) + dtheta_singlet * (j_singlet @ value)
        )
        old_current = np.stack([frame.T @ derivative for frame in frames])
        new_current = np.stack([frame.T @ transformed_derivative for frame in rotated_frames])
        current_error = max(current_error, float(np.linalg.norm(old_current - new_current)))
        old_matrix = coefficient_matrix(frames, q_matrix)
        new_matrix = coefficient_matrix(rotated_frames, q_matrix)
        matrix_error = max(matrix_error, float(np.linalg.norm(new_matrix - rotation @ old_matrix @ rotation.T)))
        gamma = float(abs(rng.normal())) * np.eye(6)
        counterterm_error = max(counterterm_error, abs(float(np.trace(new_matrix @ gamma) - np.trace(old_matrix @ gamma))))
    return {
        "frame_covariance_error": frame_error,
        "current_invariance_error": current_error,
        "matrix_covariance_error": matrix_error,
        "isotropic_counterterm_error": counterterm_error,
        "phase_kernel_error": kernel_error,
    }


def cameron_martin_rescue(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    z = np.asarray([-1.0, -1.0, 0.0, 0.0, -1.0, 0.0])
    endpoint_value = np.asarray([1.0, -1.0, 0.0, 1.0, 0.0, 0.0])
    direction = endpoint_value - z
    derivative_value = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    kernel = np.asarray([-1.0, 0.0, 0.0, 1.0, -1.0, 0.0])
    frames_0, derivatives = r072.frame_jet(z, floor, direction=direction)
    frames_1, _ = r072.frame_jet(endpoint_value, floor)
    if derivatives is None:
        raise AssertionError("directional frame derivatives were not returned")
    currents = [item.T @ derivative_value for item in frames_0]
    leakage = np.zeros(6, dtype=np.float64)
    for frame_0, frame_1, derivative, current in zip(
        frames_0, frames_1, derivatives, currents
    ):
        leakage += (frame_1 - frame_0 - derivative) @ q_matrix @ current
    slope = float(kernel @ leakage)
    slope_oracle = 27.0 * (6.0 * floor**2 + 22.0 * floor + 27.0) / (
        400.0 * (floor + 3.0) ** 3
    )
    rows = []
    for frequency in CM_FREQUENCIES:
        d_value = frequency**2 + 1.0 + frequency**-2
        optimized_loss = -slope**2 / (24.0 * CM_TEST_ETA * d_value)
        rows.append(
            {
                "frequency": frequency,
                "H2_weight": 1.5 * d_value,
                "optimized_loss": optimized_loss,
                "N2_scaled_loss": -optimized_loss * frequency**2,
            }
        )
    return {
        "kernel_slope": slope,
        "kernel_slope_oracle": slope_oracle,
        "kernel_slope_error": abs(slope - slope_oracle),
        "eta": CM_TEST_ETA,
        "rows": rows,
        "dyadic_absolute_sum_upper": slope**2 / (24.0 * CM_TEST_ETA) * sum(1.0 / n**2 for n in CM_FREQUENCIES),
    }


def besov_budget() -> dict[str, Any]:
    kappa = BESOV_KAPPA
    besov_order = 0.5 + kappa
    x_power = 0.5
    y_power = 1.0 / 3.0
    slack = 1.0 - x_power - y_power
    random_power = 1.0 / slack
    return {
        "kappa": kappa,
        "current_order": -0.5 - kappa,
        "dual_besov_order": besov_order,
        "besov_order_below_one": besov_order < 1.0,
        "analytic_product_lemma": "||A^2 grad A||_{B^(1/2+kappa)_(1,1)} <= C ||A||_H2 ||A||_6^2 for 0<kappa<1/2",
        "control_budget_power": x_power,
        "sextic_budget_power": y_power,
        "young_slack": slack,
        "random_moment_power": random_power,
        "holder_conjugates": [2.0, 3.0, 6.0],
        "weighted_random_remainder": "C eta^(-3) zeta^(-2) ||J||^6",
    }


def coefficient_growth(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED + 1)
    lambda_q = float(np.linalg.eigvalsh(q_matrix)[-1])
    # For every Pauli generator, ||p_r||<=2|z| and the exact variance
    # identity gives ||v_r||<=2|z|.  Thus ||M_r||_F^2<=8|z|^2 and the sum
    # over three generators is bounded by 24 lambda_Q |z|^2.
    analytic_bound = 24.0 * lambda_q
    maximum_ratio = 0.0
    minimum_eigenvalue = math.inf
    for _ in range(RANDOM_CASES):
        value = rng.normal(size=6)
        matrix = coefficient_matrix(r072.frame_jet(value, floor)[0], q_matrix)
        maximum_ratio = max(maximum_ratio, float(np.linalg.eigvalsh(matrix)[-1]) / float(value @ value))
        minimum_eigenvalue = min(minimum_eigenvalue, float(np.linalg.eigvalsh(matrix)[0]))
    return {
        "lambda_Q": lambda_q,
        "analytic_operator_bound_over_rho": analytic_bound,
        "sample_max_operator_over_rho": maximum_ratio,
        "sample_min_eigenvalue": minimum_eigenvalue,
        "fixed_cutoff_negative_part": "W_J(z) >= -(1/2) integral Tr(B(z) Gamma_J), hence >= -C_J ||z||_2^2",
    }


def phase_covariance_anomaly(parameters: dict[str, Any]) -> dict[str, Any]:
    """Audit the only Wick defect left by an integrable local phase orbit.

    The U(1)_D x U(1)_S group projection kills precisely the complex
    doublet--singlet covariance block.  The analytic proof uses
    (K I+M)^(-1)-K^(-1)I= -K^(-1)(K I+M)^(-1)M, so the derivative-weighted
    noncommuting tail is O(sum |k|^-6)=O(N^-3).  The finite computation is a
    convention check, not the source of the exponent.
    """

    def perpendicular(matrix: np.ndarray) -> np.ndarray:
        result = np.zeros_like(matrix)
        result[:2, 2] = matrix[:2, 2]
        result[2, :2] = matrix[2, :2]
        return result

    _, reference, reference_meta = uv.covariance_matrices(COVARIANCE_REFERENCE_CUTOFF, parameters)
    reference_perp = perpendicular(reference)
    rows = []
    for cutoff in COVARIANCE_CUTOFFS:
        _, derivative, metadata = uv.covariance_matrices(cutoff, parameters)
        perp = perpendicular(derivative)
        tail = float(np.linalg.norm(reference_perp - perp, ord="fro"))
        rows.append(
            {
                "cutoff": cutoff,
                "perpendicular_norm": float(np.linalg.norm(perp, ord="fro")),
                "reference_tail": tail,
                "N3_scaled_tail": tail * cutoff**3,
                "quadratic_symbol_minimum": metadata["quadratic_symbol_minimum"],
            }
        )
    mass = uv.internal_mass_matrix(parameters)
    mass_perp = perpendicular(mass)
    derivative_real = r072.realify(reference)
    j_doublet, j_singlet = r072.phase_generators()
    commutators = {
        "doublet": float(np.linalg.norm(derivative_real @ j_doublet - j_doublet @ derivative_real)),
        "singlet": float(np.linalg.norm(derivative_real @ j_singlet - j_singlet @ derivative_real)),
        "common": float(np.linalg.norm(derivative_real @ (j_doublet + j_singlet) - (j_doublet + j_singlet) @ derivative_real)),
    }
    x_value = np.log(np.asarray([row["cutoff"] for row in rows[-3:]], dtype=np.float64))
    y_value = np.log(np.asarray([row["reference_tail"] for row in rows[-3:]], dtype=np.float64))
    diagnostic_slope = float(np.polyfit(x_value, y_value, 1)[0])
    return {
        "cutoffs": list(COVARIANCE_CUTOFFS),
        "reference_cutoff": COVARIANCE_REFERENCE_CUTOFF,
        "rows": rows,
        "diagnostic_tail_slope": diagnostic_slope,
        "mass_perpendicular_norm": float(np.linalg.norm(mass_perp, ord="fro")),
        "reference_perpendicular_norm": float(np.linalg.norm(reference_perp, ord="fro")),
        "phase_commutator_norms": commutators,
        "reference_symbol_minimum": reference_meta["quadratic_symbol_minimum"],
        "analytic_tail_identity": "Pi_perp[(K I+M)^-1]=-K^-1 Pi_perp[(K I+M)^-1 M]",
        "analytic_tail_power": -3.0,
        "wick_anomaly_bound": "|Delta W_phase| <= 72 lambda_Q max_i||Gamma_i^perp||_op ||z||_2^2 <= zeta ||z||_6^6 + C_zeta, uniformly in cutoff",
    }


def main() -> int:
    parameters, q_matrix, floor = r072.production_data()
    mass_denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    principal = frozen_principal(q_matrix, floor, mass_denominator)
    separation = separation_audit(q_matrix, floor)
    feedback = phase_feedback(q_matrix, floor, mass_denominator)
    gauge = local_phase_covariance(q_matrix, floor)
    cm_rescue = cameron_martin_rescue(q_matrix, floor)
    besov = besov_budget()
    growth = coefficient_growth(q_matrix, floor)
    phase_anomaly = phase_covariance_anomaly(parameters)

    rows: list[dict[str, Any]] = []
    add(rows, "production_Q_is_positive", float(np.linalg.eigvalsh(q_matrix)[0]) > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), ">0")
    add(rows, "q12_plus_q22_exact", abs(principal["q12_plus_q22"] - principal["q12_plus_q22_expected"]) < IDENTITY_TOL, principal["q12_plus_q22"], principal["q12_plus_q22_expected"])
    add(rows, "principal_contraction_exact", abs(principal["analytic_contraction"] - principal["analytic_expected"]) < IDENTITY_TOL, principal["analytic_contraction"], principal["analytic_expected"])
    add(rows, "principal_contraction_nonzero", abs(principal["analytic_contraction"]) > NONZERO_TOL, principal["analytic_contraction"], "nonzero")
    add(rows, "finite_difference_confirms_principal", principal["finite_difference_error"] < 2.0e-7, principal["finite_difference_error"], "<2e-7")
    add(rows, "other_generators_do_not_cancel_principal", principal["other_generator_projection"] < 2.0e-7, principal["finite_difference_generator_contractions"], "generators 2 and 3 vanish")
    add(rows, "secant_integrals_match_closed_form", max(max(row["integral_error"], row["quadrature_refinement_error"]) for row in separation["rows"]) < QUADRATURE_TOL, {"formula": max(row["integral_error"] for row in separation["rows"]), "refinement": max(row["quadrature_refinement_error"] for row in separation["rows"])}, f"<{QUADRATURE_TOL}")
    add(rows, "secant_branches_match_closed_form", max(row["branch_error"] for row in separation["rows"]) < QUADRATURE_TOL, max(row["branch_error"] for row in separation["rows"]), f"<{QUADRATURE_TOL}")
    add(rows, "bare_separation_gain_is_absent", abs(separation["separation_spread"]) < IDENTITY_TOL, separation["separation_spread"], "0")
    add(rows, "secant_small_amplitude_matches_principal_quarter", abs(separation["small_amplitude_ratio"] - separation["principal_quarter_limit"]) < 2.0e-6, {"ratio": separation["small_amplitude_ratio"], "limit": separation["principal_quarter_limit"]}, "absolute error<2e-6")
    add(rows, "low_mode_variance_is_retained", separation["retained_low_mode_variance_ratio"] > NONZERO_TOL, separation["retained_low_mode_variance_ratio"], ">0")
    add(rows, "phase_feedback_lambda_exact", feedback["lambda_spread"] < IDENTITY_TOL and abs(float(np.mean(feedback["lambda_ratios"])) - feedback["lambda_formula"]) < IDENTITY_TOL, {"spread": feedback["lambda_spread"], "mean": float(np.mean(feedback["lambda_ratios"]))}, feedback["lambda_formula"])
    add(rows, "base_phase_direction_is_kernel", abs(feedback["base_kernel_value"]) < IDENTITY_TOL, feedback["base_kernel_value"], "0")
    add(rows, "smooth_adapted_phase_feedback_has_negative_Wick_mean", feedback["quadrature_wick_expectations"][str(GAUSS_HERMITE_ORDERS[-1])] < 0.0 and feedback["quadrature_formula_error"] < 2.0e-12, {"quadrature": feedback["quadrature_wick_expectations"], "formula": feedback["exact_wick_expectation"]}, "negative and formula error<2e-12")
    add(rows, "Gaussian_feedback_quadrature_converges", feedback["quadrature_refinement_error"] < 2.0e-12, feedback["quadrature_refinement_error"], "<2e-12")
    add(rows, "local_phase_frames_are_covariant", gauge["frame_covariance_error"] < IDENTITY_TOL, gauge["frame_covariance_error"], f"<{IDENTITY_TOL}")
    add(rows, "integrable_local_phase_currents_are_invariant", gauge["current_invariance_error"] < IDENTITY_TOL, gauge["current_invariance_error"], f"<{IDENTITY_TOL}")
    add(rows, "coefficient_matrix_is_phase_covariant", gauge["matrix_covariance_error"] < IDENTITY_TOL, gauge["matrix_covariance_error"], f"<{IDENTITY_TOL}")
    add(rows, "isotropic_counterterm_is_phase_invariant", gauge["isotropic_counterterm_error"] < IDENTITY_TOL, gauge["isotropic_counterterm_error"], f"<{IDENTITY_TOL}")
    add(rows, "phase_vectors_are_in_frame_kernel", gauge["phase_kernel_error"] < IDENTITY_TOL, gauge["phase_kernel_error"], f"<{IDENTITY_TOL}")
    add(rows, "kernel_witness_CM_slope_is_frame_derived", cm_rescue["kernel_slope_error"] < IDENTITY_TOL, {"derived": cm_rescue["kernel_slope"], "oracle": cm_rescue["kernel_slope_oracle"]}, f"error<{IDENTITY_TOL}")
    add(rows, "kernel_witness_CM_optimization_decays_N_minus_2", max(abs(row["N2_scaled_loss"] - cm_rescue["rows"][-1]["N2_scaled_loss"]) for row in cm_rescue["rows"][-2:]) < 5.0e-5, [row["N2_scaled_loss"] for row in cm_rescue["rows"]], "convergent")
    add(rows, "kernel_witness_CM_losses_are_dyadically_summable", math.isfinite(cm_rescue["dyadic_absolute_sum_upper"]) and cm_rescue["dyadic_absolute_sum_upper"] > 0.0, cm_rescue["dyadic_absolute_sum_upper"], "finite positive")
    add(rows, "Besov_duality_order_is_subunit", besov["besov_order_below_one"], besov["dual_besov_order"], "<1")
    add(rows, "Besov_control_budget_has_positive_Young_slack", abs(besov["young_slack"] - 1.0 / 6.0) < IDENTITY_TOL, besov["young_slack"], "1/6")
    add(rows, "Besov_route_requires_sixth_current_moment", abs(besov["random_moment_power"] - 6.0) < IDENTITY_TOL, besov["random_moment_power"], "6")
    add(rows, "Holder_exponents_are_conjugate", abs(sum(1.0 / value for value in besov["holder_conjugates"]) - 1.0) < IDENTITY_TOL, besov["holder_conjugates"], "reciprocals sum to one")
    add(rows, "production_coefficient_is_PSD", growth["sample_min_eigenvalue"] > -IDENTITY_TOL, growth["sample_min_eigenvalue"], ">=0")
    add(rows, "production_coefficient_obeys_derived_quadratic_growth", growth["sample_max_operator_over_rho"] <= growth["analytic_operator_bound_over_rho"] + IDENTITY_TOL, growth["sample_max_operator_over_rho"], growth["analytic_operator_bound_over_rho"])
    add(rows, "phase_covariance_noncommuting_block_is_UV_finite", phase_anomaly["rows"][-1]["reference_tail"] < phase_anomaly["rows"][0]["reference_tail"], [row["reference_tail"] for row in phase_anomaly["rows"]], "strict tail decay")
    add(rows, "phase_covariance_tail_matches_resolvent_power", phase_anomaly["diagnostic_tail_slope"] < -2.0, phase_anomaly["diagnostic_tail_slope"], "diagnostic slope<-2; analytic power=-3")
    add(rows, "phase_covariance_anisotropy_is_nontrivial_but_finite", phase_anomaly["mass_perpendicular_norm"] > NONZERO_TOL and phase_anomaly["reference_perpendicular_norm"] > NONZERO_TOL, {"mass": phase_anomaly["mass_perpendicular_norm"], "covariance": phase_anomaly["reference_perpendicular_norm"]}, "both nonzero")
    add(rows, "common_phase_covariance_anomaly_vanishes", phase_anomaly["phase_commutator_norms"]["common"] < IDENTITY_TOL, phase_anomaly["phase_commutator_norms"], "common=0")
    add(rows, "relative_phase_covariance_anomaly_is_nonzero", min(phase_anomaly["phase_commutator_norms"]["doublet"], phase_anomaly["phase_commutator_norms"]["singlet"]) > NONZERO_TOL, phase_anomaly["phase_commutator_norms"], "doublet,singlet>0")
    add(rows, "scope_keeps_terminal_coercivity_open", True, "route reduction only", "no coercivity/Nelson claim")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-resonant-phase-root-besov-reduction-run/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "run_kind": "primary",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "floor": floor,
            "mass_denominator": mass_denominator,
            "quadrature_points": QUADRATURE_POINTS,
            "random_seed": RANDOM_SEED,
            "random_cases": RANDOM_CASES,
            "besov_kappa": BESOV_KAPPA,
        },
        "derived": {
            "principal": principal,
            "separation": separation,
            "phase_feedback": feedback,
            "local_phase_covariance": gauge,
            "cameron_martin_rescue": cm_rescue,
            "besov_budget": besov,
            "coefficient_growth": growth,
            "phase_covariance_anomaly": phase_anomaly,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed == len(rows),
        "summary": {"passed": passed, "total": len(rows), "status": "PASS" if passed == len(rows) else "FAIL"},
        "source": {"path": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "sha256": digest(Path(__file__).resolve()), "version": __version__},
        "honesty_boundary": "The exact witnesses refute bare positive separation gain and automatic signed centering only. The Cameron--Martin-weighted signed terminal theorem, adapted Taylor one-form construction, finite-energy recovery, one-use, and Nelson remain open.",
    }
    atomic_json(OUT, payload)
    print(f"A13 resonant phase-root/Besov primary: {passed}/{len(rows)} PASS")
    print(f"principal coefficient = {principal['analytic_contraction']:.16g}")
    print(f"phase-feedback Wick mean = {feedback['exact_wick_expectation']:.16g}")
    print(f"Besov random moment = {besov['random_moment_power']:.16g}")
    print(f"wrote {OUT.relative_to(REPO)}")
    if passed == len(rows):
        print("A13-CLASSII-RESONANT-PHASE-ROOT-BESOV-PRIMARY-PASS")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
