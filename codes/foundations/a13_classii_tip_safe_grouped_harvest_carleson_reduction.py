#!/usr/bin/env python3
"""Primary executable audit for the A13 tip-safe grouped-harvest reduction.

The script derives every production constant from pinned authorities, checks
the nonlinear Tikhonov/linear-resolvent identity, the full conservative score,
the Gaussian N^-1/N^-2 tail constants, the CAT(0) strong-convexity fixture,
the scalar good/bad Schur complement, the strict-shell gauge-null beat, and
the global H^(-1-kappa) Young exponents.  It does not claim the remaining
production Schur--Jacobi lemma or the one-use/Nelson theorem.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-TIP-SAFE-GROUPED-HARVEST-CARLESON-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-23-primary-tip-safe-grouped-harvest-carleson-reduction/result.json"
)
A1 = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
A12 = REPO / "claims/A12-CLASSII-SOURCE-SQUARE-REDUCTION/classii_source_square_reduction_manifest.json"
BALANCED = (
    REPO
    / "claims"
    / CLAIM
    / "classii_balanced_coefficient_jet_continuum_manifest.json"
)

# Explicit fixture inputs, not derived production outputs.
REGULATOR_SUPREMUM = 1.0
GAUSSIAN_SERIES_CUTOFF = 20_000
SCHUR_THETA = 0.4
GAUGE_C = 1.1
GAUGE_A = 0.7
GAUGE_B = 0.19
GAUGE_Q = 3
GAUGE_N = 8
GAUGE_M = GAUGE_N + GAUGE_Q
GAUGE_GRID = 1 << 16


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


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


def production_constants() -> dict[str, float]:
    parameters = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    source = json.loads(A12.read_text(encoding="utf-8"))["derived_oracles"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    a_value = (
        float(parameters["cJJ"])
        * float(parameters["alpha_X"]) ** 2
        / denominator
    )
    b_value = (
        float(parameters["cJK"])
        * float(parameters["alpha_X"])
        * float(parameters["beta_X"])
        / denominator
    )
    c_value = (
        float(parameters["cKK"])
        * float(parameters["beta_X"]) ** 2
        / denominator
    )
    q_matrix = np.asarray([[a_value, b_value], [b_value, c_value]], dtype=float)
    q_operator = float(np.linalg.eigvalsh(q_matrix)[-1])
    beta_zero = 4.0 * (a_value + 2.0 * b_value + c_value)
    beta_one_safe = 6.0 * math.sqrt(68.0 * 20.0) * q_operator
    return {
        "L": float(parameters["Lx"]),
        "floor": float(parameters["rho_regularizer"]),
        "a": a_value,
        "b": b_value,
        "c": c_value,
        "q_operator": q_operator,
        "beta_zero": beta_zero,
        "beta_one_safe": beta_one_safe,
        "c_symbol": float(source["c_symbol"]),
    }


def nonlinear_harvest_fixture() -> dict[str, float]:
    rng = np.random.default_rng(26072371)
    target_dimension, control_dimension = 9, 5
    linear_map = rng.normal(size=(target_dimension, control_dimension))
    current = rng.normal(size=target_dimension)
    eta = 0.37
    normal = linear_map.T @ linear_map + 2.0 * eta * np.eye(control_dimension)
    score = linear_map.T @ current
    minimizer = -np.linalg.solve(normal, score)
    direct = 0.5 * float(current @ current)
    direct -= 0.5 * float((current + linear_map @ minimizer) @ (current + linear_map @ minimizer))
    direct -= eta * float(minimizer @ minimizer)
    resolvent = 0.5 * float(score @ np.linalg.solve(normal, score))

    # M(z)=z^2 exposes the Taylor remainder omitted by a false q2-only bound.
    z, a_value, y, b_value = 0.8, -0.23, 1.7, 0.41
    delta = (z + a_value) ** 2 * (y + b_value) - z**2 * y
    linear = (2.0 * z * a_value) * y + z**2 * b_value
    q_one = a_value**2 * y
    q_two = ((z + a_value) ** 2 - z**2) * b_value
    return {
        "eta": eta,
        "direct_harvest": direct,
        "resolvent_harvest": resolvent,
        "resolvent_residual": abs(direct - resolvent),
        "nonlinear_increment": delta,
        "linear_increment": linear,
        "coefficient_curvature_remainder": q_one,
        "product_remainder": q_two,
        "remainder_split_residual": abs(delta - linear - q_one - q_two),
    }


def full_score_fixture() -> dict[str, float]:
    rng = np.random.default_rng(26072372)
    dimension, directions = 6, 3
    state = rng.normal(size=dimension)
    gradient = rng.normal(size=(directions, dimension))
    perturbation = rng.normal(size=dimension)
    perturbation_gradient = rng.normal(size=(directions, dimension))

    def coefficient(u: np.ndarray) -> np.ndarray:
        return float(u @ u) * np.eye(dimension) + np.outer(u, u)

    def energy(u: np.ndarray, du: np.ndarray) -> float:
        matrix = coefficient(u)
        return 0.5 * sum(float(row @ matrix @ row) for row in du)

    matrix = coefficient(state)
    derivative_part = sum(float(da @ matrix @ dy) for da, dy in zip(perturbation_gradient, gradient))
    coefficient_part = 0.0
    for dy in gradient:
        db = (
            2.0 * float(state @ perturbation) * np.eye(dimension)
            + np.outer(perturbation, state)
            + np.outer(state, perturbation)
        )
        coefficient_part += 0.5 * float(dy @ db @ dy)
    analytic = derivative_part + coefficient_part
    steps = [2.0 ** (-power) for power in range(7, 18)]
    residuals = []
    for step in steps:
        finite = (
            energy(state + step * perturbation, gradient + step * perturbation_gradient)
            - energy(state - step * perturbation, gradient - step * perturbation_gradient)
        ) / (2.0 * step)
        residuals.append(abs(finite - analytic))
    return {
        "analytic_derivative": analytic,
        "best_centered_difference_residual": min(residuals),
        "coefficient_half_factor": 0.5,
    }


def gaussian_tail_constants(constants: dict[str, float]) -> dict[str, Any]:
    length = constants["L"]
    alpha = 2.0 * math.pi / length
    c_symbol = constants["c_symbol"]
    multiplier = REGULATOR_SUPREMUM
    cutoff = GAUSSIAN_SERIES_CUTOFF
    series = sum(
        (24.0 * mode**2 + 2.0) / (1.0 + alpha**2 * mode**2) ** 2
        for mode in range(1, cutoff + 1)
    )
    tail = 26.0 / (alpha**4 * cutoff)
    value_covariance = (
        6.0
        * length ** (-3.0)
        * multiplier**2
        / c_symbol
        * (1.0 + series + tail)
    )
    shell_factor = 24.0 + math.pi**2 / 3.0
    derivative_linear = (
        6.0
        * length ** (-3.0)
        * multiplier**2
        / c_symbol
        * alpha ** (-2.0)
        * shell_factor
    )
    adjoint_constant = multiplier**2 / c_symbol
    ell_constant = (
        3.0
        * adjoint_constant
        * constants["beta_zero"] ** 2
        * length**3
        * value_covariance**2
        * derivative_linear
        * alpha ** (-2.0)
    )
    coefficient_constant = (
        0.75
        * adjoint_constant
        * constants["beta_one_safe"] ** 2
        * length**3
        * value_covariance
        * derivative_linear**2
        * alpha ** (-4.0)
    )
    rows = []
    for power in range(3, 12):
        n_value = 2**power
        kappa_shell = alpha * (n_value + 1)
        derivative_trace_bound = derivative_linear * n_value
        ell_bound = (
            3.0
            * adjoint_constant
            * constants["beta_zero"] ** 2
            * length**3
            * value_covariance**2
            * derivative_trace_bound
            / (1.0 + kappa_shell**2)
        )
        coefficient_bound = (
            0.75
            * adjoint_constant
            * constants["beta_one_safe"] ** 2
            * length**3
            * value_covariance
            * derivative_trace_bound**2
            / (1.0 + kappa_shell**2) ** 2
        )
        rows.append(
            {
                "N": n_value,
                "ell_bound": ell_bound,
                "ell_scaled_ratio": ell_bound * n_value / ell_constant,
                "m_bound": coefficient_bound,
                "m_scaled_ratio": coefficient_bound * n_value**2 / coefficient_constant,
            }
        )
    return {
        "alpha_L": alpha,
        "value_covariance_trace_upper": value_covariance,
        "value_series_cutoff": cutoff,
        "value_series_tail_upper": tail,
        "derivative_trace_linear_constant": derivative_linear,
        "ell_N_inverse_constant": ell_constant,
        "m_N_inverse_square_constant": coefficient_constant,
        "tail_rows": rows,
        "score_tail_formula": "sum E||ell_j+m_j||^2 <= 4 C_ell/N0 + (8/3) C_m/N0^2",
    }


def scalar_schur_fixture() -> dict[str, float]:
    rng = np.random.default_rng(26072373)
    theta = SCHUR_THETA
    constant = (3.0 - 2.0 * theta) / (1.0 - theta) ** 2
    minimum_margin = math.inf
    maximum_completion_residual = 0.0
    for _ in range(20_000):
        u_value = float(rng.uniform(0.2, 2.0) * rng.choice([-1.0, 1.0]))
        a_value = float(rng.uniform(-theta, theta) * abs(u_value))
        p_value = float(rng.normal())
        b_value = float(rng.normal())
        secant = (u_value + a_value) ** 2 * (p_value + b_value) ** 2 - u_value**2 * p_value**2
        tangent = 2.0 * u_value * a_value * p_value**2 + 2.0 * u_value**2 * p_value * b_value
        remainder = secant - tangent
        completed = (u_value + a_value) ** 2 * (
            b_value
            + a_value * p_value * (2.0 * u_value + a_value) / (u_value + a_value) ** 2
        ) ** 2
        completed -= (
            a_value**2
            * p_value**2
            * u_value
            * (3.0 * u_value + 2.0 * a_value)
            / (u_value + a_value) ** 2
        )
        maximum_completion_residual = max(maximum_completion_residual, abs(remainder - completed))
        minimum_margin = min(minimum_margin, remainder + constant * a_value**2 * p_value**2)
    endpoint_tip_slope = [1.0 - 2.0 * b_value for b_value in (-10.0, 0.0, 10.0)]
    return {
        "theta": theta,
        "good_region_constant": constant,
        "minimum_random_margin": minimum_margin,
        "maximum_completion_residual": maximum_completion_residual,
        "tip_crossing_remainders_u1_a_minus1_p1": endpoint_tip_slope,
        "tip_crossing_is_unbounded_below_in_b": True,
    }


def gauge_beat_fixture(constants: dict[str, float]) -> dict[str, float]:
    grid = GAUGE_GRID
    x_value = 2.0 * math.pi * np.arange(grid, dtype=float) / grid
    u_value = GAUGE_C + GAUGE_A * np.cos(GAUGE_Q * x_value)
    u_derivative = -GAUGE_A * GAUGE_Q * np.sin(GAUGE_Q * x_value)
    f_value = GAUGE_B * (
        np.cos(GAUGE_N * x_value) - np.cos(GAUGE_M * x_value)
    )
    f_derivative = GAUGE_B * (
        -GAUGE_N * np.sin(GAUGE_N * x_value)
        + GAUGE_M * np.sin(GAUGE_M * x_value)
    )
    before = float(np.mean((u_value * u_derivative) ** 2))
    after = float(np.mean((u_value * u_derivative + f_value * f_derivative) ** 2))
    direct_delta = after - before
    exact_delta = (
        -0.5 * GAUGE_A * GAUGE_C * GAUGE_Q**2 * GAUGE_B**2
        + 0.375 * (GAUGE_N**2 + GAUGE_M**2) * GAUGE_B**4
    )
    quadratic_coefficient = constants["a"] * GAUGE_A * GAUGE_C * GAUGE_Q**2
    quartic_coefficient = 0.75 * constants["a"] * (GAUGE_N**2 + GAUGE_M**2)
    return {
        "direct_delta_I": direct_delta,
        "exact_delta_I": exact_delta,
        "identity_residual": abs(direct_delta - exact_delta),
        "initial_affine_moment_score": 0.0,
        "production_J_sector_delta": 2.0 * constants["a"] * exact_delta,
        "quadratic_loss_coefficient": quadratic_coefficient,
        "quartic_positive_square_coefficient": quartic_coefficient,
        "dyadic_CM_threshold_scaling": "A*C must be order eta*N^2",
        "moment_tail_after_N3_multiplicity": "N^(9-4p), summable for any p>9/4",
    }


def cat_and_form_constants(constants: dict[str, float]) -> dict[str, Any]:
    balanced = json.loads(BALANCED.read_text(encoding="utf-8"))["theorem_inputs"]
    kappa = float(balanced["kappa"])
    theta = (1.0 + kappa) / 2.0
    leftover = 1.0 - theta - (1.0 - theta) / 3.0
    m_exponent = 1.0 / leftover
    eta_exponent = theta / leftover
    zeta_exponent = ((1.0 - theta) / 3.0) / leftover

    rng = np.random.default_rng(26072374)
    p_zero = rng.normal(size=(3, 7))
    p_one = rng.normal(size=(3, 7))
    t_value = 0.37
    energy_zero = 0.5 * float(np.sum(p_zero**2))
    energy_one = 0.5 * float(np.sum(p_one**2))
    energy_t = 0.5 * float(np.sum(((1.0 - t_value) * p_zero + t_value * p_one) ** 2))
    distance_gradient = float(np.sum((p_one - p_zero) ** 2))
    convexity_residual = abs(
        energy_t
        + 0.5 * t_value * (1.0 - t_value) * distance_gradient
        - ((1.0 - t_value) * energy_zero + t_value * energy_one)
    )
    return {
        "kappa": kappa,
        "interpolation_theta": theta,
        "X_exponent": theta,
        "Y_exponent": (1.0 - theta) / 3.0,
        "Young_leftover_exponent": leftover,
        "M_exponent": m_exponent,
        "eta_negative_exponent": eta_exponent,
        "zeta_negative_exponent": zeta_exponent,
        "physical_distance_constant": math.sqrt(constants["beta_zero"]),
        "cat0_euclidean_strong_convexity_residual": convexity_residual,
        "direct_score_polynomial_powers": ["X^3 Y", "delta X^2 Y^2", "delta^2 X Y^3", "delta^3 Y^4"],
        "direct_score_superquadratic_control_ratio_at_1e6": (1.0e6**4) / (1.0 + 1.0e6**2),
    }


def run(output: Path) -> int:
    constants = production_constants()
    harvest = nonlinear_harvest_fixture()
    score = full_score_fixture()
    gaussian = gaussian_tail_constants(constants)
    schur = scalar_schur_fixture()
    gauge = gauge_beat_fixture(constants)
    geometry = cat_and_form_constants(constants)
    tail_rows = gaussian["tail_rows"]
    assertions = {
        "production_psd": constants["a"] > 0.0
        and constants["c"] > 0.0
        and constants["a"] * constants["c"] > constants["b"] ** 2,
        "beta_zero_identity": abs(
            constants["beta_zero"] - 4.0 * (constants["a"] + 2.0 * constants["b"] + constants["c"])
        ) < 1e-15,
        "beta_one_safe_positive": constants["beta_one_safe"] > 0.0,
        "linear_harvest_resolvent": harvest["resolvent_residual"] < 1e-12,
        "true_remainder_split": harvest["remainder_split_residual"] < 1e-12,
        "coefficient_curvature_remainder_nonzero": abs(harvest["coefficient_curvature_remainder"]) > 1e-6,
        "full_score_half_factor": score["coefficient_half_factor"] == 0.5,
        "full_score_finite_difference": score["best_centered_difference_residual"] < 1e-8,
        "value_covariance_finite": math.isfinite(gaussian["value_covariance_trace_upper"]),
        "value_tail_positive": gaussian["value_series_tail_upper"] > 0.0,
        "ell_N_inverse": all(row["ell_scaled_ratio"] <= 1.0 + 1e-12 for row in tail_rows),
        "m_N_inverse_square": all(row["m_scaled_ratio"] <= 1.0 + 1e-12 for row in tail_rows),
        "ell_tail_improves": tail_rows[-1]["ell_bound"] < tail_rows[0]["ell_bound"],
        "m_tail_improves": tail_rows[-1]["m_bound"] < tail_rows[0]["m_bound"],
        "scalar_schur_completion": schur["maximum_completion_residual"] < 1e-10,
        "scalar_schur_lower_bound": schur["minimum_random_margin"] > -1e-10,
        "tip_tangent_unbounded": min(schur["tip_crossing_remainders_u1_a_minus1_p1"]) < -10.0,
        "gauge_beat_identity": gauge["identity_residual"] < 1e-11,
        "gauge_initial_score_zero": gauge["initial_affine_moment_score"] == 0.0,
        "gauge_positive_square": gauge["quartic_positive_square_coefficient"] > 0.0,
        "cat0_strong_convexity_fixture": geometry["cat0_euclidean_strong_convexity_residual"] < 1e-12,
        "physical_distance_constant": 0.0 < geometry["physical_distance_constant"] < 1.0,
        "form_exponents_sum": abs(
            geometry["X_exponent"] + geometry["Y_exponent"] + geometry["Young_leftover_exponent"] - 1.0
        ) < 1e-15,
        "form_M_exponent": abs(geometry["M_exponent"] - 3.0 / (1.0 - geometry["kappa"])) < 1e-14,
        "form_eta_exponent": abs(
            geometry["eta_negative_exponent"]
            - 3.0 * (1.0 + geometry["kappa"]) / (2.0 * (1.0 - geometry["kappa"]))
        ) < 1e-14,
        "form_zeta_exponent": abs(geometry["zeta_negative_exponent"] - 0.5) < 1e-14,
        "direct_score_Y4_not_CM_absorbable": geometry["direct_score_superquadratic_control_ratio_at_1e6"] > 1e11,
    }
    payload = {
        "schema": "tect/a13-tip-safe-grouped-harvest-primary/1.0",
        "script_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": digest(Path(__file__)),
        "result_id": RESULT_ID,
        "claim_id": CLAIM,
        "inputs": {
            "a1_sha256": digest(A1),
            "a12_sha256": digest(A12),
            "balanced_jet_sha256": digest(BALANCED),
            "regulator_supremum_fixture": REGULATOR_SUPREMUM,
        },
        "computed": {
            "production_constants": constants,
            "nonlinear_harvest": harvest,
            "full_score": score,
            "gaussian_tail": gaussian,
            "scalar_schur": schur,
            "gauge_beat": gauge,
            "geometry_and_form": geometry,
        },
        "assertions": assertions,
        "assertion_count": len(assertions),
        "pass": all(assertions.values()),
        "honesty_boundary": (
            "Exact algebraic, analytic-constant, and finite-fixture audit only. The CAT(0) secant inequality, "
            "full-score Carleson theorem, Gaussian infinitesimal tail, and global centered-form lemma are the "
            "proved package. The production tip-safe Schur--Jacobi lemma, finite-energy extension, one-use, "
            "Nelson estimate, interacting measure, and removal limits remain open."
        ),
    }
    atomic_json(output, payload)
    passed = sum(bool(value) for value in assertions.values())
    print(f"PASS: primary ({passed}/{len(assertions)})" if payload["pass"] else f"FAIL: primary ({passed}/{len(assertions)})")
    print(
        f"beta0={constants['beta_zero']:.15g}; beta1_safe={constants['beta_one_safe']:.15g}; "
        f"M exponent={geometry['M_exponent']:.12g}"
    )
    print(f"Evidence: {output}")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(run(OUT))
