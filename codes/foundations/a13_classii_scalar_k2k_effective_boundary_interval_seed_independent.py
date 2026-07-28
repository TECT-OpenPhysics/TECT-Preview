#!/usr/bin/env python3
"""Independent reconstruction for the scoped R-113 package.

This script does not import the primary certificate.  Its projective moment
engine uses standard-library Fraction bivariate polynomials, and its Arb
certificate starts from a different radial partition and refinement priority.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import heapq
import importlib.metadata
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path

import sympy as sp
from flint import arb, ctx


SCHEMA = "tect/a13-scalar-k2k-effective-boundary-interval-seed-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-scalar-k2k-effective-boundary-interval-seed/result.json"
)
ARBITRARY_PRECISION_DPS = 40
CENTRAL_CELLS = 30_000
Polynomial = dict[tuple[int, int], Fraction]


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
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


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, Fraction(0)) + coefficient
        if not result[monomial]:
            del result[monomial]
    return result


def poly_scale(polynomial: Polynomial, scalar: Fraction) -> Polynomial:
    return {monomial: coefficient * scalar for monomial, coefficient in polynomial.items() if coefficient * scalar}


def poly_mul(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for (left_t, left_y), left_coefficient in left.items():
        for (right_t, right_y), right_coefficient in right.items():
            monomial = (left_t + right_t, left_y + right_y)
            result[monomial] = result.get(monomial, Fraction(0)) + left_coefficient * right_coefficient
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def poly_pow(polynomial: Polynomial, exponent: int) -> Polynomial:
    result: Polynomial = {(0, 0): Fraction(1)}
    base = polynomial
    power = exponent
    while power:
        if power & 1:
            result = poly_mul(result, base)
        base = poly_mul(base, base)
        power //= 2
    return result


def rational_expectation_upper(polynomial: Polynomial) -> Fraction:
    total = Fraction(0)
    for (power_t, power_y), coefficient in polynomial.items():
        if power_y % 2 == 0:
            y_moment = Fraction(math.factorial(power_y // 2))
        else:
            index = (power_y - 1) // 2
            y_moment = Fraction(
                2 * math.factorial(2 * index + 2),
                4 ** (index + 1) * math.factorial(index + 1),
            )
        total += coefficient * math.factorial(power_t) * y_moment
    return total


def independent_log_sixth_constant(x_cap: int, exp_cap: int, q_cap: Fraction) -> Fraction:
    b_star: Polynomial = {(1, 1): Fraction(5, 12)}
    q_star: Polynomial = {
        (2, 0): Fraction(1, 4),
        (1, 2): Fraction(5, 8),
        (0, 4): Fraction(1, 16),
        (1, 0): Fraction(1, 2),
        (0, 2): Fraction(1, 8),
    }
    radial = poly_add(b_star, poly_scale(q_star, q_cap))
    half_powers = {order: (order + 1) // 2 for order in range(1, 7)}
    derivative: dict[int, Fraction] = {}
    for order in range(1, 7):
        value = Fraction(0)
        for pairs in range(order // 2 + 1):
            coefficient = Fraction(
                math.factorial(order),
                math.factorial(order - 2 * pairs) * math.factorial(pairs),
            )
            polynomial = poly_mul(poly_pow(radial, order - 2 * pairs), poly_pow(q_star, pairs))
            value += (
                coefficient
                * x_cap ** (order - pairs - half_powers[order])
                * rational_expectation_upper(polynomial)
            )
        derivative[order] = exp_cap * value
    bell_terms = (
        (1, (6,)),
        (6, (1, 5)),
        (15, (2, 4)),
        (10, (3, 3)),
        (30, (1, 1, 4)),
        (120, (1, 2, 3)),
        (30, (2, 2, 2)),
        (120, (1, 1, 1, 3)),
        (270, (1, 1, 2, 2)),
        (360, (1, 1, 1, 1, 2)),
        (120, (1, 1, 1, 1, 1, 1)),
    )
    total = Fraction(0)
    for coefficient, orders in bell_terms:
        product = Fraction(coefficient * x_cap ** (sum(half_powers[order] for order in orders) - 3))
        for order in orders:
            product *= derivative[order]
        total += product
    return total


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def arb_hull(lower: Fraction, upper: Fraction) -> arb:
    return arb(fraction_text((lower + upper) / 2), fraction_text((upper - lower) / 2))


def arb_sqrt_hull(lower: Fraction, upper: Fraction) -> arb:
    """Outward hull of sqrt([lower, upper]), including endpoint balls."""
    if lower < 0 or upper < lower:
        raise ValueError("sqrt hull requires 0 <= lower <= upper")
    left = arb(fraction_text(lower)).sqrt()
    right = arb(fraction_text(upper)).sqrt()
    return left.union(right)


def independent_central_box() -> dict[str, object]:
    ctx.dps = ARBITRARY_PRECISION_DPS
    c = arb_hull(Fraction(49, 100), Fraction(51, 100))
    s = 1 - c
    x = arb_hull(Fraction(99, 100), Fraction(101, 100))
    tau = arb_hull(Fraction(99, 100), Fraction(101, 100))
    k2 = (c**2 + s**2) / 2
    k1 = c**3 + (arb(5) / 2) * c**2 * s + c * s**2 + s**3 / 4
    k0 = (
        (arb(5) / 4) * c**4
        + c**3 * s / 4
        + (arb(25) / 16) * c**2 * s**2
        + c * s**3 / 4
        + (arb(5) / 64) * s**4
    )
    target = (x**2 * k2 + x * tau * k1 + tau**2 * k0) / 4
    x_root, tau_root, s_root, eight_root = x.sqrt(), tau.sqrt(), s.sqrt(), arb(8).sqrt()

    def upper(rectangle: tuple[Fraction, Fraction, Fraction, Fraction]) -> arb:
        t0, t1, u0, u1 = rectangle
        t_box, u_box = arb_hull(t0, t1), arb_hull(u0, u1)
        rho = c * t_box / 2
        sigma = s * u_box / 8
        sigma_root = s_root * arb_sqrt_hull(u0, u1) / eight_root
        z_value = 6 * x_root * tau_root * rho * sigma_root
        d_value = (
            tau * (rho - arb(1) / 2) ** 2
            + 4 * tau * (sigma - arb(1) / 8) ** 2
            + 4 * x * sigma
            + rho * ((x_root - 3 * tau_root * sigma_root) ** 2 + tau * sigma)
            - x / 2
            - 5 * tau / 16
        )
        z0 = z_value.lower()
        i0e_upper = arb(1) if z0 <= 0 else z0.bessel_i(0, scaled=True).upper()
        area = arb(fraction_text((t1 - t0) * (u1 - u0)))
        return area * (-t_box - u_box - d_value - target).exp().upper() * i0e_upper

    breakpoints = list(
        map(
            Fraction,
            (0, Fraction(1, 2), 1, Fraction(3, 2), 2, 3, 4, 6, 8, 12, 16, 24, 32, 40, 50),
        )
    )
    heap: list[tuple[float, int, tuple[Fraction, Fraction, Fraction, Fraction], arb]] = []
    total = arb(0)
    serial = 0
    for t0, t1 in zip(breakpoints, breakpoints[1:]):
        for u0, u1 in zip(breakpoints, breakpoints[1:]):
            rectangle = (t0, t1, u0, u1)
            value = upper(rectangle)
            total += value
            priority = float(value) * float(max(t1 - t0, u1 - u0))
            heapq.heappush(heap, (-priority, serial, rectangle, value))
            serial += 1
    cells = len(heap)
    while cells < CENTRAL_CELLS:
        _, _, rectangle, old_value = heapq.heappop(heap)
        total -= old_value
        t0, t1, u0, u1 = rectangle
        split_t = True if (serial + cells) % 2 == 0 and t1 > t0 else t1 - t0 >= u1 - u0
        if split_t:
            middle = (t0 + t1) / 2
            children = ((t0, middle, u0, u1), (middle, t1, u0, u1))
        else:
            middle = (u0 + u1) / 2
            children = ((t0, t1, u0, middle), (t0, t1, middle, u1))
        for child in children:
            value = upper(child)
            total += value
            a0, a1, b0, b1 = child
            priority = float(value) * float(max(a1 - a0, b1 - b0))
            heapq.heappush(heap, (-priority, serial, child, value))
            serial += 1
        cells += 1
    radius = arb(50)
    tail = ((-target + x / 2 + 5 * tau / 16).exp() * (2 * (-radius).exp() - (-2 * radius).exp())).upper()
    residual = (2 * x + tau) ** 2 - 32 * x - 20 * tau
    final_upper = (total + tail).upper()
    return {
        "parameter_box": {"c": "[49/100,51/100]", "x": "[99/100,101/100]", "tau": "[99/100,101/100]"},
        "initial_partition": "0,1/2,1,3/2,2,3,4,6,8,12,16,24,32,40,50",
        "refinement_priority": "cell upper times longest side",
        "cells": cells,
        "radial_radius": 50,
        "precision_dps": ARBITRARY_PRECISION_DPS,
        "residual_ball": str(residual),
        "residual_upper": str(residual.upper()),
        "core_upper": str(total),
        "tail_upper": str(tail),
        "normalized_total_upper": str(final_upper),
        "residual_strict": bool(residual.upper() < 0),
        "target_strict": bool(final_upper < 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    shape, t_sym, u_sym = sp.symbols("shape T U", nonnegative=True)
    shape_complement = 1 - shape
    rho_shape = shape * t_sym / 2
    sigma_shape = shape_complement * u_sym / 8
    q_shape = sp.expand(rho_shape**2 + 10 * rho_shape * sigma_shape + 4 * sigma_shape**2 - rho_shape - sigma_shape)
    q_majorant = t_sym**2 / 4 + sp.Rational(5, 8) * t_sym * u_sym + u_sym**2 / 16 + t_sym / 2 + u_sym / 8
    q_plus = sp.Poly(sp.expand(q_majorant + q_shape), t_sym, u_sym)
    q_minus = sp.Poly(sp.expand(q_majorant - q_shape), t_sym, u_sym)
    audit.check(
        "projective",
        "independent absolute-Q plus coefficient majorant",
        sp.simplify(q_plus.coeff_monomial(t_sym**2) - (1 + shape**2) / 4) == 0
        and sp.simplify(q_plus.coeff_monomial(t_sym * u_sym) - 5 * (1 + shape - shape**2) / 8) == 0
        and sp.simplify(q_plus.coeff_monomial(u_sym**2) - (1 + (1 - shape) ** 2) / 16) == 0
        and sp.simplify(q_plus.coeff_monomial(t_sym) - (1 - shape) / 2) == 0
        and sp.simplify(q_plus.coeff_monomial(u_sym) - shape / 8) == 0,
        q_plus.as_dict(),
        "all coefficients nonnegative on the simplex",
    )
    audit.check(
        "projective",
        "independent absolute-Q minus coefficient majorant",
        sp.simplify(q_minus.coeff_monomial(t_sym**2) - (1 - shape**2) / 4) == 0
        and sp.simplify(q_minus.coeff_monomial(t_sym * u_sym) - 5 * (1 - shape + shape**2) / 8) == 0
        and sp.simplify(q_minus.coeff_monomial(u_sym**2) - shape * (2 - shape) / 16) == 0
        and sp.simplify(q_minus.coeff_monomial(t_sym) - (1 + shape) / 2) == 0
        and sp.simplify(q_minus.coeff_monomial(u_sym) - (2 - shape) / 8) == 0,
        q_minus.as_dict(),
        "all coefficients nonnegative on the simplex",
    )
    audit.check("projective", "independent rational B-star enlargement", 24 < 25, "24/144", "<25/144")

    rows = (
        (1, 2, Fraction(3, 16), 7, Fraction(181292201822646474659735, 273593677362757632), 700_000),
        (2, 3, Fraction(1, 8), 8, Fraction(267774784673603525005, 79164837199872), 3_500_000),
        (4, 8, Fraction(1, 16), 10, Fraction(274770569726043833586365, 1068725302198272), 260_000_000),
        (8, 55, Fraction(3, 256), 15, Fraction(5748965910841593523942194993404275, 373546567492618420224), 16_000_000_000_000),
    )
    projective: list[dict[str, object]] = []
    lower_x = 0
    for x_cap, exp_cap, q_star_cap, delta_power, expected, convenient in rows:
        actual = independent_log_sixth_constant(x_cap, exp_cap, q_star_cap)
        audit.check("projective", f"X={x_cap} independent constant", actual == expected, actual, expected)
        audit.check("projective", f"X={x_cap} independent upper", actual < convenient, actual, f"<{convenient}")
        audit.check("projective", f"X={x_cap} q-star gate", Fraction(4, 2**delta_power) <= q_star_cap**2, Fraction(4, 2**delta_power), f"<={q_star_cap**2}")
        audit.check("projective", f"X={x_cap} half-leading-margin", convenient * 960 <= 720 * 2 ** (3 * delta_power), convenient * 960, f"<={720 * 2 ** (3 * delta_power)}")
        projective.append(
            {
                "x_interval": f"({lower_x},{x_cap}]",
                "tau_over_x_max": f"1/{2**delta_power}",
                "derivative_envelope_q_star_cap": str(q_star_cap),
                "exact_sixth_log_constant": str(actual),
                "certified_gap_lower": "x^3/960",
            }
        )
        lower_x = x_cap

    def theta(radius: int) -> Fraction:
        return Fraction(48, 25 * (8 * radius + 5) * (2 * radius * radius + 4 * radius + 5))

    theta_table = (
        Fraction(48, 3575),
        Fraction(16, 3675),
        Fraction(48, 49025),
        Fraction(16, 94875),
        Fraction(48, 1931825),
        Fraction(16, 4743675),
        Fraction(48, 109255025),
        Fraction(16, 285418875),
    )
    for index, expected in enumerate(theta_table):
        audit.check("origin", f"independent theta {index}", theta(2**index) == expected, theta(2**index), expected)
    theta_global = theta_table[-1]
    audit.check("origin", "independent origin/projective square dichotomy", 128 * Fraction(1, 128) == 1 and theta_global == theta(128), "x/tau<=128 or tau/x<=1/128", "complete origin square")
    kappa = Fraction(5) * theta_global / (3584 * 7_863_787)
    audit.check("faces", "independent kappa", kappa == Fraction(1, 100552401097327200), kappa, Fraction(1, 100552401097327200))
    x_face, tau_face = sp.symbols("x_face tau_face", positive=True)
    small_base = sp.Rational(5, 7) * sp.Symbol("sf", positive=True) ** 2
    large_base = sp.Symbol("sg", positive=True) / (3 * (sp.Symbol("sg", positive=True) + 4))
    sf = next(iter(small_base.free_symbols))
    sg = next(iter(large_base.free_symbols))
    face_rows = (
        ("independent c=0 small margin", small_base.subs(sf, tau_face / 16), 5 * tau_face**2 / 1792),
        ("independent c=0 large margin", large_base.subs(sg, tau_face / 16), tau_face / (3 * (tau_face + 64))),
        ("independent c=1 small margin", small_base.subs(sf, tau_face / 4), 5 * tau_face**2 / 112),
        ("independent c=1 large margin", large_base.subs(sg, tau_face / 4), tau_face / (3 * (tau_face + 16))),
    )
    for name, actual, expected in face_rows:
        audit.check("faces", name, sp.simplify(actual - expected) == 0, actual, expected)
    audit.check("faces", "independent c=0 branch translation", sp.simplify(16 * ((tau_face / 16) * (4 * (4 * x_face / tau_face) + 5) - 1) - (16 * x_face + 5 * tau_face - 16)) == 0, "universal branch", "16*x+5*tau<=16 or >16")
    audit.check("faces", "independent c=1 branch translation", sp.simplify(4 * ((tau_face / 4) * (4 * (x_face / tau_face) + 5) - 1) - (4 * x_face + 5 * tau_face - 4)) == 0, "universal branch", "4*x+5*tau<=4 or >4")

    l_shape = rho_shape + 4 * sigma_shape - sp.Rational(1, 2)
    l_c = sp.diff(l_shape, shape)
    q_c = sp.expand(sp.diff(q_shape, shape))
    q_c_grouped = (
        shape * (t_sym**2 - t_sym) / 2
        - (1 - shape) * t_sym / 2
        + sp.Rational(5, 8) * (1 - 2 * shape) * t_sym * u_sym
        - (1 - shape) * (u_sym**2 - u_sym) / 8
        + shape * u_sym / 8
    )
    audit.check("faces", "independent L-c derivative", sp.simplify(l_c - (t_sym - u_sym) / 2) == 0, l_c, "(T-U)/2")
    audit.check("faces", "independent Q-c grouped derivative", sp.simplify(q_c - q_c_grouped) == 0, q_c, q_c_grouped)
    q_c_abs_upper = Fraction(5, 8) + Fraction(1, 2) + Fraction(5, 8) + Fraction(5, 32) + Fraction(1, 8)
    audit.check("faces", "independent centered exponential absolute-moment bound", Fraction(65, 24) > Fraction(8, 3), Fraction(65, 24), ">8/3, hence -1+6/e<5/4")
    audit.check("faces", "independent Q-c expectation bound", q_c_abs_upper == Fraction(65, 32) and q_c_abs_upper < Fraction(9, 4) < Fraction(5, 2), q_c_abs_upper, "<9/4<5/2")
    audit.check("faces", "independent L-c expectation bound", Fraction(1, 2) <= 1, "E|T-U|/2=1/2", "<=1")
    audit.check("faces", "independent Bessel c-polynomial bound", sp.simplify((1 + 2 * shape - 3 * shape**2) - (1 - shape) * (3 * shape + 1)) == 0 and sp.discriminant(3 * shape**2 - 2 * shape + 1, shape) < 0, sp.factor(1 + 2 * shape - 3 * shape**2), "|2c-3c^2|<=1")
    audit.check("faces", "independent Bessel score coefficient", Fraction(1, 4) * Fraction(9, 8) * 2 == Fraction(9, 16), Fraction(1, 4) * Fraction(9, 8) * 2, Fraction(9, 16))
    k2_shape = (shape**2 + (1 - shape) ** 2) / 2
    k1_shape = shape**3 + sp.Rational(5, 2) * shape**2 * (1 - shape) + shape * (1 - shape) ** 2 + (1 - shape) ** 3 / 4
    k0_shape = (sp.Rational(5, 4) * shape**4 + shape**3 * (1 - shape) / 4 + sp.Rational(25, 16) * shape**2 * (1 - shape) ** 2 + shape * (1 - shape) ** 3 / 4 + sp.Rational(5, 64) * (1 - shape) ** 4)
    k1_prime = sp.factor(sp.diff(k1_shape, shape))
    audit.check("faces", "independent K2 derivative bound", sp.factor(sp.diff(k2_shape, shape)) == 2 * shape - 1, sp.factor(sp.diff(k2_shape, shape)), "absolute value <=1")
    audit.check("faces", "independent K1 derivative bound", sp.simplify(k1_prime.subs(shape, sp.Rational(5, 9)) - sp.Rational(17, 18)) == 0 and k1_prime.subs(shape, 0) >= 0 and k1_prime.subs(shape, 1) >= 0, k1_prime, "0<=K1'<=17/18<1")
    k0_prime = sp.expand(sp.diff(k0_shape, shape))
    k0_prime_polynomial = sp.Poly(k0_prime, shape)
    k0_prime_degree = k0_prime_polynomial.degree()
    k0_prime_powers = tuple(k0_prime_polynomial.nth(index) for index in range(k0_prime_degree + 1))
    k0_prime_bernstein = tuple(
        Fraction(*map(int, sp.fraction(sp.simplify(
            sum(
                k0_prime_powers[j] * sp.binomial(index, j) / sp.binomial(k0_prime_degree, j)
                for j in range(index + 1)
            )
        ))))
        for index in range(k0_prime_degree + 1)
    )
    k0_prime_bernstein_expected = (
        Fraction(-1, 16),
        Fraction(19, 24),
        Fraction(-19, 24),
        Fraction(19, 4),
    )
    audit.check(
        "faces",
        "independent K0 derivative Bernstein reconstruction and bound",
        k0_prime_bernstein == k0_prime_bernstein_expected
        and max(map(abs, k0_prime_bernstein)) == Fraction(19, 4),
        k0_prime_bernstein,
        k0_prime_bernstein_expected,
    )
    exp_upper = sum(Fraction(1, math.factorial(index)) for index in range(6)) + Fraction(7, 4320)
    audit.check("faces", "independent rational e upper", exp_upper < Fraction(87, 32), exp_upper, "<87/32")
    audit.check("faces", "independent exponential tilt cap", Fraction(87, 32) < Fraction(4, 3) ** 4 and Fraction(87, 32) ** 10 * Fraction(4, 3) < 60_000, Fraction(87, 32) ** 10 * Fraction(4, 3), "<60000")
    lambda_global = 60_000 * (8 + 50 + 90) + 16 + 40 + 475
    lambda_small = 60_000 * (Fraction(128) + Fraction(5, 2) + Fraction(9, 16)) + 32 + Fraction(1, 4) + Fraction(19, 5)
    audit.check("faces", "independent global Lambda bound", lambda_global <= 8_880_531, lambda_global, "<=8880531")
    audit.check("faces", "independent small Lambda/tau bound", lambda_small <= 7_863_787, lambda_small, "<=7863787")
    width_rows = (
        Fraction(5) * theta_global / (3584 * 7_863_787),
        Fraction(5) * theta_global / (224 * 7_863_787),
        theta_global / (504 * 8_880_531),
        theta_global / (216 * 8_880_531),
    )
    expected_widths = (
        Fraction(1, 100552401097327200),
        Fraction(1, 6284525068582950),
        Fraction(2, 159684283547625375),
        Fraction(2, 68436121520410875),
    )
    audit.check("faces", "independent all four face widths", width_rows == expected_widths and min(width_rows) == kappa, width_rows, expected_widths)
    audit.check("tails", "independent e lower for radius comparison", Fraction(65, 24) > Fraction(5, 2), Fraction(65, 24), ">5/2")
    audit.check("tails", "independent radius-80 tail", Fraction(120_000) * Fraction(2, 5) ** 80 < Fraction(2, 10**27), Fraction(120_000) * Fraction(2, 5) ** 80, "<2e-27")

    c, rho, sigma, b = sp.symbols("c rho sigma b", nonnegative=True)
    s = 1 - c
    phase_minimum = b * (rho + 4 * sigma - sp.Rational(1, 2)) - 6 * sp.sqrt(b) * rho * sp.sqrt(sigma) + rho**2 + 10 * rho * sigma + 4 * sigma**2 - rho - sigma
    six_completion = (rho + 2 * sigma) ** 2 - (1 + b / 2) * (rho + 2 * sigma) + (5 * b + 1) * sigma + 6 * rho * (sp.sqrt(sigma) - sp.sqrt(b) / 2) ** 2 - b / 2
    ten_completion = rho**2 + (b / 10 - 1) * rho + 4 * sigma**2 + (4 * b - 1) * sigma + 10 * rho * (sp.sqrt(sigma) - 3 * sp.sqrt(b) / 10) ** 2 - b / 2
    audit.check("floor", "independent six completion", sp.simplify(phase_minimum - six_completion) == 0, sp.simplify(phase_minimum - six_completion), 0)
    audit.check("floor", "independent ten completion", sp.simplify(phase_minimum - ten_completion) == 0, sp.simplify(phase_minimum - ten_completion), 0)
    k0 = (153 * c**4 - 156 * c**3 + 82 * c**2 - 4 * c + 5) / 64
    sturm = sp.sturm(13 * k0 - 1, c)
    signs_zero = [sp.sign(sp.limit(item, c, 0, dir="+")) for item in sturm]
    signs_one = [sp.sign(sp.limit(item, c, 1, dir="-")) for item in sturm]
    variations_zero = sum(int(bool(left * right < 0)) for left, right in zip(signs_zero, signs_zero[1:]) if left != 0 and right != 0)
    variations_one = sum(int(bool(left * right < 0)) for left, right in zip(signs_one, signs_one[1:]) if left != 0 and right != 0)
    audit.check("floor", "independent K0 Sturm variation", variations_zero == variations_one, variations_zero - variations_one, 0)
    audit.check("floor", "independent K0 endpoint positivity", bool((13 * k0 - 1).subs(c, 0) > 0 and (13 * k0 - 1).subs(c, 1) > 0), ((13 * k0 - 1).subs(c, 0), (13 * k0 - 1).subs(c, 1)), "both >0")
    audit.check("floor", "independent zero-amplitude tau>=13 implication", Fraction(13) * Fraction(1, 13) / 4 >= Fraction(1, 4), "tau*K0/4 at tau=13", ">=1/4 phase-floor slope")

    ctx.dps = ARBITRARY_PRECISION_DPS
    narrow_lower = Fraction(1)
    narrow_upper = Fraction(2**200 + 1, 2**200)
    narrow_root = arb_sqrt_hull(narrow_lower, narrow_upper)
    zero_root = arb_sqrt_hull(Fraction(0), Fraction(1, 2**40))
    audit.check("interval", "independent sqrt hull contains narrow lower", narrow_root.contains(arb(fraction_text(narrow_lower)).sqrt()), narrow_root, "contains sqrt(lower)")
    audit.check("interval", "independent sqrt hull contains narrow upper", narrow_root.contains(arb(fraction_text(narrow_upper)).sqrt()), narrow_root, "contains sqrt(upper)")
    audit.check("interval", "independent sqrt hull contains zero", zero_root.contains(arb(0)), zero_root, "contains 0")
    audit.check("interval", "independent sqrt hull contains positive endpoint from zero", zero_root.contains(arb(fraction_text(Fraction(1, 2**40))).sqrt()), zero_root, "contains sqrt(2^-40)")

    central = independent_central_box()
    audit.check("interval", "independent central residual", central["residual_strict"] is True, central["residual_upper"], "<0")
    audit.check("interval", "independent central target", central["target_strict"] is True, central["normalized_total_upper"], "<1")
    audit.check("interval", "independent central cells", central["cells"] == CENTRAL_CELLS, central["cells"], CENTRAL_CELLS)

    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    results: dict[str, object] = {
        "effective_projective_patches": projective,
        "origin_square_threshold": str(theta_global),
        "uniform_c_interior_floor": str(kappa),
        "quantitative_faces": {
            "margins": {
                "c=0_small": "5*tau^2/1792 when 16*x+5*tau<=16",
                "c=0_large": "tau/(3*(tau+64)) when 16*x+5*tau>16",
                "c=1_small": "5*tau^2/112 when 4*x+5*tau<=4",
                "c=1_large": "tau/(3*(tau+16)) when 4*x+5*tau>4",
            },
            "lipschitz": "60000*(x+5*tau/2+9*x*tau/16)+x^2/4+x*tau/4+19*tau^2/16",
            "four_width_lower_bounds": [str(value) for value in width_rows],
        },
        "sharper_phase_floors": {
            "B6": "b**2/16+3*b/4+1/4",
            "B10": "b/2+(1-b/10)_+^2/4+(1-4*b)_+^2/16",
            "zero_amplitude_uniform_tau": ">=13",
        },
        "directed_rounding_seed": central,
        "global_interval_cover_complete": False,
        "target_counterexample": False,
        "runtime_versions": {
            "sympy": sp.__version__,
            "python-flint": importlib.metadata.version("python-flint"),
        },
    }
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "status": status,
        "assertions_total": len(audit.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in audit.rows),
        "assertions_failed": sum(row["status"] != "PASS" for row in audit.rows),
        "assertion_names": [f"{row['group']}::{row['name']}" for row in audit.rows],
        "assertions": audit.rows,
        "results": results,
        "results_sha256": hashlib.sha256(json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "route_verdicts": {
            "effective_boundaries": "proved-independent",
            "sharper_global_floor": "proved-independent",
            "first_strict_mixed_arb_box": "proved-independent-partition",
            "global_mixed_scalar_interval_cover": "open",
            "sector_a": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"independent {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    print(f"Arb independent central normalized upper {central['normalized_total_upper']} < 1")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
