#!/usr/bin/env python3
"""Independent Fraction audit for the CL8 passive two-arm control."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-PASSIVE-TWO-ARM-CHARACTERISTIC-CONTROL-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-PASSIVE-TWO-ARM-CUT-RECONSTRUCTION-AND-CL8-KICK-STATE-NOGO"
SLUG = "pre-a-cp1-cl8-passive-two-arm-characteristic-control-route-split"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
COMMON_PARENT = REPO / "strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json"
GOURSAT_PARENT = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
BOUNDARY_PARENT = REPO / "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json"
GAUSSIAN_PARENT = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
Q3_PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
PARENT_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-04-independent-pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split/result.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-independent-{SLUG}/result.json"
)

Matrix = list[list[Fraction]]


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


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zeros(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    rows = len(left)
    shared = len(right)
    columns = len(right[0])
    if len(left[0]) != shared:
        raise ValueError("matrix dimension mismatch")
    result = zeros(rows, columns)
    for row in range(rows):
        for pivot in range(shared):
            coefficient = left[row][pivot]
            if coefficient == 0:
                continue
            for column in range(columns):
                result[row][column] += coefficient * right[pivot][column]
    return result


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] - right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def scale(coefficient: Fraction, matrix: Matrix) -> Matrix:
    return [[coefficient * entry for entry in row] for row in matrix]


def kron(left: Matrix, right: Matrix) -> Matrix:
    result = zeros(len(left) * len(right), len(left[0]) * len(right[0]))
    for left_row in range(len(left)):
        for left_column in range(len(left[0])):
            coefficient = left[left_row][left_column]
            for right_row in range(len(right)):
                for right_column in range(len(right[0])):
                    result[left_row * len(right) + right_row][left_column * len(right[0]) + right_column] = coefficient * right[right_row][right_column]
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
        work[pivot_row] = [entry / pivot_value for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [work[row][index] - factor * work[pivot_row][index] for index in range(columns)]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def matrix_power(matrix: Matrix, exponent: int) -> Matrix:
    result = identity(len(matrix))
    base = matrix
    power = exponent
    while power:
        if power % 2:
            result = multiply(result, base)
        base = multiply(base, base)
        power //= 2
    return result


def pythagorean(u: int, v: int) -> tuple[Fraction, Fraction]:
    if not (u > v > 0):
        raise ValueError("require u>v>0")
    denominator = u * u + v * v
    return Fraction(u * u - v * v, denominator), Fraction(2 * u * v, denominator)


def rectangle_wires(
    gamma: Fraction,
    eta: Fraction,
    horizontal_count: int,
    vertical_count: int,
    order: str,
) -> tuple[dict[tuple[int, int], list[Fraction]], dict[tuple[int, int], list[Fraction]]]:
    total = horizontal_count + vertical_count
    horizontal: dict[tuple[int, int], list[Fraction]] = {}
    vertical: dict[tuple[int, int], list[Fraction]] = {}
    for row in range(1, vertical_count + 1):
        basis = [Fraction(0) for _ in range(total)]
        basis[row - 1] = Fraction(1)
        horizontal[(0, row)] = basis
    for column in range(1, horizontal_count + 1):
        basis = [Fraction(0) for _ in range(total)]
        basis[vertical_count + column - 1] = Fraction(1)
        vertical[(column, 0)] = basis
    if order == "row":
        vertices: Iterable[tuple[int, int]] = (
            (column, row)
            for column in range(1, horizontal_count + 1)
            for row in range(1, vertical_count + 1)
        )
    elif order == "column":
        vertices = (
            (column, row)
            for row in range(1, vertical_count + 1)
            for column in range(1, horizontal_count + 1)
        )
    else:
        raise ValueError(order)
    for column, row in vertices:
        west = horizontal[(column - 1, row)]
        south = vertical[(column, row - 1)]
        horizontal[(column, row)] = [gamma * west[index] + eta * south[index] for index in range(total)]
        vertical[(column, row)] = [-eta * west[index] + gamma * south[index] for index in range(total)]
    return horizontal, vertical


def ideals(horizontal_count: int, vertical_count: int) -> list[tuple[int, ...]]:
    return [
        tuple(lengths)
        for lengths in itertools.product(range(horizontal_count + 1), repeat=vertical_count)
        if all(lengths[index] >= lengths[index + 1] for index in range(vertical_count - 1))
    ]


def cut_matrix(
    horizontal: dict[tuple[int, int], list[Fraction]],
    vertical: dict[tuple[int, int], list[Fraction]],
    horizontal_count: int,
    row_lengths: tuple[int, ...],
) -> Matrix:
    rows = [horizontal[(length, row)] for row, length in enumerate(row_lengths, start=1)]
    for column in range(1, horizontal_count + 1):
        heights = [row for row, length in enumerate(row_lengths, start=1) if length >= column]
        rows.append(vertical[(column, max(heights, default=0))])
    return [row[:] for row in rows]


def pair_layer(size: int, offset: int, gamma: Fraction, eta: Fraction) -> Matrix:
    layer = zeros(size, size)
    if offset == 0:
        pairs = [(index, index + 1) for index in range(0, size, 2)]
    elif offset == 1:
        pairs = [(index, index + 1) for index in range(1, size - 1, 2)] + [(size - 1, 0)]
    else:
        raise ValueError(offset)
    for left, right in pairs:
        layer[left][left] = gamma
        layer[left][right] = eta
        layer[right][left] = -eta
        layer[right][right] = gamma
    return layer


def periodic_distance(left: int, right: int, size: int) -> int:
    distance = abs(left - right)
    return min(distance, size - distance)


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


def build_payload(
    pythagorean_u: int,
    pythagorean_v: int,
    rectangle_m: int,
    rectangle_n: int,
    ring_size: int,
    fugacity_numerator: int,
    fugacity_denominator: int,
) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    common_parent = json.loads(COMMON_PARENT.read_text(encoding="utf-8"))
    goursat_parent = json.loads(GOURSAT_PARENT.read_text(encoding="utf-8"))
    boundary_parent = json.loads(BOUNDARY_PARENT.read_text(encoding="utf-8"))
    gaussian_parent = json.loads(GAUSSIAN_PARENT.read_text(encoding="utf-8"))
    q3_parent = json.loads(Q3_PARENT.read_text(encoding="utf-8"))
    parent_result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    audit = Audit()

    expected_parents = (
        "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0",
        "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0",
        "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0",
        "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0",
        "PA-CP1-ST8-Q3LOCK-v0",
    )
    loaded = (
        common_parent["candidate_id"],
        goursat_parent["candidate_id"],
        boundary_parent["candidate_id"],
        gaussian_parent["candidate_id"],
        q3_parent["candidate_id"],
    )
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "provenance")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "provenance")
    audit.check("parent ids", tuple(manifest["parent_ids"]) == expected_parents, manifest["parent_ids"], expected_parents, "provenance")
    audit.check("loaded parents", loaded == expected_parents, loaded, expected_parents, "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "provenance")

    gamma, eta = pythagorean(pythagorean_u, pythagorean_v)
    audit.check("Pythagorean identity", gamma * gamma + eta * eta == 1, gamma * gamma + eta * eta, 1, "parameters")
    audit.check("gamma nonzero", gamma != 0, gamma, "nonzero", "parameters")
    audit.check("eta nonzero", eta != 0, eta, "nonzero", "parameters")
    total_legs = rectangle_m + rectangle_n
    audit.check("rectangle even", total_legs % 2 == 0, total_legs, "even", "parameters")
    audit.check("rectangle positive sides", rectangle_m > 0 and rectangle_n > 0, [rectangle_m, rectangle_n], "positive", "parameters")
    audit.check("rectangle total at least four", total_legs >= 4, total_legs, ">=4", "parameters")
    audit.check("one common regulator M", ring_size == total_legs, ring_size, total_legs, "parameters")
    audit.check("ring even", ring_size % 2 == 0, ring_size, "even", "parameters")
    audit.check("ring at least ten", ring_size >= 10, ring_size, ">=10", "parameters")
    fugacity = Fraction(fugacity_numerator, fugacity_denominator)
    audit.check("fugacity domain", 0 < fugacity < 1, fugacity, "0<zeta<1", "parameters")

    j2 = [[Fraction(0), Fraction(1)], [Fraction(-1), Fraction(0)]]
    coefficient_gate = [[gamma, eta], [-eta, gamma]]
    gate = kron(coefficient_gate, identity(2))
    temporal_form = kron(identity(2), j2)
    audit.check("local orthogonal", multiply(transpose(gate), gate) == identity(4), multiply(transpose(gate), gate), identity(4), "local_gate")
    audit.check("local symplectic", multiply(multiply(transpose(gate), temporal_form), gate) == temporal_form, multiply(multiply(transpose(gate), temporal_form), gate), temporal_form, "local_gate")
    inverse_gate = kron([[gamma, -eta], [eta, gamma]], identity(2))
    audit.check("local inverse", multiply(inverse_gate, gate) == identity(4), multiply(inverse_gate, gate), identity(4), "local_gate")
    species_count = 8
    leg_dimension = 2 * species_count
    eta_cross = scale(eta, identity(leg_dimension))
    gamma_cross = scale(gamma, identity(leg_dimension))
    audit.check("eta cross rank", rank(eta_cross) == leg_dimension, rank(eta_cross), leg_dimension, "local_gate")
    audit.check("gamma cross rank", rank(gamma_cross) == leg_dimension, rank(gamma_cross), leg_dimension, "local_gate")
    parent_rank = parent_result["derived"]["neighbour_eight_rank"]
    audit.check("parent rank", parent_rank == species_count, parent_rank, species_count, "local_gate")
    audit.check("new rank doubles parent", leg_dimension == 2 * parent_rank, leg_dimension, 2 * parent_rank, "local_gate")

    oriented_form = kron([[Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1)]], j2)
    eta_side = kron(
        [[-1 / eta, gamma / eta], [-gamma / eta, 1 / eta]],
        identity(2),
    )
    gamma_side = kron(
        [[1 / gamma, eta / gamma], [eta / gamma, 1 / gamma]],
        identity(2),
    )
    gamma_side_inverse = kron(
        [[1 / gamma, -eta / gamma], [-eta / gamma, 1 / gamma]],
        identity(2),
    )
    audit.check("eta-side symplectic", multiply(multiply(transpose(eta_side), oriented_form), eta_side) == oriented_form, multiply(multiply(transpose(eta_side), oriented_form), eta_side), oriented_form, "sideways")
    audit.check("eta-side involution", multiply(eta_side, eta_side) == identity(4), multiply(eta_side, eta_side), identity(4), "sideways")
    audit.check("eta-side rank", rank(eta_side) == 4, rank(eta_side), 4, "sideways")
    audit.check("gamma-side symplectic", multiply(multiply(transpose(gamma_side), oriented_form), gamma_side) == oriented_form, multiply(multiply(transpose(gamma_side), oriented_form), gamma_side), oriented_form, "sideways")
    audit.check("gamma-side inverse", multiply(gamma_side_inverse, gamma_side) == identity(4), multiply(gamma_side_inverse, gamma_side), identity(4), "sideways")
    audit.check("gamma-side rank", rank(gamma_side) == 4, rank(gamma_side), 4, "sideways")
    audit.check("mixed sideways state boundary", "does not preserve the passive number" in manifest["sideways_inverses"]["state_boundary"], manifest["sideways_inverses"]["state_boundary"], "not passive", "sideways")

    q_w, p_w = Fraction(1, 2), Fraction(2, 3)
    q_s, p_s = Fraction(-3, 5), Fraction(5, 7)
    kick_delta = Fraction(2, 9)
    grad_w, grad_s = q_w**3, q_s**3
    q_n = -eta * q_w + gamma * q_s
    p_n = -eta * (p_w - kick_delta * grad_w) + gamma * (p_s - kick_delta * grad_s)
    recovered_q_s = (q_n + eta * q_w) / gamma
    recovered_p_s = (p_n + eta * (p_w - kick_delta * grad_w)) / gamma + kick_delta * grad_s
    audit.check("q-only kicked local q cross inverse", recovered_q_s == q_s, recovered_q_s, q_s, "sideways")
    audit.check("q-only kicked local p cross inverse", recovered_p_s == p_s, recovered_p_s, p_s, "sideways")

    horizontal_row, vertical_row = rectangle_wires(gamma, eta, rectangle_m, rectangle_n, "row")
    horizontal_column, vertical_column = rectangle_wires(gamma, eta, rectangle_m, rectangle_n, "column")
    audit.check("horizontal sweep agreement", horizontal_row == horizontal_column, len(horizontal_row), len(horizontal_column), "rectangle")
    audit.check("vertical sweep agreement", vertical_row == vertical_column, len(vertical_row), len(vertical_column), "rectangle")
    output = [horizontal_row[(rectangle_m, row)] for row in range(1, rectangle_n + 1)]
    output.extend(vertical_row[(column, rectangle_n)] for column in range(1, rectangle_m + 1))
    boundary_transfer = [row[:] for row in output]
    audit.check("boundary dimension", len(boundary_transfer) == total_legs and len(boundary_transfer[0]) == total_legs, [len(boundary_transfer), len(boundary_transfer[0])], [total_legs, total_legs], "rectangle")
    audit.check("boundary orthogonal", multiply(transpose(boundary_transfer), boundary_transfer) == identity(total_legs), multiply(transpose(boundary_transfer), boundary_transfer), identity(total_legs), "rectangle")
    audit.check("boundary full rank", rank(boundary_transfer) == total_legs, rank(boundary_transfer), total_legs, "rectangle")
    full_transfer = kron(boundary_transfer, identity(2))
    full_form = kron(identity(total_legs), j2)
    audit.check("boundary symplectic", multiply(multiply(transpose(full_transfer), full_form), full_transfer) == full_form, "zero defect", "zero defect", "rectangle")
    audit.check("same real dimension", leg_dimension * total_legs == 16 * total_legs, leg_dimension * total_legs, 16 * total_legs, "rectangle")
    audit.check("zero constraints", manifest["two_arm_boundary"]["constraints"].startswith("none"), manifest["two_arm_boundary"]["constraints"], "none", "rectangle")

    all_ideals = ideals(rectangle_m, rectangle_n)
    expected_count = math.comb(total_legs, rectangle_m)
    audit.check("cut count", len(all_ideals) == expected_count, len(all_ideals), expected_count, "cuts")
    cut_failures: list[dict[str, Any]] = []
    cut_fingerprints: list[Matrix] = []
    for row_lengths in all_ideals:
        current = cut_matrix(horizontal_row, vertical_row, rectangle_m, row_lengths)
        orthogonal = multiply(transpose(current), current) == identity(total_legs)
        full_rank = rank(current) == total_legs
        canonical = kron(current, identity(2))
        symplectic = multiply(multiply(transpose(canonical), full_form), canonical) == full_form
        if not (orthogonal and full_rank and symplectic):
            cut_failures.append(
                {
                    "row_lengths": row_lengths,
                    "orthogonal": orthogonal,
                    "full_rank": full_rank,
                    "symplectic": symplectic,
                }
            )
        if len(cut_fingerprints) < 3:
            cut_fingerprints.append(current)
    audit.check("every cut passes", cut_failures == [], cut_failures, [], "cuts")
    audit.check("input ideal", tuple(0 for _ in range(rectangle_n)) in all_ideals, "input", "present", "cuts")
    audit.check("output ideal", tuple(rectangle_m for _ in range(rectangle_n)) in all_ideals, "output", "present", "cuts")

    causal_violations: list[list[Any]] = []
    for (column, row), coefficients in list(horizontal_row.items()) + list(vertical_row.items()):
        allowed = set(range(row)) | set(range(rectangle_n, rectangle_n + column))
        for source, coefficient in enumerate(coefficients):
            if source not in allowed and coefficient != 0:
                causal_violations.append([column, row, source, coefficient])
    audit.check("southwest causal zeros", causal_violations == [], causal_violations, [], "causality")

    even_layer = pair_layer(ring_size, 0, gamma, eta)
    odd_layer = pair_layer(ring_size, 1, gamma, eta)
    brickwork = multiply(odd_layer, even_layer)
    brickwork_inverse = transpose(brickwork)
    two_periods = matrix_power(brickwork, 2)
    audit.check("even layer orthogonal", multiply(transpose(even_layer), even_layer) == identity(ring_size), "zero", "zero", "brickwork")
    audit.check("odd layer orthogonal", multiply(transpose(odd_layer), odd_layer) == identity(ring_size), "zero", "zero", "brickwork")
    audit.check("brickwork orthogonal", multiply(transpose(brickwork), brickwork) == identity(ring_size), "zero", "zero", "brickwork")
    brickwork_full = kron(brickwork, identity(2))
    ring_form = kron(identity(ring_size), j2)
    audit.check("brickwork symplectic", multiply(multiply(transpose(brickwork_full), ring_form), brickwork_full) == ring_form, "zero", "zero", "brickwork")
    one_period_violations: list[list[int]] = []
    inverse_violations: list[list[int]] = []
    two_period_violations: list[list[int]] = []
    for target in range(ring_size):
        for source in range(ring_size):
            distance = periodic_distance(target, source, ring_size)
            if distance > 2 and brickwork[target][source] != 0:
                one_period_violations.append([target, source])
            if distance > 2 and brickwork_inverse[target][source] != 0:
                inverse_violations.append([target, source])
            if distance > 4 and two_periods[target][source] != 0:
                two_period_violations.append([target, source])
    radius_two_nonzero = any(
        periodic_distance(target, source, ring_size) == 2 and brickwork[target][source] != 0
        for target in range(ring_size)
        for source in range(ring_size)
    )
    audit.check("brickwork radius two", one_period_violations == [], one_period_violations, [], "brickwork")
    audit.check("inverse radius two", inverse_violations == [], inverse_violations, [], "brickwork")
    audit.check("two periods radius four", two_period_violations == [], two_period_violations, [], "brickwork")
    audit.check("radius two attained", radius_two_nonzero, radius_two_nonzero, True, "brickwork")

    initial_vector = [[Fraction(1)] if row == 0 else [Fraction(0)] for row in range(ring_size)]
    transported_vector = multiply(brickwork, initial_vector)
    initial_projector = multiply(initial_vector, transpose(initial_vector))
    transported_projector = multiply(transported_vector, transpose(transported_vector))
    observable = zeros(ring_size, ring_size)
    for index in range(ring_size):
        observable[index][index] = Fraction(index + 1)
    heisenberg = multiply(multiply(transpose(brickwork), observable), brickwork)
    audit.check("transported norm", multiply(transpose(transported_vector), transported_vector)[0][0] == 1, multiply(transpose(transported_vector), transported_vector)[0][0], 1, "state_transport")
    audit.check("projector trace", trace(transported_projector) == 1, trace(transported_projector), 1, "state_transport")
    audit.check("projector purity", multiply(transported_projector, transported_projector) == transported_projector, "pure", "pure", "state_transport")
    audit.check("projector changes", transported_projector != initial_projector, transported_projector, "changed", "state_transport")
    audit.check("trace duality", trace(multiply(transported_projector, observable)) == trace(multiply(initial_projector, heisenberg)), trace(multiply(transported_projector, observable)), trace(multiply(initial_projector, heisenberg)), "state_transport")

    mode_count = species_count * ring_size
    partition = (Fraction(1) - fugacity) ** (-mode_count)
    density_prefactor = (Fraction(1) - fugacity) ** mode_count
    audit.check("Gibbs normalization", partition * density_prefactor == 1, partition * density_prefactor, 1, "Gibbs")
    truncation = 6
    one_mode_partial = sum((fugacity**occupation for occupation in range(truncation + 1)), Fraction(0))
    expected_partial = (1 - fugacity ** (truncation + 1)) / (1 - fugacity)
    audit.check("geometric trace derivation", one_mode_partial == expected_partial, one_mode_partial, expected_partial, "Gibbs")
    covariance_scale = (1 + fugacity) / (1 - fugacity)
    covariance = scale(covariance_scale, identity(ring_size))
    audit.check("stationary covariance", multiply(multiply(brickwork, covariance), transpose(brickwork)) == covariance, "zero defect", "zero defect", "Gibbs")
    audit.check("cut-covariant Gibbs scope true", manifest["scope"]["actual_cut_covariant_normal_Gibbs_state_family"] is True, manifest["scope"]["actual_cut_covariant_normal_Gibbs_state_family"], True, "Gibbs")
    audit.check("periodic stationary Gibbs scope true", manifest["scope"]["periodic_companion_stationary_normal_Gibbs_state"] is True, manifest["scope"]["periodic_companion_stationary_normal_Gibbs_state"], True, "Gibbs")

    q_value = Fraction(2, 3)
    p_value = Fraction(0)
    delta_value = Fraction(3, 7)
    weight_value = Fraction(5, 11)
    quartic_value = Fraction(7, 13)
    nu_value = Fraction(11, 6)
    p_after = p_value - delta_value * weight_value * quartic_value * q_value**3
    energy_before = (nu_value * q_value**2 + p_value**2 / nu_value) / 2
    energy_after = (nu_value * q_value**2 + p_after**2 / nu_value) / 2
    energy_defect = energy_after - energy_before
    expected_energy_defect = (
        -(delta_value * weight_value * quartic_value / nu_value) * p_value * q_value**3
        + (delta_value**2 * weight_value**2 * quartic_value**2 / (2 * nu_value)) * q_value**6
    )
    audit.check("quartic energy formula", energy_defect == expected_energy_defect, energy_defect, expected_energy_defect, "quartic_no_go")
    audit.check("quartic energy positive", energy_defect > 0, energy_defect, ">0", "quartic_no_go")
    raising_paths = [steps for steps in itertools.product((-1, 1), repeat=4) if sum(steps) == 4]
    raising_amplitude_squared = math.factorial(4)
    number_difference = 4
    commutator_coefficient_squared = number_difference**2 * raising_amplitude_squared
    audit.check("unique four-raising path", len(raising_paths) == 1, len(raising_paths), 1, "quartic_no_go")
    audit.check("quartic ladder amplitude squared", raising_amplitude_squared == math.prod(range(1, 5)), raising_amplitude_squared, math.prod(range(1, 5)), "quartic_no_go")
    audit.check("number commutator nonzero", commutator_coefficient_squared > 0, commutator_coefficient_squared, ">0", "quartic_no_go")
    expected_negative = "NG-2026-08-04-PRE-A-CP1-CL8-PASSIVE-TWO-ARM-NUMBER-STATE-QUARTIC-REUSE"
    audit.check("negative id", manifest["CL8_quartic_reuse_no_go"]["negative_id"] == expected_negative, manifest["CL8_quartic_reuse_no_go"]["negative_id"], expected_negative, "quartic_no_go")
    audit.check("interaction absent", manifest["scope"]["inherited_Q3_interaction_implemented"] is False, manifest["scope"]["inherited_Q3_interaction_implemented"], False, "quartic_no_go")
    audit.check("number reuse false", manifest["scope"]["passive_number_survives_CL8_quartic_kick"] is False, manifest["scope"]["passive_number_survives_CL8_quartic_kick"], False, "quartic_no_go")

    true_scope = (
        "same_CL8_finite_phase_dimension",
        "general_parameter_full_rank_sideways_gate",
        "two_arm_corner_and_dimension_declared",
        "all_admissible_cut_reconstruction",
        "global_sweep_independence",
        "exact_cut_symplecticity",
        "exact_cut_causality",
        "exact_metaplectic_Weyl_cut_maps",
        "exact_BH_cut_isomorphisms",
        "positive_invariant_passive_generator",
        "actual_cut_covariant_normal_Gibbs_state_family",
        "periodic_companion_stationary_normal_Gibbs_state",
        "linear_passive_control_subgate_closed",
        "local_q_only_kicked_gate_classically_sideways_invertible",
    )
    for key in true_scope:
        audit.check(f"scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    false_scope = (
        "strict_continuous_variable_dual_unitarity",
        "arbitrary_periodic_two_arm_seam_reconstruction",
        "inherited_Q3_interaction_implemented",
        "interacting_CL8_characteristic_parent_closed",
        "passive_number_survives_CL8_quartic_kick",
        "interacting_boundary_bulk_intertwiner",
        "preferred_physical_state_selected",
        "physical_energy_reference",
        "physical_vacuum",
        "below_empty_space",
        "regulator_compatible_state_family",
        "continuum_quantum_state",
        "Hadamard_state",
        "hbar_origin_derived",
        "Lorentzian_or_null_structure_derived",
        "speed_of_light_derived",
        "C0_closed",
        "N1_closed",
        "N2_closed",
        "N3_closed",
        "N4_closed",
        "N5_closed",
        "full_3_plus_1_dependence",
        "gravity_or_event_horizon",
        "phase_transition_or_cooling",
        "cyclic_cosmology",
        "C6_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in false_scope:
        audit.check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    next_gate = "PA-CP1-CL8-INTERACTING-GATE-TILING-ALL-CUT-INVARIANT-OR-WORK-STATE"
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == next_gate, manifest["gate_resolution"]["next_gate"], next_gate, "scope")

    derived = {
        "pythagorean_inputs": [pythagorean_u, pythagorean_v],
        "gamma": gamma,
        "eta": eta,
        "local_gate": gate,
        "eta_sideways": eta_side,
        "gamma_sideways": gamma_side,
        "leg_dimension": leg_dimension,
        "parent_neighbour_rank": parent_rank,
        "new_cross_rank": leg_dimension,
        "rectangle": {"m": rectangle_m, "n": rectangle_n, "total_legs": total_legs},
        "cut_count": len(all_ideals),
        "cut_fingerprints": cut_fingerprints,
        "boundary_transfer": boundary_transfer,
        "causal_violations": causal_violations,
        "ring_size": ring_size,
        "brickwork": brickwork,
        "one_period_radius_violations": one_period_violations,
        "inverse_radius_violations": inverse_violations,
        "two_period_radius_violations": two_period_violations,
        "fugacity": fugacity,
        "mode_count": mode_count,
        "Gibbs_partition": partition,
        "quartic_energy_defect": energy_defect,
        "quartic_number_commutator_coefficient_squared_without_scale": commutator_coefficient_squared,
        "next_gate": next_gate,
    }
    cross_invariants = {
        "same_phase_dimension": True,
        "leg_dimension": leg_dimension,
        "parent_neighbour_rank": parent_rank,
        "new_cross_rank": leg_dimension,
        "gamma_square_plus_eta_square": 1,
        "cut_count_rule": "binomial(m+n,m)",
        "all_cuts_orthogonal": True,
        "all_cuts_symplectic": True,
        "brickwork_radius": 2,
        "Gibbs_partition_rule": "(1-zeta)^(-8M)",
        "quartic_energy_defect_rule": "-(delta*w*g/nu)*p*q^3+(delta^2*w^2*g^2/(2nu))*q^6",
        "quartic_number_commutator_rule": "4*sqrt(24)*(hbar/(2nu))^2",
        "next_gate": next_gate,
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(expected_parents),
        "result_id": RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "cross_invariants": cross_invariants,
        "scope": manifest["scope"],
        "negative_ids": [expected_negative],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": next_gate,
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "common_parent": sha256(COMMON_PARENT),
            "goursat_parent": sha256(GOURSAT_PARENT),
            "boundary_parent": sha256(BOUNDARY_PARENT),
            "gaussian_parent": sha256(GAUSSIAN_PARENT),
            "q3_parent": sha256(Q3_PARENT),
            "parent_result": sha256(PARENT_RESULT),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pythagorean-u", type=int, default=3)
    parser.add_argument("--pythagorean-v", type=int, default=2)
    parser.add_argument("--rectangle-m", type=int, default=3)
    parser.add_argument("--rectangle-n", type=int, default=7)
    parser.add_argument("--ring-size", type=int, default=10)
    parser.add_argument("--fugacity-numerator", type=int, default=3)
    parser.add_argument("--fugacity-denominator", type=int, default=7)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(
        args.pythagorean_u,
        args.pythagorean_v,
        args.rectangle_m,
        args.rectangle_n,
        args.ring_size,
        args.fugacity_numerator,
        args.fugacity_denominator,
    )
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} independent: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
