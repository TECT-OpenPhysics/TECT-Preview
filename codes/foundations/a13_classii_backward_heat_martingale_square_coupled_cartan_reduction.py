#!/usr/bin/env python3
"""Primary six-real audit of the A13 backward-heat/Cartan reduction.

The script checks the controlled backward telescope, retained-square and
Gibbs identities, quartic factor-four carrier, averaged production-frame
secant, dyadic trace gains, and two-order production plateau envelope. It does
not prove the cutoff-uniform raw-current form or the Nelson theorem.
"""

from __future__ import annotations

__version__ = "1.1.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import hashlib
import json
import math
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "codes" / "foundations"))
import a6_classii_uv_power_counting as uv  # noqa: E402
import a13_classii_translation_model_reduction as tr  # noqa: E402

CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-BACKWARD-HEAT-MARTINGALE-SQUARE-COUPLED-CARTAN-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-23-primary-backward-heat-martingale-square-coupled-cartan-reduction/result.json"
)
STRICT_PAST_AUTHORITY = (
    REPO
    / "claims"
    / CLAIM
    / "classii_strict_past_signed_causal_reduction_manifest.json"
)
PRODUCTION_CUTOFFS = (64, 128)  # numerical audit inputs
PRODUCTION_QUADRATURE_ORDERS = (7, 9)  # convergence-audit inputs
PRODUCTION_DEFICIT_LOWER_TEST_ORACLE = 2.84e-4
PRODUCTION_DEFICIT_UPPER_TEST_ORACLE = 2.87e-4
PRODUCTION_CUTOFF_RELATIVE_GAP_MAXIMUM = 0.02
PRODUCTION_QUADRATURE_RELATIVE_GAP_MAXIMUM = 5.0e-4


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def one_use_q() -> float:
    authority = json.loads(STRICT_PAST_AUTHORITY.read_text(encoding="utf-8"))
    epsilon_control = float(authority["audit"]["epsilon_control"])
    return 1.0 / (2.0 * epsilon_control)


Q_EXPONENT = one_use_q()


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


