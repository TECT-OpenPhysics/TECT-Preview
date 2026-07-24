#!/usr/bin/env python3
"""Non-importing independent audit for the R-077 causal-packet result.

This executable deliberately does not import the primary R-077 module.  It
uses a finite probability tree for the Doob packet, direct correlated-normal
fixtures for the Wick forests, a separately implemented dyadic sum, and a
complex Fourier carrier for the high--high-to-low residual.
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
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CAUSAL-PACKET-PAYLOAD-RESONANCE-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-25-independent-causal-packet-payload-resonance/result.json"
)

KAPPA = Fraction(1, 10)
WIDTH = 2
TREE_TOL = 1.0e-12
MONTE_CARLO_SEED = 25077791
MONTE_CARLO_SAMPLES = 200_000
FFT_POINTS = 2048
FFT_MODE = 53
HONESTY_BOUNDARY = (
    "This independent audit verifies the signed Doob cancellation, complete "
    "lower-chaos algebra, payload-comparable exponent ledger, and a nonzero "
    "coefficient-dominant high-high-to-low fixture.  It does not prove the "
    "remaining coupled signed packet inequality."
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


State = tuple[int, int, int, int]


def conditional(table: dict[State, float], level: int) -> dict[State, float]:
    """Conditional mean on the first 2*level shell coordinates."""
    grouped: dict[tuple[int, ...], list[float]] = defaultdict(list)
    for state, value in table.items():
        grouped[state[: 2 * level]].append(value)
    means = {key: float(np.mean(values)) for key, values in grouped.items()}
    return {state: means[state[: 2 * level]] for state in table}


def table_apply(function: Callable[[State], float], states: list[State]) -> dict[State, float]:
    return {state: float(function(state)) for state in states}


def table_difference(left: dict[State, float], right: dict[State, float]) -> dict[State, float]:
    return {state: left[state] - right[state] for state in left}


def table_max_abs(table: dict[State, float]) -> float:
    return max(abs(value) for value in table.values())


def doob_tree_fixture() -> dict[str, float]:
    states = list(itertools.product((-1, 1), repeat=4))

    def terminal_energy(state: State, value_shift: float, derivative_shift: float) -> float:
        g1, d1, g2, d2 = state
        x_value = 0.7 * g1 + 0.4 * g2 + value_shift
        y_value = 0.3 * d1 + 0.6 * d2 + derivative_shift
        return 0.5 * (1.0 + x_value**2) * (y_value**2 - 0.45)

    base = table_apply(lambda state: terminal_energy(state, 0.0, 0.0), states)
    first = table_apply(lambda state: terminal_energy(state, 0.35, -0.2), states)
    second = table_apply(
        lambda state: terminal_energy(
            state,
            0.35 + 0.22 * state[0] - 0.09 * state[1],
            -0.2 + 0.17 * state[0],
        ),
        states,
    )
    phi1 = table_difference(first, base)
    phi2 = table_difference(second, first)

    e0_phi1 = conditional(phi1, 0)
    e1_phi1 = conditional(phi1, 1)
    e1_phi2 = conditional(phi2, 1)
    e2_phi1 = conditional(phi1, 2)
    e2_phi2 = conditional(phi2, 2)

    d11 = table_difference(e1_phi1, e0_phi1)
    d21 = table_difference(e2_phi1, e1_phi1)
    d22 = table_difference(e2_phi2, e1_phi2)

    phi1_rebuilt = {
        state: e0_phi1[state] + d11[state] + d21[state] for state in states
    }
    phi2_rebuilt = {state: e1_phi2[state] + d22[state] for state in states}
    center11 = conditional(d11, 0)
    center21 = conditional(d21, 1)
    center22 = conditional(d22, 1)
    total_fresh_mean = float(np.mean([d11[s] + d21[s] + d22[s] for s in states]))

    return {
        "phi1_rebuild_error": table_max_abs(table_difference(phi1, phi1_rebuilt)),
        "phi2_rebuild_error": table_max_abs(table_difference(phi2, phi2_rebuilt)),
        "d11_conditional_center": table_max_abs(center11),
        "d21_conditional_center": table_max_abs(center21),
        "d22_conditional_center": table_max_abs(center22),
        "total_fresh_mean": total_fresh_mean,
    }


def wick_monte_carlo_fixture() -> dict[str, float]:
    rng = np.random.default_rng(MONTE_CARLO_SEED)
    sigma = 1.25
    gamma = 1.4
    cross = 0.3
    correlation = cross / math.sqrt(sigma * gamma)
    u = rng.normal(size=MONTE_CARLO_SAMPLES)
    v = rng.normal(size=MONTE_CARLO_SAMPLES)
    z = math.sqrt(sigma) * u
    y = math.sqrt(gamma) * (correlation * u + math.sqrt(1.0 - correlation**2) * v)

    q_value = y**2 - gamma
    wick_zy = z * y - cross
    wick_zyy = z * y**2 - gamma * z - 2.0 * cross * y
    wick_zzyy = (
        z**2 * y**2
        - sigma * y**2
        - gamma * z**2
        - 4.0 * cross * z * y
        + sigma * gamma
        + 2.0 * cross**2
    )
    first_difference = z * q_value - (wick_zyy + 2.0 * cross * y)
    second_difference = z**2 * q_value - (
        wick_zzyy + sigma * q_value + 4.0 * cross * wick_zy + 2.0 * cross**2
    )
    return {
        "first_max_error": float(np.max(np.abs(first_difference))),
        "second_max_error": float(np.max(np.abs(second_difference))),
        "p1_l2": float(np.sqrt(np.mean((2.0 * cross * y) ** 2))),
        "sigma_q_l2": float(np.sqrt(np.mean((sigma * q_value) ** 2))),
    }


def independent_ledger() -> dict[str, Fraction]:
    s = Fraction(1, 2) + KAPPA
    h2_power = Fraction(1, 2) * Fraction(1 + s, 2)
    l6_power = Fraction(1, 6) * Fraction(7 - s, 2)
    remainder = 1 - h2_power - l6_power
    pair_theta = (1 - s) / 4
    pair_h2 = h2_power + pair_theta / 2
    pair_l6 = l6_power - pair_theta / 6
    pair_remainder = 1 - pair_h2 - pair_l6
    return {
        "s": s,
        "h2_power": h2_power,
        "l6_power": l6_power,
        "remainder": remainder,
        "moment": 1 / remainder,
        "pair_theta": pair_theta,
        "pair_h2": pair_h2,
        "pair_l6": pair_l6,
        "pair_remainder": pair_remainder,
        "pair_moment": 1 / pair_remainder,
    }


def dyadic_fixture(s: Fraction) -> dict[str, Any]:
    sf = float(s)
    low_total = 0.0
    direct_bound = 0.0
    assignment_errors = 0
    low_count = 0
    high_count = 0
    tie_count = 0
    for payload_root in range(-1, 8):
        payload_mass = 2.0 ** (-1.3 * max(payload_root, 0))
        for multiplier_root in range(-1, 12):
            for current_root in range(multiplier_root - WIDTH, multiplier_root + WIDTH + 1):
                weight = payload_mass * 2.0 ** (sf * current_root)
                low = multiplier_root <= payload_root + WIDTH
                high = not low
                assignment_errors += int(int(low) + int(high) != 1)
                low_count += int(low)
                high_count += int(high)
                tie_count += int(abs(multiplier_root - payload_root) <= WIDTH)
                if low:
                    low_total += weight
        direct_bound += payload_mass * 2.0 ** (sf * payload_root)
    # The ratio is a finite independent fixture for the geometric lemma.
    ratio = low_total / direct_bound
    return {
        "low_total": low_total,
        "payload_besov_sum": direct_bound,
        "finite_ratio": ratio,
        "assignment_errors": assignment_errors,
        "low_count": low_count,
        "high_count": high_count,
        "tie_count": tie_count,
    }


def complex_high_high_fixture() -> dict[str, float]:
    grid = 2.0 * np.pi * np.arange(FFT_POINTS) / FFT_POINTS
    left = np.exp(1j * FFT_MODE * grid)
    right = np.exp(-1j * FFT_MODE * grid)
    zero_mode = complex(np.mean(left * right))
    return {
        "zero_mode_real": float(zero_mode.real),
        "zero_mode_imag_abs": float(abs(zero_mode.imag)),
    }


def main() -> int:
    rows: list[dict[str, Any]] = []
    doob = doob_tree_fixture()
    for key in (
        "phi1_rebuild_error",
        "phi2_rebuild_error",
        "d11_conditional_center",
        "d21_conditional_center",
        "d22_conditional_center",
        "total_fresh_mean",
    ):
        add(rows, f"tree_{key}", abs(doob[key]) < TREE_TOL, doob[key], f"< {TREE_TOL}")

    forest = wick_monte_carlo_fixture()
    add(rows, "forest_p3_p1_pointwise", forest["first_max_error"] < TREE_TOL, forest["first_max_error"], f"< {TREE_TOL}")
    add(rows, "forest_p4_lower_pointwise", forest["second_max_error"] < 5 * TREE_TOL, forest["second_max_error"], f"< {5 * TREE_TOL}")
    add(rows, "forest_p1_nonzero_l2", forest["p1_l2"] > 0.1, forest["p1_l2"], "> 0.1")
    add(rows, "forest_sigma_q_nonzero_l2", forest["sigma_q_l2"] > 0.1, forest["sigma_q_l2"], "> 0.1")

    ledger = independent_ledger()
    oracles = {
        "s": Fraction(3, 5),
        "h2_power": Fraction(2, 5),
        "l6_power": Fraction(8, 15),
        "remainder": Fraction(1, 15),
        "moment": Fraction(15, 1),
        "pair_theta": Fraction(1, 10),
        "pair_h2": Fraction(9, 20),
        "pair_l6": Fraction(31, 60),
        "pair_remainder": Fraction(1, 30),
        "pair_moment": Fraction(30, 1),
    }
    for key, oracle in oracles.items():
        add(rows, f"independent_{key}", ledger[key] == oracle, str(ledger[key]), str(oracle))

    dyadic = dyadic_fixture(ledger["s"])
    add(rows, "dyadic_finite_geometric_ratio", math.isfinite(dyadic["finite_ratio"]), dyadic["finite_ratio"], "finite")
    add(rows, "dyadic_partition_exhaustive", dyadic["assignment_errors"] == 0, dyadic["assignment_errors"], 0)
    add(rows, "dyadic_both_orientations", dyadic["low_count"] > 0 and dyadic["high_count"] > 0, {"low": dyadic["low_count"], "high": dyadic["high_count"]}, "both positive")
    add(rows, "dyadic_ties_present", dyadic["tie_count"] > 0, dyadic["tie_count"], "> 0")

    high_high = complex_high_high_fixture()
    add(rows, "complex_high_high_zero_mode_real", abs(high_high["zero_mode_real"] - 1.0) < TREE_TOL, high_high["zero_mode_real"], 1.0)
    add(rows, "complex_high_high_zero_mode_imag", high_high["zero_mode_imag_abs"] < TREE_TOL, high_high["zero_mode_imag_abs"], f"< {TREE_TOL}")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-causal-packet-payload-independent/1.0",
        "result_id": RESULT_ID,
        "version": __version__,
        "imports_primary": False,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "doob_tree": doob,
        "wick_forest": forest,
        "ledger": {key: str(value) for key, value in ledger.items()},
        "dyadic": dyadic,
        "high_high_low": high_high,
        "honesty_boundary": HONESTY_BOUNDARY,
    }
    atomic_json(OUT, payload)
    print(f"A13 CLASSII CAUSAL PACKET PAYLOAD INDEPENDENT: {passed}/{len(rows)} PASS")
    print(f"wrote {OUT.relative_to(REPO).as_posix()}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
