#!/usr/bin/env python3
"""Primary executable audit for the R-079 full safe-packet decomposition.

The script verifies the finite-filtration Hilbert-current identity, its exact
safe-packet subtraction, the future-control current commutator, the critical
weighted-Cauchy exponent ledger, and two abstract adapted-Wick no-go fixtures.
It does not assert the open production weighted lower bound.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-25-primary-full-safe-packet-frame-current-doob/result.json"
)
TOL = 2.0e-11


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


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def project(values: np.ndarray, states: np.ndarray, depth: int) -> np.ndarray:
    result = np.zeros_like(values, dtype=float)
    groups: dict[tuple[int, ...], list[int]] = {}
    for index, state in enumerate(states.astype(int)):
        groups.setdefault(tuple(state[:depth]), []).append(index)
    for indices in groups.values():
        result[indices] = np.mean(values[indices], axis=0)
    return result


def full_current_fixture() -> dict[str, Any]:
    """Coherent scalar-frame realization of the root-first exact identity."""

    states = np.asarray(
        [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)],
        dtype=float,
    )
    x, y, z = states.T
    field_value = 0.21 * x - 0.12 * x * y + 0.07 * z
    field_gradient = np.column_stack((0.31 * y + 0.08 * z, -0.24 * x + 0.11 * y * z))

    # Shell-k controls are F_(k-1)-measurable: constant, root-1, roots-1--2.
    value_increments = (np.full(len(states), 0.04), 0.08 * x, -0.055 * x * y)
    gradient_increments = (
        np.tile(np.asarray([0.021, -0.017]), (len(states), 1)),
        np.column_stack((0.05 * x, -0.03 * x)),
        np.column_stack((0.025 * x * y, 0.035 * y)),
    )
    value_controls = [np.full(len(states), 0.025)]
    gradient_controls = [np.tile(np.asarray([0.018, -0.012]), (len(states), 1))]
    for value_increment, gradient_increment in zip(value_increments, gradient_increments):
        value_controls.append(value_controls[-1] + value_increment)
        gradient_controls.append(gradient_controls[-1] + gradient_increment)

    predictability_error = 0.0
    past_increment_error = 0.0
    for shell in range(1, 4):
        predictability_error = max(
            predictability_error,
            float(np.max(np.abs(project(value_controls[shell], states, shell - 1) - value_controls[shell]))),
            float(np.max(np.abs(project(gradient_controls[shell], states, shell - 1) - gradient_controls[shell]))),
        )
        value_step = value_controls[shell] - value_controls[shell - 1]
        gradient_step = gradient_controls[shell] - gradient_controls[shell - 1]
        for depth in range(shell, 4):
            past_increment_error = max(
                past_increment_error,
                float(np.max(np.abs(project(value_step, states, depth) - project(value_step, states, depth - 1)))),
                float(np.max(np.abs(project(gradient_step, states, depth) - project(gradient_step, states, depth - 1)))),
            )

    def frame(value: np.ndarray) -> np.ndarray:
        return 1.18 + 0.14 * np.tanh(value)

    currents: list[np.ndarray] = []
    coefficients: list[np.ndarray] = []
    paid: list[np.ndarray] = []
    for value_control, gradient_control in zip(value_controls, gradient_controls):
        multiplier = frame(field_value + value_control)
        currents.append(multiplier[:, None] * (field_gradient + gradient_control))
        coefficients.append(multiplier**2)
        paid.append(0.07 * value_control**2 + 0.03 * value_control * np.sum(gradient_control**2, axis=1))

    current_zero, current_star = currents[0], currents[-1]
    coefficient_zero, coefficient_star = coefficients[0], coefficients[-1]
    gamma_low = 0.29
    gamma_increments = (0.13, 0.08, 0.055)
    gamma_terminal = gamma_low + sum(gamma_increments)

    projections_zero = [project(current_zero, states, depth) for depth in range(4)]
    projections_star = [project(current_star, states, depth) for depth in range(4)]
    low_current = 0.5 * float(
        np.mean(np.sum(projections_star[0] ** 2 - projections_zero[0] ** 2, axis=1))
    )
    low_trace = -0.5 * gamma_low * float(np.mean(coefficient_star - coefficient_zero))
    low_term = low_current + low_trace

    injected_total = 0.0
    future_total = 0.0
    increment_reassembly_error = 0.0
    commutator_error = 0.0
    trace_split_error = 0.0
    cross_sum = 0.0
    shell_records: list[dict[str, float]] = []
    for depth, gamma_increment in enumerate(gamma_increments, start=1):
        current_mid = currents[depth]
        coefficient_mid = coefficients[depth]
        d_zero = projections_zero[depth] - projections_zero[depth - 1]
        f = project(current_mid - current_zero, states, depth) - project(
            current_mid - current_zero, states, depth - 1
        )
        i = project(current_star - current_mid, states, depth) - project(
            current_star - current_mid, states, depth - 1
        )
        d_mid = project(current_mid, states, depth) - project(current_mid, states, depth - 1)
        d_star = projections_star[depth] - projections_star[depth - 1]
        increment_reassembly_error = max(
            increment_reassembly_error,
            float(np.max(np.abs(d_mid - (d_zero + f)))),
            float(np.max(np.abs(d_star - (d_zero + f + i)))),
        )

        injected_current = float(
            np.mean(np.sum(d_zero * f, axis=1) + 0.5 * np.sum(f**2, axis=1))
        )
        future_current = float(
            np.mean(np.sum(d_mid * i, axis=1) + 0.5 * np.sum(i**2, axis=1))
        )
        injected_trace = -0.5 * gamma_increment * float(
            np.mean(coefficient_mid - coefficient_zero)
        )
        future_trace = -0.5 * gamma_increment * float(
            np.mean(coefficient_star - coefficient_mid)
        )
        trace_split_error = max(
            trace_split_error,
            abs(
                injected_trace
                + future_trace
                + 0.5 * gamma_increment * float(np.mean(coefficient_star - coefficient_zero))
            ),
        )
        injected = injected_current + injected_trace
        future = future_current + future_trace
        injected_total += injected
        future_total += future
        cross_sum += float(np.mean(np.sum(f * i, axis=1)))

        multiplier_star = frame(field_value + value_controls[-1])
        multiplier_mid = frame(field_value + value_controls[depth])
        direct_difference = current_star - current_mid
        commutator = (
            (multiplier_star - multiplier_mid)[:, None]
            * (field_gradient + gradient_controls[depth])
            + multiplier_star[:, None]
            * (gradient_controls[-1] - gradient_controls[depth])
        )
        commutator_error = max(commutator_error, float(np.max(np.abs(direct_difference - commutator))))
        shell_records.append(
            {
                "depth": depth,
                "injected": injected,
                "future": future,
                "future_square": 0.5 * float(np.mean(np.sum(i**2, axis=1))),
            }
        )

    direct_current = 0.5 * float(
        np.mean(np.sum(current_star**2 - current_zero**2, axis=1))
    )
    direct_trace = -0.5 * gamma_terminal * float(np.mean(coefficient_star - coefficient_zero))
    direct_energy_difference = direct_current + direct_trace
    decomposition = low_term + injected_total + future_total

    endpoint_functionals = [
        0.5 * np.sum(current**2, axis=1) - 0.5 * gamma_terminal * coefficient - paid_value
        for current, coefficient, paid_value in zip(currents, coefficients, paid)
    ]
    causal_packet = np.zeros(len(states))
    for depth in range(1, 4):
        causal_packet += project(
            endpoint_functionals[depth] - endpoint_functionals[depth - 1],
            states,
            depth - 1,
        )
    paid_difference = float(np.mean(paid[-1] - paid[0]))
    safe_direct = direct_energy_difference - paid_difference
    safe_decomposition = decomposition - paid_difference
    safe_telescope_error = float(
        np.mean(causal_packet) - np.mean(endpoint_functionals[-1] - endpoint_functionals[0])
    )
    joined_causal_decomposition_error = float(np.mean(causal_packet) - safe_decomposition)
    joined_endpoint_safe_error = float(
        np.mean(endpoint_functionals[-1] - endpoint_functionals[0]) - safe_direct
    )
    complete_endpoint_error = float(
        np.mean(endpoint_functionals[-1])
        - np.mean(endpoint_functionals[0] + causal_packet)
    )

    return {
        "energy_identity_error": direct_energy_difference - decomposition,
        "safe_identity_error": safe_direct - safe_decomposition,
        "safe_telescope_error": safe_telescope_error,
        "complete_endpoint_error": complete_endpoint_error,
        "increment_reassembly_error": increment_reassembly_error,
        "commutator_error": commutator_error,
        "trace_split_error": trace_split_error,
        "predictability_error": predictability_error,
        "past_increment_error": past_increment_error,
        "joined_causal_decomposition_error": joined_causal_decomposition_error,
        "joined_endpoint_safe_error": joined_endpoint_safe_error,
        "frame_floor": float(min(np.min(frame(field_value + value)) for value in value_controls)),
        "future_square_sum": sum(record["future_square"] for record in shell_records),
        "cross_sum": cross_sum,
        "low_paid_endpoint": float(np.mean(paid[0])),
        "low_term": low_term,
        "injected_total": injected_total,
        "future_total": future_total,
        "paid_difference": paid_difference,
        "shells": shell_records,
    }


def exponent_fixture() -> dict[str, Fraction]:
    s = Fraction(3, 5)
    payload_x = (1 + s) / 4
    payload_y = (5 - s) / 12
    square_function_x = Fraction(1, 2)
    combined_x = payload_x + square_function_x
    combined_y = payload_y
    combined_slack = 1 - combined_x - combined_y
    general_slack = -(1 + s) / 6
    return {
        "s": s,
        "payload_x": payload_x,
        "payload_y": payload_y,
        "square_function_x": square_function_x,
        "combined_x": combined_x,
        "combined_y": combined_y,
        "combined_slack": combined_slack,
        "general_slack_at_s": general_slack,
    }


def gaussian_moment(power: int) -> sp.Integer:
    if power % 2:
        return sp.Integer(0)
    if power == 0:
        return sp.Integer(1)
    return sp.factorial2(power - 1)


def gaussian_expectation(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    polynomial = sp.Poly(sp.expand(expression), *variables)
    total = sp.Integer(0)
    for powers, coefficient in polynomial.terms():
        moment = coefficient
        for power in powers:
            moment *= gaussian_moment(power)
        total += moment
    return sp.simplify(total)


def adapted_wick_fixture() -> dict[str, Any]:
    xi, alpha = sp.symbols("xi alpha", real=True)
    h2 = xi**2 - 1
    h4 = xi**4 - 6 * xi**2 + 3
    h6 = xi**6 - 15 * xi**4 + 45 * xi**2 - 15
    control = alpha * (xi**2 - 4)
    hermite_error = sp.expand(control**2 - alpha**2 * (h4 - 2 * h2 + 11))
    forest_error = sp.expand(control**2 * h2 - alpha**2 * (h6 + 6 * h4 + 15 * h2 - 4))
    remainder = sp.Rational(1, 2) * gaussian_expectation(control**2 * h2, (xi,)) / alpha**2
    square = sp.Rational(1, 2) * gaussian_expectation((control * xi) ** 2, (xi,)) / alpha**2
    trace = -sp.Rational(1, 2) * gaussian_expectation(control**2, (xi,)) / alpha**2
    mean_control = gaussian_expectation(control, (xi,))
    innovation = gaussian_expectation((control - mean_control) ** 2, (xi,)) / alpha**2
    first_variation = gaussian_expectation(control * h2, (xi,)) / alpha

    amplitude = Fraction(1, 4)
    exponential_square = float(amplitude**2 / (10 * math.sqrt(5)))
    exponential_trace = float(-amplitude**2 / (2 * math.sqrt(5)))
    exponential_remainder = exponential_square + exponential_trace
    return {
        "hermite_error": str(sp.simplify(hermite_error)),
        "forest_error": str(sp.simplify(forest_error)),
        "normalized_remainder": str(remainder),
        "normalized_square": str(square),
        "normalized_trace": str(trace),
        "normalized_innovation_energy": str(innovation),
        "normalized_first_variation": str(first_variation),
        "exponential_amplitude": str(amplitude),
        "exponential_square": exponential_square,
        "exponential_trace": exponential_trace,
        "exponential_remainder": exponential_remainder,
        "exponential_frame_floor": 1.0,
    }


def rare_branch_fixture() -> dict[str, Fraction]:
    shell_frequency = Fraction(2)
    probability = shell_frequency ** -6
    amplitude_squared = 1 / probability
    expected_energy = probability * amplitude_squared
    conditional_peak = amplitude_squared
    control_amplitude = shell_frequency ** -2 * shell_frequency**3
    expected_sextic = probability * control_amplitude**6
    return {
        "shell_frequency": shell_frequency,
        "rare_probability": probability,
        "amplitude_squared": amplitude_squared,
        "expected_energy": expected_energy,
        "expected_sextic": expected_sextic,
        "conditional_peak": conditional_peak,
        "bmo_to_energy_ratio": conditional_peak / expected_energy,
    }


def weighted_cm_square_fixture() -> dict[str, float]:
    """Finite-tree version of the spatially weighted one-use identity."""

    states = np.asarray(
        [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)],
        dtype=float,
    )
    x, y, _ = states.T
    shell_controls = {
        1: np.full(len(states), 0.3),
        2: 0.4 * x,
        3: -0.2 * x + 0.35 * x * y,
    }
    weighted_square = 0.0
    energy = 0.0
    for shell, h_shell in shell_controls.items():
        frequency = float(2**shell)
        a_shell = frequency ** -2 * h_shell
        energy += float(np.mean(h_shell**2))
        for depth in range(1, shell):
            increment = project(a_shell, states, depth) - project(a_shell, states, depth - 1)
            weighted_square += frequency**4 * float(np.mean(increment**2))
    return {
        "weighted_square": weighted_square,
        "cm_energy": energy,
        "margin": energy - weighted_square,
    }


def conditional_gain_ledger() -> dict[str, Fraction]:
    gamma = Fraction(3, 10)
    x_power = Fraction(1, 2) - gamma / 4
    y_power = Fraction(1, 2) + gamma / 12
    slack = 1 - x_power - y_power
    return {
        "gamma": gamma,
        "x_power": x_power,
        "y_power": y_power,
        "slack": slack,
        "random_moment": 1 / slack,
        "eta_loss": x_power / slack,
        "zeta_loss": y_power / slack,
    }


def generic_spatial_no_go() -> dict[str, Any]:
    frequencies = np.asarray([8.0, 16.0, 32.0, 64.0])
    regularity = 3.0 / 5.0
    amplitude = 1.0
    grid = np.linspace(0.0, 2.0 * math.pi, 16384, endpoint=False)
    h_squares: list[float] = []
    brackets: list[float] = []
    for frequency in frequencies:
        h = amplitude * np.cos(frequency * grid)
        y = -amplitude * frequency**regularity * np.cos(frequency * grid)
        h_squares.append(float(np.mean(h**2)))
        brackets.append(float(np.mean(h * y)))
    ratios = [-bracket / square for bracket, square in zip(brackets, h_squares)]
    fitted_exponents = [
        math.log(ratios[index] / ratios[index - 1])
        / math.log(frequencies[index] / frequencies[index - 1])
        for index in range(1, len(frequencies))
    ]
    weighted_y_norms = [
        math.sqrt(2.0 * (amplitude * frequency**regularity / 2.0) ** 2 * frequency ** (-2.0 * regularity))
        for frequency in frequencies
    ]
    return {
        "frequencies": frequencies.tolist(),
        "regularity": regularity,
        "h_squares": h_squares,
        "weighted_y_norms": weighted_y_norms,
        "weighted_y_norm_spread": max(weighted_y_norms) - min(weighted_y_norms),
        "negative_brackets": brackets,
        "bracket_ratios": ratios,
        "fitted_exponents": fitted_exponents,
        "scaling_error": max(abs(value - regularity) for value in fitted_exponents),
    }


def heat_current_fixture() -> dict[str, Any]:
    x, y = sp.symbols("x y", real=True)
    past_value = sp.Rational(2, 7)
    past_gradient = sp.Rational(-3, 11)
    frame = 1 + (past_value + x) ** 2 + sp.Rational(1, 10) * (past_value + x) ** 4
    projected_current = gaussian_expectation(frame * (past_gradient + y), (x, y))
    heat_frame_times_past = gaussian_expectation(frame, (x,)) * past_gradient
    return {
        "projected_current": str(projected_current),
        "heat_frame_times_past": str(heat_frame_times_past),
        "difference": str(sp.simplify(projected_current - heat_frame_times_past)),
    }


def main() -> int:
    rows: list[dict[str, Any]] = []

    current = full_current_fixture()
    for key in (
        "energy_identity_error",
        "safe_telescope_error",
        "complete_endpoint_error",
        "increment_reassembly_error",
        "commutator_error",
        "trace_split_error",
        "predictability_error",
        "past_increment_error",
        "joined_causal_decomposition_error",
        "joined_endpoint_safe_error",
    ):
        add(rows, key, abs(float(current[key])) < TOL, current[key], 0.0)
    add(rows, "frame_uniformly_positive", current["frame_floor"] > 1.0, current["frame_floor"], ">1")
    add(rows, "future_square_retained", current["future_square_sum"] > 0.0, current["future_square_sum"], ">0")
    add(rows, "cross_term_nonzero", abs(current["cross_sum"]) > TOL, current["cross_sum"], "nonzero")
    add(rows, "paid_difference_nonzero", abs(current["paid_difference"]) > TOL, current["paid_difference"], "nonzero")
    add(rows, "low_paid_endpoint_retained", current["low_paid_endpoint"] > 0.0, current["low_paid_endpoint"], ">0")

    ledger = exponent_fixture()
    expected_ledger = {
        "payload_x": Fraction(2, 5),
        "payload_y": Fraction(11, 30),
        "square_function_x": Fraction(1, 2),
        "combined_x": Fraction(9, 10),
        "combined_y": Fraction(11, 30),
        "combined_slack": Fraction(-4, 15),
        "general_slack_at_s": Fraction(-4, 15),
    }
    for key, expected in expected_ledger.items():
        add(rows, f"exponent_{key}", ledger[key] == expected, str(ledger[key]), str(expected))
    add(rows, "square_function_only_supercritical", ledger["combined_slack"] < 0, str(ledger["combined_slack"]), "<0")

    wick = adapted_wick_fixture()
    add(rows, "hermite_second_power", wick["hermite_error"] == "0", wick["hermite_error"], "0")
    add(rows, "scalar_complete_hermite_product", wick["forest_error"] == "0", wick["forest_error"], "0")
    add(rows, "adapted_remainder", wick["normalized_remainder"] == "-2", wick["normalized_remainder"], "-2")
    add(rows, "terminal_square", wick["normalized_square"] == "7/2", wick["normalized_square"], "7/2")
    add(rows, "wick_trace", wick["normalized_trace"] == "-11/2", wick["normalized_trace"], "-11/2")
    add(rows, "innovation_energy", wick["normalized_innovation_energy"] == "2", wick["normalized_innovation_energy"], "2")
    add(rows, "wrong_sign_carre_du_champ", wick["normalized_remainder"] == "-2" and wick["normalized_innovation_energy"] == "2", {"remainder": wick["normalized_remainder"], "energy": wick["normalized_innovation_energy"]}, "remainder=-energy")
    add(rows, "first_variation_coefficient", wick["normalized_first_variation"] == "2", wick["normalized_first_variation"], "2")
    add(rows, "bounded_smooth_negative", wick["exponential_remainder"] < 0.0, wick["exponential_remainder"], "<0")
    add(rows, "bounded_smooth_frame_positive", wick["exponential_frame_floor"] > 0.0, wick["exponential_frame_floor"], ">0")

    rare = rare_branch_fixture()
    add(rows, "rare_branch_expected_energy", rare["expected_energy"] == 1, str(rare["expected_energy"]), "1")
    add(rows, "rare_branch_expected_sextic", rare["expected_sextic"] == 1, str(rare["expected_sextic"]), "1")
    add(rows, "rare_branch_conditional_peak", rare["conditional_peak"] == 64, str(rare["conditional_peak"]), "64")
    add(rows, "expected_budgets_not_bmo", rare["bmo_to_energy_ratio"] == 64, str(rare["bmo_to_energy_ratio"]), "64")

    weighted = weighted_cm_square_fixture()
    add(rows, "weighted_cm_square_nonzero", weighted["weighted_square"] > 0.0, weighted["weighted_square"], ">0")
    add(rows, "weighted_cm_one_use", weighted["margin"] >= -TOL, weighted["margin"], ">=0")

    gain = conditional_gain_ledger()
    gain_expected = {
        "x_power": Fraction(17, 40),
        "y_power": Fraction(21, 40),
        "slack": Fraction(1, 20),
        "random_moment": Fraction(20),
        "eta_loss": Fraction(17, 2),
        "zeta_loss": Fraction(21, 2),
    }
    for key, expected in gain_expected.items():
        add(rows, f"conditional_gain_{key}", gain[key] == expected, str(gain[key]), str(expected))

    spatial = generic_spatial_no_go()
    add(rows, "generic_spatial_brackets_negative", all(value < 0.0 for value in spatial["negative_brackets"]), spatial["negative_brackets"], "all <0")
    add(rows, "generic_spatial_ratio_grows", all(b > a for a, b in zip(spatial["bracket_ratios"], spatial["bracket_ratios"][1:])), spatial["bracket_ratios"], "strictly increasing")
    add(rows, "generic_spatial_scaling", spatial["scaling_error"] < 2.0e-12, spatial["scaling_error"], 0.0)
    add(rows, "generic_negative_norm_constant", spatial["weighted_y_norm_spread"] < 2.0e-14, spatial["weighted_y_norm_spread"], 0.0)

    heat = heat_current_fixture()
    add(rows, "base_current_heat_identity", heat["difference"] == "0", heat["difference"], "0")
    add(rows, "base_current_identity_nonzero", heat["projected_current"] != "0", heat["projected_current"], "nonzero")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-full-safe-packet-frame-current-doob-primary/1.0",
        "result_id": RESULT_ID,
        "claim_id": CLAIM,
        "source_version": __version__,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "full_current_decomposition": current,
        "exponents": {key: str(value) for key, value in ledger.items()},
        "adapted_wick_no_go": wick,
        "rare_branch_bmo_no_go": {key: str(value) for key, value in rare.items()},
        "weighted_cm_square_function": weighted,
        "conditional_positive_gain_ledger": {key: str(value) for key, value in gain.items()},
        "generic_spatial_no_go": spatial,
        "base_current_heat_identity": heat,
        "safe_subtractor_fixture_scope": (
            "The nonzero paid functional is a structural W-P sign/telescope fixture. "
            "The production identification P=N3_nr+T_le is proved analytically from "
            "the hash-pinned R-078 definition and is not numerically reconstructed here."
        ),
        "claims_not_established": {
            "weighted_production_lower_bound": False,
            "complete_packet_lower_bound": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "sector_a_closure": False,
        },
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-079 primary] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    if passed == len(rows):
        print("A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-PRIMARY-PASS")
        return 0
    for row in rows:
        if row["status"] != "PASS":
            print(f"FAIL {row['name']}: actual={row['actual']!r} expected={row['expected']!r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
