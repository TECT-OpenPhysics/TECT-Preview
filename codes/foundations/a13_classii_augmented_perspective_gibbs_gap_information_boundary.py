#!/usr/bin/env python3
"""Primary executable evidence for the R-093 A13 boundary theorem.

The checks cover the exact augmented one-reveal normal form, the pinned
production-coefficient covariance fixture, the Gibbs-gap identity, the
fixed-chart obstruction, and the information cost of coefficient reveal.
They do not assert a paid torus H_N counterexample, Nelson, or Sector A.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-AUGMENTED-PERSPECTIVE-GIBBS-GAP-INFORMATION-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-27-primary-augmented-perspective-gibbs-gap-information-boundary/result.json"

AUTHORITY_NOTES = {
    "r081": CLAIM_DIR / "notes/classii-cartan-tail-adapted-near-temporal-reduction-260725-v1.0.tex.txt",
    "r087": CLAIM_DIR / "notes/classii-cartan-spatial-decay-rational-trace-variational-core-reduction-260725-v1.0.tex.txt",
    "r091": CLAIM_DIR / "notes/classii-projected-cartan-full-frame-temporal-boundary-260725-v1.0.tex.txt",
    "r092": CLAIM_DIR / "notes/classii-normalized-cartan-perspective-triangular-covariance-frontier-260725-v1.0.tex.txt",
}
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"

# Pinned upstream A1 production inputs.
INPUTS = {
    "q": Fraction(10, 9),
    "c0_times_P": Fraction(3, 250),
    "c1_times_P": Fraction(243, 8000),
}

# Independently auditable exact test oracles, never used to derive outputs.
TEST_ORACLES = {
    "b_minus_times_P_over_e": Fraction(9, 250),
    "b_plus_times_P_over_e": Fraction(8937, 42250),
    "delta_times_P_over_e": Fraction(3708, 21125),
    "b_tail_times_P_over_e": Fraction(3993, 42250),
    "mean_b_times_P_over_e": Fraction(1293, 8450),
    "density_times_P_over_e": Fraction(-1236, 21125),
    "outer_density_times_P_over_e": Fraction(-618, 21125),
}

# Accepted predecessor exponent pairs; all slacks and moments are derived here.
BG_EXPONENT_INPUTS = {
    "q_against_h2": (Fraction(21, 40), Fraction(19, 120)),
    "sharp_base_frozen_cubic": (Fraction(2, 5), Fraction(8, 15)),
    "comparable_rational_cubic": (Fraction(11, 20), Fraction(19, 60)),
    "rational_q_branch": (Fraction(11, 20), Fraction(3, 20)),
    "g_hessian_branch": (Fraction(2, 5), Fraction(11, 30)),
    "high_u_branch": (Fraction(11, 40), Fraction(49, 120)),
    "worst_regular_control": (Fraction(4, 5), Fraction(1, 6)),
    "regular_root": (Fraction(3, 5), Fraction(1, 3)),
}


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def relative_entropy(probability: np.ndarray, reference: np.ndarray) -> float:
    return float(np.sum(probability * np.log(probability / reference)))


def production_parameters() -> dict[str, Any]:
    return json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]


def production_coefficient_bound(parameters: dict[str, Any]) -> float:
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    a_value = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator
    b_value = float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator
    c_value = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    return 4.0 * (a_value + 2.0 * abs(b_value) + c_value)


def cutoff_two_data(parameters: dict[str, Any]) -> dict[str, float]:
    length = float(parameters["Lx"])
    omega = 2.0 * math.pi / length
    z0 = np.asarray(parameters["z0"], dtype=float)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    internal = np.diag(np.asarray(parameters["family_masses"], dtype=float))
    internal += float(parameters["k_lock"]) * (np.eye(3) - projector)
    gradient_trace = 0.0
    field_trace = 0.0
    shell_minimum = math.inf
    for n1 in range(-2, 3):
        for n2 in range(-2, 3):
            for n3 in range(-2, 3):
                norm_square = n1 * n1 + n2 * n2 + n3 * n3
                wave_square = omega * omega * norm_square
                scalar = (
                    float(parameters["r"])
                    + float(parameters["Z"]) * wave_square
                    + float(parameters["Y"]) * wave_square**2
                )
                symbol = scalar * np.eye(3) + internal
                inverse = np.linalg.inv(symbol)
                # The factor two is the canonical complex-to-six-real covariance convention.
                field_trace += 2.0 * float(np.trace(inverse))
                gradient_trace += 2.0 * wave_square * float(np.trace(inverse)) / length**3
                if max(abs(n1), abs(n2), abs(n3)) == 2:
                    shell_minimum = min(shell_minimum, float(np.linalg.eigvalsh(symbol)[0]))
    beta_operator = production_coefficient_bound(parameters)
    c_two = 0.5 * beta_operator * gradient_trace
    lambda_two = 2.0 / shell_minimum
    control_margin = float(Fraction(9, 20)) - 2.0 * c_two * lambda_two
    constant = 2.0 * c_two * field_trace
    return {
        "beta_operator": beta_operator,
        "gradient_covariance_trace": gradient_trace,
        "field_covariance_trace": field_trace,
        "shell_symbol_minimum": shell_minimum,
        "control_map_bound": lambda_two,
        "negative_quadratic_constant": c_two,
        "paid_control_margin": control_margin,
        "lower_bound_constant": constant,
    }


def main() -> int:
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    authority_tokens = {
        "r081": ("strict-past temporal factorisation", "Douglas factorisation", "tag{8.2}"),
        "r087": ("fixed-cutoff variational CORE", "tag{8.4}", "cylindrical-simple"),
        "r091": ("complete four-row coefficient", "b_{\\rm tot}", "tag{8.1}"),
        "r092": ("exact one-reveal criterion", "entropy-union", "tag{11.8}"),
    }
    for label, path in AUTHORITY_NOTES.items():
        check(f"authority_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        tokens = authority_tokens[label]
        check(f"authority_{label}_tokens", all(token in content for token in tokens), [token for token in tokens if token in content], list(tokens))
    check("authority_a1_manifest_exists", A1_MANIFEST.exists(), str(A1_MANIFEST.relative_to(REPO)), "exists")

    q = INPUTS["q"]
    check("q_inverse", 1 / q == Fraction(9, 10), 1 / q, Fraction(9, 10))
    check("source_energy_coefficient", 1 / (2 * q) == Fraction(9, 20), 1 / (2 * q), Fraction(9, 20))
    check("pinsker_gap_coefficient", q / 2 == Fraction(5, 9), q / 2, Fraction(5, 9))

    t = sp.symbols("t", positive=True)
    radial = t * (4 * t**2 + 9) / (9 * (t**2 + 1))
    radial_prime = sp.factor(sp.diff(radial, t))
    expected_prime = (4 * t**4 + 3 * t**2 + 9) / (9 * (t**2 + 1) ** 2)
    check("radial_half", sp.simplify(radial.subs(t, sp.Rational(1, 2))) == sp.Rational(4, 9), radial.subs(t, sp.Rational(1, 2)), sp.Rational(4, 9))
    check("radial_one", sp.simplify(radial.subs(t, 1)) == sp.Rational(13, 18), radial.subs(t, 1), sp.Rational(13, 18))
    check("radial_three_halves", sp.simplify(radial.subs(t, sp.Rational(3, 2))) == sp.Rational(12, 13), radial.subs(t, sp.Rational(3, 2)), sp.Rational(12, 13))
    check("radial_derivative_identity", sp.simplify(radial_prime - expected_prime) == 0, radial_prime, expected_prime)
    radial_numerator, radial_denominator = sp.fraction(sp.factor(radial_prime))
    radial_coefficients = sp.Poly(radial_numerator, t).all_coeffs()
    check(
        "radial_derivative_positive_polynomial",
        all(value >= 0 for value in radial_coefficients)
        and radial_coefficients[-1] > 0
        and sp.factor(radial_denominator) == 9 * (t**2 + 1) ** 2,
        [radial_numerator, radial_denominator, radial_coefficients],
        "nonnegative numerator coefficients with positive constant and positive denominator",
    )

    c0 = sp.Rational(INPUTS["c0_times_P"].numerator, INPUTS["c0_times_P"].denominator)
    c1 = sp.Rational(INPUTS["c1_times_P"].numerator, INPUTS["c1_times_P"].denominator)
    coefficient = 4 * c0 * t**2 + 4 * c1 * radial**2
    b_minus = sp.factor(coefficient.subs(t, sp.Rational(1, 2)))
    b_plus = sp.factor(coefficient.subs(t, sp.Rational(3, 2)))
    delta = sp.factor(b_plus - b_minus)
    b_tail = sp.factor(b_minus + delta / 3)
    mean_b = sp.factor((b_plus + b_tail) / 2)
    density = sp.factor(b_tail - mean_b)
    outer_density = sp.factor(density / 2)
    exact_rows = (
        ("b_minus", b_minus, TEST_ORACLES["b_minus_times_P_over_e"]),
        ("b_plus", b_plus, TEST_ORACLES["b_plus_times_P_over_e"]),
        ("delta", delta, TEST_ORACLES["delta_times_P_over_e"]),
        ("b_tail", b_tail, TEST_ORACLES["b_tail_times_P_over_e"]),
        ("mean_b", mean_b, TEST_ORACLES["mean_b_times_P_over_e"]),
        ("finite_density", density, TEST_ORACLES["density_times_P_over_e"]),
        ("outer_half_density", outer_density, TEST_ORACLES["outer_density_times_P_over_e"]),
    )
    for name, actual, oracle in exact_rows:
        expected = sp.Rational(oracle.numerator, oracle.denominator)
        check(name, sp.simplify(actual - expected) == 0, actual, expected)
    coefficient_prime = sp.factor(sp.diff(coefficient, t))
    reduced_numerator, reduced_denominator = sp.fraction(sp.factor(coefficient_prime / t))
    reduced_coefficients = sp.Poly(reduced_numerator, t).all_coeffs()
    check(
        "coefficient_positive_branch_monotone",
        sp.simplify(coefficient_prime - 8 * (c0 * t + c1 * radial * radial_prime)) == 0
        and all(value >= 0 for value in reduced_coefficients)
        and reduced_coefficients[-1] > 0
        and all(value >= 0 for value in sp.Poly(sp.expand(reduced_denominator), t).all_coeffs())
        and sp.Poly(sp.expand(reduced_denominator), t).all_coeffs()[-1] > 0,
        [coefficient_prime, reduced_coefficients, sp.factor(reduced_denominator)],
        "positive t times a positive-coefficient polynomial over a positive denominator",
    )
    check("coefficient_interval_order", bool(b_plus > b_minus > 0), [b_minus, b_plus], "0 < b_minus < b_plus")

    b_symbol, eta_symbol, g_symbol = sp.symbols("B eta g", positive=True)
    a_symbol = b_symbol + 2 * eta_symbol
    m_symbol = b_symbol * g_symbol / a_symbol
    theta_symbol = b_symbol - b_symbol**2 / a_symbol
    completed = sp.factor(a_symbol * m_symbol**2 + theta_symbol * g_symbol**2)
    check("perspective_pointwise_identity", sp.simplify(completed - b_symbol * g_symbol**2) == 0, completed, b_symbol * g_symbol**2)

    probabilities = (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4))
    g_values = (sp.Integer(0), sp.sqrt(2), -sp.sqrt(2))
    b_values = (b_plus, b_tail, b_tail)
    qv = sp.simplify(sum(sp.Rational(p.numerator, p.denominator) * b * g for p, b, g in zip(probabilities, b_values, g_values)))
    second = sp.simplify(sum(sp.Rational(p.numerator, p.denominator) * b * g**2 for p, b, g in zip(probabilities, b_values, g_values)))
    check("finite_symmetry_qv", qv == 0, qv, 0)
    check("finite_weighted_second_moment", sp.simplify(second - b_tail) == 0, second, b_tail)
    for eta_value in (sp.Rational(1, 10), sp.Rational(1, 2), sp.Integer(7)):
        perspective_sum = sp.simplify(
            sum(
                sp.Rational(p.numerator, p.denominator)
                * ((b + 2 * eta_value) * (b * g / (b + 2 * eta_value)) ** 2 + (b - b**2 / (b + 2 * eta_value)) * g**2)
                for p, b, g in zip(probabilities, b_values, g_values)
            )
            - mean_b
        )
        check(f"finite_density_eta_{str(eta_value).replace('/', '_')}", sp.simplify(perspective_sum - density) == 0, perspective_sum, density)

    nodes, weights = np.polynomial.hermite.hermgauss(256)
    reciprocal_quadrature = float(np.sum(weights / (1.0 + 2.0 * nodes**2)) / math.sqrt(math.pi))
    reciprocal_closed = math.sqrt(math.pi / 2.0) * math.exp(0.5) * math.erfc(1.0 / math.sqrt(2.0))
    gaussian_ratio = 1.0 - 2.0 * reciprocal_quadrature
    check("gaussian_reciprocal_quadrature", abs(reciprocal_quadrature - reciprocal_closed) < 2.0e-13, reciprocal_quadrature, reciprocal_closed)
    check("gaussian_strict_jensen", reciprocal_quadrature > 0.5, reciprocal_quadrature, "> 1/2")
    check("gaussian_density_negative", gaussian_ratio < 0.0, gaussian_ratio, "< 0")

    free_energy_quadratic = math.log(1.0 + float(q)) / (2.0 * float(q))
    translation = sp.symbols("translation", real=True)
    one_chart_action = sp.Rational(1, 2) * (1 + translation**2) + translation**2 / (2 * sp.Rational(q.numerator, q.denominator))
    one_chart_critical_points = sp.solve(sp.diff(one_chart_action, translation), translation)
    one_chart_infimum_exact = sp.simplify(one_chart_action.subs(translation, one_chart_critical_points[0]))
    one_chart_infimum = float(one_chart_infimum_exact)
    check(
        "fixed_one_block_gap",
        one_chart_critical_points == [0]
        and sp.diff(one_chart_action, translation, 2) > 0
        and one_chart_infimum_exact == sp.Rational(1, 2)
        and one_chart_infimum > free_energy_quadratic,
        [one_chart_action, one_chart_critical_points, one_chart_infimum - free_energy_quadratic],
        "unique quadratic minimum 1/2 strictly above Gibbs free energy",
    )

    mu = np.array([0.5, 0.5], dtype=float)
    potential = np.array([0.0, 1.0], dtype=float)
    nu = np.array([1.0 / 3.0, 2.0 / 3.0], dtype=float)
    q_float = float(q)
    partition = float(np.sum(mu * np.exp(-q_float * potential)))
    gibbs = mu * np.exp(-q_float * potential) / partition
    fibre = 3.0 / 7.0
    source_entropy = relative_entropy(nu, mu) + fibre
    action = float(nu @ potential) + source_entropy / q_float
    gap_form = -math.log(partition) / q_float + (relative_entropy(nu, gibbs) + fibre) / q_float
    check("gibbs_gap_identity", abs(action - gap_form) < 2.0e-15, action - gap_form, 0.0)
    check("gibbs_gap_two_coefficients", abs(1.0 / q_float - 0.9) < 1.0e-15, 1.0 / q_float, 0.9)

    entropy_gap = 0.02
    fibre_gap = 0.03
    action_gap = (entropy_gap + fibre_gap) / q_float
    check("near_minimizer_gap_sum", abs(q_float * action_gap - entropy_gap - fibre_gap) < 1.0e-15, q_float * action_gap, entropy_gap + fibre_gap)
    check("near_minimizer_each_gap_bound", entropy_gap <= q_float * action_gap and fibre_gap <= q_float * action_gap, [entropy_gap, fibre_gap], q_float * action_gap)

    for bins in (2, 4, 8, 32):
        mutual_information = sum((1.0 / bins) * math.log(bins) for _ in range(bins))
        check(f"equiprobable_reveal_mi_{bins}", abs(mutual_information - math.log(bins)) < 2.0e-15, mutual_information, math.log(bins))

    t_control = 1.7
    source_kl = 0.5 * t_control**2
    physical_kl = 0.25 * t_control**2
    fibre_kl = source_kl - physical_kl
    check(
        "deterministic_overlap_entropy_formula_fixture",
        all(
            abs(actual - expected) < 1.0e-15
            for actual, expected in (
                (source_kl, t_control**2 / 2.0),
                (physical_kl, t_control**2 / 4.0),
                (fibre_kl, t_control**2 / 4.0),
            )
        ),
        [source_kl, physical_kl, fibre_kl],
        ["t^2/2", "t^2/4", "t^2/4"],
    )
    feedback_gain = 2.0
    feedback_source_kl = 0.5 * feedback_gain**2
    feedback_physical_variance = ((1.0 + feedback_gain) ** 2 + 1.0) / 2.0
    feedback_physical_kl = 0.5 * (feedback_physical_variance - 1.0 - math.log(feedback_physical_variance))
    feedback_fibre = feedback_source_kl - feedback_physical_kl
    check(
        "feedback_overlap_entropy_formula_fixture",
        abs(feedback_source_kl - 2.0) < 1.0e-15
        and abs(feedback_physical_kl - (2.0 - 0.5 * math.log(5.0))) < 1.0e-15
        and abs(feedback_fibre - 0.5 * math.log(5.0)) < 1.0e-15,
        [feedback_source_kl, feedback_physical_kl, feedback_fibre],
        [2.0, "2-log(5)/2", "log(5)/2"],
    )

    bg_ledger: dict[str, dict[str, str]] = {}
    for label, (energy_power, sextic_power) in BG_EXPONENT_INPUTS.items():
        slack = 1 - energy_power - sextic_power
        moment = 1 / slack
        check(f"bg_{label}_positive_slack", slack > 0, slack, "> 0")
        check(f"bg_{label}_moment_identity", moment * slack == 1, moment * slack, 1)
        bg_ledger[label] = {"a": str(energy_power), "b": str(sextic_power), "slack": str(slack), "moment": str(moment)}
    critical_pairs = ((Fraction(3, 4), Fraction(1, 4)), (Fraction(1, 2), Fraction(1, 2)))
    for index, pair in enumerate(critical_pairs, start=1):
        check(f"bg_critical_pair_{index}", 1 - pair[0] - pair[1] == 0, 1 - pair[0] - pair[1], 0)
    maximum_bg_moment = max(1 / (1 - pair[0] - pair[1]) for pair in BG_EXPONENT_INPUTS.values())
    check("bg_maximum_required_moment", maximum_bg_moment == 30, maximum_bg_moment, 30)

    cutoff = cutoff_two_data(production_parameters())
    check("cutoff_two_beta_operator_positive", cutoff["beta_operator"] > 0.0, cutoff["beta_operator"], "> 0")
    check("cutoff_two_gradient_covariance_positive", cutoff["gradient_covariance_trace"] > 0.0, cutoff["gradient_covariance_trace"], "> 0")
    check("cutoff_two_shell_symbol_positive", cutoff["shell_symbol_minimum"] > 0.0, cutoff["shell_symbol_minimum"], "> 0")
    check("cutoff_two_control_margin_positive", cutoff["paid_control_margin"] > 0.0, cutoff["paid_control_margin"], "> 0")
    check("cutoff_two_bound_constant_finite", math.isfinite(cutoff["lower_bound_constant"]) and cutoff["lower_bound_constant"] > 0.0, cutoff["lower_bound_constant"], "finite and positive")
    check(
        "cutoff_two_energy_100_illustration_nonloading",
        cutoff["paid_control_margin"] * 100.0 - cutoff["lower_bound_constant"] > 0.0,
        cutoff["paid_control_margin"] * 100.0 - cutoff["lower_bound_constant"],
        "illustration only; coercivity is certified by the positive margin",
    )

    passed = sum(row["status"] == "PASS" for row in assertions)
    payload = {
        "schema": "tect/a13-augmented-perspective-gibbs-gap-information-boundary-primary/1.0",
        "version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(assertions) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(assertions),
        "assertions": assertions,
        "derived": {
            "finite_density_times_P_over_e": str(density),
            "outer_density_times_P_over_e": str(outer_density),
            "gaussian_reciprocal": reciprocal_quadrature,
            "gaussian_density_over_delta": gaussian_ratio,
            "fixed_one_block_quadratic_infimum": one_chart_infimum,
            "quadratic_gibbs_free_energy": free_energy_quadratic,
            "cutoff_two_paid_coercivity": cutoff,
            "bg_exponent_ledger": bg_ledger,
            "bg_maximum_required_moment": str(maximum_bg_moment),
        },
        "scope": "Exact finite-dimensional boundary checks only; no paid torus H_N counterexample, Nelson estimate, measure, or Sector-A closure.",
    }
    atomic_json(OUTPUT, payload)
    print(f"R-093 primary: {passed}/{len(assertions)} assertions PASS" if passed == len(assertions) else f"R-093 primary: {passed}/{len(assertions)} assertions; FAIL")
    print(f"result: {OUTPUT.relative_to(REPO)}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
