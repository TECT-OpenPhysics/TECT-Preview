#!/usr/bin/env python3
"""Independent standard-library certificate for the scoped R-107 boundary.

This implementation does not import the primary certificate or any symbolic,
array, or scientific-computing package.  It uses exact Fractions, explicit
finite-tree conditioning, hand 2x2 determinants, and numerical quadrature only
as an independent cross-check of closed Gaussian formulas.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Callable


SCHEMA = "tect/a13-coherent-output-cluster-predictable-baseline-boundary-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-coherent-output-cluster-predictable-baseline-boundary/result.json"
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

    def close(self, group: str, name: str, actual: float, expected: float, tolerance: float) -> None:
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


def simpson(function: Callable[[float], float], left: float, right: float, intervals: int) -> float:
    if intervals % 2:
        raise ValueError("Simpson intervals must be even")
    step = (right - left) / intervals
    total = function(left) + function(right)
    total += 4.0 * math.fsum(function(left + step * index) for index in range(1, intervals, 2))
    total += 2.0 * math.fsum(function(left + step * index) for index in range(2, intervals, 2))
    return total * step / 3.0


def gaussian_expect(function: Callable[[float], float], intervals: int = 60000) -> float:
    normalization = math.sqrt(2.0 * math.pi)
    return simpson(lambda value: function(value) * math.exp(-value * value / 2.0) / normalization, -10.0, 10.0, intervals)


def det2(matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def add2(
    left: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
    right: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    return tuple(tuple(left[row][column] + right[row][column] for column in range(2)) for row in range(2))  # type: ignore[return-value]


def scale2(
    scalar: Fraction,
    matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    return tuple(tuple(scalar * matrix[row][column] for column in range(2)) for row in range(2))  # type: ignore[return-value]


def identity_plus_q(matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]], q: Fraction) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    scaled = scale2(q, matrix)
    return ((1 + scaled[0][0], scaled[0][1]), (scaled[1][0], 1 + scaled[1][1]))


def transpose(matrix: tuple[tuple[Fraction, ...], ...]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(matrix[row][column] for row in range(len(matrix))) for column in range(len(matrix[0])))


def multiply(
    left: tuple[tuple[Fraction, ...], ...],
    right: tuple[tuple[Fraction, ...], ...],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(sum(left[row][inner] * right[inner][column] for inner in range(len(right))) for column in range(len(right[0])))
        for row in range(len(left))
    )


def trace(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    return sum(matrix[index][index] for index in range(len(matrix)))


def conditional_expectation(
    values: dict[tuple[int, int, int], Fraction], revealed: int
) -> dict[tuple[int, int, int], Fraction]:
    groups: dict[tuple[int, ...], list[Fraction]] = {}
    for atom, value in values.items():
        groups.setdefault(atom[:revealed], []).append(value)
    means = {prefix: sum(entries, Fraction(0)) / len(entries) for prefix, entries in groups.items()}
    return {atom: means[atom[:revealed]] for atom in values}


def double_factorial_odd(order_minus_one: int) -> int:
    if order_minus_one <= 0:
        return 1
    product = 1
    for value in range(order_minus_one, 0, -2):
        product *= value
    return product


def gaussian_even_moment(power: int, variance: Fraction) -> Fraction:
    if power % 2:
        return Fraction(0)
    return Fraction(double_factorial_odd(power - 1)) * variance ** (power // 2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    q = Fraction(10, 9)
    source_budget = Fraction(9, 20)
    sextic_budget = Fraction(3, 20)
    checks.require("budget", "independent q source coefficient", q * source_budget == Fraction(1, 2), q * source_budget, Fraction(1, 2))
    checks.require("budget", "independent q sextic coefficient", q * sextic_budget == Fraction(1, 6), q * sextic_budget, Fraction(1, 6))

    # A distinct two-atom likelihood verifies both entropy orientations and
    # their variance-production integrals without symbolic algebra.
    base_probabilities = (0.5, 0.5)
    exponential_likelihood = (0.5, 1.5)
    likelihood = tuple(math.log(value) for value in exponential_likelihood)
    normalizer = sum(probability * value for probability, value in zip(base_probabilities, exponential_likelihood))
    self_probabilities = tuple(probability * value / normalizer for probability, value in zip(base_probabilities, exponential_likelihood))
    forward_kl = sum(probability * math.log(probability / base) for probability, base in zip(self_probabilities, base_probabilities))
    reverse_kl = sum(probability * math.log(probability / target) for probability, target in zip(base_probabilities, self_probabilities))

    def tilted_variance(parameter: float) -> float:
        weights = tuple(base_probabilities[index] * math.exp(parameter * likelihood[index]) for index in range(2))
        total = sum(weights)
        probabilities = tuple(weight / total for weight in weights)
        mean = sum(probabilities[index] * likelihood[index] for index in range(2))
        return sum(probabilities[index] * (likelihood[index] - mean) ** 2 for index in range(2))

    forward_integral = simpson(lambda parameter: parameter * tilted_variance(parameter), 0.0, 1.0, 20000)
    reverse_integral = simpson(lambda parameter: (1.0 - parameter) * tilted_variance(parameter), 0.0, 1.0, 20000)
    checks.close("entropy", "two-atom likelihood normalizer", normalizer, 1.0, 1e-14)
    checks.close("entropy", "two-atom self first mass", self_probabilities[0], 0.25, 1e-14)
    checks.close("entropy", "two-atom self second mass", self_probabilities[1], 0.75, 1e-14)
    checks.close("entropy", "two-atom forward entropy production", forward_integral, forward_kl, 2e-11)
    checks.close("entropy", "two-atom reverse entropy production", reverse_integral, reverse_kl, 2e-11)
    checks.close("entropy", "two-atom forward KL closed form", forward_kl, 0.75 * math.log(3.0) - math.log(2.0), 1e-14)
    checks.close("entropy", "two-atom reverse KL closed form", reverse_kl, 0.5 * math.log(4.0 / 3.0), 1e-14)

    # Exact scalar backward likelihood martingale.
    det_total = 1 + q * (Fraction(1) + Fraction(4))
    det_tail = 1 + q * Fraction(4)
    checks.require("martingale", "independent scalar total determinant", det_total == Fraction(59, 9), det_total, Fraction(59, 9))
    checks.require("martingale", "independent scalar tail determinant", det_tail == Fraction(49, 9), det_tail, Fraction(49, 9))

    def gaussian_quadratic(coupling: float, shift: float, coefficient: float) -> float:
        denominator = 1.0 + 2.0 * coupling * coefficient * coefficient
        return math.exp(-coupling * shift * shift / denominator) / math.sqrt(denominator)

    for index, first_root in enumerate((-2.0, -0.5, 0.0, 1.25, 3.0)):
        conditional = math.sqrt(float(det_total)) * gaussian_quadratic(float(q) / 2.0, first_root, 2.0)
        m1 = math.sqrt(float(det_total / det_tail)) * math.exp(-float(Fraction(5, 49)) * first_root * first_root)
        checks.close("martingale", f"conditional M2 equals M1 sample {index}", conditional, m1, 2e-14)
    mean_m1 = math.sqrt(float(det_total / det_tail)) / math.sqrt(1.0 + 2.0 * float(Fraction(5, 49)))
    checks.close("martingale", "independent mean M1", mean_m1, 1.0, 2e-14)
    determinant_debt = 0.5 * (float(q * 5) - math.log(float(det_total)))
    checks.require("martingale", "independent determinant debt positive", determinant_debt > 0.0, determinant_debt, ">0")

    # Independent bounded adaptive-row counterfixture.  With A1=1 and
    # A2=1_{|x1|>1}, the candidate first density uses different Gaussian
    # precisions inside and outside the threshold.
    q_float = float(q)
    beta_inner = 1 + q
    beta_outer = (1 + 2 * q) / (1 + q)
    inner_argument = math.sqrt(float(beta_inner) / 2.0)
    outer_argument = math.sqrt(float(beta_outer) / 2.0)
    inner_mass = math.erf(inner_argument)
    outer_mass = math.erfc(outer_argument)
    adaptive_mass = inner_mass + outer_mass
    adaptive_defect = adaptive_mass - 1.0
    checks.require(
        "martingale-boundary",
        "hand adaptive inner precision",
        beta_inner == Fraction(19, 9),
        beta_inner,
        Fraction(19, 9),
    )
    checks.require(
        "martingale-boundary",
        "hand adaptive outer precision",
        beta_outer == Fraction(29, 19),
        beta_outer,
        Fraction(29, 19),
    )
    checks.require(
        "martingale-boundary",
        "adaptive erf arguments ordered",
        inner_argument > outer_argument,
        (inner_argument, outer_argument),
        "inner>outer",
    )
    checks.close(
        "martingale-boundary",
        "adaptive combined closed-form oracle",
        adaptive_mass,
        1.070433115292664,
        5e-15,
    )
    checks.require(
        "martingale-boundary",
        "adaptive normalization defect bracket",
        0.0704 < adaptive_defect < 0.0705,
        adaptive_defect,
        "(0.0704,0.0705)",
    )
    checks.close(
        "martingale-boundary",
        "fixed zero-row normalization guard",
        math.erf(inner_argument) + math.erfc(inner_argument),
        1.0,
        2e-15,
    )
    checks.close(
        "martingale-boundary",
        "fixed one-row normalization guard",
        math.erf(outer_argument) + math.erfc(outer_argument),
        1.0,
        2e-15,
    )
    normalization = math.sqrt(2.0 * math.pi)
    inner_density = lambda value: math.sqrt(float(beta_inner)) * math.exp(-float(beta_inner) * value * value / 2.0) / normalization
    outer_density = lambda value: math.sqrt(float(beta_outer)) * math.exp(-float(beta_outer) * value * value / 2.0) / normalization
    adaptive_quadrature = (
        simpson(outer_density, -10.0, -1.0, 30000)
        + simpson(inner_density, -1.0, 1.0, 30000)
        + simpson(outer_density, 1.0, 10.0, 30000)
    )
    checks.close(
        "martingale-boundary",
        "adaptive piecewise quadrature",
        adaptive_quadrature,
        adaptive_mass,
        2e-12,
    )
    checks.require(
        "martingale-boundary",
        "adaptive row mean exceeds one",
        adaptive_mass > 1.07,
        adaptive_mass,
        ">1.07",
    )

    # Hand 2x2 determinant and Schur audit.
    t1 = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)))
    t2 = ((Fraction(1), Fraction(1)), (Fraction(1), Fraction(1)))
    det1 = det2(identity_plus_q(t1, q))
    det2_value = det2(identity_plus_q(t2, q))
    det12 = det2(identity_plus_q(add2(t1, t2), q))
    ratio12 = det12 / det1
    ratio21 = det12 / det2_value
    checks.require("schur", "hand first determinant", det1 == Fraction(19, 9), det1, Fraction(19, 9))
    checks.require("schur", "hand second determinant", det2_value == Fraction(29, 9), det2_value, Fraction(29, 9))
    checks.require("schur", "hand combined determinant", det12 == Fraction(451, 81), det12, Fraction(451, 81))
    checks.require("schur", "hand first Schur ratio", ratio12 == Fraction(451, 171), ratio12, Fraction(451, 171))
    checks.require("schur", "hand second Schur ratio", ratio21 == Fraction(451, 261), ratio21, Fraction(451, 261))
    checks.require("schur", "hand sequential products", det1 * ratio12 == det2_value * ratio21 == det12, (det1 * ratio12, det2_value * ratio21), det12)
    independent_ratio = det1 * det2_value / det12
    checks.require("schur", "hand independent normalizer ratio", independent_ratio == Fraction(551, 451), independent_ratio, Fraction(551, 451))
    checks.require("schur", "hand independent normalizer slack", math.log(float(independent_ratio)) / 2.0 > 0.0, math.log(float(independent_ratio)) / 2.0, ">0")
    repeated_ratio = Fraction(5, 3) ** 4 / Fraction(11, 3)
    checks.require("schur", "hand repeated-row ratio", repeated_ratio == Fraction(625, 297), repeated_ratio, Fraction(625, 297))
    checks.require("schur", "hand repeated-row slack", math.log(float(repeated_ratio)) / 2.0 > 0.0, math.log(float(repeated_ratio)) / 2.0, ">0")
    asymptotic_slope = math.log(1.0 + float(q * Fraction(3, 5))) / 2.0
    for rows in (10, 100, 1000, 10000):
        slack_per_row = 0.5 * (math.log1p(float(q * Fraction(3, 5))) - math.log1p(float(q * Fraction(3, 5) * rows)) / rows)
        checks.require("schur", f"repeated slack slope approach {rows}", 0.0 < slack_per_row < asymptotic_slope, slack_per_row, f"(0,{asymptotic_slope})")

    # One-pair output-cluster moments, independently from radial chi-square
    # moments rather than Fourier symbolic algebra.
    for index, variance in enumerate((Fraction(1), Fraction(3, 2), Fraction(7, 3))):
        ez2 = (gaussian_even_moment(2, variance) + gaussian_even_moment(2, variance)) / 4
        ez4 = (
            gaussian_even_moment(4, variance)
            + 2 * gaussian_even_moment(2, variance) ** 2
            + gaussian_even_moment(4, variance)
        ) / 16
        packet0 = -variance * ez2 / 2
        packet2 = (ez4 - variance * ez2 / 2) / 2
        complete = packet0 + 2 * packet2
        checks.require("cluster", f"independent radial second moment {index}", ez2 == variance / 2, ez2, variance / 2)
        checks.require("cluster", f"independent radial fourth moment {index}", ez4 == variance**2 / 2, ez4, variance**2 / 2)
        checks.require("cluster", f"independent zero output negative {index}", packet0 == -variance**2 / 4, packet0, -variance**2 / 4)
        checks.require("cluster", f"independent side output positive {index}", packet2 == variance**2 / 8, packet2, variance**2 / 8)
        checks.require("cluster", f"independent cluster cancellation {index}", complete == 0, complete, 0)

    # Exact finite-tree predictable-baseline/Doob reconstruction.
    atoms = tuple(itertools.product((-1, 1), repeat=3))
    scales = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 4))
    shifts: dict[int, dict[tuple[int, int, int], Fraction]] = {
        1: {atom: Fraction(1, 5) for atom in atoms},
        2: {atom: Fraction(atom[0], 3) for atom in atoms},
        3: {atom: Fraction(atom[0] * atom[1], 7) for atom in atoms},
    }
    base = {atom: sum(scales[index] * atom[index] for index in range(3)) for atom in atoms}
    base_fourth_mean = sum(value**4 for value in base.values()) / len(atoms)
    states: dict[int, dict[tuple[int, int, int], Fraction]] = {0: dict(base)}
    for step in range(1, 4):
        states[step] = {
            atom: states[step - 1][atom] + scales[step - 1] * shifts[step][atom]
            for atom in atoms
        }
    potential = {step: {atom: value**4 - base_fourth_mean for atom, value in states[step].items()} for step in range(4)}
    increments = {
        step: {atom: potential[step][atom] - potential[step - 1][atom] for atom in atoms}
        for step in range(1, 4)
    }
    for atom in atoms:
        telescope = sum(increments[step][atom] for step in range(1, 4))
        checks.require("baseline", f"finite-tree endpoint telescope {atom}", telescope == potential[3][atom] - potential[0][atom], telescope, potential[3][atom] - potential[0][atom])
    predictable: dict[int, dict[tuple[int, int, int], Fraction]] = {}
    innovations: dict[tuple[int, int], dict[tuple[int, int, int], Fraction]] = {}
    for step in range(1, 4):
        predictable[step] = conditional_expectation(increments[step], step - 1)
        for reveal in range(step, 4):
            high = conditional_expectation(increments[step], reveal)
            low = conditional_expectation(increments[step], reveal - 1)
            innovations[(reveal, step)] = {atom: high[atom] - low[atom] for atom in atoms}
        for atom in atoms:
            reconstructed = predictable[step][atom] + sum(innovations[(reveal, step)][atom] for reveal in range(step, 4))
            checks.require("baseline", f"finite-tree Doob reconstruction step {step} atom {atom}", reconstructed == increments[step][atom], reconstructed, increments[step][atom])
    for (reveal, step), values in innovations.items():
        centered = conditional_expectation(values, reveal - 1)
        checks.require("baseline", f"finite-tree innovation centered {reveal}-{step}", all(value == 0 for value in centered.values()), set(centered.values()), {Fraction(0)})
    expected_base = sum(potential[0].values()) / len(atoms)
    expected_terminal = sum(potential[3].values()) / len(atoms)
    expected_predictable = sum(sum(predictable[step].values()) / len(atoms) for step in range(1, 4))
    checks.require("baseline", "finite-tree centered base", expected_base == 0, expected_base, 0)
    checks.require("baseline", "finite-tree predictable action identity", expected_terminal == expected_predictable, expected_terminal, expected_predictable)
    checks.require("baseline", "finite-tree nonvacuous predictable packet", any(value != 0 for values in predictable.values() for value in values.values()), "nonzero", "nonzero")
    checks.require("baseline", "finite-tree nonvacuous innovation", any(value != 0 for values in innovations.values() for value in values.values()), "nonzero", "nonzero")

    # Covariance mass and its Pythagorean subdivision, with exact hand loops.
    dmat = ((Fraction(2), Fraction(1)), (Fraction(1), Fraction(3)))
    smat1 = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(2)))
    smat2 = ((Fraction(1), Fraction(1)), (Fraction(0), Fraction(1)))

    def mass(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
        return trace(multiply(multiply(transpose(matrix), dmat), matrix))

    covariance1 = multiply(smat1, transpose(smat1))
    covariance2 = multiply(smat2, transpose(smat2))
    total_covariance = tuple(tuple(covariance1[row][column] + covariance2[row][column] for column in range(2)) for row in range(2))
    mass_left = mass(smat1) + mass(smat2)
    mass_right = trace(multiply(dmat, total_covariance))
    checks.require("covariance", "independent covariance mass", mass_left == mass_right, mass_left, mass_right)
    split1 = tuple(tuple(Fraction(3, 5) * value for value in row) for row in smat1)
    split2 = tuple(tuple(Fraction(4, 5) * value for value in row) for row in smat1)
    checks.require("covariance", "independent subdivision mass", mass(split1) + mass(split2) == mass(smat1), mass(split1) + mass(split2), mass(smat1))
    random_heat_guard = gaussian_even_moment(4, Fraction(1)) - gaussian_even_moment(2, Fraction(1))
    checks.require("covariance", "independent same-root random heat guard", random_heat_guard == 2, random_heat_guard, 2)

    # Direct Gaussian quadrature checks of the adapted sine formulas.
    amplitude = 1.25
    for index, frequency in enumerate((1.0, 2.0, 4.0)):
        decay = math.exp(-2.0 * frequency * frequency)
        expected_h2 = amplitude**2 * (1.0 - decay) / 2.0
        expected_dh2 = amplitude**2 * frequency**2 * (1.0 + decay) / 2.0
        expected_hddh = -amplitude**2 * frequency**2 * (1.0 - decay) / 2.0
        numerical_h2 = gaussian_expect(lambda value: (amplitude * math.sin(frequency * value)) ** 2)
        numerical_dh2 = gaussian_expect(lambda value: (amplitude * frequency * math.cos(frequency * value)) ** 2)
        numerical_hddh = gaussian_expect(lambda value: -amplitude**2 * frequency**2 * math.sin(frequency * value) ** 2)
        numerical_hermite = gaussian_expect(lambda value: (amplitude * math.sin(frequency * value)) ** 2 * (value * value - 1.0))
        checks.close("second_jet", f"quadrature h2 {index}", numerical_h2, expected_h2, 2e-10)
        checks.close("second_jet", f"quadrature dh2 {index}", numerical_dh2, expected_dh2, 2e-10)
        checks.close("second_jet", f"quadrature h hdd {index}", numerical_hddh, expected_hddh, 2e-10)
        checks.close("second_jet", f"quadrature Hermite pairing {index}", numerical_hermite, 2.0 * amplitude**2 * frequency**2 * decay, 2e-9)
        checks.close("second_jet", f"signed companion formula {index}", expected_dh2 + expected_hddh, amplitude**2 * frequency**2 * decay, 2e-13)
    checks.require("second_jet", "separated companion growth", amplitude**2 * 100.0**2 / 2.0 > 1000.0, amplitude**2 * 100.0**2 / 2.0, ">1000")
    checks.require("second_jet", "signed companion decay", amplitude**2 * 10.0**2 * math.exp(-200.0) < 1e-80, amplitude**2 * 10.0**2 * math.exp(-200.0), "<1e-80")

    # Carrier mutual information, derived both from covariance determinant and
    # conditional Gaussian KL.
    for index, (dimension, parameter) in enumerate(((1, 0.25), (6, 0.25), (6, 1.0 / 9.0), (12, 0.5))):
        determinant_route = -0.5 * math.log(parameter**dimension)
        conditional_route = 0.5 * dimension * (parameter - 1.0 - math.log(parameter) + 1.0 - parameter)
        checks.close("carrier", f"carrier routes agree {index}", determinant_route, conditional_route, 2e-13)
    checks.close("carrier", "independent quarter bridge", -0.5 * math.log(0.25), math.log(2.0), 1e-14)
    checks.close("carrier", "independent six-dimensional ninth bridge", -3.0 * math.log(1.0 / 9.0), 6.0 * math.log(3.0), 1e-14)
    bridge_sequence = tuple(-3.0 * math.log(10.0 ** (-power)) for power in range(1, 8))
    checks.require("carrier", "carrier diagonal divergence sequence", all(bridge_sequence[index + 1] > bridge_sequence[index] for index in range(len(bridge_sequence) - 1)), bridge_sequence, "strictly increasing")

    # Polynomial point checks for the convexified divergence identity and the
    # exact unfavorable-sign linear-flow fixture.
    p = Fraction(2, 5)
    r = Fraction(-3, 7)
    coupling = Fraction(5, 11)
    for index, value in enumerate((Fraction(-3, 2), Fraction(-1, 3), Fraction(0), Fraction(2, 5), Fraction(7, 4))):
        div_b = p + 3 * r * value**2 - p * value**2 - r * value**4
        v_term = -div_b / 2
        potential = coupling * value**6
        div_f = p + 3 * r * value**2 + 10 * coupling * value**4 - p * value**2 - r * value**4 - 2 * coupling * value**6
        laplacian_u = 30 * coupling * value**4
        right = -div_f / 2 + laplacian_u / 6
        checks.require("divergence", f"independent convexified identity {index}", v_term + potential == right, v_term + potential, right)
    flow_values = []
    for index, flow_time in enumerate((0.1, 0.5, 1.0, 2.0)):
        coefficient = (1.0 - (1.0 + 2.0 * flow_time) * math.exp(-2.0 * flow_time)) / 2.0
        flow_values.append(coefficient)
        flow_expectation = 1.0 / math.sqrt(1.0 - 2.0 * coefficient)
        exact_expectation = math.exp(flow_time) / math.sqrt(1.0 + 2.0 * flow_time)
        checks.require("divergence", f"independent flow coefficient positive {index}", coefficient > 0.0, coefficient, ">0")
        checks.close("divergence", f"independent flow identity {index}", flow_expectation, exact_expectation, 2e-14)
    checks.require("divergence", "independent flow remainder increases", all(flow_values[index + 1] > flow_values[index] for index in range(len(flow_values) - 1)), flow_values, "strictly increasing")

    failed = [row for row in checks.rows if row["status"] != "PASS"]
    derived = {
        "q": str(q),
        "source_budget": str(source_budget),
        "sextic_budget": str(sextic_budget),
        "two_atom_forward_kl": repr(forward_kl),
        "two_atom_reverse_kl": repr(reverse_kl),
        "scalar_total_determinant": str(det_total),
        "scalar_tail_determinant": str(det_tail),
        "adaptive_row_normalization_defect": repr(adaptive_defect),
        "adaptive_row_mean": repr(adaptive_mass),
        "matrix_combined_determinant": str(det12),
        "independent_normalizer_ratio": str(independent_ratio),
        "repeated_row_ratio": str(repeated_ratio),
        "finite_tree_expected_baseline": str(expected_predictable),
        "covariance_mass": str(mass_left),
        "carrier_six_dimensional_ninth": repr(6.0 * math.log(3.0)),
    }
    route_verdicts = {
        "endpoint_entropy_production": "exact-identity-not-free-energy-bound",
        "jointly_frozen_whole_output": "closed-by-gaussian-likelihood",
        "progressive_future_row_backward_resolvent": "failed-positive-normalization-defect",
        "single_output_frequency_positivity": "failed-exact-moment-fixture",
        "independent_output_determinant_normalization": "failed-positive-extensive-slack",
        "predictable_baseline_action": "exact-reduction",
        "predictable_covariance_mass": "exact-subdivision-invariant",
        "termwise_adapted_second_jet": "failed-quadratic-growth",
        "pure_carrier_kl_diagonal_bridge": "failed-dimensional-divergence",
        "convexified_divergence_flow": "parked-unfavourable-sign",
        "adapted_complete_cluster_matrix_carleson": "open",
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
    print(f"Independent R-107: {payload['assertions_passed']}/{payload['assertions_total']} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
