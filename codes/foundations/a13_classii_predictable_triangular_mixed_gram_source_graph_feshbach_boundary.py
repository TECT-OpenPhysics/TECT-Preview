#!/usr/bin/env python3
"""Primary exact certificate for the scoped A13 R-140 checkpoint.

This certificate checks the predictable triangular two-parameter majorant,
one-use martingale accounting, stopping-compatible endpoint telescoping, and
the source-graph Feshbach identities used by the R-140 conditional route.  It
does not assert the missing production mixed-Gram estimate, a positive
production graph margin, either A13 gate, Nelson, or Sector A.
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
from typing import Callable


RESULT_ID = (
    "A13-CLASSII-PREDICTABLE-TRIANGULAR-MIXED-GRAM-"
    "SOURCE-GRAPH-FESHBACH-BOUNDARY"
)
SCHEMA = (
    "tect/a13-predictable-triangular-mixed-gram-source-graph-"
    "feshbach-boundary-primary/1.0"
)
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-predictable-triangular-mixed-gram-"
    "source-graph-feshbach-boundary/result.json"
)
Q = Fraction

# Declared inputs and tooling tolerances.  Every reported numerical constant
# below is computed from these exact rational values.
P_INPUT = Q(4_000_000_000_001, 1_000_000_000_000)
ALPHA_INPUT = Q(2, 5)
BETA_INPUT = 6 * ALPHA_INPUT - 1
S_INPUT = Q(2, 3)
GAMMA_INPUT = Q(7, 12)
BASE_COLLAR = 5
# This is already the normalized squared/energy coefficient multiplying the
# triangular Hilbert--Schmidt sum H_C.  It is not an amplitude to be squared.
RESPONSE_ENERGY_COEFFICIENT = Q(3, 40) / P_INPUT
TEST_ORACLE_TAIL_TAU = Q(1, 50)  # TEST_ORACLE: illustrative 0.02 tail only.
NUMERIC_TOLERANCE = 1.0e-12
TRUNCATION_TOLERANCE = 1.0e-7


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


def pow2(exponent: Fraction) -> float:
    """Return 2**exponent with the exponent derived exactly as a Fraction."""

    return math.pow(2.0, float(exponent))


def triangular_entry_squared(collar: int, a_gap: int, d_gap: int) -> float:
    """Squared production-exponent scalar majorant for one triangular cell."""

    if collar < BASE_COLLAR or a_gap < 1 or d_gap < 0:
        raise ValueError("invalid triangular index")
    delta = collar - BASE_COLLAR
    exponent = 2 * GAMMA_INPUT * d_gap - BETA_INPUT * a_gap
    if d_gap >= a_gap - delta:
        exponent -= 2 * S_INPUT * (d_gap - a_gap + delta)
    return pow2(exponent)


def hs_closed_components(collar: int) -> dict[str, float]:
    """Closed geometric decomposition of the infinite HS-square majorant."""

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

    far_low_sum = math.fsum(
        pow2(-(BETA_INPUT - 2 * S_INPUT) * a_gap)
        for a_gap in range(1, delta + 1)
    )
    far_low = (
        pow2(-2 * S_INPUT * delta)
        * far_low_sum
        / (1.0 - rho_ratio)
    )
    far_high = (
        pow2(-2 * GAMMA_INPUT * delta)
        * pow(u_ratio, delta + 1)
        / ((1.0 - rho_ratio) * (1.0 - u_ratio))
    )
    return {
        "near": near,
        "far_low": far_low,
        "far_high": far_high,
        "total": near + far_low + far_high,
        "q_ratio": q_ratio,
        "u_ratio": u_ratio,
        "v_ratio": v_ratio,
        "rho_ratio": rho_ratio,
    }


def hs_collar_five_special() -> float:
    """Independent closed form obtained by splitting d<a and d>=a."""

    q_ratio = pow2(2 * GAMMA_INPUT)
    u_ratio = pow2(-(BETA_INPUT - 2 * GAMMA_INPUT))
    v_ratio = pow2(-BETA_INPUT)
    rho_ratio = pow2(-2 * (S_INPUT - GAMMA_INPUT))
    near = (
        u_ratio / (1.0 - u_ratio) - v_ratio / (1.0 - v_ratio)
    ) / (q_ratio - 1.0)
    far = u_ratio / ((1.0 - u_ratio) * (1.0 - rho_ratio))
    return near + far


def hs_finite_truncation(collar: int, cutoff: int) -> float:
    if cutoff < 1:
        raise ValueError("cutoff must be positive")
    return math.fsum(
        triangular_entry_squared(collar, a_gap, d_gap)
        for a_gap in range(1, cutoff + 1)
        for d_gap in range(cutoff + 1)
    )


Vector = list[Fraction]
Matrix = list[list[Fraction]]


def dot(left: Vector, right: Vector) -> Fraction:
    return sum((x * y for x, y in zip(left, right)), Q(0))


def norm_squared(vector: Vector) -> Fraction:
    return dot(vector, vector)


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [dot(row, vector) for row in matrix]


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def quadratic(vector: Vector, matrix: Matrix) -> Fraction:
    return dot(vector, matvec(matrix, vector))


def vector_sub(left: Vector, right: Vector) -> Vector:
    return [x - y for x, y in zip(left, right)]


def det2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


State = tuple[int, int, int]


def cube_values(function: Callable[[int, int, int], Fraction]) -> dict[State, Fraction]:
    return {
        state: function(*state)
        for state in product((-1, 1), repeat=3)
    }


def expectation(values: dict[State, Fraction]) -> Fraction:
    return sum(values.values(), Q(0)) / len(values)


def conditional_expectation(
    values: dict[State, Fraction], reveal_count: int
) -> dict[State, Fraction]:
    if not 0 <= reveal_count <= 3:
        raise ValueError("reveal_count must lie between zero and three")
    grouped: dict[tuple[int, ...], list[Fraction]] = {}
    for state, value in values.items():
        grouped.setdefault(state[:reveal_count], []).append(value)
    means = {
        prefix: sum(group, Q(0)) / len(group)
        for prefix, group in grouped.items()
    }
    return {state: means[state[:reveal_count]] for state in values}


def martingale_difference(
    values: dict[State, Fraction], reveal_count: int
) -> dict[State, Fraction]:
    present = conditional_expectation(values, reveal_count)
    previous = conditional_expectation(values, reveal_count - 1)
    return {state: present[state] - previous[state] for state in values}


def energy(values: dict[State, Fraction]) -> Fraction:
    return expectation({state: value * value for state, value in values.items()})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # The two strict margins are the whole point of the triangular envelope.
    causal_margin = BETA_INPUT / 2 - GAMMA_INPUT
    output_margin = S_INPUT - GAMMA_INPUT
    audit.check("hs", "beta derived from alpha", BETA_INPUT == Q(7, 5), BETA_INPUT, Q(7, 5))
    audit.check("hs", "causal Schur margin", causal_margin == Q(7, 60), causal_margin, Q(7, 60))
    audit.check("hs", "output Schur margin", output_margin == Q(1, 12), output_margin, Q(1, 12))
    audit.check("hs", "both Schur margins strict", causal_margin > 0 and output_margin > 0, (causal_margin, output_margin), "positive")

    hs5_components = hs_closed_components(5)
    hs6_components = hs_closed_components(6)
    hs5 = hs5_components["total"]
    hs6 = hs6_components["total"]
    hs5_special = hs_collar_five_special()
    audit.check("hs", "C5 general and special closed forms agree", abs(hs5 - hs5_special) <= NUMERIC_TOLERANCE, hs5 - hs5_special, f"<={NUMERIC_TOLERANCE}")
    audit.check("hs", "C5 closed form positive", hs5 > 0.0, hs5, ">0")
    audit.check("hs", "C6 closed form positive", hs6 > 0.0, hs6, ">0")
    audit.check("hs", "collar six improves raw HS square", hs6 < hs5, (hs6, hs5), "C6<C5")
    audit.check("hs", "C5 near/far decomposition", abs(hs5 - (hs5_components["near"] + hs5_components["far_low"] + hs5_components["far_high"])) <= NUMERIC_TOLERANCE, hs5, "near+far_low+far_high")
    audit.check("hs", "C6 near/far decomposition", abs(hs6 - (hs6_components["near"] + hs6_components["far_low"] + hs6_components["far_high"])) <= NUMERIC_TOLERANCE, hs6, "near+far_low+far_high")

    truncation_cutoffs = (12, 24, 48, 96, 192)
    hs5_truncations = [hs_finite_truncation(5, cutoff) for cutoff in truncation_cutoffs]
    hs6_truncations = [hs_finite_truncation(6, cutoff) for cutoff in truncation_cutoffs]
    audit.check("hs", "C5 finite truncations monotone", all(left < right for left, right in zip(hs5_truncations, hs5_truncations[1:])), hs5_truncations, "strictly increasing")
    audit.check("hs", "C6 finite truncations monotone", all(left < right for left, right in zip(hs6_truncations, hs6_truncations[1:])), hs6_truncations, "strictly increasing")
    audit.check("hs", "C5 finite truncations stay below closed form", all(value < hs5 for value in hs5_truncations), hs5 - hs5_truncations[-1], ">0")
    audit.check("hs", "C6 finite truncations stay below closed form", all(value < hs6 for value in hs6_truncations), hs6 - hs6_truncations[-1], ">0")
    audit.check("hs", "C5 truncation converges to closed form", abs(hs5 - hs5_truncations[-1]) <= TRUNCATION_TOLERANCE, hs5 - hs5_truncations[-1], f"<={TRUNCATION_TOLERANCE}")
    audit.check("hs", "C6 truncation converges to closed form", abs(hs6 - hs6_truncations[-1]) <= TRUNCATION_TOLERANCE, hs6 - hs6_truncations[-1], f"<={TRUNCATION_TOLERANCE}")

    # Exact finite martingale fixture.  Each h_k is F_(k-1)-measurable.
    h2 = cube_values(lambda e1, _e2, _e3: Q(2 + e1))
    h3 = cube_values(lambda e1, e2, _e3: Q(1 + 2 * e1 + 3 * e2))
    h4 = cube_values(lambda e1, e2, e3: Q(3 + e1 + e1 * e2 + 2 * e3))
    controls = {2: h2, 3: h3, 4: h4}
    innovation_energies: dict[int, Fraction] = {}
    variances: dict[int, Fraction] = {}
    for control_index, values in controls.items():
        innovation_energies[control_index] = sum(
            (energy(martingale_difference(values, reveal)) for reveal in range(1, control_index)),
            Q(0),
        )
        mean_values = conditional_expectation(values, 0)
        centered = {state: values[state] - mean_values[state] for state in values}
        variances[control_index] = energy(centered)
        audit.check("martingale", f"h{control_index} Doob Pythagoras", innovation_energies[control_index] == variances[control_index], innovation_energies[control_index], variances[control_index])
    expected_variances = {2: Q(1), 3: Q(13), 4: Q(6)}
    audit.check("martingale", "fixture variances", variances == expected_variances, variances, expected_variances)
    total_innovation = sum(innovation_energies.values(), Q(0))
    total_source_l2 = sum((energy(values) for values in controls.values()), Q(0))
    audit.check("martingale", "one-use innovation total", total_innovation == Q(20), total_innovation, Q(20))
    audit.check("martingale", "source L2 total", total_source_l2 == Q(34), total_source_l2, Q(34))
    audit.check("martingale", "one-use source domination", total_innovation <= total_source_l2, total_innovation, f"<={total_source_l2}")
    contraction = Q(1, 2)
    output_energy = contraction * contraction * total_innovation
    audit.check("martingale", "contracted direct-sum response", output_energy == Q(5), output_energy, Q(5))

    # A reveal-predictable survival mask is constant across insertion endpoints,
    # hence it preserves the complete signed endpoint telescope.
    k0 = cube_values(lambda e1, _e2, _e3: Q(e1))
    k1 = cube_values(lambda e1, _e2, _e3: Q(1 + 2 * e1))
    k2 = cube_values(lambda e1, _e2, _e3: Q(3 - e1))
    k3 = cube_values(lambda e1, _e2, _e3: Q(4 + 2 * e1))
    sigma = cube_values(lambda e1, _e2, _e3: Q(1 + e1, 2))
    stopped_owner = expectation(
        {
            state: sigma[state]
            * ((k2[state] - k1[state]) + (k3[state] - k2[state]))
            for state in sigma
        }
    )
    stopped_endpoint = expectation(
        {state: sigma[state] * (k3[state] - k1[state]) for state in sigma}
    )
    complement_endpoint = expectation(
        {state: (1 - sigma[state]) * (k3[state] - k1[state]) for state in sigma}
    )
    audit.check("stopping", "survival mask is nonconstant", set(sigma.values()) == {Q(0), Q(1)}, sorted(set(sigma.values())), [Q(0), Q(1)])
    audit.check("stopping", "predictable stopped owner telescope", stopped_owner == stopped_endpoint, stopped_owner, stopped_endpoint)
    audit.check("stopping", "stopped endpoint exact value", stopped_endpoint == Q(3, 2), stopped_endpoint, Q(3, 2))
    audit.check("stopping", "stopped and complement recover complete endpoint", stopped_endpoint + complement_endpoint == Q(3), stopped_endpoint + complement_endpoint, Q(3))

    # SPD graph-Feshbach identity.
    z_spd = [Q(1), Q(2)]
    m2_spd = [[Q(5), Q(-1)], [Q(-1), Q(4)]]
    d_spd = [Q(4), Q(9)]
    sqrt_d_spd = [Q(2), Q(3)]
    k_spd = [[Q(2), Q(0)], [Q(0), Q(3)]]
    ell_spd = [Q(3), Q(-1)]
    kstar_z_spd = matvec(transpose(k_spd), z_spd)
    w_spd = [value / root for value, root in zip(kstar_z_spd, sqrt_d_spd)]
    delta_spd = vector_sub([root * value for root, value in zip(sqrt_d_spd, ell_spd)], w_spd)
    direct_spd = quadratic(z_spd, m2_spd) - 2 * dot(kstar_z_spd, ell_spd) + sum((d * value * value for d, value in zip(d_spd, ell_spd)), Q(0))
    reduced_spd = quadratic(z_spd, m2_spd) - norm_squared(w_spd) + norm_squared(delta_spd)
    audit.check("feshbach_spd", "M2 fixture form", quadratic(z_spd, m2_spd) == Q(17), quadratic(z_spd, m2_spd), Q(17))
    audit.check("feshbach_spd", "Douglas reduced solution", w_spd == [Q(1), Q(2)], w_spd, [Q(1), Q(2)])
    audit.check("feshbach_spd", "completed low displacement", delta_spd == [Q(5), Q(-5)], delta_spd, [Q(5), Q(-5)])
    audit.check("feshbach_spd", "direct graph form", direct_spd == Q(62), direct_spd, Q(62))
    audit.check("feshbach_spd", "SPD Feshbach identity", direct_spd == reduced_spd, direct_spd, reduced_spd)

    # Semidefinite low block.  The kernel component of K*z produces the exact
    # defect -2<N,P0 ell>; omitting it reverses the sign in this fixture.
    z_sem = [Q(1), Q(1)]
    m2_sem = [[Q(4), Q(0)], [Q(0), Q(3)]]
    d_sem = [Q(4), Q(0)]
    sqrt_d_sem = [Q(2), Q(0)]
    k_sem = [[Q(2), Q(0)], [Q(0), Q(3)]]
    ell_sem = [Q(2), Q(5)]
    kstar_z_sem = matvec(transpose(k_sem), z_sem)
    range_part = [kstar_z_sem[0], Q(0)]
    null_defect = vector_sub(kstar_z_sem, range_part)
    w_sem = [range_part[0] / sqrt_d_sem[0], Q(0)]
    delta_sem = vector_sub([sqrt_d_sem[0] * ell_sem[0], Q(0)], w_sem)
    p0_ell = [Q(0), ell_sem[1]]
    direct_sem = quadratic(z_sem, m2_sem) - 2 * dot(kstar_z_sem, ell_sem) + d_sem[0] * ell_sem[0] * ell_sem[0]
    reduced_without_defect = quadratic(z_sem, m2_sem) - norm_squared(w_sem) + norm_squared(delta_sem)
    kernel_defect = -2 * dot(null_defect, p0_ell)
    reduced_sem = reduced_without_defect + kernel_defect
    audit.check("feshbach_semidefinite", "semidefinite M2 fixture form", quadratic(z_sem, m2_sem) == Q(7), quadratic(z_sem, m2_sem), Q(7))
    audit.check("feshbach_semidefinite", "kernel range defect exposed", null_defect == [Q(0), Q(3)], null_defect, [Q(0), Q(3)])
    audit.check("feshbach_semidefinite", "semidefinite reduced solution", w_sem == [Q(1), Q(0)], w_sem, [Q(1), Q(0)])
    audit.check("feshbach_semidefinite", "semidefinite completed displacement", delta_sem == [Q(3), Q(0)], delta_sem, [Q(3), Q(0)])
    audit.check("feshbach_semidefinite", "kernel defect exact", kernel_defect == Q(-30), kernel_defect, Q(-30))
    audit.check("feshbach_semidefinite", "omitting kernel defect flips fixture sign", reduced_without_defect == Q(15) and direct_sem == Q(-15), (reduced_without_defect, direct_sem), (Q(15), Q(-15)))
    audit.check("feshbach_semidefinite", "semidefinite Feshbach identity", direct_sem == reduced_sem, direct_sem, reduced_sem)

    # A requested source gap shifts only the source diagonal.  Shifting both
    # source and companion diagonals by the same amount is not equivalent.
    source_x, companion_y = Q(2), Q(-1)
    source_form = 4 * source_x * source_x + 9 * companion_y * companion_y - 6 * source_x * companion_y
    source_completed = 3 * source_x * source_x + (3 * companion_y - source_x) ** 2
    source_matrix = [[Q(4), Q(-3)], [Q(-3), Q(9)]]
    source_only_shift = [[source_matrix[0][0] - 3, source_matrix[0][1]], [source_matrix[1][0], source_matrix[1][1]]]
    both_shift = [[source_matrix[0][0] - 3, source_matrix[0][1]], [source_matrix[1][0], source_matrix[1][1] - 3]]
    audit.check("source_shift", "source completion identity", source_form == source_completed == Q(37), (source_form, source_completed), Q(37))
    audit.check("source_shift", "unshifted source graph SPD", det2(source_matrix) > 0, det2(source_matrix), ">0")
    audit.check("source_shift", "source-only shift reaches PSD boundary", det2(source_only_shift) == 0 and source_only_shift[0][0] >= 0 and source_only_shift[1][1] >= 0, det2(source_only_shift), Q(0))
    audit.check("source_shift", "shifting both blocks is indefinite", det2(both_shift) == Q(-3), det2(both_shift), Q(-3))

    # The scalar rank-one tail attains the robust product bound exactly.
    tail_x, tail_y, tail_tau, tail_operator = Q(2), Q(-3), Q(5), Q(-5)
    tail_pairing = tail_x * tail_operator * tail_y
    tail_bound = tail_tau * abs(tail_x) * abs(tail_y)
    audit.check("tail", "tail operator norm", abs(tail_operator) == tail_tau, abs(tail_operator), tail_tau)
    audit.check("tail", "rank-one tail attains product bound", tail_pairing == tail_bound == Q(30), tail_pairing, tail_bound)

    # Exact scalar sharpness after eliminating a low block.
    scalar_d, scalar_k = Q(4), Q(2)
    scalar_sigma = scalar_k * scalar_k / scalar_d
    scalar_e, scalar_f = Q(5), Q(3)
    scalar_a0, scalar_tau = Q(1), Q(1)
    sharp_ratio = (scalar_a0 + scalar_tau) / (2 * (scalar_f - scalar_sigma))
    scalar_mu = scalar_e - scalar_sigma - (scalar_a0 + scalar_tau) ** 2 / (4 * (scalar_f - scalar_sigma))
    sharp_u = Q(2)
    sharp_y = sharp_ratio * sharp_u
    sharp_form = (scalar_e - scalar_sigma) * sharp_u * sharp_u + (scalar_f - scalar_sigma) * sharp_y * sharp_y - (scalar_a0 + scalar_tau) * sharp_u * sharp_y
    scalar_z = [sharp_u, sharp_y]
    scalar_low = [value / 2 for value in scalar_z]
    scalar_w = list(scalar_z)
    scalar_delta = vector_sub([2 * value for value in scalar_low], scalar_w)
    audit.check("scalar", "low Schur cost", scalar_sigma == Q(1), scalar_sigma, Q(1))
    audit.check("scalar", "sharp minimizing ratio", sharp_ratio == Q(1, 2), sharp_ratio, Q(1, 2))
    audit.check("scalar", "sharp source margin", scalar_mu == Q(7, 2), scalar_mu, Q(7, 2))
    audit.check("scalar", "scalar equality attained", sharp_form == scalar_mu * sharp_u * sharp_u, sharp_form, scalar_mu * sharp_u * sharp_u)
    audit.check("scalar", "canonical low choice has zero Feshbach displacement", scalar_delta == [Q(0), Q(0)], scalar_delta, [Q(0), Q(0)])

    # Conditional acceptance diagnostic.  a0 is an old acceptance ceiling and
    # is deliberately not asserted to be a production response bound.
    eta_h = Q(9, 20) - Q(3, 125) / P_INPUT - Q(1, 880)
    zeta_h = Q(27, 200)
    source_e = 2 * eta_h
    sextic_f = 2 * zeta_h
    conditional_a0_squared = 16 * (Q(197, 440) - Q(3, 125) / P_INPUT) * Q(3, 25)
    conditional_a0 = math.sqrt(float(conditional_a0_squared))
    zero_low_tail_lambda_squared = source_e - conditional_a0_squared / (4 * sextic_f)
    zero_low_tail_lambda = math.sqrt(float(zero_low_tail_lambda_squared))
    tail_room = 2.0 * math.sqrt(float(source_e * sextic_f)) - conditional_a0
    discriminant = (source_e - sextic_f) ** 2 + conditional_a0_squared
    sigma_ceiling = (
        float(source_e + sextic_f) - math.sqrt(float(discriminant))
    ) / 2.0
    sigma_root_residual = (
        float(source_e) - sigma_ceiling
    ) * (
        float(sextic_f) - sigma_ceiling
    ) - float(conditional_a0_squared) / 4.0
    test_oracle_sigma = sigma_ceiling / 2.0
    test_oracle_tau = float(TEST_ORACLE_TAIL_TAU)
    test_lambda_squared_ceiling = (
        float(source_e)
        - test_oracle_sigma
        - (conditional_a0 + test_oracle_tau) ** 2
        / (4.0 * (float(sextic_f) - test_oracle_sigma))
    )
    test_lambda_ceiling = math.sqrt(test_lambda_squared_ceiling)

    response_energy_coefficient = float(RESPONSE_ENERGY_COEFFICIENT)
    lambda5_squared = response_energy_coefficient * hs5
    lambda6_squared = response_energy_coefficient * hs6
    hessian_ceiling_gap = test_lambda_squared_ceiling - lambda6_squared
    action_half_debt = lambda6_squared / 2.0
    action_source_margin = float(eta_h) - action_half_debt

    audit.check("ceiling", "conditional headroom positive", zero_low_tail_lambda_squared > 0, zero_low_tail_lambda_squared, ">0")
    audit.check("ceiling", "conditional cross tail room positive", tail_room > 0.0, tail_room, ">0")
    audit.check("ceiling", "sigma ceiling lies in low interval", 0.0 < sigma_ceiling < float(sextic_f), sigma_ceiling, f"in (0,{float(sextic_f)})")
    audit.check("ceiling", "sigma ceiling solves sharp equation", abs(sigma_root_residual) <= NUMERIC_TOLERANCE, sigma_root_residual, f"<={NUMERIC_TOLERANCE}")
    audit.check("ceiling", "TEST_ORACLE tail is exact one fiftieth", TEST_ORACLE_TAIL_TAU == Q(1, 50), TEST_ORACLE_TAIL_TAU, Q(1, 50))
    audit.check("ceiling", "illustrative low-tail Lambda ceiling positive", test_lambda_squared_ceiling > 0.0, test_lambda_squared_ceiling, ">0")
    audit.check("ceiling", "C6 improves the C5 energy debt", lambda6_squared < lambda5_squared, lambda6_squared, f"<{lambda5_squared}")
    audit.check("ceiling", "C5 violates zero-low-tail ceiling", lambda5_squared > float(zero_low_tail_lambda_squared), lambda5_squared, f">{float(zero_low_tail_lambda_squared)}")
    audit.check("ceiling", "C6 violates zero-low-tail ceiling", lambda6_squared > float(zero_low_tail_lambda_squared), lambda6_squared, f">{float(zero_low_tail_lambda_squared)}")
    audit.check("ceiling", "C5 fails stronger illustrative ceiling", lambda5_squared > test_lambda_squared_ceiling, lambda5_squared, f">{test_lambda_squared_ceiling}")
    audit.check("ceiling", "C6 fails stronger illustrative ceiling", lambda6_squared > test_lambda_squared_ceiling, lambda6_squared, f">{test_lambda_squared_ceiling}")
    audit.check("ceiling", "C6 Hessian ceiling gap is negative", hessian_ceiling_gap < 0.0, hessian_ceiling_gap, "<0")
    audit.check("ceiling", "action debt is half Hessian debt", abs(2.0 * action_half_debt - lambda6_squared) <= NUMERIC_TOLERANCE, 2.0 * action_half_debt, lambda6_squared)
    audit.check("ceiling", "action source margin remains positive in diagnostic", action_source_margin > 0.0, action_source_margin, ">0")

    scope = {
        "predictable_triangular_hs_closed_form": True,
        "finite_truncation_convergence": True,
        "one_use_martingale_orthogonality": True,
        "predictable_stopping_telescope": True,
        "spd_graph_feshbach_identity": True,
        "semidefinite_kernel_defect_identity": True,
        "source_only_gap_shift": True,
        "rank_one_tail_attainment": True,
        "conditional_scalar_headroom_diagnostic": True,
        "conditional_a0_is_production_bound": False,
        "test_oracle_tail_is_production_bound": False,
        "production_predictable_mixed_gram_envelope": False,
        "r102_product_covariance_residual_closed": False,
        "production_graph_margin": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    computed = {
        "alpha": str(ALPHA_INPUT),
        "beta": str(BETA_INPUT),
        "s": str(S_INPUT),
        "gamma": str(GAMMA_INPUT),
        "causal_margin": str(causal_margin),
        "output_margin": str(output_margin),
        "hs_c5_components": hs5_components,
        "hs_c6_components": hs6_components,
        "hs_c5_truncations": dict(zip((str(value) for value in truncation_cutoffs), hs5_truncations)),
        "hs_c6_truncations": dict(zip((str(value) for value in truncation_cutoffs), hs6_truncations)),
        "response_energy_coefficient": str(RESPONSE_ENERGY_COEFFICIENT),
        "lambda_c5_squared": lambda5_squared,
        "lambda_c6_squared": lambda6_squared,
        "martingale_variances": {str(key): str(value) for key, value in variances.items()},
        "martingale_total_innovation": str(total_innovation),
        "martingale_total_source_l2": str(total_source_l2),
        "stopped_endpoint": str(stopped_endpoint),
        "spd_feshbach_direct": str(direct_spd),
        "semidefinite_feshbach_direct": str(direct_sem),
        "semidefinite_kernel_defect": str(kernel_defect),
        "source_only_shift_determinant": str(det2(source_only_shift)),
        "both_diagonal_shift_determinant": str(det2(both_shift)),
        "rank_one_tail_pairing": str(tail_pairing),
        "scalar_sharp_margin": str(scalar_mu),
        "P_input": str(P_INPUT),
        "eta_h": str(eta_h),
        "zeta_h": str(zeta_h),
        "source_e": str(source_e),
        "sextic_f": str(sextic_f),
        "conditional_test_input_a0_squared": str(conditional_a0_squared),
        "conditional_test_input_a0": conditional_a0,
        "zero_low_tail_lambda_squared_ceiling": str(zero_low_tail_lambda_squared),
        "zero_low_tail_lambda_ceiling": zero_low_tail_lambda,
        "tail_room": tail_room,
        "sigma_ceiling": sigma_ceiling,
        "test_oracle_sigma": test_oracle_sigma,
        "test_oracle_tail_tau": str(TEST_ORACLE_TAIL_TAU),
        "test_lambda_squared_ceiling": test_lambda_squared_ceiling,
        "test_lambda_ceiling": test_lambda_ceiling,
        "hessian_ceiling_gap_c6": hessian_ceiling_gap,
        "action_half_debt_c6": action_half_debt,
        "action_source_margin_c6": action_source_margin,
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
    print(f"R-140 primary {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
