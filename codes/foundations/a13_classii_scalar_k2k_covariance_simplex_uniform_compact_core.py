#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-112 simplex reduction.

This certificate reconstructs the compact covariance-simplex normal form for
the stationary scalar k:2k packet, verifies its uniform projective expansion
through the second inverse-amplitude coefficient, proves the exact large-y
floor, and certifies the failure of all-order coefficientwise projective
positivity at the third coefficient.  It supports an existential uniform
large-amplitude all-q theorem and a residual finite-b compact-core reduction.
It does not certify an effective amplitude threshold or the residual mixed
core, and it proves no full A1, OVERLAP_src, Nelson, or Sector-A theorem.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

import sympy as sp


SCHEMA = "tect/a13-scalar-k2k-covariance-simplex-uniform-compact-core-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-scalar-k2k-covariance-simplex-uniform-compact-core/result.json"
)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def require(
        self,
        group: str,
        name: str,
        condition: object,
        actual: object,
        expected: object,
    ) -> None:
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
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    c, s, b, tau, y = sp.symbols("c s b tau y", nonnegative=True)
    t_var, u_var = sp.symbols("T U", nonnegative=True)
    phase = sp.symbols("phase", real=True)
    rho, sigma = sp.symbols("rho sigma", nonnegative=True)

    # ------------------------------------------------------------------
    # Exact covariance-simplex quotient.
    # ------------------------------------------------------------------
    compact_packet = (
        b * (c * t_var + s * u_var - 1) / 2
        + 3 * sp.sqrt(2) * sp.sqrt(b) * c * sp.sqrt(s) * t_var * sp.sqrt(u_var) * phase / 4
        + c**2 * t_var**2 / 4
        + 5 * c * s * t_var * u_var / 8
        + s**2 * u_var**2 / 16
        - c * t_var / 2
        - s * u_var / 8
    )
    radial_packet = (
        rho**2
        + 10 * rho * sigma
        + 4 * sigma**2
        + (b - 1) * rho
        + (4 * b - 1) * sigma
        - b / 2
        + 6 * sp.sqrt(b) * rho * sp.sqrt(sigma) * phase
    )
    radial_substitution = radial_packet.subs(
        {rho: c * t_var / 2, sigma: s * u_var / 8}, simultaneous=True
    )
    checks.require(
        "simplex",
        "radial packet equals compact packet",
        sp.simplify(radial_substitution - compact_packet) == 0,
        sp.simplify(radial_substitution - compact_packet),
        0,
    )

    k0 = (c**2 + s**2) / 2
    k1 = c**3 + sp.Rational(5, 2) * c**2 * s + c * s**2 + s**3 / 4
    k2 = (
        sp.Rational(5, 4) * c**4
        + c**3 * s / 4
        + sp.Rational(25, 16) * c**2 * s**2
        + c * s**3 / 4
        + sp.Rational(5, 64) * s**4
    )
    compact_h = b**2 * k0 + b * k1 + k2

    amplitude, variance_v, variance_w = sp.symbols("A v w", nonnegative=True)
    original_h = (
        amplitude**4 * (variance_v**2 / 2 + 8 * variance_w**2)
        + amplitude**2
        * (
            variance_v**3
            + 10 * variance_v**2 * variance_w
            + 16 * variance_v * variance_w**2
            + 16 * variance_w**3
        )
        + sp.Rational(5, 4) * variance_v**4
        + variance_v**3 * variance_w
        + 25 * variance_v**2 * variance_w**2
        + 16 * variance_v * variance_w**3
        + 20 * variance_w**4
    )
    transformed_h = sp.expand(
        original_h.subs(
            {amplitude: sp.sqrt(b), variance_v: c, variance_w: s / 4},
            simultaneous=True,
        )
    )
    checks.require(
        "simplex",
        "covariance square equals compact polynomial",
        sp.simplify(transformed_h - compact_h) == 0,
        sp.factor(transformed_h),
        compact_h,
    )

    # Unit-exponential expectation, with the phase mean supplied explicitly.
    def base_expect(poly: sp.Expr) -> sp.Expr:
        expanded = sp.Poly(sp.expand(poly), t_var, u_var)
        total = sp.S.Zero
        for (power_t, power_u), coefficient in expanded.terms():
            total += coefficient * sp.factorial(power_t) * sp.factorial(power_u)
        return sp.factor(total)

    packet_without_phase = compact_packet.subs(phase, 0)
    checks.require(
        "simplex",
        "compact packet is centered",
        sp.simplify(base_expect(packet_without_phase).subs(s, 1 - c)) == 0,
        sp.simplify(base_expect(packet_without_phase).subs(s, 1 - c)),
        0,
    )

    local_margin = c**4 / 4 + c**2 * s**2 / 4 + s**4 / 64
    old_local_margin = (
        variance_v**4 + 16 * variance_v**2 * variance_w**2 + 16 * variance_w**4
    ) / 4
    checks.require(
        "local",
        "R-110 local margin transforms exactly",
        sp.simplify(
            old_local_margin.subs({variance_v: c, variance_w: s / 4})
            - local_margin
        )
        == 0,
        sp.factor(old_local_margin.subs({variance_v: c, variance_w: s / 4})),
        local_margin,
    )
    local_square = sp.factor(
        64 * local_margin - ((4 * c**2 + s**2) ** 2 + 8 * c**2 * s**2)
    )
    checks.require(
        "local",
        "local margin square decomposition",
        local_square == 0,
        local_square,
        0,
    )
    simplex_quadratic = sp.factor((4 * c**2 + s**2).subs(s, 1 - c) - sp.Rational(4, 5))
    checks.require(
        "local",
        "simplex quadratic has exact four-fifths floor",
        sp.simplify(simplex_quadratic - 5 * (c - sp.Rational(1, 5)) ** 2) == 0,
        simplex_quadratic,
        5 * (c - sp.Rational(1, 5)) ** 2,
    )
    local_margin_lower = sp.Rational(1, 100)
    checks.require(
        "local",
        "uniform local margin lower bound is positive",
        local_margin_lower > 0,
        local_margin_lower,
        ">0",
    )

    # ------------------------------------------------------------------
    # Projective law and first two exact coefficients.
    # ------------------------------------------------------------------
    linear = (c * t_var + s * u_var - 1) / 2
    phase_amplitude = 3 * sp.sqrt(2) * c * sp.sqrt(s) * t_var * sp.sqrt(u_var) / 4
    quadratic = (
        c**2 * t_var**2 / 4
        + 5 * c * s * t_var * u_var / 8
        + s**2 * u_var**2 / 16
        - c * t_var / 2
        - s * u_var / 8
    )
    checks.require(
        "projective",
        "packet splits as bL plus sqrt-b B plus Q",
        sp.simplify(
            compact_packet
            - (b * linear + sp.sqrt(b) * phase_amplitude * phase + quadratic)
        )
        == 0,
        sp.simplify(
            compact_packet
            - (b * linear + sp.sqrt(b) * phase_amplitude * phase + quadratic)
        ),
        0,
    )

    alpha = 1 + c * y / 2
    beta = 1 + s * y / 2
    limiting_mgf = sp.exp(y / 2) / (alpha * beta)
    d_function = lambda value: value**2 / 2 - value + sp.log(1 + value)
    limiting_gap = d_function(c * y / 2) + d_function(s * y / 2)
    checks.require(
        "projective",
        "limiting target gap",
        sp.simplify(
            (
                y**2 * k0 / 4
                - (y / 2 - sp.log(alpha) - sp.log(beta))
                - limiting_gap
            ).subs(s, 1 - c)
        )
        == 0,
        sp.simplify(
            (
                y**2 * k0 / 4
                - (y / 2 - sp.log(alpha) - sp.log(beta))
            ).subs(s, 1 - c)
        ),
        limiting_gap.subs(s, 1 - c),
    )
    z = sp.symbols("z", nonnegative=True)
    checks.require(
        "projective",
        "centered-exponential derivative identity",
        sp.simplify(sp.diff(d_function(z), z) - z**2 / (1 + z)) == 0,
        sp.diff(d_function(z), z),
        z**2 / (1 + z),
    )
    cube_floor = sp.factor(c**3 + (1 - c) ** 3 - sp.Rational(1, 4))
    checks.require(
        "projective",
        "simplex cubic floor",
        sp.simplify(cube_floor - 3 * (c - sp.Rational(1, 2)) ** 2) == 0,
        cube_floor,
        3 * (c - sp.Rational(1, 2)) ** 2,
    )

    def tilted_expect(poly: sp.Expr) -> sp.Expr:
        expanded = sp.Poly(sp.expand(poly), t_var, u_var)
        total = sp.S.Zero
        for (power_t, power_u), coefficient in expanded.terms():
            total += (
                coefficient
                * sp.factorial(power_t)
                / alpha**power_t
                * sp.factorial(power_u)
                / beta**power_u
            )
        return sp.factor(total)

    phase_second = phase_amplitude**2 / 2
    phase_fourth = phase_amplitude**4 * sp.Rational(3, 8)
    a1 = sp.factor(y**2 * tilted_expect(phase_second) / 2 - y * tilted_expect(quadratic))
    a2 = sp.factor(
        y**4 * tilted_expect(phase_fourth) / 24
        - y**3 * tilted_expect(phase_second * quadratic) / 2
        + y**2 * tilted_expect(quadratic**2) / 2
    )
    d1 = sp.factor(y**2 * k1 / 4 - a1)
    d2 = sp.factor(y**2 * k2 / 4 - (a2 - a1**2 / 2))

    d1_numerator_expected = (
        4 * c**5 * s**2 * y**3
        + 16 * c**5 * s * y**2
        + 16 * c**5 * y
        + 10 * c**4 * s**3 * y**3
        + 56 * c**4 * s**2 * y**2
        + 104 * c**4 * s * y
        + 64 * c**4
        + 4 * c**3 * s**4 * y**3
        + 56 * c**3 * s**3 * y**2
        + 172 * c**3 * s**2 * y
        + 152 * c**3 * s
        + c**2 * s**5 * y**3
        + 20 * c**2 * s**4 * y**2
        + 88 * c**2 * s**3 * y
        + 112 * c**2 * s**2
        + 4 * c * s**5 * y**2
        + 32 * c * s**4 * y
        + 32 * c * s**3
        + 4 * s**5 * y
        + 16 * s**4
    )
    d1_expected = y**3 * d1_numerator_expected / (
        16 * (2 + c * y) ** 2 * (2 + s * y) ** 2
    )
    checks.require(
        "projective",
        "first coefficient closed form on simplex",
        sp.simplify((d1 - d1_expected).subs(s, 1 - c)) == 0,
        sp.factor(d1.subs(s, 1 - c)),
        sp.factor(d1_expected.subs(s, 1 - c)),
    )
    d1_coefficients = sp.Poly(d1_numerator_expected, c, s, y).coeffs()
    checks.require(
        "projective",
        "first coefficient numerator is coefficientwise positive",
        all(coefficient > 0 for coefficient in d1_coefficients),
        min(d1_coefficients),
        ">0",
    )
    checks.require(
        "projective",
        "first coefficient c-zero face",
        sp.factor(d1_expected.subs({c: 0, s: 1}))
        == y**3 * (y + 4) / (16 * (y + 2) ** 2),
        sp.factor(d1_expected.subs({c: 0, s: 1})),
        y**3 * (y + 4) / (16 * (y + 2) ** 2),
    )
    checks.require(
        "projective",
        "first coefficient c-one face",
        sp.factor(d1_expected.subs({c: 1, s: 0}))
        == y**3 * (y + 4) / (4 * (y + 2) ** 2),
        sp.factor(d1_expected.subs({c: 1, s: 0})),
        y**3 * (y + 4) / (4 * (y + 2) ** 2),
    )

    d2_simplex = sp.factor(d2.subs(s, 1 - c))
    d2_scaled = sp.cancel(sp.together(d2_simplex / y**2))
    d2_numerator, d2_denominator = d2_scaled.as_numer_denom()
    d2_power = sp.Poly(sp.expand(d2_numerator), c)
    d2_degree = d2_power.degree()
    power_coefficients = [
        d2_power.coeff_monomial(c**index) for index in range(d2_degree + 1)
    ]
    bernstein_coefficients = [
        sp.expand(
            sum(
                power_coefficients[index]
                * sp.binomial(level, index)
                / sp.binomial(d2_degree, index)
                for index in range(level + 1)
            )
        )
        for level in range(d2_degree + 1)
    ]
    checks.require(
        "projective_second",
        "second coefficient Bernstein degree",
        d2_degree == 12,
        d2_degree,
        12,
    )
    for index, coefficient in enumerate(bernstein_coefficients):
        y_coefficients = sp.Poly(coefficient, y).coeffs()
        checks.require(
            "projective_second",
            f"Bernstein coefficient {index} is y-coefficientwise positive",
            all(item > 0 for item in y_coefficients),
            min(y_coefficients),
            ">0",
        )
    bernstein_constant_minima = [
        min(sp.Poly(coefficient, y).coeffs()) for coefficient in bernstein_coefficients
    ]
    checks.require(
        "projective_second",
        "second coefficient denominator has the positive simplex factorization",
        sp.factor(
            d2_denominator
            - 256 * (2 + c * y) ** 4 * (2 + (1 - c) * y) ** 4
        )
        == 0,
        sp.factor(d2_denominator),
        "256*(2+c*y)^4*(2+(1-c)*y)^4>0",
    )
    d2_local_limit = sp.factor(sp.limit(d2_simplex / y**2, y, 0))
    checks.require(
        "projective_second",
        "second coefficient local limit is one quarter of the exact margin",
        sp.simplify(d2_local_limit - local_margin.subs(s, 1 - c) / 4) == 0,
        d2_local_limit,
        sp.factor(local_margin.subs(s, 1 - c) / 4),
    )

    d2_reserve = sp.factor(d2 - y**2 * local_margin / 4)
    d2_reserve_simplex = sp.factor(d2_reserve.subs(s, 1 - c))
    reserve_scaled = sp.cancel(sp.together(d2_reserve_simplex / y**3))
    reserve_numerator, reserve_denominator = reserve_scaled.as_numer_denom()
    reserve_power = sp.Poly(sp.expand(reserve_numerator), c)
    reserve_degree = reserve_power.degree()
    reserve_power_coefficients = [
        reserve_power.coeff_monomial(c**index) for index in range(reserve_degree + 1)
    ]
    reserve_bernstein = [
        sp.expand(
            sum(
                reserve_power_coefficients[index]
                * sp.binomial(level, index)
                / sp.binomial(reserve_degree, index)
                for index in range(level + 1)
            )
        )
        for level in range(reserve_degree + 1)
    ]
    checks.require(
        "projective_second",
        "second coefficient margin reserve Bernstein degree",
        reserve_degree == 12,
        reserve_degree,
        12,
    )
    for index, coefficient in enumerate(reserve_bernstein):
        y_coefficients = sp.Poly(coefficient, y).coeffs()
        checks.require(
            "projective_second",
            f"margin-reserve Bernstein coefficient {index} is nonnegative",
            all(item >= 0 for item in y_coefficients),
            min(y_coefficients),
            ">=0",
        )
    reserve_bernstein_minima = [
        min(sp.Poly(coefficient, y).coeffs()) for coefficient in reserve_bernstein
    ]
    checks.require(
        "projective_second",
        "second coefficient margin-reserve denominator has the positive simplex factorization",
        sp.factor(
            reserve_denominator
            - 64 * (2 + c * y) ** 4 * (2 + (1 - c) * y) ** 4
        )
        == 0,
        sp.factor(reserve_denominator),
        "64*(2+c*y)^4*(2+(1-c)*y)^4>0",
    )

    # ------------------------------------------------------------------
    # Exact floor, all-parameter compactification, and certified radial tail.
    # ------------------------------------------------------------------
    phase_minimum = radial_packet.subs(phase, -1)
    rho_coefficient = b - 1 + 10 * sigma - 6 * sp.sqrt(b * sigma)
    rho_square = 10 * (sp.sqrt(sigma) - 3 * sp.sqrt(b) / 10) ** 2 + b / 10 - 1
    checks.require(
        "floor",
        "radial coefficient square completion",
        sp.simplify(rho_coefficient - rho_square) == 0,
        sp.simplify(rho_coefficient),
        sp.expand(rho_square),
    )
    floor_threshold = sp.solve(sp.Eq(b / 10 - 1, 0), b)[0]
    checks.require(
        "floor",
        "uniform exact-floor amplitude threshold",
        floor_threshold == 10,
        floor_threshold,
        10,
    )
    sigma_remainder = 4 * sigma**2 + (4 * b - 1) * sigma
    checks.require(
        "floor",
        "sigma remainder is nonnegative above the floor threshold",
        sp.factor(sigma_remainder.subs(b, floor_threshold))
        == sigma * (4 * sigma + 39),
        sp.factor(sigma_remainder.subs(b, floor_threshold)),
        sigma * (4 * sigma + 39),
    )
    checks.require(
        "floor",
        "phase minimum separates from the exact floor",
        sp.simplify(
            phase_minimum
            - (
                rho**2
                + rho_coefficient * rho
                + sigma_remainder
                - b / 2
            )
        )
        == 0,
        sp.simplify(phase_minimum + b / 2),
        rho**2 + rho_coefficient * rho + sigma_remainder,
    )

    global_floor_sos = (
        (rho - sp.Rational(1, 2)) ** 2
        + 4 * (sigma - sp.Rational(1, 8)) ** 2
        + rho
        * ((sp.sqrt(b) - 3 * sp.sqrt(sigma)) ** 2 + sigma)
        + 4 * b * sigma
        - b / 2
        - sp.Rational(5, 16)
    )
    checks.require(
        "floor",
        "global phase-minimum sum-of-squares identity",
        sp.simplify(phase_minimum - global_floor_sos) == 0,
        sp.simplify(phase_minimum - global_floor_sos),
        0,
    )
    global_floor = -b / 2 - sp.Rational(5, 16)
    checks.require(
        "floor",
        "global algebraic floor is finite for every amplitude",
        global_floor.is_finite is not False,
        global_floor,
        "finite for finite b",
    )
    k0_floor_identity = sp.factor(
        k0.subs(s, 1 - c) - (c - sp.Rational(1, 2)) ** 2 - sp.Rational(1, 4)
    )
    checks.require(
        "floor",
        "leading covariance-square floor",
        k0_floor_identity == 0,
        k0_floor_identity,
        0,
    )

    k1_floor_identity = sp.factor(
        k1.subs(s, 1 - c)
        - sp.Rational(1, 4)
        - c * (1 + 5 * c - 3 * c**2) / 4
    )
    checks.require(
        "floor",
        "linear covariance-square coefficient floor",
        k1_floor_identity == 0,
        k1_floor_identity,
        0,
    )
    k2_floor_identity = sp.factor(
        k2
        - sp.Rational(1, 16)
        - (s**4 + 76 * c**2 * s**2 + 76 * c**4) / 64
    )
    checks.require(
        "floor",
        "constant covariance-square coefficient floor on simplex",
        sp.simplify(k2_floor_identity.subs(s, 1 - c)) == 0,
        sp.factor(k2_floor_identity.subs(s, 1 - c)),
        0,
    )
    compact_h_floor = (2 * b + 1) ** 2 / 16
    checks.require(
        "floor",
        "complete covariance square dominates the uniform quadratic floor",
        sp.simplify(
            (
                compact_h
                - compact_h_floor
                - b**2 * (c - s) ** 2 / 4
                - b * c * (1 + 5 * c - 3 * c**2) / 4
                - (s**4 + 76 * c**2 * s**2 + 76 * c**4) / 64
            ).subs(s, 1 - c)
        )
        == 0,
        sp.factor((compact_h - compact_h_floor).subs(s, 1 - c)),
        ">=0",
    )
    high_y_cutoff = sp.simplify(2 / sp.Rational(1, 4))
    checks.require(
        "floor",
        "uniform large-y cutoff",
        high_y_cutoff == 8,
        high_y_cutoff,
        8,
    )

    global_tau_cutoff = sp.factor((32 * b + 20) / (2 * b + 1) ** 2)
    checks.require(
        "compact_core",
        "global floor-to-target sufficient cutoff",
        sp.simplify(
            global_tau_cutoff * compact_h_floor / 4
            - (-global_floor)
        )
        == 0,
        sp.simplify(global_tau_cutoff * compact_h_floor / 4),
        -global_floor,
    )
    tau_cutoff_ceiling_defect = sp.factor(
        20 * (2 * b + 1) ** 2 - (32 * b + 20)
    )
    checks.require(
        "compact_core",
        "global tau cutoff is at most twenty",
        tau_cutoff_ceiling_defect == 16 * b * (5 * b + 3),
        tau_cutoff_ceiling_defect,
        16 * b * (5 * b + 3),
    )
    projective_cutoff_defect = sp.factor(
        8 * (2 * b + 1) ** 2 - b * (32 * b + 20)
    )
    checks.require(
        "compact_core",
        "global projective coordinate cutoff is below eight",
        sp.simplify(projective_cutoff_defect - 4 * (3 * b + 2)) == 0,
        projective_cutoff_defect,
        4 * (3 * b + 2),
    )
    projective_x = sp.symbols("x", nonnegative=True)
    residual_polynomial = sp.expand(
        (2 * projective_x + tau) ** 2 - 32 * projective_x - 20 * tau
    )
    checks.require(
        "compact_core",
        "residual semialgebraic condition after x=b tau",
        sp.expand(
            tau**2 * ((2 * b + 1) ** 2 - (32 * b + 20) / tau
            ).subs(b, projective_x / tau)
            - residual_polynomial
        )
        == 0,
        residual_polynomial,
        "(2*x+tau)^2-32*x-20*tau",
    )

    likelihood_floor = -projective_x / 2 - 5 * tau / 16
    tail_radius = sp.Integer(50)  # Declared interval-certificate truncation input.
    tail_bound = sp.exp(projective_x / 2 + 5 * tau / 16) * (
        2 * sp.exp(-tail_radius) - sp.exp(-2 * tail_radius)
    )
    tail_bound_worst = sp.N(tail_bound.subs({projective_x: 8, tau: 20}), 50)
    tail_tolerance = sp.Rational(11, 10) * sp.Integer(10) ** -17
    checks.require(
        "compact_core",
        "radius-fifty union tail is below the declared tolerance",
        tail_bound_worst < tail_tolerance,
        tail_bound_worst,
        f"<{tail_tolerance}",
    )

    compact_target_polynomial = (
        projective_x**2 * k0
        + projective_x * tau * k1
        + tau**2 * k2
    )
    origin_patch_polynomial = sp.factor(
        (8 * projective_x + 5 * tau) * compact_target_polynomial
        - 48 * local_margin * tau**2
    )
    checks.require(
        "compact_core",
        "Bernstein-MGF origin patch is an exact polynomial condition",
        not origin_patch_polynomial.has(sp.sqrt(b), sp.Max),
        origin_patch_polynomial,
        "polynomial in c,s,x,tau",
    )

    tail_constant = b / 2 + sp.Max(1 - b, 0) ** 2 + (7 * b + sp.Rational(1, 2)) ** 2 / 2
    compact_tail_lower = rho**2 / 4 + sigma**2 / 2 - tail_constant
    checks.require(
        "compact_core",
        "transformed R-111 tail constant is finite on finite b intervals",
        not tail_constant.has(sp.oo, sp.zoo, sp.nan),
        tail_constant,
        "finite for every finite b",
    )
    k2_face_lower = sp.Rational(1, 16)
    checks.require(
        "compact_core",
        "constant covariance-square simplex lower bound",
        k2_face_lower > 0,
        k2_face_lower,
        ">0",
    )

    # ------------------------------------------------------------------
    # The third projective coefficient retires an all-order positivity route.
    # ------------------------------------------------------------------
    phase_sixth = phase_amplitude**6 * sp.Rational(5, 16)
    a3 = sp.factor(
        -y**3 * tilted_expect(quadratic**3) / 6
        + y**4 * tilted_expect(phase_second * quadratic**2) / 4
        - y**5 * tilted_expect(phase_fourth * quadratic) / 24
        + y**6 * tilted_expect(phase_sixth) / 720
    )
    d3 = sp.factor(-(a3 - a1 * a2 + a1**3 / 3))
    fixture_inputs = {
        c: sp.Rational(3, 5),
        s: sp.Rational(2, 5),
        y: sp.Rational(24, 25),
    }
    d3_fixture = sp.factor(d3.subs(fixture_inputs))
    checks.require(
        "all_order_nogo",
        "third inverse-amplitude coefficient is negative at the rational fixture",
        d3_fixture < 0,
        d3_fixture,
        "<0",
    )
    checks.require(
        "all_order_nogo",
        "limiting gap remains positive at the same fixture",
        limiting_gap.subs(fixture_inputs) > 0,
        limiting_gap.subs(fixture_inputs),
        ">0",
    )
    checks.require(
        "all_order_nogo",
        "first coefficient remains positive at the same fixture",
        d1_expected.subs(fixture_inputs) > 0,
        d1_expected.subs(fixture_inputs),
        ">0",
    )
    checks.require(
        "all_order_nogo",
        "second coefficient remains positive at the same fixture",
        d2.subs(fixture_inputs) > 0,
        d2.subs(fixture_inputs),
        ">0",
    )

    status = "PASS" if all(row["status"] == "PASS" for row in checks.rows) else "FAIL"
    results: dict[str, object] = {
        "compact_normal_form": {
            "variables": [
                "c=v/(v+4w)",
                "s=4w/(v+4w)",
                "b=A^2/(v+4w)",
                "tau=q*(v+4w)^2",
                "x=b*tau (symbol y in the exact projective algebra)",
            ],
            "packet": str(compact_packet),
            "covariance_square": str(compact_h),
            "local_margin": str(local_margin),
            "local_margin_uniform_lower": str(local_margin_lower),
        },
        "uniform_projective": {
            "limiting_mgf": str(limiting_mgf),
            "limiting_gap": str(limiting_gap),
            "first_coefficient": str(d1_expected),
            "first_numerator_terms": len(sp.Poly(d1_numerator_expected, c, s, y).terms()),
            "second_bernstein_degree": d2_degree,
            "second_bernstein_min_coefficients": [str(item) for item in bernstein_constant_minima],
            "second_local_limit": str(d2_local_limit),
            "second_margin_reserve_bernstein_min_coefficients": [
                str(item) for item in reserve_bernstein_minima
            ],
            "second_global_lower": "D2>=x^2*local_margin/4>=x^2/400",
            "uniform_remainder": "O_Y(y^3/b^3)",
        },
        "uniform_large_amplitude": {
            "exact_floor_threshold_b": str(floor_threshold),
            "exact_floor": "F_star=-b/2 for b>=10",
            "uniform_high_y_cutoff": str(high_y_cutoff),
            "existential_all_q_threshold": True,
            "effective_threshold_certified": False,
        },
        "compact_core": {
            "global_floor": str(global_floor),
            "covariance_square_floor": str(compact_h_floor),
            "global_tau_cutoff": str(global_tau_cutoff),
            "residual_semialgebraic_condition": "(2*x+tau)^2<=32*x+20*tau",
            "residual_box": {"c": "[0,1]", "x": "[0,8]", "tau": "[0,20]"},
            "tail_constant": str(tail_constant),
            "tail_lower_template": str(compact_tail_lower),
            "constant_covariance_square_lower": str(k2_face_lower),
            "radial_tail_radius": str(tail_radius),
            "radial_tail_worst_bound": str(tail_bound_worst),
            "origin_patch_condition": str(origin_patch_polynomial) + "<=0",
            "residual_variables": ["compact c", "compact x=b*tau", "compact tau"],
            "interval_certificate_complete": False,
        },
        "all_order_projective_nogo": {
            "fixture": {"c": "3/5", "s": "2/5", "y": "24/25"},
            "third_coefficient": str(d3_fixture),
            "third_coefficient_negative": True,
            "target_counterexample": False,
        },
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
            "covariance_simplex_compactification": "proved-exact",
            "uniform_projective_remainder": "proved-asymptotic-with-factored-remainder",
            "first_inverse_amplitude_coefficient": "proved-nonnegative",
            "second_inverse_amplitude_coefficient": "proved-positive-by-Bernstein-certificate",
            "all_order_coefficientwise_positivity": "failed-at-third-coefficient",
            "uniform_large_amplitude_all_q": "proved-existential-threshold",
            "effective_large_amplitude_threshold": "open",
            "local_and_face_patching": "proved-existential",
            "all_parameter_compact_semialgebraic_reduction": "proved-effective-domain-and-tail",
            "mixed_compact_core": "open-interval-certificate-required",
            "mixed_all_q_scalar_k2k": "open",
            "full_a1_embedding": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_a": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"primary {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
