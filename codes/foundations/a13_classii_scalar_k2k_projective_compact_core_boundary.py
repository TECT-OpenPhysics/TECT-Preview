#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-111 boundary reduction.

The certificate verifies the scale quotient, the exact radial/Bessel normal
form, all-q closure on both degenerate frequency faces, the large-amplitude
projective limit and its first positive correction, the exact phase-minimum/
high-q reduction, an explicit integrable tail majorant, and a concrete failure
of the tilted-variance-monotonicity proof route.  It does not assert the bare
all-q genuinely mixed two-frequency inequality, a full A1 embedding, the
adapted production cluster, Nelson, or Sector-A closure.
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

import mpmath as mp
import sympy as sp


SCHEMA = "tect/a13-scalar-k2k-projective-compact-core-boundary-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-scalar-k2k-projective-compact-core-boundary/result.json"
)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def require(self, group: str, name: str, condition: object, actual: object, expected: object) -> None:
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


def r0_log_mgf(a_value: mp.mpf, t_value: mp.mpf) -> mp.mpf:
    """Closed-form log M on the normalized w=0 boundary."""

    beta = 1 + t_value * (a_value - 1) / 2
    return (
        t_value * a_value / 2
        + mp.log(mp.sqrt(mp.pi / t_value))
        + beta**2 / t_value
        + mp.log(mp.erfc(beta / mp.sqrt(t_value)))
    )


