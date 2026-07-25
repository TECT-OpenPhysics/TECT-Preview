#!/usr/bin/env python3
"""Non-importing independent audit for the R-085 A13 reduction.

The audit uses high-precision numerical differentiation and direct finite
triangular sums rather than the primary script's symbolic derivative route.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

import mpmath as mp

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY"
MODEL = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
OUTPUT = REPO / f"claims/{CLAIM}/runs/2026-07-25-independent-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json"


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


def outer(left: list[mp.mpf], right: list[mp.mpf]) -> list[list[mp.mpf]]:
    return [[a * b for b in right] for a in left]


def matrix_add(*matrices: list[list[mp.mpf]]) -> list[list[mp.mpf]]:
    return [[sum(matrix[i][j] for matrix in matrices) for j in range(len(matrices[0][0]))] for i in range(len(matrices[0]))]


def matrix_scale(scale: mp.mpf, matrix: list[list[mp.mpf]]) -> list[list[mp.mpf]]:
    return [[scale * value for value in row] for row in matrix]


def contraction(left: list[list[mp.mpf]], right: list[list[mp.mpf]]) -> mp.mpf:
    return sum(left[i][j] * right[i][j] for i in range(len(left)) for j in range(len(left[0])))


def quadratic(vector: list[mp.mpf], matrix: list[list[mp.mpf]], other: list[mp.mpf] | None = None) -> mp.mpf:
    right = vector if other is None else other
    return sum(vector[i] * matrix[i][j] * right[j] for i in range(len(vector)) for j in range(len(right)))


def directional_derivative(function: Callable[[mp.mpf], mp.mpf], order: int) -> mp.mpf:
    return mp.diff(function, mp.mpf("0"), order)


def main() -> int:
    mp.mp.dps = 80
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if isinstance(actual, mp.mpf):
            actual = mp.nstr(actual, 30)
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    model = json.loads(MODEL.read_text(encoding="utf-8"))
    parameters = model["parameters"]
    floor = mp.mpf(str(parameters["rho_regularizer"]))
    denominator = mp.mpf(str(parameters["M_X"])) ** 2 + floor
    b_weight = mp.mpf(str(parameters["cJK"])) * mp.mpf(str(parameters["alpha_X"])) * mp.mpf(str(parameters["beta_X"])) / denominator
    c_weight = mp.mpf(str(parameters["cKK"])) * mp.mpf(str(parameters["beta_X"])) ** 2 / denominator
    pf_alpha = c_weight / (b_weight + c_weight)

    check("model_schema", model.get("schema") == "tect/a1-production-functional-realisation/1.0", model.get("schema"), "tect/a1-production-functional-realisation/1.0")
    check("production_floor", floor == mp.mpf(1) / 10**12, floor, "1e-12")
    check("pf_alpha", abs(pf_alpha - mp.mpf(5) / 9) < mp.mpf("1e-70"), pf_alpha, "5/9")

    # Independent evaluation of the weighted Schur constant.
    field_alpha = mp.mpf(2) / 5
    s = mp.mpf(7) / 12
    eta = mp.mpf(1) / 12
    margin = 2 * s - 1
    constant = 1 / ((1 - mp.power(2, -eta)) * (1 - mp.power(2, -2 * s)) * (1 - mp.power(2, 1 + eta - 2 * s)))
    tolerance = mp.mpf("1e-70")
    check("first_gain", abs((3 * field_alpha - 1) - mp.mpf(1) / 5) < tolerance, 3 * field_alpha - 1, "1/5")
    check("candidate_gain", abs((4 * field_alpha - 1) - mp.mpf(3) / 5) < tolerance, 4 * field_alpha - 1, "3/5")
    check("strict_s_window", mp.mpf(1) / 2 < s < 4 * field_alpha - 1, s, "1/2<s<3/5")
    check("eta_window", 0 < eta < margin, eta, "0<eta<2s-1")
    check("balanced_eta", abs(eta - margin / 2) < tolerance, eta, "(2s-1)/2")
    check("constant_interval", mp.mpf(572) < constant < mp.mpf(573), constant, "(572,573)")

    # A direct finite-vector stress test with changing signs and two coordinates.
    ratios: list[float] = []
    for gap, maximum in ((1, 5), (2, 7), (4, 9), (6, 11)):
        q = [mp.power(2, -k) * (1 + mp.mpf(k % 3) / 5) for k in range(maximum + 1)]
        total = mp.mpf("0")
        for m in range(gap, maximum + gap + 1):
            for j in range(m - gap + 1):
                vector = [mp.mpf("0"), mp.mpf("0")]
                for k in range(j + 1):
                    amplitude = mp.power(2, -s * (m - k)) * mp.sqrt(q[k])
                    direction = [mp.mpf(1), mp.mpf((-1) ** (j + k)) / 3]
                    vector = [vector[index] + amplitude * direction[index] / mp.sqrt(mp.mpf(10) / 9) for index in range(2)]
                total += mp.power(2, j) * quadratic(vector, [[1, 0], [0, 1]])
        bound = constant * mp.power(2, -2 * s * gap) * sum(mp.power(2, k) * q[k] for k in range(maximum + 1))
        ratio = total / bound
        ratios.append(float(ratio))
        check(f"vector_schur_C{gap}_M{maximum}", ratio <= 1, ratio, "<=1")

    critical_20 = sum((mp.power(2, m - 1) - 1) * mp.power(2, -m) for m in range(2, 21))
    critical_40 = sum((mp.power(2, m - 1) - 1) * mp.power(2, -m) for m in range(2, 41))
    check("critical_growth", critical_40 > 2 * critical_20 - 1, critical_40 / critical_20, "approximately linear")

    # Independent high-precision derivatives of the normalized rational Gram.
    alpha = mp.mpf(5) / 9

    def gram_at(z0: mp.mpf, z1: mp.mpf) -> list[list[mp.mpf]]:
        density = z0 * z0 + z1 * z1 + floor
        radius = z0 * z0
        g = [z0 - alpha * radius * z0 / density, -alpha * radius * z1 / density]
        return outer(g, g)

    base = [mp.mpf(1), mp.mpf(1)]
    shift = [mp.mpf(1), mp.mpf(-1)]
    endpoint = [base[index] + shift[index] for index in range(2)]
    gram_base = gram_at(*base)
    gram_endpoint = gram_at(*endpoint)
    first = [[mp.mpf("0") for _ in range(2)] for _ in range(2)]
    second = [[mp.mpf("0") for _ in range(2)] for _ in range(2)]
    for i in range(2):
        for j in range(2):
            path = lambda t, ii=i, jj=j: gram_at(base[0] + t * shift[0], base[1] + t * shift[1])[ii][jj]
            first[i][j] = directional_derivative(path, 1)
            second[i][j] = directional_derivative(path, 2)
    remainder = matrix_add(gram_endpoint, matrix_scale(-1, gram_base), matrix_scale(-1, first), matrix_scale(mp.mpf(-1) / 2, second))
    determinant = remainder[0][0] * remainder[1][1] - remainder[0][1] * remainder[1][0]
    trace = remainder[0][0] + remainder[1][1]

    check("gram_symmetry", abs(gram_base[0][1] - gram_base[1][0]) < mp.mpf("1e-70"), gram_base[0][1] - gram_base[1][0], "0")
    check("remainder_symmetry", abs(remainder[0][1] - remainder[1][0]) < mp.mpf("1e-65"), remainder[0][1] - remainder[1][0], "0")
    check("remainder_nonzero", max(abs(value) for row in remainder for value in row) > mp.mpf("1e-3"), max(abs(value) for row in remainder for value in row), ">1e-3")
    check("remainder_indefinite", determinant < 0, determinant, "<0")
    check("remainder_positive_trace", trace > 0, trace, ">0")

    derivative = [mp.mpf(1) / 10, mp.mpf(1)]
    q_tensor = outer(derivative, derivative)
    hidden_q = mp.mpf(1) / 2 * contraction(remainder, q_tensor)
    check("hidden_q_negative", hidden_q < 0, hidden_q, "<0")
    check("hidden_q_matches_primary_value", abs(hidden_q + mp.mpf("0.0021604938271616512346")) < mp.mpf("1e-21"), hidden_q, "-0.0021604938271616512346")

    control = [mp.mpf(1) / 3, -mp.mpf(1) / 4]
    translated = [derivative[index] + control[index] for index in range(2)]
    exact_delta = mp.mpf(1) / 2 * quadratic(translated, gram_endpoint) - mp.mpf(1) / 2 * quadratic(derivative, gram_base)
    endpoint_split = (
        mp.mpf(1) / 2 * contraction(matrix_add(gram_endpoint, matrix_scale(-1, gram_base)), q_tensor)
        + quadratic(derivative, gram_endpoint, control)
        + mp.mpf(1) / 2 * quadratic(control, gram_endpoint)
    )
    five = (
        mp.mpf(1) / 2 * contraction(first, q_tensor)
        + mp.mpf(1) / 4 * contraction(second, q_tensor)
        + quadratic(derivative, gram_base, control)
        + quadratic(derivative, first, control)
        + mp.mpf(1) / 2 * quadratic(derivative, second, control)
    )
    hidden = mp.mpf(1) / 2 * contraction(remainder, q_tensor) + quadratic(derivative, remainder, control)
    square = mp.mpf(1) / 2 * quadratic(control, gram_endpoint)
    check("endpoint_split", abs(exact_delta - endpoint_split) < mp.mpf("1e-65"), exact_delta - endpoint_split, "0")
    check("five_hidden_square_split", abs(exact_delta - five - hidden - square) < mp.mpf("1e-65"), exact_delta - five - hidden - square, "0")
    check("hidden_pair_nonzero", abs(hidden) > mp.mpf("1e-6"), hidden, "nonzero")
    check("retained_square_nonnegative", square >= 0, square, ">=0")

    # Direct numerical differentiation of the production scalar ray.
    c1 = mp.mpf(243) / (mp.mpf(8000) * denominator)

    def scalar_gram(value: mp.mpf) -> mp.mpf:
        scalar_g = value - alpha * value**3 / (value**2 + floor)
        return 4 * c1 * scalar_g**2

    third_numeric = mp.diff(scalar_gram, mp.sqrt(floor), 3)
    third_formula = 6 * alpha**2 * c1 / mp.sqrt(floor)
    check("scalar_third_derivative_formula", abs(third_numeric - third_formula) < mp.mpf("1e-60"), third_numeric - third_formula, "0")
    check("scalar_third_derivative_interval", mp.mpf(14062) < third_numeric < mp.mpf(14063), third_numeric, "(14062,14063)")

    q22 = c1 * alpha**2
    d0 = 2 + floor
    fixture_f0 = 2 * q22 / d0**2
    fixture_dr = -2 * q22 * (8 * (floor + 1) - 5 * floor - 2) / d0**3
    check("fixed_schur_ratio", abs(fixture_dr / fixture_f0 + 3) < tolerance, fixture_dr / fixture_f0, "-3")
    check("fixed_schur_sign", fixture_f0 > 0 and fixture_dr < 0, [float(fixture_f0), float(fixture_dr)], "F0>0 and DR<0")

    degrees = [mp.mpf(7) / 20, mp.mpf(7) / 10, mp.mpf(13) / 30, mp.mpf(3) / 5, mp.mpf(23) / 30]
    check("five_degrees_subcritical", max(degrees) < 1, max(degrees), "23/30<1")
    check("worst_slack", abs((1 - max(degrees)) - mp.mpf(7) / 30) < tolerance, 1 - max(degrees), "7/30")
    check("worst_moment", abs(1 / (1 - max(degrees)) - mp.mpf(30) / 7) < tolerance, 1 / (1 - max(degrees)), "30/7")

    epsilon_v = mp.mpf(45) / 100
    q_nelson = 1 / (2 * epsilon_v)
    p = mp.mpf(11) / 10
    check("q_nelson", q_nelson == mp.mpf(10) / 9, q_nelson, "10/9")
    check("q_minus_p", abs((q_nelson - p) - mp.mpf(1) / 90) < tolerance, q_nelson - p, "1/90")
    sextic_reserve = mp.mpf(27) / 100 - mp.mpf(6) / 100 - mp.mpf(15) / 100
    check("sextic_reserve", abs(sextic_reserve - mp.mpf(6) / 100) < tolerance, sextic_reserve, "3/50")
    control_reserve = 1 / (2 * p) - epsilon_v
    check("control_reserve", abs(control_reserve - mp.mpf(1) / 220) < tolerance, control_reserve, "1/220")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-nonorthogonal-cartan-schur-rational-hessian-boundary-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "schur_constant": float(constant),
        "finite_vector_fixture_ratios": ratios,
        "rational_remainder": [[float(value) for value in row] for row in remainder],
        "rational_remainder_determinant": float(determinant),
        "hidden_q_pair": float(hidden_q),
        "scalar_third_derivative": float(third_numeric),
        "fixed_schur_fixture": {"C": 2, "F0": float(fixture_f0), "DR": float(fixture_dr), "ratio": float(fixture_dr / fixture_f0)},
        "proved_scope": "independent high-precision confirmation of the weighted Schur implication, exact rational shifted-Hessian boundary, and synthesis arithmetic",
        "claims_not_established": {
            "production_cartan_atom_estimate": False,
            "rational_shifted_hessian_form_bound": False,
            "complete_regular_packet_lower_bound": False,
            "full_progressive_revisit_extension": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "sector_a_closure": False,
        },
    }
    atomic_json(OUTPUT, payload)
    if passed == len(rows):
        print(f"[R-085 independent] {passed}/{len(rows)} PASS")
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-085 independent] {passed}/{len(rows)} PASS; failures={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
