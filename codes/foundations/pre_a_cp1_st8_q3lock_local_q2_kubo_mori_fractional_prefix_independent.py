#!/usr/bin/env python3
"""Independent local Kubo--Mori weighted fractional-prefix audit for EXP-001210 / R-368."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_fractional_prefix"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-fractional-prefix-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as graph  # noqa: E402


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


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond(left: np.ndarray, right: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return hermitian(c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0)


def build_system(volume: int, size: int, parameters: dict[str, str]) -> tuple[np.ndarray, np.ndarray, list[np.ndarray], np.ndarray]:
    q_single, p_single = graph.oscillator(size)
    identity = np.eye(size, dtype=complex)
    qs = [embed(q_single, site, volume, identity) for site in range(volume)]
    ps = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(parameters[key])) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(qs, ps)]
    bonds = [bond(qs[left], qs[right], c, lam) for left, right in graph.graph_edges(volume)]
    zero = np.zeros_like(qs[0])
    full = hermitian(sum(onsite, zero) + sum(bonds, zero))
    return q_single, full, onsite + bonds, identity


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def reduce_site(state: np.ndarray, size: int, volume: int, site: int) -> np.ndarray:
    tensor = state.reshape((size,) * (2 * volume))
    reduced = np.zeros((size, size), dtype=complex)
    outside = [index for index in range(volume) if index != site]
    for values in np.ndindex(*(size for _ in outside)):
        row = [slice(None)] * volume
        column = [slice(None)] * volume
        for index, value in zip(outside, values):
            row[index] = value
            column[index] = value
        reduced += tensor[tuple(row + column)]
    return hermitian(reduced)


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
    group_id = 0
    for index in range(1, len(values)):
        if abs(float(values[index] - values[index - 1])) > tolerance:
            group_id += 1
        labels[index] = group_id
    transformed = vectors.conj().T @ matrix @ vectors
    return hermitian(vectors @ (transformed * (labels[:, None] == labels[None, :])) @ vectors.conj().T)


def all_prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[tuple[int, np.ndarray]]:
    identity = np.eye(terms[0].shape[0], dtype=complex)
    current = identity.copy()
    rows: list[tuple[int, np.ndarray]] = []
    for position in range(len(order) + 1):
        rows.append((position, current.copy()))
        if position < len(order):
            current = unitary(terms[order[position]], sign * delta, hbar) @ current
    return rows


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    theta = float(Fraction(fixture["theta"]))
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tolerance = float(fixture["finite_tolerance"])
    parameters = fixture["parameters"]
    if not (0.0 < theta <= 1.0):
        raise AssertionError("weighted fixture must contain theta in (0,1]")
    gap_tolerance = float(fixture["log_mean_gap_tolerance"])
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group_name: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 96:
            checks.append({"name": name, "group": group_name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001210" and manifest["result_id"] == "R-368" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001210/R-368/false", "provenance")
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["weighted_cutoff_uniformity_proved"] is False, manifest["scope"], "finite-weighted-stress-only", "scope")
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
    max_fractional_norm = 0.0
    min_fractional_norm = float("inf")
    max_kubo_phase_error = 0.0
    max_kubo_weighted_bound_violation = -float("inf")
    max_kubo_fractional_norm = 0.0
    max_kubo_fractional_bound = 0.0
    max_kubo_ratio = 0.0
    min_kubo_nonzero_norm = float("inf")
    max_kubo_weight_asymmetry = 0.0
    min_kubo_weight = float("inf")
    max_arithmetic_to_kubo_ratio = 0.0
    per_regime: list[dict[str, Any]] = []

    for regime in fixture["regimes"]:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        start_count = context_count
        regime_max_norm = 0.0
        regime_max_bound = 0.0
        regime_max_kubo_norm = 0.0
        regime_max_kubo_bound = 0.0
        first_terms: list[np.ndarray] | None = None
        for size in cutoffs:
            q_single, hamiltonian, terms, identity_single = build_system(volume, size, parameters)
            first_terms = terms
            projectors = pvm(q_single)
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            bond_generator = np.kron(terms[-1], identity_global) + np.kron(identity_global, terms[-1])
            eigenvalues, eigenvectors = np.linalg.eigh(hermitian(bond_generator))
            bond_two = np.kron(unitary(terms[-1], delta, hbar), unitary(terms[-1], delta, hbar))
            max_unitary_error = max(max_unitary_error, float(np.linalg.norm(bond_two - unitary(bond_generator, delta, hbar), ord="fro")))
            orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
            embedded = [[embed(projector, site, volume, identity_single) for projector in projectors] for site in sites]
            for beta_fraction in betas:
                beta = float(beta_fraction)
                rho = gibbs(hamiltonian, beta)
                omega = np.kron(rho, rho)
                omega_norm = float(np.linalg.norm(omega, ord="fro"))
                max_density_excess = max(max_density_excess, omega_norm - 1.0)
                bond_probabilities = np.exp(-beta * (eigenvalues - float(np.min(eigenvalues))))
                bond_probabilities /= float(np.sum(bond_probabilities))
                log_gap = np.log(bond_probabilities)[:, None] - np.log(bond_probabilities)[None, :]
                kubo_weights = np.empty_like(log_gap)
                arithmetic_weights = 0.5 * (bond_probabilities[:, None] + bond_probabilities[None, :])
                close_gap = np.abs(log_gap) <= gap_tolerance
                np.divide(bond_probabilities[:, None] - bond_probabilities[None, :], log_gap, out=kubo_weights, where=~close_gap)
                kubo_weights[close_gap] = arithmetic_weights[close_gap]
                kubo_weights = hermitian(kubo_weights)
                check(f"V={volume} d={size} beta={beta_fraction} Kubo normalization", np.isfinite(bond_probabilities).all() and abs(float(np.sum(bond_probabilities)) - 1.0) <= gap_tolerance, float(np.sum(bond_probabilities)), 1.0, "Kubo--Mori state")
                check(f"V={volume} d={size} beta={beta_fraction} Kubo symmetry", float(np.max(np.abs(kubo_weights - kubo_weights.T))) <= gap_tolerance, float(np.max(np.abs(kubo_weights - kubo_weights.T))), f"<={gap_tolerance}", "Kubo--Mori state")
                check(f"V={volume} d={size} beta={beta_fraction} Kubo positivity", float(np.min(kubo_weights)) >= -gap_tolerance, float(np.min(kubo_weights)), f">={-gap_tolerance}", "Kubo--Mori state")
                max_kubo_weight_asymmetry = max(max_kubo_weight_asymmetry, float(np.max(np.abs(kubo_weights - kubo_weights.T))))
                min_kubo_weight = min(min_kubo_weight, float(np.min(kubo_weights)))
                for site in sites:
                    reference = probabilities(reduce_site(rho, size, volume, site), projectors, tolerance)
                    local_witness = witness(reference, embedded[site])
                    for order_name, order in orders.items():
                        for sign in signs:
                            for prefix_length, prefix in all_prefixes(terms, order, sign, delta, hbar):
                                for history_adjoint in adjoints:
                                    evolution = prefix if not history_adjoint else prefix.conj().T
                                    doubled = np.kron(evolution, evolution)
                                    moved = hermitian(doubled.conj().T @ local_witness @ doubled)
                                    scalar = float(np.trace(omega @ moved).real)
                                    centered = hermitian(moved - scalar * np.eye(moved.shape[0], dtype=complex))
                                    off = hermitian(centered - pinching(centered, eigenvectors, eigenvalues, tolerance))
                                    reduced_comm = bond_generator @ off - off @ bond_generator
                                    coeff = eigenvectors.conj().T @ centered @ eigenvectors
                                    deltas = eigenvalues[:, None] - eigenvalues[None, :]
                                    phases = np.exp(1j * delta * deltas / hbar) - 1.0
                                    change = bond_two.conj().T @ centered @ bond_two - centered
                                    change_norm = float(np.linalg.norm(change, ord="fro"))
                                    phase_norm = float(np.sqrt(max(float(np.sum(np.abs(phases) ** 2 * np.abs(coeff) ** 2)), 0.0)))
                                    phase_error = abs(change_norm - phase_norm)
                                    change_transformed = eigenvectors.conj().T @ change @ eigenvectors
                                    coefficient_phase_error = float(np.linalg.norm(change_transformed - phases * coeff, ord="fro"))
                                    trace_change = abs(complex(np.trace(omega @ change)))
                                    kubo_fractional_norm = float(np.sqrt(max(float(2.0 * np.sum(kubo_weights * np.abs(deltas) ** (2.0 * theta) * np.abs(coeff) ** 2)), 0.0)))
                                    kubo_change_norm = float(np.sqrt(max(float(2.0 * np.sum(kubo_weights * np.abs(change_transformed) ** 2)), 0.0)))
                                    kubo_phase_norm = float(np.sqrt(max(float(2.0 * np.sum(kubo_weights * np.abs(phases * coeff) ** 2)), 0.0)))
                                    kubo_phase_error = abs(kubo_change_norm - kubo_phase_norm)
                                    kubo_bound = (2.0 ** (1.0 - theta)) * abs(delta / hbar) ** theta * kubo_fractional_norm
                                    kubo_bound_violation = kubo_change_norm - kubo_bound
                                    arithmetic_fractional_norm = float(np.sqrt(max(float(2.0 * np.sum(arithmetic_weights * np.abs(deltas) ** (2.0 * theta) * np.abs(coeff) ** 2)), 0.0)))
                                    max_kubo_phase_error = max(max_kubo_phase_error, kubo_phase_error, coefficient_phase_error)
                                    max_kubo_weighted_bound_violation = max(max_kubo_weighted_bound_violation, kubo_bound_violation)
                                    max_kubo_fractional_norm = max(max_kubo_fractional_norm, kubo_fractional_norm)
                                    max_kubo_fractional_bound = max(max_kubo_fractional_bound, kubo_bound)
                                    max_kubo_ratio = max(max_kubo_ratio, kubo_change_norm / kubo_bound if kubo_bound > tolerance else 0.0)
                                    max_arithmetic_to_kubo_ratio = max(max_arithmetic_to_kubo_ratio, arithmetic_fractional_norm / kubo_fractional_norm if kubo_fractional_norm > tolerance else 0.0)
                                    regime_max_kubo_norm = max(regime_max_kubo_norm, kubo_fractional_norm)
                                    regime_max_kubo_bound = max(regime_max_kubo_bound, kubo_bound)
                                    if kubo_fractional_norm > tolerance:
                                        min_kubo_nonzero_norm = min(min_kubo_nonzero_norm, kubo_fractional_norm)
                                    check(f"V={volume} d={size} beta={beta_fraction} site={site} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} Kubo phase", coefficient_phase_error <= tolerance * 800, coefficient_phase_error, f"<={tolerance * 800}", "Kubo--Mori phase")
                                    check(f"V={volume} d={size} beta={beta_fraction} site={site} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} Kubo bound", kubo_bound_violation <= tolerance * 800 * (1.0 + kubo_bound), [kubo_change_norm, kubo_bound], "weighted bound", "Kubo--Mori bound")
                                    check(f"V={volume} d={size} beta={beta_fraction} site={site} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} Kubo norm", kubo_phase_error <= tolerance * 800 * (1.0 + kubo_phase_norm), kubo_phase_error, f"<={tolerance * 800 * (1.0 + kubo_phase_norm)}", "Kubo--Mori norm")
                                    for current_theta in [theta]:
                                        envelope = (4.0 ** (1.0 - current_theta)) * np.abs(delta * deltas / hbar) ** (2.0 * current_theta)
                                        envelope_violation = float(np.max(np.abs(phases) ** 2 - envelope))
                                        fractional_norm = float(np.sqrt(max(float(np.sum(np.abs(deltas) ** (2.0 * current_theta) * np.abs(coeff) ** 2)), 0.0)))
                                        bound = (2.0 ** (1.0 - current_theta)) * abs(delta / hbar) ** current_theta * fractional_norm
                                        bound_violation = change_norm - bound
                                        trace_bound = omega_norm * bound
                                        trace_violation = trace_change - trace_bound
                                        max_envelope_violation = max(max_envelope_violation, envelope_violation)
                                        max_bound_violation = max(max_bound_violation, bound_violation)
                                        max_trace_violation = max(max_trace_violation, trace_violation)
                                        max_bound = max(max_bound, bound)
                                        max_change = max(max_change, change_norm)
                                        max_trace_change = max(max_trace_change, trace_change)
                                        max_ratio = max(max_ratio, change_norm / bound if bound > tolerance else 0.0)
                                        max_fractional_norm = max(max_fractional_norm, fractional_norm)
                                        regime_max_norm = max(regime_max_norm, fractional_norm)
                                        regime_max_bound = max(regime_max_bound, bound)
                                        if fractional_norm > tolerance:
                                            min_fractional_norm = min(min_fractional_norm, fractional_norm)
                                        check(f"V={volume} d={size} beta={beta_fraction} site={site} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} envelope", envelope_violation <= tolerance * 800, envelope_violation, f"<={tolerance * 800}", "fractional envelope")
                                        check(f"V={volume} d={size} beta={beta_fraction} site={site} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} bound", bound_violation <= tolerance * 800 * (1.0 + bound), [change_norm, bound], "fractional bound", "fractional bound")
                                        check(f"V={volume} d={size} beta={beta_fraction} site={site} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} trace", trace_violation <= tolerance * 800 * (1.0 + trace_bound), [trace_change, trace_bound], "state trace", "state trace")
                                        check(f"V={volume} d={size} beta={beta_fraction} site={site} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} phase", phase_error <= tolerance * 800, phase_error, f"<={tolerance * 800}", "spectral phase")
                                        context_count += 1
                                    max_phase_error = max(max_phase_error, phase_error)
                                    max_reduction_error = max(max_reduction_error, float(np.linalg.norm((bond_generator @ centered - centered @ bond_generator) - reduced_comm, ord="fro")))
        if first_terms is None:
            raise AssertionError("empty regime")
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(orders) * len(signs) * len(all_prefixes(terms, order, signs[0], delta, hbar)) * len(adjoints)
        per_regime.append({"volume": volume, "cutoffs": cutoffs, "sites": sites, "contexts": context_count - start_count, "expected_contexts": expected_regime, "maximum_fractional_norm": regime_max_norm, "maximum_fractional_bound": regime_max_bound, "maximum_kubo_fractional_norm": regime_max_kubo_norm, "maximum_kubo_fractional_bound": regime_max_kubo_bound})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("unitary factorization", max_unitary_error <= tolerance * 800, max_unitary_error, f"<={tolerance * 800}", "replica bond")
    check("density HS norm", max_density_excess <= tolerance * 800, max_density_excess, f"<={tolerance * 800}", "state trace")
    check("fractional envelope", max_envelope_violation <= tolerance * 800, max_envelope_violation, f"<={tolerance * 800}", "fractional envelope")
    check("fractional bound", max_bound_violation <= tolerance * 800 * (1.0 + max_bound), max_bound_violation, f"<={tolerance * 800 * (1.0 + max_bound)}", "fractional bound")
    check("state trace bound", max_trace_violation <= tolerance * 800 * (1.0 + max_bound), max_trace_violation, f"<={tolerance * 800 * (1.0 + max_bound)}", "state trace")
    check("spectral reduction", max_reduction_error <= tolerance * 800, max_reduction_error, f"<={tolerance * 800}", "spectral commutant")
    check("nonzero fractional shell", min_fractional_norm > tolerance, min_fractional_norm, f">{tolerance}", "growth stress")
    check("Kubo phase coefficient", max_kubo_phase_error <= tolerance * 800 * (1.0 + max_kubo_fractional_norm), max_kubo_phase_error, f"<={tolerance * 800 * (1.0 + max_kubo_fractional_norm)}", "Kubo--Mori phase")
    check("Kubo weighted bound", max_kubo_weighted_bound_violation <= tolerance * 800 * (1.0 + max_kubo_fractional_bound), max_kubo_weighted_bound_violation, f"<={tolerance * 800 * (1.0 + max_kubo_fractional_bound)}", "Kubo--Mori bound")
    check("Kubo norm nonzero", min_kubo_nonzero_norm > tolerance, min_kubo_nonzero_norm, f">{tolerance}", "Kubo--Mori topology")
    check("Kubo weight floor", min_kubo_weight >= -gap_tolerance, min_kubo_weight, f">={-gap_tolerance}", "Kubo--Mori state")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-FRACTIONAL-PREFIX",
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
            "theta": theta,
            "regimes": per_regime,
            "max_kubo_phase_error": max_kubo_phase_error,
            "max_kubo_weighted_bound_violation": max_kubo_weighted_bound_violation,
            "maximum_kubo_fractional_norm": max_kubo_fractional_norm,
            "maximum_kubo_fractional_bound": max_kubo_fractional_bound,
            "maximum_kubo_to_bound_ratio": max_kubo_ratio,
            "minimum_nonzero_kubo_fractional_norm": min_kubo_nonzero_norm,
            "maximum_kubo_weight_asymmetry": max_kubo_weight_asymmetry,
            "minimum_kubo_weight": min_kubo_weight,
            "maximum_arithmetic_to_kubo_fractional_ratio": max_arithmetic_to_kubo_ratio,
            "max_phase_identity_error": max_phase_error,
            "max_fractional_envelope_violation": max_envelope_violation,
            "max_fractional_bound_violation": max_bound_violation,
            "max_state_trace_bound_violation": max_trace_violation,
            "max_bond_unitary_factorization_error": max_unitary_error,
            "max_density_hs_norm_excess": max_density_excess,
            "max_spectral_reduction_error": max_reduction_error,
            "maximum_finite_time_change_norm": max_change,
            "maximum_fractional_bound": max_bound,
            "maximum_fractional_norm": max_fractional_norm,
            "maximum_state_trace_change": max_trace_change,
            "maximum_fractional_to_bound_ratio": max_ratio,
            "minimum_nonzero_fractional_norm": min_fractional_norm,
            "all_prefixes_finite_checked": True,
            "kubo_mori_weight_convention_checked": True,
            "weighted_fractional_bound_closed": True,
            "weighted_cutoff_uniformity_proved": False,
            "weighted_volume_uniformity_proved": False,
            "local_modular_dirichlet_comparison_proved": False,
            "common_core_closed": False,
            "common_alpha_closed": False,
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
    print(f"INDEPENDENT KUBO-MORI FRACTIONAL PREFIX PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} max_kubo={payload['derived']['maximum_kubo_fractional_norm']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
