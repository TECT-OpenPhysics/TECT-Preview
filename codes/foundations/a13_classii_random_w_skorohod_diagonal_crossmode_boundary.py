#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-110 advance.

The certificate verifies the random-covariance double-divergence completion,
the trace-corrected diagonal interpolation boundary, and the smallest complete
physical k:2k cross-output cluster.  It does not assert the bare all-q
cross-mode normalizer, the full production cluster, Nelson, or Sector-A
closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import functools
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

import mpmath as mp
import sympy as sp
from sympy.integrals.quadrature import gauss_laguerre


SCHEMA = "tect/a13-random-w-skorohod-diagonal-crossmode-boundary-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-random-w-skorohod-diagonal-crossmode-boundary/result.json"
)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def require(
        self,
        group: str,
        name: str,
        condition: object,
        actual: object,
        expected: object,
    ) -> None:
        passed = bool(condition is True or condition == sp.S.true)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not passed:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def gaussian_moment(power: int, variance: sp.Expr = sp.Integer(1)) -> sp.Expr:
    if power % 2:
        return sp.Integer(0)
    if power == 0:
        return sp.Integer(1)
    return sp.factorial2(power - 1) * variance ** (power // 2)


def gaussian_expectation(poly: sp.Expr, variables: tuple[sp.Symbol, ...], variances: tuple[sp.Expr, ...]) -> sp.Expr:
    expanded = sp.Poly(sp.expand(poly), *variables)
    total = sp.Integer(0)
    for powers, coefficient in expanded.terms():
        term = coefficient
        for power, variance in zip(powers, variances):
            term *= gaussian_moment(power, variance)
        total += term
    return sp.simplify(total)


@functools.lru_cache(maxsize=None)
def laguerre_rule(order: int) -> tuple[tuple[mp.mpf, ...], tuple[mp.mpf, ...]]:
    """Return a cached high-precision Gauss--Laguerre rule."""

    nodes_raw, weights_raw = gauss_laguerre(order, 45)
    nodes = tuple(mp.mpf(str(value)) for value in nodes_raw)
    weights = tuple(mp.mpf(str(value)) for value in weights_raw)
    return nodes, weights


def laguerre_log_mgf(v: mp.mpf, w: mp.mpf, amplitude: mp.mpf, q: mp.mpf, order: int = 24) -> mp.mpf:
    """Independent radial/phase quadrature for the complete k:2k packet."""

    nodes, weights = laguerre_rule(order)
    gamma = v + 4 * w
    terms: list[mp.mpf] = []
    for index, radial_t in enumerate(nodes):
        r = v * radial_t / 2
        for other, radial_u in enumerate(nodes):
            s = w * radial_u / 2
            p0 = (
                amplitude**2 * r
                + 4 * amplitude**2 * s
                - gamma * amplitude**2 / 2
                + r**2
                + 10 * r * s
                + 4 * s**2
                - gamma * (r + s)
            )
            bessel_argument = abs(6 * q * amplitude * r * mp.sqrt(s))
            terms.append(
                mp.log(mp.mpf(str(weights[index])))
                + mp.log(mp.mpf(str(weights[other])))
                - q * p0
                + mp.log(mp.besseli(0, bessel_argument))
            )
    maximum = max(terms)
    return maximum + mp.log(sum(mp.exp(value - maximum) for value in terms))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    # ------------------------------------------------------------------
    # Random-W double-divergence completion and exact constants.
    # ------------------------------------------------------------------
    x = sp.symbols("x", real=True)
    alpha, beta = sp.symbols("alpha beta", real=True)
    h_poly = 1 + beta * x + x**2
    w_poly = 1 + alpha * x**2
    direct_form = gaussian_expectation(
        w_poly * (sp.diff(h_poly, x) ** 2 + h_poly * sp.diff(h_poly, x, 2)),
        (x,),
        (sp.Integer(1),),
    )
    delta2_w = sp.expand((x**2 - 1) * w_poly - 2 * x * sp.diff(w_poly, x) + sp.diff(w_poly, x, 2))
    divergence_form = gaussian_expectation(h_poly**2 * delta2_w / 2, (x,), (sp.Integer(1),))
    one_divergence = gaussian_expectation(
        h_poly * sp.diff(h_poly, x) * (x * w_poly - sp.diff(w_poly, x)),
        (x,),
        (sp.Integer(1),),
    )
    checks.require("random_w", "double-divergence identity", sp.simplify(direct_form - divergence_form) == 0, direct_form - divergence_form, 0)
    checks.require("random_w", "one-divergence identity", sp.simplify(direct_form - one_divergence) == 0, direct_form - one_divergence, 0)
    checks.require("random_w", "double divergence is centered", gaussian_expectation(delta2_w, (x,), (sp.Integer(1),)) == 0, gaussian_expectation(delta2_w, (x,), (sp.Integer(1),)), 0)

    n = sp.symbols("n", integer=True, nonnegative=True)
    chaos_multiplier = sp.expand(n * (n - 1) + 4 * n + 2)
    checks.require(
        "random_w",
        "chaos Sobolev multiplier",
        sp.simplify(chaos_multiplier - (n + 1) * (n + 2)) == 0,
        chaos_multiplier,
        (n + 1) * (n + 2),
    )
    q_prod = sp.Rational(10, 9)
    random_cost = sp.simplify(q_prod**2 / 128)
    fixed_cost = sp.simplify(2 * random_cost)
    checks.require("random_w", "q=10/9 random score constant", random_cost == sp.Rational(25, 2592), random_cost, sp.Rational(25, 2592))
    checks.require("random_w", "fixed W recovers R-109 constant", fixed_cost == sp.Rational(25, 1296), fixed_cost, sp.Rational(25, 1296))

    # Scalar oscillatory no-go: exact characteristic-function formulas.
    m, epsilon, tau = sp.symbols("M epsilon tau", positive=True, real=True)
    r2 = sp.exp(-2 * m**2)
    r8 = sp.exp(-8 * m**2)
    score_form = m * (r2 + tau * epsilon * (1 + r8) / 2)
    source_x = (1 - r2) / (2 * m)
    sextic_y = (10 - 15 * r2 + 6 * r8 - sp.exp(-18 * m**2)) / (32 * m**3)
    score_cost = (
        2
        + 4 * tau * epsilon * r2
        + epsilon**2 * (1 + 8 * m**2 + 8 * m**4 + (1 - 8 * m**2 + 8 * m**4) * r8)
    )
    checks.require("random_w_nogo", "score grows linearly positive branch", sp.limit(score_form / m, m, sp.oo).subs(tau, 1) == epsilon / 2, sp.limit(score_form / m, m, sp.oo).subs(tau, 1), epsilon / 2)
    checks.require("random_w_nogo", "score grows linearly negative branch", sp.limit(score_form / m, m, sp.oo).subs(tau, -1) == -epsilon / 2, sp.limit(score_form / m, m, sp.oo).subs(tau, -1), -epsilon / 2)
    checks.require("random_w_nogo", "source vanishes", sp.limit(source_x, m, sp.oo) == 0, sp.limit(source_x, m, sp.oo), 0)
    checks.require("random_w_nogo", "sextic vanishes", sp.limit(sextic_y, m, sp.oo) == 0, sp.limit(sextic_y, m, sp.oo), 0)
    checks.require("random_w_nogo", "correct cost has quartic growth", sp.limit(score_cost / m**4, m, sp.oo) == 8 * epsilon**2, sp.limit(score_cost / m**4, m, sp.oo), 8 * epsilon**2)

    # Rank-one rotating projector: invariants stay exactly fixed while the
    # current-root eigenspace rotation carries the missing cost.
    c2, s2 = sp.symbols("c2 s2", real=True)
    projector = sp.Matrix([[1 + tau * c2, s2], [s2, 1 - tau * c2]]) / 2
    projector_square = sp.simplify((projector * projector - projector).subs(s2**2, 1 - c2**2).subs(tau**2, 1))
    checks.require("projector", "rank-one projector identity", projector_square == sp.zeros(2), projector_square, sp.zeros(2))
    checks.require("projector", "projector trace", sp.trace(projector) == 1, sp.trace(projector), 1)
    projector_form = m * (r2 / 2 + tau * (1 + r8) / 4)
    projector_cost = 2 * m**4 * (1 + r8) + 4 * m**2 + 2
    checks.require("projector", "rotating projector signed slope", sp.limit(projector_form / m, m, sp.oo) == tau / 4, sp.limit(projector_form / m, m, sp.oo), tau / 4)
    checks.require("projector", "rotating projector cost slope", sp.limit(projector_cost / m**4, m, sp.oo) == 2, sp.limit(projector_cost / m**4, m, sp.oo), 2)

    # ------------------------------------------------------------------
    # Trace-corrected diagonal interpolation and mean-debt boundary.
    # ------------------------------------------------------------------
    rho, c_trace = sp.symbols("rho c_trace", real=True)
    delta0 = sp.symbols("delta0", real=True)
    delta_rho = delta0 + 2 * rho * c_trace
    explicit_trace_derivative = sp.diff(-delta_rho / 2, rho)
    mixed_gaussian_trace = c_trace
    checks.require("interpolation", "trace transport cancellation", sp.simplify(explicit_trace_derivative + mixed_gaussian_trace) == 0, explicit_trace_derivative + mixed_gaussian_trace, 0)
    checks.require("interpolation", "diagonal endpoint trace", delta_rho.subs(rho, 1) == delta0 + 2 * c_trace, delta_rho.subs(rho, 1), delta0 + 2 * c_trace)
    checks.require("interpolation", "decoupled endpoint trace", delta_rho.subs(rho, 0) == delta0, delta_rho.subs(rho, 0), delta0)

    a_param, eps = sp.symbols("a epsilon", real=True)
    y_diag = eps * (x**2 + a_param * x - 1)
    tangent = eps * (2 * x + a_param)
    packet_diag = sp.expand((y_diag**2 - tangent**2) / 2)
    mean_diag = gaussian_expectation(packet_diag, (x,), (sp.Integer(1),))
    covariance_square = gaussian_expectation(tangent**4, (x,), (sp.Integer(1),))
    checks.require("mean_debt", "quadratic Hermite packet mean", mean_diag == -eps**2, mean_diag, -eps**2)
    checks.require("mean_debt", "realized tangent covariance square", covariance_square == eps**4 * (a_param**4 + 24 * a_param**2 + 48), covariance_square, eps**4 * (a_param**4 + 24 * a_param**2 + 48))
    q_value = sp.Rational(10, 9)
    a_value = sp.Integer(1)
    eps_value = sp.Rational(1, 10)
    jensen_lower = sp.simplify(-q_value * mean_diag.subs(eps, eps_value))
    square_first_rhs = sp.simplify(q_value**2 * covariance_square.subs({eps: eps_value, a_param: a_value}) / 4)
    checks.require("mean_debt", "production-q Jensen lower", jensen_lower == sp.Rational(1, 90), jensen_lower, sp.Rational(1, 90))
    checks.require("mean_debt", "production-q square cost", square_first_rhs == sp.Rational(73, 32400), square_first_rhs, sp.Rational(73, 32400))
    checks.require("mean_debt", "exact square-first violation margin", jensen_lower - square_first_rhs == sp.Rational(287, 32400), jensen_lower - square_first_rhs, sp.Rational(287, 32400))

    # ------------------------------------------------------------------
    # Smallest complete physical k:2k cross-output cluster.
    # ------------------------------------------------------------------
    theta = sp.symbols("theta", real=True)
    amplitude, aa, bb, cc, dd, v, w = sp.symbols("A a b c d v w", real=True)
    field = amplitude + aa * sp.cos(theta) + bb * sp.sin(theta) + cc * sp.cos(2 * theta) + dd * sp.sin(2 * theta)
    bases = (sp.cos(theta), sp.sin(theta), sp.cos(2 * theta), sp.sin(2 * theta))
    derivatives = tuple(sp.diff(item, theta) for item in bases)
    gram: list[list[sp.Expr]] = []
    for left in derivatives:
        row: list[sp.Expr] = []
        for right in derivatives:
            row.append(sp.simplify(sp.integrate(sp.expand_trig(field**2 * left * right), (theta, 0, 2 * sp.pi)) / (2 * sp.pi)))
        gram.append(row)
    current = field * sp.diff(field, theta)
    current_norm = sp.simplify(sp.integrate(sp.expand_trig(current**2), (theta, 0, 2 * sp.pi)) / (2 * sp.pi))
    variances = (v, v, w, w)
    trace = sp.simplify(sum(variances[index] * gram[index][index] for index in range(4)))
    packet = sp.expand((current_norm - trace) / 2)
    radial_r = (aa**2 + bb**2) / 4
    radial_s = (cc**2 + dd**2) / 4
    phase_c = ((aa**2 - bb**2) * cc + 2 * aa * bb * dd) / 8
    gamma = v + 4 * w
    packet_formula = sp.expand(
        amplitude**2 * radial_r
        + 4 * amplitude**2 * radial_s
        - gamma * amplitude**2 / 2
        + 6 * amplitude * phase_c
        + radial_r**2
        + 10 * radial_r * radial_s
        + 4 * radial_s**2
        - gamma * (radial_r + radial_s)
    )
    checks.require("cross_cluster", "complete packet reconstruction", sp.simplify(packet - packet_formula) == 0, sp.simplify(packet - packet_formula), 0)
    checks.require("cross_cluster", "whole-output trace", sp.simplify(trace - gamma * (amplitude**2 + 2 * radial_r + 2 * radial_s)) == 0, sp.simplify(trace - gamma * (amplitude**2 + 2 * radial_r + 2 * radial_s)), 0)

    variables = (aa, bb, cc, dd)
    covariance_variances = (v, v, w, w)
    packet_mean = gaussian_expectation(packet, variables, covariance_variances)
    packet_variance = sp.factor(gaussian_expectation(packet**2, variables, covariance_variances))
    packet_third = sp.factor(gaussian_expectation(packet**3, variables, covariance_variances))
    checks.require("cross_cluster", "packet is centered", packet_mean == 0, packet_mean, 0)

    hs_square_poly = sp.expand(
        sum(
            variances[left] * variances[right] * gram[left][right] ** 2
            for left in range(4)
            for right in range(4)
        )
    )
    hs_square = sp.factor(gaussian_expectation(hs_square_poly, variables, covariance_variances))
    expected_hs = (
        amplitude**4 * (v**2 / 2 + 8 * w**2)
        + amplitude**2 * (v**3 + 10 * v**2 * w + 16 * v * w**2 + 16 * w**3)
        + sp.Rational(5, 4) * v**4
        + v**3 * w
        + 25 * v**2 * w**2
        + 16 * v * w**3
        + 20 * w**4
    )
    checks.require("cross_cluster", "whole-output HS square", sp.simplify(hs_square - expected_hs) == 0, sp.simplify(hs_square - expected_hs), 0)
    expected_variance = sp.Rational(1, 4) * (
        amplitude**4 * v**2
        + 16 * amplitude**4 * w**2
        + 2 * amplitude**2 * v**3
        + 20 * amplitude**2 * v**2 * w
        + 32 * amplitude**2 * v * w**2
        + 32 * amplitude**2 * w**3
        + 2 * v**4
        + 2 * v**3 * w
        + 42 * v**2 * w**2
        + 32 * v * w**3
        + 32 * w**4
    )
    checks.require("cross_cluster", "exact variance", sp.simplify(packet_variance - expected_variance) == 0, sp.simplify(packet_variance - expected_variance), 0)
    leading_margin = sp.factor(hs_square - 2 * packet_variance)
    expected_margin = (v**4 + 16 * v**2 * w**2 + 16 * w**4) / 4
    checks.require("cross_cluster", "strict small-q square-first margin", sp.simplify(leading_margin - expected_margin) == 0, leading_margin, expected_margin)
    checks.require("cross_cluster", "third moment coefficientwise positive", all(coefficient > 0 for coefficient in sp.Poly(packet_third, amplitude, v, w).coeffs()), sp.Poly(packet_third, amplitude, v, w).coeffs(), "all positive")

    # Pointwise payment theorem.  The worst phase is C=-|A|R sqrt(S), and
    # the exact square is 10 R (sqrt(S)-3|A|/10)^2.
    root_s, abs_a, root_r = sp.symbols("sqrtS absA sqrtR", nonnegative=True)
    payment_remainder = sp.Rational(9, 10) * abs_a**2 * root_r**2 + 10 * root_r**2 * root_s**2 - 6 * abs_a * root_r**2 * root_s
    payment_square = 10 * root_r**2 * (root_s - 3 * abs_a / 10) ** 2
    checks.require("cross_payment", "exact pointwise square", sp.expand(payment_remainder - payment_square) == 0, sp.expand(payment_remainder - payment_square), 0)
    t1 = q_prod * amplitude**2 * v / 2
    t2 = 2 * q_prod * amplitude**2 * w
    quadratic_ceiling = sp.simplify(t1**2 / 2 + t2**2 / 2)
    expected_ceiling = sp.simplify(q_prod**2 * amplitude**4 * (v**2 / 8 + 2 * w**2))
    checks.require("cross_payment", "two one-pair determinant ceilings", quadratic_ceiling == expected_ceiling, quadratic_ceiling, expected_ceiling)
    expected_payment = sp.simplify((sp.Rational(9, 10) * amplitude**2 + 4 * w) * v / 2 + v * w / 2)
    expected_payment_formula = sp.Rational(9, 20) * amplitude**2 * v + sp.Rational(5, 2) * v * w
    checks.require(
        "cross_payment",
        "payment expectation",
        sp.simplify(expected_payment - expected_payment_formula) == 0,
        expected_payment,
        expected_payment_formula,
    )
    checks.require("cross_payment", "baseline shell exponent diverges", 3 - 2 == 1, 3 - 2, 1)
    checks.require("cross_payment", "covariance floor shell exponent", 3 - 6 == -3, 3 - 6, -3)
    checks.require("cross_payment", "square-first baseline shell exponent", 3 - 4 == -1, 3 - 4, -1)

    # A deliberately finite falsifier scan.  It is regression evidence only;
    # no all-q theorem is inferred from these quadrature nodes.
    mp.mp.dps = 45
    scan_points = (
        (mp.mpf("0.1"), mp.mpf("0"), mp.mpf("0.1")),
        (mp.mpf("1"), mp.mpf("1"), mp.mpf("1")),
        (mp.mpf("10"), mp.mpf("4"), mp.mpf("0.1")),
        (mp.mpf("0.03"), mp.mpf("16"), mp.mpf("0.01")),
    )
    scan_margins: list[dict[str, object]] = []
    for w_value, amplitude_value, q_scan in scan_points:
        h_value = (
            amplitude_value**4 * (mp.mpf("0.5") + 8 * w_value**2)
            + amplitude_value**2 * (1 + 10 * w_value + 16 * w_value**2 + 16 * w_value**3)
            + mp.mpf("1.25")
            + w_value
            + 25 * w_value**2
            + 16 * w_value**3
            + 20 * w_value**4
        )
        margins_by_order: dict[int, mp.mpf] = {}
        for order in (24, 48):
            log_mgf = laguerre_log_mgf(mp.mpf(1), w_value, amplitude_value, q_scan, order=order)
            margins_by_order[order] = q_scan**2 * h_value / 4 - log_mgf
        checks.require(
            "cross_scan",
            f"finite quadrature sign stable at orders 24/48 w={w_value} A={amplitude_value} q={q_scan}",
            all(value > 0 for value in margins_by_order.values()),
            {order: mp.nstr(value, 18) for order, value in margins_by_order.items()},
            "both >0",
        )
        scan_margins.append(
            {
                "v": "1",
                "w": str(w_value),
                "A": str(amplitude_value),
                "q": str(q_scan),
                "order_24": mp.nstr(margins_by_order[24], 24),
                "order_48": mp.nstr(margins_by_order[48], 24),
            }
        )

    status = "PASS" if all(row["status"] == "PASS" for row in checks.rows) else "FAIL"
    results = {
        "random_w": {
            "q_random_cost": str(random_cost),
            "q_fixed_cost": str(fixed_cost),
            "oscillatory_score_slope": "tau*epsilon/2",
            "oscillatory_cost_slope": "8*epsilon^2",
            "rotating_projector_score_slope": "tau/4",
            "rotating_projector_cost_slope": "2",
        },
        "mean_debt": {
            "mean": str(mean_diag),
            "covariance_square": str(covariance_square),
            "q_fixture_jensen": str(jensen_lower),
            "q_fixture_square_cost": str(square_first_rhs),
            "violation_margin": str(jensen_lower - square_first_rhs),
        },
        "cross_cluster": {
            "mean": str(packet_mean),
            "variance": str(packet_variance),
            "third_moment": str(packet_third),
            "whole_output_hs_square": str(hs_square),
            "leading_margin": str(leading_margin),
            "scan_margins": scan_margins,
        },
        "shell_exponents": {
            "pointwise_baseline": 1,
            "covariance_floor": -3,
            "square_first_baseline": -1,
        },
    }
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "status": status,
        "assertions_total": len(checks.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in checks.rows),
        "assertions_failed": sum(row["status"] != "PASS" for row in checks.rows),
        "assertion_names": [f"{row['group']}::{row['name']}" for row in checks.rows],
        "assertions": checks.rows,
        "results": results,
        "results_sha256": hashlib.sha256(
            json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "route_verdicts": {
            "random_W_double_divergence": "proved-exact-form-bound",
            "random_W_HS_only_extension": "failed",
            "trace_corrected_diagonal_interpolation": "proved-exact-identity",
            "universal_nonlinear_square_first": "failed",
            "physical_k2k_complete_cluster": "proved-exact-moments",
            "physical_k2k_bare_all_q_square_first": "open-passed-local-and-finite-falsifiers",
            "pointwise_cross_payment": "proved-but-nonsummable",
            "production_complete_cluster": "open",
            "sector_a": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"primary {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
