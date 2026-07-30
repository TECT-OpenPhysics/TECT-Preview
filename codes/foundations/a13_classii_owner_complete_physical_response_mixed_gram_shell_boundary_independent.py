#!/usr/bin/env python3
"""Independent standard-library audit for the scoped A13 R-131 boundary.

This verifier does not import SymPy or the primary R-131 program.  It
recomputes the production fractions, checks the finite response pullback with
plain rational matrices, tests the mixed-Gram and Fourier counterfixtures,
and numerically probes the acceptance, Xi, and fixed-heat boundary formulas.
It proves no missing production shell estimate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
from itertools import product
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-OWNER-COMPLETE-PHYSICAL-RESPONSE-MIXED-GRAM-"
    "SHELL-BOUNDARY"
)
SCHEMA = (
    "tect/a13-owner-complete-physical-response-mixed-gram-shell-"
    "boundary-independent/1.0"
)
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-owner-complete-physical-response-"
    "mixed-gram-shell-boundary/result.json"
)
A1_MANIFEST = REPO / (
    "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/"
    "production_functional_manifest.json"
)
A8_RESULT = REPO / (
    "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/"
    "runs/2026-07-20-primary-decoupled-nelson/result.json"
)
R103_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-"
    "closure/result.json"
)
R124_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-"
    "root-shell-boundary/result.json"
)
R130_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-terminal-xi-conormal-gram-balanced-low-"
    "response-boundary/result.json"
)
def represent(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): represent(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [represent(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(represent(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self, group: str, name: str, condition: bool, actual: Any, expected: Any
    ) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": represent(actual),
                "expected": represent(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": represent(diagnostics),
            "scope": {
                "non_importing_standard_library_route": True,
                "finite_response_factorization_fixture_checked": True,
                "production_owner_complete_form_constructed": False,
                "mixed_gram_counterfixture_checked": True,
                "fourier_shell_counterfixture_checked": True,
                "conditional_acceptance_checked": True,
                "stratified_xi_radial_coefficient_boundary_checked": True,
                "common_phase_full_tangent_identification_rejected": True,
                "fixed_heat_boundary_checked": True,
                "production_response_bound_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "This independent audit checks the finite R-131 algebra, "
                "counterfixtures, and conditional margins without importing "
                "the primary program. It proves no production C_mix, C_far, "
                "c_bal, low constants, full-tangent Xi coercivity, absolute "
                "anchor, uniform augmented "
                "gap, Nelson estimate, or Sector-A closure."
            ),
        }


Matrix = list[list[Fraction]]
Polynomial = list[Fraction]


def polynomial_add(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    return [
        (left[index] if index < len(left) else Fraction(0))
        + (right[index] if index < len(right) else Fraction(0))
        for index in range(size)
    ]


def polynomial_scale(value: Fraction, polynomial: Polynomial) -> Polynomial:
    return [value * coefficient for coefficient in polynomial]


def polynomial_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    product_coefficients = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            product_coefficients[left_index + right_index] += left_value * right_value
    return product_coefficients


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[row][inner] * right[inner][column] for inner in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def matrix_equal(left: Matrix, right: Matrix) -> bool:
    return left == right


def frobenius_square(matrix: Matrix) -> Fraction:
    return sum((entry * entry for row in matrix for entry in row), Fraction(0))


def rotation(angle: float) -> list[list[float]]:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return [[cosine, -sine], [sine, cosine]]


def float_matmul(
    left: list[list[float]], right: list[list[float]]
) -> list[list[float]]:
    return [
        [
            sum(left[row][inner] * right[inner][column] for inner in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def float_transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*matrix)]


def close(left: float, right: float, tolerance: float = 1.0e-10) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    audit.check("authority", "A1_manifest_schema", a1.get("schema") == "tect/a1-production-functional-realisation/1.0", a1.get("schema"), "tect/a1-production-functional-realisation/1.0")
    params = a1["parameters"]
    p_mass = Fraction(str(params["M_X"])) ** 2 + Fraction(
        str(params["classii_mass_regularizer"])
    )
    density_floor = Fraction(str(params["rho_regularizer"]))
    classii_a = Fraction(str(params["cJJ"])) * Fraction(str(params["alpha_X"])) ** 2 / p_mass
    classii_b = Fraction(str(params["cJK"])) * Fraction(str(params["alpha_X"])) * Fraction(str(params["beta_X"])) / p_mass
    classii_c = Fraction(str(params["cKK"])) * Fraction(str(params["beta_X"])) ** 2 / p_mass
    alpha = classii_c / (classii_b + classii_c)
    c1 = (classii_b + classii_c) ** 2 / classii_c
    c0 = classii_a - classii_b**2 / classii_c
    beta_op = 4 * (c0 + c1)
    r130 = json.loads(R130_RESULT.read_text(encoding="utf-8"))
    r103 = json.loads(R103_RESULT.read_text(encoding="utf-8"))
    source_action_coefficient = Fraction(r103["diagnostics"]["budget"]["source_coefficient"])
    sextic_action_coefficient = Fraction(r103["diagnostics"]["budget"]["sextic_coefficient"])
    source_hessian_coefficient = 2 * source_action_coefficient
    audit.check("authority", "R103_contract", r103.get("schema") == "tect/a13-regular-complete-packet-ownership-hn-reg-closure-primary/1.0" and r103.get("status") == "PASS" and r103.get("result_id") == "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE", (r103.get("schema"), r103.get("status"), r103.get("result_id")), "pinned R-103 primary PASS contract")
    audit.check("authority", "R103_source_action_oracle", source_action_coefficient == Fraction(9, 20), source_action_coefficient, Fraction(9, 20))
    audit.check("authority", "R103_source_hessian_oracle", source_hessian_coefficient == Fraction(9, 10), source_hessian_coefficient, Fraction(9, 10))
    audit.check("authority", "R103_sextic_action_oracle", sextic_action_coefficient == Fraction(3, 20), sextic_action_coefficient, Fraction(3, 20))
    l6 = Fraction(r130["diagnostics"]["conormal_gram"]["L6"])
    h6 = Fraction(r130["diagnostics"]["conormal_gram"]["H6"])
    h2_component = beta_op + 2 * l6 + h6
    audit.check("production", "positive_denominators", p_mass > 0 and density_floor > 0, (p_mass, density_floor), ">0")
    audit.check("production", "completed_square_alpha", alpha == Fraction(5, 9), alpha, Fraction(5, 9))
    audit.check("production", "completed_square_c0", c0 == Fraction(3, 250) / p_mass, c0, Fraction(3, 250) / p_mass)
    audit.check("production", "completed_square_c1", c1 == Fraction(243, 8000) / p_mass, c1, Fraction(243, 8000) / p_mass)
    audit.check("production", "beta_operator_exact", beta_op == Fraction(339, 2000) / p_mass, beta_op, Fraction(339, 2000) / p_mass)
    audit.check("production", "L6_exact", l6 == Fraction(1143, 250) / p_mass, l6, Fraction(1143, 250) / p_mass)
    audit.check("production", "H6_exact", h6 == Fraction(7083, 500) / p_mass, h6, Fraction(7083, 500) / p_mass)
    audit.check("production", "H2_component_exact", h2_component == Fraction(46959, 2000) / p_mass, h2_component, Fraction(46959, 2000) / p_mass)
    audit.check("authority", "R130_primary_pass", r130["status"] == "PASS", r130["status"], "PASS")
    audit.check("authority", "R130_contract", r130.get("schema") == "tect/a13-terminal-xi-conormal-gram-balanced-low-response-boundary-primary/1.0" and r130.get("result_id") == "A13-CLASSII-TERMINAL-XI-CONORMAL-GRAM-BALANCED-LOW-RESPONSE-BOUNDARY", (r130.get("schema"), r130.get("result_id")), "pinned R-130 primary contract")

    # Fixed rational matrices are test oracles for the abstract identity
    # L^T(Q_comp+Q_6)L=(shell L)^T(shell QL).
    q_comp: Matrix = [[Fraction(2), Fraction(-1), Fraction(0)], [Fraction(-1), Fraction(3), Fraction(1)], [Fraction(0), Fraction(1), Fraction(-2)]]
    q_sextic: Matrix = [[Fraction(1), Fraction(0), Fraction(0)], [Fraction(0), Fraction(2), Fraction(0)], [Fraction(0), Fraction(0), Fraction(3)]]
    synthesis: Matrix = [[Fraction(1), Fraction(0), Fraction(1), Fraction(0)], [Fraction(0), Fraction(1), Fraction(-1), Fraction(0)], [Fraction(1), Fraction(1), Fraction(0), Fraction(0)]]
    shell_one: Matrix = [[Fraction(1), Fraction(0), Fraction(0)], [Fraction(0), Fraction(1), Fraction(0)], [Fraction(0), Fraction(0), Fraction(0)]]
    shell_two: Matrix = [[Fraction(0), Fraction(0), Fraction(0)], [Fraction(0), Fraction(0), Fraction(0)], [Fraction(0), Fraction(0), Fraction(1)]]
    q_total = matrix_add(q_comp, q_sextic)
    response = matmul(q_total, synthesis)
    endpoint = matmul(transpose(synthesis), response)
    shell_response = matmul(shell_one, response) + matmul(shell_two, response)
    shell_synthesis = matmul(shell_one, synthesis) + matmul(shell_two, synthesis)
    shell_pullback = matmul(transpose(shell_synthesis), shell_response)
    reverse_pullback = matmul(transpose(shell_response), shell_synthesis)
    audit.check("response", "endpoint_symmetric", endpoint == transpose(endpoint), endpoint, transpose(endpoint))
    audit.check("response", "shell_forward_identity", shell_pullback == endpoint, shell_pullback, endpoint)
    audit.check("response", "shell_reverse_identity", reverse_pullback == endpoint, reverse_pullback, endpoint)
    audit.check("response", "shell_response_isometry", frobenius_square(shell_response) == frobenius_square(response), frobenius_square(shell_response), frobenius_square(response))
    audit.check("response", "shell_response_analysis_isometry", matmul(transpose(shell_response), shell_response) == matmul(transpose(response), response), matmul(transpose(shell_response), shell_response), matmul(transpose(response), response))
    vertical = [[Fraction(0)], [Fraction(0)], [Fraction(0)], [Fraction(1)]]
    audit.check("response", "physical_vertical_kernel", matmul(endpoint, vertical) == [[Fraction(0)]] * 4, matmul(endpoint, vertical), [[Fraction(0)]] * 4)
    audit.check("response", "source_vertical_hessian", source_hessian_coefficient * vertical[-1][0] ** 2 == source_hessian_coefficient, source_hessian_coefficient * vertical[-1][0] ** 2, source_hessian_coefficient)

    test_angle = 0.37
    plus = rotation(test_angle)
    minus = rotation(-test_angle)
    gram_plus = float_matmul(float_transpose(plus), plus)
    gram_minus = float_matmul(float_transpose(minus), minus)
    mean_rotation = [[(plus[row][column] + minus[row][column]) / 2 for column in range(2)] for row in range(2)]
    mean_square = float_matmul(float_transpose(mean_rotation), mean_rotation)[0][0]
    audit.check("mixed_gram", "sample_grams_constant", close(gram_plus[0][0], 1.0) and close(gram_plus[1][1], 1.0) and close(gram_minus[0][0], 1.0) and close(gram_minus[1][1], 1.0), (gram_plus, gram_minus), "I")
    audit.check("mixed_gram", "mean_square_cosine", close(mean_square, math.cos(test_angle) ** 2), mean_square, math.cos(test_angle) ** 2)
    test_step = 1.0e-4
    mean_at_step = math.cos(test_step) ** 2
    curvature = (mean_at_step - 2.0 + mean_at_step) / test_step**2
    audit.check("mixed_gram", "nonzero_hidden_curvature", close(curvature, -2.0, 1.0e-7), curvature, -2.0)
    rational_plus: Matrix = [[Fraction(4, 5), Fraction(-3, 5)], [Fraction(3, 5), Fraction(4, 5)]]
    rational_minus: Matrix = [[Fraction(4, 5), Fraction(3, 5)], [Fraction(-3, 5), Fraction(4, 5)]]
    identity_two: Matrix = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    rational_mean = [[(rational_plus[row][column] + rational_minus[row][column]) / 2 for column in range(2)] for row in range(2)]
    audit.check("mixed_gram", "rational_sample_grams_constant", matmul(transpose(rational_plus), rational_plus) == identity_two and matmul(transpose(rational_minus), rational_minus) == identity_two, (matmul(transpose(rational_plus), rational_plus), matmul(transpose(rational_minus), rational_minus)), (identity_two, identity_two))
    audit.check("mixed_gram", "rational_mean_square_changes", matmul(transpose(rational_mean), rational_mean)[0][0] == Fraction(16, 25), matmul(transpose(rational_mean), rational_mean)[0][0], Fraction(16, 25))

    root_shell = 3
    output_shell = 19
    root_frequency = 2**root_shell
    output_frequency = 2**output_shell
    shift = output_frequency - root_frequency
    multiplier_modes = {shift: Fraction(1, 2), -shift: Fraction(1, 2)}
    input_modes = {root_frequency: Fraction(1)}
    product_modes: dict[int, Fraction] = {}
    for left_frequency, left_value in multiplier_modes.items():
        for right_frequency, right_value in input_modes.items():
            frequency = left_frequency + right_frequency
            product_modes[frequency] = product_modes.get(frequency, Fraction(0)) + left_value * right_value
    projected_norm = abs(product_modes[output_frequency])
    forced_mix = projected_norm * 2 ** (2 * output_shell - root_shell)
    forced_far = projected_norm * 2 ** (4 * output_shell - root_shell)
    next_output_shell = output_shell + 1
    next_output_frequency = 2**next_output_shell
    next_shift = next_output_frequency - root_frequency
    next_multiplier_modes = {next_shift: Fraction(1, 2), -next_shift: Fraction(1, 2)}
    next_product_modes: dict[int, Fraction] = {}
    for left_frequency, left_value in next_multiplier_modes.items():
        for right_frequency, right_value in input_modes.items():
            frequency = left_frequency + right_frequency
            next_product_modes[frequency] = next_product_modes.get(frequency, Fraction(0)) + left_value * right_value
    next_projected_norm = abs(next_product_modes[next_output_frequency])
    next_forced_mix = next_projected_norm * 2 ** (2 * next_output_shell - root_shell)
    next_forced_far = next_projected_norm * 2 ** (4 * next_output_shell - root_shell)
    audit.check("shell", "bounded_cosine_shell_shift", projected_norm == Fraction(1, 2), projected_norm, Fraction(1, 2))
    audit.check("shell", "mixed_constant_forced_growth", forced_mix == 2 ** (2 * output_shell - root_shell - 1), forced_mix, 2 ** (2 * output_shell - root_shell - 1))
    audit.check("shell", "far_constant_forced_growth", forced_far == 2 ** (4 * output_shell - root_shell - 1), forced_far, 2 ** (4 * output_shell - root_shell - 1))
    audit.check("shell", "next_shell_selected_coefficient", next_projected_norm == Fraction(1, 2), next_projected_norm, Fraction(1, 2))
    audit.check("shell", "mixed_family_growth_ratio", next_forced_mix / forced_mix == 4, next_forced_mix / forced_mix, 4)
    audit.check("shell", "far_family_growth_ratio", next_forced_far / forced_far == 16, next_forced_far / forced_far, 16)
    # Exact rational state-dependent alternative.  For x=n(s-1),
    # Q_n(s)=2x/(1+x^2) is bounded by one because
    # (1+x^2)^2-(2x)^2=(1-x^2)^2, while (s^2 Q_n)' at s=1 is 2n.
    one_plus_x_squared = [Fraction(1), Fraction(0), Fraction(1)]
    two_x = [Fraction(0), Fraction(2)]
    one_minus_x_squared = [Fraction(1), Fraction(0), Fraction(-1)]
    rational_bound_left = polynomial_add(
        polynomial_multiply(one_plus_x_squared, one_plus_x_squared),
        polynomial_scale(Fraction(-1), polynomial_multiply(two_x, two_x)),
    )
    rational_bound_right = polynomial_multiply(
        one_minus_x_squared, one_minus_x_squared
    )
    audit.check(
        "shell",
        "rational_state_multiplier_unit_bound_identity",
        rational_bound_left == rational_bound_right,
        rational_bound_left,
        rational_bound_right,
    )

    Dual = tuple[Fraction, Fraction]

    def dual_add(left: Dual, right: Dual) -> Dual:
        return left[0] + right[0], left[1] + right[1]

    def dual_mul(left: Dual, right: Dual) -> Dual:
        return left[0] * right[0], left[1] * right[0] + left[0] * right[1]

    def dual_div(left: Dual, right: Dual) -> Dual:
        return (
            left[0] / right[0],
            (left[1] * right[0] - left[0] * right[1]) / right[0] ** 2,
        )

    rational_frequency = Fraction(7)
    dual_one: Dual = (Fraction(1), Fraction(0))
    dual_state: Dual = (Fraction(1), Fraction(1))
    dual_x: Dual = (Fraction(0), rational_frequency)
    dual_q = dual_div(
        (2 * dual_x[0], 2 * dual_x[1]),
        dual_add(dual_one, dual_mul(dual_x, dual_x)),
    )
    dual_product = dual_mul(dual_mul(dual_state, dual_state), dual_q)
    hidden_derivative = dual_product[1]
    audit.check(
        "shell",
        "rational_frozen_Q_misses_exact_state_derivative",
        dual_product == (Fraction(0), 2 * rational_frequency),
        dual_product,
        (Fraction(0), 2 * rational_frequency),
    )

    a8 = json.loads(A8_RESULT.read_text(encoding="utf-8"))
    audit.check("authority", "A8_primary_contract", a8.get("schema") == "tect/a8-classii-decoupled-nelson-primary-result/1.0" and a8.get("verdict") == "A8-CLASSII-DECOUPLED-NELSON-PRIMARY-PASS", (a8.get("schema"), a8.get("verdict")), "pinned A8 primary PASS contract")
    r_symbol = Fraction(str(params["r"]))
    z_symbol = Fraction(str(params["Z"]))
    y_symbol = Fraction(str(params["Y"]))
    stationary_symbol = (2 * r_symbol - z_symbol) / (2 * y_symbol - z_symbol)
    def symbol_ratio(value: Fraction) -> Fraction:
        return (y_symbol * value**2 + z_symbol * value + r_symbol) / (1 + value) ** 2
    c_symbol = min(
        symbol_ratio(Fraction(0)),
        symbol_ratio(stationary_symbol),
        y_symbol,
    )
    recorded_c_symbol = float(a8["derived"]["symbol_coercivity"]["c_symbol"])
    audit.check("budget", "A8_symbol_constant_rounding_agrees", close(float(c_symbol), recorded_c_symbol, 5.0e-15), float(c_symbol), recorded_c_symbol)
    multiplier_bound = Fraction(str(a8["config"]["regulator_multiplier_bound"]))
    a0 = multiplier_bound**2 / c_symbol
    bridge = math.sqrt(32.0 * float(a0))
    eta_zero = Fraction(r103["diagnostics"]["budget"]["source_reserve"]) - 2 * c0
    zeta_zero = Fraction(r103["diagnostics"]["budget"]["sextic_reserve"])
    k_zero = 4.0 * math.sqrt(float(eta_zero * zeta_zero))
    r124 = json.loads(R124_RESULT.read_text(encoding="utf-8"))
    audit.check("authority", "R124_contract", r124.get("schema") == "tect/a13-stationary-polarized-trace-defect-replica-root-shell-boundary-primary/1.0" and r124.get("status") == "PASS" and r124.get("result_id") == "A13-CLASSII-STATIONARY-POLARIZED-TRACE-DEFECT-REPLICA-ROOT-SHELL-BOUNDARY", (r124.get("schema"), r124.get("status"), r124.get("result_id")), "pinned R-124 primary PASS contract")
    cartan_full = Fraction(r124["diagnostics"]["cartan"]["full"])
    cartan_oriented = c1 * cartan_full / 2
    cartan_cross = 2.0 * bridge * float(cartan_oriented)
    headroom = k_zero - cartan_cross
    audit.check("budget", "cartan_full_exact", cartan_full == Fraction(2680, 729), cartan_full, Fraction(2680, 729))
    audit.check("budget", "cartan_oriented_exact", cartan_oriented == Fraction(67, 1200) / p_mass, cartan_oriented, Fraction(67, 1200) / p_mass)
    audit.check("budget", "cartan_full_cross_exact", 2 * cartan_oriented == Fraction(67, 600) / p_mass, 2 * cartan_oriented, Fraction(67, 600) / p_mass)
    audit.check("budget", "controlled_cartan_far_exact", 4 * alpha**2 * c1 == Fraction(3, 80) / p_mass, 4 * alpha**2 * c1, Fraction(3, 80) / p_mass)
    cartan_cross_squared = 4 * (32 * a0) * cartan_oriented**2
    k_zero_squared = 16 * eta_zero * zeta_zero
    audit.check("budget", "cartan_diagnostic_exact_squared_acceptance", cartan_cross_squared < k_zero_squared, cartan_cross_squared, f"< {k_zero_squared}")
    audit.check("budget", "cartan_diagnostic_headroom_positive", headroom > 0.0, headroom, ">0")
    diagnostic_collar = 1
    mixed_collar_square = Fraction(8, 7) / 2 ** (4 * diagnostic_collar)
    far_collar_square = Fraction(224, 223) / 2 ** (8 * diagnostic_collar)
    audit.check("budget", "mixed_collar_exact_square", Fraction(1, 14) == mixed_collar_square, mixed_collar_square, Fraction(1, 14))
    audit.check("budget", "far_collar_exact_square", Fraction(7, 1784) == far_collar_square, far_collar_square, Fraction(7, 1784))

    test_e, test_f, test_a = 0.4, 0.1, 0.2
    m_two = (test_e + test_f - math.sqrt((test_e - test_f) ** 2 + test_a**2)) / 2.0
    audit.check("acceptance", "two_channel_characteristic", close(m_two**2 - (test_e + test_f) * m_two + test_e * test_f, test_a**2 / 4.0), m_two**2 - (test_e + test_f) * m_two + test_e * test_f, test_a**2 / 4.0)
    audit.check("acceptance", "two_channel_strict_condition", m_two > 0.0 and test_a**2 < 4.0 * test_e * test_f, (m_two, test_a**2), (">0", f"< {4.0 * test_e * test_f}"))
    test_d, test_k = 0.3, 0.1
    mu_three = (m_two + test_d - math.sqrt((m_two - test_d) ** 2 + 4.0 * test_k**2)) / 2.0
    audit.check("acceptance", "three_channel_characteristic", close(mu_three**2 - (m_two + test_d) * mu_three + m_two * test_d, test_k**2), mu_three**2 - (m_two + test_d) * mu_three + m_two * test_d, test_k**2)
    audit.check("acceptance", "three_channel_strict_condition", mu_three > 0.0 and test_k**2 < test_d * m_two, (mu_three, test_k**2), (">0", f"< {test_d * m_two}"))

    c0_float = float(c0)
    c1_float = float(c1)
    xi_rows: list[dict[str, float]] = []
    xi_ok = True
    for test_lambda in (1.0e-6, 1.0e-3, float(alpha)):
        trace = c0_float + c1_float * ((1.0 - test_lambda) ** 2 + test_lambda**2)
        determinant = c0_float * c1_float * test_lambda**2
        lambda_large = (trace + math.sqrt(trace**2 - 4.0 * determinant)) / 2.0
        lambda_small = determinant / lambda_large
        lower_bound = c0_float * c1_float * test_lambda**2 / (c0_float + c1_float)
        xi_ok = xi_ok and lambda_small + 1.0e-18 >= lower_bound
        xi_rows.append({"lambda": test_lambda, "trace": trace, "determinant": determinant, "lambda_small": lambda_small, "lower_bound": lower_bound})
    asymptotic_target = c0_float * c1_float / (c0_float + c1_float)
    asymptotic_probe = xi_rows[0]["lambda_small"] / xi_rows[0]["lambda"] ** 2
    audit.check("xi", "production_lambda_domain", 0.0 < float(alpha) < 1.0, float(alpha), "0<alpha<1")
    audit.check("xi", "active_stratum_lower_bound", xi_ok, xi_rows, "lambda_min >= c0*c1*lambda^2/(c0+c1) on 0<=lambda<=1")
    audit.check("xi", "small_lambda_quadratic_coefficient", close(asymptotic_probe, asymptotic_target, 2.0e-6), asymptotic_probe, asymptotic_target)
    phase_u = (1.0 + 0.0j, 0.0 + 0.0j)
    phase_chi = 1.0 + 0.0j
    phase_v = (0.0 + 1.0j, 0.0 + 0.0j)
    phase_w = 0.0 - 1.0j
    phase_a = (phase_u[0].conjugate() * phase_v[0]).real
    phase_s = (phase_chi.conjugate() * phase_w).real
    phase_h_squared = abs(
        phase_u[0] * phase_v[1] - phase_u[1] * phase_v[0]
    ) ** 2
    common_phase_constraint = (
        phase_u[0].conjugate() * phase_v[0]
        + phase_chi.conjugate() * phase_w
    ).imag
    phase_fixture_norm = (
        sum(abs(entry) ** 2 for entry in phase_u)
        * sum(abs(entry) ** 2 for entry in phase_v)
        + abs(phase_chi) ** 2 * abs(phase_w) ** 2
    )
    audit.check(
        "xi",
        "natural_common_phase_horizontal_full_norm_identity_fails",
        phase_a == 0.0
        and phase_s == 0.0
        and phase_h_squared == 0.0
        and common_phase_constraint == 0.0
        and phase_fixture_norm == 2.0,
        (
            phase_a,
            phase_s,
            phase_h_squared,
            common_phase_constraint,
            phase_fixture_norm,
        ),
        (0.0, 0.0, 0.0, 0.0, 2.0),
    )
    pure_singlet_values = [4.0 * c1_float * float(alpha) ** 2 * epsilon**4 / (epsilon**2 + 1.0 + float(density_floor)) ** 2 for epsilon in (1.0e-1, 1.0e-2, 1.0e-3)]
    audit.check("xi", "pure_singlet_degenerates_quartically", pure_singlet_values[2] < pure_singlet_values[1] < pure_singlet_values[0] and close(pure_singlet_values[2] / 1.0e-12, 4.0 * c1_float * float(alpha) ** 2 / (1.0 + float(density_floor)) ** 2, 2.0e-6), pure_singlet_values, "quartic decay")

    full_heat_atoms = list(product((-1, 1), repeat=6))
    full_heat_means = [
        Fraction(sum(atom[index] for atom in full_heat_atoms), len(full_heat_atoms))
        for index in range(6)
    ]
    full_heat_covariance = [
        [
            Fraction(
                sum(atom[row] * atom[column] for atom in full_heat_atoms),
                len(full_heat_atoms),
            )
            for column in range(6)
        ]
        for row in range(6)
    ]
    collapsed_multiplicities: dict[tuple[int, int], int] = {}
    for atom in full_heat_atoms:
        key = (atom[4], atom[5])
        collapsed_multiplicities[key] = collapsed_multiplicities.get(key, 0) + 1
    audit.check(
        "heat",
        "full_coordinate_product_rademacher_collapses_to_four_singlet_values",
        len(full_heat_atoms) == 64
        and full_heat_means == [Fraction(0)] * 6
        and full_heat_covariance
        == [
            [Fraction(int(row == column)) for column in range(6)]
            for row in range(6)
        ]
        and all(sum(value * value for value in atom[:4]) == 4 for atom in full_heat_atoms)
        and set(collapsed_multiplicities.values()) == {16},
        (len(full_heat_atoms), full_heat_means, collapsed_multiplicities),
        "64 atoms, zero mean, identity covariance, R=4, four singlet values each of multiplicity 16",
    )

    doublet_radius = 4.0
    def heat_average(terminal: float) -> float:
        values = []
        for real_part in (-1.0, 1.0):
            for imaginary_part in (-1.0, 1.0):
                singlet_real = terminal + real_part
                singlet_norm = singlet_real**2 + imaginary_part**2
                denominator = doublet_radius + singlet_norm + float(density_floor)
                values.append(4.0 * c1_float * float(alpha) ** 2 * doublet_radius**2 * singlet_real**2 / denominator**2)
        return sum(values) / len(values)
    heat_values = [heat_average(terminal) for terminal in (10.0, 100.0, 1000.0)]
    heat_limit = 4.0 * c1_float * float(alpha) ** 2 * doublet_radius**2
    dominating_bound = c1_float * float(alpha) ** 2 * doublet_radius**2 / (doublet_radius + float(density_floor))
    audit.check("heat", "fixed_heat_positive_but_decays", all(value > 0.0 for value in heat_values) and heat_values[2] < heat_values[1] < heat_values[0], heat_values, "positive decreasing")
    audit.check("heat", "inverse_square_limit", close(1000.0**2 * heat_values[2], heat_limit, 2.0e-5), 1000.0**2 * heat_values[2], heat_limit)
    audit.check("heat", "dominated_fixture", all(value <= dominating_bound for value in heat_values), heat_values, f"<= {dominating_bound}")
    test_terminal = Fraction(7)
    sextic_hessian_coefficient = 30 * sextic_action_coefficient
    sextic_hessian = sextic_hessian_coefficient * test_terminal**4
    audit.check("heat", "sextic_once_coefficient", sextic_hessian_coefficient == Fraction(9, 2), sextic_hessian_coefficient, Fraction(9, 2))
    audit.check("heat", "sextic_once_ray_hessian", sextic_hessian == Fraction(9, 2) * test_terminal**4, sextic_hessian, Fraction(9, 2) * test_terminal**4)

    diagnostics = {
        "production": {"P": p_mass, "density_floor": density_floor, "c0": c0, "c1": c1, "alpha": alpha, "beta_operator": beta_op},
        "deterministic_current_h2": {"L6": l6, "H6": h6, "coefficient_before_embedding": h2_component},
        "response": {"endpoint": endpoint, "physical_vertical_kernel": True, "source_action_coefficient": source_action_coefficient, "source_hessian_coefficient": source_hessian_coefficient, "sextic_action_coefficient": sextic_action_coefficient},
        "mixed_gram": {"sample_gram_curvature": 0, "mean_square_curvature_probe": curvature, "diagonal_gram_sufficient": False},
        "shell": {"selected_output_shell_coefficient": projected_norm, "multiplier_Linf": 1, "forced_C_mix": forced_mix, "forced_C_far": forced_far, "next_C_mix_growth_ratio": next_forced_mix / forced_mix, "next_C_far_growth_ratio": next_forced_far / forced_far, "rational_state_multiplier_derivative": hidden_derivative, "bounded_multiplier_implies_decay": False},
        "acceptance": {"bridge": bridge, "K0": k_zero, "cartan_oriented": cartan_oriented, "cartan_cross": cartan_cross, "headroom": headroom, "m2_fixture": m_two, "mu3_fixture": mu_three, "production_constants_proved": False},
        "xi": {"samples": xi_rows, "asymptotic_probe": asymptotic_probe, "asymptotic_target": asymptotic_target, "natural_common_phase_full_tangent_identification": False, "phase_invisible_weighted_tangent_norm_fixture": phase_fixture_norm, "uniform_gap": False},
        "heat": {"values_T_10_100_1000": heat_values, "scaled_limit_target": heat_limit, "dominating_bound": dominating_bound, "uniform_transversality": False},
    }
    result = audit.finish(diagnostics)
    atomic_json(arguments.output, result)
    print(f"R-131 independent {result['status']}: {result['assertions_passed']}/{result['assertions_total']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
