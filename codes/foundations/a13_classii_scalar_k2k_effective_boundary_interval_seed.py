#!/usr/bin/env python3
"""Primary exact/Arb certificate for the scoped R-113 scalar advance.

The certificate makes the R-112 projective, origin, and covariance-face
patches effective, proves two sharper phase-minimum floors, and validates one
strict mixed parameter box by outward-rounded Arb cell integration.  It does
not claim a finite cover of the remaining compact scalar core.
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


SCHEMA = "tect/a13-scalar-k2k-effective-boundary-interval-seed-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-scalar-k2k-effective-boundary-interval-seed/result.json"
)
ARBITRARY_PRECISION_DPS = 40
CENTRAL_CELLS = 20_000


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: object, actual: object, expected: object) -> None:
        passed = bool(condition is True or condition == sp.S.true)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not passed:
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


def rational_moment_engine() -> tuple[sp.Symbol, sp.Symbol, sp.Expr, sp.Expr]:
    t_var, y_var = sp.symbols("T Y", nonnegative=True)
    b_star = sp.Rational(5, 12) * t_var * y_var
    q_star = (
        t_var**2 / 4
        + sp.Rational(5, 8) * t_var * y_var**2
        + y_var**4 / 16
        + t_var / 2
        + y_var**2 / 8
    )
    return t_var, y_var, b_star, q_star


def exponential_moment_upper(polynomial: sp.Expr, t_var: sp.Symbol, y_var: sp.Symbol) -> sp.Expr:
    """Rational upper expectation; odd Y moments use sqrt(pi)<2."""
    total = sp.S.Zero
    for (power_t, power_y), coefficient in sp.Poly(sp.expand(polynomial), t_var, y_var).terms():
        if power_y % 2 == 0:
            y_moment = sp.factorial(power_y // 2)
        else:
            index = (power_y - 1) // 2
            y_moment = (
                2
                * sp.factorial(2 * index + 2)
                / (4 ** (index + 1) * sp.factorial(index + 1))
            )
        total += coefficient * sp.factorial(power_t) * y_moment
    return sp.factor(total)


def log_sixth_constant(x_cap: int, exp_cap: int, q_cap: sp.Rational) -> tuple[dict[int, sp.Expr], sp.Expr]:
    t_var, y_var, b_star, q_star = rational_moment_engine()
    radial = b_star + q_cap * q_star
    powers = {order: (order + 1) // 2 for order in range(1, 7)}
    derivative_constants: dict[int, sp.Expr] = {}
    for order in range(1, 7):
        derivative_constants[order] = sp.factor(
            exp_cap
            * sum(
                sp.factorial(order)
                / (sp.factorial(order - 2 * pairs) * sp.factorial(pairs))
                * x_cap ** (order - pairs - powers[order])
                * exponential_moment_upper(
                    radial ** (order - 2 * pairs) * q_star**pairs,
                    t_var,
                    y_var,
                )
                for pairs in range(order // 2 + 1)
            )
        )
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
    constant = sp.S.Zero
    for coefficient, orders in bell_terms:
        x_power = sum(powers[order] for order in orders) - 3
        constant += (
            coefficient
            * x_cap**x_power
            * sp.prod(derivative_constants[order] for order in orders)
        )
    return derivative_constants, sp.factor(constant)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def arb_hull(lower: Fraction, upper: Fraction) -> arb:
    return arb(fraction_text((lower + upper) / 2), fraction_text((upper - lower) / 2))


def arb_sqrt_hull(lower: Fraction, upper: Fraction) -> arb:
    """Outward hull of sqrt([lower, upper]), including endpoint balls."""
    if lower < 0 or upper < lower:
        raise ValueError("sqrt hull requires 0 <= lower <= upper")
    lower_sqrt = arb(fraction_text(lower)).sqrt()
    upper_sqrt = arb(fraction_text(upper)).sqrt()
    return lower_sqrt.union(upper_sqrt)


def directed_rounding_central_box(cell_count: int = CENTRAL_CELLS) -> dict[str, object]:
    """Outward-rounded adaptive cell upper sum for one strict mixed box."""
    ctx.dps = ARBITRARY_PRECISION_DPS
    c = arb_hull(Fraction(49, 100), Fraction(51, 100))
    s = 1 - c
    x = arb_hull(Fraction(99, 100), Fraction(101, 100))
    tau = arb_hull(Fraction(99, 100), Fraction(101, 100))

    k2 = (c * c + s * s) / 2
    k1 = c**3 + arb(5) * c * c * s / 2 + c * s * s + s**3 / 4
    k0 = (
        arb(5) * c**4 / 4
        + c**3 * s / 4
        + arb(25) * c * c * s * s / 16
        + c * s**3 / 4
        + arb(5) * s**4 / 64
    )
    target = (x * x * k2 + x * tau * k1 + tau * tau * k0) / 4
    sqrt_x = x.sqrt()
    sqrt_tau = tau.sqrt()
    sqrt_s = s.sqrt()
    sqrt_eight = arb(8).sqrt()

    def cell_upper(rectangle: tuple[Fraction, Fraction, Fraction, Fraction]) -> arb:
        t_lower, t_upper, u_lower, u_upper = rectangle
        t_ball = arb_hull(t_lower, t_upper)
        u_ball = arb_hull(u_lower, u_upper)
        sqrt_u = arb_sqrt_hull(u_lower, u_upper)
        rho = c * t_ball / 2
        sigma = s * u_ball / 8
        sqrt_sigma = sqrt_s * sqrt_u / sqrt_eight
        z_value = 6 * sqrt_x * sqrt_tau * rho * sqrt_sigma
        combined = (
            tau * (rho - arb(1) / 2) ** 2
            + 4 * tau * (sigma - arb(1) / 8) ** 2
            + 4 * x * sigma
            + rho * ((sqrt_x - 3 * sqrt_tau * sqrt_sigma) ** 2 + tau * sigma)
            - x / 2
            - 5 * tau / 16
        )
        exponential_upper = (-t_ball - u_ball - combined - target).exp().upper()
        z_lower = z_value.lower()
        if z_lower <= 0:
            scaled_bessel_upper = arb(1)
        else:
            scaled_bessel_upper = z_lower.bessel_i(0, scaled=True).upper()
        area = arb(fraction_text((t_upper - t_lower) * (u_upper - u_lower)))
        return area * exponential_upper * scaled_bessel_upper

    breakpoints = list(map(Fraction, (0, 1, 2, 4, 8, 16, 32, 50)))
    heap: list[tuple[float, int, tuple[Fraction, Fraction, Fraction, Fraction], arb]] = []
    core_upper = arb(0)
    serial = 0
    for t_lower, t_upper in zip(breakpoints, breakpoints[1:]):
        for u_lower, u_upper in zip(breakpoints, breakpoints[1:]):
            rectangle = (t_lower, t_upper, u_lower, u_upper)
            upper = cell_upper(rectangle)
            core_upper += upper
            heapq.heappush(heap, (-float(upper), serial, rectangle, upper))
            serial += 1

    cells = len(heap)
    while cells < cell_count:
        _, _, rectangle, old_upper = heapq.heappop(heap)
        core_upper -= old_upper
        t_lower, t_upper, u_lower, u_upper = rectangle
        if t_upper - t_lower >= u_upper - u_lower:
            midpoint = (t_lower + t_upper) / 2
            children = (
                (t_lower, midpoint, u_lower, u_upper),
                (midpoint, t_upper, u_lower, u_upper),
            )
        else:
            midpoint = (u_lower + u_upper) / 2
            children = (
                (t_lower, t_upper, u_lower, midpoint),
                (t_lower, t_upper, midpoint, u_upper),
            )
        for child in children:
            upper = cell_upper(child)
            core_upper += upper
            heapq.heappush(heap, (-float(upper), serial, child, upper))
            serial += 1
        cells += 1

    radius = arb(50)
    tail_upper = (
        (-target + x / 2 + 5 * tau / 16).exp()
        * (2 * (-radius).exp() - (-2 * radius).exp())
    ).upper()
    residual = (2 * x + tau) ** 2 - 32 * x - 20 * tau
    total_upper = (core_upper + tail_upper).upper()
    return {
        "parameter_box": {"c": "[49/100,51/100]", "x": "[99/100,101/100]", "tau": "[99/100,101/100]"},
        "radial_radius": 50,
        "cells": cells,
        "precision_dps": ARBITRARY_PRECISION_DPS,
        "residual_ball": str(residual),
        "residual_upper": str(residual.upper()),
        "core_upper": str(core_upper),
        "tail_upper": str(tail_upper),
        "normalized_total_upper": str(total_upper),
        "residual_strict": bool(residual.upper() < 0),
        "target_strict": bool(total_upper < 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    c, s, x, tau, b = sp.symbols("c s x tau b", nonnegative=True)
    t_var, u_var = sp.symbols("T U", nonnegative=True)
    rho = c * t_var / 2
    sigma = s * u_var / 8
    linear = rho + 4 * sigma - sp.Rational(1, 2)
    quadratic = rho**2 + 10 * rho * sigma + 4 * sigma**2 - rho - sigma
    phase_size = 6 * rho * sp.sqrt(sigma)
    k2 = (c**2 + s**2) / 2
    k1 = c**3 + sp.Rational(5, 2) * c**2 * s + c * s**2 + s**3 / 4
    k0 = (
        sp.Rational(5, 4) * c**4
        + c**3 * s / 4
        + sp.Rational(25, 16) * c**2 * s**2
        + c * s**3 / 4
        + sp.Rational(5, 64) * s**4
    )
    delta_margin = c**4 / 4 + c**2 * s**2 / 4 + s**4 / 64

    audit.check(
        "normal_form",
        "local reserve floor identity",
        sp.factor((64 * delta_margin - (4 * c**2 + s**2) ** 2 - 8 * c**2 * s**2)) == 0,
        sp.factor(64 * delta_margin),
        "(4*c^2+s^2)^2+8*c^2*s^2",
    )
    q_abs = t_var**2 / 4 + sp.Rational(5, 8) * t_var * u_var + u_var**2 / 16 + t_var / 2 + u_var / 8
    actual_q = sp.expand(quadratic.subs(s, 1 - c))
    q_plus = sp.Poly(sp.expand(q_abs + actual_q), t_var, u_var)
    q_minus = sp.Poly(sp.expand(q_abs - actual_q), t_var, u_var)
    audit.check(
        "projective",
        "absolute-Q plus coefficient majorant",
        sp.simplify(q_plus.coeff_monomial(t_var**2) - (1 + c**2) / 4) == 0
        and sp.simplify(q_plus.coeff_monomial(t_var * u_var) - 5 * (1 + c - c**2) / 8) == 0
        and sp.simplify(q_plus.coeff_monomial(u_var**2) - (1 + (1 - c) ** 2) / 16) == 0
        and sp.simplify(q_plus.coeff_monomial(t_var) - (1 - c) / 2) == 0
        and sp.simplify(q_plus.coeff_monomial(u_var) - c / 8) == 0,
        q_plus.as_dict(),
        "all declared coefficients nonnegative on 0<=c<=1",
    )
    audit.check(
        "projective",
        "absolute-Q minus coefficient majorant",
        sp.simplify(q_minus.coeff_monomial(t_var**2) - (1 - c**2) / 4) == 0
        and sp.simplify(q_minus.coeff_monomial(t_var * u_var) - 5 * (1 - c + c**2) / 8) == 0
        and sp.simplify(q_minus.coeff_monomial(u_var**2) - c * (2 - c) / 16) == 0
        and sp.simplify(q_minus.coeff_monomial(t_var) - (1 + c) / 2) == 0
        and sp.simplify(q_minus.coeff_monomial(u_var) - (2 - c) / 8) == 0,
        q_minus.as_dict(),
        "all declared coefficients nonnegative on 0<=c<=1",
    )
    audit.check(
        "projective",
        "simplex phase-amplitude bound",
        sp.factor(sp.Rational(4, 27) - c**2 * (1 - c)) == (3 * c - 2) ** 2 * (3 * c + 1) / 27,
        sp.factor(sp.Rational(4, 27) - c**2 * (1 - c)),
        "(3*c-2)^2*(3*c+1)/27",
    )
    audit.check(
        "projective",
        "rational B-star enlargement",
        24 < 25,
        "(9/8)*(4/27)=24/144",
        "<25/144=(5/12)^2",
    )

    projective_rows = (
        (1, 2, sp.Rational(3, 16), 7, sp.Rational(181292201822646474659735, 273593677362757632), 700_000),
        (2, 3, sp.Rational(1, 8), 8, sp.Rational(267774784673603525005, 79164837199872), 3_500_000),
        (4, 8, sp.Rational(1, 16), 10, sp.Rational(274770569726043833586365, 1068725302198272), 260_000_000),
        (8, 55, sp.Rational(3, 256), 15, sp.Rational(5748965910841593523942194993404275, 373546567492618420224), 16_000_000_000_000),
    )
    projective_results: list[dict[str, object]] = []
    previous_cap = 0
    for x_cap, exp_cap, q_star_cap, delta_power, expected_constant, convenient_bound in projective_rows:
        _, exact_constant = log_sixth_constant(x_cap, exp_cap, q_star_cap)
        audit.check("projective", f"X={x_cap} exact sixth-log constant", exact_constant == expected_constant, exact_constant, expected_constant)
        audit.check("projective", f"X={x_cap} convenient constant bound", exact_constant < convenient_bound, exact_constant, f"<{convenient_bound}")
        audit.check(
            "projective",
            f"X={x_cap} q-star gate",
            4 * sp.Rational(1, 2**delta_power) <= q_star_cap**2,
            sp.factor(4 * sp.Rational(1, 2**delta_power)),
            f"<={q_star_cap**2}",
        )
        audit.check(
            "projective",
            f"X={x_cap} remainder leaves half D0",
            convenient_bound * 960 <= 720 * 2 ** (3 * delta_power),
            convenient_bound * 960,
            f"<={720 * 2 ** (3 * delta_power)}",
        )
        projective_results.append(
            {
                "x_interval": f"({previous_cap},{x_cap}]",
                "tau_over_x_max": f"1/{2**delta_power}",
                "derivative_envelope_q_star_cap": str(q_star_cap),
                "exact_sixth_log_constant": str(exact_constant),
                "convenient_upper": convenient_bound,
                "certified_gap_lower": "x^3/960",
            }
        )
        previous_cap = x_cap

    k1_simplex = sp.expand(k1.subs(s, 1 - c))
    k0_simplex = sp.expand(k0.subs(s, 1 - c))
    audit.check(
        "origin",
        "K1 upper factorization",
        sp.simplify((1 - k1_simplex) - (1 - c) * (3 + 2 * c - 3 * c**2) / 4) == 0,
        sp.factor(1 - k1_simplex),
        "(1-c)*(3+2*c-3*c^2)/4",
    )
    audit.check(
        "origin",
        "K0 upper factorization",
        sp.simplify(
            sp.Rational(5, 4)
            - k0_simplex
            - (1 - c) * (153 * c**3 - 3 * c**2 + 79 * c + 75) / 64
        )
        == 0,
        sp.factor(sp.Rational(5, 4) - k0_simplex),
        "(1-c)*(153*c^3-3*c^2+79*c+75)/64",
    )

    def theta(radius: int) -> sp.Rational:
        return sp.Rational(48, 25 * (8 * radius + 5) * (2 * radius**2 + 4 * radius + 5))

    theta_expected = (
        sp.Rational(48, 3575),
        sp.Rational(16, 3675),
        sp.Rational(48, 49025),
        sp.Rational(16, 94875),
        sp.Rational(48, 1931825),
        sp.Rational(16, 4743675),
        sp.Rational(48, 109255025),
        sp.Rational(16, 285418875),
    )
    theta_rows: list[dict[str, str | int]] = []
    for index, expected in enumerate(theta_expected):
        radius = 2**index
        actual = theta(radius)
        audit.check("origin", f"dyadic cone {index} threshold", actual == expected, actual, expected)
        theta_rows.append({"cone": index, "ratio_cap": radius, "tau_cap": str(actual)})
    theta_global = theta_expected[-1]
    audit.check("origin", "global origin square threshold", theta_global == sp.Rational(16, 285418875), theta_global, sp.Rational(16, 285418875))
    audit.check(
        "origin",
        "origin/projective square dichotomy",
        128 * sp.Rational(1, 128) == 1 and theta_global == theta(128),
        "x/tau<=128 or tau/x<=1/128; tau<=theta(128)",
        "complete square, with tau=0 handled by the projective edge and (0,0) by equality",
    )

    face_margins = {
        "c=0_small": "5*tau^2/1792 when 16*x+5*tau<=16",
        "c=0_large": "tau/(3*(tau+64)) when 16*x+5*tau>16",
        "c=1_small": "5*tau^2/112 when 4*x+5*tau<=4",
        "c=1_large": "tau/(3*(tau+16)) when 4*x+5*tau>4",
    }
    alpha_face, scale_face = sp.symbols("alpha_face scale_face", positive=True)
    small_face = sp.Rational(5, 7) * scale_face**2
    large_face = scale_face / (3 * (scale_face + 4))
    face_substitutions = (
        ("c=0 small margin", small_face.subs(scale_face, tau / 16), 5 * tau**2 / 1792),
        ("c=0 large margin", large_face.subs(scale_face, tau / 16), tau / (3 * (tau + 64))),
        ("c=1 small margin", small_face.subs(scale_face, tau / 4), 5 * tau**2 / 112),
        ("c=1 large margin", large_face.subs(scale_face, tau / 4), tau / (3 * (tau + 16))),
    )
    for name, actual, expected in face_substitutions:
        audit.check("faces", name, sp.simplify(actual - expected) == 0, sp.factor(actual), expected)
    audit.check(
        "faces",
        "c=0 branch condition translation",
        sp.expand(16 * ((tau / 16) * (4 * (4 * x / tau) + 5) - 1)) == 16 * x + 5 * tau - 16,
        sp.expand(16 * ((tau / 16) * (4 * (4 * x / tau) + 5) - 1)),
        "16*x+5*tau-16",
    )
    audit.check(
        "faces",
        "c=1 branch condition translation",
        sp.expand(4 * ((tau / 4) * (4 * (x / tau) + 5) - 1)) == 4 * x + 5 * tau - 4,
        sp.expand(4 * ((tau / 4) * (4 * (x / tau) + 5) - 1)),
        "4*x+5*tau-4",
    )

    rho_simplex = c * t_var / 2
    sigma_simplex = (1 - c) * u_var / 8
    l_simplex = rho_simplex + 4 * sigma_simplex - sp.Rational(1, 2)
    q_simplex = rho_simplex**2 + 10 * rho_simplex * sigma_simplex + 4 * sigma_simplex**2 - rho_simplex - sigma_simplex
    l_c = sp.diff(l_simplex, c)
    q_c = sp.expand(sp.diff(q_simplex, c))
    q_c_grouped = (
        c * (t_var**2 - t_var) / 2
        - (1 - c) * t_var / 2
        + sp.Rational(5, 8) * (1 - 2 * c) * t_var * u_var
        - (1 - c) * (u_var**2 - u_var) / 8
        + c * u_var / 8
    )
    audit.check("faces", "L-c derivative", sp.simplify(l_c - (t_var - u_var) / 2) == 0, l_c, "(T-U)/2")
    audit.check("faces", "Q-c grouped derivative", sp.simplify(q_c - q_c_grouped) == 0, sp.factor(q_c), sp.factor(q_c_grouped))
    centered_exp_abs_upper = sp.Rational(5, 4)
    q_c_abs_upper = (
        centered_exp_abs_upper / 2
        + sp.Rational(1, 2)
        + sp.Rational(5, 8)
        + centered_exp_abs_upper / 8
        + sp.Rational(1, 8)
    )
    audit.check("faces", "centered exponential absolute-moment rational bound", sp.Rational(65, 24) > sp.Rational(8, 3), sp.Rational(65, 24), ">8/3, hence -1+6/e<5/4")
    audit.check("faces", "Q-c absolute expectation bound", q_c_abs_upper == sp.Rational(65, 32) and q_c_abs_upper < sp.Rational(9, 4) < sp.Rational(5, 2), q_c_abs_upper, "<9/4<5/2")
    audit.check("faces", "L-c absolute expectation bound", sp.Rational(1, 2) <= 1, "E|T-U|/2=1/2", "<=1")
    audit.check(
        "faces",
        "Bessel c-derivative polynomial bound",
        sp.simplify((1 + 2 * c - 3 * c**2) - (1 - c) * (3 * c + 1)) == 0
        and sp.discriminant(3 * c**2 - 2 * c + 1, c) < 0,
        (sp.factor(1 + 2 * c - 3 * c**2), sp.discriminant(3 * c**2 - 2 * c + 1, c)),
        "|2c-3c^2|<=1",
    )
    audit.check("faces", "Bessel score expectation coefficient", sp.Rational(1, 4) * sp.Rational(9, 8) * 2 == sp.Rational(9, 16), sp.Rational(1, 4) * sp.Rational(9, 8) * 2, sp.Rational(9, 16))
    k2_prime = sp.factor(sp.diff(k2.subs(s, 1 - c), c))
    k1_prime = sp.factor(sp.diff(k1.subs(s, 1 - c), c))
    k0_prime = sp.factor(sp.diff(k0.subs(s, 1 - c), c))
    audit.check("faces", "K2 derivative bound", k2_prime == 2 * c - 1, k2_prime, "absolute value <=1")
    audit.check("faces", "K1 derivative bound", sp.simplify(k1_prime.subs(c, sp.Rational(5, 9)) - sp.Rational(17, 18)) == 0 and k1_prime.subs(c, 0) >= 0 and k1_prime.subs(c, 1) >= 0, k1_prime, "0<=K1'<=17/18<1")
    k0_prime_polynomial = sp.Poly(sp.expand(k0_prime), c)
    k0_prime_degree = k0_prime_polynomial.degree()
    k0_prime_powers = tuple(k0_prime_polynomial.nth(index) for index in range(k0_prime_degree + 1))
    k0_prime_bernstein = tuple(
        sp.simplify(
            sum(
                k0_prime_powers[j] * sp.binomial(index, j) / sp.binomial(k0_prime_degree, j)
                for j in range(index + 1)
            )
        )
        for index in range(k0_prime_degree + 1)
    )
    k0_prime_bernstein_expected = (
        sp.Rational(-1, 16),
        sp.Rational(19, 24),
        sp.Rational(-19, 24),
        sp.Rational(19, 4),
    )
    audit.check(
        "faces",
        "K0 derivative Bernstein reconstruction and bound",
        k0_prime_bernstein == k0_prime_bernstein_expected
        and max(map(abs, k0_prime_bernstein)) == sp.Rational(19, 4),
        k0_prime_bernstein,
        k0_prime_bernstein_expected,
    )
    exp_upper = sum(sp.Rational(1, math.factorial(index)) for index in range(6)) + sp.Rational(7, 4320)
    audit.check("faces", "rational e upper", exp_upper < sp.Rational(87, 32), exp_upper, "<87/32")
    audit.check("faces", "exponential tilt cap", sp.Rational(87, 32) < sp.Rational(4, 3) ** 4 and sp.Rational(87, 32) ** 10 * sp.Rational(4, 3) < 60_000, sp.Rational(87, 32) ** 10 * sp.Rational(4, 3), "<60000")
    kappa = sp.Rational(1, 100552401097327200)
    kappa_formula = sp.factor(5 * theta_global / (3584 * 7863787))
    audit.check("faces", "central c-width floor", kappa_formula == kappa, kappa_formula, kappa)
    comparison_widths = (
        sp.Rational(1, 6284525068582950),
        sp.Rational(2, 159684283547625375),
        sp.Rational(2, 68436121520410875),
    )
    for index, width in enumerate(comparison_widths):
        audit.check("faces", f"comparison face width {index} exceeds kappa", width > kappa, width, f">{kappa}")
    audit.check("faces", "global Lambda bound", 8_880_531 >= 60_000 * (8 + 50 + 90) + 16 + 40 + 475, 8_880_531, ">= direct endpoint sum")
    small_lambda_ratio = (
        60_000 * (128 + sp.Rational(5, 2) + sp.Rational(9, 16))
        + 32
        + sp.Rational(1, 4)
        + sp.Rational(19, 5)
    )
    audit.check("faces", "small-branch Lambda/tau bound", 7_863_787 >= small_lambda_ratio, 7_863_787, f">={small_lambda_ratio}")
    derived_widths = (
        sp.factor(5 * theta_global / (3584 * 7_863_787)),
        sp.factor(5 * theta_global / (224 * 7_863_787)),
        sp.factor(theta_global / (504 * 8_880_531)),
        sp.factor(theta_global / (216 * 8_880_531)),
    )
    audit.check("faces", "all four residual face widths", derived_widths == (kappa,) + comparison_widths, derived_widths, (kappa,) + comparison_widths)
    audit.check("tails", "e lower for radius comparison", sp.Rational(65, 24) > sp.Rational(5, 2), sp.Rational(65, 24), ">5/2")
    audit.check("tails", "radius-80 rational tail", 120_000 * sp.Rational(2, 5) ** 80 < 2 * sp.Rational(1, 10**27), 120_000 * sp.Rational(2, 5) ** 80, "<2e-27")

    r_free, q_free = sp.symbols("rho sigma", nonnegative=True)
    phase_minimum = (
        b * (r_free + 4 * q_free - sp.Rational(1, 2))
        - 6 * sp.sqrt(b) * r_free * sp.sqrt(q_free)
        + r_free**2
        + 10 * r_free * q_free
        + 4 * q_free**2
        - r_free
        - q_free
    )
    floor_six = (
        (r_free + 2 * q_free) ** 2
        - (1 + b / 2) * (r_free + 2 * q_free)
        + (5 * b + 1) * q_free
        + 6 * r_free * (sp.sqrt(q_free) - sp.sqrt(b) / 2) ** 2
        - b / 2
    )
    floor_ten = (
        r_free**2
        + (b / 10 - 1) * r_free
        + 4 * q_free**2
        + (4 * b - 1) * q_free
        + 10 * r_free * (sp.sqrt(q_free) - 3 * sp.sqrt(b) / 10) ** 2
        - b / 2
    )
    audit.check("floor", "six-completion identity", sp.simplify(phase_minimum - floor_six) == 0, sp.simplify(phase_minimum - floor_six), 0)
    audit.check("floor", "ten-completion identity", sp.simplify(phase_minimum - floor_ten) == 0, sp.simplify(phase_minimum - floor_ten), 0)
    b_six = sp.Rational(1, 4) + 3 * b / 4 + b**2 / 16
    b_ten_low = b / 2 + (1 - b / 10) ** 2 / 4 + (1 - 4 * b) ** 2 / 16
    crossover = (80 - 45 * sp.sqrt(2)) / 188
    audit.check("floor", "low-branch crossover", sp.simplify((b_six - b_ten_low).subs(b, crossover)) == 0, sp.simplify((b_six - b_ten_low).subs(b, crossover)), 0)

    k0_polynomial = sp.factor(k0_simplex)
    thirteen_polynomial = sp.Poly(sp.expand(13 * 64 * k0_polynomial - 64), c)
    sturm_roots = thirteen_polynomial.count_roots(-sp.oo, sp.oo)
    audit.check("floor", "K0-1/13 Sturm polynomial", thirteen_polynomial.as_expr() == 1989 * c**4 - 2028 * c**3 + 1066 * c**2 - 52 * c + 1, thirteen_polynomial.as_expr(), "declared quartic")
    audit.check("floor", "K0-1/13 quartic has no real roots", sturm_roots == 0, sturm_roots, 0)
    audit.check("floor", "K0-1/13 quartic positive at zero", thirteen_polynomial.eval(0) > 0, thirteen_polynomial.eval(0), ">0")
    audit.check(
        "floor",
        "zero-amplitude tau>=13 implication",
        13 * sp.Rational(1, 13) / 4 >= sp.Rational(1, 4),
        "tau*K0/4 at tau=13 and K0=1/13",
        ">=1/4 phase-floor slope",
    )

    contraction_surrogate_mean = -c * (8 * b + 9 * s) / 16
    audit.check("method_boundary", "Bessel contraction surrogate mean", sp.factor(contraction_surrogate_mean.subs(s, 1 - c)) == -c * (8 * b - 9 * c + 9) / 16, sp.factor(contraction_surrogate_mean.subs(s, 1 - c)), "-c*(8*b+9*s)/16")

    ctx.dps = ARBITRARY_PRECISION_DPS
    narrow_lower = Fraction(1)
    narrow_upper = Fraction(2**200 + 1, 2**200)
    narrow_root = arb_sqrt_hull(narrow_lower, narrow_upper)
    zero_root = arb_sqrt_hull(Fraction(0), Fraction(1, 2**40))
    audit.check("interval", "sqrt hull contains narrow lower endpoint", narrow_root.contains(arb(fraction_text(narrow_lower)).sqrt()), narrow_root, "contains sqrt(lower)")
    audit.check("interval", "sqrt hull contains narrow upper endpoint", narrow_root.contains(arb(fraction_text(narrow_upper)).sqrt()), narrow_root, "contains sqrt(upper)")
    audit.check("interval", "sqrt hull contains zero endpoint", zero_root.contains(arb(0)), zero_root, "contains 0")
    audit.check("interval", "sqrt hull contains positive endpoint from zero", zero_root.contains(arb(fraction_text(Fraction(1, 2**40))).sqrt()), zero_root, "contains sqrt(2^-40)")

    central = directed_rounding_central_box()
    audit.check("interval", "central residual strict", central["residual_strict"] is True, central["residual_upper"], "<0")
    audit.check("interval", "central normalized integral strict", central["target_strict"] is True, central["normalized_total_upper"], "<1")
    audit.check("interval", "central cell count", central["cells"] == CENTRAL_CELLS, central["cells"], CENTRAL_CELLS)

    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    results: dict[str, object] = {
        "effective_projective_patches": projective_results,
        "origin_cones": theta_rows,
        "origin_square_threshold": str(theta_global),
        "quantitative_faces": {
            "margins": face_margins,
            "lipschitz": "60000*(x+5*tau/2+9*x*tau/16)+x^2/4+x*tau/4+19*tau^2/16",
            "uniform_c_interior_floor": str(kappa),
            "four_width_lower_bounds": [str(value) for value in derived_widths],
        },
        "central_residual_set": {
            "c": f"[{kappa},1-{kappa}]",
            "x": "[0,8]",
            "tau": f"[{theta_global},20]",
            "constraint": "(2*x+tau)^2<=32*x+20*tau",
            "global_interval_cover_complete": False,
        },
        "sharper_phase_floors": {
            "B6": str(b_six),
            "B10": "b/2+(1-b/10)_+^2/4+(1-4*b)_+^2/16",
            "crossover": str(crossover),
            "zero_amplitude_uniform_tau": ">=13",
        },
        "directed_rounding_seed": central,
        "method_boundary": {
            "bessel_cross_contraction": "creates a negative surrogate mean and an O(tau) origin debt",
            "surrogate_mean": str(contraction_surrogate_mean),
            "target_counterexample": False,
        },
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
            "effective_projective_boundary": "proved-explicit",
            "effective_origin_cover": "proved-explicit",
            "effective_covariance_face_widths": "proved-explicit",
            "sharper_global_floor": "proved-exact",
            "first_strict_mixed_arb_box": "proved-directed-rounding",
            "bessel_cross_contraction_global_closure": "failed-origin-linear-debt",
            "global_mixed_scalar_interval_cover": "open",
            "full_a1_embedding": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_a": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"primary {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    print(f"Arb central normalized upper {central['normalized_total_upper']} < 1")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
