#!/usr/bin/env python3
"""Primary finite FI-2b pinching and state-weighted commutator audit.

The audit treats the coordinate eigenbasis as a finite conditional expectation.
For a coordinate-diagonal doubled bond generator B and any centered moved
collision witness X, it checks [B,X]=[B,X-E_D(X)] and the weighted
Cauchy-Schwarz bound for Tr(omega [B,X]).  It is a finite diagnostic only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_q2_pinching_commutator"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-pinching-commutator-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress as base  # noqa: E402
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def pvm(q_single: np.ndarray) -> list[np.ndarray]:
    _, vectors = np.linalg.eigh(hermitian(q_single))
    return [np.outer(vectors[:, index], vectors[:, index].conj()) for index in range(vectors.shape[1])]


def measured(reduced: np.ndarray, projectors: list[np.ndarray], tolerance: float) -> np.ndarray:
    values = np.array([float(np.trace(projector @ reduced).real) for projector in projectors])
    if float(np.min(values)) < -tolerance:
        raise AssertionError(f"negative measured probability {float(np.min(values))}")
    values = np.maximum(values, 0.0)
    values /= float(np.sum(values))
    return values


def collision_witness(reference: np.ndarray, projectors: list[np.ndarray]) -> np.ndarray:
    dimension = projectors[0].shape[0] ** 2
    witness = np.zeros((dimension, dimension), dtype=complex)
    for probability, projector in zip(reference, projectors):
        witness += np.kron(projector, projector) / probability
    return hermitian(witness)


def coordinate_basis(q_single: np.ndarray, volume: int) -> np.ndarray:
    _, vectors = np.linalg.eigh(hermitian(q_single))
    single = vectors
    global_basis = single
    identity = np.eye(single.shape[0], dtype=complex)
    for _ in range(volume - 1):
        global_basis = np.kron(global_basis, single)
    del identity
    return np.kron(global_basis, global_basis)


def pinching(matrix: np.ndarray, basis: np.ndarray) -> np.ndarray:
    coordinate = basis.conj().T @ matrix @ basis
    diagonal = np.diag(np.diag(coordinate))
    return hermitian(basis @ diagonal @ basis.conj().T)


def weighted_left(state: np.ndarray, matrix: np.ndarray) -> float:
    value = float(np.trace(matrix.conj().T @ state @ matrix).real)
    return float(np.sqrt(max(value, 0.0)))


def weighted_right(state: np.ndarray, matrix: np.ndarray) -> float:
    value = float(np.trace(state @ matrix.conj().T @ matrix).real)
    return float(np.sqrt(max(value, 0.0)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    volume = int(fixture["volume"])
    cutoffs = [int(value) for value in fixture["cutoff_values"]]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    sites = [int(value) for value in fixture["site_values"]]
    time_signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    parameters = fixture["parameters"]
    tolerance = float(fixture["finite_tolerance"])
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 96:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001205" and manifest["result_id"] == "R-363", [manifest["exploration_id"], manifest["result_id"]], "EXP-001205/R-363", "provenance")
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["local_collar_bound_proved"] is False, manifest["scope"], "finite-only", "scope")
    check("fixture", volume == 2 and fixture["prefix_policy"] == "every prefix", [volume, fixture["prefix_policy"]], "V=2/every prefix", "fixture")

    context_count = 0
    max_reduction_error = 0.0
    max_scalar_error = 0.0
    max_diagonal_commutator = 0.0
    max_b_diagonal_error = 0.0
    max_bound_violation = -float("inf")
    min_bound_slack = float("inf")
    max_expectation = 0.0
    max_bound = 0.0
    max_left_norm = 0.0
    max_right_norm = 0.0
    max_b_norm = 0.0
    max_offdiag_frobenius = 0.0
    min_nonzero_offdiag = float("inf")
    max_commutator_frobenius = 0.0

    for size in cutoffs:
        qs, hamiltonian, terms = base.split_system(volume, size, parameters)
        q_single, _ = q3.oscillator(size)
        projectors = pvm(q_single)
        identity_single = np.eye(size, dtype=complex)
        identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
        basis = coordinate_basis(q_single, volume)
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        prefixes = {}
        for order_name, order in orders.items():
            for time_sign in time_signs:
                current = identity_global.copy()
                bank = [current.copy()]
                for index in order:
                    current = base.unitary(terms[index], time_sign * delta, hbar) @ current
                    bank.append(current.copy())
                prefixes[(order_name, time_sign)] = bank
        embedded = [[base.embed(projector, site, volume, identity_single) for projector in projectors] for site in sites]
        bond_generator = np.kron(terms[-1], identity_global) + np.kron(identity_global, terms[-1])
        max_b_diagonal_error = max(max_b_diagonal_error, float(np.linalg.norm(bond_generator - pinching(bond_generator, basis), ord="fro")))

        for beta_fraction in betas:
            rho = base.gibbs(hamiltonian, float(beta_fraction))
            omega = np.kron(rho, rho)
            for site in sites:
                reference_reduced = base.reduced_site(rho, size, volume, site)
                reference = measured(reference_reduced, projectors, tolerance)
                witness = collision_witness(reference, embedded[site])
                for order_name in orders:
                    for time_sign in time_signs:
                        for prefix_length, prefix in enumerate(prefixes[(order_name, time_sign)]):
                            for history_adjoint in adjoints:
                                evolution = prefix if not history_adjoint else prefix.conj().T
                                evolution_two = np.kron(evolution, evolution)
                                moved = hermitian(evolution_two.conj().T @ witness @ evolution_two)
                                scalar = float(np.trace(omega @ moved).real)
                                centered = hermitian(moved - scalar * np.eye(moved.shape[0], dtype=complex))
                                pinched = pinching(centered, basis)
                                offdiag = hermitian(centered - pinched)
                                comm = bond_generator @ moved - moved @ bond_generator
                                centered_comm = bond_generator @ centered - centered @ bond_generator
                                offdiag_comm = bond_generator @ offdiag - offdiag @ bond_generator
                                reduction_error = float(np.linalg.norm(centered_comm - offdiag_comm, ord="fro"))
                                scalar_error = float(np.linalg.norm((bond_generator @ moved - moved @ bond_generator) - centered_comm, ord="fro"))
                                diagonal_commutator = float(np.linalg.norm(bond_generator @ pinched - pinched @ bond_generator, ord="fro"))
                                b_norm = float(np.sqrt(max(float(np.trace(omega @ bond_generator @ bond_generator).real), 0.0)))
                                left_norm = weighted_left(omega, offdiag)
                                right_norm = weighted_right(omega, offdiag)
                                expectation = abs(complex(np.trace(omega @ comm)))
                                bound = b_norm * (left_norm + right_norm)
                                slack = bound - expectation
                                context_count += 1
                                max_reduction_error = max(max_reduction_error, reduction_error)
                                max_scalar_error = max(max_scalar_error, scalar_error)
                                max_diagonal_commutator = max(max_diagonal_commutator, diagonal_commutator)
                                max_bound_violation = max(max_bound_violation, expectation - bound)
                                min_bound_slack = min(min_bound_slack, slack)
                                max_expectation = max(max_expectation, expectation)
                                max_bound = max(max_bound, bound)
                                max_left_norm = max(max_left_norm, left_norm)
                                max_right_norm = max(max_right_norm, right_norm)
                                max_b_norm = max(max_b_norm, b_norm)
                                offdiag_frobenius = float(np.linalg.norm(offdiag, ord="fro"))
                                max_offdiag_frobenius = max(max_offdiag_frobenius, offdiag_frobenius)
                                if offdiag_frobenius > tolerance:
                                    min_nonzero_offdiag = min(min_nonzero_offdiag, offdiag_frobenius)
                                max_commutator_frobenius = max(max_commutator_frobenius, float(np.linalg.norm(comm, ord="fro")))
                                check(f"d={size} beta={beta_fraction} site={site} order={order_name} sign={time_sign} prefix={prefix_length} adj={history_adjoint} reduction", reduction_error <= tolerance * 200, reduction_error, f"<={tolerance * 200}", "pinching reduction")
                                check(f"d={size} beta={beta_fraction} site={site} order={order_name} sign={time_sign} prefix={prefix_length} adj={history_adjoint} diagonal", diagonal_commutator <= tolerance * 200, diagonal_commutator, f"<={tolerance * 200}", "diagonal conditional expectation")
                                check(f"d={size} beta={beta_fraction} site={site} order={order_name} sign={time_sign} prefix={prefix_length} adj={history_adjoint} bound", expectation <= bound + tolerance * 200 * (1.0 + bound), [expectation, bound], "weighted Cauchy", "state-weighted bound")

    expected_contexts = len(cutoffs) * len(betas) * len(sites) * len(orders) * len(time_signs) * (len(terms) + 1) * len(adjoints)
    check("context coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("B coordinate diagonal", max_b_diagonal_error <= tolerance * 200, max_b_diagonal_error, f"<={tolerance * 200}", "conditional expectation")
    check("scalar center", max_scalar_error <= tolerance * 200, max_scalar_error, f"<={tolerance * 200}", "centering")
    check("reduction", max_reduction_error <= tolerance * 200, max_reduction_error, f"<={tolerance * 200}", "pinching reduction")
    check("diagonal commutation", max_diagonal_commutator <= tolerance * 200, max_diagonal_commutator, f"<={tolerance * 200}", "conditional expectation")
    check("weighted bound", max_bound_violation <= tolerance * 200 * (1.0 + max_bound), max_bound_violation, f"<={tolerance * 200 * (1.0 + max_bound)}", "state-weighted bound")
    check("nontrivial offdiagonal", min_nonzero_offdiag > tolerance, min_nonzero_offdiag, f">{tolerance}", "open collar")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-PINCHING-COMMUTATOR",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": {
            "context_count": context_count,
            "expected_contexts": expected_contexts,
            "max_reduction_error": max_reduction_error,
            "max_scalar_center_error": max_scalar_error,
            "max_diagonal_commutator": max_diagonal_commutator,
            "max_b_diagonal_error": max_b_diagonal_error,
            "max_bound_violation": max_bound_violation,
            "minimum_bound_slack": min_bound_slack,
            "maximum_commutator_expectation": max_expectation,
            "maximum_weighted_bound": max_bound,
            "maximum_b_weighted_norm": max_b_norm,
            "maximum_offdiag_left_norm": max_left_norm,
            "maximum_offdiag_right_norm": max_right_norm,
            "maximum_offdiag_frobenius": max_offdiag_frobenius,
            "minimum_nonzero_offdiag_frobenius": min_nonzero_offdiag,
            "maximum_commutator_frobenius": max_commutator_frobenius,
            "finite_pinching_reduction_closed": True,
            "finite_state_weighted_commutator_bound_closed": True,
            "finite_prefix_fixture_checked": True,
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
    print(f"PRIMARY LOCAL-Q2 PINCHING COMMUTATOR PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} max_slack_violation={payload['derived']['max_bound_violation']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
