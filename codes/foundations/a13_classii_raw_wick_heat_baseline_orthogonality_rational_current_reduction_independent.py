#!/usr/bin/env python3
"""Independent exact-arithmetic certificate for R-101.

This verifier intentionally imports neither NumPy nor the primary R-101
certificate.  Fractions on a finite strict-past filtration check the moving
heat-baseline orthogonality and cross-Doob identity.  Separate exact fixtures
check the derivative-current regrouping, endpoint telescope, Taylor ledger,
and the production rational-row range identity.
"""

from __future__ import annotations

__version__ = "1.0.2"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import itertools
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Callable, Iterable, Sequence


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RAW-WICK-HEAT-BASELINE-ORTHOGONALITY-RATIONAL-CURRENT-REDUCTION"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-27-independent-raw-wick-heat-baseline-orthogonality-rational-current-reduction/result.json"
)


def encode(value: object) -> object:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def equal(self, group: str, name: str, actual: object, expected: object) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if actual == expected else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def true(self, group: str, name: str, condition: bool, actual: object) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": actual,
                "expected": True,
            }
        )


Vector = tuple[F, F]
Matrix = tuple[tuple[F, F], tuple[F, F]]


def dot(left: Vector, right: Vector) -> F:
    return left[0] * right[0] + left[1] * right[1]


def mv(matrix: Matrix, vector: Vector) -> Vector:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


def quad(vector: Vector, matrix: Matrix) -> F:
    return dot(vector, mv(matrix, vector))


def madd(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[row][column] + right[row][column] for column in range(2))
        for row in range(2)
    )  # type: ignore[return-value]


def msub(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(2))
        for row in range(2)
    )  # type: ignore[return-value]


def mscale(scale: F, matrix: Matrix) -> Matrix:
    return tuple(
        tuple(scale * matrix[row][column] for column in range(2)) for row in range(2)
    )  # type: ignore[return-value]


def minner(left: Matrix, right: Matrix) -> F:
    return sum((left[row][column] * right[row][column] for row in range(2) for column in range(2)), F(0))


def outer(vector: Vector) -> Matrix:
    return (
        (vector[0] * vector[0], vector[0] * vector[1]),
        (vector[1] * vector[0], vector[1] * vector[1]),
    )


def vadd(left: Vector, right: Vector) -> Vector:
    return (left[0] + right[0], left[1] + right[1])


def polynomial_product(left: list[F], right: list[F]) -> list[F]:
    answer = [F(0) for _ in range(len(left) + len(right) - 1)]
    for left_degree, left_coefficient in enumerate(left):
        for right_degree, right_coefficient in enumerate(right):
            answer[left_degree + right_degree] += left_coefficient * right_coefficient
    return answer


def polynomial_derivative_value(coefficients: list[F], point: F, order: int) -> F:
    total = F(0)
    for degree, coefficient_value in enumerate(coefficients):
        if degree < order:
            continue
        falling = math.prod(range(degree - order + 1, degree + 1))
        total += coefficient_value * falling * point ** (degree - order)
    return total


def rational_taylor_coefficients(numerator: list[F], denominator: list[F], point: F, order: int) -> list[F]:
    numerator_series = [
        polynomial_derivative_value(numerator, point, derivative) / F(math.factorial(derivative))
        for derivative in range(order + 1)
    ]
    denominator_series = [
        polynomial_derivative_value(denominator, point, derivative) / F(math.factorial(derivative))
        for derivative in range(order + 1)
    ]
    quotient = [F(0) for _ in range(order + 1)]
    for degree in range(order + 1):
        correction = sum(
            (denominator_series[index] * quotient[degree - index] for index in range(1, degree + 1)),
            F(0),
        )
        quotient[degree] = (numerator_series[degree] - correction) / denominator_series[0]
    return quotient


