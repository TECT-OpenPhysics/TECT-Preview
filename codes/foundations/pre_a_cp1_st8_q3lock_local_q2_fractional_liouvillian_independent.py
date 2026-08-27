#!/usr/bin/env python3
"""Independent reconstruction of the R-366 fractional shell audit."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-fractional-liouvillian-manifest.json"
SLUG = "pre_a_cp1_st8_q3lock_local_q2_fractional_liouvillian"
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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=complex)
    for level in range(1, size):
        lowering[level - 1, level] = np.sqrt(float(level))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, identity: np.ndarray) -> np.ndarray:
    answer = np.array([[1.0 + 0.0j]])
    for position in range(2):
        answer = np.kron(answer, single if position == site else identity)
    return answer


def bond_term(left: np.ndarray, right: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def build_system(size: int, parameters: dict[str, str]) -> tuple[np.ndarray, list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = oscillator(size)
    identity = np.eye(size, dtype=complex)
    qs = [embed(q_single, site, identity) for site in range(2)]
    ps = [embed(p_single, site, identity) for site in range(2)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    c = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(qs, ps)]
    bond = hermitian(bond_term(qs[0], qs[1], c, lam))
    terms = onsite + [bond]
    return q_single, terms, hermitian(sum(terms, np.zeros_like(terms[0]))), identity


def unitary(generator: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(generator))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def reduce_site(state: np.ndarray, size: int, site: int) -> np.ndarray:
    tensor = state.reshape(size, size, size, size)
    result = np.zeros((size, size), dtype=complex)
    if site == 0:
        for outside in range(size):
            result += tensor[:, outside, :, outside]
    else:
        for outside in range(size):
            result += tensor[outside, :, outside, :]
    return hermitian(result)


def pvm(q_single: np.ndarray) -> list[np.ndarray]:
    _, vectors = np.linalg.eigh(hermitian(q_single))
    return [np.outer(vectors[:, index], vectors[:, index].conj()) for index in range(vectors.shape[1])]


def probabilities(reduced: np.ndarray, projectors: list[np.ndarray], tolerance: float) -> np.ndarray:
    values = np.array([float(np.trace(projector @ reduced).real) for projector in projectors])
    if float(np.min(values)) < -tolerance:
        raise AssertionError(f"negative probability {float(np.min(values))}")
    values = np.maximum(values, 0.0)
    return values / float(np.sum(values))


def witness(reference: np.ndarray, projectors: list[np.ndarray]) -> np.ndarray:
    dimension = projectors[0].shape[0] ** 2
    answer = np.zeros((dimension, dimension), dtype=complex)
    for probability, projector in zip(reference, projectors):
        answer += np.kron(projector, projector) / probability
    return hermitian(answer)


def pinching(matrix: np.ndarray, vectors: np.ndarray, values: np.ndarray, tolerance: float) -> np.ndarray:
    labels = np.zeros(len(values), dtype=int)
    group = 0
    for index in range(1, len(values)):
        if abs(float(values[index] - values[index - 1])) > tolerance:
            group += 1
        labels[index] = group
    transformed = vectors.conj().T @ matrix @ vectors
    mask = labels[:, None] == labels[None, :]
    return hermitian(vectors @ (transformed * mask) @ vectors.conj().T)


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
    tau = float(Fraction(fixture["time_step"]) / Fraction(fixture["hbar"]))
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

    check("authority", manifest["exploration_id"] == "EXP-001208" and manifest["result_id"] == "R-366" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001208/R-366/false", "provenance")
    context_count = 0
    max_phase_error = 0.0
    max_envelope_violation = -float("inf")
    max_bound_violation = -float("inf")
    max_trace_violation = -float("inf")
    max_unitary_error = 0.0
    max_density_excess = -float("inf")
    max_reduction_error = 0.0
    max_bound = 0.0
    max_change = 0.0
    max_trace_change = 0.0
    max_ratio = 0.0
    min_fractional_norm = float("inf")
    max_theta_one_error = 0.0

    for size in cutoffs:
        q_single, terms, hamiltonian, identity = build_system(size, parameters)
        projectors = pvm(q_single)
        global_identity = np.eye(hamiltonian.shape[0], dtype=complex)
        bond_generator = np.kron(terms[-1], global_identity) + np.kron(global_identity, terms[-1])
        eigenvalues, eigenvectors = np.linalg.eigh(hermitian(bond_generator))
        bond_two = np.kron(unitary(terms[-1], tau, 1.0), unitary(terms[-1], tau, 1.0))
        max_unitary_error = max(max_unitary_error, float(np.linalg.norm(bond_two - unitary(bond_generator, tau, 1.0), ord="fro")))
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        prefixes: dict[tuple[str, int], list[np.ndarray]] = {}
        for name, order in orders.items():
            for sign in signs:
                current = global_identity.copy()
                rows = [current.copy()]
                for index in order:
                    current = unitary(terms[index], sign * tau, 1.0) @ current
                    rows.append(current.copy())
                prefixes[(name, sign)] = rows
        embedded = [[embed(projector, site, identity) for projector in projectors] for site in sites]
        for beta_fraction in betas:
            rho = gibbs(hamiltonian, float(beta_fraction))
            omega = np.kron(rho, rho)
            omega_norm = float(np.linalg.norm(omega, ord="fro"))
            max_density_excess = max(max_density_excess, omega_norm - 1.0)
            for site in sites:
                reference = probabilities(reduce_site(rho, size, site), projectors, tolerance)
                local_witness = witness(reference, embedded[site])
                for order_name in orders:
                    for sign in signs:
                        for prefix_length, prefix in enumerate(prefixes[(order_name, sign)]):
                            for history_adjoint in adjoints:
                                evolution = prefix if not history_adjoint else prefix.conj().T
                                doubled = np.kron(evolution, evolution)
                                moved = hermitian(doubled.conj().T @ local_witness @ doubled)
                                scalar = float(np.trace(omega @ moved).real)
                                centered = hermitian(moved - scalar * np.eye(moved.shape[0], dtype=complex))
                                off = hermitian(centered - pinching(centered, eigenvectors, eigenvalues, tolerance))
                                commutator = bond_generator @ off - off @ bond_generator
                                coeff = eigenvectors.conj().T @ centered @ eigenvectors
                                deltas = eigenvalues[:, None] - eigenvalues[None, :]
                                phases = np.exp(1j * tau * deltas) - 1.0
                                change = bond_two.conj().T @ centered @ bond_two - centered
                                change_norm = float(np.linalg.norm(change, ord="fro"))
                                phase_norm = float(np.sqrt(max(float(np.sum(np.abs(phases) ** 2 * np.abs(coeff) ** 2)), 0.0)))
                                phase_error = abs(change_norm - phase_norm)
                                comm_norm = float(np.linalg.norm(commutator, ord="fro"))
                                trace_change = abs(complex(np.trace(omega @ change)))
                                for theta in thetas:
                                    envelope = (4.0 ** (1.0 - theta)) * np.abs(tau * deltas) ** (2.0 * theta)
                                    envelope_violation = float(np.max(np.abs(phases) ** 2 - envelope))
                                    fractional_norm = float(np.sqrt(max(float(np.sum(np.abs(deltas) ** (2.0 * theta) * np.abs(coeff) ** 2)), 0.0)))
                                    bound = (2.0 ** (1.0 - theta)) * abs(tau) ** theta * fractional_norm
                                    violation = change_norm - bound
                                    trace_bound = omega_norm * bound
                                    trace_violation = trace_change - trace_bound
                                    max_envelope_violation = max(max_envelope_violation, envelope_violation)
                                    max_bound_violation = max(max_bound_violation, violation)
                                    max_trace_violation = max(max_trace_violation, trace_violation)
                                    max_bound = max(max_bound, bound)
                                    max_ratio = max(max_ratio, change_norm / bound if bound > tolerance else 0.0)
                                    if fractional_norm > tolerance:
                                        min_fractional_norm = min(min_fractional_norm, fractional_norm)
                                    if theta == 1.0:
                                        max_theta_one_error = max(max_theta_one_error, abs(bound - abs(tau) * comm_norm))
                                    check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} theta={theta} envelope", envelope_violation <= tolerance * 800, envelope_violation, f"<={tolerance * 800}", "fractional envelope")
                                    check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} theta={theta} bound", violation <= tolerance * 800 * (1.0 + bound), [change_norm, bound], "fractional bound", "fractional bound")
                                    check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} theta={theta} trace", trace_violation <= tolerance * 800 * (1.0 + trace_bound), [trace_change, trace_bound], "state trace", "state trace")
                                    check(f"d={size} beta={beta_fraction} site={site} {order_name} sign={sign} prefix={prefix_length} adj={history_adjoint} theta={theta} phase", phase_error <= tolerance * 800, phase_error, f"<={tolerance * 800}", "spectral phase")
                                    context_count += 1
                                max_phase_error = max(max_phase_error, phase_error)
                                max_change = max(max_change, change_norm)
                                max_trace_change = max(max_trace_change, trace_change)
                                max_reduction_error = max(max_reduction_error, float(np.linalg.norm((bond_generator @ centered - centered @ bond_generator) - commutator, ord="fro")))

    expected = len(cutoffs) * len(betas) * len(sites) * len(orders) * len(signs) * (len(terms) + 1) * len(adjoints) * len(thetas)
    check("coverage", context_count == expected, context_count, expected, "coverage")
    check("unitary factorization", max_unitary_error <= tolerance * 800, max_unitary_error, f"<={tolerance * 800}", "replica bond")
    check("density HS norm", max_density_excess <= tolerance * 800, max_density_excess, f"<={tolerance * 800}", "state trace")
    check("fractional envelope", max_envelope_violation <= tolerance * 800, max_envelope_violation, f"<={tolerance * 800}", "fractional envelope")
    check("fractional bound", max_bound_violation <= tolerance * 800 * (1.0 + max_bound), max_bound_violation, f"<={tolerance * 800 * (1.0 + max_bound)}", "fractional bound")
    check("state trace bound", max_trace_violation <= tolerance * 800 * (1.0 + max_bound), max_trace_violation, f"<={tolerance * 800 * (1.0 + max_bound)}", "state trace")
    check("spectral reduction", max_reduction_error <= tolerance * 800, max_reduction_error, f"<={tolerance * 800}", "spectral commutant")
    check("theta one reduction", max_theta_one_error <= tolerance * 800, max_theta_one_error, f"<={tolerance * 800}", "R365 reduction")
    check("nonzero fractional shell", min_fractional_norm > tolerance, min_fractional_norm, f">{tolerance}", "open collar")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-FRACTIONAL-LIOUVILLIAN",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": assertions,
        "derived": {
            "context_count": context_count,
            "expected_contexts": expected,
            "theta_count": len(thetas),
            "max_phase_identity_error": max_phase_error,
            "max_fractional_envelope_violation": max_envelope_violation,
            "max_fractional_bound_violation": max_bound_violation,
            "max_state_trace_bound_violation": max_trace_violation,
            "max_spectral_reduction_error": max_reduction_error,
            "max_bond_unitary_factorization_error": max_unitary_error,
            "max_density_hs_norm_excess": max_density_excess,
            "maximum_finite_time_change_norm": max_change,
            "maximum_fractional_bound": max_bound,
            "maximum_state_trace_change": max_trace_change,
            "maximum_fractional_to_bound_ratio": max_ratio,
            "minimum_nonzero_fractional_norm": min_fractional_norm,
            "maximum_theta_one_reduction_error": max_theta_one_error,
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
    print(f"INDEPENDENT FRACTIONAL LIOUVILLIAN PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} max_ratio={payload['derived']['maximum_fractional_to_bound_ratio']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
