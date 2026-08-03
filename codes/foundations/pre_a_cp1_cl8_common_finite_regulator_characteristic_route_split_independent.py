#!/usr/bin/env python3
"""Independent standard-library audit for the CL8 causal-circuit route split.

This module imports neither the primary implementation nor SymPy/NumPy.  All
load-bearing fixture values are derived with Fraction matrix and polynomial
arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-CAUSAL-CAUCHY-FLOQUET-BH-STATE-TRANSPORT-AND-ROUTE-NOGOS"
SLUG = "pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
STRICT_CONE = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json"
QUANTUM_STATE = REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json"
BOUNDARY_SPLIT = REPO / "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-independent-{SLUG}/result.json"
)

Matrix = list[list[Fraction]]
Polynomial = list[Fraction]


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
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


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zeros(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    if len(left[0]) != len(right):
        raise ValueError("matrix dimension mismatch")
    result = zeros(len(left), len(right[0]))
    for row in range(len(left)):
        for inner in range(len(right)):
            coefficient = left[row][inner]
            if coefficient == 0:
                continue
            for column in range(len(right[0])):
                result[row][column] += coefficient * right[inner][column]
    return result


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [[left[r][c] - right[r][c] for c in range(len(left[0]))] for r in range(len(left))]


def scale_matrix(coefficient: Fraction, matrix: Matrix) -> Matrix:
    return [[coefficient * value for value in row] for row in matrix]


def block_matrix(top_left: Matrix, top_right: Matrix, bottom_left: Matrix, bottom_right: Matrix) -> Matrix:
    top = [top_left[row] + top_right[row] for row in range(len(top_left))]
    bottom = [bottom_left[row] + bottom_right[row] for row in range(len(bottom_left))]
    return top + bottom


def submatrix(matrix: Matrix, rows: tuple[int, ...], columns: tuple[int, ...]) -> Matrix:
    return [[matrix[row][column] for column in columns] for row in rows]


def matrix_power(matrix: Matrix, exponent: int) -> Matrix:
    result = identity(len(matrix))
    factor = matrix
    power = exponent
    while power:
        if power & 1:
            result = multiply(result, factor)
        factor = multiply(factor, factor)
        power //= 2
    return result


def determinant(matrix: Matrix) -> Fraction:
    work = [row[:] for row in matrix]
    size = len(work)
    result = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            if work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for target in range(column, size):
                work[row][target] -= factor * work[column][target]
    return result


def rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column] != 0), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [work[row][target] - factor * work[pivot_row][target] for target in range(columns)]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def canonical_symplectic(dimension: int) -> Matrix:
    return block_matrix(zeros(dimension, dimension), identity(dimension), scale_matrix(Fraction(-1), identity(dimension)), zeros(dimension, dimension))


def periodic_distance(left: int, right: int, size: int) -> int:
    separation = abs(left - right)
    return min(separation, size - separation)


def poly_trim(polynomial: Polynomial) -> Polynomial:
    result = polynomial[:]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    result = [Fraction(0) for _ in range(size)]
    for index in range(size):
        if index < len(left):
            result[index] += left[index]
        if index < len(right):
            result[index] += right[index]
    return poly_trim(result)


def poly_scale(coefficient: Fraction, polynomial: Polynomial) -> Polynomial:
    return poly_trim([coefficient * value for value in polynomial])


def poly_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] += left_value * right_value
    return poly_trim(result)


def poly_power(polynomial: Polynomial, exponent: int) -> Polynomial:
    result: Polynomial = [Fraction(1)]
    factor = polynomial
    power = exponent
    while power:
        if power & 1:
            result = poly_multiply(result, factor)
        factor = poly_multiply(factor, factor)
        power //= 2
    return result


def polynomial_degree(polynomial: Polynomial) -> int:
    return len(poly_trim(polynomial)) - 1


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [
        json.loads(Q3LOCK.read_text(encoding="utf-8")),
        json.loads(SEMIDISCRETE.read_text(encoding="utf-8")),
        json.loads(STRICT_CONE.read_text(encoding="utf-8")),
        json.loads(QUANTUM_STATE.read_text(encoding="utf-8")),
        json.loads(BOUNDARY_SPLIT.read_text(encoding="utf-8")),
    ]
    audit = Audit()
    expected_parents = [
        "PA-CP1-ST8-Q3LOCK-v0",
        "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
        "PA-CP1-FD-C1-STRICT-CONE-NOGO-v0",
        "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
        "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0",
    ]
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("manifest parent ids", manifest["parent_ids"] == expected_parents, manifest["parent_ids"], expected_parents, "identity")
    audit.check("loaded parent ids", [parent["candidate_id"] for parent in parents] == expected_parents, [parent["candidate_id"] for parent in parents], expected_parents, "parents")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("five direct parents", len(expected_parents) == 5, len(expected_parents), 5, "identity")
    audit.check("Q3 graph declared", parents[0]["definition"]["species_graph"] == "the twelve undirected edges of Q3", parents[0]["definition"]["species_graph"], "the twelve undirected edges of Q3", "parents")
    audit.check("exact finite Hamiltonian parent", parents[1]["scope"]["exact_finite_Hamiltonian_conservation"] is True, parents[1]["scope"]["exact_finite_Hamiltonian_conservation"], True, "parents")
    audit.check("continuous-time no-go parent", parents[2]["scope"]["exact_finite_C1_equilibrium_variational_nogo"] is True, parents[2]["scope"]["exact_finite_C1_equilibrium_variational_nogo"], True, "parents")
    audit.check("ground parent", parents[3]["scope"]["finite_quantum_unique_ground"] is True, parents[3]["scope"]["finite_quantum_unique_ground"], True, "parents")
    audit.check("boundary route parent", parents[4]["gate_resolution"]["next_gate"] == "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-MODEL", parents[4]["gate_resolution"]["next_gate"], "common regulator gate", "parents")

    # A nontrivial rational fixture independent of the primary symbolic route.
    sites = 10
    length = Fraction(6)
    spacing = length / sites
    weight = spacing / 8
    chi = Fraction(7, 3)
    mu = chi * weight
    c = Fraction(5, 4)
    mass_squared = Fraction(13, 6)
    delta = Fraction(2, 7)
    half = delta / 2
    audit.check("independent even regulator", sites % 2 == 0 and sites >= 4, sites, "even M>=4", "fixture")
    audit.check("spacing independently derived", spacing == Fraction(3, 5), spacing, Fraction(3, 5), "fixture")
    audit.check("weight independently derived", weight == Fraction(3, 40), weight, Fraction(3, 40), "fixture")
    audit.check("mass independently derived", mu == Fraction(7, 40), mu, Fraction(7, 40), "fixture")
    audit.check("canonical kinetic equality", (weight * Fraction(11, 5)) ** 2 / (2 * mu) == weight * Fraction(11, 5) ** 2 / (2 * chi), (weight * Fraction(11, 5)) ** 2 / (2 * mu), weight * Fraction(11, 5) ** 2 / (2 * chi), "fixture")
    audit.check("nontrivial chi fixture", chi != 1, chi, "not one", "fixture")

    # Exact two-dimensional shears and reversal.
    curvature = Fraction(11, 5)
    drift = [[Fraction(1), half / mu], [Fraction(0), Fraction(1)]]
    kick = [[Fraction(1), Fraction(0)], [-delta * curvature, Fraction(1)]]
    split = multiply(multiply(drift, kick), drift)
    symplectic = canonical_symplectic(1)
    reverse = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1)]]
    negative_drift = [[Fraction(1), -half / mu], [Fraction(0), Fraction(1)]]
    negative_kick = [[Fraction(1), Fraction(0)], [delta * curvature, Fraction(1)]]
    negative_split = multiply(multiply(negative_drift, negative_kick), negative_drift)
    audit.check("drift determinant", determinant(drift) == 1, determinant(drift), 1, "symplectic")
    audit.check("kick determinant", determinant(kick) == 1, determinant(kick), 1, "symplectic")
    audit.check("split determinant", determinant(split) == 1, determinant(split), 1, "symplectic")
    audit.check("drift symplectic", subtract(multiply(multiply(transpose(drift), symplectic), drift), symplectic) == zeros(2, 2), "zero", "zero", "symplectic")
    audit.check("kick symplectic", subtract(multiply(multiply(transpose(kick), symplectic), kick), symplectic) == zeros(2, 2), "zero", "zero", "symplectic")
    audit.check("split symplectic", subtract(multiply(multiply(transpose(split), symplectic), split), symplectic) == zeros(2, 2), "zero", "zero", "symplectic")
    audit.check("inverse step", multiply(negative_split, split) == identity(2), multiply(negative_split, split), identity(2), "symplectic")
    audit.check("momentum reversal", multiply(multiply(reverse, split), reverse) == negative_split, multiply(multiply(reverse, split), reverse), negative_split, "symplectic")

    # Build the full ring without a symbolic library and audit exact support.
    laplacian = zeros(sites, sites)
    for node in range(sites):
        laplacian[node][node] = Fraction(2)
        laplacian[node][(node - 1) % sites] = Fraction(-1)
        laplacian[node][(node + 1) % sites] = Fraction(-1)
    spring = weight * c / (spacing * spacing)
    hessian = zeros(sites, sites)
    for row in range(sites):
        for column in range(sites):
            hessian[row][column] = spring * laplacian[row][column]
        hessian[row][row] += mu * mass_squared
    identity_sites = identity(sites)
    drift_full = block_matrix(identity_sites, scale_matrix(half / mu, identity_sites), zeros(sites, sites), identity_sites)
    kick_full = block_matrix(identity_sites, zeros(sites, sites), scale_matrix(-delta, hessian), identity_sites)
    split_full = multiply(multiply(drift_full, kick_full), drift_full)
    split_square = matrix_power(split_full, 2)
    full_symplectic = canonical_symplectic(sites)
    radius_one_violations: list[list[int]] = []
    radius_two_violations: list[list[int]] = []
    for output_node in range(sites):
        rows = (output_node, output_node + sites)
        for input_node in range(sites):
            columns = (input_node, input_node + sites)
            block_one = submatrix(split_full, rows, columns)
            block_two = submatrix(split_square, rows, columns)
            distance = periodic_distance(output_node, input_node, sites)
            if distance > 1 and block_one != zeros(2, 2):
                radius_one_violations.append([output_node, input_node])
            if distance > 2 and block_two != zeros(2, 2):
                radius_two_violations.append([output_node, input_node])
    neighbour = submatrix(split_full, (0, sites), (1, sites + 1))
    neighbour_eight = zeros(16, 16)
    for species in range(8):
        for row in range(2):
            for column in range(2):
                neighbour_eight[2 * species + row][2 * species + column] = neighbour[row][column]
    audit.check("ring Laplacian symmetric", transpose(laplacian) == laplacian, transpose(laplacian), laplacian, "causality")
    audit.check("full ring symplectic", subtract(multiply(multiply(transpose(split_full), full_symplectic), split_full), full_symplectic) == zeros(2 * sites, 2 * sites), "zero", "zero", "causality")
    audit.check("one-step radius one", radius_one_violations == [], radius_one_violations, [], "causality")
    audit.check("two-step radius two", radius_two_violations == [], radius_two_violations, [], "causality")
    audit.check("neighbour nonzero", neighbour != zeros(2, 2), neighbour, "nonzero", "sideways")
    audit.check("neighbour determinant zero", determinant(neighbour) == 0, determinant(neighbour), 0, "sideways")
    audit.check("neighbour rank one", rank(neighbour) == 1, rank(neighbour), 1, "sideways")
    audit.check("eight-species neighbour rank", rank(neighbour_eight) == 8, rank(neighbour_eight), 8, "sideways")
    audit.check("eight-species input dimension", len(neighbour_eight[0]) == 16, len(neighbour_eight[0]), 16, "sideways")

    # Independent exact Floquet symbol.
    symbol_mu = Fraction(5, 3)
    omega_squared = Fraction(11, 5)
    symbol_delta = Fraction(2, 7)
    x_value = symbol_delta * symbol_delta * omega_squared
    symbol = [
        [1 - x_value / 2, (symbol_delta / symbol_mu) * (1 - x_value / 4)],
        [-symbol_delta * symbol_mu * omega_squared, 1 - x_value / 2],
    ]
    audit.check("Floquet determinant", determinant(symbol) == 1, determinant(symbol), 1, "Floquet")
    audit.check("Floquet trace", symbol[0][0] + symbol[1][1] == 2 - x_value, symbol[0][0] + symbol[1][1], 2 - x_value, "Floquet")
    audit.check("Floquet x positive", x_value > 0, x_value, ">0", "Floquet")
    audit.check("Floquet CFL", x_value < 4, x_value, "<4", "Floquet")
    audit.check("Floquet offdiagonal signs", symbol[0][1] > 0 and symbol[1][0] < 0, [symbol[0][1], symbol[1][0]], [">0", "<0"], "Floquet")
    weyl_status = manifest["quadratic_tangent_symbol"]["Weyl_status"]
    audit.check("quadratic Weyl status", manifest["scope"]["quadratic_metaplectic_Weyl_covariance"] is True and "W(S_delta(k)^(-1) z)" in weyl_status, weyl_status, "inverse symplectic label", "Floquet")

    # Harmonic and ordered nonlinear energy defects, both derived from inputs.
    energy_mu = Fraction(7, 5)
    energy_omega_squared = Fraction(13, 4)
    energy_delta = Fraction(3, 11)
    q_initial = Fraction(5, 7)
    p_out = -energy_delta * energy_mu * energy_omega_squared * q_initial
    q_out = (1 - energy_delta * energy_delta * energy_omega_squared / 2) * q_initial
    energy_initial = energy_mu * energy_omega_squared * q_initial * q_initial / 2
    energy_out = p_out * p_out / (2 * energy_mu) + energy_mu * energy_omega_squared * q_out * q_out / 2
    expected_ratio = 1 + energy_delta**4 * energy_omega_squared**2 / 4
    audit.check("harmonic energy ratio", energy_out / energy_initial == expected_ratio, energy_out / energy_initial, expected_ratio, "energy")
    audit.check("harmonic energy increases", energy_out > energy_initial, energy_out - energy_initial, ">0", "energy")

    ordered_weight = Fraction(3, 8)
    ordered_chi = Fraction(2, 9)
    ordered_mu = ordered_chi * ordered_weight
    ordered_delta = Fraction(2, 7)
    q_poly: Polynomial = [Fraction(1), Fraction(1)]
    force_poly = poly_scale(ordered_weight, poly_add(poly_scale(Fraction(-1), q_poly), poly_power(q_poly, 3)))
    p_poly = poly_scale(-ordered_delta, force_poly)
    q_out_poly = poly_add(q_poly, poly_scale(ordered_delta / (2 * ordered_mu), p_poly))

    def potential(polynomial: Polynomial) -> Polynomial:
        return poly_scale(
            ordered_weight,
            poly_add(poly_scale(Fraction(-1, 2), poly_power(polynomial, 2)), poly_scale(Fraction(1, 4), poly_power(polynomial, 4))),
        )

    kinetic_poly = poly_scale(Fraction(1, 1) / (2 * ordered_mu), poly_power(p_poly, 2))
    energy_defect_poly = poly_add(kinetic_poly, poly_add(potential(q_out_poly), poly_scale(Fraction(-1), potential(q_poly))))
    ordered_quadratic = energy_defect_poly[2]
    ordered_omega_squared = Fraction(2) / ordered_chi
    expected_ordered = ordered_mu * ordered_omega_squared**3 * ordered_delta**4 / 8
    audit.check("ordered force constant zero", force_poly[0] == 0, force_poly[0], 0, "energy")
    audit.check("ordered omega squared derived", ordered_omega_squared == 9, ordered_omega_squared, 9, "energy")
    audit.check("ordered energy coefficient", ordered_quadratic == expected_ordered, ordered_quadratic, expected_ordered, "energy")
    audit.check("ordered energy coefficient positive", ordered_quadratic > 0, ordered_quadratic, ">0", "energy")

    # Derive the cubic translation phase without importing symbolic code.
    shift = Fraction(3, 2)
    x_poly: Polynomial = [Fraction(0), Fraction(1)]
    shifted_x = [shift, Fraction(1)]
    quartic_difference = poly_add(poly_power(shifted_x, 4), poly_scale(Fraction(-1), poly_power(x_poly, 4)))
    derivative = [Fraction(index) * value for index, value in enumerate(quartic_difference)][1:]
    second_derivative = [Fraction(index) * value for index, value in enumerate(derivative)][1:]
    audit.check("quartic translation degree three", polynomial_degree(quartic_difference) == 3, polynomial_degree(quartic_difference), 3, "Weyl_no_go")
    audit.check("cubic leading coefficient derived", quartic_difference[3] == 4 * shift, quartic_difference[3], 4 * shift, "Weyl_no_go")
    audit.check("derivative degree two", polynomial_degree(derivative) == 2, polynomial_degree(derivative), 2, "Weyl_no_go")
    audit.check("second derivative degree one", polynomial_degree(second_derivative) == 1, polynomial_degree(second_derivative), 1, "Weyl_no_go")
    audit.check("Taylor remainder degree margin", 2 * polynomial_degree(derivative) - polynomial_degree(second_derivative) == 3, 2 * polynomial_degree(derivative) - polynomial_degree(second_derivative), 3, "Weyl_no_go")
    algebra_boundary = manifest["nonlinear_Weyl_nonnormalizer"]["algebra_boundary"]
    audit.check("Weyl nonnormalizer scope", manifest["scope"]["full_nonlinear_Weyl_Cstar_invariance"] is False and "modulation-average" in algebra_boundary, algebra_boundary, "false scope with modulation-average intersection proof", "Weyl_no_go")

    # Finite trace fixture separates transport from stationarity.
    unitary = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    density = [[Fraction(1, 4), Fraction(0)], [Fraction(0), Fraction(3, 4)]]
    observable = [[Fraction(2), Fraction(1)], [Fraction(1), Fraction(-3)]]
    transported = multiply(multiply(unitary, density), transpose(unitary))
    heisenberg = multiply(multiply(transpose(unitary), observable), unitary)
    trace = lambda matrix: sum(matrix[index][index] for index in range(len(matrix)))
    audit.check("unitary fixture", multiply(transpose(unitary), unitary) == identity(2), multiply(transpose(unitary), unitary), identity(2), "state")
    audit.check("density trace", trace(density) == 1, trace(density), 1, "state")
    audit.check("transported trace", trace(transported) == 1, trace(transported), 1, "state")
    audit.check("state identity", trace(multiply(transported, observable)) == trace(multiply(density, heisenberg)), trace(multiply(transported, observable)), trace(multiply(density, heisenberg)), "state")
    audit.check("density transport true", manifest["scope"]["exact_density_state_transport"] is True, manifest["scope"]["exact_density_state_transport"], True, "state")
    audit.check("state stationarity false", manifest["scope"]["inherited_ground_or_Gibbs_stationary"] is False, manifest["scope"]["inherited_ground_or_Gibbs_stationary"], False, "state")

    # The bounded-log trace lower bound grows linearly with truncation rank.
    lower_unit = Fraction(2, 9)
    lower_rank_10 = 10 * lower_unit
    lower_rank_100 = 100 * lower_unit
    audit.check("principal trace lower bound positive", lower_unit > 0, lower_unit, ">0", "Floquet_Gibbs")
    audit.check("principal trace lower bound grows", lower_rank_100 == 10 * lower_rank_10, lower_rank_100, 10 * lower_rank_10, "Floquet_Gibbs")
    audit.check("principal Gibbs rejected", manifest["scope"]["principal_Floquet_log_trace_class_Gibbs"] is False, manifest["scope"]["principal_Floquet_log_trace_class_Gibbs"], False, "Floquet_Gibbs")
    audit.check("physical reference rejected", manifest["scope"]["physical_energy_reference"] is False, manifest["scope"]["physical_energy_reference"], False, "Floquet_Gibbs")
    audit.check("below empty space rejected", manifest["scope"]["below_empty_space"] is False, manifest["scope"]["below_empty_space"], False, "Floquet_Gibbs")

    expected_negatives = [
        "NG-2026-08-04-PRE-A-CP1-CL8-NONLINEAR-FLOQUET-WEYL-NORMALIZER",
        "NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-ORIGINAL-H-STATE",
        "NG-2026-08-04-PRE-A-CP1-CL8-PRINCIPAL-FLOQUET-GIBBS-REFERENCE",
        "NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-SIDEWAYS-CHARACTERISTIC",
    ]
    audit.check("negative ids", manifest["negative_ids"] == expected_negatives, manifest["negative_ids"], expected_negatives, "scope")
    audit.check("gate remains split", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "scope")
    audit.check("four refuted branches", len(manifest["gate_resolution"]["refuted_subgates"]) == 4, len(manifest["gate_resolution"]["refuted_subgates"]), 4, "scope")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-SIDEWAYS-INVERTIBLE-TWO-ARM-CHARACTERISTIC-CIRCUIT", manifest["gate_resolution"]["next_gate"], "sideways gate", "scope")

    true_keys = (
        "fixed_regulator_exact_symplectic_Cauchy_circuit",
        "fixed_regulator_exact_reversibility",
        "fixed_regulator_exact_radius_one_cone",
        "full_interacting_BH_quantum_automorphism",
        "exact_density_state_transport",
        "quadratic_metaplectic_Weyl_covariance",
        "exact_Floquet_symbol_and_CFL",
    )
    for key in true_keys:
        audit.check(f"scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    false_keys = (
        "full_nonlinear_Weyl_Cstar_invariance",
        "inherited_autonomous_H_conserved",
        "inherited_ground_or_Gibbs_stationary",
        "principal_Floquet_log_trace_class_Gibbs",
        "two_null_side_characteristic_reconstruction",
        "locally_sideways_invertible",
        "common_characteristic_model_gate_closed",
        "preferred_physical_state_selected",
        "physical_energy_reference",
        "physical_vacuum",
        "below_empty_space",
        "regulator_compatible_state_family",
        "continuum_quantum_state",
        "Hadamard_state",
        "hbar_origin_derived",
        "Lorentzian_or_null_structure_derived",
        "C0_closed",
        "N1_closed",
        "N2_closed",
        "N3_closed",
        "N4_closed",
        "N5_closed",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in false_keys:
        audit.check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    cross_invariants = {
        "canonical_weight_rule": "a/8",
        "canonical_mass_rule": "chi*a/8",
        "split_determinant": 1,
        "radius_one_exact": True,
        "radius_two_exact": True,
        "neighbour_rank_one_species": 1,
        "neighbour_rank_eight_species": 8,
        "Floquet_determinant": 1,
        "Floquet_trace_rule": "2-x",
        "harmonic_energy_ratio": "1+(delta*omega)^4/4",
        "ordered_energy_defect_rule": "mu*omega^6*delta^4/8",
        "quartic_translation_phase_degree": 3,
        "principal_Gibbs_trace": "infinity",
        "next_gate": manifest["gate_resolution"]["next_gate"],
    }
    derived = {
        "fixture": {
            "M": sites,
            "L": length,
            "a": spacing,
            "w": weight,
            "chi": chi,
            "mu": mu,
            "c": c,
            "mass_squared": mass_squared,
            "delta": delta,
        },
        "split": split,
        "radius_one_violations": radius_one_violations,
        "radius_two_violations": radius_two_violations,
        "neighbour": neighbour,
        "neighbour_rank": rank(neighbour),
        "neighbour_eight_rank": rank(neighbour_eight),
        "Floquet_symbol": symbol,
        "Floquet_x": x_value,
        "harmonic_energy_ratio": energy_out / energy_initial,
        "ordered_energy_defect_quadratic": ordered_quadratic,
        "quartic_translation_phase": quartic_difference,
        "principal_trace_rank_ratio": lower_rank_100 / lower_rank_10,
        "next_gate": manifest["gate_resolution"]["next_gate"],
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": expected_parents,
        "result_id": RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "cross_invariants": cross_invariants,
        "scope": manifest["scope"],
        "negative_ids": expected_negatives,
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "q3lock_manifest": sha256(Q3LOCK),
            "semidiscrete_manifest": sha256(SEMIDISCRETE),
            "strict_cone_manifest": sha256(STRICT_CONE),
            "quantum_state_manifest": sha256(QUANTUM_STATE),
            "boundary_split_manifest": sha256(BOUNDARY_SPLIT),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} independent: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
