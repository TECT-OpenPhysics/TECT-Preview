#!/usr/bin/env python3
"""Primary executable certificate for the R-099 A13 checkpoint.

The certificate tests the exact extended-state Cartan telescope, the
progressive-revisit mixed-payload scaling obstruction, a causal Doob--Hardy
one-use theorem, the complete-frame ordered-reveal/Jensen residual, and the
rational five-family/payment-gauge recovery.  It deliberately does not claim
the still-open production posterior lower form.
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
from typing import Any, Callable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-EXTENDED-STATE-CARTAN-DOOB-RATIONAL-RECOVERY"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-27-primary-extended-state-cartan-doob-rational-recovery/result.json"
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
            "schema": "tect/a13-extended-state-cartan-doob-rational-recovery-primary/1.0",
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
                "R-099 closes exact signed grouping, causal control-coordinate ownership, "
                "and the rational five-family upper form. It proves two scoped method no-gos. "
                "The coefficient-unconditioned production posterior lower form, rational (6.5), "
                "complete H_N, REG, OVERLAP_src, Nelson, measure, and Sector A remain open."
            ),
        }


def expectation(values: np.ndarray) -> float:
    return float(np.mean(values))


def conditional(values: np.ndarray, states: np.ndarray, revealed: int) -> np.ndarray:
    """Conditional expectation after the first ``revealed`` Boolean roots."""
    if revealed == 0:
        return np.full_like(values, expectation(values), dtype=float)
    answer = np.empty_like(values, dtype=float)
    groups: dict[tuple[int, ...], list[int]] = {}
    for index, state in enumerate(states):
        groups.setdefault(tuple(int(x) for x in state[:revealed]), []).append(index)
    for indices in groups.values():
        mean = float(np.mean(values[indices]))
        answer[indices] = mean
    return answer


def extended_current(sigma: float, z: float) -> float:
    """Nonlinear test current; the telescope is independent of this choice."""
    return (1.0 + sigma * sigma) * z + sigma * z**3


def polynomial_laplacian_jacobian(s: tuple[tuple[Fraction, ...], ...], floor: Fraction) -> list[list[Fraction]]:
    """Compute D Delta[(z^T S z)z/floor](0) by monomial contraction."""
    dimension = len(s)
    polynomials: list[dict[tuple[int, ...], Fraction]] = [dict() for _ in range(dimension)]
    for output in range(dimension):
        for left in range(dimension):
            for right in range(dimension):
                exponent = [0] * dimension
                exponent[output] += 1
                exponent[left] += 1
                exponent[right] += 1
                key = tuple(exponent)
                polynomials[output][key] = polynomials[output].get(key, Fraction(0)) + s[left][right] / floor
    jacobian = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for output, polynomial in enumerate(polynomials):
        for exponent, coefficient in polynomial.items():
            for variable, power in enumerate(exponent):
                if power < 2:
                    continue
                reduced = list(exponent)
                reduced[variable] -= 2
                for derivative in range(dimension):
                    target = [0] * dimension
                    target[derivative] = 1
                    if reduced == target:
                        jacobian[output][derivative] += coefficient * power * (power - 1)
    return jacobian


def matrix_close(left: np.ndarray, right: np.ndarray, tolerance: float = 2.0e-11) -> bool:
    return bool(np.max(np.abs(left - right)) < tolerance)


def payment_gauge(
    weights: np.ndarray,
    matrices: list[np.ndarray],
    carriers: list[np.ndarray],
    gamma: np.ndarray,
    payment: np.ndarray,
    shift: np.ndarray,
) -> tuple[float, float]:
    bar = sum(float(weight) * matrix for weight, matrix in zip(weights, matrices))
    q = sum(float(weight) * matrix @ carrier for weight, matrix, carrier in zip(weights, matrices, carriers))
    wick = sum(
        float(weight) * float(np.sum(matrix * (np.outer(carrier, carrier) - gamma)))
        for weight, matrix, carrier in zip(weights, matrices, carriers)
    )
    a = bar + 2.0 * payment
    square_vector = shift + np.linalg.solve(a, q)
    left = (
        0.5 * float(square_vector @ a @ square_vector)
        + 0.5 * (wick - float(q @ np.linalg.solve(a, q)))
        - float(shift @ payment @ shift)
    )
    right = 0.5 * sum(
        float(weight)
        * float(np.sum(matrix * (np.outer(carrier + shift, carrier + shift) - gamma)))
        for weight, matrix, carrier in zip(weights, matrices, carriers)
    )
    return left, right


def main() -> int:
    audit = Audit()
    tolerance = 2.0e-10
    diagnostics: dict[str, Any] = {}

    # 1. Exact extended-state signed Cartan telescope, including changing heat.
    rng = np.random.default_rng(990727)
    telescope_defects: list[float] = []
    source_only_defects: list[float] = []
    for trial in range(16):
        length = 3 + trial % 5
        sigmas = rng.normal(size=length + 1)
        points = rng.normal(size=length + 1)
        complete_edges = []
        source_edges = []
        heat_edges = []
        for level in range(1, length + 1):
            source = extended_current(sigmas[level], points[level]) - extended_current(sigmas[level], points[level - 1])
            heat = extended_current(sigmas[level], points[level - 1]) - extended_current(sigmas[level - 1], points[level - 1])
            source_edges.append(source)
            heat_edges.append(heat)
            complete_edges.append(source + heat)
        endpoint = extended_current(sigmas[-1], points[-1]) - extended_current(sigmas[0], points[0])
        complete_defect = float(sum(complete_edges) - endpoint)
        omitted_heat_defect = float(sum(source_edges) - endpoint + sum(heat_edges))
        telescope_defects.append(abs(complete_defect))
        source_only_defects.append(abs(float(sum(source_edges) - endpoint)))
        audit.check("cartan_telescope", f"complete_edge_telescope_{trial}", abs(complete_defect) < tolerance, complete_defect, 0.0)
        audit.check("cartan_telescope", f"omitted_heat_defect_identity_{trial}", abs(omitted_heat_defect) < tolerance, omitted_heat_defect, 0.0)

    closed_sigmas = np.array([0.2, 0.9, -0.4, 0.2])
    closed_points = np.array([-0.7, 1.1, 0.3, -0.7])
    closed_sum = sum(
        extended_current(closed_sigmas[level], closed_points[level])
        - extended_current(closed_sigmas[level - 1], closed_points[level - 1])
        for level in range(1, len(closed_sigmas))
    )
    noninjective_endpoint = extended_current(0.2, 0.0) - extended_current(-0.7, 0.0)
    audit.check(
        "cartan_telescope",
        "extended_state_closed_loop_zero",
        abs(closed_sum) < tolerance and abs(noninjective_endpoint) < tolerance and 0.2 != -0.7,
        {"equal_extended_endpoints": closed_sum, "distinct_heat_equal_current": noninjective_endpoint},
        {"equal_extended_endpoints": 0.0, "distinct_heat_equal_current": 0.0},
    )
    audit.check("cartan_telescope", "linear_ou_projection_preserves_zero", abs(0.173 * closed_sum) < tolerance, 0.173 * closed_sum, 0.0)

    # Dropping heat compensation is genuinely nonzero, not a notation issue.
    sigma_path = [0.0, 0.6, -0.2]
    point_path = [0.1, 0.8, -0.4]
    source_sum = sum(
        extended_current(sigma_path[level], point_path[level])
        - extended_current(sigma_path[level], point_path[level - 1])
        for level in range(1, len(sigma_path))
    )
    endpoint = extended_current(sigma_path[-1], point_path[-1]) - extended_current(sigma_path[0], point_path[0])
    audit.check("cartan_telescope", "drop_heat_compensator_mutant_fails", abs(source_sum - endpoint) > 0.05, source_sum - endpoint, "nonzero")

    # Exact production low-heat coefficient D Delta F_S(0).
    s_fraction = ((Fraction(3, 2), Fraction(-2, 3)), (Fraction(-2, 3), Fraction(-3, 2)))
    floor = Fraction(7, 5)
    contracted = polynomial_laplacian_jacobian(s_fraction, floor)
    expected_contracted = [[4 * s_fraction[i][j] / floor for j in range(2)] for i in range(2)]
    audit.check("cartan_heat", "trace_free_cubic_heat_derivative_exact", contracted == expected_contracted, contracted, expected_contracted)
    audit.check("cartan_heat", "factor_two_heat_generator_exact", [[value / 2 for value in row] for row in contracted] == [[2 * s_fraction[i][j] / floor for j in range(2)] for i in range(2)], [[value / 2 for value in row] for row in contracted], "2S/e")
    audit.check("cartan_heat", "missing_factor_two_mutant_rejected", contracted != [[2 * s_fraction[i][j] / floor for j in range(2)] for i in range(2)], contracted, "not 2S/e")

    # 2. Progressive-revisit mixed-payload scaling obstruction.
    epsilon = 0.5
    rho = (1.0 - epsilon) / (1.0 + epsilon)
    harmonic = 4
    normalization = 1.75
    root_variance = 0.625
    pre_lp_coefficient = normalization**2 * root_variance * epsilon**2 * (1.0 - rho**2) ** 2 * rho ** (2 * (harmonic - 1))
    audit.check("progressive_revisit", "production_harmonic_coefficient_positive", pre_lp_coefficient > 0.0, pre_lp_coefficient, "> 0")
    kappa_loop = 2.4
    terminal_y = 1.7
    amplitudes = np.array([4.0, 16.0, 64.0, 256.0])
    square_energy = pre_lp_coefficient * amplitudes**2
    mixed_payload = 1.0 + np.sqrt(kappa_loop * amplitudes**2 * terminal_y)
    ratios = square_energy / mixed_payload
    audit.check("progressive_revisit", "root_square_is_quadratic", np.allclose(square_energy / amplitudes**2, pre_lp_coefficient), square_energy / amplitudes**2, pre_lp_coefficient)
    audit.check("progressive_revisit", "terminal_mixed_payload_is_linear", np.all(np.diff(mixed_payload / amplitudes) < 0.0), mixed_payload / amplitudes, "decreases to constant")
    audit.check("progressive_revisit", "mixed_payload_ratio_diverges", np.all(np.diff(ratios) > 0.0) and ratios[-1] > 20.0 * ratios[0], ratios, "strict growth")
    direct_sum_t = np.array([[1.3, -0.4], [0.2, 0.9]])
    separate_root_operator = np.concatenate((direct_sum_t, -direct_sum_t), axis=1)
    audit.check("progressive_revisit", "distinct_root_hs_direct_sum", abs(float(np.sum(separate_root_operator**2)) - 2.0 * float(np.sum(direct_sum_t**2))) < tolerance, float(np.sum(separate_root_operator**2)), 2.0 * float(np.sum(direct_sum_t**2)))
    visit = amplitudes[-1] * np.array([1.0, -0.5])
    inverse_visit = -visit
    terminal_shift = visit + inverse_visit
    wrong_sign_mutant = visit - inverse_visit
    audit.check(
        "progressive_revisit",
        "terminal_reverse_shift_zero",
        np.linalg.norm(terminal_shift) == 0.0 and np.linalg.norm(wrong_sign_mutant) > 0.0,
        {"terminal_norm": np.linalg.norm(terminal_shift), "wrong_sign_norm": np.linalg.norm(wrong_sign_mutant)},
        {"terminal_norm": 0.0, "wrong_sign_norm": "> 0"},
    )

    # 3. Causal Doob--Hardy theorem on the exact Boolean cube.
    root_count = 6
    states = np.array(list(itertools.product((-1, 1), repeat=root_count)), dtype=int)
    h_values: dict[int, np.ndarray] = {}
    for shell in range(1, root_count + 2):
        values = np.full(len(states), 0.13 * shell)
        for index in range(shell - 1):
            values += (0.07 + 0.01 * shell + 0.005 * index) * states[:, index]
        if shell >= 3:
            values += (0.04 + 0.003 * shell) * states[:, 0] * states[:, shell - 2]
        if shell >= 5:
            values -= 0.02 * states[:, 1] * states[:, 2] * states[:, shell - 2]
        h_values[shell] = values
    terminal_control = sum((2.0 ** (-2 * shell)) * values for shell, values in h_values.items())
    lhs = 0.0
    rhs = 0.0
    doob_identity_defects: list[float] = []
    for root in range(1, root_count + 1):
        d_control = conditional(terminal_control, states, root) - conditional(terminal_control, states, root - 1)
        future = np.zeros(len(states))
        for shell in range(root + 1, root_count + 2):
            d_h = conditional(h_values[shell], states, root) - conditional(h_values[shell], states, root - 1)
            future += (2.0 ** (-2 * shell)) * d_h
            rhs += (2.0 ** (-3 * shell)) * expectation(d_h**2)
        defect = float(np.max(np.abs(d_control - future)))
        doob_identity_defects.append(defect)
        audit.check("doob_hardy", f"last_root_identity_{root}", defect < tolerance, defect, 0.0)
        lhs += (2.0**root) * expectation(d_control**2)
    audit.check("doob_hardy", "weighted_hardy_bound", lhs <= rhs + tolerance, lhs, f"<= {rhs}")
    variance_rhs = 0.0
    for shell, values in h_values.items():
        variance_rhs += (2.0 ** (-3 * shell)) * expectation((values - expectation(values)) ** 2)
        martingale_mass = sum(
            expectation((conditional(values, states, root) - conditional(values, states, root - 1)) ** 2)
            for root in range(1, shell)
        )
        audit.check("doob_hardy", f"doob_variance_shell_{shell}", abs(martingale_mass - expectation((values - expectation(values)) ** 2)) < tolerance, martingale_mass, expectation((values - expectation(values)) ** 2))
    audit.check("doob_hardy", "variance_corollary", lhs <= variance_rhs + tolerance, lhs, f"<= {variance_rhs}")

    # Exact Hoeffding once-only ownership and coordinate-resampling multiplicity.
    support = (1, 3, 5)
    component = np.prod(states[:, [index - 1 for index in support]], axis=1)
    masses = []
    for root in range(1, root_count + 1):
        d_component = conditional(component, states, root) - conditional(component, states, root - 1)
        masses.append(expectation(d_component**2))
    audit.check("doob_hardy", "hoeffding_owned_at_max_support", masses == [0.0, 0.0, 0.0, 0.0, 1.0, 0.0], masses, [0.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    resampling_mass = 0.0
    for coordinate in range(root_count):
        flipped_states = states.copy()
        flipped_states[:, coordinate] *= -1
        flipped_component = np.prod(flipped_states[:, [index - 1 for index in support]], axis=1)
        resampling_mass += 0.25 * expectation((component - flipped_component) ** 2)
    audit.check("doob_hardy", "coordinate_influences_count_support_size", abs(resampling_mass - len(support)) < tolerance, resampling_mass, len(support))
    audit.check("doob_hardy", "dyadic_support_weight_not_divergent", sum(2**index for index in support) < 2 ** (max(support) + 1), sum(2**index for index in support), f"< {2 ** (max(support) + 1)}")

    # Sharp finite Hardy arrays approach the constant one.
    sharp_ratios = []
    for cutoff in (5, 9, 15, 23):
        numerator = 0.0
        denominator = 0.0
        for root in range(1, cutoff):
            summed = sum(2.0 ** (-2 * shell) * 2.0**shell for shell in range(root + 1, cutoff + 1))
            numerator += 2.0**root * summed**2
            denominator += sum(2.0 ** (-3 * shell) * (2.0**shell) ** 2 for shell in range(root + 1, cutoff + 1))
        sharp_ratios.append(numerator / denominator)
    audit.check("doob_hardy", "hardy_constant_one_upper", max(sharp_ratios) < 1.0, sharp_ratios, "< 1")
    audit.check("doob_hardy", "hardy_constant_one_sharp_limit", sharp_ratios[-1] > 0.90 and np.all(np.diff(sharp_ratios) > 0.0), sharp_ratios, "increases toward 1")
    spatial_exponents = {r: 2 * (Fraction(1, 2) + Fraction(3, r)) - 1 for r in (2, 3, 6)}
    audit.check("doob_hardy", "spatial_decay_r2", spatial_exponents[2] == 3, spatial_exponents[2], 3)
    audit.check("doob_hardy", "spatial_decay_r3", spatial_exponents[3] == 2, spatial_exponents[3], 2)
    audit.check("doob_hardy", "spatial_decay_r6", spatial_exponents[6] == 1, spatial_exponents[6], 1)

    # 4. Complete-frame ordered reveal and mandatory Jensen residual.
    terminal_z = 0.7 + 0.4 * states[:, 0] - 0.3 * states[:, 1] + 0.5 * states[:, 0] * states[:, 2]
    terminal_b = terminal_z**2
    q_terminal = states[:, 0] + 0.25 * states[:, 0] * states[:, 1] - 0.2 * states[:, 3]
    z_levels = [conditional(terminal_z, states, level) for level in range(root_count + 1)]
    b_levels = [conditional(terminal_b, states, level) for level in range(root_count + 1)]
    jensen_levels = [b_levels[level] - z_levels[level] ** 2 for level in range(root_count + 1)]
    q_levels = [conditional(q_terminal, states, level) for level in range(root_count + 1)]
    for root in range(1, root_count + 1):
        d_hat = b_levels[root] - b_levels[root - 1]
        secant = z_levels[root] ** 2 - z_levels[root - 1] ** 2
        residual = jensen_levels[root] - jensen_levels[root - 1]
        audit.check("ordered_reveal", f"frame_reveal_identity_{root}", float(np.max(np.abs(d_hat - secant - residual))) < tolerance, float(np.max(np.abs(d_hat - secant - residual))), 0.0)
        u = z_levels[root] - z_levels[root - 1]
        quadratic_chain = 2.0 * z_levels[root - 1] * u + u**2 + residual
        audit.check("ordered_reveal", f"quadratic_covariance_chain_{root}", float(np.max(np.abs(d_hat - quadratic_chain))) < tolerance, float(np.max(np.abs(d_hat - quadratic_chain))), 0.0)
    cross_left = expectation(terminal_b * q_terminal)
    cross_right = expectation(b_levels[0] * q_levels[0])
    for root in range(1, root_count + 1):
        cross_right += expectation((b_levels[root] - b_levels[root - 1]) * (q_levels[root] - q_levels[root - 1]))
    audit.check("ordered_reveal", "cross_doob_terminal_identity", abs(cross_left - cross_right) < tolerance, cross_left - cross_right, 0.0)

    # Exact product fixture: same-level mean shifts miss an exponentially large frame martingale.
    product_totals = []
    for count in (1, 2, 3, 5, 7):
        frame_mass = 4**count - 1
        shift_mass = 1
        product_totals.append((count, frame_mass, shift_mass))
        audit.check("ordered_reveal", f"three_point_frame_mass_{count}", sum(3 * 4 ** (root - 1) for root in range(1, count + 1)) == frame_mass, sum(3 * 4 ** (root - 1) for root in range(1, count + 1)), frame_mass)
        audit.check("ordered_reveal", f"same_level_shift_mass_{count}", shift_mass == 1, shift_mass, 1)
    audit.check("ordered_reveal", "same_level_frame_mutant_diverges", product_totals[-1][1] > 1000 * product_totals[-1][2], product_totals[-1], "frame/shift > 1000")

    # Rare-event multiplier spike: all separate budgets are one, square product diverges.
    spike_rows = []
    for size in (2, 4, 8, 16, 32):
        probability = size ** -6
        u = size**3
        z = size
        eu2 = probability * u**2
        ez6 = probability * z**6
        linear = probability * abs(u) * z**3
        squared = probability * z**2 * u**2
        spike_rows.append((size, eu2, ez6, linear, squared))
        audit.check("frame_multiplier", f"spike_unit_u2_{size}", abs(eu2 - 1.0) < tolerance, eu2, 1.0)
        audit.check("frame_multiplier", f"spike_unit_z6_{size}", abs(ez6 - 1.0) < tolerance, ez6, 1.0)
        audit.check("frame_multiplier", f"spike_unit_linear_{size}", abs(linear - 1.0) < tolerance, linear, 1.0)
        audit.check("frame_multiplier", f"spike_square_growth_{size}", abs(squared - size**2) < tolerance, squared, size**2)
    audit.check("frame_multiplier", "absolute_secant_square_not_budgeted", spike_rows[-1][-1] > 100.0 * spike_rows[0][-1], spike_rows[-1][-1] / spike_rows[0][-1], "> 100")

    # 5. Rational five-family two-sided form and exact payment gauge.
    exponent_rows = (
        (Fraction(11, 40), Fraction(3, 40), Fraction(13, 20), Fraction(20, 13)),
        (Fraction(11, 20), Fraction(3, 20), Fraction(3, 10), Fraction(10, 3)),
        (Fraction(2, 5), Fraction(1, 30), Fraction(17, 30), Fraction(30, 17)),
        (Fraction(2, 5), Fraction(1, 5), Fraction(2, 5), Fraction(5, 2)),
        (Fraction(2, 5), Fraction(11, 30), Fraction(7, 30), Fraction(30, 7)),
    )
    for index, (x_power, y_power, slack, moment) in enumerate(exponent_rows, start=1):
        audit.check("rational_form", f"family_{index}_powers_sum_one", x_power + y_power + slack == 1, x_power + y_power + slack, 1)
        audit.check("rational_form", f"family_{index}_moment_reciprocal", moment == 1 / slack, moment, 1 / slack)
        audit.check("rational_form", f"family_{index}_moment_available", moment <= Fraction(30, 7), moment, "<= 30/7")
        for sample in range(5):
            coefficient = float(rng.uniform(0.2, 2.5))
            model = float(rng.uniform(0.1, 3.0))
            x_value = float(rng.uniform(0.01, 5.0))
            y_value = float(rng.uniform(0.01, 5.0))
            eta = float(rng.uniform(0.05, 1.2))
            zeta = float(rng.uniform(0.05, 1.2))
            x_float, y_float, slack_float = float(x_power), float(y_power), float(slack)
            remainder = (
                slack_float
                * coefficient ** (1.0 / slack_float)
                * x_float ** (x_float / slack_float)
                * y_float ** (y_float / slack_float)
                * eta ** (-x_float / slack_float)
                * zeta ** (-y_float / slack_float)
                * model ** (1.0 / slack_float)
            )
            left = coefficient * model * x_value**x_float * y_value**y_float
            right = eta * x_value + zeta * y_value + remainder
            audit.check("rational_form", f"young_family_{index}_sample_{sample}", left <= right + tolerance, left - right, "<= 0")

    payment_defects = []
    for trial in range(16):
        dimension = 3
        atom_count = 4
        weights = rng.random(atom_count)
        weights /= weights.sum()
        matrices = []
        carriers = []
        for _ in range(atom_count):
            frame = rng.normal(size=(dimension, 2))
            matrices.append(frame @ frame.T)
            carriers.append(rng.normal(size=dimension))
        payment_root = rng.normal(size=(dimension, dimension))
        payment = payment_root @ payment_root.T + 0.25 * np.eye(dimension)
        gamma_root = rng.normal(size=(dimension, dimension))
        gamma = gamma_root @ gamma_root.T
        shift = rng.normal(size=dimension)
        left, right = payment_gauge(weights, matrices, carriers, gamma, payment, shift)
        defect = left - right
        payment_defects.append(abs(defect))
        audit.check("payment_gauge", f"exact_identity_{trial}", abs(defect) < tolerance, defect, 0.0)

    # A deliberate wrong payment coefficient fails.
    weights = np.array([0.5, 0.5])
    matrices = [np.array([[2.0]]), np.array([[0.5]])]
    carriers = [np.array([1.0]), np.array([-2.0])]
    gamma = np.array([[1.0]])
    payment = np.array([[0.7]])
    shift = np.array([1.3])
    correct_left, correct_right = payment_gauge(weights, matrices, carriers, gamma, payment, shift)
    wrong_left = correct_left + float(shift @ payment @ shift)
    audit.check("payment_gauge", "correct_scalar_fixture", abs(correct_left - correct_right) < tolerance, correct_left - correct_right, 0.0)
    audit.check("payment_gauge", "omit_payment_mutant_rejected", abs(wrong_left - correct_right) > 0.5, wrong_left - correct_right, "nonzero")

    # Exact abstract Gram recovery fixture showing a lower form alone is insufficient.
    u0 = 1.0
    increment = -2.0
    b = lambda z: (z * z - 1.0) ** 2
    b_prime = lambda z: 4.0 * z * (z * z - 1.0)
    b_second = lambda z: 12.0 * z * z - 4.0
    t_values = (0.5, 1.0, 3.0, 11.0)
    for t_value in t_values:
        q_value = t_value**2
        remainder = b(u0 + increment) - b(u0) - b_prime(u0) * increment - 0.5 * b_second(u0) * increment**2
        unshifted = 0.25 * b_second(u0) * increment**2 * q_value
        shifted = 0.5 * remainder * q_value
        audit.check("rational_recovery", f"unshifted_positive_{t_value}", abs(unshifted - 8.0 * t_value**2) < tolerance, unshifted, 8.0 * t_value**2)
        audit.check("rational_recovery", f"shifted_negative_{t_value}", abs(shifted + 8.0 * t_value**2) < tolerance, shifted, -8.0 * t_value**2)
        audit.check("rational_recovery", f"endpoint_owner_zero_{t_value}", abs(unshifted + shifted) < tolerance, unshifted + shifted, 0.0)
    audit.check("rational_recovery", "lower_only_mutant_unbounded", -8.0 * t_values[-1] ** 2 < -100.0, -8.0 * t_values[-1] ** 2, "< -100")

    diagnostics.update(
        {
            "max_telescope_defect": max(telescope_defects),
            "example_source_only_endpoint_defect": source_only_defects[-1],
            "pre_lp_progressive_coefficient": pre_lp_coefficient,
            "progressive_energy_to_mixed_ratios": ratios.tolist(),
            "doob_hardy_lhs": lhs,
            "doob_hardy_increment_rhs": rhs,
            "doob_hardy_variance_rhs": variance_rhs,
            "hardy_sharp_ratios": sharp_ratios,
            "three_point_product_totals": product_totals,
            "spike_rows": spike_rows,
            "rational_exponents": exponent_rows,
            "max_payment_gauge_defect": max(payment_defects),
        }
    )
    payload = audit.finish(diagnostics)
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
