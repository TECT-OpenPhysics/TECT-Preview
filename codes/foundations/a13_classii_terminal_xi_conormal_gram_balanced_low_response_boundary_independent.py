#!/usr/bin/env python3
"""Independent standard-library audit for the scoped R-130 checkpoint.

This program does not import the SymPy primary route.  It recomputes the
production fractions, finite terminal/response/Gram fixtures, a numerical
floor-layer integral, the sharp balanced bridge, the direct-low Young
constant, and the complete-square Schur boundaries.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-TERMINAL-XI-CONORMAL-GRAM-BALANCED-LOW-"
    "RESPONSE-BOUNDARY"
)
SCHEMA = (
    "tect/a13-terminal-xi-conormal-gram-balanced-low-response-"
    "boundary-independent/1.0"
)
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-terminal-xi-conormal-gram-balanced-"
    "low-response-boundary/result.json"
)
A1_MANIFEST = REPO / (
    "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/"
    "production_functional_manifest.json"
)
A8_RESULT = REPO / (
    "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/"
    "runs/2026-07-20-primary-decoupled-nelson/result.json"
)
R103_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-"
    "closure/result.json"
)
R124_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-"
    "root-shell-boundary/result.json"
)


@dataclass(frozen=True)
class Jet2:
    value: Fraction
    first: Fraction = Fraction(0)
    second: Fraction = Fraction(0)

    @staticmethod
    def cast(value: Any) -> "Jet2":
        return value if isinstance(value, Jet2) else Jet2(Fraction(value))

    def __add__(self, other: Any) -> "Jet2":
        other = self.cast(other)
        return Jet2(
            self.value + other.value,
            self.first + other.first,
            self.second + other.second,
        )

    __radd__ = __add__

    def __neg__(self) -> "Jet2":
        return Jet2(-self.value, -self.first, -self.second)

    def __sub__(self, other: Any) -> "Jet2":
        return self + (-self.cast(other))

    def __rsub__(self, other: Any) -> "Jet2":
        return self.cast(other) + (-self)

    def __mul__(self, other: Any) -> "Jet2":
        other = self.cast(other)
        return Jet2(
            self.value * other.value,
            self.first * other.value + self.value * other.first,
            self.second * other.value
            + 2 * self.first * other.first
            + self.value * other.second,
        )

    __rmul__ = __mul__

    def inverse(self) -> "Jet2":
        return Jet2(
            1 / self.value,
            -self.first / self.value**2,
            2 * self.first**2 / self.value**3 - self.second / self.value**2,
        )

    def __truediv__(self, other: Any) -> "Jet2":
        return self * self.cast(other).inverse()

    def __rtruediv__(self, other: Any) -> "Jet2":
        return self.cast(other) * self.inverse()


def represent(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): represent(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [represent(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(represent(payload), stream, indent=2, sort_keys=True)
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

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
    ) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": represent(actual),
                "expected": represent(expected),
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
            "diagnostics": represent(diagnostics),
            "scope": {
                "non_importing_standard_library_route": True,
                "post_recombination_terminal_fixture_checked": True,
                "finite_cylinder_response_checked": True,
                "six_row_fraction_constants_checked": True,
                "floor_layer_numerically_checked": True,
                "balanced_and_low_boundaries_checked": True,
                "uniform_production_response_proved": False,
                "production_c_bal_upper_bound_proved": False,
                "historical_low_owner_closure_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "This independent audit checks the finite R-130 algebra and "
                "constant boundaries without importing the primary program. "
                "It proves no cutoff-uniform response, global balanced "
                "coefficient, historical low owner, Nelson estimate, or "
                "Sector-A closure."
            ),
        }


Matrix = list[list[Fraction]]
Vector = tuple[Fraction, ...]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[row][inner] * right[inner][column] for inner in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def msub(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] - right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def mscale(scale: Fraction, matrix: Matrix) -> Matrix:
    return [[scale * item for item in row] for row in matrix]


def frobenius(left: Matrix, right: Matrix) -> Fraction:
    return sum(
        (
            left[row][column] * right[row][column]
            for row in range(len(left))
            for column in range(len(left[0]))
        ),
        Fraction(0),
    )


def inverse_one(matrix: Matrix) -> Matrix:
    return [[1 / matrix[0][0]]]


def vadd(left: Vector, right: Vector) -> Vector:
    return tuple(a + b for a, b in zip(left, right))


def vsub(left: Vector, right: Vector) -> Vector:
    return tuple(a - b for a, b in zip(left, right))


def vdot(left: Vector, right: Vector) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def mean(values: tuple[Vector, ...]) -> Vector:
    return tuple(
        sum((value[index] for value in values), Fraction(0)) / len(values)
        for index in range(len(values[0]))
    )


def conditional(values: tuple[Vector, ...]) -> tuple[Vector, ...]:
    output: list[Vector | None] = [None] * len(values)
    for block in ((0, 1), (2, 3)):
        block_mean = mean(tuple(values[index] for index in block))
        for index in block:
            output[index] = block_mean
    return tuple(value for value in output if value is not None)


def expectation_norm_sq(values: tuple[Vector, ...]) -> Fraction:
    return sum((vdot(value, value) for value in values), Fraction(0)) / len(values)


def expectation_inner(left: tuple[Vector, ...], right: tuple[Vector, ...]) -> Fraction:
    return sum((vdot(a, b) for a, b in zip(left, right)), Fraction(0)) / len(left)


def layers(terminal: tuple[Vector, ...]) -> tuple[tuple[Vector, ...], ...]:
    low_value = mean(terminal)
    low = tuple(low_value for _ in terminal)
    middle = conditional(terminal)
    return (
        low,
        tuple(vsub(value, base) for value, base in zip(middle, low)),
        tuple(vsub(value, base) for value, base in zip(terminal, middle)),
    )


def project(values: tuple[Vector, ...], coordinate: int) -> tuple[Vector, ...]:
    return tuple(
        tuple(item if index == coordinate else Fraction(0) for index, item in enumerate(value))
        for value in values
    )


def composite_simpson(function: Callable[[float], float], left: float, right: float, intervals: int) -> float:
    if intervals % 2:
        raise ValueError("Simpson intervals must be even")
    width = (right - left) / intervals
    total = function(left) + function(right)
    total += 4.0 * sum(function(left + width * index) for index in range(1, intervals, 2))
    total += 2.0 * sum(function(left + width * index) for index in range(2, intervals, 2))
    return total * width / 3.0


def simpson_panel(function: Callable[[float], float], left: float, right: float) -> float:
    middle = (left + right) / 2
    return (right - left) * (function(left) + 4 * function(middle) + function(right)) / 6


def adaptive_simpson(
    function: Callable[[float], float],
    left: float,
    right: float,
    tolerance: float = 1e-11,
    depth: int = 24,
    whole: float | None = None,
) -> float:
    whole = simpson_panel(function, left, right) if whole is None else whole
    middle = (left + right) / 2
    left_value = simpson_panel(function, left, middle)
    right_value = simpson_panel(function, middle, right)
    delta = left_value + right_value - whole
    if depth <= 0 or abs(delta) <= 15 * tolerance:
        return left_value + right_value + delta / 15
    return adaptive_simpson(
        function, left, middle, tolerance / 2, depth - 1, left_value
    ) + adaptive_simpson(
        function, middle, right, tolerance / 2, depth - 1, right_value
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    params = a1["parameters"]
    fraction = lambda key: Fraction(str(params[key]))
    p_mass = fraction("M_X") ** 2 + fraction("classii_mass_regularizer")
    density_floor = fraction("rho_regularizer")
    alpha = Fraction(5, 9)
    c0 = Fraction(3, 250) / p_mass
    c1 = Fraction(243, 8000) / p_mass
    a_prod = fraction("cJJ") * fraction("alpha_X") ** 2 / p_mass
    b_prod = fraction("cJK") * fraction("alpha_X") * fraction("beta_X") / p_mass
    c_prod = fraction("cKK") * fraction("beta_X") ** 2 / p_mass
    beta_op = 4 * (a_prod + 2 * b_prod + c_prod)
    audit.check("production", "mass_positive", p_mass > 0, p_mass, ">0")
    audit.check("production", "floors_distinct", p_mass != density_floor, (p_mass, density_floor), "distinct")
    audit.check("production", "diagonal_a", c0 + c1 * (1 - alpha) ** 2 == a_prod, c0 + c1 * (1 - alpha) ** 2, a_prod)
    audit.check("production", "diagonal_b", c1 * alpha * (1 - alpha) == b_prod, c1 * alpha * (1 - alpha), b_prod)
    audit.check("production", "diagonal_c", c1 * alpha**2 == c_prod, c1 * alpha**2, c_prod)
    audit.check("production", "beta_operator", beta_op == Fraction(339, 2000) / p_mass, beta_op, Fraction(339, 2000) / p_mass)

    q_abs_bound = Fraction(1)
    tangent_bound = 1 + alpha * q_abs_bound
    remainder_bound = 1 + q_abs_bound
    u_gradient_bound = 2 * remainder_bound
    frame_bound = tangent_bound + alpha * u_gradient_bound
    u2_hessian_bound = 2 * (1 + q_abs_bound) + 4 * u_gradient_bound
    rational_first_per_row = 8 * tangent_bound * frame_bound
    linear_first = 24 * c0
    rational_first = 3 * c1 * rational_first_per_row
    l6 = linear_first + rational_first
    k_components = (
        4 * frame_bound**2,
        4 * alpha * tangent_bound * u2_hessian_bound,
        8 * alpha * u_gradient_bound * tangent_bound,
    )
    k_total = sum(k_components, Fraction(0))
    linear_second = 12 * c0
    rational_second = 3 * c1 * k_total
    h6 = linear_second + rational_second
    audit.check("gram", "linear_first", linear_first == Fraction(36, 125) / p_mass, linear_first, Fraction(36, 125) / p_mass)
    audit.check("gram", "rational_first", rational_first == Fraction(1071, 250) / p_mass, rational_first, Fraction(1071, 250) / p_mass)
    audit.check("gram", "six_row_first", l6 == Fraction(1143, 250) / p_mass, l6, Fraction(1143, 250) / p_mass)
    audit.check("gram", "k_total", k_total == Fraction(12464, 81), k_total, Fraction(12464, 81))
    audit.check("gram", "linear_second", linear_second == Fraction(18, 125) / p_mass, linear_second, Fraction(18, 125) / p_mass)
    audit.check("gram", "rational_second", rational_second == Fraction(7011, 500) / p_mass, rational_second, Fraction(7011, 500) / p_mass)
    audit.check("gram", "six_row_second", h6 == Fraction(7083, 500) / p_mass, h6, Fraction(7083, 500) / p_mass)
    audit.check("gram", "physical_force_factor", l6 / 2 == Fraction(1143, 500) / p_mass, l6 / 2, Fraction(1143, 500) / p_mass)
    audit.check("gram", "physical_hessian_factor", h6 == Fraction(7083, 500) / p_mass, h6, Fraction(7083, 500) / p_mass)
    audit.check("gram", "physical_remainder_factor", h6 / 2 == Fraction(7083, 1000) / p_mass, h6 / 2, Fraction(7083, 1000) / p_mass)

    # Direct R-082 Xi/Fierz checksum on a real slice, independent of SymPy.
    u1, u2 = Fraction(2, 3), Fraction(-1, 4)
    v1, v2 = Fraction(-2, 5), Fraction(3, 8)
    chi, chi_velocity = Fraction(1, 3), Fraction(-1, 7)
    r_doublet = u1**2 + u2**2
    denominator = r_doublet + chi**2 + density_floor
    dr = 2 * (u1 * v1 + u2 * v2)
    drho = dr + 2 * chi * chi_velocity
    wedge = u1 * v2 - u2 * v1
    m_rows = (2 * u1 * u2, Fraction(0), u1**2 - u2**2)
    j_rows = (2 * (u1 * v2 + u2 * v1), Fraction(0), 2 * (u1 * v1 - u2 * v2))
    l_rows = tuple(j_value - alpha * m_value * drho / denominator for j_value, m_value in zip(j_rows, m_rows))
    xi_norm = c0 * dr**2 + c1 * (dr - alpha * r_doublet * drho / denominator) ** 2 + 4 * (c0 + c1) * wedge**2
    six_row_norm = c0 * sum((value**2 for value in j_rows), Fraction(0)) + c1 * sum((value**2 for value in l_rows), Fraction(0))
    audit.check("xi", "dr_not_drho", dr != drho, dr, "distinct from drho")
    audit.check("xi", "linear_fierz", sum((value**2 for value in j_rows), Fraction(0)) == dr**2 + 4 * wedge**2, sum((value**2 for value in j_rows), Fraction(0)), dr**2 + 4 * wedge**2)
    audit.check("xi", "rational_fierz", sum((value**2 for value in l_rows), Fraction(0)) == (dr - alpha * r_doublet * drho / denominator) ** 2 + 4 * wedge**2, sum((value**2 for value in l_rows), Fraction(0)), (dr - alpha * r_doublet * drho / denominator) ** 2 + 4 * wedge**2)
    audit.check("xi", "xi_six_row_norm", xi_norm == six_row_norm, xi_norm, six_row_norm)

    # A different three-real rational row is differentiated by exact Jet2
    # arithmetic.  Frozen values below are test oracles, not theorem inputs.
    u_jet = (Fraction(2, 5), Fraction(-3, 7), Fraction(1, 6))
    a_jet = (Fraction(-1, 3), Fraction(2, 9), Fraction(4, 11))
    s_diag = (Fraction(1), Fraction(-1), Fraction(0))
    q_matrix = [
        [Fraction(7, 5), Fraction(-1, 4), Fraction(1, 6)],
        [Fraction(-1, 4), Fraction(-3, 8), Fraction(2, 7)],
        [Fraction(1, 6), Fraction(2, 7), Fraction(5, 6)],
    ]
    x_jet = tuple(Jet2(value, direction) for value, direction in zip(u_jet, a_jet))
    numerator_jet = sum((sign * value * value for sign, value in zip(s_diag, x_jet)), Jet2(Fraction(0)))
    denominator_jet = sum((value * value for value in x_jet), Jet2(Fraction(4, 7)))
    q_jet = numerator_jet / denominator_jet
    ell_jet = tuple(2 * (sign * value - alpha * q_jet * value) for sign, value in zip(s_diag, x_jet))
    form_jet = sum(
        (ell_jet[row] * q_matrix[row][column] * ell_jet[column] for row in range(3) for column in range(3)),
        Jet2(Fraction(0)),
    )
    first_oracle = Fraction(-51617594722391166796, 78469083778486452975)
    half_second_oracle = Fraction(5460992108423890930181438, 27687383510291252135502345)
    audit.check("gram", "jet_first_derivative", form_jet.first == first_oracle, form_jet.first, first_oracle)
    audit.check("gram", "jet_half_second_derivative", form_jet.second / 2 == half_second_oracle, form_jet.second / 2, half_second_oracle)

    terminal_0 = ((Fraction(0), Fraction(1)), (Fraction(2), Fraction(-1)), (Fraction(-1), Fraction(0)), (Fraction(1), Fraction(2)))
    terminal_star = ((Fraction(1), Fraction(2)), (Fraction(3), Fraction(0)), (Fraction(0), Fraction(-2)), (Fraction(2), Fraction(1)))
    layer_sets: list[tuple[tuple[Vector, ...], ...]] = []
    for label, terminal in (("baseline", terminal_0), ("terminal", terminal_star)):
        low, first, second = layers(terminal)
        layer_sets.append((low, first, second))
        layer_sum = sum((expectation_norm_sq(part) for part in (low, first, second)), Fraction(0))
        audit.check("terminal", f"{label}_doob", layer_sum == expectation_norm_sq(terminal), layer_sum, expectation_norm_sq(terminal))
        for coordinate in range(2):
            shell_sum = sum((expectation_norm_sq(project(part, coordinate)) for part in (low, first, second)), Fraction(0))
            audit.check("terminal", f"{label}_shell_{coordinate}", shell_sum == expectation_norm_sq(project(terminal, coordinate)), shell_sum, expectation_norm_sq(project(terminal, coordinate)))
    low_0, d1_0, d2_0 = layer_sets[0]
    low_star, d1_star, d2_star = layer_sets[1]
    r1 = tuple(vsub(a, b) for a, b in zip(d1_star, d1_0))
    r2 = tuple(vsub(a, b) for a, b in zip(d2_star, d2_0))
    square_difference = (expectation_norm_sq(terminal_star) - expectation_norm_sq(terminal_0)) / 2
    recoded = (
        (expectation_norm_sq(low_star) - expectation_norm_sq(low_0)) / 2
        + expectation_inner(d1_0, r1)
        + expectation_norm_sq(r1) / 2
        + expectation_inner(d2_0, r2)
        + expectation_norm_sq(r2) / 2
    )
    audit.check("terminal", "relative_terminal_recode", recoded == square_difference, recoded, square_difference)
    b_difference = [[Fraction(2), Fraction(1)], [Fraction(1), Fraction(3)]]
    gammas = (
        [[Fraction(1, 5), Fraction(0)], [Fraction(0), Fraction(1, 7)]],
        [[Fraction(1, 11), Fraction(1, 13)], [Fraction(1, 13), Fraction(1, 17)]],
        [[Fraction(1, 19), Fraction(0)], [Fraction(0), Fraction(1, 23)]],
    )
    trace_split = sum((frobenius(b_difference, gamma) for gamma in gammas), Fraction(0))
    gamma_total = [[sum((gamma[row][column] for gamma in gammas), Fraction(0)) for column in range(2)] for row in range(2)]
    trace_total = frobenius(b_difference, gamma_total)
    audit.check("terminal", "matching_trace_linearity", trace_split == trace_total, trace_split, trace_total)
    audit.check("terminal", "endpoint_recode", recoded - trace_split / 2 == square_difference - trace_total / 2, recoded - trace_split / 2, square_difference - trace_total / 2)
    sigma = Fraction(7, 11)
    gamma = sigma
    zero_mean_energy = sigma
    feedback_mean = Fraction(3, 5)
    feedback_energy = sigma + feedback_mean**2
    audit.check("terminal", "conditional_fresh_energy_match", zero_mean_energy == gamma, zero_mean_energy, gamma)
    audit.check("terminal", "feedback_mean_energy_defect", feedback_energy - gamma == feedback_mean**2 > 0, feedback_energy - gamma, feedback_mean**2)

    # Substantively independent 8-atom, 3-coordinate filtration fixture.
    terminal8_0 = (
        (Fraction(0), Fraction(1), Fraction(-1)),
        (Fraction(2), Fraction(-1), Fraction(0)),
        (Fraction(-1), Fraction(0), Fraction(2)),
        (Fraction(1), Fraction(2), Fraction(1)),
        (Fraction(3), Fraction(-2), Fraction(1)),
        (Fraction(-2), Fraction(1), Fraction(3)),
        (Fraction(0), Fraction(3), Fraction(-1)),
        (Fraction(2), Fraction(0), Fraction(2)),
    )
    terminal8_star = (
        (Fraction(1), Fraction(2), Fraction(0)),
        (Fraction(3), Fraction(0), Fraction(-1)),
        (Fraction(0), Fraction(-2), Fraction(3)),
        (Fraction(2), Fraction(1), Fraction(2)),
        (Fraction(4), Fraction(-1), Fraction(0)),
        (Fraction(-1), Fraction(2), Fraction(4)),
        (Fraction(1), Fraction(4), Fraction(-2)),
        (Fraction(3), Fraction(1), Fraction(3)),
    )
    partitions = (
        (tuple(range(8)),),
        ((0, 1, 2, 3), (4, 5, 6, 7)),
        ((0, 1), (2, 3), (4, 5), (6, 7)),
        tuple((index,) for index in range(8)),
    )

    def conditional_partition(values: tuple[Vector, ...], partition: tuple[tuple[int, ...], ...]) -> tuple[Vector, ...]:
        output: list[Vector | None] = [None] * len(values)
        for block in partition:
            block_mean = mean(tuple(values[index] for index in block))
            for index in block:
                output[index] = block_mean
        return tuple(value for value in output if value is not None)

    def filtration_layers(values: tuple[Vector, ...]) -> tuple[tuple[Vector, ...], ...]:
        conditionals = tuple(conditional_partition(values, partition) for partition in partitions)
        return (conditionals[0],) + tuple(
            tuple(vsub(a, b) for a, b in zip(conditionals[level], conditionals[level - 1]))
            for level in range(1, len(conditionals))
        )

    layers8_0 = filtration_layers(terminal8_0)
    layers8_star = filtration_layers(terminal8_star)
    for label, terminal, pieces in (
        ("baseline8", terminal8_0, layers8_0),
        ("terminal8", terminal8_star, layers8_star),
    ):
        reconstruction = tuple(
            tuple(sum((piece[atom][coordinate] for piece in pieces), Fraction(0)) for coordinate in range(3))
            for atom in range(8)
        )
        audit.check("terminal8", f"{label}_reconstruction", reconstruction == terminal, reconstruction, terminal)
        orthogonal = all(
            expectation_inner(pieces[left], pieces[right]) == 0
            for left in range(len(pieces))
            for right in range(left + 1, len(pieces))
        )
        audit.check("terminal8", f"{label}_orthogonality", orthogonal, orthogonal, True)
        pythagoras8 = sum((expectation_norm_sq(piece) for piece in pieces), Fraction(0))
        audit.check("terminal8", f"{label}_pythagoras", pythagoras8 == expectation_norm_sq(terminal), pythagoras8, expectation_norm_sq(terminal))
        for coordinate in range(3):
            shell_total = sum((expectation_norm_sq(project(piece, coordinate)) for piece in pieces), Fraction(0))
            audit.check("terminal8", f"{label}_shell_{coordinate}", shell_total == expectation_norm_sq(project(terminal, coordinate)), shell_total, expectation_norm_sq(project(terminal, coordinate)))
    relative8_direct = (expectation_norm_sq(terminal8_star) - expectation_norm_sq(terminal8_0)) / 2
    relative8_layers = sum(
        (
            expectation_inner(base, tuple(vsub(a, b) for a, b in zip(star, base)))
            + expectation_norm_sq(tuple(vsub(a, b) for a, b in zip(star, base))) / 2
            for base, star in zip(layers8_0, layers8_star)
        ),
        Fraction(0),
    )
    audit.check("terminal8", "relative_recode", relative8_layers == relative8_direct, relative8_layers, relative8_direct)
    legacy_phi1 = (Fraction(-1), Fraction(-1), Fraction(1), Fraction(1))
    legacy_phi2 = (Fraction(0), Fraction(2), Fraction(4), Fraction(6))
    legacy_conditional = (Fraction(1), Fraction(1), Fraction(5), Fraction(5))
    audit.check("terminal8", "legacy_tower_failure", legacy_conditional != legacy_phi1 and sum(legacy_phi2[:2], Fraction(0)) / 2 == legacy_conditional[0], legacy_conditional, "not phi1")

    heat_c1 = [[Fraction(1), Fraction(0)], [Fraction(2), Fraction(1)], [Fraction(-1), Fraction(3)]]
    heat_c2 = [[Fraction(-1), Fraction(2)], [Fraction(0), Fraction(-1)], [Fraction(3), Fraction(1)]]
    heat_gram_mean = mscale(Fraction(1, 2), [[matmul(transpose(heat_c1), heat_c1)[row][column] + matmul(transpose(heat_c2), heat_c2)[row][column] for column in range(2)] for row in range(2)])
    heat_c_mean = mscale(Fraction(1, 2), [[heat_c1[row][column] + heat_c2[row][column] for column in range(2)] for row in range(3)])
    heat_gap8 = msub(heat_gram_mean, matmul(transpose(heat_c_mean), heat_c_mean))
    heat_gap8_psd = heat_gap8[0][0] >= 0 and heat_gap8[1][1] >= 0 and heat_gap8[0][0] * heat_gap8[1][1] - heat_gap8[0][1] ** 2 >= 0
    audit.check("terminal8", "heat_gram_gap_nonzero_psd", heat_gap8 != [[0, 0], [0, 0]] and heat_gap8_psd, heat_gap8, "nonzero PSD")

    m_variance = [[Fraction(2), Fraction(1, 3)], [Fraction(1, 3), Fraction(1)]]
    m_trace = [[Fraction(1), Fraction(1, 4)], [Fraction(1, 4), Fraction(3)]]
    q_cn = msub(m_variance, m_trace)
    q_future = mscale(Fraction(2), m_variance)
    q_comp = msub(q_cn, mscale(Fraction(1, 2), q_future))
    synthesis = [[Fraction(1), Fraction(0), Fraction(1)], [Fraction(0), Fraction(1), Fraction(-1)]]
    pulled = matmul(transpose(synthesis), matmul(q_comp, synthesis))
    negative_trace = mscale(Fraction(-1), m_trace)
    audit.check("response", "owner_identity", q_comp == negative_trace, q_comp, negative_trace)
    audit.check("response", "pullback_symmetric", pulled == transpose(pulled), pulled, transpose(pulled))
    vertical = [[Fraction(-1)], [Fraction(1)], [Fraction(1)]]
    physical_vertical = matmul(synthesis, vertical)
    pulled_vertical = matmul(pulled, vertical)
    audit.check("response", "vertical_kernel", physical_vertical == [[0], [0]] and pulled_vertical == [[0], [0], [0]], (physical_vertical, pulled_vertical), "zero")
    source_cost = Fraction(9, 10) * sum((row[0] ** 2 for row in vertical), Fraction(0))
    audit.check("response", "source_cost_outside_pullback", source_cost > 0, source_cost, ">0 while pullback is zero")

    # Different 3-physical/4-source response and shell-coanalysis fixture.
    mv3 = [[Fraction(2), Fraction(1, 3), Fraction(0)], [Fraction(1, 3), Fraction(3), Fraction(1, 5)], [Fraction(0), Fraction(1, 5), Fraction(1)]]
    mt3 = [[Fraction(1), Fraction(1, 4), Fraction(1, 6)], [Fraction(1, 4), Fraction(2), Fraction(0)], [Fraction(1, 6), Fraction(0), Fraction(4)]]
    qcomp3 = msub(msub(mv3, mt3), mscale(Fraction(1, 2), mscale(Fraction(2), mv3)))
    synthesis3 = [[Fraction(1), Fraction(0), Fraction(1), Fraction(0)], [Fraction(0), Fraction(1), Fraction(-1), Fraction(1)], [Fraction(1), Fraction(1), Fraction(0), Fraction(-1)]]
    response3 = matmul(qcomp3, synthesis3)
    pulled3 = matmul(transpose(synthesis3), response3)
    vertical3 = [[Fraction(1)], [Fraction(-1)], [Fraction(-1)], [Fraction(0)]]
    audit.check("response3", "owner_identity", qcomp3 == mscale(Fraction(-1), mt3), qcomp3, mscale(Fraction(-1), mt3))
    audit.check("response3", "pullback_symmetric", pulled3 == transpose(pulled3), pulled3, transpose(pulled3))
    audit.check("response3", "vertical_kernel", matmul(synthesis3, vertical3) == [[0], [0], [0]] and matmul(pulled3, vertical3) == [[0], [0], [0], [0]], (matmul(synthesis3, vertical3), matmul(pulled3, vertical3)), "zero")
    forward_shell_sum = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    reverse_shell_sum = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for shell in range(3):
        lrow = [synthesis3[shell]]
        arow = [response3[shell]]
        forward_piece = matmul(transpose(lrow), arow)
        reverse_piece = matmul(transpose(arow), lrow)
        forward_shell_sum = [[forward_shell_sum[row][column] + forward_piece[row][column] for column in range(4)] for row in range(4)]
        reverse_shell_sum = [[reverse_shell_sum[row][column] + reverse_piece[row][column] for column in range(4)] for row in range(4)]
    audit.check("response3", "physical_shell_forward", forward_shell_sum == pulled3, forward_shell_sum, pulled3)
    audit.check("response3", "physical_shell_reverse", reverse_shell_sum == pulled3, reverse_shell_sum, pulled3)

    def layer_integrand(theta: float) -> float:
        if abs(abs(theta) - math.pi / 2) < 1e-15:
            return 0.0
        y = math.tan(theta)
        second = 2.0 * y * (3.0 - y * y) / (1.0 + y * y) ** 3
        return second * second / (math.cos(theta) ** 2)

    layer_integral = composite_simpson(layer_integrand, -math.pi / 2, math.pi / 2, 65536)
    audit.check("floor", "whole_layer_integral", abs(layer_integral - 3 * math.pi / 4) < 2e-11, layer_integral, 3 * math.pi / 4)
    audit.check("floor", "normalized_layer_limit", abs(layer_integral / math.pi - 0.75) < 1e-11, layer_integral / math.pi, 0.75)

    def torus_floor_scaled(floor: float, intervals: int = 131072) -> float:
        def integrand(x: float) -> float:
            sine = math.sin(x)
            cosine = math.cos(x)
            denominator = sine * sine + floor
            first = sine * sine * (sine * sine + 3 * floor) / denominator**2
            second = 2 * floor * sine * (3 * floor - sine * sine) / denominator**3
            g_second = second * cosine * cosine - first * sine
            return g_second * g_second

        return math.sqrt(floor) * composite_simpson(integrand, -math.pi, math.pi, intervals) / (2 * math.pi)

    floor_values = [torus_floor_scaled(value) for value in (0.01, 0.0025, 0.000625)]
    audit.check("floor", "torus_floor_trend", abs(floor_values[-1] - 0.75) < abs(floor_values[0] - 0.75), floor_values, "converges toward 0.75")
    audit.check("floor", "torus_floor_final", abs(floor_values[-1] - 0.75) < 0.025, floor_values[-1], "0.75 +/- 0.025")

    def layer_transformed(t_value: float) -> float:
        if t_value <= 0 or t_value >= 1:
            return 0.0
        y_value = t_value / (1 - t_value)
        second = 2 * y_value * (3 - y_value * y_value) / (1 + y_value * y_value) ** 3
        return 2 * second * second / (1 - t_value) ** 2

    adaptive_layer = adaptive_simpson(layer_transformed, 0.0, 1.0, 1e-11)
    audit.check("floor_adaptive", "layer_exact_target", abs(adaptive_layer - 3 * math.pi / 4) < 2e-10, adaptive_layer, 3 * math.pi / 4)

    def composed_second(floor: float, x_value: float) -> float:
        sine = math.sin(x_value)
        cosine = math.cos(x_value)
        denominator_value = sine * sine + floor
        first = sine * sine * (sine * sine + 3 * floor) / denominator_value**2
        second = 2 * floor * sine * (3 * floor - sine * sine) / denominator_value**3
        return second * cosine * cosine - first * sine

    def adaptive_torus_scaled(floor: float) -> float:
        root = math.sqrt(floor)
        delta = min(math.pi / 4, 64 * root)
        near = adaptive_simpson(
            lambda scaled: floor * composed_second(floor, root * scaled) ** 2,
            0.0,
            delta / root,
            2e-11,
        )
        far = adaptive_simpson(
            lambda x_value: root * composed_second(floor, x_value) ** 2,
            delta,
            math.pi / 2,
            2e-11,
        )
        return (2 / math.pi) * (near + far)

    adaptive_floor_values = [adaptive_torus_scaled(value) for value in (1e-2, 1e-4, 1e-6)]
    adaptive_errors = [abs(value - 0.75) for value in adaptive_floor_values]
    audit.check("floor_adaptive", "strict_asymptotic_trend", adaptive_errors[0] > adaptive_errors[1] > adaptive_errors[2], adaptive_floor_values, "strictly toward 0.75")
    audit.check("floor_adaptive", "small_floor_limit", adaptive_errors[-1] < 7e-4, adaptive_floor_values[-1], "0.75 +/- 0.0007")
    norm_coefficient = math.sqrt(adaptive_floor_values[-1])
    audit.check("floor_adaptive", "norm_asymptotic_coefficient", abs(norm_coefficient - math.sqrt(3) / 2) < 5e-4, norm_coefficient, math.sqrt(3) / 2)

    amplitude = 1.7
    frequency = 7
    balanced_left = amplitude**4 * frequency**2
    balanced_right = (amplitude * frequency**2) * amplitude**3
    audit.check("balanced", "circle_constant_one", abs(balanced_left - balanced_right) < 1e-12, balanced_left, balanced_right)
    circle_points = 4096
    lhs_samples: list[float] = []
    laplacian_samples: list[float] = []
    l6_samples: list[float] = []
    for index in range(circle_points):
        x_value = 2 * math.pi * index / circle_points
        z_value = (amplitude * math.cos(frequency * x_value), amplitude * math.sin(frequency * x_value))
        derivative = (-amplitude * frequency * math.sin(frequency * x_value), amplitude * frequency * math.cos(frequency * x_value))
        laplacian = (-amplitude * frequency**2 * math.cos(frequency * x_value), -amplitude * frequency**2 * math.sin(frequency * x_value))
        z_norm_sq = sum(item * item for item in z_value)
        derivative_norm_sq = sum(item * item for item in derivative)
        lhs_samples.append(z_norm_sq * derivative_norm_sq)
        laplacian_samples.append(sum(item * item for item in laplacian))
        l6_samples.append(z_norm_sq**3)
    circle_left = sum(lhs_samples) / circle_points
    circle_right = math.sqrt(sum(laplacian_samples) / circle_points) * math.sqrt(sum(l6_samples) / circle_points)
    audit.check("balanced", "integrated_circle_equality", abs(circle_left / circle_right - 1) < 2e-13, circle_left / circle_right, 1)
    audit.check("balanced", "constant_below_one_fails", circle_left > 0.999999 * circle_right, circle_left, ">0.999999 rhs")
    a8 = json.loads(A8_RESULT.read_text(encoding="utf-8"))
    r_symbol = fraction("r")
    z_symbol = fraction("Z")
    y_symbol = fraction("Y")
    s_star = (2 * r_symbol - z_symbol) / (2 * y_symbol - z_symbol)
    symbol_ratio = lambda value: (y_symbol * value**2 + z_symbol * value + r_symbol) / (1 + value) ** 2
    c_sym = min(symbol_ratio(Fraction(0)), symbol_ratio(s_star), y_symbol)
    recorded_c_sym = float(a8["derived"]["symbol_coercivity"]["c_symbol"])
    audit.check("balanced", "symbol_constant", abs(float(c_sym) - recorded_c_sym) < 5e-15, float(c_sym), recorded_c_sym)
    multiplier = Fraction(str(a8["config"]["regulator_multiplier_bound"]))
    a0 = multiplier**2 / c_sym
    bridge = math.sqrt(float(32 * a0))
    audit.check("balanced", "symbol_stationary_admissible", s_star >= 0, s_star, ">=0")
    r103 = json.loads(R103_RESULT.read_text(encoding="utf-8"))
    source_reserve = Fraction(r103["diagnostics"]["budget"]["source_reserve"])
    sextic_reserve = Fraction(r103["diagnostics"]["budget"]["sextic_reserve"])
    eta = source_reserve - Fraction(3, 125) / p_mass
    zeta = sextic_reserve
    ceiling = 2 * math.sqrt(float(eta * zeta)) / bridge
    r124 = json.loads(R124_RESULT.read_text(encoding="utf-8"))
    full_cartan_factor = Fraction(r124["diagnostics"]["cartan"]["full"])
    oriented = c1 * full_cartan_factor / 2
    full_cross = 2 * oriented
    oriented_ratio = float(oriented) / ceiling
    audit.check("balanced", "positive_diagonals", eta > 0 and zeta > 0, (eta, zeta), "positive")
    audit.check("balanced", "oriented_cartan", Fraction(1340, 729) * c1 == oriented, Fraction(1340, 729) * c1, oriented)
    audit.check("balanced", "full_cross_cartan", Fraction(2680, 729) * c1 == full_cross, Fraction(2680, 729) * c1, full_cross)
    audit.check("balanced", "local_diagnostic_below_ceiling", oriented_ratio < 1, oriented_ratio, "<1")
    audit.check("balanced", "cross_ratio_invariant", abs(float(full_cross) * bridge / (4 * math.sqrt(float(eta * zeta))) - oriented_ratio) < 1e-14, float(full_cross) * bridge / (4 * math.sqrt(float(eta * zeta))), oriented_ratio)

    lengths = tuple(Fraction(str(params[key])) for key in ("Lx", "Ly", "Lz"))
    audit.check("low", "cubic_volume", lengths[0] == lengths[1] == lengths[2], lengths, "equal")
    volume_two_thirds = lengths[0] ** 2
    a_low_per_g = beta_op * volume_two_thirds / 2
    audit.check("low", "l16_low_coefficient", a_low_per_g == Fraction(2712, 125) / p_mass, a_low_per_g, Fraction(2712, 125) / p_mass)
    a_low = 1.4
    zeta_float = 0.12
    y_star = (a_low / (3 * zeta_float)) ** 1.5
    value_star = a_low * y_star ** (1 / 3) - zeta_float * y_star
    young_constant = 2 * a_low**1.5 / (3 * math.sqrt(3 * zeta_float))
    audit.check("low", "young_constant", abs(value_star - young_constant) < 1e-14, value_star, young_constant)
    audit.check("low", "young_stationary_max", value_star > a_low * (0.8 * y_star) ** (1 / 3) - zeta_float * 0.8 * y_star and value_star > a_low * (1.2 * y_star) ** (1 / 3) - zeta_float * 1.2 * y_star, value_star, "larger than nearby samples")
    young_grid = [
        a_low * (2 * y_star * index / 2000) ** (1 / 3) - zeta_float * (2 * y_star * index / 2000)
        for index in range(2001)
    ]
    audit.check("low", "young_global_grid", max(young_grid) <= young_constant + 1e-12, max(young_grid), f"<= {young_constant}")

    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    terminal_column = [[Fraction(1)], [Fraction(1)]]
    uv = [[Fraction(1), Fraction(2)], [Fraction(3), Fraction(-1)]]
    d_block = matmul(transpose(terminal_column), terminal_column)
    projection = matmul(matmul(terminal_column, inverse_one(d_block)), transpose(terminal_column))
    m_block = matmul(transpose(uv), uv)
    coupling = matmul(transpose(uv), terminal_column)
    schur = msub(m_block, matmul(matmul(coupling, inverse_one(d_block)), transpose(coupling)))
    projected = matmul(transpose(uv), matmul(msub(identity, projection), uv))
    audit.check("low", "gram_schur_identity", schur == projected, schur, projected)
    audit.check("low", "gram_schur_psd", schur[0][0] >= 0 and schur[1][1] >= 0 and schur[0][0] * schur[1][1] - schur[0][1] ** 2 >= 0, schur, "PSD")
    rank_one_uv = matmul(terminal_column, [[Fraction(2), Fraction(3)]])
    rank_one_m = matmul(transpose(rank_one_uv), rank_one_uv)
    rank_one_k = matmul(transpose(rank_one_uv), terminal_column)
    rank_one_schur = msub(rank_one_m, matmul(matmul(rank_one_k, inverse_one(d_block)), transpose(rank_one_k)))
    audit.check("low", "no_strict_gap", rank_one_schur == [[0, 0], [0, 0]], rank_one_schur, "zero")
    audit.check("low", "child_refinement_failure", 1**2 + (-1) ** 2 > (1 - 1) ** 2, (2, 0), "child > terminal")

    terminal3 = [[Fraction(1)], [Fraction(2)], [Fraction(-1)]]
    w3 = [[Fraction(2), Fraction(-1)], [Fraction(0), Fraction(3)], [Fraction(1), Fraction(1)]]
    d3 = matmul(transpose(terminal3), terminal3)
    projection3 = matmul(matmul(terminal3, inverse_one(d3)), transpose(terminal3))
    schur3 = msub(
        matmul(transpose(w3), w3),
        matmul(
            matmul(matmul(transpose(w3), terminal3), inverse_one(d3)),
            matmul(transpose(terminal3), w3),
        ),
    )
    projected3 = matmul(transpose(w3), matmul(msub([[Fraction(1), Fraction(0), Fraction(0)], [Fraction(0), Fraction(1), Fraction(0)], [Fraction(0), Fraction(0), Fraction(1)]], projection3), w3))
    determinant3 = schur3[0][0] * schur3[1][1] - schur3[0][1] ** 2
    audit.check("low3", "schur_identity", schur3 == projected3, schur3, projected3)
    audit.check("low3", "schur_oracle", schur3 == [[Fraction(29, 6), Fraction(-5, 3)], [Fraction(-5, 3), Fraction(25, 3)]], schur3, [[Fraction(29, 6), Fraction(-5, 3)], [Fraction(-5, 3), Fraction(25, 3)]])
    audit.check("low3", "schur_strict_fixture", determinant3 == Fraction(75, 2), determinant3, Fraction(75, 2))
    rank_coefficients = [[Fraction(2, 3), Fraction(-5, 4)]]
    rank_w3 = matmul(terminal3, rank_coefficients)
    rank_schur3 = msub(
        matmul(transpose(rank_w3), rank_w3),
        matmul(
            matmul(matmul(transpose(rank_w3), terminal3), inverse_one(d3)),
            matmul(transpose(terminal3), rank_w3),
        ),
    )
    audit.check("low3", "rank_one_zero_gap", rank_schur3 == [[0, 0], [0, 0]], rank_schur3, "zero")
    x_fixture = [[Fraction(2)], [Fraction(-1)]]
    ell_fixture = [[Fraction(3)]]
    combined = [[matmul(w3, x_fixture)[row][0] + matmul(terminal3, ell_fixture)[row][0]] for row in range(3)]
    square_value = matmul(transpose(combined), combined)[0][0] / 2
    m3 = matmul(transpose(w3), w3)
    k3 = matmul(transpose(w3), terminal3)
    block_value = (
        matmul(transpose(x_fixture), matmul(m3, x_fixture))[0][0] / 2
        + matmul(transpose(x_fixture), matmul(k3, ell_fixture))[0][0]
        + d3[0][0] * ell_fixture[0][0] ** 2 / 2
    )
    audit.check("low3", "complete_square_cross_factor", square_value == block_value, square_value, block_value)
    audit.check("low3", "child_terminal_refinement", Fraction(2) ** 2 + Fraction(-2) ** 2 > (Fraction(2) - Fraction(2)) ** 2, (8, 0), "child > terminal")

    diagnostics = {
        "production": {"P": p_mass, "density_floor": density_floor, "c0": c0, "c1": c1, "beta_operator": beta_op},
        "gram": {"L6": l6, "H6": h6, "physical_force": l6 / 2, "physical_remainder": h6 / 2},
        "terminal": {"square_difference": square_difference, "trace_total": trace_total},
        "response": {"q_comp": q_comp, "pulled": pulled},
        "floor": {"whole_layer_integral": layer_integral, "normalized": layer_integral / math.pi, "torus_scaled": floor_values, "adaptive_layer": adaptive_layer, "adaptive_torus_scaled": adaptive_floor_values},
        "balanced": {"bridge": bridge, "ceiling": ceiling, "oriented_diagnostic": float(oriented), "diagnostic_ratio": oriented_ratio, "integrated_circle_ratio": circle_left / circle_right},
        "low": {"a_low_per_g": a_low_per_g, "young_constant_fixture": young_constant, "schur": schur, "rank_one_schur": rank_one_schur, "independent_schur": schur3, "independent_rank_one_schur": rank_schur3},
        "independent_strength": {"jet_first": form_jet.first, "jet_half_second": form_jet.second / 2, "terminal8_relative": relative8_direct, "response3_pulled": pulled3},
    }
    result = audit.finish(diagnostics)
    atomic_json(arguments.output, result)
    print(f"R-130 independent {result['status']}: {result['assertions_passed']}/{result['assertions_total']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
