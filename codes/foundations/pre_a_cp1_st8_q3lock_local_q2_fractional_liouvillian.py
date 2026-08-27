#!/usr/bin/env python3
"""Primary finite fractional-Liouvillian audit for EXP-001208 / R-366."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_fractional_liouvillian"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-fractional-liouvillian-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_q2_pinching_commutator as coordinate  # noqa: E402


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


def spectral_data(generator: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(coordinate.hermitian(generator))


def spectral_pinching(matrix: np.ndarray, vectors: np.ndarray, values: np.ndarray, tolerance: float) -> np.ndarray:
    labels = np.zeros(len(values), dtype=int)
    group = 0
    for index in range(1, len(values)):
        if abs(float(values[index] - values[index - 1])) > tolerance:
            group += 1
        labels[index] = group
    transformed = vectors.conj().T @ matrix @ vectors
    mask = labels[:, None] == labels[None, :]
    return coordinate.hermitian(vectors @ (transformed * mask) @ vectors.conj().T)


def collision_witness(reference: np.ndarray, projectors: list[np.ndarray]) -> np.ndarray:
    dimension = projectors[0].shape[0] ** 2
    witness = np.zeros((dimension, dimension), dtype=complex)
    for probability, projector in zip(reference, projectors):
        witness += np.kron(projector, projector) / probability
    return coordinate.hermitian(witness)


def measured(reduced: np.ndarray, projectors: list[np.ndarray], tolerance: float) -> np.ndarray:
    values = np.array([float(np.trace(projector @ reduced).real) for projector in projectors])
    if float(np.min(values)) < -tolerance:
        raise AssertionError(f"negative measured probability {float(np.min(values))}")
    values = np.maximum(values, 0.0)
    values /= float(np.sum(values))
    return values


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    volume = int(fixture["volume"])
    cutoffs = [int(value) for value in fixture["cutoff_values"]]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    sites = [int(value) for value in fixture["site_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    thetas = [float(Fraction(value)) for value in fixture["theta_values"]]
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tau = delta / hbar
    tolerance = float(fixture["finite_tolerance"])
    parameters = fixture["parameters"]
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 96:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001208" and manifest["result_id"] == "R-366", [manifest["exploration_id"], manifest["result_id"]], "EXP-001208/R-366", "provenance")
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["local_modular_square_function_proved"] is False, manifest["scope"], "finite-only", "scope")
    context_count = 0
    max_phase_identity_error = 0.0
    max_envelope_violation = -float("inf")
    max_bound_violation = -float("inf")
    max_trace_violation = -float("inf")
    max_reduction_error = 0.0
    max_unitary_factor_error = 0.0
    max_density_norm_excess = -float("inf")
    max_change_norm = 0.0
    max_fractional_bound = 0.0
    max_trace_change = 0.0
    max_ratio = 0.0
    min_nonzero_fractional_norm = float("inf")
    max_theta_one_difference = 0.0

    for size in cutoffs:
        qs, hamiltonian, terms = coordinate.base.split_system(volume, size, parameters)
        q_single, _ = coordinate.q3.oscillator(size)
        projectors = coordinate.pvm(q_single)
        identity_single = np.eye(size, dtype=complex)
        identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
        bond_generator = np.kron(terms[-1], identity_global) + np.kron(identity_global, terms[-1])
        eigenvalues, eigenvectors = spectral_data(bond_generator)
        bond_unitary = coordinate.base.unitary(terms[-1], delta, hbar)
        bond_two = np.kron(bond_unitary, bond_unitary)
        exact_bond_unitary = coordinate.base.unitary(bond_generator, delta, hbar)
        max_unitary_factor_error = max(max_unitary_factor_error, float(np.linalg.norm(bond_two - exact_bond_unitary, ord="fro")))
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        prefix_bank: dict[tuple[str, int], list[np.ndarray]] = {}
        for order_name, order in orders.items():
            for sign in signs:
                current = identity_global.copy()
                rows = [current.copy()]
                for index in order:
                    current = coordinate.base.unitary(terms[index], sign * delta, hbar) @ current
                    rows.append(current.copy())
                prefix_bank[(order_name, sign)] = rows
        embedded = [[coordinate.base.embed(projector, site, volume, identity_single) for projector in projectors] for site in sites]
        for beta_fraction in betas:
            rho = coordinate.base.gibbs(hamiltonian, float(beta_fraction))
            omega = np.kron(rho, rho)
            omega_norm = float(np.linalg.norm(omega, ord="fro"))
            max_density_norm_excess = max(max_density_norm_excess, omega_norm - 1.0)
            for site in sites:
                reference = measured(coordinate.base.reduced_site(rho, size, volume, site), projectors, tolerance)
                witness = collision_witness(reference, embedded[site])
                for order_name in orders:
                    for sign in signs:
                        for prefix_length, prefix in enumerate(prefix_bank[(order_name, sign)]):
                            for history_adjoint in adjoints:
                                evolution = prefix if not history_adjoint else prefix.conj().T
                                evolution_two = np.kron(evolution, evolution)
                                moved = coordinate.hermitian(evolution_two.conj().T @ witness @ evolution_two)
                                scalar = float(np.trace(omega @ moved).real)
                                centered = coordinate.hermitian(moved - scalar * np.eye(moved.shape[0], dtype=complex))
                                spectral_off = coordinate.hermitian(centered - spectral_pinching(centered, eigenvectors, eigenvalues, tolerance))
                                reduced_comm = bond_generator @ spectral_off - spectral_off @ bond_generator
                                transformed = eigenvectors.conj().T @ centered @ eigenvectors
                                deltas = eigenvalues[:, None] - eigenvalues[None, :]
                                phases = np.exp(1j * tau * deltas) - 1.0
                                change = bond_two.conj().T @ centered @ bond_two - centered
                                change_norm = float(np.linalg.norm(change, ord="fro"))
                                phase_norm = float(np.sqrt(max(float(np.sum(np.abs(phases) ** 2 * np.abs(transformed) ** 2)), 0.0)))
                                phase_error = abs(change_norm - phase_norm)
                                comm_norm = float(np.linalg.norm(reduced_comm, ord="fro"))
                                trace_change = abs(complex(np.trace(omega @ change)))
                                for theta in thetas:
                                    envelope = (4.0 ** (1.0 - theta)) * np.abs(tau * deltas) ** (2.0 * theta)
                                    envelope_violation = float(np.max(np.abs(phases) ** 2 - envelope))
                                    fractional_norm = float(np.sqrt(max(float(np.sum(np.abs(deltas) ** (2.0 * theta) * np.abs(transformed) ** 2)), 0.0)))
                                    fractional_bound = (2.0 ** (1.0 - theta)) * abs(tau) ** theta * fractional_norm
                                    bound_violation = change_norm - fractional_bound
                                    trace_bound = omega_norm * fractional_bound
                                    trace_violation = trace_change - trace_bound
                                    max_envelope_violation = max(max_envelope_violation, envelope_violation)
                                    max_bound_violation = max(max_bound_violation, bound_violation)
                                    max_trace_violation = max(max_trace_violation, trace_violation)
                                    max_fractional_bound = max(max_fractional_bound, fractional_bound)
                                    max_ratio = max(max_ratio, change_norm / fractional_bound if fractional_bound > tolerance else 0.0)
                                    if fractional_norm > tolerance:
                                        min_nonzero_fractional_norm = min(min_nonzero_fractional_norm, fractional_norm)
                                    if abs(theta - 1.0) < tolerance:
                                        max_theta_one_difference = max(max_theta_one_difference, abs(fractional_bound - abs(tau) * comm_norm))
                                    check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} theta={theta} envelope", envelope_violation <= tolerance * 800, envelope_violation, f"<={tolerance * 800}", "fractional envelope")
                                    check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} theta={theta} bound", bound_violation <= tolerance * 800 * (1.0 + fractional_bound), [change_norm, fractional_bound], "fractional bound", "fractional bound")
                                    check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} theta={theta} trace", trace_violation <= tolerance * 800 * (1.0 + trace_bound), [trace_change, trace_bound], "state trace", "state trace")
                                    check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} theta={theta} phase", phase_error <= tolerance * 800, phase_error, f"<={tolerance * 800}", "spectral phase")
                                    context_count += 1
                                max_phase_identity_error = max(max_phase_identity_error, phase_error)
                                max_change_norm = max(max_change_norm, change_norm)
                                max_trace_change = max(max_trace_change, trace_change)
                                max_reduction_error = max(max_reduction_error, float(np.linalg.norm((bond_generator @ centered - centered @ bond_generator) - reduced_comm, ord="fro")))

    expected_contexts = len(cutoffs) * len(betas) * len(sites) * len(orders) * len(signs) * (len(terms) + 1) * len(adjoints) * len(thetas)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("density HS norm", max_density_norm_excess <= tolerance * 800, max_density_norm_excess, f"<={tolerance * 800}", "state trace")
    check("unitary factorization", max_unitary_factor_error <= tolerance * 800, max_unitary_factor_error, f"<={tolerance * 800}", "replica bond")
    check("fractional envelope", max_envelope_violation <= tolerance * 800, max_envelope_violation, f"<={tolerance * 800}", "fractional envelope")
    check("fractional bound", max_bound_violation <= tolerance * 800 * (1.0 + max_fractional_bound), max_bound_violation, f"<={tolerance * 800 * (1.0 + max_fractional_bound)}", "fractional bound")
    check("state trace bound", max_trace_violation <= tolerance * 800 * (1.0 + max_fractional_bound), max_trace_violation, f"<={tolerance * 800 * (1.0 + max_fractional_bound)}", "state trace")
    check("theta one reduction", max_theta_one_difference <= tolerance * 800, max_theta_one_difference, f"<={tolerance * 800}", "R365 reduction")
    check("nonzero fractional shell", min_nonzero_fractional_norm > tolerance, min_nonzero_fractional_norm, f">{tolerance}", "open collar")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-FRACTIONAL-LIOUVILLIAN",
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
            "theta_count": len(thetas),
            "max_phase_identity_error": max_phase_identity_error,
            "max_fractional_envelope_violation": max_envelope_violation,
            "max_fractional_bound_violation": max_bound_violation,
            "max_state_trace_bound_violation": max_trace_violation,
            "max_spectral_reduction_error": max_reduction_error,
            "max_bond_unitary_factorization_error": max_unitary_factor_error,
            "max_density_hs_norm_excess": max_density_norm_excess,
            "maximum_finite_time_change_norm": max_change_norm,
            "maximum_fractional_bound": max_fractional_bound,
            "maximum_state_trace_change": max_trace_change,
            "maximum_fractional_to_bound_ratio": max_ratio,
            "minimum_nonzero_fractional_norm": min_nonzero_fractional_norm,
            "maximum_theta_one_reduction_error": max_theta_one_difference,
            "fractional_liouvillian_bound_closed": True,
            "fractional_theta_half_pilot_checked": True,
            "local_modular_square_function_proved": False,
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
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FRACTIONAL LIOUVILLIAN PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} max_ratio={payload['derived']['maximum_fractional_to_bound_ratio']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
