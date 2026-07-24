#!/usr/bin/env python3
"""Non-importing audit of the A13 Wick--Doob/resolvent reduction."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import itertools
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-24-independent-wick-doob-terminal-resolvent-reduction/result.json"
)

# Independent test inputs and numerical tolerances.
SEED = 70240724
CASES = 180
GH_ORDER = 7
GH_ORDER_FINE = 9
MATRIX_GH_ORDER = 3
MATRIX_GH_ORDER_FINE = 5
FOURIER_GRID = 192
FOURIER_GRID_FINE = 384
KAPPA_NUMERATOR = 1
KAPPA_DENOMINATOR = 10
P_COLUMN_TEST_WEIGHT = 0.37
TOL = 3.0e-10


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name, suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})


def matrix_wick_step() -> dict[str, float]:
    rng = np.random.default_rng(SEED)
    maximum = 0.0
    nontrivial = 0.0
    resolution_envelope = 0.0
    for _ in range(CASES):
        dimension = 4
        root = rng.normal(size=(dimension, dimension))
        coefficient = root.T @ root + 0.2 * np.eye(dimension)
        g_value = rng.normal(size=dimension)
        c_value = rng.normal(size=dimension)
        noise_root = rng.normal(size=(dimension, dimension)) / dimension
        covariance = noise_root @ noise_root.T
        old = 0.5 * (
            (g_value + c_value) @ coefficient @ (g_value + c_value)
            - np.trace(coefficient @ covariance)
        )
        order_values: dict[int, tuple[float, float]] = {}
        for order in (MATRIX_GH_ORDER, MATRIX_GH_ORDER_FINE):
            nodes, weights = np.polynomial.hermite.hermgauss(order)
            nodes = math.sqrt(2.0) * nodes
            weights = weights / math.sqrt(math.pi)
            expected_next = 0.0
            absolute_increment = 0.0
            for multi in itertools.product(range(order), repeat=dimension):
                standard = np.asarray([nodes[index] for index in multi])
                weight = float(np.prod([weights[index] for index in multi]))
                noise = noise_root @ standard
                next_value = 0.5 * (
                    (g_value + c_value + noise)
                    @ coefficient
                    @ (g_value + c_value + noise)
                    - 2.0 * np.trace(coefficient @ covariance)
                )
                expected_next += weight * next_value
                absolute_increment += weight * abs(next_value - old)
            order_values[order] = (expected_next, absolute_increment)
        coarse_expected, _ = order_values[MATRIX_GH_ORDER]
        fine_expected, fine_absolute = order_values[MATRIX_GH_ORDER_FINE]
        maximum = max(maximum, abs(float(fine_expected - old)))
        nontrivial = max(nontrivial, fine_absolute)
        resolution_envelope = max(
            resolution_envelope, abs(float(fine_expected - coarse_expected))
        )
    return {
        "maximum_conditional_residual": maximum,
        "maximum_absolute_increment": nontrivial,
        "resolution_envelope": resolution_envelope,
        "coarse_order": MATRIX_GH_ORDER,
        "fine_order": MATRIX_GH_ORDER_FINE,
    }


def two_shell_telescope_at_order(order: int) -> dict[str, float]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    nodes = math.sqrt(2.0) * nodes
    weights = weights / math.sqrt(math.pi)
    value_variance = [0.36, 0.16]
    derivative_variance = [0.49, 0.25]
    total_raw = 0.0
    total_wick = 0.0
    total_trace = 0.0
    total_terminal_raw = 0.0
    total_terminal_wick = 0.0
    for indices in itertools.product(range(order), repeat=4):
        xi = [math.sqrt(value_variance[i]) * nodes[indices[i]] for i in range(2)]
        derivative = [math.sqrt(derivative_variance[i]) * nodes[indices[i + 2]] for i in range(2)]
        weight = float(np.prod([weights[index] for index in indices]))
        u_value = float(sum(xi))
        a_value = 0.0
        c_value = 0.0
        g_value = 0.0
        covariance = 0.0
        raw_sum = 0.0
        wick_sum = 0.0
        trace_sum = 0.0
        injection = 0.0
        for shell in range(2):
            if shell == 0:
                a_shell, b_shell = 0.11, -0.07
            else:
                a_shell = -0.04 + 0.03 * xi[0] - 0.02 * derivative[0]
                b_shell = 0.02 + 0.01 * xi[0] + 0.025 * derivative[0]
            z_old = u_value + a_value
            z_new = z_old + a_shell
            b_old = 1.0 + z_old**2 + 0.15 * z_old**4
            b_new = 1.0 + z_new**2 + 0.15 * z_new**4
            c_new = c_value + b_shell
            raw_increment = 0.5 * b_new * (g_value + c_new) ** 2
            raw_increment -= 0.5 * b_old * (g_value + c_value) ** 2
            wick_increment = raw_increment - 0.5 * (b_new - b_old) * covariance
            trace_increment = 0.5 * (b_new - b_old) * covariance
            raw_sum += raw_increment
            wick_sum += wick_increment
            trace_sum += trace_increment
            injection += 0.5 * b_new * derivative_variance[shell]
            a_value += a_shell
            c_value = c_new
            g_value += derivative[shell]
            covariance += derivative_variance[shell]
        terminal_coefficient = 1.0 + (u_value + a_value) ** 2 + 0.15 * (u_value + a_value) ** 4
        terminal_raw = 0.5 * terminal_coefficient * (g_value + c_value) ** 2 - injection
        terminal_wick = 0.5 * terminal_coefficient * ((g_value + c_value) ** 2 - covariance)
        total_raw += weight * raw_sum
        total_wick += weight * wick_sum
        total_trace += weight * trace_sum
        total_terminal_raw += weight * terminal_raw
        total_terminal_wick += weight * terminal_wick
    return {
        "raw_terminal_residual": total_raw - total_terminal_raw,
        "wick_terminal_residual": total_wick - total_terminal_wick,
        "trace_restoration_residual": total_raw - total_wick - total_trace,
        "nonzero_terminal_wick": total_terminal_wick,
    }


def two_shell_telescope() -> dict[str, float]:
    coarse = two_shell_telescope_at_order(GH_ORDER)
    fine = two_shell_telescope_at_order(GH_ORDER_FINE)
    result = dict(fine)
    result["resolution_envelope"] = max(
        abs(fine[key] - coarse[key]) for key in coarse
    )
    result["coarse_order"] = float(GH_ORDER)
    result["fine_order"] = float(GH_ORDER_FINE)
    return result


def schur_completion() -> dict[str, float]:
    rng = np.random.default_rng(SEED + 1)
    maximum = 0.0
    minimum_trace_margin = math.inf
    for _ in range(CASES):
        dimension = 3
        root = rng.normal(size=(dimension, dimension))
        operator = root.T @ root
        gaussian = rng.normal(size=dimension)
        shift = rng.normal(size=dimension)
        p_value = 0.1 + rng.random()
        resolver = np.linalg.solve(np.eye(dimension) + p_value * operator, np.eye(dimension))
        centered_operator = operator @ resolver
        lhs = 0.5 * (gaussian + shift) @ operator @ (gaussian + shift)
        lhs -= 0.5 * np.trace(operator)
        lhs += float(shift @ shift) / (2.0 * p_value)
        vector = shift + p_value * resolver @ operator @ gaussian
        rhs = 0.5 * (gaussian @ centered_operator @ gaussian - np.trace(centered_operator))
        rhs -= 0.5 * p_value * np.trace(operator @ operator @ resolver)
        rhs += 0.5 * vector @ (operator + np.eye(dimension) / p_value) @ vector
        maximum = max(maximum, abs(float(lhs - rhs)))
        minimum_trace_margin = min(
            minimum_trace_margin,
            float(np.trace(operator @ operator) - np.trace(operator @ operator @ resolver)),
        )
    return {"maximum_residual": maximum, "minimum_trace_margin": minimum_trace_margin}


def adapted_indicator() -> dict[str, float]:
    threshold = 0.65
    amplitude = 1.25
    p_value = 0.9
    density = math.exp(-(threshold**2) / 2.0) / math.sqrt(2.0 * math.pi)
    probability = math.erf(threshold / math.sqrt(2.0))
    second = probability - 2.0 * threshold * density
    raw = 0.5 * amplitude**2 * (second - probability)
    formula = -threshold * density * amplitude**2
    resolved = raw / (1.0 + p_value * amplitude**2)
    return {"raw": raw, "formula": formula, "resolved": resolved}


def asymmetric_covariance() -> dict[str, float]:
    background = -0.6
    correlation = -0.2
    formula = 2.0 * background * correlation
    return {"formula": formula, "background": background, "correlation": correlation}


def hardy_exact() -> dict[str, float]:
    rng = np.random.default_rng(SEED + 2)
    count = 14
    scales = 2.0 ** np.arange(3, 3 + count)
    h_value = rng.normal(size=count)
    a_square = scales ** (-4.0) * h_value**2
    left = sum(
        scales[index] ** (-2.0) * float(np.sum(a_square[:index]))
        for index in range(count)
    )
    rearranged = sum(
        a_square[index] * float(np.sum(scales[index + 1 :] ** (-2.0)))
        for index in range(count)
    )
    adjacent_ratio = float(scales[1] / scales[0])
    tail_ratio = adjacent_ratio ** (-2.0)
    geometric_tail_factor = tail_ratio / (1.0 - tail_ratio)
    infinite = geometric_tail_factor * float(
        np.sum(scales ** (-6.0) * h_value**2)
    )
    return {
        "left": left,
        "rearranged": rearranged,
        "infinite": infinite,
        "adjacent_scale_ratio": adjacent_ratio,
        "geometric_tail_factor": geometric_tail_factor,
    }


def fourier_parts_at_grid(count: int) -> tuple[float, float]:
    x_value = 2.0 * math.pi * np.arange(count) / count
    # Independent resonant anchor with exact nonzero value test_weight/2.
    u_value = np.sin(x_value)
    a_value = np.sin(x_value)
    frequencies = np.fft.fftfreq(count, d=1.0 / count)

    def derivative(values: np.ndarray, degree: int) -> np.ndarray:
        return np.fft.ifft((1j * frequencies) ** degree * np.fft.fft(values)).real

    left = P_COLUMN_TEST_WEIGHT * float(
        np.mean(derivative(u_value**2, 1) * derivative(a_value**2, 1))
    )
    right = -P_COLUMN_TEST_WEIGHT * float(
        np.mean(derivative(u_value**2, 2) * a_value**2)
    )
    return left, right


def fourier_parts() -> dict[str, float]:
    coarse_left, coarse_right = fourier_parts_at_grid(FOURIER_GRID)
    left, right = fourier_parts_at_grid(FOURIER_GRID_FINE)
    kappa = KAPPA_NUMERATOR / KAPPA_DENOMINATOR
    theta = (1.0 + 2.0 * kappa) / 3.0
    x_power = (1.0 + theta) / 2.0
    y_power = (1.0 - theta) / 6.0
    moment = 1.0 / (1.0 - x_power - y_power)
    analytic_oracle = P_COLUMN_TEST_WEIGHT / 2.0
    return {
        "left": left,
        "right": right,
        "analytic_oracle": analytic_oracle,
        "moment": moment,
        "test_weight": P_COLUMN_TEST_WEIGHT,
        "coarse_grid": FOURIER_GRID,
        "fine_grid": FOURIER_GRID_FINE,
        "resolution_envelope": max(
            abs(left - coarse_left), abs(right - coarse_right)
        ),
    }


def main() -> int:
    wick_step = matrix_wick_step()
    telescope = two_shell_telescope()
    schur = schur_completion()
    adapted = adapted_indicator()
    asymmetric = asymmetric_covariance()
    hardy = hardy_exact()
    parts = fourier_parts()
    kappa_oracle = Fraction(KAPPA_NUMERATOR, KAPPA_DENOMINATOR)
    theta_oracle = (1 + 2 * kappa_oracle) / 3
    x_power_oracle = (1 + theta_oracle) / 2
    y_power_oracle = (1 - theta_oracle) / 6
    moment_oracle = 1 / (1 - x_power_oracle - y_power_oracle)
    rows: list[dict[str, Any]] = []
    add(rows, "matrix_fresh_wick_step", wick_step["maximum_conditional_residual"] < TOL and wick_step["resolution_envelope"] < TOL, wick_step, "centered; coarse/fine envelope < tolerance")
    add(rows, "matrix_step_nontrivial", wick_step["maximum_absolute_increment"] > 1.0e-3, wick_step["maximum_absolute_increment"], "nonzero")
    add(rows, "quartic_coefficient_raw_telescope", abs(telescope["raw_terminal_residual"]) < TOL, telescope["raw_terminal_residual"], 0.0)
    add(rows, "quartic_coefficient_wick_telescope", abs(telescope["wick_terminal_residual"]) < TOL, telescope["wick_terminal_residual"], 0.0)
    add(rows, "quartic_trace_restoration", abs(telescope["trace_restoration_residual"]) < TOL and telescope["resolution_envelope"] < TOL, telescope, "trace restored; coarse/fine envelope < tolerance")
    add(rows, "adapted_telescope_nontrivial", abs(telescope["nonzero_terminal_wick"]) > 1.0e-4, telescope["nonzero_terminal_wick"], "nonzero")
    add(rows, "independent_schur_completion", schur["maximum_residual"] < TOL, schur["maximum_residual"], TOL)
    add(rows, "independent_trace_bound", schur["minimum_trace_margin"] > -TOL, schur["minimum_trace_margin"], ">=0")
    add(rows, "indicator_formula", abs(adapted["raw"] - adapted["formula"]) < TOL, adapted, "raw=formula")
    add(rows, "indicator_centering_negative", adapted["raw"] < 0.0, adapted["raw"], "<0")
    add(rows, "indicator_resolver_negative", adapted["resolved"] < 0.0, adapted["resolved"], "<0")
    add(rows, "asymmetric_covariance_nonzero", abs(asymmetric["formula"]) > 1.0e-3, asymmetric, "nonzero")
    add(rows, "hardy_rearrangement", abs(hardy["left"] - hardy["rearranged"]) < TOL, hardy, "left=rearranged")
    add(rows, "hardy_geometric_bound", hardy["left"] <= hardy["infinite"] + TOL, hardy, "left<=infinite")
    add(rows, "independent_weighted_p_column_parts", abs(parts["left"] - parts["right"]) < TOL and abs(parts["left"] - parts["analytic_oracle"]) < TOL and abs(parts["right"] - parts["analytic_oracle"]) < TOL and parts["resolution_envelope"] < TOL and parts["analytic_oracle"] > 1.0e-6, parts, "nonzero test_weight/2 oracle; weighted left=right; coarse/fine envelope < tolerance")
    add(rows, "independent_fifth_moment", abs(parts["moment"] - float(moment_oracle)) < TOL, parts["moment"], str(moment_oracle))
    passed = all(row["pass"] for row in rows)
    payload = {
        "schema": "tect/a13-wick-doob-terminal-resolvent-independent/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {
            "seed": SEED,
            "cases": CASES,
            "gauss_hermite_orders": [GH_ORDER, GH_ORDER_FINE],
            "matrix_gauss_hermite_orders": [
                MATRIX_GH_ORDER,
                MATRIX_GH_ORDER_FINE,
            ],
            "fourier_grids": [FOURIER_GRID, FOURIER_GRID_FINE],
            "kappa": f"{KAPPA_NUMERATOR}/{KAPPA_DENOMINATOR}",
            "p_column_test_weight": P_COLUMN_TEST_WEIGHT,
            "tolerance": TOL,
        },
        "computed": {
            "matrix_wick_step": wick_step,
            "two_shell_telescope": telescope,
            "terminal_schur": schur,
            "adapted_indicator": adapted,
            "asymmetric_covariance": asymmetric,
            "dyadic_hardy": hardy,
            "p_column_parts": parts,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": (
            "This non-importing finite-dimensional audit checks the exact Wick--Doob, "
            "raw/Wick trace, terminal Schur, adapted-centering, Hardy, weighted p-p, "
            "and two-resolution identities. It does not prove the full QII-weighted "
            "production rational-frame/cross-square residual."
        ),
    }
    atomic_json(OUT, payload)
    if not passed:
        for row in rows:
            if not row["pass"]:
                print(f"FAIL {row['name']}: {row['actual']} expected {row['expected']}")
        return 1
    print(
        f"{RESULT_ID}-INDEPENDENT-PASS: {len(rows)}/{len(rows)}; "
        f"Wick residual={telescope['wick_terminal_residual']:.3e}; "
        f"resolved diagnostic={adapted['resolved']:.9g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
