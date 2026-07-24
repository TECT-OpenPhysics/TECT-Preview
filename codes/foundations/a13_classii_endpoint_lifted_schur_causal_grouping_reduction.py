#!/usr/bin/env python3
"""Primary audit for the A13 endpoint-lifted Schur/causal reduction.

The script derives every reported constant from the pinned production
coefficients, checks the exact endpoint-transported current decomposition,
tests its floor-uniform good/bad bounds, exercises the rotating phase-kernel
falsifier for the old affine tangent, and verifies the coherent heat-value
causal polarization which telescopes the control-derivative current.

It does not prove the remaining adapted Gaussian-rooted transported-current
bound, the controlled-shell one-use theorem, or the Nelson estimate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

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
import a13_classii_npc_cone_martingale_injection_reduction as npc  # noqa: E402
import a13_classii_translation_model_reduction as tr  # noqa: E402
import a6_classii_uv_power_counting as uv  # noqa: E402

CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ENDPOINT-LIFTED-SCHUR-CAUSAL-GROUPING-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-24-primary-endpoint-lifted-schur-causal-grouping-reduction/result.json"
)

# Test inputs and numerical regression thresholds, not derived model outputs.
RANDOM_SEED = 26072413
RANDOM_CASES = 360
IDENTITY_TOL = 4.0e-10
BOUND_TOL = 2.0e-9
ROTATING_EPSILON = 0.1
ROTATING_VERTICAL_AMPLITUDE = 7.0
GH_ORDER = 9
PURE_CONTROL_ETA = 1.0e-5
PURE_CONTROL_ZETA = 1.0e-5


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
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
    rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})


def production_data() -> tuple[dict[str, Any], np.ndarray, float]:
    parameters = npc.production_parameters()
    q_matrix = np.asarray(tr.coefficients(parameters), dtype=np.float64)
    q_matrix = np.asarray([[q_matrix[0], q_matrix[1]], [q_matrix[1], q_matrix[2]]])
    floor = float(parameters["rho_regularizer"])
    return parameters, q_matrix, floor


def real_generators() -> list[np.ndarray]:
    return [tr.realify(generator) for generator in uv.generators()]


def frame_jet(
    z: np.ndarray,
    floor: float,
    direction: np.ndarray | None = None,
    second: tuple[np.ndarray, np.ndarray] | None = None,
) -> tuple[list[np.ndarray], list[np.ndarray] | None, list[np.ndarray] | None]:
    """Return M_A, DM_A[direction], and D2M_A[h,k] from exact formulas."""
    z = np.asarray(z, dtype=np.float64)
    d_value = float(z @ z + floor)
    frames: list[np.ndarray] = []
    derivatives: list[np.ndarray] = []
    second_derivatives: list[np.ndarray] = []
    for symmetric in real_generators():
        sz = symmetric @ z
        q_value = float(z @ sz / d_value)
        r_value = sz - q_value * z
        frames.append(np.stack((2.0 * sz, 2.0 * r_value), axis=-1))
        if direction is not None:
            h = np.asarray(direction, dtype=np.float64)
            dq_h = 2.0 * float(r_value @ h) / d_value
            dp_h = 2.0 * (symmetric @ h)
            dv_h = dp_h - 2.0 * dq_h * z - 2.0 * q_value * h
            derivatives.append(np.stack((dp_h, dv_h), axis=-1))
        if second is not None:
            h, k = (np.asarray(item, dtype=np.float64) for item in second)
            dq_h = 2.0 * float(r_value @ h) / d_value
            dq_k = 2.0 * float(r_value @ k) / d_value
            d2q = 2.0 * float(h @ ((symmetric - q_value * np.eye(6)) @ k)) / d_value
            d2q -= 4.0 * float(r_value @ k) * float(z @ h) / (d_value * d_value)
            d2q -= 4.0 * float(r_value @ h) * float(z @ k) / (d_value * d_value)
            d2_qz = d2q * z + dq_h * k + dq_k * h
            second_derivatives.append(
                np.stack((np.zeros(6, dtype=np.float64), -2.0 * d2_qz), axis=-1)
            )
    return frames, derivatives if direction is not None else None, second_derivatives if second is not None else None


def current_vectors(frames: list[np.ndarray], derivative: np.ndarray) -> np.ndarray:
    return np.stack([frame.T @ derivative for frame in frames], axis=0)


def q_inner(left: np.ndarray, q_matrix: np.ndarray, right: np.ndarray) -> float:
    return float(np.einsum("ai,ij,aj->", left, q_matrix, right))


def q_square(value: np.ndarray, q_matrix: np.ndarray) -> float:
    return q_inner(value, q_matrix, value)


def local_terms(
    z: np.ndarray,
    a_control: np.ndarray,
    y: np.ndarray,
    b_control: np.ndarray,
    q_matrix: np.ndarray,
    floor: float,
) -> dict[str, float | np.ndarray]:
    frames_0, derivatives, _ = frame_jet(z, floor, direction=a_control)
    frames_1, _, _ = frame_jet(z + a_control, floor)
    assert derivatives is not None
    w = current_vectors(frames_0, y)
    endpoint = current_vectors(frames_1, y + b_control)
    delta = endpoint - w
    linear_endpoint = np.stack(
        [derivative.T @ y + frame_1.T @ b_control for derivative, frame_1 in zip(derivatives, frames_1)],
        axis=0,
    )
    linear_affine = np.stack(
        [derivative.T @ y + frame_0.T @ b_control for derivative, frame_0 in zip(derivatives, frames_0)],
        axis=0,
    )
    remainder = np.stack(
        [(frame_1 - frame_0 - derivative).T @ y for frame_0, frame_1, derivative in zip(frames_0, frames_1, derivatives)],
        axis=0,
    )
    raw = q_inner(w, q_matrix, delta) + 0.5 * q_square(delta, q_matrix)
    tangent_endpoint = q_inner(w, q_matrix, linear_endpoint)
    tangent_affine = q_inner(w, q_matrix, linear_affine)
    jacobi = 0.5 * q_square(delta, q_matrix)
    curvature = q_inner(w, q_matrix, remainder)
    return {
        "w": w,
        "endpoint": endpoint,
        "delta": delta,
        "linear_endpoint": linear_endpoint,
        "linear_affine": linear_affine,
        "remainder": remainder,
        "raw": raw,
        "tangent_endpoint": tangent_endpoint,
        "tangent_affine": tangent_affine,
        "jacobi": jacobi,
        "curvature": curvature,
    }


def constants(q_matrix: np.ndarray) -> dict[str, float]:
    lambda_q = float(np.linalg.eigvalsh(q_matrix)[-1])
    theta_good_bad = 2.0 / (1.0 + math.sqrt(1.0 + 32.0 * math.sqrt(2.0)))
    c_good_bad = 3.0 * lambda_q * (1.0 + math.sqrt(1.0 + 32.0 * math.sqrt(2.0))) ** 2
    theta_global = math.sqrt(34.0) / (math.sqrt(34.0) + 4.0 * math.sqrt(2.0))
    c_global = 24.0 * lambda_q * (math.sqrt(34.0) + 4.0 * math.sqrt(2.0))
    return {
        "lambda_q": lambda_q,
        "theta_good_bad": theta_good_bad,
        "c_good_bad": c_good_bad,
        "theta_global": theta_global,
        "c_global": c_global,
    }


def frame_and_local_audit(q_matrix: np.ndarray) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED)
    const = constants(q_matrix)
    max_frame_ratio = 0.0
    max_derivative_ratio = 0.0
    max_second_ratio = 0.0
    max_delta_residual = 0.0
    max_secant_residual = 0.0
    min_good_margin = math.inf
    min_bad_margin = math.inf
    min_global_margin = math.inf
    good_cases = 0
    bad_cases = 0
    for case in range(RANDOM_CASES):
        floor = 10.0 ** rng.uniform(-12.0, 3.0)
        z = rng.normal(size=6) * 10.0 ** rng.uniform(-2.0, 2.0)
        a_control = rng.normal(size=6) * 10.0 ** rng.uniform(-3.0, 1.0)
        y = rng.normal(size=6)
        b_control = rng.normal(size=6) * 10.0 ** rng.uniform(-1.0, 2.0)
        h = rng.normal(size=6)
        k = rng.normal(size=6)
        frames, derivatives, second_derivatives = frame_jet(
            z, floor, direction=h, second=(h, k)
        )
        assert derivatives is not None and second_derivatives is not None
        z_norm = float(np.linalg.norm(z))
        h_norm = float(np.linalg.norm(h))
        k_norm = float(np.linalg.norm(k))
        scale = math.sqrt(float(z @ z + floor))
        for frame, derivative, d2_frame in zip(frames, derivatives, second_derivatives):
            if z_norm > 0.0:
                max_frame_ratio = max(max_frame_ratio, float(np.linalg.norm(frame)) / z_norm)
            if h_norm > 0.0:
                max_derivative_ratio = max(
                    max_derivative_ratio, float(np.linalg.norm(derivative)) / h_norm
                )
            if h_norm * k_norm > 0.0:
                max_second_ratio = max(
                    max_second_ratio,
                    float(np.linalg.norm(d2_frame)) * scale / (h_norm * k_norm),
                )
        terms = local_terms(z, a_control, y, b_control, q_matrix, floor)
        delta_residual = np.asarray(terms["delta"]) - np.asarray(terms["linear_endpoint"]) - np.asarray(terms["remainder"])
        max_delta_residual = max(max_delta_residual, float(np.linalg.norm(delta_residual)))
        secant_residual = float(terms["raw"]) - (
            float(terms["tangent_endpoint"])
            + float(terms["jacobi"])
            + float(terms["curvature"])
        )
        max_secant_residual = max(max_secant_residual, abs(secant_residual))
        defect_scale = float(a_control @ a_control) * float(y @ y)
        global_margin = float(terms["raw"]) - float(terms["tangent_endpoint"]) - float(terms["jacobi"]) + const["c_global"] * defect_scale
        min_global_margin = min(min_global_margin, global_margin)
        if np.linalg.norm(a_control) <= const["theta_good_bad"] * scale:
            good_cases += 1
            margin = float(terms["raw"]) - float(terms["tangent_endpoint"]) - float(terms["jacobi"]) + const["c_good_bad"] * defect_scale
            min_good_margin = min(min_good_margin, margin)
        else:
            bad_cases += 1
            margin = float(terms["raw"]) + const["c_good_bad"] * defect_scale
            min_bad_margin = min(min_bad_margin, margin)
    return {
        **const,
        "random_cases": RANDOM_CASES,
        "good_cases": good_cases,
        "bad_cases": bad_cases,
        "max_frame_ratio": max_frame_ratio,
        "max_derivative_ratio": max_derivative_ratio,
        "max_second_ratio": max_second_ratio,
        "max_delta_residual": max_delta_residual,
        "max_secant_residual": max_secant_residual,
        "min_good_margin": min_good_margin,
        "min_bad_margin": min_bad_margin,
        "min_global_margin": min_global_margin,
    }


def rotating_kernel_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    eps = ROTATING_EPSILON
    vertical = ROTATING_VERTICAL_AMPLITUDE
    z = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    a_control = np.asarray([0.0, eps, 0.0, 0.0, 0.0, 0.0])
    y = np.asarray([0.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    b_control = vertical * np.asarray([0.0, 0.0, 0.0, 1.0, eps, 0.0])
    terms = local_terms(z, a_control, y, b_control, q_matrix, floor)
    parameters = npc.production_parameters()
    a_value, b_value, c_value = tr.coefficients(parameters)
    beta_0 = 4.0 * (a_value + 2.0 * b_value + c_value)
    expected_affine = beta_0 * eps * vertical
    endpoint_kernel_norm = float(np.linalg.norm(np.asarray(terms["endpoint"]) - np.asarray(terms["w"])))
    return {
        "epsilon": eps,
        "vertical_amplitude": vertical,
        "raw_secant": float(terms["raw"]),
        "affine_tangent": float(terms["tangent_affine"]),
        "expected_affine_tangent": expected_affine,
        "endpoint_tangent": float(terms["tangent_endpoint"]),
        "endpoint_jacobi": float(terms["jacobi"]),
        "endpoint_curvature": float(terms["curvature"]),
        "endpoint_current_change_norm": endpoint_kernel_norm,
        "affine_remainder": float(terms["raw"]) - float(terms["tangent_affine"]),
    }


def coherent_causal_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 91)
    shell_count = 7
    full_value = rng.normal(size=6)
    a_increments = [0.13 * rng.normal(size=6) for _ in range(shell_count)]
    b_increments = [0.17 * rng.normal(size=6) for _ in range(shell_count)]
    d_increments = [0.19 * rng.normal(size=6) for _ in range(shell_count)]
    accumulated_value = np.zeros(6)
    accumulated_control_derivative = np.zeros(6)
    accumulated_gaussian_derivative = np.zeros(6)
    sum_raw = 0.0
    sum_control = 0.0
    sum_gaussian = 0.0
    sum_cross = 0.0
    max_split_residual = 0.0
    max_cross_residual = 0.0
    initial_control_energy = 0.0
    initial_cross = 0.0
    terminal_control_energy = 0.0
    terminal_cross = 0.0
    noise_cross_sum = 0.0
    for index in range(shell_count):
        z_0 = full_value + accumulated_value
        z_1 = z_0 + a_increments[index]
        frames_0, _, _ = frame_jet(z_0, floor)
        frames_1, _, _ = frame_jet(z_1, floor)
        c_0 = current_vectors(frames_0, accumulated_control_derivative)
        g_0 = current_vectors(frames_0, accumulated_gaussian_derivative)
        c_1 = current_vectors(
            frames_1, accumulated_control_derivative + b_increments[index]
        )
        g_plus = current_vectors(frames_1, accumulated_gaussian_derivative)
        delta_c = c_1 - c_0
        delta_g = g_plus - g_0
        raw = 0.5 * q_square(c_1 + g_plus, q_matrix) - 0.5 * q_square(c_0 + g_0, q_matrix)
        control = 0.5 * q_square(c_1, q_matrix) - 0.5 * q_square(c_0, q_matrix)
        gaussian = 0.5 * q_square(g_plus, q_matrix) - 0.5 * q_square(g_0, q_matrix)
        cross = q_inner(c_0, q_matrix, delta_g)
        cross += q_inner(g_0, q_matrix, delta_c)
        cross += q_inner(delta_c, q_matrix, delta_g)
        cross_endpoint = q_inner(c_1, q_matrix, g_plus) - q_inner(c_0, q_matrix, g_0)
        max_split_residual = max(max_split_residual, abs(raw - control - gaussian - cross))
        max_cross_residual = max(max_cross_residual, abs(cross - cross_endpoint))
        if index == 0:
            initial_control_energy = 0.5 * q_square(c_0, q_matrix)
            initial_cross = q_inner(c_0, q_matrix, g_0)
        sum_raw += raw
        sum_control += control
        sum_gaussian += gaussian
        sum_cross += cross
        noise_current = current_vectors(frames_1, d_increments[index])
        noise_cross_sum += q_inner(c_1, q_matrix, noise_current)
        accumulated_value += a_increments[index]
        accumulated_control_derivative += b_increments[index]
        accumulated_gaussian_derivative += d_increments[index]
        terminal_control_energy = 0.5 * q_square(c_1, q_matrix)
        terminal_cross = q_inner(
            c_1, q_matrix, current_vectors(frames_1, accumulated_gaussian_derivative)
        )
    cross_telescoping_residual = sum_cross - (
        terminal_cross - initial_cross - noise_cross_sum
    )
    return {
        "shell_count": shell_count,
        "max_split_residual": max_split_residual,
        "max_cross_residual": max_cross_residual,
        "control_telescoping_residual": sum_control - (
            terminal_control_energy - initial_control_energy
        ),
        "cross_telescoping_residual": cross_telescoping_residual,
        "sum_raw": sum_raw,
        "sum_control": sum_control,
        "sum_gaussian": sum_gaussian,
        "sum_cross": sum_cross,
    }


def gh_cross_cancellation(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    nodes, weights = np.polynomial.hermite.hermgauss(GH_ORDER)
    nodes = math.sqrt(2.0) * nodes
    weights = weights / math.sqrt(math.pi)
    base = np.asarray([0.6, -0.2, 0.1, 0.05, -0.03, 0.02])
    control_value = np.asarray([0.12, 0.04, -0.02, 0.01, 0.03, -0.01])
    control_derivative = np.asarray([0.2, -0.1, 0.04, 0.03, 0.02, -0.05])
    value_direction = np.asarray([0.3, -0.1, 0.0, 0.2, 0.05, 0.0])
    derivative_direction = np.asarray([-0.2, 0.15, 0.1, 0.0, 0.05, -0.12])
    total = 0.0
    absolute_total = 0.0
    for index_s, value_node in enumerate(nodes):
        z = base + control_value + value_node * value_direction
        frames, _, _ = frame_jet(z, floor)
        control_current = current_vectors(frames, control_derivative)
        for index_t, derivative_node in enumerate(nodes):
            noise_current = current_vectors(frames, derivative_node * derivative_direction)
            term = q_inner(control_current, q_matrix, noise_current)
            weight = float(weights[index_s] * weights[index_t])
            total += weight * term
            absolute_total += weight * abs(term)
    return {
        "order": GH_ORDER,
        "signed_expectation": total,
        "absolute_expectation": absolute_total,
    }


def pure_control_separate_payment_nogo() -> dict[str, float]:
    # On a normalized circle use a_N=tN cos(Nx), a_2N=tN cos(2Nx).
    # Trapezoidal averaging is exact for this degree once the grid exceeds 24.
    grid = 256
    phase = 2.0 * math.pi * np.arange(grid) / grid
    mode_ratios = np.asarray([1.0, 2.0])
    mode_profiles = np.cos(mode_ratios[:, None] * phase[None, :])
    profile = np.sum(mode_profiles, axis=0)
    sixth_coefficient = float(np.mean(profile**6))
    interaction_coefficient = float(
        np.mean(mode_profiles[1] ** 2 * np.sin(mode_ratios[0] * phase) ** 2)
    )
    h2_coefficient = float(
        sum(
            ratio**4 * np.mean(mode_profile**2)
            for ratio, mode_profile in zip(mode_ratios, mode_profiles)
        )
    )
    amplitude_cutoff_power = 1.0
    spatial_derivative_cutoff_power = 1.0
    interaction_growth_power = (
        2.0 * amplitude_cutoff_power
        + 2.0 * (amplitude_cutoff_power + spatial_derivative_cutoff_power)
    )
    h2_growth_power = 2.0 * (
        amplitude_cutoff_power + 2.0 * spatial_derivative_cutoff_power
    )
    sextic_growth_power = 6.0 * amplitude_cutoff_power
    amplitude_ratio = 1.0
    scaled_margin = (
        interaction_coefficient * amplitude_ratio**4
        - PURE_CONTROL_ETA * h2_coefficient * amplitude_ratio**2
        - PURE_CONTROL_ZETA * sixth_coefficient * amplitude_ratio**6
    )
    return {
        "interaction_coefficient": interaction_coefficient,
        "h2_coefficient": h2_coefficient,
        "sixth_coefficient": sixth_coefficient,
        "eta_test_input": PURE_CONTROL_ETA,
        "zeta_test_input": PURE_CONTROL_ZETA,
        "scaled_margin": scaled_margin,
        "interaction_growth_power": interaction_growth_power,
        "h2_growth_power": h2_growth_power,
        "sextic_growth_power": sextic_growth_power,
    }


def main() -> int:
    parameters, q_matrix, floor = production_data()
    local = frame_and_local_audit(q_matrix)
    rotating = rotating_kernel_audit(q_matrix, floor)
    coherent = coherent_causal_audit(q_matrix, floor)
    gh = gh_cross_cancellation(q_matrix, floor)
    pure_control = pure_control_separate_payment_nogo()
    rows: list[dict[str, Any]] = []
    a_value, b_value, c_value = tr.coefficients(parameters)
    p_value = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    lambda_formula = (219.0 + 3.0 * math.sqrt(2129.0)) / (16000.0 * p_value)
    add(rows, "q_matrix_positive", float(np.linalg.eigvalsh(q_matrix)[0]) > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), "minimum > 0")
    add(rows, "lambda_formula", abs(local["lambda_q"] - lambda_formula) < IDENTITY_TOL, local["lambda_q"], lambda_formula)
    add(rows, "frame_bound", local["max_frame_ratio"] <= math.sqrt(8.0) + BOUND_TOL, local["max_frame_ratio"], math.sqrt(8.0))
    add(rows, "first_frame_jet_bound", local["max_derivative_ratio"] <= math.sqrt(68.0) + BOUND_TOL, local["max_derivative_ratio"], math.sqrt(68.0))
    add(rows, "second_frame_jet_bound", local["max_second_ratio"] <= 32.0 + BOUND_TOL, local["max_second_ratio"], 32.0)
    add(rows, "endpoint_delta_identity", local["max_delta_residual"] < IDENTITY_TOL, local["max_delta_residual"], IDENTITY_TOL)
    add(rows, "endpoint_secant_identity", local["max_secant_residual"] < IDENTITY_TOL, local["max_secant_residual"], IDENTITY_TOL)
    add(rows, "good_region_populated", local["good_cases"] > 0, local["good_cases"], ">0")
    add(rows, "bad_region_populated", local["bad_cases"] > 0, local["bad_cases"], ">0")
    add(rows, "optimized_good_bound", local["min_good_margin"] > -BOUND_TOL, local["min_good_margin"], f">={-BOUND_TOL}")
    add(rows, "optimized_bad_bound", local["min_bad_margin"] > -BOUND_TOL, local["min_bad_margin"], f">={-BOUND_TOL}")
    add(rows, "global_transport_bound", local["min_global_margin"] > -BOUND_TOL, local["min_global_margin"], f">={-BOUND_TOL}")
    add(rows, "rotating_raw_zero", abs(rotating["raw_secant"]) < IDENTITY_TOL, rotating["raw_secant"], 0.0)
    add(rows, "rotating_affine_tangent", abs(rotating["affine_tangent"] - rotating["expected_affine_tangent"]) < IDENTITY_TOL, rotating["affine_tangent"], rotating["expected_affine_tangent"])
    add(rows, "rotating_affine_remainder_negative", rotating["affine_remainder"] < -1.0e-3, rotating["affine_remainder"], "< -1e-3")
    add(rows, "rotating_endpoint_lift_cancels", abs(rotating["endpoint_tangent"]) + abs(rotating["endpoint_jacobi"]) + abs(rotating["endpoint_curvature"]) < IDENTITY_TOL, {key: rotating[key] for key in ("endpoint_tangent", "endpoint_jacobi", "endpoint_curvature")}, "all zero")
    add(rows, "causal_polarization_identity", coherent["max_split_residual"] < IDENTITY_TOL, coherent["max_split_residual"], IDENTITY_TOL)
    add(rows, "mixed_current_endpoint_identity", coherent["max_cross_residual"] < IDENTITY_TOL, coherent["max_cross_residual"], IDENTITY_TOL)
    add(rows, "control_current_telescopes", abs(coherent["control_telescoping_residual"]) < IDENTITY_TOL, coherent["control_telescoping_residual"], 0.0)
    add(rows, "mixed_current_noise_telescope", abs(coherent["cross_telescoping_residual"]) < IDENTITY_TOL, coherent["cross_telescoping_residual"], 0.0)
    add(rows, "fresh_derivative_cross_centers", abs(gh["signed_expectation"]) < IDENTITY_TOL and gh["absolute_expectation"] > 1.0e-4, gh, "signed zero; absolute nonzero")
    add(
        rows,
        "separate_pure_control_payment_fails",
        pure_control["scaled_margin"] > 0.1
        and pure_control["interaction_growth_power"] == 6.0
        and pure_control["h2_growth_power"] == 6.0
        and pure_control["sextic_growth_power"] == 6.0,
        pure_control,
        "positive margin with all three cutoff powers equal to 6",
    )
    passed = all(row["pass"] for row in rows)
    payload = {
        "schema": "tect/a13-endpoint-lifted-schur-causal-primary/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {
            "random_seed": RANDOM_SEED,
            "random_cases": RANDOM_CASES,
            "production_coefficients": {"a": a_value, "b": b_value, "c": c_value},
            "positive_floor": floor,
            "identity_tolerance": IDENTITY_TOL,
            "bound_tolerance": BOUND_TOL,
        },
        "computed": {
            "local": local,
            "rotating_kernel": rotating,
            "coherent_causal": coherent,
            "fresh_noise_cross": gh,
            "pure_control_separate_payment_nogo": pure_control,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": (
            "The endpoint-lifted local Schur bounds and coherent frozen-value causal "
            "polarization are verified. The adapted Gaussian-rooted transported-current "
            "bound, finite-energy extension, one-use, and Nelson estimate remain open."
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
        f"C#={local['c_good_bad']:.12g}; C*={local['c_global']:.12g}; "
        f"affine remainder={rotating['affine_remainder']:.8g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
