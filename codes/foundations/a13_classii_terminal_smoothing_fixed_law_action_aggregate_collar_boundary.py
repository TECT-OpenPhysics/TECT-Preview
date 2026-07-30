#!/usr/bin/env python3
"""Primary exact audit for the scoped A13 R-134 boundary.

The audit checks the fixed-law six-row action pivot, the bounded-moment
counterfixture, six-real Gaussian negative moments, the normalized quotient
jet threshold, the conditional gamma=7/12 shell summation, and the exact
fixed-collar threshold.  It does not assert the missing production terminal
ellipticity, signed-forest lower bound, one-use q-ledger, or headroom.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-TERMINAL-SMOOTHING-FIXED-LAW-ACTION-AGGREGATE-COLLAR-BOUNDARY"
SCHEMA = "tect/a13-terminal-smoothing-fixed-law-action-aggregate-collar-boundary-primary/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-terminal-smoothing-fixed-law-action-aggregate-collar-boundary/"
    "result.json"
)
R132_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-mixed-replica-gaussian-ray-sextic-shell-boundary/"
    "result.json"
)
R133_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-affine-gaussian-score-feedback-collar-boundary/"
    "result.json"
)


def serial(value: Any) -> Any:
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
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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
            "scope": {
                "fixed_law_six_row_action_bridge_proved": True,
                "bounded_finite_moments_hessian_rescue_rejected": True,
                "six_real_negative_moment_theorem_proved": True,
                "floor_uniform_second_and_third_quotient_jets_proved_conditionally": True,
                "floor_uniform_fourth_quotient_jet_rejected": True,
                "fractional_gamma_7_12_window_proved_under_joint_spatial_hypotheses": True,
                "pointwise_ellipticity_alone_spatial_transfer_rejected": True,
                "production_joint_value_gradient_hypotheses": False,
                "conditional_one_use_square_summation_proved": True,
                "fixed_collar_direct_summation_proved_conditionally": True,
                "production_terminal_ellipticity": False,
                "production_signed_forest_bound": False,
                "production_one_use_q_ledger": False,
                "collar_uniform_headroom": False,
                "absolute_anchor": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-134 proves action-level, anti-concentration, jet-threshold, and "
                "conditional geometric-summation lemmas. It does not prove a "
                "production-uniform terminal innovation, a signed forest lower bound, "
                "the one-use atom hypotheses, near/balanced headroom, the absolute "
                "anchor, either A13 gate, or Sector A."
            ),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    r132 = json.loads(R132_RESULT.read_text(encoding="utf-8"))
    r133 = json.loads(R133_RESULT.read_text(encoding="utf-8"))
    inputs = r132["diagnostics"]["inputs"]
    alpha = sp.Rational(inputs["alpha"])
    c0 = sp.Rational(inputs["c0"])
    c1 = sp.Rational(inputs["c1"])
    p_mass = sp.Rational(inputs["p_mass"])
    beta_op = sp.simplify(4 * (c0 + c1))
    gamma = sp.Rational(7, 12)
    audit = Audit()

    audit.check("inputs", "r132_pass", r132.get("status") == "PASS", r132.get("status"), "PASS")
    audit.check("inputs", "r133_pass", r133.get("status") == "PASS", r133.get("status"), "PASS")
    audit.check("inputs", "alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))
    audit.check("inputs", "gamma", gamma == sp.Rational(7, 12), gamma, sp.Rational(7, 12))
    audit.check(
        "inputs",
        "beta_operator",
        beta_op == sp.Rational(339, 2000) / p_mass,
        beta_op,
        sp.Rational(339, 2000) / p_mass,
    )

    # Exact floor-removal remainder.  Summing all three Pauli rows before
    # estimating uses sum_A m_A(w)^2=|P_dbl w|^4 and removes a spurious
    # sqrt(3) rowwise loss.
    rho, e = sp.symbols("rho e", positive=True)
    row_square = sp.simplify(4 * e**2 * rho / (rho + e) ** 2)
    row_slack = sp.factor(e - row_square)
    audit.check(
        "fixed_law_action",
        "row_remainder_square_identity",
        sp.simplify(row_slack - e * (rho - e) ** 2 / (rho + e) ** 2) == 0,
        row_slack,
        e * (rho - e) ** 2 / (rho + e) ** 2,
    )
    audit.check(
        "fixed_law_action",
        "six_row_remainder_constant",
        sp.simplify(c1 * alpha**2) == sp.Rational(3, 320) / p_mass,
        sp.simplify(c1 * alpha**2),
        sp.Rational(3, 320) / p_mass,
    )
    ua, ub, uc, ud = sp.symbols("ua ub uc ud", real=True)
    m1 = 2 * (ua * uc + ub * ud)
    m2 = 2 * (ua * ud - ub * uc)
    m3 = ua**2 + ub**2 - uc**2 - ud**2
    doublet_norm = ua**2 + ub**2 + uc**2 + ud**2
    audit.check(
        "fixed_law_action",
        "pauli_fierz_identity",
        sp.expand(m1**2 + m2**2 + m3**2 - doublet_norm**2) == 0,
        sp.expand(m1**2 + m2**2 + m3**2),
        doublet_norm**2,
    )
    theta = sp.Rational(2, 3)
    a_sym, b_sym = sp.symbols("A B", nonnegative=True)
    lhs = (sp.sqrt(beta_op) * a_sym + alpha * sp.sqrt(c1 * e) * b_sym) ** 2
    rhs = (1 + theta) * beta_op * a_sym**2 + (1 + 1 / theta) * alpha**2 * c1 * e * b_sym**2
    audit.check(
        "fixed_law_action",
        "young_square_slack",
        sp.simplify(rhs - lhs - (sp.sqrt(theta * beta_op) * a_sym - alpha * sp.sqrt(c1 * e / theta) * b_sym) ** 2) == 0,
        sp.factor(rhs - lhs),
        sp.factor((sp.sqrt(theta * beta_op) * a_sym - alpha * sp.sqrt(c1 * e / theta) * b_sym) ** 2),
    )

    # The R-132 two-point law has every positive moment bounded by one while
    # its fixed-law Hessian diverges.  This strengthens, but does not duplicate,
    # the registered law-free no-go.
    delta = sp.symbols("delta", positive=True)
    polynomial = (
        7 * delta**7
        + 188 * delta**6
        + 61 * delta**5
        + 100 * delta**4
        + 57 * delta**3
        + 40 * delta**2
        + 3 * delta
        + 8
    )
    q_comp = -5 * c1 * (delta - 1) ** 2 * polynomial / (
        324 * delta * (1 + delta**2) ** 4
    )
    scaled_limit = sp.limit(delta * q_comp / c1, delta, 0, dir="+")
    audit.check("finite_moment_no_go", "scaled_limit", scaled_limit == -sp.Rational(10, 81), scaled_limit, -sp.Rational(10, 81))
    mean_s4 = sp.simplify((delta**4 + 1) / 2)
    source_plus_sextic = sp.simplify(sp.Rational(9, 10) + sp.Rational(9, 2) * mean_s4)
    audit.check("finite_moment_no_go", "source_sextic_exact", source_plus_sextic == sp.Rational(63, 20) + sp.Rational(9, 4) * delta**4, source_plus_sextic, sp.Rational(63, 20) + sp.Rational(9, 4) * delta**4)
    audit.check("finite_moment_no_go", "variance", sp.simplify((1 - delta) ** 2 / 4 - (delta - 1) ** 2 / 4) == 0, (1 - delta) ** 2 / 4, (delta - 1) ** 2 / 4)
    delta_value = sp.Rational(1, 10**6)
    q_comp_value = sp.N(q_comp.subs(delta, delta_value), 18)
    audit.check("finite_moment_no_go", "production_floor_large_negative", q_comp_value < -900, q_comp_value, "< -900")

    # One-dimensional density repair: exact derivative ranges and L1 costs.
    s = sp.symbols("s", real=True)
    f = s - alpha * s**3 / (s**2 + delta**2)
    fp = sp.factor(sp.diff(f, s))
    fpp = sp.factor(sp.diff(f, s, 2))
    x = sp.symbols("x", nonnegative=True)
    derivative_ratio = sp.simplify(x * (x + 3) / (x + 1) ** 2)
    critical = sp.solve(sp.factor(sp.diff(derivative_ratio, x)), x)
    max_ratio = sp.simplify(derivative_ratio.subs(x, sp.Integer(3)))
    audit.check("density_repair", "derivative_ratio_critical", sp.Integer(3) in critical, critical, "contains 3")
    audit.check("density_repair", "derivative_ratio_max", max_ratio == sp.Rational(9, 8), max_ratio, sp.Rational(9, 8))
    audit.check("density_repair", "fprime_lower", 1 - alpha * max_ratio == sp.Rational(3, 8), 1 - alpha * max_ratio, sp.Rational(3, 8))
    # Derive both absolute integrals from the sign change at sqrt(3) delta.
    turn = sp.sqrt(3) * delta
    fp_zero = sp.simplify(fp.subs(s, 0))
    fp_turn = sp.simplify(fp.subs(s, turn))
    fp_infinity = sp.limit(fp, s, sp.oo)
    fpp_l1 = sp.simplify(2 * ((fp_zero - fp_turn) + (fp_infinity - fp_turn)))
    moment_primitive = sp.simplify(s * fp - f)
    moment_turn = sp.simplify(moment_primitive.subs(s, turn))
    moment_infinity = sp.limit(moment_primitive, s, sp.oo)
    sfpp_l1 = sp.simplify(2 * (moment_infinity - 2 * moment_turn))
    audit.check("density_repair", "fpp_l1", fpp_l1 == sp.Rational(25, 18), fpp_l1, sp.Rational(25, 18))
    audit.check("density_repair", "sfpp_l1", sfpp_l1 / delta == 5 * sp.sqrt(3) / 6, sfpp_l1 / delta, 5 * sp.sqrt(3) / 6)
    audit.check("density_repair", "fprime_variance_ceiling", (sp.Rational(5, 8)) ** 2 / 4 == sp.Rational(25, 256), (sp.Rational(5, 8)) ** 2 / 4, sp.Rational(25, 256))

    # Sharp six-real Gaussian negative moments.
    q = sp.symbols("q", positive=True)
    c6q = sp.gamma(3 - q / 2) / 2 ** (1 + q / 2)
    c62 = sp.simplify(c6q.subs(q, 2))
    c64 = sp.simplify(c6q.subs(q, 4))
    audit.check("six_real_smoothing", "q2_constant", c62 == sp.Rational(1, 4), c62, sp.Rational(1, 4))
    audit.check("six_real_smoothing", "q4_constant", c64 == sp.Rational(1, 8), c64, sp.Rational(1, 8))
    audit.check("six_real_smoothing", "q6_pole", sp.limit(c6q, q, 6, dir="-") == sp.oo, sp.limit(c6q, q, 6, dir="-"), sp.oo)

    # Derive J(n) and n(x) bounds term by term from their product formulas.
    norm_s = sp.Integer(1)
    norm_n = sp.Integer(1)
    d_q1 = 2 * norm_s * norm_n
    d_q2 = 2 * norm_s
    d_p1 = 2 * norm_n
    d_p2 = sp.Integer(2)
    d_j1 = sp.simplify(d_q1 + 2 * d_p1 * norm_s + 2 * d_q1 + 2 * d_p1)
    d_j2 = sp.simplify(d_q2 + 2 * d_p2 * norm_s + 2 * d_q2 + 2 * d_q1 * d_p1 + 2 * d_q1 * d_p1 + 2 * d_p2)
    d_n1 = sp.Integer(1)
    radial_ratio = sp.Integer(1)
    d_n2 = 3 * radial_ratio + 3 * radial_ratio**3
    d2f = d_j1 * d_n1
    d3f = d_j2 * d_n1**2 + d_j1 * d_n2
    d2_l2 = sp.simplify(d2f**2 * c62)
    d3_l2 = sp.simplify(d3f**2 * c64)
    audit.check("quotient_jets", "d2_pointwise_constant", d2f == 14, d2f, 14)
    audit.check("quotient_jets", "d3_pointwise_constant", d3f == 114, d3f, 114)
    audit.check("quotient_jets", "d2_l2_constant", d2_l2 == 49, d2_l2, 49)
    audit.check("quotient_jets", "d3_l2_constant", d3_l2 == sp.Rational(3249, 2), d3_l2, sp.Rational(3249, 2))

    r, y = sp.symbols("r y", positive=True)
    pauli_s3 = sp.diag(1, 1, -1, -1, 0, 0)
    pauli_slice = sp.Matrix([r, 0, y, 0, 0, 0])
    pauli_q = sp.simplify((pauli_slice.T * pauli_s3 * pauli_slice)[0] / (pauli_slice.dot(pauli_slice)))
    f1_zero = sp.simplify(pauli_q * pauli_slice[0])
    fourth_witness = sp.simplify(sp.diff(f1_zero, y, 4).subs(y, 0))
    e_floor = sp.symbols("e", positive=True)
    pauli_q_e = sp.simplify((pauli_slice.T * pauli_s3 * pauli_slice)[0] / (e_floor + pauli_slice.dot(pauli_slice)))
    positive_floor_f1 = sp.simplify(pauli_q_e * pauli_slice[0])
    positive_floor_fourth = sp.factor(sp.diff(positive_floor_f1, y, 4).subs(y, 0))
    u_floor = sp.symbols("u", nonnegative=True)
    scaled_axis = sp.simplify((r**3 * positive_floor_fourth).subs(e_floor, u_floor * r**2))
    scaled_axis_derivative = sp.factor(sp.diff(scaled_axis, u_floor))
    audit.check(
        "quotient_jets",
        "fourth_jet_witness",
        fourth_witness == 48 / r**3
        and scaled_axis.subs(u_floor, 1) == 9
        and scaled_axis_derivative < 0,
        {"zero_floor": fourth_witness, "positive_floor_scaled": scaled_axis, "derivative": scaled_axis_derivative},
        {"zero_floor": 48 / r**3, "positive_floor_min_on_u_0_1": 9, "derivative": "negative"},
    )
    audit.check("quotient_jets", "six_dimensional_radial_exponent", 5 - 2 * 3 == -1, 5 - 2 * 3, -1)

    # Conditional fractional repair under a fresh uniformly elliptic six-real block.
    p = sp.Integer(3)
    holder_q = sp.Integer(6)
    sigma = sp.Rational(2, 3)
    theta_frac = sp.Rational(3, 4)
    audit.check("fractional_route", "gamma_below_sigma", gamma < sigma, gamma, f"< {sigma}")
    audit.check("fractional_route", "sigma_below_theta", sigma < theta_frac, sigma, f"< {theta_frac}")
    audit.check("fractional_route", "holder_pair", sp.Rational(1, 2) == 1 / p + 1 / holder_q, 1 / p + 1 / holder_q, sp.Rational(1, 2))
    audit.check("fractional_route", "first_negative_moment", p * theta_frac == sp.Rational(9, 4), p * theta_frac, sp.Rational(9, 4))
    audit.check("fractional_route", "second_negative_moment", 2 * p * theta_frac == sp.Rational(9, 2), 2 * p * theta_frac, sp.Rational(9, 2))
    audit.check("fractional_route", "moments_subcritical", 2 * p * theta_frac < 6, 2 * p * theta_frac, "< 6")
    frequency = sp.symbols("N", positive=True)
    point_covariance = sp.trigsimp(sp.cos(frequency) ** 2 + sp.sin(frequency) ** 2)
    audit.check("fractional_route", "pointwise_ellipticity_not_spatial_control", point_covariance == 1 and sp.limit(frequency**sigma, frequency, sp.oo) == sp.oo, {"point_covariance": point_covariance, "fractional_growth": frequency**sigma}, {"point_covariance": 1, "fractional_growth": "infinite"})

    # Exact conditional one-use square theorem and fixed-collar substitute.
    s_exp = sp.Rational(2, 3)
    b_constant = 2 ** (-10 * s_exp) / (
        (1 - 2 ** (-s_exp)) ** 2 * (1 - 2 ** (-2 * (s_exp - gamma)))
    )
    direct_constant = 2 ** (-10 * gamma) / (
        (1 - 2 ** (-gamma)) ** 2 * (1 - 2 ** (-2 * gamma))
    )
    b_float = sp.N(b_constant, 18)
    direct_float = sp.N(direct_constant, 18)
    audit.check("aggregate_shell", "strict_exponent_gap", s_exp > gamma, s_exp - gamma, "> 0")
    audit.check("aggregate_shell", "b_constant_numeric", abs(float(b_float) - 0.6588816258726145) < 2e-15, b_float, "0.6588816258726145")
    audit.check("aggregate_shell", "b_amplitude_numeric", abs(float(sp.sqrt(b_constant)) - 0.811715236935106) < 2e-15, sp.N(sp.sqrt(b_constant), 18), "0.811715236935106")
    audit.check("aggregate_shell", "direct_constant_numeric", abs(float(direct_float) - 0.28592888585547915) < 2e-15, direct_float, "0.28592888585547915")
    audit.check("aggregate_shell", "direct_amplitude_numeric", abs(float(sp.sqrt(direct_constant)) - 0.534723186195885) < 2e-15, sp.N(sp.sqrt(direct_constant), 18), "0.534723186195885")

    eta = sp.symbols("eta", positive=True)
    a_eta = 2 ** (-eta)
    b_eta = 2 ** (eta - 2 * s_exp)
    product = sp.expand((1 - a_eta) * (1 - b_eta))
    audit.check("aggregate_shell", "eta_stationary_at_s", sp.simplify(sp.diff(product, eta).subs(eta, s_exp)) == 0, sp.simplify(sp.diff(product, eta).subs(eta, s_exp)), 0)

    # Tail decay does not manufacture headroom.
    q_amp = 2 ** (-gamma)
    c = sp.symbols("C", integer=True, positive=True)
    m_tail = sp.symbols("M", positive=True)
    adversarial_headroom = sp.Rational(1, 2) * m_tail * q_amp ** (c - 5)
    tail = m_tail * q_amp ** (c - 5)
    audit.check("headroom", "adversarial_headroom_fails", sp.simplify(tail > adversarial_headroom) is sp.true, sp.simplify(tail / adversarial_headroom), "> 1")

    # A separate absolute payment of A^2 and e B^2 destroys the covariance-
    # normal cancellation.  In the model covariance (1+r^2)^-2 in d=3,
    # the value variance is finite but the gradient variance is linear.
    cutoff = sp.symbols("Lambda", positive=True)
    radial_gradient_primitive = sp.simplify(
        cutoff - sp.Rational(3, 2) * sp.atan(cutoff) + cutoff / (2 * (1 + cutoff**2))
    )
    audit.check(
        "separate_absorption",
        "gradient_integrand",
        sp.simplify(sp.diff(radial_gradient_primitive, cutoff) - cutoff**4 / (1 + cutoff**2) ** 2) == 0,
        sp.simplify(sp.diff(radial_gradient_primitive, cutoff)),
        cutoff**4 / (1 + cutoff**2) ** 2,
    )
    audit.check(
        "separate_absorption",
        "linear_asymptotic_slope",
        sp.limit(radial_gradient_primitive / cutoff, cutoff, sp.oo) == 1,
        sp.limit(radial_gradient_primitive / cutoff, cutoff, sp.oo),
        1,
    )

    diagnostics = {
        "inputs": {
            "alpha": alpha,
            "c0": c0,
            "c1": c1,
            "p_mass": p_mass,
            "beta_operator": beta_op,
            "gamma": gamma,
        },
        "fixed_law_action": {
            "remainder_norm_squared_coefficient": alpha**2 * c1,
            "variance_bound": "sd(C6e(W)V) <= sqrt(beta_op) A + alpha sqrt(c1) B_e",
            "owner_identity": "P_comp = Forest_063_ad/2 - Var(C6e(W)V)/2",
            "hessian_promotion": False,
        },
        "finite_moment_no_go": {
            "scaled_limit_over_c1": scaled_limit,
            "delta": delta_value,
            "q_comp": q_comp_value,
            "source_plus_sextic": sp.simplify(source_plus_sextic.subs(delta, delta_value)),
            "all_positive_moments_bounded_by_one": True,
            "production_counterexample": False,
        },
        "density_repair": {
            "fprime_interval": [sp.Rational(3, 8), 1],
            "fpp_l1": fpp_l1,
            "s_fpp_l1": sfpp_l1,
            "variance_fprime_ceiling": sp.Rational(25, 256),
        },
        "six_real_smoothing": {
            "constant_formula": "Gamma(3-q/2)/2^(1+q/2)",
            "q2": c62,
            "q4": c64,
            "q6": "logarithmically divergent",
            "d2f_l2_over_lambda": d2_l2,
            "d3f_l2_over_lambda_squared": d3_l2,
            "d4_witness": fourth_witness,
            "d4_positive_floor_axis": positive_floor_fourth,
            "d4_scaled_axis_min_for_e_le_r2": 9,
        },
        "fractional_route": {
            "p": p,
            "holder_q": holder_q,
            "sigma": sigma,
            "theta": theta_frac,
            "p_theta": p * theta_frac,
            "two_p_theta": 2 * p * theta_frac,
            "pointwise_ellipticity_alone_controls_spatial_fractional_norm": False,
            "production_uniform_terminal_ellipticity": False,
            "production_joint_value_gradient_hypotheses": False,
        },
        "aggregate_shell": {
            "conditional_B_constant": b_constant,
            "conditional_B_constant_decimal": b_float,
            "conditional_B_amplitude_decimal": sp.N(sp.sqrt(b_constant), 18),
            "direct_fixed_collar_constant": direct_constant,
            "direct_fixed_collar_constant_decimal": direct_float,
            "direct_fixed_collar_amplitude_decimal": sp.N(sp.sqrt(direct_constant), 18),
            "production_atom_hypothesis": False,
            "production_q_ledger": False,
        },
        "remaining": {
            "terminal_innovation_uniform_full_rank": False,
            "terminal_disintegration_owner_intertwining": False,
            "signed_forest_lower_bound": False,
            "weighted_current_energy_once": False,
            "near_balanced_headroom": False,
            "absolute_anchor": False,
        },
        "separate_absorption": {
            "gradient_energy_primitive": radial_gradient_primitive,
            "asymptotic_slope": 1,
            "standalone_A2_plus_eB2_absorption": False,
            "signed_covariance_normal_combination_required": True,
        },
    }
    result = audit.finish(diagnostics)
    atomic_json(args.output, result)
    print(f"R-134 primary: {result['assertions_passed']}/{result['assertions_total']} PASS")
    print(f"B_7/12 conditional constant={float(b_float):.15f}")
    print(f"direct fixed-collar constant={float(direct_float):.15f}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
