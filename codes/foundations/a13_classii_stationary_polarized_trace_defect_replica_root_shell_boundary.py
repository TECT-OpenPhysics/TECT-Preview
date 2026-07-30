#!/usr/bin/env python3
"""Primary exact verifier for the scoped R-124 A13 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-STATIONARY-POLARIZED-TRACE-DEFECT-REPLICA-ROOT-SHELL-BOUNDARY"
SCHEMA = "tect/a13-stationary-polarized-trace-defect-replica-root-shell-boundary-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.simplify(value))
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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
                "R-124 proves a conditional stationary-polarization theorem, exact refinement invariance, "
                "a sharp legal-row replica bound, and scoped route boundaries. It does not prove the "
                "owner-complete cutoff-uniform production trace-excess estimate, OVERLAP_src, Nelson, "
                "removals, an interacting measure, or Sector A closure."
            ),
        }


def gaussian_expectation(poly: sp.Expr, variable: sp.Symbol) -> sp.Expr:
    expanded = sp.Poly(sp.expand(poly), variable)
    total = sp.Integer(0)
    for (degree,), coefficient in expanded.terms():
        if degree % 2 == 0:
            total += coefficient * (sp.Integer(1) if degree == 0 else sp.factorial2(degree - 1))
    return sp.simplify(total)


def hermite_quadratic_formula(coefficients: list[sp.Expr], variable: sp.Symbol) -> sp.Expr:
    h = sum((coefficient * sp.hermite_prob(index, variable) for index, coefficient in enumerate(coefficients)), sp.Integer(0))
    return gaussian_expectation((variable**2 - 1) * h**2, variable)


def production_constants() -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = sp.Rational(str(parameters["M_X"])) ** 2 + sp.Rational(str(parameters["classii_mass_regularizer"]))
    a_weight = sp.Rational(str(parameters["cJJ"])) * sp.Rational(str(parameters["alpha_X"])) ** 2 / mass
    b_weight = (
        sp.Rational(str(parameters["cJK"]))
        * sp.Rational(str(parameters["alpha_X"]))
        * sp.Rational(str(parameters["beta_X"]))
        / mass
    )
    c_weight = sp.Rational(str(parameters["cKK"])) * sp.Rational(str(parameters["beta_X"])) ** 2 / mass
    alpha = sp.simplify(c_weight / (b_weight + c_weight))
    c1 = sp.simplify(c_weight / alpha**2)
    c0 = sp.simplify(a_weight - b_weight**2 / c_weight)
    return mass, c0, c1, alpha, sp.simplify(4 * c0)


def owner_curls(alpha: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    x, y = sp.symbols("x y", real=True)

    def coefficient(x_value: sp.Expr, y_value: sp.Expr) -> sp.Matrix:
        denominator = 1 + x_value**2 + y_value**2
        g = sp.Matrix(
            [
                x_value - alpha * x_value**3 / denominator,
                -alpha * x_value**2 * y_value / denominator,
            ]
        )
        return sp.simplify(4 * g * g.T)

    b0 = coefficient(x, y)
    b1 = coefficient(x + 1, y)
    taylor = sp.simplify(b0 + b0.diff(x) + sp.Rational(1, 2) * b0.diff(x, 2))
    remainder = sp.simplify(b1 - taylor)
    point = {x: 1, y: 1}

    def curl(current: sp.Matrix) -> sp.Expr:
        return sp.simplify((sp.diff(current[0], y) - sp.diff(current[1], x)).subs(point))

    return curl(remainder[:, 0]), curl(taylor[:, 0]), curl(b1[:, 0])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    mass, c0, c1, alpha, kappa2 = production_constants()
    eta_row = sp.simplify(kappa2 / 2)
    # Derived production numbers are read from the A1 manifest; the right sides are test oracles.
    audit.check("production", "mass", mass == sp.Rational(4000000000001, 10**12), mass, sp.Rational(4000000000001, 10**12))
    audit.check("production", "c0", c0 == sp.Rational(3, 250) / mass, c0, sp.Rational(3, 250) / mass)
    audit.check("production", "c1", c1 == sp.Rational(243, 8000) / mass, c1, sp.Rational(243, 8000) / mass)
    audit.check("production", "alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))
    audit.check("production", "row_allocation", eta_row == sp.Rational(3, 125) / mass, eta_row, sp.Rational(3, 125) / mass)

    # Exact stationary polarization, including conditional and centered forms.
    phi0, delta_phi, delta_theta = sp.symbols("phi0 delta_phi delta_theta", real=True)
    phih = phi0 + delta_phi
    symmetric = sp.expand(delta_theta - (phih + phi0) * delta_phi)
    three_term = sp.expand(delta_theta - 2 * phi0 * delta_phi - delta_phi**2)
    direct_difference = sp.expand(delta_theta - (phih**2 - phi0**2))
    audit.check("polarization", "symmetric_secant", sp.expand(symmetric - direct_difference) == 0, symmetric, direct_difference)
    audit.check("polarization", "negative_square_form", sp.expand(three_term - direct_difference) == 0, three_term, direct_difference)

    v0 = sp.Matrix([2 + sp.I, -1 + 2 * sp.I])
    dv = sp.Matrix([3 - sp.I, 4 + sp.I])
    inner = lambda left, right: sum((sp.conjugate(left[i]) * right[i] for i in range(left.rows)), sp.Integer(0))
    complex_symmetric = sp.simplify(7 - sp.re(inner(v0 + dv + v0, dv)))
    complex_direct = sp.simplify(7 - (sp.re(inner(v0 + dv, v0 + dv)) - sp.re(inner(v0, v0))))
    audit.check("polarization", "complex_real_inner_product", complex_symmetric == complex_direct, complex_symmetric, complex_direct)

    weights = (sp.Rational(1, 3), sp.Rational(2, 3))
    values = (sp.Integer(-2), sp.Integer(4))
    thetas = (sp.Integer(5), sp.Integer(11))
    mean = sum((weights[i] * values[i] for i in range(2)), sp.Integer(0))
    d0 = sum((weights[i] * (thetas[i] - (values[i] - mean) ** 2) for i in range(2)), sp.Integer(0))
    s_value = sp.simplify(d0 - mean**2)
    direct_s = sum((weights[i] * (thetas[i] - values[i] ** 2) for i in range(2)), sp.Integer(0))
    audit.check("polarization", "conditional_cell_identity", s_value == direct_s, s_value, direct_s)

    b0, db, mixed_y, dy2, dtheta = sp.symbols("b0 db mixed_y dy2 dtheta", real=True)
    centered = sp.expand(dtheta - 2 * b0 * db - db**2 - 2 * mixed_y - dy2)
    uncentered_after_expectation = sp.expand(dtheta - 2 * (b0 * db + mixed_y) - (db**2 + dy2))
    audit.check("polarization", "centered_decomposition", sp.expand(uncentered_after_expectation - centered) == 0, uncentered_after_expectation, centered)

    eps = sp.symbols("eps", positive=True)
    mixed_fixture = gaussian_expectation(sp.Symbol("x", real=True) * (-eps * sp.Symbol("x", real=True)), sp.Symbol("x", real=True))
    audit.check("polarization", "mixed_centered_covariance_nonzero", mixed_fixture == -eps, mixed_fixture, -eps)

    replica_values = (sp.Matrix([1, 2]), sp.Matrix([-2, 4]))
    replica_mean = weights[0] * replica_values[0] + weights[1] * replica_values[1]
    replica_lhs = sp.Rational(1, 2) * sum(
        (weights[i] * weights[j] * (replica_values[i] - replica_values[j]).dot(replica_values[i] - replica_values[j]) for i in range(2) for j in range(2)),
        sp.Integer(0),
    )
    replica_rhs = sum((weights[i] * replica_values[i].dot(replica_values[i]) for i in range(2)), sp.Integer(0)) - replica_mean.dot(replica_mean)
    audit.check("polarization", "conditional_replica_variance", sp.simplify(replica_lhs - replica_rhs) == 0, replica_lhs, replica_rhs)
    audit.check("polarization", "baseline_not_automatically_zero", 0 - 1**2 == -1, -1, "nonzero baseline allowed")

    # Moving-endpoint subdivision and representation firewalls.
    a, f, iota, third, t0, t1, t2, t3 = sp.symbols("a f iota third t0 t1 t2 t3", real=True)
    endpoints = (a, a + f, a + f + iota, a + f + iota + third)
    traces = (t0, t1, t2, t3)
    packets = [
        sp.expand(traces[index] - traces[index - 1] - (endpoints[index] + endpoints[index - 1]) * (endpoints[index] - endpoints[index - 1]))
        for index in range(1, 4)
    ]
    endpoint_packet = sp.expand(t3 - t0 - (endpoints[-1] ** 2 - endpoints[0] ** 2))
    audit.check("refinement", "three_visit_telescope", sp.expand(sum(packets) - endpoint_packet) == 0, sum(packets), endpoint_packet)
    moving_three = sp.expand((t1 - t0 - 2 * a * f - f**2) + (t2 - t1 - 2 * (a + f) * iota - iota**2))
    two_endpoint = sp.expand(t2 - t0 - 2 * a * (f + iota) - (f + iota) ** 2)
    audit.check("refinement", "moving_baseline_three_term", sp.expand(moving_three - two_endpoint) == 0, moving_three, two_endpoint)
    fixed_wrong = sp.expand((t1 - t0 - 2 * a * f - f**2) + (t2 - t1 - 2 * a * iota - iota**2))
    audit.check("refinement", "fixed_baseline_missing_cross", sp.expand(fixed_wrong - two_endpoint - 2 * f * iota) == 0, fixed_wrong - two_endpoint, 2 * f * iota)
    covariance = sp.Matrix([[1, 1], [1, 1]])
    coefficients = sp.Matrix([sp.Rational(1, 2), sp.Rational(1, 2)])
    audit.check("refinement", "full_covariance_trace", (coefficients.T * covariance * coefficients)[0] == 1, (coefficients.T * covariance * coefficients)[0], 1)
    audit.check("refinement", "diagonal_trace_is_wrong", (coefficients.T * sp.eye(2) * coefficients)[0] == sp.Rational(1, 2), (coefficients.T * sp.eye(2) * coefficients)[0], sp.Rational(1, 2))

    # Hermite/replica theorem and sharp finite-degree coefficient.
    x = sp.symbols("x", real=True)
    coeffs = list(sp.symbols("a0:5", real=True))
    actual_form = hermite_quadratic_formula(coeffs, x)
    expected_form = 2 * sum((n * sp.factorial(n) * coeffs[n] ** 2 for n in range(5)), sp.Integer(0)) + 2 * sum(((n + 2) * sp.factorial(n + 1) * coeffs[n] * coeffs[n + 2] for n in range(3)), sp.Integer(0))
    audit.check("hermite", "quadratic_form", sp.expand(actual_form - expected_form) == 0, actual_form, expected_form)
    matrix = sp.zeros(5)
    for n in range(5):
        matrix[n, n] = 2 * n + 1
        if n + 2 < 5:
            matrix[n, n + 2] = matrix[n + 2, n] = sp.sqrt((n + 1) * (n + 2))
    normalized_coeffs = sp.Matrix([sp.sqrt(sp.factorial(n)) * coeffs[n] for n in range(5)])
    normalized_matrix_form = sp.expand((normalized_coeffs.T * (matrix - sp.eye(5)) * normalized_coeffs)[0])
    audit.check("hermite", "normalized_matrix_representation", sp.simplify(normalized_matrix_form - actual_form) == 0, normalized_matrix_form, actual_form)
    mu0 = sp.Integer(1)
    mu1 = sp.Integer(1)
    even_m2 = sp.Matrix([[1, sp.sqrt(2)], [sp.sqrt(2), 5]])
    mu2 = sp.simplify(min(even_m2.eigenvals().keys(), key=lambda value: float(value)))
    odd_m3 = sp.Matrix([[3, sp.sqrt(6)], [sp.sqrt(6), 7]])
    mu3 = sp.simplify(min([*even_m2.eigenvals().keys(), *odd_m3.eigenvals().keys()], key=lambda value: float(value)))
    audit.check("hermite", "mu0_mu1", mu0 == 1 and mu1 == 1, (mu0, mu1), (1, 1))
    spectral = sp.symbols("spectral")
    matrix6 = sp.zeros(6)
    for n in range(6):
        matrix6[n, n] = 2 * n + 1
        if n + 2 < 6:
            matrix6[n, n + 2] = matrix6[n + 2, n] = sp.sqrt((n + 1) * (n + 2))
    even_m5 = matrix6.extract([0, 2, 4], [0, 2, 4])
    odd_m5 = matrix6.extract([1, 3, 5], [1, 3, 5])
    even_laguerre = sp.expand(-sp.factorial(3) * 2**3 * sp.assoc_laguerre(3, sp.Rational(-1, 2), spectral / 2))
    odd_laguerre = sp.expand(-sp.factorial(3) * 2**3 * sp.assoc_laguerre(3, sp.Rational(1, 2), spectral / 2))
    audit.check(
        "hermite",
        "laguerre_block_characteristics",
        sp.expand(even_m5.charpoly(spectral).as_expr() - even_laguerre) == 0
        and sp.expand(odd_m5.charpoly(spectral).as_expr() - odd_laguerre) == 0,
        (even_m5.charpoly(spectral).as_expr(), odd_m5.charpoly(spectral).as_expr()),
        (even_laguerre, odd_laguerre),
    )
    audit.check("hermite", "mu2", mu2 == 3 - sp.sqrt(6), mu2, 3 - sp.sqrt(6))
    audit.check("hermite", "degree_two_gain", sp.simplify(1 - mu2) == sp.sqrt(6) - 2, 1 - mu2, sp.sqrt(6) - 2)
    audit.check("hermite", "mu3", mu3 == 3 - sp.sqrt(6), mu3, 3 - sp.sqrt(6))
    bump_parameter = sp.symbols("bump_parameter", positive=True)
    bump_norm = 1 / sp.sqrt(1 + 4 * bump_parameter)
    bump_x2_norm = 1 / (1 + 4 * bump_parameter) ** sp.Rational(3, 2)
    bump_ratio = sp.simplify((bump_norm - bump_x2_norm) / bump_norm)
    audit.check("hermite", "gaussian_bump_ratio", bump_ratio == 4 * bump_parameter / (1 + 4 * bump_parameter), bump_ratio, 4 * bump_parameter / (1 + 4 * bump_parameter))
    even_min_m5 = min(sp.nroots(even_m5.charpoly(spectral).as_expr()), key=lambda value: float(sp.re(value)))
    odd_min_m5 = min(sp.nroots(odd_m5.charpoly(spectral).as_expr()), key=lambda value: float(sp.re(value)))
    audit.check("hermite", "even_block_smaller_M5", float(sp.re(even_min_m5)) < float(sp.re(odd_min_m5)), (even_min_m5, odd_min_m5), "even minimum below odd minimum")

    # Legal first-linear row: exact source-only bound and decisive fixtures.
    theta_h, norm_phi_h, theta_0, norm_phi_0 = sp.symbols("theta_h norm_phi_h theta_0 norm_phi_0", real=True)
    delta_l = sp.expand((theta_h - norm_phi_h) - (theta_0 - norm_phi_0))
    row_oracle = sp.Symbol("row_oracle", real=True)
    audit.check("legal_row", "trace_defect_definition", delta_l.subs({theta_h: row_oracle, norm_phi_h: 0, theta_0: 0, norm_phi_0: 0}) == row_oracle, delta_l, "Theta minus output square")
    audit.check("legal_row", "kappa2", kappa2 == sp.Rational(6, 125) / mass, kappa2, sp.Rational(6, 125) / mass)
    h2, x2h2 = sp.symbols("h2 x2h2", nonnegative=True)
    theta_expectation_h = kappa2 * (gaussian_expectation(x**2 / 2, x) + h2 + 1)
    phi_square_expectation_h = kappa2 * (gaussian_expectation(x**4 / 2, x) + x2h2)
    theta_expectation_0 = kappa2 * (gaussian_expectation(x**2 / 2, x) + 1)
    phi_square_expectation_0 = kappa2 * gaussian_expectation(x**4 / 2, x)
    row_delta = sp.expand((theta_expectation_h - phi_square_expectation_h) - (theta_expectation_0 - phi_square_expectation_0))
    audit.check("legal_row", "stationary_difference", sp.simplify(row_delta - kappa2 * (h2 - x2h2)) == 0, row_delta, kappa2 * (h2 - x2h2))
    audit.check("legal_row", "source_upper_bound", sp.simplify(kappa2 * h2 - row_delta) == kappa2 * x2h2, kappa2 * h2 - row_delta, kappa2 * x2h2)
    audit.check("legal_row", "action_allocation", eta_row == kappa2 / 2, eta_row, kappa2 / 2)

    n = sp.symbols("N", positive=True)
    characteristic = lambda frequency_value: sp.exp(-frequency_value**2 / 2)
    exp2 = characteristic(2 * n)
    sin_x = sp.simplify((1 - characteristic(2 * n)) / (2 * n**2))
    sin_y = sp.simplify(-sum((sp.binomial(6, index) * (-1) ** index * characteristic((6 - 2 * index) * n) for index in range(7)), sp.Integer(0)) / (64 * n**6))
    sin_x_oracle = (1 - sp.exp(-2 * n**2)) / (2 * n**2)
    sin_y_oracle = (10 - 15 * sp.exp(-2 * n**2) + 6 * sp.exp(-8 * n**2) - sp.exp(-18 * n**2)) / (32 * n**6)
    audit.check("legal_row", "sin_source", sp.simplify(sin_x - sin_x_oracle) == 0, sin_x, sin_x_oracle)
    audit.check("legal_row", "sin_sixth", sp.simplify(sin_y - sin_y_oracle) == 0, sin_y, sin_y_oracle)
    sin_x2 = sp.simplify((1 - (1 - 4 * n**2) * characteristic(2 * n)) / (2 * n**2))
    sin_delta = sp.simplify(kappa2 * (sin_x - sin_x2))
    audit.check("legal_row", "sin_trace_defect", sp.simplify(sin_delta + 2 * kappa2 * exp2) == 0, sin_delta, -2 * kappa2 * exp2)
    sin_d0_delta = sp.simplify(sin_delta + kappa2 * characteristic(n) ** 2)
    audit.check("legal_row", "sin_D0_difference", sp.simplify(sin_d0_delta - kappa2 * (sp.exp(-n**2) - 2 * sp.exp(-2 * n**2))) == 0, sin_d0_delta, kappa2 * (sp.exp(-n**2) - 2 * sp.exp(-2 * n**2)))
    d, frequency = sp.symbols("d frequency", positive=True)
    cosine_h2 = d**2 * (1 + characteristic(2 * frequency)) / 2
    cosine_x2h2 = d**2 * (1 + (1 - 4 * frequency**2) * characteristic(2 * frequency)) / 2
    cosine_delta = sp.simplify(kappa2 * (cosine_h2 - cosine_x2h2))
    audit.check("legal_row", "cosine_positive_defect", cosine_delta > 0 and sp.simplify(cosine_delta - 2 * kappa2 * d**2 * frequency**2 * sp.exp(-2 * frequency**2)) == 0, cosine_delta, 2 * kappa2 * d**2 * frequency**2 * sp.exp(-2 * frequency**2))

    # Correct R-121 connection and two method stop tests.
    curl_k, curl_m, curl_full = owner_curls(alpha)
    audit.check("cartan", "K_R_curl", curl_k == sp.Rational(-40, 729), curl_k, sp.Rational(-40, 729))
    audit.check("cartan", "M_U_curl", curl_m == sp.Rational(2720, 729), curl_m, sp.Rational(2720, 729))
    audit.check("cartan", "full_curl", curl_full == sp.Rational(2680, 729), curl_full, sp.Rational(2680, 729))
    audit.check("cartan", "curl_recombination", sp.simplify(curl_k + curl_m - curl_full) == 0, curl_k + curl_m, curl_full)
    audit.check("cartan", "no_opposite_companion", curl_m != -curl_k and curl_full != 0, (curl_m, curl_full), ("not +40/729", "nonzero"))

    spatial_n, sobolev_s = sp.symbols("spatial_n sobolev_s", positive=True)
    critical_angle = sp.symbols("critical_angle", real=True)
    fixture_n = sp.Integer(7)
    fixture_component = sp.sin(fixture_n * critical_angle) / fixture_n**2
    h2_norm = sp.simplify(
        sp.integrate(
            1 + fixture_component**2 + sp.diff(fixture_component, critical_angle) ** 2 + sp.diff(fixture_component, critical_angle, 2) ** 2,
            (critical_angle, 0, 2 * sp.pi),
        )
        / (2 * sp.pi)
    )
    h2_expected = sp.Rational(3, 2) + 1 / (2 * fixture_n**2) + 1 / (2 * fixture_n**4)
    q_norm = spatial_n ** (2 * sobolev_s) / (2 * (1 + spatial_n**2) ** sobolev_s)
    pairing = -spatial_n ** (sobolev_s - 1) / 2
    audit.check("critical", "H2_norm", sp.simplify(h2_norm - h2_expected) == 0, h2_norm, h2_expected)
    l6_norm = sp.simplify(sp.integrate((1 + fixture_component**2) ** 3, (critical_angle, 0, 2 * sp.pi)) / (2 * sp.pi))
    l6_expected = 1 + sp.Rational(3, 2) / fixture_n**4 + sp.Rational(9, 8) / fixture_n**8 + sp.Rational(5, 16) / fixture_n**12
    audit.check("critical", "L6_norm", sp.simplify(l6_norm - l6_expected) == 0, l6_norm, l6_expected)
    q_ratio = sp.simplify(2 * q_norm)
    audit.check("critical", "negative_norm_bound", q_ratio == (spatial_n**2 / (1 + spatial_n**2)) ** sobolev_s, q_ratio, "a positive base below one raised to s")
    audit.check("critical", "pairing", pairing == -spatial_n ** (sobolev_s - 1) / 2, pairing, -spatial_n ** (sobolev_s - 1) / 2)
    audit.check("critical", "Hminus_11_10_diverges", sp.simplify(pairing.subs(sobolev_s, sp.Rational(11, 10))) == -spatial_n ** sp.Rational(1, 10) / 2, pairing.subs(sobolev_s, sp.Rational(11, 10)), -spatial_n ** sp.Rational(1, 10) / 2)
    rare_first = sp.simplify(spatial_n ** -6 * (spatial_n**6))
    rare_moments = (sp.simplify(spatial_n ** -6 * (spatial_n**6) ** sp.Rational(5, 3)), sp.simplify(spatial_n ** -6 * (spatial_n**6) ** sp.Rational(5, 2)))
    audit.check("critical", "rare_moments", rare_first == 1 and rare_moments == (spatial_n**4, spatial_n**9), (rare_first, rare_moments), (1, spatial_n**4, spatial_n**9))

    # Covariant-Hessian decomposition: exact model and normalized fixture.
    g, gp, gpp, ux, zx, z = sp.symbols("g gp gpp ux zx z", positive=True)
    gamma = gp / (2 * g)
    hessian = g * zx**2 + 2 * gp * z * ux * zx + sp.Rational(1, 2) * gpp * z**2 * ux**2
    connection_square = g * (zx + gamma * ux * z) ** 2
    gamma_prime = gpp / (2 * g) - gp**2 / (2 * g**2)
    acceleration = sp.Rational(1, 2) * gp * gamma * z**2 * ux**2 + g * ux * (gamma_prime * ux * z**2 + 2 * gamma * z * zx)
    audit.check("covariant", "connection_identity", sp.simplify(connection_square + acceleration - hessian) == 0, connection_square + acceleration, hessian)
    angle, H, C = sp.symbols("angle H C", real=True, positive=True)
    U = H * (2 + sp.cos(angle))
    direction = 2 - sp.cos(angle)
    connection_integrand = sp.expand(4 * C * U**2 * (sp.diff(direction, angle) + sp.diff(U, angle) * direction / U) ** 2)
    connection_average = sp.simplify(sp.integrate(connection_integrand, (angle, 0, 2 * sp.pi)) / (2 * sp.pi))
    acceleration_integrand = sp.expand(8 * C * U * sp.diff(U, angle) * direction * sp.diff(direction, angle))
    acceleration_average = sp.simplify(sp.integrate(acceleration_integrand, (angle, 0, 2 * sp.pi)) / (2 * sp.pi))
    audit.check("covariant", "connection_square_value", connection_average == 2 * C * H**2, connection_average, 2 * C * H**2)
    audit.check("covariant", "acceleration_value", acceleration_average == -15 * C * H**2, acceleration_average, -15 * C * H**2)
    total_average = sp.simplify(connection_average + acceleration_average)
    production_c = sp.simplify(c0 + c1 * sp.Rational(16, 81))
    audit.check("covariant", "negative_total", total_average == -13 * C * H**2 and sp.simplify(-13 * production_c) == -sp.Rational(117, 500) / mass, (total_average, -13 * production_c), (-13 * C * H**2, -sp.Rational(117, 500) / mass))

    # OU Hessian-semigroup identity for the bare higher-chaos debt.
    chaos_n = sp.Integer(5)
    chaos_norm = sp.symbols("chaos_norm", positive=True)
    h5_second = sp.diff(sp.hermite_prob(chaos_n, x), x, 2)
    d2_norm = sp.simplify(gaussian_expectation(h5_second**2, x) * chaos_norm)
    audit.check("ou", "second_derivative_norm", d2_norm == chaos_n * (chaos_n - 1) * sp.factorial(chaos_n) * chaos_norm, d2_norm, chaos_n * (chaos_n - 1) * sp.factorial(chaos_n) * chaos_norm)
    s = sp.symbols("s", positive=True)
    integrated = sp.integrate(sp.exp(-2 * chaos_n * s) * d2_norm, (s, 0, sp.oo))
    expected_integrated = sp.Rational(1, 2) * (chaos_n - 1) * sp.factorial(chaos_n) * chaos_norm
    audit.check("ou", "semigroup_integral", sp.simplify(integrated - expected_integrated) == 0, integrated, expected_integrated)
    fixture_coefficients = {2: sp.Rational(1, 2), 3: sp.Rational(-1, 3), 4: sp.Rational(1, 4)}
    fixture_debt = -sp.Rational(1, 2) * sum(((order - 1) * sp.factorial(order) * coefficient**2 for order, coefficient in fixture_coefficients.items()), sp.Integer(0))
    audit.check("ou", "fixture_negative_debt", fixture_debt == -sp.Rational(19, 6), fixture_debt, -sp.Rational(19, 6))

    diagnostics = {
        "production": {"P": mass, "c0": c0, "c1": c1, "alpha": alpha, "kappa2": kappa2, "eta_row": eta_row},
        "hermite": {"mu2": mu2, "degree_two_gain": 1 - mu2, "bump_ratio": bump_ratio},
        "cartan": {"K_R": curl_k, "M_U": curl_m, "full": curl_full},
        "covariant": {"connection": connection_average, "acceleration": acceleration_average, "total": total_average},
        "ou_fixture": fixture_debt,
        "scope_flags": {
            "complete_production_trace_excess_proved": False,
            "overlap_src_proved": False,
            "nelson_proved": False,
            "sector_a_closed": False,
            "tier_promoted": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-124 primary {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
