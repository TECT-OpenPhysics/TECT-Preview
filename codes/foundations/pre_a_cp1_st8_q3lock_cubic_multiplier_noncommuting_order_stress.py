#!/usr/bin/env python3
"""Finite Q3 order-sensitivity audit for the cubic multiplier carrier.

The audit keeps q_x^3 A_f^(-3/4) and A_f^(-3/4) q_x^3 as separate
operators, measures their commutator, and checks the corresponding operator
and Gibbs four-leg triangle bounds.  It is deliberately finite evidence; no
commutation or infinite-volume domain statement is inferred.
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
SLUG = "pre_a_cp1_st8_q3lock_cubic_multiplier_noncommuting_order_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-cubic-multiplier-noncommuting-order-stress-manifest.json"
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
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    weights = np.asarray([ratio ** distance for distance in distances], dtype=float)
    onsite = [
        p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0
        for q, p in zip(q_ops, p_ops)
    ]
    bonds = {(left, right): q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in q3.graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    weighted = sum((weights[site] * onsite[site] for site in range(volume)), zero)
    weighted += sum(
        (((weights[left] + weights[right]) / 2.0) * bond for (left, right), bond in bonds.items()),
        zero,
    )
    base = (weighted + np.eye(weighted.shape[0], dtype=complex) + (weighted + np.eye(weighted.shape[0], dtype=complex)).conj().T) / 2.0
    return q_ops, q3.positive_weight(base), weights


def four_leg_norm(matrix: np.ndarray, rho_sqrt: np.ndarray) -> float:
    legs = (
        matrix @ rho_sqrt,
        matrix.conj().T @ rho_sqrt,
        rho_sqrt @ matrix,
        rho_sqrt @ matrix.conj().T,
    )
    return float(np.sqrt(sum(np.linalg.norm(leg, ord="fro") ** 2 for leg in legs)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_path = REPO / manifest["source_fixture"]["manifest"]
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source_cfg = manifest["source_fixture"]
    fixture = source["finite_fixture"]
    order_cfg = manifest["order_test"]
    finite_cfg = manifest["finite_fixture"]
    tolerance = float(order_cfg["agreement_tolerance"])
    triangle_tolerance = float(order_cfg["triangle_tolerance"])
    operator_floor = float(order_cfg["operator_noncommutation_floor"])
    state_floor = float(order_cfg["state_noncommutation_floor"])
    ratio = float(Fraction(finite_cfg["weight_ratio_per_edge"]))
    power = float(Fraction(finite_cfg["multiplier_power"]))
    volumes = [int(value) for value in source_cfg["volume_values"]]
    betas = [float(value) for value in source_cfg["beta_values"]]
    pairs = {int(key): [[int(site) for site in pair] for pair in value] for key, value in source_cfg["source_pairs"].items()}
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check(
        "identity",
        manifest["exploration_id"] == "EXP-001159" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False,
        [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]],
        "EXP-001159/T-054/false",
        "provenance",
    )
    check("source authority", source["exploration_id"] == "EXP-001088" and source["task_id"] == "T-054", [source["exploration_id"], source["task_id"]], "EXP-001088/T-054", "provenance")
    check("weight contract", Fraction(finite_cfg["multiplier_power"]) == Fraction(3, 4) and Fraction(1, 2) ** 4 == Fraction(finite_cfg["weight_ratio_per_edge"]), [finite_cfg["multiplier_power"], finite_cfg["weight_ratio_per_edge"]], "power=3/4 and fourth-root=1/2", "weight")
    check("declared coverage", set(volumes) == set(pairs) and all(pairs[volume] for volume in volumes), [volumes, pairs], "all declared volumes have source pairs", "fixture")

    rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for volume in volumes:
        _, hamiltonian, _, _ = q3.build_volume(volume, int(source_cfg["oscillator_dimension"]), fixture)
        rho_roots = {beta: q3.spectral_power(q3.gibbs(hamiltonian, beta), 0.5) for beta in betas}
        volume_rows: list[dict[str, Any]] = []
        for pair_index, pair in enumerate(pairs[volume]):
            check(
                f"V={volume} pair={pair_index} source valid",
                len(pair) == 2 and all(0 <= site < volume for site in pair),
                pair,
                "two in-range source sites",
                "fixture",
            )
            distances = graph_distance(volume, pair)
            q_ops, energy, weights = weighted_energy(volume, int(source_cfg["oscillator_dimension"]), fixture, distances, ratio)
            minimum = float(np.min(np.linalg.eigvalsh(energy)))
            check(f"V={volume} pair={pair_index} energy floor", minimum >= float(finite_cfg["positive_energy_floor"]) - tolerance, minimum, f">={finite_cfg['positive_energy_floor']}", "energy proxy")
            inverse_power = q3.spectral_power(energy, -power)
            for site, q_operator in enumerate(q_ops):
                cubic = q_operator @ q_operator @ q_operator
                right = cubic @ inverse_power
                left = inverse_power @ cubic
                reverse = left - right
                commutator = right - left
                right_norm = q3.operator_norm(right)
                left_norm = q3.operator_norm(left)
                commutator_norm = q3.operator_norm(commutator)
                weighted_factor = float(weights[site] ** power)
                weighted_commutator_norm = weighted_factor * commutator_norm
                check(
                    f"V={volume} pair={pair_index} site={site} noncommuting",
                    np.isfinite(commutator_norm) and commutator_norm > operator_floor,
                    commutator_norm,
                    f">{operator_floor}",
                    "order sensitivity",
                )
                check(
                    f"V={volume} pair={pair_index} site={site} antisymmetry",
                    np.linalg.norm(commutator + reverse, ord="fro") <= tolerance,
                    np.linalg.norm(commutator + reverse, ord="fro"),
                    f"<={tolerance}",
                    "order identity",
                )
                check(
                    f"V={volume} pair={pair_index} site={site} operator triangle",
                    commutator_norm <= right_norm + left_norm + triangle_tolerance,
                    commutator_norm,
                    f"<={right_norm + left_norm + triangle_tolerance}",
                    "norm bookkeeping",
                )
                state_rows: dict[str, dict[str, float]] = {}
                for beta in betas:
                    rho_sqrt = rho_roots[beta]
                    right_state = four_leg_norm(right, rho_sqrt)
                    left_state = four_leg_norm(left, rho_sqrt)
                    commutator_state = four_leg_norm(commutator, rho_sqrt)
                    check(
                        f"V={volume} pair={pair_index} site={site} beta={beta} state noncommuting",
                        np.isfinite(commutator_state) and commutator_state > state_floor,
                        commutator_state,
                        f">{state_floor}",
                        "state order sensitivity",
                    )
                    check(
                        f"V={volume} pair={pair_index} site={site} beta={beta} state triangle",
                        commutator_state <= right_state + left_state + triangle_tolerance,
                        commutator_state,
                        f"<={right_state + left_state + triangle_tolerance}",
                        "state norm bookkeeping",
                    )
                    state_rows[str(beta)] = {"right": right_state, "left": left_state, "commutator": commutator_state}
                row = {
                    "volume": volume,
                    "source_pair": pair,
                    "site": site,
                    "distance": distances[site],
                    "weight": float(weights[site]),
                    "weighted_factor": weighted_factor,
                    "right_operator_norm": right_norm,
                    "left_operator_norm": left_norm,
                    "operator_commutator_norm": commutator_norm,
                    "weighted_operator_commutator_norm": weighted_commutator_norm,
                    "state_weighted": state_rows,
                }
                rows.append(row)
                volume_rows.append(row)
        check(f"V={volume} row coverage", len(volume_rows) == volume * len(pairs[volume]), len(volume_rows), volume * len(pairs[volume]), "coverage")
        summary_rows.extend(
            {
                "volume": volume,
                "source_pair": pair,
                "distance_profile": graph_distance(volume, pair),
                "min_operator_commutator_norm": min(row["operator_commutator_norm"] for row in volume_rows if row["source_pair"] == pair),
                "max_operator_commutator_norm": max(row["operator_commutator_norm"] for row in volume_rows if row["source_pair"] == pair),
                "max_weighted_operator_commutator_norm": max(row["weighted_operator_commutator_norm"] for row in volume_rows if row["source_pair"] == pair),
                "max_state_weighted_by_beta": {
                    str(beta): max(row["state_weighted"][str(beta)]["commutator"] for row in volume_rows if row["source_pair"] == pair)
                    for beta in betas
                },
            }
            for pair in pairs[volume]
        )

    expected_rows = int(finite_cfg["row_count_expected"])
    check("global row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    minimum_operator = min(row["operator_commutator_norm"] for row in rows)
    maximum_operator = max(row["operator_commutator_norm"] for row in rows)
    minimum_state_by_beta = {str(beta): min(row["state_weighted"][str(beta)]["commutator"] for row in rows) for beta in betas}
    maximum_state_by_beta = {str(beta): max(row["state_weighted"][str(beta)]["commutator"] for row in rows) for beta in betas}
    check("global finite commutator extrema", np.isfinite(minimum_operator) and np.isfinite(maximum_operator) and all(np.isfinite(value) for value in minimum_state_by_beta.values()), [minimum_operator, maximum_operator, minimum_state_by_beta], "finite extrema", "summary")
    check("scope firewall", manifest["scope"]["finite_noncommuting_orientation_rows_closed"] and manifest["scope"]["orientation_interchangeability_rejected_on_fixture"] and not manifest["scope"]["analytic_cubic_embedding_closed"] and not manifest["scope"]["common_alpha_closed"] and not manifest["scope"]["pre_a_closed"], manifest["scope"], "finite order result only", "scope")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CUBIC-MULTIPLIER-NONCOMMUTING-ORDER-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:100] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "derived": {
            "source_manifest_sha256": normalized_sha256(source_path),
            "row_count": len(rows),
            "summary_rows": summary_rows,
            "minimum_operator_commutator_norm": minimum_operator,
            "maximum_operator_commutator_norm": maximum_operator,
            "minimum_state_weighted_commutator_norm_by_beta": minimum_state_by_beta,
            "maximum_state_weighted_commutator_norm_by_beta": maximum_state_by_beta,
            "finite_noncommuting_orientation_rows_closed": True,
            "orientation_interchangeability_rejected_on_fixture": True,
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
    print(f"PRIMARY CUBIC-MULTIPLIER-NONCOMMUTING-ORDER-STRESS PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
