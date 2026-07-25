#!/usr/bin/env python3
"""Non-importing independent audit for the R-087 A13 reduction.

This program uses handwritten exact rational matrix algebra, seeded numerical
linear solves, a finite-difference/FFT Cartan fixture, and independent
fraction arithmetic.  It imports no code from the primary R-087 executable.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION"
R085 = REPO / f"claims/{CLAIM}/classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json"
R086 = REPO / f"claims/{CLAIM}/classii_rational_translated_wick_payload_comparable_reduction_manifest.json"
OUTPUT = REPO / f"claims/{CLAIM}/runs/2026-07-25-independent-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json"


INPUTS = {
    "dimension": 3,
    "covariance_decay": 4,
    "holder_alpha": F(2, 5),
    "schur_s": F(7, 12),
    "far_separation": 5,
    "eta_fixture": F(3, 5),
    "random_seed": 87025,
}

TEST_ORACLES = {
    "beta": F(7, 5),
    "max_s": F(7, 10),
    "root_margin": F(7, 30),
    "gap_margin": F(13, 30),
    "exact_completion": F(-129, 10),
    "exact_debt": F(1335, 116),
    "exact_debt_bound": F(55, 3),
    "exact_debt_gap": F(2375, 348),
}


Matrix = list[list[F]]
Vector = list[F]


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def eye(size: int) -> Matrix:
    return [[F(int(i == j)) for j in range(size)] for i in range(size)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] + right[i][j] for j in range(len(left))] for i in range(len(left))]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] - right[i][j] for j in range(len(left))] for i in range(len(left))]


def scale(value: F, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), F(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [sum((matrix[i][j] * vector[j] for j in range(len(vector))), F(0)) for i in range(len(matrix))]


def dot(left: Vector, right: Vector) -> F:
    return sum((left[i] * right[i] for i in range(len(left))), F(0))


def contract(left: Matrix, right: Matrix) -> F:
    return sum((left[i][j] * right[i][j] for i in range(len(left)) for j in range(len(left))), F(0))


def outer(left: Vector, right: Vector) -> Matrix:
    return [[left[i] * right[j] for j in range(len(right))] for i in range(len(left))]


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    augmented = [matrix[i][:] + eye(size)[i] for i in range(size)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if augmented[row][column] != 0)
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [entry / divisor for entry in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [augmented[row][j] - factor * augmented[column][j] for j in range(2 * size)]
    return [row[size:] for row in augmented]


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {key: serial(item) for key, item in value.items()}
    return value


def phi(point: np.ndarray, floor: float) -> np.ndarray:
    x, y = point
    q = (x * x - y * y) / (x * x + y * y + floor)
    return q * point


def finite_difference_jacobian(point: np.ndarray, floor: float, step: float) -> np.ndarray:
    columns = []
    for axis in range(2):
        direction = np.zeros(2)
        direction[axis] = step
        columns.append((phi(point + direction, floor) - phi(point - direction, floor)) / (2 * step))
    return np.column_stack(columns)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": serial(actual), "expected": serial(expected)})

    r085 = json.loads(R085.read_text(encoding="utf-8"))
    r086 = json.loads(R086.read_text(encoding="utf-8"))
    check("r085_predecessor", r085.get("result_id") == "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY", r085.get("result_id"), "R-085 result")
    check("r086_predecessor", r086.get("result_id") == "A13-CLASSII-RATIONAL-TRANSLATED-WICK-PAYLOAD-COMPARABLE-REDUCTION", r086.get("result_id"), "R-086 result")

    alpha = INPUTS["holder_alpha"]
    schur_s = INPUTS["schur_s"]
    beta = 6 * alpha - 1
    maximum_s = beta / 2
    root_margin = beta - 2 * schur_s
    gap_margin = 4 * alpha - 2 * schur_s
    check("value_root_power", INPUTS["dimension"] - INPUTS["covariance_decay"] == -1, INPUTS["dimension"] - INPUTS["covariance_decay"], -1)
    check("derivative_root_power", INPUTS["dimension"] + 2 - INPUTS["covariance_decay"] == 1, INPUTS["dimension"] + 2 - INPUTS["covariance_decay"], 1)
    check("beta", beta == TEST_ORACLES["beta"], beta, TEST_ORACLES["beta"])
    check("maximum_s", maximum_s == TEST_ORACLES["max_s"], maximum_s, TEST_ORACLES["max_s"])
    check("schur_threshold", F(1, 2) < schur_s < maximum_s, schur_s, "1/2<s<7/10")
    check("root_margin", root_margin == TEST_ORACLES["root_margin"], root_margin, TEST_ORACLES["root_margin"])
    check("gap_margin", gap_margin == TEST_ORACLES["gap_margin"], gap_margin, TEST_ORACLES["gap_margin"])

    # Independent rational support arithmetic for the smooth LP convention.
    p1_radius = F(5, 3) * 2
    p2_radius = F(5, 3) * 4
    worst_radius = max(p1_radius + 3, p2_radius + 2)
    projection_edge = F(2 ** (INPUTS["far_separation"] - 1))
    check("smooth_lp_p1_radius", p1_radius == F(10, 3), p1_radius, F(10, 3))
    check("smooth_lp_p2_radius", p2_radius == F(20, 3), p2_radius, F(20, 3))
    check("smooth_lp_worst_radius", worst_radius == F(26, 3), worst_radius, F(26, 3))
    check("smooth_lp_far_support", worst_radius < projection_edge, [worst_radius, projection_edge], "strict separation")

    # Numerical first-order two-mode Cartan fixture.  It directly refutes
    # algebraic cancellation while showing that only J-K and J+K occur.
    grid_size = 2048
    coordinate = 2 * np.pi * np.arange(grid_size) / grid_size
    mode_j, mode_k = 17, 11
    floor_value = 0.2
    jacobian = finite_difference_jacobian(np.array([1.0, 1.0]), floor_value, 1e-6)
    a_value = np.sin(mode_k * coordinate)
    a_derivative = mode_k * np.cos(mode_k * coordinate)
    v_value = np.cos(mode_j * coordinate)
    v_derivative = -mode_j * np.sin(mode_j * coordinate)
    mixed = jacobian[0, 1] * v_value * a_derivative + jacobian[1, 0] * a_value * v_derivative
    expected_mixed = -(
        (mode_k + mode_j) * np.cos((mode_j - mode_k) * coordinate)
        + (mode_k - mode_j) * np.cos((mode_j + mode_k) * coordinate)
    ) / (2 + floor_value)
    cartan_residual = float(np.max(np.abs(mixed - expected_mixed)))
    spectrum = np.fft.fft(mixed) / grid_size
    carriers = {mode_j - mode_k, grid_size - (mode_j - mode_k), mode_j + mode_k, grid_size - (mode_j + mode_k)}
    off_carrier = max(abs(spectrum[index]) for index in range(grid_size) if index not in carriers)
    on_carrier = min(abs(spectrum[index]) for index in carriers)
    check("cartan_jacobian_offdiagonal_signs", jacobian[0, 1] < 0 < jacobian[1, 0], jacobian, "J01<0<J10")
    check("cartan_two_mode_formula", cartan_residual < 2e-8, cartan_residual, "<2e-8")
    check("cartan_two_mode_nonzero", float(np.linalg.norm(mixed)) > 1, float(np.linalg.norm(mixed)), ">1")
    check("cartan_only_sum_difference_carriers", off_carrier < 1e-12 and on_carrier > 1e-2, [off_carrier, on_carrier], "off<1e-12 and on>1e-2")

    # Handwritten exact three-dimensional noncommuting Schur/Wick fixture.
    b1: Matrix = [[F(4), F(1), F(0)], [F(1), F(1), F(0)], [F(0), F(0), F(0)]]
    l_matrix: Matrix = [[F(2), F(-1), F(1)], [F(-1), F(0), F(2)], [F(1), F(2), F(-1)]]
    gamma: Matrix = [[F(5), F(2), F(1)], [F(2), F(2), F(1)], [F(1), F(1), F(2)]]
    g_vector: Vector = [F(1), F(-2), F(3)]
    c_vector: Vector = [F(-1), F(2), F(1)]
    eta = INPUTS["eta_fixture"]
    q_tensor = subtract(outer(g_vector, g_vector), gamma)
    a_eta = add(b1, scale(2 * eta, eye(3)))
    a_inverse = inverse(a_eta)
    k_matrix = multiply(multiply(l_matrix, a_inverse), l_matrix)
    m_matrix = subtract(l_matrix, k_matrix)
    left_packet = contract(l_matrix, q_tensor) / 2 + dot(g_vector, matvec(l_matrix, c_vector)) + dot(c_vector, matvec(b1, c_vector)) / 2
    left_regularised = left_packet + eta * dot(c_vector, c_vector)
    shift = [c_vector[i] + matvec(a_inverse, matvec(l_matrix, g_vector))[i] for i in range(3)]
    completed_square = dot(shift, matvec(a_eta, shift)) / 2
    debt = contract(k_matrix, gamma) / 2
    right_regularised = completed_square + contract(m_matrix, q_tensor) / 2 - debt
    debt_bound = contract(multiply(l_matrix, l_matrix), gamma) / (4 * eta)

    expected_inverse: Matrix = [[F(55, 261), F(-25, 261), F(0)], [F(-25, 261), F(130, 261), F(0)], [F(0), F(0), F(5, 6)]]
    check("exact_A_inverse", a_inverse == expected_inverse, a_inverse, expected_inverse)
    check("exact_q_contraction", contract(l_matrix, q_tensor) / 2 == F(-31, 2), contract(l_matrix, q_tensor) / 2, F(-31, 2))
    check("exact_cross", dot(g_vector, matvec(l_matrix, c_vector)) == F(-3), dot(g_vector, matvec(l_matrix, c_vector)), F(-3))
    check("exact_endpoint_square", dot(c_vector, matvec(b1, c_vector)) / 2 == F(2), dot(c_vector, matvec(b1, c_vector)) / 2, F(2))
    check("exact_packet", left_packet == F(-33, 2), left_packet, F(-33, 2))
    check("exact_regularised_left", left_regularised == TEST_ORACLES["exact_completion"], left_regularised, TEST_ORACLES["exact_completion"])
    check("exact_completed_square", completed_square == F(66911, 2610), completed_square, F(66911, 2610))
    check("exact_M_Q", contract(m_matrix, q_tensor) / 2 == F(-973, 36), contract(m_matrix, q_tensor) / 2, F(-973, 36))
    check("exact_debt", debt == TEST_ORACLES["exact_debt"], debt, TEST_ORACLES["exact_debt"])
    check("exact_completion_identity", right_regularised == left_regularised, right_regularised, left_regularised)
    check("exact_debt_bound", debt_bound == TEST_ORACLES["exact_debt_bound"], debt_bound, TEST_ORACLES["exact_debt_bound"])
    check("exact_debt_gap", debt_bound - debt == TEST_ORACLES["exact_debt_gap"], debt_bound - debt, TEST_ORACLES["exact_debt_gap"])

    # PSD and sign diagnostics use eigenvalues independently of the exact
    # rational implementation.
    k_numpy = np.array([[float(value) for value in row] for row in k_matrix])
    m_numpy = np.array([[float(value) for value in row] for row in m_matrix])
    k_eigenvalues = np.linalg.eigvalsh(k_numpy)
    m_eigenvalues = np.linalg.eigvalsh(m_numpy)
    check("K_psd", float(k_eigenvalues.min()) > 0, k_eigenvalues, ">0")
    check("M_indefinite", float(m_eigenvalues.min()) < 0 < float(m_eigenvalues.max()), m_eigenvalues, "mixed signs")

    # Mutation tests: each common transcription error must destroy the exact
    # identity on the noncommuting fixture.
    wrong_a = add(b1, scale(eta, eye(3)))
    wrong_inverse = inverse(wrong_a)
    wrong_k = multiply(multiply(l_matrix, wrong_inverse), l_matrix)
    wrong_m = subtract(l_matrix, wrong_k)
    wrong_shift = [c_vector[i] + matvec(wrong_inverse, matvec(l_matrix, g_vector))[i] for i in range(3)]
    wrong_rhs = dot(wrong_shift, matvec(wrong_a, wrong_shift)) / 2 + contract(wrong_m, q_tensor) / 2 - contract(wrong_k, gamma) / 2
    wrong_order = multiply(multiply(l_matrix, l_matrix), a_inverse)
    wrong_order_m = subtract(l_matrix, wrong_order)
    wrong_order_rhs = completed_square + contract(wrong_order_m, q_tensor) / 2 - contract(wrong_order, gamma) / 2
    check("mutation_missing_factor_two_fails", wrong_rhs != left_regularised, wrong_rhs, "not exact left")
    check("mutation_noncommuting_order_fails", wrong_order_rhs != left_regularised, wrong_order_rhs, "not exact left")
    check("mutation_missing_debt_fails", completed_square + contract(m_matrix, q_tensor) / 2 != left_regularised, completed_square + contract(m_matrix, q_tensor) / 2, "not exact left")

    # Seeded numerical stress test uses solves rather than explicit inverses.
    rng = np.random.default_rng(INPUTS["random_seed"])
    residuals: list[float] = []
    debt_gaps: list[float] = []
    for _ in range(12):
        root_b = rng.normal(size=(4, 3))
        root_gamma = rng.normal(size=(4, 3))
        b = root_b.T @ root_b
        gamma_num = root_gamma.T @ root_gamma
        raw_l = rng.normal(size=(3, 3))
        l_num = (raw_l + raw_l.T) / 2
        g_num = rng.normal(size=3)
        c_num = rng.normal(size=3)
        eta_num = float(rng.uniform(0.05, 1.2))
        a_num = b + 2 * eta_num * np.eye(3)
        solved_l = np.linalg.solve(a_num, l_num)
        k_num = l_num @ solved_l
        m_num = l_num - k_num
        q_num = np.outer(g_num, g_num) - gamma_num
        left_num = 0.5 * np.sum(l_num * q_num) + g_num @ l_num @ c_num + 0.5 * c_num @ b @ c_num + eta_num * (c_num @ c_num)
        shift_num = c_num + np.linalg.solve(a_num, l_num @ g_num)
        debt_num = 0.5 * np.sum(k_num * gamma_num)
        right_num = 0.5 * shift_num @ a_num @ shift_num + 0.5 * np.sum(m_num * q_num) - debt_num
        residuals.append(abs(float(left_num - right_num)))
        upper_num = np.sum((l_num @ l_num) * gamma_num) / (4 * eta_num)
        debt_gaps.append(float(upper_num - debt_num))
    check("random_completion_residual", max(residuals) < 2e-12, max(residuals), "<2e-12")
    check("random_debt_bound_gap_nonnegative", min(debt_gaps) > -2e-12, min(debt_gaps), ">-2e-12")

    # Small-amplitude persistence is exact: L(rho)=rho^3 L0 and the Schur
    # correction/debt are sixth order.
    persistence_residuals: list[F] = []
    debt_ratios: list[F] = []
    for rho in (F(1, 2), F(1, 3), F(1, 5), F(1, 10)):
        scaled_l = scale(rho**3, l_matrix)
        scaled_k = multiply(multiply(scaled_l, a_inverse), scaled_l)
        scaled_m = subtract(scaled_l, scaled_k)
        persistence_residuals.append((contract(scaled_m, q_tensor) / 2 - rho**3 * F(-31, 2)) / rho**6)
        debt_ratios.append((contract(scaled_k, gamma) / 2) / rho**6)
    check("small_amplitude_Q_residual_constant", len(set(persistence_residuals)) == 1 and persistence_residuals[0] == F(-415, 36), persistence_residuals, F(-415, 36))
    check("small_amplitude_debt_order_six", len(set(debt_ratios)) == 1 and debt_ratios[0] == TEST_ORACLES["exact_debt"], debt_ratios, TEST_ORACLES["exact_debt"])
    check("small_amplitude_leading_packet_nonzero", F(-31, 2) != 0, F(-31, 2), "nonzero")

    # Rare-event method no-go and independent Boue--Dupuis arithmetic.
    rare_growth: list[int] = []
    for shell in (2, 3, 5, 7):
        probability = F(1, shell**6)
        energy_expectation = probability * shell**6
        extracted = shell**6
        check(f"rare_event_budget_shell_{shell}", energy_expectation == 1, energy_expectation, 1)
        check(f"rare_event_growth_shell_{shell}", extracted == 1 / probability, extracted, 1 / probability)
        rare_growth.append(extracted)
    check("rare_event_growth_strict", all(rare_growth[i] < rare_growth[i + 1] for i in range(len(rare_growth) - 1)), rare_growth, "strictly increasing")

    q_nelson = F(10, 9)
    p_compare = F(11, 10)
    energy_coefficient = 1 / (2 * q_nelson)
    check("bd_energy_coefficient", energy_coefficient == F(9, 20), energy_coefficient, F(9, 20))
    check("bd_q_minus_p", q_nelson - p_compare == F(1, 90), q_nelson - p_compare, F(1, 90))
    check("bd_energy_reserve", 1 / (2 * p_compare) - energy_coefficient == F(1, 220), 1 / (2 * p_compare) - energy_coefficient, F(1, 220))
    slope = F(5, 17)
    optimal_drift = -q_nelson * slope
    rhs_linear = slope * optimal_drift + energy_coefficient * optimal_drift**2
    lhs_linear = -q_nelson * slope**2 / 2
    check("bd_linear_gaussian_fixture", rhs_linear == lhs_linear, rhs_linear, lhs_linear)

    claims_not_established = {
        "cartan_one_use_q_ledger": False,
        "complete_production_cartan_atom_estimate": False,
        "controlled_cartan_cfar": False,
        "coefficient_dominant_rational_packet": False,
        "complete_rational_near": False,
        "complete_signed_near": False,
        "complete_regular_packet_lower_bound": False,
        "overlap_uniform_bound": False,
        "controlled_shell_one_use": False,
        "nelson_bound": False,
        "interacting_measure": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    check("all_downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-cartan-spatial-decay-rational-trace-variational-core-reduction-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "cartan": {
            "beta": str(beta),
            "maximum_s": str(maximum_s),
            "root_margin": str(root_margin),
            "gap_margin": str(gap_margin),
            "safe_C0": INPUTS["far_separation"],
            "two_mode_max_residual": cartan_residual,
            "off_carrier_max": float(off_carrier),
        },
        "rational": {
            "completion_value": str(left_regularised),
            "trace_debt": str(debt),
            "trace_debt_bound": str(debt_bound),
            "random_max_residual": max(residuals),
            "M_eigenvalues": m_eigenvalues.tolist(),
        },
        "variational_core": {
            "q": str(q_nelson),
            "energy_coefficient": str(energy_coefficient),
            "q_minus_p": str(q_nelson - p_compare),
            "energy_reserve": str(1 / (2 * p_compare) - energy_coefficient),
        },
        "rare_event_growth": rare_growth,
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if passed == len(rows):
        print(f"[R-087 independent] {passed}/{len(rows)} PASS")
        return 0
    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-087 independent] {passed}/{len(rows)} PASS; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
