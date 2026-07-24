#!/usr/bin/env python3
"""Non-importing independent audit for R-079.

This implementation uses a two-component matrix frame, a four-root tree,
Gauss--Hermite quadrature, and separately derived rational ledgers.  It never
imports the primary executable.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-25-independent-full-safe-packet-frame-current-doob/result.json"
)
TOL = 4.0e-10


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="independent-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected}
    )


def conditional(values: np.ndarray, roots: np.ndarray, depth: int) -> np.ndarray:
    answer = np.zeros_like(values, dtype=float)
    groups: dict[tuple[int, ...], list[int]] = {}
    for index, root in enumerate(roots.astype(int)):
        groups.setdefault(tuple(root[:depth]), []).append(index)
    for indices in groups.values():
        answer[indices] = np.mean(values[indices], axis=0)
    return answer


def matrix_frame(z: np.ndarray) -> np.ndarray:
    matrices = np.zeros((len(z), 2, 2), dtype=float)
    matrices[:, 0, 0] = 1.16 + 0.06 * np.tanh(z[:, 0])
    matrices[:, 0, 1] = 0.025 * np.sin(z[:, 1])
    matrices[:, 1, 0] = -0.018 * np.sin(z[:, 0])
    matrices[:, 1, 1] = 1.21 + 0.045 * np.tanh(z[:, 1])
    return matrices


def matrix_fixture() -> dict[str, Any]:
    roots = np.asarray(
        [(a, b, c, d) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1) for d in (-1, 1)],
        dtype=float,
    )
    a, b, c, d = roots.T
    field = np.column_stack((0.17 * a - 0.09 * b * c, -0.13 * b + 0.08 * a * d))
    gradient = np.zeros((len(roots), 2, 2), dtype=float)
    gradient[:, :, 0] = np.column_stack((0.22 * b + 0.05 * d, -0.19 * a + 0.07 * c))
    gradient[:, :, 1] = np.column_stack((-0.16 * c + 0.04 * a * b, 0.14 * d - 0.06 * b * c))

    value_controls = [np.tile(np.asarray([0.018, -0.014]), (len(roots), 1))]
    gradient_controls = [np.tile(np.asarray([[0.01, -0.008], [0.006, 0.009]]), (len(roots), 1, 1))]
    value_steps = (
        np.tile(np.asarray([0.026, -0.019]), (len(roots), 1)),
        np.column_stack((0.05 * a, -0.035 * a)),
        np.column_stack((-0.04 * a * b, 0.03 * b)),
        np.column_stack((0.028 * c, -0.022 * a * c)),
    )
    gradient_steps = (
        np.tile(np.asarray([[0.012, -0.009], [0.007, 0.011]]), (len(roots), 1, 1)),
        np.einsum("n,ab->nab", a, np.asarray([[0.02, -0.01], [0.012, 0.008]])),
        np.einsum("n,ab->nab", a * b, np.asarray([[-0.012, 0.009], [0.007, -0.011]])),
        np.einsum("n,ab->nab", c, np.asarray([[0.008, 0.006], [-0.009, 0.005]])),
    )
    for value_step, gradient_step in zip(value_steps, gradient_steps):
        value_controls.append(value_controls[-1] + value_step)
        gradient_controls.append(gradient_controls[-1] + gradient_step)

    predictability_error = 0.0
    past_increment_error = 0.0
    for shell in range(1, 5):
        predictability_error = max(
            predictability_error,
            float(np.max(np.abs(conditional(value_controls[shell], roots, shell - 1) - value_controls[shell]))),
            float(np.max(np.abs(conditional(gradient_controls[shell], roots, shell - 1) - gradient_controls[shell]))),
        )
        value_step = value_controls[shell] - value_controls[shell - 1]
        gradient_step = gradient_controls[shell] - gradient_controls[shell - 1]
        for depth in range(shell, 5):
            past_increment_error = max(
                past_increment_error,
                float(np.max(np.abs(conditional(value_step, roots, depth) - conditional(value_step, roots, depth - 1)))),
                float(np.max(np.abs(conditional(gradient_step, roots, depth) - conditional(gradient_step, roots, depth - 1)))),
            )

    q = np.asarray([[1.3, 0.17], [0.17, 0.92]])
    eigenvalues, eigenvectors = np.linalg.eigh(q)
    q_sqrt = eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
    currents: list[np.ndarray] = []
    coefficients: list[np.ndarray] = []
    paid: list[np.ndarray] = []
    frames: list[np.ndarray] = []
    for value_control, gradient_control in zip(value_controls, gradient_controls):
        frame = matrix_frame(field + value_control)
        frames.append(frame)
        current = np.zeros((len(roots), 2, 2), dtype=float)
        for direction in range(2):
            vectors = gradient[:, :, direction] + gradient_control[:, :, direction]
            current[:, :, direction] = np.einsum("ab,nbc,nc->na", q_sqrt, np.transpose(frame, (0, 2, 1)), vectors)
        currents.append(current.reshape(len(roots), -1))
        coefficients.append(np.einsum("nab,bc,ndc->nad", frame, q, frame))
        paid.append(0.025 * np.sum(value_control**2, axis=1) + 0.012 * np.sum(gradient_control**2, axis=(1, 2)))

    metric_convention_error = 0.0
    covariance_convention_error = 0.0
    gamma_test = np.asarray([[0.71, -0.09], [-0.09, 0.54]])
    gamma_factor = np.linalg.cholesky(gamma_test)
    for frame, gradient_control, current, coefficient in zip(
        frames, gradient_controls, currents, coefficients
    ):
        current_shaped = current.reshape(len(roots), 2, 2)
        for direction in range(2):
            vectors = gradient[:, :, direction] + gradient_control[:, :, direction]
            current_square = np.sum(current_shaped[:, :, direction] ** 2, axis=1)
            coefficient_square = np.einsum("ni,nij,nj->n", vectors, coefficient, vectors)
            metric_convention_error = max(
                metric_convention_error, float(np.max(np.abs(current_square - coefficient_square)))
            )
        for state_index in range(len(roots)):
            gaussian_columns = [
                q_sqrt @ frame[state_index].T @ gamma_factor[:, column]
                for column in range(gamma_factor.shape[1])
            ]
            square_sum = sum(float(vector @ vector) for vector in gaussian_columns)
            trace_value = float(np.sum(coefficient[state_index] * gamma_test))
            covariance_convention_error = max(
                covariance_convention_error, abs(square_sum - trace_value)
            )

    gamma_low = np.asarray([[0.19, 0.015], [0.015, 0.16]])
    gamma_steps = (
        np.asarray([[0.08, 0.006], [0.006, 0.07]]),
        np.asarray([[0.055, -0.004], [-0.004, 0.05]]),
        np.asarray([[0.04, 0.003], [0.003, 0.035]]),
        np.asarray([[0.03, 0.002], [0.002, 0.027]]),
    )
    gamma_terminal = gamma_low + sum(gamma_steps)

    def trace_pair(coefficient: np.ndarray, gamma: np.ndarray) -> np.ndarray:
        return np.einsum("nij,ij->n", coefficient, gamma)

    current_zero, current_star = currents[0], currents[-1]
    coefficient_zero, coefficient_star = coefficients[0], coefficients[-1]
    p_zero = [conditional(current_zero, roots, depth) for depth in range(5)]
    p_star = [conditional(current_star, roots, depth) for depth in range(5)]
    low = 0.5 * float(np.mean(np.sum(p_star[0] ** 2 - p_zero[0] ** 2, axis=1)))
    low -= 0.5 * float(np.mean(trace_pair(coefficient_star - coefficient_zero, gamma_low)))

    shell_sum = 0.0
    reassembly_error = 0.0
    commutator_error = 0.0
    future_square = 0.0
    trace_split_error = 0.0
    cross_sum = 0.0
    for depth, gamma_step in enumerate(gamma_steps, start=1):
        current_mid = currents[depth]
        coefficient_mid = coefficients[depth]
        d_zero = p_zero[depth] - p_zero[depth - 1]
        f = conditional(current_mid - current_zero, roots, depth) - conditional(
            current_mid - current_zero, roots, depth - 1
        )
        i = conditional(current_star - current_mid, roots, depth) - conditional(
            current_star - current_mid, roots, depth - 1
        )
        d_mid = conditional(current_mid, roots, depth) - conditional(current_mid, roots, depth - 1)
        d_star = p_star[depth] - p_star[depth - 1]
        reassembly_error = max(
            reassembly_error,
            float(np.max(np.abs(d_mid - d_zero - f))),
            float(np.max(np.abs(d_star - d_zero - f - i))),
        )
        injected = float(np.mean(np.sum(d_zero * f, axis=1) + 0.5 * np.sum(f**2, axis=1)))
        injected -= 0.5 * float(np.mean(trace_pair(coefficient_mid - coefficient_zero, gamma_step)))
        future = float(np.mean(np.sum(d_mid * i, axis=1) + 0.5 * np.sum(i**2, axis=1)))
        future -= 0.5 * float(np.mean(trace_pair(coefficient_star - coefficient_mid, gamma_step)))
        trace_split_error = max(
            trace_split_error,
            abs(
                -0.5 * float(np.mean(trace_pair(coefficient_mid - coefficient_zero, gamma_step)))
                - 0.5 * float(np.mean(trace_pair(coefficient_star - coefficient_mid, gamma_step)))
                + 0.5 * float(np.mean(trace_pair(coefficient_star - coefficient_zero, gamma_step)))
            ),
        )
        future_square += 0.5 * float(np.mean(np.sum(i**2, axis=1)))
        cross_sum += float(np.mean(np.sum(f * i, axis=1)))
        shell_sum += injected + future

        direct = np.zeros((len(roots), 2, 2), dtype=float)
        for direction in range(2):
            old_gradient = gradient[:, :, direction] + gradient_controls[depth][:, :, direction]
            gradient_gap = gradient_controls[-1][:, :, direction] - gradient_controls[depth][:, :, direction]
            frame_gap = frames[-1] - frames[depth]
            direct[:, :, direction] = np.einsum(
                "ab,nbc,nc->na", q_sqrt, np.transpose(frame_gap, (0, 2, 1)), old_gradient
            ) + np.einsum(
                "ab,nbc,nc->na", q_sqrt, np.transpose(frames[-1], (0, 2, 1)), gradient_gap
            )
        commutator_error = max(
            commutator_error,
            float(np.max(np.abs(current_star - current_mid - direct.reshape(len(roots), -1)))),
        )

    direct = 0.5 * float(np.mean(np.sum(current_star**2 - current_zero**2, axis=1)))
    direct -= 0.5 * float(np.mean(trace_pair(coefficient_star - coefficient_zero, gamma_terminal)))
    decomposition = low + shell_sum

    functionals = [
        0.5 * np.sum(current**2, axis=1) - 0.5 * trace_pair(coefficient, gamma_terminal) - paid_value
        for current, coefficient, paid_value in zip(currents, coefficients, paid)
    ]
    causal = np.zeros(len(roots))
    for depth in range(1, 5):
        causal += conditional(functionals[depth] - functionals[depth - 1], roots, depth - 1)
    safe_error = (
        direct
        - float(np.mean(paid[-1] - paid[0]))
        - (decomposition - float(np.mean(paid[-1] - paid[0])))
    )
    telescope_error = float(np.mean(causal) - np.mean(functionals[-1] - functionals[0]))
    paid_difference = float(np.mean(paid[-1] - paid[0]))
    safe_decomposition = decomposition - paid_difference
    joined_causal_decomposition_error = float(np.mean(causal) - safe_decomposition)
    joined_endpoint_safe_error = float(
        np.mean(functionals[-1] - functionals[0]) - (direct - paid_difference)
    )
    return {
        "energy_error": direct - decomposition,
        "safe_error": safe_error,
        "telescope_error": telescope_error,
        "reassembly_error": reassembly_error,
        "commutator_error": commutator_error,
        "trace_split_error": trace_split_error,
        "predictability_error": predictability_error,
        "past_increment_error": past_increment_error,
        "joined_causal_decomposition_error": joined_causal_decomposition_error,
        "joined_endpoint_safe_error": joined_endpoint_safe_error,
        "future_square": future_square,
        "cross_sum": cross_sum,
        "paid_difference": paid_difference,
        "low_paid_endpoint": float(np.mean(paid[0])),
        "metric_floor": float(np.min(eigenvalues)),
        "frame_determinant_floor": float(min(np.min(np.linalg.det(frame)) for frame in frames)),
        "metric_convention_error": metric_convention_error,
        "covariance_convention_error": covariance_convention_error,
    }


def four_node_wick_fixture() -> dict[str, float]:
    root = math.sqrt(6.0)
    nodes = np.asarray(
        [-math.sqrt(3.0 + root), -math.sqrt(3.0 - root), math.sqrt(3.0 - root), math.sqrt(3.0 + root)]
    )
    weight_large = (root - 2.0) / (4.0 * root)
    weight_small = (root + 2.0) / (4.0 * root)
    weights = np.asarray([weight_large, weight_small, weight_small, weight_large])
    amplitude = 0.37
    control = amplitude * (nodes**2 - 4.0)
    remainder = 0.5 * float(np.dot(weights, control**2 * (nodes**2 - 1.0))) / amplitude**2
    square = 0.5 * float(np.dot(weights, (control * nodes) ** 2)) / amplitude**2
    trace = -0.5 * float(np.dot(weights, control**2)) / amplitude**2
    innovation = float(np.dot(weights, (control - np.dot(weights, control)) ** 2)) / amplitude**2
    moments = [float(np.dot(weights, nodes**degree)) for degree in range(7)]
    return {
        "weight_sum": float(np.sum(weights)),
        "moment_errors": max(
            abs(moments[0] - 1.0),
            abs(moments[1]),
            abs(moments[2] - 1.0),
            abs(moments[3]),
            abs(moments[4] - 3.0),
            abs(moments[5]),
            abs(moments[6] - 15.0),
        ),
        "remainder": remainder,
        "square": square,
        "trace": trace,
        "innovation": innovation,
    }


def smooth_wick_quadrature() -> dict[str, float]:
    raw_nodes, raw_weights = np.polynomial.hermite.hermgauss(80)
    nodes = math.sqrt(2.0) * raw_nodes
    weights = raw_weights / math.sqrt(math.pi)
    amplitude = 0.23
    control = amplitude * np.exp(-(nodes**2))
    remainder = 0.5 * float(np.dot(weights, control**2 * (nodes**2 - 1.0)))
    analytic = -2.0 * amplitude**2 / (5.0 * math.sqrt(5.0))
    return {
        "remainder": remainder,
        "analytic": analytic,
        "error": remainder - analytic,
        "frame_floor": float(np.min(1.0 + control)),
    }


def fraction_ledgers() -> dict[str, Fraction]:
    s_numerator, s_denominator = 3, 5
    s = Fraction(s_numerator, s_denominator)
    base_x = Fraction(s_denominator + s_numerator, 4 * s_denominator)
    base_y = Fraction(5 * s_denominator - s_numerator, 12 * s_denominator)
    combined_x = base_x + Fraction(1, 2)
    deficit = Fraction(1) - combined_x - base_y
    gamma = Fraction(3, 10)
    gain_x = Fraction(1, 2) - gamma / 4
    gain_y = Fraction(1, 2) + gamma / 12
    gain_slack = Fraction(1) - gain_x - gain_y
    return {
        "combined_x": combined_x,
        "combined_y": base_y,
        "deficit": deficit,
        "gain_x": gain_x,
        "gain_y": gain_y,
        "gain_slack": gain_slack,
        "gain_moment": 1 / gain_slack,
        "gain_eta": gain_x / gain_slack,
        "gain_zeta": gain_y / gain_slack,
    }


def weighted_tree_and_rare_branch() -> dict[str, float]:
    roots = np.asarray([(a, b, c, d) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1) for d in (-1, 1)], dtype=float)
    a, b, c, _ = roots.T
    h = {2: 0.27 * a, 3: 0.19 * a - 0.31 * a * b, 4: 0.14 * b + 0.24 * a * b * c}
    lhs = 0.0
    rhs = 0.0
    for shell, value in h.items():
        frequency = float(2**shell)
        control = frequency**-2 * value
        rhs += float(np.mean(value**2))
        for depth in range(1, shell):
            delta = conditional(control, roots, depth) - conditional(control, roots, depth - 1)
            lhs += frequency**4 * float(np.mean(delta**2))
    frequency = 3.0
    probability = frequency**-6
    h_amplitude = probability**-0.5
    control_amplitude = frequency**-2 * h_amplitude
    return {
        "weighted_lhs": lhs,
        "energy_rhs": rhs,
        "weighted_margin": rhs - lhs,
        "rare_energy": probability * h_amplitude**2,
        "rare_sextic": probability * control_amplitude**6,
        "rare_conditional": h_amplitude**2,
    }


def heat_projection_quadrature() -> dict[str, float]:
    raw_nodes, raw_weights = np.polynomial.hermite.hermgauss(48)
    nodes = math.sqrt(2.0) * raw_nodes
    weights = raw_weights / math.sqrt(math.pi)
    past_value, past_gradient = -0.31, 0.42
    value_grid, derivative_grid = np.meshgrid(nodes, nodes, indexing="ij")
    joint_weights = np.outer(weights, weights)
    multiplier = 1.0 + 0.2 * np.tanh(past_value + value_grid) + 0.04 * np.cos(past_value + value_grid)
    current = float(np.sum(joint_weights * multiplier * (past_gradient + derivative_grid)))
    heat = float(np.dot(weights, 1.0 + 0.2 * np.tanh(past_value + nodes) + 0.04 * np.cos(past_value + nodes)))
    return {"current": current, "heat_times_past": heat * past_gradient, "error": current - heat * past_gradient}


def main() -> int:
    rows: list[dict[str, Any]] = []
    matrix = matrix_fixture()
    for key in (
        "energy_error", "telescope_error", "reassembly_error", "commutator_error",
        "trace_split_error", "predictability_error", "past_increment_error",
        "joined_causal_decomposition_error", "joined_endpoint_safe_error",
        "metric_convention_error", "covariance_convention_error",
    ):
        add(rows, f"matrix_{key}", abs(matrix[key]) < TOL, matrix[key], 0.0)
    add(rows, "matrix_metric_positive", matrix["metric_floor"] > 0.0, matrix["metric_floor"], ">0")
    add(rows, "matrix_frame_invertible", matrix["frame_determinant_floor"] > 1.0, matrix["frame_determinant_floor"], ">1")
    add(rows, "matrix_future_square_retained", matrix["future_square"] > 0.0, matrix["future_square"], ">0")
    add(rows, "matrix_cross_term_nonzero", abs(matrix["cross_sum"]) > TOL, matrix["cross_sum"], "nonzero")
    add(rows, "matrix_paid_difference_nonzero", abs(matrix["paid_difference"]) > TOL, matrix["paid_difference"], "nonzero")
    add(rows, "matrix_low_paid_endpoint", matrix["low_paid_endpoint"] > 0.0, matrix["low_paid_endpoint"], ">0")

    wick = four_node_wick_fixture()
    add(rows, "four_node_weights", abs(wick["weight_sum"] - 1.0) < TOL, wick["weight_sum"], 1.0)
    add(rows, "four_node_moments", wick["moment_errors"] < TOL, wick["moment_errors"], 0.0)
    for key, expected in (("remainder", -2.0), ("square", 3.5), ("trace", -5.5), ("innovation", 2.0)):
        add(rows, f"four_node_{key}", abs(wick[key] - expected) < TOL, wick[key], expected)
    add(rows, "four_node_wrong_sign", abs(wick["remainder"] + wick["innovation"]) < TOL, {"remainder": wick["remainder"], "innovation": wick["innovation"]}, "remainder=-innovation")

    smooth = smooth_wick_quadrature()
    add(rows, "smooth_quadrature", abs(smooth["error"]) < 2.0e-12, smooth["error"], 0.0)
    add(rows, "smooth_negative", smooth["remainder"] < 0.0, smooth["remainder"], "<0")
    add(rows, "smooth_frame_positive", smooth["frame_floor"] >= 1.0, smooth["frame_floor"], ">=1")

    ledgers = fraction_ledgers()
    expected = {
        "combined_x": Fraction(9, 10), "combined_y": Fraction(11, 30), "deficit": Fraction(-4, 15),
        "gain_x": Fraction(17, 40), "gain_y": Fraction(21, 40), "gain_slack": Fraction(1, 20),
        "gain_moment": Fraction(20), "gain_eta": Fraction(17, 2), "gain_zeta": Fraction(21, 2),
    }
    for key, value in expected.items():
        add(rows, f"ledger_{key}", ledgers[key] == value, str(ledgers[key]), str(value))

    weighted = weighted_tree_and_rare_branch()
    add(rows, "weighted_square_nonzero", weighted["weighted_lhs"] > 0.0, weighted["weighted_lhs"], ">0")
    add(rows, "weighted_square_one_use", weighted["weighted_margin"] >= -TOL, weighted["weighted_margin"], ">=0")
    add(rows, "rare_expected_energy", abs(weighted["rare_energy"] - 1.0) < TOL, weighted["rare_energy"], 1.0)
    add(rows, "rare_expected_sextic", abs(weighted["rare_sextic"] - 1.0) < TOL, weighted["rare_sextic"], 1.0)
    add(rows, "rare_conditional_growth", weighted["rare_conditional"] > 700.0, weighted["rare_conditional"], ">700")

    heat = heat_projection_quadrature()
    add(rows, "heat_projection_identity", abs(heat["error"]) < 2.0e-12, heat["error"], 0.0)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-full-safe-packet-frame-current-doob-independent/1.0",
        "result_id": RESULT_ID,
        "claim_id": CLAIM,
        "source_version": __version__,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "matrix_decomposition": matrix,
        "four_node_wick_no_go": wick,
        "smooth_wick_no_go": smooth,
        "exponents": {key: str(value) for key, value in ledgers.items()},
        "weighted_cm_and_bmo": weighted,
        "base_current_heat_identity": heat,
        "safe_subtractor_fixture_scope": (
            "The independent nonzero paid functional tests only structural W-P "
            "bookkeeping. The production N3_nr+T_le identification is analytic and "
            "pinned to R-078, not rebuilt by this synthetic matrix fixture."
        ),
        "imports_primary": False,
        "claims_not_established": {
            "weighted_production_lower_bound": False,
            "complete_packet_lower_bound": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "sector_a_closure": False,
        },
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-079 independent] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    if passed == len(rows):
        print("A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-INDEPENDENT-PASS")
        return 0
    for row in rows:
        if row["status"] != "PASS":
            print(f"FAIL {row['name']}: actual={row['actual']!r} expected={row['expected']!r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
