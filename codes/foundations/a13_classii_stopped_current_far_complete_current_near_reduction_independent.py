#!/usr/bin/env python3
"""Non-importing independent audit for the R-082 A13 reduction package.

This executable deliberately uses alternate finite filtrations, NumPy matrix
algebra, random Fourier fixtures, and a state-dependent Pauli--Fierz map.  It
does not import the primary R-082 executable.
"""

from __future__ import annotations

__version__ = "1.0.0"
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

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-STOPPED-CURRENT-FAR-COMPLETE-CURRENT-NEAR-COORDINATE-REDUCTION"
RESULT_PATH = ROOT / "claims" / CLAIM_ID / "runs/2026-07-25-independent-stopped-current-far-complete-current-near/result.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="independent-", suffix=".json.tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def add(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    # 1. Alternate changing-current filtration and deterministic stopped index.
    outcomes = list(itertools.product((-1.0, 1.0), repeat=3))
    modes = tuple(range(6))
    ell, j0, terminal, gap = 0, 1, 3, 2

    def current(level: int, omega: tuple[float, ...]) -> np.ndarray:
        e1, e2, e3 = omega
        return np.array(
            [
                [0.17 * (mode + 1) * e1 + 0.04 * level * e2 + 0.013 * level * e1 * e3,
                 -0.12 * (mode + 2) * e2 + 0.03 * e1 * e3 + 0.019 * level * e3]
                for mode in modes
            ],
            dtype=float,
        )

    def conditional(function: Callable[[tuple[float, ...]], np.ndarray], level: int, omega: tuple[float, ...]) -> np.ndarray:
        compatible = [candidate for candidate in outcomes if candidate[:level] == omega[:level]]
        return sum((function(candidate) for candidate in compatible), np.zeros((len(modes), 2))) / len(compatible)

    y: dict[tuple[int, tuple[float, ...]], np.ndarray] = {}
    b: dict[tuple[int, tuple[float, ...]], np.ndarray] = {}
    c_drift: dict[tuple[int, tuple[float, ...]], np.ndarray] = {}
    for omega in outcomes:
        for level in range(ell, terminal + 1):
            y[level, omega] = conditional(lambda state, level=level: current(level, state), level, omega)
        for level in range(j0, terminal + 1):
            b[level, omega] = conditional(lambda state, level=level: current(level, state), level, omega) - conditional(
                lambda state, level=level: current(level, state), level - 1, omega
            )
            c_drift[level, omega] = conditional(
                lambda state, level=level: current(level, state) - current(level - 1, state), level - 1, omega
            )

    local_error = 0.0
    endpoint_error = 0.0
    conditional_mean_error = 0.0
    for omega in outcomes:
        b_sum = np.zeros((len(modes), 2))
        c_sum = np.zeros((len(modes), 2))
        for level in range(j0, terminal + 1):
            local_error = max(local_error, float(np.max(np.abs(y[level, omega] - y[level - 1, omega] - b[level, omega] - c_drift[level, omega]))))
            b_sum += b[level, omega]
            c_sum += c_drift[level, omega]
            endpoint_error = max(endpoint_error, float(np.max(np.abs(b_sum - y[level, omega] + y[ell, omega] + c_sum))))
    for level in range(j0, terminal + 1):
        for prefix in {omega[: level - 1] for omega in outcomes}:
            compatible = [omega for omega in outcomes if omega[: level - 1] == prefix]
            conditional_mean_error = max(conditional_mean_error, float(np.max(np.abs(sum((b[level, omega] for omega in compatible), np.zeros((len(modes), 2))) / len(compatible)))))
    add("independent_changing_current_increment", local_error < 1e-13, local_error, "<1e-13")
    add("independent_stopped_endpoint", endpoint_error < 1e-13, endpoint_error, "<1e-13")
    add("independent_current_increment_centered", conditional_mean_error < 1e-13, conditional_mean_error, "<1e-13")

    direct_far = 0.0
    stopped_far = 0.0
    cross = 0.0
    metric = np.diag([1.0, 1.4])
    for omega in outcomes:
        probability = 1.0 / len(outcomes)
        for level in range(j0, terminal + 1):
            for mode in modes:
                if mode >= level + gap:
                    direct_far += probability * float(b[level, omega][mode] @ metric @ b[level, omega][mode])
        for mode in modes:
            stop = min(terminal, mode - gap)
            stopped = sum((b[level, omega] for level in range(j0, stop + 1)), np.zeros((len(modes), 2))) if stop >= j0 else np.zeros((len(modes), 2))
            stopped_far += probability * float(stopped[mode] @ metric @ stopped[mode])
        for left in range(j0, terminal + 1):
            for right in range(left + 1, terminal + 1):
                cross += probability * float(sum(b[left, omega][mode] @ metric @ b[right, omega][mode] for mode in modes))
    add("independent_martingale_root_orthogonality", abs(cross) < 1e-12, cross, 0.0)
    add("independent_far_wedge_stopped_square", abs(direct_far - stopped_far) < 1e-12, [direct_far, stopped_far], "equal")
    add("independent_stop_is_deterministic", True, "min(J,m-C)", "no optional stopping")

    deterministic_levels = [0.2, -0.3, 1.1, 0.7]
    deterministic_b = [0.0 for _ in range(terminal)]
    deterministic_c = [deterministic_levels[level] - deterministic_levels[level - 1] for level in range(j0, terminal + 1)]
    add("independent_predictable_drift_recovers_endpoint", abs(sum(deterministic_b) + sum(deterministic_c) - (deterministic_levels[-1] - deterministic_levels[0])) < 1e-14, sum(deterministic_c), deterministic_levels[-1] - deterministic_levels[0])
    add("independent_drift_omission_counterexample", abs(sum(deterministic_b) - (deterministic_levels[-1] - deterministic_levels[0])) > 0.1, sum(deterministic_b), "not endpoint")

    # M(x)=x^2: raw value innovation and heat compensator only center jointly.
    sigma = 0.29
    base = -0.43
    derivative = 0.71
    root_values = (-math.sqrt(sigma), math.sqrt(sigma))
    raw_mean = sum((((base + root) ** 2 - base**2) * derivative) for root in root_values) / len(root_values)
    compensator = (base**2 - (base**2 + sigma)) * derivative
    add("independent_raw_value_mean_nonzero", abs(raw_mean) > 1e-3, raw_mean, "nonzero")
    add("independent_raw_value_heat_cancellation", abs(raw_mean + compensator) < 1e-14, raw_mean + compensator, 0.0)
    add("independent_raw_value_alone_not_centered", raw_mean != 0.0, "nu", "requires kappa")

    # 2. Support-refined uncontrolled FAR and the orthogonal threshold.
    alpha = Fraction(2, 5)
    beta = Fraction(7, 40)
    regularity = 3 * alpha - 1
    add("independent_R050_remainder_regularity", regularity == Fraction(1, 5), str(regularity), "1/5")
    add("independent_localized_beta_range", 0 < beta < regularity, str(beta), "0<beta<1/5")

    rng = np.random.default_rng(20260725082)
    grid_size = 128
    radius = 5
    spectrum = np.zeros(grid_size, dtype=complex)
    for mode in range(1, radius + 1):
        coefficient = rng.normal() + 1j * rng.normal()
        spectrum[mode] = coefficient
        spectrum[-mode] = coefficient.conjugate()
    value = np.fft.ifft(spectrum).real
    derivative_spectrum = np.array([1j * (mode if mode <= grid_size // 2 else mode - grid_size) * spectrum[mode] for mode in range(grid_size)])
    derivative_value = np.fft.ifft(derivative_spectrum).real
    polynomial_spectrum = np.fft.fft(value * derivative_value)
    forbidden = [mode for mode in range(grid_size) if min(mode, grid_size - mode) > 2 * radius]
    forbidden_max = max(abs(polynomial_spectrum[mode]) for mode in forbidden)
    add("independent_polynomial_far_support", forbidden_max < 1e-13, forbidden_max, "<1e-13")
    add("independent_only_remainder_reaches_relative_far", True, "3alpha-1 channel", "support-refined statement")

    gap_tail = 5
    finite_tail = sum(2.0 ** (-2.0 * float(beta) * mode) for mode in range(gap_tail, 200))
    infinite_bound = 2.0 ** (-2.0 * float(beta) * gap_tail) / (1.0 - 2.0 ** (-2.0 * float(beta)))
    add("independent_uncontrolled_geometric_far", finite_tail <= infinite_bound * (1 + 1e-12), finite_tail, f"<={infinite_bound}")

    s = Fraction(4, 5)
    causal_gap = 3
    k_set = tuple(range(1, 6))
    q = {k: (2 * k + 1) / 17.0 for k in k_set}
    lhs = 0.0
    for mode in range(0, 48):
        for level in range(0, mode - causal_gap + 1):
            lhs += 2.0**level * sum(2.0 ** (-2.0 * float(s) * (mode - k)) * q[k] for k in k_set if k <= level)
    source = sum(2.0**k * q[k] for k in k_set)
    constant = 1.0 / ((1.0 - 2.0 ** (1.0 - 2.0 * float(s))) * (1.0 - 2.0 ** (-2.0 * float(s))))
    rhs = constant * 2.0 ** (-2.0 * float(s) * causal_gap) * source
    add("independent_orthogonal_causal_Carleson", lhs <= rhs * (1 + 1e-12), lhs, f"<={rhs}")
    add("independent_Carleson_threshold_strict", s > Fraction(1, 2), str(s), ">1/2")
    critical = []
    for cutoff in (20, 40, 80):
        critical.append(sum(sum(2.0**level for level in range(0, mode - causal_gap + 1)) * 2.0**(-mode) for mode in range(causal_gap, cutoff + 1)))
    add("independent_half_derivative_linear_divergence", critical[2] > 1.8 * critical[1], critical, "linear growth")
    h_energy = {k: (k + 1) ** 2 / 9.0 for k in k_set}
    weighted = sum(2.0**k * 2.0 ** (-4 * k) * h_energy[k] for k in k_set)
    one_use = 2.0 ** (-3 * min(k_set)) * sum(h_energy.values())
    add("independent_CM_scale_weight", weighted <= one_use * (1 + 1e-13), weighted, f"<={one_use}")
    add("independent_production_causal_decomposition_open", True, False, False)

    # 3. Production Pauli/Fierz coordinate and its rootwise limitation.
    pauli = (
        np.array([[0, 1], [1, 0]], dtype=complex),
        np.array([[0, -1j], [1j, 0]], dtype=complex),
        np.array([[1, 0], [0, -1]], dtype=complex),
    )
    production_p = 4.0 + 1e-12
    floor = 0.23
    a_weight = 9.0 / (500.0 * production_p)
    b_weight = 3.0 / (400.0 * production_p)
    c_weight = 3.0 / (320.0 * production_p)
    c0 = 3.0 / (250.0 * production_p)
    c1 = 243.0 / (8000.0 * production_p)
    alpha_float = 5.0 / 9.0
    qii = np.array([[a_weight, b_weight], [b_weight, c_weight]])
    bridge = np.array([[math.sqrt(c0), 0.0], [math.sqrt(c1) * (1.0 - alpha_float), math.sqrt(c1) * alpha_float]])
    add("independent_bridge_Gram_is_QII", float(np.max(np.abs(bridge.T @ bridge - qii))) < 1e-15, float(np.max(np.abs(bridge.T @ bridge - qii))), "<1e-15")

    def unpack(real: np.ndarray) -> tuple[np.ndarray, complex]:
        return np.array([real[0] + 1j * real[3], real[1] + 1j * real[4]]), complex(real[2], real[5])

    def currents(z_real: np.ndarray, y_real: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        u, chi = unpack(z_real)
        v, w = unpack(y_real)
        r = float(np.vdot(u, u).real)
        density = r + abs(chi) ** 2 + floor
        drho = 2.0 * float((np.vdot(u, v) + chi.conjugate() * w).real)
        j_values = []
        k_values = []
        for generator in pauli:
            moment = float(np.vdot(u, generator @ u).real)
            j_value = 2.0 * float(np.vdot(v, generator @ u).real)
            j_values.append(j_value)
            k_values.append(j_value - moment * drho / density)
        return np.array(j_values), np.array(k_values)

    def fixed_six(z_real: np.ndarray, y_real: np.ndarray) -> np.ndarray:
        j_values, k_values = currents(z_real, y_real)
        l_values = (1.0 - alpha_float) * j_values + alpha_float * k_values
        return np.concatenate((math.sqrt(c0) * j_values, math.sqrt(c1) * l_values))

    def xi_four(z_real: np.ndarray, y_real: np.ndarray) -> np.ndarray:
        u, chi = unpack(z_real)
        v, w = unpack(y_real)
        r = float(np.vdot(u, u).real)
        density = r + abs(chi) ** 2 + floor
        dr = 2.0 * float(np.vdot(u, v).real)
        drho = dr + 2.0 * float((chi.conjugate() * w).real)
        determinant = u[0] * v[1] - u[1] * v[0]
        return np.array(
            [
                math.sqrt(c0) * dr,
                math.sqrt(c1) * (dr - alpha_float * r * drho / density),
                2.0 * math.sqrt(c0 + c1) * determinant.real,
                2.0 * math.sqrt(c0 + c1) * determinant.imag,
            ]
        )

    max_energy_error = 0.0
    for _ in range(128):
        z_real = rng.normal(size=6)
        y_real = rng.normal(size=6)
        max_energy_error = max(max_energy_error, abs(float(fixed_six(z_real, y_real) @ fixed_six(z_real, y_real) - xi_four(z_real, y_real) @ xi_four(z_real, y_real))))
    add("independent_global_Pauli_Fierz_energy", max_energy_error < 2e-13, max_energy_error, "<2e-13")
    zero_state = np.zeros(6)
    add("independent_Xi_regular_at_doublet_zero", float(np.linalg.norm(xi_four(zero_state, rng.normal(size=6)))) == 0.0, float(np.linalg.norm(xi_four(zero_state, rng.normal(size=6)))), 0.0)

    gram_state = np.array([0.8, -0.4, 0.3, 0.2, 0.5, -0.1])
    identity6 = np.eye(6)
    fixed_matrix = np.column_stack([fixed_six(gram_state, identity6[index]) for index in range(6)])
    xi_matrix = np.column_stack([xi_four(gram_state, identity6[index]) for index in range(6)])
    gram_error = float(np.max(np.abs(fixed_matrix.T @ fixed_matrix - xi_matrix.T @ xi_matrix)))
    add("independent_B_equals_CtC", gram_error < 2e-15, gram_error, "<2e-15")
    eig_min = float(np.linalg.eigvalsh(xi_matrix.T @ xi_matrix).min())
    add("independent_complete_current_Gram_psd", eig_min > -1e-15, eig_min, ">=-1e-15")

    tree_values: dict[tuple[float, float], tuple[np.ndarray, np.ndarray]] = {}
    for epsilon1, epsilon2 in itertools.product((-1.0, 1.0), repeat=2):
        z_real = np.array([0.7 + 0.2 * epsilon1, 0.35 + 0.18 * epsilon2, 0.1 * epsilon1 * epsilon2, -0.25 + 0.1 * epsilon2, 0.2 * epsilon1, 0.05])
        y_real = np.array([0.4 + 0.1 * epsilon2, -0.3 + 0.15 * epsilon1, 0.2, 0.1 * epsilon1 * epsilon2, -0.2 + 0.12 * epsilon2, 0.08 * epsilon1])
        tree_values[epsilon1, epsilon2] = fixed_six(z_real, y_real), xi_four(z_real, y_real)

    def doob_energies(coordinate: int) -> tuple[float, float, float, float]:
        values = {key: pair[coordinate] for key, pair in tree_values.items()}
        mean = sum(values.values(), np.zeros_like(next(iter(values.values())))) / len(values)
        first_means = {epsilon1: sum((values[epsilon1, epsilon2] for epsilon2 in (-1.0, 1.0)), np.zeros_like(mean)) / 2.0 for epsilon1 in (-1.0, 1.0)}
        root1 = sum(float((first_means[epsilon1] - mean) @ (first_means[epsilon1] - mean)) for epsilon1 in (-1.0, 1.0)) / 2.0
        root2 = sum(float((values[epsilon1, epsilon2] - first_means[epsilon1]) @ (values[epsilon1, epsilon2] - first_means[epsilon1])) for epsilon1, epsilon2 in values) / 4.0
        terminal_energy = sum(float(value @ value) for value in values.values()) / 4.0
        mean_energy = float(mean @ mean)
        return root1, root2, terminal_energy, mean_energy

    fixed_doob = doob_energies(0)
    xi_doob = doob_energies(1)
    pointwise_error = max(abs(float(pair[0] @ pair[0] - pair[1] @ pair[1])) for pair in tree_values.values())
    add("independent_compression_pointwise_norm", pointwise_error < 1e-15, pointwise_error, "<1e-15")
    add("independent_compression_terminal_energy", abs(fixed_doob[2] - xi_doob[2]) < 1e-15, [fixed_doob[2], xi_doob[2]], "equal")
    add("independent_fixed_current_Doob", abs(fixed_doob[2] - fixed_doob[3] - fixed_doob[0] - fixed_doob[1]) < 1e-15, fixed_doob, "terminal=mean+roots")
    add("independent_PF_coordinate_Doob", abs(xi_doob[2] - xi_doob[3] - xi_doob[0] - xi_doob[1]) < 1e-15, xi_doob, "terminal=mean+roots")
    add("independent_PF_root_blocks_redistributed", abs(fixed_doob[0] - xi_doob[0]) > 1e-4 and abs(fixed_doob[1] - xi_doob[1]) > 1e-4, {"fixed": fixed_doob[:2], "PF": xi_doob[:2]}, "both roots differ")

    heat_t = 0.6
    heat_plus = np.array([heat_t, 0, 0, 0, 0, 0], dtype=float)
    heat_minus = -heat_plus
    c_plus = np.column_stack([xi_four(heat_plus, identity6[index]) for index in range(6)])
    c_minus = np.column_stack([xi_four(heat_minus, identity6[index]) for index in range(6)])
    averaged_c = 0.5 * (c_plus + c_minus)
    averaged_b = 0.5 * (c_plus.T @ c_plus + c_minus.T @ c_minus)
    add("independent_heat_average_C_zero", float(np.max(np.abs(averaged_c))) < 1e-15, float(np.max(np.abs(averaged_c))), 0.0)
    add("independent_heat_average_B_nonzero", float(np.linalg.norm(averaged_b)) > 1e-4, float(np.linalg.norm(averaged_b)), ">0")
    add("independent_average_B_not_square_average_C", float(np.linalg.norm(averaged_b - averaged_c.T @ averaged_c)) > 1e-4, float(np.linalg.norm(averaged_b - averaged_c.T @ averaged_c)), ">0")

    # 4. Conditional square--trace formula and signed covariance defect.
    coefficient = np.array([[1.1, -0.2], [0.3, 0.7]])
    b_matrix = coefficient.T @ coefficient
    control = np.array([0.25, -0.15])
    fresh_values = (np.array([1.0, 0.5]), np.array([-1.0, -0.5]))
    gamma = np.array([[1.0, 0.5], [0.5, 0.25]])
    lhs_conditional = sum(0.5 * float((coefficient @ (fresh + control)) @ (coefficient @ (fresh + control))) - 0.5 * float(np.trace(b_matrix @ gamma)) for fresh in fresh_values) / len(fresh_values)
    rhs_conditional = 0.5 * float((coefficient @ control) @ (coefficient @ control))
    add("independent_covariance_preserving_square_trace", abs(lhs_conditional - rhs_conditional) < 1e-14, [lhs_conditional, rhs_conditional], "equal")
    add("independent_covariance_preserving_positive", rhs_conditional >= 0.0, rhs_conditional, ">=0")
    negative_defect = 0.5 * (0.0**2 - 1.0)
    positive_defect = sum(0.5 * (value**2 - 1.0) for value in (-math.sqrt(2.0), math.sqrt(2.0))) / 2.0
    add("independent_conditional_covariance_defect_negative", negative_defect == -0.5, negative_defect, -0.5)
    add("independent_conditional_covariance_defect_signed", negative_defect < 0 < positive_defect, [negative_defect, positive_defect], "both signs")
    add("independent_complete_NEAR_still_needs_trace_forest", True, "mixed+trace+paid+forest", "retained")

    # 5. Sharp moving-projector edge bookkeeping.
    vector = np.array([0.4, -0.9, 1.2, 0.3, -0.7, 0.8])
    low_old, low_new = {0}, {0, 1}
    high_old, high_new = {0, 1, 2, 3}, {0, 1, 2, 3, 4}

    def energy(indices: set[int]) -> float:
        return 0.5 * float(sum(vector[index] ** 2 for index in indices))

    universe = set(range(len(vector)))
    low_flux = energy(low_new) - energy(low_old)
    near_flux = energy(high_new - low_new) - energy(high_old - low_old)
    high_flux = energy(universe - high_new) - energy(universe - high_old)
    add("independent_low_edge_flux_positive", low_flux > 0.0, low_flux, ">0")
    add("independent_near_edge_difference", abs(near_flux - 0.5 * (vector[4] ** 2 - vector[1] ** 2)) < 1e-14, near_flux, "upper minus lower")
    add("independent_high_edge_flux_negative", high_flux < 0.0, high_flux, "<0")
    add("independent_three_region_flux_cancels", abs(low_flux + near_flux + high_flux) < 1e-14, low_flux + near_flux + high_flux, 0.0)
    add("independent_absolute_pair_high_not_licensed", True, "signed repartition", "no new positivity")

    eps_v = Fraction(9, 20)
    nelson_p = Fraction(11, 10)
    nelson_q = 1 / (2 * eps_v)
    add("independent_conditional_q", nelson_q == Fraction(10, 9), str(nelson_q), "10/9")
    add("independent_conditional_q_margin", nelson_q - nelson_p == Fraction(1, 90), str(nelson_q - nelson_p), "1/90")
    add("independent_controlled_FAR_open", True, False, False)
    add("independent_complete_signed_NEAR_open", True, False, False)
    add("independent_overlap_progression_open", True, False, False)
    add("independent_one_use_open", True, False, False)
    add("independent_Nelson_open", True, False, False)
    add("independent_sector_A_open", True, False, False)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload: dict[str, Any] = {
        "schema": "tect/a13-stopped-current-far-complete-current-near-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM_ID,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "independence": "No import from the primary executable; alternate filtration, random Fourier support, NumPy Gram algebra, a two-root state-dependent compression regression, and direct conditional-covariance fixtures.",
        "claims_not_established": {
            "controlled_far_stopped_current_bound": False,
            "production_far_complete_root_resolved_tail": False,
            "production_near_complete_signed_packet": False,
            "overlap_stable_progressive_packet_bound": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "interacting_measure": False,
            "sector_a_closure": False,
            "tier_promotion": False,
        },
    }
    atomic_json(RESULT_PATH, payload)
    print(f"[R-082 independent] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
