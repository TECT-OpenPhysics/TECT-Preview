#!/usr/bin/env python3
"""Primary exact audit for the scoped R-121 A13 correction and advance.

The audit separates path-space exactness from target-space one-form closure,
reconstructs the two-visit rational owner telescope, computes all three owner
current curls on the R-102 slice, and derives the sharp fixed-skew Sobolev
one-use exponents.  It does not assert an adapted R-063 forest theorem.
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
RESULT_ID = "A13-CLASSII-CARTAN-PATHSPACE-EXACTNESS-FIXED-SKEW-SOBOLEV-BOUNDARY"
SCHEMA = "tect/a13-cartan-pathspace-exactness-fixed-skew-sobolev-primary/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-29-primary-cartan-pathspace-exactness-fixed-skew-sobolev-boundary/result.json"
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
                "R-121 corrects the local companion-curl inference, proves the exact two-visit "
                "owner telescope, and proves a deterministic fixed-skew H^{-s}, s<1, one-use "
                "theorem.  It does not reconstruct the adapted R-063 forest, evaluate production "
                "D0/D1, prove a uniform adapted H^{-3/5} fifth moment, close A13 one-use, Nelson, "
                "or Sector A."
            ),
        }


def colon(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.expand(sum(left[i, j] * right[i, j] for i in range(left.rows) for j in range(left.cols)))


def gaussian_expectation(poly: sp.Expr, variable: sp.Symbol) -> sp.Expr:
    expanded = sp.Poly(sp.expand(poly), variable)
    total = sp.Integer(0)
    for (degree,), coefficient in expanded.terms():
        if degree % 2:
            continue
        total += coefficient * (sp.Integer(1) if degree == 0 else sp.factorial2(degree - 1))
    return sp.expand(total)


def production_alpha() -> sp.Rational:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = sp.Rational(str(parameters["M_X"])) ** 2 + sp.Rational(str(parameters["classii_mass_regularizer"]))
    b_weight = (
        sp.Rational(str(parameters["cJK"]))
        * sp.Rational(str(parameters["alpha_X"]))
        * sp.Rational(str(parameters["beta_X"]))
        / mass
    )
    c_weight = sp.Rational(str(parameters["cKK"])) * sp.Rational(str(parameters["beta_X"])) ** 2 / mass
    return sp.simplify(c_weight / (b_weight + c_weight))


def owner_current_audit(audit: Audit) -> dict[str, Any]:
    x, y = sp.symbols("x y", real=True)
    alpha = production_alpha()
    audit.check("owner_curl", "production_alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))

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
    b_taylor = sp.simplify(b0 + b0.diff(x) + sp.Rational(1, 2) * b0.diff(x, 2))
    remainder = sp.simplify(b1 - b_taylor)
    point = {x: 1, y: 1}

    expected_b0 = sp.Matrix([[1936, -440], [-440, 100]]) / 729
    expected_b1 = sp.Matrix([[4624, -1360], [-1360, 400]]) / 729
    expected_remainder = sp.Matrix([[80, 520], [520, -300]]) / 2187
    audit.check("owner_curl", "B0_at_slice", sp.simplify(b0.subs(point) - expected_b0) == sp.zeros(2), b0.subs(point), expected_b0)
    audit.check("owner_curl", "B1_at_slice", sp.simplify(b1.subs(point) - expected_b1) == sp.zeros(2), b1.subs(point), expected_b1)
    audit.check(
        "owner_curl",
        "L_at_slice",
        sp.simplify(remainder.subs(point) - expected_remainder) == sp.zeros(2),
        remainder.subs(point),
        expected_remainder,
    )

    omega_k = remainder[:, 0]
    omega_m = b_taylor[:, 0]
    omega_full = b1[:, 0]

    def derivatives(omega: sp.Matrix) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
        dy_x = sp.simplify(sp.diff(omega[0], y).subs(point))
        dx_y = sp.simplify(sp.diff(omega[1], x).subs(point))
        return dy_x, dx_y, sp.simplify(dy_x - dx_y)

    k_dyx, k_dxy, curl_k = derivatives(omega_k)
    m_dyx, m_dxy, curl_m = derivatives(omega_m)
    f_dyx, f_dxy, curl_full = derivatives(omega_full)

    # These exact fractions are test oracles copied from neither executable.
    audit.check("owner_curl", "K_dy_omega_x", k_dyx == sp.Rational(-4480, 6561), k_dyx, sp.Rational(-4480, 6561))
    audit.check("owner_curl", "K_dx_omega_y", k_dxy == sp.Rational(-4120, 6561), k_dxy, sp.Rational(-4120, 6561))
    audit.check("owner_curl", "K_repo_curl", curl_k == sp.Rational(-40, 729), curl_k, sp.Rational(-40, 729))
    audit.check("owner_curl", "M_dy_omega_x", m_dyx == sp.Rational(20800, 6561), m_dyx, sp.Rational(20800, 6561))
    audit.check("owner_curl", "M_dx_omega_y", m_dxy == sp.Rational(-3680, 6561), m_dxy, sp.Rational(-3680, 6561))
    audit.check("owner_curl", "M_repo_curl", curl_m == sp.Rational(2720, 729), curl_m, sp.Rational(2720, 729))
    audit.check("owner_curl", "full_dy_omega_x", f_dyx == sp.Rational(5440, 2187), f_dyx, sp.Rational(5440, 2187))
    audit.check("owner_curl", "full_dx_omega_y", f_dxy == sp.Rational(-2600, 2187), f_dxy, sp.Rational(-2600, 2187))
    audit.check("owner_curl", "full_repo_curl", curl_full == sp.Rational(2680, 729), curl_full, sp.Rational(2680, 729))
    audit.check("owner_curl", "current_recombination", sp.simplify(omega_m + omega_k - omega_full) == sp.zeros(2, 1), omega_m + omega_k - omega_full, sp.zeros(2, 1))
    audit.check("owner_curl", "curl_recombination", sp.simplify(curl_m + curl_k - curl_full) == 0, curl_m + curl_k, curl_full)
    audit.check("owner_curl", "M_is_not_opposite_companion", curl_m != -curl_k, curl_m, -curl_k)
    audit.check("owner_curl", "full_current_not_closed", curl_full != 0, curl_full, "nonzero")
    terminal_square = sp.simplify(sp.Rational(1, 2) * b1[0, 0])
    terminal_gradient_curl = sp.simplify(sp.diff(sp.diff(terminal_square, x), y) - sp.diff(sp.diff(terminal_square, y), x))
    audit.check("owner_curl", "terminal_square_gradient_curl", terminal_gradient_curl == 0, terminal_gradient_curl, 0)
    ellipse_mixed_hessian = sp.simplify(-curl_k / 2)
    audit.check(
        "path_space",
        "R102_ellipse_mixed_hessian",
        ellipse_mixed_hessian == sp.Rational(20, 729),
        ellipse_mixed_hessian,
        sp.Rational(20, 729),
    )

    return {
        "B0": b0.subs(point),
        "B1": b1.subs(point),
        "L": remainder.subs(point),
        "repo_curls": {"K_R": curl_k, "M_U": curl_m, "M_U_plus_K_R": curl_full},
        "standard_exterior_curl_K_R": -curl_k,
        "normalized_ellipse_mixed_hessian": ellipse_mixed_hessian,
    }


def owner_telescope_audit(audit: Audit) -> dict[str, Any]:
    b0a, b0b, b0c, b1a, b1b, b1c, b2a, b2b, b2c = sp.symbols(
        "b0a b0b b0c b1a b1b b1c b2a b2b b2c", real=True
    )
    t1a, t1b, t1c, t2a, t2b, t2c = sp.symbols("t1a t1b t1c t2a t2b t2c", real=True)
    g01, g02, d11, d12, d21, d22 = sp.symbols("g01 g02 d11 d12 d21 d22", real=True)
    ga, gb, gc = sp.symbols("ga gb gc", real=True)
    matrices = [
        sp.Matrix([[b0a, b0b], [b0b, b0c]]),
        sp.Matrix([[b1a, b1b], [b1b, b1c]]),
        sp.Matrix([[b2a, b2b], [b2b, b2c]]),
    ]
    taylors = [sp.Matrix([[t1a, t1b], [t1b, t1c]]), sp.Matrix([[t2a, t2b], [t2b, t2c]])]
    gamma = sp.Matrix([[ga, gb], [gb, gc]])
    gradients = [sp.Matrix([g01, g02])]
    increments = [sp.Matrix([d11, d12]), sp.Matrix([d21, d22])]
    gradients.extend([gradients[0] + increments[0], gradients[0] + increments[0] + increments[1]])

    owner_sums: list[sp.Expr] = []
    endpoint_differences: list[sp.Expr] = []
    for index in range(2):
        previous_b, next_b = matrices[index], matrices[index + 1]
        previous_g, next_g = gradients[index], gradients[index + 1]
        increment, taylor = increments[index], taylors[index]
        previous_q = previous_g * previous_g.T - gamma
        next_q = next_g * next_g.T - gamma
        r_q = sp.Rational(1, 2) * colon(next_b - previous_b, previous_q)
        m_u = (previous_g.T * taylor * increment)[0]
        k_r = (previous_g.T * (next_b - taylor) * increment)[0] + sp.Rational(1, 2) * (increment.T * next_b * increment)[0]
        owner_sum = sp.expand(r_q + m_u + k_r)
        endpoint = sp.Rational(1, 2) * colon(next_b, next_q) - sp.Rational(1, 2) * colon(previous_b, previous_q)
        owner_sums.append(owner_sum)
        endpoint_differences.append(sp.expand(endpoint))
        defect = sp.simplify(owner_sum - endpoint)
        audit.check("owner_telescope", f"visit_{index + 1}_defect", defect == 0, defect, 0)

    total_defect = sp.simplify(sum(owner_sums) - (endpoint_differences[0] + endpoint_differences[1]))
    terminal_defect = sp.simplify(
        sum(owner_sums)
        - (
            sp.Rational(1, 2) * colon(matrices[2], gradients[2] * gradients[2].T - gamma)
            - sp.Rational(1, 2) * colon(matrices[0], gradients[0] * gradients[0].T - gamma)
        )
    )
    audit.check("owner_telescope", "two_visit_defect", total_defect == 0, total_defect, 0)
    audit.check("owner_telescope", "terminal_endpoint_only", terminal_defect == 0, terminal_defect, 0)
    for symbol in (b1a, b1b, b1c, t1a, t1b, t1c, t2a, t2b, t2c):
        derivative = sp.simplify(sp.diff(terminal_defect, symbol))
        audit.check("owner_telescope", f"cancel_{symbol}", derivative == 0, derivative, 0)

    return {
        "visit_defects": [sp.simplify(owner_sums[i] - endpoint_differences[i]) for i in range(2)],
        "two_visit_defect": terminal_defect,
        "intermediate_owner_cancels": True,
        "heat_location": "internal to the common heat-smoothed coefficient B_k",
        "forest_location": "endpoint reconstruction once; not an appended repair",
    }


def path_space_audit(audit: Audit) -> dict[str, Any]:
    t = sp.symbols("t", real=True)
    x, y = sp.symbols("x y", real=True)
    theta_x = -y / 2
    theta_y = x / 2
    curvature = sp.diff(theta_y, x) - sp.diff(theta_x, y)
    circle = sp.Matrix([sp.cos(t), sp.sin(t)])
    velocity = circle.diff(t)
    action_integrand = sp.simplify(theta_x.subs({x: circle[0], y: circle[1]}) * velocity[0] + theta_y.subs({x: circle[0], y: circle[1]}) * velocity[1])
    action = sp.integrate(action_integrand, (t, 0, 2 * sp.pi))
    z = sp.Matrix([sp.cos(t), 0])
    w = sp.Matrix([0, sp.sin(t)])
    h_zw = sp.integrate(z[0] * w.diff(t)[1] - z[1] * w.diff(t)[0], (t, 0, 2 * sp.pi))
    h_wz = sp.integrate(w[0] * z.diff(t)[1] - w[1] * z.diff(t)[0], (t, 0, 2 * sp.pi))
    audit.check("path_space", "target_one_form_nonclosed", curvature == 1, curvature, 1)
    audit.check("path_space", "circle_action", action == sp.pi, action, sp.pi)
    audit.check("path_space", "mixed_hessian_zw", h_zw == sp.pi, h_zw, sp.pi)
    audit.check("path_space", "mixed_hessian_wz", h_wz == sp.pi, h_wz, sp.pi)
    audit.check("path_space", "hessian_symmetric", sp.simplify(h_zw - h_wz) == 0, h_zw - h_wz, 0)
    audit.check("path_space", "nonclosed_but_exact_scalar", curvature != 0 and action != 0 and h_zw == h_wz, True, True)
    return {
        "theta": "(-y/2) dx + (x/2) dy",
        "dtheta": curvature,
        "circle_action": action,
        "mixed_hessian": h_zw,
    }


def skew_and_sobolev_audit(audit: Audit) -> dict[str, Any]:
    dimension = 6
    basis: list[sp.Matrix] = []
    absolute_sum = sp.zeros(dimension)
    for p in range(dimension):
        for q in range(p + 1, dimension):
            matrix = sp.zeros(dimension)
            matrix[p, q] = sp.Rational(1, 2)
            matrix[q, p] = sp.Rational(-1, 2)
            basis.append(matrix)
            modulus = sp.zeros(dimension)
            modulus[p, p] = sp.Rational(1, 2)
            modulus[q, q] = sp.Rational(1, 2)
            absolute_sum += modulus
            audit.check("skew_basis", f"A_{p + 1}_{q + 1}_skew", matrix.T == -matrix, matrix.T + matrix, sp.zeros(dimension))
    audit.check("skew_basis", "basis_count", len(basis) == 15, len(basis), 15)
    audit.check("skew_basis", "absolute_sum", absolute_sum == sp.Rational(5, 2) * sp.eye(dimension), absolute_sum, sp.Rational(5, 2) * sp.eye(dimension))

    z_symbols = sp.Matrix(sp.symbols("z0:6", real=True))
    v_symbols = sp.Matrix(sp.symbols("v0:6", real=True))
    wedge_square = sp.expand(sum(((z_symbols.T * matrix * v_symbols)[0]) ** 2 for matrix in basis))
    wedge_oracle = sp.expand(
        sp.Rational(1, 4)
        * ((z_symbols.T * z_symbols)[0] * (v_symbols.T * v_symbols)[0] - (z_symbols.T * v_symbols)[0] ** 2)
    )
    audit.check("skew_basis", "wedge_square_identity", sp.expand(wedge_square - wedge_oracle) == 0, wedge_square, wedge_oracle)

    s = sp.symbols("s", real=True)
    x_power = sp.simplify((1 + 3 * s) / 4)
    y_power = sp.simplify((1 - s) / 4)
    gap = sp.simplify(1 - x_power - y_power)
    moment = sp.simplify(1 / gap)
    eta_power = sp.simplify(x_power / gap)
    zeta_power = sp.simplify(y_power / gap)
    audit.check("sobolev", "general_gap", sp.simplify(gap - (1 - s) / 2) == 0, gap, (1 - s) / 2)
    audit.check("sobolev", "general_moment", sp.simplify(moment - 2 / (1 - s)) == 0, moment, 2 / (1 - s))
    audit.check("sobolev", "general_eta_power", sp.simplify(eta_power - (1 + 3 * s) / (2 * (1 - s))) == 0, eta_power, (1 + 3 * s) / (2 * (1 - s)))
    audit.check("sobolev", "general_zeta_power", sp.simplify(zeta_power - sp.Rational(1, 2)) == 0, zeta_power, sp.Rational(1, 2))

    production_s = sp.Rational(3, 5)
    values = {
        "s": production_s,
        "X_power": sp.simplify(x_power.subs(s, production_s)),
        "Y_power": sp.simplify(y_power.subs(s, production_s)),
        "gap": sp.simplify(gap.subs(s, production_s)),
        "moment": sp.simplify(moment.subs(s, production_s)),
        "eta_power": sp.simplify(eta_power.subs(s, production_s)),
        "zeta_power": sp.simplify(zeta_power.subs(s, production_s)),
    }
    expected = {
        "s": sp.Rational(3, 5),
        "X_power": sp.Rational(7, 10),
        "Y_power": sp.Rational(1, 10),
        "gap": sp.Rational(1, 5),
        "moment": 5,
        "eta_power": sp.Rational(7, 2),
        "zeta_power": sp.Rational(1, 2),
    }
    for key, oracle in expected.items():
        audit.check("sobolev", f"s_three_fifths_{key}", values[key] == oracle, values[key], oracle)
    audit.check("sobolev", "R071_old_moment_is_stronger", sp.Rational(45, 4) > values["moment"], sp.Rational(45, 4), f">{values['moment']}")

    a0, epsilon, epsilon6, k_sk = sp.symbols("A0 epsilon epsilon6 Ksk", positive=True)
    horizontal_remainder = sp.simplify(
        k_sk**5
        * (epsilon / a0) ** (-sp.Rational(7, 2))
        * (epsilon6 / 32) ** (-sp.Rational(1, 2))
    )
    horizontal_oracle = sp.sqrt(32) * k_sk**5 * a0 ** sp.Rational(7, 2) * epsilon ** (-sp.Rational(7, 2)) * epsilon6 ** (-sp.Rational(1, 2))
    audit.check("sobolev", "horizontal_substitution", sp.simplify(horizontal_remainder - horizontal_oracle) == 0, horizontal_remainder, horizontal_oracle)

    return {
        "basis_count": len(basis),
        "absolute_operator_sum": sp.Rational(5, 2),
        "canonical_wedge_l2_constant": sp.Rational(1, 2),
        "interpolation": {
            "H0": "X^(1/4) Y^(1/4)",
            "H1": "X",
            "Hs": "X^((1+3s)/4) Y^((1-s)/4)",
        },
        "s_three_fifths": values,
        "horizontal_remainder_with_abstract_C_sk": horizontal_oracle,
    }


def high_frequency_and_low_chaos_audit(audit: Audit) -> dict[str, Any]:
    s_bad = sp.Rational(11, 10)
    growth = sp.simplify(s_bad - 1)
    audit.check("high_frequency", "bad_growth_exponent", growth == sp.Rational(1, 10), growth, sp.Rational(1, 10))
    audit.check("high_frequency", "positive_growth", growth > 0, growth, ">0")
    audit.check("high_frequency", "absolute_threshold", sp.simplify(s_bad > 1), s_bad, ">1")
    n = sp.symbols("N", positive=True, integer=True)
    pairing = -sp.Rational(1, 2) * n ** growth
    audit.check("high_frequency", "pairing_formula", pairing == -n ** sp.Rational(1, 10) / 2, pairing, -n ** sp.Rational(1, 10) / 2)
    h2_derivative_norm = sp.Rational(3, 2) + 1 / (2 * n**2) + 1 / (2 * n**4)
    l6_sixth = 1 + sp.Rational(3, 2) / n**4 + sp.Rational(9, 8) / n**8 + sp.Rational(5, 16) / n**12
    audit.check("high_frequency", "H2_uniform_at_N_ge_1", sp.simplify(h2_derivative_norm.subs(n, 1)) <= sp.Rational(5, 2), h2_derivative_norm.subs(n, 1), "<=5/2")
    audit.check("high_frequency", "L6_uniform_at_N_ge_1", sp.simplify(l6_sixth.subs(n, 1)) < 4, l6_sixth.subs(n, 1), "<4")

    g, affine, alpha, beta, q0, q1 = sp.symbols("g affine alpha beta q0 q1", real=True)
    h2 = g**2 - 1
    h3 = g**3 - 3 * g
    residual = alpha * h2 + beta * h3
    d0 = sp.expand(q0 - gaussian_expectation(residual**2, g))
    d1 = sp.expand(q1 - gaussian_expectation(g * (residual**2 + 2 * affine * g * residual), g))
    expected_d0 = q0 - 2 * alpha**2 - 6 * beta**2
    expected_d1 = q1 - 4 * affine * alpha - 12 * alpha * beta
    audit.check("adapted_low_chaos", "D0_scalar_diagnostic", sp.expand(d0 - expected_d0) == 0, d0, expected_d0)
    audit.check("adapted_low_chaos", "D1_scalar_diagnostic", sp.expand(d1 - expected_d1) == 0, d1, expected_d1)

    s1, s2, dh2, d2h2 = sp.symbols("S1 S2 Dh2 D2h2", real=True)
    v = s1 + s2 * dh2
    expanded_second = sp.expand(v**2 + s2 * d2h2)
    expected_second = s1**2 + 2 * s1 * s2 * dh2 + s2**2 * dh2**2 + s2 * d2h2
    audit.check("adapted_low_chaos", "four_adapted_families", sp.expand(expanded_second - expected_second) == 0, expanded_second, expected_second)

    return {
        "counterfixture": {
            "z_N": "(1,N^-2 sin(Nx))",
            "Q_N": "N^s cos(Nx)",
            "pairing": pairing,
            "H2_derivative_norm_squared": h2_derivative_norm,
            "L6_sixth_power": l6_sixth,
            "Hminus_s_norm_squared": "N^(2s)/(2(1+N^2)^s) <= 1/2",
        },
        "D0": expected_d0,
        "D1": expected_d1,
        "adapted_hessian_families": [
            "D2B[S1,S1]",
            "2D2B[S1,S2 Dh2]",
            "D2B[S2 Dh2,S2 Dh2]",
            "DB[S2 D2h2]",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    diagnostics = {
        "owner_current": owner_current_audit(audit),
        "owner_telescope": owner_telescope_audit(audit),
        "path_space": path_space_audit(audit),
        "fixed_skew": skew_and_sobolev_audit(audit),
        "frontier": high_frequency_and_low_chaos_audit(audit),
        "scope": {
            "mandatory_plus_40_over_729_companion": False,
            "isolated_chain_primitive_no_go_retained": True,
            "two_visit_owner_telescope": True,
            "fixed_skew_s_less_than_one": True,
            "unshifted_R071_at_s_three_fifths": True,
            "adapted_R063_forest": False,
            "adapted_D0_D1_evaluated": False,
            "adapted_uniform_fifth_moment": False,
            "A13_one_use": False,
            "sector_A_closure": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-121 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
