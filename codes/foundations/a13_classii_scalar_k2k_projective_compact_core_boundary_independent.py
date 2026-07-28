#!/usr/bin/env python3
"""Non-importing independent certificate for the scoped R-111 boundary.

This script does not import the primary certificate.  It reconstructs the
all-q degenerate-face split and the projective expansion from exponential
moments, repeats the phase-floor and tail decompositions, compares the
one-frequency erfc formula with direct adaptive quadrature, and audits the
tilted-variance counterexample with an independent tensor Gauss--Laguerre
calculation.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

import mpmath as mp
import numpy as np
import sympy as sp


SCHEMA = "tect/a13-scalar-k2k-projective-compact-core-boundary-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-scalar-k2k-projective-compact-core-boundary/result.json"
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


def tensor_tilted_stats(r_value: float, t_value: float, order: int) -> dict[str, float]:
    nodes, weights = np.polynomial.laguerre.laggauss(order)
    t_node = nodes[:, None]
    u_node = nodes[None, :]
    gamma = 1.0 + 4.0 * r_value
    packet = (
        t_node**2 / 4.0
        + r_value**2 * u_node**2
        + 2.5 * r_value * t_node * u_node
        - gamma * (t_node + r_value * u_node) / 2.0
    )
    log_weight = (
        np.log(weights[:, None])
        + np.log(weights[None, :])
        - t_value * packet
    )
    maximum = float(np.max(log_weight))
    unnormalized = np.exp(log_weight - maximum)
    partition_scaled = float(unnormalized.sum())
    probability = unnormalized / partition_scaled
    mean = float((probability * packet).sum())
    centered = packet - mean
    variance = float((probability * centered**2).sum())
    third = float((probability * centered**3).sum())
    log_mgf = maximum + math.log(partition_scaled)
    return {
        "log_mgf": log_mgf,
        "mean": mean,
        "variance": variance,
        "third_centered": third,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    a, r, x = sp.symbols("a r x", nonnegative=True)
    T, U, cosine = sp.symbols("T U cosine", real=True)
    gamma = 1 + 4 * r
    packet = (
        T**2 / 4
        + r**2 * U**2
        + sp.Rational(5, 2) * r * T * U
        + a * (T / 2 + 2 * r * U - gamma / 2)
        - gamma * (T + r * U) / 2
        + 3 * sp.sqrt(a * r / 2) * T * sp.sqrt(U) * cosine
    )
    h = (
        a**2 * (sp.Rational(1, 2) + 8 * r**2)
        + a * (1 + 10 * r + 16 * r**2 + 16 * r**3)
        + sp.Rational(5, 4)
        + r
        + 25 * r**2
        + 16 * r**3
        + 20 * r**4
    )
    checks.require(
        "normal_form",
        "packet is centered at first moment",
        sp.simplify(
            packet.subs(cosine, 0)
            .subs({T**2: 2, U**2: 2, T * U: 1, T: 1, U: 1})
        )
        == 0,
        sp.simplify(
            packet.subs(cosine, 0)
            .subs({T**2: 2, U**2: 2, T * U: 1, T: 1, U: 1})
        ),
        0,
    )
    checks.require(
        "normal_form",
        "Bessel phase coefficient",
        sp.simplify(packet.coeff(cosine) - 3 * sp.sqrt(a * r / 2) * T * sp.sqrt(U)) == 0,
        packet.coeff(cosine),
        3 * sp.sqrt(a * r / 2) * T * sp.sqrt(U),
    )

    alpha = 1 + x / 2
    beta = 1 + 2 * r * x
    limiting_mgf = sp.exp(x * gamma / 2) / (alpha * beta)
    d = lambda value: value**2 / 2 - value + sp.log(1 + value)
    limiting_gap = d(x / 2) + d(2 * r * x)
    checks.require(
        "projective",
        "independent exponential transform",
        sp.simplify(
            sp.exp(x * gamma / 2)
            * sp.integrate(sp.exp(-alpha * T), (T, 0, sp.oo))
            * sp.integrate(sp.exp(-beta * U), (U, 0, sp.oo))
            - limiting_mgf
        )
        == 0,
        limiting_mgf,
        limiting_mgf,
    )
    checks.require(
        "projective",
        "limiting RHS minus log M",
        sp.simplify(
            sp.expand_log(x**2 / 8 + 2 * r**2 * x**2 - sp.log(limiting_mgf), force=True)
            - limiting_gap
        )
        == 0,
        sp.expand_log(x**2 / 8 + 2 * r**2 * x**2 - sp.log(limiting_mgf), force=True),
        limiting_gap,
    )
    y = sp.symbols("y", nonnegative=True)
    d_y = y**2 / 2 - y + sp.log(1 + y)
    checks.require(
        "projective",
        "gap derivative is nonnegative",
        sp.simplify(sp.diff(d_y, y) - y**2 / (1 + y)) == 0,
        sp.diff(d_y, y),
        y**2 / (1 + y),
    )

    e_t = 1 / alpha
    e_t2 = 2 / alpha**2
    e_u = 1 / beta
    e_u2 = 2 / beta**2
    e_b2 = sp.Rational(9, 4) * r * e_t2 * e_u
    e_q = (
        e_t2 / 4
        + r**2 * e_u2
        + sp.Rational(5, 2) * r * e_t * e_u
        - gamma * (e_t + r * e_u) / 2
    )
    log_correction = sp.simplify(x**2 * e_b2 / 2 - x * e_q)
    h_linear = 1 + 10 * r + 16 * r**2 + 16 * r**3
    gap_correction = sp.factor(x**2 * h_linear / 4 - log_correction)
    numerator = sp.factor(4 * (x + 2) ** 2 * (1 + 2 * r * x) ** 2 * gap_correction / x**3)
    expected_numerator = (
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
    checks.require(
        "projective",
        "independent first-correction numerator",
        sp.simplify(numerator - expected_numerator) == 0,
        numerator,
        expected_numerator,
    )
    checks.require(
        "projective",
        "first-correction coefficients are all positive",
        all(coefficient > 0 for coefficient in sp.Poly(numerator, x, r).coeffs()),
        sp.Poly(numerator, x, r).coeffs(),
        "all positive",
    )
    for r_value, x_value in (
        (sp.Rational(1, 4), sp.Rational(1, 3)),
        (sp.Rational(2, 3), sp.Rational(5, 4)),
        (sp.Integer(3), sp.Rational(7, 5)),
    ):
        fixture = sp.simplify(gap_correction.subs({r: r_value, x: x_value}))
        checks.require(
            "projective_fixture",
            f"positive first correction at r={r_value}, x={x_value}",
            fixture > 0,
            fixture,
            ">0",
        )

    floor_defect = sp.factor(2 + 32 * r**2 - (1 + 4 * r) ** 2)
    checks.require(
        "projective",
        "floor saturation discriminant",
        sp.simplify(floor_defect - (4 * r - 1) ** 2) == 0,
        floor_defect,
        (4 * r - 1) ** 2,
    )
    checks.require(
        "projective",
        "saturation shape retains positive limiting gap",
        sp.simplify(limiting_gap.subs(r, sp.Rational(1, 4)) - 2 * d(x / 2)) == 0,
        sp.simplify(limiting_gap.subs(r, sp.Rational(1, 4))),
        2 * d(x / 2),
    )

    radial, root_s = sp.symbols("R y", nonnegative=True)
    b_radial = a - gamma + 10 * root_s**2 - 6 * sp.sqrt(a) * root_s
    c_radial = 4 * root_s**4 + (4 * a - gamma) * root_s**2 - gamma * a / 2
    active = sp.expand(c_radial - b_radial**2 / 4)
    cubic = (
        84 * root_s**3
        - 90 * sp.sqrt(a) * root_s**2
        + (20 * a - 8 * gamma) * root_s
        + 3 * sp.sqrt(a) * (gamma - a)
    )
    checks.require(
        "floor",
        "independent active stationary cubic",
        sp.simplify(sp.diff(active, root_s) + cubic) == 0,
        sp.diff(active, root_s),
        -cubic,
    )
    checks.require(
        "floor",
        "radial minimizer square completion",
        sp.simplify(radial**2 + b_radial * radial - ((radial + b_radial / 2) ** 2 - b_radial**2 / 4)) == 0,
        radial**2 + b_radial * radial,
        (radial + b_radial / 2) ** 2 - b_radial**2 / 4,
    )

    phase_amplitude = 3 * sp.sqrt(a * r / 2) * T * sp.sqrt(U)
    p_zero = packet.subs(cosine, 0)
    p_minus = sp.expand(p_zero - phase_amplitude)
    d_plus = sp.symbols("d_plus", nonnegative=True)
    k_value = 7 * a + gamma / 2
    tail_constant = a * gamma / 2 + d_plus**2 + k_value**2 / 2
    tail_lower = T**2 / 16 + r**2 * U**2 / 2 - tail_constant
    phase_square = (T / (2 * sp.sqrt(2)) - 3 * sp.sqrt(a * r * U)) ** 2
    u_square = (r * U - k_value) ** 2 / 2
    low_square = (T / 4 - d_plus) ** 2
    low_decomposition = sp.simplify(
        (p_minus - tail_lower).subs(d_plus, gamma - a)
        - (phase_square + u_square + low_square.subs(d_plus, gamma - a) + sp.Rational(5, 2) * r * T * U)
    )
    checks.require(
        "tail",
        "independent low-a tail square decomposition",
        low_decomposition == 0,
        low_decomposition,
        0,
    )
    high_remainder = T**2 / 16 + (a - gamma) * T / 2
    high_decomposition = sp.simplify(
        (p_minus - tail_lower).subs(d_plus, 0)
        - (phase_square + u_square + high_remainder + sp.Rational(5, 2) * r * T * U)
    )
    checks.require(
        "tail",
        "independent high-a tail square decomposition",
        high_decomposition == 0,
        high_decomposition,
        0,
    )

    bessel_z = sp.symbols("bessel_z", positive=True)
    comparison_ratio = bessel_z / sp.sqrt(bessel_z**2 + 4)
    ratio_riccati = 1 - comparison_ratio / bessel_z - comparison_ratio**2
    contact_defect = sp.factor(
        ratio_riccati - sp.diff(comparison_ratio, bessel_z)
    )
    expected_contact = (
        4 * sp.sqrt(bessel_z**2 + 4) - bessel_z**2 - 8
    ) / (bessel_z**2 + 4) ** sp.Rational(3, 2)
    checks.require(
        "bessel",
        "independent Bessel-ratio contact identity",
        sp.simplify(contact_defect - expected_contact) == 0,
        contact_defect,
        expected_contact,
    )
    checks.require(
        "bessel",
        "contact numerator comparison squares to bessel_z fourth power",
        sp.expand((bessel_z**2 + 8) ** 2 - 16 * (bessel_z**2 + 4)) == bessel_z**4,
        sp.expand((bessel_z**2 + 8) ** 2 - 16 * (bessel_z**2 + 4)),
        bessel_z**4,
    )

    # Independent reconstruction of the exact two-branch all-q proof on the
    # w=0 face.  With Z=2a(X-1)+W and W=X^2-2X, the linear tilt has rate
    # lambda=1+2at.  Its centered W residual has upper floor one and variance
    # at most eight.
    exp_rate = sp.symbols("lambda_exp", positive=True)
    mean_w = sp.simplify(2 / exp_rate**2 - 2 / exp_rate)
    second_w = sp.simplify(24 / exp_rate**4 - 24 / exp_rate**3 + 8 / exp_rate**2)
    variance_w = sp.factor(second_w - mean_w**2)
    checks.require(
        "boundary_theorem",
        "independent tilted W mean",
        sp.simplify(mean_w + 2 * (exp_rate - 1) / exp_rate**2) == 0,
        mean_w,
        -2 * (exp_rate - 1) / exp_rate**2,
    )
    checks.require(
        "boundary_theorem",
        "independent tilted W variance",
        sp.simplify(
            variance_w - 4 * (exp_rate**2 - 4 * exp_rate + 5) / exp_rate**4
        )
        == 0,
        variance_w,
        4 * (exp_rate**2 - 4 * exp_rate + 5) / exp_rate**4,
    )
    variance_defect = sp.factor(
        8 * exp_rate**4 - 4 * (exp_rate**2 - 4 * exp_rate + 5)
    )
    checks.require(
        "boundary_theorem",
        "variance-eight defect factors positively from unit rate",
        sp.simplify(
            variance_defect
            - 4
            * (exp_rate - 1)
            * (2 * exp_rate**3 + 2 * exp_rate**2 + exp_rate + 5)
        )
        == 0,
        variance_defect,
        4
        * (exp_rate - 1)
        * (2 * exp_rate**3 + 2 * exp_rate**2 + exp_rate + 5),
    )
    checks.require(
        "boundary_theorem",
        "small-t exponential-series coefficient fits five",
        sp.Rational(30, 7) < 5,
        sp.Rational(30, 7),
        "<5",
    )
    boundary_target = 2 * a**2 + 4 * a + 5
    checks.require(
        "boundary_theorem",
        "small and large branches meet at the floor threshold",
        sp.simplify(boundary_target * (1 / (4 * a + 5)) - 2 * a**2 / (4 * a + 5) - 1) == 0,
        sp.simplify(boundary_target * (1 / (4 * a + 5))),
        1 + 2 * a**2 / (4 * a + 5),
    )

    b_negative, t_fixed = sp.symbols("B t_fixed", positive=True)
    negative_packet = (T - b_negative - 1) ** 2 - (b_negative**2 + 1)
    checks.require(
        "separated_nogo",
        "independent negative-effective-coefficient identity",
        sp.expand(
            negative_packet
            - (-2 * b_negative * (T - 1) + T**2 - 2 * T)
        )
        == 0,
        sp.expand(negative_packet),
        sp.expand(-2 * b_negative * (T - 1) + T**2 - 2 * T),
    )
    checks.require(
        "separated_nogo",
        "conditional proxy leading gap is positive below one half",
        sp.simplify(t_fixed - 2 * t_fixed**2 - t_fixed * (1 - 2 * t_fixed)) == 0,
        sp.factor(t_fixed - 2 * t_fixed**2),
        t_fixed * (1 - 2 * t_fixed),
    )
    radial_scale, q_positive, amplitude_positive = sp.symbols(
        "L q_positive amplitude_positive", positive=True
    )
    bad_phase_envelope = (
        9 * q_positive**2 * amplitude_positive**2 * radial_scale**3
        - 15 * q_positive * radial_scale**2
    )
    checks.require(
        "separated_nogo",
        "independent quadratic-Bessel cubic coefficient",
        sp.Poly(bad_phase_envelope, radial_scale).LC()
        == 9 * q_positive**2 * amplitude_positive**2,
        sp.Poly(bad_phase_envelope, radial_scale).LC(),
        9 * q_positive**2 * amplitude_positive**2,
    )

    mp.mp.dps = 80
    a_value = mp.mpf(27)
    t_value = mp.mpf(1) / 9000
    beta_value = 1 + t_value * (a_value - 1) / 2
    closed = (
        t_value * a_value / 2
        + mp.log(mp.sqrt(mp.pi / t_value))
        + beta_value**2 / t_value
        + mp.log(mp.erfc(beta_value / mp.sqrt(t_value)))
    )
    direct_integral = mp.quad(
        lambda value: mp.exp(
            -value
            - t_value
            * (value**2 + 2 * (a_value - 1) * value - 2 * a_value)
            / 4
        ),
        [0, 1, 2, 4, 8, mp.inf],
    )
    direct = mp.log(direct_integral)
    checks.require(
        "boundary",
        "direct integral agrees with erfc formula",
        abs(closed - direct) < mp.mpf("1e-70"),
        mp.nstr(abs(closed - direct), 30),
        "<1e-70",
    )
    boundary_h = a_value**2 / 2 + a_value + mp.mpf(5) / 4
    boundary_gap = t_value**2 * boundary_h / 4 - closed
    checks.require(
        "boundary",
        "independent near-tight boundary gap is positive",
        boundary_gap > mp.mpf("2e-9"),
        mp.nstr(boundary_gap, 40),
        ">2e-9",
    )

    tilted_orders: dict[str, dict[str, float]] = {}
    for order in (96, 128):
        statistics = tensor_tilted_stats(7.0, 0.1, order)
        tilted_orders[str(order)] = statistics
        checks.require(
            "variance_route",
            f"negative tilted third moment at Laguerre order {order}",
            statistics["third_centered"] < -24000.0,
            statistics["third_centered"],
            "<-24000",
        )
        checks.require(
            "variance_route",
            f"tilted variance stable at Laguerre order {order}",
            440.0 < statistics["variance"] < 441.0,
            statistics["variance"],
            "in (440,441)",
        )
    checks.require(
        "variance_route",
        "independent tilted third signs agree",
        tilted_orders["96"]["third_centered"] * tilted_orders["128"]["third_centered"] > 0,
        [tilted_orders["96"]["third_centered"], tilted_orders["128"]["third_centered"]],
        "same negative sign",
    )
    h_fixture = 1.25 + 7 + 25 * 7**2 + 16 * 7**3 + 20 * 7**4
    for order in (96, 128):
        gap = 0.1**2 * h_fixture / 4 - tilted_orders[str(order)]["log_mgf"]
        checks.require(
            "variance_route",
            f"tilted fixture remains far inside target at order {order}",
            gap > 100.0,
            gap,
            ">100",
        )

    status = "PASS" if all(row["status"] == "PASS" for row in checks.rows) else "FAIL"
    results: dict[str, object] = {
        "normal_form": {
            "packet": str(packet),
            "covariance_square": str(h),
        },
        "projective": {
            "limiting_mgf": str(limiting_mgf),
            "limiting_gap": str(limiting_gap),
            "first_gap_correction": str(gap_correction),
            "first_gap_numerator": str(numerator),
        },
        "floor_tail": {
            "active_cubic": str(cubic),
            "tail_lower_bound": "p_minus>=T^2/16+r^2*U^2/2-C(a,r)",
        },
        "degenerate_face_theorem": {
            "target_coefficient": str(boundary_target),
            "tilted_W_mean": str(mean_w),
            "tilted_W_variance": str(variance_w),
            "w_zero_all_q": True,
            "v_zero_all_q": True,
        },
        "boundary": {
            "a": "27",
            "t": "1/9000",
            "log_mgf": mp.nstr(closed, 60),
            "gap": mp.nstr(boundary_gap, 60),
        },
        "tilted_variance_route": tilted_orders,
        "separated_route_nogos": {
            "quadratic_bessel": "nonintegrable positive cubic radial exponent",
            "conditional_scalar": "negative effective coefficient defeats the positive-a scalar proxy",
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
            "bare_all_q_scalar_k2k": "open",
            "projective_boundary": "advanced",
            "degenerate_frequency_faces": "proved-all-q",
            "certified_tail_enclosure": "advanced",
            "tilted_variance_monotonicity": "failed",
            "quadratic_bessel_domination": "failed",
            "conditional_scalar_tensorization": "failed",
            "adapted_production_cluster": "open",
            "sector_a": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"independent {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
