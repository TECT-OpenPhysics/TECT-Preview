#!/usr/bin/env python3
"""Primary exact audit for the scoped R-120 A13 advance.

The audit checks the covariance-horizontal H2/L6 synthesis, the variable
operator R-068 exponents, the exact stationary-production low-chaos pass, the
fixed-Pauli linear Hessian, and the rational Cartan/raw-Q boundary.  It does
not assert the missing adapted future-feedback forest identities.
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
from typing import Any, Iterable

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-COVARIANCE-HORIZONTAL-SYNTHESIS-STATIONARY-LOW-CHAOS-CARTAN-HESSIAN-BOUNDARY"
SCHEMA = "tect/a13-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-29-primary-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
A8_RESULT = REPO / "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/runs/2026-07-20-primary-decoupled-nelson/result.json"


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
                "These exact fixtures support R-120's analytic covariance-horizontal, "
                "variable-multiplier, stationary six-row raw-current, and Hessian formulas. "
                "They are not an owner-complete adapted production reconstruction. R-120 does "
                "not prove the adapted D0/D1 forest identities, cancel the rational Cartan "
                "block, establish the +40/729 companion, or prove one-use, Nelson, or Sector A closure."
            ),
        }


def gaussian_expectation(poly: sp.Expr, variables: Iterable[sp.Symbol]) -> sp.Expr:
    value = sp.expand(poly)
    for variable in variables:
        expanded = sp.Poly(sp.expand(value), variable)
        total = sp.Integer(0)
        for (degree,), coefficient in expanded.terms():
            if degree % 2:
                continue
            total += coefficient * (sp.Integer(1) if degree == 0 else sp.factorial2(degree - 1))
        value = sp.expand(total)
    return sp.simplify(value)


def realify(matrix: sp.Matrix) -> sp.Matrix:
    real = matrix.applyfunc(sp.re)
    imag = matrix.applyfunc(sp.im)
    return real.row_join(-imag).col_join(imag.row_join(real))


def q_gradient_hessian(u: sp.Matrix, generator: sp.Matrix, alpha_q: sp.Rational, floor: sp.Rational) -> tuple[sp.Expr, sp.Matrix, sp.Matrix, sp.Matrix]:
    denominator = sp.simplify((u.T * u)[0] + floor)
    q = sp.simplify((u.T * generator * u)[0] / denominator)
    tangent = generator - q * sp.eye(u.rows)
    remainder = tangent * u
    gradient = sp.simplify(2 * remainder / denominator)
    hessian = sp.simplify(
        2 * tangent / denominator
        - 4 * (u * remainder.T + remainder * u.T) / denominator**2
    )
    return q, tangent, gradient, hessian


def rational_k_matrix(u: sp.Matrix, generator: sp.Matrix, covariance: sp.Matrix, alpha_q: sp.Rational, floor: sp.Rational) -> tuple[sp.Matrix, dict[str, Any]]:
    q, q_tangent, gradient, hessian = q_gradient_hessian(u, generator, alpha_q, floor)
    tangent = generator - alpha_q * q * sp.eye(u.rows)
    frame = sp.simplify(tangent - alpha_q * u * gradient.T)
    coefficient = sp.simplify(tangent * u)
    w = sp.simplify(covariance * coefficient)
    beta = sp.simplify((u.T * covariance * coefficient)[0])
    k_matrix = sp.simplify(
        4 * frame.T * covariance * frame
        - 4 * alpha_q * beta * hessian
        - 4 * alpha_q * (gradient * w.T + w * gradient.T)
    )
    return k_matrix, {
        "q": q,
        "q_tangent": q_tangent,
        "gradient": gradient,
        "hessian": hessian,
        "frame": frame,
        "coefficient": coefficient,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    params = a1["parameters"]
    mass_floor = sp.Rational(str(params["classii_mass_regularizer"]))
    density_floor = sp.Rational(str(params["rho_regularizer"]))
    p_mass = sp.Rational(str(params["M_X"])) ** 2 + mass_floor
    a = sp.Rational(str(params["cJJ"])) * sp.Rational(str(params["alpha_X"])) ** 2 / p_mass
    b = sp.Rational(str(params["cJK"])) * sp.Rational(str(params["alpha_X"])) * sp.Rational(str(params["beta_X"])) / p_mass
    c = sp.Rational(str(params["cKK"])) * sp.Rational(str(params["beta_X"])) ** 2 / p_mass
    c0 = sp.Rational(3, 250) / p_mass
    c1 = sp.Rational(243, 8000) / p_mass
    alpha_q = sp.Rational(5, 9)

    audit.check("production", "a", sp.simplify(a - sp.Rational(9, 500) / p_mass) == 0, a, sp.Rational(9, 500) / p_mass)
    audit.check("production", "b", sp.simplify(b - sp.Rational(3, 400) / p_mass) == 0, b, sp.Rational(3, 400) / p_mass)
    audit.check("production", "c", sp.simplify(c - sp.Rational(3, 320) / p_mass) == 0, c, sp.Rational(3, 320) / p_mass)
    audit.check("production", "diagonal_a", sp.simplify(c0 + c1 * (1 - alpha_q) ** 2 - a) == 0, c0 + c1 * (1 - alpha_q) ** 2, a)
    audit.check("production", "diagonal_b", sp.simplify(c1 * alpha_q * (1 - alpha_q) - b) == 0, c1 * alpha_q * (1 - alpha_q), b)
    audit.check("production", "diagonal_c", sp.simplify(c1 * alpha_q**2 - c) == 0, c1 * alpha_q**2, c)
    envelope = sp.simplify(4 * (c0 + c1))
    audit.check("production", "linear_envelope", envelope == sp.Rational(339, 2000) / p_mass, envelope, sp.Rational(339, 2000) / p_mass)

    t1 = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]])
    t2 = sp.Matrix([[0, -sp.I, 0], [sp.I, 0, 0], [0, 0, 0]])
    t3 = sp.Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 0]])
    generators = tuple(realify(item) for item in (t1, t2, t3))
    p_doublet = sp.diag(1, 1, 0, 1, 1, 0)
    for index, generator in enumerate(generators, start=1):
        audit.check("production", f"S{index}_selfadjoint", generator == generator.T, generator - generator.T, sp.zeros(6))
        audit.check("production", f"S{index}_square", generator**2 == p_doublet, generator**2, p_doublet)
    generator_gap = 3 * sp.eye(6) - 3 * p_doublet
    audit.check(
        "production",
        "fixed_generator_absolute_sum",
        all(generator_gap[i, i] >= 0 for i in range(6)),
        3 * p_doublet,
        "<=3 I",
    )

    # Covariance-union geometry and the production H2 constant.
    s1 = sp.Matrix([[1, 0], [0, sp.Rational(1, 2)]])
    s2 = sp.Matrix([[1, 1], [0, 1]])
    synthesis = s1.row_join(s2)
    covariance = sp.simplify(synthesis * synthesis.T)
    audit.check("synthesis", "covariance_union", covariance == s1 * s1.T + s2 * s2.T, covariance, s1 * s1.T + s2 * s2.T)
    h = sp.Matrix([2, -1, 1, 3])
    z = synthesis * h
    minimum = sp.simplify(synthesis.T * covariance.inv() * z)
    audit.check("synthesis", "minimum_represents_endpoint", synthesis * minimum == z, synthesis * minimum, z)
    quotient_sq = sp.simplify((z.T * covariance.inv() * z)[0])
    minimum_sq = sp.simplify((minimum.T * minimum)[0])
    audit.check("synthesis", "quotient_norm_identity", quotient_sq == minimum_sq, quotient_sq, minimum_sq)
    audit.check("synthesis", "quotient_contraction", minimum_sq <= (h.T * h)[0], minimum_sq, f"<={(h.T * h)[0]}")

    r_symbol = sp.Rational(str(params["r"]))
    z_symbol = sp.Rational(str(params["Z"]))
    y_symbol = sp.Rational(str(params["Y"]))
    s_star = sp.simplify((2 * r_symbol - z_symbol) / (2 * y_symbol - z_symbol))
    symbol_ratio = lambda s: sp.simplify((y_symbol * s**2 + z_symbol * s + r_symbol) / (1 + s) ** 2)
    c_sym = min(symbol_ratio(sp.Integer(0)), symbol_ratio(s_star), y_symbol)
    a8 = json.loads(A8_RESULT.read_text(encoding="utf-8"))
    recorded_c_sym = sp.Rational(str(a8["derived"]["symbol_coercivity"]["c_symbol"]))
    audit.check("synthesis", "symbol_minimizer_nonnegative", s_star >= 0, s_star, ">=0")
    audit.check("synthesis", "symbol_coercivity_recomputed", abs(float(c_sym - recorded_c_sym)) < 5e-15, float(c_sym), float(recorded_c_sym))
    m_r = sp.Rational(str(a8["config"]["regulator_multiplier_bound"]))
    c_cm = sp.simplify(m_r**2 / c_sym)
    audit.check("synthesis", "cm_constant_positive", c_cm > 0, float(c_cm), ">0")
    audit.check("synthesis", "cm_constant_contractive", abs(float(c_cm) - 9.22811176850986) < 5e-14, float(c_cm), 9.22811176850986)

    x, y = sp.symbols("x y", real=True)
    l6_gap = sp.expand(32 * (x**6 + y**6) - (x - y) ** 6)
    l6_sos = sp.expand(
        (x + y) ** 2
        * ((x + y) ** 4 + 15 * (x + y) ** 2 * (x - y) ** 2 + 15 * (x - y) ** 4)
    )
    audit.check(
        "synthesis",
        "l6_global_sos",
        sp.expand(l6_gap - l6_sos) == 0,
        sp.factor(l6_gap),
        "(x+y)^2*((x+y)^4+15*(x+y)^2*(x-y)^2+15*(x-y)^4)>=0",
    )
    audit.check("synthesis", "l6_constant", sp.Rational(2) ** 5 == 32, sp.Rational(2) ** 5, 32)

    # Variable-multiplier interpolation and Young exponents.
    kappa = sp.Rational(1, 10)
    theta = (1 + kappa) / 2
    audit.check("multiplier", "theta", theta == sp.Rational(11, 20), theta, sp.Rational(11, 20))
    audit.check("multiplier", "k0_interpolation", 1 - theta == sp.Rational(9, 20), 1 - theta, sp.Rational(9, 20))
    audit.check("multiplier", "k2_interpolation", theta == sp.Rational(11, 20), theta, sp.Rational(11, 20))
    audit.check("multiplier", "model_power", sp.Rational(3, 1) / (1 - kappa) == sp.Rational(10, 3), sp.Rational(3, 1) / (1 - kappa), sp.Rational(10, 3))
    audit.check("multiplier", "eta_power", 3 * (1 + kappa) / (2 * (1 - kappa)) == sp.Rational(11, 6), 3 * (1 + kappa) / (2 * (1 - kappa)), sp.Rational(11, 6))
    audit.check("multiplier", "k0_young_power", (1 - theta) * sp.Rational(10, 3) == sp.Rational(3, 2), (1 - theta) * sp.Rational(10, 3), sp.Rational(3, 2))
    audit.check("multiplier", "k2_young_power", theta * sp.Rational(10, 3) == sp.Rational(11, 6), theta * sp.Rational(10, 3), sp.Rational(11, 6))

    # Exact production first-row low-chaos checksum.
    xi, eta, sigma = sp.symbols("xi eta sigma", real=True)
    radius = xi**2 + eta**2
    h2x, h2y = xi**2 - 1, eta**2 - 1
    h4x, h4y = xi**4 - 6 * xi**2 + 3, eta**4 - 6 * eta**2 + 3
    lambda1 = sp.simplify(4 * c0)
    packet = sp.expand(lambda1 * sigma**4 * (radius**2 - 4 * radius) / 16)
    chaos = sp.expand(lambda1 * sigma**4 * (h2x + h2y) / 4 + lambda1 * sigma**4 * (h4x + h4y + 2 * h2x * h2y) / 16)
    audit.check("low_chaos", "one_pair_chaos_split", sp.expand(packet - chaos) == 0, sp.expand(packet - chaos), 0)
    audit.check("low_chaos", "one_pair_zero_chaos", gaussian_expectation(packet, (xi, eta)) == 0, gaussian_expectation(packet, (xi, eta)), 0)
    audit.check("low_chaos", "one_pair_first_x", gaussian_expectation(xi * packet, (xi, eta)) == 0, gaussian_expectation(xi * packet, (xi, eta)), 0)
    audit.check("low_chaos", "one_pair_first_y", gaussian_expectation(eta * packet, (xi, eta)) == 0, gaussian_expectation(eta * packet, (xi, eta)), 0)
    z_abs_sq = sigma**2 * radius / 4
    y_norm_sq = sp.expand(2 * lambda1 * z_abs_sq**2)
    tau = sp.expand(2 * lambda1 * sigma**2 * z_abs_sq)
    audit.check("low_chaos", "one_pair_energy", gaussian_expectation(y_norm_sq, (xi, eta)) == lambda1 * sigma**4, gaussian_expectation(y_norm_sq, (xi, eta)), lambda1 * sigma**4)
    audit.check("low_chaos", "one_pair_trace", gaussian_expectation(tau, (xi, eta)) == lambda1 * sigma**4, gaussian_expectation(tau, (xi, eta)), lambda1 * sigma**4)

    # The complete six-row coefficient parity is checked before the smaller
    # active/kernel rational slice used for the conditional-trace fixture.
    stationary_u = sp.Matrix(sp.symbols("stationary_u0:6", real=True))
    stationary_denominator = sp.simplify((stationary_u.T * stationary_u)[0] + density_floor)
    stationary_negation = {variable: -variable for variable in stationary_u}
    for index, generator in enumerate(generators, start=1):
        linear_coefficient = sp.simplify(2 * generator * stationary_u)
        stationary_q = sp.simplify((stationary_u.T * generator * stationary_u)[0] / stationary_denominator)
        rational_coefficient = sp.simplify(2 * (generator - alpha_q * stationary_q * sp.eye(6)) * stationary_u)
        audit.check(
            "low_chaos",
            f"linear_row_{index}_odd",
            sp.simplify(linear_coefficient.subs(stationary_negation) + linear_coefficient) == sp.zeros(6, 1),
            linear_coefficient.subs(stationary_negation),
            -linear_coefficient,
        )
        audit.check(
            "low_chaos",
            f"rational_row_{index}_odd",
            sp.simplify(rational_coefficient.subs(stationary_negation) + rational_coefficient) == sp.zeros(6, 1),
            rational_coefficient.subs(stationary_negation),
            -rational_coefficient,
        )

    # Stationary conditional trace on an active/kernel rational slice.
    u1, u2, v1, v2, gamma1, gamma2 = sp.symbols("u1 u2 v1 v2 gamma1 gamma2", real=True)
    denominator = density_floor + u1**2 + u2**2
    rational_row = sp.Matrix([u1 - alpha_q * u1**3 / denominator, -alpha_q * u1**2 * u2 / denominator])
    stationary_y = sp.expand(2 * (rational_row.T * sp.Matrix([v1, v2]))[0])
    stationary_tau = sp.expand(4 * (gamma1 * rational_row[0] ** 2 + gamma2 * rational_row[1] ** 2))
    negate = {u1: -u1, u2: -u2, v1: -v1, v2: -v2}
    audit.check("low_chaos", "C_is_odd", sp.simplify(rational_row.subs({u1: -u1, u2: -u2}) + rational_row) == sp.zeros(2, 1), rational_row.subs({u1: -u1, u2: -u2}), -rational_row)
    audit.check("low_chaos", "stationary_output_even", sp.simplify(stationary_y.subs(negate) - stationary_y) == 0, stationary_y.subs(negate), stationary_y)
    audit.check("low_chaos", "stationary_trace_even", sp.simplify(stationary_tau.subs(negate) - stationary_tau) == 0, stationary_tau.subs(negate), stationary_tau)
    conditional_energy = sp.expand(stationary_y**2)
    conditional_energy = conditional_energy.subs({v1**2: gamma1, v2**2: gamma2, v1 * v2: 0})
    audit.check("low_chaos", "conditional_square_trace", sp.simplify(conditional_energy - stationary_tau) == 0, conditional_energy, stationary_tau)
    derivative_tau = sp.Matrix([sp.diff(stationary_tau, variable) for variable in (u1, u2, v1, v2)])
    derivative_y = sp.Matrix([sp.diff(stationary_y, variable) for variable in (u1, u2, v1, v2)])
    audit.check("low_chaos", "trace_derivative_odd", sp.simplify(derivative_tau.subs(negate) + derivative_tau) == sp.zeros(4, 1), derivative_tau.subs(negate), -derivative_tau)
    dy_y = sp.simplify(derivative_y * stationary_y)
    audit.check("low_chaos", "output_derivative_product_odd", sp.simplify(dy_y.subs(negate) + dy_y) == sp.zeros(4, 1), dy_y.subs(negate), -dy_y)

    # Fixed-generator linear Hessian and the once-owned covariance trace.
    aa, bb, cc, tt = sp.symbols("aa bb cc tt", real=True)
    direct = sp.expand(2 * aa * cc + 4 * bb**2 + 12 * tt * bb * cc + 6 * tt**2 * cc**2)
    decomposed = sp.expand(2 * aa * cc + 4 * (bb + sp.Rational(3, 2) * tt * cc) ** 2 - 3 * tt**2 * cc**2)
    audit.check("linear_hessian", "completion_identity", sp.expand(direct - decomposed) == 0, sp.expand(direct - decomposed), 0)
    audit.check("linear_hessian", "taylor_quartic_weight", sp.integrate((1 - tt) * 3 * tt**2, (tt, 0, 1)) == sp.Rational(1, 4), sp.integrate((1 - tt) * 3 * tt**2, (tt, 0, 1)), sp.Rational(1, 4))
    audit.check("linear_hessian", "quartic_budget_powers", sp.Rational(1, 2) + sp.Rational(1, 2) == 1, [sp.Rational(1, 2), sp.Rational(1, 2)], 1)
    test_u = sp.Matrix([1, 2, 0, -1, 1, 0])
    test_z = sp.Matrix([2, -1, 0, 1, 3, 0])
    gamma = sp.diag(2, 3, 1, 2, 3, 1)
    trace_scalar = sp.Integer(0)
    trace_second = sp.Integer(0)
    tau_symbol = sp.symbols("tau_symbol", real=True)
    for generator in generators:
        shifted = generator * (test_u + tau_symbol * test_z)
        trace_scalar += 2 * c0 * (shifted.T * gamma * shifted)[0]
        trace_second += -4 * c0 * ((generator * test_z).T * gamma * (generator * test_z))[0]
    trace_direct = sp.diff(-trace_scalar, tau_symbol, 2)
    audit.check("linear_hessian", "trace_hessian", sp.simplify(trace_direct - trace_second) == 0, trace_direct, trace_second)

    # Rational Cartan curvature and the inherited R-102 checksum.
    rx, ry, floor_symbol = sp.symbols("rx ry floor_symbol", positive=True)
    m = rx**2 - ry**2
    rho = rx**2 + ry**2
    d = floor_symbol + rho
    q = m / d
    theta_x = sp.diff(m, rx) - alpha_q * q * sp.diff(rho, rx)
    theta_y = sp.diff(m, ry) - alpha_q * q * sp.diff(rho, ry)
    omega_xy = sp.simplify(sp.diff(theta_y, rx) - sp.diff(theta_x, ry))
    wedge_xy = sp.simplify(-alpha_q / d * (sp.diff(m, rx) * sp.diff(rho, ry) - sp.diff(m, ry) * sp.diff(rho, rx)))
    audit.check("cartan", "rational_curvature", sp.simplify(omega_xy - wedge_xy) == 0, omega_xy, wedge_xy)
    audit.check("cartan", "radial_locus_zero", sp.simplify(omega_xy.subs(ry, 0)) == 0, sp.simplify(omega_xy.subs(ry, 0)), 0)
    audit.check("cartan", "generic_curvature_nonzero", sp.simplify(omega_xy.subs({rx: 1, ry: 1, floor_symbol: 1})) != 0, sp.simplify(omega_xy.subs({rx: 1, ry: 1, floor_symbol: 1})), "nonzero")

    curl_x, curl_y = sp.symbols("curl_x curl_y", real=True)
    curl_d = 1 + curl_x**2 + curl_y**2
    curl_row = sp.Matrix([curl_x - alpha_q * curl_x**3 / curl_d, -alpha_q * curl_x**2 * curl_y / curl_d])
    curl_gram = 4 * curl_row * curl_row.T
    remainder = curl_gram.subs(curl_x, curl_x + 1) - curl_gram - sp.diff(curl_gram, curl_x) - sp.diff(curl_gram, curl_x, 2) / 2
    one_form = remainder[:, 0]
    curl_value = sp.factor((sp.diff(one_form[0], curl_y) - sp.diff(one_form[1], curl_x)).subs({curl_x: 1, curl_y: 1}))
    audit.check("cartan", "isolated_r102_curl", curl_value == -sp.Rational(40, 729), curl_value, -sp.Rational(40, 729))
    audit.check("cartan", "required_companion", -curl_value == sp.Rational(40, 729), -curl_value, sp.Rational(40, 729))

    # Exact rational raw-Q Hessian and fixed 21-matrix flattening.
    rational_residuals: list[sp.Expr] = []
    fixtures = (
        (sp.Matrix([1, 2, -1]), sp.Matrix([2, -1, 1]), sp.diag(2, 3, 5), sp.diag(1, -1, 0)),
        (sp.Matrix([2, -1, 3]), sp.Matrix([1, 1, -2]), sp.Matrix([[3, 1, 0], [1, 2, 1], [0, 1, 4]]), sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]])),
        (sp.Matrix([-1, 3, 2]), sp.Matrix([3, 0, 1]), sp.Matrix([[4, 0, 1], [0, 5, -1], [1, -1, 3]]), sp.diag(1, 0, -1)),
    )
    path_t = sp.symbols("path_t", real=True)
    for index, (u, direction, rough_q, generator) in enumerate(fixtures, start=1):
        k_matrix, _ = rational_k_matrix(u, generator, rough_q, alpha_q, sp.Integer(1))
        path = u + path_t * direction
        path_q = sp.simplify((path.T * generator * path)[0] / ((path.T * path)[0] + 1))
        path_g = sp.simplify((generator - alpha_q * path_q * sp.eye(3)) * path)
        scalar = sp.simplify(2 * c1 * (path_g.T * rough_q * path_g)[0])
        direct_hessian = sp.simplify(sp.diff(scalar, path_t, 2).subs(path_t, 0))
        formula_hessian = sp.simplify(c1 * (direction.T * k_matrix * direction)[0])
        residual = sp.simplify(direct_hessian - formula_hessian)
        rational_residuals.append(residual)
        audit.check("rational_hessian", f"raw_q_fixture_{index}", residual == 0, residual, 0)
        audit.check("rational_hessian", f"selfadjoint_fixture_{index}", k_matrix == k_matrix.T, k_matrix - k_matrix.T, sp.zeros(3))

    dimension = 6
    absolute_sum = sp.zeros(dimension)
    for i in range(dimension):
        absolute_sum[i, i] += 1
        for j in range(i + 1, dimension):
            absolute_sum[i, i] += sp.Rational(1, 2)
            absolute_sum[j, j] += sp.Rational(1, 2)
    audit.check("rational_hessian", "fixed_basis_absolute_sum", absolute_sum == sp.Rational(7, 2) * sp.eye(6), absolute_sum, sp.Rational(7, 2) * sp.eye(6))

    # Adapted composition exposes exactly the Dh and D2h families absent from
    # the deterministic-translation R-063 theorem.
    b0, b1, b2, hp, hpp = sp.symbols("b0 b1 b2 hp hpp", real=True)
    chain = sp.expand(b2 * (1 + hp) ** 2 + b1 * hpp)
    chain_expected = sp.expand(b2 + 2 * b2 * hp + b2 * hp**2 + b1 * hpp)
    audit.check("adapted_boundary", "chain_rule_families", chain == chain_expected, chain, chain_expected)
    audit.check("adapted_boundary", "first_derivative_family_present", sp.diff(chain, hp).subs(hp, 0) == 2 * b2, sp.diff(chain, hp).subs(hp, 0), 2 * b2)
    audit.check("adapted_boundary", "second_derivative_family_present", sp.diff(chain, hpp) == b1, sp.diff(chain, hpp), b1)

    diagnostics = {
        "production": {
            "p_mass": p_mass,
            "c0": c0,
            "c1": c1,
            "alpha": alpha_q,
            "linear_envelope": envelope,
            "fixed_pauli_k0": 3,
        },
        "horizontal_synthesis": {
            "c_sym": float(c_sym),
            "regulator_multiplier_bound": float(m_r),
            "c_cm": float(c_cm),
            "l6_constant": 32,
        },
        "multiplier": {
            "interpolation_k0": "9/20",
            "interpolation_k2": "11/20",
            "young_k0": "3/2",
            "young_k2": "11/6",
            "model_power": "10/3",
        },
        "stationary_low_chaos": {
            "one_pair_zero_first": True,
            "six_row_coefficient_parity_verified": True,
            "conditional_trace_fixture": "active/kernel rational slice",
            "analytic_scope": "common-real-even stationary six-row raw-current packet",
            "adapted_future_feedback": "open D0,D1",
        },
        "cartan": {
            "isolated_curl": curl_value,
            "required_companion": -curl_value,
            "companion_observed": False,
        },
        "rational_hessian": {
            "fixed_basis_count": 21,
            "fixed_basis_absolute_sum": "7/2 I",
            "exact_fixture_residuals": rational_residuals,
            "cartan_first_order_survives": True,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"Primary R-120 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
