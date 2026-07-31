#!/usr/bin/env python3
"""Independent standard-library certificate for the A13 R-140 checkpoint.

The verifier deliberately avoids the primary implementation.  It recomputes
the predictable triangular Hilbert--Schmidt sums by direct finite enumeration
and independent geometric series, and it checks the algebraic boundary
fixtures with exact rational arithmetic wherever possible.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
from itertools import product
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Iterable


RESULT_ID = "A13-CLASSII-PREDICTABLE-TRIANGULAR-MIXED-GRAM-SOURCE-GRAPH-FESHBACH-BOUNDARY"
SCHEMA = "tect/a13-predictable-triangular-mixed-gram-source-graph-feshbach-boundary-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-predictable-triangular-mixed-gram-source-graph-feshbach-boundary/"
    "result.json"
)
Q = Fraction
State = tuple[int, int, int]


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
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
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


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


def expectation(values: dict[State, Fraction]) -> Fraction:
    return sum(values.values(), Q(0)) / len(values)


def conditional(values: dict[State, Fraction], revealed: int) -> dict[State, Fraction]:
    grouped: dict[tuple[int, ...], list[Fraction]] = {}
    for state, value in values.items():
        grouped.setdefault(state[:revealed], []).append(value)
    means = {key: sum(group, Q(0)) / len(group) for key, group in grouped.items()}
    return {state: means[state[:revealed]] for state in values}


def dot(left: Iterable[Fraction], right: Iterable[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Q(0))


def matvec(matrix: list[list[Fraction]], vector: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(dot(row, vector) for row in matrix)


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Q(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def finite_triangular_sum(collar: int, cutoff: int) -> tuple[float, float, float]:
    """Enumerate the squared piecewise kernel without using a closed formula."""

    beta = Q(7, 5)
    smoothing = Q(2, 3)
    gamma = Q(7, 12)
    delta = collar - 5
    near_terms: list[float] = []
    far_terms: list[float] = []
    for a in range(1, cutoff + 1):
        for d in range(cutoff + 1):
            exponent = gamma * d - beta * a / 2
            if d >= a - delta:
                exponent -= smoothing * (d - a + delta)
                far_terms.append(2.0 ** (2.0 * float(exponent)))
            else:
                near_terms.append(2.0 ** (2.0 * float(exponent)))
    near = math.fsum(near_terms)
    far = math.fsum(far_terms)
    return near + far, near, far


def geometric_triangular_sum(collar: int) -> tuple[float, float, float]:
    """Sum the two triangular regions as independent geometric series."""

    beta = Q(7, 5)
    smoothing = Q(2, 3)
    gamma = Q(7, 12)
    delta = collar - 5
    if delta not in (0, 1):
        raise ValueError("this independent certificate covers collars 5 and 6")

    vertical_growth = 2.0 ** float(2 * gamma)
    diagonal_decay = 2.0 ** -float(beta - 2 * gamma)
    pure_a_decay = 2.0 ** -float(beta)
    far_decay = 2.0 ** -float(2 * (smoothing - gamma))

    near = (
        vertical_growth ** (-delta) * diagonal_decay ** (delta + 1) / (1.0 - diagonal_decay)
        - pure_a_decay ** (delta + 1) / (1.0 - pure_a_decay)
    ) / (vertical_growth - 1.0)

    far_low = 0.0
    if delta:
        far_low = (
            2.0 ** -float(2 * smoothing * delta)
            * math.fsum(2.0 ** -float((beta - 2 * smoothing) * a) for a in range(1, delta + 1))
            / (1.0 - far_decay)
        )
    far_high = (
        2.0 ** -float(2 * gamma * delta)
        * diagonal_decay ** (delta + 1)
        / ((1.0 - far_decay) * (1.0 - diagonal_decay))
    )
    far = far_low + far_high
    return near + far, near, far


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    beta = Q(7, 5)
    smoothing = Q(2, 3)
    gamma = Q(7, 12)
    audit.check("triangular", "near diagonal exponent margin", beta / 2 - gamma == Q(7, 60), beta / 2 - gamma, Q(7, 60))
    audit.check("triangular", "far diagonal exponent margin", smoothing - gamma == Q(1, 12), smoothing - gamma, Q(1, 12))

    triangular_oracles = {
        5: (56.298154029170405, 4.085653505135112, 52.212500524035285),
        6: (24.806198069571057, 1.5481731756886412, 23.25802489388241),
    }
    triangular: dict[int, dict[str, float]] = {}
    for collar in (5, 6):
        closed, closed_near, closed_far = geometric_triangular_sum(collar)
        finite, finite_near, finite_far = finite_triangular_sum(collar, 400)
        oracle, oracle_near, oracle_far = triangular_oracles[collar]
        audit.check("triangular", f"C{collar} geometric total regression", abs(closed - oracle) < 2.0e-13, closed, oracle)
        audit.check("triangular", f"C{collar} geometric near regression", abs(closed_near - oracle_near) < 2.0e-13, closed_near, oracle_near)
        audit.check("triangular", f"C{collar} geometric far regression", abs(closed_far - oracle_far) < 2.0e-13, closed_far, oracle_far)
        audit.check("triangular", f"C{collar} finite enumeration parity", abs(finite - closed) < 2.0e-11, finite, closed)
        audit.check("triangular", f"C{collar} finite near parity", abs(finite_near - closed_near) < 2.0e-11, finite_near, closed_near)
        audit.check("triangular", f"C{collar} finite far parity", abs(finite_far - closed_far) < 2.0e-11, finite_far, closed_far)
        triangular[collar] = {
            "closed": closed,
            "near": closed_near,
            "far": closed_far,
            "finite_cutoff_400": finite,
            "finite_residual": finite - closed,
            "sqrt": math.sqrt(closed),
        }
    audit.check("triangular", "collar six strictly improves HS square", triangular[6]["closed"] < triangular[5]["closed"], triangular[6]["closed"] / triangular[5]["closed"], "<1")

    # Exact one-use Doob decomposition on a finite Rademacher cube.
    states: tuple[State, ...] = tuple(product((-1, 1), repeat=3))
    controls: dict[int, dict[State, Fraction]] = {
        2: {state: Q(1 + 2 * state[0]) for state in states},
        3: {
            state: Q(-2 + state[0] + 3 * state[1] + 2 * state[0] * state[1])
            for state in states
        },
        4: {
            state: Q(2 * state[0] - state[1] + 4 * state[2] + state[0] * state[2])
            for state in states
        },
    }
    expected_increment_energies = {2: [Q(4)], 3: [Q(1), Q(13)], 4: [Q(4), Q(1), Q(17)]}
    one_use_total = Q(0)
    for insertion, values in controls.items():
        projections = [conditional(values, revealed) for revealed in range(insertion)]
        increments = [
            {state: projections[level][state] - projections[level - 1][state] for state in states}
            for level in range(1, insertion)
        ]
        reconstructed = all(
            sum((increment[state] for increment in increments), Q(0))
            == values[state] - projections[0][state]
            for state in states
        )
        audit.check("one_use", f"h{insertion} pointwise reconstruction", reconstructed, reconstructed, True)
        increment_energies = [expectation({state: increment[state] ** 2 for state in states}) for increment in increments]
        centered_energy = expectation(
            {state: (values[state] - projections[0][state]) ** 2 for state in states}
        )
        audit.check("one_use", f"h{insertion} increment energies", increment_energies == expected_increment_energies[insertion], increment_energies, expected_increment_energies[insertion])
        audit.check("one_use", f"h{insertion} orthogonal energy identity", sum(increment_energies, Q(0)) == centered_energy, sum(increment_energies, Q(0)), centered_energy)
        one_use_total += centered_energy
    audit.check("one_use", "all strict-past innovations used once", one_use_total == Q(40), one_use_total, Q(40))

    # Predictable stopping telescope and its exact L2 identity.
    terminal = {
        state: Q(3 * state[0] - 2 * state[1] + 5 * state[2] + 4 * state[0] * state[1] - state[1] * state[2])
        for state in states
    }
    martingale = [conditional(terminal, revealed) for revealed in range(4)]
    stop = {
        state: 1 if state[0] == 1 else (2 if state[1] == 1 else 3)
        for state in states
    }
    stopped_increments: list[dict[State, Fraction]] = []
    for level in range(1, 4):
        indicator = {state: Q(1 if stop[state] >= level else 0) for state in states}
        predictable = all(
            len({indicator[state] for state in states if state[: level - 1] == prefix}) == 1
            for prefix in {state[: level - 1] for state in states}
        )
        audit.check("stopping", f"level {level} indicator is predictable", predictable, predictable, True)
        stopped_increments.append(
            {
                state: indicator[state] * (martingale[level][state] - martingale[level - 1][state])
                for state in states
            }
        )
    pathwise_stop = all(
        martingale[stop[state]][state] - martingale[0][state]
        == sum((increment[state] for increment in stopped_increments), Q(0))
        for state in states
    )
    audit.check("stopping", "pathwise stopped telescope", pathwise_stop, pathwise_stop, True)
    stopped_energy = expectation(
        {state: (martingale[stop[state]][state] - martingale[0][state]) ** 2 for state in states}
    )
    increment_energy = sum(
        (expectation({state: increment[state] ** 2 for state in states}) for increment in stopped_increments),
        Q(0),
    )
    audit.check("stopping", "optional stopping energy identity", stopped_energy == increment_energy, stopped_energy, increment_energy)
    cross_terms = [
        expectation({state: stopped_increments[i][state] * stopped_increments[j][state] for state in states})
        for i in range(3)
        for j in range(i + 1, 3)
    ]
    audit.check("stopping", "predictable stopped increments remain orthogonal", all(value == 0 for value in cross_terms), cross_terms, [Q(0)] * 3)

    # Exact positive-definite graph-Feshbach completion.
    z = (Q(1), Q(2))
    ell = (Q(3), Q(-1))
    m2 = [[Q(5), Q(-1)], [Q(-1), Q(4)]]
    d_matrix = [[Q(4), Q(0)], [Q(0), Q(9)]]
    k_matrix = [[Q(2), Q(0)], [Q(0), Q(3)]]
    m2_form = dot(z, matvec(m2, z))
    direct_spd = m2_form - 2 * dot(z, matvec(k_matrix, ell)) + dot(ell, matvec(d_matrix, ell))
    w = (Q(1), Q(2))
    d_half_ell = (Q(6), Q(-3))
    delta = tuple(d_half_ell[i] - w[i] for i in range(2))
    reduced_spd = m2_form - dot(w, w) + dot(delta, delta)
    audit.check("feshbach", "SPD direct form value", direct_spd == Q(62), direct_spd, Q(62))
    audit.check("feshbach", "SPD exact completed-square identity", direct_spd == reduced_spd, direct_spd, reduced_spd)
    audit.check("feshbach", "SPD reduced source form", m2_form - dot(w, w) == Q(12), m2_form - dot(w, w), Q(12))

    # A semidefinite low block needs the kernel defect retained explicitly.
    semidefinite_m2 = Q(7)
    kz = (Q(2), Q(3))
    semidefinite_ell = (Q(2), Q(5))
    direct_semidefinite = semidefinite_m2 - 2 * dot(kz, semidefinite_ell) + Q(4) * semidefinite_ell[0] ** 2
    semidefinite_w = (Q(1), Q(0))
    semidefinite_delta = (Q(3), Q(0))
    kernel_defect = (Q(0), Q(3))
    kernel_ell = (Q(0), Q(5))
    completed_semidefinite = (
        semidefinite_m2
        - dot(semidefinite_w, semidefinite_w)
        + dot(semidefinite_delta, semidefinite_delta)
        - 2 * dot(kernel_defect, kernel_ell)
    )
    omitted_kernel_defect = semidefinite_m2 - dot(semidefinite_w, semidefinite_w) + dot(semidefinite_delta, semidefinite_delta)
    audit.check("feshbach", "semidefinite direct form value", direct_semidefinite == Q(-15), direct_semidefinite, Q(-15))
    audit.check("feshbach", "semidefinite exact completion with defect", direct_semidefinite == completed_semidefinite, direct_semidefinite, completed_semidefinite)
    audit.check("feshbach", "kernel defect cannot be omitted", omitted_kernel_defect == Q(15) and omitted_kernel_defect != direct_semidefinite, omitted_kernel_defect, "15 and not the direct form")

    # Mixed-Gram orientation has one owner after symmetrization.
    predictable_projection = [[Q(1), Q(0)], [Q(0), Q(0)]]
    riesz_metric = [[Q(2), Q(1)], [Q(1), Q(3)]]
    mixed = matmul(riesz_metric, predictable_projection)
    gram = matmul(transpose(predictable_projection), mixed)
    forward = matmul(transpose(predictable_projection), mixed)
    reverse = matmul(transpose(mixed), predictable_projection)
    symmetrized = [[(forward[i][j] + reverse[i][j]) / 2 for j in range(2)] for i in range(2)]
    audit.check("mixed_gram", "forward orientation equals restricted Gram", forward == gram, forward, gram)
    audit.check("mixed_gram", "reverse orientation equals restricted Gram", reverse == gram, reverse, gram)
    audit.check("mixed_gram", "half symmetrization has one owner", symmetrized == gram, symmetrized, gram)

    # Source-only gap extraction is valid; an ambient shift is not.
    source_x, source_y = Q(7, 5), Q(-2, 3)
    original_source = 4 * source_x**2 + 9 * source_y**2 - 6 * source_x * source_y
    completed_source = 3 * source_x**2 + (3 * source_y - source_x) ** 2
    audit.check("source_gap", "exact source-only completion", original_source == completed_source == Q(436, 25), original_source, Q(436, 25))
    source_shift_determinant = Q(1) * Q(9) - Q(3) ** 2
    ambient_shift_determinant = Q(1) * Q(6) - Q(3) ** 2
    audit.check("source_gap", "source-only shift is semidefinite", source_shift_determinant == 0, source_shift_determinant, Q(0))
    audit.check("source_gap", "ambient shift is indefinite", ambient_shift_determinant == Q(-3), ambient_shift_determinant, Q(-3))
    ambient_negative_vector = Q(1) * Q(3) ** 2 - 6 * Q(3) * Q(1) + Q(6) * Q(1) ** 2
    audit.check("source_gap", "ambient shift has explicit negative vector", ambient_negative_vector == Q(-3), ambient_negative_vector, Q(-3))

    # Rank-one tails attain the robust product estimate exactly.
    rank_x, rank_y, rank_tau, rank_t = Q(2), Q(-3), Q(5), Q(-5)
    tail_pairing = rank_x * rank_t * rank_y
    product_bound = rank_tau * abs(rank_x) * abs(rank_y)
    audit.check("sharpness", "rank-one tail operator norm", abs(rank_t) == rank_tau, abs(rank_t), rank_tau)
    audit.check("sharpness", "rank-one product bound attained", tail_pairing == product_bound == Q(30), tail_pairing, product_bound)

    sharp_e, sharp_f, sharp_sigma = Q(4), Q(9), Q(0)
    sharp_a0, sharp_tau = Q(4), Q(2)
    sharp_ratio = (sharp_a0 + sharp_tau) / (2 * (sharp_f - sharp_sigma))
    sharp_mu = sharp_e - sharp_sigma - (sharp_a0 + sharp_tau) ** 2 / (4 * (sharp_f - sharp_sigma))
    sharp_value = (
        sharp_e
        - sharp_sigma
        + (sharp_f - sharp_sigma) * sharp_ratio**2
        - (sharp_a0 + sharp_tau) * sharp_ratio
    )
    audit.check("sharpness", "scalar adverse minimizer", sharp_ratio == Q(1, 3), sharp_ratio, Q(1, 3))
    audit.check("sharpness", "scalar lower bound attained", sharp_value == sharp_mu == Q(3), sharp_value, Q(3))

    # Conditional half-debt diagnostics from upstream rational parameters.
    production_p = Q(4000000000001, 10**12)
    eta_h = Q(9, 20) - Q(3) / (Q(125) * production_p) - Q(1, 880)
    zeta_h = Q(27, 200)
    source_e = float(2 * eta_h)
    source_f = float(2 * zeta_h)
    eta0 = Q(197, 440) - Q(3) / (Q(125) * production_p)
    zeta0 = Q(3, 25)
    a0 = 4.0 * math.sqrt(float(eta0 * zeta0))
    mu0 = source_e - a0 * a0 / (4.0 * source_f)
    tail_room = 2.0 * math.sqrt(source_e * source_f) - a0
    sigma_ceiling = (source_e + source_f - math.sqrt((source_e - source_f) ** 2 + a0 * a0)) / 2.0
    sigma_example = sigma_ceiling / 2.0
    tau_example = 0.02
    example_mu = source_e - sigma_example - (a0 + tau_example) ** 2 / (4.0 * (source_f - sigma_example))
    lambda0_threshold = math.sqrt(mu0)
    lambda_example_threshold = math.sqrt(example_mu)
    half_debt_oracles = {
        "source_e": 0.8857272727272757,
        "source_f": 0.27,
        "a0": 0.9209323339075279,
        "mu0": 0.10043434343434376,
        "tail_room": 0.05711953309414486,
        "sigma_ceiling": 0.02396011633137274,
        "lambda0_threshold": 0.316913779180306,
        "example_mu": 0.015912689545308223,
        "lambda_example_threshold": 0.126145509413963,
    }
    half_debt_actual = {
        "source_e": source_e,
        "source_f": source_f,
        "a0": a0,
        "mu0": mu0,
        "tail_room": tail_room,
        "sigma_ceiling": sigma_ceiling,
        "lambda0_threshold": lambda0_threshold,
        "example_mu": example_mu,
        "lambda_example_threshold": lambda_example_threshold,
    }
    for name, oracle in half_debt_oracles.items():
        audit.check("half_debt", f"{name} regression", abs(half_debt_actual[name] - oracle) < 2.0e-12, half_debt_actual[name], oracle)
    audit.check("half_debt", "zero-low-tail scalar margin positive", mu0 > 0.0, mu0, ">0")
    audit.check("half_debt", "example low-tail scalar margin positive", example_mu > 0.0, example_mu, ">0")
    audit.check("half_debt", "zero-low-tail Lambda boundary is sharp", abs(mu0 - lambda0_threshold**2) < 2.0e-16, mu0 - lambda0_threshold**2, 0.0)
    audit.check("half_debt", "example Lambda boundary is sharp", abs(example_mu - lambda_example_threshold**2) < 2.0e-16, example_mu - lambda_example_threshold**2, 0.0)

    # R-138's coefficient already multiplies the squared HS norm.  Squaring it
    # again would undercount the source Hessian debt by an entire factor.
    energy_coefficient = float(Q(3) / (Q(40) * production_p))
    lambda_square = {collar: energy_coefficient * triangular[collar]["closed"] for collar in (5, 6)}
    lambda_value = {collar: math.sqrt(lambda_square[collar]) for collar in (5, 6)}
    action_half_debt = {collar: lambda_square[collar] / 2.0 for collar in (5, 6)}
    audit.check("half_debt", "C5 action half-debt normalization", abs(action_half_debt[5] - 0.5277951940233406) < 2.0e-12, action_half_debt[5], 0.5277951940233406)
    audit.check("half_debt", "C6 action half-debt normalization", abs(action_half_debt[6] - 0.23255810690217052) < 2.0e-12, action_half_debt[6], 0.23255810690217052)
    audit.check("half_debt", "source Hessian debt is twice action debt", all(lambda_square[c] == 2.0 * action_half_debt[c] for c in (5, 6)), lambda_square, "twice each action half-debt")
    mistaken_squared_coefficient = {collar: energy_coefficient**2 * triangular[collar]["closed"] for collar in (5, 6)}
    audit.check("half_debt", "coefficient-squared undercount rejected", all(lambda_square[c] > mistaken_squared_coefficient[c] for c in (5, 6)), mistaken_squared_coefficient, "strictly below the correctly normalized debts")
    audit.check("half_debt", "C6 improves but exceeds zero-low-tail threshold", lambda_value[5] > lambda_value[6] > lambda0_threshold, lambda_value, f">{lambda0_threshold}")
    audit.check("half_debt", "both collars exceed example threshold", all(lambda_value[c] > lambda_example_threshold for c in (5, 6)), lambda_value, f">{lambda_example_threshold}")
    zero_tail_residual = {collar: mu0 - lambda_square[collar] for collar in (5, 6)}
    example_residual = {collar: example_mu - lambda_square[collar] for collar in (5, 6)}
    audit.check("half_debt", "triangular bound alone does not close zero-low-tail gate", all(value < 0.0 for value in zero_tail_residual.values()), zero_tail_residual, "both negative")
    audit.check("half_debt", "triangular bound alone does not close example gate", all(value < 0.0 for value in example_residual.values()), example_residual, "both negative")

    scope = {
        "predictable_triangular_hs_sum": True,
        "one_use_doob_decomposition": True,
        "stopping_telescope": True,
        "source_metric_graph_feshbach": True,
        "semidefinite_kernel_defect_retained": True,
        "conditional_half_debt_acceptance": True,
        "production_mixed_gram_bound": False,
        "production_low_tail_constants": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    computed = {
        "triangular": {str(collar): values for collar, values in triangular.items()},
        "triangular_ratio_C6_over_C5": triangular[6]["closed"] / triangular[5]["closed"],
        "one_use_total_centered_energy": str(one_use_total),
        "stopped_energy": str(stopped_energy),
        "stopped_increment_energy": str(increment_energy),
        "spd_direct": str(direct_spd),
        "spd_reduced": str(reduced_spd),
        "semidefinite_direct": str(direct_semidefinite),
        "semidefinite_completed": str(completed_semidefinite),
        "semidefinite_without_kernel_defect": str(omitted_kernel_defect),
        "source_shift_determinant": str(source_shift_determinant),
        "invalid_ambient_shift_determinant": str(ambient_shift_determinant),
        "rank_one_tail_attainment": str(tail_pairing),
        "scalar_sharp_mu": str(sharp_mu),
        "conditional_parameters": half_debt_actual,
        "energy_coefficient_3_over_40P": energy_coefficient,
        "lambda_square": {str(collar): value for collar, value in lambda_square.items()},
        "lambda": {str(collar): value for collar, value in lambda_value.items()},
        "action_half_debt": {str(collar): value for collar, value in action_half_debt.items()},
        "zero_low_tail_residual_after_source_debt": {str(collar): value for collar, value in zero_tail_residual.items()},
        "example_residual_after_source_debt": {str(collar): value for collar, value in example_residual.items()},
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
        "limitations": [
            "a0=K0 is a conditional acceptance ceiling, not a proved production mixed-Gram norm bound.",
            "The triangular Hilbert--Schmidt estimate is an upper bound and, with the correct energy normalization, does not close the A13 source-budget gate.",
            "No Nelson estimate or Sector-A closure is asserted.",
        ],
    }
    atomic_json(args.output, payload)
    print(f"R-140 independent {payload['status']}: {len(audit.rows) - failed}/{len(audit.rows)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
