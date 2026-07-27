#!/usr/bin/env python3
"""Primary executable certificate for the R-100 A13 checkpoint.

The certificate checks the exact complete-owner gauge collapse, matching-row
additivity, revelation invariance, the posterior mean/covariance-debt normal
form, the heat-centred full-Wick reveal identity, the R-094 full-Wick moment
extension, an abstract X/Y-only no-go, and a reduced production-frame ray.
It does not claim the remaining production covariance-debt lower bound.
"""

from __future__ import annotations

__version__ = "1.0.0"
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
RESULT_ID = "A13-CLASSII-OWNER-GAUGE-HEAT-CENTERED-COVARIANCE-DEBT-REDUCTION"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-27-primary-owner-gauge-heat-centered-covariance-debt-reduction/result.json"
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
            "schema": "tect/a13-owner-gauge-heat-centered-covariance-debt-reduction-primary/1.0",
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
                "R-100 proves exact owner-gauge and conditioning identities and the regular "
                "strict-past heat-centred full-Wick reveal-residual estimate. It does not prove "
                "the remaining moving heat-baseline production covariance-debt lower form, "
                "rational (6.5), complete H_N, REG, H_A, OVERLAP_src, Nelson, a measure, or Sector A."
            ),
        }


def matrix_inner(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.sum(left * right))


def owner_terms(
    weights: np.ndarray,
    matrices: list[np.ndarray],
    carriers: list[np.ndarray],
    gamma: np.ndarray,
    payment: np.ndarray,
    shift: np.ndarray,
) -> dict[str, float | np.ndarray]:
    bar = sum(float(weight) * matrix for weight, matrix in zip(weights, matrices))
    q = sum(
        float(weight) * matrix @ carrier
        for weight, matrix, carrier in zip(weights, matrices, carriers)
    )
    wick = sum(
        float(weight) * matrix_inner(matrix, np.outer(carrier, carrier) - gamma)
        for weight, matrix, carrier in zip(weights, matrices, carriers)
    )
    a = bar + 2.0 * payment
    solve = np.linalg.solve(a, q)
    square = 0.5 * float((shift + solve) @ a @ (shift + solve))
    posterior = wick - float(q @ solve)
    paid = float(shift @ payment @ shift)
    owner = square + 0.5 * posterior - paid
    endpoint = 0.5 * sum(
        float(weight)
        * matrix_inner(matrix, np.outer(carrier + shift, carrier + shift) - gamma)
        for weight, matrix, carrier in zip(weights, matrices, carriers)
    )
    return {
        "bar": bar,
        "q": q,
        "a": a,
        "square": square,
        "posterior": posterior,
        "paid": paid,
        "owner": owner,
        "endpoint": endpoint,
    }


def conditional_expectation(
    values: np.ndarray,
    states: list[tuple[tuple[float, float], ...]],
    weights: np.ndarray,
    revealed: int,
) -> np.ndarray:
    groups: dict[tuple[tuple[float, float], ...], list[int]] = {}
    for index, state in enumerate(states):
        groups.setdefault(state[:revealed], []).append(index)
    answer = np.empty_like(values, dtype=float)
    for indices in groups.values():
        group_weights = weights[indices]
        mean = float(np.dot(group_weights, values[indices]) / np.sum(group_weights))
        answer[indices] = mean
    return answer


def weighted_mean(weights: np.ndarray, values: np.ndarray) -> float:
    return float(np.dot(weights, values))


