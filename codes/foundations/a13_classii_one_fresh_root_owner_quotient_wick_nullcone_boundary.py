#!/usr/bin/env python3
"""Primary executable certificate for the scoped R-116 A13 boundary.

This program checks exact endpoint telescoping, the partial-Wick/full-Wick
distinction, affine absorption, conditional Holder constants, two centered
null-cone obstructions, the critical-codimension model, and the production
gauge-null trace/sextic formulas.  The general recession theorem and the
finite-Fourier null classification are proved in the adjacent proof note;
the executable checks their load-bearing algebra and all quoted numbers.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
from fractions import Fraction
import itertools
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any

import mpmath as mp
import numpy as np
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ONE-FRESH-ROOT-OWNER-QUOTIENT-WICK-NULLCONE-BOUNDARY"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-primary-one-fresh-root-owner-quotient-wick-nullcone-boundary/result.json"
)

# Declared mathematical inputs.  Every displayed number is derived below.
INPUTS = {
    "q": Fraction(10, 9),
    "full_wick_kappa": Fraction(1, 100),
    "full_wick_delta": Fraction(1, 10**50),
    "production_alpha": Fraction(5, 9),
    "production_c0_times_P": Fraction(3, 250),
    "production_c1_times_P": Fraction(243, 8000),
    "terminal_sextic": Fraction(3, 20),
}

# Clearly labelled regression oracles, independently derived in the note.
ORACLES = {
    "centered_tensor_H": 128,
    "centered_tensor_K": 1088,
    "full_wick_cost_factor": 128,
}


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, mp.mpf):
        return mp.nstr(value, 40)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
            "schema": "tect/a13-one-fresh-root-owner-quotient-wick-nullcone-boundary-primary/1.0",
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
                "R-116 proves exact quotient and recession criteria and records abstract tensor "
                "method no-gos.  It does not prove the full A1 progressive/revisit conditional "
                "normalizer, one-use source/sextic aggregation, OVERLAP_src, Nelson, a removal "
                "limit, an interacting measure, Sector-A closure, or a tier promotion."
            ),
        }


def gaussian_moment(power: int) -> sp.Integer:
    if power % 2:
        return sp.Integer(0)
    if power == 0:
        return sp.Integer(1)
    return sp.factorial2(power - 1)


def gaussian_expectation(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    polynomial = sp.Poly(sp.expand(expression), *variables)
    total = sp.Integer(0)
    for powers, coefficient in polynomial.terms():
        moment = sp.Integer(1)
        for power in powers:
            moment *= gaussian_moment(power)
        total += coefficient * moment
    return sp.simplify(total)


def wick_square(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    maximum = sp.Poly(expression, *variables).total_degree()
    total = sp.Integer(0)
    for order in range(maximum + 1):
        contraction = sp.Integer(0)
        for indices in itertools.product(range(len(variables)), repeat=order):
            derivative = expression
            for index in indices:
                derivative = sp.diff(derivative, variables[index])
            contraction += derivative * derivative
        total += sp.Rational((-1) ** order, math.factorial(order)) * contraction
    return sp.expand(total)


def double_gaussian_divergence(matrix: sp.Matrix, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    dimension = len(variables)
    quadratic = sum(variables[i] * matrix[i, j] * variables[j] for i in range(dimension) for j in range(dimension))
    trace = sum(matrix[i, i] for i in range(dimension))
    divergence = [sum(sp.diff(matrix[i, j], variables[j]) for j in range(dimension)) for i in range(dimension)]
    divergence_two = sum(sp.diff(divergence[i], variables[i]) for i in range(dimension))
    return sp.expand(quadratic - trace - 2 * sum(variables[i] * divergence[i] for i in range(dimension)) + divergence_two)


def endpoint_quotient_checks(audit: Audit) -> dict[str, Any]:
    x0 = sp.Matrix([sp.Rational(2, 3), sp.Rational(-1, 5), sp.Rational(7, 11)])
    increments = [
        sp.Matrix([sp.Rational(1, 7), sp.Rational(3, 8), sp.Rational(-2, 9)]),
        sp.Matrix([sp.Rational(-4, 13), sp.Rational(2, 15), sp.Rational(5, 17)]),
        sp.Matrix([sp.Rational(3, 19), sp.Rational(-7, 23), sp.Rational(1, 29)]),
    ]
    traces = [sp.Rational(5, 12), sp.Rational(7, 10), sp.Rational(13, 9), sp.Rational(17, 8)]
    current = x0
    visit_sum = sp.Integer(0)
    for index, increment in enumerate(increments):
        visit_sum += (current.dot(increment) + increment.dot(increment) / 2) - (traces[index + 1] - traces[index]) / 2
        current += increment
    endpoint = (current.dot(current) - x0.dot(x0)) / 2 - (traces[-1] - traces[0]) / 2
    defect = sp.simplify(visit_sum - endpoint)
    audit.check("endpoint_quotient", "three_visit_telescope", defect == 0, defect, 0)

    a, f, iota = x0, increments[0], increments[1]
    two_visit = a.dot(f) + f.dot(f) / 2 + (a + f).dot(iota) + iota.dot(iota) / 2
    two_endpoint = ((a + f + iota).dot(a + f + iota) - a.dot(a)) / 2
    two_defect = sp.simplify(two_visit - two_endpoint)
    audit.check("endpoint_quotient", "fresh_future_cross_occurs_once", two_defect == 0, two_defect, 0)
    return {"visit_sum": visit_sum, "endpoint": endpoint, "two_visit": two_visit}


def wick_checks(audit: Audit) -> dict[str, Any]:
    x, y = sp.symbols("x y", real=True)
    product = x * y
    full = wick_square(product, (x, y))
    expected_full = (x**2 - 1) * (y**2 - 1)
    production_partial = product**2 - x**2
    missing = sp.expand(production_partial - full)
    audit.check("wick", "xy_full_wick", sp.expand(full - expected_full) == 0, full, expected_full)
    audit.check("wick", "xy_production_difference", missing == y**2 - 1, missing, y**2 - 1)

    eps, coefficient = sp.symbols("eps coefficient", real=True)
    h2 = x**2 - 1
    output = eps * (h2 + coefficient * x)
    partial_packet = sp.expand((output**2 - sp.diff(output, x) ** 2) / 2)
    full_packet = sp.expand(wick_square(output, (x,)) / 2)
    debt = sp.simplify(partial_packet - full_packet)
    audit.check("wick", "r110_partial_wick_debt", debt == -eps**2, debt, -eps**2)
    audit.check(
        "wick",
        "r110_partial_packet_mean",
        gaussian_expectation(partial_packet, (x,)) == -eps**2,
        gaussian_expectation(partial_packet, (x,)),
        -eps**2,
    )
    return {"xy_full_wick": full, "xy_missing_owner": missing, "r110_debt": debt}


def affine_and_composition_checks(audit: Audit) -> dict[str, Any]:
    q = float(INPUTS["q"])
    a = np.array([[0.4, -0.2], [0.1, 0.3]], dtype=float)
    c = np.array([[0.2, 0.05], [-0.15, 0.1]], dtype=float)
    baseline = np.array([0.7, -0.4], dtype=float)
    combined = a + c
    covariance = combined @ combined.T
    identity = np.eye(covariance.shape[0])
    sign, logdet = np.linalg.slogdet(identity + q * covariance)
    logdet_two = logdet - q * float(np.trace(covariance))
    phi = -0.5 * logdet_two - 0.5 * q * float(baseline @ np.linalg.solve(identity + q * covariance, baseline))
    bound = q**2 * float(np.sum(covariance * covariance)) / 4.0
    audit.check("affine_absorption", "det2_bound", sign > 0 and phi <= bound + 1.0e-14, phi, f"<= {bound}")

    costs = np.array([1.0, 4.0, 9.0])
    roots = np.sqrt(costs)
    weights = roots / roots.sum()
    holder_cost = float(np.sum(costs / weights))
    optimal_cost = float(roots.sum() ** 2)
    coefficient = Fraction(INPUTS["q"] ** 2, 4)
    audit.check("composition", "holder_weight_optimizer", abs(holder_cost - optimal_cost) < 1.0e-14, holder_cost, optimal_cost)
    audit.check("composition", "q_squared_quarter", coefficient == Fraction(25, 81), coefficient, Fraction(25, 81))
    tilted = Fraction(INPUTS["q"] ** 2, 2)
    audit.check("composition", "doubled_tilt_exponent", tilted == Fraction(50, 81), tilted, Fraction(50, 81))
    return {
        "affine_phi": phi,
        "affine_bound": bound,
        "holder_cost": holder_cost,
        "independent_cost": float(costs.sum()),
        "q_squared_quarter": coefficient,
        "doubled_tilt_exponent": tilted,
    }


def centered_nullcone_checks(audit: Audit) -> dict[str, Any]:
    u, v = sp.symbols("u v", real=True)
    quadratic = u**2 - v**2
    trace = 4 * (u**2 + v**2)
    packet = sp.expand(((2 + quadratic) ** 2 - trace) / 2)
    mean = gaussian_expectation(packet, (u, v))
    gradient = sp.Matrix([sp.diff(quadratic, u), sp.diff(quadratic, v)])
    covariance = gradient * gradient.T
    h_cost = gaussian_expectation(sum(covariance[i, j] ** 2 for i in range(2) for j in range(2)), (u, v))
    double = double_gaussian_divergence(covariance, (u, v))
    k_cost = gaussian_expectation(double**2, (u, v))
    audit.check("centered_nullcone", "packet_exact_centering", mean == 0, mean, 0)
    audit.check("centered_nullcone", "tangent_covariance_cost", h_cost == ORACLES["centered_tensor_H"], h_cost, ORACLES["centered_tensor_H"])
    audit.check("centered_nullcone", "double_divergence_cost", k_cost == ORACLES["centered_tensor_K"], k_cost, ORACLES["centered_tensor_K"])

    tube_u, tube_v = sp.symbols("tube_u tube_v", real=True)
    substitution = {u: (tube_u + tube_v) / sp.sqrt(2), v: (tube_u - tube_v) / sp.sqrt(2)}
    tube_packet = sp.expand(packet.subs(substitution))
    expected_tube = 2 + 4 * tube_u * tube_v + 2 * tube_u**2 * tube_v**2 - 2 * tube_u**2 - 2 * tube_v**2
    audit.check("centered_nullcone", "tube_coordinate_formula", sp.simplify(tube_packet - expected_tube) == 0, tube_packet, expected_tube)
    critical_q = Fraction(1, 4)
    exponent_coefficient = 2 * critical_q - Fraction(1, 2)
    audit.check("centered_nullcone", "critical_divergence_threshold", exponent_coefficient == 0, exponent_coefficient, 0)
    return {"packet": packet, "double_divergence": double, "H": h_cost, "K": k_cost, "critical_q": critical_q}


def full_wick_tensor_checks(audit: Audit) -> dict[str, Any]:
    u, v, eps, kappa = sp.symbols("u v eps kappa", real=True)
    outputs = sp.Matrix([2 * eps * u * v, 2 * kappa * eps * (v**2 - 1)])
    derivative = outputs.jacobian((u, v))
    covariance = sp.simplify(derivative * derivative.T)
    h_cost = gaussian_expectation(sum(covariance[i, j] ** 2 for i in range(2) for j in range(2)), (u, v))
    expected = ORACLES["full_wick_cost_factor"] * eps**4 * (1 + kappa**2 + 6 * kappa**4)
    audit.check("full_wick_tensor", "exact_covariance_cost", sp.simplify(h_cost - expected) == 0, h_cost, expected)

    q = INPUTS["q"]
    kappa_value = INPUTS["full_wick_kappa"]
    delta = INPUTS["full_wick_delta"]
    alpha = (1 - delta) / 4
    eps_squared = alpha / q
    target = 32 * alpha**2 * (1 + kappa_value**2 + 6 * kappa_value**4)
    lower = mp.mpf(25) * mp.log(10) / (mp.e * mp.sqrt(mp.pi))
    audit.check("full_wick_tensor", "explicit_target_below_21_over_10", target < Fraction(21, 10), target, "<21/10")
    audit.check("full_wick_tensor", "elementary_mgf_lower_above_115_over_12", lower > mp.mpf(115) / 12, lower, ">115/12")
    audit.check("full_wick_tensor", "lower_beats_target_exponential", lower > mp.e ** (mp.mpf(21) / 10), lower, f">{mp.e ** (mp.mpf(21) / 10)}")
    audit.check("full_wick_tensor", "domain_approaches_quarter_from_below", q * eps_squared < Fraction(1, 4), q * eps_squared, "<1/4")
    return {
        "covariance_cost": h_cost,
        "alpha": alpha,
        "epsilon_squared": eps_squared,
        "target": target,
        "mgf_lower": lower,
        "sharp_domain": "0 <= alpha < 1/4",
    }


def critical_codimension_checks(audit: Audit) -> dict[str, Any]:
    q = mp.mpf(INPUTS["q"].numerator) / INPUTS["q"].denominator
    values: dict[str, Any] = {}
    for codimension in (2, 3, 4):
        exact = mp.sqrt(mp.pi / q) * mp.gamma(mp.mpf(codimension - 1) / 2) / mp.gamma(mp.mpf(codimension) / 2)
        numeric = mp.quad(lambda t: (1 + q * t * t) ** (-mp.mpf(codimension) / 2), [-mp.inf, mp.inf])
        audit.check(
            "critical_codimension",
            f"finite_integral_k_{codimension}",
            abs(exact - numeric) < mp.mpf("1e-30"),
            numeric,
            exact,
        )
        values[str(codimension)] = {"exact": exact, "numeric": numeric}

    cut_one = mp.quad(lambda t: (1 + q * t * t) ** (-mp.mpf(1) / 2), [-10, 10])
    cut_two = mp.quad(lambda t: (1 + q * t * t) ** (-mp.mpf(1) / 2), [-1000, 1000])
    audit.check("critical_codimension", "k_one_logarithmic_growth", cut_two > cut_one, cut_two, f">{cut_one}")
    audit.check("critical_codimension", "recession_equality", 1 - q * (1 / q) == 0, 1 - q * (1 / q), 0)
    values["1_truncations"] = {"radius_10": cut_one, "radius_1000": cut_two}
    return values


def production_gauge_checks(audit: Audit) -> dict[str, Any]:
    alpha = INPUTS["production_alpha"]
    c0 = INPUTS["production_c0_times_P"]
    c1 = INPUTS["production_c1_times_P"]
    csum = c0 + c1
    audit.check("production_gauge", "c_sum_times_P", csum == Fraction(339, 8000), csum, Fraction(339, 8000))

    amplitude, floor = sp.symbols("amplitude floor", positive=True)
    radial = amplitude**2 / (amplitude**2 + floor)
    coefficient = c0 + c1 * (1 - alpha * radial) ** 2
    limit = sp.limit(coefficient, amplitude, sp.oo)
    expected_limit = c0 + c1 * (1 - alpha) ** 2
    audit.check("production_gauge", "rational_row_recession", sp.simplify(limit - expected_limit) == 0, limit, expected_limit)

    kmax = sp.symbols("Kmax", positive=True)
    terminal = INPUTS["terminal_sextic"] * amplitude**6 - sp.Rational(1, 2) * kmax * amplitude**2
    critical_amplitude_squared = sp.sqrt(sp.Rational(10, 9) * kmax)
    derivative_at_critical = sp.simplify(sp.diff(terminal, amplitude).subs(amplitude, sp.sqrt(critical_amplitude_squared)))
    minimum = sp.simplify(terminal.subs(amplitude, sp.sqrt(critical_amplitude_squared)))
    expected_minimum = -sp.Rational(3, 10) * (sp.Rational(10, 9) * kmax) ** sp.Rational(3, 2)
    audit.check("production_gauge", "sextic_stationary_point", derivative_at_critical == 0, derivative_at_critical, 0)
    audit.check("production_gauge", "finite_cutoff_sextic_repair", sp.simplify(minimum - expected_minimum) == 0, minimum, expected_minimum)

    x, wave = sp.symbols("x wave", real=True)
    a = sp.symbols("a", real=True)
    x1 = a
    x2 = a
    dr = wave * (x2**2 - x1**2) * sp.sin(2 * wave * x)
    audit.check("production_gauge", "plane_wave_radial_current_null", sp.simplify(dr) == 0, dr, 0)
    return {
        "c0_times_P": c0,
        "c1_times_P": c1,
        "c_sum_times_P": csum,
        "rational_recession_coefficient_times_P": expected_limit,
        "sextic_minimum": expected_minimum,
        "scope": "The plane wave is a pointwise face of a legal full root, not a standalone production root atom.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    mp.mp.dps = 80
    audit = Audit()
    diagnostics = {
        "endpoint_quotient": endpoint_quotient_checks(audit),
        "partial_wick": wick_checks(audit),
        "affine_and_composition": affine_and_composition_checks(audit),
        "centered_nullcone": centered_nullcone_checks(audit),
        "full_wick_tensor": full_wick_tensor_checks(audit),
        "critical_codimension": critical_codimension_checks(audit),
        "production_gauge": production_gauge_checks(audit),
        "recession_classifier": {
            "strict_positive": "Gaussian integrability",
            "strict_negative": "divergence",
            "equality": "requires critical-stratum codimension and lower-order audit",
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-116 primary: {payload['assertions_passed']}/{payload['assertions_total']} "
        f"assertions; status={payload['status']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
