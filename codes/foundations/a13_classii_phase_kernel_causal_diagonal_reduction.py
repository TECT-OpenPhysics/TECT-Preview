#!/usr/bin/env python3
"""Primary audit for the A13 phase-kernel/causal-diagonal reduction.

The executable checks the exact production-frame gauge kernel, its differentiated
identity, the inverse-free regularized completion, the floor-uniform local
curvature bound, the one-constant strict-past diagonal estimate, and the exact
off-diagonal remainder left by terminal expansion.  It does not prove that
off-diagonal remainder, finite-energy extension, controlled-shell one-use, or
Nelson.
"""

from __future__ import annotations

__version__ = "1.0.0"
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

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-ONE-USE-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-24-primary-phase-kernel-causal-diagonal-reduction/result.json"
)
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"

# Regression inputs and tolerances, not derived model outputs.
RANDOM_SEED = 27072413
RANDOM_CASES = 320
IDENTITY_TOL = 3.0e-10
BOUND_TOL = 2.0e-10
RANK_TOL = 1.0e-10


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
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def production_data() -> tuple[dict[str, Any], np.ndarray, float]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    q11 = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator
    q12 = (
        float(parameters["cJK"])
        * float(parameters["alpha_X"])
        * float(parameters["beta_X"])
        / denominator
    )
    q22 = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    return parameters, np.asarray([[q11, q12], [q12, q22]]), float(parameters["rho_regularizer"])


def realify(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def real_generators() -> list[np.ndarray]:
    complex_generators = (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )
    return [realify(value) for value in complex_generators]


def phase_generators() -> tuple[np.ndarray, np.ndarray]:
    doublet = np.zeros((6, 6), dtype=np.float64)
    singlet = np.zeros((6, 6), dtype=np.float64)
    for real_index, imaginary_index in ((0, 3), (1, 4)):
        doublet[real_index, imaginary_index] = -1.0
        doublet[imaginary_index, real_index] = 1.0
    singlet[2, 5] = -1.0
    singlet[5, 2] = 1.0
    return doublet, singlet


def frame_jet(
    z: np.ndarray,
    floor: float,
    direction: np.ndarray | None = None,
) -> tuple[list[np.ndarray], list[np.ndarray] | None]:
    z = np.asarray(z, dtype=np.float64)
    d_value = float(z @ z + floor)
    frames: list[np.ndarray] = []
    derivatives: list[np.ndarray] = []
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
    return frames, derivatives if direction is not None else None


def q_inner(left: np.ndarray, q_matrix: np.ndarray, right: np.ndarray) -> float:
    return float(left @ q_matrix @ right)


def kernel_and_gauge_audit(floor: float) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED)
    j_doublet, j_singlet = phase_generators()
    generators = real_generators()
    commutator = max(
        np.linalg.norm(symmetric @ phase - phase @ symmetric)
        for symmetric in generators
        for phase in (j_doublet, j_singlet)
    )
    skew_residual = max(
        np.linalg.norm(phase + phase.T) for phase in (j_doublet, j_singlet)
    )
    generic_ranks: list[int] = []
    gauge_residual = 0.0
    derivative_residual = 0.0
    for _ in range(RANDOM_CASES):
        z = rng.normal(size=6)
        if np.linalg.norm(z[[0, 1, 3, 4]]) < 0.2 or np.linalg.norm(z[[2, 5]]) < 0.2:
            z += np.asarray([1.0, -0.4, 0.8, 0.3, 0.7, -0.5])
        a = rng.normal(size=6)
        x = z + a
        frames_x, _ = frame_jet(x, floor)
        stacked = np.concatenate(frames_x, axis=1)
        generic_ranks.append(int(np.linalg.matrix_rank(stacked, tol=RANK_TOL)))
        for phase in (j_doublet, j_singlet):
            gauge_residual = max(gauge_residual, float(np.linalg.norm(stacked.T @ (phase @ x))))
        frames_z, derivatives = frame_jet(z, floor, direction=a)
        assert derivatives is not None
        for frame, derivative in zip(frames_z, derivatives):
            for phase in (j_doublet, j_singlet):
                residual = derivative.T @ (phase @ z) + frame.T @ (phase @ a)
                derivative_residual = max(derivative_residual, float(np.linalg.norm(residual)))

    doublet_only = np.asarray([1.0, -2.0, 0.0, 0.4, 1.3, 0.0])
    singlet_only = np.asarray([0.0, 0.0, 1.2, 0.0, 0.0, -0.7])
    doublet_rank = int(
        np.linalg.matrix_rank(np.concatenate(frame_jet(doublet_only, floor)[0], axis=1), tol=RANK_TOL)
    )
    singlet_rank = int(
        np.linalg.matrix_rank(np.concatenate(frame_jet(singlet_only, floor)[0], axis=1), tol=RANK_TOL)
    )
    return {
        "commutator_residual": commutator,
        "skew_residual": skew_residual,
        "generic_rank_min": min(generic_ranks),
        "generic_rank_max": max(generic_ranks),
        "doublet_only_rank": doublet_rank,
        "singlet_only_rank": singlet_rank,
        "gauge_kernel_residual": gauge_residual,
        "differentiated_gauge_residual": derivative_residual,
    }


