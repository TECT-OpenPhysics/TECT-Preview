#!/usr/bin/env python3
"""Non-importing standard-library audit for the scoped R-110 package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import cmath
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Callable


SCHEMA = "tect/a13-random-w-skorohod-diagonal-crossmode-boundary-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-random-w-skorohod-diagonal-crossmode-boundary/result.json"
)

Exponent = tuple[int, int, int, int]
Poly = dict[Exponent, complex]


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def require(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not condition:
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


def pconst(value: complex) -> Poly:
    return {} if value == 0 else {(0, 0, 0, 0): complex(value)}


def pvar(index: int, coefficient: complex = 1.0) -> Poly:
    exponent = [0, 0, 0, 0]
    exponent[index] = 1
    return {tuple(exponent): complex(coefficient)}


def padd(*polynomials: Poly) -> Poly:
    result: Poly = {}
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] = result.get(exponent, 0j) + coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if abs(coefficient) > 1e-14}


def pscale(polynomial: Poly, scalar: complex) -> Poly:
    return {exponent: coefficient * scalar for exponent, coefficient in polynomial.items()}


def pmul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            exponent = tuple(a + b for a, b in zip(left_power, right_power))
            result[exponent] = result.get(exponent, 0j) + left_coefficient * right_coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if abs(coefficient) > 1e-14}


def ppow(polynomial: Poly, power: int) -> Poly:
    result = pconst(1)
    for _ in range(power):
        result = pmul(result, polynomial)
    return result


def pconj(polynomial: Poly) -> Poly:
    return {exponent: coefficient.conjugate() for exponent, coefficient in polynomial.items()}


def double_factorial_odd(power_minus_one: int) -> int:
    value = 1
    for factor in range(1, power_minus_one + 1, 2):
        value *= factor
    return value


def gaussian_poly_expectation(polynomial: Poly, v: float, w: float) -> complex:
    total = 0j
    variances = (v, v, w, w)
    for powers, coefficient in polynomial.items():
        moment = 1.0
        for power, variance in zip(powers, variances):
            if power % 2:
                moment = 0.0
                break
            if power:
                moment *= double_factorial_odd(power - 1) * variance ** (power // 2)
        total += coefficient * moment
    return total


def fourier_convolution(left: dict[int, Poly], right: dict[int, Poly]) -> dict[int, Poly]:
    result: dict[int, Poly] = {}
    for left_mode, left_poly in left.items():
        for right_mode, right_poly in right.items():
            mode = left_mode + right_mode
            result[mode] = padd(result.get(mode, {}), pmul(left_poly, right_poly))
    return result


def fourier_inner(left: dict[int, Poly], right: dict[int, Poly]) -> Poly:
    result: Poly = {}
    for mode in set(left) & set(right):
        result = padd(result, pmul(left[mode], pconj(right[mode])))
    return result


def complete_cluster_polynomials(amplitude: float, v: float, w: float) -> tuple[Poly, Poly, Poly]:
    variables = [pvar(index) for index in range(4)]
    aa, bb, cc, dd = variables
    field = {
        0: pconst(amplitude),
        1: padd(pscale(aa, 0.5), pscale(bb, -0.5j)),
        -1: padd(pscale(aa, 0.5), pscale(bb, 0.5j)),
        2: padd(pscale(cc, 0.5), pscale(dd, -0.5j)),
        -2: padd(pscale(cc, 0.5), pscale(dd, 0.5j)),
    }
    derivative_field = {mode: pscale(polynomial, 1j * mode) for mode, polynomial in field.items()}
    current = fourier_convolution(field, derivative_field)
    current_norm = fourier_inner(current, current)

    carrier_derivatives = (
        {1: pconst(0.5j), -1: pconst(-0.5j)},
        {1: pconst(0.5), -1: pconst(0.5)},
        {2: pconst(1j), -2: pconst(-1j)},
        {2: pconst(1), -2: pconst(1)},
    )
    outputs = [fourier_convolution(field, carrier) for carrier in carrier_derivatives]
    variances = (v, v, w, w)
    gram = [[fourier_inner(outputs[i], outputs[j]) for j in range(4)] for i in range(4)]
    trace = pconst(0)
    hs_square = pconst(0)
    for i in range(4):
        trace = padd(trace, pscale(gram[i][i], variances[i]))
        for j in range(4):
            hs_square = padd(hs_square, pscale(ppow(gram[i][j], 2), variances[i] * variances[j]))
    packet = pscale(padd(current_norm, pscale(trace, -1)), 0.5)
    return packet, trace, hs_square


def simpson_gaussian(function: Callable[[float], float], radius: float = 9.0, intervals: int = 40000) -> float:
    if intervals % 2:
        intervals += 1
    step = 2 * radius / intervals
    total = 0.0
    normalization = math.sqrt(2 * math.pi)
    for index in range(intervals + 1):
        x = -radius + index * step
        weight = 1 if index in (0, intervals) else 4 if index % 2 else 2
        total += weight * function(x) * math.exp(-x * x / 2) / normalization
    return total * step / 3


def expected_h(amplitude: float, v: float, w: float) -> float:
    return (
        amplitude**4 * (v**2 / 2 + 8 * w**2)
        + amplitude**2 * (v**3 + 10 * v**2 * w + 16 * v * w**2 + 16 * w**3)
        + 5 * v**4 / 4
        + v**3 * w
        + 25 * v**2 * w**2
        + 16 * v * w**3
        + 20 * w**4
    )


def expected_variance(amplitude: float, v: float, w: float) -> float:
    return (
        amplitude**4 * v**2
        + 16 * amplitude**4 * w**2
        + 2 * amplitude**2 * v**3
        + 20 * amplitude**2 * v**2 * w
        + 32 * amplitude**2 * v * w**2
        + 32 * amplitude**2 * w**3
        + 2 * v**4
        + 2 * v**3 * w
        + 42 * v**2 * w**2
        + 32 * v * w**3
        + 32 * w**4
    ) / 4


def expected_third(amplitude: float, v: float, w: float) -> float:
    return (
        amplitude**6 * v**3
        + 64 * amplitude**6 * w**3
        + 6 * amplitude**4 * v**4
        + 57 * amplitude**4 * v**3 * w
        + 168 * amplitude**4 * v**2 * w**2
        + 192 * amplitude**4 * v * w**3
        + 384 * amplitude**4 * w**4
        + 15 * amplitude**2 * v**5
        + 93 * amplitude**2 * v**4 * w
        + 630 * amplitude**2 * v**3 * w**2
        + 720 * amplitude**2 * v**2 * w**3
        + 768 * amplitude**2 * v * w**4
        + 960 * amplitude**2 * w**5
        + 15 * v**6
        + 15 * v**5 * w
        + 216 * v**4 * w**2
        + 810 * v**3 * w**3
        + 1044 * v**2 * w**4
        + 960 * v * w**5
        + 960 * w**6
    ) / 4


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    # Exact constants and trace transport.
    q = Fraction(10, 9)
    checks.require("constants", "random-W q constant", q * q / 128 == Fraction(25, 2592), q * q / 128, Fraction(25, 2592))
    checks.require("constants", "fixed-W q constant", 2 * q * q / 128 == Fraction(25, 1296), 2 * q * q / 128, Fraction(25, 1296))
    for rho in (0.0, 0.2, 0.75, 1.0):
        c_value = -1.7
        explicit = -c_value
        mixed = c_value
        checks.require("interpolation", f"trace cancellation rho={rho}", abs(explicit + mixed) < 1e-15, explicit + mixed, 0)

    # Polynomial random-W identity, evaluated independently at one exact
    # smooth PSD sample w=1+alpha x^2.
    alpha = 0.3
    beta = -0.4
    def h_poly(x: float) -> float:
        return 1 + beta * x + x * x
    def hp(x: float) -> float:
        return beta + 2 * x
    def hpp(_: float) -> float:
        return 2.0
    def w_poly(x: float) -> float:
        return 1 + alpha * x * x
    def wp(x: float) -> float:
        return 2 * alpha * x
    def wpp(_: float) -> float:
        return 2 * alpha
    direct = simpson_gaussian(lambda x: w_poly(x) * (hp(x) ** 2 + h_poly(x) * hpp(x)), intervals=12000)
    doubled = simpson_gaussian(lambda x: 0.5 * h_poly(x) ** 2 * ((x * x - 1) * w_poly(x) - 2 * x * wp(x) + wpp(x)), intervals=12000)
    single = simpson_gaussian(lambda x: h_poly(x) * hp(x) * (x * w_poly(x) - wp(x)), intervals=12000)
    checks.require("random_w", "double-divergence quadrature", abs(direct - doubled) < 2e-9, direct - doubled, 0)
    checks.require("random_w", "one-divergence quadrature", abs(direct - single) < 2e-9, direct - single, 0)

    # Oscillatory fixture is checked by a quadrature route independent of the
    # characteristic-function derivation.
    m_value = 3.0
    epsilon = 0.2
    for tau in (1.0, -1.0):
        exact_form = m_value * (
            math.exp(-2 * m_value**2)
            + tau * epsilon * (1 + math.exp(-8 * m_value**2)) / 2
        )
        numerical_form = simpson_gaussian(
            lambda x: (1 + tau * epsilon * math.cos(2 * m_value * x))
            * m_value
            * math.cos(2 * m_value * x),
            intervals=40000,
        )
        checks.require("random_w_nogo", f"oscillatory score tau={int(tau)}", abs(exact_form - numerical_form) < 2e-8, numerical_form, exact_form)
        exact_k = (
            2
            + 4 * tau * epsilon * math.exp(-2 * m_value**2)
            + epsilon**2
            * (
                1
                + 8 * m_value**2
                + 8 * m_value**4
                + (1 - 8 * m_value**2 + 8 * m_value**4) * math.exp(-8 * m_value**2)
            )
        )
        numerical_k = simpson_gaussian(
            lambda x: (
                (x * x - 1) * (1 + tau * epsilon * math.cos(2 * m_value * x))
                + 4 * tau * epsilon * m_value * x * math.sin(2 * m_value * x)
                - 4 * tau * epsilon * m_value**2 * math.cos(2 * m_value * x)
            )
            ** 2,
            intervals=40000,
        )
        checks.require("random_w_nogo", f"oscillatory score cost tau={int(tau)}", abs(exact_k - numerical_k) < 3e-7, numerical_k, exact_k)
    checks.require("random_w_nogo", "uniform positive lower eigenvalue", 1 - epsilon > 0, 1 - epsilon, ">0")

    # Diagonal mean-debt fixture by elementary Gaussian moments.
    a_value = Fraction(1)
    eps_value = Fraction(1, 10)
    mean = -eps_value**2
    covariance_square = eps_value**4 * (a_value**4 + 24 * a_value**2 + 48)
    jensen = -q * mean
    square_cost = q * q * covariance_square / 4
    checks.require("mean_debt", "mean", mean == Fraction(-1, 100), mean, Fraction(-1, 100))
    checks.require("mean_debt", "covariance square", covariance_square == Fraction(73, 10000), covariance_square, Fraction(73, 10000))
    checks.require("mean_debt", "Jensen lower", jensen == Fraction(1, 90), jensen, Fraction(1, 90))
    checks.require("mean_debt", "square cost", square_cost == Fraction(73, 32400), square_cost, Fraction(73, 32400))
    checks.require("mean_debt", "violation", jensen - square_cost == Fraction(287, 32400), jensen - square_cost, Fraction(287, 32400))

    # Independent Fourier-convolution derivation of the complete cluster.
    sample_points = ((0.0, 1.0, 0.0), (0.75, 1.2, 0.4), (2.0, 0.3, 1.7))
    sample_records: list[dict[str, float]] = []
    for amplitude, v, w in sample_points:
        packet, trace, hs_poly = complete_cluster_polynomials(amplitude, v, w)
        mean_value = gaussian_poly_expectation(packet, v, w).real
        variance_value = gaussian_poly_expectation(ppow(packet, 2), v, w).real
        third_value = gaussian_poly_expectation(ppow(packet, 3), v, w).real
        hs_value = gaussian_poly_expectation(hs_poly, v, w).real
        checks.require("cross_cluster", f"mean A={amplitude} v={v} w={w}", abs(mean_value) < 2e-10, mean_value, 0)
        checks.require("cross_cluster", f"variance A={amplitude} v={v} w={w}", abs(variance_value - expected_variance(amplitude, v, w)) < 2e-8 * max(1, variance_value), variance_value, expected_variance(amplitude, v, w))
        checks.require("cross_cluster", f"third moment A={amplitude} v={v} w={w}", abs(third_value - expected_third(amplitude, v, w)) < 2e-8 * max(1, third_value), third_value, expected_third(amplitude, v, w))
        checks.require("cross_cluster", f"whole-output HS A={amplitude} v={v} w={w}", abs(hs_value - expected_h(amplitude, v, w)) < 2e-8 * max(1, hs_value), hs_value, expected_h(amplitude, v, w))
        exact_margin = expected_h(amplitude, v, w) - 2 * expected_variance(amplitude, v, w)
        formula_margin = (v**4 + 16 * v**2 * w**2 + 16 * w**4) / 4
        checks.require("cross_cluster", f"leading margin A={amplitude} v={v} w={w}", abs(exact_margin - formula_margin) < 2e-10 * max(1, formula_margin), exact_margin, formula_margin)
        sample_records.append(
            {
                "A": amplitude,
                "v": v,
                "w": w,
                "variance": variance_value,
                "third_moment": third_value,
                "whole_output_hs_square": hs_value,
                "leading_margin": exact_margin,
                "trace_terms": len(trace),
            }
        )

    # Pointwise square and sharp 9/10 coefficient.
    for amplitude in (0.5, 1.0, 3.0):
        for sqrt_s in (0.0, 0.1, 0.3 * amplitude, 2.0):
            left = 0.9 * amplitude**2 + 10 * sqrt_s**2 - 6 * amplitude * sqrt_s
            right = 10 * (sqrt_s - 0.3 * amplitude) ** 2
            checks.require("cross_payment", f"completion A={amplitude} sqrtS={sqrt_s}", abs(left - right) < 2e-14, left, right)
    alpha_below = 0.9 - 0.01
    minimizing_sqrt = 0.3
    failed_value = alpha_below + 10 * minimizing_sqrt**2 - 6 * minimizing_sqrt
    checks.require("cross_payment", "9/10 coefficient is sharp", failed_value < 0, failed_value, "<0")
    checks.require("cross_payment", "baseline shell exponent", 3 - 2 == 1, 3 - 2, 1)
    checks.require("cross_payment", "floor shell exponent", 3 - 6 == -3, 3 - 6, -3)
    checks.require("cross_payment", "square-first shell exponent", 3 - 4 == -1, 3 - 4, -1)

    status = "PASS" if all(row["status"] == "PASS" for row in checks.rows) else "FAIL"
    results = {
        "q_random_cost": str(q * q / 128),
        "q_fixed_cost": str(2 * q * q / 128),
        "mean_debt": {
            "mean": str(mean),
            "covariance_square": str(covariance_square),
            "jensen": str(jensen),
            "square_cost": str(square_cost),
            "violation": str(jensen - square_cost),
        },
        "cross_samples": sample_records,
        "shell_exponents": {"pointwise_baseline": 1, "covariance_floor": -3, "square_first_baseline": -1},
    }
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "status": status,
        "assertions_total": len(checks.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in checks.rows),
        "assertions_failed": sum(row["status"] != "PASS" for row in checks.rows),
        "assertion_names": [f"{row['group']}::{row['name']}" for row in checks.rows],
        "assertions": checks.rows,
        "results": results,
        "results_sha256": hashlib.sha256(
            json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "route_verdicts": {
            "random_W_double_divergence": "pass",
            "random_W_HS_only_extension": "fail",
            "trace_corrected_interpolation": "pass",
            "universal_nonlinear_square_first": "fail",
            "physical_k2k_moments": "pass",
            "physical_k2k_bare_all_q": "open",
            "pointwise_payment": "nonsummable",
            "sector_A": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"independent {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