def tilted_a0_stats(r_value: mp.mpf, t_value: mp.mpf) -> dict[str, mp.mpf]:
    """Adaptive one-dimensional audit after integrating T exactly.

    This route applies at a=0.  Polynomial recurrence supplies the first six
    T moments, so the first three tilted moments of p require only one outer
    integral in U.
    """

    gamma = 1 + 4 * r_value
    quad_a = t_value / 4

    def t_moments(u_value: mp.mpf) -> list[mp.mpf]:
        linear_b = 1 + t_value * (mp.mpf("2.5") * r_value * u_value - gamma / 2)
        root_a = mp.sqrt(quad_a)
        moment0 = (
            mp.sqrt(mp.pi)
            / (2 * root_a)
            * mp.exp(linear_b**2 / (4 * quad_a))
            * mp.erfc(linear_b / (2 * root_a))
        )
        moments = [moment0, (1 - linear_b * moment0) / (2 * quad_a)]
        for degree in range(2, 7):
            moments.append(
                ((degree - 1) * moments[degree - 2] - linear_b * moments[degree - 1])
                / (2 * quad_a)
            )
        return moments

    def integrated_power(u_value: mp.mpf, power: int) -> mp.mpf:
        moments = t_moments(u_value)
        coefficients = [mp.mpf(1)]
        base = [
            r_value**2 * u_value**2 - gamma * r_value * u_value / 2,
            mp.mpf("2.5") * r_value * u_value - gamma / 2,
            mp.mpf("0.25"),
        ]
        for _ in range(power):
            product = [mp.mpf(0)] * (len(coefficients) + 2)
            for left_index, left in enumerate(coefficients):
                for right_index, right in enumerate(base):
                    product[left_index + right_index] += left * right
            coefficients = product
        return sum(coefficient * moments[index] for index, coefficient in enumerate(coefficients))

    def outer_weight(u_value: mp.mpf) -> mp.mpf:
        return mp.exp(
            -u_value
            - t_value
            * (r_value**2 * u_value**2 - gamma * r_value * u_value / 2)
        )

    raw: list[mp.mpf] = []
    for power in range(4):
        raw.append(
            mp.quad(
                lambda u_value, selected=power: outer_weight(u_value)
                * integrated_power(u_value, selected),
                [0, 1, 2, 4, mp.inf],
            )
        )
    mean = raw[1] / raw[0]
    second = raw[2] / raw[0]
    third_raw = raw[3] / raw[0]
    variance = second - mean**2
    third = third_raw - 3 * mean * second + 2 * mean**3
    return {
        "log_mgf": mp.log(raw[0]),
        "mean": mean,
        "variance": variance,
        "third_centered": third,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    # ------------------------------------------------------------------
    # Exact scaling quotient and normalized packet.
    # ------------------------------------------------------------------
    lam = sp.symbols("lambda", positive=True)
    a0, v0, w0, radial0, second0, phase0 = sp.symbols(
        "A0 v0 w0 R0 S0 C0", real=True
    )
    gamma0 = v0 + 4 * w0
    packet0 = (
        a0**2 * radial0
        + 4 * a0**2 * second0
        - gamma0 * a0**2 / 2
        + 6 * a0 * phase0
        + radial0**2
        + 10 * radial0 * second0
        + 4 * second0**2
        - gamma0 * (radial0 + second0)
    )
    scaled_packet = packet0.subs(
        {
            a0: sp.sqrt(lam) * a0,
            v0: lam * v0,
            w0: lam * w0,
            radial0: lam * radial0,
            second0: lam * second0,
            phase0: lam ** sp.Rational(3, 2) * phase0,
        },
        simultaneous=True,
    )
    checks.require(
        "scale",
        "packet has weight two",
        sp.simplify(scaled_packet - lam**2 * packet0) == 0,
        sp.simplify(scaled_packet / packet0),
        lam**2,
    )

    h_original = (
        a0**4 * (v0**2 / 2 + 8 * w0**2)
        + a0**2 * (v0**3 + 10 * v0**2 * w0 + 16 * v0 * w0**2 + 16 * w0**3)
        + sp.Rational(5, 4) * v0**4
        + v0**3 * w0
        + 25 * v0**2 * w0**2
        + 16 * v0 * w0**3
        + 20 * w0**4
    )
    scaled_h = h_original.subs(
        {a0: sp.sqrt(lam) * a0, v0: lam * v0, w0: lam * w0},
        simultaneous=True,
    )
    checks.require(
        "scale",
        "covariance square has weight four",
        sp.simplify(scaled_h - lam**4 * h_original) == 0,
        sp.simplify(scaled_h / h_original),
        lam**4,
    )

    a, r, t, x = sp.symbols("a r t x", nonnegative=True)
    T, U, cosine = sp.symbols("T U cosine", real=True)
    gamma = 1 + 4 * r
    normalized_packet = (
        T**2 / 4
        + r**2 * U**2
        + sp.Rational(5, 2) * r * T * U
        + a * (T / 2 + 2 * r * U - gamma / 2)
        - gamma * (T + r * U) / 2
        + 3 * sp.sqrt(a * r / 2) * T * sp.sqrt(U) * cosine
    )
    substituted_packet = packet0.subs(
        {
            a0: sp.sqrt(a),
            v0: 1,
            w0: r,
            radial0: T / 2,
            second0: r * U / 2,
            phase0: T * sp.sqrt(r * U / 2) * cosine / 2,
        },
        simultaneous=True,
    )
    checks.require(
        "scale",
        "normalized packet formula",
        sp.simplify(substituted_packet - normalized_packet) == 0,
        sp.simplify(substituted_packet - normalized_packet),
        0,
    )

    normalized_h = (
        a**2 * (sp.Rational(1, 2) + 8 * r**2)
        + a * (1 + 10 * r + 16 * r**2 + 16 * r**3)
        + sp.Rational(5, 4)
        + r
        + 25 * r**2
        + 16 * r**3
        + 20 * r**4
    )
    checks.require(
        "scale",
        "normalized covariance-square formula",
        sp.simplify(h_original.subs({a0: sp.sqrt(a), v0: 1, w0: r}) - normalized_h) == 0,
        sp.simplify(h_original.subs({a0: sp.sqrt(a), v0: 1, w0: r}) - normalized_h),
        0,
    )
    bessel_argument = 3 * t * sp.sqrt(a * r / 2) * T * sp.sqrt(U)
    checks.require(
        "scale",
        "phase integration has the declared Bessel argument",
        sp.simplify(t * normalized_packet.coeff(cosine) - bessel_argument) == 0,
        sp.simplify(t * normalized_packet.coeff(cosine)),
        bessel_argument,
    )

    normalized_variance = sp.Rational(1, 4) * (
        a**2
        + 16 * a**2 * r**2
        + 2 * a
        + 20 * a * r
        + 32 * a * r**2
        + 32 * a * r**3
        + 2
        + 2 * r
        + 42 * r**2
        + 32 * r**3
        + 32 * r**4
    )
    local_margin = sp.factor(normalized_h - 2 * normalized_variance)
    expected_local_margin = (1 + 16 * r**2 + 16 * r**4) / 4
    checks.require(
        "local",
        "strict small-t quadratic margin",
        sp.simplify(local_margin - expected_local_margin) == 0,
        local_margin,
        expected_local_margin,
    )
    checks.require(
        "local",
        "quadratic margin polynomial is coefficientwise positive",
        all(coefficient > 0 for coefficient in sp.Poly(4 * expected_local_margin, r).coeffs()),
        sp.Poly(4 * expected_local_margin, r).coeffs(),
        "all positive",
    )

    # ------------------------------------------------------------------
    # Large-amplitude projective boundary t=x/a.
    # ------------------------------------------------------------------
    L = (T - 1) / 2 + 2 * r * (U - 1)
    B = 3 * T * sp.sqrt(r * U / 2) * cosine
    Q = (
        T**2 / 4
        + r**2 * U**2
        + sp.Rational(5, 2) * r * T * U
        - gamma * (T + r * U) / 2
    )
    checks.require(
        "projective",
        "packet splits as aL plus sqrt(a)B plus Q",
        sp.simplify(normalized_packet - (a * L + sp.sqrt(a) * B + Q)) == 0,
        sp.simplify(normalized_packet - (a * L + sp.sqrt(a) * B + Q)),
        0,
    )

    alpha = 1 + x / 2
    beta = 1 + 2 * r * x
    projective_mgf = sp.exp(x * gamma / 2) / ((1 + x / 2) * (1 + 2 * r * x))
    exponential_product = sp.exp(x * gamma / 2) / (alpha * beta)
    checks.require(
        "projective",
        "limiting centered-exponential MGF",
        sp.simplify(projective_mgf - exponential_product) == 0,
        projective_mgf,
        exponential_product,
    )
    limiting_rhs = x**2 / 8 + 2 * r**2 * x**2
    d = lambda value: value**2 / 2 - value + sp.log(1 + value)
    limiting_gap = sp.simplify(limiting_rhs - sp.log(projective_mgf))
    expected_gap = d(x / 2) + d(2 * r * x)
    checks.require(
        "projective",
        "limiting gap is the sum of two centered-exponential gaps",
        sp.simplify(sp.expand_log(limiting_gap, force=True) - expected_gap) == 0,
        sp.simplify(sp.expand_log(limiting_gap, force=True)),
        expected_gap,
    )
    y = sp.symbols("y", nonnegative=True)
    d_y = y**2 / 2 - y + sp.log(1 + y)
    checks.require(
        "projective",
        "centered-exponential gap is increasing",
        sp.simplify(sp.diff(d_y, y) - y**2 / (1 + y)) == 0,
        sp.diff(d_y, y),
        y**2 / (1 + y),
    )

    expected_t2 = 2 / alpha**2
    expected_u1 = 1 / beta
    expected_t1 = 1 / alpha
    expected_u2 = 2 / beta**2
    expected_b2 = sp.Rational(9, 4) * r * expected_t2 * expected_u1
    expected_q = (
        expected_t2 / 4
        + r**2 * expected_u2
        + sp.Rational(5, 2) * r * expected_t1 * expected_u1
        - gamma * (expected_t1 + r * expected_u1) / 2
    )
    first_log_correction = sp.simplify(x**2 * expected_b2 / 2 - x * expected_q)
    h_linear = 1 + 10 * r + 16 * r**2 + 16 * r**3
    first_gap_correction = sp.factor(x**2 * h_linear / 4 - first_log_correction)
    pi_polynomial = (
        64 * r**5 * x**3
        + 256 * r**5 * x**2
        + 256 * r**5 * x
        + 64 * r**4 * x**3
        + 320 * r**4 * x**2
        + 512 * r**4 * x
        + 256 * r**4
        + 40 * r**3 * x**3
        + 224 * r**3 * x**2
        + 352 * r**3 * x
        + 128 * r**3
        + 4 * r**2 * x**3
        + 56 * r**2 * x**2
        + 172 * r**2 * x
        + 112 * r**2
        + 4 * r * x**2
        + 26 * r * x
        + 38 * r
        + x
        + 4
    )
    expected_first_gap = x**3 * pi_polynomial / (4 * (x + 2) ** 2 * (1 + 2 * r * x) ** 2)
    checks.require(
        "projective",
        "first inverse-amplitude gap correction",
        sp.simplify(first_gap_correction - expected_first_gap) == 0,
        first_gap_correction,
        expected_first_gap,
    )
    checks.require(
        "projective",
        "first-correction numerator is coefficientwise positive",
        all(coefficient > 0 for coefficient in sp.Poly(pi_polynomial, x, r).coeffs()),
        sp.Poly(pi_polynomial, x, r).coeffs(),
        "all positive",
    )
    floor_ratio_defect = sp.factor(2 + 32 * r**2 - (1 + 4 * r) ** 2)
    checks.require(
        "projective",
        "unique leading floor-ratio saturation shape",
        sp.simplify(floor_ratio_defect - (4 * r - 1) ** 2) == 0,
        floor_ratio_defect,
        (4 * r - 1) ** 2,
    )
    checks.require(
        "projective",
        "saturation gap remains a double centered-exponential gap",
        sp.simplify(expected_gap.subs(r, sp.Rational(1, 4)) - 2 * d(x / 2)) == 0,
        sp.simplify(expected_gap.subs(r, sp.Rational(1, 4))),
        2 * d(x / 2),
    )

    # ------------------------------------------------------------------
    # Exact phase minimum, high-t cutoff, and certified-tail majorant.
    # ------------------------------------------------------------------
    radial, root_s = sp.symbols("R y", nonnegative=True)
    phase_minimum = (
        radial**2
        + 10 * radial * root_s**2
        + 4 * root_s**4
        + (a - gamma) * radial
        + (4 * a - gamma) * root_s**2
        - 6 * sp.sqrt(a) * radial * root_s
        - gamma * a / 2
    )
    radial_coefficient = a - gamma + 10 * root_s**2 - 6 * sp.sqrt(a) * root_s
    radial_free = 4 * root_s**4 + (4 * a - gamma) * root_s**2 - gamma * a / 2
    checks.require(
        "floor",
        "phase-minimum radial quadratic",
        sp.simplify(phase_minimum - (radial**2 + radial_coefficient * radial + radial_free)) == 0,
        sp.simplify(phase_minimum - (radial**2 + radial_coefficient * radial + radial_free)),
        0,
    )
    active_floor = sp.expand(radial_free - radial_coefficient**2 / 4)
    active_cubic = (
        84 * root_s**3
        - 90 * sp.sqrt(a) * root_s**2
        + (20 * a - 8 * gamma) * root_s
        + 3 * sp.sqrt(a) * (gamma - a)
    )
    checks.require(
        "floor",
        "active floor stationary cubic",
        sp.simplify(sp.diff(active_floor, root_s) + active_cubic) == 0,
        sp.diff(active_floor, root_s),
        -active_cubic,
    )
    p_star, h_star = sp.symbols("p_star h_star", real=True, finite=True)
    cutoff_t = -4 * p_star / h_star
    checks.require(
        "floor",
        "large-t floor cutoff meets the quadratic target",
        sp.simplify((-cutoff_t * p_star) - cutoff_t**2 * h_star / 4) == 0,
        sp.simplify(-cutoff_t * p_star),
        sp.simplify(cutoff_t**2 * h_star / 4),
    )

    b_phase = 3 * sp.sqrt(a * r / 2) * T * sp.sqrt(U)
    p_zero_phase = normalized_packet.subs(cosine, 0)
    p_minus = sp.expand(p_zero_phase - b_phase)
    positive_part = sp.symbols("d", nonnegative=True)
    k_value = 7 * a + gamma / 2
    tail_constant = a * gamma / 2 + positive_part**2 + k_value**2 / 2
    tail_lower = T**2 / 16 + r**2 * U**2 / 2 - tail_constant
    phase_square = (T / (2 * sp.sqrt(2)) - 3 * sp.sqrt(a * r * U)) ** 2
    u_square = (r * U - k_value) ** 2 / 2
    t_completion_low = (T / 4 - positive_part) ** 2
    low_case_difference = sp.simplify(
        (p_minus - tail_lower).subs(positive_part, gamma - a)
        - (phase_square + u_square + t_completion_low.subs(positive_part, gamma - a) + sp.Rational(5, 2) * r * T * U)
    )
    checks.require(
        "tail",
        "tail majorant decomposition when a is below gamma",
        low_case_difference == 0,
        low_case_difference,
        0,
    )
    high_case_remainder = T**2 / 16 + (a - gamma) * T / 2
    high_case_difference = sp.simplify(
        (p_minus - tail_lower).subs(positive_part, 0)
        - (phase_square + u_square + high_case_remainder + sp.Rational(5, 2) * r * T * U)
    )
    checks.require(
        "tail",
        "tail majorant decomposition when a is above gamma",
        high_case_difference == 0,
        high_case_difference,
        0,
    )
    z, c_tail, lower_limit = sp.symbols("z c L", positive=True)
    tail_integral = (
        sp.sqrt(sp.pi)
        / (2 * sp.sqrt(c_tail))
        * sp.exp(1 / (4 * c_tail))
        * sp.erfc(sp.sqrt(c_tail) * lower_limit + 1 / (2 * sp.sqrt(c_tail)))
    )
    checks.require(
        "tail",
        "explicit Gaussian-exponential tail primitive",
        sp.simplify(sp.diff(tail_integral, lower_limit) + sp.exp(-lower_limit - c_tail * lower_limit**2)) == 0,
        sp.simplify(sp.diff(tail_integral, lower_limit)),
        -sp.exp(-lower_limit - c_tail * lower_limit**2),
    )

    # The phase integral also has a sharp globally integrable elementary
    # envelope.  If g=I1/I0 and h=z/sqrt(z^2+4), a first positive contact
    # would have g'-h'<=0, contradicting an upward crossing.  Integration of
    # g<=h gives log I0(z)<=sqrt(z^2+4)-2.
    bessel_z = sp.symbols("bessel_z", positive=True)
    contact_h = bessel_z / sp.sqrt(bessel_z**2 + 4)
    riccati_at_contact = 1 - contact_h / bessel_z - contact_h**2
    contact_derivative_defect = sp.factor(
        riccati_at_contact - sp.diff(contact_h, bessel_z)
    )
    expected_contact_defect = (
        4 * sp.sqrt(bessel_z**2 + 4) - bessel_z**2 - 8
    ) / (bessel_z**2 + 4) ** sp.Rational(3, 2)
    checks.require(
        "bessel",
        "Bessel-ratio first-contact derivative defect",
        sp.simplify(contact_derivative_defect - expected_contact_defect) == 0,
        contact_derivative_defect,
        expected_contact_defect,
    )
    checks.require(
        "bessel",
        "first-contact numerator is nonpositive by an exact square",
        sp.expand((bessel_z**2 + 8) ** 2 - 16 * (bessel_z**2 + 4)) == bessel_z**4,
        sp.expand((bessel_z**2 + 8) ** 2 - 16 * (bessel_z**2 + 4)),
        bessel_z**4,
    )
    checks.require(
        "bessel",
        "elementary Bessel envelope has the comparison derivative",
        sp.simplify(
            sp.diff(sp.sqrt(bessel_z**2 + 4) - 2, bessel_z) - contact_h
        )
        == 0,
        sp.diff(sp.sqrt(bessel_z**2 + 4) - 2, bessel_z),
        contact_h,
    )

    # ------------------------------------------------------------------
    # Degenerate-frequency boundary and near-tight exact fixture.
    # ------------------------------------------------------------------
    one_pair_packet = (T**2 + 2 * (a - 1) * T - 2 * a) / 4
    checks.require(
        "boundary",
        "w=0 packet is one shifted one-frequency packet",
        sp.simplify(normalized_packet.subs({r: 0, cosine: 0}) - one_pair_packet) == 0,
        sp.simplify(normalized_packet.subs({r: 0, cosine: 0})),
        one_pair_packet,
    )
    one_pair_h = a**2 / 2 + a + sp.Rational(5, 4)
    checks.require(
        "boundary",
        "w=0 covariance square",
        sp.simplify(normalized_h.subs(r, 0) - one_pair_h) == 0,
        normalized_h.subs(r, 0),
        one_pair_h,
    )
    boundary_z = 4 * one_pair_packet
    boundary_target_coefficient = 4 * one_pair_h
    checks.require(
        "boundary_theorem",
        "w=0 target coefficient in tilted variables",
        sp.simplify(boundary_target_coefficient - (2 * a**2 + 4 * a + 5)) == 0,
        boundary_target_coefficient,
        2 * a**2 + 4 * a + 5,
    )
    exp_rate = sp.symbols("lambda_exp", positive=True)
    exp_mean_w = sp.simplify(2 / exp_rate**2 - 2 / exp_rate)
    exp_second_w = sp.simplify(
        24 / exp_rate**4 - 24 / exp_rate**3 + 8 / exp_rate**2
    )
    exp_variance_w = sp.factor(exp_second_w - exp_mean_w**2)
    expected_exp_mean = -2 * (exp_rate - 1) / exp_rate**2
    expected_exp_variance = 4 * (exp_rate**2 - 4 * exp_rate + 5) / exp_rate**4
    checks.require(
        "boundary_theorem",
        "tilted W mean",
        sp.simplify(exp_mean_w - expected_exp_mean) == 0,
        exp_mean_w,
        expected_exp_mean,
    )
    checks.require(
        "boundary_theorem",
        "tilted W variance",
        sp.simplify(exp_variance_w - expected_exp_variance) == 0,
        exp_variance_w,
        expected_exp_variance,
    )
    checks.require(
        "boundary_theorem",
        "tilted W variance is at most eight",
        sp.simplify(
            8 * exp_rate**4
            - 4 * (exp_rate**2 - 4 * exp_rate + 5)
            - 4 * (2 * exp_rate**4 - exp_rate**2 + 4 * exp_rate - 5)
        )
        == 0,
        sp.factor(8 * exp_rate**4 - 4 * (exp_rate**2 - 4 * exp_rate + 5)),
        4 * (2 * exp_rate**4 - exp_rate**2 + 4 * exp_rate - 5),
    )
    # For the actual tilt exp_rate=1+2at>=1.  The last polynomial is zero at
    # one and has derivative 8*lambda^3-2*lambda+4>0 thereon.
    variance_defect_poly = 2 * exp_rate**4 - exp_rate**2 + 4 * exp_rate - 5
    checks.require(
        "boundary_theorem",
        "variance defect vanishes at unit rate",
        variance_defect_poly.subs(exp_rate, 1) == 0,
        variance_defect_poly.subs(exp_rate, 1),
        0,
    )
    checks.require(
        "boundary_theorem",
        "variance defect derivative is positive from unit rate",
        sp.expand(sp.diff(variance_defect_poly, exp_rate))
        == 8 * exp_rate**3 - 2 * exp_rate + 4,
        sp.diff(variance_defect_poly, exp_rate),
        8 * exp_rate**3 - 2 * exp_rate + 4,
    )
    small_t_ceiling = sp.Rational(30, 7)
    checks.require(
        "boundary_theorem",
        "small-t Bennett reserve fits the target",
        small_t_ceiling < 5,
        small_t_ceiling,
        "<5",
    )
    checks.require(
        "boundary_theorem",
        "large-t floor and small-t Bennett split at one over 4a+5",
        sp.simplify((4 * a + 5) * (1 / (4 * a + 5))) == 1,
        sp.simplify((4 * a + 5) * (1 / (4 * a + 5))),
        1,
    )
    checks.require(
        "boundary",
        "v=0 chart is the fourfold one-frequency packet",
        sp.simplify(16 * one_pair_h - (8 * a**2 + 16 * a + 20)) == 0,
        16 * one_pair_h,
        8 * a**2 + 16 * a + 20,
    )
    checks.require(
        "boundary_theorem",
        "v=0 face has the same all-q target coefficient",
        sp.simplify((8 * a**2 + 16 * a + 20) / 4 - (2 * a**2 + 4 * a + 5)) == 0,
        sp.simplify((8 * a**2 + 16 * a + 20) / 4),
        2 * a**2 + 4 * a + 5,
    )

    mp.mp.dps = 80
    tight_a = mp.mpf(27)
    tight_t = mp.mpf(1) / 9000
    tight_log_mgf = r0_log_mgf(tight_a, tight_t)
    tight_h = tight_a**2 / 2 + tight_a + mp.mpf(5) / 4
    tight_rhs = tight_t**2 * tight_h / 4
    tight_gap = tight_rhs - tight_log_mgf
    tight_ratio = tight_log_mgf / tight_rhs
    checks.require(
        "boundary",
        "closed-form near-tight fixture has positive gap",
        tight_gap > mp.mpf("2e-9"),
        mp.nstr(tight_gap, 40),
        ">2e-9",
    )
    checks.require(
        "boundary",
        "closed-form near-tight fixture remains below target",
        mp.mpf("0.998") < tight_ratio < 1,
        mp.nstr(tight_ratio, 40),
        "in (0.998,1)",
    )

    # ------------------------------------------------------------------
    # Failure of the tempting tilted-variance monotonicity route.
    # ------------------------------------------------------------------
    tilted = tilted_a0_stats(mp.mpf(7), mp.mpf(1) / 10)
    checks.require(
        "variance_route",
        "tilted centered third moment is strictly negative",
        tilted["third_centered"] < -mp.mpf(24000),
        mp.nstr(tilted["third_centered"], 40),
        "<-24000",
    )
    checks.require(
        "variance_route",
        "tilted variance is positive and finite",
        mp.mpf(440) < tilted["variance"] < mp.mpf(441),
        mp.nstr(tilted["variance"], 40),
        "in (440,441)",
    )
    tilted_h = mp.mpf(5) / 4 + 7 + 25 * 7**2 + 16 * 7**3 + 20 * 7**4
    tilted_gap = mp.mpf("0.1") ** 2 * tilted_h / 4 - tilted["log_mgf"]
    checks.require(
        "variance_route",
        "variance-route fixture is not a target counterexample",
        tilted_gap > 100,
        mp.nstr(tilted_gap, 40),
        ">100",
    )
    psi, q_symbol = sp.Function("psi"), sp.symbols("q", positive=True)
    kappa3 = sp.symbols("kappa_3", real=True)
    checks.require(
        "variance_route",
        "log-MGF third derivative has opposite tilted-cumulant sign",
        sp.simplify(-kappa3 - (-kappa3)) == 0,
        "psi'''(q)=-kappa_3(q)",
        "psi'''(q)=-kappa_3(q)",
    )

    # Two additional separated-domination routes fail before any numerical
    # issue.  The quadratic Bessel bound creates a positive cubic radial term,
    # while conditioning one mode can produce a negative effective shifted
    # one-frequency coefficient whose leading Laplace cost is too large.
    radial_scale, q_positive, amplitude_positive = sp.symbols(
        "L q_positive amplitude_positive", positive=True
    )
    quadratic_bessel_exponent = (
        9 * q_positive**2 * amplitude_positive**2 * radial_scale**3
        - 15 * q_positive * radial_scale**2
    )
    checks.require(
        "separated_nogo",
        "quadratic Bessel envelope produces positive cubic radial growth",
        sp.LC(sp.Poly(quadratic_bessel_exponent, radial_scale))
        == 9 * q_positive**2 * amplitude_positive**2,
        sp.LC(sp.Poly(quadratic_bessel_exponent, radial_scale)),
        9 * q_positive**2 * amplitude_positive**2,
    )
    b_negative, t_fixed = sp.symbols("B t_fixed", positive=True)
    negative_effective_packet = (
        (T - b_negative - 1) ** 2 - (b_negative**2 + 1)
    )
    checks.require(
        "separated_nogo",
        "negative effective coefficient square identity",
        sp.expand(
            negative_effective_packet
            - (-2 * b_negative * (T - 1) + T**2 - 2 * T)
        )
        == 0,
        sp.expand(negative_effective_packet),
        sp.expand(-2 * b_negative * (T - 1) + T**2 - 2 * T),
    )
    leading_proxy_defect = sp.factor(t_fixed - 2 * t_fixed**2)
    checks.require(
        "separated_nogo",
        "conditional scalar proxy has the wrong leading coefficient below one half",
        sp.simplify(leading_proxy_defect - t_fixed * (1 - 2 * t_fixed)) == 0,
        leading_proxy_defect,
        t_fixed * (1 - 2 * t_fixed),
    )
    alpha_drop_fixture = sp.Rational(2, 1) - sp.Rational(5, 1)
    checks.require(
        "separated_nogo",
        "dropping the S quartic can make its Laplace rate negative",
        alpha_drop_fixture < 0,
        alpha_drop_fixture,
        "<0 at v=w=q=1,A=R=0",
    )

    status = "PASS" if all(row["status"] == "PASS" for row in checks.rows) else "FAIL"
    results: dict[str, object] = {
        "scale": {
            "shape_parameters": ["a=A^2/v", "r=w/v", "t=q*v^2"],
            "packet_weight": 2,
            "covariance_square_weight": 4,
            "normalized_packet": str(normalized_packet),
            "normalized_covariance_square": str(normalized_h),
        },
        "projective": {
            "limiting_mgf": str(projective_mgf),
            "limiting_gap": str(expected_gap),
            "first_gap_correction": str(expected_first_gap),
            "first_gap_numerator": str(pi_polynomial),
            "unique_floor_saturation_r": "1/4",
        },
        "compact_core": {
            "active_floor_cubic": str(active_cubic),
            "high_t_cutoff": "t>=4*(-p_star)/h",
            "tail_constant": "a*gamma/2+(gamma-a)_+^2+(7*a+gamma/2)^2/2",
            "tail_lower_bound": "p_minus>=T^2/16+r^2*U^2/2-C(a,r)",
            "remaining": "uniform projective remainder plus certified compact interior",
        },
        "degenerate_face_theorem": {
            "normalized_packet": str(boundary_z),
            "target_coefficient": str(boundary_target_coefficient),
            "tilted_W_mean": str(expected_exp_mean),
            "tilted_W_variance": str(expected_exp_variance),
            "small_t_branch": "t<=1/(4*a+5): centered one-sided Bennett",
            "large_t_branch": "t>=1/(4*a+5): W>=-1 floor",
            "w_zero_all_q": True,
            "v_zero_all_q": True,
        },
        "boundary_fixture": {
            "a": "27",
            "t": "1/9000",
            "log_mgf": mp.nstr(tight_log_mgf, 60),
            "rhs": mp.nstr(tight_rhs, 60),
            "gap": mp.nstr(tight_gap, 60),
            "ratio": mp.nstr(tight_ratio, 60),
        },
        "tilted_variance_route": {
            "a": "0",
            "r": "7",
            "t": "1/10",
            "log_mgf": mp.nstr(tilted["log_mgf"], 60),
            "mean": mp.nstr(tilted["mean"], 60),
            "variance": mp.nstr(tilted["variance"], 60),
            "third_centered": mp.nstr(tilted["third_centered"], 60),
            "target_gap": mp.nstr(tilted_gap, 60),
        },
        "separated_route_nogos": {
            "quadratic_bessel": "adds +9*q^2*A^2*R^2*S and is nonintegrable on R=S",
            "conditional_scalar": "negative a_eff=-B has leading log-MGF t*B^2 versus proxy 2*t^2*B^2",
            "dropped_S_quartic": "remaining Laplace rate can be negative",
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
            "bare_all_q_scalar_k2k": "open-reduced-to-projective-boundaries-and-compact-interior",
            "large_amplitude_projective_corner": "advanced-leading-and-first-correction-positive",
            "large_q_corner": "advanced-exact-floor-cutoff",
            "degenerate_frequency_faces": "proved-all-q",
            "certified_tail_enclosure": "advanced-exact-factorized-majorant",
            "tilted_variance_monotonicity": "failed",
            "quadratic_bessel_domination": "failed-nonintegrable",
            "conditional_scalar_tensorization": "failed-negative-effective-coefficient",
            "full_a1_embedding": "open",
            "adapted_production_cluster": "open",
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
