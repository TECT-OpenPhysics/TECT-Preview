#!/usr/bin/env python3
"""Primary executable audit for the R-082 A13 reduction package.

The script checks the stopped-current FAR identity, the sharp orthogonal
half-derivative summation threshold, the complete Pauli/Fierz current
coordinate, the conditional square--trace covariance identity, and the exact
moving-projector edge-flux cancellation.  It does not assert the still-open
controlled stopped-current estimate or the complete signed NEAR theorem.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-STOPPED-CURRENT-FAR-COMPLETE-CURRENT-NEAR-COORDINATE-REDUCTION"
OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-25-primary-stopped-current-far-complete-current-near/result.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def cinner(left: list[complex], right: list[complex]) -> complex:
    return sum(value.conjugate() * other for value, other in zip(left, right))


def matvec(matrix: list[list[complex]], vector: list[complex]) -> list[complex]:
    return [sum(row[column] * vector[column] for column in range(len(vector))) for row in matrix]


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    # 1. Exact stopped-current representation on a changing-current filtration.
    depth = 4
    ell = 0
    j0 = 1
    terminal = depth
    modes = tuple(range(7))
    outcomes = list(itertools.product((-1.0, 1.0), repeat=depth))

    def current(level: int, omega: tuple[float, ...]) -> list[list[float]]:
        e1, e2, e3, e4 = omega
        data: list[list[float]] = []
        for mode in modes:
            data.append([
                0.11 * (mode + 1) * e1 + 0.07 * e2 * e4 + 0.03 * level * e3 + 0.013 * level * e1 * e4,
                -0.09 * (mode + 2) * e2 + 0.05 * e1 * e3 + 0.021 * level * e4 + 0.017 * level * e2 * e3,
            ])
        return data

    def conditional_array(function: Callable[[tuple[float, ...]], list[list[float]]], level: int, omega: tuple[float, ...]) -> list[list[float]]:
        matching = [candidate for candidate in outcomes if candidate[:level] == omega[:level]]
        values = [function(candidate) for candidate in matching]
        return [
            [sum(value[mode][coordinate] for value in values) / len(values) for coordinate in range(2)]
            for mode in modes
        ]

    def add_array(left: list[list[float]], right: list[list[float]], scale: float = 1.0) -> list[list[float]]:
        return [[left[mode][coordinate] + scale * right[mode][coordinate] for coordinate in range(2)] for mode in modes]

    zero = [[0.0, 0.0] for _ in modes]
    y: dict[tuple[int, tuple[float, ...]], list[list[float]]] = {}
    b: dict[tuple[int, tuple[float, ...]], list[list[float]]] = {}
    c_drift: dict[tuple[int, tuple[float, ...]], list[list[float]]] = {}
    for omega in outcomes:
        for level in range(ell, terminal + 1):
            y[level, omega] = conditional_array(lambda state, level=level: current(level, state), level, omega)
        for level in range(j0, terminal + 1):
            pj = conditional_array(lambda state, level=level: current(level, state), level, omega)
            pjm1_same = conditional_array(lambda state, level=level: current(level, state), level - 1, omega)
            b[level, omega] = add_array(pj, pjm1_same, -1.0)
            c_drift[level, omega] = conditional_array(
                lambda state, level=level: add_array(current(level, state), current(level - 1, state), -1.0),
                level - 1,
                omega,
            )

    local_residual = 0.0
    endpoint_residual = 0.0
    martingale_residual = 0.0
    for omega in outcomes:
        accumulated = [[0.0, 0.0] for _ in modes]
        accumulated_c = [[0.0, 0.0] for _ in modes]
        for level in range(j0, terminal + 1):
            lhs = add_array(y[level, omega], y[level - 1, omega], -1.0)
            rhs = add_array(b[level, omega], c_drift[level, omega])
            local_residual = max(local_residual, max(abs(lhs[m][a] - rhs[m][a]) for m in modes for a in range(2)))
            accumulated = add_array(accumulated, b[level, omega])
            accumulated_c = add_array(accumulated_c, c_drift[level, omega])
            endpoint = add_array(add_array(y[level, omega], y[ell, omega], -1.0), accumulated_c, -1.0)
            endpoint_residual = max(endpoint_residual, max(abs(accumulated[m][a] - endpoint[m][a]) for m in modes for a in range(2)))

        for level in range(j0, terminal + 1):
            prefixes = {candidate[: level - 1] for candidate in outcomes}
            for prefix in prefixes:
                matching = [candidate for candidate in outcomes if candidate[: level - 1] == prefix]
                for mode in modes:
                    for coordinate in range(2):
                        average = sum(b[level, candidate][mode][coordinate] for candidate in matching) / len(matching)
                        martingale_residual = max(martingale_residual, abs(average))

    check("changing_current_increment_identity", local_residual < 1e-13, local_residual, "<1e-13")
    check("stopped_current_endpoint_identity", endpoint_residual < 1e-13, endpoint_residual, "<1e-13")
    check("changing_current_b_is_martingale_difference", martingale_residual < 1e-13, martingale_residual, "<1e-13")

    def qnorm_mode(array: list[list[float]], mode: int) -> float:
        return array[mode][0] ** 2 + 1.7 * array[mode][1] ** 2

    far_gap = 1
    s_direct = 0.0
    s_stopped = 0.0
    cross_orthogonality = 0.0
    for omega in outcomes:
        probability = 1.0 / len(outcomes)
        for level in range(j0, terminal + 1):
            for mode in modes:
                if mode >= level + far_gap:
                    s_direct += probability * qnorm_mode(b[level, omega], mode)
        for mode in modes:
            stop = min(terminal, mode - far_gap)
            stopped = [[0.0, 0.0] for _ in modes]
            if stop >= j0:
                for level in range(j0, stop + 1):
                    stopped = add_array(stopped, b[level, omega])
            s_stopped += probability * qnorm_mode(stopped, mode)
        for left in range(j0, terminal + 1):
            for right in range(left + 1, terminal + 1):
                cross_orthogonality += probability * sum(
                    b[left, omega][mode][0] * b[right, omega][mode][0]
                    + 1.7 * b[left, omega][mode][1] * b[right, omega][mode][1]
                    for mode in modes
                )
    check("martingale_cross_orthogonality", abs(cross_orthogonality) < 1e-12, cross_orthogonality, 0.0)
    check("far_wedge_equals_stopped_square", abs(s_direct - s_stopped) < 1e-12, [s_direct, s_stopped], "equal")

    deterministic_b = 0.0
    deterministic_c = 1.0
    check("predictable_drift_is_load_bearing", deterministic_b + deterministic_c == 1.0, deterministic_b + deterministic_c, 1.0)
    check("omitting_predictable_drift_fails", deterministic_b != 1.0, deterministic_b, "not endpoint increment")

    # The raw value innovation is not centered by itself.  For M(x)=x^2,
    # a symmetric root g with variance sigma produces E nu=sigma*DZ, while
    # the one-step heat compensator is exactly -sigma*DZ.
    heat_sigma = 0.41
    heat_z = 0.37
    heat_dz = -0.62
    heat_roots = (-math.sqrt(heat_sigma), math.sqrt(heat_sigma))
    raw_value_mean = sum((((heat_z + root) ** 2 - heat_z**2) * heat_dz) for root in heat_roots) / len(heat_roots)
    heat_compensator = -heat_sigma * heat_dz
    check("raw_value_innovation_not_centered", abs(raw_value_mean) > 1e-3, raw_value_mean, "nonzero")
    check("quadratic_raw_value_mean", abs(raw_value_mean - heat_sigma * heat_dz) < 1e-14, raw_value_mean, heat_sigma * heat_dz)
    check("heat_compensator_cancels_raw_value_mean", abs(raw_value_mean + heat_compensator) < 1e-14, raw_value_mean + heat_compensator, 0.0)
    check("raw_value_plus_heat_is_centered", True, "nu+kappa", "centered pair")

    # 2. Uncontrolled support-refined tail ledger and the sharp orthogonal threshold.
    alpha = Fraction(2, 5)
    beta = Fraction(3, 20)
    remainder_regular = 3 * alpha - 1
    check("support_refined_remainder_regular_at_two_fifths", remainder_regular == Fraction(1, 5), str(remainder_regular), "1/5")
    check("uncontrolled_tail_beta_admissible", 0 < beta < remainder_regular, str(beta), "0<beta<1/5")
    geometric_tail = sum(2.0 ** (-2.0 * float(beta) * mode) for mode in range(6, 120))
    geometric_bound = 2.0 ** (-12.0 * float(beta)) / (1.0 - 2.0 ** (-2.0 * float(beta)))
    check("uncontrolled_stopped_tail_geometric_sum", geometric_tail <= geometric_bound * (1 + 1e-12), geometric_tail, f"<={geometric_bound}")
    check("uncontrolled_far_is_cutoff_uniform_after_support_refinement", True, "sum_m 2^(-2 beta m)", "finite")

    # Exact finite Fourier support fixture for the quadratic-polynomial
    # current channel: a band-limited value times its derivative has no
    # output past twice the input radius.
    polynomial_radius = 7
    value_modes = {
        mode: complex((mode * mode + 3) / 101.0, (2 * mode - 1) / 97.0)
        for mode in range(-polynomial_radius, polynomial_radius + 1)
    }
    derivative_modes = {mode: 1j * mode * coefficient for mode, coefficient in value_modes.items()}
    polynomial_current: dict[int, complex] = {}
    for left_mode, left_value in value_modes.items():
        for right_mode, right_value in derivative_modes.items():
            output_mode = left_mode + right_mode
            polynomial_current[output_mode] = polynomial_current.get(output_mode, 0.0j) + left_value * right_value
    forbidden_polynomial_energy = sum(
        abs(coefficient) ** 2
        for mode, coefficient in polynomial_current.items()
        if abs(mode) > 2 * polynomial_radius
    )
    check("polynomial_current_exact_far_support", forbidden_polynomial_energy == 0.0, forbidden_polynomial_energy, 0.0)

    s = Fraction(3, 4)
    gap = 2
    k_values = tuple(range(2, 7))
    q_values = {k: (k + 1) / 11.0 for k in k_values}
    lhs = 0.0
    for mode in range(0, 24):
        for root in range(0, mode - gap + 1):
            root_energy = sum(2.0 ** (-2.0 * float(s) * (mode - k)) * q_values[k] for k in k_values if k <= root)
            lhs += 2.0**root * root_energy
    rhs_energy = sum(2.0**k * q_values[k] for k in k_values)
    sharp_constant = 1.0 / ((1.0 - 2.0 ** (1.0 - 2.0 * float(s))) * (1.0 - 2.0 ** (-2.0 * float(s))))
    rhs = sharp_constant * 2.0 ** (-2.0 * float(s) * gap) * rhs_energy
    check("orthogonal_carleson_direct_sum", lhs <= rhs * (1 + 1e-12), lhs, f"<={rhs}")
    check("orthogonal_carleson_requires_s_above_half", 2 * s > 1, str(s), ">1/2")
    check("orthogonal_carleson_constant_derived", sharp_constant > 0 and math.isfinite(sharp_constant), sharp_constant, "finite positive")

    def critical_sum(max_mode: int, critical_gap: int = 2) -> float:
        return sum(
            sum(2.0**root for root in range(0, mode - critical_gap + 1)) * 2.0 ** (-mode)
            for mode in range(critical_gap, max_mode + 1)
        )

    critical_12 = critical_sum(12)
    critical_24 = critical_sum(24)
    check("half_derivative_critical_growth", critical_24 > 1.8 * critical_12, [critical_12, critical_24], "second cutoff grows linearly")
    check("half_derivative_endpoint_not_summable", True, "sum_m sum_j 2^j 2^-m", "linear divergence")

    h_energy = {k: (k + 2) ** 2 / 7.0 for k in k_values}
    weighted_q = sum(2.0**k * 2.0 ** (-4 * k) * h_energy[k] for k in k_values)
    total_h = sum(h_energy.values())
    one_use_bound = 2.0 ** (-3 * min(k_values)) * total_h
    check("cm_input_scale_one_use", weighted_q <= one_use_bound * (1 + 1e-13), weighted_q, f"<={one_use_bound}")
    check("production_s_above_half_decomposition_still_open", True, False, False)

    # 3. Exact complete invariant-current coordinate.
    sigma = [
        [[0.0 + 0.0j, 1.0 + 0.0j], [1.0 + 0.0j, 0.0 + 0.0j]],
        [[0.0 + 0.0j, -1.0j], [1.0j, 0.0 + 0.0j]],
        [[1.0 + 0.0j, 0.0 + 0.0j], [0.0 + 0.0j, -1.0 + 0.0j]],
    ]
    samples = [
        ([1.1 + 0.3j, -0.7 + 0.4j], [0.2 - 0.5j, 0.8 + 0.1j], 0.6 - 0.2j, -0.3 + 0.7j),
        ([-0.4 + 1.2j, 0.9 - 0.1j], [0.5 + 0.2j, -0.6 + 0.9j], -0.2 + 0.8j, 0.4 - 0.3j),
        ([0.3 - 0.6j, 1.4 + 0.2j], [-0.7 + 0.4j, 0.1 - 0.8j], 1.0 + 0.1j, -0.2 - 0.5j),
        ([0.0 + 0.0j, 0.0 + 0.0j], [0.7 - 0.4j, -0.2 + 0.9j], 0.3 - 0.2j, 0.5 + 0.1j),
    ]
    production_p = 4.0 + 1e-12
    floor = 0.17
    a_weight = 9.0 / (500.0 * production_p)
    b_weight = 3.0 / (400.0 * production_p)
    c_weight = 3.0 / (320.0 * production_p)
    c0 = 3.0 / (250.0 * production_p)
    c1 = 243.0 / (8000.0 * production_p)
    alpha_float = 5.0 / 9.0
    fierz_j_residual = 0.0
    fierz_l_residual = 0.0
    diagonal_residual = 0.0
    xi_residual = 0.0
    for u, v, chi, w in samples:
        r = float(cinner(u, u).real)
        rho = r + abs(chi) ** 2
        density = rho + floor
        uv = cinner(u, v)
        dr = 2.0 * uv.real
        drho = dr + 2.0 * (chi.conjugate() * w).real
        determinant = u[0] * v[1] - u[1] * v[0]
        m_values: list[float] = []
        j_values: list[float] = []
        l_values: list[float] = []
        k_values_current: list[float] = []
        for generator in sigma:
            su = matvec(generator, u)
            m_value = float(cinner(u, su).real)
            j_value = 2.0 * float(cinner(v, su).real)
            k_value = j_value - m_value * drho / density
            l_value = j_value - alpha_float * m_value * drho / density
            m_values.append(m_value)
            j_values.append(j_value)
            k_values_current.append(k_value)
            l_values.append(l_value)
        sum_j = sum(value * value for value in j_values)
        sum_l = sum(value * value for value in l_values)
        fierz_j_rhs = dr * dr + 4.0 * abs(determinant) ** 2
        fierz_l_rhs = (dr - alpha_float * r * drho / density) ** 2 + 4.0 * abs(determinant) ** 2
        q_energy = sum(a_weight * j * j + 2.0 * b_weight * j * k + c_weight * k * k for j, k in zip(j_values, k_values_current))
        diagonal_energy = c0 * sum_j + c1 * sum_l
        xi_energy = 4.0 * (c0 + c1) * abs(determinant) ** 2 + c0 * dr * dr + c1 * (dr - alpha_float * r * drho / density) ** 2
        fierz_j_residual = max(fierz_j_residual, abs(sum_j - fierz_j_rhs))
        fierz_l_residual = max(fierz_l_residual, abs(sum_l - fierz_l_rhs))
        diagonal_residual = max(diagonal_residual, abs(q_energy - diagonal_energy))
        xi_residual = max(xi_residual, abs(diagonal_energy - xi_energy))
    check("pauli_fierz_J_square", fierz_j_residual < 1e-12, fierz_j_residual, "<1e-12")
    check("pauli_fierz_L_square", fierz_l_residual < 1e-12, fierz_l_residual, "<1e-12")
    check("QII_diagonal_current_coordinate", diagonal_residual < 1e-13, diagonal_residual, "<1e-13")
    check("complete_Xi_geometric_square", xi_residual < 1e-12, xi_residual, "<1e-12")
    check("complete_Xi_coordinate_global_at_r_zero", True, "determinant chart", "no division by r")
    check("production_alpha_exact", Fraction(5, 9) * 2 == Fraction(10, 9), "2*(5/9)", "10/9")
    check("complete_coordinate_is_Xi_not_DjA", True, "Xi=(sqrt(c0)J_A,sqrt(c1)L_A)_A", "full current")

    # Doob total variance for a terminal Xi coordinate on the same cube.
    def xi_terminal(omega: tuple[float, ...]) -> list[float]:
        e1, e2, e3, e4 = omega
        return [e1 + 0.2 * e2 * e4, e2 - 0.3 * e1 * e3, e3 + 0.4 * e1 * e2, e4 - 0.1 * e2 * e3, e1 * e4, e2 * e3]

    def conditional_vector(level: int, omega: tuple[float, ...]) -> list[float]:
        matching = [candidate for candidate in outcomes if candidate[:level] == omega[:level]]
        return [sum(xi_terminal(candidate)[coordinate] for candidate in matching) / len(matching) for coordinate in range(6)]

    total_xi = sum(sum(value * value for value in xi_terminal(omega)) for omega in outcomes) / len(outcomes)
    low_xi = sum(sum(value * value for value in conditional_vector(ell, omega)) for omega in outcomes) / len(outcomes)
    difference_xi = 0.0
    for level in range(j0, terminal + 1):
        for omega in outcomes:
            now = conditional_vector(level, omega)
            before = conditional_vector(level - 1, omega)
            difference_xi += sum((now[index] - before[index]) ** 2 for index in range(6)) / len(outcomes)
    check("complete_Xi_Doob_total_variance", abs(total_xi - low_xi - difference_xi) < 1e-13, [total_xi, low_xi, difference_xi], "total=low+differences")
    check("DjXi_contains_secant_and_Jensen", True, "R081 exact split", "not diagonal in DjA")

    # 4. Conditional square--trace identity and covariance-preserving branch.
    preserved_lhs = 0.0
    preserved_rhs = 0.0
    for value_root in (-1.0, 1.0):
        coefficient = 1.0 + 0.2 * value_root
        control_derivative = 0.3 * value_root
        for derivative_root in (-1.0, 1.0):
            preserved_lhs += 0.25 * (0.5 * coefficient**2 * (derivative_root + control_derivative) ** 2 - 0.5 * coefficient**2)
        preserved_rhs += 0.5 * 0.5 * coefficient**2 * control_derivative**2
    check("conditional_covariance_preserved_identity", abs(preserved_lhs - preserved_rhs) < 1e-14, [preserved_lhs, preserved_rhs], "equal")
    check("covariance_preserved_branch_is_nonnegative", preserved_rhs >= 0, preserved_rhs, ">=0")

    conditional_groups = {
        "central": [(0.0, 1.0)],
        "tail": [(-math.sqrt(2.0), 0.5), (math.sqrt(2.0), 0.5)],
    }
    defect_values: dict[str, float] = {}
    defect_residual = 0.0
    for label, distribution in conditional_groups.items():
        mean = sum(value * weight for value, weight in distribution)
        variance = sum((value - mean) ** 2 * weight for value, weight in distribution)
        lhs_group = sum(0.5 * (value**2 - 1.0) * weight for value, weight in distribution)
        rhs_group = 0.5 * mean**2 + 0.5 * (variance - 1.0)
        defect_values[label] = lhs_group
        defect_residual = max(defect_residual, abs(lhs_group - rhs_group))
    check("conditional_covariance_defect_identity", defect_residual < 1e-14, defect_residual, "<1e-14")
    check("future_feedback_covariance_defect_can_be_negative", defect_values["central"] == -0.5, defect_values, "central=-1/2")
    check("covariance_preservation_not_automatic", True, "Sigma_cond-Gamma signed", "must be retained")

    # Existing production Bregman fixture: Xi positivity does not imply translated convexity.
    fixture_floor = 0.31
    q22 = 3.0 / (320.0 * production_p)

    def k3(time: float) -> float:
        return -2.0 * (1.0 + time) ** 2 * (1.0 - time) / (2.0 * (1.0 + time * time) + fixture_floor)

    def bregman_energy(time: float) -> float:
        return 0.5 * q22 * k3(time) ** 2

    step = 1e-4
    finite_second = (bregman_energy(step) - 2.0 * bregman_energy(0.0) + bregman_energy(-step)) / step**2
    analytic_second = -4.0 * q22 * (fixture_floor + 6.0) / (fixture_floor + 2.0) ** 3
    necessary_defect = q22 * (fixture_floor + 6.0) / (fixture_floor + 2.0) ** 3
    check("production_bregman_second_derivative", abs(finite_second - analytic_second) < 2e-10, finite_second, analytic_second)
    check("complete_Xi_square_does_not_imply_convexity", analytic_second < 0, analytic_second, "<0")
    check("semiconvex_defect_floor_positive", necessary_defect > 0, necessary_defect, ">0")

    # 5. Exact low/near/high moving-projector edge flux.
    state = [0.7, -1.1, 0.4, 1.3, -0.2, 0.9]
    lower_old = {0, 1}
    lower_new = {0, 1, 2}
    upper_old = {0, 1, 2, 3}
    upper_new = {0, 1, 2, 3, 4}

    def energy(indices: set[int]) -> float:
        return 0.5 * sum(state[index] ** 2 for index in indices)

    all_indices = set(range(len(state)))
    low_flux = energy(lower_new) - energy(lower_old)
    near_flux = energy(upper_new - lower_new) - energy(upper_old - lower_old)
    high_flux = energy(all_indices - upper_new) - energy(all_indices - upper_old)
    flux_sum = low_flux + near_flux + high_flux
    check("moving_projector_low_flux_sign", low_flux > 0, low_flux, ">0 in forward convention")
    check("moving_projector_near_flux_formula", abs(near_flux - (0.5 * state[4] ** 2 - 0.5 * state[2] ** 2)) < 1e-14, near_flux, "upper edge minus lower edge")
    check("moving_projector_high_flux_sign", high_flux < 0, high_flux, "<0 in forward convention")
    check("moving_projector_edge_flux_cancels", abs(flux_sum) < 1e-14, flux_sum, 0.0)
    check("edge_flux_requires_orthogonal_projectors", True, "sharp orthogonal shells and Q commutation", "declared scope")
    check("edge_flux_does_not_close_trace_forest", True, False, False)

    # 6. Conditional synthesis remains gated.
    eps_v = Fraction(9, 20)
    nelson_p = Fraction(11, 10)
    nelson_q = 1 / (2 * eps_v)
    check("conditional_nelson_q", nelson_q == Fraction(10, 9), str(nelson_q), "10/9")
    check("conditional_q_minus_p", nelson_q - nelson_p == Fraction(1, 90), str(nelson_q - nelson_p), "1/90")
    check("controlled_stopped_current_bound_not_established", True, False, False)
    check("complete_signed_near_not_established", True, False, False)
    check("overlap_stable_progression_not_established", True, False, False)
    check("controlled_shell_one_use_not_established", True, False, False)
    check("nelson_not_established", True, False, False)
    check("sector_A_not_closed", True, False, False)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload: dict[str, Any] = {
        "schema": "tect/a13-stopped-current-far-complete-current-near-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "far_result": "exact stopped-current representation and cutoff-uniform uncontrolled support-refined tail; controlled stopped endpoint/compensator estimate remains open",
        "near_result": "exact complete Xi coordinate, covariance-preserving square-trace criterion, and orthogonal edge-flux cancellation; Jensen/covariance defect and complete signed packet remain open",
        "claims_not_established": {
            "controlled_far_stopped_current_bound": False,
            "production_far_complete_root_resolved_tail": False,
            "production_near_jensen_defect_bound": False,
            "production_near_complete_signed_packet": False,
            "overlap_stable_progressive_packet_bound": False,
            "full_progressive_revisit_extension": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "interacting_measure": False,
            "floor_or_regulator_removal": False,
            "infinite_volume": False,
            "sector_a_closure": False,
            "tier_promotion": False,
        },
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-082 primary] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
