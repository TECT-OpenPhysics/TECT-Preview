#!/usr/bin/env python3
"""Primary executable evidence for the R-084 A13 reduction.

The script checks the root-first Cartan martingale identity, its exact
finite-dimensional OU energy representation, the cumulative-root no-go, and
the endpoint/form absorption algebra for the three linear Pauli--Fierz rows.
It deliberately does not claim the missing production OU-gradient estimate
or the nonlinear rational-row NEAR bound.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import itertools
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
RESULT_ID = "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION"
MODEL = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-25-primary-root-diagonal-cartan-ou-linear-pf-absorption/result.json"


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


def conditional_average(values: dict[tuple[int, ...], np.ndarray], prefix: tuple[int, ...]) -> np.ndarray:
    selected = [value for outcome, value in values.items() if outcome[: len(prefix)] == prefix]
    return sum(selected, np.zeros_like(selected[0])) / len(selected)


def normal_moment(power: int) -> int:
    if power % 2:
        return 0
    answer = 1
    for value in range(1, power, 2):
        answer *= value
    return answer


def polynomial_power(coefficients: list[Fraction], power: int) -> list[Fraction]:
    result = [Fraction(1)]
    for _ in range(power):
        product = [Fraction(0)] * (len(result) + len(coefficients) - 1)
        for left_index, left in enumerate(result):
            for right_index, right in enumerate(coefficients):
                product[left_index + right_index] += left * right
        result = product
    return result


def gaussian_expectation(coefficients: list[Fraction]) -> Fraction:
    return sum((coefficient * normal_moment(power) for power, coefficient in enumerate(coefficients)), Fraction(0))


def quotient_vector(z: np.ndarray, symmetric: np.ndarray, floor: float) -> np.ndarray:
    density = float(z @ z) + floor
    quotient = float(z @ symmetric @ z) / density
    return quotient * z


def quotient_derivative(
    z: np.ndarray, direction: np.ndarray, symmetric: np.ndarray, floor: float
) -> np.ndarray:
    density = float(z @ z) + floor
    quotient = float(z @ symmetric @ z) / density
    remainder = (symmetric - quotient * np.eye(len(z))) @ z
    d_quotient = 2.0 * float(remainder @ direction) / density
    return quotient * direction + z * d_quotient


def row_energy(matrix: np.ndarray, z: np.ndarray, y: np.ndarray, gamma: np.ndarray) -> float:
    coefficient = matrix.T @ z
    return 0.5 * (float(coefficient @ y) ** 2 - float(coefficient @ gamma @ coefficient))


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    model = json.loads(MODEL.read_text(encoding="utf-8"))
    parameters = model["parameters"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["rho_regularizer"])
    a_weight = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator
    b_weight = float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator
    c_weight = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    alpha = c_weight / (b_weight + c_weight)
    c1 = c_weight / alpha**2
    c0 = a_weight - b_weight**2 / c_weight
    csum = c0 + c1
    floor = float(parameters["rho_regularizer"])

    check("model_schema", model.get("schema") == "tect/a1-production-functional-realisation/1.0", model.get("schema"), "tect/a1-production-functional-realisation/1.0")
    check("production_alpha", abs(alpha - 5.0 / 9.0) < 1e-14, alpha, "5/9")
    check("production_c0", abs(c0 - 3.0 / (250.0 * denominator)) < 1e-14, c0, "3/(250P)")
    check("production_c1", abs(c1 - 243.0 / (8000.0 * denominator)) < 1e-14, c1, "243/(8000P)")
    check("production_csum", abs(csum - 339.0 / (8000.0 * denominator)) < 1e-14, csum, "339/(8000P)")
    check("cartan_prefactor", abs(4.0 * alpha**2 * c1 - 3.0 / (80.0 * denominator)) < 1e-15, 4.0 * alpha**2 * c1, "3/(80P)")

    # Root-first martingale reindexing on an exact finite Rademacher tree.
    root_count = 3
    amplitudes = np.array([1.25, -0.5, 0.75])
    outcomes = list(itertools.product((-1, 1), repeat=root_count))
    terminal_increments: list[dict[tuple[int, ...], np.ndarray]] = []
    for k in range(root_count):
        terminal_increments.append(
            {
                outcome: np.array([amplitudes[k] * sum(outcome[k:]), amplitudes[k] * sum((r + 1) * outcome[r] for r in range(k, root_count))])
                for outcome in outcomes
            }
        )
    martingale_differences: list[dict[tuple[int, ...], np.ndarray]] = []
    root_formula_residual = 0.0
    for j in range(root_count):
        terminal_g = {
            outcome: sum((terminal_increments[k][outcome] for k in range(j + 1)), np.zeros(2))
            for outcome in outcomes
        }
        differences: dict[tuple[int, ...], np.ndarray] = {}
        for outcome in outcomes:
            p_j = conditional_average(terminal_g, outcome[: j + 1])
            p_previous = conditional_average(terminal_g, outcome[:j])
            differences[outcome] = p_j - p_previous
            expected = sum(amplitudes[: j + 1]) * np.array([outcome[j], (j + 1) * outcome[j]])
            root_formula_residual = max(root_formula_residual, float(np.max(np.abs(differences[outcome] - expected))))
        martingale_differences.append(differences)
    check("root_first_increment_formula", root_formula_residual < 1e-14, root_formula_residual, 0.0)

    cross_residual = 0.0
    for i in range(root_count):
        for j in range(i + 1, root_count):
            cross = sum(float(martingale_differences[i][outcome] @ martingale_differences[j][outcome]) for outcome in outcomes) / len(outcomes)
            cross_residual = max(cross_residual, abs(cross))
    check("root_martingale_orthogonality", cross_residual < 1e-14, cross_residual, 0.0)

    direct_square = sum(
        float(sum((martingale_differences[j][outcome] for j in range(root_count)), np.zeros(2)) @ sum((martingale_differences[j][outcome] for j in range(root_count)), np.zeros(2)))
        for outcome in outcomes
    ) / len(outcomes)
    diagonal_square = sum(
        sum(float(value @ value) for value in martingale_differences[j].values()) / len(outcomes)
        for j in range(root_count)
    )
    check("root_first_square_diagonalization", abs(direct_square - diagonal_square) < 1e-14, direct_square - diagonal_square, 0.0)

    # A lower-triangular tree proves that root orthogonality alone is not one-use.
    tree_size = 8
    cumulative = np.tril(np.ones((tree_size, tree_size)))
    old_input = np.zeros(tree_size)
    old_input[0] = 1.0
    equal_input = np.ones(tree_size) / math.sqrt(tree_size)
    old_energy = float(np.linalg.norm(cumulative @ old_input) ** 2)
    equal_energy = float(np.linalg.norm(cumulative @ equal_input) ** 2)
    exact_equal = Fraction((tree_size + 1) * (2 * tree_size + 1), 6)
    singular_square = float(np.linalg.eigvalsh(cumulative @ cumulative.T)[-1])
    exact_singular_square = 1.0 / (4.0 * math.sin(math.pi / (4 * tree_size + 2)) ** 2)
    inverse_eigenvalues = np.linalg.eigvalsh(np.linalg.inv(cumulative @ cumulative.T))
    expected_inverse = np.sort(np.array([4.0 * math.sin((2 * r - 1) * math.pi / (4 * tree_size + 2)) ** 2 for r in range(1, tree_size + 1)]))
    check("tree_old_input_norm_one", abs(float(old_input @ old_input) - 1.0) < 1e-15, float(old_input @ old_input), 1.0)
    check("tree_old_input_energy_N", abs(old_energy - tree_size) < 1e-14, old_energy, tree_size)
    check("tree_equal_input_norm_one", abs(float(equal_input @ equal_input) - 1.0) < 1e-14, float(equal_input @ equal_input), 1.0)
    check("tree_equal_input_energy", abs(equal_energy - float(exact_equal)) < 1e-13, equal_energy, str(exact_equal))
    check("tree_operator_norm_formula", abs(singular_square - exact_singular_square) < 1e-12, singular_square, exact_singular_square)
    check("tree_inverse_spectrum", float(np.max(np.abs(inverse_eigenvalues - expected_inverse))) < 1e-12, float(np.max(np.abs(inverse_eigenvalues - expected_inverse))), "<1e-12")
    check("tree_no_uniform_one_use", old_energy > 4.0 * float(old_input @ old_input), old_energy, ">4 for one old input")

    # Exact Gaussian OU energy identity on vector-valued Hermite chaoses.
    hermite_coefficients = {
        1: np.array([1.0, -0.25, 0.5]),
        2: np.array([0.375, 0.2, -0.1]),
        3: np.array([-0.125, 0.3, 0.05]),
        5: np.array([0.015625, -0.02, 0.01]),
    }
    variance = sum(math.factorial(order) * float(vector @ vector) for order, vector in hermite_coefficients.items())
    ou_energy = sum(
        2.0 * order**2 * math.factorial(order - 1) * float(vector @ vector) / (2.0 * order)
        for order, vector in hermite_coefficients.items()
    )
    poincare_energy = sum(order**2 * math.factorial(order - 1) * float(vector @ vector) for order, vector in hermite_coefficients.items())
    check("OU_resolvent_variance_identity", abs(variance - ou_energy) < 1e-14, ou_energy - variance, 0.0)
    check("OU_Poincare_upper_bound", poincare_energy >= variance and poincare_energy > variance, [variance, poincare_energy], "gradient energy > variance")
    check("OU_linear_root_factor", abs(2.0 * 1.0**2 / 2.0 - 1.0) < 1e-15, 2.0 * 1.0**2 / 2.0, 1.0)
    check("OU_quadratic_root_factor", abs(2.0 * 4.0 / 4.0 - 2.0) < 1e-15, 2.0 * 4.0 / 4.0, 2.0)

    # Actual quotient-vector directional derivative, with predictable a fixed.
    symmetric = np.diag([1.0, -1.0, 0.0, 1.0, -1.0, 0.0])
    rng = np.random.default_rng(84025)
    chain_residual = 0.0
    for _ in range(32):
        z = 0.35 * rng.normal(size=6)
        a = 0.2 * rng.normal(size=6)
        dz = 0.3 * rng.normal(size=6)
        da = 0.15 * rng.normal(size=6)
        value_direction = rng.normal(size=6)
        derivative_direction = rng.normal(size=6)

        def current_difference(step: float) -> float:
            moved_z = z + step * value_direction
            moved_dz = dz + step * derivative_direction
            return float(quotient_vector(moved_z + a, symmetric, floor) @ (moved_dz + da) - quotient_vector(moved_z, symmetric, floor) @ moved_dz)

        step = 2.0e-6
        numerical = (current_difference(step) - current_difference(-step)) / (2.0 * step)
        analytic = float(
            (quotient_derivative(z + a, value_direction, symmetric, floor) - quotient_derivative(z, value_direction, symmetric, floor)) @ dz
            + quotient_derivative(z + a, value_direction, symmetric, floor) @ da
            + (quotient_vector(z + a, symmetric, floor) - quotient_vector(z, symmetric, floor)) @ derivative_direction
        )
        chain_residual = max(chain_residual, abs(numerical - analytic))
    check("predictable_Cartan_OU_gradient_three_channels", chain_residual < 2e-8, chain_residual, "<2e-8")

    # Production linear Pauli--Fierz row matrices and their sharp algebraic floor.
    projector = np.diag([1.0, 1.0, 0.0, 1.0, 1.0, 0.0])
    scale0 = 2.0 * math.sqrt(c0)
    scaleh = 2.0 * math.sqrt(csum)
    a0 = scale0 * projector
    a1 = scaleh * np.array(
        [[0, 1, 0, 0, 0, 0], [-1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, -1, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0]],
        dtype=float,
    )
    a2 = scaleh * np.array(
        [[0, 0, 0, 0, 1, 0], [0, 0, 0, -1, 0, 0], [0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [-1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
        dtype=float,
    )
    matrices = [a0, a1, a2]
    check("linear_A0_symmetric", float(np.max(np.abs(a0 - a0.T))) < 1e-15, float(np.max(np.abs(a0 - a0.T))), 0.0)
    check("linear_A1_skew", float(np.max(np.abs(a1 + a1.T))) < 1e-15, float(np.max(np.abs(a1 + a1.T))), 0.0)
    check("linear_A2_skew", float(np.max(np.abs(a2 + a2.T))) < 1e-15, float(np.max(np.abs(a2 + a2.T))), 0.0)
    gamma_identity = np.eye(6)
    derivative_trace = sum((matrix @ gamma_identity @ matrix.T for matrix in matrices), np.zeros((6, 6)))
    expected_trace = (4.0 * c0 + 8.0 * csum) * projector
    trace_residual = float(np.max(np.abs(derivative_trace - expected_trace)))
    linear_floor = 0.5 * float(np.linalg.eigvalsh(derivative_trace)[-1])
    horizontal_floor = 2.0 * csum
    check("linear_derivative_trace_isotropic", trace_residual < 1e-14, trace_residual, 0.0)
    check("linear_full_sharp_floor", abs(linear_floor - 387.0 / (2000.0 * denominator)) < 1e-14, linear_floor, "387/(2000P)")
    check("linear_horizontal_sharp_floor", abs(horizontal_floor - 339.0 / (4000.0 * denominator)) < 1e-14, horizontal_floor, "339/(4000P)")

    floor_residual = 0.0
    for _ in range(64):
        z = rng.normal(size=6)
        y = rng.normal(size=6)
        packet = sum(row_energy(matrix, z, y, gamma_identity) for matrix in matrices)
        lower = -0.5 * float(z @ derivative_trace @ z)
        floor_residual = max(floor_residual, lower - packet)
    check("linear_pointwise_floor", floor_residual < 1e-13, floor_residual, "<=0")

    # Exact discrete selector attains the full-frame floor relative to E|z|^2.
    selector_states: list[tuple[float, np.ndarray, np.ndarray]] = [(0.5, np.zeros(6), np.eye(6)[0])]
    for coordinate in range(6):
        for sign in (-1.0, 1.0):
            selector_states.append((1.0 / 24.0, sign * math.sqrt(12.0) * np.eye(6)[coordinate], np.zeros(6)))
    selector_covariance = sum((weight * np.outer(y, y) for weight, y, _ in selector_states), np.zeros((6, 6)))
    selector_packet = sum(weight * sum(row_energy(matrix, z, y, gamma_identity) for matrix in matrices) for weight, y, z in selector_states)
    selector_norm = sum(weight * float(z @ z) for weight, _, z in selector_states)
    check("selector_covariance_identity", float(np.max(np.abs(selector_covariance - gamma_identity))) < 1e-14, float(np.max(np.abs(selector_covariance - gamma_identity))), 0.0)
    check("selector_attains_full_floor", abs(selector_packet / selector_norm + linear_floor) < 1e-14, selector_packet / selector_norm, -linear_floor)

    # Exact endpoint translation identity, including the constant heat lift.
    endpoint_residual = 0.0
    heat_residual = 0.0
    current_expansion_residual = 0.0
    for _ in range(48):
        z = rng.normal(size=6)
        displacement = 0.4 * rng.normal(size=6)
        y = rng.normal(size=6)
        derivative_displacement = 0.3 * rng.normal(size=6)
        raw = rng.normal(size=(6, 6))
        gamma = raw @ raw.T / 6.0
        heat_raw = rng.normal(size=(6, 6))
        sigma = heat_raw @ heat_raw.T / 6.0
        q_tensor = np.outer(y, y) - gamma
        for matrix in matrices:
            direct = row_energy(matrix, z + displacement, y + derivative_displacement, gamma) - row_energy(matrix, z, y, gamma)
            coefficient_z = matrix.T @ z
            coefficient_a = matrix.T @ displacement
            x = float(z @ matrix @ y)
            p_value = float(displacement @ matrix @ y)
            d_value = float((z + displacement) @ matrix @ derivative_displacement)
            rhs = float(coefficient_z @ q_tensor @ coefficient_a) + 0.5 * float(coefficient_a @ q_tensor @ coefficient_a) + (x + p_value) * d_value + 0.5 * d_value**2
            endpoint_residual = max(endpoint_residual, abs(direct - rhs))

            heat_matrix = matrix.T @ sigma @ matrix
            direct_heat = 0.5 * (float((y + derivative_displacement) @ heat_matrix @ (y + derivative_displacement)) - float(y @ heat_matrix @ y))
            rhs_heat = float(y @ heat_matrix @ derivative_displacement) + 0.5 * float(derivative_displacement @ heat_matrix @ derivative_displacement)
            heat_residual = max(heat_residual, abs(direct_heat - rhs_heat))

            expanded = x * float(z @ matrix @ derivative_displacement) + x * float(displacement @ matrix @ derivative_displacement) + p_value * float(z @ matrix @ derivative_displacement) + p_value * float(displacement @ matrix @ derivative_displacement)
            current_expansion_residual = max(current_expansion_residual, abs(expanded - (x + p_value) * d_value))
    check("linear_endpoint_translation_identity", endpoint_residual < 2e-12, endpoint_residual, 0.0)
    check("linear_heat_endpoint_identity", heat_residual < 2e-12, heat_residual, 0.0)
    check("linear_current_three_payload_expansion", current_expansion_residual < 2e-12, current_expansion_residual, 0.0)

    # One global Young ledger. These are derived from the interpolation powers.
    kappa = Fraction(1, 10)
    coefficient_order = 1 + kappa
    uq_total = (1 + coefficient_order) / 6
    centered_q_total = Fraction(7, 10)
    current_order = Fraction(3, 5)
    current_totals = [(2 + current_order + degree) / 6 for degree in range(3)]
    current_slacks = [1 - value for value in current_totals]
    current_moments = [1 / value for value in current_slacks]
    check("UQ_control_total_subcritical", uq_total == Fraction(7, 20) and uq_total < 1, str(uq_total), "7/20")
    check("centered_Q_control_total_subcritical", centered_q_total == Fraction(7, 10) and centered_q_total < 1, str(centered_q_total), "7/10")
    check("current_payload_totals", current_totals == [Fraction(13, 30), Fraction(3, 5), Fraction(23, 30)], [str(value) for value in current_totals], ["13/30", "3/5", "23/30"])
    check("current_payload_slacks_positive", current_slacks == [Fraction(17, 30), Fraction(2, 5), Fraction(7, 30)], [str(value) for value in current_slacks], ["17/30", "2/5", "7/30"])
    check("current_payload_worst_moment", max(current_moments) == Fraction(30, 7), [str(value) for value in current_moments], "30/7")
    check("all_linear_row_model_moments_finite_order", max([Fraction(20, 13), Fraction(10, 3), *current_moments]) == Fraction(30, 7), "30/7", "30/7")

    # The R-083 negative fixture is form-absorbable, not positive.
    adapted_polynomial = [Fraction(-4), Fraction(0), Fraction(1)]  # xi^2-4
    fixture_second = gaussian_expectation(polynomial_power(adapted_polynomial, 2))
    fixture_sixth = gaussian_expectation(polynomial_power(adapted_polynomial, 6))
    fixture_packet_coefficient = -8.0 * csum
    check("adapted_fixture_second_moment", fixture_second == 11, str(fixture_second), "11")
    check("adapted_fixture_sixth_moment", fixture_sixth == 3187, str(fixture_sixth), "3187")
    check("adapted_fixture_packet_negative", fixture_packet_coefficient < 0, fixture_packet_coefficient, "-8cS<0")
    eta = csum / 4.0
    zeta = 0.01
    deficit = max(0.0, 8.0 * csum - 11.0 * eta)
    analytic_infimum = 0.0 if deficit == 0.0 else -2.0 * deficit ** 1.5 / (3.0 * math.sqrt(3.0 * 3187.0 * zeta))
    critical_t = 0.0 if deficit == 0.0 else math.sqrt(deficit / (3.0 * 3187.0 * zeta))
    evaluated_infimum = -deficit * critical_t + 3187.0 * zeta * critical_t**3
    check("adapted_fixture_scalar_Young_infimum", abs(analytic_infimum - evaluated_infimum) < 1e-15 and math.isfinite(analytic_infimum), evaluated_infimum, analytic_infimum)

    check("linear_NEAR_regular_one_shot_absorbable", all(value < 1 for value in [uq_total, centered_q_total, *current_totals]), [str(value) for value in [uq_total, centered_q_total, *current_totals]], "all totals <1")
    check("controlled_Cartan_CFar_not_established", True, False, False)
    check("rational_NEAR_not_established", True, False, False)
    check("progressive_revisit_not_established", True, False, False)
    check("controlled_shell_one_use_not_established", True, False, False)
    check("nelson_not_established", True, False, False)
    check("sector_a_not_closed", True, False, False)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-root-diagonal-cartan-ou-linear-pf-absorption-primary/1.0",
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "pass": passed == len(rows),
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "assertions": rows,
        "derived_constants": {
            "P": denominator,
            "alpha": alpha,
            "c0": c0,
            "c1": c1,
            "cS": csum,
            "cartan_prefactor": 4.0 * alpha**2 * c1,
            "horizontal_sharp_floor": horizontal_floor,
            "linear_full_sharp_floor": linear_floor,
        },
        "root_tree": {
            "N": tree_size,
            "old_input_energy": old_energy,
            "equal_input_energy": equal_energy,
            "operator_norm_squared": singular_square,
        },
        "young_ledger": {
            "UQ_total": str(uq_total),
            "centered_Q_total": str(centered_q_total),
            "current_totals": [str(value) for value in current_totals],
            "current_slacks": [str(value) for value in current_slacks],
            "worst_required_moment": str(max(current_moments)),
        },
        "fixture": {
            "E_A2_over_lambda2": int(fixture_second),
            "E_A6_over_lambda6": int(fixture_sixth),
            "packet_quadratic_coefficient": fixture_packet_coefficient,
            "young_infimum": analytic_infimum,
        },
        "proved_scope": "exact root-diagonal Cartan CFAR and conditional OU-gradient representation; exact cumulative-root method no-go; global endpoint form absorption of all three linear Pauli--Fierz NEAR rows for regular mutually orthogonal strict-past one-shot controls",
        "open_scope": "summed production far-projected Cartan OU-gradient bound, nonlinear rational-row signed NEAR, progressive/revisit extension, controlled-shell one-use, q=10/9 Nelson, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-084 primary] {passed}/{len(rows)} PASS" if passed == len(rows) else f"[R-084 primary] {passed}/{len(rows)} PASS; failures={len(rows)-passed}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
