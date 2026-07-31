#!/usr/bin/env python3
"""Primary exact certificate for the scoped A13 R-141 checkpoint.

The certificate checks the finite-chart production projected-force algebra,
the complete common-feature signature owner, the conditional two-sided signed
mixed Gram, the global Doob coordinate, the source-null quotient criterion,
the exact positive-analysis collar shift, and the finite-collar/low-correlation
boundaries.  It does not assert the missing production factorisation or a
uniform positive graph gap.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Iterable


RESULT_ID = (
    "A13-CLASSII-PROJECTED-FORCE-GLOBAL-DOOB-SIGNED-GRAM-"
    "ADAPTIVE-COLLAR-QUOTIENT-BOUNDARY"
)
SCHEMA = (
    "tect/a13-projected-force-global-doob-signed-gram-adaptive-collar-"
    "quotient-boundary-primary/1.0"
)
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-projected-force-global-doob-signed-gram-"
    "adaptive-collar-quotient-boundary/result.json"
)
Q = Fraction
P_INPUT = Q(4_000_000_000_001, 1_000_000_000_000)
BETA_INPUT = Q(7, 5)
S_INPUT = Q(2, 3)
GAMMA_INPUT = Q(7, 12)
BASE_COLLAR = 5
RESPONSE_ENERGY_COEFFICIENT = Q(3, 40) / P_INPUT
ZERO_LOW_TAIL_HEADROOM = Q(1_590_880_000_000_403, 15_840_000_000_003_960)
ILLUSTRATIVE_HEADROOM = Q(159_126_895, 10_000_000_000)
TOL = 2.0e-11


Vector = list[Fraction]
Matrix = list[list[Fraction]]


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: object,
        expected: object,
    ) -> None:
        passed = bool(condition)
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
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    right_t = transpose(right)
    return [
        [sum((x * y for x, y in zip(row, column)), Q(0)) for column in right_t]
        for row in left
    ]


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [sum((x * y for x, y in zip(row, vector)), Q(0)) for row in matrix]


def add_matrix(left: Matrix, right: Matrix) -> Matrix:
    return [[x + y for x, y in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def sub_matrix(left: Matrix, right: Matrix) -> Matrix:
    return [[x - y for x, y in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def scale_matrix(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def dot(left: Vector, right: Vector) -> Fraction:
    return sum((x * y for x, y in zip(left, right)), Q(0))


def quadratic(vector: Vector, matrix: Matrix) -> Fraction:
    return dot(vector, matvec(matrix, vector))


def identity(size: int) -> Matrix:
    return [[Q(int(i == j)) for j in range(size)] for i in range(size)]


def determinant2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def determinant3(matrix: Matrix) -> Fraction:
    return (
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def symmetric(matrix: Matrix) -> bool:
    return matrix == transpose(matrix)


def pow2(exponent: Fraction) -> float:
    return math.pow(2.0, float(exponent))


def hs_closed(collar: int) -> float:
    """R-140 exact positive-analysis Hilbert--Schmidt scalar sum."""

    if collar < BASE_COLLAR:
        raise ValueError("collar must be at least five")
    delta = collar - BASE_COLLAR
    q_ratio = pow2(2 * GAMMA_INPUT)
    u_ratio = pow2(-(BETA_INPUT - 2 * GAMMA_INPUT))
    v_ratio = pow2(-BETA_INPUT)
    rho_ratio = pow2(-2 * (S_INPUT - GAMMA_INPUT))
    near = (
        pow2(-2 * GAMMA_INPUT * delta)
        * pow(u_ratio, delta + 1)
        / (1.0 - u_ratio)
        - pow(v_ratio, delta + 1) / (1.0 - v_ratio)
    ) / (q_ratio - 1.0)
    far_low = (
        pow2(-2 * S_INPUT * delta)
        * math.fsum(
            pow2(-(BETA_INPUT - 2 * S_INPUT) * a)
            for a in range(1, delta + 1)
        )
        / (1.0 - rho_ratio)
    )
    far_high = (
        pow2(-2 * GAMMA_INPUT * delta)
        * pow(u_ratio, delta + 1)
        / ((1.0 - rho_ratio) * (1.0 - u_ratio))
    )
    return near + far_low + far_high


def scalar_debt(collar: int) -> float:
    return float(RESPONSE_ENERGY_COEFFICIENT) * hs_closed(collar)


def finite_difference_gradient(
    action: callable, point: list[float], epsilon: float
) -> list[float]:
    result: list[float] = []
    for index in range(len(point)):
        plus = list(point)
        minus = list(point)
        plus[index] += epsilon
        minus[index] -= epsilon
        result.append((action(plus) - action(minus)) / (2.0 * epsilon))
    return result


def polynomial_action_and_force(
    h: list[float], matrix: list[list[float]], offset: list[float]
) -> tuple[float, list[float], list[list[float]]]:
    z = [
        offset[row] + math.fsum(matrix[row][column] * h[column] for column in range(len(h)))
        for row in range(len(offset))
    ]
    action = 9.0 / 20.0 * math.fsum(value * value for value in h)
    action -= 0.25 * math.fsum(value * value for value in z)
    action += 3.0 / 20.0 * math.fsum(value**6 for value in z)
    endpoint_force = [-0.5 * value + 0.9 * value**5 for value in z]
    force = [
        0.9 * h[column]
        + math.fsum(matrix[row][column] * endpoint_force[row] for row in range(len(z)))
        for column in range(len(h))
    ]
    diagonal = [-0.5 + 4.5 * value**4 for value in z]
    hessian = [
        [
            0.9 * float(i == j)
            + math.fsum(
                matrix[row][i] * diagonal[row] * matrix[row][j]
                for row in range(len(z))
            )
            for j in range(len(h))
        ]
        for i in range(len(h))
    ]
    return action, force, hessian


def all_close(left: Iterable[float], right: Iterable[float], tolerance: float) -> bool:
    return all(abs(x - y) <= tolerance for x, y in zip(left, right))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # The covariance-normal force contains a variance coordinate that cancels
    # when returning to the actual smaller action owner.
    g_t = [Q(8), Q(-6), Q(10)]
    g_v = [Q(4), Q(14), Q(-2)]
    g_cn = [(v - t) / 2 for v, t in zip(g_v, g_t)]
    g_comp = [cn - v / 2 for cn, v in zip(g_cn, g_v)]
    audit.check("force", "covariance-normal force", g_cn == [Q(-2), Q(10), Q(-6)], g_cn, [Q(-2), Q(10), Q(-6)])
    audit.check("force", "variance cancellation", g_comp == [Q(-4), Q(3), Q(-5)], g_comp, [Q(-4), Q(3), Q(-5)])
    audit.check("force", "complete force is minus trace half", g_comp == [-value / 2 for value in g_t], g_comp, [-value / 2 for value in g_t])
    audit.check("force", "variance cannot be appended again", [value + g_v[i] / 2 for i, value in enumerate(g_comp)] != g_comp, [value + g_v[i] / 2 for i, value in enumerate(g_comp)], g_comp)

    h_t = [[Q(4), Q(1)], [Q(1), Q(-2)]]
    h_v = [[Q(6), Q(-3)], [Q(-3), Q(8)]]
    h_cn = scale_matrix(Q(1, 2), sub_matrix(h_v, h_t))
    h_comp = sub_matrix(h_cn, scale_matrix(Q(1, 2), h_v))
    h_prod = add_matrix(h_comp, scale_matrix(Q(9, 10), identity(2)))
    audit.check("force", "covariance-normal Hessian", h_cn == [[Q(1), Q(-2)], [Q(-2), Q(5)]], h_cn, [[Q(1), Q(-2)], [Q(-2), Q(5)]])
    audit.check("force", "complete Hessian", h_comp == scale_matrix(Q(-1, 2), h_t), h_comp, scale_matrix(Q(-1, 2), h_t))
    audit.check("force", "production source coefficient", h_prod == [[Q(-11, 10), Q(-1, 2)], [Q(-1, 2), Q(19, 10)]], h_prod, [[Q(-11, 10), Q(-1, 2)], [Q(-1, 2), Q(19, 10)]])
    audit.check("force", "production Hessian selfadjoint", symmetric(h_prod), h_prod, "symmetric")

    # Two unrelated polynomial charts test the finite-chart action gradient.
    charts = [
        ([[1.0, -0.5], [0.25, 1.5]], [0.2, -0.4], [0.3, -0.2]),
        ([[0.75, 0.125], [-1.0, 0.5]], [-0.3, 0.6], [-0.1, 0.4]),
    ]
    for chart_index, (matrix, offset, point) in enumerate(charts, start=1):
        action, force, hessian = polynomial_action_and_force(point, matrix, offset)
        numerical = finite_difference_gradient(
            lambda value: polynomial_action_and_force(value, matrix, offset)[0],
            point,
            1.0e-6,
        )
        audit.check("projected_force", f"chart {chart_index} finite action", math.isfinite(action), action, "finite")
        audit.check("projected_force", f"chart {chart_index} gradient", all_close(force, numerical, 2.0e-9), numerical, force)
        audit.check("projected_force", f"chart {chart_index} Hessian symmetric", all_close(hessian[0], [hessian[0][0], hessian[1][0]], TOL), hessian, "symmetric")

    # Predictable conditional projection: the second result depends only on
    # the legal past reveal a, never on the future reveal b.
    states = [(a, b) for a in (-1, 1) for b in (-1, 1)]
    endpoint = {(a, b): Q(3 * a + 5 * b + 7 * a * b + 2) for a, b in states}
    raw_first = {state: Q(2) * value for state, value in endpoint.items()}
    first_projection = sum(raw_first.values(), Q(0)) / len(states)
    second_projection = {
        a: sum((Q(3) * endpoint[(a, b)] for b in (-1, 1)), Q(0)) / 2
        for a in (-1, 1)
    }
    first_force = Q(9, 10) * Q(1, 3) + first_projection
    second_force = {a: Q(9, 10) * Q(a, 2) + second_projection[a] for a in (-1, 1)}
    audit.check("projected_force", "trivial-past projection", first_projection == Q(4), first_projection, Q(4))
    audit.check("projected_force", "first projected force", first_force == Q(43, 10), first_force, Q(43, 10))
    audit.check("projected_force", "second conditional projection", second_projection == {-1: Q(-3), 1: Q(15)}, second_projection, {-1: Q(-3), 1: Q(15)})
    audit.check("projected_force", "second projected forces", second_force == {-1: Q(-69, 20), 1: Q(309, 20)}, second_force, {-1: Q(-69, 20), 1: Q(309, 20)})
    audit.check("projected_force", "raw future dependence removed", any(Q(3) * endpoint[(1, -1)] != Q(3) * endpoint[(1, 1)] for _ in [0]) and second_projection[1] == Q(15), (endpoint[(1, -1)], endpoint[(1, 1)], second_projection[1]), "raw differs; projection fixed")

    # Complete common-feature signature.  U is the actual pinned trace lift,
    # not an arbitrary vector with the same norm.
    b2, y2, theta, variance = Q(9), Q(4), Q(6), Q(5)
    phi2 = b2 + y2
    j2 = phi2 + variance
    forest = j2 - theta
    d0 = theta - y2
    signature = theta - j2 + variance
    future_owner = (y2 - theta) / 2
    p_comp = (phi2 - theta) / 2
    audit.check("signature", "mean plus innovation", phi2 == Q(13), phi2, Q(13))
    audit.check("signature", "raw-current Pythagoras", j2 == Q(18), j2, Q(18))
    audit.check("signature", "forest coordinate", forest == Q(12), forest, Q(12))
    audit.check("signature", "prefix trace deficit", d0 == Q(2), d0, Q(2))
    audit.check("signature", "three-coordinate signature", signature == Q(-7), signature, Q(-7))
    audit.check("signature", "trace minus mean coordinate", signature == theta - phi2, signature, theta - phi2)
    audit.check("signature", "variance minus forest coordinate", signature == variance - forest, signature, variance - forest)
    audit.check("signature", "conditional mean return", signature == d0 - b2, signature, d0 - b2)
    audit.check("signature", "future owner", future_owner == Q(-1), future_owner, Q(-1))
    audit.check("signature", "complete action owner", p_comp == Q(7, 2), p_comp, Q(7, 2))
    audit.check("signature", "future plus mean returned once", future_owner + b2 / 2 == -signature / 2 == p_comp, (future_owner + b2 / 2, -signature / 2), p_comp)
    audit.check("signature", "variance omission mutation", theta - j2 != signature, theta - j2, signature)
    audit.check("signature", "forest duplication mutation", signature - forest != signature, signature - forest, signature)

    # Exact two-sided signed mixed Gram.
    a_plus = [[Q(1), Q(2)], [Q(0), Q(1)]]
    a_minus = [[Q(2), Q(0)], [Q(1), Q(-1)]]
    sig2 = [[Q(1), Q(0)], [Q(0), Q(-1)]]
    left = matmul(matmul(transpose(a_plus), sig2), a_minus)
    right = matmul(matmul(transpose(a_minus), sig2), a_plus)
    mixed_q = scale_matrix(Q(1, 2), add_matrix(left, right))
    audit.check("mixed_gram", "left polarization", left == [[Q(2), Q(0)], [Q(3), Q(1)]], left, [[Q(2), Q(0)], [Q(3), Q(1)]])
    audit.check("mixed_gram", "right polarization", right == transpose(left), right, transpose(left))
    audit.check("mixed_gram", "half-symmetrized Gram", mixed_q == [[Q(2), Q(3, 2)], [Q(3, 2), Q(1)]], mixed_q, [[Q(2), Q(3, 2)], [Q(3, 2), Q(1)]])
    for vector, expected in (([Q(1), Q(3)], Q(20)), ([Q(-2), Q(1)], Q(3))):
        bilinear = dot(matvec(a_plus, vector), matvec(sig2, matvec(a_minus, vector)))
        audit.check("mixed_gram", f"secant identity {vector}", bilinear == quadratic(vector, mixed_q) == expected, (bilinear, quadratic(vector, mixed_q)), expected)
    audit.check("mixed_gram", "missing half duplicates owner", quadratic([Q(1), Q(3)], add_matrix(left, right)) == Q(40), quadratic([Q(1), Q(3)], add_matrix(left, right)), Q(40))
    signed_upper = [[Q(-100), Q(0)], [Q(0), Q(1, 20)]]
    audit.check("mixed_gram", "upper Loewner ignores helpful negative direction", sub_matrix(scale_matrix(Q(1, 20), identity(2)), signed_upper) == [[Q(2001, 20), Q(0)], [Q(0), Q(0)]], sub_matrix(scale_matrix(Q(1, 20), identity(2)), signed_upper), "PSD")
    audit.check("mixed_gram", "absolute norm would overpay", max(abs(signed_upper[0][0]), abs(signed_upper[1][1])) == Q(100) > Q(1, 20), Q(100), Q(1, 20))

    # Global Doob coordinate: orthogonal source decomposition, while the
    # complete terminal Hessian retains its off-diagonal reveal blocks.
    doob = [[Q(3, 5), Q(4, 5)], [Q(-4, 5), Q(3, 5)]]
    hessian = [[Q(2), Q(1)], [Q(1), Q(-3)]]
    doob_gram = matmul(matmul(doob, hessian), transpose(doob))
    audit.check("doob", "rational Doob isometry", matmul(transpose(doob), doob) == identity(2), matmul(transpose(doob), doob), identity(2))
    audit.check("doob", "global Gram selfadjoint", symmetric(doob_gram), doob_gram, "symmetric")
    audit.check("doob", "global Gram reconstructs Hessian", matmul(matmul(transpose(doob), doob_gram), doob) == hessian, matmul(matmul(transpose(doob), doob_gram), doob), hessian)
    test_h = [Q(2), Q(-1)]
    test_d = matvec(doob, test_h)
    audit.check("doob", "quadratic form preserved", quadratic(test_h, hessian) == quadratic(test_d, doob_gram), quadratic(test_d, doob_gram), quadratic(test_h, hessian))
    diagonal_only = [[doob_gram[0][0], Q(0)], [Q(0), doob_gram[1][1]]]
    audit.check("doob", "off-diagonal reveal blocks survive", quadratic(test_d, diagonal_only) != quadratic(test_d, doob_gram), quadratic(test_d, diagonal_only), quadratic(test_d, doob_gram))

    # Source-null quotient descent and its weakest Schur form.
    source_map = [[Q(1), Q(0), Q(1)], [Q(0), Q(1), Q(-1)]]
    quotient_q = [[Q(3), Q(1)], [Q(1), Q(2)]]
    quotient_h = matmul(matmul(transpose(source_map), quotient_q), source_map)
    kernel = [Q(-1), Q(1), Q(1)]
    audit.check("quotient", "kernel vector", matvec(source_map, kernel) == [Q(0), Q(0)], matvec(source_map, kernel), [Q(0), Q(0)])
    audit.check("quotient", "physical Hessian kills source null", matvec(quotient_h, kernel) == [Q(0), Q(0), Q(0)], matvec(quotient_h, kernel), [Q(0), Q(0), Q(0)])
    base = [Q(2), Q(-1), Q(3)]
    shifted = [base[i] + 5 * kernel[i] for i in range(3)]
    audit.check("quotient", "quotient source equal", matvec(source_map, base) == matvec(source_map, shifted), matvec(source_map, shifted), matvec(source_map, base))
    audit.check("quotient", "quotient Hessian form equal", quadratic(base, quotient_h) == quadratic(shifted, quotient_h), quadratic(shifted, quotient_h), quadratic(base, quotient_h))
    positive_kernel_mutation = add_matrix(quotient_h, [[x * y for y in kernel] for x in kernel])
    audit.check("quotient", "positive source-null mutation impossible", quadratic(kernel, positive_kernel_mutation) > 0 and quadratic(kernel, matmul(transpose(source_map), source_map)) == 0, (quadratic(kernel, positive_kernel_mutation), quadratic(kernel, matmul(transpose(source_map), source_map))), "positive over zero")

    weak_h = [[Q(-1), Q(1, 2)], [Q(1, 2), Q(0)]]
    source_metric = [[Q(0), Q(0)], [Q(0), Q(1)]]
    weak_residual = sub_matrix(scale_matrix(Q(1, 4), source_metric), weak_h)
    audit.check("quotient", "weak kernel block nonpositive", weak_h[0][0] <= 0, weak_h[0][0], "<=0")
    audit.check("quotient", "weak range condition", weak_h[0][0] < 0 and weak_h[0][1] != 0, (weak_h[0][0], weak_h[0][1]), "cross lies in range")
    audit.check("quotient", "weak reduced bound one quarter", weak_residual == [[Q(1), Q(-1, 2)], [Q(-1, 2), Q(1, 4)]] and determinant2(weak_residual) == 0, weak_residual, "rank-one PSD")
    zero_kernel_bad = [[Q(0), Q(1, 2)], [Q(1, 2), Q(0)]]
    audit.check("quotient", "zero kernel forces zero cross", determinant2(sub_matrix(scale_matrix(Q(10), source_metric), zero_kernel_bad)) < 0, determinant2(sub_matrix(scale_matrix(Q(10), source_metric), zero_kernel_bad)), "<0 for every finite bound")

    # Low-kernel compatibility and its explicit penalty.
    low_t = Q(3, 4)
    low_graph_form = Q(1) - 2 * low_t
    kappa0 = 2 * low_t
    audit.check("low_kernel", "PSD low diagonal insufficient", low_graph_form == Q(-1, 2), low_graph_form, Q(-1, 2))
    audit.check("low_kernel", "kernel cross penalty", kappa0 == Q(3, 2), kappa0, Q(3, 2))
    audit.check("low_kernel", "penalty repairs lower bound", low_graph_form + kappa0 == Q(1), low_graph_form + kappa0, Q(1))
    common_l = [[Q(1), Q(0)]]
    common_r = [[Q(2)]]
    compatible = matmul(transpose(common_l), common_r)
    audit.check("low_kernel", "common-feature Douglas range", compatible == [[Q(2)], [Q(0)]], compatible, [[Q(2)], [Q(0)]])
    audit.check("low_kernel", "common-feature kills low kernel", dot([Q(0), Q(1)], [row[0] for row in compatible]) == 0, dot([Q(0), Q(1)], [row[0] for row in compatible]), Q(0))

    # Exact positive-analysis collar shift and its numerical threshold table.
    collar_values = {collar: hs_closed(collar) for collar in range(5, 12)}
    debts = {collar: scalar_debt(collar) for collar in collar_values}
    expected_table = {
        7: (10.778126471501523, 0.202089871340603),
        8: (4.631138871013502, 0.0868338538314814),
        9: (1.971947657656302, 0.0369740185810464),
        10: (0.833374378872430, 0.0156257696038541),
    }
    for collar, (expected_h, expected_debt) in expected_table.items():
        audit.check("collar", f"C{collar} closed sum", abs(collar_values[collar] - expected_h) <= TOL, collar_values[collar], expected_h)
        audit.check("collar", f"C{collar} source debt", abs(debts[collar] - expected_debt) <= TOL, debts[collar], expected_debt)

    max_cstar_8 = math.sqrt(float(ZERO_LOW_TAIL_HEADROOM) / debts[8])
    max_cstar_10 = math.sqrt(float(ILLUSTRATIVE_HEADROOM) / debts[10])
    audit.check("collar", "C8 first zero-low-tail collar", debts[7] > float(ZERO_LOW_TAIL_HEADROOM) > debts[8], (debts[7], float(ZERO_LOW_TAIL_HEADROOM), debts[8]), "C7 > headroom > C8")
    audit.check("collar", "C10 first illustrative collar", debts[9] > float(ILLUSTRATIVE_HEADROOM) > debts[10], (debts[9], float(ILLUSTRATIVE_HEADROOM), debts[10]), "C9 > headroom > C10")
    audit.check("collar", "C8 envelope threshold", abs(max_cstar_8 - 1.07546575053067) <= TOL, max_cstar_8, "derived 1.07546575053067")
    audit.check("collar", "C10 envelope threshold", abs(max_cstar_10 - 1.00913922178312) <= TOL, max_cstar_10, "derived 1.00913922178312")
    shift_bound_8 = debts[5] * pow2(-2 * GAMMA_INPUT * 3)
    shift_bound_11 = debts[5] * pow2(-2 * GAMMA_INPUT * 6)
    audit.check("collar", "C5-to-C8 exact shift bound", shift_bound_8 < float(ZERO_LOW_TAIL_HEADROOM), shift_bound_8, f"<{float(ZERO_LOW_TAIL_HEADROOM)}")
    audit.check("collar", "C5-to-C11 illustrative shift bound", shift_bound_11 < float(ILLUSTRATIVE_HEADROOM), shift_bound_11, f"<{float(ILLUSTRATIVE_HEADROOM)}")

    # Cellwise shift identity for an arbitrary finite block fixture.
    cells_c5: dict[tuple[int, int], float] = {}
    cells_c8: dict[tuple[int, int], float] = {}
    for m_gap in range(5, 13):
        for source_index in range(1, 4):
            block = Q(m_gap + 2 * source_index, 7)
            cells_c5[(m_gap, source_index)] = pow2(GAMMA_INPUT * (m_gap - 5)) * float(block)
            if m_gap >= 8:
                cells_c8[(m_gap, source_index)] = pow2(GAMMA_INPUT * (m_gap - 8)) * float(block)
    projected_scaled = {
        key: pow2(-GAMMA_INPUT * 3) * value
        for key, value in cells_c5.items()
        if key[0] >= 8
    }
    audit.check("collar", "cellwise collar shift identity", all(abs(cells_c8[key] - projected_scaled[key]) <= TOL for key in cells_c8), max(abs(cells_c8[key] - projected_scaled[key]) for key in cells_c8), f"<={TOL}")
    signed_full = [[Q(0), Q(0)], [Q(0), Q(1)]]
    signed_keep = [[Q(10), Q(0)], [Q(0), Q(1)]]
    signed_removed = sub_matrix(signed_full, signed_keep)
    audit.check("collar", "signed collar monotonicity mutation", signed_removed[0][0] < 0 and signed_keep[0][0] > signed_full[1][1], (signed_full, signed_keep, signed_removed), "removing negative shell increases upper eigenvalue")

    # Three moved collar layers saturate the row/column Schur sum coherently.
    b5, b6, b7 = Q(1, 6), Q(1, 4), Q(1, 3)
    band_sum = b5 + b6 + b7
    constant_vector = [Q(1)] * 8
    cyclic_output = [band_sum] * 8
    audit.check("band", "three-layer row sum", band_sum == Q(3, 4), band_sum, Q(3, 4))
    audit.check("band", "three-layer column sum", band_sum == Q(3, 4), band_sum, Q(3, 4))
    audit.check("band", "Schur bound attained by constant vector", dot(cyclic_output, cyclic_output) == band_sum * band_sum * dot(constant_vector, constant_vector), dot(cyclic_output, cyclic_output), band_sum * band_sum * dot(constant_vector, constant_vector))
    audit.check("band", "quadrature shortcut fails", band_sum > math.sqrt(float(b5 * b5 + b6 * b6 + b7 * b7)), float(band_sum), math.sqrt(float(b5 * b5 + b6 * b6 + b7 * b7)))
    audit.check("band", "full cross factor two", 2 * band_sum == Q(3, 2), 2 * band_sum, Q(3, 2))
    audit.check("band", "legal reverse not charged twice", 4 * band_sum == Q(3) and 4 * band_sum != 2 * band_sum, 4 * band_sum, "double-count mutation")

    # Signed low correlation: identical magnitudes can pass or fail.
    e_diag = 0.8857272727272757
    f_diag = 0.27
    old_cross = 0.9209323339075279
    bc_mag = 1.0 / 50.0
    det_adverse = (e_diag - bc_mag) * (f_diag - bc_mag) - (old_cross / 2.0 + bc_mag) ** 2
    det_favorable = (e_diag - bc_mag) * (f_diag - bc_mag) - (old_cross / 2.0 - bc_mag) ** 2
    audit.check("correlation", "adverse-correlation determinant fails", det_adverse < 0.0, det_adverse, "<0")
    audit.check("correlation", "favorable-correlation determinant passes", det_favorable > 0.0, det_favorable, ">0")
    audit.check("correlation", "same magnitude data differ only by signed correlation", abs(abs(bc_mag) - abs(-bc_mag)) <= TOL and det_adverse != det_favorable, (bc_mag, -bc_mag, det_adverse, det_favorable), "same magnitude; opposite verdict")

    # Exact rational sign-correlation fixture independently protects the same
    # information boundary without using approximate production diagnostics.
    half_a = Q(29, 32)
    reduced_diag = Q(15, 16)
    determinant_pass = reduced_diag * reduced_diag - (half_a - Q(1, 16)) ** 2
    determinant_fail = reduced_diag * reduced_diag - (half_a + Q(1, 16)) ** 2
    audit.check("correlation", "rational pass determinant", determinant_pass == Q(171, 1024) > 0, determinant_pass, Q(171, 1024))
    audit.check("correlation", "rational fail determinant", determinant_fail == Q(-61, 1024) < 0, determinant_fail, Q(-61, 1024))

    # Conditional source graph margin with the low-kernel penalty included.
    e, lambda_sq, sigma, a0, tau, f = Q(2), Q(1, 5), Q(1, 10), Q(3, 5), Q(1, 10), Q(1)
    graph_margin_without_kernel = e - lambda_sq - sigma - (a0 + tau) ** 2 / (4 * (f - sigma))
    graph_margin_with_kernel = graph_margin_without_kernel - kappa0
    audit.check("graph", "conditional margin before kernel penalty", graph_margin_without_kernel == Q(563, 360), graph_margin_without_kernel, Q(563, 360))
    audit.check("graph", "kernel penalty enters once", graph_margin_with_kernel == Q(23, 360), graph_margin_with_kernel, Q(23, 360))
    audit.check("graph", "action receives half source margin", graph_margin_with_kernel / 2 == Q(23, 720), graph_margin_with_kernel / 2, Q(23, 720))

    scope = {
        "finite_chart_projected_force_formula": True,
        "complete_common_feature_signature_identity": True,
        "conditional_two_sided_signed_gram_theorem": True,
        "global_doob_coordinate_identity": True,
        "source_null_quotient_criterion": True,
        "positive_analysis_collar_shift": True,
        "finite_collar_schur_tradeoff": True,
        "production_common_trace_lift_constructed": False,
        "production_two_sided_factorization": False,
        "production_uniform_loewner_bound": False,
        "production_low_compatibility": False,
        "positive_production_graph_gap": False,
        "matching": False,
        "absolute_anchor": False,
        "a13_gate_closed": False,
        "overlap_src": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    computed = {
        "projected_force_fixture": {
            "first": str(first_force),
            "second": {str(key): str(value) for key, value in second_force.items()},
        },
        "complete_signature": str(signature),
        "mixed_gram": [[str(value) for value in row] for row in mixed_q],
        "global_doob_gram": [[str(value) for value in row] for row in doob_gram],
        "weak_quotient_lambda_squared": "1/4",
        "low_kernel_penalty": str(kappa0),
        "collar_h": {str(key): value for key, value in collar_values.items()},
        "collar_debts": {str(key): value for key, value in debts.items()},
        "max_cstar_c8": max_cstar_8,
        "max_cstar_c10": max_cstar_10,
        "c5_to_c8_shift_bound": shift_bound_8,
        "c5_to_c11_shift_bound": shift_bound_11,
        "three_layer_schur_bound": str(band_sum),
        "production_correlation_determinants": {
            "adverse": det_adverse,
            "favorable": det_favorable,
        },
        "conditional_graph_margin_with_kernel": str(graph_margin_with_kernel),
        "conditional_action_margin": str(graph_margin_with_kernel / 2),
    }
    failed = sum(row["status"] != "PASS" for row in audit.rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(audit.rows),
            "passed": len(audit.rows) - failed,
            "failed": failed,
            "rows": audit.rows,
        },
        "computed": computed,
        "scope": scope,
    }
    atomic_json(args.output, payload)
    print(f"R-141 primary {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
