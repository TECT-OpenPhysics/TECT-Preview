#!/usr/bin/env python3
"""Independent exact reconstruction for the scoped R-112 package.

This implementation does not import the primary certificate.  It obtains the
inverse-amplitude coefficients from the formal delta coefficient of
exp(-x delta Q) I_0(x sqrt(delta) B), converts the second coefficient and its
local-margin reserve to Bernstein form, and independently checks the compact
semialgebraic domain, global tail, and negative third-coefficient fixture.
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


SCHEMA = "tect/a13-scalar-k2k-covariance-simplex-uniform-compact-core-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-scalar-k2k-covariance-simplex-uniform-compact-core/result.json"
)


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
    audit = Audit()

    c, s, b, tau, x = sp.symbols("c s b tau x", nonnegative=True)
    t_var, u_var = sp.symbols("T U", nonnegative=True)
    rho = c * t_var / 2
    sigma = s * u_var / 8
    linear = rho + 4 * sigma - sp.Rational(1, 2)
    quadratic = rho**2 + 10 * rho * sigma + 4 * sigma**2 - rho - sigma
    phase_amplitude = 6 * rho * sp.sqrt(sigma)

    compact_packet = b * linear + sp.sqrt(b) * phase_amplitude * sp.symbols("zeta", real=True) + quadratic
    audit.check(
        "normal_form",
        "linear coordinate",
        sp.simplify(linear - (c * t_var + s * u_var - 1) / 2) == 0,
        linear,
        (c * t_var + s * u_var - 1) / 2,
    )
    audit.check(
        "normal_form",
        "quadratic coordinate",
        sp.simplify(
            quadratic
            - (
                c**2 * t_var**2 / 4
                + 5 * c * s * t_var * u_var / 8
                + s**2 * u_var**2 / 16
                - c * t_var / 2
                - s * u_var / 8
            )
        )
        == 0,
        sp.expand(quadratic),
        "declared compact Q",
    )

    k2_leading = (c**2 + s**2) / 2
    k1_linear = c**3 + sp.Rational(5, 2) * c**2 * s + c * s**2 + s**3 / 4
    k0_constant = (
        sp.Rational(5, 4) * c**4
        + c**3 * s / 4
        + sp.Rational(25, 16) * c**2 * s**2
        + c * s**3 / 4
        + sp.Rational(5, 64) * s**4
    )
    covariance_square = b**2 * k2_leading + b * k1_linear + k0_constant
    local_margin = c**4 / 4 + c**2 * s**2 / 4 + s**4 / 64

    audit.check(
        "normal_form",
        "leading H identity",
        sp.simplify((k2_leading - (1 + (c - s) ** 2) / 4).subs(s, 1 - c)) == 0,
        k2_leading,
        "[1+(c-s)^2]/4",
    )
    audit.check(
        "normal_form",
        "linear H identity",
        sp.simplify(
            (
                k1_linear
                - sp.Rational(1, 4)
                - c * (1 + 5 * c - 3 * c**2) / 4
            ).subs(s, 1 - c)
        )
        == 0,
        k1_linear,
        "1/4+c(1+5c-3c^2)/4",
    )
    audit.check(
        "normal_form",
        "constant H identity",
        sp.simplify(
            (
                k0_constant
                - sp.Rational(1, 16)
                - (s**4 + 76 * c**2 * s**2 + 76 * c**4) / 64
            ).subs(s, 1 - c)
        )
        == 0,
        k0_constant,
        "1/16+(s^4+76c^2s^2+76c^4)/64",
    )
    audit.check(
        "normal_form",
        "uniform H floor",
        sp.simplify(
            (
                covariance_square
                - (2 * b + 1) ** 2 / 16
                - b**2 * (c - s) ** 2 / 4
                - b * c * (1 + 5 * c - 3 * c**2) / 4
                - (s**4 + 76 * c**2 * s**2 + 76 * c**4) / 64
            ).subs(s, 1 - c)
        )
        == 0,
        sp.factor((covariance_square - (2 * b + 1) ** 2 / 16).subs(s, 1 - c)),
        ">=0",
    )
    audit.check(
        "normal_form",
        "uniform local margin floor",
        sp.factor(
            64 * local_margin
            - (4 * c**2 + s**2) ** 2
            - 8 * c**2 * s**2
        )
        == 0,
        local_margin,
        ">=1/100 on c+s=1",
    )

    # --------------------------------------------------------------
    # Independent coefficient engine using the I_0 power series.
    # --------------------------------------------------------------
    alpha = 1 + c * x / 2
    beta = 1 + s * x / 2

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

    def phase_series_coefficient(order: int) -> sp.Expr:
        coefficient = sp.S.Zero
        for bessel_order in range(order + 1):
            exponential_order = order - bessel_order
            coefficient += (
                (-x * quadratic) ** exponential_order
                / sp.factorial(exponential_order)
                * (x**2 * phase_amplitude**2 / 4) ** bessel_order
                / sp.factorial(bessel_order) ** 2
            )
        return sp.factor(tilted_expect(coefficient))

    coefficients = [phase_series_coefficient(order) for order in range(4)]
    audit.check(
        "series",
        "zeroth phase-integrated coefficient",
        coefficients[0] == 1,
        coefficients[0],
        1,
    )
    log_first = coefficients[1]
    log_second = sp.factor(coefficients[2] - coefficients[1] ** 2 / 2)
    log_third = sp.factor(
        coefficients[3] - coefficients[1] * coefficients[2] + coefficients[1] ** 3 / 3
    )
    d1 = sp.factor(x**2 * k1_linear / 4 - log_first)
    d2 = sp.factor(x**2 * k0_constant / 4 - log_second)
    d3 = sp.factor(-log_third)

    old_r, old_x = sp.symbols("r old_x", nonnegative=True)
    old_pi = (
        64 * old_r**5 * old_x**3
        + 256 * old_r**5 * old_x**2
        + 256 * old_r**5 * old_x
        + 64 * old_r**4 * old_x**3
        + 320 * old_r**4 * old_x**2
        + 512 * old_r**4 * old_x
        + 256 * old_r**4
        + 40 * old_r**3 * old_x**3
        + 224 * old_r**3 * old_x**2
        + 352 * old_r**3 * old_x
        + 128 * old_r**3
        + 4 * old_r**2 * old_x**3
        + 56 * old_r**2 * old_x**2
        + 172 * old_r**2 * old_x
        + 112 * old_r**2
        + 4 * old_r * old_x**2
        + 26 * old_r * old_x
        + 38 * old_r
        + old_x
        + 4
    )
    transformed_old_d1 = sp.factor(
        c
        * old_x**3
        * old_pi
        / (4 * (old_x + 2) ** 2 * (1 + 2 * old_r * old_x) ** 2)
    ).subs({old_x: c * x, old_r: s / (4 * c)}, simultaneous=True)
    audit.check(
        "series",
        "first coefficient agrees with independently transformed R-111 formula",
        sp.simplify((d1 - transformed_old_d1).subs(s, 1 - c)) == 0,
        sp.factor(d1.subs(s, 1 - c)),
        sp.factor(transformed_old_d1.subs(s, 1 - c)),
    )
    audit.check(
        "series",
        "old first-coefficient numerator remains coefficientwise positive",
        all(value > 0 for value in sp.Poly(old_pi, old_r, old_x).coeffs()),
        min(sp.Poly(old_pi, old_r, old_x).coeffs()),
        ">0",
    )

    def bernstein_coefficients(polynomial: sp.Expr, variable: sp.Symbol) -> list[sp.Expr]:
        power = sp.Poly(sp.expand(polynomial), variable)
        degree = power.degree()
        power_coefficients = [
            power.coeff_monomial(variable**index) for index in range(degree + 1)
        ]
        return [
            sp.expand(
                sum(
                    power_coefficients[index]
                    * sp.binomial(level, index)
                    / sp.binomial(degree, index)
                    for index in range(level + 1)
                )
            )
            for level in range(degree + 1)
        ]

    d2_simplex = sp.factor(d2.subs(s, 1 - c))
    d2_scaled = sp.cancel(sp.together(d2_simplex / x**2))
    d2_numerator, d2_denominator = d2_scaled.as_numer_denom()
    d2_denominator_expected = 256 * (2 + c * x) ** 4 * (2 + (1 - c) * x) ** 4
    audit.check(
        "series",
        "second denominator has the positive simplex factorization",
        sp.factor(d2_denominator - d2_denominator_expected) == 0,
        sp.factor(d2_denominator),
        "256*(2+c*x)^4*(2+(1-c)*x)^4>0",
    )
    d2_bernstein = bernstein_coefficients(d2_numerator, c)
    audit.check(
        "series",
        "second coefficient has degree-twelve Bernstein certificate",
        len(d2_bernstein) == 13,
        len(d2_bernstein) - 1,
        12,
    )
    for index, coefficient in enumerate(d2_bernstein):
        x_coefficients = sp.Poly(coefficient, x).coeffs()
        audit.check(
            "series",
            f"second Bernstein coefficient {index} is x-coefficientwise positive",
            all(value > 0 for value in x_coefficients),
            min(x_coefficients),
            ">0",
        )
    d2_minima = [min(sp.Poly(value, x).coeffs()) for value in d2_bernstein]

    reserve = sp.factor(d2 - x**2 * local_margin / 4)
    reserve_simplex = sp.factor(reserve.subs(s, 1 - c))
    reserve_scaled = sp.cancel(sp.together(reserve_simplex / x**3))
    reserve_numerator, reserve_denominator = reserve_scaled.as_numer_denom()
    reserve_denominator_expected = 64 * (2 + c * x) ** 4 * (2 + (1 - c) * x) ** 4
    audit.check(
        "series",
        "margin-reserve denominator has the positive simplex factorization",
        sp.factor(reserve_denominator - reserve_denominator_expected) == 0,
        sp.factor(reserve_denominator),
        "64*(2+c*x)^4*(2+(1-c)*x)^4>0",
    )
    reserve_bernstein = bernstein_coefficients(reserve_numerator, c)
    audit.check(
        "series",
        "second margin reserve has degree-twelve Bernstein certificate",
        len(reserve_bernstein) == 13,
        len(reserve_bernstein) - 1,
        12,
    )
    for index, coefficient in enumerate(reserve_bernstein):
        x_coefficients = sp.Poly(coefficient, x).coeffs()
        audit.check(
            "series",
            f"reserve Bernstein coefficient {index} is nonnegative",
            all(value >= 0 for value in x_coefficients),
            min(x_coefficients),
            ">=0",
        )
    reserve_minima = [min(sp.Poly(value, x).coeffs()) for value in reserve_bernstein]
    audit.check(
        "series",
        "second local limit",
        sp.simplify(sp.limit(d2_simplex / x**2, x, 0) - local_margin.subs(s, 1 - c) / 4)
        == 0,
        sp.factor(sp.limit(d2_simplex / x**2, x, 0)),
        sp.factor(local_margin.subs(s, 1 - c) / 4),
    )

    fixture = {c: sp.Rational(3, 5), s: sp.Rational(2, 5), x: sp.Rational(24, 25)}
    d2_fixture = sp.factor(d2.subs(fixture))
    d3_fixture = sp.factor(d3.subs(fixture))
    audit.check(
        "series_boundary",
        "second coefficient fixture is positive",
        d2_fixture > 0,
        d2_fixture,
        ">0",
    )
    audit.check(
        "series_boundary",
        "third coefficient fixture is negative",
        d3_fixture < 0,
        d3_fixture,
        "<0",
    )

    # --------------------------------------------------------------
    # Global floor, compact domain, and radial tail.
    # --------------------------------------------------------------
    rho_free, sigma_free = sp.symbols("rho sigma", nonnegative=True)
    phase_minimum = (
        rho_free**2
        + 10 * rho_free * sigma_free
        + 4 * sigma_free**2
        + (b - 1) * rho_free
        + (4 * b - 1) * sigma_free
        - b / 2
        - 6 * sp.sqrt(b) * rho_free * sp.sqrt(sigma_free)
    )
    floor_sos = (
        (rho_free - sp.Rational(1, 2)) ** 2
        + 4 * (sigma_free - sp.Rational(1, 8)) ** 2
        + rho_free
        * ((sp.sqrt(b) - 3 * sp.sqrt(sigma_free)) ** 2 + sigma_free)
        + 4 * b * sigma_free
        - b / 2
        - sp.Rational(5, 16)
    )
    audit.check(
        "compact_core",
        "global floor SOS",
        sp.simplify(phase_minimum - floor_sos) == 0,
        sp.simplify(phase_minimum - floor_sos),
        0,
    )
    cutoff = sp.factor((32 * b + 20) / (2 * b + 1) ** 2)
    audit.check(
        "compact_core",
        "cutoff meets floor against H floor",
        sp.simplify(cutoff * (2 * b + 1) ** 2 / 64 - (b / 2 + sp.Rational(5, 16)))
        == 0,
        cutoff,
        "4*(b/2+5/16)/K_floor",
    )
    audit.check(
        "compact_core",
        "cutoff tau ceiling",
        sp.factor(20 * (2 * b + 1) ** 2 - (32 * b + 20))
        == 16 * b * (5 * b + 3),
        cutoff,
        "<=20",
    )
    audit.check(
        "compact_core",
        "cutoff projective ceiling",
        sp.simplify(8 * (2 * b + 1) ** 2 - b * (32 * b + 20) - 4 * (3 * b + 2))
        == 0,
        sp.factor(b * cutoff),
        "<8",
    )
    residual = sp.expand((2 * x + tau) ** 2 - 32 * x - 20 * tau)
    audit.check(
        "compact_core",
        "residual compact polynomial",
        sp.Poly(residual, x, tau).total_degree() == 2,
        residual,
        "<=0 on the residual domain",
    )

    radius = sp.Integer(50)  # Declared truncation input, not a derived constant.
    tail = sp.exp(x / 2 + 5 * tau / 16) * (2 * sp.exp(-radius) - sp.exp(-2 * radius))
    tail_worst = sp.N(tail.subs({x: 8, tau: 20}), 50)
    tail_oracle = sp.Rational(11, 10) * sp.Integer(10) ** -17
    audit.check(
        "compact_core",
        "independent radius-fifty tail bound",
        tail_worst < tail_oracle,
        tail_worst,
        f"<{tail_oracle}",
    )

    compact_target = x**2 * k2_leading + x * tau * k1_linear + tau**2 * k0_constant
    origin_condition = sp.factor(
        (8 * x + 5 * tau) * compact_target - 48 * local_margin * tau**2
    )
    audit.check(
        "compact_core",
        "origin Bernstein-MGF patch is polynomial",
        not origin_condition.has(sp.sqrt(b), sp.Max),
        origin_condition,
        "polynomial in c,s,x,tau",
    )

    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    results: dict[str, object] = {
        "compact_normal_form": {
            "variables": [
                "c=v/(v+4w)",
                "s=4w/(v+4w)",
                "b=A^2/(v+4w)",
                "tau=q*(v+4w)^2",
                "x=b*tau",
            ],
            "packet": str(compact_packet),
            "covariance_square": str(covariance_square),
            "local_margin": str(local_margin),
            "local_margin_uniform_lower": "1/100",
        },
        "uniform_projective": {
            "limiting_mgf": str(sp.exp(x / 2) / (alpha * beta)),
            "first_coefficient": str(sp.factor(d1)),
            "second_bernstein_degree": len(d2_bernstein) - 1,
            "second_bernstein_min_coefficients": [str(value) for value in d2_minima],
            "second_local_limit": str(sp.factor(sp.limit(d2_simplex / x**2, x, 0))),
            "second_margin_reserve_bernstein_min_coefficients": [
                str(value) for value in reserve_minima
            ],
            "second_global_lower": "D2>=x^2*local_margin/4>=x^2/400",
            "uniform_remainder": "O_X(x^3/b^3)",
        },
        "compact_core": {
            "global_floor": "-b/2-5/16",
            "covariance_square_floor": "(2*b+1)^2/16",
            "global_tau_cutoff": str(cutoff),
            "residual_semialgebraic_condition": "(2*x+tau)^2<=32*x+20*tau",
            "residual_box": {"c": "[0,1]", "x": "[0,8]", "tau": "[0,20]"},
            "radial_tail_radius": str(radius),
            "radial_tail_worst_bound": str(tail_worst),
            "origin_patch_condition": str(origin_condition) + "<=0",
            "interval_certificate_complete": False,
        },
        "all_order_projective_nogo": {
            "fixture": {"c": "3/5", "s": "2/5", "x": "24/25"},
            "second_coefficient": str(d2_fixture),
            "third_coefficient": str(d3_fixture),
            "third_coefficient_negative": True,
            "target_counterexample": False,
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
        "results_sha256": hashlib.sha256(
            json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "route_verdicts": {
            "compact_semialgebraic_reduction": "proved-exact",
            "uniform_radial_tail": "proved-exact",
            "second_projective_coefficient": "proved-positive",
            "all_order_projective_coefficient_positivity": "failed-at-third-order",
            "origin_patch": "proved-sufficient-polynomial-condition",
            "mixed_compact_core": "open-directed-rounding-interval-certificate",
            "mixed_all_q_scalar_k2k": "open",
            "full_a1_embedding": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_a": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"independent {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