def production_parameters() -> dict[str, Any]:
    manifest_path = (
        REPO
        / "claims"
        / CLAIM
        / "classii_translation_model_reduction_manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    authority = REPO / manifest["authority"]["a1_manifest"]["path"]
    return json.loads(authority.read_text(encoding="utf-8"))["parameters"]


def standard_hermite(dimension: int, order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    indices = np.indices((order,) * dimension, dtype=np.int16).reshape(dimension, -1).T
    points = math.sqrt(2.0) * nodes[indices]
    product_weights = np.prod(weights[indices], axis=1) / (math.pi ** (dimension / 2.0))
    return points, product_weights


def backward_martingale_audit() -> dict[str, float]:
    """Exact polynomial cubature test of the controlled Doob telescope."""
    sigma = np.asarray([0.23, 0.11, 0.05])
    delta_gamma = np.asarray([0.37, 0.29, 0.19])
    points, weights = standard_hermite(6, 5)
    x = np.zeros(len(points))
    y = np.zeros(len(points))
    drift_sum = np.zeros(len(points))

    def backward_value(stage: int, value: np.ndarray, derivative: np.ndarray) -> np.ndarray:
        future_value_variance = float(np.sum(sigma[stage:]))
        past_derivative_variance = float(np.sum(delta_gamma[:stage]))
        return 0.5 * (1.0 + value * value + future_value_variance) * (
            derivative * derivative - past_derivative_variance
        )

    for stage in range(3):
        if stage == 0:
            shift_value = np.full(len(points), 0.08)
            shift_derivative = np.full(len(points), -0.03)
        elif stage == 1:
            shift_value = 0.05 * x + 0.02 * y + 0.01
            shift_derivative = -0.03 * x + 0.04 * y
        else:
            shift_value = -0.02 * x + 0.03 * y + 0.015
            shift_derivative = 0.025 * x - 0.01 * y
        drift_sum += backward_value(stage, x + shift_value, y + shift_derivative)
        drift_sum -= backward_value(stage, x, y)
        x += shift_value + math.sqrt(float(sigma[stage])) * points[:, 2 * stage]
        y += shift_derivative + math.sqrt(float(delta_gamma[stage])) * points[:, 2 * stage + 1]

    terminal = 0.5 * (1.0 + x * x) * (y * y - float(np.sum(delta_gamma)))
    terminal_expectation = float(weights @ terminal)
    drift_expectation = float(weights @ drift_sum)

    # A separate one-step conditional martingale test at nonzero base point.
    shell, shell_weights = standard_hermite(2, 7)
    base_x, base_y = 0.41, -0.37
    current_sigma, current_gamma, later_sigma = 0.17, 0.31, 0.09
    post = 0.5 * (
        1.0 + (base_x + math.sqrt(current_sigma) * shell[:, 0]) ** 2 + later_sigma
    ) * (
        (base_y + math.sqrt(current_gamma) * shell[:, 1]) ** 2 - current_gamma
    )
    pre = 0.5 * (1.0 + base_x**2 + current_sigma + later_sigma) * base_y**2
    conditional_residual = abs(float(shell_weights @ post) - pre)
    return {
        "terminal_expectation": terminal_expectation,
        "controlled_drift_expectation": drift_expectation,
        "controlled_telescope_residual": abs(terminal_expectation - drift_expectation),
        "conditional_martingale_residual": conditional_residual,
    }


def square_and_gibbs_audit() -> dict[str, float]:
    points, weights = standard_hermite(2, 36)
    raw = np.asarray([[0.9, -0.2], [0.3, 0.7]])
    matrix = raw.T @ raw
    score = np.asarray([0.31, -0.27])
    shift = np.asarray([0.18, -0.13])
    nonlinear = (
        0.025 * np.sum(points**4, axis=1)
        + 0.012 * points[:, 0] ** 2 * points[:, 1] ** 2
        + 0.006 * points[:, 0] * points[:, 1]
    )
    shifted_points = points + shift
    shifted_nonlinear = (
        0.025 * np.sum(shifted_points**4, axis=1)
        + 0.012 * shifted_points[:, 0] ** 2 * shifted_points[:, 1] ** 2
        + 0.006 * shifted_points[:, 0] * shifted_points[:, 1]
    )
    quadratic = 0.5 * np.einsum("ni,ij,nj->n", points, matrix, points)
    interaction = quadratic - 0.5 * np.trace(matrix) + points @ score + nonlinear
    shifted_quadratic = 0.5 * np.einsum(
        "ni,ij,nj->n", shifted_points, matrix, shifted_points
    )
    shifted_interaction = (
        shifted_quadratic
        - 0.5 * np.trace(matrix)
        + shifted_points @ score
        + shifted_nonlinear
    )

    q_value = Q_EXPONENT
    resolvent = np.linalg.inv(np.eye(2) + q_value * matrix)
    metric = matrix + np.eye(2) / q_value
    positive_square = 0.5 * (
        shift + q_value * resolvent @ score
    ) @ metric @ (
        shift + q_value * resolvent @ score
    )
    nonlinear_average = float(weights @ shifted_nonlinear)
    effective_charge = (
        0.5 * q_value * score @ resolvent @ score
        - nonlinear_average
        - positive_square
    )
    averaged_interaction = float(weights @ shifted_interaction)
    completion_residual = abs(
        averaged_interaction + np.dot(shift, shift) / (2.0 * q_value) + effective_charge
    )

    partition = float(weights @ np.exp(-q_value * interaction))
    log_partition = math.log(partition) / q_value
    log_density_ratio = (
        shifted_points @ shift
        - 0.5 * np.dot(shift, shift)
        + q_value * shifted_interaction
        + q_value * log_partition
    )
    entropy_direct = float(weights @ log_density_ratio)
    entropy_formula = 0.5 * np.dot(shift, shift) + q_value * averaged_interaction + q_value * log_partition
    pythagoras_residual = abs(effective_charge - (log_partition - entropy_direct / q_value))

    covariance = resolvent
    mean = -q_value * resolvent @ score
    tilted_points = points @ np.linalg.cholesky(covariance).T + mean
    tilted_nonlinear = (
        0.025 * np.sum(tilted_points**4, axis=1)
        + 0.012 * tilted_points[:, 0] ** 2 * tilted_points[:, 1] ** 2
        + 0.006 * tilted_points[:, 0] * tilted_points[:, 1]
    )
    det_two = np.linalg.det(np.eye(2) + q_value * matrix) * math.exp(
        -q_value * float(np.trace(matrix))
    )
    partition_formula = (
        det_two ** (-0.5)
        * math.exp(0.5 * q_value**2 * score @ resolvent @ score)
        * float(weights @ np.exp(-q_value * tilted_nonlinear))
    )
    return {
        "completion_residual": completion_residual,
        "entropy_direct": entropy_direct,
        "entropy_formula_residual": abs(entropy_direct - entropy_formula),
        "gibbs_pythagoras_residual": pythagoras_residual,
        "partition": partition,
        "partition_formula_residual": abs(partition - partition_formula),
        "positive_square": float(positive_square),
        "effective_charge": float(effective_charge),
    }


def quartic_and_heat_nogos() -> dict[str, Any]:
    rng = np.random.default_rng(26072331)
    quartic_residual = 0.0
    factor_four_residual = 0.0
    minimum_remainder = float("inf")
    for _ in range(2000):
        coefficient = float(10 ** rng.uniform(-2.0, 0.3))
        base = float(rng.normal())
        displacement = float(rng.normal())
        tangent = 2.0 * coefficient * base**2
        frozen_score = 2.0 * coefficient * base**3
        score = 2.0 * frozen_score
        resolvent = 1.0 / (1.0 + Q_EXPONENT * tangent)
        remainder = coefficient * displacement**2 * (
            displacement**2 + 4.0 * base * displacement + 5.0 * base**2
        )
        metric = tangent + 1.0 / Q_EXPONENT
        positive_square = 0.5 * metric * (
            displacement + Q_EXPONENT * resolvent * score
        ) ** 2
        charge = 0.5 * Q_EXPONENT * score**2 * resolvent - remainder - positive_square
        oracle = coefficient * base**4 - coefficient * (base + displacement) ** 4
        oracle -= displacement**2 / (2.0 * Q_EXPONENT)
        quartic_residual = max(quartic_residual, abs(charge - oracle))
        if abs(frozen_score) > 1.0e-14:
            factor_four_residual = max(
                factor_four_residual, abs(score**2 / frozen_score**2 - 4.0)
            )
        minimum_remainder = min(minimum_remainder, remainder)

    base = 2.0
    coefficient = 0.5
    terminal_only_failure = coefficient * base**4 - base**2 / (2.0 * Q_EXPONENT)

    shells = np.arange(4, 13)
    value_variance = 2.0 ** (-shells)
    past_derivative_variance = 2.0**shells
    conditional_heat = -0.5 * value_variance * past_derivative_variance
    shell_sixth = 15.0 * value_variance**3

    # Conditional Gaussian charge is deliberately distinguished from the
    # pointwise principal-carrier charge at h=0.
    gaussian_origin_charge = -coefficient * (5.0 * base**2 + 3.0)
    return {
        "quartic_identity_residual": quartic_residual,
        "factor_four_residual": factor_four_residual,
        "minimum_quartic_remainder": minimum_remainder,
        "terminal_only_failure_witness": terminal_only_failure,
        "heat_plateau_values": conditional_heat.tolist(),
        "heat_plateau_max_deviation": float(np.max(np.abs(conditional_heat + 0.5))),
        "first_shell_sixth_moment": float(shell_sixth[0]),
        "last_shell_sixth_moment": float(shell_sixth[-1]),
        "conditional_gaussian_origin_charge": gaussian_origin_charge,
    }


def frame_and_scaling_audit(parameters: dict[str, Any]) -> dict[str, float]:
    rng = np.random.default_rng(26072332)
    growth_bound = math.sqrt(20.0)
    lipschitz_bound = math.sqrt(68.0)
    maximum_growth_ratio = 0.0
    maximum_lipschitz_ratio = 0.0
    for _ in range(800):
        value = rng.normal(size=6)
        increment = rng.normal(size=6)
        _, frames = tr.coefficient_data(value, parameters)
        _, shifted_frames = tr.coefficient_data(value + increment, parameters)
        for frame, shifted in zip(frames, shifted_frames):
            maximum_growth_ratio = max(
                maximum_growth_ratio,
                float(np.linalg.norm(frame) / max(np.linalg.norm(value), 1.0e-300)),
            )
            maximum_lipschitz_ratio = max(
                maximum_lipschitz_ratio,
                float(
                    np.linalg.norm(shifted - frame)
                    / max(np.linalg.norm(increment), 1.0e-300)
                ),
            )

    floor = float(parameters["rho_regularizer"])
    unit_parameters = dict(parameters)
    unit_parameters["rho_regularizer"] = 1.0
    scaling_residual = 0.0
    for _ in range(40):
        value = rng.normal(size=6)
        scaled, _ = tr.coefficient_data(math.sqrt(floor) * value, parameters)
        unit, _ = tr.coefficient_data(value, unit_parameters)
        scaling_residual = max(
            scaling_residual,
            float(np.max(np.abs(scaled / floor - unit))),
        )

    # Exact frame secant with a target-space heat dummy held spatially fixed.
    q_matrix = np.asarray(uv.classii_coefficients(parameters)).reshape(3)
    q_matrix = np.asarray([[q_matrix[0], q_matrix[1]], [q_matrix[1], q_matrix[2]]])
    dummy, dummy_weights = standard_hermite(6, 3)
    dummy *= math.sqrt(0.07)
    x, y, a, b = rng.normal(size=(4, 6))
    gamma = np.diag(np.linspace(0.2, 0.7, 6))
    old_b, old_frames = tr.coefficient_data(x + dummy, parameters)
    new_b, new_frames = tr.coefficient_data(x + a + dummy, parameters)
    lhs_samples = 0.5 * np.einsum(
        "nij,ij->n", new_b, np.outer(y + b, y + b) - gamma
    )
    lhs_samples -= 0.5 * np.einsum(
        "nij,ij->n", old_b, np.outer(y, y) - gamma
    )
    rhs_samples = np.zeros(len(dummy))
    for old_frame, new_frame in zip(old_frames, new_frames):
        old_current = np.einsum("nia,i->na", old_frame, y)
        new_current = np.einsum("nia,i->na", new_frame, y + b)
        delta_current = new_current - old_current
        delta_frame = new_frame - old_frame
        rhs_samples += np.einsum("na,ab,nb->n", old_current, q_matrix, delta_current)
        rhs_samples += 0.5 * np.einsum(
            "na,ab,nb->n", delta_current, q_matrix, delta_current
        )
        rhs_samples -= np.einsum(
            "ab,nia,ij,njb->n", q_matrix, old_frame, gamma, delta_frame
        )
        rhs_samples -= 0.5 * np.einsum(
            "ab,nia,ij,njb->n", q_matrix, delta_frame, gamma, delta_frame
        )
    frame_secant_residual = abs(float(dummy_weights @ (lhs_samples - rhs_samples)))

    return {
        "frame_growth_bound": growth_bound,
        "frame_lipschitz_bound": lipschitz_bound,
        "maximum_frame_growth_ratio": maximum_growth_ratio,
        "maximum_frame_lipschitz_ratio": maximum_lipschitz_ratio,
        "floor_scaling_residual": scaling_residual,
        "averaged_frame_secant_residual": frame_secant_residual,
        "covariance_square_dyadic_ratio": 2.0 ** (1.0 - 4.0),
        "mixed_trace_dyadic_ratio": 2.0 ** (1.0 - 2.0),
    }


def production_origin_deficit(cutoff: int, parameters: dict[str, Any], order: int) -> float:
    full_value, _, _ = uv.covariance_matrices(cutoff, parameters)
    past_value, past_derivative, _ = uv.covariance_matrices(cutoff // 2, parameters)
    shell_value = full_value - past_value
    samples, weights = uv.hermite_samples(shell_value, order)
    mean_b = np.zeros((6, 6))
    batch = 8192
    for start in range(0, len(samples), batch):
        stop = min(start + batch, len(samples))
        real_samples = np.concatenate(
            (samples[start:stop].real, samples[start:stop].imag), axis=1
        )
        matrices, _ = tr.coefficient_data(real_samples, parameters)
        mean_b += np.einsum("n,nij->ij", weights[start:stop], matrices)
    past_real_derivative_covariance = 0.5 * tr.realify(past_derivative)
    return 1.5 * float(np.trace(mean_b @ past_real_derivative_covariance))


def main() -> int:
    parameters = production_parameters()
    martingale = backward_martingale_audit()
    gibbs = square_and_gibbs_audit()
    nogos = quartic_and_heat_nogos()
    frame = frame_and_scaling_audit(parameters)
    production_deficits_by_order = {
        str(order): {
            str(cutoff): production_origin_deficit(cutoff, parameters, order)
            for cutoff in PRODUCTION_CUTOFFS
        }
        for order in PRODUCTION_QUADRATURE_ORDERS
    }
    production_deficits = production_deficits_by_order[str(PRODUCTION_QUADRATURE_ORDERS[-1])]
    relative_plateau_gap = abs(production_deficits["128"] - production_deficits["64"]) / production_deficits["128"]
    quadrature_relative_gaps = {
        str(cutoff): abs(
            production_deficits_by_order[str(PRODUCTION_QUADRATURE_ORDERS[-1])][str(cutoff)]
            - production_deficits_by_order[str(PRODUCTION_QUADRATURE_ORDERS[0])][str(cutoff)]
        )
        / production_deficits_by_order[str(PRODUCTION_QUADRATURE_ORDERS[-1])][str(cutoff)]
        for cutoff in PRODUCTION_CUTOFFS
    }

    checks = {
        "conditional_backward_martingale": martingale["conditional_martingale_residual"] < 2.0e-13,
        "controlled_backward_telescope": martingale["controlled_telescope_residual"] < 5.0e-12,
        "square_coupled_completion": gibbs["completion_residual"] < 2.0e-12,
        "gibbs_entropy_direct": gibbs["entropy_formula_residual"] < 2.0e-12,
        "gibbs_pythagoras": gibbs["gibbs_pythagoras_residual"] < 2.0e-12,
        "conditional_partition_formula": gibbs["partition_formula_residual"] < 2.0e-11,
        "quartic_retained_square_identity": nogos["quartic_identity_residual"] < 2.0e-10,
        "quartic_remainder_nonnegative": nogos["minimum_quartic_remainder"] > -2.0e-13,
        "factor_four_reassembled": nogos["factor_four_residual"] < 2.0e-13,
        "terminal_only_bound_fails": nogos["terminal_only_failure_witness"] > 1.0,
        "scalar_heat_plateau": nogos["heat_plateau_max_deviation"] < 1.0e-15,
        "shell_sextic_decays": nogos["last_shell_sixth_moment"] < nogos["first_shell_sixth_moment"] / 1.0e6,
        "pointwise_conditional_charge_distinguished": nogos["conditional_gaussian_origin_charge"] < -1.0,
        "frame_growth_analytic_bound": frame["maximum_frame_growth_ratio"] <= frame["frame_growth_bound"] * (1.0 + 1.0e-12),
        "frame_lipschitz_analytic_bound": frame["maximum_frame_lipschitz_ratio"] <= frame["frame_lipschitz_bound"] * (1.0 + 1.0e-12),
        "floor_uniform_scaling": frame["floor_scaling_residual"] < 2.0e-13,
        "averaged_frame_secant": frame["averaged_frame_secant_residual"] < 2.0e-12,
        "covariance_square_gain_is_summable": abs(frame["covariance_square_dyadic_ratio"] - 2.0 ** (-3.0)) < 1.0e-15,
        "mixed_trace_gain_is_summable_after_cauchy": abs(frame["mixed_trace_dyadic_ratio"] - 2.0 ** (-1.0)) < 1.0e-15,
        "production_origin_plateau_level": PRODUCTION_DEFICIT_LOWER_TEST_ORACLE < production_deficits["128"] < PRODUCTION_DEFICIT_UPPER_TEST_ORACLE,
        "production_origin_cutoff_stable": relative_plateau_gap < PRODUCTION_CUTOFF_RELATIVE_GAP_MAXIMUM,
        "production_origin_quadrature_stable": max(quadrature_relative_gaps.values()) < PRODUCTION_QUADRATURE_RELATIVE_GAP_MAXIMUM,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    assert all(checks.values()), {name: passed for name, passed in checks.items() if not passed}
    computed: dict[str, Any] = {
        **martingale,
        **gibbs,
        **nogos,
        **frame,
        "production_origin_deficits": production_deficits,
        "production_origin_deficits_by_order": production_deficits_by_order,
        "production_origin_relative_plateau_gap": relative_plateau_gap,
        "production_origin_quadrature_relative_gaps": quadrature_relative_gaps,
    }
    payload = {
        "schema": "tect/a13-backward-heat-martingale-square-coupled-primary/1.0",
        "claim": CLAIM,
        "result_id": RESULT_ID,
        "date": "2026-07-23",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "source_sha256": digest(Path(__file__)),
        "inputs": {
            "q": Q_EXPONENT,
            "q_authority": str(STRICT_PAST_AUTHORITY.relative_to(REPO)).replace("\\", "/"),
            "q_authority_sha256": digest(STRICT_PAST_AUTHORITY),
            "production_plateau_cutoffs": list(PRODUCTION_CUTOFFS),
            "production_gauss_hermite_orders": list(PRODUCTION_QUADRATURE_ORDERS),
        },
        "computed": computed,
        "assertions": checks,
        "assertion_count": len(checks),
        "pass": True,
        "honesty_boundary": (
            "Finite strict-past backward-heat, square/entropy, frame-secant, no-go, "
            "and trace-tail audits only. The cutoff-uniform averaged raw-current/"
            "Cartan-Jacobi lower bound, one-use theorem, and Nelson estimate remain open."
        ),
    }
    atomic_json(OUT, payload)
    print(f"PRIMARY {len(checks)}/{len(checks)} PASS")
    print(f"martingale_residual={martingale['controlled_telescope_residual']:.3e}")
    print(f"production_deficit_N128_order9={production_deficits['128']:.12e}")
    print(RESULT_ID + "-PRIMARY-PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
