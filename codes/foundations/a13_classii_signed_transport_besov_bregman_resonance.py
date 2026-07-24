#!/usr/bin/env python3
"""Primary audit for the R-076 signed-transport resonance reduction.

The executable checks the nonduplicating endpoint ledger, the sharpened
Besov/Young exponent calculation, an exact affine-current Bregman witness,
the centered selector diagnostic, the path square/curvature split, and the
separated shifted-multiplier obstruction.  It does not assert the missing
paired adapted shifted-enhancement estimate, controlled-shell one-use, or
the q=10/9 Nelson theorem.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-25"

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp

import a13_classii_phase_kernel_causal_diagonal_reduction as r072

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SIGNED-TRANSPORT-BESOV-BREGMAN-RESONANCE-REDUCTION"
MANIFEST = REPO / "claims" / CLAIM / "classii_signed_transport_besov_bregman_resonance_manifest.json"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-24-primary-signed-transport-besov-bregman-resonance/result.json"

# Audited parameter and regression-fixture inputs, not derived results.
KAPPA = Fraction(1, 10)
RANDOM_SEED = 24077601
RANDOM_CASES = 48
SECOND_DIFFERENCE_STEP = 2.0e-4
LEDGER_TOL = 2.0e-10
FORMULA_TOL = 2.0e-9
QUADRATURE_ORDER = 256
MULTIPLIER_DELTA = 1.0e-3
MULTIPLIER_TIME = 0.5
MULTIPLIER_MODES = (8, 16, 32, 64)
MULTIPLIER_POINTS = 32768
HONESTY_BOUNDARY = (
    "The sharpened Besov estimate closes the A-independent cubic one-form "
    "branch and both nonresonant paraproduct branches. The paired adapted "
    "shifted high-high resonance, complete R-063 lower-chaos/Wick endpoint, "
    "controlled-shell one-use theorem, and q=10/9 Nelson bound remain open."
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


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
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def raw_energy(z: np.ndarray, derivative: np.ndarray, q_matrix: np.ndarray, floor: float) -> float:
    return 0.5 * sum(
        float((frame.T @ derivative) @ q_matrix @ (frame.T @ derivative))
        for frame in r072.frame_jet(z, floor)[0]
    )


def production_matrix(frames: list[np.ndarray], q_matrix: np.ndarray) -> np.ndarray:
    return sum((frame @ q_matrix @ frame.T for frame in frames), start=np.zeros((6, 6)))


def q_inner(left: np.ndarray, q_matrix: np.ndarray, right: np.ndarray) -> float:
    return float(left @ q_matrix @ right)


def signed_endpoint_ledger(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    """Check the exact Xi regrouping and its direct Wick-Bregman value."""
    rng = np.random.default_rng(RANDOM_SEED)
    max_regroup_error = 0.0
    max_direct_error = 0.0
    for _ in range(RANDOM_CASES):
        z = rng.normal(size=6)
        a = 0.35 * rng.normal(size=6)
        g = rng.normal(size=6)
        c_value = 0.35 * rng.normal(size=6)
        gamma_seed = 0.2 * rng.normal(size=(6, 6))
        gamma = gamma_seed @ gamma_seed.T

        frames0, directional = r072.frame_jet(z, floor, a)
        assert directional is not None
        frames1, _ = r072.frame_jet(z + a, floor)
        plus, _ = r072.frame_jet(z + SECOND_DIFFERENCE_STEP * a, floor)
        minus, _ = r072.frame_jet(z - SECOND_DIFFERENCE_STEP * a, floor)

        b0 = production_matrix(frames0, q_matrix)
        b1 = production_matrix(frames1, q_matrix)
        db = sum(
            (
                dframe @ q_matrix @ frame.T
                + frame @ q_matrix @ dframe.T
                for frame, dframe in zip(frames0, directional)
            ),
            start=np.zeros((6, 6)),
        )
        coefficient_remainder = b1 - b0 - db

        original_xi = 0.5 * float(np.sum(coefficient_remainder * (np.outer(g, g) - gamma)))
        regrouped_xi = -0.5 * float(np.sum(coefficient_remainder * gamma))
        principal_c = 0.0
        linear_c = 0.0
        for frame0, frame1, dframe, frame_plus, frame_minus in zip(
            frames0, frames1, directional, plus, minus
        ):
            e_value = frame1 - frame0 - dframe
            e2 = (frame_plus - 2.0 * frame0 + frame_minus) / (2.0 * SECOND_DIFFERENCE_STEP**2)
            e3 = e_value - e2
            w = frame0.T @ g
            delta_w = (dframe + e_value).T @ g
            control_current = frame1.T @ c_value

            original_xi += (
                q_inner(w, q_matrix, e3.T @ c_value)
                + q_inner(delta_w, q_matrix, control_current)
                + 0.5 * q_inner(control_current, q_matrix, control_current)
            )
            regrouped_xi += (
                q_inner(w, q_matrix, e2.T @ g)
                + q_inner(w, q_matrix, e3.T @ (g + c_value))
                + 0.5 * q_inner(delta_w + control_current, q_matrix, delta_w + control_current)
            )
            principal_c += q_inner(w, q_matrix, e2.T @ c_value)
            linear_c += q_inner(w, q_matrix, dframe.T @ c_value)

        max_regroup_error = max(max_regroup_error, abs(original_xi - regrouped_xi))

        direct_raw = raw_energy(z + a, g + c_value, q_matrix, floor) - raw_energy(z, g, q_matrix, floor)
        first_raw = 0.0
        for frame0, dframe in zip(frames0, directional):
            w = frame0.T @ g
            first_raw += q_inner(w, q_matrix, dframe.T @ g + frame0.T @ c_value)
        direct_wick_remainder = (
            direct_raw
            - first_raw
            - 0.5 * float(np.sum(coefficient_remainder * gamma))
        )
        ledger_wick_remainder = linear_c + principal_c + regrouped_xi
        max_direct_error = max(max_direct_error, abs(direct_wick_remainder - ledger_wick_remainder))

    return {
        "random_cases": RANDOM_CASES,
        "max_regroup_error": max_regroup_error,
        "max_direct_wick_error": max_direct_error,
    }


def besov_budget() -> dict[str, Any]:
    """Derive the improved payload and weighted-Young exponents."""
    s = Fraction(1, 2) + KAPPA
    a_power = (1 + s) / 4
    b_power = (7 - s) / 12
    slack = 1 - a_power - b_power
    moment = 1 / slack
    eta_power = a_power / slack
    zeta_power = b_power / slack

    # Direct numerical checks of the exact weighted AM--GM normalization.
    rng = np.random.default_rng(RANDOM_SEED + 1)
    worst_gap = math.inf
    af = float(a_power)
    bf = float(b_power)
    cf = float(slack)
    for _ in range(128):
        x_value, y_value, r_value, eta, zeta = np.exp(rng.uniform(-4.0, 4.0, size=5))
        left = r_value * x_value**af * y_value**bf
        remainder = cf * (
            r_value * af**af * bf**bf * eta ** (-af) * zeta ** (-bf)
        ) ** (1.0 / cf)
        right = eta * x_value + zeta * y_value + remainder
        worst_gap = min(worst_gap, right - left)

    return {
        "s": str(s),
        "x_power": str(a_power),
        "y_power": str(b_power),
        "young_slack": str(slack),
        "required_moment": str(moment),
        "eta_loss_power": str(eta_power),
        "zeta_loss_power": str(zeta_power),
        "exponent_sum": str(a_power + b_power),
        "weighted_amgm_min_gap": worst_gap,
    }


def bregman_fixture(q_matrix: np.ndarray, floor: float, denominator_p: float) -> dict[str, Any]:
    """Evaluate the exact affine-current nonconvexity and selector diagnostic."""
    z = np.asarray([1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    a = np.asarray([1.0, 0.0, -1.0, 0.0, 0.0, 0.0])
    g = np.asarray([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    c_value = np.zeros(6)
    frames0, directional = r072.frame_jet(z, floor, a)
    frames1, _ = r072.frame_jet(z + a, floor)
    assert directional is not None

    square = 0.0
    curvature = 0.0
    base_energy = raw_energy(z, g, q_matrix, floor)
    for frame0, frame1, dframe in zip(frames0, frames1, directional):
        w0 = frame0.T @ g
        w1 = frame1.T @ (g + c_value)
        delta = w1 - w0
        linear = dframe.T @ g + frame0.T @ c_value
        square += 0.5 * q_inner(delta, q_matrix, delta)
        curvature += q_inner(w0, q_matrix, delta - linear)
    remainder = square + curvature
    d_value = float(z @ z + floor)
    q22 = float(q_matrix[1, 1])
    expected_square = 2.0 * q22 / d_value**2
    expected_curvature = -8.0 * q22 / d_value**2
    expected_remainder = -6.0 * q22 / d_value**2
    pinned_formula = -9.0 / (160.0 * denominator_p * (2.0 + floor) ** 2)

    family: list[dict[str, float]] = []
    for endpoint_amplitude in (0.0, 1.0, 2.0, 5.0, 10.0):
        direction = np.asarray([endpoint_amplitude - 1.0, 0.0, -1.0, 0.0, 0.0, 0.0])
        _, family_directional = r072.frame_jet(z, floor, direction)
        assert family_directional is not None
        first = sum(
            q_inner(frame.T @ g, q_matrix, dframe.T @ g)
            for frame, dframe in zip(frames0, family_directional)
        )
        endpoint = np.asarray([endpoint_amplitude, 0.0, 0.0, 0.0, 0.0, 0.0])
        direct = raw_energy(endpoint, g, q_matrix, floor) - base_energy - first
        formula = -3.0 * (
            4.0 * endpoint_amplitude * (floor + 1.0) - 5.0 * floor - 2.0
        ) / (160.0 * denominator_p * (floor + 2.0) ** 3)
        family.append(
            {
                "endpoint_amplitude": endpoint_amplitude,
                "direct": direct,
                "formula": formula,
                "ratio_to_base": direct / base_energy,
            }
        )

    threshold = 1.0
    phi = math.exp(-0.5 * threshold**2) / math.sqrt(2.0 * math.pi)
    centered_tail_moment = 2.0 * threshold * phi
    centered_selector_expectation = expected_remainder * centered_tail_moment
    return {
        "base_energy": base_energy,
        "square": square,
        "curvature": curvature,
        "remainder": remainder,
        "expected_square": expected_square,
        "expected_curvature": expected_curvature,
        "expected_remainder": expected_remainder,
        "pinned_formula": pinned_formula,
        "curvature_to_square": curvature / square,
        "remainder_to_base": remainder / base_energy,
        "endpoint_family": family,
        "selector_threshold": threshold,
        "centered_tail_moment": centered_tail_moment,
        "centered_selector_expectation": centered_selector_expectation,
    }


def path_square_curvature() -> dict[str, Any]:
    """Independently integrate the exact zero-floor fixture path."""
    t = sp.symbols("t", real=True)
    current = (t - 1) * (t + 1) ** 2 / (1 + t**2)
    positive_integrand = (1 - t) * sp.diff(current, t) ** 2
    curvature_integrand = (1 - t) * current * sp.diff(current, t, 2)
    positive_exact = sp.simplify(sp.integrate(positive_integrand, (t, 0, 1)))
    curvature_exact = sp.simplify(sp.integrate(curvature_integrand, (t, 0, 1)))

    nodes, weights = np.polynomial.legendre.leggauss(QUADRATURE_ORDER)
    points = 0.5 * (nodes + 1.0)
    scaled_weights = 0.5 * weights
    positive_function = sp.lambdify(t, positive_integrand, "numpy")
    curvature_function = sp.lambdify(t, curvature_integrand, "numpy")
    positive_quad = float(np.dot(scaled_weights, positive_function(points)))
    curvature_quad = float(np.dot(scaled_weights, curvature_function(points)))
    return {
        "positive_exact": str(positive_exact),
        "curvature_exact": str(curvature_exact),
        "total_exact": str(sp.simplify(positive_exact + curvature_exact)),
        "positive_numeric": positive_quad,
        "curvature_numeric": curvature_quad,
        "total_numeric": positive_quad + curvature_quad,
    }


def shifted_multiplier_obstruction() -> dict[str, Any]:
    """Check the exact radial fourth derivative and zero-mode leakage."""
    radius, floor_symbol = sp.symbols("radius floor", positive=True)
    radial_frame = 2 * floor_symbol * radius / (radius**2 + floor_symbol)
    third = sp.diff(radial_frame, radius, 3)
    fourth = sp.diff(radial_frame, radius, 4)
    fourth_at_floor = sp.simplify(fourth.subs(radius, sp.sqrt(floor_symbol)))
    third_function = sp.lambdify((radius, floor_symbol), third, "numpy")

    s_value = float(Fraction(1, 2) + KAPPA)
    points = 2.0 * math.pi * np.arange(MULTIPLIER_POINTS) / MULTIPLIER_POINTS
    leakages: list[float] = []
    h2_norms: list[float] = []
    for mode in MULTIPLIER_MODES:
        wave = np.cos(mode * points)
        shifted = third_function(1.0 + MULTIPLIER_TIME * MULTIPLIER_DELTA * wave, 1.0)
        base = float(third_function(1.0, 1.0))
        rough_mode = mode**s_value * wave
        leakages.append(float(abs(np.mean(rough_mode * (shifted - base)))))
        h2_norms.append(
            MULTIPLIER_DELTA
            * math.sqrt((1.0 + mode**2 + mode**4) / 2.0)
        )
    leakage_ratios = [right / left for left, right in zip(leakages[:-1], leakages[1:])]
    expected_ratio = 2.0**s_value
    log_slope_h2 = math.log(leakages[-1] / leakages[0]) / math.log(h2_norms[-1] / h2_norms[0])
    separated_budget_sum = Fraction(5, 6) + (Fraction(1, 6) + Fraction(1, 4)) * (Fraction(1, 2) + KAPPA)
    return {
        "radial_frame": str(radial_frame),
        "fourth_derivative_at_sqrt_floor": str(fourth_at_floor),
        "modes": list(MULTIPLIER_MODES),
        "zero_mode_leakages": leakages,
        "leakage_ratios": leakage_ratios,
        "expected_doubling_ratio": expected_ratio,
        "h2_norms": h2_norms,
        "leakage_vs_h2_log_slope": log_slope_h2,
        "expected_h2_power": s_value / 2.0,
        "separated_budget_exponent_sum": str(separated_budget_sum),
    }


def run() -> int:
    parameters, q_matrix, floor = r072.production_data()
    denominator_p = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    ledger = signed_endpoint_ledger(q_matrix, floor)
    budget = besov_budget()
    bregman = bregman_fixture(q_matrix, floor, denominator_p)
    path = path_square_curvature()
    multiplier = shifted_multiplier_obstruction()

    rows: list[dict[str, Any]] = []
    add(rows, "signed_Xi_regrouping", ledger["max_regroup_error"] < LEDGER_TOL, ledger["max_regroup_error"], f"<{LEDGER_TOL}")
    add(rows, "signed_Xi_matches_direct_Wick_Bregman", ledger["max_direct_wick_error"] < LEDGER_TOL, ledger["max_direct_wick_error"], f"<{LEDGER_TOL}")
    add(rows, "besov_s", budget["s"] == "3/5", budget["s"], "3/5")
    add(rows, "besov_X_power", budget["x_power"] == "2/5", budget["x_power"], "2/5")
    add(rows, "besov_Y_power", budget["y_power"] == "8/15", budget["y_power"], "8/15")
    add(rows, "besov_positive_slack", budget["young_slack"] == "1/15", budget["young_slack"], "1/15")
    add(rows, "besov_required_moment", budget["required_moment"] == "15", budget["required_moment"], "15")
    add(rows, "besov_eta_loss", budget["eta_loss_power"] == "6", budget["eta_loss_power"], "6")
    add(rows, "besov_zeta_loss", budget["zeta_loss_power"] == "8", budget["zeta_loss_power"], "8")
    add(rows, "weighted_AMGM_samples", budget["weighted_amgm_min_gap"] >= -1.0e-10, budget["weighted_amgm_min_gap"], ">=-1e-10")
    add(rows, "bregman_square_formula", abs(bregman["square"] - bregman["expected_square"]) < FORMULA_TOL, bregman["square"], bregman["expected_square"])
    add(rows, "bregman_curvature_formula", abs(bregman["curvature"] - bregman["expected_curvature"]) < FORMULA_TOL, bregman["curvature"], bregman["expected_curvature"])
    add(rows, "bregman_remainder_formula", abs(bregman["remainder"] - bregman["pinned_formula"]) < FORMULA_TOL, bregman["remainder"], bregman["pinned_formula"])
    add(rows, "bregman_curvature_overwhelms_square", bregman["curvature_to_square"] < -1.0 and bregman["remainder"] < 0.0, [bregman["curvature_to_square"], bregman["remainder"]], "ratio<-1 and remainder<0")
    add(rows, "bregman_ratio_minus_three", abs(bregman["remainder_to_base"] + 3.0) < FORMULA_TOL, bregman["remainder_to_base"], -3.0)
    add(rows, "bregman_endpoint_family", max(abs(item["direct"] - item["formula"]) for item in bregman["endpoint_family"]) < FORMULA_TOL, bregman["endpoint_family"], "all direct=formula")
    add(rows, "centered_selector_negative", bregman["centered_selector_expectation"] < 0.0, bregman["centered_selector_expectation"], "<0")
    add(rows, "path_positive_formula", abs(path["positive_numeric"] - (3.5 - math.log(4.0) - math.pi / 2.0)) < 1.0e-12, path["positive_numeric"], "7/2-log(4)-pi/2")
    add(rows, "path_curvature_formula", abs(path["curvature_numeric"] - (-5.0 + math.log(4.0) + math.pi / 2.0)) < 1.0e-12, path["curvature_numeric"], "-5+log(4)+pi/2")
    add(rows, "path_total_negative", abs(path["total_numeric"] + 1.5) < 1.0e-12, path["total_numeric"], -1.5)
    add(rows, "radial_fourth_derivative", multiplier["fourth_derivative_at_sqrt_floor"] == "-6/floor**(3/2)", multiplier["fourth_derivative_at_sqrt_floor"], "-6/floor**(3/2)")
    add(rows, "shifted_multiplier_zero_mode_growth", max(abs(value - multiplier["expected_doubling_ratio"]) for value in multiplier["leakage_ratios"]) < 2.0e-6, multiplier["leakage_ratios"], multiplier["expected_doubling_ratio"])
    add(rows, "shifted_multiplier_H2_power", abs(multiplier["leakage_vs_h2_log_slope"] - multiplier["expected_h2_power"]) < 2.0e-3, multiplier["leakage_vs_h2_log_slope"], multiplier["expected_h2_power"])
    add(rows, "separated_multiplier_supercritical", multiplier["separated_budget_exponent_sum"] == "13/12", multiplier["separated_budget_exponent_sum"], "13/12")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-signed-transport-besov-bregman-resonance-primary/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "source_version": __version__,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_sha256": digest(MANIFEST) if MANIFEST.exists() else None,
        "parameters": {
            "kappa": str(KAPPA),
            "floor": floor,
            "P": denominator_p,
            "q_matrix": q_matrix.tolist(),
        },
        "signed_ledger": ledger,
        "besov_budget": budget,
        "bregman_fixture": bregman,
        "path_square_curvature": path,
        "shifted_multiplier": multiplier,
        "assertions": rows,
        "summary": {"passed": passed, "total": len(rows), "verdict": "PASS" if passed == len(rows) else "FAIL"},
        "honesty_boundary": HONESTY_BOUNDARY,
        "source_sha256": digest(Path(__file__)),
    }
    atomic_json(OUT, payload)
    print(f"[R-076 primary] {passed}/{len(rows)} PASS" if passed == len(rows) else f"[R-076 primary] {passed}/{len(rows)} FAIL")
    print(f"result: {OUT.relative_to(REPO)}")
    print(f"signed-ledger max residual: {ledger['max_direct_wick_error']:.3e}")
    print(
        f"s={budget['s']} payload: X^({budget['x_power']}) "
        f"Y^({budget['y_power']}), slack={budget['young_slack']}, "
        f"moment={budget['required_moment']}, "
        f"eta^-{budget['eta_loss_power']} zeta^-{budget['zeta_loss_power']}"
    )
    print(f"affine Bregman fixture: {bregman['remainder']:.16g}")
    print(f"separated multiplier exponent sum: {multiplier['separated_budget_exponent_sum']}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(run())
