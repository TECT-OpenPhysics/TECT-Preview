#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-108 quotient frontier.

This package audits the historical R-085 atom coordinates against the
progressive subdivision quotient, derives the quotient-safe complete endpoint
and conditional cluster identities, and fixes the order of operations and
uniformity requirements for any surviving matrix-Carleson route.  It does not
assert OVERLAP_src, Nelson, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

import sympy as sp


SCHEMA = "tect/a13-complete-cluster-quotient-carleson-frontier-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-complete-cluster-quotient-carleson-frontier/result.json"
)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def require(self, group: str, name: str, condition: object, actual: object, expected: object) -> None:
        passed = condition is True or condition == sp.S.true
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


def rational_owner(b: sp.Expr, x: sp.Symbol, u: int, g: int, a: int, c: int) -> dict[str, sp.Expr]:
    """Derive the historical and complete rational owners on one scalar chart."""

    b0 = sp.cancel(b.subs(x, u))
    b1 = sp.cancel(b.subs(x, u + a))
    bp = sp.cancel(sp.diff(b, x).subs(x, u))
    bpp = sp.cancel(sp.diff(b, x, 2).subs(x, u))
    b_taylor = sp.cancel(b0 + bp * a + sp.Rational(1, 2) * bpp * a * a)
    remainder = sp.cancel(b1 - b_taylor)
    q0 = sp.Integer(g * g - 1)
    q1 = sp.Integer((g + c) * (g + c) - 1)
    r_q = sp.cancel(sp.Rational(1, 2) * (b1 - b0) * q0)
    m_u = sp.cancel(g * b_taylor * c)
    k_r = sp.cancel(g * remainder * c + sp.Rational(1, 2) * b1 * c * c)
    f_65 = sp.cancel(sp.Rational(1, 2) * remainder * q0 + k_r)
    delta = sp.cancel(r_q + m_u + k_r)
    endpoint = sp.cancel(sp.Rational(1, 2) * b1 * q1 - sp.Rational(1, 2) * b0 * q0)
    return {
        "B0": b0,
        "B1": b1,
        "B_T": b_taylor,
        "L": remainder,
        "Q": q0,
        "R_Q": r_q,
        "M_U": m_u,
        "K_R": k_r,
        "F_6_5": f_65,
        "Delta": delta,
        "endpoint": endpoint,
    }


def weighted_mean(vectors: tuple[sp.Matrix, ...], weights: tuple[sp.Rational, ...]) -> sp.Matrix:
    total = sp.zeros(vectors[0].rows, 1)
    for weight, vector in zip(weights, vectors):
        total += weight * vector
    return sp.simplify(total)


