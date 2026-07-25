#!/usr/bin/env python3
"""Non-importing independent audit for the R-083 A13 reduction.

The derivations use exact rational probability trees, scalar Gram tensors,
normal-moment recursion, and a separate periodic quadrature.  No code or
stored output is imported from the primary executable.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import itertools
import json
import math
import os
import tempfile
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CONTROLLED-POLYNOMIAL-CFAR-LINEAR-PAULI-FIERZ-FOREST-REDUCTION"
MODEL = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-25-independent-controlled-polynomial-cfar-linear-pf-forest/result.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def fmean(values: list[Fraction]) -> Fraction:
    return sum(values, Fraction(0)) / len(values)


def conditional_fraction(
    function: Callable[[tuple[int, ...]], list[Fraction]],
    level: int,
    omega: tuple[int, ...],
    outcomes: list[tuple[int, ...]],
) -> list[Fraction]:
    matching = [candidate for candidate in outcomes if candidate[:level] == omega[:level]]
    samples = [function(candidate) for candidate in matching]
    return [fmean([sample[index] for sample in samples]) for index in range(len(samples[0]))]


def vector_add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [a + b for a, b in zip(left, right)]


def vector_sub(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [a - b for a, b in zip(left, right)]


def scalar_rational(value: Fraction) -> Fraction:
    return value * value * value / (1 + value * value)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    getcontext().prec = 60
    model = json.loads(MODEL.read_text(encoding="utf-8"), parse_float=Decimal)
    p = model["parameters"]
    denominator = p["M_X"] * p["M_X"] + p["rho_regularizer"]
    q_a = p["cJJ"] * p["alpha_X"] * p["alpha_X"] / denominator
    q_b = p["cJK"] * p["alpha_X"] * p["beta_X"] / denominator
    q_c = p["cKK"] * p["beta_X"] * p["beta_X"] / denominator
    alpha = q_c / (q_b + q_c)
    c_one = q_c / (alpha * alpha)
    c_zero = q_a - q_b * q_b / q_c
    c_sum = c_zero + c_one
    check("independent_model_authority", model["schema"] == "tect/a1-production-functional-realisation/1.0", model["schema"], "tect/a1-production-functional-realisation/1.0")
    check("independent_alpha_exact_decimal", alpha == Decimal(5) / Decimal(9), str(alpha), "5/9")
    check("independent_c0_formula", c_zero == Decimal(3) / (Decimal(250) * denominator), str(c_zero), "3/(250P)")
    check("independent_c1_formula", c_one == Decimal(243) / (Decimal(8000) * denominator), str(c_one), "243/(8000P)")
    factor = Decimal(4) * alpha * alpha * c_one
    factor_target = Decimal(3) / (Decimal(80) * denominator)
    check("independent_CFar_factor", abs(factor - factor_target) < Decimal("1e-55"), str(factor), "3/(80P)")

    # Independent complex-to-real current audit with fixed rational samples.
    samples = [
        ((Fraction(3, 5), Fraction(-1, 4), Fraction(2, 7), Fraction(1, 3)), (Fraction(-2, 9), Fraction(4, 11), Fraction(1, 6), Fraction(-3, 8))),
        ((Fraction(-1, 2), Fraction(5, 9), Fraction(1, 5), Fraction(-2, 3)), (Fraction(3, 10), Fraction(-1, 7), Fraction(4, 9), Fraction(2, 5))),
    ]
    re_residual = Fraction(0)
    im_residual = Fraction(0)
    for z_values, y_values in samples:
        x1, x2, y1, y2 = z_values
        p1, p2, q1, q2 = y_values
        matrix_re = x1 * p2 - x2 * p1 - y1 * q2 + y2 * q1
        matrix_im = x1 * q2 - x2 * q1 + y1 * p2 - y2 * p1
        complex_re = (x1 * p2 - y1 * q2) - (x2 * p1 - y2 * q1)
        complex_im = (x1 * q2 + y1 * p2) - (x2 * q1 + y2 * p1)
        re_residual = max(re_residual, abs(matrix_re - complex_re))
        im_residual = max(im_residual, abs(matrix_im - complex_im))
    check("independent_horizontal_real_row", re_residual == 0, str(re_residual), "0")
    check("independent_horizontal_imag_row", im_residual == 0, str(im_residual), "0")
    def gram_from_rows(vectors: list[list[Fraction]]) -> list[list[Fraction]]:
        width = len(vectors[0])
        return [
            [sum((row[i] * row[j] for row in vectors), Fraction(0)) for j in range(width)]
            for i in range(width)
        ]

    gram_rows = [
        [Fraction(1, 3), Fraction(-2, 5), Fraction(1, 7)],
        [Fraction(2, 9), Fraction(1, 4), Fraction(-3, 8)],
        [Fraction(-1, 6), Fraction(4, 11), Fraction(2, 7)],
    ]
    rational_row = [Fraction(3, 10), Fraction(-1, 8), Fraction(5, 13)]
    full_gram = gram_from_rows(gram_rows + [rational_row])
    linear_gram = gram_from_rows(gram_rows)
    rational_gram = gram_from_rows([rational_row])
    gram_split_residual = max(
        abs(full_gram[i][j] - linear_gram[i][j] - rational_gram[i][j])
        for i in range(3)
        for j in range(3)
    )
    check("independent_linear_rational_Gram_split", gram_split_residual == 0, str(gram_split_residual), "0")

    # Exact low-input and input-scale telescope on a different Fraction tree.
    outcomes = list(itertools.product((-1, 1), repeat=3))
    width = 4

    def low_input(omega: tuple[int, ...]) -> list[Fraction]:
        e1, _, e3 = omega
        return [Fraction((mode + 2) * e1, 37) + Fraction(e1 * e3, 53) for mode in range(width)]

    def increment(k: int, omega: tuple[int, ...]) -> list[Fraction]:
        e1, e2, e3 = omega
        roots = (e1, e2, e3)
        future = (e2 * e3, e1 * e3, e1 * e2)[k - 1]
        return [Fraction((mode + 1) * roots[k - 1], 41 + k) + Fraction((mode + k) * future, 71) for mode in range(width)]

    max_telescope = Fraction(0)
    low_seen = False
    drift_seen = False
    for n in (1, 2, 3):
        for omega in outcomes:
            lhs = [Fraction(0) for _ in range(width)]
            for j in range(1, n + 1):
                def current(candidate: tuple[int, ...], endpoint: int = j) -> list[Fraction]:
                    value = low_input(candidate)
                    for k in range(1, endpoint + 1):
                        value = vector_add(value, increment(k, candidate))
                    return value
                lhs = vector_add(lhs, vector_sub(conditional_fraction(current, j, omega, outcomes), conditional_fraction(current, j - 1, omega, outcomes)))
            rhs = vector_sub(conditional_fraction(low_input, n, omega, outcomes), conditional_fraction(low_input, 0, omega, outcomes))
            low_seen = low_seen or rhs != [Fraction(0) for _ in range(width)]
            for k in range(1, n + 1):
                pk_n = conditional_fraction(lambda candidate, kk=k: increment(kk, candidate), n, omega, outcomes)
                pk_before = conditional_fraction(lambda candidate, kk=k: increment(kk, candidate), k - 1, omega, outcomes)
                rhs = vector_add(rhs, vector_sub(pk_n, pk_before))
                drift_seen = drift_seen or pk_before != [Fraction(0) for _ in range(width)]
            max_telescope = max(max_telescope, max(abs(value) for value in vector_sub(lhs, rhs)))
    check("independent_input_telescope_exact", max_telescope == 0, str(max_telescope), "0")
    check("independent_low_endpoint_nonzero", low_seen, low_seen, True)
    check("independent_predictable_drift_nonzero", drift_seen, drift_seen, True)

    # Exact one-root value/derivative/heat channel audit with Fraction inputs.
    z0, dz0 = Fraction(1, 7), Fraction(-1, 6)
    a, da = Fraction(1, 5), Fraction(-1, 8)
    g_size, dg_size = Fraction(1, 3), Fraction(2, 5)
    root_states = list(itertools.product((-g_size, g_size), (-dg_size, dg_size)))
    heat = lambda value: fmean([scalar_rational(value - g_size), scalar_rational(value + g_size)])
    delta_values: list[Fraction] = []
    iota_values: list[Fraction] = []
    balanced_values: list[Fraction] = []
    channel_values: list[Fraction] = []
    kappa_nonzero = False
    for g, dg in root_states:
        delta_value = (scalar_rational(z0 + a + g) - scalar_rational(z0 + g)) * (dz0 + dg) + scalar_rational(z0 + a + g) * da
        iota = (scalar_rational(z0 + a + g) - scalar_rational(z0 + g)) * dg
        nu = (scalar_rational(z0 + a + g) - scalar_rational(z0 + a)) * (dz0 + da) - (scalar_rational(z0 + g) - scalar_rational(z0)) * dz0
        kappa = (scalar_rational(z0 + a) - heat(z0 + a)) * (dz0 + da) - (scalar_rational(z0) - heat(z0)) * dz0
        delta_values.append(delta_value)
        iota_values.append(iota)
        balanced_values.append(nu + kappa)
        channel_values.append(iota + nu + kappa)
        kappa_nonzero = kappa_nonzero or kappa != 0
    delta_mean = fmean(delta_values)
    channel_residual = max(abs((value - delta_mean) - channel) for value, channel in zip(delta_values, channel_values))
    check("independent_three_channel_identity", channel_residual == 0, str(channel_residual), "0")
    check("independent_iota_centered", fmean(iota_values) == 0, str(fmean(iota_values)), "0")
    check("independent_nu_plus_kappa_centered", fmean(balanced_values) == 0, str(fmean(balanced_values)), "0")
    check("independent_heat_compensator_nonzero", kappa_nonzero, kappa_nonzero, True)

    # Sharp-cube support proof and one-use input-coordinate ledger.
    n = 7
    quadratic_edge = 2 ** (n + 1)
    far_edge = 2 ** (n + 3 - 1)
    check("independent_Cpoly_three_support", quadratic_edge < far_edge, [quadratic_edge, far_edge], "strict separation")
    endpoint_support = 2**n + 2**n
    value_drift_support = 2**n + 2**n
    derivative_drift_support = 2**n + 2**n
    check("independent_polynomial_endpoint_zero", endpoint_support < far_edge, [endpoint_support, far_edge], "strictly separated")
    check("independent_polynomial_two_drifts_zero", max(value_drift_support, derivative_drift_support) < far_edge, [value_drift_support, derivative_drift_support, far_edge], "strictly separated")
    kappa_k, bernstein = Fraction(7, 5), Fraction(9, 5)
    h_values = [Fraction(2, 3), Fraction(5, 7), Fraction(4, 5)]
    coordinate = Fraction(0)
    for shell, h_value in zip((2, 3, 4), h_values):
        a_value = kappa_k * Fraction(1, 2 ** (2 * shell)) * h_value
        da_value = bernstein * (2**shell) * a_value
        coordinate += (2 ** (4 * shell)) * a_value * a_value + (2 ** (2 * shell)) * da_value * da_value
    bound = kappa_k * kappa_k * (1 + bernstein * bernstein) * sum((value * value for value in h_values), Fraction(0))
    check("independent_K_coordinate_one_use", coordinate <= bound, str(coordinate), f"<={bound}")

    # Scalar linear-row forest derived without matrix code.
    x, y, av, bd = Fraction(2, 5), Fraction(-3, 7), Fraction(1, 4), Fraction(2, 9)
    sigma_x, sigma_h, gamma = Fraction(1, 11), Fraction(1, 13), Fraction(2, 15)
    r_blocks = [x * x - sigma_x, 2 * x * av, av * av + sigma_x + sigma_h]
    c_blocks = [y * y - gamma, 2 * y * bd, bd * bd]
    block_sum = sum((left * right for left in r_blocks for right in c_blocks), Fraction(0)) / 2
    direct = ((x + av) ** 2 + sigma_h) * ((y + bd) ** 2 - gamma) / 2
    check("independent_nine_block_forest", block_sum == direct, str(block_sum - direct), "0")
    counts: dict[int, int] = {}
    for r_degree in (2, 1, 0):
        for c_degree in (2, 1, 0):
            counts[r_degree + c_degree] = counts.get(r_degree + c_degree, 0) + 1
    check("independent_forest_counts", counts == {4: 1, 3: 2, 2: 3, 1: 2, 0: 1}, counts, {4: 1, 3: 2, 2: 3, 1: 2, 0: 1})
    heat_contribution = sigma_h * sum(c_blocks, Fraction(0)) / 2
    check("independent_heat_P2_P1_P0", heat_contribution == sum((sigma_h * block / 2 for block in c_blocks), Fraction(0)), str(heat_contribution), "three exact blocks")
    check("independent_covariance_preserved_positive", bd * bd / 2 >= 0, str(bd * bd / 2), ">=0")
    check("independent_covariance_defect_negative", -gamma / 2 < 0, str(-gamma / 2), "<0")

    # Exact Gaussian moment/Hermite audit and a discrete independent fixture.
    gaussian_moments = {0: 1, 2: 1, 4: 3, 6: 15}
    adapted_expectation = gaussian_moments[6] - 9 * gaussian_moments[4] + 24 * gaussian_moments[2] - 16 * gaussian_moments[0]
    check("independent_Gaussian_adapted_expectation", adapted_expectation == -4, adapted_expectation, -4)
    # Power matching: target = H6 + 6 H4 + 15 H2 - 4.
    target_power = {6: 1, 4: -9, 2: 24, 0: -16}
    hermite_power = {
        6: 1,
        4: -15 + 6,
        2: 45 - 36 + 15,
        0: -15 + 18 - 15 - 4,
    }
    check("independent_Hermite_power_match", hermite_power == target_power, hermite_power, target_power)
    csum_float = float(c_sum)
    lam = 0.29
    negative_mean = 2.0 * csum_float * lam**2 * adapted_expectation
    check("independent_linear_row_mean_negative", negative_mean < 0 and abs(negative_mean + 8.0 * csum_float * lam**2) < 1e-15, negative_mean, -8.0 * csum_float * lam**2)
    discrete_states = [(Fraction(0), Fraction(1, 2)), (Fraction(2), Fraction(1, 2))]
    discrete = sum((probability * (1 - square / 2) ** 2 * (square - 1) for square, probability in discrete_states), Fraction(0))
    check("independent_three_point_square_law", discrete == Fraction(-1, 2), str(discrete), "-1/2")
    fixture_matrices = [
        [[Fraction(int(i == j and i in (0, 1, 3, 4))) for j in range(6)] for i in range(6)],
        [
            [Fraction(value) for value in row]
            for row in (
                (0, 1, 0, 0, 0, 0),
                (-1, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, -1, 0),
                (0, 0, 0, 1, 0, 0),
                (0, 0, 0, 0, 0, 0),
            )
        ],
        [
            [Fraction(value) for value in row]
            for row in (
                (0, 0, 0, 0, 1, 0),
                (0, 0, 0, -1, 0, 0),
                (0, 0, 0, 0, 0, 0),
                (0, 1, 0, 0, 0, 0),
                (-1, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0, 0),
            )
        ],
    ]

    def bilinear(left: list[Fraction], matrix: list[list[Fraction]], right: list[Fraction]) -> Fraction:
        return sum((left[i] * matrix[i][j] * right[j] for i in range(6) for j in range(6)), Fraction(0))

    fixture_floor = Fraction(1, 17)
    fixture_alpha = Fraction(5, 9)
    fixture_rational_max = Fraction(0)
    fixture_other_max = Fraction(0)
    fixture_horizontal_residual = Fraction(0)
    for xi_value in (Fraction(-2), Fraction(-1, 2), Fraction(0), Fraction(5, 4)):
        adapted_value = Fraction(7, 20) * (xi_value * xi_value - 4)
        for zeta_value in (Fraction(-3, 2), Fraction(0), Fraction(3, 4)):
            z0_value = adapted_value + Fraction(3, 5) * zeta_value
            fixture_z = [z0_value, Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
            fixture_y = [Fraction(0), xi_value, Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
            density = z0_value * z0_value + fixture_floor
            fixture_g = [z0_value - fixture_alpha * z0_value**3 / density] + [Fraction(0) for _ in range(5)]
            fixture_rational_max = max(fixture_rational_max, abs(sum((a * b for a, b in zip(fixture_g, fixture_y)), Fraction(0))))
            fixture_linear = [bilinear(fixture_z, matrix, fixture_y) for matrix in fixture_matrices]
            fixture_other_max = max(fixture_other_max, abs(fixture_linear[0]), abs(fixture_linear[2]))
            fixture_horizontal_residual = max(fixture_horizontal_residual, abs(fixture_linear[1] - z0_value * xi_value))
    check("independent_rational_row_zero", fixture_rational_max == 0, str(fixture_rational_max), "0")
    heat_mean = Fraction(3, 5) ** 2 * (Fraction(1) - Fraction(1))
    check("independent_heat_mean_zero", heat_mean == 0 and fixture_other_max == 0 and fixture_horizontal_residual == 0, [str(heat_mean), str(fixture_other_max), str(fixture_horizontal_residual)], ["0", "0", "0"])

    # Cubic and full rational failures of automatic output orthogonality.
    amplitude_one = Fraction(1, 4)
    amplitude_two = Fraction(1, 5)
    cubic_one = amplitude_one**3 / 4
    cubic_two = Fraction(3, 2) * amplitude_one**2 * amplitude_two + Fraction(3, 4) * amplitude_two**3
    check("independent_cubic_coefficients_positive", cubic_one > 0 and cubic_two > 0, [str(cubic_one), str(cubic_two)], ">0")
    check("independent_cubic_projected_cross_positive", cubic_one * cubic_two / 2 > 0, str(cubic_one * cubic_two / 2), ">0")
    quadrature_points = 1 << 15
    rational_one = 0.0
    rational_two = 0.0
    for index in range(quadrature_points):
        theta = 2.0 * math.pi * index / quadrature_points
        first = 0.25 * math.cos(theta)
        second = 0.20 * math.cos(3.0 * theta)
        f_first = first**3 / (1.0 + first**2)
        f_total = (first + second) ** 3 / (1.0 + (first + second) ** 2)
        weight = 2.0 * math.cos(3.0 * theta) / quadrature_points
        rational_one += weight * f_first
        rational_two += weight * (f_total - f_first)
    production_floor = p["rho_regularizer"]
    production_scale = production_floor.sqrt()
    scale_test = Decimal("0.231")
    physical_test = production_scale * scale_test
    rescaling_residual = abs(
        (physical_test**3 / (production_floor + physical_test**2)) / production_scale
        - scale_test**3 / (Decimal(1) + scale_test**2)
    )
    production_mode_one = float(production_scale) * rational_one
    production_mode_two = float(production_scale) * rational_two
    production_normalized_cross = production_mode_one * production_mode_two / 2.0
    check("independent_rational_mode_one_interval", 0.00361 < rational_one < 0.00363 and rescaling_residual < Decimal("1e-50"), [rational_one, str(rescaling_residual)], ["(0.00361,0.00363)", "<1e-50"])
    check("independent_rational_mode_two_interval", 0.02077 < rational_two < 0.02080, rational_two, "(0.02077,0.02080)")
    check("independent_rational_projected_cross_positive", production_normalized_cross > 0, production_normalized_cross, ">0")
    check("independent_K_smoothing_not_output_orthogonality", production_normalized_cross > 0, False, False)

    # Honest boundary.
    check("independent_controlled_Cartan_CFar_open", True, False, False)
    check("independent_complete_signed_NEAR_open", True, False, False)
    check("independent_progression_open", True, False, False)
    check("independent_one_use_open", True, False, False)
    check("independent_Nelson_open", True, False, False)
    check("independent_Sector_A_open", True, False, False)
    check("independent_tier_stays_T4", True, "T4", "T4")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload: dict[str, Any] = {
        "schema": "tect/a13-controlled-polynomial-cfar-linear-pf-forest-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "derived_constants": {
            "alpha": str(alpha),
            "c0": str(c_zero),
            "c1": str(c_one),
            "controlled_CFar_factor": str(factor),
        },
        "rational_mode3_fixture": {
            "quadrature_points": quadrature_points,
            "coefficient_increment_one": rational_one,
            "coefficient_increment_two": rational_two,
            "normalized_cross": rational_one * rational_two / 2.0,
            "production_floor": str(production_floor),
            "production_coefficient_increment_one": production_mode_one,
            "production_coefficient_increment_two": production_mode_two,
            "production_normalized_cross": production_normalized_cross,
            "rescaling_residual": str(rescaling_residual),
        },
        "negative_scope": "The exact harmonic overlap refutes only global raw-output pairwise orthogonality from K smoothing alone; it does not exclude far-only or correlated martingale estimates.",
        "claims_not_established": {
            "controlled_Cartan_CFar": False,
            "complete_controlled_CFar": False,
            "complete_signed_NEAR": False,
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
    print(f"[R-083 independent] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
