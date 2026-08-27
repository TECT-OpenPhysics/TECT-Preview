#!/usr/bin/env python3
"""Non-importing independent spectral-commutant reconstruction for R-364."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_q2_spectral_commutant"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-spectral-commutant-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def clean(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=complex)
    for level in range(1, size):
        lowering[level - 1, level] = np.sqrt(float(level))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for position in range(2):
        result = np.kron(result, single if position == site else identity)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = left - right
    return c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (left @ left + right @ right) / 4.0


def build_system(size: int, parameters: dict[str, str]) -> tuple[np.ndarray, list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_ops = [embed(q_single, site, identity) for site in range(2)]
    p_ops = [embed(p_single, site, identity) for site in range(2)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    c = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    difference = q_ops[0] - q_ops[1]
    bond = bond_term(q_ops[0], q_ops[1], c, lam)
    terms = onsite + [clean(bond)]
    return q_single, terms, clean(sum(terms, np.zeros_like(terms[0]))), identity


def spectral_unitary(generator: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(clean(generator))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def thermal_state(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(clean(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return clean((vectors * weights) @ vectors.conj().T)


def site_reduce(state: np.ndarray, size: int, site: int) -> np.ndarray:
    tensor = state.reshape(size, size, size, size)
    reduced = np.zeros((size, size), dtype=complex)
    if site == 0:
        for outside in range(size):
            reduced += tensor[:, outside, :, outside]
    else:
        for outside in range(size):
            reduced += tensor[outside, :, outside, :]
    return clean(reduced)


def local_pvm(q_single: np.ndarray) -> list[np.ndarray]:
    _, vectors = np.linalg.eigh(clean(q_single))
    return [np.outer(vectors[:, index], vectors[:, index].conj()) for index in range(vectors.shape[1])]


def probabilities(reduced: np.ndarray, projectors: list[np.ndarray], tolerance: float) -> np.ndarray:
    values = np.array([float(np.trace(projector @ reduced).real) for projector in projectors])
    if float(np.min(values)) < -tolerance:
        raise AssertionError(f"negative probability {float(np.min(values))}")
    values = np.maximum(values, 0.0)
    return values / float(np.sum(values))


def witness(reference: np.ndarray, projectors: list[np.ndarray]) -> np.ndarray:
    dimension = projectors[0].shape[0] ** 2
    result = np.zeros((dimension, dimension), dtype=complex)
    for probability, projector in zip(reference, projectors):
        result += np.kron(projector, projector) / probability
    return clean(result)


def coordinate_basis(q_single: np.ndarray) -> np.ndarray:
    _, vectors = np.linalg.eigh(clean(q_single))
    return np.kron(np.kron(vectors, vectors), np.kron(vectors, vectors))


def coordinate_pinching(matrix: np.ndarray, basis: np.ndarray) -> np.ndarray:
    transformed = basis.conj().T @ matrix @ basis
    return clean(basis @ np.diag(np.diag(transformed)) @ basis.conj().T)


def spectral_data(generator: np.ndarray, tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    values, vectors = np.linalg.eigh(clean(generator))
    labels = np.zeros(len(values), dtype=int)
    group = 0
    for index in range(1, len(values)):
        if abs(float(values[index] - values[index - 1])) > tolerance:
            group += 1
        labels[index] = group
    return values, vectors, labels, group + 1


def spectral_pinching(matrix: np.ndarray, eigenvectors: np.ndarray, labels: np.ndarray) -> np.ndarray:
    transformed = eigenvectors.conj().T @ matrix @ eigenvectors
    mask = labels[:, None] == labels[None, :]
    return clean(eigenvectors @ (transformed * mask) @ eigenvectors.conj().T)


def weighted_left(state: np.ndarray, matrix: np.ndarray) -> float:
    return float(np.sqrt(max(float(np.trace(matrix.conj().T @ state @ matrix).real), 0.0)))


def weighted_right(state: np.ndarray, matrix: np.ndarray) -> float:
    return float(np.sqrt(max(float(np.trace(state @ matrix.conj().T @ matrix).real), 0.0)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    cutoffs = [int(value) for value in fixture["cutoff_values"]]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    sites = [int(value) for value in fixture["site_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tolerance = float(fixture["finite_tolerance"])
    group_tolerance = float(fixture["spectral_group_tolerance"])
    parameters = fixture["parameters"]
    assertions: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(assertions) < 96:
            assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001206" and manifest["result_id"] == "R-364" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001206/R-364/false", "provenance")
    context_count = 0
    max_reduction_error = 0.0
    max_scalar_error = 0.0
    max_spectral_commutator = 0.0
    max_b_diagonal_error = 0.0
    max_bound_violation = -float("inf")
    min_bound_slack = float("inf")
    max_b_norm = 0.0
    max_expectation = 0.0
    max_bound = 0.0
    max_spectral_frobenius = 0.0
    max_coordinate_frobenius = 0.0
    min_frobenius_gain = float("inf")
    min_nonzero_spectral_frobenius = float("inf")
    max_spectral_left_norm = 0.0
    max_spectral_right_norm = 0.0
    min_spectral_group_count = float("inf")
    max_spectral_group_count = 0
    max_idempotence_error = 0.0
    max_weighted_ratio = 0.0

    for size in cutoffs:
        q_single, terms, hamiltonian, identity = build_system(size, parameters)
        projectors = local_pvm(q_single)
        basis = coordinate_basis(q_single)
        global_identity = np.eye(hamiltonian.shape[0], dtype=complex)
        bond_generator = np.kron(terms[-1], global_identity) + np.kron(global_identity, terms[-1])
        bond_values, bond_vectors, labels, group_count = spectral_data(bond_generator, group_tolerance)
        min_spectral_group_count = min(min_spectral_group_count, group_count)
        max_spectral_group_count = max(max_spectral_group_count, group_count)
        max_b_diagonal_error = max(max_b_diagonal_error, float(np.linalg.norm(bond_generator - spectral_pinching(bond_generator, bond_vectors, labels), ord="fro")))
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        prefix_bank: dict[tuple[str, int], list[np.ndarray]] = {}
        for order_name, order in orders.items():
            for sign in signs:
                current = global_identity.copy()
                rows = [current.copy()]
                for index in order:
                    current = spectral_unitary(terms[index], sign * delta, hbar) @ current
                    rows.append(current.copy())
                prefix_bank[(order_name, sign)] = rows
        embedded = [[embed(projector, site, identity) for projector in projectors] for site in sites]

        for beta_fraction in betas:
            rho = thermal_state(hamiltonian, float(beta_fraction))
            omega = np.kron(rho, rho)
            for site in sites:
                reference = probabilities(site_reduce(rho, size, site), projectors, tolerance)
                local_witness = witness(reference, embedded[site])
                for order_name in orders:
                    for sign in signs:
                        for prefix_length, prefix in enumerate(prefix_bank[(order_name, sign)]):
                            for history_adjoint in adjoints:
                                evolution = prefix if not history_adjoint else prefix.conj().T
                                evolution_two = np.kron(evolution, evolution)
                                moved = clean(evolution_two.conj().T @ local_witness @ evolution_two)
                                scalar = float(np.trace(omega @ moved).real)
                                centered = clean(moved - scalar * np.eye(moved.shape[0], dtype=complex))
                                coord_off = clean(centered - coordinate_pinching(centered, basis))
                                spectral_projection = spectral_pinching(centered, bond_vectors, labels)
                                spectral_off = clean(centered - spectral_projection)
                                comm = bond_generator @ moved - moved @ bond_generator
                                centered_comm = bond_generator @ centered - centered @ bond_generator
                                spectral_comm = bond_generator @ spectral_off - spectral_off @ bond_generator
                                diagonal_comm = bond_generator @ spectral_projection - spectral_projection @ bond_generator
                                reduction_error = float(np.linalg.norm(centered_comm - spectral_comm, ord="fro"))
                                scalar_error = float(np.linalg.norm(comm - centered_comm, ord="fro"))
                                spectral_commutator = float(np.linalg.norm(diagonal_comm, ord="fro"))
                                idempotence = float(np.linalg.norm(spectral_pinching(spectral_projection, bond_vectors, labels) - spectral_projection, ord="fro"))
                                b_norm = float(np.sqrt(max(float(np.trace(omega @ bond_generator @ bond_generator).real), 0.0)))
                                left_norm = weighted_left(omega, spectral_off)
                                right_norm = weighted_right(omega, spectral_off)
                                expectation = abs(complex(np.trace(omega @ comm)))
                                bound = b_norm * (left_norm + right_norm)
                                slack = bound - expectation
                                spectral_size = float(np.linalg.norm(spectral_off, ord="fro"))
                                coordinate_size = float(np.linalg.norm(coord_off, ord="fro"))
                                coordinate_weighted = weighted_left(omega, coord_off) + weighted_right(omega, coord_off)
                                spectral_weighted = left_norm + right_norm
                                context_count += 1
                                max_reduction_error = max(max_reduction_error, reduction_error)
                                max_scalar_error = max(max_scalar_error, scalar_error)
                                max_spectral_commutator = max(max_spectral_commutator, spectral_commutator)
                                max_bound_violation = max(max_bound_violation, expectation - bound)
                                min_bound_slack = min(min_bound_slack, slack)
                                max_b_norm = max(max_b_norm, b_norm)
                                max_expectation = max(max_expectation, expectation)
                                max_bound = max(max_bound, bound)
                                max_spectral_frobenius = max(max_spectral_frobenius, spectral_size)
                                max_coordinate_frobenius = max(max_coordinate_frobenius, coordinate_size)
                                min_frobenius_gain = min(min_frobenius_gain, coordinate_size - spectral_size)
                                if spectral_size > tolerance:
                                    min_nonzero_spectral_frobenius = min(min_nonzero_spectral_frobenius, spectral_size)
                                max_spectral_left_norm = max(max_spectral_left_norm, left_norm)
                                max_spectral_right_norm = max(max_spectral_right_norm, right_norm)
                                max_idempotence_error = max(max_idempotence_error, idempotence)
                                if coordinate_weighted > tolerance:
                                    max_weighted_ratio = max(max_weighted_ratio, spectral_weighted / coordinate_weighted)
                                check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} reduction", reduction_error <= tolerance * 400, reduction_error, f"<={tolerance * 400}", "spectral reduction")
                                check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} bound", expectation <= bound + tolerance * 400 * (1.0 + bound), [expectation, bound], "weighted Cauchy", "state-weighted bound")
                                check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} comparison", spectral_size <= coordinate_size + tolerance * 400, [spectral_size, coordinate_size], "spectral <= coordinate", "residual comparison")

    expected_contexts = len(cutoffs) * len(betas) * len(sites) * len(orders) * len(signs) * (len(terms) + 1) * len(adjoints)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("bond spectral diagonal", max_b_diagonal_error <= tolerance * 400, max_b_diagonal_error, f"<={tolerance * 400}", "spectral commutant")
    check("scalar center", max_scalar_error <= tolerance * 400, max_scalar_error, f"<={tolerance * 400}", "centering")
    check("spectral commutation", max_spectral_commutator <= tolerance * 400, max_spectral_commutator, f"<={tolerance * 400}", "spectral commutant")
    check("spectral idempotence", max_idempotence_error <= tolerance * 600, max_idempotence_error, f"<={tolerance * 600}", "conditional expectation")
    check("weighted bound", max_bound_violation <= tolerance * 400 * (1.0 + max_bound), max_bound_violation, f"<={tolerance * 400 * (1.0 + max_bound)}", "state-weighted bound")
    check("nontrivial spectral residual", min_nonzero_spectral_frobenius > tolerance, min_nonzero_spectral_frobenius, f">{tolerance}", "open collar")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-SPECTRAL-COMMUTANT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": assertions,
        "derived": {
            "context_count": context_count,
            "expected_contexts": expected_contexts,
            "minimum_spectral_group_count": min_spectral_group_count,
            "maximum_spectral_group_count": max_spectral_group_count,
            "max_reduction_error": max_reduction_error,
            "max_scalar_center_error": max_scalar_error,
            "max_spectral_commutator": max_spectral_commutator,
            "max_b_diagonal_error": max_b_diagonal_error,
            "max_spectral_idempotence_error": max_idempotence_error,
            "max_bound_violation": max_bound_violation,
            "minimum_bound_slack": min_bound_slack,
            "maximum_commutator_expectation": max_expectation,
            "maximum_weighted_bound": max_bound,
            "maximum_b_weighted_norm": max_b_norm,
            "maximum_spectral_offdiag_frobenius": max_spectral_frobenius,
            "maximum_coordinate_offdiag_frobenius": max_coordinate_frobenius,
            "minimum_frobenius_gain": min_frobenius_gain,
            "minimum_nonzero_spectral_offdiag_frobenius": min_nonzero_spectral_frobenius,
            "maximum_spectral_left_norm": max_spectral_left_norm,
            "maximum_spectral_right_norm": max_spectral_right_norm,
            "maximum_spectral_to_coordinate_weighted_ratio": max_weighted_ratio,
            "finite_spectral_pinching_reduction_closed": True,
            "finite_state_weighted_commutator_bound_closed": True,
            "finite_hilbert_schmidt_residual_comparison_closed": True,
            "local_collar_bound_proved": False,
            "positive_Euclidean_path_measure_constructed": False,
            "phase_weight_preservation_proved": False,
            "phase_conditioned_influence_contraction_proved": False,
            "cutoff_uniformity_proved": False,
            "volume_uniformity_proved": False,
            "history_uniformity_proved": False,
            "common_core_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False
        },
        "boundary": manifest["boundary"],
        "recorded_by": "Codex"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT LOCAL-Q2 SPECTRAL COMMUTANT PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} max_slack_violation={payload['derived']['max_bound_violation']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
