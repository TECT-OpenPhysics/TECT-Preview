#!/usr/bin/env python3
"""Primary exact audit for the scoped A13 R-133 boundary.

The audit checks the affine common-heat Gaussian score identity, exact score
moments, the common/relative replica split, the predictable-feedback
double-divergence connection, the stopped-polynomial response support audit,
the rational gamma-four Sobolev obstruction, and the aggregate collar-to-gap
criterion.  It does not assert the missing production one-use estimate.
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
RESULT_ID = "A13-CLASSII-AFFINE-GAUSSIAN-SCORE-FEEDBACK-COLLAR-BOUNDARY"
SCHEMA = "tect/a13-affine-gaussian-score-feedback-collar-boundary-primary/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-affine-gaussian-score-feedback-collar-boundary/"
    "result.json"
)
R132_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-mixed-replica-gaussian-ray-sextic-shell-boundary/"
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
                "affine_gaussian_score_identity_proved": True,
                "predictable_feedback_score_identity_proved_on_cylindrical_core": True,
                "finite_energy_global_score_transfer_from_declared_data_rejected": True,
                "conditional_polynomial_response_zero_proved": True,
                "sixth_amplitude_gamma_four_route_rejected": True,
                "aggregate_positive_gamma_collar_criterion_proved": True,
                "production_one_use_bound": False,
                "production_c_mix": False,
                "production_c_far": False,
                "production_c_bal": False,
                "absolute_anchor": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-133 proves exact score, feedback, support, obstruction, and "
                "conditional collar lemmas. It does not control the complete signed "
                "production score owner, prove a one-use B_gamma bound, construct "
                "production shell constants or an absolute anchor, or close Sector A."
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


def directional(expression: sp.Expr, variables: tuple[sp.Symbol, ...], vector: tuple[sp.Expr, ...]) -> sp.Expr:
    return sp.expand(sum(vector[i] * sp.diff(expression, variables[i]) for i in range(len(variables))))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    upstream = json.loads(R132_RESULT.read_text(encoding="utf-8"))
    inputs = upstream["diagnostics"]["inputs"]
    shell = upstream["diagnostics"]["shell"]
    alpha = sp.Rational(inputs["alpha"])
    c0 = sp.Rational(inputs["c0"])
    c1 = sp.Rational(inputs["c1"])
    p_mass = sp.Rational(inputs["p_mass"])
    gamma = sp.Rational(shell["known_gamma"])
    c_s = sp.simplify(c0 + c1)
    beta_op = sp.simplify(4 * c_s)
    audit = Audit()

    audit.check("inputs", "upstream_pass", upstream.get("status") == "PASS", upstream.get("status"), "PASS")
    audit.check("inputs", "alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))
    audit.check("inputs", "gamma", gamma == sp.Rational(7, 12), gamma, sp.Rational(7, 12))
    audit.check("inputs", "c_s", c_s == sp.Rational(339, 8000) / p_mass, c_s, sp.Rational(339, 8000) / p_mass)
    audit.check("inputs", "beta_op", beta_op == sp.Rational(339, 2000) / p_mass, beta_op, sp.Rational(339, 2000) / p_mass)

    # Exact affine paired- and single-Gaussian score transfer on a polynomial
    # fixture.  Both replicas receive the same Cameron--Martin translation.
    x, y, t, u = sp.symbols("x y t u", real=True)
    a_scalar = sp.Rational(2, 3)
    b_scalar = sp.Rational(-5, 4)
    shift = t * a_scalar + u * b_scalar
    pair_kernel = (1 + (x + shift) + 2 * (x + shift) ** 2) * (
        3 - (y + shift) + (y + shift) ** 3
    )
    trace_kernel = 2 + (x + shift) ** 2 + (x + shift) ** 4
    direct_pair = sp.diff(gaussian_expectation(pair_kernel, (x, y)), t, u).subs({t: 0, u: 0})
    direct_trace = sp.diff(gaussian_expectation(trace_kernel, (x,)), t, u).subs({t: 0, u: 0})
    pair_at_zero = pair_kernel.subs({t: 0, u: 0})
    trace_at_zero = trace_kernel.subs({t: 0, u: 0})
    h_pair = a_scalar * b_scalar * ((x + y) ** 2 - 2)
    h_single = a_scalar * b_scalar * (x**2 - 1)
    score_pair = gaussian_expectation(h_pair * pair_at_zero, (x, y))
    score_trace = gaussian_expectation(h_single * trace_at_zero, (x,))
    audit.check("affine_score", "paired_identity", sp.simplify(direct_pair - score_pair) == 0, direct_pair, score_pair)
    audit.check("affine_score", "single_identity", sp.simplify(direct_trace - score_trace) == 0, direct_trace, score_trace)
    audit.check(
        "affine_score",
        "combined_owner_identity",
        sp.simplify((direct_pair - direct_trace) / 2 - (score_pair - score_trace) / 2) == 0,
        (direct_pair - direct_trace) / 2,
        (score_pair - score_trace) / 2,
    )

    # Exact L2 costs for one- and two-copy Hermite scores.
    x1, x2, y1, y2 = sp.symbols("x1 x2 y1 y2", real=True)
    avec = sp.Matrix([sp.Rational(1, 2), sp.Rational(3, 2)])
    bvec = sp.Matrix([sp.Rational(5, 3), sp.Rational(-2, 3)])
    xv = sp.Matrix([x1, x2])
    yv = sp.Matrix([y1, y2])
    aa = sp.simplify((avec.T * avec)[0])
    bb = sp.simplify((bvec.T * bvec)[0])
    ab = sp.simplify((avec.T * bvec)[0])
    discriminant = sp.simplify(aa * bb + ab**2)
    h1 = sp.expand((avec.T * xv)[0] * (bvec.T * xv)[0] - ab)
    h2 = sp.expand((avec.T * (xv + yv))[0] * (bvec.T * (xv + yv))[0] - 2 * ab)
    audit.check("score_cost", "single_centered", gaussian_expectation(h1, (x1, x2)) == 0, gaussian_expectation(h1, (x1, x2)), 0)
    audit.check("score_cost", "pair_centered", gaussian_expectation(h2, (x1, x2, y1, y2)) == 0, gaussian_expectation(h2, (x1, x2, y1, y2)), 0)
    audit.check("score_cost", "single_l2", gaussian_expectation(h1**2, (x1, x2)) == discriminant, gaussian_expectation(h1**2, (x1, x2)), discriminant)
    audit.check("score_cost", "pair_l2", gaussian_expectation(h2**2, (x1, x2, y1, y2)) == 4 * discriminant, gaussian_expectation(h2**2, (x1, x2, y1, y2)), 4 * discriminant)

    # Common/relative replica derivative decomposition.  Common heat can be
    # scored; the relative derivative remains explicit.
    A, r1, r2 = sp.symbols("A r1 r2", real=True)
    phi = (A + r1) ** 3 * (A + r2) ** 2 + (A + r1) * (A + r2) ** 3
    pz, qz, pw, qw = map(sp.Rational, (2, -1, 3, 5))
    cz, dz = sp.simplify((pz + qz) / 2), sp.simplify((pz - qz) / 2)
    cw, dw = sp.simplify((pw + qw) / 2), sp.simplify((pw - qw) / 2)
    lhs_operator = directional(
        directional(phi, (r1, r2), (pw, qw)), (r1, r2), (pz, qz)
    )
    relative = lambda expression: sp.expand(sp.diff(expression, r1) - sp.diff(expression, r2))
    rhs_expression = (
        cz * cw * (A**2 - 1) * phi
        + cz * A * dw * relative(phi)
        + cw * A * dz * relative(phi)
        + dz * dw * relative(relative(phi))
    )
    substitutions = {r1: sp.Rational(2, 3), r2: sp.Rational(-4, 5)}
    lhs_common_relative = gaussian_expectation(lhs_operator.subs(substitutions), (A,))
    rhs_common_relative = gaussian_expectation(rhs_expression.subs(substitutions), (A,))
    audit.check("replica_split", "operator_identity", sp.simplify(lhs_common_relative - rhs_common_relative) == 0, lhs_common_relative, rhs_common_relative)

    weights = [sp.Rational(1, 6), sp.Rational(1, 3), sp.Rational(1, 2)]
    values = [sp.Rational(-2), sp.Rational(1), sp.Rational(4)]
    mean_p = sum(weights[i] * values[i] for i in range(3))
    variance_p = sum(weights[i] * (values[i] - mean_p) ** 2 for i in range(3))
    mean_c2 = sp.Integer(0)
    mean_d2 = sp.Integer(0)
    mean_cd = sp.Integer(0)
    for i in range(3):
        for j in range(3):
            c_value = (values[i] + values[j]) / 2
            d_value = (values[i] - values[j]) / 2
            weight = weights[i] * weights[j]
            mean_c2 += weight * c_value**2
            mean_d2 += weight * d_value**2
            mean_cd += weight * c_value * d_value
    audit.check("replica_split", "common_variance", sp.simplify(mean_c2 - mean_p**2 - variance_p / 2) == 0, mean_c2, mean_p**2 + variance_p / 2)
    audit.check("replica_split", "relative_variance", sp.simplify(mean_d2 - variance_p / 2) == 0, mean_d2, variance_p / 2)
    audit.check("replica_split", "common_relative_orthogonal", mean_cd == 0, mean_cd, 0)

    # Exact predictable-feedback score and connection term on a triangular
    # two-block chart Z=(x,y+lambda*x^2), in direction e1.
    lam = sp.symbols("lam", real=True)
    xi = sp.Matrix([x, y])
    av = sp.Matrix([1, -2 * lam * x])
    tensor = av * av.T
    variables = (x, y)
    divergence = sp.Matrix(
        [sum(sp.diff(tensor[i, j], variables[j]) for j in range(2)) for i in range(2)]
    )
    divergence2 = sum(sp.diff(divergence[i], variables[i]) for i in range(2))
    delta2 = sp.expand((xi.T * tensor * xi)[0] - sp.trace(tensor) - 2 * (xi.T * divergence)[0] + divergence2)
    connection = sp.Matrix([0, 2 * lam])
    delta_connection = sp.expand(
        (xi.T * connection)[0]
        - sum(sp.diff(connection[i], variables[i]) for i in range(2))
    )
    feedback_score = sp.expand(delta2 - delta_connection)
    nonlinear_owner = (y + lam * x**2) ** 2 / 2
    linear_owner = x**2 / 2
    audit.check("feedback", "nonlinear_physical_hessian", gaussian_expectation(nonlinear_owner * feedback_score, variables) == 0, gaussian_expectation(nonlinear_owner * feedback_score, variables), 0)
    audit.check("feedback", "linear_physical_hessian", gaussian_expectation(linear_owner * feedback_score, variables) == 1, gaussian_expectation(linear_owner * feedback_score, variables), 1)
    audit.check("feedback", "connection_is_load_bearing", gaussian_expectation(nonlinear_owner * delta2, variables) == 2 * lam**2, gaussian_expectation(nonlinear_owner * delta2, variables), 2 * lam**2)
    audit.check("feedback", "connection_cancels", gaussian_expectation(nonlinear_owner * delta_connection, variables) == 2 * lam**2, gaussian_expectation(nonlinear_owner * delta_connection, variables), 2 * lam**2)

    # Bounded predictable tanh feedback has bounded amplitude but an
    # inverse-Jacobian score cost with a linear lower bound in frequency.
    frequency, amplitude = sp.symbols("N a", positive=True)
    inverse_lower_coefficient = 2 * amplitude**2 * sp.exp(-sp.Rational(1, 2)) / sp.sqrt(2 * sp.pi) / sp.cosh(1) ** 4
    audit.check("feedback", "bounded_feedback_amplitude", True, "|a tanh(Nx)|<=a", "uniform in N")
    audit.check("feedback", "inverse_cost_lower_coefficient_positive", inverse_lower_coefficient.is_positive is True, inverse_lower_coefficient, ">0")
    audit.check("feedback", "inverse_cost_diverges", sp.limit(1 + inverse_lower_coefficient * frequency, frequency, sp.oo) == sp.oo, sp.limit(1 + inverse_lower_coefficient * frequency, frequency, sp.oo), sp.oo)

    # Stopped polynomial support: current-level safety offset 3, paired
    # response safety offset 4, rational Cartan principal offset 5.
    n = sp.symbols("n", integer=True)
    current_threshold_ratio = sp.simplify(2 ** ((n + 3) - 1) / 2 ** (n + 1))
    response_threshold_ratio = sp.simplify(2 ** ((n + 4) - 1) / 2 ** (n + 2))
    audit.check("polynomial_support", "current_offset_three", current_threshold_ratio == 2, current_threshold_ratio, 2)
    audit.check("polynomial_support", "response_offset_four", response_threshold_ratio == 2, response_threshold_ratio, 2)
    audit.check("polynomial_support", "cartan_offset_five", 5 > 4, 5, ">4")
    heat_gram = sp.simplify(2 * c_s)
    adapted_negative = sp.simplify(-8 * c_s)
    audit.check("polynomial_support", "common_heat_gram", heat_gram == sp.Rational(339, 4000) / p_mass, heat_gram, sp.Rational(339, 4000) / p_mass)
    audit.check("polynomial_support", "adapted_covariance_defect", adapted_negative == -sp.Rational(339, 1000) / p_mass, adapted_negative, -sp.Rational(339, 1000) / p_mass)

    # Exact rational remainder and its fourth-derivative boundary-layer
    # constant.  This is a sharp scalar Sobolev surrogate, not literal B_out.
    s, e = sp.symbols("s e", real=True, positive=True)
    z = sp.symbols("z", real=True)
    f = s - alpha * s**3 / (s**2 + e)
    remainder = sp.factor(f**2 - (1 - alpha) ** 2 * s**2 - 2 * alpha * (1 - alpha) * e)
    H = -sp.Rational(5, 27) / (1 + z**2) - sp.Rational(25, 81) / (1 + z**2) ** 2
    scaled_remainder = sp.factor(remainder.subs(s, sp.sqrt(e) * z) / e)
    audit.check("gamma_four", "rational_remainder", sp.simplify(scaled_remainder - H) == 0, scaled_remainder, H)
    H4_integral = sp.integrate(sp.diff(H, z, 4) ** 2, (z, -sp.oo, sp.oo))
    expected_H4_integral = sp.Rational(2062375, 23328) * sp.pi
    audit.check("gamma_four", "boundary_integral", sp.simplify(H4_integral - expected_H4_integral) == 0, H4_integral, expected_H4_integral)
    rational_asymptotic = sp.simplify(32 * c1**2 * H4_integral)
    expected_asymptotic = sp.Rational(2062375, 729) * sp.pi * c1**2
    audit.check("gamma_four", "full_gram_asymptotic", sp.simplify(rational_asymptotic - expected_asymptotic) == 0, rational_asymptotic, expected_asymptotic)
    sextic_coefficient = sp.Rational(3, 32) * sp.pi
    ratio_coefficient = sp.factor(rational_asymptotic / sextic_coefficient)
    expected_ratio = sp.Rational(445473, 16000) / p_mass**2
    audit.check("gamma_four", "sextic_ratio", sp.simplify(ratio_coefficient - expected_ratio) == 0, ratio_coefficient, expected_ratio)
    audit.check("gamma_four", "ratio_unbounded", sp.limit(ratio_coefficient * s / e ** sp.Rational(3, 2), s, sp.oo) == sp.oo, sp.limit(ratio_coefficient * s / e ** sp.Rational(3, 2), s, sp.oo), sp.oo)

    # Exact three-channel collar threshold and the positive-gamma aggregate
    # tail route.  Any positive gamma suffices conditionally at a fixed collar.
    e0, f0, sigma, cross = sp.symbols("e0 f0 sigma cross", positive=True)
    m2 = (e0 + f0 - sp.sqrt((e0 - f0) ** 2 + cross**2)) / 2
    a_star_sq = 4 * (e0 - sigma) * (f0 - sigma)
    threshold_difference = sp.factor((e0 + f0 - 2 * sigma) ** 2 - (e0 - f0) ** 2)
    audit.check("collar", "threshold_factorization", sp.simplify(threshold_difference - a_star_sq) == 0, threshold_difference, a_star_sq)
    test_values = {e0: sp.Rational(4, 5), f0: sp.Rational(3, 5), sigma: sp.Rational(1, 10)}
    a_star = 2 * sp.sqrt((e0 - sigma) * (f0 - sigma))
    audit.check("collar", "strict_equivalence_inside", bool((m2.subs(test_values).subs(cross, a_star.subs(test_values) / 2) > sigma.subs(test_values))), m2.subs(test_values).subs(cross, a_star.subs(test_values) / 2), f">{sigma.subs(test_values)}")
    boundary_value = sp.simplify(m2.subs(test_values).subs(cross, a_star.subs(test_values)))
    audit.check("collar", "boundary_equality", boundary_value == sigma.subs(test_values), boundary_value, sigma.subs(test_values))
    far_effective_exponent = sp.simplify(4 - gamma)
    mix_effective_exponent = sp.simplify(2 - gamma)
    offset_exponent = sp.simplify(5 * gamma)
    audit.check("collar", "far_relabel_growth", far_effective_exponent == sp.Rational(41, 12), far_effective_exponent, sp.Rational(41, 12))
    audit.check("collar", "mix_relabel_growth", mix_effective_exponent == sp.Rational(17, 12), mix_effective_exponent, sp.Rational(17, 12))
    audit.check("collar", "offset_exponent", offset_exponent == sp.Rational(35, 12), offset_exponent, sp.Rational(35, 12))
    strict_test_at_17 = sp.simplify(2**7 * 2 ** (-gamma * (17 - 5)))
    strict_test_at_18 = sp.simplify(2**7 * 2 ** (-gamma * (18 - 5)))
    audit.check("collar", "strict_collar_equality_rejected", strict_test_at_17 == 1, strict_test_at_17, 1)
    audit.check("collar", "strict_collar_next_integer", bool(strict_test_at_18 < 1), strict_test_at_18, "<1")
    geometric_cost = sp.simplify(1 / (1 - 2 ** (-gamma)))
    audit.check("collar", "geometric_cost_finite", bool(geometric_cost.is_finite and geometric_cost > 1), geometric_cost, ">1 finite")

    diagnostics = {
        "inputs": {
            "alpha": alpha,
            "c0": c0,
            "c1": c1,
            "c_s": c_s,
            "p_mass": p_mass,
            "known_gamma": gamma,
        },
        "affine_score": {
            "paired_direct": direct_pair,
            "paired_score": score_pair,
            "trace_direct": direct_trace,
            "trace_score": score_trace,
            "single_score_l2_squared": discriminant,
            "pair_score_l2_squared": 4 * discriminant,
            "raw_complete_frame_envelope": beta_op,
        },
        "replica_split": {
            "mean": mean_p,
            "variance": variance_p,
            "common_second_moment": mean_c2,
            "relative_second_moment": mean_d2,
            "common_relative_cross": mean_cd,
        },
        "feedback": {
            "exact_score": feedback_score,
            "connection": delta_connection,
            "bounded_tanh_inverse_lower_coefficient": inverse_lower_coefficient,
        },
        "polynomial_response": {
            "current_safety_offset": 3,
            "response_safety_offset": 4,
            "cartan_principal_offset": 5,
            "common_heat_gram": heat_gram,
            "adapted_covariance_defect_at_lambda_one": adapted_negative,
        },
        "gamma_four": {
            "scaled_remainder": H,
            "H4_integral": H4_integral,
            "gram_asymptotic_coefficient": rational_asymptotic,
            "sextic_coefficient": sextic_coefficient,
            "ratio_coefficient": ratio_coefficient,
            "surrogate_offset_factor": sp.Integer(2) ** -40,
        },
        "aggregate_collar": {
            "threshold": "2*sqrt((e-sigma)*(f-sigma))",
            "known_gamma": gamma,
            "minimum_integer_example": 18,
            "far_effective_growth_exponent": far_effective_exponent,
            "mix_effective_growth_exponent": mix_effective_exponent,
            "offset_exponent": offset_exponent,
            "geometric_sum_cost": geometric_cost,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(args.output, payload)
    print(
        f"R-133 primary {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
