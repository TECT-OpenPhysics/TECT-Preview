#!/usr/bin/env python3
"""Primary audit for the A13 one-form Sobolev linear closure (R-071).

The analytic proof is in the paired note.  This executable recomputes the
production frame algebra, the Sobolev/Young exponents, the low--high
principal symbols, and the terminal-frame kernel-leakage fixture.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

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
sys.path.insert(0, str(REPO))

from codes.foundations import (
    a13_classii_endpoint_lifted_schur_causal_grouping_reduction as endpoint,
)

CLAIM_DIR = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
OUTPUT = CLAIM_DIR / "runs/2026-07-24-primary-one-form-sobolev-linear-closure/result.json"

# Proof/test inputs.  Derived production coefficients are never pasted here.
DELTA = Fraction(1, 10)
RANDOM_SEED = 260724071
IDENTITY_TOL = 2.0e-10
NONZERO_TOL = 1.0e-12

# Clearly labelled exact proof-oracles at delta=1/10.
ORACLE_S = Fraction(8, 5)
ORACLE_THETA = Fraction(4, 5)
ORACLE_SYM_ETA = Fraction(6, 1)
ORACLE_SYM_MOMENT = Fraction(15, 2)
ORACLE_CARTAN_ETA = Fraction(39, 4)
ORACLE_CARTAN_MOMENT = Fraction(45, 4)


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


def add(
    rows: list[dict[str, Any]],
    name: str,
    passed: bool,
    actual: Any,
    expected: Any,
) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def frame_current_parts(
    value: np.ndarray,
    derivative: np.ndarray,
    q_matrix: np.ndarray,
    floor: float,
) -> dict[str, np.ndarray]:
    """Compute (2.1)--(2.5) directly from the production generators."""
    full = np.zeros((6, 6), dtype=np.float64)
    non_pp = np.zeros_like(full)
    polynomial = np.zeros_like(full)
    rational = np.zeros_like(full)
    cartan = np.zeros_like(full)
    q11, q12, q22 = float(q_matrix[0, 0]), float(q_matrix[0, 1]), float(q_matrix[1, 1])
    rho = float(value @ value)
    denominator = rho + floor
    identity = np.eye(6)
    for symmetric in endpoint.real_generators():
        p = 2.0 * symmetric @ value
        mass = float(value @ symmetric @ value)
        q_value = mass / denominator
        v = p - 2.0 * q_value * value
        p_current = float(p @ derivative)
        rho_current = 2.0 * float(value @ derivative)
        v_current = p_current - q_value * rho_current
        kp = 2.0 * symmetric
        kv = 2.0 * (symmetric - q_value * identity)
        kv -= (np.outer(v, value) + np.outer(value, v)) / denominator
        h_matrix = kv - kp

        full += q11 * p_current * kp
        full += q12 * (p_current * kv + v_current * kp)
        full += q22 * v_current * kv
        non_pp += q12 * (p_current * kv + v_current * kp)
        non_pp += q22 * v_current * kv
        polynomial += (q11 + 2.0 * q12 + q22) * p_current * kp
        rational += (q12 + q22) * (p_current * h_matrix - q_value * rho_current * kp)
        rational -= q22 * q_value * rho_current * h_matrix

        d_rho = 2.0 * value
        d_mass = p
        d_omega = (np.outer(d_rho, d_mass) - np.outer(d_mass, d_rho)) / denominator
        cartan += (q12 * p_current + q22 * v_current) * d_omega
    return {
        "full": full,
        "non_pp": non_pp,
        "polynomial": polynomial,
        "rational": rational,
        "cartan": cartan,
    }


def algebra_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED)
    max_full_error = 0.0
    max_non_pp_error = 0.0
    for _ in range(128):
        value = rng.normal(size=6) * 10.0 ** rng.uniform(-1.5, 1.5)
        derivative = rng.normal(size=6)
        parts = frame_current_parts(value, derivative, q_matrix, floor)
        q11 = float(q_matrix[0, 0])
        q12 = float(q_matrix[0, 1])
        q22 = float(q_matrix[1, 1])
        pp = np.zeros((6, 6), dtype=np.float64)
        for symmetric in endpoint.real_generators():
            p = 2.0 * symmetric @ value
            pp += q11 * float(p @ derivative) * (2.0 * symmetric)
        max_full_error = max(
            max_full_error,
            float(np.linalg.norm(parts["full"] - parts["polynomial"] - parts["rational"])),
        )
        max_non_pp_error = max(
            max_non_pp_error,
            float(
                np.linalg.norm(
                    parts["non_pp"]
                    - (parts["polynomial"] - pp)
                    - parts["rational"]
                )
            ),
        )
    return {
        "max_full_split_error": max_full_error,
        "max_non_pp_split_error": max_non_pp_error,
    }


def exponent_audit() -> dict[str, Fraction]:
    s_value = Fraction(3, 2) + DELTA
    theta = s_value / 2
    symmetric_eta = 3 * s_value / (2 * (2 - s_value))
    symmetric_moment = 3 / (2 - s_value)
    cartan_eta = 3 * (5 + 2 * DELTA) / (2 * (1 - 2 * DELTA))
    cartan_moment = 9 / (1 - 2 * DELTA)
    return {
        "s": s_value,
        "theta": theta,
        "symmetric_eta": symmetric_eta,
        "symmetric_moment": symmetric_moment,
        "cartan_eta": cartan_eta,
        "cartan_moment": cartan_moment,
        "raw_false_growth": 1 - 2 * DELTA,
        "current_order": Fraction(1, 2) + DELTA,
        "divergence_order": Fraction(3, 2) + DELTA,
    }


def low_high_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    value = np.zeros(6, dtype=np.float64)
    value[0] = 1.0
    derivative = np.zeros(6, dtype=np.float64)
    derivative[1] = 1.0
    parts = frame_current_parts(value, derivative, q_matrix, floor)
    return {
        "non_pp_entry_12": float(parts["non_pp"][0, 1]),
        "full_entry_12": float(parts["full"][0, 1]),
        "cartan_entry_12": float(parts["cartan"][0, 1]),
    }


def kernel_leakage_audit(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    z = np.asarray([-1.0, -1.0, 0.0, 0.0, -1.0, 0.0])
    endpoint_value = np.asarray([1.0, -1.0, 0.0, 1.0, 0.0, 0.0])
    a_control = endpoint_value - z
    y = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    kernel = np.asarray([-1.0, 0.0, 0.0, 1.0, -1.0, 0.0])
    frames_0, derivatives, _ = endpoint.frame_jet(
        z, floor, direction=a_control
    )
    frames_1, _, _ = endpoint.frame_jet(endpoint_value, floor)
    assert derivatives is not None
    w = endpoint.current_vectors(frames_0, y)
    terminal_kernel_current = endpoint.current_vectors(frames_1, kernel)
    leakage_vector = np.zeros(6, dtype=np.float64)
    remainders: list[np.ndarray] = []
    for frame_0, frame_1, derivative, w_value in zip(
        frames_0, frames_1, derivatives, w
    ):
        remainder = frame_1 - frame_0 - derivative
        remainders.append(remainder)
        leakage_vector += remainder @ q_matrix @ w_value
    slope = float(kernel @ leakage_vector)

    def shifted_piece(parameter: float) -> tuple[float, float, float]:
        b_control = parameter * kernel
        delta_current = endpoint.current_vectors(frames_1, y + b_control) - w
        e_current = np.stack(
            [remainder.T @ (y + b_control) for remainder in remainders], axis=0
        )
        nonlinear = endpoint.q_inner(w, q_matrix, e_current)
        square = 0.5 * endpoint.q_square(delta_current, q_matrix)
        return nonlinear + square, nonlinear, square

    left, _, square_left = shifted_piece(-100.0)
    center, _, square_center = shifted_piece(0.0)
    right, _, square_right = shifted_piece(100.0)
    finite_difference_slope = (right - left) / 200.0
    affine_residual = max(
        abs((right - center) - 100.0 * slope),
        abs((center - left) - 100.0 * slope),
    )
    return {
        "kernel_current_norm": float(np.linalg.norm(terminal_kernel_current)),
        "leakage_slope": slope,
        "finite_difference_slope": finite_difference_slope,
        "affine_residual": affine_residual,
        "shifted_piece_minus_100": left,
        "shifted_piece_zero": center,
        "shifted_piece_plus_100": right,
        "square_spread": max(square_left, square_center, square_right)
        - min(square_left, square_center, square_right),
    }


def run(output: Path = OUTPUT) -> int:
    parameters, q_matrix, floor = endpoint.production_data()
    eigenvalues = np.linalg.eigvalsh(q_matrix)
    q11 = float(q_matrix[0, 0])
    q12 = float(q_matrix[0, 1])
    q22 = float(q_matrix[1, 1])
    non_pp_polynomial = 2.0 * q12 + q22
    full_polynomial = q11 + non_pp_polynomial
    algebra = algebra_audit(q_matrix, floor)
    exponents = exponent_audit()
    low_high = low_high_audit(q_matrix, floor)
    leakage = kernel_leakage_audit(q_matrix, floor)
    rows: list[dict[str, Any]] = []

    add(rows, "production_q_positive", float(eigenvalues[0]) > 0.0, eigenvalues.tolist(), "> 0")
    add(rows, "non_pp_polynomial_core_nonzero", abs(non_pp_polynomial) > NONZERO_TOL, non_pp_polynomial, "nonzero")
    add(rows, "full_polynomial_core_is_sum", abs(full_polynomial - (q11 + 2.0 * q12 + q22)) < IDENTITY_TOL, full_polynomial, "q11+2q12+q22")
    add(rows, "full_current_exact_split", algebra["max_full_split_error"] < IDENTITY_TOL, algebra["max_full_split_error"], IDENTITY_TOL)
    add(rows, "non_pp_current_exact_split", algebra["max_non_pp_split_error"] < IDENTITY_TOL, algebra["max_non_pp_split_error"], IDENTITY_TOL)
    add(rows, "non_pp_low_high_symbol_nonzero", abs(low_high["non_pp_entry_12"]) > NONZERO_TOL, low_high["non_pp_entry_12"], "nonzero")
    add(rows, "full_low_high_symbol_nonzero", abs(low_high["full_entry_12"]) > NONZERO_TOL, low_high["full_entry_12"], "nonzero")
    add(rows, "cartan_low_high_symbol_nonzero", abs(low_high["cartan_entry_12"]) > NONZERO_TOL, low_high["cartan_entry_12"], "nonzero")
    add(rows, "raw_h_minus_one_growth_positive", exponents["raw_false_growth"] > 0, str(exponents["raw_false_growth"]), "> 0")
    add(rows, "corrected_s_oracle", exponents["s"] == ORACLE_S, str(exponents["s"]), str(ORACLE_S))
    add(rows, "corrected_theta_oracle", exponents["theta"] == ORACLE_THETA, str(exponents["theta"]), str(ORACLE_THETA))
    add(rows, "symmetric_eta_oracle", exponents["symmetric_eta"] == ORACLE_SYM_ETA, str(exponents["symmetric_eta"]), str(ORACLE_SYM_ETA))
    add(rows, "symmetric_moment_oracle", exponents["symmetric_moment"] == ORACLE_SYM_MOMENT, str(exponents["symmetric_moment"]), str(ORACLE_SYM_MOMENT))
    add(rows, "cartan_eta_oracle", exponents["cartan_eta"] == ORACLE_CARTAN_ETA, str(exponents["cartan_eta"]), str(ORACLE_CARTAN_ETA))
    add(rows, "cartan_moment_oracle", exponents["cartan_moment"] == ORACLE_CARTAN_MOMENT, str(exponents["cartan_moment"]), str(ORACLE_CARTAN_MOMENT))
    add(rows, "current_to_divergence_order", exponents["divergence_order"] == exponents["current_order"] + 1, str(exponents["divergence_order"]), "current order + 1")
    add(rows, "terminal_frame_kernel", leakage["kernel_current_norm"] < IDENTITY_TOL, leakage["kernel_current_norm"], IDENTITY_TOL)
    add(rows, "kernel_leakage_positive", leakage["leakage_slope"] > NONZERO_TOL, leakage["leakage_slope"], "> 0")
    add(rows, "kernel_residual_affine", leakage["affine_residual"] < IDENTITY_TOL, leakage["affine_residual"], IDENTITY_TOL)
    add(rows, "terminal_square_blind_to_kernel", leakage["square_spread"] < IDENTITY_TOL, leakage["square_spread"], IDENTITY_TOL)
    add(rows, "kernel_route_unbounded_sample", leakage["shifted_piece_minus_100"] < 0.0, leakage["shifted_piece_minus_100"], "< 0")

    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-one-form-sobolev-linear-primary/1.0",
        "result_id": "A13-CLASSII-ONE-FORM-SOBOLEV-LINEAR-CLOSURE-AND-KERNEL-LEAKAGE",
        "claim": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {
            "rho_regularizer": float(parameters["rho_regularizer"]),
            "q_matrix": q_matrix.tolist(),
            "delta": str(DELTA),
        },
        "derived": {
            "non_pp_polynomial_core": non_pp_polynomial,
            "full_polynomial_core": full_polynomial,
            "algebra": algebra,
            "exponents": {key: str(value) for key, value in exponents.items()},
            "low_high": low_high,
            "kernel_leakage": leakage,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": (
            "The executable checks exact finite-dimensional algebra, derived exponents, "
            "and falsifier fixtures.  The continuum one-form lift is the analytic theorem "
            "in the paired note.  The integrated nonlinear kernel-leakage estimate, "
            "finite-energy extension, one-use, and Nelson theorem remain open."
        ),
    }
    atomic_json(output, payload)
    print(f"{sum(row['status'] == 'PASS' for row in rows)}/{len(rows)} PASS")
    print("A13-CLASSII-ONE-FORM-SOBOLEV-LINEAR-PRIMARY-PASS" if passed else "A13-CLASSII-ONE-FORM-SOBOLEV-LINEAR-PRIMARY-FAIL")
    print(f"Non-pp polynomial core: {non_pp_polynomial:.15g}")
    print(f"Kernel leakage slope: {leakage['leakage_slope']:.15g}")
    print(f"Evidence: {output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run())