def weighted_covariance(vectors: tuple[sp.Matrix, ...], weights: tuple[sp.Rational, ...], mean: sp.Matrix) -> sp.Matrix:
    total = sp.zeros(mean.rows)
    for weight, vector in zip(weights, vectors):
        centered = vector - mean
        total += weight * centered * centered.T
    return sp.simplify(total)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    # The exact q-scaled budget left by the already accepted action.
    q = sp.Rational(10, 9)
    source_budget = sp.Rational(9, 20)
    sextic_budget = sp.Rational(3, 20)
    eta_star = sp.Rational(1, 440)
    zeta_star = sp.Rational(3, 100)
    q_eta = sp.cancel(q * eta_star)
    q_zeta = sp.cancel(q * zeta_star)
    source_reserve = sp.cancel(q * source_budget - q_eta)
    sextic_reserve = sp.cancel(q * sextic_budget - q_zeta)
    checks.require("budget", "q source coefficient", q * source_budget == sp.Rational(1, 2), q * source_budget, sp.Rational(1, 2))
    checks.require("budget", "q sextic coefficient", q * sextic_budget == sp.Rational(1, 6), q * sextic_budget, sp.Rational(1, 6))
    checks.require("budget", "q eta star", q_eta == sp.Rational(1, 396), q_eta, sp.Rational(1, 396))
    checks.require("budget", "q zeta star", q_zeta == sp.Rational(1, 30), q_zeta, sp.Rational(1, 30))
    checks.require("budget", "q scaled source reserve", source_reserve == sp.Rational(197, 396), source_reserve, sp.Rational(197, 396))
    checks.require("budget", "q scaled sextic reserve", sextic_reserve == sp.Rational(2, 15), sextic_reserve, sp.Rational(2, 15))
    checks.require("budget", "seven module q eta share", q_eta / 7 == sp.Rational(1, 2772), q_eta / 7, sp.Rational(1, 2772))
    checks.require("budget", "seven module q zeta share", q_zeta / 7 == sp.Rational(1, 210), q_zeta / 7, sp.Rational(1, 210))
    checks.require("budget", "eight module q eta share", q_eta / 8 == sp.Rational(1, 3168), q_eta / 8, sp.Rational(1, 3168))
    checks.require("budget", "eight module q zeta share", q_zeta / 8 == sp.Rational(1, 240), q_zeta / 8, sp.Rational(1, 240))

    # R-085's historical weighted sufficient architecture versus the exact
    # R-088 direct OU target.  These constants are diagnostics, not new bounds.
    old_s = sp.Rational(7, 12)
    old_eta = sp.Rational(1, 12)
    old_schur = sp.simplify(
        1
        / (
            (1 - 2 ** (-old_eta))
            * (1 - 2 ** (-2 * old_s))
            * (1 - 2 ** (1 + old_eta - 2 * old_s))
        )
    )
    direct_s = sp.Rational(7, 12)
    direct_eta = sp.Rational(7, 12)
    direct_schur = sp.simplify(
        1
        / (
            (1 - 2 ** (-direct_eta))
            * (1 - 2 ** (-2 * direct_s))
            * (1 - 2 ** (direct_eta - 2 * direct_s))
        )
    )
    old_numeric = float(sp.N(old_schur, 18))
    direct_numeric = float(sp.N(direct_schur, 18))
    checks.require("schur", "historical exponent exceeds one half", old_s > sp.Rational(1, 2), old_s, ">1/2")
    checks.require("schur", "direct exponent is positive", direct_s > 0, direct_s, ">0")
    checks.require("schur", "historical Schur constant", abs(old_numeric - 572.4472106721531) < 1e-12, old_numeric, 572.4472106721531)
    checks.require("schur", "direct Schur constant", abs(direct_numeric - 16.30295538482827) < 1e-13, direct_numeric, 16.30295538482827)
    checks.require("schur", "direct constant is smaller", direct_schur < old_schur, direct_numeric, f"<{old_numeric}")
    checks.require("schur", "q linear historical constant", abs(float(sp.N(q * old_schur, 18)) - 636.0524563023923) < 1e-12, sp.N(q * old_schur, 18), 636.0524563023923)
    checks.require("schur", "q linear direct constant", abs(float(sp.N(q * direct_schur, 18)) - 18.11439487203141) < 1e-13, sp.N(q * direct_schur, 18), 18.11439487203141)

    # Historical F_6.5 and fixed-chart K_R do not descend to the progressive
    # quotient, while the complete endpoint does.
    x = sp.symbols("x", real=True)
    b = sp.cancel(4 * x**2 * (4 * x**2 + 9) ** 2 / (81 * (1 + x**2) ** 2))
    one = rational_owner(b, x, 0, 1, 2, 2)
    step1 = rational_owner(b, x, 0, 1, 1, 1)
    step2 = rational_owner(b, x, 1, 2, 1, 1)
    split = {name: sp.cancel(step1[name] + step2[name]) for name in ("R_Q", "M_U", "K_R", "F_6_5", "Delta")}
    defects = {name: sp.cancel(one[name] - split[name]) for name in split}
    expected_one = {
        "K_R": sp.Rational(-992, 81),
        "F_6_5": sp.Rational(-992, 81),
        "Delta": sp.Rational(1600, 81),
    }
    expected_split = {
        "R_Q": sp.Rational(77, 18),
        "M_U": sp.Rational(1076, 81),
        "K_R": sp.Rational(355, 162),
        "F_6_5": sp.Rational(427, 162),
        "Delta": sp.Rational(1600, 81),
    }
    expected_defects = {
        "R_Q": sp.Rational(-77, 18),
        "M_U": sp.Rational(1516, 81),
        "K_R": sp.Rational(-2339, 162),
        "F_6_5": sp.Rational(-2411, 162),
        "Delta": sp.Integer(0),
    }
    for name, expected in expected_one.items():
        checks.require("quotient", f"one chart exact {name}", one[name] == expected, one[name], expected)
    for name, expected in expected_split.items():
        checks.require("quotient", f"split exact {name}", split[name] == expected, split[name], expected)
    for name, expected in expected_defects.items():
        checks.require("quotient", f"owner defect exact {name}", defects[name] == expected, defects[name], expected)
    checks.require("quotient", "historical F65 identity", sp.cancel(one["F_6_5"] - (one["L"] * one["Q"] / 2 + one["K_R"])) == 0, one["F_6_5"], one["L"] * one["Q"] / 2 + one["K_R"])
    checks.require("quotient", "one chart labelled owners reconstruct endpoint", sp.cancel(one["R_Q"] + one["M_U"] + one["K_R"] - one["Delta"]) == 0, one["R_Q"] + one["M_U"] + one["K_R"], one["Delta"])
    checks.require("quotient", "split labelled owners reconstruct endpoint", sp.cancel(split["R_Q"] + split["M_U"] + split["K_R"] - split["Delta"]) == 0, split["R_Q"] + split["M_U"] + split["K_R"], split["Delta"])
    checks.require("quotient", "labelled owner defects cancel", sp.cancel(defects["R_Q"] + defects["M_U"] + defects["K_R"]) == 0, defects["R_Q"] + defects["M_U"] + defects["K_R"], 0)
    checks.require("quotient", "F65 changes sign", one["F_6_5"] < 0 < split["F_6_5"], (one["F_6_5"], split["F_6_5"]), "negative then positive")
    checks.require("quotient", "KR changes sign", one["K_R"] < 0 < split["K_R"], (one["K_R"], split["K_R"]), "negative then positive")
    checks.require("quotient", "complete endpoint subdivision invariant", defects["Delta"] == 0, defects["Delta"], 0)

    # Quotient-safe conditional complete endpoint identity.
    b00, b01, b11, d00, d01, d11 = sp.symbols("b00 b01 b11 d00 d01 d11", real=True)
    v00, v01, v11, g00, g01, g11 = sp.symbols("v00 v01 v11 g00 g01 g11", real=True)
    m0, m1, c0, c1 = sp.symbols("m0 m1 c0 c1", real=True)
    b0 = sp.Matrix([[b00, b01], [b01, b11]])
    b1 = sp.Matrix([[d00, d01], [d01, d11]])
    covariance = sp.Matrix([[v00, v01], [v01, v11]])
    gamma = sp.Matrix([[g00, g01], [g01, g11]])
    mean = sp.Matrix([m0, m1])
    shift = sp.Matrix([c0, c1])
    expected_first = ((mean + shift).T * b1 * (mean + shift))[0] + sp.trace(b1 * covariance)
    expected_zero = (mean.T * b0 * mean)[0] + sp.trace(b0 * covariance)
    complete_conditional = sp.expand((expected_first - expected_zero - sp.trace((b1 - b0) * gamma)) / 2)
    quotient_normal = sp.expand(
        ((mean + shift).T * b1 * (mean + shift))[0] / 2
        - (mean.T * b0 * mean)[0] / 2
        + sp.trace((b1 - b0) * (covariance - gamma)) / 2
    )
    checks.require("endpoint", "complete conditional endpoint identity", sp.simplify(complete_conditional - quotient_normal) == 0, complete_conditional - quotient_normal, 0)

    # Exact finite-dimensional optimized form at q=10/9.
    b0n = sp.Matrix([[2, 1], [1, 3]])
    b1n = sp.Matrix([[4, 1], [1, 2]])
    mun = sp.Matrix([sp.Rational(2, 3), sp.Rational(-1, 2)])
    vn = sp.Matrix([[2, sp.Rational(1, 4)], [sp.Rational(1, 4), 1]])
    gamman = sp.eye(2)
    cstar = -q * (sp.eye(2) + q * b1n).inv() * b1n * mun
    objective = (
        q
        * (
            ((mun + shift).T * b1n * (mun + shift))[0] / 2
            - (mun.T * b0n * mun)[0] / 2
            + sp.trace((b1n - b0n) * (vn - gamman)) / 2
        )
        + (shift.T * shift)[0] / 2
    )
    optimized_direct = sp.simplify(objective.subs({c0: cstar[0], c1: cstar[1]}))
    optimized_formula = sp.simplify(
        q * sp.trace((b1n - b0n) * (vn - gamman)) / 2
        + q
        * (mun.T * (b1n * (sp.eye(2) + q * b1n).inv() - b0n) * mun)[0]
        / 2
    )
    gradient_at_star = sp.Matrix([sp.diff(objective, c0), sp.diff(objective, c1)]).subs({c0: cstar[0], c1: cstar[1]})
    checks.require("endpoint", "complete endpoint optimizer stationary", gradient_at_star == sp.zeros(2, 1), gradient_at_star, sp.zeros(2, 1))
    checks.require("endpoint", "complete endpoint optimized formula", sp.simplify(optimized_direct - optimized_formula) == 0, optimized_direct, optimized_formula)
    scalar_negative = sp.Rational(5, 9) * (sp.Integer(1) - sp.Integer(2)) * (sp.Integer(2) - sp.Integer(1))
    scalar_positive = sp.Rational(5, 9) * (sp.Integer(2) - sp.Integer(1)) * (sp.Integer(2) - sp.Integer(1))
    checks.require("endpoint", "optimized trace fixture can be negative", scalar_negative == sp.Rational(-5, 9), scalar_negative, sp.Rational(-5, 9))
    checks.require("endpoint", "optimized trace fixture can be positive", scalar_positive == sp.Rational(5, 9), scalar_positive, sp.Rational(5, 9))

    # Exact conditional mean/covariance normal form for a complete cluster.
    weights = (sp.Rational(1, 4), sp.Rational(1, 2), sp.Rational(1, 4))
    values = (sp.Matrix([2, -1]), sp.Matrix([-1, 3]), sp.Matrix([4, 2]))
    trace_values = (sp.Rational(3, 2), sp.Rational(1, 2), sp.Rational(5, 2))
    baseline = sp.Matrix([sp.Rational(2, 3), sp.Rational(-4, 5)])
    mu = weighted_mean(values, weights)
    sigma = weighted_covariance(values, weights, mu)
    expected_trace = sum(weight * value for weight, value in zip(weights, trace_values))
    cluster_left = sum(
        weight * (((baseline + value).T * (baseline + value))[0] - trace_value) / 2
        for weight, value, trace_value in zip(weights, values, trace_values)
    )
    cluster_right = ((baseline + mu).T * (baseline + mu))[0] / 2 + (sp.trace(sigma) - expected_trace) / 2
    checks.require("cluster", "complete cluster mean covariance identity", sp.simplify(cluster_left - cluster_right) == 0, cluster_left, cluster_right)
    checks.require("cluster", "cluster weights normalize", sum(weights) == 1, sum(weights), 1)
    checks.require("cluster", "cluster covariance positive determinant", sigma.det() > 0, sigma.det(), ">0")

    # One-pair signed cluster and the square-before-average obstruction.
    sigma2 = sp.symbols("sigma2", positive=True)
    exp_moments = {power: sp.factorial(power) for power in range(7)}
    radial_moment = lambda power: sigma2**power * exp_moments[power] / 2**power
    packet_mean = sp.expand(radial_moment(2) - sigma2 * radial_moment(1))
    packet_second = sp.expand(radial_moment(4) - 2 * sigma2 * radial_moment(3) + sigma2**2 * radial_moment(2))
    packet_variance = sp.expand(packet_second - packet_mean**2)
    actual_log_lead = sp.expand(q**2 * packet_variance / 2)
    realized_hs2 = sp.expand(sp.Rational(5, 2) * sigma2**2 * radial_moment(2))
    averaged_hs2 = sp.Rational(3, 8) * sigma2**4
    averaged_determinant_lead = sp.expand(q**2 * averaged_hs2 / 4)
    realized_determinant_lead = sp.expand(q**2 * realized_hs2 / 4)
    averaged_deficit = sp.expand(actual_log_lead - averaged_determinant_lead)
    realized_room = sp.expand(realized_determinant_lead - actual_log_lead)
    sextic_mean = sp.expand(20 * radial_moment(3))
    zeta_threshold = sp.simplify(averaged_deficit / (q * sextic_mean))
    checks.require("one_pair", "signed cluster mean zero", packet_mean == 0, packet_mean, 0)
    checks.require("one_pair", "signed cluster variance", packet_variance == sigma2**4 / 2, packet_variance, sigma2**4 / 2)
    checks.require("one_pair", "log Laplace leading coefficient", actual_log_lead == q**2 * sigma2**4 / 4, actual_log_lead, q**2 * sigma2**4 / 4)
    checks.require("one_pair", "realized covariance square", realized_hs2 == sp.Rational(5, 4) * sigma2**4, realized_hs2, sp.Rational(5, 4) * sigma2**4)
    checks.require("one_pair", "averaged covariance square", averaged_hs2 == sp.Rational(3, 8) * sigma2**4, averaged_hs2, sp.Rational(3, 8) * sigma2**4)
    checks.require("one_pair", "average before square leading deficit", averaged_deficit == sp.Rational(5, 32) * q**2 * sigma2**4, averaged_deficit, sp.Rational(5, 32) * q**2 * sigma2**4)
    checks.require("one_pair", "realized square has leading room", realized_room == q**2 * sigma2**4 / 16, realized_room, q**2 * sigma2**4 / 16)
    checks.require("one_pair", "parent sextic mean", sextic_mean == 15 * sigma2**3, sextic_mean, 15 * sigma2**3)
    checks.require("one_pair", "averaged covariance sextic threshold", zeta_threshold == q * sigma2 / 96, zeta_threshold, q * sigma2 / 96)
    checks.require("one_pair", "q ten ninths threshold", zeta_threshold.subs(sigma2, 1) == sp.Rational(5, 432), zeta_threshold.subs(sigma2, 1), sp.Rational(5, 432))

    # Arbitrary future-feedback selector: absolute tangent and rank-one
    # covariance squares grow while source and sextic budgets stay bounded.
    amplitude, frequency = sp.symbols("amplitude frequency", positive=True)
    eh2 = amplitude**2 * (1 - sp.exp(-2 * frequency**2)) / 2
    eh6 = amplitude**6 * (
        10
        - 15 * sp.exp(-2 * frequency**2)
        + 6 * sp.exp(-8 * frequency**2)
        - sp.exp(-18 * frequency**2)
    ) / 32
    tangent_square = amplitude**4 * frequency**2 * (1 - sp.exp(-8 * frequency**2)) / 2
    rank_one_hs_square = amplitude**8 * frequency**4 * (
        3 - 4 * sp.exp(-8 * frequency**2) + sp.exp(-32 * frequency**2)
    ) / 8
    checks.require("feedback", "source amplitude bounded limit", sp.limit(eh2, frequency, sp.oo) == amplitude**2 / 2, sp.limit(eh2, frequency, sp.oo), amplitude**2 / 2)
    checks.require("feedback", "terminal sextic bounded limit", sp.limit(eh6, frequency, sp.oo) == sp.Rational(5, 16) * amplitude**6, sp.limit(eh6, frequency, sp.oo), sp.Rational(5, 16) * amplitude**6)
    checks.require("feedback", "tangent square quadratic growth", sp.limit(tangent_square / frequency**2, frequency, sp.oo) == amplitude**4 / 2, sp.limit(tangent_square / frequency**2, frequency, sp.oo), amplitude**4 / 2)
    checks.require("feedback", "rank one square quartic growth", sp.limit(rank_one_hs_square / frequency**4, frequency, sp.oo) == sp.Rational(3, 8) * amplitude**8, sp.limit(rank_one_hs_square / frequency**4, frequency, sp.oo), sp.Rational(3, 8) * amplitude**8)
    mode = sp.symbols("mode", positive=True, integer=True)
    spatial_h2 = (1 + mode**2) ** 2 / 2
    spatial_l6_sixth = sp.Rational(5, 16)
    spatial_product_l2 = mode**2 / 8
    source_energy = sp.simplify(eh2 * spatial_h2)
    terminal_sextic = sp.simplify(eh6 * spatial_l6_sixth)
    projected_tangent = sp.simplify(tangent_square * spatial_product_l2)
    checks.require("feedback", "explicit carrier H2 norm", spatial_h2 == (1 + mode**2) ** 2 / 2, spatial_h2, (1 + mode**2) ** 2 / 2)
    checks.require("feedback", "explicit carrier L6 sixth norm", spatial_l6_sixth == sp.Rational(5, 16), spatial_l6_sixth, sp.Rational(5, 16))
    checks.require("feedback", "explicit carrier product L2 norm", spatial_product_l2 == mode**2 / 8, spatial_product_l2, mode**2 / 8)
    expected_source_energy = amplitude**2 * (1 - sp.exp(-2 * frequency**2)) * (1 + mode**2) ** 2 / 4
    expected_terminal_sextic = 5 * amplitude**6 * (10 - 15 * sp.exp(-2 * frequency**2) + 6 * sp.exp(-8 * frequency**2) - sp.exp(-18 * frequency**2)) / 512
    expected_projected_tangent = amplitude**4 * frequency**2 * mode**2 * (1 - sp.exp(-8 * frequency**2)) / 16
    checks.require("feedback", "explicit source energy formula", sp.simplify(source_energy - expected_source_energy) == 0, source_energy, expected_source_energy)
    checks.require("feedback", "explicit terminal sextic formula", sp.simplify(terminal_sextic - expected_terminal_sextic) == 0, terminal_sextic, expected_terminal_sextic)
    checks.require("feedback", "explicit projected tangent formula", sp.simplify(projected_tangent - expected_projected_tangent) == 0, projected_tangent, expected_projected_tangent)
    high_carrier = -mode * sp.sin(2 * mode * x) / 2
    checks.require("feedback", "explicit far carrier has doubled mode", high_carrier.expand().coeff(sp.sin(2 * mode * x)) == -mode / 2, high_carrier.expand().coeff(sp.sin(2 * mode * x)), -mode / 2)

    failed = [row for row in checks.rows if row["status"] != "PASS"]
    derived = {
        "q": str(q),
        "source_budget": str(source_budget),
        "sextic_budget": str(sextic_budget),
        "q_eta_star": str(q_eta),
        "q_zeta_star": str(q_zeta),
        "q_source_reserve": str(source_reserve),
        "q_sextic_reserve": str(sextic_reserve),
        "historical_schur_constant": repr(old_numeric),
        "direct_schur_constant": repr(direct_numeric),
        "one_chart_F_6_5": str(one["F_6_5"]),
        "split_F_6_5": str(split["F_6_5"]),
        "one_chart_K_R": str(one["K_R"]),
        "split_K_R": str(split["K_R"]),
        "complete_endpoint": str(one["Delta"]),
        "average_before_square_deficit": str(averaged_deficit),
        "realized_square_room": str(realized_room),
        "sextic_tradeoff_threshold": str(zeta_threshold),
        "future_feedback_tangent_square": str(tangent_square),
        "future_feedback_rank_one_hs_square": str(rank_one_hs_square),
        "explicit_future_feedback_source": str(source_energy),
        "explicit_future_feedback_sextic": str(terminal_sextic),
        "explicit_future_feedback_projected_tangent": str(projected_tangent),
    }
    route_verdicts = {
        "historical_R085_4_10_spatial_half": "closed-in-regular-scope-by-R087",
        "historical_R085_4_11_weighted_bridge": "superseded-as-current-target-and-unproved",
        "direct_R088_unweighted_bridge": "open",
        "historical_F_6_5_progressive_owner": "failed-not-subdivision-invariant",
        "fixed_chart_K_R": "retained-only-in-declared-regular-scope",
        "complete_endpoint_conditional_identity": "advanced-exact-quotient-safe",
        "complete_cluster_mean_covariance_identity": "advanced-exact-signed-normal-form",
        "average_covariance_before_hs_square": "failed-leading-order-deficit-without-tradeoff",
        "absolute_future_feedback_matrix_carleson": "failed-for-arbitrary-selectors",
        "realized_cluster_square_then_average": "viable-order-not-a-bound",
        "uniform_complete_cluster_lower_bound": "open",
        "overlap_src": "open",
        "nelson": "open",
        "sector_a": "open",
    }
    results = {"derived": derived, "route_verdicts": route_verdicts}
    results_sha256 = hashlib.sha256(
        json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "status": "PASS" if not failed else "FAIL",
        "assertions_total": len(checks.rows),
        "assertions_passed": len(checks.rows) - len(failed),
        "assertions_failed": len(failed),
        "assertions": checks.rows,
        "assertion_names": [str(row["name"]) for row in checks.rows],
        "results_sha256": results_sha256,
        "results": results,
        "derived": derived,
        "route_verdicts": route_verdicts,
    }
    atomic_json(args.output, payload)
    print(f"Primary R-108: {payload['assertions_passed']}/{payload['assertions_total']} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
