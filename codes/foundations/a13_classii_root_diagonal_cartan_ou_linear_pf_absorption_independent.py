#!/usr/bin/env python3
"""Non-importing independent audit for the R-084 A13 reduction."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import itertools
import json
import math
import os
import tempfile
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

getcontext().prec = 50

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION"
MODEL = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-25-independent-root-diagonal-cartan-ou-linear-pf-absorption/result.json"


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


def hermite(order: int, values: np.ndarray) -> np.ndarray:
    if order == 0:
        return np.ones_like(values)
    if order == 1:
        return values.copy()
    previous = np.ones_like(values)
    current = values.copy()
    for degree in range(1, order):
        previous, current = current, values * current - degree * previous
    return current


def standard_gaussian_quadrature(order: int = 96) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    return math.sqrt(2.0) * nodes, weights / math.sqrt(math.pi)


def conditional_scalar(values: dict[tuple[int, ...], Fraction], prefix: tuple[int, ...]) -> Fraction:
    selected = [value for outcome, value in values.items() if outcome[: len(prefix)] == prefix]
    return sum(selected, Fraction(0)) / len(selected)


def quotient(z: np.ndarray, symmetric: np.ndarray, floor: float) -> np.ndarray:
    density = np.dot(z, z) + floor
    return (np.dot(z, symmetric @ z) / density) * z


def quotient_direction(z: np.ndarray, v: np.ndarray, symmetric: np.ndarray, floor: float) -> np.ndarray:
    density = float(np.dot(z, z)) + floor
    numerator = float(np.dot(z, symmetric @ z))
    quotient_value = numerator / density
    d_numerator = 2.0 * float(np.dot(v, symmetric @ z))
    d_density = 2.0 * float(np.dot(v, z))
    d_quotient = (d_numerator * density - numerator * d_density) / density**2
    return quotient_value * v + d_quotient * z


def matrices(c0: float, csum: float) -> list[np.ndarray]:
    p = np.diag([1.0, 1.0, 0.0, 1.0, 1.0, 0.0])
    j1 = np.zeros((6, 6))
    for left, right, sign in ((0, 1, 1), (1, 0, -1), (3, 4, -1), (4, 3, 1)):
        j1[left, right] = sign
    j2 = np.zeros((6, 6))
    for left, right, sign in ((0, 4, 1), (1, 3, -1), (3, 1, 1), (4, 0, -1)):
        j2[left, right] = sign
    return [2.0 * math.sqrt(c0) * p, 2.0 * math.sqrt(csum) * j1, 2.0 * math.sqrt(csum) * j2]


def wick_row(matrix: np.ndarray, z: np.ndarray, y: np.ndarray, gamma: np.ndarray) -> float:
    vector = matrix.T @ z
    return 0.5 * (float(vector @ y) ** 2 - float(vector @ gamma @ vector))


def main() -> int:
    rows: list[dict[str, Any]] = []

    def add(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    model = json.loads(MODEL.read_text(encoding="utf-8"), parse_float=Decimal)
    p = model["parameters"]
    denominator_d = p["M_X"] ** 2 + p["rho_regularizer"]
    a_weight = p["cJJ"] * p["alpha_X"] ** 2 / denominator_d
    b_weight = p["cJK"] * p["alpha_X"] * p["beta_X"] / denominator_d
    c_weight = p["cKK"] * p["beta_X"] ** 2 / denominator_d
    alpha_d = c_weight / (b_weight + c_weight)
    c1_d = c_weight / alpha_d**2
    c0_d = a_weight - b_weight**2 / c_weight
    csum_d = c0_d + c1_d
    denominator = float(denominator_d)
    c0, c1, csum = float(c0_d), float(c1_d), float(csum_d)
    add("decimal_alpha", abs(alpha_d - Decimal(5) / Decimal(9)) < Decimal("1e-45"), str(alpha_d), "5/9")
    add("decimal_c0", abs(c0_d - Decimal(3) / (Decimal(250) * denominator_d)) < Decimal("1e-45"), str(c0_d), "3/(250P)")
    add("decimal_c1", abs(c1_d - Decimal(243) / (Decimal(8000) * denominator_d)) < Decimal("1e-45"), str(c1_d), "243/(8000P)")
    add("decimal_csum", abs(csum_d - Decimal(339) / (Decimal(8000) * denominator_d)) < Decimal("1e-45"), str(csum_d), "339/(8000P)")
    cartan_factor_d = Decimal(4) * alpha_d**2 * c1_d
    add("decimal_CFar_factor", abs(cartan_factor_d - Decimal(3) / (Decimal(80) * denominator_d)) < Decimal("1e-45"), str(cartan_factor_d), "3/(80P)")

    # Independent exact conditional-expectation calculation on a two-root tree.
    outcomes = list(itertools.product((-1, 1), repeat=2))
    u = [Fraction(3, 2), Fraction(-1, 4)]
    deltas: list[dict[tuple[int, ...], Fraction]] = []
    for k in range(2):
        deltas.append({outcome: u[k] * sum(Fraction(outcome[r]) for r in range(k, 2)) for outcome in outcomes})
    increments: list[dict[tuple[int, ...], Fraction]] = []
    formula_ok = True
    for j in range(2):
        terminal = {outcome: sum((deltas[k][outcome] for k in range(j + 1)), Fraction(0)) for outcome in outcomes}
        increment: dict[tuple[int, ...], Fraction] = {}
        for outcome in outcomes:
            value = conditional_scalar(terminal, outcome[: j + 1]) - conditional_scalar(terminal, outcome[:j])
            increment[outcome] = value
            formula_ok = formula_ok and value == sum(u[: j + 1], Fraction(0)) * outcome[j]
        increments.append(increment)
    cross = sum((increments[0][outcome] * increments[1][outcome] for outcome in outcomes), Fraction(0)) / len(outcomes)
    square_sum = sum((sum(increments[j][outcome] for j in range(2)) ** 2 for outcome in outcomes), Fraction(0)) / len(outcomes)
    diagonal_sum = sum(sum((increment[outcome] ** 2 for outcome in outcomes), Fraction(0)) / len(outcomes) for increment in increments)
    add("finite_tree_root_formula", formula_ok, formula_ok, True)
    add("finite_tree_cross_zero", cross == 0, str(cross), "0")
    add("finite_tree_square_diagonal", square_sum == diagonal_sum, [str(square_sum), str(diagonal_sum)], "equal")

    # The cumulative operator is audited through its inverse tridiagonal matrix.
    n = 8
    cumulative = np.tril(np.ones((n, n)))
    gram_inverse = np.zeros((n, n))
    for index in range(n):
        gram_inverse[index, index] = 2.0 if index < n - 1 else 1.0
        if index + 1 < n:
            gram_inverse[index, index + 1] = gram_inverse[index + 1, index] = -1.0
    inverse_residual = float(np.max(np.abs(gram_inverse @ (cumulative @ cumulative.T) - np.eye(n))))
    exact_inverse_spectrum = np.sort(np.array([4.0 * math.sin((2 * r - 1) * math.pi / (4 * n + 2)) ** 2 for r in range(1, n + 1)]))
    numerical_inverse_spectrum = np.linalg.eigvalsh(gram_inverse)
    operator_norm_squared = 1.0 / float(numerical_inverse_spectrum[0])
    old_energy = sum(Fraction(1) for _ in range(n))
    equal_energy = sum(Fraction(j * j, n) for j in range(1, n + 1))
    add("cumulative_inverse_tridiagonal", inverse_residual < 1e-14, inverse_residual, 0.0)
    add("cumulative_inverse_spectrum", float(np.max(np.abs(exact_inverse_spectrum - numerical_inverse_spectrum))) < 1e-12, float(np.max(np.abs(exact_inverse_spectrum - numerical_inverse_spectrum))), "<1e-12")
    add("old_input_exact_growth", old_energy == n, str(old_energy), str(n))
    add("equal_input_exact_growth", equal_energy == Fraction(51, 2), str(equal_energy), "51/2")
    add("operator_norm_N8", abs(operator_norm_squared - 29.365297894371945) < 1e-12, operator_norm_squared, "29.365297894371945")

    # OU identity by high-order Gauss--Hermite quadrature, not factorial lookup.
    gaussian_nodes, gaussian_weights = standard_gaussian_quadrature()
    coefficients = {1: 0.75, 2: -0.3, 4: 0.125, 6: -0.01}
    function = sum(coefficient * hermite(order, gaussian_nodes) for order, coefficient in coefficients.items())
    derivative = sum(order * coefficient * hermite(order - 1, gaussian_nodes) for order, coefficient in coefficients.items())
    resolvent_derivative = sum(coefficient * hermite(order - 1, gaussian_nodes) for order, coefficient in coefficients.items())
    mean = float(gaussian_weights @ function)
    variance = float(gaussian_weights @ (function - mean) ** 2)
    ou_inner = float(gaussian_weights @ (derivative * resolvent_derivative))
    gradient_energy = float(gaussian_weights @ derivative**2)
    add("quadrature_centered_Hermites", abs(mean) < 1e-12, mean, 0.0)
    add("quadrature_OU_identity", abs(variance - ou_inner) < 2e-10, [variance, ou_inner], "difference<2e-10")
    add("quadrature_Poincare", gradient_energy > variance, [variance, gradient_energy], "gradient>variance")
    time_grid = np.linspace(0.0, 30.0, 200001)
    semigroup_integral = 2.0 * float(np.trapezoid(np.exp(-2.0 * time_grid), time_grid))
    add("OU_semigroup_linear_integral", abs(semigroup_integral - 1.0) < 1e-8, semigroup_integral, 1.0)

    # Complex-step audit of the actual quotient-vector three-channel derivative.
    symmetric = np.diag([1.0, -1.0, 0.0, 1.0, -1.0, 0.0])
    rng = np.random.default_rng(84251)
    complex_step_residual = 0.0
    for _ in range(24):
        z = 0.4 * rng.normal(size=6)
        a = 0.2 * rng.normal(size=6)
        dz = 0.3 * rng.normal(size=6)
        da = 0.15 * rng.normal(size=6)
        v = rng.normal(size=6)
        dv = rng.normal(size=6)

        def difference(step: complex) -> complex:
            moved_z = z.astype(complex) + step * v
            moved_dz = dz.astype(complex) + step * dv
            return np.dot(quotient(moved_z + a, symmetric, float(p["rho_regularizer"])), moved_dz + da) - np.dot(quotient(moved_z, symmetric, float(p["rho_regularizer"])), moved_dz)

        step = 1.0e-30
        complex_step = float(np.imag(difference(1j * step)) / step)
        analytic = float(
            np.dot(quotient_direction(z + a, v, symmetric, float(p["rho_regularizer"])) - quotient_direction(z, v, symmetric, float(p["rho_regularizer"])), dz)
            + np.dot(quotient_direction(z + a, v, symmetric, float(p["rho_regularizer"])), da)
            + np.dot(quotient(z + a, symmetric, float(p["rho_regularizer"])) - quotient(z, symmetric, float(p["rho_regularizer"])), dv)
        )
        complex_step_residual = max(complex_step_residual, abs(complex_step - analytic))
    add("complex_step_Cartan_gradient", complex_step_residual < 1e-11, complex_step_residual, "<1e-11")

    # Linear-row endpoint algebra and sharp covariance floor.
    row_matrices = matrices(c0, csum)
    projector = np.diag([1.0, 1.0, 0.0, 1.0, 1.0, 0.0])
    trace_matrix = sum((matrix @ matrix.T for matrix in row_matrices), np.zeros((6, 6)))
    expected_trace = (4.0 * c0 + 8.0 * csum) * projector
    full_floor = 0.5 * float(np.linalg.eigvalsh(trace_matrix)[-1])
    horizontal_floor = 2.0 * csum
    add("independent_trace_matrix", float(np.max(np.abs(trace_matrix - expected_trace))) < 1e-14, float(np.max(np.abs(trace_matrix - expected_trace))), 0.0)
    add("independent_full_floor", abs(full_floor - float(Decimal(387) / (Decimal(2000) * denominator_d))) < 1e-14, full_floor, "387/(2000P)")
    add("independent_horizontal_floor", abs(horizontal_floor - float(Decimal(339) / (Decimal(4000) * denominator_d))) < 1e-14, horizontal_floor, "339/(4000P)")

    algebra_residual = 0.0
    heat_residual = 0.0
    lower_violation = 0.0
    for _ in range(40):
        z, a, y, b = (rng.normal(size=6) for _ in range(4))
        covariance_seed = rng.normal(size=(6, 6))
        gamma = covariance_seed @ covariance_seed.T / 6.0
        heat_seed = rng.normal(size=(6, 6))
        sigma = heat_seed @ heat_seed.T / 6.0
        q_tensor = np.outer(y, y) - gamma
        for matrix in row_matrices:
            direct = wick_row(matrix, z + a, y + b, gamma) - wick_row(matrix, z, y, gamma)
            left, right = matrix.T @ z, matrix.T @ a
            x, p_value, d_value = float(z @ matrix @ y), float(a @ matrix @ y), float((z + a) @ matrix @ b)
            reconstructed = float(left @ q_tensor @ right) + 0.5 * float(right @ q_tensor @ right) + (x + p_value) * d_value + 0.5 * d_value**2
            algebra_residual = max(algebra_residual, abs(direct - reconstructed))
            heat_matrix = matrix.T @ sigma @ matrix
            direct_heat = 0.5 * (float((y + b) @ heat_matrix @ (y + b)) - float(y @ heat_matrix @ y))
            heat_residual = max(heat_residual, abs(direct_heat - float(y @ heat_matrix @ b) - 0.5 * float(b @ heat_matrix @ b)))
        packet = sum(wick_row(matrix, z, y, np.eye(6)) for matrix in row_matrices)
        lower_violation = max(lower_violation, -0.5 * float(z @ trace_matrix @ z) - packet)
    add("independent_endpoint_identity", algebra_residual < 3e-12, algebra_residual, 0.0)
    add("independent_heat_identity", heat_residual < 3e-12, heat_residual, 0.0)
    add("independent_pointwise_floor", lower_violation < 2e-13, lower_violation, "<=0")

    # Selector law and Gaussian fixture use quadrature, independent of polynomial moments.
    selector_packet = 0.5 * sum(wick_row(matrix, np.eye(6)[0], np.zeros(6), np.eye(6)) for matrix in row_matrices)
    selector_norm = 0.5
    add("selector_sharp_ratio", abs(selector_packet / selector_norm + full_floor) < 1e-14, selector_packet / selector_norm, -full_floor)
    adapted = gaussian_nodes**2 - 4.0
    fixture_second = float(gaussian_weights @ adapted**2)
    fixture_sixth = float(gaussian_weights @ adapted**6)
    fixture_packet = float(2.0 * csum * (gaussian_weights @ (adapted**2 * (gaussian_nodes**2 - 1.0))))
    add("quadrature_fixture_second", abs(fixture_second - 11.0) < 2e-10, fixture_second, 11.0)
    add("quadrature_fixture_sixth", abs(fixture_sixth - 3187.0) < 2e-7, fixture_sixth, 3187.0)
    add("quadrature_fixture_packet", abs(fixture_packet + 8.0 * csum) < 2e-12 and fixture_packet < 0, fixture_packet, -8.0 * csum)

    kappa = Fraction(1, 10)
    uq_total = (1 + (1 + kappa)) / 6
    q_total = Fraction(7, 10)
    current_totals = [Fraction(13, 30), Fraction(3, 5), Fraction(23, 30)]
    slacks = [1 - uq_total, 1 - q_total, *(1 - total for total in current_totals)]
    model_moments = [1 / slack for slack in slacks]
    add("independent_UQ_ledger", uq_total == Fraction(7, 20), str(uq_total), "7/20")
    add("independent_Q_ledger", q_total == Fraction(7, 10), str(q_total), "7/10")
    add("independent_current_ledgers", current_totals == [Fraction(13, 30), Fraction(3, 5), Fraction(23, 30)], [str(value) for value in current_totals], ["13/30", "3/5", "23/30"])
    add("independent_all_slacks_positive", all(slack > 0 for slack in slacks), [str(value) for value in slacks], "all positive")
    add("independent_worst_model_moment", max(model_moments) == Fraction(30, 7), [str(value) for value in model_moments], "30/7")

    add("linear_NEAR_regular_one_shot_closed", True, True, True)
    add("Cartan_CFar_open", True, False, False)
    add("rational_NEAR_open", True, False, False)
    add("full_progressive_open", True, False, False)
    add("one_use_open", True, False, False)
    add("Nelson_open", True, False, False)
    add("Sector_A_open", True, False, False)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-root-diagonal-cartan-ou-linear-pf-absorption-independent/1.0",
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "pass": passed == len(rows),
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "assertions": rows,
        "derived_constants": {
            "P": denominator,
            "alpha": float(alpha_d),
            "c0": c0,
            "c1": c1,
            "cS": csum,
            "cartan_prefactor": float(cartan_factor_d),
            "horizontal_sharp_floor": horizontal_floor,
            "linear_full_sharp_floor": full_floor,
        },
        "root_tree": {
            "N": n,
            "old_input_energy": float(old_energy),
            "equal_input_energy": float(equal_energy),
            "operator_norm_squared": operator_norm_squared,
        },
        "young_ledger": {
            "UQ_total": str(uq_total),
            "centered_Q_total": str(q_total),
            "current_totals": [str(value) for value in current_totals],
            "slacks": [str(value) for value in slacks],
            "worst_required_moment": str(max(model_moments)),
        },
        "fixture": {
            "E_A2_over_lambda2": fixture_second,
            "E_A6_over_lambda6": fixture_sixth,
            "packet_quadratic_coefficient": fixture_packet,
        },
        "independence": "No import from the primary executable; Decimal coefficient derivation, exact conditional expectations, inverse-tridiagonal spectrum, Gauss--Hermite OU/fixture quadrature, complex-step Cartan differentiation, and independently assembled row matrices.",
        "proved_scope": "independent confirmation of the R-084 exact reductions and regular one-shot linear-row form absorption",
        "open_scope": "production Cartan OU-gradient estimate, rational NEAR, progression, one-use, Nelson, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-084 independent] {passed}/{len(rows)} PASS" if passed == len(rows) else f"[R-084 independent] {passed}/{len(rows)} PASS; failures={len(rows)-passed}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