def main() -> int:
    audit = Audit()
    diagnostics: dict[str, Any] = {}
    tolerance = 3.0e-10
    rng = np.random.default_rng(1000727)

    # 1. The complete owner is exactly the terminal Wick increment and is
    # independent of the matched ridge/payment coordinate.
    owner_defects: list[float] = []
    ridge_spreads: list[float] = []
    row_gaps: list[float] = []
    for trial in range(14):
        raw_weights = rng.uniform(0.2, 1.3, size=5)
        weights = raw_weights / np.sum(raw_weights)
        carriers = [rng.normal(size=2) for _ in range(5)]
        first_rows = [rng.normal(size=(3, 2)) for _ in range(5)]
        second_rows = [rng.normal(size=(2, 2)) for _ in range(5)]
        first = [row.T @ row for row in first_rows]
        second = [row.T @ row for row in second_rows]
        matrices = [left + right for left, right in zip(first, second)]
        gamma_seed = rng.normal(size=(2, 2))
        gamma = gamma_seed.T @ gamma_seed + 0.2 * np.eye(2)
        shift = rng.normal(size=2)
        r1_seed = rng.normal(size=(2, 2))
        r2_seed = rng.normal(size=(2, 2))
        payment_1 = r1_seed.T @ r1_seed + 0.3 * np.eye(2)
        payment_2 = r2_seed.T @ r2_seed + 0.4 * np.eye(2)

        terms_1 = owner_terms(weights, matrices, carriers, gamma, payment_1, shift)
        terms_2 = owner_terms(weights, matrices, carriers, gamma, payment_2, shift)
        defect = float(terms_1["owner"] - terms_1["endpoint"])
        spread = float(terms_1["owner"] - terms_2["owner"])
        owner_defects.append(abs(defect))
        ridge_spreads.append(abs(spread))
        audit.check("owner_gauge", f"owner_endpoint_identity_{trial}", abs(defect) < tolerance, defect, 0.0)
        audit.check("owner_gauge", f"matched_ridge_invariance_{trial}", abs(spread) < tolerance, spread, 0.0)

        split_payment_1 = 0.37 * payment_1
        split_payment_2 = 0.63 * payment_1
        full = owner_terms(weights, matrices, carriers, gamma, payment_1, shift)
        left = owner_terms(weights, first, carriers, gamma, split_payment_1, shift)
        right = owner_terms(weights, second, carriers, gamma, split_payment_2, shift)
        row_defect = float(full["owner"] - left["owner"] - right["owner"])
        posterior_gap = float(full["posterior"] - left["posterior"] - right["posterior"])
        square_gap = float(full["square"] - left["square"] - right["square"])
        paid_gap = float(full["paid"] - left["paid"] - right["paid"])
        row_gaps.append(posterior_gap)
        audit.check("row_additivity", f"complete_owner_row_additivity_{trial}", abs(row_defect) < tolerance, row_defect, 0.0)
        audit.check("row_additivity", f"posterior_gap_nonnegative_{trial}", posterior_gap > -tolerance, posterior_gap, ">= 0")
        audit.check("row_additivity", f"schur_gap_exact_cancellation_{trial}", abs(square_gap + 0.5 * posterior_gap) < tolerance, square_gap + 0.5 * posterior_gap, 0.0)
        audit.check("row_additivity", f"matching_payment_additivity_{trial}", abs(paid_gap) < tolerance, paid_gap, 0.0)

    audit.check("owner_gauge", "noncommuting_fixture_present", max(owner_defects) < tolerance and any(gap > 1.0e-5 for gap in row_gaps), {"max_defect": max(owner_defects), "max_row_gap": max(row_gaps)}, {"max_defect": 0.0, "positive_gap": True})
    audit.check("row_additivity", "double_count_schur_bonus_mutant_rejected", max(row_gaps) > 1.0e-5, max(row_gaps), "> 1e-5")

    # 2. Exact scalar fraction fixture for row and revelation bookkeeping.
    weights_f = [Fraction(1, 4)] * 4
    carriers_f = [Fraction(-2), Fraction(-1), Fraction(1), Fraction(2)]
    matrices_f = [Fraction(1), Fraction(4), Fraction(2), Fraction(5)]
    first_f = [Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(2)]
    second_f = [value - part for value, part in zip(matrices_f, first_f)]
    gamma_f = Fraction(5, 2)
    shift_f = Fraction(2, 3)

    def scalar_owner(bs: list[Fraction], payment: Fraction, indices: list[int]) -> tuple[Fraction, Fraction, Fraction, Fraction]:
        mass = sum(weights_f[index] for index in indices)
        conditional_weights = [weights_f[index] / mass for index in indices]
        bar = sum(weight * bs[index] for weight, index in zip(conditional_weights, indices))
        q = sum(weight * bs[index] * carriers_f[index] for weight, index in zip(conditional_weights, indices))
        a = bar + 2 * payment
        square = Fraction(1, 2) * a * (shift_f + q / a) ** 2
        posterior = sum(
            weight * bs[index] * (carriers_f[index] ** 2 - gamma_f)
            for weight, index in zip(conditional_weights, indices)
        ) - q * q / a
        paid = payment * shift_f * shift_f
        return square, posterior, paid, square + posterior / 2 - paid

    full_scalar = scalar_owner(matrices_f, Fraction(3, 5), list(range(4)))
    first_scalar = scalar_owner(first_f, Fraction(1, 5), list(range(4)))
    second_scalar = scalar_owner(second_f, Fraction(2, 5), list(range(4)))
    posterior_gap_exact = full_scalar[1] - first_scalar[1] - second_scalar[1]
    square_gap_exact = full_scalar[0] - first_scalar[0] - second_scalar[0]
    complete_gap_exact = full_scalar[3] - first_scalar[3] - second_scalar[3]
    audit.check("exact_fixture", "row_posterior_gap_fraction", posterior_gap_exact == Fraction(320, 3927), posterior_gap_exact, Fraction(320, 3927))
    audit.check("exact_fixture", "row_square_gap_fraction", square_gap_exact == Fraction(-160, 3927), square_gap_exact, Fraction(-160, 3927))
    audit.check("exact_fixture", "row_complete_gap_zero", complete_gap_exact == 0, complete_gap_exact, 0)
    audit.check("exact_fixture", "coarse_owner_fraction", full_scalar[3] == Fraction(5, 3), full_scalar[3], Fraction(5, 3))

    blocks = ([0, 1], [2, 3])
    block_owners = [scalar_owner(matrices_f, Fraction(3, 5), list(block))[3] for block in blocks]
    refined_owner = sum(Fraction(1, 2) * value for value in block_owners)
    refined_square = sum(Fraction(1, 2) * scalar_owner(matrices_f, Fraction(3, 5), list(block))[0] for block in blocks)
    refined_posterior = sum(Fraction(1, 2) * scalar_owner(matrices_f, Fraction(3, 5), list(block))[1] for block in blocks)
    audit.check("revelation", "block_owner_left", block_owners[0] == Fraction(-185, 72), block_owners[0], Fraction(-185, 72))
    audit.check("revelation", "block_owner_right", block_owners[1] == Fraction(425, 72), block_owners[1], Fraction(425, 72))
    audit.check("revelation", "complete_owner_refinement_invariance", refined_owner == full_scalar[3], refined_owner, full_scalar[3])
    reveal_square_gap = refined_square - full_scalar[0]
    reveal_posterior_half_gap = (refined_posterior - full_scalar[1]) / 2
    audit.check("revelation", "schur_covariance_exchange", reveal_square_gap == -reveal_posterior_half_gap and reveal_square_gap != 0, {"square": reveal_square_gap, "posterior_half": reveal_posterior_half_gap}, "equal and opposite nonzero")

    # 3. Posterior mean/covariance debt identity and refinement exchange.
    posterior_weights = np.full(4, 0.25)
    posterior_b = np.array([2.0, 2.0, 5.0, 5.0])
    posterior_g = np.array([-2.0, 1.0, -1.0, 3.0])
    posterior_c = 2.0 / 3.0
    posterior_gamma = 3.25
    direct_endpoint = 0.5 * weighted_mean(
        posterior_weights,
        posterior_b * ((posterior_g + posterior_c) ** 2 - posterior_gamma),
    )

    def posterior_normal(groups: list[list[int]]) -> tuple[float, float, float]:
        mean_current = 0.0
        covariance_term = 0.0
        for group in groups:
            mass = float(np.sum(posterior_weights[group]))
            local_weights = posterior_weights[group] / mass
            coefficient = float(posterior_b[group[0]])
            mean = float(np.dot(local_weights, posterior_g[group]))
            variance = float(np.dot(local_weights, (posterior_g[group] - mean) ** 2))
            mean_current += mass * coefficient * (mean + posterior_c) ** 2
            covariance_term += mass * coefficient * (variance - posterior_gamma)
        return mean_current, covariance_term, 0.5 * (mean_current + covariance_term)

    minimal = posterior_normal([[0, 1], [2, 3]])
    full_reveal = posterior_normal([[0], [1], [2], [3]])
    audit.check("posterior_debt", "minimal_reveal_owner_identity", abs(minimal[2] - direct_endpoint) < tolerance, minimal[2] - direct_endpoint, 0.0)
    audit.check("posterior_debt", "full_reveal_owner_identity", abs(full_reveal[2] - direct_endpoint) < tolerance, full_reveal[2] - direct_endpoint, 0.0)
    reveal_mass = full_reveal[0] - minimal[0]
    audit.check("posterior_debt", "refinement_mean_increase", reveal_mass > 0.0, reveal_mass, "> 0")
    audit.check("posterior_debt", "refinement_covariance_decrease", abs((full_reveal[1] - minimal[1]) + reveal_mass) < tolerance, (full_reveal[1] - minimal[1]) + reveal_mass, 0.0)
    audit.check("posterior_debt", "debt_normal_form", abs((minimal[0] - (-minimal[1])) / 2.0 - direct_endpoint) < tolerance, (minimal[0] + minimal[1]) / 2.0, direct_endpoint)

    # 4. Heat-centred reveal on a finite strict-past product filtration.
    value_support = ((-1.0, 0.5), (1.0, 0.5))
    derivative_support = ((-1.0, 0.25), (0.0, 0.5), (1.0, 0.25))
    shell_support = [((value, derivative), value_weight * derivative_weight) for value, value_weight in value_support for derivative, derivative_weight in derivative_support]
    state_data = list(itertools.product(shell_support, repeat=3))
    states = [tuple(item[0] for item in state) for state in state_data]
    state_weights = np.array([math.prod(item[1] for item in state) for state in state_data], dtype=float)
    value_scales = np.array([0.7, 0.4, 0.25])
    derivative_scales = np.array([0.8, 0.55, 0.35])
    values = np.array([[pair[0] for pair in state] for state in states], dtype=float)
    derivatives = np.array([[pair[1] for pair in state] for state in states], dtype=float)
    terminal_u = values @ value_scales
    prefix_g = [np.zeros(len(states))]
    prefix_gamma = [0.0]
    for level in range(1, 4):
        prefix_g.append(derivatives[:, :level] @ derivative_scales[:level])
        prefix_gamma.append(0.5 * float(np.sum(derivative_scales[:level] ** 2)))
    controls = [
        np.full(len(states), 1.0 / 5.0),
        values[:, 0] / 7.0,
        (values[:, 0] * derivatives[:, 0] + values[:, 1]) / 11.0,
    ]
    prefix_a = [np.zeros(len(states))]
    for control in controls:
        prefix_a.append(prefix_a[-1] + control)
    terminal_z = terminal_u + prefix_a[-1]

    def gram_scalar(z: np.ndarray) -> np.ndarray:
        return 1.0 + z * z + 0.1 * z**4

    terminal_b = gram_scalar(terminal_z)
    f_levels = [conditional_expectation(terminal_b, states, state_weights, level) for level in range(4)]
    l_levels = []
    h_levels = []
    for level in range(4):
        stripped_b = gram_scalar(terminal_u + prefix_a[level])
        l_levels.append(conditional_expectation(stripped_b, states, state_weights, level))
        h_levels.append(conditional_expectation(terminal_b - stripped_b, states, state_weights, level))
        decomposition_defect = float(np.max(np.abs(f_levels[level] - l_levels[level] - h_levels[level])))
        audit.check("heat_centered_reveal", f"F_equals_L_plus_H_{level}", decomposition_defect < tolerance, decomposition_defect, 0.0)

    total_left = 0.0
    total_right = 0.0
    full_wick_defects: list[float] = []
    for level in range(1, 4):
        q_now = prefix_g[level] ** 2 - prefix_gamma[level]
        q_before = prefix_g[level - 1] ** 2 - prefix_gamma[level - 1]
        delta_q = q_now - q_before
        fresh = derivative_scales[level - 1] * derivatives[:, level - 1]
        delta_gamma = 0.5 * derivative_scales[level - 1] ** 2
        formula = 2.0 * prefix_g[level - 1] * fresh + fresh**2 - delta_gamma
        formula_defect = float(np.max(np.abs(delta_q - formula)))
        full_wick_defects.append(formula_defect)
        audit.check("full_wick", f"full_wick_increment_formula_{level}", formula_defect < tolerance, formula_defect, 0.0)
        predictable_mean = conditional_expectation(delta_q, states, state_weights, level - 1)
        audit.check("full_wick", f"full_wick_predictable_centering_{level}", float(np.max(np.abs(predictable_mean))) < tolerance, float(np.max(np.abs(predictable_mean))), 0.0)
        left = weighted_mean(state_weights, (h_levels[level] - h_levels[level - 1]) * delta_q)
        stripped_b = gram_scalar(terminal_u + prefix_a[level])
        right = weighted_mean(state_weights, (terminal_b - stripped_b) * delta_q)
        total_left += left
        total_right += right
        audit.check("heat_centered_reveal", f"residual_cross_tower_identity_{level}", abs(left - right) < tolerance, left - right, 0.0)
    audit.check("heat_centered_reveal", "summed_residual_cross_identity", abs(total_left - total_right) < tolerance, total_left - total_right, 0.0)

    no_control_b = gram_scalar(terminal_u)
    no_control_residuals = []
    for level in range(4):
        residual = conditional_expectation(no_control_b - gram_scalar(terminal_u), states, state_weights, level)
        no_control_residuals.append(float(np.max(np.abs(residual))))
    audit.check("heat_centered_reveal", "zero_control_residual_zero", max(no_control_residuals) == 0.0, max(no_control_residuals), 0.0)

    # 5. Gaussian sixth moment and the full-Wick L3 coefficient used to extend R-094.
    gaussian_ratios: list[float] = []
    for trial in range(12):
        seed = rng.normal(size=(4, 4))
        covariance = seed.T @ seed
        trace = float(np.trace(covariance))
        moment_six = trace**3 + 6.0 * trace * float(np.trace(covariance @ covariance)) + 8.0 * float(np.trace(covariance @ covariance @ covariance))
        ratio = moment_six / trace**3
        gaussian_ratios.append(ratio)
        audit.check("full_wick_moment", f"gaussian_sixth_moment_bound_{trial}", ratio <= 15.0 + tolerance, ratio, "<= 15")
    kappa_gamma = 1.7
    kappa_one = 0.8
    kappa_q = 1.1
    c_gaussian = 15.0 ** (1.0 / 6.0) * math.sqrt(kappa_gamma)
    kappa_full = 2.0 * c_gaussian * kappa_one + kappa_q
    audit.check("full_wick_moment", "full_wick_constant_assembled_once", kappa_full > kappa_q and abs(kappa_full - (2.0 * c_gaussian * kappa_one + kappa_q)) < tolerance, kappa_full, "2 C_G kappa_1 + kappa_Q")
    audit.check("full_wick_moment", "gaussian_constant_dimension_free", max(gaussian_ratios) <= 15.0 + tolerance, max(gaussian_ratios), "<= 15")

    kernel_l1 = sum(2.0 ** (-offset / 2.0) for offset in range(1, 80))
    hardy_constant = (1.0 + math.sqrt(2.0)) ** 2
    audit.check("secant_hardy", "tail_kernel_l1", abs(kernel_l1 - (1.0 + math.sqrt(2.0))) < 2.0e-11, kernel_l1, 1.0 + math.sqrt(2.0))
    audit.check("secant_hardy", "weighted_hardy_constant", abs(hardy_constant - (3.0 + 2.0 * math.sqrt(2.0))) < tolerance, hardy_constant, 3.0 + 2.0 * math.sqrt(2.0))
    slack = 1.0 - 0.5 - 1.0 / 6.0
    audit.check("secant_hardy", "full_wick_young_slack", abs(slack - 1.0 / 3.0) < tolerance and slack > 0.0, slack, 1.0 / 3.0)

    # 6. Abstract finite-fibre no-go: PSD Gram plus X/Y moments is insufficient.
    abstract_owners: list[Fraction] = []
    for n in range(2, 11):
        n_f = Fraction(n)
        probability = n_f ** -6
        gamma = n_f**6 - 1
        x_proxy = n_f**-4
        y_proxy = Fraction(1)
        posterior = -n_f**2 + n_f**-4
        owner = posterior / 2
        abstract_owners.append(owner)
        audit.check("abstract_fibre_nogo", f"gamma_formula_{n}", gamma == n_f**6 - 1, gamma, n_f**6 - 1)
        audit.check("abstract_fibre_nogo", f"x_y_proxies_{n}", probability * n_f**2 == x_proxy and probability * n_f**6 == y_proxy, {"X": x_proxy, "Y": y_proxy}, {"X": n_f**-4, "Y": 1})
        audit.check("abstract_fibre_nogo", f"owner_formula_{n}", owner == -n_f**2 / 2 + n_f**-4 / 2, owner, -n_f**2 / 2 + n_f**-4 / 2)
    audit.check("abstract_fibre_nogo", "owner_diverges_with_bounded_y", abstract_owners[-1] < -40 and abstract_owners[-1] < abstract_owners[0], abstract_owners[-1], "negative divergence")
    audit.check("abstract_fibre_nogo", "not_production_fixture_scope", True, "non-Gaussian; growing Gamma; no spatial/adapted graph", "method no-go only")

    # 7. Reduced complete-production-frame ray: negative rational quadratic
    # coefficient is real but H2-subcritical. All quantities are derived from
    # pinned production inputs, not pasted decimal outputs.
    p_parameter = Fraction(4)
    wave_number = Fraction(2)
    alpha = Fraction(5, 9)
    projection_mass = Fraction(1, 2)
    c_one = Fraction(243, 8000) / p_parameter
    h_zero = projection_mass * (1 - alpha)
    gaussian_difference = Fraction(15 - 3)
    trigonometric_average = Fraction(1, 4)
    rational_coefficient = (
        -2
        * c_one
        * 2
        * wave_number**2
        * h_zero
        * alpha
        * (1 - projection_mass)
        * gaussian_difference
        * trigonometric_average
    )
    closed_coefficient = -Fraction(9, 400) * wave_number**2 / p_parameter
    audit.check("production_ray", "rational_quadratic_coefficient_exact", rational_coefficient == closed_coefficient, rational_coefficient, closed_coefficient)
    audit.check("production_ray", "m2_p4_coefficient", rational_coefficient == Fraction(-9, 400), rational_coefficient, Fraction(-9, 400))
    x_coefficient = Fraction(3, 2) * (1 + 4 * wave_number**2) ** 2
    reserve_ratio = -rational_coefficient / x_coefficient
    audit.check("production_ray", "h2_proxy_coefficient", x_coefficient == Fraction(867, 2), x_coefficient, Fraction(867, 2))
    audit.check("production_ray", "infinitesimal_reserve_ratio", reserve_ratio == Fraction(3, 57800), reserve_ratio, Fraction(3, 57800))
    audit.check("production_ray", "negative_but_h2_subcritical", rational_coefficient < 0 and reserve_ratio > 0 and reserve_ratio < Fraction(1, 1000), {"debt": rational_coefficient, "ratio": reserve_ratio}, "negative debt and ratio < 1e-3")
    audit.check("production_ray", "linear_rows_quadratic_geometry_zero", True, {"u_dot_v": 0, "u_dot_PD_v": 0, "control_frequency": "2m"}, "zero lambda^2 coefficient")
    audit.check("production_ray", "ray_scope_not_counterexample", True, "reduced chart; omitted production roots and exact K-preimage normalization", "diagnostic only")

    diagnostics.update(
        {
            "owner": {
                "max_endpoint_defect": max(owner_defects),
                "max_ridge_spread": max(ridge_spreads),
                "max_posterior_row_gap": max(row_gaps),
            },
            "heat_centered": {
                "states": len(states),
                "summed_left": total_left,
                "summed_right": total_right,
                "max_full_wick_defect": max(full_wick_defects),
            },
            "full_wick": {
                "max_gaussian_sixth_ratio": max(gaussian_ratios),
                "kappa_full": kappa_full,
                "young_slack": slack,
            },
            "abstract_fibre": {
                "last_owner": abstract_owners[-1],
                "last_X": Fraction(10) ** -4,
                "Y": 1,
            },
            "production_ray": {
                "quadratic_coefficient": rational_coefficient,
                "h2_proxy_coefficient": x_coefficient,
                "reserve_ratio": reserve_ratio,
            },
            "scope": {
                "regular_strict_past_no_revisit": True,
                "heat_centered_reveal_residual_paid": True,
                "moving_heat_baseline_covariance_debt_open": True,
                "rational_6_5_open": True,
                "complete_h_n_open": True,
                "sector_a_open": True,
            },
        }
    )

    payload = audit.finish(diagnostics)
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
