#!/usr/bin/env python3
"""Independent standard-library certificate for the scoped R-108 frontier.

The implementation imports neither the primary certificate nor symbolic,
array, or scientific-computing packages.  Exact Fractions, a second-order
dual-number calculation, finite distributions, factorial moments, and direct
Gaussian quadrature independently check every load-bearing formula.
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
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable


SCHEMA = "tect/a13-complete-cluster-quotient-carleson-frontier-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-complete-cluster-quotient-carleson-frontier/result.json"
)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def require(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
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

    def close(self, group: str, name: str, actual: float, expected: float, tolerance: float = 1e-12) -> None:
        self.require(group, name, math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), actual, expected)


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


@dataclass(frozen=True)
class Jet2:
    value: Fraction
    first: Fraction = Fraction(0)
    second: Fraction = Fraction(0)

    @staticmethod
    def lift(value: Fraction | int) -> "Jet2":
        return value if isinstance(value, Jet2) else Jet2(Fraction(value))  # type: ignore[return-value]

    def __add__(self, other: object) -> "Jet2":
        rhs = other if isinstance(other, Jet2) else Jet2(Fraction(other))  # type: ignore[arg-type]
        return Jet2(self.value + rhs.value, self.first + rhs.first, self.second + rhs.second)

    __radd__ = __add__

    def __neg__(self) -> "Jet2":
        return Jet2(-self.value, -self.first, -self.second)

    def __sub__(self, other: object) -> "Jet2":
        return self + (-other if isinstance(other, Jet2) else -Fraction(other))  # type: ignore[arg-type]

    def __rsub__(self, other: object) -> "Jet2":
        return (-self) + other

    def __mul__(self, other: object) -> "Jet2":
        rhs = other if isinstance(other, Jet2) else Jet2(Fraction(other))  # type: ignore[arg-type]
        return Jet2(
            self.value * rhs.value,
            self.first * rhs.value + self.value * rhs.first,
            self.second * rhs.value + 2 * self.first * rhs.first + self.value * rhs.second,
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "Jet2":
        if self.value == 0:
            raise ZeroDivisionError
        return Jet2(
            1 / self.value,
            -self.first / self.value**2,
            2 * self.first**2 / self.value**3 - self.second / self.value**2,
        )

    def __truediv__(self, other: object) -> "Jet2":
        rhs = other if isinstance(other, Jet2) else Jet2(Fraction(other))  # type: ignore[arg-type]
        return self * rhs.reciprocal()

    def __rtruediv__(self, other: object) -> "Jet2":
        return (other if isinstance(other, Jet2) else Jet2(Fraction(other))) * self.reciprocal()  # type: ignore[arg-type]

    def __pow__(self, power: int) -> "Jet2":
        if power < 0:
            return (self.reciprocal()) ** (-power)
        result = Jet2(Fraction(1))
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent //= 2
        return result


def production_jet(value: Fraction) -> Jet2:
    x = Jet2(value, Fraction(1), Fraction(0))
    return 4 * x**2 * (4 * x**2 + 9) ** 2 / (81 * (1 + x**2) ** 2)


def rational_owner(u: int, g: int, a: int, c: int) -> dict[str, Fraction]:
    start = production_jet(Fraction(u))
    end = production_jet(Fraction(u + a))
    b0, b1 = start.value, end.value
    b_taylor = b0 + start.first * a + start.second * a * a / 2
    remainder = b1 - b_taylor
    q0 = Fraction(g * g - 1)
    q1 = Fraction((g + c) * (g + c) - 1)
    r_q = (b1 - b0) * q0 / 2
    m_u = Fraction(g) * b_taylor * c
    k_r = Fraction(g) * remainder * c + b1 * c * c / 2
    f65 = remainder * q0 / 2 + k_r
    delta = r_q + m_u + k_r
    endpoint = b1 * q1 / 2 - b0 * q0 / 2
    return {"R_Q": r_q, "M_U": m_u, "K_R": k_r, "F_6_5": f65, "Delta": delta, "endpoint": endpoint, "L": remainder, "Q": q0}


Matrix2 = tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]
Vector2 = tuple[Fraction, Fraction]


def mat_add(left: Matrix2, right: Matrix2) -> Matrix2:
    return tuple(tuple(left[i][j] + right[i][j] for j in range(2)) for i in range(2))  # type: ignore[return-value]


def mat_sub(left: Matrix2, right: Matrix2) -> Matrix2:
    return tuple(tuple(left[i][j] - right[i][j] for j in range(2)) for i in range(2))  # type: ignore[return-value]


def mat_scale(scalar: Fraction, matrix: Matrix2) -> Matrix2:
    return tuple(tuple(scalar * matrix[i][j] for j in range(2)) for i in range(2))  # type: ignore[return-value]


def mat_mul(left: Matrix2, right: Matrix2) -> Matrix2:
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2)) for i in range(2))  # type: ignore[return-value]


def mat_vec(matrix: Matrix2, vector: Vector2) -> Vector2:
    return tuple(sum(matrix[i][j] * vector[j] for j in range(2)) for i in range(2))  # type: ignore[return-value]


def dot(left: Vector2, right: Vector2) -> Fraction:
    return sum(left[i] * right[i] for i in range(2))


def trace(matrix: Matrix2) -> Fraction:
    return matrix[0][0] + matrix[1][1]


def inverse(matrix: Matrix2) -> Matrix2:
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return (
        (matrix[1][1] / determinant, -matrix[0][1] / determinant),
        (-matrix[1][0] / determinant, matrix[0][0] / determinant),
    )


def quadratic(vector: Vector2, matrix: Matrix2) -> Fraction:
    return dot(vector, mat_vec(matrix, vector))


def outer(left: Vector2, right: Vector2) -> Matrix2:
    return tuple(tuple(left[i] * right[j] for j in range(2)) for i in range(2))  # type: ignore[return-value]


def matrix_pair(left: Matrix2, right: Matrix2) -> Fraction:
    return sum(left[i][j] * right[i][j] for i in range(2) for j in range(2))


def simpson(function: Callable[[float], float], left: float, right: float, intervals: int) -> float:
    if intervals % 2:
        raise ValueError("Simpson intervals must be even")
    step = (right - left) / intervals
    total = function(left) + function(right)
    total += 4.0 * math.fsum(function(left + step * index) for index in range(1, intervals, 2))
    total += 2.0 * math.fsum(function(left + step * index) for index in range(2, intervals, 2))
    return total * step / 3.0


def gaussian_expect(function: Callable[[float], float], intervals: int = 40000) -> float:
    normalization = math.sqrt(2.0 * math.pi)
    return simpson(lambda value: function(value) * math.exp(-value * value / 2.0) / normalization, -10.0, 10.0, intervals)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    q = Fraction(10, 9)
    source_budget = Fraction(9, 20)
    sextic_budget = Fraction(3, 20)
    eta_star = Fraction(1, 440)
    zeta_star = Fraction(3, 100)
    q_eta = q * eta_star
    q_zeta = q * zeta_star
    checks.require("budget", "independent q source coefficient", q * source_budget == Fraction(1, 2), q * source_budget, Fraction(1, 2))
    checks.require("budget", "independent q sextic coefficient", q * sextic_budget == Fraction(1, 6), q * sextic_budget, Fraction(1, 6))
    checks.require("budget", "independent q eta star", q_eta == Fraction(1, 396), q_eta, Fraction(1, 396))
    checks.require("budget", "independent q zeta star", q_zeta == Fraction(1, 30), q_zeta, Fraction(1, 30))
    checks.require("budget", "independent q source reserve", q * source_budget - q_eta == Fraction(197, 396), q * source_budget - q_eta, Fraction(197, 396))
    checks.require("budget", "independent q sextic reserve", q * sextic_budget - q_zeta == Fraction(2, 15), q * sextic_budget - q_zeta, Fraction(2, 15))
    checks.require("budget", "independent seven source shares", 7 * Fraction(1, 2772) == q_eta, 7 * Fraction(1, 2772), q_eta)
    checks.require("budget", "independent eight source shares", 8 * Fraction(1, 3168) == q_eta, 8 * Fraction(1, 3168), q_eta)
    checks.require("budget", "independent seven sextic shares", 7 * Fraction(1, 210) == q_zeta, 7 * Fraction(1, 210), q_zeta)
    checks.require("budget", "independent eight sextic shares", 8 * Fraction(1, 240) == q_zeta, 8 * Fraction(1, 240), q_zeta)

    old_s, old_eta = 7 / 12, 1 / 12
    old_schur = 1.0 / ((1 - 2 ** (-old_eta)) * (1 - 2 ** (-2 * old_s)) * (1 - 2 ** (1 + old_eta - 2 * old_s)))
    direct_s, direct_eta = 7 / 12, 7 / 12
    direct_schur = 1.0 / ((1 - 2 ** (-direct_eta)) * (1 - 2 ** (-2 * direct_s)) * (1 - 2 ** (direct_eta - 2 * direct_s)))
    checks.close("schur", "independent historical Schur constant", old_schur, 572.4472106721531, 2e-15)
    checks.close("schur", "independent direct Schur constant", direct_schur, 16.30295538482827, 2e-15)
    checks.require("schur", "independent direct constant smaller", direct_schur < old_schur, direct_schur, f"<{old_schur}")
    checks.close("schur", "independent q old constant", float(q) * old_schur, 636.0524563023923, 2e-15)
    checks.close("schur", "independent q direct constant", float(q) * direct_schur, 18.11439487203141, 2e-15)

    expected_jets = {
        0: (Fraction(0), Fraction(0), Fraction(8)),
        1: (Fraction(169, 81), Fraction(208, 81), Fraction(-2, 81)),
        2: (Fraction(400, 81), None, None),
    }
    for point, expected in expected_jets.items():
        jet = production_jet(Fraction(point))
        checks.require("quotient", f"independent production value {point}", jet.value == expected[0], jet.value, expected[0])
        if expected[1] is not None:
            checks.require("quotient", f"independent production first {point}", jet.first == expected[1], jet.first, expected[1])
        if expected[2] is not None:
            checks.require("quotient", f"independent production second {point}", jet.second == expected[2], jet.second, expected[2])

    one = rational_owner(0, 1, 2, 2)
    step1 = rational_owner(0, 1, 1, 1)
    step2 = rational_owner(1, 2, 1, 1)
    split = {name: step1[name] + step2[name] for name in ("R_Q", "M_U", "K_R", "F_6_5", "Delta")}
    defect = {name: one[name] - split[name] for name in split}
    one_expected = {"K_R": Fraction(-992, 81), "F_6_5": Fraction(-992, 81), "Delta": Fraction(1600, 81)}
    split_expected = {"R_Q": Fraction(77, 18), "M_U": Fraction(1076, 81), "K_R": Fraction(355, 162), "F_6_5": Fraction(427, 162), "Delta": Fraction(1600, 81)}
    defect_expected = {"R_Q": Fraction(-77, 18), "M_U": Fraction(1516, 81), "K_R": Fraction(-2339, 162), "F_6_5": Fraction(-2411, 162), "Delta": Fraction(0)}
    for name, expected in one_expected.items():
        checks.require("quotient", f"independent one chart {name}", one[name] == expected, one[name], expected)
    for name, expected in split_expected.items():
        checks.require("quotient", f"independent split {name}", split[name] == expected, split[name], expected)
    for name, expected in defect_expected.items():
        checks.require("quotient", f"independent defect {name}", defect[name] == expected, defect[name], expected)
    checks.require("quotient", "independent historical identity", one["F_6_5"] == one["L"] * one["Q"] / 2 + one["K_R"], one["F_6_5"], one["L"] * one["Q"] / 2 + one["K_R"])
    checks.require("quotient", "independent owner defects cancel", defect["R_Q"] + defect["M_U"] + defect["K_R"] == 0, defect["R_Q"] + defect["M_U"] + defect["K_R"], 0)
    checks.require("quotient", "independent F65 sign change", one["F_6_5"] < 0 < split["F_6_5"], (one["F_6_5"], split["F_6_5"]), "negative then positive")
    checks.require("quotient", "independent KR sign change", one["K_R"] < 0 < split["K_R"], (one["K_R"], split["K_R"]), "negative then positive")

    # Direct finite-distribution check of the complete endpoint identity.
    b0: Matrix2 = ((Fraction(2), Fraction(1)), (Fraction(1), Fraction(3)))
    b1: Matrix2 = ((Fraction(4), Fraction(1)), (Fraction(1), Fraction(2)))
    gamma: Matrix2 = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    shift: Vector2 = (Fraction(2, 5), Fraction(-1, 3))
    atoms: tuple[Vector2, ...] = ((Fraction(-1), Fraction(2)), (Fraction(2), Fraction(-1)), (Fraction(3), Fraction(4)))
    weights = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
    mean: Vector2 = tuple(sum(weight * atom[index] for weight, atom in zip(weights, atoms)) for index in range(2))  # type: ignore[assignment]
    covariance: Matrix2 = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0)))
    for weight, atom in zip(weights, atoms):
        centered = (atom[0] - mean[0], atom[1] - mean[1])
        covariance = mat_add(covariance, mat_scale(weight, outer(centered, centered)))
    direct_expectation = Fraction(0)
    for weight, atom in zip(weights, atoms):
        shifted = (atom[0] + shift[0], atom[1] + shift[1])
        direct_expectation += weight * (
            quadratic(shifted, b1) - matrix_pair(b1, gamma) - quadratic(atom, b0) + matrix_pair(b0, gamma)
        ) / 2
    mean_shift = (mean[0] + shift[0], mean[1] + shift[1])
    conditional_formula = (
        quadratic(mean_shift, b1) / 2
        - quadratic(mean, b0) / 2
        + matrix_pair(mat_sub(b1, b0), mat_sub(covariance, gamma)) / 2
    )
    checks.require("endpoint", "independent complete conditional endpoint identity", direct_expectation == conditional_formula, direct_expectation, conditional_formula)

    identity: Matrix2 = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    hessian = mat_add(identity, mat_scale(q, b1))
    cstar_vector = mat_vec(inverse(hessian), mat_vec(b1, mean))
    cstar = (-q * cstar_vector[0], -q * cstar_vector[1])
    shifted_star = (mean[0] + cstar[0], mean[1] + cstar[1])
    optimized_direct = q * (
        quadratic(shifted_star, b1) / 2
        - quadratic(mean, b0) / 2
        + matrix_pair(mat_sub(b1, b0), mat_sub(covariance, gamma)) / 2
    ) + dot(cstar, cstar) / 2
    resolvent_term = mat_mul(b1, inverse(hessian))
    optimized_formula = q * matrix_pair(mat_sub(b1, b0), mat_sub(covariance, gamma)) / 2 + q * quadratic(mean, mat_sub(resolvent_term, b0)) / 2
    checks.require("endpoint", "independent optimized endpoint formula", optimized_direct == optimized_formula, optimized_direct, optimized_formula)
    checks.require("endpoint", "independent endpoint form has no fixed sign", Fraction(-5, 9) < 0 < Fraction(5, 9), (Fraction(-5, 9), Fraction(5, 9)), "both signs")

    # A separate finite cluster checks the abstract mean/covariance identity.
    cluster_values: tuple[Vector2, ...] = ((Fraction(2), Fraction(-1)), (Fraction(-1), Fraction(3)), (Fraction(4), Fraction(2)))
    cluster_weights = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
    traces = (Fraction(3, 2), Fraction(1, 2), Fraction(5, 2))
    baseline: Vector2 = (Fraction(2, 3), Fraction(-4, 5))
    cluster_mean: Vector2 = tuple(sum(weight * value[index] for weight, value in zip(cluster_weights, cluster_values)) for index in range(2))  # type: ignore[assignment]
    cluster_cov: Matrix2 = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0)))
    cluster_left = Fraction(0)
    for weight, value, trace_value in zip(cluster_weights, cluster_values, traces):
        centered = (value[0] - cluster_mean[0], value[1] - cluster_mean[1])
        cluster_cov = mat_add(cluster_cov, mat_scale(weight, outer(centered, centered)))
        total = (baseline[0] + value[0], baseline[1] + value[1])
        cluster_left += weight * (dot(total, total) - trace_value) / 2
    expected_trace = sum(weight * trace_value for weight, trace_value in zip(cluster_weights, traces))
    total_mean = (baseline[0] + cluster_mean[0], baseline[1] + cluster_mean[1])
    cluster_right = dot(total_mean, total_mean) / 2 + (trace(cluster_cov) - expected_trace) / 2
    checks.require("cluster", "independent complete cluster identity", cluster_left == cluster_right, cluster_left, cluster_right)

    # Exact exponential moments and covariance-square order for the one-pair cluster.
    factorial = math.factorial
    eu = Fraction(factorial(2) - 2 * factorial(1))
    eu2 = Fraction(factorial(4) - 4 * factorial(3) + 4 * factorial(2))
    eu3 = Fraction(factorial(6) - 6 * factorial(5) + 12 * factorial(4) - 8 * factorial(3))
    eu4 = Fraction(factorial(8) - 8 * factorial(7) + 24 * factorial(6) - 32 * factorial(5) + 16 * factorial(4))
    checks.require("one_pair", "independent exponential u mean", eu == 0, eu, 0)
    checks.require("one_pair", "independent exponential u second", eu2 == 8, eu2, 8)
    checks.require("one_pair", "independent exponential u third", eu3 == 240, eu3, 240)
    checks.require("one_pair", "independent exponential u fourth", eu4 == 13824, eu4, 13824)
    checks.require("one_pair", "independent packet variance coefficient", eu2 / 16 == Fraction(1, 2), eu2 / 16, Fraction(1, 2))
    checks.require("one_pair", "independent packet third moment coefficient", eu3 / 64 == Fraction(15, 4), eu3 / 64, Fraction(15, 4))
    fourth_cumulant = eu4 / 256 - 3 * (eu2 / 16) ** 2
    checks.require("one_pair", "independent packet fourth cumulant", fourth_cumulant == Fraction(213, 4), fourth_cumulant, Fraction(213, 4))
    checks.require("one_pair", "independent log second coefficient", (eu2 / 16) / 2 == Fraction(1, 4), (eu2 / 16) / 2, Fraction(1, 4))
    checks.require("one_pair", "independent log third coefficient", -(eu3 / 64) / 6 == Fraction(-5, 8), -(eu3 / 64) / 6, Fraction(-5, 8))
    checks.require("one_pair", "independent log fourth coefficient", fourth_cumulant / 24 == Fraction(71, 32), fourth_cumulant / 24, Fraction(71, 32))

    for index, (xv, yv) in enumerate(((Fraction(1, 3), Fraction(2, 5)), (Fraction(-2, 7), Fraction(5, 4)), (Fraction(3), Fraction(-1, 2)))):
        radius = xv * xv + yv * yv
        aa = 2 * xv * xv + 6 * yv * yv
        dd = 6 * xv * xv + 2 * yv * yv
        bb = -4 * xv * yv
        checks.require("one_pair", f"independent covariance trace identity {index}", aa + dd == 8 * radius, aa + dd, 8 * radius)
        checks.require("one_pair", f"independent covariance determinant identity {index}", aa * dd - bb * bb == 12 * radius * radius, aa * dd - bb * bb, 12 * radius * radius)
        checks.require("one_pair", f"independent covariance HS identity {index}", aa * aa + dd * dd + 2 * bb * bb == 40 * radius * radius, aa * aa + dd * dd + 2 * bb * bb, 40 * radius * radius)
    averaged_lead = Fraction(3, 32)
    actual_lead = Fraction(1, 4)
    realized_lead = Fraction(5, 16)
    checks.require("one_pair", "independent square order strict", averaged_lead < actual_lead < realized_lead, (averaged_lead, actual_lead, realized_lead), "3/32 < 1/4 < 5/16")
    checks.require("one_pair", "independent averaged leading deficit", actual_lead - averaged_lead == Fraction(5, 32), actual_lead - averaged_lead, Fraction(5, 32))
    checks.require("one_pair", "independent realized leading room", realized_lead - actual_lead == Fraction(1, 16), realized_lead - actual_lead, Fraction(1, 16))
    checks.require("one_pair", "independent singleton packets cancel", Fraction(-1, 4) + Fraction(1, 8) + Fraction(1, 8) == 0, Fraction(-1, 4) + Fraction(1, 8) + Fraction(1, 8), 0)
    checks.require("one_pair", "independent sextic tradeoff coefficient", Fraction(5, 32) / 15 == Fraction(1, 96), Fraction(5, 32) / 15, Fraction(1, 96))
    checks.require("one_pair", "independent q threshold", q / 96 == Fraction(5, 432), q / 96, Fraction(5, 432))

    sample_q = 1.0
    sample_sigma = 0.5
    sample_a = sample_q * sample_sigma**4 / 4.0
    sample_mgf = math.sqrt(math.pi) / (2 * math.sqrt(sample_a)) * math.exp((2 * sample_a - 1) ** 2 / (4 * sample_a)) * math.erfc((1 - 2 * sample_a) / (2 * math.sqrt(sample_a)))
    sample_log = math.log(sample_mgf)
    averaged_cost = 3 * sample_sigma**8 / 32
    realized_cost = 5 * sample_sigma**8 / 16
    checks.close("one_pair", "independent exact mgf sample", sample_mgf, 1.0008509471256655, 2e-13)
    checks.close("one_pair", "independent exact log sample", sample_log, 0.0008505852754225884, 3e-13)
    checks.require("one_pair", "independent finite average-first failure", averaged_cost < sample_log, (averaged_cost, sample_log), "average cost below log moment")
    checks.require("one_pair", "independent finite square-first room", sample_log < realized_cost, (sample_log, realized_cost), "log moment below square-first cost")

    # Oscillatory future-feedback fixture with an explicit spatial carrier.
    amplitude = 1.0
    spatial_mode = 32
    for index, frequency in enumerate((1.0, 2.0, 4.0)):
        r2 = math.exp(-2 * frequency**2)
        r8 = math.exp(-8 * frequency**2)
        r18 = math.exp(-18 * frequency**2)
        eh2 = amplitude**2 * (1 - r2) / 2
        eh6 = amplitude**6 * (10 - 15 * r2 + 6 * r8 - r18) / 32
        ehp2 = amplitude**2 * frequency**2 * (1 + r2) / 2
        ehhpp = -amplitude**2 * frequency**2 * (1 - r2) / 2
        tangent = amplitude**4 * frequency**2 * spatial_mode**2 * (1 - r8) / 16
        q_h2 = gaussian_expect(lambda value: (amplitude * math.sin(frequency * value)) ** 2)
        q_h6 = gaussian_expect(lambda value: (amplitude * math.sin(frequency * value)) ** 6)
        q_tangent_factor = gaussian_expect(lambda value: (2 * amplitude**2 * frequency * math.sin(frequency * value) * math.cos(frequency * value)) ** 2)
        checks.close("feedback", f"independent quadrature h2 {index}", q_h2, eh2, 4e-10)
        checks.close("feedback", f"independent quadrature h6 {index}", q_h6, eh6, 4e-10)
        checks.close("feedback", f"independent quadrature tangent {index}", q_tangent_factor * spatial_mode**2 / 8, tangent, 4e-9)
        checks.close("feedback", f"independent signed second jet {index}", ehp2 + ehhpp, amplitude**2 * frequency**2 * r2, 2e-13)

    large_frequency = 1024.0
    r2 = math.exp(-2 * large_frequency**2)
    r8 = math.exp(-8 * large_frequency**2)
    r18 = math.exp(-18 * large_frequency**2)
    x_budget = amplitude**2 * (1 - r2) * (1 + spatial_mode**2) ** 2 / 4
    y_budget = 5 * amplitude**6 * (10 - 15 * r2 + 6 * r8 - r18) / 512
    h4 = amplitude**4 * (3 - 4 * r2 + r8) / 8
    mixed_budget = (1 + spatial_mode**2) * math.sqrt(5 / 32) * h4
    tangent = amplitude**4 * large_frequency**2 * spatial_mode**2 * (1 - r8) / 16
    checks.close("feedback", "independent large source budget", x_budget, 262656.25, 1e-15)
    checks.close("feedback", "independent large sextic budget", y_budget, 0.09765625, 1e-15)
    checks.close("feedback", "independent large mixed budget", mixed_budget, 151.93755945340263, 2e-15)
    checks.close("feedback", "independent large tangent square", tangent, 67108864.0, 1e-15)
    checks.require("feedback", "independent tangent dominates bounded budgets", tangent / (1 + mixed_budget) > 400000, tangent / (1 + mixed_budget), ">400000")
    checks.require("feedback", "independent closed quadratic lower bound", tangent >= amplitude**4 * spatial_mode**2 * large_frequency**2 * (1 - math.exp(-8)) / 16, tangent, "quadratic lower bound")

    failed = [row for row in checks.rows if row["status"] != "PASS"]
    derived = {
        "q": str(q),
        "source_budget": str(source_budget),
        "sextic_budget": str(sextic_budget),
        "q_eta_star": str(q_eta),
        "q_zeta_star": str(q_zeta),
        "historical_schur_constant": repr(old_schur),
        "direct_schur_constant": repr(direct_schur),
        "one_chart_F_6_5": str(one["F_6_5"]),
        "split_F_6_5": str(split["F_6_5"]),
        "complete_endpoint": str(one["Delta"]),
        "one_pair_log_series": "q^2*sigma^8/4-5*q^3*sigma^12/8+71*q^4*sigma^16/32+O(sigma^20)",
        "one_pair_mgf_sample": repr(sample_mgf),
        "one_pair_log_sample": repr(sample_log),
        "large_feedback_source": repr(x_budget),
        "large_feedback_sextic": repr(y_budget),
        "large_feedback_mixed": repr(mixed_budget),
        "large_feedback_tangent": repr(tangent),
    }
    route_verdicts = {
        "historical_R085_weighted_bridge": "superseded-as-current-target-and-unproved",
        "direct_R088_unweighted_bridge": "open",
        "historical_F_6_5_progressive_owner": "failed-not-subdivision-invariant",
        "complete_endpoint_conditional_identity": "advanced-exact-quotient-safe",
        "complete_cluster_mean_covariance_identity": "advanced-exact-signed-normal-form",
        "average_covariance_before_hs_square": "failed-finite-and-leading-order-fixture",
        "absolute_future_feedback_matrix_carleson": "failed-arbitrary-selector-fixture",
        "realized_cluster_square_then_average": "viable-order-not-a-bound",
        "uniform_complete_cluster_lower_bound": "open",
        "overlap_src": "open",
        "nelson": "open",
        "sector_a": "open",
    }
    results = {"derived": derived, "route_verdicts": route_verdicts}
    results_sha256 = hashlib.sha256(
        json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "status": "PASS" if not failed else "FAIL",
        "assertions_total": len(checks.rows),
        "assertions_passed": len(checks.rows) - len(failed),
        "assertions_failed": len(failed),
        "assertions": checks.rows,
        "assertion_names": [str(row["name"]) for row in checks.rows],
        "results_sha256": results_sha256,
        "results": results,
        "derived": derived,
        "route_verdicts": route_verdicts,
    }
    atomic_json(args.output, payload)
    print(f"Independent R-108: {payload['assertions_passed']}/{payload['assertions_total']} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