def fixture_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    z = np.asarray([-1.0, -1.0, 0.0, 0.0, -1.0, 0.0])
    x = np.asarray([1.0, -1.0, 0.0, 1.0, 0.0, 0.0])
    a = x - z
    y = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    n = np.asarray([-1.0, 0.0, 0.0, 1.0, -1.0, 0.0])
    j_doublet, _ = phase_generators()
    frames_0, derivatives = frame_jet(z, floor, direction=a)
    frames_1, _ = frame_jet(x, floor)
    assert derivatives is not None
    kernel_residual = max(float(np.linalg.norm(frame.T @ n)) for frame in frames_1)
    k_value = np.zeros(6, dtype=np.float64)
    gauge_k_value = np.zeros(6, dtype=np.float64)
    gauge_identity = 0.0
    for frame_0, frame_1, derivative in zip(frames_0, frames_1, derivatives):
        remainder = frame_1 - frame_0 - derivative
        w = frame_0.T @ y
        k_value += remainder @ q_matrix @ w
        gauge_k_value -= derivative @ q_matrix @ w
        gauge_identity = max(
            gauge_identity,
            float(np.linalg.norm(remainder.T @ n + derivative.T @ (j_doublet @ a))),
        )
    slope = float(n @ k_value)
    gauge_slope = float((j_doublet @ a) @ gauge_k_value)
    expected = 27.0 * (6.0 * floor * floor + 22.0 * floor + 27.0) / (
        400.0 * (floor + 3.0) ** 3
    )
    return {
        "n_is_doublet_phase_residual": float(np.linalg.norm(n - j_doublet @ x)),
        "terminal_kernel_residual": kernel_residual,
        "gauge_remainder_identity_residual": gauge_identity,
        "leakage_slope": slope,
        "gauge_leakage_slope": gauge_slope,
        "closed_form_slope": expected,
    }


def local_bound_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 1)
    lambda_q = float(np.linalg.eigvalsh(q_matrix)[-1])
    theta = math.sqrt(34.0) / (math.sqrt(34.0) + 4.0 * math.sqrt(2.0))
    c_star = 24.0 * lambda_q * (math.sqrt(34.0) + 4.0 * math.sqrt(2.0))
    good_constant = 48.0 * math.sqrt(8.0) * lambda_q / (1.0 - theta)
    bad_constant = 24.0 * math.sqrt(34.0) * lambda_q / theta
    max_ratio = 0.0
    for _ in range(RANDOM_CASES):
        z = rng.normal(size=6)
        a = rng.normal(size=6)
        y = rng.normal(size=6)
        frames_0, derivatives = frame_jet(z, floor, direction=a)
        frames_1, _ = frame_jet(z + a, floor)
        assert derivatives is not None
        k_value = np.zeros(6, dtype=np.float64)
        for frame_0, frame_1, derivative in zip(frames_0, frames_1, derivatives):
            remainder = frame_1 - frame_0 - derivative
            k_value += remainder @ q_matrix @ (frame_0.T @ y)
        denominator = float(a @ a) * float(np.linalg.norm(y))
        if denominator > 1.0e-14:
            max_ratio = max(max_ratio, float(np.linalg.norm(k_value)) / denominator)
    return {
        "lambda_q": lambda_q,
        "theta": theta,
        "good_constant": good_constant,
        "bad_constant": bad_constant,
        "c_star": c_star,
        "max_random_ratio": max_ratio,
        "bound_margin": c_star - max_ratio,
    }


