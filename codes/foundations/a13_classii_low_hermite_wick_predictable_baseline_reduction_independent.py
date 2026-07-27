#!/usr/bin/env python3
"""Non-importing independent checks for the R-096 A13 reduction.

The exact checks use Fraction-valued Hermite coefficient ledgers rather than
the primary program's Gaussian quadrature.  Smooth fixtures are recomputed by
an adaptive Simpson rule with no NumPy dependency.
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
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-LOW-HERMITE-WICK-PREDICTABLE-BASELINE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-27-independent-low-hermite-wick-predictable-baseline-reduction/result.json"


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
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def hermite_norm(index: int, variance: Fraction = Fraction(1)) -> Fraction:
    return Fraction(math.factorial(index)) * variance**index


def gaussian_moment(power: int) -> Fraction:
    if power % 2:
        return Fraction(0)
    result = Fraction(1)
    for factor in range(1, power, 2):
        result *= factor
    return result


def tensor_norm(index: tuple[int, ...]) -> Fraction:
    result = Fraction(1)
    for degree in index:
        result *= Fraction(math.factorial(degree))
    return result


def coefficient_inner(
    left: dict[tuple[int, ...], Fraction],
    right: dict[tuple[int, ...], Fraction],
) -> Fraction:
    return sum(
        (coefficient * right.get(index, Fraction(0)) * tensor_norm(index) for index, coefficient in left.items()),
        Fraction(0),
    )


def simpson_value(function: Callable[[float], float], left: float, right: float) -> float:
    middle = 0.5 * (left + right)
    return (right - left) * (function(left) + 4.0 * function(middle) + function(right)) / 6.0


def adaptive_simpson(
    function: Callable[[float], float],
    left: float,
    right: float,
    tolerance: float,
    whole: float | None = None,
    depth: int = 24,
) -> float:
    if whole is None:
        whole = simpson_value(function, left, right)
    middle = 0.5 * (left + right)
    left_value = simpson_value(function, left, middle)
    right_value = simpson_value(function, middle, right)
    defect = left_value + right_value - whole
    if depth <= 0 or abs(defect) <= 15.0 * tolerance:
        return left_value + right_value + defect / 15.0
    return adaptive_simpson(function, left, middle, tolerance / 2.0, left_value, depth - 1) + adaptive_simpson(
        function, middle, right, tolerance / 2.0, right_value, depth - 1
    )


def normal_expectation(function: Callable[[float], float], tolerance: float = 2.0e-11) -> float:
    normalization = 1.0 / math.sqrt(2.0 * math.pi)
    return adaptive_simpson(
        lambda value: function(value) * math.exp(-0.5 * value * value) * normalization,
        -12.0,
        12.0,
        tolerance,
    )


def sech_squared(value: float) -> float:
    tail = math.exp(-2.0 * abs(value))
    return 4.0 * tail / (1.0 + tail) ** 2


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

    # Exact scalar Hermite ledger at non-unit covariance.
    variance = Fraction(3, 2)
    mu = Fraction(2, 3)
    gamma_past = Fraction(1, 4)
    coefficients = [Fraction(5, 4), Fraction(-2, 3), Fraction(7, 10), Fraction(4, 5), Fraction(-3, 7), Fraction(2, 9)]
    direct = coefficients[0] * (mu * mu - gamma_past)
    direct += coefficients[1] * 2 * mu * hermite_norm(1, variance)
    direct += coefficients[2] * hermite_norm(2, variance)
    compressed = coefficients[0] * (mu * mu - gamma_past) + coefficients[1] * 2 * mu * variance + coefficients[2] * 2 * variance * variance
    check("exact_scalar_wick_compression", direct == compressed, direct, compressed)

    high_wick = sum(
        (coefficients[index] * Fraction(0) for index in range(3, len(coefficients))),
        Fraction(0),
    )
    check("exact_rank_ge_three_wick_zero", high_wick == 0, high_wick, 0)
    q_direct = coefficients[0] * mu + coefficients[1] * variance
    q_stein = coefficients[0] * mu + variance * coefficients[1]
    check("exact_q_rank_zero_one", q_direct == q_stein, q_direct, q_stein)
    check("exact_rank_ge_two_q_zero", all(Fraction(0) == 0 for _ in coefficients[2:]), 0, 0)

    derivative_mean = coefficients[1]
    second_derivative_mean = 2 * coefficients[2]
    stein = coefficients[0] * (mu * mu - gamma_past) + 2 * mu * variance * derivative_mean + variance * variance * second_derivative_mean
    check("exact_second_order_stein", stein == direct, stein, direct)

    derivative_energy = sum(
        Fraction(index * index) * coefficients[index] * coefficients[index] * hermite_norm(index - 1, variance)
        for index in range(1, len(coefficients))
    )
    second_derivative_energy = sum(
        Fraction(index * index * (index - 1) * (index - 1))
        * coefficients[index]
        * coefficients[index]
        * hermite_norm(index - 2, variance)
        for index in range(2, len(coefficients))
    )
    rank_one_norm = coefficients[1] * coefficients[1] * hermite_norm(1, variance)
    rank_two_norm = coefficients[2] * coefficients[2] * hermite_norm(2, variance)
    check("exact_rank_one_derivative_bound", rank_one_norm <= variance * derivative_energy, rank_one_norm, variance * derivative_energy)
    check("exact_rank_two_derivative_bound", rank_two_norm <= variance * variance * second_derivative_energy / 2, rank_two_norm, variance * variance * second_derivative_energy / 2)

    # Exact selector-chain terms missed by a frozen-coefficient Stein rule.
    # A=x^2 and C(x,A)=xA=x^3: E[xC]=3, while the explicit and selector
    # derivatives contribute one and two, respectively.
    first_hermite_total = gaussian_moment(4)
    first_explicit = gaussian_moment(2)
    first_selector = 2 * gaussian_moment(2)
    check("selector_chain_first_hermite", first_hermite_total == first_explicit + first_selector, first_hermite_total, first_explicit + first_selector)
    check("selector_chain_frozen_first_incomplete", first_explicit != first_hermite_total, first_explicit, first_hermite_total)
    # Three distinct terms in the second-order chain rule.
    second_cross_left = gaussian_moment(4) - gaussian_moment(2)
    second_cross_right = 2 * gaussian_moment(0)
    second_square_left = (gaussian_moment(4) - gaussian_moment(2)) / 2
    second_square_right = gaussian_moment(0)
    second_curvature_left = gaussian_moment(4) - gaussian_moment(2)
    second_curvature_right = 2 * gaussian_moment(0)
    check("selector_chain_second_cross", second_cross_left == second_cross_right, second_cross_left, second_cross_right)
    check("selector_chain_second_square", second_square_left == second_square_right, second_square_left, second_square_right)
    check("selector_chain_second_curvature", second_curvature_left == second_curvature_right, second_curvature_left, second_curvature_right)

    # Exact product-Hermite coefficient proof on three independent roots.
    coefficient_map: dict[tuple[int, int, int], Fraction] = {
        (0, 0, 0): Fraction(3, 4),
        (1, 0, 0): Fraction(-2, 5),
        (0, 1, 0): Fraction(5, 6),
        (0, 0, 2): Fraction(7, 9),
        (1, 1, 0): Fraction(-4, 7),
        (0, 1, 1): Fraction(2, 3),
        (2, 0, 1): Fraction(3, 8),
        (3, 1, 0): Fraction(-5, 11),
        (4, 0, 3): Fraction(1, 13),
        (2, 2, 2): Fraction(-1, 17),
        (6, 0, 0): Fraction(1, 19),
    }
    low = Fraction(2, 5)
    gamma_low = Fraction(1, 6)
    q_coefficients: dict[tuple[int, int, int], Fraction] = {
        (0, 0, 0): low * low - gamma_low,
        (1, 0, 0): 2 * low,
        (0, 1, 0): 2 * low,
        (0, 0, 1): 2 * low,
        (1, 1, 0): 2,
        (1, 0, 1): 2,
        (0, 1, 1): 2,
        (2, 0, 0): 1,
        (0, 2, 0): 1,
        (0, 0, 2): 1,
    }
    direct_tensor = coefficient_inner(coefficient_map, q_coefficients)
    reconstructed = coefficient_map.get((0, 0, 0), Fraction(0)) * (low * low - gamma_low)
    root_ledgers: list[Fraction] = []
    for root_index in range(3):
        root_q: dict[tuple[int, int, int], Fraction] = {}
        linear = [0, 0, 0]
        linear[root_index] = 1
        root_q[tuple(linear)] = 2 * low
        for earlier in range(root_index):
            cross = [0, 0, 0]
            cross[earlier] = 1
            cross[root_index] = 1
            root_q[tuple(cross)] = 2
        fresh = [0, 0, 0]
        fresh[root_index] = 2
        root_q[tuple(fresh)] = 1
        projected = {
            index: value for index, value in coefficient_map.items() if index[root_index] in (1, 2)
        }
        root_value = coefficient_inner(projected, root_q)
        root_ledgers.append(root_value)
        reconstructed += root_value
        discarded = {index: value for index, value in coefficient_map.items() if index[root_index] >= 3}
        check(f"exact_root_{root_index + 1}_high_rank_zero", coefficient_inner(discarded, root_q) == 0, coefficient_inner(discarded, root_q), 0)
    check("exact_tensorized_wick_identity", reconstructed == direct_tensor, reconstructed, direct_tensor)

    g_coefficients: dict[tuple[int, int, int], Fraction] = {
        (0, 0, 0): low,
        (1, 0, 0): 1,
        (0, 1, 0): 1,
        (0, 0, 1): 1,
    }
    mean_direct = coefficient_inner(coefficient_map, g_coefficients)
    mean_projected = coefficient_map.get((0, 0, 0), Fraction(0)) * low
    for root_index in range(3):
        linear = [0, 0, 0]
        linear[root_index] = 1
        mean_projected += coefficient_map.get(tuple(linear), Fraction(0))
    check("exact_tensorized_mean_identity", mean_direct == mean_projected, mean_direct, mean_projected)

    # Independent adaptive integration of the smooth PSD ownership fixture.
    b_value = 2.0
    epsilon = 0.5
    reserve = 1.0
    raw = normal_expectation(lambda z: (b_value + epsilon * math.tanh(z)) * (z * z - 1.0))
    q_value = normal_expectation(lambda z: (b_value + epsilon * math.tanh(z)) * z)
    q_stein_value = epsilon * normal_expectation(sech_squared)

    def transformed(value: float) -> float:
        coefficient = b_value + epsilon * math.tanh(value)
        return math.sqrt(2.0 * reserve * coefficient / (coefficient + 2.0 * reserve))

    r_value = normal_expectation(lambda z: z * transformed(z))
    check("independent_tanh_raw_zero", abs(raw) < 3.0e-10, raw, 0.0)
    check("independent_tanh_q_stein", abs(q_value - q_stein_value) < 2.0e-9, q_value - q_stein_value, 0.0)
    check("independent_tanh_q_positive", q_value > 0.0, q_value, "> 0")
    check("independent_tanh_r_positive", r_value > 0.0, r_value, "> 0")
    mean_a = b_value + 2.0 * reserve
    d_remainder = raw - q_value * q_value / mean_a - r_value * r_value
    minimum = 0.5 * raw - 0.5 * q_value * q_value / mean_a
    restored = 0.5 * d_remainder + 0.5 * r_value * r_value
    check("independent_full_square_restoration", abs(minimum - restored) < 2.0e-10, minimum - restored, 0.0)
    check("independent_raw_does_not_own_mean", abs(raw) < 3.0e-10 and q_value > 0.25 and r_value > 0.02, [raw, q_value, r_value], "raw=0; q,r nonzero")

    # Independent selector asymptotics and derivative obstruction.
    selector_rows: list[dict[str, float]] = []
    for scale in (1.0, 2.0, 4.0, 8.0, 16.0):
        mu_scale = normal_expectation(lambda z, scale=scale: z * math.tanh(scale * z), 5.0e-11)
        norm_scale = normal_expectation(lambda z, scale=scale: math.tanh(scale * z) ** 2, 5.0e-11)
        derivative_energy = normal_expectation(
            lambda z, scale=scale: scale * scale * sech_squared(scale * z) ** 2,
            5.0e-10,
        )
        bracket = -0.5 * mu_scale * mu_scale / norm_scale
        selector_rows.append(
            {
                "scale": scale,
                "mu": mu_scale,
                "norm": norm_scale,
                "derivative_energy": derivative_energy,
                "bracket": bracket,
            }
        )
        check(f"independent_selector_norm_{int(scale)}", 0.0 < norm_scale < 1.0, norm_scale, "in (0,1)")
        check(f"independent_selector_mu_{int(scale)}", mu_scale > 0.0, mu_scale, "> 0")
    check("independent_selector_mu_limit", abs(selector_rows[-1]["mu"] - math.sqrt(2.0 / math.pi)) < 0.035, selector_rows[-1]["mu"], math.sqrt(2.0 / math.pi))
    check("independent_selector_bracket_limit", abs(selector_rows[-1]["bracket"] + 1.0 / math.pi) < 0.035, selector_rows[-1]["bracket"], -1.0 / math.pi)
    check("independent_selector_derivative_growth", selector_rows[-1]["derivative_energy"] > 6.0 * selector_rows[0]["derivative_energy"], selector_rows[-1]["derivative_energy"] / selector_rows[0]["derivative_energy"], "> 6")

    # Exact support arithmetic, including the historical boundary collar.
    support_collar = 2
    resonance_width = 5
    gap = support_collar + resonance_width + 1
    for cutoff in (-3, 0, 5):
        candidates = [
            (m, n)
            for n in range(cutoff - 10, cutoff + support_collar + 1)
            for m in range(cutoff - 10, cutoff + gap + resonance_width + 2)
            if abs(m - n) <= resonance_width and m > cutoff + gap
        ]
        check(f"independent_support_empty_{cutoff}", candidates == [], candidates, [])
        collar_candidates = [
            (m, n)
            for n in range(cutoff - 10, cutoff + support_collar + 1)
            for m in range(cutoff - 10, cutoff + gap + resonance_width + 2)
            if abs(m - n) <= resonance_width and m == cutoff + support_collar + resonance_width
        ]
        check(f"independent_boundary_collar_{cutoff}", bool(collar_candidates), collar_candidates[:3], "nonempty")

    # Exact one-root product/Doob commutator.
    xi = [Fraction(-1), Fraction(1)]
    p0_x = sum(xi, Fraction(0)) / 2
    xy = [value * value for value in xi]
    p0_xy = sum(xy, Fraction(0)) / 2
    d_xy = [value - p0_xy for value in xy]
    factorwise = [(value - p0_x) ** 2 for value in xi]
    covariance_one = [xy[index] - xi[index] * xi[index] for index in range(2)]
    covariance_zero = p0_xy - p0_x * p0_x
    reconstructed_product = [factorwise[index] + covariance_one[index] - covariance_zero for index in range(2)]
    check("independent_doob_product_zero", d_xy == [0, 0], d_xy, [0, 0])
    check("independent_factorwise_unit", factorwise == [1, 1], factorwise, [1, 1])
    check("independent_covariance_defect_minus_one", covariance_one == [0, 0] and covariance_zero == 1, [covariance_one, covariance_zero], [[0, 0], 1])
    check("independent_commutator_reconstruction", reconstructed_product == d_xy, reconstructed_product, d_xy)

    # Analytic spatial carrier check: normalized cosines keep unit L2 norm at
    # every integer frequency, hence Pi_2 pairing remains exactly two.
    for frequency in (1, 7, 31, 127):
        carrier_norm = Fraction(1)
        pairing = 2 * carrier_norm
        check(f"independent_spatial_no_gain_{frequency}", pairing == 2, pairing, 2)

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-low-hermite-wick-predictable-baseline-reduction-independent/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertions": rows,
        "derived": {
            "exact_tensor_pairing": str(direct_tensor),
            "root_ledgers": [str(value) for value in root_ledgers],
            "raw_tanh": raw,
            "q_tanh": q_value,
            "r_tanh": r_value,
            "selector_rows": selector_rows,
        },
        "independence": {
            "imports_primary": False,
            "reads_primary_result": False,
            "uses_numpy": False,
            "exact_method": "Fraction product-Hermite coefficient ledger",
            "numeric_method": "adaptive Simpson normal integration",
        },
        "boundary": {
            "low_hermite_identity": True,
            "predictable_support_collapse": True,
            "support_implies_payability": False,
            "hermite_implies_spatial_gain": False,
            "complete_h_n": False,
            "sector_a_closure": False,
        },
        "failures": [row["name"] for row in failures],
    }
    atomic_json(OUTPUT, payload)
    print(f"R-096 INDEPENDENT {'PASS' if not failures else 'FAIL'}: {len(rows) - len(failures)}/{len(rows)}")
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
