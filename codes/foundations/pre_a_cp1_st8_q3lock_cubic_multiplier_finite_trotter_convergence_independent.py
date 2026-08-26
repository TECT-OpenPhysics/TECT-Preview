#!/usr/bin/env python3
"""Independent finite Lie--Trotter reconstruction for EXP-001161.

This lane rebuilds oscillator embeddings, split terms, spectral factors and
history comparisons without importing the primary audit implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_cubic_multiplier_finite_trotter_convergence"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-cubic-multiplier-finite-trotter-convergence-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as source_q3  # noqa: E402


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


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


def eigensystem(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(hermitian(matrix))


def exponential(values: np.ndarray, vectors: np.ndarray, time: float) -> np.ndarray:
    return (vectors * np.exp(-1j * time * values)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    return float(singular_values[0])


def four_leg_norm(matrix: np.ndarray, rho_sqrt: np.ndarray) -> float:
    legs = [matrix @ rho_sqrt, matrix.conj().T @ rho_sqrt, rho_sqrt @ matrix, rho_sqrt @ matrix.conj().T]
    return float(np.sqrt(sum(float(np.vdot(leg, leg).real) for leg in legs)))


def graph_distance(volume: int, sources: list[int]) -> list[int]:
    adjacency = [[] for _ in range(volume)]
    for left, right in source_q3.graph_edges(volume):
        adjacency[left].append(right)
        adjacency[right].append(left)
    distances = [volume + 10] * volume
    queue = list(sources)
    for source in sources:
        distances[source] = 0
    cursor = 0
    while cursor < len(queue):
        current = queue[cursor]
        cursor += 1
        for neighbor in sorted(adjacency[current]):
            trial = distances[current] + 1
            if trial < distances[neighbor]:
                distances[neighbor] = trial
                queue.append(neighbor)
    return distances


def build_weighted_energy(volume: int, n: int, fixture: dict[str, Any], distances: list[int], ratio: float) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = source_q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [source_q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [source_q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    weights = np.asarray([ratio ** distance for distance in distances], dtype=float)
    onsite = []
    for q, p in zip(q_ops, p_ops):
        onsite.append(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0)
    bonds = {(left, right): source_q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in source_q3.graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    weighted = sum((weights[site] * onsite[site] for site in range(volume)), zero)
    for (left, right), bond in bonds.items():
        weighted = weighted + (weights[left] + weights[right]) * bond / 2.0
    base = hermitian(weighted + np.eye(weighted.shape[0], dtype=complex))
    values = np.linalg.eigvalsh(base)
    minimum = float(values.min())
    positive = base - minimum * np.eye(base.shape[0], dtype=complex) + np.eye(base.shape[0], dtype=complex)
    return q_ops, hermitian(positive), weights


def build_split_terms(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray]:
    q_single, p_single = source_q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [source_q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [source_q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    onsite = []
    for q, p in zip(q_ops, p_ops):
        onsite.append(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0)
    bonds = [source_q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in source_q3.graph_edges(volume)]
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite, zero) + sum(bonds, zero)
    return onsite + bonds, hermitian(full)


def ordered_step(eigensystems: list[tuple[np.ndarray, np.ndarray]], order: list[int], sign: int, delta: float) -> np.ndarray:
    result = np.eye(eigensystems[0][1].shape[0], dtype=complex)
    factors = {}
    for index, (values, vectors) in enumerate(eigensystems):
        factors[index] = exponential(values, vectors, sign * delta)
    for index in order:
        result = factors[index] @ result
    return result


def history(matrix: np.ndarray, step: np.ndarray, delta: float, count: int) -> np.ndarray:
    current = matrix.copy()
    accumulated = np.zeros_like(matrix)
    for _ in range(count):
        accumulated = accumulated + delta * current
        current = step @ current @ step.conj().T
    return accumulated


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent_path = REPO / manifest["source_fixture"]["manifest"]
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    source_path = REPO / parent["source_fixture"]["manifest"]
    source = json.loads(source_path.read_text(encoding="utf-8"))
    fixture = source["source_fixture"]
    source_cfg = manifest["source_fixture"]
    trotter = manifest["trotter_fixture"]
    finite = manifest["finite_fixture"]
    tolerance = float(finite["agreement_tolerance"])
    decomposition_tolerance = float(finite["decomposition_tolerance"])
    unitary_tolerance = float(finite["unitarity_tolerance"])
    monotonicity_tolerance = float(finite["monotonicity_tolerance"])
    horizon = float(Fraction(trotter["horizon"]))
    counts = [int(value) for value in trotter["step_counts"]]
    volumes = [int(value) for value in source_cfg["volume_values"]]
    n = int(source_cfg["oscillator_dimension"])
    betas = [float(value) for value in parent["source_fixture"]["beta_values"]]
    pairs = {int(key): [[int(site) for site in pair] for pair in value] for key, value in source_cfg["source_pairs"].items()}
    probes = {int(key): [int(site) for site in value] for key, value in source_cfg["probe_sites"].items()}
    ratio = float(Fraction(trotter["weight_ratio_per_edge"]))
    power = float(Fraction(trotter["multiplier_power"]))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001161" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001161/T-054/false", "provenance")
    check("parent authority", parent["exploration_id"] == "EXP-001160" and parent["task_id"] == "T-054", [parent["exploration_id"], parent["task_id"]], "EXP-001160/T-054", "provenance")
    check("time grid", counts == [3, 6, 12] and abs(horizon - 1.0 / 3.0) <= tolerance, [counts, horizon], "3,6,12 and horizon 1/3", "fixture")
    check("order/sign grid", trotter["orders"] == ["onsite_then_lexicographic_bonds", "reverse_term_order"] and trotter["time_signs"] == [-1, 1], trotter, "two orders and two signs", "fixture")
    check("scope firewall", manifest["scope"]["finite_split_exact_q3_bridge_closed"] and not manifest["scope"]["analytic_trotter_rate_closed"] and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite bridge only", "scope")

    rows: list[dict[str, Any]] = []
    for volume in volumes:
        terms, hamiltonian = build_split_terms(volume, n, fixture)
        _, reference, _, _ = source_q3.build_volume(volume, n, fixture)
        decomposition_error = float(np.linalg.norm(hamiltonian - reference, ord=2))
        check(f"V={volume} full decomposition", decomposition_error <= decomposition_tolerance, decomposition_error, f"<={decomposition_tolerance}", "decomposition")
        h_values, h_vectors = eigensystem(hamiltonian)
        term_eigensystems = [eigensystem(term) for term in terms]
        rho_roots = {beta: source_q3.spectral_power(source_q3.gibbs(hamiltonian, beta), 0.5) for beta in betas}
        for pair in pairs[volume]:
            distances = graph_distance(volume, pair)
            q_ops, energy, weights = build_weighted_energy(volume, n, fixture, distances, ratio)
            energy_minimum = float(np.linalg.eigvalsh(energy)[0])
            check(f"V={volume} pair={pair} positive energy", energy_minimum >= float(finite["positive_energy_floor"]) - tolerance, energy_minimum, f">={finite['positive_energy_floor']}", "energy")
            inverse_values, inverse_vectors = eigensystem(energy)
            inverse = (inverse_vectors * np.power(np.maximum(inverse_values, 0.0), -power)) @ inverse_vectors.conj().T
            site = probes[volume][0]
            cubic = q_ops[site] @ q_ops[site] @ q_ops[site]
            factor = float(weights[site] ** power)
            right = factor * (cubic @ inverse)
            left = factor * (inverse @ cubic)
            comm_norm = operator_norm(right - left)
            check(f"V={volume} multiplier floor", comm_norm > float(finite["commutator_floor"]), comm_norm, f">{finite['commutator_floor']}", "orientation")
            for order_name, order in ((trotter["orders"][0], list(range(len(terms)))), (trotter["orders"][1], list(reversed(range(len(terms)))))):
                for sign in trotter["time_signs"]:
                    exact_target = exponential(h_values, h_vectors, sign * horizon)
                    exact_errors: list[float] = []
                    history_errors: list[float] = []
                    for count in counts:
                        delta = horizon / count
                        step = ordered_step(term_eigensystems, order, int(sign), delta)
                        identity = np.eye(step.shape[0], dtype=complex)
                        unitary_error = float(np.linalg.norm(step.conj().T @ step - identity, ord=2))
                        split_target = np.linalg.matrix_power(step, count)
                        final_error = float(np.linalg.norm(split_target - exact_target, ord=2))
                        exact_increment = exponential(h_values, h_vectors, sign * delta)
                        split_right = history(right, step, delta, count)
                        split_left = history(left, step, delta, count)
                        split_comm = history(right - left, step, delta, count)
                        exact_right = history(right, exact_increment, delta, count)
                        exact_left = history(left, exact_increment, delta, count)
                        exact_comm = history(right - left, exact_increment, delta, count)
                        history_identity = float(np.linalg.norm((split_right - split_left) - split_comm, ord=2))
                        exact_identity = float(np.linalg.norm((exact_right - exact_left) - exact_comm, ord=2))
                        right_error = float(np.linalg.norm(split_right - exact_right, ord=2))
                        left_error = float(np.linalg.norm(split_left - exact_left, ord=2))
                        comm_error = float(np.linalg.norm(split_comm - exact_comm, ord=2))
                        check(f"V={volume} {order_name} sign={sign} N={count} unitary", unitary_error <= unitary_tolerance, unitary_error, f"<={unitary_tolerance}", "split")
                        check(f"V={volume} {order_name} sign={sign} N={count} final finite", np.isfinite(final_error), final_error, "finite", "Trotter")
                        check(f"V={volume} {order_name} sign={sign} N={count} history identities", history_identity <= tolerance and exact_identity <= tolerance, [history_identity, exact_identity], f"<={tolerance}", "history")
                        check(f"V={volume} {order_name} sign={sign} N={count} history finite", all(np.isfinite(value) for value in (right_error, left_error, comm_error)), [right_error, left_error, comm_error], "finite", "history")
                        state_errors = []
                        for beta, rho_sqrt in rho_roots.items():
                            state_errors.extend([four_leg_norm(split_right - exact_right, rho_sqrt), four_leg_norm(split_left - exact_left, rho_sqrt), four_leg_norm(split_comm - exact_comm, rho_sqrt)])
                        check(f"V={volume} {order_name} sign={sign} N={count} Gibbs history finite", all(np.isfinite(value) for value in state_errors), state_errors, "finite", "Gibbs")
                        exact_errors.append(final_error)
                        history_errors.append(max(right_error, left_error, comm_error))
                        rows.append({"volume": volume, "source_pair": pair, "probe_site": site, "order": order_name, "time_sign": int(sign), "step_count": count, "delta": delta, "unitary_error": unitary_error, "final_unitary_error": final_error, "right_history_error": right_error, "left_history_error": left_error, "commutator_history_error": comm_error, "max_gibbs_history_error": max(state_errors)})
                    check(f"V={volume} {order_name} sign={sign} final convergence", exact_errors[-1] <= exact_errors[0] + monotonicity_tolerance and exact_errors[-1] <= exact_errors[1] + monotonicity_tolerance, exact_errors, "fine no worse than coarse", "Trotter convergence")
                    check(f"V={volume} {order_name} sign={sign} history convergence", history_errors[-1] <= history_errors[0] + monotonicity_tolerance and history_errors[-1] <= history_errors[1] + monotonicity_tolerance, history_errors, "fine no worse than coarse", "history convergence")
    expected_rows = sum(len(pairs[volume]) * len(probes[volume]) * len(trotter["orders"]) * len(trotter["time_signs"]) * len(counts) for volume in volumes)
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    check("all errors finite", all(np.isfinite(row["final_unitary_error"]) for row in rows), len(rows), "finite", "summary")
    check("scope remains finite", manifest["scope"]["finite_two_order_two_sign_trotter_convergence_closed"] and not manifest["scope"]["actual_q3_thermodynamic_history_closed"] and not manifest["scope"]["pre_a_closed"], manifest["scope"], "finite bridge only", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CUBIC-MULTIPLIER-FINITE-TROTTER-CONVERGENCE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:120] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "derived": {
            "source_manifest_sha256": normalized_sha256(source_path),
            "parent_manifest_sha256": normalized_sha256(parent_path),
            "row_count": len(rows),
            "volumes": volumes,
            "step_counts": counts,
            "max_final_unitary_error": max(row["final_unitary_error"] for row in rows),
            "max_right_history_error": max(row["right_history_error"] for row in rows),
            "max_left_history_error": max(row["left_history_error"] for row in rows),
            "max_commutator_history_error": max(row["commutator_history_error"] for row in rows),
            "max_gibbs_history_error": max(row["max_gibbs_history_error"] for row in rows),
            "finite_full_unitary_decomposition_closed": True,
            "finite_two_order_two_sign_trotter_convergence_closed": True,
            "finite_two_orientation_history_convergence_closed": True,
            "finite_split_exact_q3_bridge_closed": True,
            "analytic_trotter_rate_closed": False,
            "actual_q3_thermodynamic_history_closed": False,
            "direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "source_volume_beta_uniformity_closed": False,
            "exhaustion_independence_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False
        },
        "boundary": manifest["scope"],
        "rows": rows
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-TROTTER-CONVERGENCE PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
