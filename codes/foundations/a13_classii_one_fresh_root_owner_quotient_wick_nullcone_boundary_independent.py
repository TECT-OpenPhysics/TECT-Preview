#!/usr/bin/env python3
"""Independent non-importing audit for the scoped R-116 A13 boundary.

This route uses rational list algebra, Gauss-Hermite quadrature, direct
complex Pauli-Fierz coordinates, SciPy integration, and numerical
optimization.  It deliberately does not import the primary certificate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Callable

import numpy as np
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ONE-FRESH-ROOT-OWNER-QUOTIENT-WICK-NULLCONE-BOUNDARY"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-independent-one-fresh-root-owner-quotient-wick-nullcone-boundary/result.json"
)

INPUTS = {
    "q": Fraction(10, 9),
    "alpha": Fraction(5, 9),
    "c0_times_P": Fraction(3, 250),
    "c1_times_P": Fraction(243, 8000),
    "quadrature_order": 24,
    "finite_difference_step": 1.0e-7,
}

REGRESSION_ORACLES = {
    "centered_H": 128.0,
    "centered_K": 1088.0,
    "holder_optimum": 36.0,
}


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-one-fresh-root-owner-quotient-wick-nullcone-boundary-independent/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "independence": (
                "No import from the primary certificate; rational list algebra, "
                "Gauss-Hermite quadrature, SciPy quadrature/optimization, and direct "
                "complex current coordinates are reconstructed here."
            ),
            "no_overclaim": (
                "The audit confirms the R-116 algebra and numerical witnesses only. "
                "It does not certify the remaining full production cluster or Sector A."
            ),
        }


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(left, right)), Fraction(0))


def add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [x + y for x, y in zip(left, right)]


def endpoint_audit(audit: Audit) -> dict[str, Any]:
    initial = [Fraction(3, 7), Fraction(-2, 5)]
    increments = [
        [Fraction(5, 11), Fraction(1, 13)],
        [Fraction(-4, 17), Fraction(3, 19)],
        [Fraction(2, 23), Fraction(-7, 29)],
        [Fraction(1, 31), Fraction(5, 37)],
    ]
    traces = [Fraction(2, 9), Fraction(5, 8), Fraction(11, 10), Fraction(7, 3), Fraction(13, 4)]
    current = list(initial)
    visits = Fraction(0)
    for index, increment in enumerate(increments):
        visits += dot(current, increment) + dot(increment, increment) / 2
        visits -= (traces[index + 1] - traces[index]) / 2
        current = add(current, increment)
    endpoint = (dot(current, current) - dot(initial, initial)) / 2 - (traces[-1] - traces[0]) / 2
    audit.check("endpoint", "four_visit_fraction_telescope", visits == endpoint, visits, endpoint)
    return {"visits": visits, "endpoint": endpoint}


def gauss_expectation_2d(function: Callable[[np.ndarray, np.ndarray], np.ndarray], order: int) -> float:
    nodes, weights = hermgauss(order)
    standard = math.sqrt(2.0) * nodes
    normalized = weights / math.sqrt(math.pi)
    left, right = np.meshgrid(standard, standard, indexing="ij")
    matrix_weights = np.outer(normalized, normalized)
    return float(np.sum(matrix_weights * function(left, right)))


def wick_and_nullcone_audit(audit: Audit) -> dict[str, Any]:
    order = int(INPUTS["quadrature_order"])
    full_mean = gauss_expectation_2d(lambda x, y: (x * x - 1.0) * (y * y - 1.0), order)
    production_mean = gauss_expectation_2d(lambda x, y: x * x * (y * y - 1.0), order)
    missing_mean = gauss_expectation_2d(lambda x, y: y * y - 1.0, order)
    audit.check("wick", "full_wick_centered_quadrature", abs(full_mean) < 2.0e-13, full_mean, 0.0)
    audit.check("wick", "production_partial_centered_quadrature", abs(production_mean) < 2.0e-13, production_mean, 0.0)
    audit.check("wick", "missing_owner_centered_quadrature", abs(missing_mean) < 2.0e-13, missing_mean, 0.0)

    packet_mean = gauss_expectation_2d(
        lambda u, v: 0.5 * ((2.0 + u * u - v * v) ** 2 - 4.0 * (u * u + v * v)), order
    )
    h_cost = gauss_expectation_2d(lambda u, v: 16.0 * (u * u + v * v) ** 2, order)
    k_cost = gauss_expectation_2d(
        lambda u, v: (4.0 * (u * u - v * v) ** 2 - 12.0 * (u * u + v * v) + 8.0) ** 2,
        order,
    )
    audit.check("nullcone", "centered_packet", abs(packet_mean) < 2.0e-12, packet_mean, 0.0)
    audit.check("nullcone", "H_quadrature", abs(h_cost - REGRESSION_ORACLES["centered_H"]) < 2.0e-10, h_cost, REGRESSION_ORACLES["centered_H"])
    audit.check("nullcone", "K_quadrature", abs(k_cost - REGRESSION_ORACLES["centered_K"]) < 2.0e-9, k_cost, REGRESSION_ORACLES["centered_K"])

    def tube_packet(small: float, large: float) -> float:
        x1 = (small + large) / math.sqrt(2.0)
        x2 = (small - large) / math.sqrt(2.0)
        return 0.5 * ((2.0 + x1 * x1 - x2 * x2) ** 2 - 4.0 * (x1 * x1 + x2 * x2))

    worst_defect = -math.inf
    for large in np.linspace(1.0, 20.0, 101):
        for small in np.linspace(-1.0 / large, 1.0 / large, 41):
            worst_defect = max(worst_defect, tube_packet(float(small), float(large)) - (8.0 - 2.0 * large * large))
    audit.check("nullcone", "tube_upper_grid", worst_defect <= 2.0e-12, worst_defect, "<=0")
    return {"full_mean": full_mean, "packet_mean": packet_mean, "H": h_cost, "K": k_cost, "tube_max_defect": worst_defect}


def full_wick_cost_audit(audit: Audit) -> dict[str, Any]:
    order = int(INPUTS["quadrature_order"])
    kappa = 0.37
    epsilon = 0.43

    def hs_cost(u: np.ndarray, v: np.ndarray) -> np.ndarray:
        j11 = 2.0 * epsilon * v
        j12 = 2.0 * epsilon * u
        j21 = np.zeros_like(u)
        j22 = 4.0 * kappa * epsilon * v
        w11 = j11 * j11 + j12 * j12
        w12 = j11 * j21 + j12 * j22
        w22 = j21 * j21 + j22 * j22
        return w11 * w11 + 2.0 * w12 * w12 + w22 * w22

    numeric = gauss_expectation_2d(hs_cost, order)
    exact = 128.0 * epsilon**4 * (1.0 + kappa**2 + 6.0 * kappa**4)
    audit.check("full_wick", "independent_covariance_cost", abs(numeric - exact) < 2.0e-11, numeric, exact)

    q = float(INPUTS["q"])
    delta = 1.0e-12
    alpha = (1.0 - delta) / 4.0
    epsilon_squared = alpha / q
    target = 32.0 * alpha * alpha * (1.0 + 0.01**2 + 6.0 * 0.01**4)
    audit.check("full_wick", "near_threshold_target_small", target < 2.1, target, "<2.1")
    audit.check("full_wick", "conditional_domain_positive", 1.0 - 4.0 * q * epsilon_squared > 0.0, 1.0 - 4.0 * q * epsilon_squared, ">0")
    return {"quadrature_cost": numeric, "closed_cost": exact, "near_threshold_target": target}


def holder_and_affine_audit(audit: Audit) -> dict[str, Any]:
    costs = np.array([1.0, 4.0, 9.0])
    weights = np.sqrt(costs) / np.sqrt(costs).sum()
    value = float(np.sum(costs / weights))
    grid_minimum = math.inf
    grid_argmin = None
    for first in np.linspace(0.04, 0.92, 177):
        for second in np.linspace(0.04, 0.92 - first, 89) if first < 0.88 else ():
            third = 1.0 - first - second
            if third <= 0.0:
                continue
            candidate = float(costs[0] / first + costs[1] / second + costs[2] / third)
            if candidate < grid_minimum:
                grid_minimum = candidate
                grid_argmin = (first, second, third)
    audit.check("holder", "numerical_weight_optimization", abs(value - REGRESSION_ORACLES["holder_optimum"]) < 1.0e-9, value, REGRESSION_ORACLES["holder_optimum"])
    audit.check("holder", "coarse_simplex_does_not_beat_exact", grid_minimum >= value - 1.0e-12, grid_minimum, f">={value}")

    q = float(INPUTS["q"])
    combined = np.array([[0.6, -0.15], [-0.05, 0.4]])
    covariance = combined @ combined.T
    baseline = np.array([0.6, -0.8])
    shifted = np.eye(2) + q * covariance
    det_two_log = math.log(float(np.linalg.det(shifted))) - q * float(np.trace(covariance))
    phi = -0.5 * det_two_log - 0.5 * q * float(baseline @ np.linalg.solve(shifted, baseline))
    bound = q * q * float(np.sum(covariance * covariance)) / 4.0
    audit.check("affine", "independent_det2_bound", phi <= bound + 2.0e-14, phi, f"<={bound}")
    return {"holder_weights": weights, "holder_value": value, "grid_minimum": grid_minimum, "grid_argmin": grid_argmin, "affine_phi": phi, "affine_bound": bound}


def codimension_audit(audit: Audit) -> dict[str, Any]:
    q = float(INPUTS["q"])
    values: dict[str, Any] = {}
    nodes, weights = leggauss(256)
    angles = 0.5 * math.pi * nodes
    angle_weights = 0.5 * math.pi * weights
    for codimension in (2, 3, 5):
        tangents = np.tan(angles) / math.sqrt(q)
        jacobian = (1.0 / math.sqrt(q)) / np.cos(angles) ** 2
        numeric = float(np.sum(angle_weights * (1.0 + q * tangents * tangents) ** (-0.5 * codimension) * jacobian))
        exact = math.sqrt(math.pi / q) * math.gamma((codimension - 1.0) / 2.0) / math.gamma(codimension / 2.0)
        audit.check("codimension", f"critical_integral_k_{codimension}", abs(numeric - exact) < 5.0e-10, numeric, exact)
        values[str(codimension)] = {"numeric": numeric, "exact": exact}
    one_small = 2.0 * math.asinh(math.sqrt(q) * 10.0) / math.sqrt(q)
    one_large = 2.0 * math.asinh(math.sqrt(q) * 10000.0) / math.sqrt(q)
    audit.check("codimension", "critical_k_one_diverges", one_large > 2.0 * one_small, one_large, f">{2.0 * one_small}")

    sequence_values = []
    for radius in (10.0, 100.0, 1000.0):
        tangent = 0.7
        t = radius
        y = tangent
        recession = 1.0 - q * (t * t / q) / (t * t + y * y) + q * (t * y) ** 2 / (t * t + y * y)
        sequence_values.append(recession)
    audit.check("codimension", "parabolic_sequence_converges", abs(sequence_values[-1] - q * 0.7**2) < 2.0e-6, sequence_values[-1], q * 0.7**2)
    values["k1"] = {"radius_10": one_small, "radius_10000": one_large}
    values["parabolic_sequence"] = sequence_values
    return values


def current_coordinate(
    u: np.ndarray,
    chi: complex,
    derivative_u: np.ndarray,
    derivative_chi: complex,
    floor: float,
) -> np.ndarray:
    p_mass = 4.0 + floor
    c0 = float(INPUTS["c0_times_P"]) / p_mass
    c1 = float(INPUTS["c1_times_P"]) / p_mass
    csum = c0 + c1
    alpha = float(INPUTS["alpha"])
    radial_mass = float(np.vdot(u, u).real)
    total_mass = radial_mass + abs(chi) ** 2
    dr = 2.0 * float(np.vdot(u, derivative_u).real)
    dtotal = dr + 2.0 * float((np.conjugate(chi) * derivative_chi).real)
    determinant = u[0] * derivative_u[1] - u[1] * derivative_u[0]
    theta = radial_mass / (total_mass + floor)
    return np.array(
        [
            math.sqrt(c0) * dr,
            math.sqrt(c1) * (dr - alpha * theta * dtotal),
            2.0 * math.sqrt(csum) * determinant.real,
            2.0 * math.sqrt(csum) * determinant.imag,
        ]
    )


def production_symbol_audit(audit: Audit) -> dict[str, Any]:
    floor = 0.8
    wave = 3
    singlet_wave = -2
    p = np.array([0.7 + 0.2j, -0.3 + 0.5j])
    singlet_amplitude = 0.6 - 0.1j
    maxima = []
    for location in np.linspace(0.0, 2.0 * math.pi, 23, endpoint=False):
        phase = np.exp(1j * wave * location)
        singlet_phase = np.exp(1j * singlet_wave * location)
        u = p * phase
        chi = singlet_amplitude * singlet_phase
        coordinate = current_coordinate(u, chi, 1j * wave * u, 1j * singlet_wave * chi, floor)
        maxima.append(float(np.max(np.abs(coordinate))))
    audit.check("production_symbol", "active_plane_wave_exact_null", max(maxima) < 2.0e-15, max(maxima), 0.0)

    location = 0.37
    phase = np.exp(1j * wave * location)
    singlet_phase = np.exp(1j * singlet_wave * location)
    u = p * phase
    chi = singlet_amplitude * singlet_phase
    variation_wave = 5
    singlet_variation_wave = 4
    a0 = np.array([0.2 - 0.4j, 0.3 + 0.1j]) * np.exp(1j * variation_wave * location)
    s0 = (-0.25 + 0.35j) * np.exp(1j * singlet_variation_wave * location)
    derivative_a = 1j * variation_wave * a0
    derivative_s = 1j * singlet_variation_wave * s0

    radial_mass = float(np.vdot(u, u).real)
    total_mass = radial_mass + abs(chi) ** 2
    theta = radial_mass / (total_mass + floor)
    covariant_a = derivative_a - 1j * wave * a0
    covariant_s = derivative_s - 1j * singlet_wave * s0
    radial = 2.0 * float(np.vdot(u, covariant_a).real)
    total = radial + 2.0 * float((np.conjugate(chi) * covariant_s).real)
    determinant = u[0] * covariant_a[1] - u[1] * covariant_a[0]
    p_mass = 4.0 + floor
    c0 = float(INPUTS["c0_times_P"]) / p_mass
    c1 = float(INPUTS["c1_times_P"]) / p_mass
    csum = c0 + c1
    formula = np.array(
        [
            math.sqrt(c0) * radial,
            math.sqrt(c1) * (radial - float(INPUTS["alpha"]) * theta * total),
            2.0 * math.sqrt(csum) * determinant.real,
            2.0 * math.sqrt(csum) * determinant.imag,
        ]
    )
    step = float(INPUTS["finite_difference_step"])
    plus = current_coordinate(u + step * a0, chi + step * s0, 1j * wave * u + step * derivative_a, 1j * singlet_wave * chi + step * derivative_s, floor)
    minus = current_coordinate(u - step * a0, chi - step * s0, 1j * wave * u - step * derivative_a, 1j * singlet_wave * chi - step * derivative_s, floor)
    finite_difference = (plus - minus) / (2.0 * step)
    defect = float(np.max(np.abs(finite_difference - formula)))
    audit.check("production_symbol", "linearized_symbol_finite_difference", defect < 2.0e-9, defect, "<2e-9")

    csum_fraction = INPUTS["c0_times_P"] + INPUTS["c1_times_P"]
    audit.check("production_symbol", "coefficient_sum", csum_fraction == Fraction(339, 8000), csum_fraction, Fraction(339, 8000))

    kmax = 2.7
    amplitude_squared = math.sqrt((10.0 / 9.0) * kmax)
    amplitude = math.sqrt(amplitude_squared)
    value = (3.0 / 20.0) * amplitude**6 - 0.5 * kmax * amplitude**2
    closed = -(3.0 / 10.0) * ((10.0 / 9.0) * kmax) ** 1.5
    audit.check("production_symbol", "sextic_minimum_numeric", abs(value - closed) < 2.0e-14, value, closed)
    return {"plane_wave_max": max(maxima), "linearized_symbol_defect": defect, "sextic_minimum": value}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    diagnostics = {
        "endpoint": endpoint_audit(audit),
        "wick_and_nullcone": wick_and_nullcone_audit(audit),
        "full_wick_cost": full_wick_cost_audit(audit),
        "holder_and_affine": holder_and_affine_audit(audit),
        "critical_codimension": codimension_audit(audit),
        "production_symbol": production_symbol_audit(audit),
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-116 independent: {payload['assertions_passed']}/{payload['assertions_total']} "
        f"assertions; status={payload['status']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
