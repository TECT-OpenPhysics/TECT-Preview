#!/usr/bin/env python3
"""Non-importing independent audit for the R-086 rational reduction.

This audit uses high-precision directional differentiation, direct numerical
matrix contractions, and Gauss--Hermite heat averages.  It imports no code
from the primary executable.
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
from typing import Any, Callable

import mpmath as mp
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RATIONAL-TRANSLATED-WICK-PAYLOAD-COMPARABLE-REDUCTION"
MODEL = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R085 = REPO / f"claims/{CLAIM}/classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json"
OUTPUT = REPO / f"claims/{CLAIM}/runs/2026-07-25-independent-rational-translated-wick-payload-comparable-reduction/result.json"


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
    return [[left[i] * right[j] for j in range(len(right))] for i in range(len(left))]


def matrix_add(*matrices: list[list[mp.mpf]]) -> list[list[mp.mpf]]:
    return [[sum(matrix[i][j] for matrix in matrices) for j in range(len(matrices[0][0]))] for i in range(len(matrices[0]))]


def matrix_scale(scale: mp.mpf, matrix: list[list[mp.mpf]]) -> list[list[mp.mpf]]:
    return [[scale * value for value in row] for row in matrix]


def contraction(left: list[list[mp.mpf]], right: list[list[mp.mpf]]) -> mp.mpf:
    return sum(left[i][j] * right[i][j] for i in range(len(left)) for j in range(len(left[0])))


def quadratic(left: list[mp.mpf], matrix: list[list[mp.mpf]], right: list[mp.mpf] | None = None) -> mp.mpf:
    target = left if right is None else right
    return sum(left[i] * matrix[i][j] * target[j] for i in range(len(left)) for j in range(len(target)))


def directional_matrix(function: Callable[[mp.mpf], list[list[mp.mpf]]], order: int) -> list[list[mp.mpf]]:
    sample = function(mp.mpf("0"))
    return [[mp.diff(lambda parameter: function(parameter)[i][j], mp.mpf("0"), order) for j in range(len(sample[0]))] for i in range(len(sample))]


def main() -> int:
    mp.mp.dps = 80
    rows: list[dict[str, Any]] = []

    def serial(value: Any) -> Any:
        if isinstance(value, mp.mpf):
            return mp.nstr(value, 35)
        if isinstance(value, list):
            return [serial(item) for item in value]
        return value

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": serial(actual), "expected": expected})

    model = json.loads(MODEL.read_text(encoding="utf-8"))
    r085 = json.loads(R085.read_text(encoding="utf-8"))
    parameters = model["parameters"]
    floor = mp.mpf(str(parameters["rho_regularizer"]))
    denominator = mp.mpf(str(parameters["M_X"])) ** 2 + floor
    b_weight = mp.mpf(str(parameters["cJK"])) * mp.mpf(str(parameters["alpha_X"])) * mp.mpf(str(parameters["beta_X"])) / denominator
    c_weight = mp.mpf(str(parameters["cKK"])) * mp.mpf(str(parameters["beta_X"])) ** 2 / denominator
    alpha = c_weight / (b_weight + c_weight)
    c1 = c_weight / alpha**2
    tolerance = mp.mpf("1e-60")

    check("model_schema", model.get("schema") == "tect/a1-production-functional-realisation/1.0", model.get("schema"), "tect/a1-production-functional-realisation/1.0")
    check("r085_predecessor", r085.get("result_id") == "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY", r085.get("result_id"), "R-085 result")
    check("production_floor", abs(floor - mp.mpf(1) / 10**12) < tolerance, floor, "1e-12")
    check("production_alpha", abs(alpha - mp.mpf(5) / 9) < tolerance, alpha, "5/9")
    check("production_c1", abs(c1 - (mp.mpf(243) / 8000) / denominator) < tolerance, c1, "243/[8000(4+e)]")

    # Five independent generic normal-form contractions.
    normal_residuals: list[mp.mpf] = []
    for seed in range(1, 6):
        l = [[mp.mpf(seed + 1) / 7, -mp.mpf(seed) / 11], [-mp.mpf(seed) / 11, mp.mpf(seed + 2) / 13]]
        bt = [[mp.mpf(seed + 3) / 5, mp.mpf(2 - seed) / 17], [mp.mpf(2 - seed) / 17, mp.mpf(seed + 4) / 9]]
        b1 = matrix_add(bt, l)
        g = [mp.mpf(seed) / 10, -mp.mpf(seed + 1) / 12]
        c = [-mp.mpf(seed + 2) / 14, mp.mpf(seed + 3) / 16]
        gamma = [[mp.mpf(3) / 8, mp.mpf(1) / 19], [mp.mpf(1) / 19, mp.mpf(5) / 12]]
        q = matrix_add(outer(g, g), matrix_scale(-1, gamma))
        translated = [g[index] + c[index] for index in range(2)]
        qa = matrix_add(outer(translated, translated), matrix_scale(-1, gamma))
        left = contraction(l, q) / 2 + quadratic(g, l, c) + quadratic(c, b1) / 2
        right = contraction(l, qa) / 2 + quadratic(c, bt) / 2
        residual = abs(left - right)
        normal_residuals.append(residual)
        check(f"normal_form_fixture_{seed}", residual < tolerance, residual, "<1e-60")

    # Independent fraction arithmetic.
    s_q = Fraction(11, 10)
    x_cubic = s_q / 2
    y_cubic = (Fraction(3) - s_q) / 6
    total_cubic = x_cubic + y_cubic
    slack_cubic = 1 - total_cubic
    check("cubic_x", x_cubic == Fraction(11, 20), str(x_cubic), "11/20")
    check("cubic_y", y_cubic == Fraction(19, 60), str(y_cubic), "19/60")
    check("cubic_total", total_cubic == Fraction(13, 15), str(total_cubic), "13/15")
    check("cubic_slack", slack_cubic == Fraction(2, 15), str(slack_cubic), "2/15")
    check("cubic_moment", 1 / slack_cubic == Fraction(15, 2), str(1 / slack_cubic), "15/2")
    check("cubic_young_powers", (x_cubic / slack_cubic, y_cubic / slack_cubic) == (Fraction(33, 8), Fraction(19, 8)), [str(x_cubic / slack_cubic), str(y_cubic / slack_cubic)], ["33/8", "19/8"])
    check("q_payload_ledger", Fraction(11, 20) + Fraction(3, 20) == Fraction(7, 10), str(Fraction(11, 20) + Fraction(3, 20)), "7/10")
    check("g_payload_ledger", Fraction(2, 5) + Fraction(11, 30) == Fraction(23, 30), str(Fraction(2, 5) + Fraction(11, 30)), "23/30")
    check("g_payload_moment", 1 / (1 - Fraction(23, 30)) == Fraction(30, 7), str(1 / (1 - Fraction(23, 30))), "30/7")

    # Scalar directional differentiation in dimensionless variables.
    def scalar_b(value: mp.mpf) -> mp.mpf:
        return (value - alpha * value**3 / (value**2 + 1)) ** 2

    b0 = scalar_b(mp.mpf(1))
    b_first = mp.diff(scalar_b, mp.mpf(1), 1)
    b_second = mp.diff(scalar_b, mp.mpf(1), 2)
    scalar_values: dict[str, mp.mpf] = {}
    for capital_c in (mp.mpf(-1), mp.mpf(2), mp.mpf(209)):
        taylor = b0 + b_first * capital_c + b_second * capital_c**2 / 2
        formula = (169 + 208 * capital_c - capital_c**2) / 324
        scalar_values[str(capital_c)] = taylor
        check(f"scalar_formula_C_{str(capital_c).replace('-', 'm')}", abs(taylor - formula) < tolerance, taylor - formula, "<1e-60")
    check("scalar_negative_minus_one", scalar_values["-1.0"] < 0 and abs(scalar_values["-1.0"] + mp.mpf(10) / 81) < tolerance, scalar_values["-1.0"], "-10/81")
    check("scalar_negative_209", scalar_values["209.0"] < 0 and abs(scalar_values["209.0"] + mp.mpf(10) / 81) < tolerance, scalar_values["209.0"], "-10/81")

    # Two-coordinate directional derivatives, independently evaluated.
    base = [mp.mpf(1), mp.mpf(1)]
    shift = [mp.mpf(1), mp.mpf(-1)]

    def gram_at(point: list[mp.mpf], local_floor: mp.mpf) -> list[list[mp.mpf]]:
        x, y = point
        density = x * x + y * y + local_floor
        radius = x * x
        g = [x - alpha * radius * x / density, -alpha * radius * y / density]
        return outer(g, g)

    def gram_path(parameter: mp.mpf, local_floor: mp.mpf) -> list[list[mp.mpf]]:
        return gram_at([base[index] + parameter * shift[index] for index in range(2)], local_floor)

    exact_matrices: dict[str, list[list[mp.mpf]]] = {}
    for local_floor, label in ((mp.mpf("0"), "zero"), (floor, "production")):
        gb = gram_path(mp.mpf("0"), local_floor)
        ge = gram_path(mp.mpf("1"), local_floor)
        d1 = directional_matrix(lambda parameter: gram_path(parameter, local_floor), 1)
        d2 = directional_matrix(lambda parameter: gram_path(parameter, local_floor), 2)
        bt = matrix_add(gb, d1, matrix_scale(mp.mpf("0.5"), d2))
        lr = matrix_add(ge, matrix_scale(-1, bt))
        exact_matrices[label] = lr
        identity_residual = max(abs(ge[i][j] - bt[i][j] - lr[i][j]) for i in range(2) for j in range(2))
        check(f"directional_taylor_identity_{label}", identity_residual < tolerance, identity_residual, "<1e-60")
        check(f"endpoint_kernel_{label}", max(abs(ge[i][1]) for i in range(2)) < tolerance, [ge[0][1], ge[1][1]], "zero second column")

    expected_l_zero = [[mp.mpf(65) / 81, -mp.mpf(5) / 81], [-mp.mpf(5) / 81, mp.mpf(0)]]
    zero_error = max(abs(exact_matrices["zero"][i][j] - expected_l_zero[i][j]) for i in range(2) for j in range(2))
    check("zero_floor_remainder_matrix", zero_error < tolerance, zero_error, "<1e-60")
    l21_formula = 5 * (27 * floor**2 + 40 * floor - 8) / (81 * (floor + 2) ** 3)
    check("production_l21_formula", abs(exact_matrices["production"][1][0] - l21_formula) < tolerance, exact_matrices["production"][1][0] - l21_formula, "<1e-60")
    check("production_l21_negative", exact_matrices["production"][1][0] < 0, exact_matrices["production"][1][0], "<0")

    # Independent Gauss--Hermite heat average of the lifted kernel entry.
    nodes, weights = np.polynomial.hermite.hermgauss(48)
    predicted = 4 * float(c1) * (20.0 / (9.0 * (4.0 + float(floor)))) ** 2
    heat_ratios: list[float] = []
    heat_errors: list[float] = []
    for sigma in (0.02, 0.01, 0.005):
        expectation = 0.0
        for i, node_x in enumerate(nodes):
            for j, node_y in enumerate(nodes):
                px = 2.0 + np.sqrt(2.0) * sigma * node_x
                py = np.sqrt(2.0) * sigma * node_y
                density = px * px + py * py + float(floor)
                g2 = -float(alpha) * px * px * py / density
                expectation += weights[i] * weights[j] * 4.0 * float(c1) * g2 * g2 / np.pi
        ratio = expectation / (sigma * sigma)
        error = abs(ratio - predicted)
        heat_ratios.append(ratio)
        heat_errors.append(error)
        check(f"heat_ratio_positive_{sigma}", ratio > 0, ratio, ">0")
    check("heat_ratio_converges", heat_errors[2] < heat_errors[1] < heat_errors[0], heat_errors, "strictly decreasing")
    check("heat_ratio_final_relative_error", heat_errors[-1] / predicted < 1e-4, heat_errors[-1] / predicted, "<1e-4")

    claims_not_established = {
        "coefficient_dominant_rational_packet": False,
        "complete_rational_near": False,
        "production_cartan_atom_estimate": False,
        "controlled_cartan_cfar": False,
        "complete_regular_packet_lower_bound": False,
        "overlap_uniform_bound": False,
        "full_progressive_revisit_extension": False,
        "controlled_shell_one_use": False,
        "nelson_bound": False,
        "sector_a_closure": False,
    }
    check("r085_bound_still_open", not bool(r085["claims_not_established"]["rational_shifted_hessian_form_bound"]), r085["claims_not_established"]["rational_shifted_hessian_form_bound"], False)
    check("downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-rational-translated-wick-payload-comparable-reduction-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "normal_form_max_residual": float(max(normal_residuals)),
        "cubic_ledger": {"x": str(x_cubic), "y": str(y_cubic), "total": str(total_cubic), "slack": str(slack_cubic), "moment": str(1 / slack_cubic)},
        "scalar_taylor_values": {key: float(value) for key, value in scalar_values.items()},
        "kernel_l21_production": float(exact_matrices["production"][1][0]),
        "heat": {"predicted_coefficient": predicted, "ratios": heat_ratios, "absolute_errors": heat_errors},
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if passed == len(rows):
        print(f"[R-086 independent] {passed}/{len(rows)} PASS")
        return 0
    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-086 independent] {passed}/{len(rows)} PASS; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
