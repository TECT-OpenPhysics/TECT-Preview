#!/usr/bin/env python3
"""Primary executable audit for the R-077 causal-packet reduction.

The program independently checks a finite Gaussian backward-heat/Doob
fixture, the complete P3/P1 and P4/lower-chaos Wick identities, the
payload-comparable Littlewood--Paley exponent ledger, an exhaustive two-way
block partition, the surviving high--high-to-low residual, and the optional
pair-high refinement.  It does not assert the remaining coefficient-dominant
signed packet bound, controlled-shell one-use, or Nelson synthesis.
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
RESULT_ID = "A13-CLASSII-CAUSAL-PACKET-PAYLOAD-RESONANCE-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-25-primary-causal-packet-payload-resonance/result.json"
)

# Declared inputs and test thresholds.  Every reported exponent is derived.
KAPPA = Fraction(1, 10)
RESONANCE_WIDTH = 2
RANDOM_SEED = 25077701
AMGM_CASES = 128
AMGM_TOL = 1.0e-12
FFT_POINTS = 4096
FFT_MODE = 64
HONESTY_BOUNDARY = (
    "The complete fresh-Gaussian Doob packet has zero signed expectation and "
    "the payload-comparable shifted-resonance block is paid once with the "
    "existing fifteenth moment.  The coefficient-dominant high-high-to-low "
    "packet, controlled-shell one-use, and q=10/9 Nelson synthesis remain open."
)


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


def gaussian_moment(power: int) -> sp.Integer:
    if power % 2:
        return sp.Integer(0)
    return sp.Integer(math.factorial(power) // (2 ** (power // 2) * math.factorial(power // 2)))


def gaussian_average(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    """Average a polynomial over independent standard normal variables."""
    result = sp.expand(expression)
    for variable in variables:
        polynomial = sp.Poly(result, variable)
        result = sp.expand(
            sum(coefficient * gaussian_moment(power[0]) for power, coefficient in polynomial.terms())
        )
    return sp.simplify(result)


def backward_heat_doob_fixture() -> dict[str, Any]:
    """Exact two-shell polynomial audit of the complete Doob packet."""
    g1, g2, d1, d2 = sp.symbols("g1 g2 d1 d2", real=True)
    beta = sp.Rational(3, 7)
    value_shift = sp.Rational(1, 3)
    derivative_shift = -sp.Rational(1, 4)
    adapted_value = sp.Rational(2, 5) * g1
    adapted_derivative = -sp.Rational(1, 5) * g1

    def energy(level: int, x_value: sp.Expr, y_value: sp.Expr) -> sp.Expr:
        future_value_variance = 2 - level
        past_derivative_variance = level
        coefficient = x_value**2 + future_value_variance + beta
        return sp.expand(sp.Rational(1, 2) * coefficient * (y_value**2 - past_derivative_variance))

    x_terminal = g1 + g2
    y_terminal = d1 + d2
    a0, c0 = sp.Integer(0), sp.Integer(0)
    a1, c1 = value_shift, derivative_shift
    a2, c2 = value_shift + adapted_value, derivative_shift + adapted_derivative

    phi1 = sp.expand(energy(2, x_terminal + a1, y_terminal + c1) - energy(2, x_terminal + a0, y_terminal + c0))
    phi2 = sp.expand(energy(2, x_terminal + a2, y_terminal + c2) - energy(2, x_terminal + a1, y_terminal + c1))

    e0_phi1 = gaussian_average(phi1, (g1, d1, g2, d2))
    e1_phi1 = gaussian_average(phi1, (g2, d2))
    e1_phi2 = gaussian_average(phi2, (g2, d2))

    fresh_11 = sp.expand(e1_phi1 - e0_phi1)
    fresh_21 = sp.expand(phi1 - e1_phi1)
    fresh_22 = sp.expand(phi2 - e1_phi2)

    baseline1 = sp.expand(energy(0, a1, c1) - energy(0, a0, c0))
    baseline2 = sp.expand(energy(1, g1 + a2, d1 + c2) - energy(1, g1 + a1, d1 + c1))

    return {
        "phi1_decomposition": sp.simplify(phi1 - baseline1 - fresh_11 - fresh_21),
        "phi2_decomposition": sp.simplify(phi2 - baseline2 - fresh_22),
        "fresh_11_center": gaussian_average(fresh_11, (g1, d1)),
        "fresh_21_center": gaussian_average(fresh_21, (g2, d2)),
        "fresh_22_center": gaussian_average(fresh_22, (g2, d2)),
        "baseline1_heat_error": sp.simplify(e0_phi1 - baseline1),
        "baseline2_heat_error": sp.simplify(e1_phi2 - baseline2),
        "total_fresh_expectation": gaussian_average(fresh_11 + fresh_21 + fresh_22, (g1, d1, g2, d2)),
        "total_tower_error": sp.simplify(
            gaussian_average(phi1 + phi2 - baseline1 - baseline2, (g1, d1, g2, d2))
        ),
    }


def wick_forest_fixture() -> dict[str, Any]:
    """Check the complete scalar P3/P1 and P4/lower-chaos identities."""
    z, y, sigma, gamma, cross = sp.symbols("z y sigma gamma cross", real=True)
    q_value = y**2 - gamma
    wick_zy = z * y - cross
    wick_zyy = z * y**2 - gamma * z - 2 * cross * y
    wick_zzyy = (
        z**2 * y**2
        - sigma * y**2
        - gamma * z**2
        - 4 * cross * z * y
        + sigma * gamma
        + 2 * cross**2
    )
    first_error = sp.expand(z * q_value - (wick_zyy + 2 * cross * y))
    second_error = sp.expand(
        z**2 * q_value
        - (wick_zzyy + sigma * q_value + 4 * cross * wick_zy + 2 * cross**2)
    )
    test_values = {sigma: sp.Rational(5, 4), gamma: sp.Rational(7, 5), cross: sp.Rational(2, 7)}
    p1 = sp.expand(2 * cross * y).subs(test_values)
    sigma_q = sp.expand(sigma * q_value).subs(test_values)
    return {
        "p3_p1_error": first_error,
        "p4_lower_error": second_error,
        "p1_polynomial": str(p1),
        "sigma_q_polynomial": str(sigma_q),
        "p1_nonzero": p1 != 0,
        "sigma_q_nonzero": sigma_q != 0,
    }


def exponent_ledger() -> dict[str, Any]:
    s = Fraction(1, 2) + KAPPA
    x_power = (1 + s) / 4
    y_power = (7 - s) / 12
    slack = 1 - x_power - y_power
    pair_theta = (1 - s) / 4
    pair_x = (3 + s) / 8
    pair_y = (13 - s) / 24
    pair_slack = 1 - pair_x - pair_y
    return {
        "s": s,
        "x_power": x_power,
        "y_power": y_power,
        "slack": slack,
        "moment": 1 / slack,
        "eta_loss": x_power / slack,
        "zeta_loss": y_power / slack,
        "pair_theta": pair_theta,
        "pair_x_power": pair_x,
        "pair_y_power": pair_y,
        "pair_slack": pair_slack,
        "pair_moment": 1 / pair_slack,
        "pair_eta_loss": pair_x / pair_slack,
        "pair_zeta_loss": pair_y / pair_slack,
        "pair_floor_decay": pair_theta / pair_slack,
    }


def geometric_and_partition_fixture(s: Fraction) -> dict[str, Any]:
    sf = float(s)
    width = RESONANCE_WIDTH
    offset_sum = sum(2.0 ** (sf * offset) for offset in range(-width, width + 1))
    geometric_constant = 2.0 ** (sf * width) * offset_sum / (1.0 - 2.0 ** (-sf))
    ratios: list[float] = []
    for payload_root in range(0, 21):
        total = 0.0
        for multiplier_root in range(-1, payload_root + width + 1):
            for current_root in range(multiplier_root - width, multiplier_root + width + 1):
                total += 2.0 ** (sf * current_root)
        ratios.append(total / 2.0 ** (sf * payload_root))

    tuples = []
    tie_count = 0
    low_count = 0
    high_count = 0
    assignment_errors = 0
    for payload_root in range(-1, 6):
        for multiplier_root in range(-1, 9):
            for current_root in range(multiplier_root - width, multiplier_root + width + 1):
                low = multiplier_root <= payload_root + width
                high = multiplier_root > payload_root + width
                assignment_errors += int((int(low) + int(high)) != 1)
                tie_count += int(abs(multiplier_root - payload_root) <= width)
                low_count += int(low)
                high_count += int(high)
                tuples.append((payload_root, multiplier_root, current_root))
    return {
        "max_geometric_ratio": max(ratios),
        "geometric_constant": geometric_constant,
        "tuple_count": len(tuples),
        "assignment_errors": assignment_errors,
        "low_count": low_count,
        "high_count": high_count,
        "tie_count": tie_count,
    }


def high_high_low_fixture() -> dict[str, Any]:
    grid = 2.0 * np.pi * np.arange(FFT_POINTS) / FFT_POINTS
    high_left = np.cos(FFT_MODE * grid)
    high_right = np.cos(FFT_MODE * grid)
    product = high_left * high_right
    zero_mode = float(np.mean(product))
    expected = Fraction(1, 2)
    return {
        "points": FFT_POINTS,
        "mode": FFT_MODE,
        "zero_mode": zero_mode,
        "expected_zero_mode": float(expected),
        "nonzero": abs(zero_mode) > 0.25,
    }


def weighted_amgm_fixture(ledger: dict[str, Any]) -> float:
    rng = np.random.default_rng(RANDOM_SEED)
    a = float(ledger["x_power"])
    b = float(ledger["y_power"])
    c = float(ledger["slack"])
    minimum_gap = math.inf
    for _ in range(AMGM_CASES):
        x_value, y_value, random_norm, eta, zeta = np.exp(rng.uniform(-5.0, 5.0, size=5))
        left = random_norm * x_value**a * y_value**b
        remainder = c * (
            random_norm * (a / eta) ** a * (b / zeta) ** b
        ) ** (1.0 / c)
        right = eta * x_value + zeta * y_value + remainder
        minimum_gap = min(minimum_gap, right - left)
    return minimum_gap


def main() -> int:
    rows: list[dict[str, Any]] = []
    doob = backward_heat_doob_fixture()
    zero = sp.Integer(0)
    add(rows, "doob_phi1_decomposition", doob["phi1_decomposition"] == zero, str(doob["phi1_decomposition"]), "0")
    add(rows, "doob_phi2_decomposition", doob["phi2_decomposition"] == zero, str(doob["phi2_decomposition"]), "0")
    add(rows, "doob_first_shell_center", doob["fresh_11_center"] == zero, str(doob["fresh_11_center"]), "0")
    add(rows, "doob_future_phi1_center", doob["fresh_21_center"] == zero, str(doob["fresh_21_center"]), "0")
    add(rows, "doob_future_phi2_center", doob["fresh_22_center"] == zero, str(doob["fresh_22_center"]), "0")
    add(rows, "doob_baseline1_heat_identity", doob["baseline1_heat_error"] == zero, str(doob["baseline1_heat_error"]), "0")
    add(rows, "doob_baseline2_heat_identity", doob["baseline2_heat_error"] == zero, str(doob["baseline2_heat_error"]), "0")
    add(rows, "doob_total_fresh_expectation", doob["total_fresh_expectation"] == zero, str(doob["total_fresh_expectation"]), "0")
    add(rows, "doob_total_tower_identity", doob["total_tower_error"] == zero, str(doob["total_tower_error"]), "0")

    forest = wick_forest_fixture()
    add(rows, "forest_p3_p1_identity", forest["p3_p1_error"] == zero, str(forest["p3_p1_error"]), "0")
    add(rows, "forest_p4_lower_identity", forest["p4_lower_error"] == zero, str(forest["p4_lower_error"]), "0")
    add(rows, "forest_p1_retained", forest["p1_nonzero"], forest["p1_polynomial"], "nonzero")
    add(rows, "forest_sigma_q_retained", forest["sigma_q_nonzero"], forest["sigma_q_polynomial"], "nonzero")

    ledger = exponent_ledger()
    exponent_oracles = {
        "s": Fraction(3, 5),
        "x_power": Fraction(2, 5),
        "y_power": Fraction(8, 15),
        "slack": Fraction(1, 15),
        "moment": Fraction(15, 1),
        "eta_loss": Fraction(6, 1),
        "zeta_loss": Fraction(8, 1),
        "pair_theta": Fraction(1, 10),
        "pair_x_power": Fraction(9, 20),
        "pair_y_power": Fraction(31, 60),
        "pair_slack": Fraction(1, 30),
        "pair_moment": Fraction(30, 1),
        "pair_eta_loss": Fraction(27, 2),
        "pair_zeta_loss": Fraction(31, 2),
        "pair_floor_decay": Fraction(3, 1),
    }
    for key, oracle in exponent_oracles.items():
        add(rows, f"ledger_{key}", ledger[key] == oracle, str(ledger[key]), str(oracle))

    geometry = geometric_and_partition_fixture(ledger["s"])
    add(
        rows,
        "geometric_resonance_sum",
        geometry["max_geometric_ratio"] <= geometry["geometric_constant"] + AMGM_TOL,
        geometry["max_geometric_ratio"],
        f"<= {geometry['geometric_constant']}",
    )
    add(rows, "block_partition_exhaustive", geometry["assignment_errors"] == 0, geometry["assignment_errors"], 0)
    add(
        rows,
        "block_partition_both_nonempty",
        geometry["low_count"] > 0 and geometry["high_count"] > 0,
        {"low": geometry["low_count"], "high": geometry["high_count"]},
        "both positive",
    )
    add(rows, "block_ties_assigned", geometry["tie_count"] > 0, geometry["tie_count"], ">0")

    high_high = high_high_low_fixture()
    add(
        rows,
        "high_high_to_zero_mode",
        abs(high_high["zero_mode"] - high_high["expected_zero_mode"]) < AMGM_TOL,
        high_high["zero_mode"],
        high_high["expected_zero_mode"],
    )
    add(rows, "coefficient_dominant_residual_nonzero", high_high["nonzero"], high_high["zero_mode"], "nonzero")

    minimum_gap = weighted_amgm_fixture(ledger)
    add(rows, "weighted_amgm_random_fixture", minimum_gap >= -AMGM_TOL, minimum_gap, f">= {-AMGM_TOL}")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-causal-packet-payload-primary/1.0",
        "result_id": RESULT_ID,
        "version": __version__,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "doob": {key: str(value) for key, value in doob.items()},
        "forest": {
            key: (str(value) if isinstance(value, sp.Basic) else value)
            for key, value in forest.items()
        },
        "ledger": {key: str(value) for key, value in ledger.items()},
        "geometric_partition": geometry,
        "high_high_low": high_high,
        "weighted_amgm_min_gap": minimum_gap,
        "honesty_boundary": HONESTY_BOUNDARY,
    }
    atomic_json(OUT, payload)
    print(f"A13 CLASSII CAUSAL PACKET PAYLOAD PRIMARY: {passed}/{len(rows)} PASS")
    print(f"wrote {OUT.relative_to(REPO).as_posix()}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
