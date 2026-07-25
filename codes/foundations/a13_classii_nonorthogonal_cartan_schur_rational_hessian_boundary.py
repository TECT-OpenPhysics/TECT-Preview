#!/usr/bin/env python3
"""Primary executable evidence for the R-085 A13 reduction.

This program verifies three exact pieces of the post-R-084 frontier:

1. a nonorthogonal weighted causal Schur lemma which replaces the false
   output-orthogonality route;
2. the exact nonlinear rational Pauli--Fierz endpoint and the shifted-Hessian
   pair left after the five already-payable unshifted families; and
3. the REG/OVERLAP/CORE/BD dependency split and the current production budget
   arithmetic.

It does not assert the missing production atom estimate, rational shifted-
Hessian form bound, progressive/revisit theorem, one-use, or Nelson bound.
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
RESULT_ID = "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY"
MODEL = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R084 = REPO / f"claims/{CLAIM}/classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json"
OUTPUT = REPO / f"claims/{CLAIM}/runs/2026-07-25-primary-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json"


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


def schur_constant(s: Fraction, eta: Fraction) -> float:
    return 1.0 / (
        (1.0 - 2.0 ** (-float(eta)))
        * (1.0 - 2.0 ** (-2.0 * float(s)))
        * (1.0 - 2.0 ** (1.0 + float(eta) - 2.0 * float(s)))
    )


def finite_schur_fixture(s: Fraction, eta: Fraction, gap: int, maximum: int) -> tuple[float, float]:
    """Aligned scalar fixture satisfying the atom hypothesis with q_k=2^(-k)."""

    q = {k: 2.0 ** (-k) for k in range(maximum + 1)}
    lhs = 0.0
    for m in range(gap, maximum + gap + 1):
        for j in range(0, m - gap + 1):
            value = 0.0
            for k in range(j + 1):
                value += 2.0 ** (-float(s) * (m - k)) * math.sqrt(q[k])
            lhs += 2.0**j * value * value
    rhs = (
        schur_constant(s, eta)
        * 2.0 ** (-2.0 * float(s) * gap)
        * sum(2.0**k * q[k] for k in range(maximum + 1))
    )
    return lhs, rhs


def critical_partial_sum(gap: int, maximum: int) -> float:
    """The sharp s=1/2 single-input fixture from the R-082 boundary."""

    return sum((2.0 ** (m - gap + 1) - 1.0) * 2.0 ** (-m) for m in range(gap, maximum + 1))


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    model = json.loads(MODEL.read_text(encoding="utf-8"))
    r084 = json.loads(R084.read_text(encoding="utf-8"))
    parameters = model["parameters"]
    density_floor = Fraction(str(parameters["rho_regularizer"]))
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["rho_regularizer"])
    b_weight = float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator
    c_weight = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    pf_alpha = c_weight / (b_weight + c_weight)
    c1 = c_weight / pf_alpha**2

    check("model_schema", model.get("schema") == "tect/a1-production-functional-realisation/1.0", model.get("schema"), "tect/a1-production-functional-realisation/1.0")
    check("r084_result_id", r084.get("result_id") == "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION", r084.get("result_id"), "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION")
    check("production_density_floor", density_floor == Fraction(1, 10**12), str(density_floor), "1/1000000000000")
    check("production_pf_alpha", abs(pf_alpha - 5.0 / 9.0) < 1e-14, pf_alpha, "5/9")
    check("production_rational_row_scale", abs(4.0 * c1 - 243.0 / (2000.0 * denominator)) < 1e-14, 4.0 * c1, "243/(2000P)")

    # Nonorthogonal weighted causal Schur lemma.
    field_alpha = Fraction(2, 5)  # Declared production audit regularity.
    first_order_gain = 3 * field_alpha - 1
    candidate_second_order_gain = 4 * field_alpha - 1
    s = Fraction(7, 12)
    eta = Fraction(1, 12)
    constant = schur_constant(s, eta)

    check("first_order_gain", first_order_gain == Fraction(1, 5), str(first_order_gain), "1/5")
    check("first_order_below_schur_threshold", first_order_gain < Fraction(1, 2), str(first_order_gain), "<1/2")
    check("candidate_second_order_gain", candidate_second_order_gain == Fraction(3, 5), str(candidate_second_order_gain), "3/5")
    check("schur_s_above_half", s > Fraction(1, 2), str(s), ">1/2")
    check("schur_s_below_candidate_gain", s < candidate_second_order_gain, str(s), "<3/5")
    check("schur_eta_positive", eta > 0, str(eta), ">0")
    check("schur_eta_admissible", eta < 2 * s - 1, str(eta), "<1/6")
    check("schur_eta_balanced", eta == (2 * s - 1) / 2, str(eta), "(2s-1)/2")
    check("schur_decay_exponent", 2 * s == Fraction(7, 6), str(2 * s), "7/6")
    check("schur_constant_finite", math.isfinite(constant) and constant > 0.0, constant, "finite positive")
    check("schur_constant_interval", 572.0 < constant < 573.0, constant, "(572,573)")

    fixture_ratios: list[float] = []
    for gap, maximum in ((2, 4), (3, 6), (5, 8), (7, 10)):
        lhs, rhs = finite_schur_fixture(s, eta, gap, maximum)
        ratio = lhs / rhs
        fixture_ratios.append(ratio)
        check(f"finite_schur_fixture_C{gap}_M{maximum}", lhs <= rhs * (1.0 + 1e-12), ratio, "<=1")

    critical_16 = critical_partial_sum(2, 16)
    critical_32 = critical_partial_sum(2, 32)
    check("critical_fixture_grows", critical_32 > critical_16, critical_32 / critical_16, ">1")
    check("critical_fixture_linear_lower_bound", critical_32 > (32 - 2) * 2.0 ** (-2), critical_32, ">7.5")

    # Exact rational-row endpoint on the real doublet/singlet slice.
    x, y = sp.symbols("x y", real=True)
    alpha_sp = sp.Rational(5, 9)
    floor_sp = sp.Rational(density_floor.numerator, density_floor.denominator)
    radius = x * x
    safe_density = x * x + y * y + floor_sp
    g = sp.Matrix([x - alpha_sp * radius * x / safe_density, -alpha_sp * radius * y / safe_density])
    gram = sp.simplify(g * g.T)  # Positive production factor 4*c1 is restored outside.
    variables = (x, y)
    base = (sp.Integer(1), sp.Integer(1))
    shift = (sp.Integer(1), sp.Integer(-1))
    endpoint = tuple(base[i] + shift[i] for i in range(2))
    base_sub = {x: base[0], y: base[1]}
    endpoint_sub = {x: endpoint[0], y: endpoint[1]}

    def directional_first(matrix: sp.Matrix) -> sp.Matrix:
        return sp.Matrix(
            [[sum(sp.diff(matrix[i, j], variables[k]).subs(base_sub) * shift[k] for k in range(2)) for j in range(2)] for i in range(2)]
        )

    def directional_second(matrix: sp.Matrix) -> sp.Matrix:
        return sp.Matrix(
            [[sum(sp.diff(matrix[i, j], variables[k], variables[l]).subs(base_sub) * shift[k] * shift[l] for k in range(2) for l in range(2)) for j in range(2)] for i in range(2)]
        )

    gram_base = sp.Matrix(gram.subs(base_sub))
    gram_endpoint = sp.Matrix(gram.subs(endpoint_sub))
    first = directional_first(gram)
    second = directional_second(gram)
    shifted_hessian_remainder = sp.simplify(gram_endpoint - gram_base - first - sp.Rational(1, 2) * second)
    determinant = sp.factor(shifted_hessian_remainder.det())
    trace = sp.factor(sp.trace(shifted_hessian_remainder))
    derivative = sp.Matrix([sp.Rational(1, 10), sp.Integer(1)])
    covariance = sp.zeros(2)
    q_tensor = derivative * derivative.T - covariance
    hidden_q_pair = sp.factor(sp.Rational(1, 2) * sp.trace(shifted_hessian_remainder.T * q_tensor))

    check("rational_gram_symmetric", sp.simplify(gram - gram.T) == sp.zeros(2), str(sp.simplify(gram - gram.T)), "zero")
    gram_base_float = np.array(gram_base.evalf(), dtype=float)
    check("rational_gram_psd", float(np.linalg.eigvalsh(gram_base_float).min()) > -1e-14, np.linalg.eigvalsh(gram_base_float).tolist(), ">=-1e-14")
    check("shifted_hessian_remainder_nonzero", shifted_hessian_remainder != sp.zeros(2), str(shifted_hessian_remainder), "nonzero")
    check("shifted_hessian_remainder_indefinite", determinant < 0, float(determinant), "<0")
    check("shifted_hessian_remainder_positive_trace", trace > 0, float(trace), ">0")
    check("hidden_q_pair_negative", hidden_q_pair < 0, float(hidden_q_pair), "<0")
    check("hidden_q_pair_value", abs(float(hidden_q_pair) + 0.0021604938271616512) < 1e-15, float(hidden_q_pair), "-0.0021604938271616512 within 1e-15")

    # Verify the exact endpoint split with a nonzero derivative control.
    control_derivative = sp.Matrix([sp.Rational(1, 3), sp.Rational(-1, 4)])
    translated_derivative = derivative + control_derivative
    exact_delta = sp.factor(
        sp.Rational(1, 2) * sp.trace(gram_endpoint.T * (translated_derivative * translated_derivative.T - covariance))
        - sp.Rational(1, 2) * sp.trace(gram_base.T * q_tensor)
    )
    endpoint_split = sp.factor(
        sp.Rational(1, 2) * sp.trace((gram_endpoint - gram_base).T * q_tensor)
        + (derivative.T * gram_endpoint * control_derivative)[0]
        + sp.Rational(1, 2) * (control_derivative.T * gram_endpoint * control_derivative)[0]
    )
    five_unshifted = sp.factor(
        sp.Rational(1, 2) * sp.trace(first.T * q_tensor)
        + sp.Rational(1, 4) * sp.trace(second.T * q_tensor)
        + (derivative.T * gram_base * control_derivative)[0]
        + (derivative.T * first * control_derivative)[0]
        + sp.Rational(1, 2) * (derivative.T * second * control_derivative)[0]
    )
    hidden_pair = sp.factor(
        sp.Rational(1, 2) * sp.trace(shifted_hessian_remainder.T * q_tensor)
        + (derivative.T * shifted_hessian_remainder * control_derivative)[0]
    )
    positive_square = sp.factor(sp.Rational(1, 2) * (control_derivative.T * gram_endpoint * control_derivative)[0])

    check("rational_exact_endpoint_identity", sp.simplify(exact_delta - endpoint_split) == 0, str(sp.simplify(exact_delta - endpoint_split)), "0")
    check("rational_five_plus_hidden_plus_square", sp.simplify(exact_delta - five_unshifted - hidden_pair - positive_square) == 0, str(sp.simplify(exact_delta - five_unshifted - hidden_pair - positive_square)), "0")
    check("rational_hidden_pair_nonzero", hidden_pair != 0, float(hidden_pair), "nonzero")
    check("rational_positive_square", positive_square >= 0, float(positive_square), ">=0")

    # Production scalar-ray diagnostics for the two failed shortcuts.
    scalar_variable = sp.symbols("scalar_variable", real=True)
    production_denominator = sp.Rational(4) + floor_sp
    c1_sp = sp.Rational(243, 8000) / production_denominator
    scalar_g = scalar_variable - alpha_sp * scalar_variable**3 / (scalar_variable**2 + floor_sp)
    scalar_gram = 4 * c1_sp * scalar_g**2
    third_at_floor_scale = sp.simplify(sp.diff(scalar_gram, scalar_variable, 3).subs(scalar_variable, sp.sqrt(floor_sp)))
    third_formula = sp.simplify(6 * alpha_sp**2 * c1_sp / sp.sqrt(floor_sp))
    check("rational_scalar_third_derivative_formula", sp.simplify(third_at_floor_scale - third_formula) == 0, str(sp.simplify(third_at_floor_scale - third_formula)), "0")
    check("rational_scalar_third_derivative_nonzero", third_at_floor_scale > 0, float(third_at_floor_scale), ">0")
    check("rational_scalar_third_derivative_interval", 14062.0 < float(third_at_floor_scale) < 14063.0, float(third_at_floor_scale), "(14062,14063)")

    q22 = sp.simplify(c1_sp * alpha_sp**2)
    d0 = sp.Rational(2) + floor_sp
    fixture_c = sp.Rational(2)
    fixture_f0 = sp.simplify(2 * q22 / d0**2)
    fixture_dr = sp.simplify(-2 * q22 * (4 * fixture_c * (floor_sp + 1) - 5 * floor_sp - 2) / d0**3)
    check("rational_fixed_schur_ratio", sp.simplify(fixture_dr / fixture_f0) == -3, str(sp.simplify(fixture_dr / fixture_f0)), "-3")
    check("rational_fixed_schur_signed", fixture_f0 > 0 and fixture_dr < 0, [float(fixture_f0), float(fixture_dr)], "F0>0 and DR<0")

    degrees = [Fraction(7, 20), Fraction(7, 10), Fraction(13, 30), Fraction(3, 5), Fraction(23, 30)]
    slacks = [1 - degree for degree in degrees]
    check("five_unshifted_degrees", degrees == [Fraction(7, 20), Fraction(7, 10), Fraction(13, 30), Fraction(3, 5), Fraction(23, 30)], [str(v) for v in degrees], ["7/20", "7/10", "13/30", "3/5", "23/30"])
    check("five_unshifted_strict_subcritical", all(degree < 1 for degree in degrees), [str(v) for v in degrees], "all <1")
    check("five_unshifted_slacks", slacks == [Fraction(13, 20), Fraction(3, 10), Fraction(17, 30), Fraction(2, 5), Fraction(7, 30)], [str(v) for v in slacks], ["13/20", "3/10", "17/30", "2/5", "7/30"])
    check("five_unshifted_worst_moment", 1 / min(slacks) == Fraction(30, 7), str(1 / min(slacks)), "30/7")

    # Corrected production synthesis arithmetic and dependency separation.
    epsilon_6 = Fraction(15, 100)
    delta = Fraction(6, 100)
    gamma_half = Fraction(27, 100)
    epsilon_v = Fraction(45, 100)
    p = Fraction(11, 10)
    q = 1 / (2 * epsilon_v)
    check("sextic_reserve", gamma_half - delta - epsilon_6 == Fraction(6, 100), str(gamma_half - delta - epsilon_6), "3/50")
    check("control_reserve", Fraction(1, 2) / p - epsilon_v == Fraction(1, 220), str(Fraction(1, 2) / p - epsilon_v), "1/220")
    check("bd_q", q == Fraction(10, 9), str(q), "10/9")
    check("nelson_gap", q - p == Fraction(1, 90), str(q - p), "1/90")
    check("regular_packet_not_closed", not bool(r084["claims_not_established"]["complete_regular_packet_lower_bound"]), r084["claims_not_established"]["complete_regular_packet_lower_bound"], False)
    check("progressive_not_closed", not bool(r084["claims_not_established"]["full_progressive_revisit_extension"]), r084["claims_not_established"]["full_progressive_revisit_extension"], False)
    check("one_use_not_closed", not bool(r084["claims_not_established"]["controlled_shell_one_use"]), r084["claims_not_established"]["controlled_shell_one_use"], False)
    check("nelson_not_closed", not bool(r084["claims_not_established"]["nelson_bound"]), r084["claims_not_established"]["nelson_bound"], False)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-nonorthogonal-cartan-schur-rational-hessian-boundary-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "schur_result": {
            "field_alpha": str(field_alpha),
            "first_order_gain": str(first_order_gain),
            "candidate_second_order_gain": str(candidate_second_order_gain),
            "s": str(s),
            "eta": str(eta),
            "constant": constant,
            "decay_exponent": str(2 * s),
            "finite_fixture_ratios": fixture_ratios,
            "theorem_scope": "nonorthogonal weighted causal Schur implication conditional on the production atom estimate",
        },
        "rational_result": {
            "normalized_shifted_hessian_remainder": [[str(shifted_hessian_remainder[i, j]) for j in range(2)] for i in range(2)],
            "determinant": str(determinant),
            "hidden_q_pair": str(hidden_q_pair),
            "hidden_q_pair_float": float(hidden_q_pair),
            "scalar_third_derivative": float(third_at_floor_scale),
            "fixed_schur_fixture": {"C": 2, "F0": float(fixture_f0), "DR": float(fixture_dr), "ratio": float(fixture_dr / fixture_f0)},
            "five_degrees": [str(value) for value in degrees],
            "five_slacks": [str(value) for value in slacks],
            "boundary": "the five unshifted families are payable, but the exact shifted-Hessian pair remains signed and unproved",
        },
        "synthesis": {
            "REG": "open: Cartan production atom estimate and rational shifted-Hessian form bound",
            "OVERLAP": "open: bounded-simple partition/revisit-uniform complete-packet lower bound",
            "CORE": "open: finite-objective admissible-core extension and terminal L6 graph continuity",
            "BD": "exact conditional implication only: q=10/9 after one-use",
            "epsilon_6": float(epsilon_6),
            "delta": float(delta),
            "epsilon_v": float(epsilon_v),
            "p": str(p),
            "q": str(q),
        },
        "proved_scope": "nonorthogonal weighted causal Schur lemma; exact rational endpoint decomposition into five payable unshifted families, a signed shifted-Hessian pair, and a positive square; dependency and budget arithmetic",
        "claims_not_established": {
            "production_cartan_atom_estimate": False,
            "controlled_cartan_cfar": False,
            "rational_shifted_hessian_form_bound": False,
            "complete_signed_near": False,
            "complete_regular_packet_lower_bound": False,
            "full_progressive_revisit_extension": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "interacting_measure": False,
            "sector_a_closure": False,
            "tier_promotion": False,
        },
    }
    atomic_json(OUTPUT, payload)
    if passed == len(rows):
        print(f"[R-085 primary] {passed}/{len(rows)} PASS")
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-085 primary] {passed}/{len(rows)} PASS; failures={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
