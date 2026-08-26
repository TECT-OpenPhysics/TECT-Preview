#!/usr/bin/env python3
"""Primary finite split-history Volterra audit for EXP-001160.

The two noncommuting cubic multiplier orientations from EXP-001159 are
propagated by exact finite onsite-plus-bond split unitaries.  The result is a
finite discrete Volterra sum and its operator/Gibbs norm bookkeeping, not an
infinite-volume dynamics theorem.
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
SLUG = "pre_a_cp1_st8_q3lock_cubic_multiplier_split_history_volterra"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-cubic-multiplier-split-history-volterra-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def weighted_energy(volume: int, n: int, fixture: dict[str, Any], distances: list[int], ratio: float) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    weights = np.asarray([ratio ** distance for distance in distances], dtype=float)
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in q3.graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    weighted = sum((weights[site] * onsite[site] for site in range(volume)), zero)
    weighted += sum((((weights[left] + weights[right]) / 2.0) * bond for (left, right), bond in bonds.items()), zero)
    base = weighted + np.eye(weighted.shape[0], dtype=complex)
    base = (base + base.conj().T) / 2.0
    return q_ops, q3.positive_weight(base), weights


def split_terms(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = [q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in q3.graph_edges(volume)]
    zero = np.zeros_like(q_ops[0])
    return onsite + bonds, (sum(onsite, zero) + sum(bonds, zero) + (sum(onsite, zero) + sum(bonds, zero)).conj().T) / 2.0


def unitary_from_hermitian(matrix: np.ndarray, time: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def four_leg_norm(matrix: np.ndarray, rho_sqrt: np.ndarray) -> float:
    legs = (matrix @ rho_sqrt, matrix.conj().T @ rho_sqrt, rho_sqrt @ matrix, rho_sqrt @ matrix.conj().T)
    return float(np.sqrt(sum(np.linalg.norm(leg, ord="fro") ** 2 for leg in legs)))


def graph_distance(volume: int, sources: list[int]) -> list[int]:
    adjacency = {site: set() for site in range(volume)}
    for left, right in q3.graph_edges(volume):
        adjacency[left].add(right)
        adjacency[right].add(left)
    distances = [volume + 10] * volume
    frontier = list(sources)
    for site in sources:
        distances[site] = 0
    cursor = 0
    while cursor < len(frontier):
        current = frontier[cursor]
        cursor += 1
        for neighbor in sorted(adjacency[current]):
            trial = distances[current] + 1
            if trial < distances[neighbor]:
                distances[neighbor] = trial
                frontier.append(neighbor)
    return distances


def split_step(terms: list[np.ndarray], order: list[int], sign: int, delta: float) -> np.ndarray:
    result = np.eye(terms[0].shape[0], dtype=complex)
    for index in order:
        result = unitary_from_hermitian(terms[index], sign * delta) @ result
    return result


def volterra_sums(right: np.ndarray, left: np.ndarray, step: np.ndarray, delta: float, step_counts: list[int]) -> dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    wanted = set(step_counts)
    result: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    current_right, current_left, current_comm = right.copy(), left.copy(), (right - left).copy()
    accumulated_right = np.zeros_like(right)
    accumulated_left = np.zeros_like(left)
    accumulated_comm = np.zeros_like(right)
    for count in range(1, max(step_counts) + 1):
        accumulated_right = accumulated_right + delta * current_right
        accumulated_left = accumulated_left + delta * current_left
        accumulated_comm = accumulated_comm + delta * current_comm
        if count in wanted:
            result[count] = (accumulated_right.copy(), accumulated_left.copy(), accumulated_comm.copy())
        current_right = step @ current_right @ step.conj().T
        current_left = step @ current_left @ step.conj().T
        current_comm = step @ current_comm @ step.conj().T
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_path = REPO / manifest["source_fixture"]["manifest"]
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source_cfg = manifest["source_fixture"]
    fixture = source["source_fixture"]
    history = manifest["split_history"]
    finite = manifest["finite_fixture"]
    checks: list[dict[str, Any]] = []
    tolerance = float(finite["agreement_tolerance"])
    triangle_tolerance = float(finite["triangle_tolerance"])
    unitary_tolerance = float(finite["unitarity_tolerance"])
    delta = float(Fraction(history["time_step"]))
    step_counts = [int(value) for value in history["step_counts"]]
    ratio = float(Fraction(history["weight_ratio_per_edge"]))
    power = float(Fraction(history["multiplier_power"]))
    volumes = [int(value) for value in source_cfg["volume_values"]]
    betas = [float(value) for value in source_cfg["beta_values"]]
    pairs = {int(key): [[int(site) for site in pair] for pair in value] for key, value in source_cfg["source_pairs"].items()}
    probes = {int(key): [int(site) for site in value] for key, value in source_cfg["probe_sites"].items()}

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001160" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001160/T-054/false", "provenance")
    check("source authority", source["exploration_id"] == "EXP-001158" and source["task_id"] == "T-054", [source["exploration_id"], source["task_id"]], "EXP-001158/T-054", "upstream")
    check("time fixture", step_counts == [1, 3, 6] and abs(max(step_counts) * delta - 1.0 / 3.0) <= tolerance, [step_counts, delta], "6*(1/18)=1/3", "fixture")
    check("orientation fixture", history["right_orientation"] != history["left_orientation"] and len(history["orders"]) == 2 and history["time_signs"] == [-1, 1], history, "two orders and two signs", "orientation")
    check("scope firewall", manifest["scope"]["finite_split_history_both_orientations_closed"] and manifest["scope"]["finite_orientation_difference_closed"] and not manifest["scope"]["analytic_volterra_bound_closed"] and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite carrier only", "scope")

    rows: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    for volume in volumes:
        terms, hamiltonian = split_terms(volume, int(source_cfg["oscillator_dimension"]), fixture)
        _, reference, _, _ = q3.build_volume(volume, int(source_cfg["oscillator_dimension"]), fixture)
        decomposition_error = float(np.linalg.norm(hamiltonian - reference, ord=2))
        check(f"V={volume} split decomposition", decomposition_error <= tolerance, decomposition_error, f"<={tolerance}", "split")
        rho_roots = {beta: q3.spectral_power(q3.gibbs(hamiltonian, beta), 0.5) for beta in betas}
        for pair in pairs[volume]:
            distances = graph_distance(volume, pair)
            q_ops, energy, weights = weighted_energy(volume, int(source_cfg["oscillator_dimension"]), fixture, distances, ratio)
            minimum = float(np.min(np.linalg.eigvalsh(energy)))
            check(f"V={volume} pair={pair} energy floor", minimum >= float(finite["positive_energy_floor"]) - tolerance, minimum, f">={finite['positive_energy_floor']}", "energy")
            inverse = q3.spectral_power(energy, -power)
            for order_name, order in ((history["orders"][0], list(range(len(terms)))), (history["orders"][1], list(reversed(range(len(terms)))))):
                for sign in history["time_signs"]:
                    step = split_step(terms, order, int(sign), delta)
                    identity = np.eye(step.shape[0], dtype=complex)
                    unitary_error = float(np.linalg.norm(step.conj().T @ step - identity, ord=2))
                    check(f"V={volume} pair={pair} order={order_name} sign={sign} unitary", unitary_error <= unitary_tolerance, unitary_error, f"<={unitary_tolerance}", "split")
                    for site in probes[volume]:
                        cubic = q_ops[site] @ q_ops[site] @ q_ops[site]
                        factor = float(weights[site] ** power)
                        right = factor * (cubic @ inverse)
                        left = factor * (inverse @ cubic)
                        comm = right - left
                        right_norm, left_norm, comm_norm = operator_norm(right), operator_norm(left), operator_norm(comm)
                        check(f"V={volume} pair={pair} site={site} commutator floor", np.isfinite(comm_norm) and comm_norm > float(finite["commutator_floor"]), comm_norm, f">{finite['commutator_floor']}", "orientation")
                        histories = volterra_sums(right, left, step, delta, step_counts)
                        for count in step_counts:
                            history_right, history_left, history_comm = histories[count]
                            direct_error = float(np.linalg.norm((history_right - history_left) - history_comm, ord=2))
                            op_right, op_left, op_comm = operator_norm(history_right), operator_norm(history_left), operator_norm(history_comm)
                            total_time = count * delta
                            check(f"V={volume} pair={pair} site={site} N={count} history identity", direct_error <= tolerance, direct_error, f"<={tolerance}", "Volterra")
                            check(f"V={volume} pair={pair} site={site} N={count} operator finite", all(np.isfinite(value) for value in (op_right, op_left, op_comm)), [op_right, op_left, op_comm], "finite", "Volterra")
                            check(f"V={volume} pair={pair} site={site} N={count} operator triangle", op_comm <= op_right + op_left + triangle_tolerance, op_comm, f"<={op_right + op_left + triangle_tolerance}", "norm")
                            check(f"V={volume} pair={pair} site={site} N={count} telescoping right", op_right <= total_time * right_norm + triangle_tolerance, op_right, f"<={total_time * right_norm + triangle_tolerance}", "Volterra bound")
                            check(f"V={volume} pair={pair} site={site} N={count} telescoping left", op_left <= total_time * left_norm + triangle_tolerance, op_left, f"<={total_time * left_norm + triangle_tolerance}", "Volterra bound")
                            state_rows: dict[str, dict[str, float]] = {}
                            for beta in betas:
                                rho_sqrt = rho_roots[beta]
                                state_right = four_leg_norm(history_right, rho_sqrt)
                                state_left = four_leg_norm(history_left, rho_sqrt)
                                state_comm = four_leg_norm(history_comm, rho_sqrt)
                                check(f"V={volume} pair={pair} site={site} N={count} beta={beta} state finite", all(np.isfinite(value) and value >= -tolerance for value in (state_right, state_left, state_comm)), [state_right, state_left, state_comm], "finite nonnegative", "Gibbs")
                                check(f"V={volume} pair={pair} site={site} N={count} beta={beta} state triangle", state_comm <= state_right + state_left + triangle_tolerance, state_comm, f"<={state_right + state_left + triangle_tolerance}", "Gibbs norm")
                                check(f"V={volume} pair={pair} site={site} N={count} beta={beta} state operator envelope", state_right <= 2.0 * op_right + triangle_tolerance and state_left <= 2.0 * op_left + triangle_tolerance and state_comm <= 2.0 * op_comm + triangle_tolerance, [state_right, state_left, state_comm], "<=2 operator norm", "Gibbs envelope")
                                state_rows[str(beta)] = {"right": state_right, "left": state_left, "commutator": state_comm}
                            rows.append({"volume": volume, "source_pair": pair, "probe_site": site, "order": order_name, "time_sign": int(sign), "step_count": count, "time": total_time, "weighted_factor": factor, "right_operator_norm": op_right, "left_operator_norm": op_left, "commutator_operator_norm": op_comm, "state_weighted": state_rows})
    check("history row coverage", len(rows) == sum(len(probes[volume]) * len(history["orders"]) * len(history["time_signs"]) * len(step_counts) for volume in volumes), len(rows), "declared history grid", "coverage")
    check("global extrema finite", all(np.isfinite(row["commutator_operator_norm"]) for row in rows), len(rows), "all finite", "summary")
    check("scope remains finite", manifest["scope"]["finite_volterra_telescoping_bound_closed"] and not manifest["scope"]["source_volume_beta_uniformity_closed"] and not manifest["scope"]["pre_a_closed"], manifest["scope"], "finite Volterra only", "scope")
    max_right = max(row["right_operator_norm"] for row in rows)
    max_left = max(row["left_operator_norm"] for row in rows)
    max_comm = max(row["commutator_operator_norm"] for row in rows)
    max_state = max(value for row in rows for state in row["state_weighted"].values() for value in state.values())
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CUBIC-MULTIPLIER-SPLIT-HISTORY-VOLTERRA",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:120] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "derived": {
            "source_manifest_sha256": normalized_sha256(source_path),
            "history_row_count": len(rows),
            "max_right_operator_norm": max_right,
            "max_left_operator_norm": max_left,
            "max_commutator_operator_norm": max_comm,
            "max_state_weighted_norm": max_state,
            "finite_split_history_both_orientations_closed": True,
            "finite_volterra_telescoping_bound_closed": True,
            "finite_orientation_difference_closed": True,
            "analytic_volterra_bound_closed": False,
            "operator_domain_embedding_closed": False,
            "actual_q3_history_closed": False,
            "direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "source_volume_beta_uniformity_closed": False,
            "exhaustion_independence_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False
        },
        "boundary": manifest["scope"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY CUBIC-MULTIPLIER-SPLIT-HISTORY-VOLTERRA PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['history_row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
