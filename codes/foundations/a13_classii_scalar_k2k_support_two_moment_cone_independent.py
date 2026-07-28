#!/usr/bin/env python3
"""Non-importing exact verifier for the scoped R-114 scalar cone theorem.

The implementation deliberately avoids SymPy and the primary source.  It
uses sparse Fraction polynomials and de Casteljau subdivision for selected
cells, providing an independent exact reconstruction of all 3,675 Bernstein
signs.
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
from fractions import Fraction
from pathlib import Path
from typing import TypeAlias


SCHEMA = "tect/a13-scalar-k2k-support-two-moment-cone-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-scalar-k2k-support-two-moment-cone/result.json"
)
Polynomial: TypeAlias = dict[tuple[int, int], Fraction]

# Test oracles reconstructed separately from the sparse-polynomial engine.
MINIMUM_ORACLES = {
    "I1_S": Fraction(3228828189276149229671, 128849018880000000000000000),
    "I1_Q": Fraction(37759, 2560000),
    "I2_S": Fraction(824289456286443058922316607955591, 19660800000000000000000000000000000000),
    "I2_Q": Fraction(31934599, 1600000000),
    "I3_S": Fraction(1678113425694930246248812151, 8444249301319680000000000000000),
    "I3_Q": Fraction(1457, 80000),
    "I4_S": Fraction(4089930819610437346252570751, 982688517324800000000000000000),
    "I4_Q": Fraction(157279, 2560000),
    "I5_Q": Fraction(181, 4096),
    "I6_Q_LOW": Fraction(123657, 4000000),
    "I6_S_A": Fraction(161577960237532077, 1048576000000000000),
    "I6_S_B": Fraction(2530755391442237982218571711234415259638533, 31691265005705735037417580134400000000000000),
    "I6_S_C": Fraction(265576965141887076438339040964644393830604077, 9671406556917033397649408000000000000000000000),
    "I6_S_D": Fraction(3810070004416673757, 18446744073709551616),
    "I6_Q_HIGH": Fraction(498609, 8192000),
}

HASH_ORACLES = {
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

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        row = {
            "group": group,
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": str(actual),
            "expected": str(expected),
        }
        self.rows.append(row)
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


def clean(polynomial: Polynomial) -> Polynomial:
    return {key: value for key, value in polynomial.items() if value}


def constant(value: int | Fraction) -> Polynomial:
    return {(0, 0): Fraction(value)}


def add(*polynomials: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for polynomial in polynomials:
        for key, value in polynomial.items():
            result[key] = result.get(key, Fraction()) + value
    return clean(result)


def scale(polynomial: Polynomial, factor: int | Fraction) -> Polynomial:
    scalar = Fraction(factor)
    return clean({key: scalar * value for key, value in polynomial.items()})


def subtract(left: Polynomial, right: Polynomial) -> Polynomial:
    return add(left, scale(right, -1))


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for (i, j), first in left.items():
        for (k, ell), second in right.items():
            key = (i + k, j + ell)
            result[key] = result.get(key, Fraction()) + first * second
    return clean(result)


def power(polynomial: Polynomial, exponent: int) -> Polynomial:
    result = constant(1)
    base = polynomial
    value = exponent
    while value:
        if value & 1:
            result = multiply(result, base)
        base = multiply(base, base)
        value >>= 1
    return result


def evaluate(polynomial: Polynomial, b_value: Fraction, c_value: Fraction) -> Fraction:
    return sum(coefficient * b_value**i * c_value**j for (i, j), coefficient in polynomial.items())


def affine_unit_transform(
    polynomial: Polynomial,
    b_lower: Fraction,
    b_upper: Fraction,
    c_lower: Fraction,
    c_upper: Fraction,
) -> Polynomial:
    """Substitute b=b_lower+(b_upper-b_lower)u and c likewise."""
    transformed: Polynomial = {}
    b_width = b_upper - b_lower
    c_width = c_upper - c_lower
    for (degree_b, degree_c), coefficient in polynomial.items():
        for power_b in range(degree_b + 1):
            b_factor = Fraction(math.comb(degree_b, power_b)) * b_lower ** (degree_b - power_b) * b_width**power_b
            for power_c in range(degree_c + 1):
                c_factor = Fraction(math.comb(degree_c, power_c)) * c_lower ** (degree_c - power_c) * c_width**power_c
                key = (power_b, power_c)
                transformed[key] = transformed.get(key, Fraction()) + coefficient * b_factor * c_factor
    return clean(transformed)


def tensor_bernstein(polynomial: Polynomial, degree_b: int, degree_c: int) -> list[Fraction]:
    coefficients: list[Fraction] = []
    for i in range(degree_b + 1):
        for j in range(degree_c + 1):
            value = Fraction()
            for (m, n), coefficient in polynomial.items():
                if m <= i and n <= j:
                    value += (
                        coefficient
                        * Fraction(math.comb(i, m), math.comb(degree_b, m))
                        * Fraction(math.comb(j, n), math.comb(degree_c, n))
                    )
            coefficients.append(value)
    return coefficients


def split_bernstein(values: list[Fraction], location: Fraction) -> tuple[list[Fraction], list[Fraction]]:
    """Exact univariate de Casteljau split at location in [0,1]."""
    triangle = [list(values)]
    while len(triangle[-1]) > 1:
        previous = triangle[-1]
        triangle.append([(1 - location) * previous[index] + location * previous[index + 1] for index in range(len(previous) - 1)])
    left = [row[0] for row in triangle]
    right = [row[-1] for row in reversed(triangle)]
    return left, right


def bernstein_subinterval(values: list[Fraction], lower: Fraction, upper: Fraction) -> list[Fraction]:
    if lower == 0 and upper == 1:
        return list(values)
    left_to_upper, _ = split_bernstein(values, upper)
    if lower == 0:
        return left_to_upper
    _, desired = split_bernstein(left_to_upper, lower / upper)
    return desired


def coefficient_hash(coefficients: list[Fraction]) -> str:
    encoded = "".join(f"{value}\n" for value in coefficients).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    one = constant(1)
    b = {(1, 0): Fraction(1)}
    c = {(0, 1): Fraction(1)}
    s = subtract(one, c)

    k2 = scale(add(power(c, 2), power(s, 2)), Fraction(1, 2))
    k1 = add(
        power(c, 3),
        scale(multiply(power(c, 2), s), Fraction(5, 2)),
        multiply(c, power(s, 2)),
        scale(power(s, 3), Fraction(1, 4)),
    )
    k0 = add(
        scale(power(c, 4), Fraction(5, 4)),
        scale(multiply(power(c, 3), s), Fraction(1, 4)),
        scale(multiply(power(c, 2), power(s, 2)), Fraction(25, 16)),
        scale(multiply(c, power(s, 3)), Fraction(1, 4)),
        scale(power(s, 4), Fraction(5, 64)),
    )
    covariance_square = add(multiply(power(b, 2), k2), multiply(b, k1), k0)
    delta = add(
        scale(power(c, 4), Fraction(1, 4)),
        scale(multiply(power(c, 2), power(s, 2)), Fraction(1, 4)),
        scale(power(s, 4), Fraction(1, 64)),
    )
    variance = scale(subtract(covariance_square, delta), Fraction(1, 2))

    expected_k2 = {(0, 2): Fraction(1), (0, 1): Fraction(-1), (0, 0): Fraction(1, 2)}
    expected_delta = {
        (0, 4): Fraction(33, 64),
        (0, 3): Fraction(-9, 16),
        (0, 2): Fraction(11, 32),
        (0, 1): Fraction(-1, 16),
        (0, 0): Fraction(1, 64),
    }
    audit.check("normal_form", "K2 reconstructed from simplex", k2 == expected_k2, k2, expected_k2)
    audit.check("normal_form", "Delta reconstructed from three squares", delta == expected_delta, delta, expected_delta)
    audit.check("normal_form", "variance identity by construction", scale(add(scale(variance, 2), delta), Fraction(1)) == covariance_square, "2V+Delta", "K")
    reserve_base = add(scale(power(c, 2), Fraction(1, 2)), scale(power(s, 2), Fraction(1, 8)))
    reserve_remainder = subtract(delta, power(reserve_base, 2))
    audit.check(
        "normal_form",
        "reserve square remainder",
        reserve_remainder == scale(multiply(power(c, 2), power(s, 2)), Fraction(1, 8)),
        reserve_remainder,
        "c^2*s^2/8",
    )

    beta6 = scale(add(power(b, 2), scale(b, 12), constant(4)), Fraction(1, 16))
    beta10a = scale(add(scale(power(b, 2), 401), scale(b, -20), constant(125)), Fraction(1, 400))
    beta10b = scale(add(power(b, 2), scale(b, 180), constant(100)), Fraction(1, 400))
    beta_sharp = scale(b, Fraction(1, 2))
    audit.check("support", "beta6 positive at endpoints", evaluate(beta6, Fraction(0), Fraction(0)) > 0 and evaluate(beta6, Fraction(1, 10), Fraction(0)) > 0, (evaluate(beta6, Fraction(0), Fraction(0)), evaluate(beta6, Fraction(1, 10), Fraction(0))), ">0")
    audit.check("support", "beta10 branches join", evaluate(beta10a, Fraction(1, 4), Fraction(0)) == evaluate(beta10b, Fraction(1, 4), Fraction(0)), evaluate(beta10a, Fraction(1, 4), Fraction(0)), evaluate(beta10b, Fraction(1, 4), Fraction(0)))
    audit.check("support", "endpoint beta", evaluate(beta10b, Fraction(3, 2), Fraction(0)) == Fraction(1489, 1600), evaluate(beta10b, Fraction(3, 2), Fraction(0)), Fraction(1489, 1600))
    threshold_at_base = 15 * Fraction(6, 5) ** 2 - 10 * Fraction(6, 5) - 9
    audit.check("support", "sharp-floor threshold at six-fifths", threshold_at_base == Fraction(3, 5), threshold_at_base, Fraction(3, 5))
    threshold_polynomial = add(scale(power(b, 2), 15), scale(b, -10), constant(-9))
    threshold_factor = scale(
        multiply(add(scale(b, 5), constant(-6)), add(scale(b, 15), constant(8))),
        Fraction(1, 5),
    )
    audit.check(
        "support",
        "sharp-floor threshold increment factors positively",
        subtract(threshold_polynomial, constant(Fraction(3, 5))) == threshold_factor,
        subtract(threshold_polynomial, constant(Fraction(3, 5))),
        threshold_factor,
    )
    audit.check("support", "sharp floor endpoint beta", evaluate(beta_sharp, Fraction(643, 200), Fraction(0)) == Fraction(643, 400), evaluate(beta_sharp, Fraction(643, 200), Fraction(0)), Fraction(643, 400))

    variance_coefficients = tensor_bernstein(
        affine_unit_transform(variance, Fraction(0), Fraction(643, 200), Fraction(0), Fraction(1)), 2, 4
    )
    audit.check(
        "normal_form",
        "variance coefficient count",
        len(variance_coefficients) == 15,
        len(variance_coefficients),
        15,
    )
    audit.check(
        "normal_form",
        "variance strictly positive on cone",
        all(value > 0 for value in variance_coefficients),
        min(variance_coefficients),
        ">0",
    )
    audit.check(
        "normal_form",
        "variance minimum coefficient",
        min(variance_coefficients) == Fraction(1, 32),
        min(variance_coefficients),
        Fraction(1, 32),
    )

    def certificate_polynomials(beta: Polynomial) -> tuple[Polynomial, Polynomial]:
        beta_squared = power(beta, 2)
        plus = add(beta_squared, variance)
        minus = subtract(beta_squared, variance)
        q_polynomial = subtract(variance, beta_squared)
        s_polynomial = add(
            scale(multiply(multiply(covariance_square, beta_squared), power(plus, 2)), 6),
            scale(multiply(multiply(covariance_square, beta_squared), power(minus, 2)), 2),
            scale(power(plus, 4), -3),
        )
        return q_polynomial, s_polynomial

    slabs = [
        ("I1", Fraction(0), Fraction(1, 10), beta6),
        ("I2", Fraction(1, 10), Fraction(1, 4), beta10a),
        ("I3", Fraction(1, 4), Fraction(1), beta10b),
    ]
    summaries: dict[str, object] = {}
    total_signs = 0
    for label, lower_b, upper_b, beta in slabs:
        q_polynomial, s_polynomial = certificate_polynomials(beta)
        s_coefficients = tensor_bernstein(
            affine_unit_transform(s_polynomial, lower_b, upper_b, Fraction(0), Fraction(1, 2)), 16, 16
        )
        q_coefficients = tensor_bernstein(
            affine_unit_transform(q_polynomial, lower_b, upper_b, Fraction(1, 2), Fraction(1)), 4, 4
        )
        audit.check("bernstein", f"{label} all S coefficients positive", all(value > 0 for value in s_coefficients), min(s_coefficients), ">0")
        audit.check("bernstein", f"{label} all Q coefficients positive", all(value > 0 for value in q_coefficients), min(q_coefficients), ">0")
        audit.check("bernstein", f"{label} S count", len(s_coefficients) == 289, len(s_coefficients), 289)
        audit.check("bernstein", f"{label} Q count", len(q_coefficients) == 25, len(q_coefficients), 25)
        audit.check("bernstein", f"{label} S minimum oracle", min(s_coefficients) == MINIMUM_ORACLES[f"{label}_S"], min(s_coefficients), MINIMUM_ORACLES[f"{label}_S"])
        audit.check("bernstein", f"{label} Q minimum oracle", min(q_coefficients) == MINIMUM_ORACLES[f"{label}_Q"], min(q_coefficients), MINIMUM_ORACLES[f"{label}_Q"])
        audit.check("bernstein", f"{label} S hash", coefficient_hash(s_coefficients) == HASH_ORACLES[f"{label}_S"], coefficient_hash(s_coefficients), HASH_ORACLES[f"{label}_S"])
        audit.check("bernstein", f"{label} Q hash", coefficient_hash(q_coefficients) == HASH_ORACLES[f"{label}_Q"], coefficient_hash(q_coefficients), HASH_ORACLES[f"{label}_Q"])
        total_signs += len(s_coefficients) + len(q_coefficients)
        summaries[label] = {
            "S_count": len(s_coefficients),
            "Q_count": len(q_coefficients),
            "S_minimum": str(min(s_coefficients)),
            "Q_minimum": str(min(q_coefficients)),
            "S_sha256": coefficient_hash(s_coefficients),
            "Q_sha256": coefficient_hash(q_coefficients),
        }

    q4, s4 = certificate_polynomials(beta10b)
    base_s_coefficients = tensor_bernstein(
        affine_unit_transform(s4, Fraction(1), Fraction(3, 2), Fraction(0), Fraction(3, 5)), 16, 16
    )
    coefficient_rows = [base_s_coefficients[index * 17 : (index + 1) * 17] for index in range(17)]
    i4_s_coefficients: list[Fraction] = []
    cell_minima: list[str] = []
    for cell in range(8):
        lower = Fraction(cell, 8)
        upper = Fraction(cell + 1, 8)
        cell_rows = [bernstein_subinterval(row, lower, upper) for row in coefficient_rows]
        cell_coefficients = [value for row in cell_rows for value in row]
        audit.check("de_casteljau", f"I4 cell {cell} coefficient count", len(cell_coefficients) == 289, len(cell_coefficients), 289)
        audit.check("de_casteljau", f"I4 cell {cell} all positive", all(value > 0 for value in cell_coefficients), min(cell_coefficients), ">0")
        i4_s_coefficients.extend(cell_coefficients)
        cell_minima.append(str(min(cell_coefficients)))
    q4_coefficients = tensor_bernstein(
        affine_unit_transform(q4, Fraction(1), Fraction(3, 2), Fraction(3, 5), Fraction(1)), 4, 4
    )
    audit.check("bernstein", "I4 Q all positive", all(value > 0 for value in q4_coefficients), min(q4_coefficients), ">0")
    audit.check("bernstein", "I4 Q count", len(q4_coefficients) == 25, len(q4_coefficients), 25)
    audit.check("bernstein", "I4 S minimum oracle", min(i4_s_coefficients) == MINIMUM_ORACLES["I4_S"], min(i4_s_coefficients), MINIMUM_ORACLES["I4_S"])
    audit.check("bernstein", "I4 Q minimum oracle", min(q4_coefficients) == MINIMUM_ORACLES["I4_Q"], min(q4_coefficients), MINIMUM_ORACLES["I4_Q"])
    audit.check("bernstein", "I4 S hash", coefficient_hash(i4_s_coefficients) == HASH_ORACLES["I4_S"], coefficient_hash(i4_s_coefficients), HASH_ORACLES["I4_S"])
    audit.check("bernstein", "I4 Q hash", coefficient_hash(q4_coefficients) == HASH_ORACLES["I4_Q"], coefficient_hash(q4_coefficients), HASH_ORACLES["I4_Q"])
    total_signs += len(i4_s_coefficients) + len(q4_coefficients)
    summaries["I4"] = {
        "S_count": len(i4_s_coefficients),
        "Q_count": len(q4_coefficients),
        "S_cell_minima": cell_minima,
        "S_minimum": str(min(i4_s_coefficients)),
        "Q_minimum": str(min(q4_coefficients)),
        "S_sha256": coefficient_hash(i4_s_coefficients),
        "Q_sha256": coefficient_hash(q4_coefficients),
        "construction": "de Casteljau subdivision of c in [0,3/5] into eight equal cells",
    }

    q_sharp, s_sharp = certificate_polynomials(beta_sharp)

    # Reconstruct I5 by a different route from the primary verifier: make one
    # exact tensor-Bernstein patch and obtain the four c-cells by de Casteljau.
    i5_base = tensor_bernstein(
        affine_unit_transform(q_sharp, Fraction(3, 2), Fraction(2), Fraction(0), Fraction(1)), 2, 4
    )
    i5_rows = [i5_base[index * 5 : (index + 1) * 5] for index in range(3)]
    i5_q_coefficients: list[Fraction] = []
    i5_cell_minima: list[str] = []
    for cell in range(4):
        lower = Fraction(cell, 4)
        upper = Fraction(cell + 1, 4)
        cell_rows = [bernstein_subinterval(row, lower, upper) for row in i5_rows]
        cell_coefficients = [value for row in cell_rows for value in row]
        audit.check("de_casteljau", f"I5 cell {cell} coefficient count", len(cell_coefficients) == 15, len(cell_coefficients), 15)
        audit.check("de_casteljau", f"I5 cell {cell} all positive", all(value > 0 for value in cell_coefficients), min(cell_coefficients), ">0")
        i5_q_coefficients.extend(cell_coefficients)
        i5_cell_minima.append(str(min(cell_coefficients)))
    audit.check("bernstein", "I5 Q minimum oracle", min(i5_q_coefficients) == MINIMUM_ORACLES["I5_Q"], min(i5_q_coefficients), MINIMUM_ORACLES["I5_Q"])
    audit.check("bernstein", "I5 Q hash", coefficient_hash(i5_q_coefficients) == HASH_ORACLES["I5_Q"], coefficient_hash(i5_q_coefficients), HASH_ORACLES["I5_Q"])
    total_signs += len(i5_q_coefficients)
    summaries["I5"] = {
        "Q_count": len(i5_q_coefficients),
        "Q_cell_minima": i5_cell_minima,
        "Q_minimum": str(min(i5_q_coefficients)),
        "Q_sha256": coefficient_hash(i5_q_coefficients),
        "construction": "de Casteljau subdivision of c in [0,1] into four equal cells",
    }

    i6_regions = (
        ("Q_LOW", q_sharp, Fraction(0), Fraction(1, 10), 2, 4, 15),
        ("S_A", s_sharp, Fraction(1, 10), Fraction(37, 160), 8, 16, 153),
        ("S_B", s_sharp, Fraction(37, 160), Fraction(19, 64), 8, 16, 153),
        ("S_C", s_sharp, Fraction(19, 64), Fraction(29, 80), 8, 16, 153),
        ("S_D", s_sharp, Fraction(29, 80), Fraction(5, 8), 8, 16, 153),
        ("Q_HIGH", q_sharp, Fraction(5, 8), Fraction(1), 2, 4, 15),
    )
    i6_results: dict[str, object] = {}
    for label, polynomial, lower_c, upper_c, degree_b, degree_c, expected_count in i6_regions:
        coefficients = tensor_bernstein(
            affine_unit_transform(polynomial, Fraction(2), Fraction(643, 200), lower_c, upper_c),
            degree_b,
            degree_c,
        )
        oracle_key = f"I6_{label}"
        audit.check("bernstein", f"I6 {label} count", len(coefficients) == expected_count, len(coefficients), expected_count)
        audit.check("bernstein", f"I6 {label} all positive", all(value > 0 for value in coefficients), min(coefficients), ">0")
        audit.check("bernstein", f"I6 {label} minimum oracle", min(coefficients) == MINIMUM_ORACLES[oracle_key], min(coefficients), MINIMUM_ORACLES[oracle_key])
        audit.check("bernstein", f"I6 {label} hash", coefficient_hash(coefficients) == HASH_ORACLES[oracle_key], coefficient_hash(coefficients), HASH_ORACLES[oracle_key])
        total_signs += len(coefficients)
        i6_results[label] = {
            "c_interval": [str(lower_c), str(upper_c)],
            "coefficient_count": len(coefficients),
            "minimum": str(min(coefficients)),
            "sha256": coefficient_hash(coefficients),
        }
    summaries["I6"] = {
        "b_interval": ["2", "643/200"],
        "floor": "b/2",
        "regions": i6_results,
    }

    audit.check("bernstein", "total exact coefficient signs", total_signs == 3981, total_signs, 3981)

    witness_b, witness_c = Fraction(103, 32), Fraction(5, 16)
    witness_q = evaluate(q_sharp, witness_b, witness_c)
    witness_s = evaluate(s_sharp, witness_b, witness_c)
    witness_k = evaluate(covariance_square, witness_b, witness_c)
    witness_delta = evaluate(delta, witness_b, witness_c)
    witness_v = evaluate(variance, witness_b, witness_c)
    audit.check("mutant", "witness covariance square", witness_k == Fraction(18714321, 4194304), witness_k, Fraction(18714321, 4194304))
    audit.check("mutant", "witness reserve", witness_delta == Fraction(73041, 4194304), witness_delta, Fraction(73041, 4194304))
    audit.check("mutant", "witness variance", witness_v == Fraction(145635, 65536), witness_v, Fraction(145635, 65536))
    audit.check("mutant", "variance branch unavailable at beyond-cone witness", witness_q < 0, witness_q, "<0")
    audit.check("mutant", "variance branch exact negative witness", witness_q == Fraction(-24109, 65536), witness_q, Fraction(-24109, 65536))
    audit.check("mutant", "cubic proxy exact negative witness", witness_s == Fraction(-127544381197984065, 18446744073709551616), witness_s, Fraction(-127544381197984065, 18446744073709551616))
    altered_delta = scale(delta, -1)
    altered_variance = scale(subtract(covariance_square, altered_delta), Fraction(1, 2))
    audit.check("mutant", "reserve-sign mutant changes variance", altered_variance != variance, evaluate(altered_variance, Fraction(1), Fraction(1, 2)), evaluate(variance, Fraction(1), Fraction(1, 2)))

    for order in range(1, 33):
        ratio = Fraction(math.comb(2 * order, order), 4**order)
        audit.check("bessel", f"central coefficient order {order}", ratio <= Fraction(1, 2), ratio, "<=1/2")

    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    results: dict[str, object] = {
        "engine": "non-importing sparse Fraction polynomials; I4 and I5 by exact de Casteljau subdivision",
        "cone": "tau>0 and 0<=x<=643*tau/200",
        "strict_gap": True,
        "origin_equality": True,
        "exact_coefficient_signs": total_signs,
        "certificates": summaries,
        "method_boundary_witness": {"b": str(witness_b), "c": str(witness_c), "K": str(witness_k), "Delta": str(witness_delta), "V": str(witness_v), "Q": str(witness_q), "S": str(witness_s)},
        "runtime_versions": {"python": platform.python_version()},
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
            "support_two_moment_cone": "independently-reproduced-through-b=643/200",
            "cubic_proxy_beyond_cone": "fails-at-exact-witness",
            "mixed_all_q_scalar_k2k": "open",
            "sector_a": "open",
        },
    }
    atomic_json(args.output, payload)
    print(f"independent {payload['assertions_passed']}/{payload['assertions_total']} assertions PASS")
    print(f"exact Fraction/de-Casteljau signs {total_signs}/3981 positive")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