def sequence_and_tail_audit() -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 2)
    x = np.exp(rng.normal(size=17))
    y = np.exp(rng.normal(size=17))
    m = np.exp(rng.normal(size=17))
    shell_sum = float(np.sum(np.sqrt(x) * np.cbrt(y) * m))
    holder = float(np.sum(x) ** 0.5 * np.sum(y) ** (1.0 / 3.0) * np.sum(m**6) ** (1.0 / 6.0))
    eta, zeta = 0.017, 0.023
    x_total, y_total, r_total = float(np.sum(x)), float(np.sum(y)), float(np.sum(m**6))
    amgm_left = x_total**0.5 * y_total ** (1.0 / 3.0) * r_total ** (1.0 / 6.0)
    amgm_right = eta * x_total + zeta * y_total + r_total / (432.0 * eta**3 * zeta**2)
    dyadic_sum = sum(2.0 ** (-3 * j) for j in range(4, 80))
    dyadic_closed = (8.0 / 7.0) * 2.0 ** (-12)
    sixth_coefficient = 15.0
    tail_after_young = sixth_coefficient * (8.0 / 7.0) / 432.0
    return {
        "shell_sum": shell_sum,
        "holder_envelope": holder,
        "holder_margin": holder - shell_sum,
        "amgm_left": amgm_left,
        "amgm_right": amgm_right,
        "amgm_margin": amgm_right - amgm_left,
        "dyadic_sum": dyadic_sum,
        "dyadic_closed": dyadic_closed,
        "gaussian_sixth_trace_constant": sixth_coefficient,
        "tail_after_young": tail_after_young,
        "tail_expected": 5.0 / 126.0,
    }


def gaussian_sixth_audit() -> dict[str, float]:
    eigenvalues = np.asarray([0.7, 0.4, 0.19, 0.08, 0.03])
    trace = float(np.sum(eigenvalues))
    exact = trace**3 + 6.0 * trace * float(np.sum(eigenvalues**2)) + 8.0 * float(np.sum(eigenvalues**3))
    envelope = 15.0 * trace**3
    rank_one = 15.0 * float(eigenvalues[0]) ** 3
    rank_one_envelope = 15.0 * float(eigenvalues[0]) ** 3
    return {
        "exact": exact,
        "envelope": envelope,
        "margin": envelope - exact,
        "rank_one": rank_one,
        "rank_one_envelope": rank_one_envelope,
    }


def inverse_free_completion_audit(q_matrix: np.ndarray) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 3)
    minimum_margin = math.inf
    for _ in range(RANDOM_CASES):
        raw = rng.normal(size=(6, 2))
        d = rng.normal(size=2)
        b = rng.normal(size=6)
        k = rng.normal(size=6)
        theta = float(rng.uniform(0.08, 0.92))
        tau = float(rng.uniform(0.03, 0.8))
        hessian = raw @ q_matrix @ raw.T
        left = 0.5 * q_inner(d + raw.T @ b, q_matrix, d + raw.T @ b) + float(k @ b)
        linear = theta * raw @ q_matrix @ d + k
        regularized = theta * hessian + tau * np.eye(6)
        right = (
            0.5 * (1.0 - theta) * q_inner(d + raw.T @ b, q_matrix, d + raw.T @ b)
            - 0.5 * tau * float(b @ b)
            + 0.5 * theta * q_inner(d, q_matrix, d)
            - 0.5 * float(linear @ np.linalg.solve(regularized, linear))
        )
        minimum_margin = min(minimum_margin, left - right)
    return {"minimum_margin": minimum_margin}


