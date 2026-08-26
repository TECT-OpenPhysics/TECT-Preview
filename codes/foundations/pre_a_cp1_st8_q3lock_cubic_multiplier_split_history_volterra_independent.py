#!/usr/bin/env python3
"""Independent finite reconstruction of EXP-001160.

This lane diagonalizes each split term once, builds the ordered unitary from
those factors, and recomputes both cubic-multiplier Volterra orientations
without importing the primary implementation.
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


def graph_distance(volume: int, sources: list[int]) -> list[int]:
    adjacency = [[] for _ in range(volume)]
    for left, right in source_q3.graph_edges(volume):
        adjacency[left].append(right)
        adjacency[right].append(left)
    distances = [volume + 10] * volume
    queue = list(sources)
    for site in sources:
        distances[site] = 0
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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0




def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    """Evaluate a real power of a positive-semidefinite Hermitian matrix."""
    values, vectors = np.linalg.eigh(hermitian(matrix))
    if float(values.min()) < -1.0e-9:
        raise AssertionError(f"spectral input is not positive: min={values.min()}")
    return (vectors * np.power(np.maximum(values, 0.0), exponent)) @ vectors.conj().T

def build_energy(volume: int, n: int, fixture: dict[str, Any], distances: list[int], ratio: float) -> tuple[list[np.ndarray], np.ndarray, list[float]]:
    q_one, p_one = source_q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [source_q3.embed(q_one, site, volume, identity) for site in range(volume)]
    p_ops = [source_q3.embed(p_one, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    factors = [ratio ** distance for distance in distances]
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): source_q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in source_q3.graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    weighted = sum((factors[site] * onsite[site] for site in range(volume)), zero)
    for (left, right), bond in bonds.items():
        weighted = weighted + (factors[left] + factors[right]) * bond / 2.0
    identity_full = np.eye(weighted.shape[0], dtype=complex)
    base = hermitian(weighted + identity_full)
    minimum = float(np.linalg.eigvalsh(base)[0])
    return q_ops, base + (1.0 - minimum) * identity_full, factors


def split_terms(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray]:
    q_one, p_one = source_q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [source_q3.embed(q_one, site, volume, identity) for site in range(volume)]
    p_ops = [source_q3.embed(p_one, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = [source_q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in source_q3.graph_edges(volume)]
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite, zero) + sum(bonds, zero)
    return onsite + bonds, hermitian(full)


def term_unitary(term: np.ndarray, sign: int, delta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(term))
    return (vectors * np.exp(-1j * sign * delta * values)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def four_leg(matrix: np.ndarray, rho_sqrt: np.ndarray) -> float:
    terms = (matrix @ rho_sqrt, matrix.conj().T @ rho_sqrt, rho_sqrt @ matrix, rho_sqrt @ matrix.conj().T)
    return float(np.sqrt(sum(float(np.vdot(term, term).real) for term in terms)))


def history_sums(right: np.ndarray, left: np.ndarray, unitary: np.ndarray, delta: float, counts: list[int]) -> dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    result: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    current_right, current_left, current_comm = right.copy(), left.copy(), right - left
    accumulated_right = np.zeros_like(right)
    accumulated_left = np.zeros_like(left)
    accumulated_comm = np.zeros_like(right)
    for count in range(1, max(counts) + 1):
        accumulated_right = accumulated_right + delta * current_right
        accumulated_left = accumulated_left + delta * current_left
        accumulated_comm = accumulated_comm + delta * current_comm
        if count in counts:
            result[count] = (accumulated_right.copy(), accumulated_left.copy(), accumulated_comm.copy())
        current_right = unitary @ current_right @ unitary.conj().T
        current_left = unitary @ current_left @ unitary.conj().T
        current_comm = unitary @ current_comm @ unitary.conj().T
    return result


def gibbs_root(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    probabilities = np.exp(-beta * (values - values.min()))
    probabilities /= probabilities.sum()
    return (vectors * np.sqrt(probabilities)) @ vectors.conj().T


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_path = REPO / manifest["source_fixture"]["manifest"]
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source_cfg = manifest["source_fixture"]
    fixture = source["source_fixture"]
    history = manifest["split_history"]
    finite = manifest["finite_fixture"]
    tolerance = float(finite["agreement_tolerance"])
    triangle_tolerance = float(finite["triangle_tolerance"])
    unitary_tolerance = float(finite["unitarity_tolerance"])
    delta = float(Fraction(history["time_step"]))
    counts = [int(value) for value in history["step_counts"]]
    ratio = float(Fraction(history["weight_ratio_per_edge"]))
    power = float(Fraction(history["multiplier_power"]))
    volumes = [int(value) for value in source_cfg["volume_values"]]
    betas = [float(value) for value in source_cfg["beta_values"]]
    pairs = {int(key): [[int(site) for site in pair] for pair in value] for key, value in source_cfg["source_pairs"].items()}
    probes = {int(key): [int(site) for site in value] for key, value in source_cfg["probe_sites"].items()}
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001160" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001160/T-054/false", "provenance")
    check("source authority", source["exploration_id"] == "EXP-001158" and source["task_id"] == "T-054", [source["exploration_id"], source["task_id"]], "EXP-001158/T-054", "upstream")
    check("history grid", counts == [1, 3, 6] and len(history["orders"]) == 2 and history["time_signs"] == [-1, 1], history, "declared finite grid", "fixture")
    check("scope firewall", manifest["scope"]["finite_split_history_both_orientations_closed"] and manifest["scope"]["finite_volterra_telescoping_bound_closed"] and not manifest["scope"]["analytic_volterra_bound_closed"] and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite carrier only", "scope")

    rows: list[dict[str, Any]] = []
    for volume in volumes:
        terms, hamiltonian = split_terms(volume, int(source_cfg["oscillator_dimension"]), fixture)
        _, reference, _, _ = source_q3.build_volume(volume, int(source_cfg["oscillator_dimension"]), fixture)
        decomposition_error = float(np.linalg.norm(hamiltonian - reference, ord=2))
        check(f"V={volume} split decomposition", decomposition_error <= tolerance, decomposition_error, f"<={tolerance}", "split")
        rho_roots = {beta: gibbs_root(hamiltonian, beta) for beta in betas}
        distances = graph_distance(volume, pairs[volume][0])
        q_ops, energy, weights = build_energy(volume, int(source_cfg["oscillator_dimension"]), fixture, distances, ratio)
        energy_minimum = float(np.linalg.eigvalsh(energy)[0])
        check(f"V={volume} weighted energy floor", energy_minimum >= float(finite["positive_energy_floor"]) - tolerance, energy_minimum, f">={finite['positive_energy_floor']}", "energy")
        inverse = spectral_power(energy, -power)
        for order_name, order in ((history["orders"][0], list(range(len(terms)))), (history["orders"][1], list(reversed(range(len(terms)))))):
            for sign in history["time_signs"]:
                factors = [term_unitary(terms[index], int(sign), delta) for index in range(len(terms))]
                step = np.eye(terms[0].shape[0], dtype=complex)
                for index in order:
                    step = factors[index] @ step
                unitary_error = float(np.linalg.norm(step.conj().T @ step - np.eye(step.shape[0]), ord=2))
                check(f"V={volume} order={order_name} sign={sign} unitary", unitary_error <= unitary_tolerance, unitary_error, f"<={unitary_tolerance}", "split")
                for site in probes[volume]:
                    cubic = q_ops[site] @ q_ops[site] @ q_ops[site]
                    factor = float(weights[site] ** power)
                    right = factor * cubic @ inverse
                    left = factor * inverse @ cubic
                    comm = right - left
                    comm_norm = operator_norm(comm)
                    check(f"V={volume} order={order_name} sign={sign} site={site} order floor", np.isfinite(comm_norm) and comm_norm > float(finite["commutator_floor"]), comm_norm, f">{finite['commutator_floor']}", "orientation")
                    right_norm = operator_norm(right)
                    left_norm = operator_norm(left)
                    histories = history_sums(right, left, step, delta, counts)
                    for count in counts:
                        history_right, history_left, history_comm = histories[count]
                        op_right, op_left, op_comm = operator_norm(history_right), operator_norm(history_left), operator_norm(history_comm)
                        direct_error = float(np.linalg.norm((history_right - history_left) - history_comm, ord=2))
                        check(f"V={volume} order={order_name} sign={sign} site={site} N={count} identity", direct_error <= tolerance, direct_error, f"<={tolerance}", "Volterra")
                        total_time = count * delta
                        check(f"V={volume} order={order_name} sign={sign} site={site} N={count} triangle", op_comm <= op_right + op_left + triangle_tolerance, op_comm, f"<={op_right + op_left + triangle_tolerance}", "norm")
                        check(f"V={volume} order={order_name} sign={sign} site={site} N={count} right bound", op_right <= total_time * right_norm + triangle_tolerance, op_right, f"<={total_time * right_norm + triangle_tolerance}", "Volterra bound")
                        check(f"V={volume} order={order_name} sign={sign} site={site} N={count} left bound", op_left <= total_time * left_norm + triangle_tolerance, op_left, f"<={total_time * left_norm + triangle_tolerance}", "Volterra bound")
                        state_rows: dict[str, dict[str, float]] = {}
                        for beta, rho_sqrt in rho_roots.items():
                            state_right, state_left, state_comm = (four_leg(history_right, rho_sqrt), four_leg(history_left, rho_sqrt), four_leg(history_comm, rho_sqrt))
                            check(f"V={volume} order={order_name} sign={sign} site={site} N={count} beta={beta} state", all(np.isfinite(value) and value >= -tolerance for value in (state_right, state_left, state_comm)), [state_right, state_left, state_comm], "finite nonnegative", "Gibbs")
                            check(f"V={volume} order={order_name} sign={sign} site={site} N={count} beta={beta} state triangle", state_comm <= state_right + state_left + triangle_tolerance, state_comm, f"<={state_right + state_left + triangle_tolerance}", "Gibbs norm")
                            check(f"V={volume} order={order_name} sign={sign} site={site} N={count} beta={beta} state envelope", state_right <= 2.0 * op_right + triangle_tolerance and state_left <= 2.0 * op_left + triangle_tolerance and state_comm <= 2.0 * op_comm + triangle_tolerance, [state_right, state_left, state_comm], "<=2 operator norm", "Gibbs envelope")
                            state_rows[str(beta)] = {"right": state_right, "left": state_left, "commutator": state_comm}
                        rows.append({"volume": volume, "source_pair": pairs[volume][0], "probe_site": site, "order": order_name, "time_sign": int(sign), "step_count": count, "time": total_time, "weighted_factor": factor, "right_operator_norm": op_right, "left_operator_norm": op_left, "commutator_operator_norm": op_comm, "state_weighted": state_rows})

    expected = sum(len(probes[volume]) * len(history["orders"]) * len(history["time_signs"]) * len(counts) for volume in volumes)
    check("history row coverage", len(rows) == expected, len(rows), expected, "coverage")
    check("all extrema finite", all(np.isfinite(row["commutator_operator_norm"]) for row in rows), len(rows), "finite", "summary")
    max_right = max(row["right_operator_norm"] for row in rows)
    max_left = max(row["left_operator_norm"] for row in rows)
    max_comm = max(row["commutator_operator_norm"] for row in rows)
    max_state = max(value for row in rows for state in row["state_weighted"].values() for value in state.values())
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
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
    print(f"INDEPENDENT CUBIC-MULTIPLIER-SPLIT-HISTORY-VOLTERRA PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['history_row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
