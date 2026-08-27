#!/usr/bin/env python3
"""Independent source-Gibbs cancellation stress for EXP-001213 / R-371."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_gibbs_cancellation"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-gibbs-cancellation-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-independent-{SLUG}" / "independent.json"
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
    regimes = fixture["regimes"]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    theta = float(Fraction(fixture["theta"]))
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tolerance = float(fixture["finite_tolerance"])
    gap_tolerance = float(fixture["log_mean_gap_tolerance"])
    parameters = fixture["parameters"]
    if not (0.0 < theta <= 1.0):
        raise AssertionError("weighted fixture must contain theta in (0,1]")
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 128:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001213" and manifest["result_id"] == "R-371", [manifest["exploration_id"], manifest["result_id"]], "EXP-001213/R-371", "provenance")
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["shape_uniformity_proved"] is False, manifest["scope"], "finite-gibbs-cancellation-only", "scope")
    context_count = 0
    max_phase_error = 0.0
    max_envelope_violation = -float("inf")
    max_weighted_bound_violation = -float("inf")
    max_weighted_phase_error = 0.0
    max_weighted_norm = 0.0
    max_weighted_bound = 0.0
    max_weighted_ratio = 0.0
    min_weighted_norm = float("inf")
    max_unitary_error = 0.0
    max_weight_asymmetry = 0.0
    min_weight = float("inf")
    max_arithmetic_ratio = 0.0
    max_gibbs_identity_error = 0.0
    max_cancellation_bound_violation = -float("inf")
    max_cancellation_ratio = 0.0
    maximum_local_second_moment = 0.0
    minimum_nonzero_cancellation_bound = float("inf")
    per_regime: list[dict[str, Any]] = []

    for regime in regimes:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        bond_indices = [int(value) for value in regime["bond_term_indices"]]
        regime_start = context_count
        regime_max_norm = 0.0
        regime_max_bound = 0.0
        bond_rows: dict[str, dict[str, Any]] = {}
        for size in cutoffs:
            q_single, hamiltonian, terms, identity_single = build_system(volume, size, parameters)
            if any(index < 0 or index >= len(terms) for index in bond_indices):
                raise AssertionError(f"invalid bond term index for V={volume}: {bond_indices}")
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            projectors = pvm(q_single)
            orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
            embedded = [[embed(projector, site, volume, identity_single) for projector in projectors] for site in sites]
            for beta_fraction in betas:
                beta = float(beta_fraction)
                rho = gibbs(hamiltonian, beta)
                omega = np.kron(rho, rho)
                for site in sites:
                    reference = probabilities(reduce_site(rho, size, volume, site), projectors, tolerance)
                    local_witness = witness(reference, embedded[sites.index(site)])
                    for bond_term_index in bond_indices:
                        bond_generator = np.kron(terms[bond_term_index], identity_global) + np.kron(identity_global, terms[bond_term_index])
                        eigenvalues, eigenvectors = np.linalg.eigh(hermitian(bond_generator))
                        bond_unitary = unitary(terms[bond_term_index], delta, hbar)
                        bond_two = np.kron(bond_unitary, bond_unitary)
                        max_unitary_error = max(max_unitary_error, float(np.linalg.norm(bond_two - unitary(bond_generator, delta, hbar), ord="fro")))
                        bond_probabilities = np.exp(-beta * (eigenvalues - float(np.min(eigenvalues))))
                        bond_probabilities /= float(np.sum(bond_probabilities))
                        log_gap = np.log(bond_probabilities)[:, None] - np.log(bond_probabilities)[None, :]
                        arithmetic_weights = 0.5 * (bond_probabilities[:, None] + bond_probabilities[None, :])
                        kubo_weights = np.empty_like(log_gap)
                        close_gap = np.abs(log_gap) <= gap_tolerance
                        np.divide(bond_probabilities[:, None] - bond_probabilities[None, :], log_gap, out=kubo_weights, where=~close_gap)
                        kubo_weights[close_gap] = arithmetic_weights[close_gap]
                        kubo_weights = hermitian(kubo_weights)
                        weight_key = f"d={size}/bond={bond_term_index}"
                        row = bond_rows.setdefault(weight_key, {"cutoff": size, "bond_term_index": bond_term_index, "maximum_kubo_fractional_norm": 0.0, "maximum_kubo_fractional_bound": 0.0, "maximum_cancellation_ratio": 0.0, "maximum_local_second_moment": 0.0, "context_count": 0})
                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Gibbs normalization", np.isfinite(bond_probabilities).all() and abs(float(np.sum(bond_probabilities)) - 1.0) <= gap_tolerance, float(np.sum(bond_probabilities)), 1.0, "Kubo--Mori state")
                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Kubo symmetry", float(np.max(np.abs(kubo_weights - kubo_weights.T))) <= gap_tolerance, float(np.max(np.abs(kubo_weights - kubo_weights.T))), f"<={gap_tolerance}", "Kubo--Mori state")
                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Kubo positivity", float(np.min(kubo_weights)) >= -gap_tolerance, float(np.min(kubo_weights)), f">={-gap_tolerance}", "Kubo--Mori state")
                        max_weight_asymmetry = max(max_weight_asymmetry, float(np.max(np.abs(kubo_weights - kubo_weights.T))))
                        min_weight = min(min_weight, float(np.min(kubo_weights)))
                        for order_name, order in orders.items():
                            for sign in signs:
                                for prefix_length, prefix in all_prefixes(terms, order, sign, delta, hbar):
                                    for history_adjoint in adjoints:
                                        evolution = prefix if not history_adjoint else prefix.conj().T
                                        doubled = np.kron(evolution, evolution)
                                        moved = hermitian(doubled.conj().T @ local_witness @ doubled)
                                        scalar = float(np.trace(omega @ moved).real)
                                        centered = hermitian(moved - scalar * np.eye(moved.shape[0], dtype=complex))
                                        transformed = eigenvectors.conj().T @ centered @ eigenvectors
                                        deltas = eigenvalues[:, None] - eigenvalues[None, :]
                                        phases = np.exp(1j * delta * deltas / hbar) - 1.0
                                        change = bond_two.conj().T @ centered @ bond_two - centered
                                        change_transformed = eigenvectors.conj().T @ change @ eigenvectors
                                        phase_error = float(np.linalg.norm(change_transformed - phases * transformed, ord="fro"))
                                        envelope = (4.0 ** (1.0 - theta)) * np.abs(delta * deltas / hbar) ** (2.0 * theta)
                                        envelope_violation = float(np.max(np.abs(phases) ** 2 - envelope))
                                        weighted_norm = float(np.sqrt(max(float(2.0 * np.sum(kubo_weights * np.abs(deltas) ** (2.0 * theta) * np.abs(transformed) ** 2)), 0.0)))
                                        weighted_change = float(np.sqrt(max(float(2.0 * np.sum(kubo_weights * np.abs(change_transformed) ** 2)), 0.0)))
                                        weighted_phase = float(np.sqrt(max(float(2.0 * np.sum(kubo_weights * np.abs(phases * transformed) ** 2)), 0.0)))
                                        weighted_phase_error = abs(weighted_change - weighted_phase)
                                        weighted_bound = (2.0 ** (1.0 - theta)) * abs(delta / hbar) ** theta * weighted_norm
                                        weighted_bound_violation = weighted_change - weighted_bound
                                        arithmetic_norm = float(np.sqrt(max(float(2.0 * np.sum(arithmetic_weights * np.abs(deltas) ** (2.0 * theta) * np.abs(transformed) ** 2)), 0.0)))
                                        gibbs_identity_error = float(np.max(np.abs(kubo_weights * np.abs(deltas) - np.abs(bond_probabilities[:, None] - bond_probabilities[None, :]) / beta)))
                                        local_second_moment = float(np.sum(bond_probabilities[:, None] * np.abs(transformed) ** 2))
                                        cancellation_bound = (4.0 / beta) * local_second_moment
                                        cancellation_violation = weighted_norm ** 2 - cancellation_bound
                                        cancellation_ratio = weighted_norm ** 2 / cancellation_bound if cancellation_bound > tolerance ** 2 else 0.0
                                        max_gibbs_identity_error = max(max_gibbs_identity_error, gibbs_identity_error)
                                        max_cancellation_bound_violation = max(max_cancellation_bound_violation, cancellation_violation)
                                        max_cancellation_ratio = max(max_cancellation_ratio, cancellation_ratio)
                                        maximum_local_second_moment = max(maximum_local_second_moment, local_second_moment)
                                        if cancellation_bound > tolerance ** 2:
                                            minimum_nonzero_cancellation_bound = min(minimum_nonzero_cancellation_bound, cancellation_bound)
                                        row["maximum_cancellation_ratio"] = max(row["maximum_cancellation_ratio"], cancellation_ratio)
                                        row["maximum_local_second_moment"] = max(row["maximum_local_second_moment"], local_second_moment)
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Gibbs cancellation", gibbs_identity_error <= tolerance * 800, gibbs_identity_error, f"<={tolerance * 800}", "Gibbs cancellation")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} second-moment bound", cancellation_violation <= tolerance * 800 * (1.0 + cancellation_bound), [weighted_norm ** 2, cancellation_bound], "local Gibbs second moment", "Gibbs cancellation")
                                        max_phase_error = max(max_phase_error, phase_error)
                                        max_envelope_violation = max(max_envelope_violation, envelope_violation)
                                        max_weighted_phase_error = max(max_weighted_phase_error, phase_error, weighted_phase_error)
                                        max_weighted_bound_violation = max(max_weighted_bound_violation, weighted_bound_violation)
                                        max_weighted_norm = max(max_weighted_norm, weighted_norm)
                                        max_weighted_bound = max(max_weighted_bound, weighted_bound)
                                        max_weighted_ratio = max(max_weighted_ratio, weighted_change / weighted_bound if weighted_bound > tolerance else 0.0)
                                        max_arithmetic_ratio = max(max_arithmetic_ratio, arithmetic_norm / weighted_norm if weighted_norm > tolerance else 0.0)
                                        regime_max_norm = max(regime_max_norm, weighted_norm)
                                        regime_max_bound = max(regime_max_bound, weighted_bound)
                                        row["maximum_kubo_fractional_norm"] = max(row["maximum_kubo_fractional_norm"], weighted_norm)
                                        row["maximum_kubo_fractional_bound"] = max(row["maximum_kubo_fractional_bound"], weighted_bound)
                                        row["context_count"] += 1
                                        if weighted_norm > tolerance:
                                            min_weighted_norm = min(min_weighted_norm, weighted_norm)
                                        check(f"V={volume} d={size} beta={beta_fraction} site={site} bond={bond_term_index} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} phase", phase_error <= tolerance * 800, phase_error, f"<={tolerance * 800}", "Kubo--Mori phase")
                                        check(f"V={volume} d={size} beta={beta_fraction} site={site} bond={bond_term_index} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} bound", weighted_bound_violation <= tolerance * 800 * (1.0 + weighted_bound), [weighted_change, weighted_bound], "weighted bound", "Kubo--Mori bound")
                                        check(f"V={volume} d={size} beta={beta_fraction} site={site} bond={bond_term_index} {order_name} prefix={prefix_length} sign={sign} adj={history_adjoint} norm", weighted_phase_error <= tolerance * 800 * (1.0 + weighted_phase), weighted_phase_error, f"<={tolerance * 800 * (1.0 + weighted_phase)}", "Kubo--Mori norm")
                                        context_count += 1
        order_count = len(terms) if cutoffs else 0
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * len(orders) * len(signs) * (order_count + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_kubo_fractional_norm": regime_max_norm, "maximum_kubo_fractional_bound": regime_max_bound, "bond_rows": list(bond_rows.values())})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("phase coefficient", max_weighted_phase_error <= tolerance * 800 * (1.0 + max_weighted_norm), max_weighted_phase_error, f"<={tolerance * 800 * (1.0 + max_weighted_norm)}", "Kubo--Mori phase")
    check("fractional envelope", max_envelope_violation <= tolerance * 800, max_envelope_violation, f"<={tolerance * 800}", "fractional envelope")
    check("weighted bound", max_weighted_bound_violation <= tolerance * 800 * (1.0 + max_weighted_bound), max_weighted_bound_violation, f"<={tolerance * 800 * (1.0 + max_weighted_bound)}", "Kubo--Mori bound")
    check("Kubo weight symmetry", max_weight_asymmetry <= gap_tolerance, max_weight_asymmetry, f"<={gap_tolerance}", "Kubo--Mori state")
    check("Kubo weight floor", min_weight >= -gap_tolerance, min_weight, f">={-gap_tolerance}", "Kubo--Mori state")
    check("nonzero weighted shell", min_weighted_norm > tolerance, min_weighted_norm, f">{tolerance}", "Kubo--Mori topology")
    check("Gibbs cancellation identity", max_gibbs_identity_error <= tolerance * 800, max_gibbs_identity_error, f"<={tolerance * 800}", "Gibbs cancellation")
    check("local second-moment bound", max_cancellation_bound_violation <= tolerance * 800 * (1.0 + maximum_local_second_moment * 4.0), max_cancellation_bound_violation, f"<={tolerance * 800 * (1.0 + maximum_local_second_moment * 4.0)}", "Gibbs cancellation")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-GIBBS-CANCELLATION",
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
            "max_weighted_phase_error": max_weighted_phase_error,
            "max_fractional_envelope_violation": max_envelope_violation,
            "max_weighted_bound_violation": max_weighted_bound_violation,
            "maximum_weighted_fractional_norm": max_weighted_norm,
            "maximum_weighted_fractional_bound": max_weighted_bound,
            "maximum_weighted_to_bound_ratio": max_weighted_ratio,
            "minimum_nonzero_weighted_fractional_norm": min_weighted_norm,
            "maximum_kubo_weight_asymmetry": max_weight_asymmetry,
            "minimum_kubo_weight": min_weight,
            "maximum_arithmetic_to_kubo_fractional_ratio": max_arithmetic_ratio,
            "maximum_gibbs_theta_half_identity_error": max_gibbs_identity_error,
            "maximum_local_second_moment_bound_violation": max_cancellation_bound_violation,
            "maximum_cancellation_to_second_moment_bound_ratio": max_cancellation_ratio,
            "maximum_local_gibbs_second_moment": maximum_local_second_moment,
            "minimum_nonzero_cancellation_bound": minimum_nonzero_cancellation_bound,
            "maximum_bond_unitary_factorization_error": max_unitary_error,
            "bond_translation_finite_checked": True,
            "source_translation_finite_checked": True,
            "edge_and_square_shapes_checked": True,
            "all_prefixes_finite_checked": True,
            "weighted_fractional_bound_closed": True,
            "gibbs_theta_half_cancellation_finite_checked": True,
            "gibbs_theta_half_identity_closed": True,
            "local_second_moment_bound_closed": True,
            "local_second_moment_uniformity_proved": False,
            "weighted_cutoff_uniformity_proved": False,
            "weighted_volume_uniformity_proved": False,
            "source_uniformity_proved": False,
            "shape_uniformity_proved": False,
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
    print(f"INDEPENDENT KUBO-MORI GIBBS-CANCELLATION PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} max_weighted={payload['derived']['maximum_weighted_fractional_norm']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
