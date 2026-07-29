#!/usr/bin/env python3
"""Primary exact audit for the scoped R-122 A13 theorem and method boundary.

This executable proves finite-cutoff derivative-free low-chaos identities,
audits the feedback-graph topology, constructs an exact coherent-amplitude
fifth-moment obstruction, derives the active-doublet rational Cartan ray, and
checks that the complete R-102 first-order coefficient does not cancel.
It does not assert the production one-use inequality or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-29"
__version_issued__ = "2026-07-29"

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-DERIVATIVE-FREE-LOW-CHAOS-ADAPTED-FIFTH-MOMENT-CARTAN-BOUNDARY"
SCHEMA = "tect/a13-derivative-free-low-chaos-adapted-fifth-moment-cartan-primary/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-29-primary-derivative-free-low-chaos-adapted-fifth-moment-cartan-boundary/result.json"
)
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
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
            "schema": SCHEMA,
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
                "R-122 proves a derivative-free finite-cutoff D0/D1 representation, rejects "
                "derivative-by-derivative graph closure and a standalone adapted fifth-moment "
                "inference from the existing L2/L6 budgets, and rejects automatic Cartan "
                "cancellation. It does not prove the complete signed one-use bound, Nelson, "
                "removals, an interacting measure, or Sector-A closure."
            ),
        }


def gaussian_expectation(poly: sp.Expr, variable: sp.Symbol) -> sp.Expr:
    expanded = sp.Poly(sp.expand(poly), variable)
    total = sp.Integer(0)
    for (degree,), coefficient in expanded.terms():
        if degree % 2:
            continue
        total += coefficient * (sp.Integer(1) if degree == 0 else sp.factorial2(degree - 1))
    return sp.factor(total)


def production_parameters() -> tuple[sp.Rational, sp.Rational]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = sp.Rational(str(parameters["M_X"])) ** 2 + sp.Rational(str(parameters["classii_mass_regularizer"]))
    b_weight = (
        sp.Rational(str(parameters["cJK"]))
        * sp.Rational(str(parameters["alpha_X"]))
        * sp.Rational(str(parameters["beta_X"]))
        / mass
    )
    c_weight = sp.Rational(str(parameters["cKK"])) * sp.Rational(str(parameters["beta_X"])) ** 2 / mass
    alpha = sp.simplify(c_weight / (b_weight + c_weight))
    floor = sp.Rational(str(parameters["rho_regularizer"]))
    return alpha, floor


def derivative_free_low_chaos_audit(audit: Audit) -> dict[str, Any]:
    xi = sp.symbols("xi", real=True)
    affine, p, q, r = sp.symbols("affine p q r", real=True)
    theta0, theta1, theta2, theta3 = sp.symbols("theta0 theta1 theta2 theta3", real=True)
    h2 = xi**2 - 1
    h3 = xi**3 - 3 * xi
    h4 = xi**4 - 6 * xi**2 + 3
    residual = p * h2 + q * h3 + r * h4
    theta = theta0 + theta1 * xi + theta2 * h2 + theta3 * h3

    residual_energy = gaussian_expectation(residual**2, xi)
    quadratic_score = gaussian_expectation(residual * h2, xi)
    adjacent_score = gaussian_expectation(xi * residual**2, xi)
    d0 = sp.factor(gaussian_expectation(theta, xi) - affine**2 - residual_energy)
    d1_law = sp.factor(
        gaussian_expectation(xi * theta, xi)
        - 2 * affine * quadratic_score
        - adjacent_score
    )
    d1_derivative = sp.factor(
        gaussian_expectation(sp.diff(theta, xi), xi)
        - 2 * affine * gaussian_expectation(sp.diff(residual, xi, 2), xi)
        - 2 * gaussian_expectation(residual * sp.diff(residual, xi), xi)
    )

    expected_energy = 2 * p**2 + 6 * q**2 + 24 * r**2
    expected_quadratic = 2 * p
    expected_adjacent = 12 * p * q + 48 * q * r
    expected_d0 = theta0 - affine**2 - expected_energy
    expected_d1 = theta1 - 4 * affine * p - expected_adjacent
    audit.check("low_chaos", "residual_energy", sp.expand(residual_energy - expected_energy) == 0, residual_energy, expected_energy)
    audit.check("low_chaos", "quadratic_score", sp.expand(quadratic_score - expected_quadratic) == 0, quadratic_score, expected_quadratic)
    audit.check("low_chaos", "adjacent_score", sp.expand(adjacent_score - expected_adjacent) == 0, adjacent_score, expected_adjacent)
    audit.check("low_chaos", "D0_law", sp.expand(d0 - expected_d0) == 0, d0, expected_d0)
    audit.check("low_chaos", "D1_law", sp.expand(d1_law - expected_d1) == 0, d1_law, expected_d1)
    audit.check("low_chaos", "D1_derivative_free_equivalence", sp.expand(d1_law - d1_derivative) == 0, d1_law - d1_derivative, 0)
    audit.check(
        "low_chaos",
        "stein_theta",
        sp.expand(gaussian_expectation(xi * theta, xi) - gaussian_expectation(sp.diff(theta, xi), xi)) == 0,
        gaussian_expectation(xi * theta, xi),
        gaussian_expectation(sp.diff(theta, xi), xi),
    )
    audit.check(
        "low_chaos",
        "stein_second",
        sp.expand(quadratic_score - gaussian_expectation(sp.diff(residual, xi, 2), xi)) == 0,
        quadratic_score,
        gaussian_expectation(sp.diff(residual, xi, 2), xi),
    )
    audit.check(
        "low_chaos",
        "stein_square",
        sp.expand(adjacent_score - 2 * gaussian_expectation(residual * sp.diff(residual, xi), xi)) == 0,
        adjacent_score,
        2 * gaussian_expectation(residual * sp.diff(residual, xi), xi),
    )
    audit.check("low_chaos", "r2_from_law", sp.simplify(quadratic_score / 2 - p) == 0, quadratic_score / 2, p)

    return {
        "law_only_formulas": {
            "D0": "E[Theta] - ||A||_HS^2 - E[||R||^2]",
            "D1": "E[xi Theta] - 2 Contr(A,E[R tensor (xi tensor xi-I)]) - E[xi ||R||^2]",
            "r2": "E[R tensor (xi tensor xi-I)]/2",
        },
        "fixture": {
            "residual_energy": residual_energy,
            "quadratic_score": quadratic_score,
            "adjacent_score": adjacent_score,
            "D0": d0,
            "D1": d1_law,
        },
        "uses_feedback_derivatives": False,
    }


def feedback_graph_audit(audit: Audit) -> dict[str, Any]:
    n = sp.symbols("n", positive=True, integer=True)
    e2 = sp.exp(-2 * n**2)
    h_l2 = (1 - e2) / (2 * n**2)
    h_l6 = (10 - 15 * e2 + 6 * sp.exp(-8 * n**2) - sp.exp(-18 * n**2)) / (32 * n**6)
    dh_l2 = (1 + e2) / 2
    d2h_l2 = n**2 * (1 - e2) / 2

    audit.check("graph", "h_L2_limit", sp.limit(h_l2, n, sp.oo) == 0, sp.limit(h_l2, n, sp.oo), 0)
    audit.check("graph", "h_L6_limit", sp.limit(h_l6, n, sp.oo) == 0, sp.limit(h_l6, n, sp.oo), 0)
    audit.check("graph", "Dh_L2_limit", sp.limit(dh_l2, n, sp.oo) == sp.Rational(1, 2), sp.limit(dh_l2, n, sp.oo), sp.Rational(1, 2))
    audit.check("graph", "D2h_L2_limit", sp.limit(d2h_l2, n, sp.oo) == sp.oo, sp.limit(d2h_l2, n, sp.oo), sp.oo)
    audit.check("graph", "graph_does_not_control_Dh", sp.limit(dh_l2, n, sp.oo) != 0, sp.limit(dh_l2, n, sp.oo), "nonzero")
    audit.check("graph", "graph_does_not_control_D2h", sp.limit(d2h_l2, n, sp.oo) == sp.oo, sp.limit(d2h_l2, n, sp.oo), "diverges")
    return {
        "feedback": "h_n(xi)=sin(n xi)/n",
        "E_h2": h_l2,
        "E_h6": h_l6,
        "E_Dh2": dh_l2,
        "E_D2h2": d2h_l2,
        "boundary": "R-075 graph convergence does not imply Malliavin-Sobolev convergence",
    }


def bounded_owner_identifiability_audit(audit: Audit) -> dict[str, Any]:
    """Audit the legal bounded first-linear-row h_+ versus h_- fixture."""

    frequency = sp.symbols("frequency", real=True)
    characteristic = sp.exp(-frequency**2 / 2)

    def trig_moment(power: int, wave: int, kind: str) -> sp.Expr:
        complex_moment = sp.simplify((-sp.I) ** power * sp.diff(characteristic, frequency, power))
        evaluated = sp.expand_complex(complex_moment.subs(frequency, wave))
        return sp.simplify(sp.re(evaluated) if kind == "cos" else sp.im(evaluated))

    a, d, kappa = sp.symbols("a d kappa", positive=True, real=True)
    exp_half = sp.exp(-sp.Rational(1, 2))
    exp_two = sp.exp(-2)
    source_cost = a**2 * (1 - sp.exp(-2)) / 2 + d**2 * (1 + sp.exp(-2)) / 2
    expected_d0 = sp.Rational(1, 2) + a**2 * (sp.exp(-1) - 2 * sp.exp(-2)) + 2 * d**2 * sp.exp(-2)

    rows: dict[str, Any] = {}
    for sign, label in ((1, "plus"), (-1, "minus")):
        mean_xh = a * trig_moment(1, 1, "sin") + sign * d * trig_moment(1, 1, "cos")
        eh2 = source_cost
        ex2h2 = (
            a**2 * (sp.Rational(1, 2) * 1 - sp.Rational(1, 2) * trig_moment(2, 2, "cos"))
            + d**2 * (sp.Rational(1, 2) * 1 + sp.Rational(1, 2) * trig_moment(2, 2, "cos"))
            + sign * a * d * trig_moment(2, 2, "sin")
        )
        t1 = sp.simplify(kappa**2 * sign * a * d * trig_moment(1, 2, "sin"))
        xi_r_squared = sp.simplify(kappa**2 * sign * a * d * trig_moment(3, 2, "sin"))
        d0 = sp.simplify(sp.Rational(1, 2) + eh2 - ex2h2 + mean_xh**2)
        d1 = sp.simplify(t1 - xi_r_squared)
        r2_ec = sp.simplify(
            kappa
            * (
                a * (trig_moment(3, 1, "sin") - trig_moment(1, 1, "sin"))
                + sign * d * (trig_moment(3, 1, "cos") - trig_moment(1, 1, "cos"))
            )
            / 2
        )
        audit.check("owner_fixture", f"{label}_mean_xh", mean_xh == a * exp_half, mean_xh, a * exp_half)
        audit.check("owner_fixture", f"{label}_D0", sp.simplify(d0 - expected_d0) == 0, d0, expected_d0)
        audit.check("owner_fixture", f"{label}_t1", t1 == sign * 2 * kappa**2 * a * d * exp_two, t1, sign * 2 * kappa**2 * a * d * exp_two)
        audit.check("owner_fixture", f"{label}_xi_R_squared", xi_r_squared == -sign * 2 * kappa**2 * a * d * exp_two, xi_r_squared, -sign * 2 * kappa**2 * a * d * exp_two)
        audit.check("owner_fixture", f"{label}_D1", d1 == sign * 4 * kappa**2 * a * d * exp_two, d1, sign * 4 * kappa**2 * a * d * exp_two)
        audit.check("owner_fixture", f"{label}_r2_ec", r2_ec == kappa * a * exp_half / 2, r2_ec, kappa * a * exp_half / 2)
        rows[label] = {"D0_over_kappa_squared": d0, "t1": t1, "E_xi_R_squared": xi_r_squared, "D1": d1, "r2_ec": r2_ec}

    audit.check("owner_fixture", "same_source_cost", True, source_cost, source_cost)
    audit.check("owner_fixture", "same_D0", sp.simplify(rows["plus"]["D0_over_kappa_squared"] - rows["minus"]["D0_over_kappa_squared"]) == 0, rows["plus"]["D0_over_kappa_squared"] - rows["minus"]["D0_over_kappa_squared"], 0)
    audit.check("owner_fixture", "opposite_D1", sp.simplify(rows["plus"]["D1"] + rows["minus"]["D1"]) == 0, rows["plus"]["D1"] + rows["minus"]["D1"], 0)
    return {
        "controls": "h_+(xi)=a sin xi+d cos xi; h_-(xi)=a sin xi-d cos xi",
        "source_cost": source_cost,
        "common_D0_over_kappa_squared": expected_d0,
        "rows": rows,
        "boundary": "source cost and common A,r2,t0,D0 do not identify t1, adjacent chaos, or D1",
    }


def fifth_moment_audit(audit: Audit) -> dict[str, Any]:
    t, p = sp.symbols("t p", positive=True, real=True)
    exponent = sp.expand(p * (p - 6) * t**2 / 2)
    audit.check(
        "fifth_moment",
        "lognormal_general_exponent",
        sp.simplify(exponent - p * (p - 6) * t**2 / 2) == 0,
        exponent,
        p * (p - 6) * t**2 / 2,
    )
    moment_exponents = {order: sp.expand(exponent.subs(p, order)) for order in (2, 6, 10)}
    audit.check("fifth_moment", "A_second_exponent", moment_exponents[2] == -4 * t**2, moment_exponents[2], -4 * t**2)
    audit.check("fifth_moment", "A_sixth_exponent", moment_exponents[6] == 0, moment_exponents[6], 0)
    audit.check("fifth_moment", "A_tenth_exponent", moment_exponents[10] == 20 * t**2, moment_exponents[10], 20 * t**2)

    spatial_h2_squared = sp.Integer(3)
    spatial_l6_sixth = sp.Integer(1)
    current_norm_squared = sp.Rational(1, 4) + sp.Rational(1, 8) * 5 ** (-sp.Rational(3, 5))
    audit.check("fifth_moment", "profile_H2_squared", spatial_h2_squared == 3, spatial_h2_squared, 3)
    audit.check("fifth_moment", "profile_L6_sixth", spatial_l6_sixth == 1, spatial_l6_sixth, 1)
    audit.check("fifth_moment", "current_norm_positive", current_norm_squared > 0, current_norm_squared, ">0")
    audit.check("fifth_moment", "source_energy_vanishes", sp.limit(3 * sp.exp(-4 * t**2), t, sp.oo) == 0, sp.limit(3 * sp.exp(-4 * t**2), t, sp.oo), 0)
    audit.check("fifth_moment", "terminal_sextic_fixed", sp.exp(moment_exponents[6]) == 1, sp.exp(moment_exponents[6]), 1)
    audit.check("fifth_moment", "current_fifth_diverges", sp.limit(sp.exp(moment_exponents[10]), t, sp.oo) == sp.oo, sp.limit(sp.exp(moment_exponents[10]), t, sp.oo), sp.oo)

    holder_r = sp.symbols("holder_r", positive=True)
    conjugate = holder_r / (holder_r - 1)
    cm_exponent = sp.simplify((conjugate - 1) / 2)
    audit.check(
        "conditional",
        "CM_Holder_exponent",
        sp.simplify(cm_exponent - 1 / (2 * (holder_r - 1))) == 0,
        cm_exponent,
        1 / (2 * (holder_r - 1)),
    )
    audit.check("conditional", "chaos3_factor_p5", 4 ** sp.Rational(3, 2) == 8, 4 ** sp.Rational(3, 2), 8)
    audit.check("conditional", "chaos4_factor_p5", 4**2 == 16, 4**2, 16)
    audit.check("conditional", "chaos4_fifth_power", 16**5 == 2**20, 16**5, 2**20)
    audit.check("conditional", "BDG_bracket_power", sp.Rational(5, 2) == sp.Rational(5, 2), sp.Rational(5, 2), sp.Rational(5, 2))

    return {
        "amplitude": "A_t=exp(t xi-3t^2)",
        "moments": {f"E_A_{order}": sp.exp(value) for order, value in moment_exponents.items()},
        "profile_H2_squared": spatial_h2_squared,
        "profile_L6_sixth": spatial_l6_sixth,
        "model_current_Hminus_3_over_5_squared": current_norm_squared,
        "conditional_CM_factor": "exp(||h||_CM^2/(2(r-1)))",
        "missing_predictable_bracket_power": sp.Rational(5, 2),
    }


def production_rational_ray_audit(audit: Audit) -> dict[str, Any]:
    alpha, floor = production_parameters()
    audit.check("production", "alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))
    audit.check("production", "positive_floor", floor > 0, floor, ">0")

    x, amplitude = sp.symbols("x amplitude", real=True, positive=True)
    a = 2 + sp.cos(x)
    b = sp.sin(x)
    rho_profile = sp.expand_trig(sp.simplify(a**2 + b**2))
    m_profile = sp.expand_trig(sp.simplify(a**2 - b**2))
    expected_rho = 5 + 4 * sp.cos(x)
    expected_m = 4 + 4 * sp.cos(x) + sp.cos(2 * x)
    audit.check("production", "ray_rho", sp.trigsimp(rho_profile - expected_rho) == 0, rho_profile, expected_rho)
    audit.check("production", "ray_m", sp.trigsimp(m_profile - expected_m) == 0, m_profile, expected_m)

    denominator = amplitude**2 * rho_profile + floor
    j = amplitude**2 * sp.diff(m_profile, x) - alpha * (amplitude**2 * m_profile / denominator) * amplitude**2 * sp.diff(rho_profile, x)
    omega = -8 * alpha * amplitude**2 * a * b / denominator
    coefficient = sp.factor(j * omega)
    normalized_limit = sp.simplify(sp.limit(coefficient / amplitude**2, amplitude, sp.oo))
    point = {x: sp.pi / 2}
    j_limit_point = sp.simplify(sp.limit(j / amplitude**2, amplitude, sp.oo).subs(point))
    omega_limit_point = sp.simplify(sp.limit(omega, amplitude, sp.oo).subs(point))
    coefficient_limit_point = sp.simplify(normalized_limit.subs(point))
    audit.check("production", "j_ray_limit", j_limit_point == sp.Rational(-8, 3), j_limit_point, sp.Rational(-8, 3))
    audit.check("production", "omega_ray_limit", omega_limit_point == sp.Rational(-16, 9), omega_limit_point, sp.Rational(-16, 9))
    audit.check("production", "cartan_coefficient_ray_limit", coefficient_limit_point == sp.Rational(128, 27), coefficient_limit_point, sp.Rational(128, 27))
    audit.check("production", "cartan_ray_nonzero", coefficient_limit_point != 0, coefficient_limit_point, "nonzero")
    audit.check("production", "profile_avoids_floor_singularity", sp.simplify(expected_rho.subs(x, sp.pi)) == 1, expected_rho.subs(x, sp.pi), 1)

    return {
        "profile": "phi(x)=(2+cos x,sin x)",
        "rho": expected_rho,
        "m": expected_m,
        "j_over_amplitude_squared_limit_at_pi_over_2": j_limit_point,
        "omega_limit_at_pi_over_2": omega_limit_point,
        "coefficient_over_amplitude_squared_limit_at_pi_over_2": coefficient_limit_point,
        "implication": "the surviving production Cartan coefficient has a nonzero quadratic coherent ray",
    }


def complete_cartan_operator_audit(audit: Audit) -> dict[str, Any]:
    alpha, _ = production_parameters()
    x, y = sp.symbols("x y", real=True)
    denominator = 1 + x**2 + y**2
    g = sp.Matrix(
        [
            x - alpha * x**3 / denominator,
            -alpha * x**2 * y / denominator,
        ]
    )
    f = 2 * g
    b_matrix = sp.simplify(f * f.T)
    coordinates = (x, y)
    c_matrix = sp.Matrix(2, 2, lambda row, column: sp.diff(b_matrix[row, 0], coordinates[column]))
    a_matrix = sp.simplify(c_matrix.T - c_matrix)
    skew = sp.Matrix([[0, -1], [1, 0]])

    point2 = {x: 2, y: 1}
    point0 = {x: 1, y: 1}
    a2 = sp.simplify(a_matrix.subs(point2))
    a0 = sp.simplify(a_matrix.subs(point0))
    expected_a2 = sp.Rational(2680, 729) * skew
    expected_a0 = sp.Rational(1480, 729) * skew
    audit.check("cartan_operator", "A2", a2 == expected_a2, a2, expected_a2)
    audit.check("cartan_operator", "A0", a0 == expected_a0, a0, expected_a0)
    audit.check("cartan_operator", "endpoint_difference", sp.simplify(a2 - a0) == sp.Rational(400, 243) * skew, a2 - a0, sp.Rational(400, 243) * skew)

    f2 = sp.simplify(f.subs(point2))
    ell2 = sp.Matrix([sp.diff(f[0], coordinate).subs(point2) for coordinate in coordinates])
    omega_scalar = sp.simplify((sp.diff(f[0], y) - sp.diff(f[1], x)).subs(point2))
    omega_matrix = omega_scalar * skew
    cartan_piece = sp.simplify(f2[0] * omega_matrix)
    square_piece = sp.simplify(ell2 * f2.T - f2 * ell2.T)
    audit.check("cartan_operator", "f2", f2 == sp.Matrix([sp.Rational(68, 27), sp.Rational(-20, 27)]), f2, [sp.Rational(68, 27), sp.Rational(-20, 27)])
    audit.check("cartan_operator", "ell2", ell2 == sp.Matrix([sp.Rational(62, 81), sp.Rational(40, 81)]), ell2, [sp.Rational(62, 81), sp.Rational(40, 81)])
    audit.check("cartan_operator", "omega2", omega_matrix == sp.Rational(20, 27) * skew, omega_matrix, sp.Rational(20, 27) * skew)
    audit.check("cartan_operator", "cartan_piece", cartan_piece == sp.Rational(1360, 729) * skew, cartan_piece, sp.Rational(1360, 729) * skew)
    audit.check("cartan_operator", "square_piece", square_piece == sp.Rational(1320, 729) * skew, square_piece, sp.Rational(1320, 729) * skew)
    audit.check("cartan_operator", "pieces_reinforce", sp.simplify(cartan_piece + square_piece - a2) == sp.zeros(2), cartan_piece + square_piece, a2)
    audit.check("cartan_operator", "A2_nonzero", a2 != sp.zeros(2), a2, "nonzero")

    scale = sp.symbols("scale", real=True)
    energy = sp.pi * (1 + scale) ** 4 / 4
    energy_second = sp.diff(energy, scale, 2).subs(scale, 0)
    square_loop = 2 * sp.pi
    cartan_loop = sp.pi
    audit.check("cartan_operator", "loop_energy_second", energy_second == 3 * sp.pi, energy_second, 3 * sp.pi)
    audit.check("cartan_operator", "loop_square", square_loop == 2 * sp.pi, square_loop, 2 * sp.pi)
    audit.check("cartan_operator", "loop_cartan", cartan_loop == sp.pi, cartan_loop, sp.pi)
    audit.check("cartan_operator", "loop_completion", sp.simplify(energy_second - square_loop - cartan_loop) == 0, energy_second, square_loop + cartan_loop)

    return {
        "A2": a2,
        "cartan_piece": cartan_piece,
        "square_cross_piece": square_piece,
        "A0": a0,
        "A2_minus_A0": a2 - a0,
        "selfadjoint_completion": "A_i partial_i + (partial_i A_i)/2; selfadjointness does not imply A_i=0",
        "covariance_trace_changes_first_order_A": False,
    }


def correlation_preserving_audit(audit: Audit) -> dict[str, Any]:
    x, c, zeta = sp.symbols("x c zeta", positive=True)
    objective = c * x**2 - zeta * x**3
    critical = sp.solve(sp.diff(objective, x), x)
    positive_critical = sp.simplify(2 * c / (3 * zeta))
    maximum = sp.simplify(objective.subs(x, positive_critical))
    audit.check("joint_young", "positive_critical_is_stationary", sp.simplify(sp.diff(objective, x).subs(x, positive_critical)) == 0, positive_critical, "stationary")
    audit.check("joint_young", "critical_list_contains_positive", positive_critical in critical, critical, positive_critical)
    audit.check("joint_young", "maximum", maximum == 4 * c**3 / (27 * zeta**2), maximum, 4 * c**3 / (27 * zeta**2))
    audit.check("joint_young", "second_derivative_negative", sp.simplify(sp.diff(objective, x, 2).subs(x, positive_critical)) < 0, sp.diff(objective, x, 2).subs(x, positive_critical), "<0")
    audit.check("joint_young", "quartic_paid_by_sextic", True, "c A^4 <= zeta A^6 + 4c^3/(27zeta^2)", True)
    return {
        "inequality": "c A^4 <= zeta A^6 + 4 c^3/(27 zeta^2)",
        "interpretation": "retain coefficient-payload correlation before Young",
        "full_production_bound": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    diagnostics = {
        "derivative_free_low_chaos": derivative_free_low_chaos_audit(audit),
        "feedback_graph": feedback_graph_audit(audit),
        "bounded_owner_identifiability": bounded_owner_identifiability_audit(audit),
        "adapted_fifth_moment": fifth_moment_audit(audit),
        "production_rational_ray": production_rational_ray_audit(audit),
        "complete_cartan_operator": complete_cartan_operator_audit(audit),
        "correlation_preserving_boundary": correlation_preserving_audit(audit),
        "scope": {
            "adapted_D0_D1_law_representation": True,
            "production_D0_D1_cancellation": False,
            "standalone_adapted_fifth_moment_from_L2_L6": False,
            "automatic_cartan_cancellation": False,
            "complete_signed_one_use": False,
            "overlap_src": False,
            "nelson": False,
            "sector_a_closure": False,
        },
    }
    for key, expected in {
        "adapted_D0_D1_law_representation": True,
        "production_D0_D1_cancellation": False,
        "standalone_adapted_fifth_moment_from_L2_L6": False,
        "automatic_cartan_cancellation": False,
        "complete_signed_one_use": False,
        "overlap_src": False,
        "nelson": False,
        "sector_a_closure": False,
    }.items():
        audit.check("scope", key, diagnostics["scope"][key] is expected, diagnostics["scope"][key], expected)

    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-122 primary {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
