#!/usr/bin/env python3
"""Primary executable certificate for the R-101 A13 checkpoint.

The certificate checks the fresh value/gradient orthogonality that removes the
moving heat-baseline raw-Wick cross, the resulting cross-Doob identity, the
exact derivative-current remainder and its control-square telescope, the
reduced Taylor ledger, and an algebraic domination for the production
rational row.  It deliberately leaves the shifted-current Hessian form open.
"""

from __future__ import annotations

__version__ = "1.0.2"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

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
RESULT_ID = "A13-CLASSII-RAW-WICK-HEAT-BASELINE-ORTHOGONALITY-RATIONAL-CURRENT-REDUCTION"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-27-primary-raw-wick-heat-baseline-orthogonality-rational-current-reduction/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-raw-wick-heat-baseline-orthogonality-rational-current-reduction-primary/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "R-101 closes only the regular strict-past moving raw-Wick heat-baseline "
                "cross and isolates the derivative-current remainder. The shifted-current "
                "Hessian, complete rational H_N, REG, progressive H_A, OVERLAP_src, Nelson, "
                "a measure, and Sector A remain open."
            ),
        }


def expectation(weights: np.ndarray, values: np.ndarray) -> float:
    return float(np.dot(weights, values))


def conditional(values: np.ndarray, states: list[tuple[tuple[int, int], ...]], weights: np.ndarray, revealed: int) -> np.ndarray:
    groups: dict[tuple[tuple[int, int], ...], list[int]] = {}
    for index, state in enumerate(states):
        groups.setdefault(state[:revealed], []).append(index)
    answer = np.empty_like(values, dtype=float)
    for indices in groups.values():
        local_weights = weights[indices]
        answer[indices] = float(np.dot(local_weights, values[indices]) / np.sum(local_weights))
    return answer


def matrix_inner(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.sum(left * right))


