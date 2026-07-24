#!/usr/bin/env python3
"""Non-importing independent audit for the A13 R-071 continuation.

This script does not import the primary R-071 implementation or the R-069
endpoint helper.  It reconstructs the production frames and their directional
derivatives from the pinned upstream coefficient sources.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import json
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

from codes.foundations import a6_classii_uv_power_counting as uv
from codes.foundations import a13_classii_npc_cone_martingale_injection_reduction as npc
from codes.foundations import a13_classii_translation_model_reduction as translation

CLAIM_DIR = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
OUTPUT = CLAIM_DIR / "runs/2026-07-24-independent-one-form-sobolev-linear-closure/result.json"
DELTA = Fraction(1, 10)
RANDOM_SEED = 710724062
TOL = 5.0e-10


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


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def upstream() -> tuple[dict[str, Any], np.ndarray, list[np.ndarray]]:
    parameters = npc.production_parameters()
    a_value, b_value, c_value = translation.coefficients(parameters)
    q_matrix = np.asarray(
        [[a_value, b_value], [b_value, c_value]], dtype=np.float64
    )
    generators = [translation.realify(item) for item in uv.generators()]
    return parameters, q_matrix, generators


def frames_and_jets(
    value: np.ndarray,
    floor: float,
    generators: list[np.ndarray],
    direction: np.ndarray | None = None,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    denominator = float(value @ value + floor)
    frames: list[np.ndarray] = []
    jets: list[np.ndarray] = []
    for symmetric in generators:
        sz = symmetric @ value
        mass = float(value @ sz)
        q_value = mass / denominator
        v_value = 2.0 * (sz - q_value * value)
        frames.append(np.stack((2.0 * sz, v_value), axis=-1))
        if direction is not None:
            d_denominator = 2.0 * float(value @ direction)
            d_mass = 2.0 * float(direction @ sz)
            dq = (d_mass * denominator - mass * d_denominator) / denominator**2
            dp = 2.0 * symmetric @ direction
            dv = dp - 2.0 * dq * value - 2.0 * q_value * direction
            jets.append(np.stack((dp, dv), axis=-1))
    return frames, jets


def currents(frames: list[np.ndarray], derivative: np.ndarray) -> np.ndarray:
    return np.stack([frame.T @ derivative for frame in frames], axis=0)


def q_inner(left: np.ndarray, q_matrix: np.ndarray, right: np.ndarray) -> float:
    return float(np.einsum("ai,ij,aj->", left, q_matrix, right))


def current_split(
    value: np.ndarray,
    derivative: np.ndarray,
    floor: float,
    q_matrix: np.ndarray,
    generators: list[np.ndarray],
) -> dict[str, np.ndarray]:
    q11, q12, q22 = float(q_matrix[0, 0]), float(q_matrix[0, 1]), float(q_matrix[1, 1])
    denominator = float(value @ value + floor)
    identity = np.eye(6)
    full = np.zeros((6, 6), dtype=np.float64)
    polynomial = np.zeros_like(full)
    rational = np.zeros_like(full)
    non_pp = np.zeros_like(full)
    cartan = np.zeros_like(full)
    for symmetric in generators:
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
        non_pp += q12 * (p_current * kv + v_current * kp) + q22 * v_current * kv
        polynomial += (q11 + 2.0 * q12 + q22) * p_current * kp
        rational += (q12 + q22) * (p_current * h_matrix - q_value * rho_current * kp)
        rational -= q22 * q_value * rho_current * h_matrix
        d_rho = 2.0 * value
        d_mass = p
        curvature = (np.outer(d_rho, d_mass) - np.outer(d_mass, d_rho)) / denominator
        cartan += (q12 * p_current + q22 * v_current) * curvature
    return {
        "full": full,
        "polynomial": polynomial,
        "rational": rational,
        "non_pp": non_pp,
        "cartan": cartan,
    }


def independent_algebra(
    floor: float, q_matrix: np.ndarray, generators: list[np.ndarray]
) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED)
    full_error = 0.0
    non_pp_error = 0.0
    q11 = float(q_matrix[0, 0])
    for _ in range(97):
        value = rng.normal(size=6) * 10.0 ** rng.uniform(-1.0, 1.0)
        derivative = rng.normal(size=6)
        split = current_split(value, derivative, floor, q_matrix, generators)
        pp = np.zeros((6, 6), dtype=np.float64)
        for symmetric in generators:
            p = 2.0 * symmetric @ value
            pp += q11 * float(p @ derivative) * (2.0 * symmetric)
        full_error = max(
            full_error,
            float(np.linalg.norm(split["full"] - split["polynomial"] - split["rational"])),
        )
        non_pp_error = max(
            non_pp_error,
            float(np.linalg.norm(split["non_pp"] - split["polynomial"] + pp - split["rational"])),
        )
    return {"full_error": full_error, "non_pp_error": non_pp_error}


def independent_kernel(
    floor: float, q_matrix: np.ndarray, generators: list[np.ndarray]
) -> dict[str, float]:
    z = np.asarray([-1.0, -1.0, 0.0, 0.0, -1.0, 0.0])
    endpoint_value = np.asarray([1.0, -1.0, 0.0, 1.0, 0.0, 0.0])
    a_control = endpoint_value - z
    y = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    kernel = np.asarray([-1.0, 0.0, 0.0, 1.0, -1.0, 0.0])
    frames_0, jets = frames_and_jets(z, floor, generators, a_control)
    frames_1, _ = frames_and_jets(endpoint_value, floor, generators)
    w = currents(frames_0, y)
    endpoint_kernel = currents(frames_1, kernel)
    remainders = [frame_1 - frame_0 - jet for frame_0, frame_1, jet in zip(frames_0, frames_1, jets)]
    leakage = np.zeros(6, dtype=np.float64)
    linear = np.zeros(6, dtype=np.float64)
    for remainder, jet, w_value in zip(remainders, jets, w):
        leakage += remainder @ q_matrix @ w_value
        linear += jet @ q_matrix @ w_value
    slope = float(kernel @ leakage)
    linear_slope = float(kernel @ linear)

    def residual(parameter: float) -> tuple[float, float]:
        b_control = parameter * kernel
        delta = currents(frames_1, y + b_control) - w
        remainder_current = np.stack(
            [remainder.T @ (y + b_control) for remainder in remainders], axis=0
        )
        return q_inner(w, q_matrix, remainder_current) + 0.5 * q_inner(delta, q_matrix, delta), 0.5 * q_inner(delta, q_matrix, delta)

    left, square_left = residual(-80.0)
    center, square_center = residual(0.0)
    right, square_right = residual(80.0)
    finite_slope = (right - left) / 160.0
    return {
        "kernel_norm": float(np.linalg.norm(endpoint_kernel)),
        "slope": slope,
        "linear_slope": linear_slope,
        "combined_slope": slope + linear_slope,
        "finite_slope": finite_slope,
        "affine_error": max(abs(right - center - 80.0 * slope), abs(center - left - 80.0 * slope)),
        "square_spread": max(square_left, square_center, square_right) - min(square_left, square_center, square_right),
        "negative_sample": left,
    }


def run(output: Path = OUTPUT) -> int:
    parameters, q_matrix, generators = upstream()
    floor = float(parameters["rho_regularizer"])
    q11, q12, q22 = float(q_matrix[0, 0]), float(q_matrix[0, 1]), float(q_matrix[1, 1])
    algebra = independent_algebra(floor, q_matrix, generators)
    axis_value = np.zeros(6)
    axis_value[0] = 1.0
    axis_derivative = np.zeros(6)
    axis_derivative[1] = 1.0
    axis = current_split(axis_value, axis_derivative, floor, q_matrix, generators)
    kernel = independent_kernel(floor, q_matrix, generators)
    floor_scan = [independent_kernel(test_floor, q_matrix, generators) for test_floor in (floor, 1.0e-6, 1.0e-2, 1.0, 100.0)]

    s_value = Fraction(3, 2) + DELTA
    theta = s_value / 2
    symmetric_eta = 3 * s_value / (2 * (2 - s_value))
    symmetric_moment = 3 / (2 - s_value)
    cartan_eta = 3 * (5 + 2 * DELTA) / (2 * (1 - 2 * DELTA))
    cartan_moment = 9 / (1 - 2 * DELTA)
    rows: list[dict[str, Any]] = []

    add(rows, "independent_q_positive", float(np.linalg.det(q_matrix)) > 0.0 and q11 > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), "positive definite")
    add(rows, "independent_non_pp_core", abs(2.0 * q12 + q22) > 1.0e-12, 2.0 * q12 + q22, "nonzero")
    add(rows, "independent_full_split", algebra["full_error"] < TOL, algebra["full_error"], TOL)
    add(rows, "independent_non_pp_split", algebra["non_pp_error"] < TOL, algebra["non_pp_error"], TOL)
    add(rows, "independent_non_pp_axis", abs(float(axis["non_pp"][0, 1])) > 1.0e-12, float(axis["non_pp"][0, 1]), "nonzero")
    add(rows, "independent_full_axis", abs(float(axis["full"][0, 1])) > 1.0e-12, float(axis["full"][0, 1]), "nonzero")
    add(rows, "independent_cartan_axis", abs(float(axis["cartan"][0, 1])) > 1.0e-12, float(axis["cartan"][0, 1]), "nonzero")
    add(rows, "independent_raw_growth", 1 - 2 * DELTA == Fraction(4, 5), str(1 - 2 * DELTA), "4/5")
    add(rows, "independent_symmetric_eta", symmetric_eta == Fraction(6, 1), str(symmetric_eta), "6")
    add(rows, "independent_symmetric_moment", symmetric_moment == Fraction(15, 2), str(symmetric_moment), "15/2")
    add(rows, "independent_cartan_eta", cartan_eta == Fraction(39, 4), str(cartan_eta), "39/4")
    add(rows, "independent_cartan_moment", cartan_moment == Fraction(45, 4), str(cartan_moment), "45/4")
    add(rows, "independent_interpolation_theta", theta == Fraction(4, 5), str(theta), "4/5")
    add(rows, "independent_kernel", kernel["kernel_norm"] < TOL, kernel["kernel_norm"], TOL)
    add(rows, "independent_leakage_positive", kernel["slope"] > 0.0, kernel["slope"], "> 0")
    add(rows, "independent_affine_identity", kernel["affine_error"] < TOL, kernel["affine_error"], TOL)
    add(rows, "independent_square_kernel_blind", kernel["square_spread"] < TOL, kernel["square_spread"], TOL)
    add(rows, "independent_unbounded_sample", kernel["negative_sample"] < 0.0, kernel["negative_sample"], "< 0")
    add(rows, "independent_floor_scan_kernel", max(item["kernel_norm"] for item in floor_scan) < TOL, max(item["kernel_norm"] for item in floor_scan), TOL)
    add(rows, "independent_floor_scan_positive", min(item["slope"] for item in floor_scan) > 0.0, min(item["slope"] for item in floor_scan), "> 0")
    add(rows, "independent_linear_does_not_cancel", kernel["combined_slope"] > 0.0, kernel["combined_slope"], "> 0")

    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-one-form-sobolev-linear-independent/1.0",
        "result_id": "A13-CLASSII-ONE-FORM-SOBOLEV-LINEAR-CLOSURE-AND-KERNEL-LEAKAGE",
        "claim": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {"rho_regularizer": floor, "q_matrix": q_matrix.tolist(), "delta": str(DELTA)},
        "derived": {
            "algebra": algebra,
            "axis": {key: float(value[0, 1]) for key, value in axis.items()},
            "kernel": kernel,
            "floor_scan": floor_scan,
            "exponents": {
                "s": str(s_value),
                "theta": str(theta),
                "symmetric_eta": str(symmetric_eta),
                "symmetric_moment": str(symmetric_moment),
                "cartan_eta": str(cartan_eta),
                "cartan_moment": str(cartan_moment),
            },
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": (
            "Independent finite-dimensional reconstruction and exponent audit only; "
            "the analytic one-form Sobolev lift is in the proof note, and the integrated "
            "kernel-leakage estimate and all downstream closure steps remain open."
        ),
    }
    atomic_json(output, payload)
    print(f"{sum(row['status'] == 'PASS' for row in rows)}/{len(rows)} PASS")
    print("A13-CLASSII-ONE-FORM-SOBOLEV-LINEAR-INDEPENDENT-PASS" if passed else "A13-CLASSII-ONE-FORM-SOBOLEV-LINEAR-INDEPENDENT-FAIL")
    print(f"Independent leakage slope: {kernel['slope']:.15g}")
    print(f"Evidence: {output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run())
