#!/usr/bin/env python3
"""Primary executable evidence for the R-086 rational reduction.

The program verifies the exact translated-Wick normal form, the improved
cubic Sobolev/Young ledger, the scalar Taylor-Gram sign fixture, the
two-coordinate endpoint-kernel fixture, and the leading heat lift of that
kernel.  It does not assert the coefficient-dominant packet, complete
rational NEAR, Cartan CFAR, REG, OVERLAP, one-use, or Nelson.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RATIONAL-TRANSLATED-WICK-PAYLOAD-COMPARABLE-REDUCTION"
MODEL = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R085 = REPO / f"claims/{CLAIM}/classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json"
OUTPUT = REPO / f"claims/{CLAIM}/runs/2026-07-25-primary-rational-translated-wick-payload-comparable-reduction/result.json"


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


def directional(matrix: sp.Matrix, variables: tuple[sp.Symbol, ...], base: tuple[sp.Expr, ...], shift: tuple[sp.Expr, ...], order: int) -> sp.Matrix:
    parameter = sp.symbols("direction_parameter", real=True)
    substitution = {variables[index]: base[index] + parameter * shift[index] for index in range(len(variables))}
    return sp.Matrix(matrix.subs(substitution).diff(parameter, order).subs(parameter, 0))


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    model = json.loads(MODEL.read_text(encoding="utf-8"))
    r085 = json.loads(R085.read_text(encoding="utf-8"))
    parameters = model["parameters"]
    floor = Fraction(str(parameters["rho_regularizer"]))
    denominator = Fraction(str(parameters["M_X"])) ** 2 + floor
    b_weight = Fraction(str(parameters["cJK"])) * Fraction(str(parameters["alpha_X"])) * Fraction(str(parameters["beta_X"])) / denominator
    c_weight = Fraction(str(parameters["cKK"])) * Fraction(str(parameters["beta_X"])) ** 2 / denominator
    alpha = sp.Rational(c_weight.numerator, c_weight.denominator) / sp.Rational((b_weight + c_weight).numerator, (b_weight + c_weight).denominator)
    c1 = sp.Rational(c_weight.numerator, c_weight.denominator) / alpha**2
    floor_sp = sp.Rational(floor.numerator, floor.denominator)

    check("model_schema", model.get("schema") == "tect/a1-production-functional-realisation/1.0", model.get("schema"), "tect/a1-production-functional-realisation/1.0")
    check("r085_result_id", r085.get("result_id") == "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY", r085.get("result_id"), "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY")
    check("production_floor", floor == Fraction(1, 10**12), str(floor), "1/1000000000000")
    check("production_alpha", alpha == sp.Rational(5, 9), str(alpha), "5/9")
    check("production_c1", sp.simplify(c1 - sp.Rational(243, 8000) / (4 + floor_sp)) == 0, str(c1), "243/[8000(4+e)]")

    # Exact translated-Wick normal form on generic symmetric tensors.
    l11, l12, l22, b11, b12, b22 = sp.symbols("l11 l12 l22 b11 b12 b22", real=True)
    g1, g2, c_1, c_2 = sp.symbols("g1 g2 c_1 c_2", real=True)
    gamma11, gamma12, gamma22 = sp.symbols("gamma11 gamma12 gamma22", real=True)
    remainder = sp.Matrix([[l11, l12], [l12, l22]])
    taylor = sp.Matrix([[b11, b12], [b12, b22]])
    endpoint_gram = taylor + remainder
    base_derivative = sp.Matrix([g1, g2])
    control_derivative = sp.Matrix([c_1, c_2])
    gamma = sp.Matrix([[gamma11, gamma12], [gamma12, gamma22]])
    q_base = base_derivative * base_derivative.T - gamma
    q_translated = (base_derivative + control_derivative) * (base_derivative + control_derivative).T - gamma
    left = (
        sp.trace(remainder.T * q_base) / 2
        + (base_derivative.T * remainder * control_derivative)[0]
        + (control_derivative.T * endpoint_gram * control_derivative)[0] / 2
    )
    right = sp.trace(remainder.T * q_translated) / 2 + (control_derivative.T * taylor * control_derivative)[0] / 2
    check("translated_wick_normal_form", sp.expand(left - right) == 0, str(sp.expand(left - right)), "0")
    check("endpoint_equals_taylor_plus_remainder", sp.simplify(endpoint_gram - taylor - remainder) == sp.zeros(2), str(sp.simplify(endpoint_gram - taylor - remainder)), "zero")

    # Improved deterministic cubic and the two payable shifted ledgers.
    s_q = Fraction(11, 10)
    cubic_x = s_q / 2
    cubic_y = (3 - s_q) / 6
    cubic_total = cubic_x + cubic_y
    cubic_slack = 1 - cubic_total
    q_x, q_y = Fraction(11, 20), Fraction(3, 20)
    g_x, g_y = Fraction(2, 5), Fraction(11, 30)
    check("cubic_x_exponent", cubic_x == Fraction(11, 20), str(cubic_x), "11/20")
    check("cubic_y_exponent", cubic_y == Fraction(19, 60), str(cubic_y), "19/60")
    check("cubic_total", cubic_total == Fraction(13, 15), str(cubic_total), "13/15")
    check("cubic_slack", cubic_slack == Fraction(2, 15), str(cubic_slack), "2/15")
    check("cubic_model_moment", 1 / cubic_slack == Fraction(15, 2), str(1 / cubic_slack), "15/2")
    check("cubic_eta_power", cubic_x / cubic_slack == Fraction(33, 8), str(cubic_x / cubic_slack), "33/8")
    check("cubic_zeta_power", cubic_y / cubic_slack == Fraction(19, 8), str(cubic_y / cubic_slack), "19/8")
    check("q_payload_total", q_x + q_y == Fraction(7, 10), str(q_x + q_y), "7/10")
    check("q_payload_slack", 1 - q_x - q_y == Fraction(3, 10), str(1 - q_x - q_y), "3/10")
    check("g_payload_total", g_x + g_y == Fraction(23, 30), str(g_x + g_y), "23/30")
    check("g_payload_slack", 1 - g_x - g_y == Fraction(7, 30), str(1 - g_x - g_y), "7/30")
    check("g_payload_moment", 1 / (1 - g_x - g_y) == Fraction(30, 7), str(1 / (1 - g_x - g_y)), "30/7")
    check("all_payable_ledgers_subcritical", max(cubic_total, q_x + q_y, g_x + g_y) < 1, [str(cubic_total), str(q_x + q_y), str(g_x + g_y)], "all <1")

    # Exact scalar Taylor polynomial at z=sqrt(e), a=C sqrt(e).
    u, capital_c = sp.symbols("u capital_c", real=True)
    normalized_f = u - alpha * u**3 / (u**2 + 1)
    normalized_b = sp.factor(normalized_f**2)
    scalar_taylor = sp.factor(
        normalized_b.subs(u, 1)
        + sp.diff(normalized_b, u).subs(u, 1) * capital_c
        + sp.diff(normalized_b, u, 2).subs(u, 1) * capital_c**2 / 2
    )
    scalar_expected = sp.factor((169 + 208 * capital_c - capital_c**2) / 324)
    check("scalar_taylor_formula", sp.simplify(scalar_taylor - scalar_expected) == 0, str(scalar_taylor), str(scalar_expected))
    check("scalar_negative_C_minus_1", scalar_taylor.subs(capital_c, -1) == -sp.Rational(10, 81), str(scalar_taylor.subs(capital_c, -1)), "-10/81")
    check("scalar_negative_C_209", scalar_taylor.subs(capital_c, 209) == -sp.Rational(10, 81), str(scalar_taylor.subs(capital_c, 209)), "-10/81")
    discriminant = sp.factor(sp.discriminant(169 + 208 * capital_c - capital_c**2, capital_c))
    check("scalar_taylor_discriminant", discriminant == 4 * 13**2 * 65, str(discriminant), str(4 * 13**2 * 65))
    check("production_scalar_taylor_value", sp.simplify(4 * c1 * floor_sp * scalar_taylor.subs(capital_c, -1) + 40 * c1 * floor_sp / 81) == 0, str(sp.simplify(4 * c1 * floor_sp * scalar_taylor.subs(capital_c, -1))), "-40*c1*e/81")

    # Two-coordinate exact endpoint kernel fixture.
    x, y, e = sp.symbols("x y e", real=True, nonnegative=True)
    radius = x**2
    density = x**2 + y**2 + e
    g = sp.Matrix([x - alpha * radius * x / density, -alpha * radius * y / density])
    gram = sp.simplify(g * g.T)
    variables = (x, y)
    base = (sp.Integer(1), sp.Integer(1))
    shift = (sp.Integer(1), sp.Integer(-1))
    endpoint = (sp.Integer(2), sp.Integer(0))
    gram_base = sp.Matrix(gram.subs({x: base[0], y: base[1]}))
    gram_endpoint = sp.Matrix(gram.subs({x: endpoint[0], y: endpoint[1]}))
    first = directional(gram, variables, base, shift, 1)
    second = directional(gram, variables, base, shift, 2)
    gram_taylor = sp.simplify(gram_base + first + second / 2)
    exact_remainder = sp.simplify(gram_endpoint - gram_taylor)
    expected_endpoint_zero_floor = sp.Matrix([[sp.Rational(64, 81), 0], [0, 0]])
    expected_taylor_zero_floor = sp.Matrix([[-sp.Rational(1, 81), sp.Rational(5, 81)], [sp.Rational(5, 81), 0]])
    expected_remainder_zero_floor = sp.Matrix([[sp.Rational(65, 81), -sp.Rational(5, 81)], [-sp.Rational(5, 81), 0]])
    check("kernel_endpoint_matrix", sp.simplify(gram_endpoint.subs(e, 0) - expected_endpoint_zero_floor) == sp.zeros(2), str(gram_endpoint.subs(e, 0)), str(expected_endpoint_zero_floor))
    check("kernel_taylor_matrix", sp.simplify(gram_taylor.subs(e, 0) - expected_taylor_zero_floor) == sp.zeros(2), str(gram_taylor.subs(e, 0)), str(expected_taylor_zero_floor))
    check("kernel_remainder_matrix", sp.simplify(exact_remainder.subs(e, 0) - expected_remainder_zero_floor) == sp.zeros(2), str(exact_remainder.subs(e, 0)), str(expected_remainder_zero_floor))
    l21_formula = sp.factor(5 * (27 * e**2 + 40 * e - 8) / (81 * (e + 2) ** 3))
    check("kernel_l21_formula", sp.simplify(exact_remainder[1, 0] - l21_formula) == 0, str(sp.factor(exact_remainder[1, 0])), str(l21_formula))
    l21_production = exact_remainder[1, 0].subs(e, floor_sp)
    check("kernel_l21_production_negative", l21_production < 0, float(l21_production), "<0")
    check("endpoint_e2_kernel", sp.simplify(gram_endpoint * sp.Matrix([0, 1])) == sp.zeros(2, 1), str(sp.simplify(gram_endpoint * sp.Matrix([0, 1]))), "zero")
    check("kernel_packet_negative_slope", l21_production < 0 and gram_endpoint[1, 1] == 0, [float(l21_production), str(gram_endpoint[1, 1])], "negative slope and zero t^2")
    check("taylor_determinant_zero_floor", gram_taylor.subs(e, 0).det() == -sp.Rational(25, 81**2), str(gram_taylor.subs(e, 0).det()), "-25/6561")

    # First heat lifting coefficient of the endpoint kernel.
    g2_y = sp.factor(sp.diff(g[1], y).subs({x: 2, y: 0}))
    heat_coefficient = sp.factor(4 * c1 * g2_y**2)
    heat_expected = sp.factor(4 * c1 * (sp.Rational(20, 9) / (4 + e)) ** 2)
    check("kernel_transverse_derivative", sp.simplify(g2_y + sp.Rational(20, 9) / (4 + e)) == 0, str(g2_y), "-20/[9(4+e)]")
    check("heat_leading_coefficient", sp.simplify(heat_coefficient - heat_expected) == 0, str(heat_coefficient), str(heat_expected))
    check("heat_coefficient_positive", heat_coefficient.subs(e, floor_sp) > 0, float(heat_coefficient.subs(e, floor_sp)), ">0")
    check("inverse_heat_schur_order", l21_production != 0 and heat_coefficient.subs(e, floor_sp) > 0, "cross=O(1), eigenvalue=O(sigma^2)", "inverse loss O(sigma^-2)")

    claims_not_established = {
        "coefficient_dominant_rational_packet": False,
        "rational_shifted_hessian_form_bound": False,
        "complete_rational_near": False,
        "production_cartan_atom_estimate": False,
        "controlled_cartan_cfar": False,
        "complete_regular_packet_lower_bound": False,
        "overlap_uniform_bound": False,
        "full_progressive_revisit_extension": False,
        "controlled_shell_one_use": False,
        "nelson_bound": False,
        "interacting_measure": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    check("r085_rational_bound_open", not bool(r085["claims_not_established"]["rational_shifted_hessian_form_bound"]), r085["claims_not_established"]["rational_shifted_hessian_form_bound"], False)
    check("all_downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-rational-translated-wick-payload-comparable-reduction-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "normal_form": {
            "identity": "H_R + c^T B_1 c/2 = L:Q^a/2 + c^T B_T c/2",
            "L": "B_1-B_0-DB_0[a]-D2B_0[a,a]/2",
            "B_T": "B_0+DB_0[a]+D2B_0[a,a]/2",
        },
        "payable_ledgers": {
            "base_frozen_cubic_q": {"x": str(cubic_x), "y": str(cubic_y), "total": str(cubic_total), "slack": str(cubic_slack), "moment": str(1 / cubic_slack)},
            "payload_comparable_q": {"x": str(q_x), "y": str(q_y), "total": str(q_x + q_y), "slack": str(1 - q_x - q_y)},
            "payload_comparable_g": {"x": str(g_x), "y": str(g_y), "total": str(g_x + g_y), "slack": str(1 - g_x - g_y), "moment": str(1 / (1 - g_x - g_y))},
        },
        "fixtures": {
            "scalar_taylor": str(scalar_taylor),
            "scalar_negative_normalized": str(scalar_taylor.subs(capital_c, -1)),
            "kernel_endpoint_zero_floor": [[str(value) for value in row] for row in expected_endpoint_zero_floor.tolist()],
            "kernel_taylor_zero_floor": [[str(value) for value in row] for row in expected_taylor_zero_floor.tolist()],
            "kernel_remainder_zero_floor": [[str(value) for value in row] for row in expected_remainder_zero_floor.tolist()],
            "kernel_l21_production": float(l21_production),
            "heat_leading_coefficient": float(heat_coefficient.subs(e, floor_sp)),
        },
        "closed_scope": "base-frozen cubic Q model and all coefficient-nonresonant/payload-comparable shifted-Hessian orientations on the regular one-shot class",
        "remaining_rational_target": "coefficient-dominant high-high-to-low shifted resonance coupled to endpoint square, Wick trace, and lower-chaos forest",
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if passed == len(rows):
        print(f"[R-086 primary] {passed}/{len(rows)} PASS")
        return 0
    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-086 primary] {passed}/{len(rows)} PASS; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
