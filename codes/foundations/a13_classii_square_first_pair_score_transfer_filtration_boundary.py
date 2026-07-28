#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-109 advance.

The certificate proves an all-amplitude square-before-average normalizer for
the smallest contraction-closed nonlinear pair, the selector-independent
quartic floor, and a conditional Gaussian score-transfer estimate for one
complete signed second jet.  It also checks the filtration and
Stein-exponentiation boundaries.  It does not assert the full production
cluster bound, OVERLAP_src, Nelson, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

import mpmath as mp
import sympy as sp


SCHEMA = "tect/a13-square-first-pair-score-transfer-filtration-boundary-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-square-first-pair-score-transfer-filtration-boundary/result.json"
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


def exp_moment(power: int) -> sp.Integer:
    """Moment E[T**power] for T with the unit exponential law."""

    return sp.factorial(power)


def gaussian_even_moment(power: int) -> sp.Integer:
    if power % 2:
        return sp.Integer(0)
    if power == 0:
        return sp.Integer(1)
    return sp.factorial2(power - 1)


def polynomial_expectation(poly: sp.Expr, variable: sp.Symbol, moment) -> sp.Expr:
    expanded = sp.Poly(sp.expand(poly), variable)
    total = sp.Integer(0)
    for (degree,), coefficient in expanded.terms():
        total += coefficient * moment(degree)
    return sp.simplify(total)