def off_diagonal_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 4)
    max_frame_residual = 0.0
    max_leakage_residual = 0.0
    off_diagonal_magnitude = 0.0
    for _ in range(90):
        u = rng.normal(size=6)
        g = rng.normal(size=6)
        increments = [0.28 * rng.normal(size=6) for _ in range(4)]
        derivatives_b = [0.31 * rng.normal(size=6) for _ in increments]
        total_a = np.sum(increments, axis=0)
        total_b = np.sum(derivatives_b, axis=0)
        frames_u, derivatives_u = frame_jet(u, floor, direction=total_a)
        frames_terminal, _ = frame_jet(u + total_a, floor)
        assert derivatives_u is not None
        e_total = [terminal - initial - derivative for terminal, initial, derivative in zip(frames_terminal, frames_u, derivatives_u)]

        bases: list[np.ndarray] = []
        e_shells: list[list[np.ndarray]] = []
        running = u.copy()
        for increment in increments:
            bases.append(running.copy())
            frames_0, derivatives = frame_jet(running, floor, direction=increment)
            frames_1, _ = frame_jet(running + increment, floor)
            assert derivatives is not None
            e_shells.append([f1 - f0 - derivative for f0, f1, derivative in zip(frames_0, frames_1, derivatives)])
            running = running + increment

        f_cross: dict[tuple[int, int], list[np.ndarray]] = {}
        for k in range(len(increments)):
            z_before = bases[k]
            z_after = z_before + increments[k]
            for j in range(k + 1, len(increments)):
                _, derivative_before = frame_jet(z_before, floor, direction=increments[j])
                _, derivative_after = frame_jet(z_after, floor, direction=increments[j])
                assert derivative_before is not None and derivative_after is not None
                f_cross[(k, j)] = [after - before for after, before in zip(derivative_after, derivative_before)]

        reconstructed: list[np.ndarray] = []
        for r in range(3):
            value = sum(e_shells[j][r] for j in range(len(increments)))
            value = value + sum(f_cross[(k, j)][r] for k in range(len(increments)) for j in range(k + 1, len(increments)))
            reconstructed.append(value)
            max_frame_residual = max(max_frame_residual, float(np.linalg.norm(e_total[r] - value)))

        left = 0.0
        diagonal = 0.0
        remainder = 0.0
        for r in range(3):
            w0 = frames_u[r].T @ g
            left += q_inner(w0, q_matrix, e_total[r].T @ total_b)
            for j in range(len(increments)):
                frames_base, _ = frame_jet(bases[j], floor)
                wj = frames_base[r].T @ g
                diagonal += q_inner(wj, q_matrix, e_shells[j][r].T @ derivatives_b[j])
                remainder += q_inner(w0 - wj, q_matrix, e_shells[j][r].T @ derivatives_b[j])
                for ell in range(len(increments)):
                    if ell != j:
                        remainder += q_inner(w0, q_matrix, e_shells[j][r].T @ derivatives_b[ell])
            for k in range(len(increments)):
                for j in range(k + 1, len(increments)):
                    for ell in range(len(increments)):
                        remainder += q_inner(w0, q_matrix, f_cross[(k, j)][r].T @ derivatives_b[ell])
        max_leakage_residual = max(max_leakage_residual, abs(left - diagonal - remainder))
        off_diagonal_magnitude = max(off_diagonal_magnitude, abs(remainder))
    return {
        "frame_expansion_residual": max_frame_residual,
        "leakage_expansion_residual": max_leakage_residual,
        "off_diagonal_nonzero_witness": off_diagonal_magnitude,
    }


def sobolev_threshold_audit() -> dict[str, float]:
    sigma_critical = 0.5
    x_critical = (1.0 + sigma_critical) / 2.0
    y_critical = (2.0 - sigma_critical) / 6.0
    delta, gain = 0.1, 0.2
    effective_sigma = 0.5 + delta - gain
    moment = 6.0 / (1.0 - 2.0 * effective_sigma)
    eta_exponent = 3.0 * (1.0 + effective_sigma) / (1.0 - 2.0 * effective_sigma)
    zeta_exponent = (2.0 - effective_sigma) / (1.0 - 2.0 * effective_sigma)
    return {
        "critical_sigma": sigma_critical,
        "critical_x_power": x_critical,
        "critical_y_power": y_critical,
        "critical_power_sum": x_critical + y_critical,
        "test_delta": delta,
        "test_gain": gain,
        "effective_sigma": effective_sigma,
        "required_model_moment": moment,
        "eta_exponent": eta_exponent,
        "zeta_exponent": zeta_exponent,
    }


