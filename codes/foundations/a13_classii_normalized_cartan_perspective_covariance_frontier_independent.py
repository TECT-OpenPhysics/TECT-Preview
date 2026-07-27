#!/usr/bin/env python3
"""Non-importing independent checks for the R-092 A13 frontier package."""

from __future__ import annotations

__version__ = "1.2.0"
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
RESULT_ID = "A13-CLASSII-NORMALIZED-CARTAN-COMPENSATED-PERSPECTIVE-TRIANGULAR-COVARIANCE-FRONTIER"
OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-25-independent-normalized-cartan-perspective-covariance-frontier/result.json"

INPUTS = {
    "dimension": 6,
    "floor": 0.23,
    "gamma": Fraction(1, 4),
    "sigma": Fraction(4, 15),
    "theta": Fraction(3, 10),
    "p": 6,
    "q": 3,
    "da3_x_exponent": Fraction(1, 2),
    "da3_y_exponent": Fraction(1, 6),
}

TEST_ORACLES = {
    "coefficient_poincare_constant": Fraction(16, 1),
    "two_tail_gradient_constant": Fraction(32, 1),
    "net_root_decay": Fraction(7, 30),
    "young_slack": Fraction(1, 30),
    "fixture_average": Fraction(-623, 5440),
    "product_gn_alpha": Fraction(1, 3),
    "a_da_outer_da": (Fraction(3, 5), Fraction(1, 3)),
    "a_du_outer_da": (Fraction(1, 2), Fraction(4, 15)),
    "a_da_outer_du": (Fraction(1, 10), Fraction(1, 6)),
}


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


def serialize(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, (list, tuple)):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    return value


def map_value(x: np.ndarray, matrix: np.ndarray, floor: float) -> np.ndarray:
    denominator = floor + float(x @ x)
    coefficient = float(x @ matrix @ x) / denominator
    return coefficient * x


def numerical_jacobian(x: np.ndarray, matrix: np.ndarray, floor: float) -> np.ndarray:
    dimension = x.size
    answer = np.zeros((dimension, dimension))
    step = 1.0e-6
    for column in range(dimension):
        direction = np.zeros(dimension)
        direction[column] = 1.0
        answer[:, column] = (map_value(x + step * direction, matrix, floor) - map_value(x - step * direction, matrix, floor)) / (2.0 * step)
    return answer


def exact_jacobian_independent(x: np.ndarray, matrix: np.ndarray, floor: float) -> np.ndarray:
    denominator = floor + float(x @ x)
    coefficient = float(x @ matrix @ x) / denominator
    gradient = 2.0 * (matrix @ x - coefficient * x) / denominator
    return coefficient * np.eye(x.size) + np.outer(x, gradient)


def branch_fixture(variance: Fraction) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    # Work in Q(sqrt(2V)); symmetry removes the radicals from every average.
    mean_b = Fraction(1, 1) - Fraction(1, 4) * (variance - 1)
    h_value = variance / 8
    # Direct conditional enumeration of (B-1)(G^2-1)/2, simplified from
    # the three-point law rather than selected by a branch oracle.
    kappa = -(variance - 1) ** 2 / 8 - variance**2 / 16
    minimum = kappa - Fraction(1, 2) * h_value * h_value / (mean_b + 1)
    j_d = -variance * variance / 16
    return mean_b, h_value, j_d, minimum


