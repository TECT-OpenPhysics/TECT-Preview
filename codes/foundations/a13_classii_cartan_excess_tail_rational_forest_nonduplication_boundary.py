#!/usr/bin/env python3
"""Primary executable evidence for the R-090 A13 boundary theorem.

The analytic companion proves that the global Sobolev coefficient ledger
proposed in R-089 (3.12) counts a root-diagonal first Gaussian chaos once per
root and therefore grows linearly with the cutoff for every s>0.  The actual
far projection removes that diagonal, so this is a no-go for the global
Sobolev extraction, not for controlled Cartan CFAR.  The companion also
compresses the two Cartan coefficients to one conservative secant, records
the exact excess-tail replacement, corrects R-089's conditional-covariance
attribution, and enforces the R-063 forest nonduplication rule.

This program checks exact algebra and scale arithmetic.  Finite shell sums
are diagnostics for the proved q^-4 asymptotic, not substitutes for it.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

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
RESULT_ID = "A13-CLASSII-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER-NOGO-RATIONAL-FOREST-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
R063_NOTE = CLAIM_DIR / "notes/classii-balanced-coefficient-jet-continuum-and-a7-reconstruction-260722-v1.0.tex.txt"
R079_NOTE = CLAIM_DIR / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt"
R087_NOTE = CLAIM_DIR / "notes/classii-cartan-spatial-decay-rational-trace-variational-core-reduction-260725-v1.0.tex.txt"
R089_NOTE = CLAIM_DIR / "notes/classii-progressive-covariance-compression-rational-mean-spectral-boundary-260725-v1.0.tex.txt"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-cartan-excess-tail-rational-forest-nonduplication/result.json"


# Upstream inputs and declared diagnostic parameters.
INPUTS = {
    "scalar_floor": Fraction(1, 1),
    "scalar_base": Fraction(1, 1),
    "scalar_shift": Fraction(1, 2),
    "dimension": 3,
    "covariance_order": 4,
    "r084_prefactor": Fraction(3, 40),
    "lp_upper_coordinate_factor": 2,
    "principal_excess": 5,
    "test_gap": 10,
    "shell_levels": (2, 3, 4, 5),
    "sobolev_exponents": (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(5, 4)),
    "nelson_q": Fraction(10, 9),
    "comparison_p": Fraction(11, 10),
    "control_charge": Fraction(9, 20),
    "sextic_capacity": Fraction(27, 100),
    "sextic_delta": Fraction(6, 100),
    "sextic_packet": Fraction(15, 100),
}

# Clearly labelled test oracles, never proof inputs.
TEST_ORACLES = {
    "secant_derivative": Fraction(20, 169),
    "ou_first_chaos_integral": Fraction(1, 4),
    "forest_h2_coefficient": 5,
    "forest_h0_coefficient": 2,
    "raw_endpoint_factor": Fraction(-35840, 13689),
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
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


def shell_sum(level: int, exponent: float) -> float:
    """q^-4 sharp-cube diagnostic with one fixed Fourier shift."""
    radius = 2**level
    axis = np.arange(-radius, radius + 1, dtype=float)
    x0, x1, x2 = np.meshgrid(axis, axis, axis, indexing="ij")
    points = np.stack((x0.ravel(), x1.ravel(), x2.ravel()), axis=1)
    maximum = np.max(np.abs(points), axis=1)
    points = points[(maximum > radius / 2) & (maximum <= radius)]
    input_norm = np.linalg.norm(points, axis=1)
    shifted = points + np.asarray([1.0, 0.0, 0.0])
    output_norm = np.linalg.norm(shifted, axis=1)
    raw = float(np.sum(input_norm ** (-INPUTS["covariance_order"]) * output_norm ** (2 * exponent)))
    return raw * 2.0 ** ((1.0 - 2.0 * exponent) * level)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    # 1. Authority tokens prevent a detached reinterpretation of forest or
    # complete-packet bookkeeping.
    r063_text = R063_NOTE.read_text(encoding="utf-8")
    r079_text = R079_NOTE.read_text(encoding="utf-8")
    r087_text = R087_NOTE.read_text(encoding="utf-8")
    r089_text = R089_NOTE.read_text(encoding="utf-8")
    check("r063_reconstruction_authority", "Formula (5.5) is an" in r063_text and "identity, not an asymptotic expansion" in r063_text, True, True)
    check("r063_lower_chaos_authority", "Complete lower-chaos conversion" in r063_text, True, True)
    check("r079_full_packet_authority", "Theorem 3.1 (full-current identity)" in r079_text, True, True)
    check("r079_forest_reassembly_authority", "forest after reassembly" in r079_text, True, True)
    check("r087_principal_support_authority", "Principal contribution lies in" in r087_text or "principal contribution lies in" in r087_text, True, True)
    check("r089_global_ledger_authority", "mathfrak E_s" in r089_text and "tag{3.12}" in r089_text, True, True)
    check("r089_placeholder_forest_authority", "complete backward-heat and lower-chaos forest" in r089_text, True, True)

    # 2. b=grad c is an identity.  A nontrivial scalar production slice is
    # used only to make the chain rule executable.
    x = sp.symbols("x", real=True)
    base_field = x
    control_field = x**2 / 3
    scalar_map = lambda value: value**3 / (1 + value**2)
    coefficient = sp.factor(scalar_map(base_field + control_field) - scalar_map(base_field))
    b_formula = (
        (sp.diff(scalar_map(sp.Symbol("z")), sp.Symbol("z")).subs(sp.Symbol("z"), base_field + control_field)
         - sp.diff(scalar_map(sp.Symbol("z")), sp.Symbol("z")).subs(sp.Symbol("z"), base_field))
        * sp.diff(base_field, x)
        + sp.diff(scalar_map(sp.Symbol("z")), sp.Symbol("z")).subs(sp.Symbol("z"), base_field + control_field)
        * sp.diff(control_field, x)
    )
    gradient_residual = sp.factor(sp.cancel(sp.together(sp.diff(coefficient, x) - b_formula)))
    check("cartan_b_equals_gradient_c", gradient_residual == 0, gradient_residual, 0)

    z = sp.symbols("z", real=True)
    f = z**3 / (1 + z**2)
    fp = sp.diff(f, z)
    base = sp.Rational(INPUTS["scalar_base"].numerator, INPUTS["scalar_base"].denominator)
    shift = sp.Rational(INPUTS["scalar_shift"].numerator, INPUTS["scalar_shift"].denominator)
    derivative_secant = sp.factor(fp.subs(z, base + shift) - fp.subs(z, base))
    check("production_scalar_derivative_secant", derivative_secant == sp.Rational(20, 169), derivative_secant, TEST_ORACLES["secant_derivative"])
    check("production_scalar_map_nonaffine", sp.diff(f, z, 2) != 0, sp.factor(sp.diff(f, z, 2)), "nonzero")
    hessian_at_one = sp.factor(sp.diff(f, z, 2).subs(z, 1))
    check("production_scalar_hessian_at_one", hessian_at_one == sp.Rational(1, 2), hessian_at_one, sp.Rational(1, 2))

    # The apparently separate value and derivative coefficients recombine
    # before any estimate.  With k=q-p, b_hat_i=i*k_i*c_hat, so the current
    # multiplier is i*(k_i+p_i)=i*q_i.  This is the exact one-coefficient
    # conservative trace identity used by the analytic proof.
    p_symbols = sp.symbols("p0:3", real=True)
    q_symbols = sp.symbols("q0:3", real=True)
    c_hat = sp.symbols("c_hat", real=True)
    compressed = [
        sp.simplify(sp.I * (q_symbols[index] - p_symbols[index]) * c_hat + sp.I * p_symbols[index] * c_hat)
        for index in range(3)
    ]
    expected_compressed = [sp.I * q_symbols[index] * c_hat for index in range(3)]
    check("cartan_fourier_single_coefficient_compression", compressed == expected_compressed, compressed, expected_compressed)
    compressed_square = sp.simplify(sum(sp.expand_complex(value * sp.conjugate(value)) for value in compressed))
    expected_square = sp.simplify(c_hat**2 * sum(value**2 for value in q_symbols))
    check("cartan_fourier_trace_is_q_squared_c_squared", sp.simplify(compressed_square - expected_square) == 0, compressed_square, expected_square)
    max_norm_square_factor = INPUTS["dimension"] * INPUTS["lp_upper_coordinate_factor"] ** 2
    max_norm_shell_constant = INPUTS["r084_prefactor"] * max_norm_square_factor
    check("cartan_conservative_shell_prefactor", max_norm_shell_constant == Fraction(9, 10), max_norm_shell_constant, Fraction(9, 10))

    # 3. The q^-4 root-diagonal scale is critical for every s.  The analytic
    # exponent cancellation is exact; finite sharp-cube sums are convergence
    # diagnostics with deliberately loose tooling thresholds.
    dimension = Fraction(INPUTS["dimension"], 1)
    covariance_order = Fraction(INPUTS["covariance_order"], 1)
    normalized_shells: dict[str, list[float]] = {}
    for exponent in INPUTS["sobolev_exponents"]:
        scale_power = Fraction(1, 1) - 2 * exponent + dimension - covariance_order + 2 * exponent
        check(f"critical_scale_power_s_{exponent}", scale_power == 0, scale_power, 0)
        values = [shell_sum(level, float(exponent)) for level in INPUTS["shell_levels"]]
        normalized_shells[str(exponent)] = values
        check(f"shell_normalization_positive_s_{exponent}", min(values) > 1.0, min(values), ">1 diagnostic threshold")
        consecutive = [values[index + 1] / values[index] for index in range(len(values) - 1)]
        check(f"shell_normalization_stable_s_{exponent}", min(consecutive) > 0.5 and max(consecutive) < 2.0, consecutive, "all in (0.5,2)")
        roots = 17
        exact_per_root = 2.0 ** float(scale_power)
        cumulative = sum(exact_per_root for _ in range(roots))
        check(f"linear_root_accumulation_s_{exponent}", math.isclose(cumulative, float(roots), rel_tol=0, abs_tol=1e-12), cumulative, roots)

    outer_decay = Fraction(2, 1)
    first_chaos_decay = Fraction(2, 1)
    ou_integral = 1 / (outer_decay + first_chaos_decay)
    check("ou_first_chaos_integral", ou_integral == Fraction(1, 4), ou_integral, TEST_ORACLES["ou_first_chaos_integral"])

    # The q^-4 shell exponent is geometrically summable.  This normalized
    # template omits the production covariance constant and is not itself a
    # numerical point-variance bound.
    geometric_shell_tail = sum(Fraction(1, 2**level) for level in range(1, 40))
    check("q4_geometric_shell_tail_summable", geometric_shell_tail < 1, geometric_shell_tail, "<1 normalized exponent template")

    # 4. Correct excess-tail extraction.  Starting five shells above the
    # root removes the diagonal; a later far gap gains 2^(-2s(C-7)).
    rng = np.random.default_rng(90025)
    principal_excess = INPUTS["principal_excess"]
    far_gap = INPUTS["test_gap"]
    for exponent in (Fraction(1, 4), Fraction(7, 12), Fraction(3, 4)):
        blocks = {offset: float(rng.uniform(0.05, 2.0)) for offset in range(principal_excess, 20)}
        weighted = sum(2.0 ** (2.0 * float(exponent) * (offset - principal_excess)) * value for offset, value in blocks.items())
        threshold = far_gap - 2
        tail = sum(value for offset, value in blocks.items() if offset >= threshold)
        gap_factor = 2.0 ** (-2.0 * float(exponent) * (far_gap - 2 - principal_excess))
        check(f"excess_tail_gap_s_{exponent}", tail <= gap_factor * weighted * (1 + 1e-13), tail, f"<={gap_factor * weighted}")
    check("far_gap_excludes_diagonal", far_gap - 2 > 1, far_gap - 2, ">1 fixed-shift diagonal")

    # 5. R-063 forest terms reconstruct the product and cannot be added to it.
    g = sp.symbols("g", real=True)
    h2 = sp.hermite_prob(2, g)
    h4 = sp.hermite_prob(4, g)
    product = sp.expand(g**2 * (g**2 - 1))
    alpha4, alpha2, alpha0 = sp.symbols("alpha4 alpha2 alpha0")
    polynomial = sp.Poly(sp.expand(product - alpha4 * h4 - alpha2 * h2 - alpha0), g)
    solution = sp.solve(polynomial.all_coeffs(), (alpha4, alpha2, alpha0), dict=True)[0]
    reconstructed = sp.expand(solution[alpha4] * h4 + solution[alpha2] * h2 + solution[alpha0])
    lower_forest = sp.expand(solution[alpha2] * h2 + solution[alpha0])
    check("forest_reconstruction_exact", sp.expand(product - reconstructed) == 0, sp.expand(product - reconstructed), 0)
    check("forest_h4_coefficient", solution[alpha4] == 1, solution[alpha4], 1)
    check("forest_h2_coefficient", solution[alpha2] == 5, solution[alpha2], TEST_ORACLES["forest_h2_coefficient"])
    check("forest_h0_coefficient", solution[alpha0] == 2, solution[alpha0], TEST_ORACLES["forest_h0_coefficient"])
    double_count_residual = sp.expand(product + lower_forest - product)
    check("adding_lower_forest_double_counts", double_count_residual != 0, double_count_residual, "nonzero")

    # 6. R-089's switch is centered and covariance matched only before
    # conditioning.  Conditional second moments on |G|>=1 and |G|<1 differ
    # from one, although their probability-weighted average is one.
    phi_one = math.exp(-0.5) / math.sqrt(2 * math.pi)
    probability_plus = math.erfc(1 / math.sqrt(2))
    probability_minus = 1.0 - probability_plus
    conditional_variance_plus = 1.0 + 2.0 * phi_one / probability_plus
    conditional_variance_minus = 1.0 - 2.0 * phi_one / probability_minus
    unconditional_variance = probability_plus * conditional_variance_plus + probability_minus * conditional_variance_minus
    check("r089_switch_conditional_variance_plus_not_one", conditional_variance_plus > 1.0, conditional_variance_plus, ">1")
    check("r089_switch_conditional_variance_minus_not_one", 0.0 < conditional_variance_minus < 1.0, conditional_variance_minus, "in (0,1)")
    check("r089_switch_unconditional_covariance_matched", abs(unconditional_variance - 1.0) < 2e-15, unconditional_variance, 1.0)

    # The complete local scalar raw rational endpoint, rather than its Taylor
    # fragment, has a strict negative fixture.  Values are normalized by
    # 4*c1*e; the final expectation below is normalized by c1*e.
    def rational_endpoint_normalized(value: sp.Rational) -> sp.Expr:
        return sp.factor((value - sp.Rational(5, 9) * value**3 / (value**2 + 1)) ** 2)

    endpoint_base = rational_endpoint_normalized(sp.Rational(1, 1))
    endpoint_minus = rational_endpoint_normalized(sp.Rational(1, 2))
    endpoint_plus = rational_endpoint_normalized(sp.Rational(3, 2))
    check("raw_endpoint_base_value", endpoint_base == sp.Rational(169, 324), endpoint_base, sp.Rational(169, 324))
    check("raw_endpoint_minus_value", endpoint_minus == sp.Rational(16, 81), endpoint_minus, sp.Rational(16, 81))
    check("raw_endpoint_plus_value", endpoint_plus == sp.Rational(144, 169), endpoint_plus, sp.Rational(144, 169))
    outside_factor = 2 * (endpoint_minus - endpoint_base) * 2
    inside_factor = 2 * (endpoint_plus - endpoint_base) * (-2)
    raw_endpoint_factor = sp.factor(outside_factor + inside_factor)
    check("raw_endpoint_pathwise_outside_negative", endpoint_minus - endpoint_base < 0, endpoint_minus - endpoint_base, "<0")
    check("raw_endpoint_pathwise_inside_negative", endpoint_plus - endpoint_base > 0, endpoint_plus - endpoint_base, ">0 while Q<0")
    check("raw_endpoint_expectation_exact_factor", raw_endpoint_factor == sp.Rational(-35840, 13689), raw_endpoint_factor, TEST_ORACLES["raw_endpoint_factor"])
    raw_endpoint_normalized_expectation = float(raw_endpoint_factor) * phi_one
    check("raw_endpoint_expectation_strictly_negative", raw_endpoint_normalized_expectation < -0.6, raw_endpoint_normalized_expectation, "<-0.6 per c1*e")

    # 7. The R-079 current identity keeps the f--i cross exactly once.  This
    # is the assembly object; reduced Cartan and rational pieces do not imply it.
    w, fresh, future = sp.symbols("w fresh future", real=True)
    square_difference = sp.expand(((w + fresh + future) ** 2 - w**2) / 2)
    packet_split = sp.expand(w * fresh + fresh**2 / 2 + (w + fresh) * future + future**2 / 2)
    check("full_packet_cross_nonduplication", sp.expand(square_difference - packet_split) == 0, sp.expand(square_difference - packet_split), 0)
    omitted_cross = sp.expand(w * fresh + fresh**2 / 2 + w * future + future**2 / 2)
    check("omitting_fresh_future_cross_fails", sp.expand(square_difference - omitted_cross) == fresh * future, sp.expand(square_difference - omitted_cross), fresh * future)

    # 8. Conditional budget arithmetic remains compatible but proves no bound.
    sextic_remaining = INPUTS["sextic_capacity"] - INPUTS["sextic_delta"] - INPUTS["sextic_packet"]
    control_remaining = 1 / (2 * INPUTS["comparison_p"]) - INPUTS["control_charge"]
    q_minus_p = INPUTS["nelson_q"] - INPUTS["comparison_p"]
    check("sextic_budget_remaining", sextic_remaining == Fraction(3, 50), sextic_remaining, Fraction(3, 50))
    check("control_budget_remaining", control_remaining == Fraction(1, 220), control_remaining, Fraction(1, 220))
    check("nelson_exponent_gap", q_minus_p == Fraction(1, 90), q_minus_p, Fraction(1, 90))

    claims_not_established = {
        "cartan_excess_tail_one_use": False,
        "controlled_cartan_cfar": False,
        "complete_temporal_rational_packet": False,
        "complete_progressive_packet_assembly": False,
        "regular_packet_lower_bound": False,
        "uniform_overlap": False,
        "nelson": False,
        "sector_a": False,
        "tier_promotion": False,
    }
    check("all_downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "cartan": {
            "identity": "b=spatial-gradient(c)",
            "fourier_identity": "b_hat_i(q-p)+i*p_i*c_hat(q-p)=i*q_i*c_hat(q-p)",
            "lp_upper_support_convention": "|pi_m|<=1 and |q|_infinity<=2^(m+1)",
            "conservative_shell_prefactor_without_kappa0_over_P": str(max_norm_shell_constant),
            "scalar_derivative_secant": str(derivative_secant),
            "scalar_hessian_at_one": str(hessian_at_one),
            "critical_exponent": "(1-2s)+3-4+2s=0 for every s",
            "normalized_shell_diagnostics": normalized_shells,
            "global_sobolev_ledger_3_12": False,
            "obstructing_chaos": "current-root first chaos; P_t attenuation e^(-t)",
            "direct_far_cfar_refuted": False,
            "correct_target": "R-089 (3.9), or an excess-tail ledger beginning at coefficient offset five",
            "principal_excess": principal_excess,
        },
        "rational": {
            "conditional_variances": {
                "event_abs_G_ge_1": conditional_variance_plus,
                "event_abs_G_lt_1": conditional_variance_minus,
                "unconditional_recombination": unconditional_variance,
            },
            "raw_endpoint_values_normalized_by_4c1e": {
                "base": str(endpoint_base),
                "minus_half_shift": str(endpoint_minus),
                "plus_half_shift": str(endpoint_plus),
            },
            "raw_endpoint_expectation_factor_before_phi_per_c1e": str(raw_endpoint_factor),
            "raw_endpoint_expectation_per_c1e": raw_endpoint_normalized_expectation,
            "ordinary_product": str(product),
            "forest_reconstruction": str(reconstructed),
            "lower_forest": str(lower_forest),
            "lower_forest_is_additional_to_unexpanded_product": False,
            "canonical_assembly": "R-063 reconstructs the Wick coefficient once; R-066/R-070 supply the heat-transported endpoint, and R-079 gives its nonduplicating temporal decomposition. No separate forest or heat term is added to the unexpanded endpoint.",
        },
        "budgets": {
            "sextic_remaining": str(sextic_remaining),
            "control_remaining": str(control_remaining),
            "q_minus_p": str(q_minus_p),
        },
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(f"[R-090 primary] {passed}/{len(rows)} PASS")
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-090 primary] {passed}/{len(rows)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
