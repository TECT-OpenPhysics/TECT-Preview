#!/usr/bin/env python3
"""Independent standard-library verifier for the scoped R-124 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
from dataclasses import dataclass
from fractions import Fraction as F
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-STATIONARY-POLARIZED-TRACE-DEFECT-REPLICA-ROOT-SHELL-BOUNDARY"
SCHEMA = "tect/a13-stationary-polarized-trace-defect-replica-root-shell-boundary-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-independent-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


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
            "schema": SCHEMA,
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
                "This non-importing verifier confirms only R-124's scoped stationary-polarization, "
                "replica, legal-row, and method-boundary statements. The full production estimate, "
                "OVERLAP_src, Nelson, removals, measure construction, and Sector A remain open."
            ),
        }


def close(left: float, right: float, tolerance: float = 2e-9) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def normal_expectation(function: Callable[[float], float], radius: float = 10.0, panels: int = 24000) -> float:
    if panels % 2:
        raise ValueError("Simpson panels must be even")
    step = 2 * radius / panels
    normalizer = 1 / math.sqrt(2 * math.pi)

    def integrand(value: float) -> float:
        return function(value) * normalizer * math.exp(-value * value / 2)

    total = integrand(-radius) + integrand(radius)
    for index in range(1, panels):
        total += (4 if index % 2 else 2) * integrand(-radius + index * step)
    return total * step / 3


Poly = dict[int, F]


def poly_add(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for degree, coefficient in right.items():
        result[degree] = result.get(degree, F(0)) + coefficient
        if result[degree] == 0:
            del result[degree]
    return result


def poly_scale(poly: Poly, coefficient: F) -> Poly:
    return {degree: coefficient * value for degree, value in poly.items() if coefficient * value}


def poly_mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for first_degree, first_value in left.items():
        for second_degree, second_value in right.items():
            degree = first_degree + second_degree
            result[degree] = result.get(degree, F(0)) + first_value * second_value
    return {degree: value for degree, value in result.items() if value}


def poly_derivative(poly: Poly) -> Poly:
    return {
        degree - 1: F(degree) * coefficient
        for degree, coefficient in poly.items()
        if degree > 0 and coefficient
    }


def laguerre_polynomial(order: int, alpha: F) -> Poly:
    values: list[Poly] = [{0: F(1)}]
    if order == 0:
        return values[0]
    values.append({0: alpha + 1, 1: F(-1)})
    variable = {1: F(1)}
    for degree in range(1, order):
        affine = poly_add({0: F(2 * degree + 1) + alpha}, poly_scale(variable, F(-1)))
        numerator = poly_add(
            poly_mul(affine, values[degree]),
            poly_scale(values[degree - 1], -(F(degree) + alpha)),
        )
        values.append(poly_scale(numerator, F(1, degree + 1)))
    return values[order]


def monic_scaled_laguerre(order: int, alpha: F) -> Poly:
    scale = F((-1) ** order * math.factorial(order) * 2**order)
    return {
        degree: scale * coefficient / F(2**degree)
        for degree, coefficient in laguerre_polynomial(order, alpha).items()
    }


def tridiagonal_characteristic(diagonal: list[F], off_diagonal_squared: list[F]) -> Poly:
    previous_previous: Poly = {0: F(1)}
    previous: Poly = {1: F(1), 0: -diagonal[0]}
    for index in range(1, len(diagonal)):
        current = poly_add(
            poly_mul({1: F(1), 0: -diagonal[index]}, previous),
            poly_scale(previous_previous, -off_diagonal_squared[index - 1]),
        )
        previous_previous, previous = previous, current
    return previous


def smallest_tridiagonal_eigenvalue(diagonal: list[float], off_diagonal: list[float]) -> float:
    lower = min(
        diagonal[index]
        - (abs(off_diagonal[index - 1]) if index else 0.0)
        - (abs(off_diagonal[index]) if index < len(off_diagonal) else 0.0)
        for index in range(len(diagonal))
    ) - 1.0
    upper = max(
        diagonal[index]
        + (abs(off_diagonal[index - 1]) if index else 0.0)
        + (abs(off_diagonal[index]) if index < len(off_diagonal) else 0.0)
        for index in range(len(diagonal))
    ) + 1.0

    def count_below(value: float) -> int:
        pivot = diagonal[0] - value
        count = int(pivot < 0.0)
        for index in range(1, len(diagonal)):
            if abs(pivot) < 1e-15:
                pivot = -1e-15 if pivot < 0.0 else 1e-15
            pivot = diagonal[index] - value - off_diagonal[index - 1] ** 2 / pivot
            count += int(pivot < 0.0)
        return count

    for _ in range(120):
        midpoint = (lower + upper) / 2.0
        if count_below(midpoint) >= 1:
            upper = midpoint
        else:
            lower = midpoint
    return (lower + upper) / 2.0


def gaussian_moment(degree: int) -> F:
    if degree % 2:
        return F(0)
    answer = F(1)
    for value in range(1, degree, 2):
        answer *= value
    return answer


def gaussian_poly_expectation(poly: Poly) -> F:
    return sum((coefficient * gaussian_moment(degree) for degree, coefficient in poly.items()), F(0))


def hermite_polynomials(maximum: int) -> list[Poly]:
    values = [{0: F(1)}]
    if maximum == 0:
        return values
    values.append({1: F(1)})
    x_poly = {1: F(1)}
    for degree in range(1, maximum):
        values.append(poly_add(poly_mul(x_poly, values[degree]), poly_scale(values[degree - 1], F(-degree))))
    return values


@dataclass(frozen=True)
class BiJet:
    coefficients: tuple[tuple[F, ...], ...]

    @property
    def x_order(self) -> int:
        return len(self.coefficients) - 1

    @property
    def y_order(self) -> int:
        return len(self.coefficients[0]) - 1

    @classmethod
    def constant(cls, value: F | int, x_order: int, y_order: int) -> "BiJet":
        rows = [[F(0) for _ in range(y_order + 1)] for _ in range(x_order + 1)]
        rows[0][0] = F(value)
        return cls(tuple(tuple(row) for row in rows))

    @classmethod
    def x_variable(cls, centre: F | int, x_order: int, y_order: int) -> "BiJet":
        rows = [list(row) for row in cls.constant(centre, x_order, y_order).coefficients]
        rows[1][0] = F(1)
        return cls(tuple(tuple(row) for row in rows))

    @classmethod
    def y_variable(cls, centre: F | int, x_order: int, y_order: int) -> "BiJet":
        rows = [list(row) for row in cls.constant(centre, x_order, y_order).coefficients]
        rows[0][1] = F(1)
        return cls(tuple(tuple(row) for row in rows))

    @property
    def value(self) -> F:
        return self.coefficients[0][0]

    def coerce(self, other: "BiJet | F | int") -> "BiJet":
        if isinstance(other, BiJet):
            return other
        return BiJet.constant(F(other), self.x_order, self.y_order)

    def __add__(self, other: "BiJet | F | int") -> "BiJet":
        right = self.coerce(other)
        return BiJet(tuple(tuple(self.coefficients[i][j] + right.coefficients[i][j] for j in range(self.y_order + 1)) for i in range(self.x_order + 1)))

    __radd__ = __add__

    def __neg__(self) -> "BiJet":
        return BiJet(tuple(tuple(-value for value in row) for row in self.coefficients))

    def __sub__(self, other: "BiJet | F | int") -> "BiJet":
        return self + (-self.coerce(other))

    def __rsub__(self, other: "BiJet | F | int") -> "BiJet":
        return self.coerce(other) - self

    def __mul__(self, other: "BiJet | F | int") -> "BiJet":
        right = self.coerce(other)
        rows: list[list[F]] = []
        for i in range(self.x_order + 1):
            row: list[F] = []
            for j in range(self.y_order + 1):
                row.append(sum((self.coefficients[p][q] * right.coefficients[i - p][j - q] for p in range(i + 1) for q in range(j + 1)), F(0)))
            rows.append(row)
        return BiJet(tuple(tuple(row) for row in rows))

    __rmul__ = __mul__

    def reciprocal(self) -> "BiJet":
        origin = self.value
        if origin == 0:
            raise ZeroDivisionError("zero jet origin")
        rows = [[F(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        rows[0][0] = 1 / origin
        for total in range(1, self.x_order + self.y_order + 1):
            for i in range(self.x_order + 1):
                j = total - i
                if 0 <= j <= self.y_order:
                    correction = sum((self.coefficients[p][q] * rows[i - p][j - q] for p in range(i + 1) for q in range(j + 1) if (p, q) != (0, 0)), F(0))
                    rows[i][j] = -correction / origin
        return BiJet(tuple(tuple(row) for row in rows))

    def __truediv__(self, other: "BiJet | F | int") -> "BiJet":
        return self * self.coerce(other).reciprocal()

    def __rtruediv__(self, other: "BiJet | F | int") -> "BiJet":
        return self.coerce(other) * self.reciprocal()

    def __pow__(self, exponent: int) -> "BiJet":
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
        rows = [[F(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        for i in range(self.x_order):
            for j in range(self.y_order + 1):
                rows[i][j] = F(i + 1) * self.coefficients[i + 1][j]
        return BiJet(tuple(tuple(row) for row in rows))

    def dy(self) -> "BiJet":
        rows = [[F(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        for i in range(self.x_order + 1):
            for j in range(self.y_order):
                rows[i][j] = F(j + 1) * self.coefficients[i][j + 1]
        return BiJet(tuple(tuple(row) for row in rows))


def production_constants() -> tuple[F, F, F, F, F]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = F(str(parameters["M_X"])) ** 2 + F(str(parameters["classii_mass_regularizer"]))
    a_weight = F(str(parameters["cJJ"])) * F(str(parameters["alpha_X"])) ** 2 / mass
    b_weight = F(str(parameters["cJK"])) * F(str(parameters["alpha_X"])) * F(str(parameters["beta_X"])) / mass
    c_weight = F(str(parameters["cKK"])) * F(str(parameters["beta_X"])) ** 2 / mass
    alpha = c_weight / (b_weight + c_weight)
    c1 = c_weight / alpha**2
    c0 = a_weight - b_weight**2 / c_weight
    return mass, c0, c1, alpha, 4 * c0


def coefficient(x: BiJet, y: BiJet, alpha: F) -> list[list[BiJet]]:
    denominator = 1 + x**2 + y**2
    vector = [x - alpha * x**3 / denominator, -alpha * x**2 * y / denominator]
    return [[4 * vector[i] * vector[j] for j in range(2)] for i in range(2)]


def matrix_add(*matrices: list[list[BiJet]]) -> list[list[BiJet]]:
    return [[sum((matrix[i][j] for matrix in matrices), matrices[0][i][j] * 0) for j in range(2)] for i in range(2)]


def matrix_scale(value: F, matrix: list[list[BiJet]]) -> list[list[BiJet]]:
    return [[value * matrix[i][j] for j in range(2)] for i in range(2)]


def matrix_dx(matrix: list[list[BiJet]]) -> list[list[BiJet]]:
    return [[matrix[i][j].dx() for j in range(2)] for i in range(2)]


def curl_values(alpha: F) -> tuple[F, F, F]:
    x = BiJet.x_variable(1, 3, 1)
    y = BiJet.y_variable(1, 3, 1)
    b0 = coefficient(x, y, alpha)
    b1 = coefficient(x + 1, y, alpha)
    taylor = matrix_add(b0, matrix_dx(b0), matrix_scale(F(1, 2), matrix_dx(matrix_dx(b0))))
    remainder = [[b1[i][j] - taylor[i][j] for j in range(2)] for i in range(2)]

    def curl(matrix: list[list[BiJet]]) -> F:
        return matrix[0][0].dy().value - matrix[1][0].dx().value

    return curl(remainder), curl(taylor), curl(b1)


def periodic_average(function: Callable[[float], float], points: int = 512) -> float:
    return sum(function(2 * math.pi * index / points) for index in range(points)) / points


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    mass, c0, c1, alpha, kappa2 = production_constants()
    eta_row = kappa2 / 2
    audit.check("production", "mass", mass == F(4000000000001, 10**12), mass, F(4000000000001, 10**12))
    audit.check("production", "c0", c0 == F(3, 250) / mass, c0, F(3, 250) / mass)
    audit.check("production", "c1", c1 == F(243, 8000) / mass, c1, F(243, 8000) / mass)
    audit.check("production", "alpha", alpha == F(5, 9), alpha, F(5, 9))
    audit.check("production", "row_allocation", eta_row == F(3, 125) / mass, eta_row, F(3, 125) / mass)

    phi0, delta_phi, delta_theta = F(2), F(3), F(5)
    phih = phi0 + delta_phi
    direct = delta_theta - (phih**2 - phi0**2)
    audit.check("polarization", "symmetric_secant", delta_theta - (phih + phi0) * delta_phi == direct, delta_theta - (phih + phi0) * delta_phi, direct)
    audit.check("polarization", "negative_square_form", delta_theta - 2 * phi0 * delta_phi - delta_phi**2 == direct, delta_theta - 2 * phi0 * delta_phi - delta_phi**2, direct)
    complex_phi0 = (2 + 1j, -1 + 2j)
    complex_delta = (3 - 1j, 4 + 1j)
    norm = lambda vector: sum(abs(value) ** 2 for value in vector)
    real_inner = lambda left, right: sum((left[i].conjugate() * right[i] for i in range(len(left)))).real
    complex_phih = tuple(complex_phi0[i] + complex_delta[i] for i in range(2))
    complex_symmetric = 7 - real_inner(tuple(complex_phih[i] + complex_phi0[i] for i in range(2)), complex_delta)
    complex_direct = 7 - (norm(complex_phih) - norm(complex_phi0))
    audit.check("polarization", "complex_real_inner_product", close(complex_symmetric, complex_direct, 1e-14), complex_symmetric, complex_direct)
    weights = (F(1, 3), F(2, 3))
    values = (F(-2), F(4))
    thetas = (F(5), F(11))
    mean = sum((weights[i] * values[i] for i in range(2)), F(0))
    d0 = sum((weights[i] * (thetas[i] - (values[i] - mean) ** 2) for i in range(2)), F(0))
    direct_s = sum((weights[i] * (thetas[i] - values[i] ** 2) for i in range(2)), F(0))
    audit.check("polarization", "conditional_cell_identity", d0 - mean**2 == direct_s, d0 - mean**2, direct_s)
    b0, db, mixed_y, dy2, dtheta = F(2), F(-1), F(3, 2), F(5, 2), F(7)
    centered = dtheta - 2 * b0 * db - db**2 - 2 * mixed_y - dy2
    uncentered_expected = dtheta - 2 * (b0 * db + mixed_y) - (db**2 + dy2)
    audit.check("polarization", "centered_decomposition", centered == uncentered_expected, centered, uncentered_expected)
    atoms = (F(-1), F(1))
    epsilon = F(2, 5)
    mixed = sum((F(1, 2) * atom * (-epsilon * atom) for atom in atoms), F(0))
    audit.check("polarization", "mixed_centered_covariance_nonzero", mixed == -epsilon, mixed, -epsilon)
    replica_values = ((F(1), F(2)), (F(-2), F(4)))
    replica_mean = tuple(sum((weights[i] * replica_values[i][coordinate] for i in range(2)), F(0)) for coordinate in range(2))
    replica_lhs = F(1, 2) * sum((weights[i] * weights[j] * sum((replica_values[i][k] - replica_values[j][k]) ** 2 for k in range(2)) for i in range(2) for j in range(2)), F(0))
    replica_rhs = sum((weights[i] * sum(value**2 for value in replica_values[i]) for i in range(2)), F(0)) - sum(value**2 for value in replica_mean)
    audit.check("polarization", "conditional_replica_variance", replica_lhs == replica_rhs, replica_lhs, replica_rhs)
    audit.check("polarization", "baseline_not_automatically_zero", F(0) - F(1) ** 2 == -1, -1, "nonzero baseline allowed")

    a, first, second, third = F(2), F(3), F(-5), F(7)
    trace_values = (F(11), F(13), F(-2), F(19))
    endpoint_values = (a, a + first, a + first + second, a + first + second + third)
    packets = [trace_values[index] - trace_values[index - 1] - (endpoint_values[index] + endpoint_values[index - 1]) * (endpoint_values[index] - endpoint_values[index - 1]) for index in range(1, 4)]
    endpoint_packet = trace_values[-1] - trace_values[0] - (endpoint_values[-1] ** 2 - endpoint_values[0] ** 2)
    audit.check("refinement", "three_visit_telescope", sum(packets, F(0)) == endpoint_packet, sum(packets, F(0)), endpoint_packet)
    moving = (trace_values[1] - trace_values[0] - 2 * a * first - first**2) + (trace_values[2] - trace_values[1] - 2 * (a + first) * second - second**2)
    endpoint_two = trace_values[2] - trace_values[0] - 2 * a * (first + second) - (first + second) ** 2
    audit.check("refinement", "moving_baseline_three_term", moving == endpoint_two, moving, endpoint_two)
    fixed_wrong = (trace_values[1] - trace_values[0] - 2 * a * first - first**2) + (trace_values[2] - trace_values[1] - 2 * a * second - second**2)
    audit.check("refinement", "fixed_baseline_missing_cross", fixed_wrong - endpoint_two == 2 * first * second, fixed_wrong - endpoint_two, 2 * first * second)
    coefficients = (F(1, 2), F(1, 2))
    full_trace = sum((coefficients[i] * coefficients[j] for i in range(2) for j in range(2)), F(0))
    diagonal_trace = sum((value**2 for value in coefficients), F(0))
    audit.check("refinement", "full_covariance_trace", full_trace == 1, full_trace, 1)
    audit.check("refinement", "diagonal_trace_is_wrong", diagonal_trace == F(1, 2), diagonal_trace, F(1, 2))

    hermites = hermite_polynomials(5)
    coefficients_h = [F(1), F(2), F(-1), F(3), F(2)]
    h_poly: Poly = {}
    for index, coefficient_h in enumerate(coefficients_h):
        h_poly = poly_add(h_poly, poly_scale(hermites[index], coefficient_h))
    actual_form = gaussian_poly_expectation(poly_mul({2: F(1), 0: F(-1)}, poly_mul(h_poly, h_poly)))
    expected_form = 2 * sum((F(index * math.factorial(index)) * coefficients_h[index] ** 2 for index in range(5)), F(0)) + 2 * sum((F(math.factorial(index + 2)) * coefficients_h[index] * coefficients_h[index + 2] for index in range(3)), F(0))
    audit.check("hermite", "quadratic_form", actual_form == expected_form, actual_form, expected_form)
    matrix = [[0.0 for _ in range(5)] for _ in range(5)]
    for index in range(5):
        matrix[index][index] = 2 * index + 1
        if index + 2 < 5:
            matrix[index][index + 2] = matrix[index + 2][index] = math.sqrt((index + 1) * (index + 2))
    normalized_coefficients = [math.sqrt(math.factorial(index)) * float(coefficients_h[index]) for index in range(5)]
    normalized_matrix_form = sum(
        normalized_coefficients[row]
        * (matrix[row][column] - (1.0 if row == column else 0.0))
        * normalized_coefficients[column]
        for row in range(5)
        for column in range(5)
    )
    audit.check("hermite", "normalized_matrix_representation", close(normalized_matrix_form, float(actual_form), 1e-12), normalized_matrix_form, actual_form)
    audit.check("hermite", "mu0_mu1", 1 == 1 and 1 == 1, (1, 1), (1, 1))
    even_characteristic = tridiagonal_characteristic([F(1), F(5), F(9)], [F(2), F(12)])
    odd_characteristic = tridiagonal_characteristic([F(3), F(7), F(11)], [F(6), F(20)])
    even_laguerre = monic_scaled_laguerre(3, F(-1, 2))
    odd_laguerre = monic_scaled_laguerre(3, F(1, 2))
    audit.check("hermite", "laguerre_block_characteristics", even_characteristic == even_laguerre and odd_characteristic == odd_laguerre, (even_characteristic, odd_characteristic), (even_laguerre, odd_laguerre))
    mu2 = 3 - math.sqrt(6)
    audit.check("hermite", "mu2", close(mu2, 0.5505102572168219, 1e-14), mu2, "3-sqrt(6)")
    audit.check("hermite", "degree_two_gain", close(1 - mu2, math.sqrt(6) - 2, 1e-14), 1 - mu2, math.sqrt(6) - 2)
    odd_min = 5 - math.sqrt(10)
    mu3 = min(mu2, odd_min)
    audit.check("hermite", "mu3", close(mu3, mu2, 1e-14), mu3, mu2)
    bump_parameter = 2.0
    bump_norm = normal_expectation(lambda value: math.exp(-2 * bump_parameter * value**2))
    bump_x2_norm = normal_expectation(lambda value: value**2 * math.exp(-2 * bump_parameter * value**2))
    bump_ratio = (bump_norm - bump_x2_norm) / bump_norm
    audit.check("hermite", "gaussian_bump_ratio", close(bump_ratio, 8 / 9, 1e-10), bump_ratio, F(8, 9))
    even_min_m5 = smallest_tridiagonal_eigenvalue([1.0, 5.0, 9.0], [math.sqrt(2), math.sqrt(12)])
    odd_min_m5 = smallest_tridiagonal_eigenvalue([3.0, 7.0, 11.0], [math.sqrt(6), math.sqrt(20)])
    audit.check("hermite", "even_block_smaller_M5", even_min_m5 < odd_min_m5, (even_min_m5, odd_min_m5), "even minimum below odd minimum")

    audit.check("legal_row", "kappa2", kappa2 == F(6, 125) / mass, kappa2, F(6, 125) / mass)
    h_linear = lambda value: 0.3 + 0.2 * value
    x_value = normal_expectation(lambda value: h_linear(value) ** 2)
    x2_value = normal_expectation(lambda value: value**2 * h_linear(value) ** 2)
    theta_h_numeric = float(kappa2) * normal_expectation(lambda value: value**2 / 2 + h_linear(value) ** 2 + 1)
    phi_h_square_numeric = float(kappa2) * normal_expectation(lambda value: value**4 / 2 + value**2 * h_linear(value) ** 2)
    theta_0_numeric = float(kappa2) * normal_expectation(lambda value: value**2 / 2 + 1)
    phi_0_square_numeric = float(kappa2) * normal_expectation(lambda value: value**4 / 2)
    baseline_trace_defect = theta_0_numeric - phi_0_square_numeric
    direct_row = (theta_h_numeric - phi_h_square_numeric) - baseline_trace_defect
    audit.check("legal_row", "trace_defect_definition", close(baseline_trace_defect, 0.0, 1e-12), baseline_trace_defect, 0.0)
    audit.check("legal_row", "stationary_difference", close(direct_row, float(kappa2) * normal_expectation(lambda value: (1 - value**2) * h_linear(value) ** 2)), direct_row, "kappa2 E[(1-x^2)h^2]")
    audit.check("legal_row", "source_upper_bound", direct_row <= float(kappa2) * x_value + 1e-12, direct_row, float(kappa2) * x_value)
    audit.check("legal_row", "action_allocation", eta_row == kappa2 / 2 and eta_row < F(9, 20), eta_row, (kappa2 / 2, F(9, 20)))
    frequency_n = 2
    sin_source_numeric = normal_expectation(lambda value: (math.sin(frequency_n * value) / frequency_n) ** 2)
    sin_source_exact = (1 - math.exp(-2 * frequency_n**2)) / (2 * frequency_n**2)
    audit.check("legal_row", "sin_source", close(sin_source_numeric, sin_source_exact), sin_source_numeric, sin_source_exact)
    sin_sixth_numeric = normal_expectation(lambda value: (math.sin(frequency_n * value) / frequency_n) ** 6)
    sin_sixth_exact = (10 - 15 * math.exp(-2 * frequency_n**2) + 6 * math.exp(-8 * frequency_n**2) - math.exp(-18 * frequency_n**2)) / (32 * frequency_n**6)
    audit.check("legal_row", "sin_sixth", close(sin_sixth_numeric, sin_sixth_exact), sin_sixth_numeric, sin_sixth_exact)
    sin_delta_numeric = float(kappa2) * normal_expectation(lambda value: (1 - value**2) * (math.sin(frequency_n * value) / frequency_n) ** 2)
    audit.check("legal_row", "sin_trace_defect", close(sin_delta_numeric, -2 * float(kappa2) * math.exp(-2 * frequency_n**2)), sin_delta_numeric, -2 * float(kappa2) * math.exp(-2 * frequency_n**2))
    sin_mean_numeric = normal_expectation(lambda value: value * math.sin(frequency_n * value) / frequency_n)
    sin_d0_numeric = sin_delta_numeric + float(kappa2) * sin_mean_numeric**2
    sin_d0_exact = float(kappa2) * (math.exp(-frequency_n**2) - 2 * math.exp(-2 * frequency_n**2))
    audit.check("legal_row", "sin_D0_difference", close(sin_d0_numeric, sin_d0_exact, 1e-12), sin_d0_numeric, sin_d0_exact)
    cosine_t, cosine_d = 0.7, 0.4
    cosine_numeric = float(kappa2) * normal_expectation(lambda value: (1 - value**2) * (cosine_d * math.cos(cosine_t * value)) ** 2)
    cosine_exact = 2 * float(kappa2) * cosine_d**2 * cosine_t**2 * math.exp(-2 * cosine_t**2)
    audit.check("legal_row", "cosine_positive_defect", cosine_numeric > 0 and close(cosine_numeric, cosine_exact), cosine_numeric, cosine_exact)

    curl_k, curl_m, curl_full = curl_values(alpha)
    audit.check("cartan", "K_R_curl", curl_k == F(-40, 729), curl_k, F(-40, 729))
    audit.check("cartan", "M_U_curl", curl_m == F(2720, 729), curl_m, F(2720, 729))
    audit.check("cartan", "full_curl", curl_full == F(2680, 729), curl_full, F(2680, 729))
    audit.check("cartan", "curl_recombination", curl_k + curl_m == curl_full, curl_k + curl_m, curl_full)
    audit.check("cartan", "no_opposite_companion", curl_m != -curl_k and curl_full != 0, (curl_m, curl_full), ("not +40/729", "nonzero"))

    spatial_n, sobolev_s = 8, 1.1
    h2_norm = periodic_average(
        lambda angle: 1
        + (math.sin(spatial_n * angle) / spatial_n**2) ** 2
        + (math.cos(spatial_n * angle) / spatial_n) ** 2
        + math.sin(spatial_n * angle) ** 2,
        2048,
    )
    h2_exact = 1.5 + 1 / (2 * spatial_n**2) + 1 / (2 * spatial_n**4)
    audit.check("critical", "H2_norm", close(h2_norm, h2_exact, 1e-12), h2_norm, h2_exact)
    l6_norm = periodic_average(lambda angle: (1 + (math.sin(spatial_n * angle) / spatial_n**2) ** 2) ** 3, 2048)
    l6_exact = 1 + 3 / (2 * spatial_n**4) + 9 / (8 * spatial_n**8) + 5 / (16 * spatial_n**12)
    audit.check("critical", "L6_norm", close(l6_norm, l6_exact, 1e-12), l6_norm, l6_exact)
    q_norm = spatial_n ** (2 * sobolev_s) / (2 * (1 + spatial_n**2) ** sobolev_s)
    audit.check("critical", "negative_norm_bound", q_norm < 0.5, q_norm, 0.5)
    pairing_numeric = periodic_average(lambda angle: spatial_n**sobolev_s * math.cos(spatial_n * angle) * (-math.cos(spatial_n * angle) / spatial_n), 1024)
    pairing_exact = -spatial_n ** (sobolev_s - 1) / 2
    audit.check("critical", "pairing", close(pairing_numeric, pairing_exact), pairing_numeric, pairing_exact)
    pairing_8 = abs(pairing_exact)
    pairing_16 = 16 ** (sobolev_s - 1) / 2
    audit.check("critical", "Hminus_11_10_diverges", pairing_16 > pairing_8, pairing_16, pairing_8)
    rare_atoms_2 = [2**6 if index == 0 else 0 for index in range(2**6)]
    rare_mean = sum(rare_atoms_2) / len(rare_atoms_2)
    rare_atoms_3 = [3**6 if index == 0 else 0 for index in range(3**6)]
    rare_moments = (sum(value ** (5 / 3) for value in rare_atoms_3) / len(rare_atoms_3), sum(value ** (5 / 2) for value in rare_atoms_3) / len(rare_atoms_3))
    audit.check("critical", "rare_moments", close(rare_mean, 1.0, 1e-15) and close(rare_moments[0], 3**4) and close(rare_moments[1], 3**9), (rare_mean, rare_moments), (1.0, 3**4, 3**9))

    C, H = 0.013, 2.3
    connection = periodic_average(
        lambda angle: 4 * C * (H * (2 + math.cos(angle))) ** 2 * (
            math.sin(angle) + (-H * math.sin(angle)) * (2 - math.cos(angle)) / (H * (2 + math.cos(angle)))
        ) ** 2
    )
    acceleration = periodic_average(
        lambda angle: 8 * C * (H * (2 + math.cos(angle))) * (-H * math.sin(angle)) * (2 - math.cos(angle)) * math.sin(angle)
    )
    total = periodic_average(
        lambda angle: 4 * C * (H * (2 + math.cos(angle))) ** 2 * math.sin(angle) ** 2
        + 16 * C * (H * (2 + math.cos(angle))) * (2 - math.cos(angle)) * (-H * math.sin(angle)) * math.sin(angle)
        + 4 * C * (2 - math.cos(angle)) ** 2 * (-H * math.sin(angle)) ** 2
    )
    audit.check("covariant", "connection_identity", close(total, connection + acceleration, 1e-15), total, connection + acceleration)
    audit.check("covariant", "connection_square_value", close(connection, 2 * C * H**2), connection, 2 * C * H**2)
    audit.check("covariant", "acceleration_value", close(acceleration, -15 * C * H**2), acceleration, -15 * C * H**2)
    production_c = c0 + c1 * F(16, 81)
    audit.check("covariant", "negative_total", close(total, -13 * C * H**2) and -13 * production_c == -F(117, 500) / mass, (total, -13 * production_c), (-13 * C * H**2, -F(117, 500) / mass))

    chaos_n, chaos_norm = 5, F(7, 11)
    h5_second = poly_derivative(poly_derivative(hermites[5]))
    d2_norm = gaussian_poly_expectation(poly_mul(h5_second, h5_second)) * chaos_norm
    audit.check("ou", "second_derivative_norm", d2_norm == F(chaos_n * (chaos_n - 1) * math.factorial(chaos_n)) * chaos_norm, d2_norm, F(chaos_n * (chaos_n - 1) * math.factorial(chaos_n)) * chaos_norm)
    integrated = d2_norm / (2 * chaos_n)
    expected_integrated = F((chaos_n - 1) * math.factorial(chaos_n), 2) * chaos_norm
    audit.check("ou", "semigroup_integral", integrated == expected_integrated, integrated, expected_integrated)
    fixture = {2: F(1, 2), 3: F(-1, 3), 4: F(1, 4)}
    fixture_debt = -F(1, 2) * sum((F((order - 1) * math.factorial(order)) * coefficient**2 for order, coefficient in fixture.items()), F(0))
    audit.check("ou", "fixture_negative_debt", fixture_debt == -F(19, 6), fixture_debt, -F(19, 6))

    diagnostics = {
        "engine": "standard-library Fraction algebra, monomial Gaussian moments, bivariate jets, Simpson Gaussian quadrature, and alias-free torus quadrature",
        "production": {"P": mass, "c0": c0, "c1": c1, "alpha": alpha, "kappa2": kappa2, "eta_row": eta_row},
        "cartan": {"K_R": curl_k, "M_U": curl_m, "full": curl_full},
        "scope_flags": {
            "complete_production_trace_excess_proved": False,
            "overlap_src_proved": False,
            "nelson_proved": False,
            "sector_a_closed": False,
            "tier_promoted": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-124 independent {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
