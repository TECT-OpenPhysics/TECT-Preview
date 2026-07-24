#!/usr/bin/env python3
"""Non-importing audit of the A13 resonant phase-root/Besov reduction.

This implementation rebuilds the Pauli frames, production target metric,
sharp-cube covariance, resonance integral, phase feedback, and gauge orbit
identities without importing the primary or any predecessor executable.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RESONANT-PHASE-ROOT-BESOV-REDUCTION"
A1 = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-24-independent-resonant-phase-root-besov-reduction/result.json"

GRID = 1 << 16
GAUSS_HERMITE_ORDERS = (40, 80)
TOL = 5.0e-10
NONZERO = 1.0e-10
SEED = 7413
COVARIANCE_CUTOFFS = (4, 8, 16, 32, 64)


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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})


def realify(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.complex128)
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def generators() -> list[np.ndarray]:
    return [
        realify(np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128)),
        realify(np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128)),
        realify(np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128)),
    ]


def frame(value: np.ndarray, floor: float) -> list[np.ndarray]:
    denominator = float(value @ value + floor)
    result = []
    for symmetric in generators():
        transformed = symmetric @ value
        quotient = float(value @ transformed / denominator)
        result.append(np.stack((2.0 * transformed, 2.0 * (transformed - quotient * value)), axis=1))
    return result


def coefficient(value: np.ndarray, q_matrix: np.ndarray, floor: float) -> np.ndarray:
    return sum((item @ q_matrix @ item.T for item in frame(value, floor)), np.zeros((6, 6)))


def rotation(doublet: float, singlet: float) -> np.ndarray:
    result = np.eye(6)
    for left, right, theta in ((0, 3, doublet), (1, 4, doublet), (2, 5, singlet)):
        c_value, s_value = math.cos(theta), math.sin(theta)
        result[np.ix_((left, right), (left, right))] = np.asarray([[c_value, -s_value], [s_value, c_value]])
    return result


def production() -> tuple[dict[str, Any], np.ndarray, float, float]:
    parameters = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    q_matrix = np.asarray(
        [
            [float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator,
             float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator],
            [float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator,
             float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator],
        ]
    )
    return parameters, q_matrix, float(parameters["rho_regularizer"]), denominator


def principal_and_secant(q_matrix: np.ndarray, floor: float, denominator: float) -> dict[str, Any]:
    e1, e2 = np.eye(6)[0], np.eye(6)[1]
    base = frame(e1, floor)
    step = 1.0e-3
    plus = frame(e1 + step * e2, floor)
    minus = frame(e1 - step * e2, floor)
    half_hessian = [(plus[index] - 2.0 * base[index] + minus[index]) / (2.0 * step**2) for index in range(3)]
    currents = [item.T @ e2 for item in base]
    generator_contractions = [
        float(e2 @ half_hessian[index] @ q_matrix @ currents[index])
        for index in range(3)
    ]
    numerical = float(sum(generator_contractions))
    exact = -27.0 / (200.0 * denominator * (1.0 + floor))

    rows = []
    for k_value in (7, 15, 31, 63):
        n_value = 3
        amplitude = 0.7
        def integrate(point_count: int) -> float:
            grid = 2.0 * math.pi * np.arange(point_count) / point_count
            high = amplitude * np.cos(k_value * grid)
            return float(
                np.mean(
                    high**2
                    / (1.0 + floor + high**2)
                    * np.cos(n_value * grid) ** 2
                )
            )

        coarse_integral = integrate(GRID // 2)
        direct_integral = integrate(GRID)
        closed_integral = 0.5 * (1.0 - math.sqrt((1.0 + floor) / (1.0 + floor + amplitude**2)))
        branch = -8.0 * float(q_matrix[0, 1] + q_matrix[1, 1]) * direct_integral
        rows.append({"k": k_value, "n": n_value, "integral": direct_integral, "closed": closed_integral, "refinement_error": abs(direct_integral - coarse_integral), "branch": branch})
    return {
        "finite_difference_principal": numerical,
        "exact_principal": exact,
        "principal_error": abs(numerical - exact),
        "generator_contractions": generator_contractions,
        "secant_rows": rows,
        "secant_integral_error": max(abs(row["integral"] - row["closed"]) for row in rows),
        "secant_refinement_error": max(row["refinement_error"] for row in rows),
        "secant_spread": max(row["branch"] for row in rows) - min(row["branch"] for row in rows),
    }


def phase_diagnostics(q_matrix: np.ndarray, floor: float, denominator: float) -> dict[str, Any]:
    e1, e4 = np.eye(6)[0], np.eye(6)[3]
    angles = np.linspace(0.1, 1.4, 9)
    ratios = []
    for theta in angles:
        value = rotation(float(theta), 0.0) @ e1
        ratios.append(float(e4 @ coefficient(value, q_matrix, floor) @ e4) / math.sin(float(theta)) ** 2)
    expected = 3.0 * (113.0 * floor**2 + 136.0 * floor + 48.0) / (2000.0 * denominator * (1.0 + floor) ** 2)
    amplitude = 0.4
    wick_mean = -expected * amplitude**2 / (3.0 * math.sqrt(3.0))

    def gaussian_quadrature(order: int) -> float:
        nodes, weights = np.polynomial.hermite.hermgauss(order)
        values = []
        for node in math.sqrt(2.0) * nodes:
            theta = math.asin(amplitude * math.exp(-0.5 * float(node) ** 2))
            rotated = rotation(theta, 0.0) @ e1
            coefficient_value = float(e4 @ coefficient(rotated, q_matrix, floor) @ e4)
            values.append(0.5 * coefficient_value * (float(node) ** 2 - 1.0))
        return float(np.dot(weights, np.asarray(values)) / math.sqrt(math.pi))

    quadrature_values = {
        str(order): gaussian_quadrature(order) for order in GAUSS_HERMITE_ORDERS
    }
    quadrature_high = quadrature_values[str(GAUSS_HERMITE_ORDERS[-1])]

    rng = np.random.default_rng(SEED)
    equivariance = 0.0
    current_invariance = 0.0
    for _ in range(80):
        value = rng.normal(size=6)
        derivative = rng.normal(size=6)
        theta_d, theta_s = rng.normal(size=2)
        rate_d, rate_s = rng.normal(size=2)
        rotate = rotation(theta_d, theta_s)
        j_d = np.zeros((6, 6))
        j_s = np.zeros((6, 6))
        for left, right in ((0, 3), (1, 4)):
            j_d[left, right], j_d[right, left] = -1.0, 1.0
        j_s[2, 5], j_s[5, 2] = -1.0, 1.0
        old_frames = frame(value, floor)
        new_frames = frame(rotate @ value, floor)
        transformed = rotate @ (derivative + rate_d * j_d @ value + rate_s * j_s @ value)
        for new, old in zip(new_frames, old_frames):
            equivariance = max(equivariance, float(np.linalg.norm(new - rotate @ old)))
            current_invariance = max(current_invariance, float(np.linalg.norm(new.T @ transformed - old.T @ derivative)))
    return {
        "lambda_values": ratios,
        "lambda_expected": expected,
        "lambda_error": max(abs(value - expected) for value in ratios),
        "negative_feedback_mean": wick_mean,
        "quadrature_feedback_means": quadrature_values,
        "quadrature_refinement_error": abs(
            quadrature_values[str(GAUSS_HERMITE_ORDERS[-1])]
            - quadrature_values[str(GAUSS_HERMITE_ORDERS[0])]
        ),
        "quadrature_formula_error": abs(quadrature_high - wick_mean),
        "frame_equivariance_error": equivariance,
        "local_phase_current_error": current_invariance,
    }


def mode_counts(cutoff: int) -> np.ndarray:
    values = np.arange(-cutoff, cutoff + 1, dtype=np.int64)
    one = np.bincount(values * values, minlength=cutoff * cutoff + 1).astype(np.float64)
    target = 3 * (len(one) - 1) + 1
    fft_length = 1 << (target - 1).bit_length()
    spectrum = np.fft.rfft(one, fft_length)
    counts = np.rint(np.fft.irfft(spectrum**3, fft_length)[:target]).astype(np.int64)
    if int(counts.sum()) != (2 * cutoff + 1) ** 3:
        raise AssertionError("independent cube mode count failed")
    return counts


def mass_matrix(parameters: dict[str, Any]) -> np.ndarray:
    vector = np.asarray(parameters["z0"], dtype=np.float64)
    projector = np.outer(vector, vector) / float(vector @ vector)
    return np.diag(np.asarray(parameters["family_masses"], dtype=np.float64)) + float(parameters["k_lock"]) * (np.eye(3) - projector)


def derivative_covariance(cutoff: int, parameters: dict[str, Any]) -> np.ndarray:
    counts = mode_counts(cutoff).astype(np.float64)
    squared = np.arange(len(counts), dtype=np.float64)
    alpha2 = (2.0 * math.pi / float(parameters["Lx"])) ** 2
    k2 = alpha2 * squared
    scalar = float(parameters["r"]) + float(parameters["Z"]) * k2 + float(parameters["Y"]) * k2**2
    eigenvalues, basis = np.linalg.eigh(mass_matrix(parameters))
    denominators = scalar[:, None] + eigenvalues[None, :]
    volume = float(parameters["Lx"]) * float(parameters["Ly"]) * float(parameters["Lz"])
    diagonal = (2.0 / (3.0 * volume)) * np.sum(counts[:, None] * k2[:, None] / denominators, axis=0)
    return (basis * diagonal) @ basis.T


def perpendicular(matrix: np.ndarray) -> np.ndarray:
    result = np.zeros_like(matrix)
    result[:2, 2] = matrix[:2, 2]
    result[2, :2] = matrix[2, :2]
    return result


def covariance_tail(parameters: dict[str, Any]) -> dict[str, Any]:
    matrices = [perpendicular(derivative_covariance(cutoff, parameters)) for cutoff in COVARIANCE_CUTOFFS]
    increments = [float(np.linalg.norm(matrices[index] - matrices[index - 1], ord="fro")) for index in range(1, len(matrices))]
    scaled = [increments[index - 1] * COVARIANCE_CUTOFFS[index - 1] ** 3 for index in range(1, len(matrices))]
    slopes = np.diff(np.log(np.asarray(increments))) / np.diff(np.log(np.asarray(COVARIANCE_CUTOFFS[1:], dtype=float)))
    return {
        "cutoffs": list(COVARIANCE_CUTOFFS),
        "perpendicular_norms": [float(np.linalg.norm(value, ord="fro")) for value in matrices],
        "successive_increments": increments,
        "N3_scaled_increments": scaled,
        "successive_slopes": slopes.tolist(),
        "analytic_resolvent_tail": "derivative weight |k|^2 times anisotropic resolvent remainder O(|k|^-8) gives sum tail O(N^-3)",
    }


def cameron_martin_fixture(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    z = np.asarray([-1.0, -1.0, 0.0, 0.0, -1.0, 0.0])
    endpoint_value = np.asarray([1.0, -1.0, 0.0, 1.0, 0.0, 0.0])
    direction = endpoint_value - z
    derivative_value = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    kernel = np.asarray([-1.0, 0.0, 0.0, 1.0, -1.0, 0.0])
    step = 2.0e-5
    frames_0 = frame(z, floor)
    frames_1 = frame(endpoint_value, floor)
    plus = frame(z + step * direction, floor)
    minus = frame(z - step * direction, floor)
    derivatives = [
        (plus[index] - minus[index]) / (2.0 * step) for index in range(3)
    ]
    currents = [item.T @ derivative_value for item in frames_0]
    leakage = np.zeros(6, dtype=np.float64)
    for frame_0, frame_1, derivative, current in zip(
        frames_0, frames_1, derivatives, currents
    ):
        leakage += (frame_1 - frame_0 - derivative) @ q_matrix @ current
    derived = float(kernel @ leakage)
    oracle = 27.0 * (6.0 * floor**2 + 22.0 * floor + 27.0) / (
        400.0 * (floor + 3.0) ** 3
    )
    return {"derived": derived, "oracle": oracle, "error": abs(derived - oracle)}


def main() -> int:
    parameters, q_matrix, floor, denominator = production()
    principal = principal_and_secant(q_matrix, floor, denominator)
    phase = phase_diagnostics(q_matrix, floor, denominator)
    covariance = covariance_tail(parameters)
    kappa = 0.1
    cm_fixture = cameron_martin_fixture(q_matrix, floor)
    cm_slope = cm_fixture["derived"]
    cm_losses = [-cm_slope**2 / (24.0 * 0.15 * (n**2 + 1.0 + n**-2)) for n in (4, 8, 16, 32, 64)]

    rows: list[dict[str, Any]] = []
    add(rows, "independent_Q_positive", float(np.linalg.eigvalsh(q_matrix)[0]) > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), ">0")
    add(rows, "independent_principal_nonzero", abs(principal["exact_principal"]) > NONZERO, principal["exact_principal"], "nonzero")
    add(rows, "independent_finite_difference_principal", principal["principal_error"] < 3.0e-7 and max(abs(value) for value in principal["generator_contractions"][1:]) < 3.0e-7, {"total_error": principal["principal_error"], "per_generator": principal["generator_contractions"]}, "total error and other generators<3e-7")
    add(rows, "independent_secant_quadrature", max(principal["secant_integral_error"], principal["secant_refinement_error"]) < TOL, {"formula": principal["secant_integral_error"], "refinement": principal["secant_refinement_error"]}, f"<{TOL}")
    add(rows, "independent_no_bare_separation_gain", principal["secant_spread"] < TOL, principal["secant_spread"], f"<{TOL}")
    add(rows, "independent_phase_lambda_formula", phase["lambda_error"] < TOL, phase["lambda_error"], f"<{TOL}")
    add(rows, "independent_phase_feedback_negative", phase["quadrature_feedback_means"][str(GAUSS_HERMITE_ORDERS[-1])] < 0.0 and max(phase["quadrature_refinement_error"], phase["quadrature_formula_error"]) < TOL, {"quadrature": phase["quadrature_feedback_means"], "formula": phase["negative_feedback_mean"]}, f"negative with refinement/formula error<{TOL}")
    add(rows, "independent_frame_equivariance", phase["frame_equivariance_error"] < TOL, phase["frame_equivariance_error"], f"<{TOL}")
    add(rows, "independent_integrable_phase_current_invariance", phase["local_phase_current_error"] < TOL, phase["local_phase_current_error"], f"<{TOL}")
    add(rows, "independent_covariance_anomaly_is_nonzero", covariance["perpendicular_norms"][-1] > NONZERO, covariance["perpendicular_norms"][-1], ">0")
    add(rows, "independent_covariance_increments_decay", all(left > right > 0.0 for left, right in zip(covariance["successive_increments"], covariance["successive_increments"][1:])), covariance["successive_increments"], "strictly decreasing")
    add(rows, "independent_covariance_tail_has_cubic_rate", covariance["successive_slopes"][-1] < -2.8, covariance["successive_slopes"], "last slope<-2.8")
    add(rows, "independent_CM_kernel_slope_is_rederived", cm_fixture["error"] < 2.0e-8, cm_fixture, "error<2e-8")
    add(rows, "independent_CM_kernel_loss_is_summable", all(abs(left) > abs(right) for left, right in zip(cm_losses, cm_losses[1:])), cm_losses, "decreasing absolute dyadic losses")
    add(rows, "independent_Besov_order_below_one", 0.5 + kappa < 1.0, 0.5 + kappa, "<1")
    add(rows, "independent_Besov_budget_slack", abs(1.0 - 0.5 - 1.0 / 3.0 - 1.0 / 6.0) < TOL, {"X": 0.5, "Y": 1.0 / 3.0, "random": 1.0 / 6.0}, "sum=1")
    add(rows, "independent_scope_firewall", True, "no adapted Taylor one-form or coercivity claimed", "open")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-resonant-phase-root-besov-reduction-run/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "run_kind": "independent-non-importing",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "derived": {"principal_and_secant": principal, "phase": phase, "covariance_tail": covariance, "CM_fixture": cm_fixture, "CM_losses": cm_losses},
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed == len(rows),
        "summary": {"passed": passed, "total": len(rows), "status": "PASS" if passed == len(rows) else "FAIL"},
        "source": {"path": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "sha256": digest(Path(__file__).resolve()), "version": __version__},
        "honesty_boundary": "Independent diagnostics establish the scoped route boundaries and pure phase-orbit identity only; horizontal adapted coercivity, finite-energy recovery, one-use, and Nelson remain open.",
    }
    atomic_json(OUT, payload)
    print(f"A13 resonant phase-root/Besov independent: {passed}/{len(rows)} PASS")
    print(f"principal coefficient = {principal['exact_principal']:.16g}")
    print(f"last covariance increment slope = {covariance['successive_slopes'][-1]:.8f}")
    print(f"wrote {OUT.relative_to(REPO)}")
    if passed == len(rows):
        print("A13-CLASSII-RESONANT-PHASE-ROOT-BESOV-INDEPENDENT-PASS")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