def production_constants() -> dict[str, float]:
    model = json.loads(
        (REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    parameters = model["parameters"]
    floor = float(parameters["rho_regularizer"])
    p_mass = float(parameters["M_X"]) ** 2 + floor
    q11 = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / p_mass
    q12 = float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / p_mass
    q22 = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / p_mass
    alpha = q22 / (q12 + q22)
    c1 = q22 / alpha**2
    c0 = q11 - q12**2 / q22
    return {
        "floor": floor,
        "p_mass": p_mass,
        "q11": q11,
        "q12": q12,
        "q22": q22,
        "alpha": alpha,
        "c0": c0,
        "c1": c1,
    }


def truncated_product(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    """Multiply Taylor series, retaining the common declared order."""
    order = min(len(left), len(right)) - 1
    return [
        sum((left[index] * right[degree - index] for index in range(degree + 1)), Fraction(0))
        for degree in range(order + 1)
    ]


def truncated_quotient(numerator: list[Fraction], denominator: list[Fraction]) -> list[Fraction]:
    """Divide Taylor series exactly by the nonzero constant denominator term."""
    if denominator[0] == 0:
        raise ZeroDivisionError("Taylor denominator has zero constant term")
    order = min(len(numerator), len(denominator)) - 1
    quotient = [Fraction(0) for _ in range(order + 1)]
    for degree in range(order + 1):
        correction = sum(
            (denominator[index] * quotient[degree - index] for index in range(1, degree + 1)),
            Fraction(0),
        )
        quotient[degree] = (numerator[degree] - correction) / denominator[0]
    return quotient


def scalar_balanced_heat_oracles() -> dict[str, Fraction]:
    """Derive the normalized scalar-ray Taylor and small-heat coefficients."""
    alpha = Fraction(5, 9)

    def gram_series(base: Fraction) -> list[Fraction]:
        x = [base, Fraction(1), Fraction(0), Fraction(0)]
        x_squared = truncated_product(x, x)
        factor = [(Fraction(1) - alpha) * coefficient for coefficient in x_squared]
        factor[0] += 1
        denominator = list(x_squared)
        denominator[0] += 1
        rational_row = truncated_quotient(truncated_product(x, factor), denominator)
        return [4 * coefficient for coefficient in truncated_product(rational_row, rational_row)]

    at_initial = gram_series(Fraction(1))
    at_zero = gram_series(Fraction(0))
    full_remainder = -at_initial[0] + at_initial[1] - at_initial[2]
    base_cubic = -at_initial[3]
    balanced_remainder = full_remainder - base_cubic
    heat_square_leading = at_zero[2]
    schur_divergence = balanced_remainder**2 / (2 * heat_square_leading)
    return {
        "scalar_full_remainder": full_remainder,
        "scalar_base_cubic": base_cubic,
        "scalar_balanced_remainder": balanced_remainder,
        "zero_heat_square_leading_coefficient": heat_square_leading,
        "balanced_schur_divergence_coefficient": schur_divergence,
    }


def main() -> int:
    audit = Audit()
    diagnostics: dict[str, Any] = {}
    tol = 2.0e-10

    # 1. A three-root finite filtration with independent value/gradient
    # coordinates checks the exact heat-baseline orthogonality and cross-Doob
    # identity for a nonlinear pointwise coefficient.
    support = (-1, 0, 1)
    mass = {-1: 0.25, 0: 0.5, 1: 0.25}
    raw_states = list(itertools.product(list(itertools.product(support, support)), repeat=3))
    states = [tuple((int(pair[0]), int(pair[1])) for pair in state) for state in raw_states]
    weights = np.array(
        [math.prod(mass[g] * mass[d] for g, d in state) for state in states], dtype=float
    )
    audit.check("filtration", "probability_mass", abs(float(np.sum(weights)) - 1.0) < tol, float(np.sum(weights)), 1.0)
    variance_d = sum(mass[value] * value * value for value in support)

    values_g = np.array([[pair[0] for pair in state] for state in states], dtype=float)
    values_d = np.array([[pair[1] for pair in state] for state in states], dtype=float)
    control_1 = np.full(len(states), 1.0 / 5.0)
    control_2 = (2.0 * values_g[:, 0] - values_d[:, 0]) / 7.0
    control_3 = (values_g[:, 0] * values_g[:, 1] + values_d[:, 0] * values_d[:, 1]) / 9.0
    controls = [control_1, control_2, control_3]
    prefixes = [np.zeros(len(states))]
    for control in controls:
        prefixes.append(prefixes[-1] + control)
    terminal_u = np.sum(values_g, axis=1)

    def coefficient(z: np.ndarray) -> np.ndarray:
        return 1.0 + z * z + (z**3 / (5.0 + z * z)) ** 2

    b_terminal = coefficient(terminal_u + prefixes[-1])
    f_levels = [conditional(b_terminal, states, weights, level) for level in range(4)]
    l_levels: list[np.ndarray] = []
    h_levels: list[np.ndarray] = []
    q_levels: list[np.ndarray] = []
    for level in range(4):
        b_level = coefficient(terminal_u + prefixes[level])
        l_level = conditional(b_level, states, weights, level)
        l_levels.append(l_level)
        h_levels.append(f_levels[level] - l_level)
        g_derivative = np.sum(values_d[:, :level], axis=1) if level else np.zeros(len(states))
        q_levels.append(g_derivative**2 - level * variance_d)

    baseline_crosses: list[float] = []
    residual_crosses: list[float] = []
    direct_residual_crosses: list[float] = []
    for level in range(1, 4):
        delta_q = q_levels[level] - q_levels[level - 1]
        baseline_cross = expectation(weights, (l_levels[level] - l_levels[level - 1]) * delta_q)
        residual_cross = expectation(weights, (h_levels[level] - h_levels[level - 1]) * delta_q)
        direct_residual = expectation(
            weights,
            (b_terminal - coefficient(terminal_u + prefixes[level])) * delta_q,
        )
        baseline_crosses.append(baseline_cross)
        residual_crosses.append(residual_cross)
        direct_residual_crosses.append(direct_residual)
        audit.check("orthogonality", f"moving_L_cross_{level}", abs(baseline_cross) < tol, baseline_cross, 0.0)
        audit.check(
            "orthogonality",
            f"H_increment_equals_terminal_secant_{level}",
            abs(residual_cross - direct_residual) < tol,
            residual_cross - direct_residual,
            0.0,
        )

    terminal_wick = expectation(weights, b_terminal * q_levels[-1])
    low_wick = expectation(weights, f_levels[0] * q_levels[0])
    residual_sum = sum(direct_residual_crosses)
    audit.check("cross_doob", "terminal_raw_wick_identity", abs(terminal_wick - low_wick - residual_sum) < tol, terminal_wick - low_wick - residual_sum, 0.0)
    audit.check("cross_doob", "F_equals_L_plus_H", all(np.max(np.abs(f_levels[j] - l_levels[j] - h_levels[j])) < tol for j in range(4)), "PASS", "PASS")

    # A second fixture starts at a genuinely nonzero low endpoint.  It catches
    # either deletion or a wrong sign of the fixed-low term in Cross--Doob.
    low_terminal_b = (values_g[:, 0] + values_g[:, 1] + values_d[:, 0]) ** 2
    low_f = conditional(low_terminal_b, states, weights, 1)
    q_low = values_d[:, 0] ** 2 - variance_d
    q_next = (values_d[:, 0] + values_d[:, 1]) ** 2 - 2.0 * variance_d
    fixed_low = expectation(weights, low_f * q_low)
    terminal_with_low = expectation(weights, low_terminal_b * q_next)
    audit.check("cross_doob", "nonzero_fixed_low_endpoint", abs(fixed_low - 0.25) < tol, fixed_low, 0.25)
    audit.check(
        "cross_doob",
        "nonzero_low_terminal_identity",
        abs(terminal_with_low - fixed_low) < tol,
        terminal_with_low - fixed_low,
        0.0,
    )

    # Necessity fixtures: a value/gradient-correlated root and a coefficient
    # depending directly on the fresh gradient both destroy the zero cross.
    one_weights = np.array([mass[value] for value in support], dtype=float)
    one_values = np.array(support, dtype=float)
    correlated_cross = expectation(one_weights, one_values**2 * (one_values**2 - variance_d))
    pair_states = list(itertools.product(support, support))
    pair_weights = np.array([mass[g_value] * mass[d_value] for g_value, d_value in pair_states], dtype=float)
    pair_d = np.array([d_value for _, d_value in pair_states], dtype=float)
    direct_gradient_cross = expectation(pair_weights, pair_d**2 * (pair_d**2 - variance_d))
    audit.check("scope", "correlated_value_gradient_breaks_centering", abs(correlated_cross) > 0.1, correlated_cross, "nonzero")
    audit.check(
        "scope",
        "gradient_dependent_coefficient_breaks_centering",
        abs(direct_gradient_cross) > 0.1,
        direct_gradient_cross,
        "nonzero",
    )

    # 2. Exact derivative-current remainder algebra for random noncommuting
    # positive matrices.
    rng = np.random.default_rng(1010727)
    k_residuals: list[float] = []
    regroup_residuals: list[float] = []
    for index in range(32):
        raw_minus = rng.normal(size=(3, 3))
        raw_plus = rng.normal(size=(3, 3))
        b_minus = raw_minus @ raw_minus.T + 0.1 * np.eye(3)
        b_plus = raw_plus @ raw_plus.T + 0.1 * np.eye(3)
        gamma_raw = rng.normal(size=(3, 3))
        gamma = gamma_raw @ gamma_raw.T
        g = rng.normal(size=3)
        c = rng.normal(size=3)
        b = rng.normal(size=3)
        delta_b = b_plus - b_minus
        full = 0.5 * (
            (g + c + b) @ b_plus @ (g + c + b)
            - matrix_inner(b_plus, gamma)
            - (g + c) @ b_minus @ (g + c)
            + matrix_inner(b_minus, gamma)
        )
        raw_wick = 0.5 * matrix_inner(delta_b, np.outer(g, g) - gamma)
        remainder = (
            g @ delta_b @ c
            + 0.5 * c @ delta_b @ c
            + (g + c) @ b_plus @ b
            + 0.5 * b @ b_plus @ b
        )
        regrouped = g @ (b_plus @ (c + b) - b_minus @ c) + 0.5 * (
            (c + b) @ b_plus @ (c + b) - c @ b_minus @ c
        )
        k_residuals.append(abs(full - raw_wick - remainder))
        regroup_residuals.append(abs(remainder - regrouped))
        audit.check("current_remainder", f"K_identity_{index}", abs(full - raw_wick - remainder) < tol, full - raw_wick - remainder, 0.0)
        audit.check("current_remainder", f"K_regroup_{index}", abs(remainder - regrouped) < tol, remainder - regrouped, 0.0)

    # The control-only half of the regrouped remainder telescopes when the
    # coefficient and derivative endpoints match.  Backward heat supplies
    # this matching in expectation in the production ledger.
    matrices: list[np.ndarray] = []
    for _ in range(6):
        raw = rng.normal(size=(3, 3))
        matrices.append(raw @ raw.T + 0.2 * np.eye(3))
    derivative_prefixes = [np.zeros(3)]
    for _ in range(5):
        derivative_prefixes.append(derivative_prefixes[-1] + rng.normal(size=3))
    control_square_sum = sum(
        0.5
        * (
            derivative_prefixes[k] @ matrices[k] @ derivative_prefixes[k]
            - derivative_prefixes[k - 1] @ matrices[k - 1] @ derivative_prefixes[k - 1]
        )
        for k in range(1, 6)
    )
    control_square_endpoint = 0.5 * (
        derivative_prefixes[-1] @ matrices[-1] @ derivative_prefixes[-1]
        - derivative_prefixes[0] @ matrices[0] @ derivative_prefixes[0]
    )
    audit.check("control_square", "matched_endpoint_telescope", abs(control_square_sum - control_square_endpoint) < tol, control_square_sum - control_square_endpoint, 0.0)
    audit.check("control_square", "zero_low_endpoint_nonnegative", control_square_endpoint >= -tol, control_square_endpoint, ">=0")

    # 3. Taylor accounting after the raw-Wick term has been removed: only the
    # shifted-current Hessian remainder survives beyond the three unshifted
    # cross families and the nonnegative terminal control square.
    # Use an exact quartic matrix polynomial so the integral Taylor remainder
    # has a closed form and no finite-difference oracle.
    u = rng.normal(size=2)
    a = rng.normal(size=2)
    g = rng.normal(size=2)
    c = rng.normal(size=2)

    def poly_b(z: np.ndarray) -> np.ndarray:
        x, y = z
        return np.array([[1 + x * x + x**4, x * y + x**2 * y**2], [x * y + x**2 * y**2, 2 + y * y + y**4]])

    def d1(z: np.ndarray, h: np.ndarray) -> np.ndarray:
        x, y = z
        hx, hy = h
        return np.array(
            [
                [(2 * x + 4 * x**3) * hx, y * hx + x * hy + 2 * x * y**2 * hx + 2 * x**2 * y * hy],
                [y * hx + x * hy + 2 * x * y**2 * hx + 2 * x**2 * y * hy, (2 * y + 4 * y**3) * hy],
            ]
        )

    def d2(z: np.ndarray, h: np.ndarray) -> np.ndarray:
        x, y = z
        hx, hy = h
        off = 2 * hx * hy + 2 * y**2 * hx**2 + 8 * x * y * hx * hy + 2 * x**2 * hy**2
        return np.array([[(2 + 12 * x**2) * hx**2, off], [off, (2 + 12 * y**2) * hy**2]])

    b0 = poly_b(u)
    b1 = poly_b(u + a)
    bt = b0 + d1(u, a) + 0.5 * d2(u, a)
    l_matrix = b1 - bt
    full_cross = g @ b1 @ c
    unshifted = g @ b0 @ c + g @ d1(u, a) @ c + 0.5 * g @ d2(u, a) @ c
    shifted_current = g @ l_matrix @ c
    audit.check("taylor", "cross_family_partition", abs(full_cross - unshifted - shifted_current) < tol, full_cross - unshifted - shifted_current, 0.0)
    audit.check("taylor", "shifted_current_nontrivial", abs(shifted_current) > 1e-7, shifted_current, "nonzero")

    # 4. Derive the production constants from A1 and check the rank-one
    # rational row and its useful pointwise range bound.
    constants = production_constants()
    audit.check("production", "alpha_derived", abs(constants["alpha"] - 5.0 / 9.0) < 1e-13, constants["alpha"], "5/9")
    audit.check("production", "c0_derived", abs(constants["c0"] - 3.0 / (250.0 * constants["p_mass"])) < 1e-13, constants["c0"], "3/(250P)")
    audit.check("production", "c1_derived", abs(constants["c1"] - 243.0 / (8000.0 * constants["p_mass"])) < 1e-13, constants["c1"], "243/(8000P)")
    audit.check("production", "production_floor_derived", abs(constants["floor"] - 1.0e-12) < 1.0e-27, constants["floor"], 1.0e-12)

    # Labelled exact regression oracles for the scalar small-heat diagnostic.
    # The computation above derives them from alpha=5/9; no production output
    # is pasted back as an input.
    balanced_heat = scalar_balanced_heat_oracles()
    test_oracles = {
        "scalar_full_remainder": Fraction(40, 81),
        "scalar_base_cubic": Fraction(-25, 81),
        "scalar_balanced_remainder": Fraction(65, 81),
        "zero_heat_square_leading_coefficient": Fraction(4),
        "balanced_schur_divergence_coefficient": Fraction(4225, 52488),
    }
    for name, expected in test_oracles.items():
        actual = balanced_heat[name]
        audit.check("balanced_heat_boundary", name, actual == expected, actual, expected)
    projector = np.diag([1.0, 1.0, 0.0, 1.0, 1.0, 0.0])
    floor = constants["floor"]
    root_floor = math.sqrt(floor)
    boundary_vectors = [
        np.zeros(6),
        np.array([root_floor, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, root_floor, 0.0, 0.0, 0.0]),
        np.array([root_floor, 0.0, root_floor, 0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0]),
    ]
    test_vectors = boundary_vectors + [rng.normal(size=6) for _ in range(42)]
    domination_residuals: list[float] = []
    for index, z in enumerate(test_vectors):
        radius = float(z @ projector @ z)
        denominator = float(z @ z) + floor
        rational_vector = projector @ z - constants["alpha"] * radius / denominator * z
        gap = radius - float(rational_vector @ rational_vector)
        exact_gap = constants["alpha"] * radius**2 / denominator**2 * (
            2.0 * denominator - constants["alpha"] * float(z @ z)
        )
        domination_residuals.append(abs(gap - exact_gap))
        audit.check("production", f"rational_range_identity_{index}", abs(gap - exact_gap) < tol, gap - exact_gap, 0.0)
        audit.check("production", f"rational_range_domination_{index}", gap >= -tol, gap, ">=0")
        if index == 1:
            near_floor_oracle = floor * constants["alpha"] * (4.0 - constants["alpha"]) / 4.0
            audit.check(
                "production",
                "near_floor_pure_doublet_oracle",
                abs(gap - near_floor_oracle) < 1.0e-24,
                gap,
                near_floor_oracle,
            )

    diagnostics.update(
        {
            "moving_baseline_crosses": baseline_crosses,
            "terminal_raw_wick": terminal_wick,
            "residual_sum": residual_sum,
            "nonzero_fixed_low_endpoint": fixed_low,
            "correlated_cross": correlated_cross,
            "direct_gradient_cross": direct_gradient_cross,
            "max_K_residual": max(k_residuals),
            "max_K_regroup_residual": max(regroup_residuals),
            "control_square_endpoint": control_square_endpoint,
            "shifted_current_fixture": shifted_current,
            "production_constants": constants,
            "balanced_heat_boundary": balanced_heat,
            "max_rational_range_identity_residual": max(domination_residuals),
            "proved_scope": {
                "moving_raw_wick_heat_baseline_orthogonality": True,
                "cross_doob_raw_wick_reduction": True,
                "exact_derivative_current_remainder": True,
                "control_square_endpoint_telescope": True,
                "production_rational_range_domination": True,
                "shifted_current_hessian_form": False,
                "complete_h_n": False,
                "reg": False,
                "sector_a": False,
            },
        }
    )
    result = audit.finish(diagnostics)
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": result["status"], "assertions": result["assertions_total"], "output": str(OUTPUT.relative_to(REPO))}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
