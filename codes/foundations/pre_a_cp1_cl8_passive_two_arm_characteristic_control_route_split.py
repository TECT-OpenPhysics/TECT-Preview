#!/usr/bin/env python3
"""Primary exact audit for the CL8 passive two-arm characteristic control."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-PASSIVE-TWO-ARM-CHARACTERISTIC-CONTROL-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-PASSIVE-TWO-ARM-CUT-RECONSTRUCTION-AND-CL8-KICK-STATE-NOGO"
SLUG = "pre-a-cp1-cl8-passive-two-arm-characteristic-control-route-split"
SCHEMA = f"tect/{SLUG}-primary/0.1"
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
    / "2026-08-04-primary-pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split/result.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-primary-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, column]) for column in range(value.cols)] for row in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
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


def pythagorean(u: int, v: int) -> tuple[sp.Rational, sp.Rational]:
    if not (u > v > 0):
        raise ValueError("require u>v>0")
    denominator = u * u + v * v
    return sp.Rational(u * u - v * v, denominator), sp.Rational(2 * u * v, denominator)


def matrix_zero(matrix: sp.MatrixBase) -> bool:
    return all(sp.simplify(entry) == 0 for entry in matrix)


def on_unit_circle(matrix: sp.MatrixBase, gamma: sp.Symbol, eta: sp.Symbol) -> sp.Matrix:
    return matrix.applyfunc(lambda entry: sp.cancel(entry).subs(eta**2, 1 - gamma**2).simplify())


def rectangle_wires(
    gamma: sp.Rational,
    eta: sp.Rational,
    horizontal_count: int,
    vertical_count: int,
    order: str,
) -> tuple[dict[tuple[int, int], sp.Matrix], dict[tuple[int, int], sp.Matrix]]:
    if horizontal_count < 1 or vertical_count < 1:
        raise ValueError("rectangle sides must be positive")
    total = horizontal_count + vertical_count
    horizontal: dict[tuple[int, int], sp.Matrix] = {}
    vertical: dict[tuple[int, int], sp.Matrix] = {}
    for row in range(1, vertical_count + 1):
        basis = sp.zeros(1, total)
        basis[0, row - 1] = 1
        horizontal[(0, row)] = basis
    for column in range(1, horizontal_count + 1):
        basis = sp.zeros(1, total)
        basis[0, vertical_count + column - 1] = 1
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
        horizontal[(column, row)] = gamma * west + eta * south
        vertical[(column, row)] = -eta * west + gamma * south
    return horizontal, vertical


def row_length_ideals(horizontal_count: int, vertical_count: int) -> list[tuple[int, ...]]:
    ideals: list[tuple[int, ...]] = []
    for row_lengths in itertools.product(range(horizontal_count + 1), repeat=vertical_count):
        if all(row_lengths[index] >= row_lengths[index + 1] for index in range(vertical_count - 1)):
            ideals.append(tuple(row_lengths))
    return ideals


def cut_matrix(
    horizontal: dict[tuple[int, int], sp.Matrix],
    vertical: dict[tuple[int, int], sp.Matrix],
    horizontal_count: int,
    vertical_count: int,
    row_lengths: tuple[int, ...],
) -> sp.Matrix:
    rows: list[sp.Matrix] = []
    for row, length in enumerate(row_lengths, start=1):
        rows.append(horizontal[(length, row)])
    for column in range(1, horizontal_count + 1):
        heights = [row for row, length in enumerate(row_lengths, start=1) if length >= column]
        height = max(heights, default=0)
        rows.append(vertical[(column, height)])
    return sp.Matrix.vstack(*rows)


def pair_layer(size: int, offset: int, gamma: sp.Rational, eta: sp.Rational) -> sp.Matrix:
    if size < 4 or size % 2:
        raise ValueError("ring size must be even and at least four")
    layer = sp.zeros(size)
    if offset == 0:
        pairs = [(index, index + 1) for index in range(0, size, 2)]
    elif offset == 1:
        pairs = [(index, index + 1) for index in range(1, size - 1, 2)] + [(size - 1, 0)]
    else:
        raise ValueError(offset)
    for left, right in pairs:
        layer[left, left] = gamma
        layer[left, right] = eta
        layer[right, left] = -eta
        layer[right, right] = gamma
    return layer


def periodic_distance(left: int, right: int, size: int) -> int:
    separation = abs(left - right)
    return min(separation, size - separation)


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
    loaded_parents = (
        common_parent["candidate_id"],
        goursat_parent["candidate_id"],
        boundary_parent["candidate_id"],
        gaussian_parent["candidate_id"],
        q3_parent["candidate_id"],
    )
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "provenance")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "provenance")
    audit.check("parent ids", tuple(manifest["parent_ids"]) == expected_parents, manifest["parent_ids"], expected_parents, "provenance")
    audit.check("loaded parent ids", loaded_parents == expected_parents, loaded_parents, expected_parents, "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "provenance")
    audit.check("T0 authority", manifest["authority"].startswith("T0 "), manifest["authority"], "T0", "provenance")

    gamma, eta = pythagorean(pythagorean_u, pythagorean_v)
    audit.check("Pythagorean normalization", sp.factor(gamma**2 + eta**2) == 1, gamma**2 + eta**2, 1, "parameters")
    audit.check("gamma nonzero", gamma != 0, gamma, "nonzero", "parameters")
    audit.check("eta nonzero", eta != 0, eta, "nonzero", "parameters")
    audit.check("rectangle total even", (rectangle_m + rectangle_n) % 2 == 0, rectangle_m + rectangle_n, "even", "parameters")
    audit.check("rectangle total at least four", rectangle_m + rectangle_n >= 4, rectangle_m + rectangle_n, ">=4", "parameters")
    audit.check("one common regulator M", ring_size == rectangle_m + rectangle_n, ring_size, rectangle_m + rectangle_n, "parameters")
    audit.check("ring size even", ring_size % 2 == 0, ring_size, "even", "parameters")
    audit.check("ring size at least ten", ring_size >= 10, ring_size, ">=10", "parameters")
    fugacity = sp.Rational(fugacity_numerator, fugacity_denominator)
    audit.check("fugacity domain", bool(0 < fugacity < 1), fugacity, "0<zeta<1", "parameters")

    gamma_symbol, eta_symbol = sp.symbols("gamma eta", real=True, nonzero=True)
    coefficient_gate = sp.Matrix([[gamma_symbol, eta_symbol], [-eta_symbol, gamma_symbol]])
    j2 = sp.Matrix([[0, 1], [-1, 0]])
    gate = sp.kronecker_product(coefficient_gate, sp.eye(2))
    temporal_form = sp.kronecker_product(sp.eye(2), j2)
    norm_square = gamma_symbol**2 + eta_symbol**2
    audit.check("general temporal symplectic identity", matrix_zero(gate.T * temporal_form * gate - norm_square * temporal_form), gate.T * temporal_form * gate, norm_square * temporal_form, "local_gate")
    audit.check("general orthogonal identity", matrix_zero(gate.T * gate - norm_square * sp.eye(4)), gate.T * gate, norm_square * sp.eye(4), "local_gate")
    audit.check("general determinant", sp.factor(gate.det()) == norm_square**2, sp.factor(gate.det()), norm_square**2, "local_gate")
    inverse_gate = sp.kronecker_product(sp.Matrix([[gamma_symbol, -eta_symbol], [eta_symbol, gamma_symbol]]), sp.eye(2))
    audit.check("general inverse numerator", matrix_zero(inverse_gate * gate - norm_square * sp.eye(4)), inverse_gate * gate, norm_square * sp.eye(4), "local_gate")
    leg_dimension = 2 * 8
    eta_block = eta_symbol * sp.eye(leg_dimension)
    gamma_block = gamma_symbol * sp.eye(leg_dimension)
    audit.check("eta cross block full rank", eta_block.rank() == leg_dimension, eta_block.rank(), leg_dimension, "local_gate")
    audit.check("gamma cross block full rank", gamma_block.rank() == leg_dimension, gamma_block.rank(), leg_dimension, "local_gate")
    parent_rank = parent_result["derived"]["neighbour_rank_eight_species"]
    audit.check("parent rank loaded", parent_rank == leg_dimension // 2, parent_rank, leg_dimension // 2, "local_gate")
    audit.check("new rank strictly improves parent", leg_dimension > parent_rank, [leg_dimension, parent_rank], "new>parent", "local_gate")

    oriented_form = sp.kronecker_product(sp.diag(1, -1), j2)
    eta_side_coeff = sp.Matrix(
        [
            [-1 / eta_symbol, gamma_symbol / eta_symbol],
            [-gamma_symbol / eta_symbol, 1 / eta_symbol],
        ]
    )
    eta_side = sp.kronecker_product(eta_side_coeff, sp.eye(2))
    eta_defect = on_unit_circle(eta_side.T * oriented_form * eta_side - oriented_form, gamma_symbol, eta_symbol)
    eta_square_defect = on_unit_circle(eta_side * eta_side - sp.eye(4), gamma_symbol, eta_symbol)
    audit.check("eta-side oriented symplectic", matrix_zero(eta_defect), eta_defect, sp.zeros(4), "sideways")
    audit.check("eta-side inverse", matrix_zero(eta_square_defect), eta_square_defect, sp.zeros(4), "sideways")
    audit.check("eta-side full rank", sp.factor(eta_side.det()) != 0, sp.factor(eta_side.det()), "nonzero", "sideways")
    gamma_side_coeff = sp.Matrix(
        [
            [1 / gamma_symbol, eta_symbol / gamma_symbol],
            [eta_symbol / gamma_symbol, 1 / gamma_symbol],
        ]
    )
    gamma_side = sp.kronecker_product(gamma_side_coeff, sp.eye(2))
    gamma_defect = on_unit_circle(gamma_side.T * oriented_form * gamma_side - oriented_form, gamma_symbol, eta_symbol)
    gamma_inverse_coeff = sp.Matrix(
        [
            [1 / gamma_symbol, -eta_symbol / gamma_symbol],
            [-eta_symbol / gamma_symbol, 1 / gamma_symbol],
        ]
    )
    gamma_inverse = sp.kronecker_product(gamma_inverse_coeff, sp.eye(2))
    gamma_inverse_defect = on_unit_circle(gamma_inverse * gamma_side - sp.eye(4), gamma_symbol, eta_symbol)
    audit.check("gamma-side oriented symplectic", matrix_zero(gamma_defect), gamma_defect, sp.zeros(4), "sideways")
    audit.check("gamma-side inverse", matrix_zero(gamma_inverse_defect), gamma_inverse_defect, sp.zeros(4), "sideways")
    audit.check("gamma-side full rank", sp.factor(gamma_side.det()) != 0, sp.factor(gamma_side.det()), "nonzero", "sideways")
    audit.check("sideways Gibbs boundary declared", "does not preserve the passive number" in manifest["sideways_inverses"]["state_boundary"], manifest["sideways_inverses"]["state_boundary"], "not stationary", "sideways")

    q_w, p_w, q_s, p_s, kick_delta, grad_w, grad_s = sp.symbols(
        "q_w p_w q_s p_s kick_delta grad_w grad_s", real=True
    )
    q_n = -eta_symbol * q_w + gamma_symbol * q_s
    p_n = -eta_symbol * (p_w - kick_delta * grad_w) + gamma_symbol * (p_s - kick_delta * grad_s)
    recovered_q_s = (q_n + eta_symbol * q_w) / gamma_symbol
    recovered_p_s = (p_n + eta_symbol * (p_w - kick_delta * grad_w)) / gamma_symbol + kick_delta * grad_s
    audit.check("q-only kicked local q cross inverse", sp.simplify(recovered_q_s - q_s) == 0, recovered_q_s, q_s, "sideways")
    audit.check("q-only kicked local p cross inverse", sp.simplify(recovered_p_s - p_s) == 0, recovered_p_s, p_s, "sideways")

    horizontal_row, vertical_row = rectangle_wires(gamma, eta, rectangle_m, rectangle_n, "row")
    horizontal_column, vertical_column = rectangle_wires(gamma, eta, rectangle_m, rectangle_n, "column")
    audit.check("row-column horizontal sweep agreement", horizontal_row == horizontal_column, len(horizontal_row), len(horizontal_column), "rectangle")
    audit.check("row-column vertical sweep agreement", vertical_row == vertical_column, len(vertical_row), len(vertical_column), "rectangle")
    total_legs = rectangle_m + rectangle_n
    output_rows = [horizontal_row[(rectangle_m, row)] for row in range(1, rectangle_n + 1)]
    output_rows.extend(vertical_row[(column, rectangle_n)] for column in range(1, rectangle_m + 1))
    boundary_transfer = sp.Matrix.vstack(*output_rows)
    audit.check("boundary transfer dimension", boundary_transfer.shape == (total_legs, total_legs), boundary_transfer.shape, (total_legs, total_legs), "rectangle")
    audit.check("boundary transfer orthogonal", matrix_zero(boundary_transfer.T * boundary_transfer - sp.eye(total_legs)), boundary_transfer.T * boundary_transfer, sp.eye(total_legs), "rectangle")
    audit.check("boundary transfer full rank", boundary_transfer.rank() == total_legs, boundary_transfer.rank(), total_legs, "rectangle")
    audit.check("boundary inverse transpose", matrix_zero(boundary_transfer.T * boundary_transfer - sp.eye(total_legs)), boundary_transfer.T, "inverse", "rectangle")
    one_species_transfer = sp.kronecker_product(boundary_transfer, sp.eye(2))
    cut_symplectic_form = sp.kronecker_product(sp.eye(total_legs), j2)
    audit.check("boundary transfer symplectic", matrix_zero(one_species_transfer.T * cut_symplectic_form * one_species_transfer - cut_symplectic_form), "zero defect", "zero defect", "rectangle")
    audit.check("complete cut real dimension", 16 * total_legs == int(manifest["fixed_regulator"]["leg_dimension"].split()[0]) * total_legs, 16 * total_legs, "16M", "rectangle")
    audit.check("constraint space zero", manifest["two_arm_boundary"]["constraints"].startswith("none"), manifest["two_arm_boundary"]["constraints"], "none", "rectangle")
    audit.check("corner not duplicated", "no duplicated corner coordinate" in manifest["two_arm_boundary"]["corner"], manifest["two_arm_boundary"]["corner"], "one geometric corner", "rectangle")

    ideals = row_length_ideals(rectangle_m, rectangle_n)
    expected_cut_count = math.comb(total_legs, rectangle_m)
    audit.check("cut count derived", len(ideals) == expected_cut_count, len(ideals), expected_cut_count, "cuts")
    cut_failures: list[dict[str, Any]] = []
    cut_fingerprints: list[list[list[Any]]] = []
    for row_lengths in ideals:
        current_cut = cut_matrix(horizontal_row, vertical_row, rectangle_m, rectangle_n, row_lengths)
        orthogonal = matrix_zero(current_cut.T * current_cut - sp.eye(total_legs))
        full_rank = current_cut.rank() == total_legs
        canonical_cut = sp.kronecker_product(current_cut, sp.eye(2))
        symplectic = matrix_zero(canonical_cut.T * cut_symplectic_form * canonical_cut - cut_symplectic_form)
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
            cut_fingerprints.append(serial(current_cut))
    audit.check("all cuts orthogonal symplectic full rank", cut_failures == [], cut_failures, [], "cuts")
    audit.check("input cut present", tuple(0 for _ in range(rectangle_n)) in ideals, "input", "present", "cuts")
    audit.check("output cut present", tuple(rectangle_m for _ in range(rectangle_n)) in ideals, "output", "present", "cuts")

    causal_violations: list[dict[str, Any]] = []
    for (column, row), coefficients in list(horizontal_row.items()) + list(vertical_row.items()):
        allowed_left = set(range(row))
        allowed_bottom = set(range(rectangle_n, rectangle_n + column))
        allowed = allowed_left | allowed_bottom
        for input_index in range(total_legs):
            if input_index not in allowed and coefficients[0, input_index] != 0:
                causal_violations.append(
                    {
                        "edge": [column, row],
                        "input": input_index,
                        "coefficient": coefficients[0, input_index],
                    }
                )
    audit.check("southwest causal support", causal_violations == [], causal_violations, [], "causality")

    even_layer = pair_layer(ring_size, 0, gamma, eta)
    odd_layer = pair_layer(ring_size, 1, gamma, eta)
    brickwork = odd_layer * even_layer
    inverse_brickwork = brickwork.T
    two_periods = brickwork**2
    audit.check("even layer orthogonal", matrix_zero(even_layer.T * even_layer - sp.eye(ring_size)), "zero defect", "zero defect", "brickwork")
    audit.check("odd layer orthogonal", matrix_zero(odd_layer.T * odd_layer - sp.eye(ring_size)), "zero defect", "zero defect", "brickwork")
    audit.check("brickwork orthogonal", matrix_zero(brickwork.T * brickwork - sp.eye(ring_size)), "zero defect", "zero defect", "brickwork")
    brickwork_canonical = sp.kronecker_product(brickwork, sp.eye(2))
    ring_form = sp.kronecker_product(sp.eye(ring_size), j2)
    audit.check("brickwork symplectic", matrix_zero(brickwork_canonical.T * ring_form * brickwork_canonical - ring_form), "zero defect", "zero defect", "brickwork")
    one_period_violations: list[list[int]] = []
    inverse_violations: list[list[int]] = []
    two_period_violations: list[list[int]] = []
    for output in range(ring_size):
        for source in range(ring_size):
            distance = periodic_distance(output, source, ring_size)
            if distance > 2 and brickwork[output, source] != 0:
                one_period_violations.append([output, source])
            if distance > 2 and inverse_brickwork[output, source] != 0:
                inverse_violations.append([output, source])
            if distance > 4 and two_periods[output, source] != 0:
                two_period_violations.append([output, source])
    distance_two_nonzero = any(
        periodic_distance(output, source, ring_size) == 2 and brickwork[output, source] != 0
        for output in range(ring_size)
        for source in range(ring_size)
    )
    audit.check("one-period radius two", one_period_violations == [], one_period_violations, [], "brickwork")
    audit.check("inverse radius two", inverse_violations == [], inverse_violations, [], "brickwork")
    audit.check("two-period radius four", two_period_violations == [], two_period_violations, [], "brickwork")
    audit.check("radius-two coefficient nonzero", distance_two_nonzero, distance_two_nonzero, True, "brickwork")

    initial_vector = sp.zeros(ring_size, 1)
    initial_vector[0, 0] = 1
    transported_vector = brickwork * initial_vector
    initial_projector = initial_vector * initial_vector.T
    transported_projector = transported_vector * transported_vector.T
    observable = sp.diag(*range(1, ring_size + 1))
    heisenberg_observable = brickwork.T * observable * brickwork
    audit.check("transported vector norm", (transported_vector.T * transported_vector)[0] == 1, (transported_vector.T * transported_vector)[0], 1, "state_transport")
    audit.check("transported projector trace", sp.trace(transported_projector) == 1, sp.trace(transported_projector), 1, "state_transport")
    audit.check("transported projector pure", matrix_zero(transported_projector**2 - transported_projector), "zero defect", "zero defect", "state_transport")
    audit.check("transported projector changes", transported_projector != initial_projector, transported_projector, "nonstationary witness", "state_transport")
    audit.check("Schrodinger-Heisenberg trace", sp.trace(transported_projector * observable) == sp.trace(initial_projector * heisenberg_observable), sp.trace(transported_projector * observable), sp.trace(initial_projector * heisenberg_observable), "state_transport")

    mode_count = 8 * ring_size
    partition = (1 - fugacity) ** (-mode_count)
    density_prefactor = (1 - fugacity) ** mode_count
    audit.check("full-Fock Gibbs normalization", sp.factor(partition * density_prefactor) == 1, sp.factor(partition * density_prefactor), 1, "Gibbs")
    mean_number = sp.factor(mode_count * fugacity / (1 - fugacity))
    audit.check("Gibbs mean number positive", bool(mean_number > 0), mean_number, ">0", "Gibbs")
    covariance_scale = sp.factor((1 + fugacity) / (1 - fugacity))
    covariance = covariance_scale * sp.eye(ring_size)
    audit.check("one-particle Gibbs covariance invariant", matrix_zero(brickwork * covariance * brickwork.T - covariance), "zero defect", "zero defect", "Gibbs")
    audit.check("cut-covariant Gibbs family declared", manifest["scope"]["actual_cut_covariant_normal_Gibbs_state_family"] is True, manifest["scope"]["actual_cut_covariant_normal_Gibbs_state_family"], True, "Gibbs")
    audit.check("periodic stationary Gibbs declared", manifest["scope"]["periodic_companion_stationary_normal_Gibbs_state"] is True, manifest["scope"]["periodic_companion_stationary_normal_Gibbs_state"], True, "Gibbs")
    audit.check("physical state remains false", manifest["scope"]["preferred_physical_state_selected"] is False, manifest["scope"]["preferred_physical_state_selected"], False, "Gibbs")

    q, p, delta, weight, quartic, nu = sp.symbols("q p delta weight quartic nu", positive=True, real=True)
    p_after = p - delta * weight * quartic * q**3
    energy_before = sp.factor((nu * q**2 + p**2 / nu) / 2)
    energy_after = sp.factor((nu * q**2 + p_after**2 / nu) / 2)
    energy_defect = sp.factor(energy_after - energy_before)
    expected_energy_defect = sp.factor(
        -(delta * weight * quartic / nu) * p * q**3
        + (delta**2 * weight**2 * quartic**2 / (2 * nu)) * q**6
    )
    audit.check("quartic passive-energy defect", sp.factor(energy_defect - expected_energy_defect) == 0, energy_defect, expected_energy_defect, "quartic_no_go")
    zero_momentum_defect = sp.factor(energy_defect.subs(p, 0))
    audit.check("zero-momentum defect positive", zero_momentum_defect.is_positive is True, zero_momentum_defect, ">0", "quartic_no_go")

    ladder_dimension = 7
    annihilation = sp.zeros(ladder_dimension)
    for occupation in range(1, ladder_dimension):
        annihilation[occupation - 1, occupation] = sp.sqrt(occupation)
    creation = annihilation.T
    number_operator = sp.diag(*range(ladder_dimension))
    hbar = sp.symbols("hbar", positive=True, real=True)
    q_operator = sp.sqrt(hbar / (2 * nu)) * (annihilation + creation)
    q_four = sp.expand(q_operator**4)
    number_commutator = number_operator * q_four - q_four * number_operator
    commutator_matrix_element = sp.factor(number_commutator[4, 0])
    expected_matrix_element = sp.factor(4 * sp.sqrt(sp.factorial(4)) * (hbar / (2 * nu)) ** 2)
    audit.check("quartic number commutator matrix element", sp.simplify(commutator_matrix_element - expected_matrix_element) == 0, commutator_matrix_element, expected_matrix_element, "quartic_no_go")
    audit.check("quartic changes vacuum", q_four[4, 0] != 0, q_four[4, 0], "nonzero", "quartic_no_go")
    expected_negative = "NG-2026-08-04-PRE-A-CP1-CL8-PASSIVE-TWO-ARM-NUMBER-STATE-QUARTIC-REUSE"
    audit.check("negative id", manifest["CL8_quartic_reuse_no_go"]["negative_id"] == expected_negative, manifest["CL8_quartic_reuse_no_go"]["negative_id"], expected_negative, "quartic_no_go")
    audit.check("passive number reuse false", manifest["scope"]["passive_number_survives_CL8_quartic_kick"] is False, manifest["scope"]["passive_number_survives_CL8_quartic_kick"], False, "quartic_no_go")
    audit.check("interacting parent false", manifest["scope"]["interacting_CL8_characteristic_parent_closed"] is False, manifest["scope"]["interacting_CL8_characteristic_parent_closed"], False, "quartic_no_go")

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
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-INTERACTING-GATE-TILING-ALL-CUT-INVARIANT-OR-WORK-STATE", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-INTERACTING-GATE-TILING-ALL-CUT-INVARIANT-OR-WORK-STATE", "scope")

    derived = {
        "pythagorean_inputs": [pythagorean_u, pythagorean_v],
        "gamma": gamma,
        "eta": eta,
        "local_gate": sp.kronecker_product(sp.Matrix([[gamma, eta], [-eta, gamma]]), sp.eye(2)),
        "eta_sideways": eta_side.subs({gamma_symbol: gamma, eta_symbol: eta}),
        "gamma_sideways": gamma_side.subs({gamma_symbol: gamma, eta_symbol: eta}),
        "leg_dimension": leg_dimension,
        "parent_neighbour_rank": parent_rank,
        "new_cross_rank": leg_dimension,
        "rectangle": {"m": rectangle_m, "n": rectangle_n, "total_legs": total_legs},
        "cut_count": len(ideals),
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
        "Gibbs_mean_number": mean_number,
        "quartic_energy_defect": energy_defect,
        "quartic_number_commutator_40": commutator_matrix_element,
        "next_gate": manifest["gate_resolution"]["next_gate"],
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
        "next_gate": manifest["gate_resolution"]["next_gate"],
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
        "next_gate": manifest["gate_resolution"]["next_gate"],
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
    parser.add_argument("--pythagorean-u", type=int, default=2)
    parser.add_argument("--pythagorean-v", type=int, default=1)
    parser.add_argument("--rectangle-m", type=int, default=4)
    parser.add_argument("--rectangle-n", type=int, default=6)
    parser.add_argument("--ring-size", type=int, default=10)
    parser.add_argument("--fugacity-numerator", type=int, default=2)
    parser.add_argument("--fugacity-denominator", type=int, default=5)
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
    print(f"{CANDIDATE_ID} primary: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