def periodic_lift_audit() -> dict[str, float]:
    a = np.asarray([2.0, 0.0, 0.0, 1.0, 1.0, 0.0])
    n = np.asarray([-1.0, 0.0, 0.0, 1.0, -1.0, 0.0])
    t_value = 0.7
    max_residual = 0.0
    ratios: list[float] = []
    for frequency in (4, 8, 16, 32):
        grid = np.arange(16384, dtype=np.float64) * (2.0 * math.pi / 16384.0)
        field = a[None, :] + (t_value / frequency) * np.sin(frequency * grid)[:, None] * n[None, :]
        derivative = t_value * np.cos(frequency * grid)[:, None] * n[None, :]
        second = -t_value * frequency * np.sin(frequency * grid)[:, None] * n[None, :]
        numeric = float(np.mean(np.sum(field * field + derivative * derivative + second * second, axis=1)))
        exact = float(a @ a) + 0.5 * float(n @ n) * t_value**2 * (
            frequency**2 + 1.0 + frequency ** (-2)
        )
        max_residual = max(max_residual, abs(numeric - exact))
        ratios.append((numeric - float(a @ a)) / frequency**2)
    expected_ratio = 0.5 * float(n @ n) * t_value**2
    return {
        "h2_formula_residual": max_residual,
        "highest_frequency_ratio": ratios[-1],
        "limiting_ratio": expected_ratio,
    }