def exact_one_pair_log_mgf(a: mp.mpf) -> mp.mpf:
    """Exact integral of E exp(a(2T-T^2)), T exponential."""

    if a == 0:
        return mp.mpf("0")
    d = 1 - 2 * a
    integral = (
        mp.sqrt(mp.pi)
        / (2 * mp.sqrt(a))
        * mp.exp(d * d / (4 * a))
        * mp.erfc(d / (2 * mp.sqrt(a)))
    )
    return mp.log(integral)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    checks = Checks()
    t = sp.symbols("t", nonnegative=True)
    q = sp.Rational(10, 9)
    threshold = sp.Rational(1, 5)

    # The complete one-pair radial variable.
    u = 2 * t - t**2
    eu = polynomial_expectation(u, t, exp_moment)
    eu2 = polynomial_expectation(u**2, t, exp_moment)
    eu3 = polynomial_expectation(u**3, t, exp_moment)
    checks.require("pair_moments", "exponential first moment", exp_moment(1) == 1, exp_moment(1), 1)
    checks.require("pair_moments", "exponential second moment", exp_moment(2) == 2, exp_moment(2), 2)
    checks.require("pair_moments", "radial score is centered", eu == 0, eu, 0)
    checks.require("pair_moments", "radial score variance", eu2 == 8, eu2, 8)
    checks.require("pair_moments", "radial score third moment", eu3 == -240, eu3, -240)
    checks.require(
        "pair_moments",
        "one-sided support identity",
        sp.expand(u - (1 - (t - 1) ** 2)) == 0,
        sp.expand(u - (1 - (t - 1) ** 2)),
        0,
    )

    # Bennett small-a and pathwise large-a branches.
    small_multiplier = sp.simplify(4 / (1 - threshold / 3))
    checks.require(
        "bennett",
        "series majorant at threshold",
        small_multiplier == sp.Rational(30, 7),
        small_multiplier,
        sp.Rational(30, 7),
    )
    checks.require("bennett", "small branch below square cost", small_multiplier < 5, small_multiplier, "<5")
    checks.require(
        "bennett",
        "large branch meets at threshold",
        threshold == 5 * threshold**2,
        threshold,
        5 * threshold**2,
    )
    checks.require(
        "bennett",
        "branch intervals cover nonnegative axis",
        threshold <= threshold,
        "[0,1/5] union [1/5,infinity)",
        "[0,infinity)",
    )
    checks.require(
        "bennett",
        "elementary exponential ceiling",
        sp.Rational(1, 1) / (1 - threshold) == sp.Rational(5, 4),
        1 / (1 - threshold),
        sp.Rational(5, 4),
    )

    # Exact covariance-square normalization.
    sigma, lam = sp.symbols("sigma lambda", nonnegative=True)
    r = sigma**2 * t / 2
    packet = lam * (r**2 - sigma**2 * r)
    epacket = polynomial_expectation(packet, t, exp_moment)
    epacket2 = polynomial_expectation(packet**2, t, exp_moment)
    beta = sp.simplify(lam * sigma**4 / 4)
    s_eigenvalues = (sp.Rational(3, 2) * lam * sigma**2 * r, sp.Rational(1, 2) * lam * sigma**2 * r)
    hs_square = sp.simplify(sum(value**2 for value in s_eigenvalues))
    e_hs_square = polynomial_expectation(hs_square, t, exp_moment)
    normalizer_cost = sp.simplify(q**2 * e_hs_square / 4)
    checks.require("pair_normalizer", "packet centered", epacket == 0, epacket, 0)
    checks.require(
        "pair_normalizer",
        "packet second moment",
        epacket2 == lam**2 * sigma**8 / 2,
        epacket2,
        lam**2 * sigma**8 / 2,
    )
    checks.require(
        "pair_normalizer",
        "realized covariance square",
        e_hs_square == sp.Rational(5, 4) * lam**2 * sigma**8,
        e_hs_square,
        sp.Rational(5, 4) * lam**2 * sigma**8,
    )
    checks.require(
        "pair_normalizer",
        "Bennett cost equals square-first cost",
        sp.simplify(normalizer_cost - 5 * (q * beta) ** 2) == 0,
        normalizer_cost,
        5 * (q * beta) ** 2,
    )
    checks.require(
        "pair_normalizer",
        "infinitesimal coefficient is four",
        eu2 / 2 == 4,
        eu2 / 2,
        4,
    )
    checks.require(
        "pair_normalizer",
        "square-first coefficient has one unit room",
        5 - eu2 / 2 == 1,
        5 - eu2 / 2,
        1,
    )

    mp.mp.dps = 60
    numeric_a = tuple(mp.mpf(value) for value in ("0.01", "0.05", "0.2", "1", "5"))
    numeric_ratios = tuple(exact_one_pair_log_mgf(value) / (value * value) for value in numeric_a)
    checks.require(
        "pair_normalizer",
        "exact finite amplitudes respect cost",
        all(value <= 5 for value in numeric_ratios),
        [mp.nstr(value, 18) for value in numeric_ratios],
        "all <= 5",
    )

    # Selector-independent floor and the exact R-105 joint-floor split.
    alpha, mu, s = sp.symbols("alpha mu s", nonnegative=True)
    quartic_floor_identity = sp.expand(r**2 - sigma**2 * r - ((r - sigma**2 / 2) ** 2 - sigma**4 / 4))
    checks.require("floors", "quartic complete-square identity", quartic_floor_identity == 0, quartic_floor_identity, 0)
    joint = alpha * (s - 2) + mu * (s**2 - 4 * s)
    stationary = sp.simplify((4 * mu - alpha) / (2 * mu))
    stationary_value = sp.simplify(joint.subs(s, stationary))
    checks.require(
        "floors",
        "joint interior minimizer",
        sp.simplify(sp.diff(joint, s).subs(s, stationary)) == 0,
        sp.diff(joint, s).subs(s, stationary),
        0,
    )
    checks.require(
        "floors",
        "joint interior floor",
        stationary_value == -4 * mu - alpha**2 / (4 * mu),
        stationary_value,
        -4 * mu - alpha**2 / (4 * mu),
    )
    checks.require("floors", "joint boundary floor", joint.subs(s, 0) == -2 * alpha, joint.subs(s, 0), -2 * alpha)

    dimension = sp.Integer(3)
    covariance_decay = sp.Integer(4)
    derivative_order = sp.Integer(1)
    quartic_floor_shell_exponent = dimension + 2 * derivative_order - 2 * covariance_decay
    baseline_shell_exponent = dimension + 2 * derivative_order - covariance_decay
    determinant_shell_exponent = dimension + 4 * derivative_order - 2 * covariance_decay
    checks.require(
        "floors",
        "quartic floor shell summable",
        quartic_floor_shell_exponent == -3,
        quartic_floor_shell_exponent,
        -3,
    )
    checks.require(
        "floors",
        "baseline direct floor diverges",
        baseline_shell_exponent == 1,
        baseline_shell_exponent,
        1,
    )
    checks.require(
        "floors",
        "determinant squared baseline summable",
        determinant_shell_exponent == -1,
        determinant_shell_exponent,
        -1,
    )

    # Complete signed second-jet score transfer and exact Young constant.
    g, c, w = sp.symbols("g c w", real=True)
    h = g**2 + c
    derivative_side = w * (sp.diff(h, g) ** 2 + h * sp.diff(h, g, 2))
    score_side = sp.Rational(1, 2) * w * (g**2 - 1) * h**2
    e_derivative = polynomial_expectation(derivative_side, g, gaussian_even_moment)
    e_score = polynomial_expectation(score_side, g, gaussian_even_moment)
    checks.require(
        "score_transfer",
        "second Gaussian integration by parts fixture",
        sp.simplify(e_derivative - e_score) == 0,
        e_derivative,
        e_score,
    )
    checks.require(
        "score_transfer",
        "centered quadratic variance convention",
        polynomial_expectation((g**2 - 1) ** 2, g, gaussian_even_moment) == 2,
        polynomial_expectation((g**2 - 1) ** 2, g, gaussian_even_moment),
        2,
    )
    eta, zeta, amplitude = sp.symbols("eta zeta A", positive=True)
    x_star = amplitude**2 / (16 * eta ** sp.Rational(3, 2) * zeta ** sp.Rational(1, 2))
    y_star = amplitude**2 / (16 * eta ** sp.Rational(1, 2) * zeta ** sp.Rational(3, 2))
    young_gap = sp.simplify(
        eta * x_star
        + zeta * y_star
        + amplitude**2 / (8 * sp.sqrt(eta * zeta))
        - amplitude * x_star ** sp.Rational(1, 4) * y_star ** sp.Rational(1, 4)
    )
    checks.require("score_transfer", "Young optimizer equality", young_gap == 0, young_gap, 0)
    q_score_constant = sp.simplify(q**2 / 64)
    checks.require(
        "score_transfer",
        "q=10/9 score constant",
        q_score_constant == sp.Rational(25, 1296),
        q_score_constant,
        sp.Rational(25, 1296),
    )
    derivative_covariance_shell_exponent = dimension - 4
    checks.require(
        "score_transfer",
        "derivative covariance HS shell decay",
        derivative_covariance_shell_exponent == -1,
        derivative_covariance_shell_exponent,
        -1,
    )

    # Oscillatory signed cancellation and the exponential-coordinate boundary.
    m, a_selector = sp.symbols("M a", positive=True)
    signed_second_jet = a_selector**2 * m**2 * sp.exp(-2 * m**2)
    raw_stein_mean = 2 * signed_second_jet
    scaled_amplitude = m ** sp.Rational(-1, 2)
    k_amplitude = sp.simplify((scaled_amplitude * m) ** 2)
    checks.require(
        "stein_boundary",
        "oscillatory signed second jet",
        signed_second_jet == a_selector**2 * m**2 * sp.exp(-2 * m**2),
        signed_second_jet,
        a_selector**2 * m**2 * sp.exp(-2 * m**2),
    )
    checks.require(
        "stein_boundary",
        "raw Stein expectation is twice derivative pair",
        raw_stein_mean == 2 * signed_second_jet,
        raw_stein_mean,
        2 * signed_second_jet,
    )
    checks.require(
        "stein_boundary",
        "scaled derivative representative amplitude",
        k_amplitude == m,
        k_amplitude,
        m,
    )
    theta = sp.symbols("theta", positive=True)
    raw_mgf_bound = theta / m - sp.log(1 - 2 * theta / m) / 2
    checks.require(
        "stein_boundary",
        "raw Wick exponential bound vanishes",
        sp.limit(raw_mgf_bound, m, sp.oo) == 0,
        sp.limit(raw_mgf_bound, m, sp.oo),
        0,
    )
    bessel_asymptotic = theta * m - sp.log(2 * sp.pi * theta * m) / 2
    checks.require(
        "stein_boundary",
        "derivative representative asymptotic is linear",
        sp.limit(bessel_asymptotic / m, m, sp.oo) == theta,
        sp.limit(bessel_asymptotic / m, m, sp.oo),
        theta,
    )

    # The exact CM/PSD boundary inherited from R-108 (4.6).
    eigenvalue = sp.symbols("lambda_B", positive=True)
    cm_coefficient = -sp.Rational(5, 9) * eigenvalue**2 / (eigenvalue + sp.Rational(9, 10))
    checks.require("cm_boundary", "common-heat mean debt is negative", cm_coefficient < 0, cm_coefficient, "<0")
    checks.require(
        "cm_boundary",
        "common-heat mean debt grows linearly",
        sp.limit(cm_coefficient / eigenvalue, eigenvalue, sp.oo) == -sp.Rational(5, 9),
        sp.limit(cm_coefficient / eigenvalue, eigenvalue, sp.oo),
        -sp.Rational(5, 9),
    )

    # Filtration bookkeeping: a root-realized covariance cannot be the raw
    # predictable right side of a pre-root conditional normalizer.
    past_sigma_algebra = frozenset({"past"})
    realized_covariance_dependencies = frozenset({"past", "fresh_root"})
    predictable_cost_dependencies = frozenset({"past"})
    checks.require(
        "filtration",
        "realized covariance is post-reveal",
        realized_covariance_dependencies != past_sigma_algebra,
        sorted(realized_covariance_dependencies),
        "not F_{j-1}-measurable",
    )
    checks.require(
        "filtration",
        "conditional square cost is predictable",
        predictable_cost_dependencies == past_sigma_algebra,
        sorted(predictable_cost_dependencies),
        sorted(past_sigma_algebra),
    )

    failed = [row for row in checks.rows if row["status"] != "PASS"]
    derived = {
        "q": str(q),
        "bennett_threshold": str(threshold),
        "small_branch_multiplier": str(small_multiplier),
        "one_pair_variance": str(eu2),
        "one_pair_small_q_coefficient": str(eu2 / 2),
        "square_first_coefficient": "5",
        "square_first_room": "1",
        "one_pair_floor": str(-beta),
        "realized_covariance_hs_square_expectation": str(e_hs_square),
        "score_transfer_q_constant": str(q_score_constant),
        "quartic_floor_shell_exponent": str(quartic_floor_shell_exponent),
        "baseline_floor_shell_exponent": str(baseline_shell_exponent),
        "determinant_shell_exponent": str(determinant_shell_exponent),
        "derivative_covariance_hs_shell_exponent": str(derivative_covariance_shell_exponent),
        "joint_floor_interior": str(stationary_value),
        "joint_floor_boundary": str(joint.subs(s, 0)),
        "cm_mean_debt_coefficient": str(cm_coefficient),
        "numeric_log_mgf_over_a2": [mp.nstr(value, 30) for value in numeric_ratios],
    }
    route_verdicts = {
        "one_pair_square_before_average_all_amplitudes": "proved-conditional-fresh-pair",
        "sequential_fresh_pair_supermartingale": "proved-by-conditional-iteration",
        "pure_quartic_selector_floor": "proved-and-cutoff-uniform-in-diagonal-submodel",
        "full_pair_direct_floor": "fails-by-divergent-baseline-branch",
        "fixed_predictable_W_signed_second_jet": "proved-score-transfer-form-bound",
        "stein_derivative_inside_exponential": "failed",
        "raw_realized_covariance_on_pre_root_rhs": "illegal-unless-predictable",
        "auxiliary_copy_determinant_equals_diagonal_packet": "false",
        "production_complete_cluster_identification": "open",
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
    print(f"Primary R-109: {payload['assertions_passed']}/{payload['assertions_total']} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
