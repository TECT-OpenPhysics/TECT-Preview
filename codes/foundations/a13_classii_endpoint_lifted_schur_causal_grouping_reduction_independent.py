#!/usr/bin/env python3
"""Non-importing audit of the endpoint-lifted Schur/causal reduction.

This program reconstructs the six-real Pauli frames and production
coefficients without importing any A13 implementation.  It uses a distinct
random ensemble, centered finite differences, and a different Hermite order.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

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
RESULT_ID = "A13-CLASSII-ENDPOINT-LIFTED-SCHUR-CAUSAL-GROUPING-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-24-independent-endpoint-lifted-schur-causal-grouping-reduction/result.json"
)
TRANSLATION_MANIFEST = (
    REPO / "claims" / CLAIM / "classii_translation_model_reduction_manifest.json"
)

# Independent regression inputs and thresholds.
RANDOM_SEED = 72426031
RANDOM_CASES = 280
IDENTITY_TOL = 2.0e-8
BOUND_TOL = 2.0e-7
FINITE_DIFFERENCE_COARSE_STEP = 2.0e-5
FINITE_DIFFERENCE_STEP = 1.0e-5
GH_ORDER = 11


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


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})


def realify(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def generators() -> list[np.ndarray]:
    zero = 0.0j
    one = 1.0 + 0.0j
    return [
        realify(np.asarray([[zero, one, zero], [one, zero, zero], [zero, zero, zero]])),
        realify(np.asarray([[zero, -1.0j, zero], [1.0j, zero, zero], [zero, zero, zero]])),
        realify(np.asarray([[one, zero, zero], [zero, -one, zero], [zero, zero, zero]])),
    ]


def parameters_and_q() -> tuple[dict[str, Any], np.ndarray]:
    authority = json.loads(TRANSLATION_MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / authority["authority"]["a1_manifest"]["path"]
    parameters = json.loads(a1_path.read_text(encoding="utf-8"))["parameters"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    a_value = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator
    b_value = (
        float(parameters["cJK"])
        * float(parameters["alpha_X"])
        * float(parameters["beta_X"])
        / denominator
    )
    c_value = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    return parameters, np.asarray([[a_value, b_value], [b_value, c_value]])


def frames(z: np.ndarray, floor: float) -> list[np.ndarray]:
    z = np.asarray(z, dtype=np.float64)
    denominator = float(z @ z + floor)
    answer: list[np.ndarray] = []
    for symmetric in generators():
        sz = symmetric @ z
        q_value = float(z @ sz / denominator)
        answer.append(np.stack((2.0 * sz, 2.0 * (sz - q_value * z)), axis=-1))
    return answer


def directional_frames(z: np.ndarray, h: np.ndarray, floor: float) -> list[np.ndarray]:
    z = np.asarray(z, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64)
    denominator = float(z @ z + floor)
    answer: list[np.ndarray] = []
    for symmetric in generators():
        sz = symmetric @ z
        q_value = float(z @ sz / denominator)
        r_value = sz - q_value * z
        dq = 2.0 * float(r_value @ h) / denominator
        dp = 2.0 * (symmetric @ h)
        dv = dp - 2.0 * dq * z - 2.0 * q_value * h
        answer.append(np.stack((dp, dv), axis=-1))
    return answer


def current(frame_list: list[np.ndarray], derivative: np.ndarray) -> np.ndarray:
    return np.stack([frame.T @ derivative for frame in frame_list])


def q_inner(left: np.ndarray, q_matrix: np.ndarray, right: np.ndarray) -> float:
    return float(np.einsum("ai,ij,aj->", left, q_matrix, right))


def q_square(value: np.ndarray, q_matrix: np.ndarray) -> float:
    return q_inner(value, q_matrix, value)


def local_decomposition(
    z: np.ndarray,
    a_control: np.ndarray,
    y: np.ndarray,
    b_control: np.ndarray,
    q_matrix: np.ndarray,
    floor: float,
) -> dict[str, float | np.ndarray]:
    frame_0 = frames(z, floor)
    frame_1 = frames(z + a_control, floor)
    derivative = directional_frames(z, a_control, floor)
    w = current(frame_0, y)
    endpoint = current(frame_1, y + b_control)
    delta = endpoint - w
    linear_endpoint = np.stack(
        [dm.T @ y + m1.T @ b_control for dm, m1 in zip(derivative, frame_1)]
    )
    linear_affine = np.stack(
        [dm.T @ y + m0.T @ b_control for dm, m0 in zip(derivative, frame_0)]
    )
    remainder = np.stack(
        [(m1 - m0 - dm).T @ y for m0, m1, dm in zip(frame_0, frame_1, derivative)]
    )
    raw = q_inner(w, q_matrix, delta) + 0.5 * q_square(delta, q_matrix)
    return {
        "w": w,
        "delta": delta,
        "linear_endpoint": linear_endpoint,
        "linear_affine": linear_affine,
        "remainder": remainder,
        "raw": raw,
        "tangent_endpoint": q_inner(w, q_matrix, linear_endpoint),
        "tangent_affine": q_inner(w, q_matrix, linear_affine),
        "jacobi": 0.5 * q_square(delta, q_matrix),
        "curvature": q_inner(w, q_matrix, remainder),
    }


def constants(q_matrix: np.ndarray) -> dict[str, float]:
    lambda_q = float(np.linalg.eigvalsh(q_matrix)[-1])
    root = math.sqrt(1.0 + 32.0 * math.sqrt(2.0))
    theta_hash = 2.0 / (1.0 + root)
    c_hash = 3.0 * lambda_q * (1.0 + root) ** 2
    theta_star = math.sqrt(34.0) / (math.sqrt(34.0) + 4.0 * math.sqrt(2.0))
    c_star = 24.0 * lambda_q * (math.sqrt(34.0) + 4.0 * math.sqrt(2.0))
    return {
        "lambda_q": lambda_q,
        "theta_hash": theta_hash,
        "c_hash": c_hash,
        "theta_star": theta_star,
        "c_star": c_star,
    }


def independent_random_audit(q_matrix: np.ndarray) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED)
    const = constants(q_matrix)
    max_finite_difference_coarse_residual = 0.0
    max_finite_difference_residual = 0.0
    max_delta_residual = 0.0
    max_secant_residual = 0.0
    min_good_margin = math.inf
    min_bad_margin = math.inf
    min_global_margin = math.inf
    good_count = 0
    bad_count = 0
    for _ in range(RANDOM_CASES):
        floor = 10.0 ** rng.uniform(-11.0, 2.0)
        z = rng.normal(size=6) * 10.0 ** rng.uniform(-1.5, 1.5)
        a_control = rng.normal(size=6) * 10.0 ** rng.uniform(-2.5, 0.8)
        y = rng.normal(size=6)
        b_control = rng.normal(size=6) * 10.0 ** rng.uniform(-0.5, 1.7)
        dm = directional_frames(z, a_control, floor)
        scale = max(1.0, float(np.linalg.norm(z)), float(np.linalg.norm(a_control)))
        coarse_step = FINITE_DIFFERENCE_COARSE_STEP / scale
        finite_difference_coarse = [
            (plus - minus) / (2.0 * coarse_step)
            for plus, minus in zip(
                frames(z + coarse_step * a_control, floor),
                frames(z - coarse_step * a_control, floor),
            )
        ]
        max_finite_difference_coarse_residual = max(
            max_finite_difference_coarse_residual,
            max(
                float(np.linalg.norm(exact - numeric))
                for exact, numeric in zip(dm, finite_difference_coarse)
            ),
        )
        step = FINITE_DIFFERENCE_STEP / scale
        finite_difference = [
            (plus - minus) / (2.0 * step)
            for plus, minus in zip(frames(z + step * a_control, floor), frames(z - step * a_control, floor))
        ]
        max_finite_difference_residual = max(
            max_finite_difference_residual,
            max(float(np.linalg.norm(exact - numeric)) for exact, numeric in zip(dm, finite_difference)),
        )
        terms = local_decomposition(z, a_control, y, b_control, q_matrix, floor)
        max_delta_residual = max(
            max_delta_residual,
            float(
                np.linalg.norm(
                    np.asarray(terms["delta"])
                    - np.asarray(terms["linear_endpoint"])
                    - np.asarray(terms["remainder"])
                )
            ),
        )
        max_secant_residual = max(
            max_secant_residual,
            abs(
                float(terms["raw"])
                - float(terms["tangent_endpoint"])
                - float(terms["jacobi"])
                - float(terms["curvature"])
            ),
        )
        defect = float(a_control @ a_control) * float(y @ y)
        min_global_margin = min(
            min_global_margin,
            float(terms["raw"])
            - float(terms["tangent_endpoint"])
            - float(terms["jacobi"])
            + const["c_star"] * defect,
        )
        radius = math.sqrt(float(z @ z + floor))
        if np.linalg.norm(a_control) <= const["theta_hash"] * radius:
            good_count += 1
            min_good_margin = min(
                min_good_margin,
                float(terms["raw"])
                - float(terms["tangent_endpoint"])
                - float(terms["jacobi"])
                + const["c_hash"] * defect,
            )
        else:
            bad_count += 1
            min_bad_margin = min(
                min_bad_margin, float(terms["raw"]) + const["c_hash"] * defect
            )
    return {
        **const,
        "good_count": good_count,
        "bad_count": bad_count,
        "max_finite_difference_coarse_residual": max_finite_difference_coarse_residual,
        "max_finite_difference_residual": max_finite_difference_residual,
        "max_delta_residual": max_delta_residual,
        "max_secant_residual": max_secant_residual,
        "min_good_margin": min_good_margin,
        "min_bad_margin": min_bad_margin,
        "min_global_margin": min_global_margin,
    }


def rotating_fixture(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    epsilon = 0.125
    vertical = 5.5
    z = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    a_control = np.asarray([0.0, epsilon, 0.0, 0.0, 0.0, 0.0])
    y = np.asarray([0.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    b_control = vertical * np.asarray([0.0, 0.0, 0.0, 1.0, epsilon, 0.0])
    terms = local_decomposition(z, a_control, y, b_control, q_matrix, floor)
    beta_0 = 4.0 * float(q_matrix[0, 0] + 2.0 * q_matrix[0, 1] + q_matrix[1, 1])
    return {
        "raw": float(terms["raw"]),
        "affine_tangent": float(terms["tangent_affine"]),
        "expected_affine": beta_0 * epsilon * vertical,
        "endpoint_tangent": float(terms["tangent_endpoint"]),
        "jacobi": float(terms["jacobi"]),
        "curvature": float(terms["curvature"]),
    }


def coherent_fixture(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 404)
    shell_count = 6
    full_value = rng.normal(size=6)
    a_sum = np.zeros(6)
    c_sum = np.zeros(6)
    g_sum = np.zeros(6)
    control_sum = 0.0
    cross_sum = 0.0
    noise_cross_sum = 0.0
    split_max = 0.0
    initial_control = 0.0
    initial_cross = 0.0
    terminal_control = 0.0
    terminal_cross = 0.0
    for shell in range(shell_count):
        a_increment = 0.09 * rng.normal(size=6)
        c_increment = 0.14 * rng.normal(size=6)
        d_increment = 0.16 * rng.normal(size=6)
        m_0 = frames(full_value + a_sum, floor)
        m_1 = frames(full_value + a_sum + a_increment, floor)
        c_0 = current(m_0, c_sum)
        g_0 = current(m_0, g_sum)
        c_1 = current(m_1, c_sum + c_increment)
        g_plus = current(m_1, g_sum)
        raw = 0.5 * q_square(c_1 + g_plus, q_matrix) - 0.5 * q_square(c_0 + g_0, q_matrix)
        control = 0.5 * q_square(c_1, q_matrix) - 0.5 * q_square(c_0, q_matrix)
        gaussian = 0.5 * q_square(g_plus, q_matrix) - 0.5 * q_square(g_0, q_matrix)
        cross = q_inner(c_1, q_matrix, g_plus) - q_inner(c_0, q_matrix, g_0)
        split_max = max(split_max, abs(raw - control - gaussian - cross))
        if shell == 0:
            initial_control = 0.5 * q_square(c_0, q_matrix)
            initial_cross = q_inner(c_0, q_matrix, g_0)
        control_sum += control
        cross_sum += cross
        noise_current = current(m_1, d_increment)
        noise_cross_sum += q_inner(c_1, q_matrix, noise_current)
        a_sum += a_increment
        c_sum += c_increment
        g_sum += d_increment
        terminal_control = 0.5 * q_square(c_1, q_matrix)
        terminal_cross = q_inner(c_1, q_matrix, current(m_1, g_sum))
    return {
        "split_max": split_max,
        "control_telescope": control_sum - (terminal_control - initial_control),
        "cross_telescope": cross_sum - (terminal_cross - initial_cross - noise_cross_sum),
    }


def independent_hermite(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    nodes, weights = np.polynomial.hermite.hermgauss(GH_ORDER)
    nodes = math.sqrt(2.0) * nodes
    weights = weights / math.sqrt(math.pi)
    base = np.asarray([0.4, 0.1, -0.05, 0.03, -0.02, 0.01])
    c_derivative = np.asarray([0.15, -0.08, 0.02, 0.04, 0.01, -0.03])
    value_direction = np.asarray([0.2, 0.0, -0.1, 0.05, 0.03, 0.01])
    derivative_direction = np.asarray([0.0, 0.12, -0.07, 0.02, -0.05, 0.04])
    signed = 0.0
    absolute = 0.0
    for i, value_node in enumerate(nodes):
        frame_list = frames(base + value_node * value_direction, floor)
        c_current = current(frame_list, c_derivative)
        for j, derivative_node in enumerate(nodes):
            n_current = current(frame_list, derivative_node * derivative_direction)
            term = q_inner(c_current, q_matrix, n_current)
            weight = float(weights[i] * weights[j])
            signed += weight * term
            absolute += weight * abs(term)
    return {"order": GH_ORDER, "signed": signed, "absolute": absolute}


def main() -> int:
    parameters, q_matrix = parameters_and_q()
    floor = float(parameters["rho_regularizer"])
    random_audit = independent_random_audit(q_matrix)
    rotating = rotating_fixture(q_matrix, floor)
    coherent = coherent_fixture(q_matrix, floor)
    hermite = independent_hermite(q_matrix, floor)
    primary_source = (
        REPO / "codes/foundations/a13_classii_endpoint_lifted_schur_causal_grouping_reduction.py"
    ).read_text(encoding="utf-8")
    this_source = Path(__file__).read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []
    forbidden_import = "import " + "a13_classii_endpoint_lifted_schur_causal_grouping_reduction"
    add(rows, "non_importing_source", forbidden_import not in this_source, forbidden_import in this_source, False)
    add(rows, "distinct_random_seed", str(RANDOM_SEED) not in primary_source, RANDOM_SEED, "not primary seed")
    add(rows, "q_matrix_positive", float(np.linalg.eigvalsh(q_matrix)[0]) > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), "minimum > 0")
    add(rows, "finite_difference_frame_jet", random_audit["max_finite_difference_residual"] < 2.0e-7, random_audit["max_finite_difference_residual"], 2.0e-7)
    add(
        rows,
        "finite_difference_second_order_convergence",
        random_audit["max_finite_difference_residual"]
        < 0.30 * random_audit["max_finite_difference_coarse_residual"],
        random_audit["max_finite_difference_residual"]
        / random_audit["max_finite_difference_coarse_residual"],
        "<0.30 when the centered-difference step is halved",
    )
    add(rows, "delta_identity", random_audit["max_delta_residual"] < IDENTITY_TOL, random_audit["max_delta_residual"], IDENTITY_TOL)
    add(rows, "secant_identity", random_audit["max_secant_residual"] < IDENTITY_TOL, random_audit["max_secant_residual"], IDENTITY_TOL)
    add(rows, "good_cases_present", random_audit["good_count"] > 0, random_audit["good_count"], ">0")
    add(rows, "bad_cases_present", random_audit["bad_count"] > 0, random_audit["bad_count"], ">0")
    add(rows, "good_bound", random_audit["min_good_margin"] > -BOUND_TOL, random_audit["min_good_margin"], f">={-BOUND_TOL}")
    add(rows, "bad_bound", random_audit["min_bad_margin"] > -BOUND_TOL, random_audit["min_bad_margin"], f">={-BOUND_TOL}")
    add(rows, "global_bound", random_audit["min_global_margin"] > -BOUND_TOL, random_audit["min_global_margin"], f">={-BOUND_TOL}")
    add(rows, "rotating_raw_zero", abs(rotating["raw"]) < IDENTITY_TOL, rotating["raw"], 0.0)
    add(rows, "rotating_affine_formula", abs(rotating["affine_tangent"] - rotating["expected_affine"]) < IDENTITY_TOL, rotating["affine_tangent"], rotating["expected_affine"])
    add(rows, "rotating_endpoint_repair", abs(rotating["endpoint_tangent"]) + abs(rotating["jacobi"]) + abs(rotating["curvature"]) < IDENTITY_TOL, rotating, "endpoint pieces zero")
    add(rows, "coherent_split", coherent["split_max"] < IDENTITY_TOL, coherent["split_max"], IDENTITY_TOL)
    add(rows, "control_telescope", abs(coherent["control_telescope"]) < IDENTITY_TOL, coherent["control_telescope"], 0.0)
    add(rows, "cross_noise_telescope", abs(coherent["cross_telescope"]) < IDENTITY_TOL, coherent["cross_telescope"], 0.0)
    add(rows, "independent_fresh_noise_center", abs(hermite["signed"]) < IDENTITY_TOL and hermite["absolute"] > 1.0e-5, hermite, "signed zero; absolute nonzero")
    add(rows, "reported_constant_order", 0.0 < random_audit["c_hash"] < random_audit["c_star"] < 2.0, {"c_hash": random_audit["c_hash"], "c_star": random_audit["c_star"]}, "0<C#<C*<2")
    passed = all(row["pass"] for row in rows)
    payload = {
        "schema": "tect/a13-endpoint-lifted-schur-causal-independent/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {
            "random_seed": RANDOM_SEED,
            "random_cases": RANDOM_CASES,
            "finite_difference_coarse_step": FINITE_DIFFERENCE_COARSE_STEP,
            "finite_difference_step": FINITE_DIFFERENCE_STEP,
            "hermite_order": GH_ORDER,
        },
        "computed": {
            "random": random_audit,
            "rotating_kernel": rotating,
            "coherent_causal": coherent,
            "fresh_noise_cross": hermite,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "imports_primary": False,
        "honesty_boundary": (
            "Independent finite-dimensional and causal audits only. The adapted "
            "Gaussian-rooted transported-current lower bound remains unproved."
        ),
    }
    atomic_json(OUT, payload)
    if not passed:
        for row in rows:
            if not row["pass"]:
                print(f"FAIL {row['name']}: {row['actual']} expected {row['expected']}")
        return 1
    print(
        f"{RESULT_ID}-INDEPENDENT-PASS: {len(rows)}/{len(rows)}; "
        f"C#={random_audit['c_hash']:.12g}; C*={random_audit['c_star']:.12g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