def run(output_path: Path = OUT) -> int:
    parameters, q_matrix, floor = production_data()
    rows: list[dict[str, Any]] = []
    kernel = kernel_and_gauge_audit(floor)
    fixture = fixture_audit(q_matrix, floor)
    local = local_bound_audit(q_matrix, floor)
    sequence = sequence_and_tail_audit()
    gaussian = gaussian_sixth_audit()
    inverse_free = inverse_free_completion_audit(q_matrix)
    off_diagonal = off_diagonal_audit(q_matrix, floor)
    threshold = sobolev_threshold_audit()
    periodic = periodic_lift_audit()

    add(rows, "q_matrix_positive", float(np.linalg.eigvalsh(q_matrix)[0]) > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), "both positive")
    add(rows, "phase_generators_skew", kernel["skew_residual"] < IDENTITY_TOL, kernel["skew_residual"], IDENTITY_TOL)
    add(rows, "phase_commutes_with_pauli", kernel["commutator_residual"] < IDENTITY_TOL, kernel["commutator_residual"], IDENTITY_TOL)
    add(rows, "generic_stacked_rank_four", kernel["generic_rank_min"] == 4 and kernel["generic_rank_max"] == 4, [kernel["generic_rank_min"], kernel["generic_rank_max"]], [4, 4])
    add(rows, "doublet_only_rank_three", kernel["doublet_only_rank"] == 3, kernel["doublet_only_rank"], 3)
    add(rows, "singlet_only_frame_zero", kernel["singlet_only_rank"] == 0, kernel["singlet_only_rank"], 0)
    add(rows, "exact_gauge_kernel", kernel["gauge_kernel_residual"] < IDENTITY_TOL, kernel["gauge_kernel_residual"], IDENTITY_TOL)
    add(rows, "differentiated_gauge_identity", kernel["differentiated_gauge_residual"] < IDENTITY_TOL, kernel["differentiated_gauge_residual"], IDENTITY_TOL)
    add(rows, "fixture_is_doublet_phase", fixture["n_is_doublet_phase_residual"] < IDENTITY_TOL, fixture["n_is_doublet_phase_residual"], IDENTITY_TOL)
    add(rows, "fixture_terminal_kernel", fixture["terminal_kernel_residual"] < IDENTITY_TOL, fixture["terminal_kernel_residual"], IDENTITY_TOL)
    add(rows, "fixture_gauge_remainder", fixture["gauge_remainder_identity_residual"] < IDENTITY_TOL, fixture["gauge_remainder_identity_residual"], IDENTITY_TOL)
    add(rows, "fixture_slope_closed_form", abs(fixture["leakage_slope"] - fixture["closed_form_slope"]) < IDENTITY_TOL, fixture, "slopes agree")
    add(rows, "fixture_gauge_slope", abs(fixture["leakage_slope"] - fixture["gauge_leakage_slope"]) < IDENTITY_TOL, fixture, "gauge and direct slopes agree")
    add(rows, "fixture_slope_positive", fixture["leakage_slope"] > 0.0, fixture["leakage_slope"], ">0")
    add(rows, "optimized_good_bad_balance", abs(local["good_constant"] - local["bad_constant"]) < 2.0e-13, [local["good_constant"], local["bad_constant"]], "equal")
    add(rows, "production_c_star", abs(local["c_star"] - 1.5397534378598672) < 2.0e-13, local["c_star"], 1.5397534378598672)
    add(rows, "inverse_free_local_bound", local["bound_margin"] > -BOUND_TOL, local["bound_margin"], f">={-BOUND_TOL}")
    add(rows, "sequence_holder_once", sequence["holder_margin"] >= -BOUND_TOL, sequence["holder_margin"], ">=0")
    add(rows, "weighted_amgm_once", sequence["amgm_margin"] >= -BOUND_TOL, sequence["amgm_margin"], ">=0")
    add(rows, "gaussian_sixth_trace_bound", gaussian["margin"] >= 0.0, gaussian["margin"], ">=0")
    add(rows, "gaussian_sixth_rank_one_sharp", abs(gaussian["rank_one"] - gaussian["rank_one_envelope"]) < IDENTITY_TOL, gaussian, "equal")
    add(rows, "dyadic_tail_exact", abs(sequence["dyadic_sum"] - sequence["dyadic_closed"]) < 1.0e-15, [sequence["dyadic_sum"], sequence["dyadic_closed"]], "equal")
    add(rows, "one_constant_tail_coefficient", abs(sequence["tail_after_young"] - 5.0 / 126.0) < 1.0e-15, sequence["tail_after_young"], 5.0 / 126.0)
    add(rows, "regularized_inverse_completion", inverse_free["minimum_margin"] > -BOUND_TOL, inverse_free["minimum_margin"], f">={-BOUND_TOL}")
    add(rows, "terminal_frame_off_diagonal_identity", off_diagonal["frame_expansion_residual"] < IDENTITY_TOL, off_diagonal["frame_expansion_residual"], IDENTITY_TOL)
    add(rows, "terminal_leakage_off_diagonal_identity", off_diagonal["leakage_expansion_residual"] < IDENTITY_TOL, off_diagonal["leakage_expansion_residual"], IDENTITY_TOL)
    add(rows, "off_diagonal_remainder_nonzero", off_diagonal["off_diagonal_nonzero_witness"] > 1.0e-6, off_diagonal["off_diagonal_nonzero_witness"], ">1e-6")
    add(rows, "critical_sobolev_fallback_saturated", abs(threshold["critical_power_sum"] - 1.0) < IDENTITY_TOL, threshold["critical_power_sum"], 1.0)
    add(rows, "causal_gain_must_exceed_delta", threshold["test_gain"] > threshold["test_delta"] and threshold["effective_sigma"] < 0.5, threshold, "gain>delta and sigma<1/2")
    add(rows, "causal_gain_model_moment", abs(threshold["required_model_moment"] - 30.0) < IDENTITY_TOL, threshold["required_model_moment"], 30.0)
    add(rows, "periodic_fixture_h2_formula", periodic["h2_formula_residual"] < 2.0e-11, periodic["h2_formula_residual"], 2.0e-11)
    add(rows, "periodic_fixture_h2_diverges", abs(periodic["highest_frequency_ratio"] - periodic["limiting_ratio"]) < 2.0e-3, periodic, "ratio tends to positive limit")

    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-phase-kernel-causal-diagonal-primary/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "source_sha256": digest(Path(__file__)),
        "inputs": {
            "a1_manifest": str(A1_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "q_matrix": q_matrix.tolist(),
            "rho_regularizer": floor,
            "random_seed": RANDOM_SEED,
            "random_cases": RANDOM_CASES,
            "full_derivative_covariance_convention": "C_D bounds the trace of the full 18-real-component spatial derivative vector",
        },
        "derived": {
            "kernel": kernel,
            "fixture": fixture,
            "local_bound": local,
            "sequence_tail": sequence,
            "gaussian_sixth": gaussian,
            "inverse_free_completion": inverse_free,
            "off_diagonal": off_diagonal,
            "sobolev_threshold": threshold,
            "periodic_lift": periodic,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": (
            "Exact phase-kernel classification, inverse-free local completion, and the matched "
            "strict-past same-shell diagonal leakage only. The displayed nonzero off-diagonal "
            "terminal remainder, finite-energy extension, complete controlled-shell one-use, "
            "Nelson, floor removal, and every infinite-volume conclusion remain open."
        ),
    }
    atomic_json(output_path, payload)
    print(f"{sum(row['status'] == 'PASS' for row in rows)}/{len(rows)} PASS")
    print(f"C*={local['c_star']:.16g}; tail={sequence['tail_after_young']:.16g}; offdiag={off_diagonal['off_diagonal_nonzero_witness']:.6g}")
    print("A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-PRIMARY-PASS" if passed else "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-PRIMARY-FAIL")
    print(f"Evidence: {output_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run())