def direct_scalar_balanced_heat_oracles() -> dict[str, F]:
    """Independent polynomial-derivative derivation of the scalar boundary."""
    alpha = F(5, 9)
    x_squared = [F(0), F(0), F(1)]
    rational_factor = [F(1), F(0), F(1) - alpha]
    numerator = [4 * coefficient_value for coefficient_value in polynomial_product(
        x_squared, polynomial_product(rational_factor, rational_factor)
    )]
    denominator_factor = [F(1), F(0), F(1)]
    denominator = polynomial_product(denominator_factor, denominator_factor)
    at_initial = rational_taylor_coefficients(numerator, denominator, F(1), 3)
    at_zero = rational_taylor_coefficients(numerator, denominator, F(0), 3)
    full_remainder = -at_initial[0] + at_initial[1] - at_initial[2]
    base_cubic = -at_initial[3]
    balanced_remainder = full_remainder - base_cubic
    heat_square_leading = at_zero[2]
    return {
        "scalar_full_remainder": full_remainder,
        "scalar_base_cubic": base_cubic,
        "scalar_balanced_remainder": balanced_remainder,
        "zero_heat_square_leading_coefficient": heat_square_leading,
        "balanced_schur_divergence_coefficient": balanced_remainder**2 / (2 * heat_square_leading),
    }


def expectation(weights: Sequence[F], values: Sequence[F]) -> F:
    return sum((weight * value for weight, value in zip(weights, values)), F(0))


def conditional(
    values: Sequence[F],
    states: Sequence[tuple[tuple[int, int], ...]],
    weights: Sequence[F],
    revealed: int,
) -> list[F]:
    groups: dict[tuple[tuple[int, int], ...], list[int]] = {}
    for index, state in enumerate(states):
        groups.setdefault(state[:revealed], []).append(index)
    answer = [F(0) for _ in values]
    for indices in groups.values():
        mass = sum((weights[index] for index in indices), F(0))
        mean = sum((weights[index] * values[index] for index in indices), F(0)) / mass
        for index in indices:
            answer[index] = mean
    return answer


def coefficient(value: F) -> F:
    return F(1) + value * value + value**4


def polynomial_matrix(z: Vector) -> Matrix:
    x, y = z
    off = x * y + x * x * y * y
    return ((F(1) + x * x + x**4, off), (off, F(2) + y * y + y**4))


def polynomial_d1(z: Vector, h: Vector) -> Matrix:
    x, y = z
    hx, hy = h
    off = y * hx + x * hy + 2 * x * y * y * hx + 2 * x * x * y * hy
    return (((2 * x + 4 * x**3) * hx, off), (off, (2 * y + 4 * y**3) * hy))


def polynomial_d2(z: Vector, h: Vector) -> Matrix:
    x, y = z
    hx, hy = h
    off = 2 * hx * hy + 2 * y * y * hx * hx + 8 * x * y * hx * hy + 2 * x * x * hy * hy
    return (((2 + 12 * x * x) * hx * hx, off), (off, (2 + 12 * y * y) * hy * hy))


