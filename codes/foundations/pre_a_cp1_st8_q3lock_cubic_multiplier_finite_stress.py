#!/usr/bin/env python3
"""Primary finite stress audit for the Q3 cubic energy-graph multiplier."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_cubic_multiplier_finite_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-cubic-multiplier-finite-stress-manifest.json"
SOURCE_MANIFEST = REPO / "strategy/pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress_manifest.json"
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


def graph_distance(volume: int, sources: list[int]) -> list[int]:
    edges = q3.graph_edges(volume)
    adjacency = {site: set() for site in range(volume)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    distances = [10**9] * volume
    frontier = list(sources)
    for site in sources:
        distances[site] = 0
    while frontier:
        current = frontier.pop(0)
        for neighbor in sorted(adjacency[current]):
            if distances[neighbor] > distances[current] + 1:
                distances[neighbor] = distances[current] + 1
                frontier.append(neighbor)
    return distances


def four_leg_norm(matrix: np.ndarray, rho_sqrt: np.ndarray) -> float:
    legs = (
        matrix @ rho_sqrt,
        matrix.conj().T @ rho_sqrt,
        rho_sqrt @ matrix,
        rho_sqrt @ matrix.conj().T,
    )
    return float(np.sqrt(sum(np.linalg.norm(leg, ord="fro") ** 2 for leg in legs)))


def weighted_energy(
    volume: int,
    n: int,
    fixture: dict[str, Any],
    distances: list[int],
    ratio: float,
) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    weights = [ratio ** distance for distance in distances]
    onsite = [
        p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0
        for q, p in zip(q_ops, p_ops)
    ]
    bonds = {(left, right): q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in q3.graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    weighted = sum((weight * term for weight, term in zip(weights, onsite)), zero)
    weighted += sum(
        (((weights[left] + weights[right]) / 2.0) * bond for (left, right), bond in bonds.items()),
        zero,
    )
    base = (weighted + np.eye(weighted.shape[0], dtype=complex) + (weighted + np.eye(weighted.shape[0], dtype=complex)).conj().T) / 2.0
    energy = q3.positive_weight(base)
    return q_ops, energy, np.asarray(weights, dtype=float)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    source_fixture = manifest["source_fixture"]
    graph = manifest["energy_graph"]
    fixture = source_fixture
    volumes = [int(value) for value in source_fixture["volume_values"]]
    n = int(source_fixture["oscillator_dimension"])
    betas = [float(value) for value in source_fixture["beta_values"]]
    ratio = float(Fraction(graph["weight_ratio_per_edge"]))
    root = Fraction(graph["weight_fourth_root"])
    multiplier_power = Fraction(graph["multiplier_power"])
    tolerance = float(manifest["finite_fixture"]["tolerance"])
    source_pairs = {int(key): [[int(site) for site in pair] for pair in pairs] for key, pairs in source_fixture["source_pairs"].items()}
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001158" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001158/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("source authority", source["exploration_id"] == "EXP-001088" and source["task_id"] == "T-054", [source["exploration_id"], source["task_id"]], "EXP-001088/T-054", "provenance")
    check("weight fourth-power identity", root > 0 and root**4 == Fraction(graph["weight_ratio_per_edge"]), [root, Fraction(graph["weight_ratio_per_edge"])], "root^4=ratio", "weight")
    check("multiplier power", multiplier_power == Fraction(3, 4), multiplier_power, "3/4", "weight")
    check("finite fixture", all(volume in source_pairs for volume in volumes) and all(beta > 0 for beta in betas), [volumes, betas], "declared finite cases", "fixture")

    all_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for volume in volumes:
        q_ops_full, hamiltonian, _, _ = q3.build_volume(volume, n, fixture)
        rho_by_beta = {beta: q3.gibbs(hamiltonian, beta) for beta in betas}
        rho_sqrt_by_beta = {beta: q3.spectral_power(rho, 0.5) for beta, rho in rho_by_beta.items()}
        check(f"V={volume} source pairs valid", all(len(pair) == 2 and all(0 <= site < volume for site in pair) for pair in source_pairs[volume]), source_pairs[volume], "valid pairs", "fixture")
        for pair_index, pair in enumerate(source_pairs[volume]):
            distances = graph_distance(volume, pair)
            q_ops, energy, weights = weighted_energy(volume, n, fixture, distances, ratio)
            negative_minimum = float(np.min(np.linalg.eigvalsh(energy)))
            check(f"V={volume} pair={pair_index} A positive", negative_minimum >= 1.0 - tolerance, negative_minimum, ">=1", "energy proxy")
            inverse_power = q3.spectral_power(energy, -float(multiplier_power))
            pair_rows: list[dict[str, Any]] = []
            for site, q_operator in enumerate(q_ops):
                cubic = q_operator @ q_operator @ q_operator
                right = cubic @ inverse_power
                left = inverse_power @ cubic
                right_norm = q3.operator_norm(right)
                left_norm = q3.operator_norm(left)
                weighted_right = float(weights[site] ** float(multiplier_power)) * right_norm
                weighted_left = float(weights[site] ** float(multiplier_power)) * left_norm
                check(f"V={volume} pair={pair_index} site={site} operator finite", all(np.isfinite(value) for value in (right_norm, left_norm, weighted_right, weighted_left)), [right_norm, left_norm, weighted_right, weighted_left], "finite", "operator multiplier")
                state_rows: dict[str, dict[str, float]] = {}
                for beta in betas:
                    rho_sqrt = rho_sqrt_by_beta[beta]
                    right_state = four_leg_norm(right, rho_sqrt)
                    left_state = four_leg_norm(left, rho_sqrt)
                    check(f"V={volume} pair={pair_index} site={site} beta={beta} state finite", all(np.isfinite(value) and value >= -tolerance for value in (right_state, left_state)), [right_state, left_state], "finite nonnegative", "state weighted")
                    state_rows[str(beta)] = {"right": right_state, "left": left_state}
                row = {
                    "volume": volume,
                    "source_pair": pair,
                    "site": site,
                    "distance": distances[site],
                    "weight": float(weights[site]),
                    "weighted_factor": float(weights[site] ** float(multiplier_power)),
                    "right_operator_norm": right_norm,
                    "left_operator_norm": left_norm,
                    "weighted_right_operator_norm": weighted_right,
                    "weighted_left_operator_norm": weighted_left,
                    "state_weighted": state_rows,
                }
                all_rows.append(row)
                pair_rows.append(row)
            summary_rows.append({
                "volume": volume,
                "source_pair": pair,
                "distance_profile": distances,
                "max_right_operator_norm": max(row["right_operator_norm"] for row in pair_rows),
                "max_left_operator_norm": max(row["left_operator_norm"] for row in pair_rows),
                "max_weighted_right_operator_norm": max(row["weighted_right_operator_norm"] for row in pair_rows),
                "max_weighted_left_operator_norm": max(row["weighted_left_operator_norm"] for row in pair_rows),
                "max_state_weighted_by_beta": {
                    str(beta): max(
                        max(row["state_weighted"][str(beta)]["right"], row["state_weighted"][str(beta)]["left"])
                        for row in pair_rows
                    )
                    for beta in betas
                },
            })
        check(f"V={volume} row coverage", len([row for row in all_rows if row["volume"] == volume]) == len(source_pairs[volume]) * volume, len([row for row in all_rows if row["volume"] == volume]), len(source_pairs[volume]) * volume, "coverage")

    check("row coverage", len(all_rows) == sum(len(source_pairs[volume]) * volume for volume in volumes), len(all_rows), sum(len(source_pairs[volume]) * volume for volume in volumes), "coverage")
    max_operator = max(max(row["weighted_right_operator_norm"], row["weighted_left_operator_norm"]) for row in all_rows)
    max_state = max(max(value.values()) for row in all_rows for value in row["state_weighted"].values())
    check("global finite maxima", np.isfinite(max_operator) and np.isfinite(max_state), [max_operator, max_state], "finite", "summary")
    check("scope firewall", not manifest["scope"]["analytic_cubic_embedding_closed"] and not manifest["scope"]["common_alpha_closed"] and not manifest["scope"]["pre_a_closed"], manifest["scope"], "analytic/QFT gates remain open", "scope")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CUBIC-MULTIPLIER-FINITE-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:80] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "derived": {
            "source_manifest_sha256": normalized_sha256(SOURCE_MANIFEST),
            "row_count": len(all_rows),
            "summary_rows": summary_rows,
            "max_weighted_operator_norm": max_operator,
            "max_state_weighted_norm": max_state,
            "finite_cubic_multiplier_rows_closed": True,
            "finite_source_beta_volume_stress_closed": True,
            "analytic_cubic_embedding_closed": False,
            "operator_domain_embedding_closed": False,
            "actual_q3_history_closed": False,
            "direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
        },
        "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY CUBIC-MULTIPLIER-FINITE-STRESS PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
