#!/usr/bin/env python3
"""Non-importing independent audit for the R-076 reduction.

This route rebuilds the real Pauli frames, uses only finite differences for
the endpoint ledger, uses a small automatic Taylor-jet algebra for the radial
multiplier derivatives, and uses composite Simpson quadrature for the path
split.  It imports neither the primary executable nor its runtime frame helper.
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

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SIGNED-TRANSPORT-BESOV-BREGMAN-RESONANCE-REDUCTION"
MANIFEST = REPO / "claims" / CLAIM / "classii_signed_transport_besov_bregman_resonance_manifest.json"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-24-independent-signed-transport-besov-bregman-resonance/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"

# Independent regression inputs and tolerances.
KAPPA = Fraction(1, 10)
RANDOM_SEED = 24077691
RANDOM_CASES = 24
DIFFERENCE_STEP = 2.0e-5
LEDGER_TOL = 3.0e-6
FIXTURE_TOL = 2.0e-8
SIMPSON_INTERVALS = 1 << 15
MULTIPLIER_DELTA = 8.0e-4
MULTIPLIER_TIME = 0.4
MULTIPLIER_MODES = (5, 10, 20, 40)
MULTIPLIER_POINTS = 40960
HONESTY_BOUNDARY = (
    "This independent audit confirms the corrected payload allocation and "
    "the failure of affine-Bregman and separated shifted-multiplier shortcuts. "
    "It does not prove the paired adapted shifted resonance, one-use, or Nelson."
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


def realify(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def generators() -> list[np.ndarray]:
    return [
        realify(np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128)),
        realify(np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128)),
        realify(np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128)),
    ]


def production_data() -> tuple[np.ndarray, float, float]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    q11 = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator
    q12 = float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator
    q22 = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    return np.asarray([[q11, q12], [q12, q22]]), float(parameters["rho_regularizer"]), denominator


def frames(z: np.ndarray, floor: float) -> list[np.ndarray]:
    denominator = float(z @ z + floor)
    output: list[np.ndarray] = []
    for symmetric in generators():
        sz = symmetric @ z
        quotient = float(z @ sz / denominator)
        output.append(np.stack((2.0 * sz, 2.0 * (sz - quotient * z)), axis=-1))
    return output


def production_matrix(z: np.ndarray, q_matrix: np.ndarray, floor: float) -> np.ndarray:
    return sum((frame @ q_matrix @ frame.T for frame in frames(z, floor)), start=np.zeros((6, 6)))


def energy(z: np.ndarray, y: np.ndarray, q_matrix: np.ndarray, floor: float) -> float:
    return 0.5 * sum(float((frame.T @ y) @ q_matrix @ (frame.T @ y)) for frame in frames(z, floor))


def ledger_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED)
    h = DIFFERENCE_STEP
    regroup_error = 0.0
    direct_error = 0.0
    for _ in range(RANDOM_CASES):
        z = rng.normal(size=6)
        a = 0.25 * rng.normal(size=6)
        g = rng.normal(size=6)
        c_value = 0.25 * rng.normal(size=6)
        gamma_seed = 0.15 * rng.normal(size=(6, 6))
        gamma = gamma_seed @ gamma_seed.T
        m0 = frames(z, floor)
        m1 = frames(z + a, floor)
        mp = frames(z + h * a, floor)
        mm = frames(z - h * a, floor)
        dframes = [(right - left) / (2.0 * h) for right, left in zip(mp, mm)]
        e2s = [(right - 2.0 * middle + left) / (2.0 * h**2) for right, middle, left in zip(mp, m0, mm)]
        b0 = production_matrix(z, q_matrix, floor)
        b1 = production_matrix(z + a, q_matrix, floor)
        bp = production_matrix(z + h * a, q_matrix, floor)
        bm = production_matrix(z - h * a, q_matrix, floor)
        db = (bp - bm) / (2.0 * h)
        fa = b1 - b0 - db

        original = 0.5 * float(np.sum(fa * (np.outer(g, g) - gamma)))
        regrouped = -0.5 * float(np.sum(fa * gamma))
        principal_c = 0.0
        linear_c = 0.0
        for frame0, frame1, dframe, e2 in zip(m0, m1, dframes, e2s):
            e_value = frame1 - frame0 - dframe
            e3 = e_value - e2
            w = frame0.T @ g
            delta = (dframe + e_value).T @ g
            current_c = frame1.T @ c_value
            original += float(w @ q_matrix @ (e3.T @ c_value)) + float(delta @ q_matrix @ current_c) + 0.5 * float(current_c @ q_matrix @ current_c)
            regrouped += float(w @ q_matrix @ (e2.T @ g)) + float(w @ q_matrix @ (e3.T @ (g + c_value))) + 0.5 * float((delta + current_c) @ q_matrix @ (delta + current_c))
            principal_c += float(w @ q_matrix @ (e2.T @ c_value))
            linear_c += float(w @ q_matrix @ (dframe.T @ c_value))
        regroup_error = max(regroup_error, abs(original - regrouped))

        first_raw = (energy(z + h * a, g + h * c_value, q_matrix, floor) - energy(z - h * a, g - h * c_value, q_matrix, floor)) / (2.0 * h)
        direct = energy(z + a, g + c_value, q_matrix, floor) - energy(z, g, q_matrix, floor) - first_raw - 0.5 * float(np.sum(fa * gamma))
        direct_error = max(direct_error, abs(direct - (linear_c + principal_c + regrouped)))
    return {"max_regroup_error": regroup_error, "max_direct_error": direct_error}


def exponent_audit() -> dict[str, str]:
    """Re-derive the allocation from input-max interpolation data.

    This route deliberately does not reuse the primary closed formulas for
    the X and Y powers.  One maximal input is interpolated between L2 and H2;
    the three remaining L6 inputs plus the residual L2 power are then
    converted to the sextic energy.
    """
    s = Fraction(1, 2) + KAPPA
    derivative_order = Fraction(1)
    top_sobolev_order = Fraction(2)
    number_of_inputs = Fraction(4)
    interpolation_theta = (derivative_order + s) / top_sobolev_order
    residual_l6_power = number_of_inputs - interpolation_theta
    x_power = interpolation_theta / 2
    y_power = residual_l6_power / 6
    slack = 1 - x_power - y_power
    separated = x_power + y_power + s / 4
    return {
        "s": str(s),
        "interpolation_theta": str(interpolation_theta),
        "residual_l6_power": str(residual_l6_power),
        "x_power": str(x_power),
        "y_power": str(y_power),
        "slack": str(slack),
        "moment": str(1 / slack),
        "eta_power": str(x_power / slack),
        "zeta_power": str(y_power / slack),
        "separated_sum": str(separated),
    }


def fixture_audit(q_matrix: np.ndarray, floor: float, denominator_p: float) -> dict[str, Any]:
    z = np.asarray([1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    a = np.asarray([1.0, 0.0, -1.0, 0.0, 0.0, 0.0])
    g = np.asarray([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    h = DIFFERENCE_STEP
    first = (energy(z + h * a, g, q_matrix, floor) - energy(z - h * a, g, q_matrix, floor)) / (2.0 * h)
    remainder = energy(z + a, g, q_matrix, floor) - energy(z, g, q_matrix, floor) - first
    formula = -9.0 / (160.0 * denominator_p * (2.0 + floor) ** 2)
    base = energy(z, g, q_matrix, floor)
    threshold = 1.0
    centered_tail = 2.0 * threshold * math.exp(-threshold**2 / 2.0) / math.sqrt(2.0 * math.pi)
    return {
        "remainder": remainder,
        "formula": formula,
        "ratio_to_base": remainder / base,
        "centered_tail_moment": centered_tail,
        "selector_expectation": formula * centered_tail,
    }


def simpson(function: Any, left: float, right: float, intervals: int) -> float:
    if intervals % 2:
        raise ValueError("Simpson intervals must be even")
    grid = np.linspace(left, right, intervals + 1)
    values = function(grid)
    return float((right - left) / (3.0 * intervals) * (values[0] + values[-1] + 4.0 * values[1:-1:2].sum() + 2.0 * values[2:-1:2].sum()))


def path_audit() -> dict[str, float]:
    def current(t: np.ndarray) -> np.ndarray:
        return (t - 1.0) * (t + 1.0) ** 2 / (1.0 + t**2)

    # Derivatives generated independently by symmetric finite differences.
    h = 5.0e-5
    def first(t: np.ndarray) -> np.ndarray:
        return (current(t + h) - current(t - h)) / (2.0 * h)

    def second(t: np.ndarray) -> np.ndarray:
        return (current(t + h) - 2.0 * current(t) + current(t - h)) / h**2

    positive = simpson(lambda t: (1.0 - t) * first(t) ** 2, 0.0, 1.0, SIMPSON_INTERVALS)
    curvature = simpson(lambda t: (1.0 - t) * current(t) * second(t), 0.0, 1.0, SIMPSON_INTERVALS)
    return {"positive": positive, "curvature": curvature, "total": positive + curvature}


def jet_variable(value: np.ndarray | float, order: int = 4) -> list[np.ndarray]:
    base = np.asarray(value, dtype=np.float64)
    return [base, np.ones_like(base)] + [np.zeros_like(base) for _ in range(order - 1)]


def jet_constant(value: np.ndarray | float, order: int = 4) -> list[np.ndarray]:
    base = np.asarray(value, dtype=np.float64)
    return [base] + [np.zeros_like(base) for _ in range(order)]


def jet_add(left: list[np.ndarray], right: list[np.ndarray]) -> list[np.ndarray]:
    return [a + b for a, b in zip(left, right)]


def jet_mul(left: list[np.ndarray], right: list[np.ndarray]) -> list[np.ndarray]:
    order = len(left) - 1
    return [sum((left[k] * right[n - k] for k in range(n + 1)), start=np.zeros_like(left[0])) for n in range(order + 1)]


def jet_inv(value: list[np.ndarray]) -> list[np.ndarray]:
    order = len(value) - 1
    output = [1.0 / value[0]]
    for n in range(1, order + 1):
        output.append(-sum((value[k] * output[n - k] for k in range(1, n + 1)), start=np.zeros_like(value[0])) / value[0])
    return output


def radial_derivatives(radius: np.ndarray | float, floor: float) -> tuple[np.ndarray, np.ndarray]:
    r_jet = jet_variable(radius)
    e_jet = jet_constant(floor)
    numerator = [2.0 * floor * coefficient for coefficient in r_jet]
    denominator = jet_add(jet_mul(r_jet, r_jet), e_jet)
    quotient = jet_mul(numerator, jet_inv(denominator))
    return math.factorial(3) * quotient[3], math.factorial(4) * quotient[4]


def multiplier_audit() -> dict[str, Any]:
    _, fourth = radial_derivatives(1.0, 1.0)
    s_value = float(Fraction(1, 2) + KAPPA)
    grid = 2.0 * math.pi * np.arange(MULTIPLIER_POINTS) / MULTIPLIER_POINTS
    base_third, _ = radial_derivatives(1.0, 1.0)
    leakages: list[float] = []
    for mode in MULTIPLIER_MODES:
        wave = np.cos(mode * grid)
        shifted_third, _ = radial_derivatives(1.0 + MULTIPLIER_TIME * MULTIPLIER_DELTA * wave, 1.0)
        leakages.append(float(abs(np.mean(mode**s_value * wave * (shifted_third - base_third)))))
    ratios = [right / left for left, right in zip(leakages[:-1], leakages[1:])]
    return {
        "fourth_derivative_normalized": float(fourth),
        "leakages": leakages,
        "ratios": ratios,
        "expected_ratio": 2.0**s_value,
    }


def run() -> int:
    q_matrix, floor, denominator_p = production_data()
    ledger = ledger_audit(q_matrix, floor)
    exponents = exponent_audit()
    fixture = fixture_audit(q_matrix, floor, denominator_p)
    path = path_audit()
    multiplier = multiplier_audit()

    rows: list[dict[str, Any]] = []
    add(rows, "ledger_regroup", ledger["max_regroup_error"] < LEDGER_TOL, ledger["max_regroup_error"], f"<{LEDGER_TOL}")
    add(rows, "ledger_direct", ledger["max_direct_error"] < LEDGER_TOL, ledger["max_direct_error"], f"<{LEDGER_TOL}")
    add(rows, "exponent_payload", [exponents["x_power"], exponents["y_power"]] == ["2/5", "8/15"], [exponents["x_power"], exponents["y_power"]], ["2/5", "8/15"])
    add(rows, "exponent_slack", exponents["slack"] == "1/15", exponents["slack"], "1/15")
    add(rows, "exponent_moment", exponents["moment"] == "15", exponents["moment"], "15")
    add(rows, "exponent_losses", [exponents["eta_power"], exponents["zeta_power"]] == ["6", "8"], [exponents["eta_power"], exponents["zeta_power"]], ["6", "8"])
    add(rows, "separated_supercritical", exponents["separated_sum"] == "13/12", exponents["separated_sum"], "13/12")
    add(rows, "fixture_formula", abs(fixture["remainder"] - fixture["formula"]) < FIXTURE_TOL, fixture["remainder"], fixture["formula"])
    add(rows, "fixture_ratio", abs(fixture["ratio_to_base"] + 3.0) < FIXTURE_TOL, fixture["ratio_to_base"], -3.0)
    add(rows, "selector_negative", fixture["selector_expectation"] < 0.0, fixture["selector_expectation"], "<0")
    add(rows, "path_positive", abs(path["positive"] - (3.5 - math.log(4.0) - math.pi / 2.0)) < 4.0e-7, path["positive"], "7/2-log4-pi/2")
    add(rows, "path_curvature", abs(path["curvature"] - (-5.0 + math.log(4.0) + math.pi / 2.0)) < 4.0e-7, path["curvature"], "-5+log4+pi/2")
    add(rows, "path_total", abs(path["total"] + 1.5) < 5.0e-7, path["total"], -1.5)
    add(rows, "jet_fourth_derivative", abs(multiplier["fourth_derivative_normalized"] + 6.0) < 1.0e-12, multiplier["fourth_derivative_normalized"], -6.0)
    add(rows, "multiplier_growth", max(abs(value - multiplier["expected_ratio"]) for value in multiplier["ratios"]) < 3.0e-6, multiplier["ratios"], multiplier["expected_ratio"])

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-signed-transport-besov-bregman-resonance-independent/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "source_version": __version__,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_sha256": digest(MANIFEST) if MANIFEST.exists() else None,
        "ledger": ledger,
        "exponents": exponents,
        "fixture": fixture,
        "path": path,
        "multiplier": multiplier,
        "assertions": rows,
        "summary": {"passed": passed, "total": len(rows), "verdict": "PASS" if passed == len(rows) else "FAIL"},
        "honesty_boundary": HONESTY_BOUNDARY,
        "source_sha256": digest(Path(__file__)),
    }
    atomic_json(OUT, payload)
    print(f"[R-076 independent] {passed}/{len(rows)} PASS" if passed == len(rows) else f"[R-076 independent] {passed}/{len(rows)} FAIL")
    print(f"result: {OUT.relative_to(REPO)}")
    print(f"finite-difference ledger residual: {ledger['max_direct_error']:.3e}")
    print(f"affine Bregman fixture: {fixture['remainder']:.16g}")
    print(f"separated multiplier exponent sum: {exponents['separated_sum']}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(run())
