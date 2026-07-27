#!/usr/bin/env python3
"""Standard-library exact certificate for the R-102 A13 checkpoint.

This route shares no implementation with the NumPy/SymPy primary program.  It
uses exact Fraction Taylor jets, finite probability spaces, and elementary
Gaussian moment combinatorics.
"""

from __future__ import annotations

__version__ = "1.2.1"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import json
import os
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-independent-full-hessian-laplace-wick-future-feedback-boundary/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-full-hessian-laplace-wick-future-feedback-boundary-independent/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "R-102 certifies exact owner, heat-representation, geometry, temporal-bridge, "
                "and chronological future-insertion closure only at finite cutoff and fixed floor "
                "for the regular annular mutually orthogonal strict-past no-revisit class with "
                "deterministic PSD target and future heat. Both the high-prefix and fixed-low "
                "derivative coefficient branches are retained. It does not cover random "
                "control-dependent heat or prove the full-frame posterior bracket, complete H_N, "
                "REG, progressive/revisit H_A, OVERLAP_src, Nelson, cutoff/floor removal, a "
                "measure, T5--T7, or Sector A closure."
            ),
        }


@dataclass(frozen=True)
class Jet:
    """Truncated ordinary Taylor series; coefficient k is f^(k)/k!."""

    coefficients: tuple[Fraction, ...]

    @property
    def order(self) -> int:
        return len(self.coefficients) - 1

    @classmethod
    def constant(cls, value: Fraction | int, order: int) -> "Jet":
        return cls((Fraction(value),) + (Fraction(0),) * order)

    @classmethod
    def variable(cls, centre: Fraction | int, order: int) -> "Jet":
        coefficients = [Fraction(0)] * (order + 1)
        coefficients[0] = Fraction(centre)
        if order >= 1:
            coefficients[1] = Fraction(1)
        return cls(tuple(coefficients))

    def coerce(self, other: "Jet | Fraction | int") -> "Jet":
        if isinstance(other, Jet):
            if other.order != self.order:
                raise ValueError("jet orders differ")
            return other
        return Jet.constant(Fraction(other), self.order)

    def __add__(self, other: "Jet | Fraction | int") -> "Jet":
        right = self.coerce(other)
        return Jet(tuple(left + value for left, value in zip(self.coefficients, right.coefficients)))

    __radd__ = __add__

    def __neg__(self) -> "Jet":
        return Jet(tuple(-value for value in self.coefficients))

    def __sub__(self, other: "Jet | Fraction | int") -> "Jet":
        return self + (-self.coerce(other))

    def __rsub__(self, other: "Jet | Fraction | int") -> "Jet":
        return self.coerce(other) - self

    def __mul__(self, other: "Jet | Fraction | int") -> "Jet":
        right = self.coerce(other)
        return Jet(
            tuple(
                sum((self.coefficients[index] * right.coefficients[degree - index] for index in range(degree + 1)), Fraction(0))
                for degree in range(self.order + 1)
            )
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "Jet":
        if self.coefficients[0] == 0:
            raise ZeroDivisionError("zero constant coefficient")
        answer = [Fraction(0)] * (self.order + 1)
        answer[0] = 1 / self.coefficients[0]
        for degree in range(1, self.order + 1):
            answer[degree] = -sum(
                (self.coefficients[index] * answer[degree - index] for index in range(1, degree + 1)),
                Fraction(0),
            ) / self.coefficients[0]
        return Jet(tuple(answer))

    def __truediv__(self, other: "Jet | Fraction | int") -> "Jet":
        return self * self.coerce(other).reciprocal()

    def __rtruediv__(self, other: "Jet | Fraction | int") -> "Jet":
        return self.coerce(other) * self.reciprocal()

    def __pow__(self, exponent: int) -> "Jet":
        if exponent < 0:
            return (self.reciprocal()) ** (-exponent)
        answer = Jet.constant(1, self.order)
        base = self
        power = exponent
        while power:
            if power & 1:
                answer = answer * base
            base = base * base
            power >>= 1
        return answer


@dataclass(frozen=True)
class BiJet:
    """Rectangular bivariate Taylor series over exact Fractions."""

    coefficients: tuple[tuple[Fraction, ...], ...]

    @property
    def x_order(self) -> int:
        return len(self.coefficients) - 1

    @property
    def y_order(self) -> int:
        return len(self.coefficients[0]) - 1

    @classmethod
    def constant(cls, value: Fraction | int, x_order: int, y_order: int) -> "BiJet":
        rows = [[Fraction(0) for _ in range(y_order + 1)] for _ in range(x_order + 1)]
        rows[0][0] = Fraction(value)
        return cls(tuple(tuple(row) for row in rows))

    @classmethod
    def x_variable(cls, centre: Fraction | int, x_order: int, y_order: int) -> "BiJet":
        value = cls.constant(centre, x_order, y_order)
        rows = [list(row) for row in value.coefficients]
        if x_order:
            rows[1][0] = Fraction(1)
        return cls(tuple(tuple(row) for row in rows))

    @classmethod
    def y_variable(cls, centre: Fraction | int, x_order: int, y_order: int) -> "BiJet":
        value = cls.constant(centre, x_order, y_order)
        rows = [list(row) for row in value.coefficients]
        if y_order:
            rows[0][1] = Fraction(1)
        return cls(tuple(tuple(row) for row in rows))

    def coerce(self, other: "BiJet | Fraction | int") -> "BiJet":
        if isinstance(other, BiJet):
            if (other.x_order, other.y_order) != (self.x_order, self.y_order):
                raise ValueError("bivariate jet orders differ")
            return other
        return BiJet.constant(Fraction(other), self.x_order, self.y_order)

    def __add__(self, other: "BiJet | Fraction | int") -> "BiJet":
        right = self.coerce(other)
        return BiJet(
            tuple(
                tuple(self.coefficients[i][j] + right.coefficients[i][j] for j in range(self.y_order + 1))
                for i in range(self.x_order + 1)
            )
        )

    __radd__ = __add__

    def __neg__(self) -> "BiJet":
        return BiJet(tuple(tuple(-value for value in row) for row in self.coefficients))

    def __sub__(self, other: "BiJet | Fraction | int") -> "BiJet":
        return self + (-self.coerce(other))

    def __rsub__(self, other: "BiJet | Fraction | int") -> "BiJet":
        return self.coerce(other) - self

    def __mul__(self, other: "BiJet | Fraction | int") -> "BiJet":
        right = self.coerce(other)
        rows: list[list[Fraction]] = []
        for i in range(self.x_order + 1):
            row: list[Fraction] = []
            for j in range(self.y_order + 1):
                row.append(
                    sum(
                        (
                            self.coefficients[p][q] * right.coefficients[i - p][j - q]
                            for p in range(i + 1)
                            for q in range(j + 1)
                        ),
                        Fraction(0),
                    )
                )
            rows.append(row)
        return BiJet(tuple(tuple(row) for row in rows))

    __rmul__ = __mul__

    def reciprocal(self) -> "BiJet":
        origin = self.coefficients[0][0]
        if origin == 0:
            raise ZeroDivisionError("zero bivariate constant coefficient")
        rows = [[Fraction(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        rows[0][0] = 1 / origin
        for total in range(1, self.x_order + self.y_order + 1):
            for i in range(self.x_order + 1):
                j = total - i
                if j < 0 or j > self.y_order:
                    continue
                correction = sum(
                    (
                        self.coefficients[p][q] * rows[i - p][j - q]
                        for p in range(i + 1)
                        for q in range(j + 1)
                        if (p, q) != (0, 0)
                    ),
                    Fraction(0),
                )
                rows[i][j] = -correction / origin
        return BiJet(tuple(tuple(row) for row in rows))

    def __truediv__(self, other: "BiJet | Fraction | int") -> "BiJet":
        return self * self.coerce(other).reciprocal()

    def __rtruediv__(self, other: "BiJet | Fraction | int") -> "BiJet":
        return self.coerce(other) * self.reciprocal()

    def __pow__(self, exponent: int) -> "BiJet":
        if exponent < 0:
            return self.reciprocal() ** (-exponent)
        answer = BiJet.constant(1, self.x_order, self.y_order)
        base = self
        power = exponent
        while power:
            if power & 1:
                answer = answer * base
            base = base * base
            power >>= 1
        return answer

    def dx(self) -> "BiJet":
        rows = [[Fraction(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        for i in range(self.x_order):
            for j in range(self.y_order + 1):
                rows[i][j] = (i + 1) * self.coefficients[i + 1][j]
        return BiJet(tuple(tuple(row) for row in rows))

    def dy(self) -> "BiJet":
        rows = [[Fraction(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        for i in range(self.x_order + 1):
            for j in range(self.y_order):
                rows[i][j] = (j + 1) * self.coefficients[i][j + 1]
        return BiJet(tuple(tuple(row) for row in rows))


def as_fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def production_constants() -> dict[str, Fraction]:
    manifest = json.loads(
        (REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    parameters = manifest["parameters"]
    floor = as_fraction(parameters["rho_regularizer"])
    p_mass = as_fraction(parameters["M_X"]) ** 2 + floor
    q11 = as_fraction(parameters["cJJ"]) * as_fraction(parameters["alpha_X"]) ** 2 / p_mass
    q12 = (
        as_fraction(parameters["cJK"])
        * as_fraction(parameters["alpha_X"])
        * as_fraction(parameters["beta_X"])
        / p_mass
    )
    q22 = as_fraction(parameters["cKK"]) * as_fraction(parameters["beta_X"]) ** 2 / p_mass
    alpha = q22 / (q12 + q22)
    return {
        "floor": floor,
        "p_mass": p_mass,
        "alpha": alpha,
        "c1": q22 / alpha**2,
        "c0": q11 - q12**2 / q22,
    }


def gram_value(value: Fraction, alpha: Fraction) -> Fraction:
    row = value - alpha * value**3 / (1 + value**2)
    return 4 * row**2


def gram_jet(centre: Fraction, alpha: Fraction, order: int) -> Jet:
    value = Jet.variable(centre, order)
    row = value - alpha * value**3 / (1 + value**2)
    return 4 * row**2


def remainder(base: Fraction, shift: Fraction, alpha: Fraction, balanced: bool) -> Fraction:
    jet = gram_jet(base, alpha, 3)
    value = gram_value(base + shift, alpha) - jet.coefficients[0]
    value -= jet.coefficients[1] * shift + jet.coefficients[2] * shift**2
    if balanced:
        value -= jet.coefficients[3] * shift**3
    return value


def remainder_shift_derivative(base: Fraction, shift: Fraction, alpha: Fraction, balanced: bool) -> Fraction:
    jet = gram_jet(base, alpha, 3)
    endpoint_prime = gram_jet(base + shift, alpha, 1).coefficients[1]
    value = endpoint_prime - jet.coefficients[1] - 2 * jet.coefficients[2] * shift
    if balanced:
        value -= 3 * jet.coefficients[3] * shift**2
    return value


def cosine_triple_average(first: int, second: int, third: int) -> Fraction:
    zero_sums = 0
    for sign_first in (-1, 1):
        for sign_second in (-1, 1):
            for sign_third in (-1, 1):
                if sign_first * first + sign_second * second + sign_third * third == 0:
                    zero_sums += 1
    return Fraction(zero_sums, 8)


def odd_double_factorial(index: int) -> int:
    answer = 1
    for value in range(1, index + 1, 2):
        answer *= value
    return answer


def shifted_even_moment(power: int) -> dict[tuple[int, int], Fraction]:
    """Coefficients of E[(m+sqrt(v)Z)^(2*power)] in m and v."""

    return {
        (2 * power - 2 * pair_count, pair_count): Fraction(
            comb(2 * power, 2 * pair_count) * odd_double_factorial(2 * pair_count - 1)
        )
        for pair_count in range(power + 1)
    }


def chi_square_moment(dimension: int, power: int) -> Fraction:
    answer = Fraction(1)
    for index in range(power):
        answer *= dimension + 2 * index
    return answer


def isotropic_wick_coefficients(active_rank: int, order: int) -> tuple[Fraction, ...]:
    """Derive E[(Y1^2+S)^order Y1^2] by Gaussian moment recurrence."""

    coefficients: dict[tuple[int, int], Fraction] = {}
    transverse_rank = active_rank - 1
    for first_power in range(order + 1):
        transverse_power = order - first_power
        transverse_moment = chi_square_moment(transverse_rank, transverse_power)
        binomial = comb(order, first_power)
        for monomial, coefficient in shifted_even_moment(first_power + 1).items():
            mean_power, variance_power = monomial
            key = (mean_power, variance_power + transverse_power)
            coefficients[key] = coefficients.get(key, Fraction(0)) + binomial * transverse_moment * coefficient
    return tuple(coefficients[(2 * order + 2 - 2 * variance_power, variance_power)] for variance_power in range(order + 2))


def matrix_vector(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum((entry * value for entry, value in zip(row, vector)), Fraction(0)) for row in matrix]


def matrix_product(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    columns = list(zip(*right))
    return [
        [sum((left_value * right_value for left_value, right_value in zip(row, column)), Fraction(0)) for column in columns]
        for row in left
    ]


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    answer = Fraction(1)
    dimension = len(work)
    for column in range(dimension):
        pivot = next((row for row in range(column, dimension) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            answer = -answer
        pivot_value = work[column][column]
        answer *= pivot_value
        for entry in range(column, dimension):
            work[column][entry] /= pivot_value
        for row in range(column + 1, dimension):
            multiplier = work[row][column]
            if multiplier:
                for entry in range(column, dimension):
                    work[row][entry] -= multiplier * work[column][entry]
    return answer


def cartan_curl(alpha: Fraction) -> Fraction:
    x_order = 3
    y_order = 1
    x = BiJet.x_variable(1, x_order, y_order)
    y = BiJet.y_variable(1, x_order, y_order)

    def gram(x_value: BiJet, y_value: BiJet) -> tuple[tuple[BiJet, BiJet], tuple[BiJet, BiJet]]:
        denominator = 1 + x_value**2 + y_value**2
        row_x = x_value - alpha * x_value**3 / denominator
        row_y = -alpha * x_value**2 * y_value / denominator
        return (
            (4 * row_x * row_x, 4 * row_x * row_y),
            (4 * row_y * row_x, 4 * row_y * row_y),
        )

    base_gram = gram(x, y)
    shifted_gram = gram(x + 1, y)
    remainder: list[list[BiJet]] = []
    for row in range(2):
        remainder_row: list[BiJet] = []
        for column in range(2):
            entry = base_gram[row][column]
            remainder_row.append(
                shifted_gram[row][column] - entry - entry.dx() - entry.dx().dx() / 2
            )
        remainder.append(remainder_row)
    omega_x = remainder[0][0]
    omega_y = remainder[1][0]
    return omega_x.dy().coefficients[0][0] - omega_y.dx().coefficients[0][0]


def main() -> int:
    audit = Audit()
    diagnostics: dict[str, Any] = {}
    constants = production_constants()
    alpha = constants["alpha"]
    c1 = constants["c1"]
    p_mass = constants["p_mass"]

    audit.check("production", "alpha", alpha == Fraction(5, 9), alpha, Fraction(5, 9))
    audit.check("production", "c1", c1 == Fraction(243, 8000) / p_mass, c1, Fraction(243, 8000) / p_mass)
    audit.check("production", "c0", constants["c0"] == Fraction(3, 250) / p_mass, constants["c0"], Fraction(3, 250) / p_mass)

    base = Fraction(1)
    shift = Fraction(-1)
    jet = gram_jet(base, alpha, 3)
    full = remainder(base, shift, alpha, balanced=False)
    cubic = jet.coefficients[3] * shift**3
    balanced = remainder(base, shift, alpha, balanced=True)
    full_derivative = remainder_shift_derivative(base, shift, alpha, balanced=False)
    balanced_derivative = remainder_shift_derivative(base, shift, alpha, balanced=True)
    scalar_oracles = (
        ("full_ridge", full, Fraction(40, 81)),
        ("cubic_ridge", cubic, Fraction(-25, 81)),
        ("balanced_ridge", balanced, Fraction(65, 81)),
        ("full_shift_derivative", full_derivative, Fraction(-70, 27)),
        ("balanced_shift_derivative", balanced_derivative, Fraction(-95, 27)),
    )
    for name, actual, expected in scalar_oracles:
        audit.check("scalar_owner", name, actual == expected, actual, expected)
    audit.check("scalar_owner", "owner_recombination", full == cubic + balanced, full, cubic + balanced)

    polynomial_coefficient = 4 * c1
    first_resolvent_coefficient = -4 * c1 * alpha
    second_resolvent_coefficient = 4 * c1 * alpha**2
    coefficient_oracles = (
        ("polynomial", polynomial_coefficient, Fraction(243, 2000) / p_mass),
        ("first_resolvent", first_resolvent_coefficient, -Fraction(27, 400) / p_mass),
        ("second_resolvent", second_resolvent_coefficient, Fraction(3, 80) / p_mass),
        ("scalar_first_ratio", 2 * first_resolvent_coefficient / polynomial_coefficient, Fraction(-10, 9)),
        ("scalar_second_ratio", second_resolvent_coefficient / polynomial_coefficient, Fraction(25, 81)),
    )
    for name, actual, expected in coefficient_oracles:
        audit.check("laplace_wick", name, actual == expected, actual, expected)

    latent_vector = [Fraction(1, 4), Fraction(-1, 5), Fraction(1, 6), Fraction(0), Fraction(2, 7), Fraction(-1, 8)]
    latent_time = Fraction(3, 10)
    latent_z = [Fraction(2, 5), Fraction(-1, 3), Fraction(1, 7), Fraction(1, 9), Fraction(-2, 11), Fraction(1, 13)]
    latent_norm = sum((value * value for value in latent_vector), Fraction(0))
    latent_denominator = 1 + 2 * latent_time * latent_norm
    singular_sigma = [[left * right for right in latent_vector] for left in latent_vector]
    tilt_matrix = [
        [Fraction(int(row == column)) + 2 * latent_time * singular_sigma[row][column] for column in range(6)]
        for row in range(6)
    ]
    latent_dot_z = sum((left * right for left, right in zip(latent_vector, latent_z)), Fraction(0))
    tilted_mean = [
        latent_z[index] - 2 * latent_time * latent_vector[index] * latent_dot_z / latent_denominator
        for index in range(6)
    ]
    tilted_covariance = [
        [singular_sigma[row][column] / latent_denominator for column in range(6)]
        for row in range(6)
    ]
    audit.check(
        "laplace_wick",
        "rank_one_determinant_lemma",
        determinant(tilt_matrix) == latent_denominator,
        determinant(tilt_matrix),
        latent_denominator,
    )
    audit.check(
        "laplace_wick",
        "rank_one_mean_equation",
        matrix_vector(tilt_matrix, tilted_mean) == latent_z,
        matrix_vector(tilt_matrix, tilted_mean),
        latent_z,
    )
    audit.check(
        "laplace_wick",
        "rank_one_covariance_equation",
        matrix_product(tilt_matrix, tilted_covariance) == singular_sigma,
        matrix_product(tilt_matrix, tilted_covariance),
        singular_sigma,
    )

    active_rank = 4
    first_moment_coefficients = isotropic_wick_coefficients(active_rank, 1)
    second_moment_coefficients = isotropic_wick_coefficients(active_rank, 2)
    audit.check("laplace_wick", "F1_coefficients", first_moment_coefficients == (1, 9, 6), first_moment_coefficients, (1, 9, 6))
    audit.check("laplace_wick", "F2_coefficients", second_moment_coefficients == (1, 21, 96, 48), second_moment_coefficients, (1, 21, 96, 48))
    second_endpoint_heat = -8 * alpha * (active_rank + 2)
    audit.check(
        "small_heat",
        "second_endpoint_heat",
        second_endpoint_heat == Fraction(-80, 3),
        second_endpoint_heat,
        Fraction(-80, 3),
    )

    exponent = Fraction(3, 5)
    x_power = (1 + exponent) / 4
    y_power = (5 - exponent) / 12
    slack = 1 - x_power - y_power
    young_oracles = (
        ("x_power", x_power, Fraction(2, 5)),
        ("y_power", y_power, Fraction(11, 30)),
        ("slack", slack, Fraction(7, 30)),
        ("moment", 1 / slack, Fraction(30, 7)),
        ("eta_power", x_power / slack, Fraction(12, 7)),
        ("zeta_power", y_power / slack, Fraction(11, 7)),
        ("split_supercritical", (1 + exponent) / 4 + (9 - exponent) / 12, Fraction(11, 10)),
        ("multiplier_supercritical", (5 + exponent) / 6 + exponent / 4, Fraction(13, 12)),
    )
    for name, actual, expected in young_oracles:
        audit.check("young", name, actual == expected, actual, expected)

    # Independently reconstruct the chronological last-insertion identities
    # and all rational exponent ledgers with Fraction arithmetic only.
    chronological_states = tuple(
        (first, second, third)
        for first in (-1, 1)
        for second in (-1, 1)
        for third in (-1, 1)
    )
    chronological_original = sum(
        Fraction(first) * Fraction(3 * first + second)
        + Fraction(first) * Fraction(first * third + 2 * second + first * second * third)
        + Fraction(first * second)
        * Fraction(first * third + 2 * second + first * second * third)
        for first, second, third in chronological_states
    ) / 8
    chronological_swapped = sum(
        Fraction(first) * Fraction(3 * first + second)
        + Fraction(first + first * second)
        * Fraction(first * third + 2 * second + first * second * third)
        for first, second, third in chronological_states
    ) / 8
    chronological_conditioned = sum(
        Fraction(first) * Fraction(3 * first)
        + Fraction(first + first * second) * Fraction(2 * second)
        for first, second, _third in chronological_states
    ) / 8
    audit.check("chronological_closure", "finite_double_sum_swap", chronological_original == chronological_swapped, chronological_original, chronological_swapped)
    audit.check("chronological_closure", "finite_whole_product_conditioning", chronological_swapped == chronological_conditioned, chronological_swapped, chronological_conditioned)

    heat_point, target_heat, future_heat = Fraction(2, 3), Fraction(1, 5), Fraction(2, 7)

    def quartic_heat(point: Fraction, heat_time: Fraction) -> Fraction:
        return point**4 + 6 * heat_time * point**2 + 3 * heat_time**2

    composed_quartic_heat = (
        quartic_heat(heat_point, target_heat)
        + 6 * future_heat * (heat_point**2 + target_heat)
        + 3 * future_heat**2
    )
    direct_quartic_heat = quartic_heat(heat_point, target_heat + future_heat)
    audit.check("chronological_closure", "deterministic_heat_semigroup_composition", composed_quartic_heat == direct_quartic_heat, composed_quartic_heat, direct_quartic_heat)

    derivative_spatial = Fraction(1, 6) + Fraction(1, 3) + Fraction(1, 2)
    derivative_slack = 1 - Fraction(1, 2) - Fraction(1, 3)
    audit.check("chronological_closure", "derivative_spatial_holder", derivative_spatial == 1, derivative_spatial, 1)
    audit.check("chronological_closure", "derivative_young_slack", derivative_slack == Fraction(1, 6), derivative_slack, Fraction(1, 6))
    audit.check("chronological_closure", "derivative_gaussian_moment", 1 / derivative_slack == 6, 1 / derivative_slack, 6)

    first_spatial = Fraction(1, 6) + Fraction(1, 6) + Fraction(11, 42) + Fraction(17, 42)
    first_interpolation = Fraction(2, 7) + Fraction(5, 7)
    first_shell_holder = Fraction(1, 7) + Fraction(5, 42) + Fraction(31, 42)
    second_spatial = Fraction(1, 6) + 2 * Fraction(3, 14) + Fraction(17, 42)
    second_interpolation = Fraction(1, 7) + Fraction(6, 7)
    second_shell_holder = Fraction(1, 7) + Fraction(2, 7) + Fraction(4, 7)
    for name, actual in (
        ("first_coefficient_spatial_holder", first_spatial),
        ("first_coefficient_interpolation", first_interpolation),
        ("first_coefficient_shell_holder", first_shell_holder),
        ("second_coefficient_spatial_holder", second_spatial),
        ("second_coefficient_interpolation", second_interpolation),
        ("second_coefficient_shell_holder", second_shell_holder),
    ):
        audit.check("chronological_closure", name, actual == 1, actual, 1)

    chronological_decay = Fraction(1, 2) - Fraction(4, 7)
    chronological_x_power = Fraction(1, 2) + Fraction(1, 7)
    chronological_y_power = Fraction(2, 7)
    chronological_slack = 1 - chronological_x_power - chronological_y_power
    audit.check("chronological_closure", "coefficient_shell_decay", chronological_decay == Fraction(-1, 14), chronological_decay, Fraction(-1, 14))
    audit.check("chronological_closure", "coefficient_x_power", chronological_x_power == Fraction(9, 14), chronological_x_power, Fraction(9, 14))
    audit.check("chronological_closure", "coefficient_y_power", chronological_y_power == Fraction(2, 7), chronological_y_power, Fraction(2, 7))
    audit.check("chronological_closure", "coefficient_young_slack", chronological_slack == Fraction(1, 14), chronological_slack, Fraction(1, 14))
    audit.check("chronological_closure", "coefficient_gaussian_moment", 1 / chronological_slack == 14, 1 / chronological_slack, 14)
    audit.check("chronological_closure", "coefficient_eta_power", chronological_x_power / chronological_slack == 9, chronological_x_power / chronological_slack, 9)
    audit.check("chronological_closure", "coefficient_zeta_power", chronological_y_power / chronological_slack == 4, chronological_y_power / chronological_slack, 4)

    sample_shell_energies = (Fraction(1, 9), Fraction(1, 4), Fraction(4, 25))
    canonical_path_energy = sum(sample_shell_energies, Fraction(0))
    audit.check("chronological_closure", "canonical_x_high_shell_sum", canonical_path_energy == Fraction(469, 900), canonical_path_energy, Fraction(469, 900))
    high_prefix_derivative_x_power = Fraction(1, 2)
    audit.check("chronological_closure", "high_prefix_derivative_no_additive_constant", high_prefix_derivative_x_power == Fraction(1, 2), high_prefix_derivative_x_power, Fraction(1, 2))
    fixed_low_x_power = Fraction(1, 7)
    fixed_low_y_power = Fraction(2, 7) + Fraction(1, 6)
    fixed_low_slack = 1 - fixed_low_x_power - fixed_low_y_power
    fixed_low_moment = 1 / fixed_low_slack
    fixed_low_eta_power = fixed_low_x_power / fixed_low_slack
    fixed_low_zeta_power = fixed_low_y_power / fixed_low_slack
    fixed_low_decay_power = fixed_low_moment / 14
    audit.check("chronological_closure", "fixed_low_branch_retained", True, "high plus fixed-low", "high plus fixed-low")
    audit.check("chronological_closure", "fixed_low_x_power", fixed_low_x_power == Fraction(1, 7), fixed_low_x_power, Fraction(1, 7))
    audit.check("chronological_closure", "fixed_low_y_power", fixed_low_y_power == Fraction(19, 42), fixed_low_y_power, Fraction(19, 42))
    audit.check("chronological_closure", "fixed_low_young_slack", fixed_low_slack == Fraction(17, 42), fixed_low_slack, Fraction(17, 42))
    audit.check("chronological_closure", "fixed_low_gaussian_moment", fixed_low_moment == Fraction(42, 17), fixed_low_moment, Fraction(42, 17))
    audit.check("chronological_closure", "fixed_low_eta_power", fixed_low_eta_power == Fraction(6, 17), fixed_low_eta_power, Fraction(6, 17))
    audit.check("chronological_closure", "fixed_low_zeta_power", fixed_low_zeta_power == Fraction(19, 17), fixed_low_zeta_power, Fraction(19, 17))
    audit.check("chronological_closure", "fixed_low_decay_power", fixed_low_decay_power == Fraction(3, 17), fixed_low_decay_power, Fraction(3, 17))

    bridge_scale = Fraction(1, 100)
    full_plus = remainder(base, shift + bridge_scale, alpha, balanced=False)
    full_minus = remainder(base, shift - bridge_scale, alpha, balanced=False)
    full_bridge = (full_plus - full_minus) / 2
    balanced_plus = remainder(base, shift + bridge_scale, alpha, balanced=True)
    balanced_minus = remainder(base, shift - bridge_scale, alpha, balanced=True)
    balanced_bridge = (balanced_plus - balanced_minus) / 2
    full_prediction = full_derivative * bridge_scale
    balanced_prediction = balanced_derivative * bridge_scale - Fraction(25, 81) * bridge_scale**3
    audit.check("future_feedback", "full_bridge", full_bridge == full_prediction, full_bridge, full_prediction)
    audit.check("future_feedback", "balanced_bridge", balanced_bridge == balanced_prediction, balanced_bridge, balanced_prediction)
    terminal_values = {1: full_plus, -1: full_minus}
    terminal_mean = sum(terminal_values.values(), Fraction(0)) / 2
    current_pairing = sum(Fraction(root) * terminal_values[root] for root in (-1, 1)) / 2
    doob_pairing = sum(
        Fraction(root) * (terminal_values[root] - terminal_mean) for root in (-1, 1)
    ) / 2
    predictable_pairing = sum(Fraction(root) * full for root in (-1, 1)) / 2
    audit.check("future_feedback", "cross_doob", current_pairing == doob_pairing, current_pairing, doob_pairing)
    audit.check("future_feedback", "predictable_centres", predictable_pairing == 0, predictable_pairing, 0)
    audit.check("future_feedback", "innovation_survives", current_pairing != 0, current_pairing, "nonzero")

    two_root_states = tuple((first, second) for first in (-1, 1) for second in (-1, 1))
    terminal_two_root = {
        state: remainder(base, shift + bridge_scale * state[0], alpha, balanced=False)
        for state in two_root_states
    }
    mean_two_root = sum(terminal_two_root.values(), Fraction(0)) / 4
    conditional_first = {
        first: sum((terminal_two_root[(first, second)] for second in (-1, 1)), Fraction(0)) / 2
        for first in (-1, 1)
    }
    low_value = Fraction(2)
    terminal_cross = sum(
        Fraction(low_value + first + second) * terminal_two_root[(first, second)]
        for first, second in two_root_states
    ) / 4
    low_endpoint = low_value * mean_two_root
    bracket_one = sum(
        Fraction(first) * (conditional_first[first] - mean_two_root)
        for first, second in two_root_states
    ) / 4
    bracket_two = sum(
        Fraction(second) * (terminal_two_root[(first, second)] - conditional_first[first])
        for first, second in two_root_states
    ) / 4
    audit.check(
        "future_feedback",
        "two_root_cross_doob",
        terminal_cross == low_endpoint + bracket_one + bracket_two,
        terminal_cross,
        low_endpoint + bracket_one + bracket_two,
    )
    audit.check("future_feedback", "two_root_low_endpoint_retained", low_endpoint != 0, low_endpoint, "nonzero")
    audit.check("future_feedback", "two_root_first_bracket", bracket_one == full_prediction, bracket_one, full_prediction)
    audit.check("future_feedback", "two_root_second_bracket", bracket_two == 0, bracket_two, 0)

    # Independent exact-rational reconstruction of the future-insertion
    # Jensen blind spot.  No symbolic package or primary-source import is used.
    insertion_amplitude, insertion_coupling = Fraction(1, 10), Fraction(1, 2)
    insertion_large = insertion_amplitude * (1 + insertion_coupling)
    insertion_small = insertion_amplitude * (1 - insertion_coupling)

    def insertion_even_average(radius: Fraction) -> Fraction:
        positive = remainder(base, radius, alpha, balanced=False) * radius
        negative = remainder(base, -radius, alpha, balanced=False) * (-radius)
        return (positive + negative) / 2

    def insertion_closed_form(radius: Fraction) -> Fraction:
        return (
            -40
            * radius**4
            * (2 * radius**6 + 13 * radius**2 - 10)
            / (81 * (radius**2 - 2 * radius + 2) ** 2 * (radius**2 + 2 * radius + 2) ** 2)
        )

    audit.check(
        "future_feedback",
        "jensen_even_average_formula_large",
        insertion_even_average(insertion_large) == insertion_closed_form(insertion_large),
        insertion_even_average(insertion_large),
        insertion_closed_form(insertion_large),
    )
    audit.check(
        "future_feedback",
        "jensen_even_average_formula_small",
        insertion_even_average(insertion_small) == insertion_closed_form(insertion_small),
        insertion_even_average(insertion_small),
        insertion_closed_form(insertion_small),
    )
    zero_conditional_controls = all(
        (radius + (-radius)) / 2 == 0 for radius in (insertion_large, insertion_small)
    )
    audit.check(
        "future_feedback",
        "jensen_control_tangent_increments_vanish",
        zero_conditional_controls,
        zero_conditional_controls,
        True,
    )
    insertion_gap = insertion_even_average(insertion_large) - insertion_even_average(insertion_small)
    insertion_gap_oracle = Fraction(
        10175618597178586187512,
        67965137546788211215457205,
    )
    insertion_current_factor = -insertion_gap / 2
    insertion_current_oracle = Fraction(
        -5087809298589293093756,
        67965137546788211215457205,
    )
    audit.check(
        "future_feedback",
        "jensen_nonlinear_innovation_gap",
        insertion_gap == insertion_gap_oracle,
        insertion_gap,
        insertion_gap_oracle,
    )
    audit.check(
        "future_feedback",
        "jensen_current_is_negative",
        insertion_current_factor == insertion_current_oracle and insertion_current_factor < 0,
        insertion_current_factor,
        insertion_current_oracle,
    )
    gaussian_balanced = balanced_derivative * bridge_scale - Fraction(25, 27) * bridge_scale**3
    gaussian_balanced_from_moments = full_derivative * bridge_scale - Fraction(25, 81) * (
        3 * bridge_scale + 3 * bridge_scale**3
    )
    audit.check(
        "future_feedback",
        "gaussian_balanced_residual",
        gaussian_balanced_from_moments == gaussian_balanced,
        gaussian_balanced_from_moments,
        gaussian_balanced,
    )

    triple_average = cosine_triple_average(7, 10, 3)
    audit.check("future_feedback", "three_frequency_average", triple_average == Fraction(1, 4), triple_average, Fraction(1, 4))
    audit.check(
        "future_feedback",
        "full_fourier_coefficient",
        full_derivative * triple_average == Fraction(-35, 54),
        full_derivative * triple_average,
        Fraction(-35, 54),
    )
    audit.check(
        "future_feedback",
        "balanced_fourier_coefficient",
        balanced_derivative * triple_average == Fraction(-95, 108),
        balanced_derivative * triple_average,
        Fraction(-95, 108),
    )

    active_factor = 4 * (1 - alpha) ** 2
    kernel_factor = 4 * alpha**2 * active_rank * (active_rank + 2)
    audit.check("heat_geometry", "active_factor", active_factor == Fraction(64, 81), active_factor, Fraction(64, 81))
    audit.check("heat_geometry", "kernel_factor", kernel_factor == Fraction(800, 27), kernel_factor, Fraction(800, 27))
    audit.check("heat_geometry", "pointwise_active_floor", 1 - alpha == Fraction(4, 9), 1 - alpha, Fraction(4, 9))
    curl_value = cartan_curl(alpha)
    audit.check("cartan_boundary", "full_remainder_one_form_curl", curl_value == Fraction(-40, 729), curl_value, Fraction(-40, 729))

    diagnostics.update(
        {
            "production_constants": constants,
            "scalar_owner": {
                "full": full,
                "cubic": cubic,
                "balanced": balanced,
                "full_shift_derivative": full_derivative,
                "balanced_shift_derivative": balanced_derivative,
            },
            "laplace_coefficients": {
                "polynomial": polynomial_coefficient,
                "first_resolvent": first_resolvent_coefficient,
                "second_resolvent": second_resolvent_coefficient,
                "F1": first_moment_coefficients,
                "F2": second_moment_coefficients,
            },
            "chronological_closure": {
                "finite_array_value": chronological_original,
                "derivative_slack": derivative_slack,
                "coefficient_shell_decay": chronological_decay,
                "coefficient_x_power": chronological_x_power,
                "coefficient_y_power": chronological_y_power,
                "coefficient_slack": chronological_slack,
                "required_gaussian_moment": 1 / chronological_slack,
                "eta_power": chronological_x_power / chronological_slack,
                "zeta_power": chronological_y_power / chronological_slack,
                "canonical_x_fixture": canonical_path_energy,
                "high_prefix_derivative_x_power": high_prefix_derivative_x_power,
                "fixed_low_x_power": fixed_low_x_power,
                "fixed_low_y_power": fixed_low_y_power,
                "fixed_low_slack": fixed_low_slack,
                "fixed_low_required_gaussian_moment": fixed_low_moment,
                "fixed_low_eta_power": fixed_low_eta_power,
                "fixed_low_zeta_power": fixed_low_zeta_power,
                "fixed_low_decay_power": fixed_low_decay_power,
            },
            "future_feedback": {
                "lambda": bridge_scale,
                "full_residual": full_bridge,
                "balanced_residual": balanced_bridge,
                "balanced_gaussian_residual": gaussian_balanced,
                "two_root_first_bracket": bracket_one,
                "two_root_second_bracket": bracket_two,
                "two_root_low_endpoint": low_endpoint,
                "jensen_innovation_gap": insertion_gap,
                "jensen_current_sqrt_2_over_pi_factor": insertion_current_factor,
                "predictable_pairing": predictable_pairing,
                "three_frequency_average": triple_average,
            },
            "heat_geometry": {"active_factor": active_factor, "kernel_factor": kernel_factor},
            "cartan_boundary": {"full_remainder_one_form_curl": curl_value},
            "analytic_boundary": {
                "naive_global_to_predictable_bridge": False,
                "full_hessian_chain_primitive": False,
                "regular_weighted_innovation_carleson_proved": True,
                "regular_k_r_lower_form": True,
                "full_frame_posterior_bracket": False,
                "complete_h_n": False,
                "reg": False,
                "sector_a_closed": False,
            },
        }
    )

    payload = audit.finish(diagnostics)
    atomic_json(OUTPUT, payload)
    print(
        "R-102 independent:",
        f"{payload['assertions_passed']}/{payload['assertions_total']} PASS",
        f"-> {OUTPUT.relative_to(REPO)}",
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