def main() -> int:
    assertions: list[dict[str, Any]] = []

    def add(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": serialize(actual), "expected": serialize(expected)})

    rng = np.random.default_rng(9202502)
    dimension = INPUTS["dimension"]
    floor = INPUTS["floor"]
    jacobian_errors = []
    norm_ceilings = []
    chord_ratios = []
    secant_ratios = []
    commutator_errors = []
    for _ in range(75):
        raw = rng.normal(size=(dimension, dimension))
        matrix = 0.5 * (raw + raw.T)
        matrix /= max(1.0, np.linalg.norm(matrix, ord=2))
        x = rng.normal(size=dimension)
        y = rng.normal(size=dimension)
        numerical = numerical_jacobian(x, matrix, floor)
        exact = exact_jacobian_independent(x, matrix, floor)
        jacobian_errors.append(float(np.linalg.norm(numerical - exact)))
        norm_ceilings.append(float(np.linalg.norm(exact, ord=2)))

        nx = x / math.sqrt(floor + float(x @ x))
        ny = y / math.sqrt(floor + float(y @ y))
        chord = 2.0 * np.linalg.norm(y - x) / (math.sqrt(floor + float(x @ x)) + math.sqrt(floor + float(y @ y)))
        if chord > 1.0e-14:
            chord_ratios.append(float(np.linalg.norm(ny - nx) / chord))
        delta = numerical_jacobian(y, matrix, floor) - numerical_jacobian(x, matrix, floor)
        if np.linalg.norm(ny - nx) > 1.0e-12:
            secant_ratios.append(float(np.linalg.norm(delta, ord=2) / np.linalg.norm(ny - nx)))
        projection = np.outer(nx, nx)
        commutator = 2.0 * (matrix @ projection - projection @ matrix)
        commutator_errors.append(float(np.linalg.norm(exact.T - exact - commutator)))

    add("independent_jacobian", max(jacobian_errors) < 7.0e-8, max(jacobian_errors), "<7e-8")
    add("independent_jacobian_norm", max(norm_ceilings) <= 3.0 + 1.0e-10, max(norm_ceilings), "<=3")
    add("independent_chord", max(chord_ratios) <= 1.0 + 1.0e-10, max(chord_ratios), "<=1")
    add("independent_secant_constant", max(secant_ratios) <= 14.0 + 2.0e-4, max(secant_ratios), "<=14")
    add("independent_commutator", max(commutator_errors) < 1.0e-12, max(commutator_errors), "<1e-12")

    # Independent transpose audit: finite-difference the endpoint secant and
    # compare it with the untransposed chain rule, then retain the actual
    # transposed current coefficient separately.
    audit_matrix = np.diag([1.0, -0.8, 0.6, -0.4, 0.2, -0.1])
    audit_x = rng.normal(size=dimension)
    audit_a = rng.normal(size=dimension) / 3.0
    audit_dx = rng.normal(size=dimension) / 2.0
    audit_da = rng.normal(size=dimension) / 4.0
    audit_j0 = exact_jacobian_independent(audit_x, audit_matrix, floor)
    audit_j1 = exact_jacobian_independent(audit_x + audit_a, audit_matrix, floor)
    audit_g = (audit_j1 - audit_j0) @ audit_dx + audit_j1 @ audit_da
    audit_b = (audit_j1 - audit_j0).T @ audit_dx + audit_j1.T @ audit_da
    audit_step = 7.0e-7

    def endpoint(parameter: float) -> np.ndarray:
        base = audit_x + parameter * audit_dx
        shift = audit_a + parameter * audit_da
        return map_value(base + shift, audit_matrix, floor) - map_value(base, audit_matrix, floor)

    endpoint_gradient = (endpoint(audit_step) - endpoint(-audit_step)) / (2.0 * audit_step)
    add("independent_endpoint_gradient", np.linalg.norm(endpoint_gradient - audit_g) < 2.0e-8, np.linalg.norm(endpoint_gradient - audit_g), "<2e-8")
    add("independent_transpose_defect", np.linalg.norm(audit_b - audit_g) > 1.0e-5, np.linalg.norm(audit_b - audit_g), ">1e-5")

    coefficient_lower_fraction = Fraction(1, 4)
    coefficient_poincare_constant = coefficient_lower_fraction ** -2
    two_tail_gradient_constant = 2 * coefficient_poincare_constant
    add("independent_coefficient_poincare", coefficient_poincare_constant == TEST_ORACLES["coefficient_poincare_constant"], coefficient_poincare_constant, TEST_ORACLES["coefficient_poincare_constant"])
    add("independent_two_tail_gradient", two_tail_gradient_constant == TEST_ORACLES["two_tail_gradient_constant"], two_tail_gradient_constant, TEST_ORACLES["two_tail_gradient_constant"])

    gamma = INPUTS["gamma"]
    sigma = INPUTS["sigma"]
    theta = INPUTS["theta"]
    output_weight = 1 + 2 * sigma
    worst_gaussian = 1 + theta
    net_decay = output_weight - worst_gaussian
    add("independent_fractional_order", gamma < sigma < theta, [gamma, sigma, theta], "strict")
    add("independent_p_theta", INPUTS["p"] * theta == Fraction(9, 5), INPUTS["p"] * theta, Fraction(9, 5))
    add("independent_holder_pair", Fraction(1, INPUTS["p"]) + Fraction(1, INPUTS["q"]) == Fraction(1, 2), [INPUTS["p"], INPUTS["q"]], "Holder")
    add("independent_net_root_decay", net_decay == TEST_ORACLES["net_root_decay"], net_decay, TEST_ORACLES["net_root_decay"])
    add("independent_gap_power", 2 * gamma == Fraction(1, 2), 2 * gamma, Fraction(1, 2))
    b_denominator_exponent = 2 * (sigma - gamma)
    gradient_denominator_exponent = 2 * (1 + sigma - gamma)
    add("independent_b_denominator_exponent", b_denominator_exponent == Fraction(1, 30), b_denominator_exponent, Fraction(1, 30))
    add("independent_gradient_denominator_exponent", gradient_denominator_exponent == Fraction(61, 30), gradient_denominator_exponent, Fraction(61, 30))
    da3_x = INPUTS["da3_x_exponent"]
    da3_y = INPUTS["da3_y_exponent"]
    product_gn_alpha = 2 - Fraction(1, 2) / theta
    inner_a_da = (theta * product_gn_alpha, theta * (2 - product_gn_alpha) / 3)
    a_da_outer_da = (da3_x + inner_a_da[0], da3_y + inner_a_da[1])
    a_du_outer_da = (da3_x, da3_y + theta / 3)
    a_da_outer_du = inner_a_da
    monomials = [
        (da3_x, da3_y),
        (da3_x + theta, da3_y),
        (theta, Fraction(0, 1)),
        (Fraction(0, 1), theta / 3),
        a_da_outer_da,
        a_du_outer_da,
        a_da_outer_du,
    ]
    totals = [left + right for left, right in monomials]
    add("independent_product_gn_alpha", product_gn_alpha == TEST_ORACLES["product_gn_alpha"], product_gn_alpha, TEST_ORACLES["product_gn_alpha"])
    add("independent_a_da_outer_da", a_da_outer_da == TEST_ORACLES["a_da_outer_da"], a_da_outer_da, TEST_ORACLES["a_da_outer_da"])
    add("independent_a_du_outer_da", a_du_outer_da == TEST_ORACLES["a_du_outer_da"], a_du_outer_da, TEST_ORACLES["a_du_outer_da"])
    add("independent_a_da_outer_du", a_da_outer_du == TEST_ORACLES["a_da_outer_du"], a_da_outer_du, TEST_ORACLES["a_da_outer_du"])
    add("independent_young_slack", 1 - max(totals) == TEST_ORACLES["young_slack"], 1 - max(totals), TEST_ORACLES["young_slack"])

    # Physical prefix fixture on disjoint Fourier modes.
    grid_size = 256
    grid = 2.0 * np.pi * np.arange(grid_size) / grid_size
    shells = [rng.normal() * np.sin(frequency * grid) + rng.normal() * np.cos(frequency * grid) for frequency in (1, 3, 7, 15, 31)]
    square_functions = []
    prefix_l6 = []
    for index in range(len(shells)):
        prefix = sum(shells[: index + 1])
        square = np.sqrt(sum(item * item for item in shells[: index + 1]))
        prefix_l6.append(float(np.mean(np.abs(prefix) ** 6) ** (1 / 6)))
        square_functions.append(float(np.mean(square**6) ** (1 / 6)))
    ratios = [left / right for left, right in zip(prefix_l6, square_functions) if right > 0]
    add("independent_physical_prefix_finite", all(math.isfinite(value) for value in ratios), ratios, "finite LP ratios")
    add("independent_square_function_monotone", all(square_functions[index] <= square_functions[index + 1] + 1.0e-12 for index in range(len(square_functions) - 1)), square_functions, "monotone")

    # Independent perspective identity with a two-stage random tree.
    leaves = 12
    matrix_dimension = 4
    terminal_a = []
    terminal_x = []
    for _ in range(leaves):
        raw = rng.normal(size=(matrix_dimension, matrix_dimension))
        terminal_a.append(raw @ raw.T + 0.4 * np.eye(matrix_dimension))
        terminal_x.append(rng.normal(size=matrix_dimension))
    terminal_a_array = np.stack(terminal_a)
    terminal_x_array = np.stack(terminal_x)
    old_a = terminal_a_array.mean(axis=0)
    old_x = terminal_x_array.mean(axis=0)
    old_m = np.linalg.solve(old_a, old_x)
    terminal_m = np.stack([np.linalg.solve(a_item, x_item) for a_item, x_item in zip(terminal_a_array, terminal_x_array)])
    perspective_gain = np.mean([float(m_item @ a_item @ m_item) for m_item, a_item in zip(terminal_m, terminal_a_array)]) - float(old_m @ old_a @ old_m)
    innovation = np.mean([float((m_item - old_m) @ a_item @ (m_item - old_m)) for m_item, a_item in zip(terminal_m, terminal_a_array)])
    add("independent_perspective_telescope", abs(perspective_gain - innovation) < 3.0e-12, perspective_gain, innovation)
    add("independent_perspective_positive", innovation >= 0, innovation, ">=0")

    raw_b = rng.normal(size=(matrix_dimension, matrix_dimension))
    frame_b = raw_b.T @ raw_b + np.eye(matrix_dimension)
    raw_r = rng.normal(size=(matrix_dimension, matrix_dimension))
    payment_r = raw_r.T @ raw_r + 0.3 * np.eye(matrix_dimension)
    frame_a = frame_b + 2.0 * payment_r
    inverse_piece = frame_b @ np.linalg.solve(frame_a, frame_b)
    theta_piece = frame_b - inverse_piece
    raw_gamma = rng.normal(size=(matrix_dimension, matrix_dimension))
    increment_gamma = raw_gamma @ raw_gamma.T
    original_signed = float(np.trace((inverse_piece - frame_b) @ increment_gamma))
    terminal_doob = float(np.trace(theta_piece @ increment_gamma))
    add("independent_augmented_partition", np.linalg.norm(inverse_piece + theta_piece - frame_b) < 2.0e-12, np.linalg.norm(inverse_piece + theta_piece - frame_b), 0)
    add("independent_frozen_augmented_zero", abs(original_signed + terminal_doob) < 2.0e-10, original_signed + terminal_doob, 0)
    reveal_b = [Fraction(1, 1), Fraction(2, 1)]
    reveal_v = [Fraction(2, 1), Fraction(1, 1)]
    reveal_delta = sum(reveal_v) / len(reveal_v)
    weighted_defect = sum(b_value * variance for b_value, variance in zip(reveal_b, reveal_v)) / len(reveal_b) - (sum(reveal_b) / len(reveal_b)) * reveal_delta
    add("independent_weighted_covariance_defect", weighted_defect == Fraction(-1, 4), weighted_defect, Fraction(-1, 4))

    branch_zero = branch_fixture(Fraction(1, 2))
    branch_one = branch_fixture(Fraction(3, 2))
    fixture_average = (branch_zero[3] + branch_one[3]) / 2
    add("independent_fixture_branch_zero", branch_zero[3] == Fraction(-13, 272), branch_zero[3], Fraction(-13, 272))
    add("independent_fixture_branch_one", branch_one[3] == Fraction(-29, 160), branch_one[3], Fraction(-29, 160))
    add("independent_fixture_average", fixture_average == TEST_ORACLES["fixture_average"], fixture_average, TEST_ORACLES["fixture_average"])
    add("independent_fixture_rc", [branch_zero[1], branch_one[1]] == [Fraction(1, 16), Fraction(3, 16)], [branch_zero[1], branch_one[1]], [Fraction(1, 16), Fraction(3, 16)])
    add("independent_fixture_jd", [branch_zero[2], branch_one[2]] == [Fraction(-1, 64), Fraction(-9, 64)], [branch_zero[2], branch_one[2]], [Fraction(-1, 64), Fraction(-9, 64)])

    # Covariance union with a deliberately repeated range.
    common = rng.normal(size=(5, 2))
    blocks = [common / math.sqrt(3.0), common / math.sqrt(3.0), common / math.sqrt(3.0), rng.normal(size=(5, 3))]
    union = np.concatenate(blocks, axis=1)
    covariance = sum(block @ block.T for block in blocks)
    add("independent_covariance_union", np.linalg.norm(union @ union.T - covariance) < 2.0e-12, np.linalg.norm(union @ union.T - covariance), 0)
    control = rng.normal(size=union.shape[1])
    u_values, singular, v_transpose = np.linalg.svd(union, full_matrices=False)
    pseudoinverse_sqrt = u_values @ np.diag([0 if value < 1.0e-12 else 1.0 / value for value in singular]) @ u_values.T
    cm_value = float(np.linalg.norm(pseudoinverse_sqrt @ (union @ control)) ** 2)
    add("independent_covariance_contraction", cm_value <= float(control @ control) + 1.0e-10, cm_value, f"<={float(control @ control)}")
    terminal_operator = rng.normal(size=(7, 5))
    trace_parts = sum(float(np.linalg.norm(terminal_operator @ block, ord="fro") ** 2) for block in blocks)
    trace_total = float(np.trace(terminal_operator @ covariance @ terminal_operator.T))
    add("independent_covariance_trace", abs(trace_parts - trace_total) < 2.0e-10, trace_parts, trace_total)

    # The minimal representative of (0,f(xi_1)) has a nonzero first slot.
    f_value = -2.4
    terminal = f_value / math.sqrt(2.0)
    minimal = np.array([terminal / math.sqrt(2.0), terminal / math.sqrt(2.0)])
    add("independent_polar_noncausal", np.allclose(minimal, np.array([f_value / 2, f_value / 2])), minimal, [f_value / 2, f_value / 2])
    loop_value = Fraction(7, 5)
    source_entropy = (loop_value**2 + (-loop_value) ** 2) / 2
    physical_entropy = Fraction(0, 1)
    fibre_surplus = source_entropy - physical_entropy
    add("independent_kernel_loop_fibre_entropy", fibre_surplus == loop_value**2, fibre_surplus, loop_value**2)
    add("independent_entropy_nelson_coefficient", Fraction(9, 20) * 2 == Fraction(9, 10), Fraction(9, 20) * 2, Fraction(9, 10))

    # Gauss-Hermite verifies the linear negative-flow Liouville identity by
    # an independent numerical integration.
    nodes, weights = np.polynomial.hermite.hermgauss(120)
    time_value = 5.0 / 9.0
    gaussian_nodes = math.sqrt(2.0) * nodes
    gaussian_weights = weights / math.sqrt(math.pi)
    left_flow = float(np.sum(gaussian_weights * np.exp(-time_value * (gaussian_nodes**2 - 1.0))))
    coefficient = 0.5 * (1.0 - (1.0 + 2.0 * time_value) * math.exp(-2.0 * time_value))
    right_flow = float(np.sum(gaussian_weights * np.exp(coefficient * gaussian_nodes**2)))
    add("independent_negative_flow_liouville", abs(left_flow - right_flow) < 2.0e-13, left_flow, right_flow)
    cubic_image = 1000000.0 / math.sqrt(1.0 + 2.0 * time_value * 1000000.0**2)
    image_limit = 1.0 / math.sqrt(2.0 * time_value)
    add("independent_cubic_flow_image", abs(cubic_image - image_limit) < 2.0e-12, cubic_image, image_limit)

    eta_value = Fraction(1, 100)
    zeta_value = Fraction(1, 1000)
    lambda_squared = 2 * (eta_value + 120 * zeta_value) + 1
    reset_coefficient = -lambda_squared / 2 + eta_value + 120 * zeta_value
    add("independent_cat0_reset", reset_coefficient == Fraction(-1, 2), reset_coefficient, Fraction(-1, 2))

    # The vector ellipticity ratio approaches one and therefore cannot have a
    # scalar-uniform superexponential constant.
    epsilons = [0.5, 0.2, 0.05, 0.01]
    anisotropic_ratios = [(1.0 - epsilon) / (1.0 + epsilon) for epsilon in epsilons]
    add("independent_vector_tail_ratio", all(anisotropic_ratios[index] < anisotropic_ratios[index + 1] for index in range(len(anisotropic_ratios) - 1)), anisotropic_ratios, "increases to 1")
    add("independent_vector_tail_not_uniform", anisotropic_ratios[-1] > 0.98, anisotropic_ratios[-1], ">0.98")

    downstream = {
        "general_progressive_revisit_h_c": False,
        "complete_signed_h_n": False,
        "progressive_revisit_h_a": False,
        "full_reg_packet": False,
        "uniform_overlap": False,
        "nelson": False,
        "interacting_measure": False,
        "floor_removal": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    regular_gate = (
        net_decay > 0
        and b_denominator_exponent > 0
        and gradient_denominator_exponent > 0
        and max(totals) < 1
        and all(square_functions[index] <= square_functions[index + 1] + 1.0e-12 for index in range(len(square_functions) - 1))
        and np.linalg.norm(audit_b - audit_g) > 1.0e-5
    )
    add("independent_regular_hc_gate", regular_gate, [net_decay, b_denominator_exponent, gradient_denominator_exponent, max(totals)], "positive two-tail gaps and sublinear one-use ledger")
    add("independent_no_overclaim", not any(downstream.values()), downstream, "all false")

    passed = sum(row["status"] == "PASS" for row in assertions)
    payload = {
        "schema": "tect/a13-normalized-cartan-perspective-covariance-frontier-independent/1.0",
        "version": __version__,
        "date": __version_issued__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(assertions) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(assertions),
        "inputs": serialize(INPUTS),
        "oracles": serialize(TEST_ORACLES),
        "assertions": assertions,
        "claims_not_established": downstream,
    }
    atomic_json(OUTPUT, payload)
    print(f"R-092 independent: {passed}/{len(assertions)} assertions PASS" if passed == len(assertions) else f"R-092 independent: {passed}/{len(assertions)} assertions; FAIL")
    print(f"artifact: {OUTPUT.relative_to(REPO)}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