def main() -> int:
    audit = Audit()

    # Exact finite strict-past filtration.  Each fresh value root g_j and
    # derivative root d_j is independent with law (1/4, 1/2, 1/4) on
    # {-1, 0, 1}.  This is the discrete same-point analogue of the real-even
    # Gaussian value/gradient independence used by the theorem.
    support = (-1, 0, 1)
    law = {-1: F(1, 4), 0: F(1, 2), 1: F(1, 4)}
    states = list(itertools.product(list(itertools.product(support, support)), repeat=3))
    weights = [
        law[state[0][0]]
        * law[state[0][1]]
        * law[state[1][0]]
        * law[state[1][1]]
        * law[state[2][0]]
        * law[state[2][1]]
        for state in states
    ]
    audit.equal("filtration", "probability_mass", sum(weights, F(0)), F(1))
    derivative_variance = F(1, 2)
    controls: list[list[F]] = [
        [F(1, 5) for _ in states],
        [F(2 * state[0][0] - state[0][1], 7) for state in states],
        [F(state[0][0] * state[1][0] + state[0][1] * state[1][1], 9) for state in states],
    ]
    prefixes: list[list[F]] = [[F(0) for _ in states]]
    for control in controls:
        prefixes.append([old + increment for old, increment in zip(prefixes[-1], control)])
    terminal_u = [F(sum(pair[0] for pair in state)) for state in states]
    terminal_b = [coefficient(u + a) for u, a in zip(terminal_u, prefixes[-1])]
    f_levels = [conditional(terminal_b, states, weights, level) for level in range(4)]
    l_levels: list[list[F]] = []
    h_levels: list[list[F]] = []
    q_levels: list[list[F]] = []
    for level in range(4):
        b_level = [coefficient(u + a) for u, a in zip(terminal_u, prefixes[level])]
        l_level = conditional(b_level, states, weights, level)
        l_levels.append(l_level)
        h_levels.append([f - ell for f, ell in zip(f_levels[level], l_level)])
        q_levels.append(
            [F(sum(pair[1] for pair in state[:level])) ** 2 - level * derivative_variance for state in states]
        )

    direct_residuals: list[F] = []
    for level in range(1, 4):
        delta_q = [new - old for new, old in zip(q_levels[level], q_levels[level - 1])]
        baseline = expectation(
            weights,
            [(new - old) * dq for new, old, dq in zip(l_levels[level], l_levels[level - 1], delta_q)],
        )
        h_cross = expectation(
            weights,
            [(new - old) * dq for new, old, dq in zip(h_levels[level], h_levels[level - 1], delta_q)],
        )
        b_level = [coefficient(u + a) for u, a in zip(terminal_u, prefixes[level])]
        direct = expectation(weights, [(last - now) * dq for last, now, dq in zip(terminal_b, b_level, delta_q)])
        direct_residuals.append(direct)
        audit.equal("orthogonality", f"moving_heat_baseline_{level}", baseline, F(0))
        audit.equal("orthogonality", f"future_control_residual_{level}", h_cross, direct)

    terminal_wick = expectation(weights, [b * q for b, q in zip(terminal_b, q_levels[-1])])
    low_wick = expectation(weights, [b * q for b, q in zip(f_levels[0], q_levels[0])])
    audit.equal("cross_doob", "terminal_raw_wick", terminal_wick, low_wick + sum(direct_residuals, F(0)))

    # Start a second Cross--Doob identity at a nonzero low endpoint so that
    # dropping or sign-flipping the fixed-low owner is detected exactly.
    low_terminal_b = [F(state[0][0] + state[1][0] + state[0][1]) ** 2 for state in states]
    low_f = conditional(low_terminal_b, states, weights, 1)
    q_low = [F(state[0][1]) ** 2 - derivative_variance for state in states]
    q_next = [F(state[0][1] + state[1][1]) ** 2 - 2 * derivative_variance for state in states]
    fixed_low = expectation(weights, [b * q for b, q in zip(low_f, q_low)])
    terminal_with_low = expectation(weights, [b * q for b, q in zip(low_terminal_b, q_next)])
    audit.equal("cross_doob", "nonzero_fixed_low_endpoint", fixed_low, F(1, 4))
    audit.equal("cross_doob", "nonzero_low_terminal_identity", terminal_with_low, fixed_low)

    correlated_cross = sum((law[x] * F(x**2) * (F(x**2) - derivative_variance) for x in support), F(0))
    audit.equal("scope", "correlated_value_gradient_cross", correlated_cross, F(1, 4))
    direct_gradient_cross = sum(
        (
            law[g_value]
            * law[d_value]
            * F(d_value**2)
            * (F(d_value**2) - derivative_variance)
            for g_value, d_value in itertools.product(support, repeat=2)
        ),
        F(0),
    )
    local_value_gradient_covariance = sum(
        (law[g_value] * law[d_value] * F(g_value * d_value) for g_value, d_value in itertools.product(support, repeat=2)),
        F(0),
    )
    two_site_nonlocal_cross = sum(
        (
            law[g_value]
            * law[d_value]
            * F(d_value**2)
            * (F(d_value**2) - derivative_variance)
            for g_value, d_value in itertools.product(support, repeat=2)
        ),
        F(0),
    )
    same_root_control_cross = sum(
        (
            law[g_value]
            * law[d_value]
            * F((g_value + d_value) ** 2)
            * (F(d_value**2) - derivative_variance)
            for g_value, d_value in itertools.product(support, repeat=2)
        ),
        F(0),
    )
    audit.equal("scope", "direct_gradient_coefficient_cross", direct_gradient_cross, F(1, 4))
    audit.equal("scope", "two_site_same_point_covariance_zero", local_value_gradient_covariance, F(0))
    audit.equal("scope", "two_site_nonlocal_cross", two_site_nonlocal_cross, F(1, 4))
    audit.equal("scope", "same_root_control_cross", same_root_control_cross, F(1, 4))

    # Exact 2x2 noncommuting derivative-current algebra.
    b_minus: Matrix = ((F(2), F(1)), (F(1), F(3)))
    b_plus: Matrix = ((F(5), F(-1)), (F(-1), F(4)))
    gamma: Matrix = ((F(3, 2), F(1, 3)), (F(1, 3), F(5, 4)))
    g: Vector = (F(2, 3), F(-3, 5))
    c: Vector = (F(5, 7), F(1, 4))
    fresh: Vector = (F(-2, 9), F(4, 11))
    delta_b = msub(b_plus, b_minus)
    gc = vadd(g, c)
    gcf = vadd(gc, fresh)
    full = F(1, 2) * (
        quad(gcf, b_plus) - minner(b_plus, gamma) - quad(gc, b_minus) + minner(b_minus, gamma)
    )
    raw_wick = F(1, 2) * minner(delta_b, msub(outer(g), gamma))
    remainder = (
        dot(g, mv(delta_b, c))
        + F(1, 2) * quad(c, delta_b)
        + dot(gc, mv(b_plus, fresh))
        + F(1, 2) * quad(fresh, b_plus)
    )
    regrouped = dot(g, vadd(mv(b_plus, vadd(c, fresh)), tuple(-entry for entry in mv(b_minus, c)))) + F(1, 2) * (
        quad(vadd(c, fresh), b_plus) - quad(c, b_minus)
    )
    audit.equal("current_remainder", "raw_plus_current_partition", full, raw_wick + remainder)
    audit.equal("current_remainder", "exact_regroup", remainder, regrouped)

    # The control-only pieces telescope exactly under matched endpoints.
    matrices: list[Matrix] = [
        ((F(2), F(0)), (F(0), F(3))),
        ((F(4), F(1)), (F(1), F(5))),
        ((F(3), F(-1)), (F(-1), F(6))),
    ]
    derivative_prefixes: list[Vector] = [(F(0), F(0)), (F(1, 3), F(-2, 5)), (F(7, 12), F(1, 10))]
    telescope = sum(
        (
            F(1, 2)
            * (
                quad(derivative_prefixes[level], matrices[level])
                - quad(derivative_prefixes[level - 1], matrices[level - 1])
            )
            for level in range(1, 3)
        ),
        F(0),
    )
    endpoint = F(1, 2) * (
        quad(derivative_prefixes[-1], matrices[-1]) - quad(derivative_prefixes[0], matrices[0])
    )
    audit.equal("control_square", "matched_endpoint_telescope", telescope, endpoint)
    audit.true("control_square", "zero_low_endpoint_nonnegative", endpoint >= 0, endpoint)

    # Exact Taylor partition of the surviving current cross.
    u: Vector = (F(2, 5), F(-1, 3))
    a: Vector = (F(3, 7), F(2, 9))
    current: Vector = (F(5, 8), F(-4, 11))
    dc: Vector = (F(7, 13), F(1, 6))
    p0 = polynomial_matrix(u)
    p1 = polynomial_matrix(vadd(u, a))
    taylor2 = madd(p0, madd(polynomial_d1(u, a), mscale(F(1, 2), polynomial_d2(u, a))))
    shifted = msub(p1, taylor2)
    audit.equal(
        "taylor",
        "current_cross_partition",
        dot(current, mv(p1, dc)),
        dot(current, mv(taylor2, dc)) + dot(current, mv(shifted, dc)),
    )
    audit.true("taylor", "shifted_current_is_not_algebraically_zero", dot(current, mv(shifted, dc)) != 0, dot(current, mv(shifted, dc)))

    # Derive exact production constants from the hash-pinned A1 decimal input.
    model = json.loads(
        (REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json").read_text(
            encoding="utf-8"
        ),
        parse_float=F,
    )
    parameters = model["parameters"]
    parameter = lambda name: F(parameters[name])
    floor = parameter("rho_regularizer")
    p_mass = parameter("M_X") ** 2 + floor
    q11 = parameter("cJJ") * parameter("alpha_X") ** 2 / p_mass
    q12 = parameter("cJK") * parameter("alpha_X") * parameter("beta_X") / p_mass
    q22 = parameter("cKK") * parameter("beta_X") ** 2 / p_mass
    alpha = q22 / (q12 + q22)
    c1 = q22 / alpha**2
    c0 = q11 - q12**2 / q22
    audit.equal("production", "production_floor", floor, F(1, 10**12))
    audit.equal("production", "production_p_mass", p_mass, F(4_000_000_000_001, 10**12))
    audit.equal("production", "alpha", alpha, F(5, 9))
    audit.equal("production", "c0", c0, F(3, 250) / p_mass)
    audit.equal("production", "c1", c1, F(243, 8000) / p_mass)

    balanced_heat = direct_scalar_balanced_heat_oracles()
    labelled_test_oracles = {
        "scalar_full_remainder": F(40, 81),
        "scalar_base_cubic": F(-25, 81),
        "scalar_balanced_remainder": F(65, 81),
        "zero_heat_square_leading_coefficient": F(4),
        "balanced_schur_divergence_coefficient": F(4225, 52488),
    }
    for name, expected in labelled_test_oracles.items():
        audit.equal("balanced_heat_boundary", name, balanced_heat[name], expected)

    projector_indices = (0, 1, 3, 4)
    rational_rows: list[dict[str, F]] = []
    rational_fixtures = (
        (F(0), F(0), F(0), F(0), F(0), F(0)),
        (F(1, 10**6), F(0), F(0), F(0), F(0), F(0)),
        (F(1), F(-2), F(3), F(2), F(0), F(-1)),
    )
    for z in rational_fixtures:
        radius = sum((z[index] ** 2 for index in projector_indices), F(0))
        norm2 = sum((value * value for value in z), F(0))
        denominator = norm2 + floor
        projected = tuple(z[index] if index in projector_indices else F(0) for index in range(6))
        rational_vector = tuple(projected[index] - alpha * radius / denominator * z[index] for index in range(6))
        gap = radius - sum((value * value for value in rational_vector), F(0))
        formula = alpha * radius**2 / denominator**2 * (2 * denominator - alpha * norm2)
        audit.equal("production", f"rational_range_identity_{len(rational_rows)}", gap, formula)
        audit.true("production", f"rational_range_domination_{len(rational_rows)}", gap >= 0, gap)
        if len(rational_rows) == 1:
            audit.equal("production", "near_floor_pure_doublet_oracle", gap / floor, alpha * (4 - alpha) / 4)
        rational_rows.append({"gap": gap, "formula": formula})

    passed = sum(row["status"] == "PASS" for row in audit.rows)
    result: dict[str, object] = {
        "schema": "tect/a13-raw-wick-heat-baseline-orthogonality-rational-current-reduction-independent/1.0",
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(audit.rows) else "FAIL",
        "assertions_total": len(audit.rows),
        "assertions_passed": passed,
        "assertions_failed": len(audit.rows) - passed,
        "assertions": audit.rows,
        "diagnostics": {
            "terminal_raw_wick": terminal_wick,
            "low_raw_wick": low_wick,
            "residual_sum": sum(direct_residuals, F(0)),
            "nonzero_fixed_low_endpoint": fixed_low,
            "correlated_cross": correlated_cross,
            "direct_gradient_cross": direct_gradient_cross,
            "two_site_same_point_covariance": local_value_gradient_covariance,
            "two_site_nonlocal_cross": two_site_nonlocal_cross,
            "same_root_control_cross": same_root_control_cross,
            "control_square_endpoint": endpoint,
            "shifted_current_fixture": dot(current, mv(shifted, dc)),
            "production_constants": {"p_mass": p_mass, "floor": floor, "alpha": alpha, "c0": c0, "c1": c1},
            "balanced_heat_boundary": balanced_heat,
            "rational_rows": rational_rows,
        },
        "no_overclaim": (
            "The exact certificate closes the regular strict-past moving raw-Wick heat-baseline cross and "
            "checks the rational-current reduction. It does not prove the surviving shifted-current Hessian "
            "form, complete rational H_N, REG, progressive H_A, OVERLAP_src, Nelson, a measure, or Sector A."
        ),
    }
    atomic_json(OUTPUT, result)
    print(
        json.dumps(
            {
                "assertions": len(audit.rows),
                "output": str(OUTPUT.relative_to(REPO)),
                "status": result["status"],
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
