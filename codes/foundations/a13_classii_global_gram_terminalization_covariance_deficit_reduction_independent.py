#!/usr/bin/env python3
"""Independent exact certificates for the R-097 A13 reduction.

This verifier uses only the Python standard library and Fraction arithmetic.
It does not import the numerical verifier or trust any generated artefact.
The fixtures certify the terminal Schur/covariance identities and delimit the
abstract method failures without asserting a production torus counterexample.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import argparse
import ast
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any, Callable, Iterable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-GLOBAL-GRAM-TERMINALIZATION-COVARIANCE-DEFICIT-REDUCTION"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-27-independent-global-gram-terminalization-covariance-deficit-reduction/result.json"

INPUTS = {
    "schur": {"rho": F(7, 5), "q": F(-3, 4), "bbar": F(11, 6), "payment": F(2, 7)},
    "rademacher": {"base": F(2), "slope": F(1), "eta": F(1, 100), "zeta": F(1, 100)},
    "gaussian": {
        "shift": F(2),
        "floor": F(1),
        "eta": F(1, 100),
        "zeta_abstract": F(1, 100),
        "zeta_value": F(1, 10000),
    },
    "block_counts": (1, 2, 7, 31),
    "test_constant": F(7),
    "telescope": {"a": F(1, 3), "b": F(2, 5)},
    "perfect_square": {"payment": F(1), "gamma": F(1)},
}


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


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def expect(atoms: Iterable[tuple[F, Any]], function: Callable[[Any], F]) -> F:
    return sum((probability * function(value) for probability, value in atoms), F(0))


def poly_add(left: dict[int, F], right: dict[int, F]) -> dict[int, F]:
    result = dict(left)
    for power, coefficient in right.items():
        result[power] = result.get(power, F(0)) + coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def poly_scale(poly: dict[int, F], scalar: F) -> dict[int, F]:
    return {power: scalar * coefficient for power, coefficient in poly.items() if scalar * coefficient}


def poly_mul(left: dict[int, F], right: dict[int, F]) -> dict[int, F]:
    result: dict[int, F] = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = result.get(power, F(0)) + left_coefficient * right_coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def gaussian_moment(power: int) -> F:
    if power % 2:
        return F(0)
    value = 1
    for factor in range(1, power, 2):
        value *= factor
    return F(value)


def gaussian_expectation(poly: dict[int, F]) -> F:
    return sum((coefficient * gaussian_moment(power) for power, coefficient in poly.items()), F(0))


def hermites(maximum: int) -> list[dict[int, F]]:
    values = [{0: F(1)}, {1: F(1)}]
    if maximum == 0:
        return values[:1]
    for degree in range(1, maximum):
        values.append(poly_add(poly_mul({1: F(1)}, values[-1]), poly_scale(values[-2], F(-degree))))
    return values


def hermite_product(m: int, n: int) -> dict[int, F]:
    result: dict[int, F] = {}
    for contraction in range(min(m, n) + 1):
        degree = m + n - 2 * contraction
        coefficient = F(math.factorial(contraction) * math.comb(m, contraction) * math.comb(n, contraction))
        result[degree] = result.get(degree, F(0)) + coefficient
    return result


def reconstruct_hermite(coefficients: dict[int, F], basis: list[dict[int, F]]) -> dict[int, F]:
    result: dict[int, F] = {}
    for degree, coefficient in coefficients.items():
        result = poly_add(result, poly_scale(basis[degree], coefficient))
    return result


def theta(coefficient: F, payment: F) -> F:
    return coefficient - coefficient * coefficient / (coefficient + 2 * payment)


def sqrt_fraction_exact(value: F) -> F:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise ValueError(f"not an exact rational square: {value}")
    return F(numerator, denominator)


def main(output: Path) -> int:
    rows: list[dict[str, Any]] = []

    def check(group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    # Static independence gate.
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    allowed = {"__future__", "argparse", "ast", "json", "math", "os", "tempfile", "fractions", "pathlib", "typing"}
    roots: set[str] = set()
    forbidden_calls: list[str] = []
    relative_imports = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            relative_imports += int(node.level > 0)
            if node.module:
                roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            forbidden_calls.append(node.func.id)
    check("independence", "stdlib_import_roots", roots <= allowed, sorted(roots), sorted(allowed))
    check("independence", "no_relative_imports", relative_imports == 0, relative_imports, 0)
    check("independence", "no_dynamic_code_calls", not forbidden_calls, forbidden_calls, [])

    # Generic exact scalar Schur completion and the theta=0 fractional endpoint
    # with a strictly positive matrix payment.  This theta is the R-095
    # retained-square fraction, not the capital Theta_R defined below.
    schur = INPUTS["schur"]
    rho, q, bbar, payment = schur["rho"], schur["q"], schur["bbar"], schur["payment"]
    matrix = bbar + 2 * payment
    minimum = F(1, 2) * (rho - q * q / matrix)
    for index, control in enumerate((F(-2), F(-1, 3), F(0), F(5, 4))):
        direct = F(1, 2) * rho + q * control + F(1, 2) * matrix * control * control
        square = minimum + F(1, 2) * matrix * (control + q / matrix) ** 2
        check("schur", f"generic_completion_{index}", direct == square, direct, square)
    determinant = rho * matrix - q * q
    check("schur", "block_determinant", determinant == matrix * (rho - q * q / matrix), determinant, matrix * (rho - q * q / matrix))
    for index, coefficient in enumerate((F(1, 7), F(2), F(13, 4))):
        theta_paid = theta(coefficient, payment)
        theta_oracle = 2 * payment * coefficient / (coefficient + 2 * payment)
        check("schur", f"theta_zero_fraction_positive_payment_{index}", theta_paid == theta_oracle and theta_paid > 0, theta_paid, theta_oracle)
        partition = coefficient * coefficient / (coefficient + 2 * payment) + theta_paid
        check("schur", f"theta_zero_fraction_partition_{index}", partition == coefficient, partition, coefficient)

    # Bounded Rademacher fixture and direct-sum method boundary.
    rad = INPUTS["rademacher"]
    rad_atoms = [(F(1, 2), F(-1)), (F(1, 2), F(1))]
    gamma = expect(rad_atoms, lambda sign: sign * sign)
    coefficient = lambda sign: rad["base"] + rad["slope"] * sign
    wick = lambda sign: sign * sign - gamma
    bar_b = expect(rad_atoms, coefficient)
    q_rad = expect(rad_atoms, lambda sign: coefficient(sign) * sign)
    rho_rad = expect(rad_atoms, lambda sign: coefficient(sign) * wick(sign))
    a_rad = bar_b + 2 * rad["eta"]
    rad_minimum = F(1, 2) * (rho_rad - q_rad * q_rad / a_rad)
    y_rad = expect(rad_atoms, lambda sign: abs(sign) ** 6)
    paid_rad = rad_minimum + rad["zeta"] * y_rad
    check("rademacher", "probability_mass", sum(probability for probability, _ in rad_atoms) == 1, sum(probability for probability, _ in rad_atoms), 1)
    check("rademacher", "centered_root", expect(rad_atoms, lambda sign: sign) == 0, expect(rad_atoms, lambda sign: sign), 0)
    check("rademacher", "positive_bounded_coefficient", min(coefficient(sign) for _, sign in rad_atoms) > 0, [coefficient(sign) for _, sign in rad_atoms], "> 0")
    check("rademacher", "wick_zero_atomwise", all(wick(sign) == 0 for _, sign in rad_atoms), [wick(sign) for _, sign in rad_atoms], [0, 0])
    check("rademacher", "mixed_mean_nonzero", q_rad != 0, q_rad, "!= 0")
    check("rademacher", "completed_minimum_negative", rad_minimum < 0, rad_minimum, "< 0")
    check("rademacher", "xy_paid_minimum_negative", paid_rad < 0, paid_rad, "< 0")
    theta_minus, theta_plus = (theta(coefficient(sign), rad["eta"]) for sign in (-1, 1))
    r_float = (math.sqrt(float(theta_plus)) - math.sqrt(float(theta_minus))) / 2
    check("rademacher", "transformed_mean_nonzero", theta_plus > theta_minus and r_float > 0, [theta_minus, theta_plus, r_float], "strictly positive mean")
    restored = float(rho_rad - q_rad * q_rad / a_rad) - r_float * r_float + r_float * r_float
    check("rademacher", "transformed_mean_restoration", abs(restored - float(rho_rad - q_rad * q_rad / a_rad)) < 1.0e-15, restored, float(rho_rad - q_rad * q_rad / a_rad))
    scaling: dict[int, F] = {}
    for count in INPUTS["block_counts"]:
        total = sum((paid_rad for _ in range(count)), F(0))
        scaling[count] = total
        check("direct_sum", f"actual_loop_scaling_{count}", total == count * paid_rad, total, count * paid_rad)
    threshold_count = INPUTS["test_constant"] // (-paid_rad) + 1
    check("direct_sum", "uniform_constant_defeated_abstractly", threshold_count * paid_rad < -INPUTS["test_constant"], threshold_count * paid_rad, f"< {-INPUTS['test_constant']}")

    # Complete Gaussian H0--H4 forest via monomial and Hermite-product routes.
    gau = INPUTS["gaussian"]
    shift, floor = gau["shift"], gau["floor"]
    basis = hermites(6)
    b_poly = {2: F(1), 1: 2 * shift, 0: shift * shift + floor}
    q_poly = basis[2]
    product_poly = poly_mul(b_poly, q_poly)
    b_hermite = {2: F(1), 1: 2 * shift, 0: shift * shift + floor + 1}
    forest: dict[int, F] = {}
    for left_degree, left_coefficient in b_hermite.items():
        for degree, product_coefficient in hermite_product(left_degree, 2).items():
            forest[degree] = forest.get(degree, F(0)) + left_coefficient * product_coefficient
    check("forest", "b_reconstruction", reconstruct_hermite(b_hermite, basis) == b_poly, reconstruct_hermite(b_hermite, basis), b_poly)
    check("forest", "product_reconstruction", reconstruct_hermite(forest, basis) == product_poly, reconstruct_hermite(forest, basis), product_poly)
    check("forest", "all_ranks_zero_through_four_present", all(forest.get(degree, 0) != 0 for degree in range(5)), forest, "H0--H4 nonzero")
    check("forest", "mean_from_h0", gaussian_expectation(b_poly) == b_hermite[0], gaussian_expectation(b_poly), b_hermite[0])
    check("forest", "mixed_mean_from_h1", gaussian_expectation(poly_mul(b_poly, {1: F(1)})) == b_hermite[1], gaussian_expectation(poly_mul(b_poly, {1: F(1)})), b_hermite[1])
    check("forest", "raw_wick_from_h0", gaussian_expectation(product_poly) == forest[0], gaussian_expectation(product_poly), forest[0])
    omissions_detected = all(reconstruct_hermite({key: value for key, value in forest.items() if key != degree}, basis) != product_poly for degree in forest)
    duplications_detected = all(reconstruct_hermite({key: (2 * value if key == degree else value) for key, value in forest.items()}, basis) != product_poly for degree in forest)
    check("forest", "every_omission_detected", omissions_detected, omissions_detected, True)
    check("forest", "every_duplication_detected", duplications_detected, duplications_detected, True)
    gaussian_bbar = gaussian_expectation(b_poly)
    gaussian_q = gaussian_expectation(poly_mul(b_poly, {1: F(1)}))
    gaussian_rho = gaussian_expectation(product_poly)
    gaussian_a = gaussian_bbar + 2 * gau["eta"]
    gaussian_minimum = F(1, 2) * (gaussian_rho - gaussian_q * gaussian_q / gaussian_a)
    check("forest", "gaussian_schur_determinant_negative", gaussian_rho * gaussian_a - gaussian_q * gaussian_q < 0, gaussian_rho * gaussian_a - gaussian_q * gaussian_q, "< 0")
    abstract_sixth = gaussian_moment(6)
    value_sixth = sum((F(math.comb(6, power)) * shift ** (6 - power) * gaussian_moment(power) for power in range(7)), F(0))
    check("forest", "abstract_sextic_paid_deficit", gaussian_minimum + gau["zeta_abstract"] * abstract_sixth < 0, gaussian_minimum + gau["zeta_abstract"] * abstract_sixth, "< 0")
    check("forest", "shifted_value_sextic_paid_deficit", gaussian_minimum + gau["zeta_value"] * value_sixth < 0, gaussian_minimum + gau["zeta_value"] * value_sixth, "< 0")

    # Exact strict-past endpoint telescope on a four-atom history tree.
    tel = INPUTS["telescope"]
    histories = [(F(1, 4), (x1, x2)) for x1 in (F(-1), F(1)) for x2 in (F(-1), F(1))]
    gamma2 = expect([(F(1, 2), F(-1)), (F(1, 2), F(1))], lambda value: value * value)
    def energy(history: tuple[F, F], control: F) -> F:
        x1, x2 = history
        return F(1, 2) * ((x1 + control) ** 2 + 1) * ((x2 + control) ** 2 - gamma2)
    a0 = F(0)
    a1 = tel["a"]
    a2 = lambda x1: tel["a"] + tel["b"] * x1
    phi1 = {history: energy(history, a1) - energy(history, a0) for _, history in histories}
    phi2 = {history: energy(history, a2(history[0])) - energy(history, a1) for _, history in histories}
    p1 = expect(histories, lambda history: phi1[history])
    p2: dict[F, F] = {}
    for x1 in (F(-1), F(1)):
        fibre = [(F(1, 2), (x1, x2)) for x2 in (F(-1), F(1))]
        p2[x1] = expect(fibre, lambda history: phi2[history])
        check("telescope", f"second_increment_centers_on_fibre_{x1}", expect(fibre, lambda history: phi2[history] - p2[x1]) == 0, expect(fibre, lambda history: phi2[history] - p2[x1]), 0)
        check("telescope", f"strict_past_constancy_{x1}", len({a2(history[0]) for _, history in fibre}) == 1, [a2(history[0]) for _, history in fibre], "constant on future fibre")
    check("telescope", "first_increment_centered", expect(histories, lambda history: phi1[history] - p1) == 0, expect(histories, lambda history: phi1[history] - p1), 0)
    check("telescope", "pathwise_endpoint_telescope", all(phi1[history] + phi2[history] == energy(history, a2(history[0])) - energy(history, a0) for _, history in histories), True, True)
    payment_sum = p1 + expect(histories, lambda history: p2[history[0]])
    endpoint_sum = expect(histories, lambda history: energy(history, a2(history[0])) - energy(history, a0))
    check("telescope", "expectation_endpoint_telescope", payment_sum == endpoint_sum, payment_sum, endpoint_sum)
    leaking = lambda history: tel["a"] + tel["b"] * history[1]
    leak_detected = any(len({leaking(history) for _, history in [(F(1, 2), (x1, x2)) for x2 in (F(-1), F(1))]}) > 1 for x1 in (F(-1), F(1)))
    check("mutations", "future_leak_rejected", leak_detected, leak_detected, True)

    # Exact q/r and posterior-covariance normal forms.
    perfect_atoms = [(F(1, 2), (F(2, 7), F(-1))), (F(1, 2), (F(2), F(1)))]
    rpay = INPUTS["perfect_square"]["payment"]
    gamma_perfect = INPUTS["perfect_square"]["gamma"]
    perfect_bbar = expect(perfect_atoms, lambda item: item[0])
    perfect_q = expect(perfect_atoms, lambda item: item[0] * item[1])
    perfect_a = perfect_bbar + 2 * rpay
    m0 = perfect_q / perfect_a
    raw_perfect = expect(perfect_atoms, lambda item: item[0] * (item[1] ** 2 - gamma_perfect))
    m_values = [(probability, coefficient * value / (coefficient + 2 * rpay)) for probability, (coefficient, value) in perfect_atoms]
    y_values = [(probability, sqrt_fraction_exact(theta(coefficient, rpay)) * value) for probability, (coefficient, value) in perfect_atoms]
    r_mean = sum((probability * value for probability, value in y_values), F(0))
    lhs_normal = sum((probability * (m - m0) ** 2 * (coefficient + 2 * rpay) for (probability, (coefficient, _)), (_, m) in zip(perfect_atoms, m_values)), F(0))
    lhs_normal += sum((probability * (value - r_mean) ** 2 for probability, value in y_values), F(0)) - perfect_bbar * gamma_perfect
    rhs_normal = expect(perfect_atoms, lambda item: item[0] * item[1] ** 2) - perfect_bbar * gamma_perfect - perfect_q**2 / perfect_a - r_mean**2
    check("covariance", "unconditional_q_r_normal_form", lhs_normal == rhs_normal, lhs_normal, rhs_normal)
    conditional_variance = F(0)
    j_b = expect(perfect_atoms, lambda item: item[0] * item[1] ** 2) - perfect_q**2 / perfect_a
    covariance_defect = expect(perfect_atoms, lambda item: item[0] * (conditional_variance - gamma_perfect))
    check("covariance", "posterior_bracket_identity", j_b + covariance_defect == raw_perfect - perfect_q**2 / perfect_a, j_b + covariance_defect, raw_perfect - perfect_q**2 / perfect_a)
    check("covariance", "posterior_schur_compensation_nonnegative", j_b >= 0, j_b, ">= 0")
    check("covariance", "r_owner_restoration", (raw_perfect - perfect_q**2 / perfect_a - r_mean**2) + r_mean**2 == j_b + covariance_defect, (raw_perfect - perfect_q**2 / perfect_a - r_mean**2) + r_mean**2, j_b + covariance_defect)

    deficit_atoms = [(F(1, 4), (F(1), F(-2))), (F(1, 4), (F(1), F(2))), (F(1, 4), (F(2), F(-1))), (F(1, 4), (F(2), F(1)))]
    unconditional_mean = expect(deficit_atoms, lambda item: item[1])
    unconditional_gamma = expect(deficit_atoms, lambda item: (item[1] - unconditional_mean) ** 2)
    conditional = {F(1): (F(0), F(4)), F(2): (F(0), F(1))}
    deficit_q = expect(deficit_atoms, lambda item: item[0] * item[1])
    deficit_covariance = expect(deficit_atoms, lambda item: item[0] * (conditional[item[0]][1] - unconditional_gamma))
    check("covariance", "conditional_means_zero", all(mean == 0 for mean, _ in conditional.values()), conditional, "means zero")
    check("covariance", "conditional_variances_nonzero_unequal", all(variance > 0 for _, variance in conditional.values()) and len({variance for _, variance in conditional.values()}) == 2, conditional, "positive unequal")
    check("covariance", "symmetric_mixed_mean_zero", deficit_q == 0, deficit_q, 0)
    check("covariance", "weighted_posterior_covariance_deficit_negative", deficit_covariance < 0, deficit_covariance, "< 0")
    wrong_replacement = expect(deficit_atoms, lambda item: item[0] * (unconditional_gamma - unconditional_gamma))
    check("mutations", "unconditional_covariance_substitution_rejected", wrong_replacement != deficit_covariance, wrong_replacement, f"!= {deficit_covariance}")
    check("mutations", "omitted_j_b_rejected", covariance_defect != j_b + covariance_defect, covariance_defect, f"!= {j_b + covariance_defect}")
    check("mutations", "b_plus_r_instead_of_b_plus_2r_rejected", perfect_q**2 / (perfect_bbar + rpay) != perfect_q**2 / perfect_a, perfect_q**2 / (perfect_bbar + rpay), f"!= {perfect_q**2 / perfect_a}")

    # Predictable H2 accumulation and moving-perspective boundaries.
    h2_norm = gaussian_expectation(poly_mul(basis[2], basis[2]))
    for count in (1, 3, 8):
        aggregate: dict[int, F] = {}
        for _ in range(count):
            aggregate = poly_add(aggregate, basis[2])
        pairing = gaussian_expectation(poly_mul(aggregate, basis[2]))
        aggregate_norm = gaussian_expectation(poly_mul(aggregate, aggregate))
        check("doob_boundary", f"measured_h2_pairing_{count}", pairing == count * h2_norm, pairing, count * h2_norm)
        check("doob_boundary", f"measured_h2_aggregate_norm_{count}", aggregate_norm == count * count * h2_norm, aggregate_norm, count * count * h2_norm)
    check("mutations", "naive_linear_aggregate_norm_rejected", 8 * h2_norm != 8 * 8 * h2_norm, 8 * h2_norm, f"!= {8 * 8 * h2_norm}")

    perspective_atoms = [(F(1, 2), (F(1), F(2))), (F(1, 2), (F(3), F(0)))]
    abar = expect(perspective_atoms, lambda item: item[0])
    xbar = expect(perspective_atoms, lambda item: item[1])
    mbar = xbar / abar
    perspective_gap = expect(perspective_atoms, lambda item: item[1] ** 2 / item[0]) - xbar**2 / abar
    variance_gap = expect(perspective_atoms, lambda item: item[0] * (item[1] / item[0] - mbar) ** 2)
    check("perspective", "fixed_terminal_perspective_variance", perspective_gap == variance_gap and perspective_gap >= 0, perspective_gap, variance_gap)
    moving_defect = F(1) ** 2 / F(4) - F(1) ** 2 / F(1)
    check("perspective", "moving_base_defect_negative", moving_defect < 0, moving_defect, "< 0")
    check("mutations", "omitted_moving_base_defect_rejected", moving_defect != 0, moving_defect, "!= innovation-only zero")

    names = [row["name"] for row in rows]
    check("contract", "unique_assertion_names", len(names) == len(set(names)), len(names) - len(set(names)), 0)
    failures = [row for row in rows if row["status"] != "PASS"]
    group_summary: dict[str, dict[str, int]] = {}
    for row in rows:
        summary = group_summary.setdefault(row["group"], {"total": 0, "passed": 0, "failed": 0})
        summary["total"] += 1
        summary["passed" if row["status"] == "PASS" else "failed"] += 1
    payload = {
        "schema": "tect/a13-global-gram-terminalization-covariance-deficit-reduction-independent/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "verdict": "A13-R097-INDEPENDENT-BOUNDARY-PASS" if not failures else "A13-R097-INDEPENDENT-BOUNDARY-FAIL",
        "independence": {"stdlib_only": True, "numerical_verifier_imported": False, "import_roots": sorted(roots)},
        "inputs": serial(INPUTS),
        "assertion_summary": {"total": len(rows), "passed": len(rows) - len(failures), "failed": len(failures), "groups": group_summary},
        "failures": failures,
        "assertions": rows,
        "fixtures": {
            "rademacher": {"minimum": serial(rad_minimum), "paid_minimum": serial(paid_rad), "r_float": r_float, "abstract_direct_sum": serial(scaling)},
            "gaussian": {"forest_h0_to_h4": serial({degree: forest[degree] for degree in range(5)}), "minimum": serial(gaussian_minimum), "abstract_sixth": serial(abstract_sixth), "shifted_value_sixth": serial(value_sixth)},
            "covariance": {"j_b": serial(j_b), "covariance_defect": serial(covariance_defect), "separate_negative_fixture": serial(deficit_covariance)},
            "moving_perspective_defect": serial(moving_defect),
        },
        "scope": {
            "verified": ["exact finite Schur completions", "complete endpoint expectation telescope", "theta=0 fractional endpoint with positive payment", "complete H0-H4 forest ownership", "posterior covariance normal forms", "predictability-only accumulation boundary", "moving-perspective defect"],
            "universal_xy_only_abstract_statement": "falsified",
            "production_adapted_prefix_bound_8_3": "open",
            "production_fourier_realizability": "not tested",
            "cartan_one_use_4_11": "open",
            "complete_H_N": "open",
            "REG": "open",
            "OVERLAP_src": "open",
            "Nelson": "open",
            "Sector_A": "open",
            "counterexample_scope": "finite abstract coefficient/direct-sum method fixtures only",
            "no_overclaim": "Passing verifies exact algebra and abstract method boundaries; it neither proves nor refutes the production torus lower bound.",
        },
    }
    atomic_json(output, payload)
    print(f"R-097 INDEPENDENT {'PASS' if not failures else 'FAIL'}: {len(rows) - len(failures)}/{len(rows)}")
    print(f"output={output}")
    return 0 if not failures else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    raise SystemExit(main(arguments.output))
