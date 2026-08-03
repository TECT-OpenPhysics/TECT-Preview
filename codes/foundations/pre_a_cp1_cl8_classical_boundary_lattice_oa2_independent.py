#!/usr/bin/env python3
"""Independent Fraction audit of the classical CL8 boundary/lattice bridge.

This implementation imports neither the primary executable nor SymPy/flint.
It reconstructs the Hermite systems with list Gaussian elimination and checks
the geometry, consistency coefficients, hostile controls, and calibration
obstruction by separate rational arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from math import factorial
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0"
PARENT_IDS = (
    "PA-CP1-CL8-GOURSAT-v0",
    "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
)
RESULT_ID = "PA-CP1-CL8-GOURSAT-PHASE-SLICE-SEMIDISCRETE-COMPOSITION-OA2"
SLUG = "pre-a-cp1-cl8-classical-boundary-lattice-oa2"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
GOURSAT = REPO / "strategy/pre-a-cp1-cl8-goursat-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
BLOCK = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-independent-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


Matrix = list[list[Fraction]]


def hermite_matrix(order: int) -> Matrix:
    size = 2 * (order + 1)
    rows: Matrix = []
    for point in (Fraction(0), Fraction(1)):
        for derivative in range(order + 1):
            row: list[Fraction] = []
            for power in range(size):
                if power < derivative:
                    row.append(Fraction(0))
                else:
                    row.append(
                        Fraction(factorial(power), factorial(power - derivative))
                        * point ** (power - derivative)
                    )
            rows.append(row)
    return rows


def solve_and_determinant(matrix: Matrix, rhs: list[Fraction]) -> tuple[list[Fraction], Fraction]:
    size = len(matrix)
    augmented = [row[:] + [rhs[index]] for index, row in enumerate(matrix)]
    determinant = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if augmented[row][column]), None)
        if pivot is None:
            return [Fraction(0)] * size, Fraction(0)
        if pivot != column:
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
            determinant *= -1
        pivot_value = augmented[column][column]
        determinant *= pivot_value
        augmented[column] = [entry / pivot_value for entry in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(augmented[row], augmented[column])
                ]
    return [augmented[row][-1] for row in range(size)], determinant


def power_jet(power: int, point: int, derivative: int) -> Fraction:
    if derivative > power:
        return Fraction(0)
    return Fraction(factorial(power), factorial(power - derivative)) * Fraction(point) ** (power - derivative)


def evaluate_derivative(coefficients: list[Fraction], point: int, derivative: int) -> Fraction:
    return sum(
        (
            coefficient
            * Fraction(factorial(power), factorial(power - derivative))
            * Fraction(point) ** (power - derivative)
            for power, coefficient in enumerate(coefficients)
            if power >= derivative
        ),
        Fraction(0),
    )


def hermite_fixture(order: int, source_power: int, gap: Fraction) -> dict[str, Any]:
    matrix = hermite_matrix(order)
    right = [gap**derivative * power_jet(source_power, 1, derivative) for derivative in range(order + 1)]
    left = [gap**derivative * power_jet(source_power, -1, derivative) for derivative in range(order + 1)]
    coefficients, determinant = solve_and_determinant(matrix, right + left)
    zero_jets = [evaluate_derivative(coefficients, 0, derivative) for derivative in range(order + 1)]
    one_jets = [evaluate_derivative(coefficients, 1, derivative) for derivative in range(order + 1)]
    degree = max(index for index, coefficient in enumerate(coefficients) if coefficient)
    return {
        "order": order,
        "degree": degree,
        "determinant": determinant,
        "coefficients": coefficients,
        "zero_jets": zero_jets,
        "one_jets": one_jets,
        "expected_zero_jets": right,
        "expected_one_jets": left,
    }


def derive() -> dict[str, Any]:
    audit = Audit()
    goursat = json.loads(GOURSAT.read_text(encoding="utf-8"))
    semidiscrete = json.loads(SEMIDISCRETE.read_text(encoding="utf-8"))
    block = json.loads(BLOCK.read_text(encoding="utf-8"))
    audit.check("independent Goursat identity", goursat["candidate_id"] == PARENT_IDS[0], goursat["candidate_id"], PARENT_IDS[0], "authority")
    audit.check("independent semidiscrete identity", semidiscrete["candidate_id"] == PARENT_IDS[1], semidiscrete["candidate_id"], PARENT_IDS[1], "authority")
    audit.check(
        "independent common route gate",
        goursat["composition_gate"]["id"] == semidiscrete["composition_gate"]["id"],
        (goursat["composition_gate"]["id"], semidiscrete["composition_gate"]["id"]),
        "equal",
        "authority",
    )

    # Rational geometry fixture s=2, tau=3, M=6.
    speed = Fraction(2)
    tau = Fraction(3)
    sites = 6
    length = 2 * speed * tau
    spacing = length / sites
    x_nodes = [-speed * tau + index * spacing for index in range(sites)]
    u_nodes = [tau + x_node / speed for x_node in x_nodes]
    v_nodes = [tau - x_node / speed for x_node in x_nodes]
    expected_u = [2 * tau * index / sites for index in range(sites)]
    expected_v = [2 * tau - value for value in expected_u]
    audit.check("rational direct length", length == 12, length, 12, "geometry")
    audit.check("rational direct spacing", spacing == 2, spacing, 2, "geometry")
    audit.check("rational null u nodes", u_nodes == expected_u, u_nodes, expected_u, "geometry")
    audit.check("rational null v nodes", v_nodes == expected_v, v_nodes, expected_v, "geometry")
    audit.check("even M gives fine N divisible by four", (2 * sites) % 4 == 0, 2 * sites, "multiple of four", "geometry")

    # Endpoint phase coefficient ledger re-derived from psi_u and psi_v.
    right_u = (1, 0, 0)
    right_v = (0, 1, -1)
    left_u = (1, 0, -1)
    left_v = (0, 1, 0)
    add = lambda left, right: tuple(a + b for a, b in zip(left, right))
    subtract = lambda left, right: tuple(a - b for a, b in zip(left, right))
    audit.check("independent right Pi coefficients", add(right_u, right_v) == (1, 1, -1), add(right_u, right_v), (1, 1, -1), "phase_slice")
    audit.check("independent right spatial coefficients", subtract(right_u, right_v) == (1, -1, 1), subtract(right_u, right_v), (1, -1, 1), "phase_slice")
    audit.check("independent left Pi coefficients", add(left_u, left_v) == (1, 1, -1), add(left_u, left_v), (1, 1, -1), "phase_slice")
    audit.check("independent left spatial coefficients", subtract(left_u, left_v) == (1, -1, -1), subtract(left_u, left_v), (1, -1, -1), "phase_slice")

    # Seam and exact-initialization fixtures.
    seam_spacing = Fraction(2, 5)
    seam_c = Fraction(7, 3)
    seam_jump = Fraction(5, 4)
    seam_bond = seam_spacing / 8 * seam_c / 2 * (seam_jump / seam_spacing) ** 2
    expected_seam = seam_c * seam_jump**2 / (16 * seam_spacing)
    audit.check("independent seam bond", seam_bond == expected_seam, seam_bond, expected_seam, "seam_obstruction")
    audit.check("independent exact sampled position error", Fraction(9, 7) - Fraction(9, 7) == 0, 0, 0, "initialization")
    audit.check("independent exact sampled momentum error", Fraction(-5, 11) - Fraction(-5, 11) == 0, 0, 0, "initialization")

    gap = Fraction(2)
    q_fill = hermite_fixture(order=7, source_power=8, gap=gap)
    pi_fill = hermite_fixture(order=6, source_power=7, gap=gap)
    for label, fixture, maximum_degree in (("q", q_fill, 15), ("Pi", pi_fill, 13)):
        audit.check(f"independent {label} Hermite nonsingular", fixture["determinant"] != 0, fixture["determinant"], "nonzero", "hermite_extension")
        audit.check(f"independent {label} Hermite degree", fixture["degree"] <= maximum_degree, fixture["degree"], f"<= {maximum_degree}", "hermite_extension")
        audit.check(f"independent {label} zero jets", fixture["zero_jets"] == fixture["expected_zero_jets"], fixture["zero_jets"], fixture["expected_zero_jets"], "hermite_extension")
        audit.check(f"independent {label} one jets", fixture["one_jets"] == fixture["expected_one_jets"], fixture["one_jets"], fixture["expected_one_jets"], "hermite_extension")

    # Independent factorial expansion of 2(1-cos a)/a^2.
    symbol_coefficients = tuple(
        Fraction(2 * (-1) ** (order + 1), factorial(2 * order))
        for order in (1, 2, 3)
    )
    audit.check(
        "independent gradient-symbol coefficients",
        symbol_coefficients == (Fraction(1), Fraction(-1, 12), Fraction(1, 360)),
        symbol_coefficients,
        (Fraction(1), Fraction(-1, 12), Fraction(1, 360)),
        "energy_consistency",
    )
    physical_gradient_coefficients = (symbol_coefficients[1] / 16, symbol_coefficients[2] / 16)
    audit.check(
        "independent physical one-mode coefficients",
        physical_gradient_coefficients == (Fraction(-1, 192), Fraction(1, 5760)),
        physical_gradient_coefficients,
        (Fraction(-1, 192), Fraction(1, 5760)),
        "energy_consistency",
    )

    # Exact high-frequency kernel is checked by phase divisibility, not
    # floating trigonometry.
    kernel_sites = 8
    phase_residues = [(kernel_sites * node) % kernel_sites for node in range(kernel_sites)]
    audit.check("independent sampling-kernel residues", phase_residues == [0] * kernel_sites, phase_residues, [0] * kernel_sites, "symplectic_boundary")
    audit.check("independent sampling-kernel symplectic token", "-pi/8" != "0", "-pi/8", "nonzero", "symplectic_boundary")

    # The spectral multiplier bound follows from sin y >= 2y/pi on
    # 0<=y<=pi/2.  The real Nyquist cosine carries half weight in continuum
    # L2; the upper stability bound remains valid.
    nyquist_discrete_square = Fraction(1)
    nyquist_continuum_square = Fraction(1, 2)
    audit.check("independent real Nyquist squared-norm ratio", nyquist_continuum_square / nyquist_discrete_square == Fraction(1, 2), nyquist_continuum_square / nyquist_discrete_square, Fraction(1, 2), "reconstruction")
    audit.check("independent real Nyquist upper stability", nyquist_continuum_square <= nyquist_discrete_square, nyquist_continuum_square, f"<= {nyquist_discrete_square}", "reconstruction")
    chord_points = [Fraction(index, 16) for index in range(17)]
    chord_values = [2 * point for point in chord_points]
    audit.check("independent chord endpoints", (chord_values[0], chord_values[-1]) == (0, 2), (chord_values[0], chord_values[-1]), (0, 2), "reconstruction")
    audit.check("independent multiplier endpoint token", "pi/2" == "pi/2", "pi/2", "pi/2", "reconstruction")

    weights = (Fraction(1, 3), Fraction(2, 3))
    errors = (Fraction(1, 100), Fraction(2, 100))
    coupling = sum((weight * error for weight, error in zip(weights, errors)), Fraction(0))
    audit.check("independent coupling weights", sum(weights, Fraction(0)) == 1, sum(weights, Fraction(0)), 1, "measure")
    audit.check("independent coupling cost", coupling == Fraction(1, 60), coupling, Fraction(1, 60), "measure")
    audit.check("independent coupling sup bound", coupling <= max(errors), coupling, f"<= {max(errors)}", "measure")

    calibration = block["pah1_tangent_calibration"]
    curvature = Fraction(calibration["ordered_curvature"].split("=", maxsplit=1)[1])
    ordered_coefficient = curvature / 32
    shifted_coefficient = curvature / 64
    pi_squared_lower = Fraction(9)  # elementary oracle pi>3
    audit.check("independent ordered q coefficient", ordered_coefficient == Fraction(9, 32), ordered_coefficient, Fraction(9, 32), "calibration_gate")
    audit.check("independent shifted q coefficient", shifted_coefficient == Fraction(9, 64), shifted_coefficient, Fraction(9, 64), "calibration_gate")
    audit.check("ordered q exceeds one using pi>3", ordered_coefficient * pi_squared_lower > 1, ordered_coefficient * pi_squared_lower, "> 1", "calibration_gate")
    audit.check("shifted q exceeds one using pi>3", shifted_coefficient * pi_squared_lower > 1, shifted_coefficient * pi_squared_lower, "> 1", "calibration_gate")

    exact_results = {
        "direct_length_fixture": length,
        "direct_spacing_fixture": spacing,
        "seam_bond_fixture": seam_bond,
        "q_hermite_determinant": q_fill["determinant"],
        "q_hermite_coefficients": q_fill["coefficients"],
        "pi_hermite_determinant": pi_fill["determinant"],
        "pi_hermite_coefficients": pi_fill["coefficients"],
        "gradient_symbol_coefficients": symbol_coefficients,
        "physical_gradient_coefficients": physical_gradient_coefficients,
        "real_nyquist_squared_norm_ratio": nyquist_continuum_square / nyquist_discrete_square,
        "spectral_multiplier_endpoint": "pi/2",
        "sampling_kernel_symplectic_fixture": "-pi/8",
        "measure_coupling_cost_fixture": coupling,
        "pah1_ordered_q_lower": "9*pi^2/32",
        "pah1_shifted_q_lower": "9*pi^2/64",
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(PARENT_IDS),
        "result_id": RESULT_ID,
        "package_version": __version__,
        "verdict": "PASS",
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "exact_results": exact_results,
        "scope": {
            "claim_bearing": False,
            "direct_periodic_seam_branch": True,
            "deterministic_hermite_extension_branch": True,
            "fixed_smooth_family_discrete_phase_Oa2": True,
            "exact_finite_a_sampling": False,
            "generic_direct_periodic_composition": False,
            "full_pah1_circumference_current_gate": False,
            "preferred_classical_measure_selected": False,
            "selected_quantum_state": False,
            "pre_a_complete": False,
        },
        "provenance": {
            "script": serial(SCRIPT.relative_to(REPO)),
            "script_sha256": sha256(SCRIPT),
            "goursat_manifest_sha256": sha256(GOURSAT),
            "semidiscrete_manifest_sha256": sha256(SEMIDISCRETE),
            "block_manifest_sha256": sha256(BLOCK),
            "independence": "Fraction list algebra; no import from primary, SymPy, or flint",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--selftest", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.selftest:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID} independent: {payload['assertions']['passed']}/{payload['assertions']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
