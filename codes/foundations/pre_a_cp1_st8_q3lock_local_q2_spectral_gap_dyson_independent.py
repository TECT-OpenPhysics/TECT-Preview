#!/usr/bin/env python3
"""Non-importing independent spectral-gap/Duhamel reconstruction for R-365."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_spectral_gap_dyson"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-spectral-gap-dyson-manifest.json"
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
    return c * difference @ difference / 2.0 + lam * (difference @ difference) @ (left @ left + right @ right) / 4.0


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


def spectral_data(generator: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(clean(generator))


def spectral_pinching(matrix: np.ndarray, eigenvectors: np.ndarray, eigenvalues: np.ndarray, tolerance: float) -> np.ndarray:
    labels = np.zeros(len(eigenvalues), dtype=int)
    group = 0
    for index in range(1, len(eigenvalues)):
        if abs(float(eigenvalues[index] - eigenvalues[index - 1])) > tolerance:
            group += 1
        labels[index] = group
    transformed = eigenvectors.conj().T @ matrix @ eigenvectors
    mask = labels[:, None] == labels[None, :]
    return clean(eigenvectors @ (transformed * mask) @ eigenvectors.conj().T)


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
    tau = delta / hbar
    tolerance = float(fixture["finite_tolerance"])
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

    check("authority", manifest["exploration_id"] == "EXP-001207" and manifest["result_id"] == "R-365" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001207/R-365/false", "provenance")
    context_count = 0
    max_commutator_formula_error = 0.0
    max_phase_identity_error = 0.0
    max_reduction_error = 0.0
    max_duhamel_violation = -float("inf")
    max_trace_violation = -float("inf")
    max_unitary_factor_error = 0.0
    max_omega_norm_excess = -float("inf")
    max_commutator_norm = 0.0
    max_finite_change_norm = 0.0
    max_trace_change = 0.0
    max_duhamel_bound = 0.0
    max_trace_bound = 0.0
    min_commutator_norm = float("inf")
    max_damped_ratio = 0.0
    min_nonzero_commutator = float("inf")
    max_spectral_group_count = 0
    min_spectral_group_count = float("inf")

    for size in cutoffs:
        q_single, terms, hamiltonian, identity = build_system(size, parameters)
        projectors = local_pvm(q_single)
        global_identity = np.eye(hamiltonian.shape[0], dtype=complex)
        bond_generator = np.kron(terms[-1], global_identity) + np.kron(global_identity, terms[-1])
        eigenvalues, eigenvectors = spectral_data(bond_generator)
        labels = np.zeros(len(eigenvalues), dtype=int)
        group = 0
        for index in range(1, len(eigenvalues)):
            if abs(float(eigenvalues[index] - eigenvalues[index - 1])) > tolerance:
                group += 1
            labels[index] = group
        min_spectral_group_count = min(min_spectral_group_count, group + 1)
        max_spectral_group_count = max(max_spectral_group_count, group + 1)
        bond_unitary = spectral_unitary(terms[-1], delta, hbar)
        bond_two = np.kron(bond_unitary, bond_unitary)
        exact_bond_unitary = spectral_unitary(bond_generator, delta, hbar)
        max_unitary_factor_error = max(max_unitary_factor_error, float(np.linalg.norm(bond_two - exact_bond_unitary, ord="fro")))
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
            omega_norm = float(np.linalg.norm(omega, ord="fro"))
            max_omega_norm_excess = max(max_omega_norm_excess, omega_norm - 1.0)
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
                                comm = bond_generator @ centered - centered @ bond_generator
                                spectral_off = clean(centered - spectral_pinching(centered, eigenvectors, eigenvalues, tolerance=tolerance))
                                reduced_comm = bond_generator @ spectral_off - spectral_off @ bond_generator
                                coeff = eigenvectors.conj().T @ centered @ eigenvectors
                                comm_formula = float(np.sqrt(max(float(np.sum((eigenvalues[:, None] - eigenvalues[None, :]) ** 2 * np.abs(coeff) ** 2)), 0.0)))
                                comm_norm = float(np.linalg.norm(comm, ord="fro"))
                                commutator_formula_error = abs(comm_norm - comm_formula)
                                change = bond_two.conj().T @ centered @ bond_two - centered
                                change_norm = float(np.linalg.norm(change, ord="fro"))
                                phase = np.exp(1j * tau * (eigenvalues[:, None] - eigenvalues[None, :])) - 1.0
                                phase_norm = float(np.sqrt(max(float(np.sum(np.abs(phase) ** 2 * np.abs(coeff) ** 2)), 0.0)))
                                phase_identity_error = abs(change_norm - phase_norm)
                                duhamel_bound = tau * comm_norm
                                trace_change = abs(complex(np.trace(omega @ change)))
                                trace_bound = omega_norm * duhamel_bound
                                reduction_error = float(np.linalg.norm(comm - reduced_comm, ord="fro"))
                                max_commutator_formula_error = max(max_commutator_formula_error, commutator_formula_error)
                                max_phase_identity_error = max(max_phase_identity_error, phase_identity_error)
                                max_reduction_error = max(max_reduction_error, reduction_error)
                                max_duhamel_violation = max(max_duhamel_violation, change_norm - duhamel_bound)
                                max_trace_violation = max(max_trace_violation, trace_change - trace_bound)
                                max_unitary_factor_error = max(max_unitary_factor_error, float(np.linalg.norm(bond_two - exact_bond_unitary, ord="fro")))
                                max_commutator_norm = max(max_commutator_norm, comm_norm)
                                max_finite_change_norm = max(max_finite_change_norm, change_norm)
                                max_trace_change = max(max_trace_change, trace_change)
                                max_duhamel_bound = max(max_duhamel_bound, duhamel_bound)
                                max_trace_bound = max(max_trace_bound, trace_bound)
                                min_commutator_norm = min(min_commutator_norm, comm_norm)
                                if comm_norm > tolerance:
                                    min_nonzero_commutator = min(min_nonzero_commutator, comm_norm)
                                    max_damped_ratio = max(max_damped_ratio, change_norm / duhamel_bound if duhamel_bound > tolerance else 0.0)
                                context_count += 1
                                check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} spectral", commutator_formula_error <= tolerance * 800, commutator_formula_error, f"<={tolerance * 800}", "spectral gap identity")
                                check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} phase", phase_identity_error <= tolerance * 800, phase_identity_error, f"<={tolerance * 800}", "finite-time spectral identity")
                                check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} bound", change_norm <= duhamel_bound + tolerance * 800 * (1.0 + duhamel_bound), [change_norm, duhamel_bound], "Duhamel bound", "finite-time bound")

    expected_contexts = len(cutoffs) * len(betas) * len(sites) * len(orders) * len(signs) * (len(terms) + 1) * len(adjoints)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("bond unitary factorization", max_unitary_factor_error <= tolerance * 800, max_unitary_factor_error, f"<={tolerance * 800}", "replica bond")
    check("density HS norm", max_omega_norm_excess <= tolerance * 800, max_omega_norm_excess, f"<={tolerance * 800}", "state trace")
    check("spectral reduction", max_reduction_error <= tolerance * 800, max_reduction_error, f"<={tolerance * 800}", "spectral commutant")
    check("Duhamel bound", max_duhamel_violation <= tolerance * 800 * (1.0 + max_duhamel_bound), max_duhamel_violation, f"<={tolerance * 800 * (1.0 + max_duhamel_bound)}", "finite-time bound")
    check("state trace bound", max_trace_violation <= tolerance * 800 * (1.0 + max_trace_bound), max_trace_violation, f"<={tolerance * 800 * (1.0 + max_trace_bound)}", "state trace")
    check("nonzero spectral commutator", min_nonzero_commutator > tolerance, min_nonzero_commutator, f">{tolerance}", "open collar")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-SPECTRAL-GAP-DYSON",
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
            "max_commutator_spectral_formula_error": max_commutator_formula_error,
            "max_phase_identity_error": max_phase_identity_error,
            "max_spectral_reduction_error": max_reduction_error,
            "max_duhamel_violation": max_duhamel_violation,
            "max_state_trace_violation": max_trace_violation,
            "max_bond_unitary_factorization_error": max_unitary_factor_error,
            "max_density_hs_norm_excess": max_omega_norm_excess,
            "maximum_commutator_norm": max_commutator_norm,
            "maximum_finite_time_change_norm": max_finite_change_norm,
            "maximum_state_trace_change": max_trace_change,
            "maximum_duhamel_bound": max_duhamel_bound,
            "maximum_state_trace_bound": max_trace_bound,
            "minimum_commutator_norm": min_commutator_norm,
            "minimum_nonzero_commutator_norm": min_nonzero_commutator,
            "maximum_finite_time_to_duhamel_ratio": max_damped_ratio,
            "finite_spectral_gap_duhamel_bound_closed": True,
            "finite_state_trace_influence_bound_closed": True,
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
    print(f"INDEPENDENT LOCAL-Q2 SPECTRAL GAP DYSON PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} max_duhamel_violation={payload['derived']['max_duhamel_violation']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
