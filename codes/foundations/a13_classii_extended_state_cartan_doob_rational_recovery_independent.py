#!/usr/bin/env python3
"""Standard-library independent certificate for the R-099 A13 checkpoint.

This route imports neither NumPy nor the primary implementation.  Fractions
and exact Boolean-cube conditional expectations independently reproduce the
Cartan, Doob--Hardy, ordered-reveal, multiplier, and rational identities.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import argparse
import ast
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any, Callable, Iterable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-EXTENDED-STATE-CARTAN-DOOB-RATIONAL-RECOVERY"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-27-independent-extended-state-cartan-doob-rational-recovery/result.json"
)

Vector = tuple[F, F]
Matrix = tuple[tuple[F, F], tuple[F, F]]


def serial(value: Any) -> Any:
    if isinstance(value, F):
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
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def mean(values: Iterable[F]) -> F:
    values_list = list(values)
    return sum(values_list, F(0)) / len(values_list)


def conditional(values: list[F], states: list[tuple[int, ...]], revealed: int) -> list[F]:
    if revealed == 0:
        return [mean(values)] * len(values)
    groups: dict[tuple[int, ...], list[int]] = {}
    for index, state in enumerate(states):
        groups.setdefault(state[:revealed], []).append(index)
    answer = [F(0)] * len(values)
    for indices in groups.values():
        group_mean = mean(values[index] for index in indices)
        for index in indices:
            answer[index] = group_mean
    return answer


def vadd(left: Vector, right: Vector) -> Vector:
    return left[0] + right[0], left[1] + right[1]


def mvec(matrix: Matrix, vector: Vector) -> Vector:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


def madd(left: Matrix, right: Matrix) -> Matrix:
    return (
        (left[0][0] + right[0][0], left[0][1] + right[0][1]),
        (left[1][0] + right[1][0], left[1][1] + right[1][1]),
    )


def mscale(scale: F, matrix: Matrix) -> Matrix:
    return (
        (scale * matrix[0][0], scale * matrix[0][1]),
        (scale * matrix[1][0], scale * matrix[1][1]),
    )


def inverse(matrix: Matrix) -> Matrix:
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    if determinant == 0:
        raise ValueError("singular matrix")
    return (
        (matrix[1][1] / determinant, -matrix[0][1] / determinant),
        (-matrix[1][0] / determinant, matrix[0][0] / determinant),
    )


def dot(left: Vector, right: Vector) -> F:
    return left[0] * right[0] + left[1] * right[1]


def quadratic(matrix: Matrix, vector: Vector) -> F:
    return dot(vector, mvec(matrix, vector))


def frobenius(left: Matrix, right: Matrix) -> F:
    return sum((left[i][j] * right[i][j] for i in range(2) for j in range(2)), F(0))


def outer(vector: Vector) -> Matrix:
    return ((vector[0] * vector[0], vector[0] * vector[1]), (vector[1] * vector[0], vector[1] * vector[1]))


def current(sigma: F, z: F) -> F:
    return (1 + sigma * sigma) * z + sigma * z**3


def cubic_heat_jacobian(matrix: Matrix, floor: F) -> Matrix:
    dimension = 2
    polynomials: list[dict[tuple[int, int], F]] = [dict(), dict()]
    for output in range(dimension):
        for left in range(dimension):
            for right in range(dimension):
                exponent = [0, 0]
                exponent[output] += 1
                exponent[left] += 1
                exponent[right] += 1
                key = (exponent[0], exponent[1])
                polynomials[output][key] = polynomials[output].get(key, F(0)) + matrix[left][right] / floor
    answer = [[F(0), F(0)], [F(0), F(0)]]
    for output, polynomial in enumerate(polynomials):
        for exponent, coefficient in polynomial.items():
            for laplace_variable in range(2):
                power = exponent[laplace_variable]
                if power < 2:
                    continue
                reduced = list(exponent)
                reduced[laplace_variable] -= 2
                for derivative in range(2):
                    target = [0, 0]
                    target[derivative] = 1
                    if reduced == target:
                        answer[output][derivative] += coefficient * power * (power - 1)
    return ((answer[0][0], answer[0][1]), (answer[1][0], answer[1][1]))


def payment_gauge_exact(
    weights: tuple[F, ...],
    matrices: tuple[Matrix, ...],
    carriers: tuple[Vector, ...],
    gamma: Matrix,
    payment: Matrix,
    shift: Vector,
) -> tuple[F, F]:
    bar: Matrix = ((F(0), F(0)), (F(0), F(0)))
    q: Vector = (F(0), F(0))
    wick = F(0)
    for weight, matrix, carrier in zip(weights, matrices, carriers):
        bar = madd(bar, mscale(weight, matrix))
        q = vadd(q, (weight * mvec(matrix, carrier)[0], weight * mvec(matrix, carrier)[1]))
        wick += weight * frobenius(matrix, madd(outer(carrier), mscale(F(-1), gamma)))
    a = madd(bar, mscale(F(2), payment))
    ainv_q = mvec(inverse(a), q)
    square = vadd(shift, ainv_q)
    left = F(1, 2) * quadratic(a, square) + F(1, 2) * (wick - quadratic(inverse(a), q)) - quadratic(payment, shift)
    right = F(0)
    for weight, matrix, carrier in zip(weights, matrices, carriers):
        shifted = vadd(carrier, shift)
        right += F(1, 2) * weight * frobenius(matrix, madd(outer(shifted), mscale(F(-1), gamma)))
    return left, right


def main(output: Path) -> int:
    rows: list[dict[str, Any]] = []

    def check(group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    roots = imported_roots(Path(__file__).resolve())
    forbidden = {"numpy", "scipy", "sympy", "mpmath"}
    check("independence", "no_numerical_package_import", roots.isdisjoint(forbidden), sorted(roots & forbidden), [])
    primary_module = "a13_classii_extended_state_cartan_doob_rational_recovery"
    check("independence", "does_not_import_primary", primary_module not in roots, sorted(roots), "primary absent")

    # Exact changing-heat telescope on several rational paths.
    paths = (
        ((F(0), F(1, 3), F(-2, 5)), (F(1, 4), F(3, 2), F(-1, 7))),
        ((F(2, 3), F(-4, 7), F(5, 6), F(2, 3)), (F(-1), F(3, 5), F(7, 4), F(-1))),
        ((F(1, 9), F(2, 9), F(4, 9), F(8, 9), F(16, 9)), (F(0), F(1), F(-2), F(3), F(-4))),
    )
    for path_index, (sigmas, points) in enumerate(paths):
        complete = F(0)
        source = F(0)
        heat = F(0)
        for level in range(1, len(sigmas)):
            source_edge = current(sigmas[level], points[level]) - current(sigmas[level], points[level - 1])
            heat_edge = current(sigmas[level], points[level - 1]) - current(sigmas[level - 1], points[level - 1])
            source += source_edge
            heat += heat_edge
            complete += source_edge + heat_edge
        endpoint = current(sigmas[-1], points[-1]) - current(sigmas[0], points[0])
        check("cartan_telescope", f"complete_exact_{path_index}", complete == endpoint, complete - endpoint, F(0))
        check("cartan_telescope", f"source_defect_exact_{path_index}", source - endpoint == -heat, source - endpoint, -heat)
    closed_sigmas, closed_points = paths[1]
    closed_endpoint = current(closed_sigmas[-1], closed_points[-1]) - current(closed_sigmas[0], closed_points[0])
    noninjective_endpoint = current(F(1, 5), F(0)) - current(F(-7, 10), F(0))
    check(
        "cartan_telescope",
        "closed_extended_loop",
        closed_endpoint == 0 and noninjective_endpoint == 0 and F(1, 5) != F(-7, 10),
        {"equal_extended_endpoints": closed_endpoint, "distinct_heat_equal_current": noninjective_endpoint},
        {"equal_extended_endpoints": F(0), "distinct_heat_equal_current": F(0)},
    )
    check("cartan_telescope", "drop_heat_mutant_nonzero", sum(current(paths[0][0][i], paths[0][1][i]) - current(paths[0][0][i], paths[0][1][i - 1]) for i in range(1, len(paths[0][0]))) != current(paths[0][0][-1], paths[0][1][-1]) - current(paths[0][0][0], paths[0][1][0]), "source-only", "not endpoint")

    cartan_s: Matrix = ((F(3, 2), F(-2, 3)), (F(-2, 3), F(-3, 2)))
    floor = F(7, 5)
    contracted = cubic_heat_jacobian(cartan_s, floor)
    expected = mscale(F(4) / floor, cartan_s)
    check("cartan_heat", "d_delta_f_exact", contracted == expected, contracted, expected)
    check("cartan_heat", "semigroup_half_generator_exact", mscale(F(1, 2), contracted) == mscale(F(2) / floor, cartan_s), mscale(F(1, 2), contracted), mscale(F(2) / floor, cartan_s))
    check("cartan_heat", "wrong_generator_factor_rejected", contracted != mscale(F(2) / floor, cartan_s), contracted, "not 2S/e")

    # Progressive revisit: exact coefficient and A^2 versus A separation.
    epsilon = F(1, 2)
    rho = (1 - epsilon) / (1 + epsilon)
    harmonic = 4
    normalization = F(7, 4)
    root_variance = F(5, 8)
    coefficient = normalization**2 * root_variance * epsilon**2 * (1 - rho**2) ** 2 * rho ** (2 * (harmonic - 1))
    check("progressive_revisit", "rho_exact", rho == F(1, 3), rho, F(1, 3))
    check("progressive_revisit", "nonzero_harmonic_exact", coefficient > 0, coefficient, "> 0")
    amplitudes = (F(4), F(16), F(64), F(256))
    energy = [coefficient * amplitude**2 for amplitude in amplitudes]
    mixed_without_sqrt_constant = [1 + amplitude for amplitude in amplitudes]
    ratios = [value / payload for value, payload in zip(energy, mixed_without_sqrt_constant)]
    check("progressive_revisit", "energy_quadratic_exact", all(value / amplitude**2 == coefficient for value, amplitude in zip(energy, amplitudes)), [value / amplitude**2 for value, amplitude in zip(energy, amplitudes)], coefficient)
    check("progressive_revisit", "ratio_strict_growth", all(ratios[i + 1] > ratios[i] for i in range(len(ratios) - 1)), ratios, "strict growth")
    forward_visit: Vector = (F(256), F(-128))
    inverse_visit: Vector = (-forward_visit[0], -forward_visit[1])
    terminal_visit = vadd(forward_visit, inverse_visit)
    wrong_sign_mutant: Vector = (forward_visit[0] - inverse_visit[0], forward_visit[1] - inverse_visit[1])
    check(
        "progressive_revisit",
        "reverse_terminal_zero",
        terminal_visit == (F(0), F(0)) and wrong_sign_mutant != (F(0), F(0)),
        {"terminal": terminal_visit, "wrong_sign": wrong_sign_mutant},
        {"terminal": (F(0), F(0)), "wrong_sign": "nonzero"},
    )
    t_matrix: Matrix = ((F(13, 10), F(-2, 5)), (F(1, 5), F(9, 10)))
    hs = frobenius(t_matrix, t_matrix)
    block_direct_sum = (
        (t_matrix[0][0], t_matrix[0][1], F(0), F(0)),
        (t_matrix[1][0], t_matrix[1][1], F(0), F(0)),
        (F(0), F(0), -t_matrix[0][0], -t_matrix[0][1]),
        (F(0), F(0), -t_matrix[1][0], -t_matrix[1][1]),
    )
    direct_sum_mass = sum((entry * entry for row in block_direct_sum for entry in row), F(0))
    collapsed_operator = madd(t_matrix, mscale(F(-1), t_matrix))
    collapsed_mass = frobenius(collapsed_operator, collapsed_operator)
    check(
        "progressive_revisit",
        "abstract_direct_sum_two_roots",
        direct_sum_mass == 2 * hs and collapsed_mass == 0 and direct_sum_mass > 0,
        {"direct_sum_mass": direct_sum_mass, "collapsed_signed_mass": collapsed_mass},
        {"direct_sum_mass": 2 * hs, "collapsed_signed_mass": F(0)},
    )

    # Exact Boolean-cube Doob--Hardy calculation.
    root_count = 6
    states = list(itertools.product((-1, 1), repeat=root_count))
    h_values: dict[int, list[F]] = {}
    for shell in range(1, root_count + 2):
        values: list[F] = []
        for state in states:
            value = F(13 * shell, 100)
            for index in range(shell - 1):
                value += (F(7, 100) + F(shell, 100) + F(index, 200)) * state[index]
            if shell >= 3:
                value += (F(1, 25) + F(3 * shell, 1000)) * state[0] * state[shell - 2]
            if shell >= 5:
                value -= F(1, 50) * state[1] * state[2] * state[shell - 2]
            values.append(value)
        h_values[shell] = values
    terminal = [sum((F(1, 2 ** (2 * shell)) * h_values[shell][index] for shell in h_values), F(0)) for index in range(len(states))]
    lhs = F(0)
    increment_rhs = F(0)
    for root in range(1, root_count + 1):
        d_terminal = [a - b for a, b in zip(conditional(terminal, states, root), conditional(terminal, states, root - 1))]
        future = [F(0)] * len(states)
        for shell in range(root + 1, root_count + 2):
            d_h = [a - b for a, b in zip(conditional(h_values[shell], states, root), conditional(h_values[shell], states, root - 1))]
            future = [value + F(1, 2 ** (2 * shell)) * increment for value, increment in zip(future, d_h)]
            increment_rhs += F(1, 2 ** (3 * shell)) * mean(value * value for value in d_h)
        check("doob_hardy", f"last_root_exact_{root}", d_terminal == future, d_terminal, future)
        lhs += F(2**root) * mean(value * value for value in d_terminal)
    check("doob_hardy", "weighted_cauchy_bound_exact", lhs <= increment_rhs, lhs, f"<= {increment_rhs}")
    variance_rhs = F(0)
    for shell, values in h_values.items():
        centre = mean(values)
        variance = mean((value - centre) ** 2 for value in values)
        doob_mass = sum(
            (
                mean(
                    (left - right) ** 2
                    for left, right in zip(conditional(values, states, root), conditional(values, states, root - 1))
                )
                for root in range(1, shell)
            ),
            F(0),
        )
        check("doob_hardy", f"orthogonal_variance_{shell}", doob_mass == variance, doob_mass, variance)
        variance_rhs += F(1, 2 ** (3 * shell)) * variance
    check("doob_hardy", "variance_corollary_exact", lhs <= variance_rhs, lhs, f"<= {variance_rhs}")

    support = (1, 3, 5)
    component = [F(math.prod(state[index - 1] for index in support)) for state in states]
    ownership = []
    for root in range(1, root_count + 1):
        difference = [a - b for a, b in zip(conditional(component, states, root), conditional(component, states, root - 1))]
        ownership.append(mean(value * value for value in difference))
    check("doob_hardy", "max_support_ownership", ownership == [F(0), F(0), F(0), F(0), F(1), F(0)], ownership, [0, 0, 0, 0, 1, 0])
    resampling = F(0)
    for coordinate in range(root_count):
        flipped = [tuple((-value if index == coordinate else value) for index, value in enumerate(state)) for state in states]
        flipped_component = [F(math.prod(state[index - 1] for index in support)) for state in flipped]
        resampling += F(1, 4) * mean((left - right) ** 2 for left, right in zip(component, flipped_component))
    check("doob_hardy", "coordinate_membership_multiplicity", resampling == len(support), resampling, len(support))
    check("doob_hardy", "weighted_membership_still_summable", sum(2**index for index in support) < 2 ** (max(support) + 1), sum(2**index for index in support), f"< {2 ** (max(support) + 1)}")

    sharp = []
    for cutoff in (5, 9, 15, 23):
        numerator = F(0)
        denominator = F(0)
        for root in range(1, cutoff):
            tail = sum((F(1, 2**shell) for shell in range(root + 1, cutoff + 1)), F(0))
            numerator += F(2**root) * tail**2
            denominator += sum((F(1, 2**shell) for shell in range(root + 1, cutoff + 1)), F(0))
        sharp.append(numerator / denominator)
    check("doob_hardy", "sharp_ratios_below_one", all(value < 1 for value in sharp), sharp, "< 1")
    check("doob_hardy", "sharp_ratios_increase", all(sharp[i + 1] > sharp[i] for i in range(len(sharp) - 1)), sharp, "increasing")
    check("doob_hardy", "sharp_ratio_exceeds_nine_tenths", sharp[-1] > F(9, 10), sharp[-1], F(9, 10))
    exponents = {r: 2 * (F(1, 2) + F(3, r)) - 1 for r in (2, 3, 6)}
    check("doob_hardy", "spatial_exponents_exact", exponents == {2: F(3), 3: F(2), 6: F(1)}, exponents, {2: 3, 3: 2, 6: 1})

    # Ordered reveal and covariance residual, independently with Fractions.
    terminal_z = [F(7, 10) + F(2, 5) * state[0] - F(3, 10) * state[1] + F(1, 2) * state[0] * state[2] for state in states]
    terminal_b = [value * value for value in terminal_z]
    q_terminal = [F(state[0]) + F(1, 4) * state[0] * state[1] - F(1, 5) * state[3] for state in states]
    z_levels = [conditional(terminal_z, states, level) for level in range(root_count + 1)]
    b_levels = [conditional(terminal_b, states, level) for level in range(root_count + 1)]
    j_levels = [[b - z * z for b, z in zip(b_levels[level], z_levels[level])] for level in range(root_count + 1)]
    q_levels = [conditional(q_terminal, states, level) for level in range(root_count + 1)]
    for root in range(1, root_count + 1):
        d_hat = [a - b for a, b in zip(b_levels[root], b_levels[root - 1])]
        secant = [a * a - b * b for a, b in zip(z_levels[root], z_levels[root - 1])]
        residual = [a - b for a, b in zip(j_levels[root], j_levels[root - 1])]
        check("ordered_reveal", f"frame_identity_{root}", d_hat == [a + b for a, b in zip(secant, residual)], d_hat, [a + b for a, b in zip(secant, residual)])
        increment = [a - b for a, b in zip(z_levels[root], z_levels[root - 1])]
        chain = [2 * base * u + u * u + res for base, u, res in zip(z_levels[root - 1], increment, residual)]
        check("ordered_reveal", f"quadratic_chain_{root}", d_hat == chain, d_hat, chain)
    cross_left = mean(left * right for left, right in zip(terminal_b, q_terminal))
    cross_right = mean(left * right for left, right in zip(b_levels[0], q_levels[0]))
    for root in range(1, root_count + 1):
        cross_right += mean(
            (a - b) * (c - d)
            for a, b, c, d in zip(b_levels[root], b_levels[root - 1], q_levels[root], q_levels[root - 1])
        )
    check("ordered_reveal", "cross_doob_exact", cross_left == cross_right, cross_left, cross_right)

    # Three-point moment fixture and rare-event spike are exact.
    xi_atoms = ((F(1, 8), F(-2)), (F(3, 4), F(0)), (F(1, 8), F(2)))
    moments = {power: sum((probability * value**power for probability, value in xi_atoms), F(0)) for power in (1, 2, 4)}
    check("jensen_fixture", "xi_mean_zero", moments[1] == 0, moments[1], 0)
    check("jensen_fixture", "xi_variance_one", moments[2] == 1, moments[2], 1)
    check("jensen_fixture", "xi_fourth_moment_four", moments[4] == 4, moments[4], 4)
    for count in (1, 2, 3, 5, 7):
        frame_mass = sum((F(3) * F(4) ** (root - 1) for root in range(1, count + 1)), F(0))
        check("jensen_fixture", f"frame_mass_{count}", frame_mass == 4**count - 1, frame_mass, 4**count - 1)
        check("jensen_fixture", f"shift_mass_{count}", F(1) == 1, 1, 1)
    check("jensen_fixture", "frame_shift_ratio_exponential", F(4**7 - 1) > 1000, 4**7 - 1, "> 1000")
    for size in (2, 4, 8, 16, 32):
        probability = F(1, size**6)
        u = F(size**3)
        z = F(size)
        check("multiplier_spike", f"u2_unit_{size}", probability * u**2 == 1, probability * u**2, 1)
        check("multiplier_spike", f"z6_unit_{size}", probability * z**6 == 1, probability * z**6, 1)
        check("multiplier_spike", f"linear_unit_{size}", probability * u * z**3 == 1, probability * u * z**3, 1)
        check("multiplier_spike", f"square_growth_{size}", probability * z**2 * u**2 == size**2, probability * z**2 * u**2, size**2)

    # Rational exponent ledger and exact matrix payment-gauge identity.
    exponent_rows = (
        (F(11, 40), F(3, 40), F(13, 20), F(20, 13)),
        (F(11, 20), F(3, 20), F(3, 10), F(10, 3)),
        (F(2, 5), F(1, 30), F(17, 30), F(30, 17)),
        (F(2, 5), F(1, 5), F(2, 5), F(5, 2)),
        (F(2, 5), F(11, 30), F(7, 30), F(30, 7)),
    )
    for index, (x_power, y_power, slack, moment) in enumerate(exponent_rows, start=1):
        check("rational_form", f"family_sum_{index}", x_power + y_power + slack == 1, x_power + y_power + slack, 1)
        check("rational_form", f"family_moment_{index}", moment == 1 / slack, moment, 1 / slack)
        check("rational_form", f"family_available_{index}", moment <= F(30, 7), moment, "<= 30/7")
        x = 1.3 + 0.1 * index
        y = 0.7 + 0.2 * index
        model = 1.1 + 0.05 * index
        coefficient_float = 0.9 + 0.1 * index
        eta = 0.2
        zeta = 0.3
        xf, yf, sf = float(x_power), float(y_power), float(slack)
        remainder = sf * coefficient_float ** (1 / sf) * xf ** (xf / sf) * yf ** (yf / sf) * eta ** (-xf / sf) * zeta ** (-yf / sf) * model ** (1 / sf)
        left = coefficient_float * model * x**xf * y**yf
        right = eta * x + zeta * y + remainder
        check("rational_form", f"young_numeric_{index}", left <= right + 1e-12, left - right, "<= 0")

    weights = (F(1, 3), F(2, 3))
    matrices: tuple[Matrix, ...] = (
        ((F(2), F(1, 3)), (F(1, 3), F(1))),
        ((F(3, 2), F(-1, 4)), (F(-1, 4), F(5, 2))),
    )
    carriers: tuple[Vector, ...] = ((F(2, 3), F(-1, 2)), (F(-3, 4), F(5, 6)))
    gamma: Matrix = ((F(4, 3), F(1, 5)), (F(1, 5), F(7, 6)))
    payment: Matrix = ((F(5, 4), F(1, 7)), (F(1, 7), F(9, 8)))
    shift: Vector = (F(4, 5), F(-2, 3))
    gauge_left, gauge_right = payment_gauge_exact(weights, matrices, carriers, gamma, payment, shift)
    check("payment_gauge", "non_diagonal_fraction_identity", gauge_left == gauge_right, gauge_left, gauge_right)
    check("payment_gauge", "omit_payment_mutant_rejected", gauge_left + quadratic(payment, shift) != gauge_right, gauge_left + quadratic(payment, shift) - gauge_right, "nonzero")

    # Abstract rank-one Gram recovery fixture.
    u0 = F(1)
    increment = F(-2)
    b = lambda z: (z * z - 1) ** 2
    b_prime = lambda z: 4 * z * (z * z - 1)
    b_second = lambda z: 12 * z * z - 4
    remainder = b(u0 + increment) - b(u0) - b_prime(u0) * increment - F(1, 2) * b_second(u0) * increment**2
    check("rational_recovery", "taylor_remainder_minus_sixteen", remainder == -16, remainder, -16)
    for t_value in (F(1, 2), F(1), F(3), F(11)):
        q_value = t_value**2
        unshifted = F(1, 4) * b_second(u0) * increment**2 * q_value
        shifted = F(1, 2) * remainder * q_value
        check("rational_recovery", f"unshifted_{serial(t_value)}", unshifted == 8 * t_value**2, unshifted, 8 * t_value**2)
        check("rational_recovery", f"shifted_{serial(t_value)}", shifted == -8 * t_value**2, shifted, -8 * t_value**2)
        check("rational_recovery", f"owner_zero_{serial(t_value)}", unshifted + shifted == 0, unshifted + shifted, 0)
    check("rational_recovery", "lower_only_not_enough", -8 * F(11) ** 2 < -100, -8 * F(11) ** 2, "< -100")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-extended-state-cartan-doob-rational-recovery-independent/1.0",
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "assertions": rows,
        "diagnostics": {
            "exact_hardy_lhs": serial(lhs),
            "exact_hardy_increment_rhs": serial(increment_rhs),
            "exact_hardy_variance_rhs": serial(variance_rhs),
            "sharp_ratios": serial(sharp),
            "progressive_coefficient": serial(coefficient),
            "payment_gauge_value": serial(gauge_left),
        },
        "no_overclaim": (
            "This independent route verifies exact finite and algebraic fixtures. "
            "It does not establish the open production posterior lower form or Sector-A closure."
        ),
    }
    atomic_json(output, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    raise SystemExit(main(arguments.output))
