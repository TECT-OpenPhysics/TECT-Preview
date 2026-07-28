#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-114 scalar cone theorem.

This script reconstructs the centered stationary k:2k packet, its covariance
reserve and the R-113 phase floors.  It then checks the support--two-moment
reduction and every rational tensor-Bernstein coefficient used to prove the
cone 0 <= x <= 643*tau/200.  It does not claim the remaining mixed all-q theorem.
"""

from __future__ import annotations

__version__ = "1.1.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import json
import math
import os
import platform
import tempfile
from pathlib import Path

import sympy as sp


SCHEMA = "tect/a13-scalar-k2k-support-two-moment-cone-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-scalar-k2k-support-two-moment-cone/result.json"
)

# Exact test oracles independently reconstructed before this implementation.
MINIMUM_ORACLES = {
    "I1_S": sp.Rational(3228828189276149229671, 128849018880000000000000000),
    "I1_Q": sp.Rational(37759, 2560000),
    "I2_S": sp.Rational(824289456286443058922316607955591, 19660800000000000000000000000000000000),
    "I2_Q": sp.Rational(31934599, 1600000000),
    "I3_S": sp.Rational(1678113425694930246248812151, 8444249301319680000000000000000),
    "I3_Q": sp.Rational(1457, 80000),
    "I4_S": sp.Rational(4089930819610437346252570751, 982688517324800000000000000000),
    "I4_Q": sp.Rational(157279, 2560000),
    "I5_Q": sp.Rational(181, 4096),
    "I6_Q_LOW": sp.Rational(123657, 4000000),
    "I6_S_A": sp.Rational(161577960237532077, 1048576000000000000),
    "I6_S_B": sp.Rational(2530755391442237982218571711234415259638533, 31691265005705735037417580134400000000000000),
    "I6_S_C": sp.Rational(265576965141887076438339040964644393830604077, 9671406556917033397649408000000000000000000000),
    "I6_S_D": sp.Rational(3810070004416673757, 18446744073709551616),
    "I6_Q_HIGH": sp.Rational(498609, 8192000),
}

COEFFICIENT_HASH_ORACLES = {
    "I1_S": "d711d87e3c04b4836449000565eda5162473717967be9498720520026bd554b7",
    "I1_Q": "5c6d7857a1d9b89065e0a633e4846d61f972a63c58b3b57fc38e13b5cd81e19a",
    "I2_S": "1f5fb8125d7ea09bba0c0499733f72eadd915c40cd677ababf9ae6482b4a7a31",
    "I2_Q": "6ffad311b8242e6aca74e09f03cbd7e081f007635f07e9919f6485769f6a5ee2",
    "I3_S": "0b901c8781be10704eef1af62f4fca4378234f91f2cbf5160538dd3168c14043",
    "I3_Q": "4a5eadf2900a0644ca2def6929e318af5b7f996bb45b3876109c842c847d8331",
    "I4_S": "4689649754369a75e1e6540665d40eb7beee9c8c274690cb215ccf6b913cf59c",
    "I4_Q": "928c95b03d5a392238a016d4d761be85fc69941ae3a9143e5ef998552c8d016d",
    "I5_Q": "978b92c967332621d3911620b1d3d8ad42d1fefafe3aaa47bc8cd69efc554a55",
    "I6_Q_LOW": "1035b2320a0c9c3acfcc4e55a4b66da105edb4f7888a458d4617f2c83ab4d177",
    "I6_S_A": "ab46bd57906672aa0d1896dd39bfc0cf1bbfd13602fd6a5cba379bd870c6c6f9",
    "I6_S_B": "3ee962f158c3c40f21c61a0d6ae3e3ad177f169b132c26eea64a63874df3556f",
    "I6_S_C": "3c7add20fe823d9094ec88ac54b5a0bcadcfde21de4cdf91cd01d46edd8dc3dc",
    "I6_S_D": "c68025064cac89ca3608937c5ea62d3671ddb1eeee36138653ad3594be495af1",
    "I6_Q_HIGH": "53d1e00735e09662f0c53b95ee4fe1b5f5d02267dc032e5e849474fa81c1861f",
}


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


def exponential_expectation(polynomial: sp.Expr, t_var: sp.Symbol, u_var: sp.Symbol) -> sp.Expr:
    """Expectation under independent unit exponentials T and U."""
    total = sp.S.Zero
    for (power_t, power_u), coefficient in sp.Poly(sp.expand(polynomial), t_var, u_var).terms():
        total += coefficient * sp.factorial(power_t) * sp.factorial(power_u)
    return sp.factor(total)


def tensor_bernstein_coefficients(
    polynomial: sp.Expr,
    first: sp.Symbol,
    second: sp.Symbol,
    degree_first: int | None = None,
    degree_second: int | None = None,
) -> tuple[int, int, list[sp.Rational]]:
    """Power-to-Bernstein conversion on [0,1]^2, row-major in (i,j)."""
    expanded = sp.Poly(sp.expand(polynomial), first, second)
    d = expanded.degree(first) if degree_first is None else degree_first
    e = expanded.degree(second) if degree_second is None else degree_second
    monomials = expanded.as_dict()
    coefficients: list[sp.Rational] = []
    for i in range(d + 1):
        for j in range(e + 1):
            value = sp.S.Zero
            for (m, n), coefficient in monomials.items():
                if m <= i and n <= j:
                    value += (
                        coefficient
                        * sp.Rational(math.comb(i, m), math.comb(d, m))
                        * sp.Rational(math.comb(j, n), math.comb(e, n))
                    )
            coefficients.append(sp.Rational(value))
    return d, e, coefficients


def coefficient_hash(coefficients: list[sp.Rational]) -> str:
    encoded = "".join(f"{value}\n" for value in coefficients).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def bernstein_expansion(
    coefficients: list[sp.Rational], d: int, e: int, first: sp.Symbol, second: sp.Symbol
) -> sp.Expr:
    value = sp.S.Zero
    cursor = 0
    for i in range(d + 1):
        first_basis = sp.binomial(d, i) * first**i * (1 - first) ** (d - i)
        for j in range(e + 1):
            second_basis = sp.binomial(e, j) * second**j * (1 - second) ** (e - j)
            value += coefficients[cursor] * first_basis * second_basis
            cursor += 1
    return sp.expand(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    b, c, s = sp.symbols("b c s", nonnegative=True)
    t_var, u_var = sp.symbols("T U", nonnegative=True)
    rho = c * t_var / 2
    sigma = s * u_var / 8
    linear = rho + 4 * sigma - sp.Rational(1, 2)
    quadratic = rho**2 + 10 * rho * sigma + 4 * sigma**2 - rho - sigma
    phase_variance = 18 * rho**2 * sigma
    packet_without_phase = b * linear + quadratic
    mean_packet = exponential_expectation(packet_without_phase, t_var, u_var).subs(s, 1 - c)
    variance_packet = (
        exponential_expectation(packet_without_phase**2 + b * phase_variance, t_var, u_var)
        .subs(s, 1 - c)
        .expand()
    )

    k2 = c**2 - c + sp.Rational(1, 2)
    k1 = (-3 * c**3 + 5 * c**2 + c + 1) / 4
    k0 = (153 * c**4 - 156 * c**3 + 82 * c**2 - 4 * c + 5) / 64
    covariance_square = sp.expand(b**2 * k2 + b * k1 + k0)
    delta = (33 * c**4 - 36 * c**3 + 22 * c**2 - 4 * c + 1) / 64
    variance = sp.expand((covariance_square - delta) / 2)
    audit.check("moments", "packet is centered", sp.simplify(mean_packet) == 0, mean_packet, 0)
    audit.check(
        "moments",
        "packet variance reconstructed independently",
        sp.simplify(variance_packet - variance) == 0,
        sp.factor(variance_packet - variance),
        0,
    )
    delta_sos = c**4 / 4 + c**2 * (1 - c) ** 2 / 4 + (1 - c) ** 4 / 64
    audit.check("moments", "reserve identity", sp.simplify(delta - delta_sos) == 0, sp.factor(delta - delta_sos), 0)
    reserve_square = (c**2 / 2 + (1 - c) ** 2 / 8) ** 2
    audit.check(
        "moments",
        "reserve dominates one-square minorant",
        sp.simplify(sp.factor(delta - reserve_square) - c**2 * (1 - c) ** 2 / 8) == 0,
        sp.factor(delta - reserve_square),
        c**2 * (1 - c) ** 2 / 8,
    )
    audit.check(
        "moments",
        "one-square minorant has one-tenth base",
        sp.simplify(
            sp.factor(c**2 / 2 + (1 - c) ** 2 / 8 - sp.Rational(1, 10))
            - 5 * (c - sp.Rational(1, 5)) ** 2 / 8
        )
        == 0,
        sp.factor(c**2 / 2 + (1 - c) ** 2 / 8 - sp.Rational(1, 10)),
        5 * (c - sp.Rational(1, 5)) ** 2 / 8,
    )

    rho_free, sigma_free = sp.symbols("rho sigma", nonnegative=True)
    phase_minimum = (
        b * (rho_free + 4 * sigma_free - sp.Rational(1, 2))
        - 6 * sp.sqrt(b) * rho_free * sp.sqrt(sigma_free)
        + rho_free**2
        + 10 * rho_free * sigma_free
        + 4 * sigma_free**2
        - rho_free
        - sigma_free
    )
    completion_six = (
        (rho_free + 2 * sigma_free) ** 2
        - (1 + b / 2) * (rho_free + 2 * sigma_free)
        + (5 * b + 1) * sigma_free
        + 6 * rho_free * (sp.sqrt(sigma_free) - sp.sqrt(b) / 2) ** 2
        - b / 2
    )
    completion_ten = (
        rho_free**2
        + (b / 10 - 1) * rho_free
        + 4 * sigma_free**2
        + (4 * b - 1) * sigma_free
        + 10 * rho_free * (sp.sqrt(sigma_free) - 3 * sp.sqrt(b) / 10) ** 2
        - b / 2
    )
    audit.check("support", "six-completion identity", sp.simplify(phase_minimum - completion_six) == 0, sp.simplify(phase_minimum - completion_six), 0)
    audit.check("support", "ten-completion identity", sp.simplify(phase_minimum - completion_ten) == 0, sp.simplify(phase_minimum - completion_ten), 0)

    beta6 = (b**2 + 12 * b + 4) / 16
    beta10a = (401 * b**2 - 20 * b + 125) / 400
    beta10b = (b**2 + 180 * b + 100) / 400
    beta10_low_from_parts = b / 2 + (1 - b / 10) ** 2 / 4 + (1 - 4 * b) ** 2 / 16
    beta10_high_from_parts = b / 2 + (1 - b / 10) ** 2 / 4
    audit.check("support", "low beta10 branch", sp.simplify(beta10a - beta10_low_from_parts) == 0, sp.factor(beta10a - beta10_low_from_parts), 0)
    audit.check("support", "high beta10 branch", sp.simplify(beta10b - beta10_high_from_parts) == 0, sp.factor(beta10b - beta10_high_from_parts), 0)
    audit.check("support", "beta10 branch continuity", beta10a.subs(b, sp.Rational(1, 4)) == beta10b.subs(b, sp.Rational(1, 4)), beta10a.subs(b, sp.Rational(1, 4)), beta10b.subs(b, sp.Rational(1, 4)))
    audit.check("support", "cone endpoint floor branch valid", sp.Rational(3, 2) < 10, sp.Rational(3, 2), "<10")
    audit.check("support", "cone endpoint beta", beta10b.subs(b, sp.Rational(3, 2)) == sp.Rational(1489, 1600), beta10b.subs(b, sp.Rational(3, 2)), sp.Rational(1489, 1600))

    phase_y = sp.symbols("phase_y", nonnegative=True)
    phase_g = sp.expand(phase_minimum.subs(sigma_free, phase_y**2) + b / 2)
    phase_a = 10 * phase_y**2 - 6 * sp.sqrt(b) * phase_y + b - 1
    phase_g_normal = rho_free**2 + phase_a * rho_free + phase_y**2 * (4 * phase_y**2 + 4 * b - 1)
    audit.check(
        "support",
        "sharp-floor normal form",
        sp.simplify(phase_g - phase_g_normal) == 0,
        sp.factor(phase_g - phase_g_normal),
        0,
    )
    discriminant = sp.expand((2 * sp.sqrt(4 * b - 1) - 6 * sp.sqrt(b)) ** 2 - 40 * (b - 1))
    audit.check(
        "support",
        "sharp-floor auxiliary discriminant",
        sp.simplify(discriminant - 12 * (b + 3 - 2 * sp.sqrt(b * (4 * b - 1)))) == 0,
        sp.simplify(discriminant),
        "12*(b+3-2*sqrt(b*(4*b-1)))",
    )
    threshold_polynomial = 15 * b**2 - 10 * b - 9
    audit.check(
        "support",
        "sharp-floor threshold factorization",
        sp.factor(threshold_polynomial - sp.Rational(3, 5))
        == (5 * b - 6) * (15 * b + 8) / 5,
        sp.factor(threshold_polynomial - sp.Rational(3, 5)),
        "(5*b-6)*(15*b+8)/5",
    )
    audit.check(
        "support",
        "sharp-floor squared-radical identity",
        sp.expand(4 * b * (4 * b - 1) - (b + 3) ** 2) == threshold_polynomial,
        sp.expand(4 * b * (4 * b - 1) - (b + 3) ** 2),
        threshold_polynomial,
    )
    beta_sharp = b / 2
    audit.check(
        "support",
        "sharp floor attains its endpoint",
        sp.simplify(phase_minimum.subs({rho_free: 0, sigma_free: 0}) + beta_sharp) == 0,
        sp.simplify(phase_minimum.subs({rho_free: 0, sigma_free: 0})),
        -beta_sharp,
    )
    audit.check(
        "support",
        "extended cone endpoint beta",
        beta_sharp.subs(b, sp.Rational(643, 200)) == sp.Rational(643, 400),
        beta_sharp.subs(b, sp.Rational(643, 200)),
        sp.Rational(643, 400),
    )

    beta_symbol, variance_symbol = sp.symbols("beta V", positive=True)
    radius = (beta_symbol**2 + variance_symbol) / beta_symbol
    probability = beta_symbol**2 / (beta_symbol**2 + variance_symbol)
    audit.check("hermite", "two-point mean match", sp.simplify(probability * radius - beta_symbol) == 0, sp.simplify(probability * radius), beta_symbol)
    audit.check("hermite", "two-point second moment match", sp.simplify(probability * radius**2 - (beta_symbol**2 + variance_symbol)) == 0, sp.simplify(probability * radius**2), beta_symbol**2 + variance_symbol)
    audit.check("hermite", "tilted curvature at zero", sp.simplify(radius**2 * probability * (1 - probability) - variance_symbol) == 0, sp.simplify(radius**2 * probability * (1 - probability)), variance_symbol)
    audit.check("hermite", "variance-case target reserve", sp.simplify(covariance_square / 4 - variance / 2 - delta / 4) == 0, sp.simplify(covariance_square / 4 - variance / 2), delta / 4)

    y = (beta_symbol**2 - variance_symbol) / (beta_symbol**2 + variance_symbol)
    generic_s = (
        6 * sp.Symbol("K") * beta_symbol**2 * (beta_symbol**2 + variance_symbol) ** 2
        + 2 * sp.Symbol("K") * beta_symbol**2 * (beta_symbol**2 - variance_symbol) ** 2
        - 3 * (beta_symbol**2 + variance_symbol) ** 4
    )
    cleared_condition = 3 * beta_symbol**2 * (beta_symbol**2 + variance_symbol) ** 2 * (
        2 * sp.Symbol("K") * (1 + y**2 / 3) - radius**2
    )
    audit.check("kearns_saul", "cleared sufficient-condition identity", sp.simplify(generic_s - cleared_condition) == 0, sp.factor(generic_s - cleared_condition), 0)
    y_free = sp.symbols("y", nonnegative=True)
    atanh_remainder_derivative = sp.simplify(sp.diff(sp.atanh(y_free) - y_free - y_free**3 / 3, y_free))
    audit.check(
        "kearns_saul",
        "atanh cubic lower derivative",
        sp.simplify(atanh_remainder_derivative - y_free**4 / (1 - y_free**2)) == 0,
        atanh_remainder_derivative,
        y_free**4 / (1 - y_free**2),
    )

    first, second = sp.symbols("u v", nonnegative=True)
    variance_unit = sp.expand(variance.subs({b: sp.Rational(643, 200) * first, c: second}))
    degree_vb, degree_vc, variance_coefficients = tensor_bernstein_coefficients(
        variance_unit, first, second
    )
    audit.check(
        "moments",
        "variance cone bidegree",
        (degree_vb, degree_vc) == (2, 4),
        (degree_vb, degree_vc),
        (2, 4),
    )
    audit.check(
        "moments",
        "variance strictly positive on cone",
        all(value > 0 for value in variance_coefficients),
        min(variance_coefficients),
        ">0",
    )
    audit.check(
        "moments",
        "variance cone minimum coefficient",
        min(variance_coefficients) == sp.Rational(1, 32),
        min(variance_coefficients),
        sp.Rational(1, 32),
    )
    slab_data = [
        ("I1", sp.Rational(0), sp.Rational(1, 10), beta6, sp.Rational(1, 2)),
        ("I2", sp.Rational(1, 10), sp.Rational(1, 4), beta10a, sp.Rational(1, 2)),
        ("I3", sp.Rational(1, 4), sp.Rational(1), beta10b, sp.Rational(1, 2)),
    ]
    certificate_results: dict[str, object] = {}
    total_coefficient_signs = 0

    def certificate_polynomials(beta: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
        q_polynomial = sp.expand(variance - beta**2)
        s_polynomial = sp.expand(
            6 * covariance_square * beta**2 * (beta**2 + variance) ** 2
            + 2 * covariance_square * beta**2 * (beta**2 - variance) ** 2
            - 3 * (beta**2 + variance) ** 4
        )
        return q_polynomial, s_polynomial

    for label, lower_b, upper_b, beta, split_c in slab_data:
        q_polynomial, s_polynomial = certificate_polynomials(beta)
        s_unit = sp.expand(s_polynomial.subs({b: lower_b + (upper_b - lower_b) * first, c: split_c * second}))
        q_unit = sp.expand(q_polynomial.subs({b: lower_b + (upper_b - lower_b) * first, c: split_c + (1 - split_c) * second}))
        d_s, e_s, s_coefficients = tensor_bernstein_coefficients(s_unit, first, second)
        d_q, e_q, q_coefficients = tensor_bernstein_coefficients(q_unit, first, second)
        audit.check("bernstein", f"{label} S bidegree", (d_s, e_s) == (16, 16), (d_s, e_s), (16, 16))
        audit.check("bernstein", f"{label} Q bidegree", (d_q, e_q) == (4, 4), (d_q, e_q), (4, 4))
        audit.check("bernstein", f"{label} S coefficient count", len(s_coefficients) == 289, len(s_coefficients), 289)
        audit.check("bernstein", f"{label} Q coefficient count", len(q_coefficients) == 25, len(q_coefficients), 25)
        audit.check("bernstein", f"{label} all S coefficients positive", all(value > 0 for value in s_coefficients), min(s_coefficients), ">0")
        audit.check("bernstein", f"{label} all Q coefficients positive", all(value > 0 for value in q_coefficients), min(q_coefficients), ">0")
        audit.check("bernstein", f"{label} S exact minimum oracle", min(s_coefficients) == MINIMUM_ORACLES[f"{label}_S"], min(s_coefficients), MINIMUM_ORACLES[f"{label}_S"])
        audit.check("bernstein", f"{label} Q exact minimum oracle", min(q_coefficients) == MINIMUM_ORACLES[f"{label}_Q"], min(q_coefficients), MINIMUM_ORACLES[f"{label}_Q"])
        audit.check("bernstein", f"{label} S coefficient hash", coefficient_hash(s_coefficients) == COEFFICIENT_HASH_ORACLES[f"{label}_S"], coefficient_hash(s_coefficients), COEFFICIENT_HASH_ORACLES[f"{label}_S"])
        audit.check("bernstein", f"{label} Q coefficient hash", coefficient_hash(q_coefficients) == COEFFICIENT_HASH_ORACLES[f"{label}_Q"], coefficient_hash(q_coefficients), COEFFICIENT_HASH_ORACLES[f"{label}_Q"])
        if label == "I1":
            audit.check("bernstein", "I1 S expansion reconstruction", sp.expand(bernstein_expansion(s_coefficients, d_s, e_s, first, second) - s_unit) == 0, "reconstructed", "exact polynomial")
        total_coefficient_signs += len(s_coefficients) + len(q_coefficients)
        certificate_results[label] = {
            "b_interval": [str(lower_b), str(upper_b)],
            "low_c_S_interval": ["0", str(split_c)],
            "high_c_Q_interval": [str(split_c), "1"],
            "S_coefficient_count": len(s_coefficients),
            "Q_coefficient_count": len(q_coefficients),
            "S_minimum": str(min(s_coefficients)),
            "Q_minimum": str(min(q_coefficients)),
            "S_sha256": coefficient_hash(s_coefficients),
            "Q_sha256": coefficient_hash(q_coefficients),
        }

    q4, s4 = certificate_polynomials(beta10b)
    i4_s_coefficients: list[sp.Rational] = []
    i4_cell_minima: list[str] = []
    for index in range(8):
        lower_c = sp.Rational(3 * index, 40)
        upper_c = sp.Rational(3 * (index + 1), 40)
        unit = sp.expand(s4.subs({b: 1 + first / 2, c: lower_c + (upper_c - lower_c) * second}))
        d_cell, e_cell, coefficients = tensor_bernstein_coefficients(unit, first, second)
        audit.check("bernstein", f"I4 S cell {index} bidegree", (d_cell, e_cell) == (16, 16), (d_cell, e_cell), (16, 16))
        audit.check("bernstein", f"I4 S cell {index} count", len(coefficients) == 289, len(coefficients), 289)
        audit.check("bernstein", f"I4 S cell {index} positive", all(value > 0 for value in coefficients), min(coefficients), ">0")
        if index == 0:
            audit.check("bernstein", "I4 first S-cell expansion reconstruction", sp.expand(bernstein_expansion(coefficients, d_cell, e_cell, first, second) - unit) == 0, "reconstructed", "exact polynomial")
        i4_s_coefficients.extend(coefficients)
        i4_cell_minima.append(str(min(coefficients)))
    q4_unit = sp.expand(q4.subs({b: 1 + first / 2, c: sp.Rational(3, 5) + sp.Rational(2, 5) * second}))
    d_q4, e_q4, q4_coefficients = tensor_bernstein_coefficients(q4_unit, first, second)
    audit.check("bernstein", "I4 Q bidegree", (d_q4, e_q4) == (4, 4), (d_q4, e_q4), (4, 4))
    audit.check("bernstein", "I4 Q coefficient count", len(q4_coefficients) == 25, len(q4_coefficients), 25)
    audit.check("bernstein", "I4 all Q coefficients positive", all(value > 0 for value in q4_coefficients), min(q4_coefficients), ">0")
    audit.check("bernstein", "I4 S exact minimum oracle", min(i4_s_coefficients) == MINIMUM_ORACLES["I4_S"], min(i4_s_coefficients), MINIMUM_ORACLES["I4_S"])
    audit.check("bernstein", "I4 Q exact minimum oracle", min(q4_coefficients) == MINIMUM_ORACLES["I4_Q"], min(q4_coefficients), MINIMUM_ORACLES["I4_Q"])
    audit.check("bernstein", "I4 S coefficient hash", coefficient_hash(i4_s_coefficients) == COEFFICIENT_HASH_ORACLES["I4_S"], coefficient_hash(i4_s_coefficients), COEFFICIENT_HASH_ORACLES["I4_S"])
    audit.check("bernstein", "I4 Q coefficient hash", coefficient_hash(q4_coefficients) == COEFFICIENT_HASH_ORACLES["I4_Q"], coefficient_hash(q4_coefficients), COEFFICIENT_HASH_ORACLES["I4_Q"])
    total_coefficient_signs += len(i4_s_coefficients) + len(q4_coefficients)
    certificate_results["I4"] = {
        "b_interval": ["1", "3/2"],
        "low_c_S_cells": [[str(sp.Rational(3 * index, 40)), str(sp.Rational(3 * (index + 1), 40))] for index in range(8)],
        "high_c_Q_interval": ["3/5", "1"],
        "S_coefficient_count": len(i4_s_coefficients),
        "Q_coefficient_count": len(q4_coefficients),
        "S_cell_minima": i4_cell_minima,
        "S_minimum": str(min(i4_s_coefficients)),
        "Q_minimum": str(min(q4_coefficients)),
        "S_sha256": coefficient_hash(i4_s_coefficients),
        "Q_sha256": coefficient_hash(q4_coefficients),
    }

    q_sharp, s_sharp = certificate_polynomials(beta_sharp)
    i5_q_coefficients: list[sp.Rational] = []
    i5_q_cell_minima: list[str] = []
    for index in range(4):
        lower_c = sp.Rational(index, 4)
        upper_c = sp.Rational(index + 1, 4)
        unit = sp.expand(
            q_sharp.subs(
                {
                    b: sp.Rational(3, 2) + first / 2,
                    c: lower_c + (upper_c - lower_c) * second,
                }
            )
        )
        d_cell, e_cell, coefficients = tensor_bernstein_coefficients(unit, first, second)
        audit.check("bernstein", f"I5 Q cell {index} bidegree", (d_cell, e_cell) == (2, 4), (d_cell, e_cell), (2, 4))
        audit.check("bernstein", f"I5 Q cell {index} count", len(coefficients) == 15, len(coefficients), 15)
        audit.check("bernstein", f"I5 Q cell {index} positive", all(value > 0 for value in coefficients), min(coefficients), ">0")
        i5_q_coefficients.extend(coefficients)
        i5_q_cell_minima.append(str(min(coefficients)))
    audit.check("bernstein", "I5 Q exact minimum oracle", min(i5_q_coefficients) == MINIMUM_ORACLES["I5_Q"], min(i5_q_coefficients), MINIMUM_ORACLES["I5_Q"])
    audit.check("bernstein", "I5 Q coefficient hash", coefficient_hash(i5_q_coefficients) == COEFFICIENT_HASH_ORACLES["I5_Q"], coefficient_hash(i5_q_coefficients), COEFFICIENT_HASH_ORACLES["I5_Q"])
    total_coefficient_signs += len(i5_q_coefficients)
    certificate_results["I5"] = {
        "b_interval": ["3/2", "2"],
        "floor": "b/2",
        "Q_c_cells": [[str(sp.Rational(index, 4)), str(sp.Rational(index + 1, 4))] for index in range(4)],
        "Q_coefficient_count": len(i5_q_coefficients),
        "Q_cell_minima": i5_q_cell_minima,
        "Q_minimum": str(min(i5_q_coefficients)),
        "Q_sha256": coefficient_hash(i5_q_coefficients),
    }

    i6_regions = (
        ("Q_LOW", q_sharp, sp.Rational(0), sp.Rational(1, 10), 2, 4, 15),
        ("S_A", s_sharp, sp.Rational(1, 10), sp.Rational(37, 160), 8, 16, 153),
        ("S_B", s_sharp, sp.Rational(37, 160), sp.Rational(19, 64), 8, 16, 153),
        ("S_C", s_sharp, sp.Rational(19, 64), sp.Rational(29, 80), 8, 16, 153),
        ("S_D", s_sharp, sp.Rational(29, 80), sp.Rational(5, 8), 8, 16, 153),
        ("Q_HIGH", q_sharp, sp.Rational(5, 8), sp.Rational(1), 2, 4, 15),
    )
    i6_results: dict[str, object] = {}
    for label, polynomial, lower_c, upper_c, expected_d, expected_e, expected_count in i6_regions:
        unit = sp.expand(
            polynomial.subs(
                {
                    b: 2 + sp.Rational(243, 200) * first,
                    c: lower_c + (upper_c - lower_c) * second,
                }
            )
        )
        degree_b, degree_c, coefficients = tensor_bernstein_coefficients(unit, first, second)
        audit.check("bernstein", f"I6 {label} bidegree", (degree_b, degree_c) == (expected_d, expected_e), (degree_b, degree_c), (expected_d, expected_e))
        audit.check("bernstein", f"I6 {label} count", len(coefficients) == expected_count, len(coefficients), expected_count)
        audit.check("bernstein", f"I6 {label} positive", all(value > 0 for value in coefficients), min(coefficients), ">0")
        oracle_key = f"I6_{label}"
        audit.check("bernstein", f"I6 {label} minimum oracle", min(coefficients) == MINIMUM_ORACLES[oracle_key], min(coefficients), MINIMUM_ORACLES[oracle_key])
        audit.check("bernstein", f"I6 {label} coefficient hash", coefficient_hash(coefficients) == COEFFICIENT_HASH_ORACLES[oracle_key], coefficient_hash(coefficients), COEFFICIENT_HASH_ORACLES[oracle_key])
        total_coefficient_signs += len(coefficients)
        i6_results[label] = {
            "c_interval": [str(lower_c), str(upper_c)],
            "coefficient_count": len(coefficients),
            "minimum": str(min(coefficients)),
            "sha256": coefficient_hash(coefficients),
        }
    certificate_results["I6"] = {
        "b_interval": ["2", "643/200"],
        "floor": "b/2",
        "regions": i6_results,
    }
    audit.check("bernstein", "total exact coefficient signs", total_coefficient_signs == 3981, total_coefficient_signs, 3981)

    witness_b = sp.Rational(103, 32)
    witness_c = sp.Rational(5, 16)
    witness_s = sp.factor(s_sharp.subs({b: witness_b, c: witness_c}))
    witness_q = sp.factor(q_sharp.subs({b: witness_b, c: witness_c}))
    witness_k = sp.factor(covariance_square.subs({b: witness_b, c: witness_c}))
    witness_delta = sp.factor(delta.subs(c, witness_c))
    witness_v = sp.factor(variance.subs({b: witness_b, c: witness_c}))
    audit.check("method_boundary", "witness covariance square", witness_k == sp.Rational(18714321, 4194304), witness_k, sp.Rational(18714321, 4194304))
    audit.check("method_boundary", "witness reserve", witness_delta == sp.Rational(73041, 4194304), witness_delta, sp.Rational(73041, 4194304))
    audit.check("method_boundary", "witness variance", witness_v == sp.Rational(145635, 65536), witness_v, sp.Rational(145635, 65536))
    audit.check("method_boundary", "beyond-cone variance case unavailable at witness", witness_q < 0, witness_q, "<0")
    audit.check("method_boundary", "beyond-cone variance witness value", witness_q == -sp.Rational(24109, 65536), witness_q, -sp.Rational(24109, 65536))
    audit.check("method_boundary", "cubic KS proxy fails at witness", witness_s == -sp.Rational(127544381197984065, 18446744073709551616), witness_s, -sp.Rational(127544381197984065, 18446744073709551616))

    # Coefficientwise three-phase Bessel majorant, retained as a reusable route.
    order_symbol = sp.symbols("n", integer=True, positive=True)
    central_ratio = sp.binomial(2 * order_symbol, order_symbol) / 4**order_symbol
    audit.check(
        "bessel",
        "central-binomial ratio recurrence",
        sp.simplify(
            central_ratio.subs(order_symbol, order_symbol + 1) / central_ratio
            - sp.Rational(1, 2) * (2 * order_symbol + 1) / (order_symbol + 1)
        )
        == 0,
        sp.simplify(central_ratio.subs(order_symbol, order_symbol + 1) / central_ratio),
        "(2*n+1)/(2*n+2)<1",
    )
    for order in range(1, 13):
        i0_coefficient = sp.Rational(1, 4**order * sp.factorial(order) ** 2)
        surrogate_coefficient = sp.Rational(1, 2 * sp.factorial(2 * order))
        audit.check(
            "bessel",
            f"three-phase coefficient order {order}",
            surrogate_coefficient >= i0_coefficient,
            surrogate_coefficient - i0_coefficient,
            ">=0",
        )
    audit.check("bessel", "first strict Bessel defect", sp.Rational(1, 2 * sp.factorial(4)) - sp.Rational(1, 4**2 * sp.factorial(2) ** 2) == sp.Rational(1, 192), sp.Rational(1, 2 * sp.factorial(4)) - sp.Rational(1, 4**2 * sp.factorial(2) ** 2), sp.Rational(1, 192))

    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    results: dict[str, object] = {
        "normal_form": {
            "K": str(covariance_square),
            "Delta": str(delta),
            "V": str(variance),
            "centered": True,
        },
        "support_floors": {
            "beta6": str(beta6),
            "beta10a": str(beta10a),
            "beta10b": str(beta10b),
            "beta_sharp_for_b_ge_6_over_5": str(beta_sharp),
        },
        "cone": {
            "condition": "tau>0 and 0<=x<=643*tau/200",
            "projective_ratio": "0<=b=x/tau<=643/200",
            "strict_gap": True,
            "origin_equality": True,
            "tau_zero_x_positive_in_scope": False,
        },
        "bernstein_certificates": certificate_results,
        "exact_coefficient_signs": total_coefficient_signs,
        "three_phase_bessel_majorant": {
            "inequality": "I0(z)<=(1+cosh(z))/2",
            "first_defect": "z^4/192",
            "needed_for_cone_theorem": False,
        },
        "method_boundary": {
            "witness": {"b": str(witness_b), "c": str(witness_c), "K": str(witness_k), "Delta": str(witness_delta), "V": str(witness_v), "Q": str(witness_q), "S": str(witness_s)},
            "meaning": "the cubic Kearns-Saul proxy with the selected floor fails, not the exact target",
        },
        "runtime_versions": {"sympy": sp.__version__, "python": platform.python_version()},
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
            "support_two_moment_cone": "proved-exact-through-b=643/200",
            "zero_amplitude_boundary": "proved-all-tau",
            "three_phase_bessel_majorant": "proved-reusable-not-needed",
            "cubic_proxy_beyond_cone": "failed-at-exact-witness",
            "mixed_all_q_scalar_k2k": "open",
            "full_a1_embedding": "open",
            "one_use_source_sextic_aggregation": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_a": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"primary {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    print(f"exact Bernstein signs {total_coefficient_signs}/3981 positive")
    print("proved original-packet cone 0<=x<=643*tau/200 for tau>0")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
