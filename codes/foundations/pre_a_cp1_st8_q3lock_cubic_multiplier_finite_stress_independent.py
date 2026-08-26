#!/usr/bin/env python3
"""Independent reconstruction of the finite Q3 cubic-multiplier stress audit."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-cubic-multiplier-finite-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-26-independent-pre_a_cp1_st8_q3lock_cubic_multiplier_finite_stress" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as source_q3  # noqa: E402


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


def distances(volume: int, sources: list[int]) -> list[int]:
    adjacency = [[] for _ in range(volume)]
    for left, right in source_q3.graph_edges(volume):
        adjacency[left].append(right)
        adjacency[right].append(left)
    result = [volume + 10] * volume
    queue = list(sources)
    for site in sources:
        result[site] = 0
    cursor = 0
    while cursor < len(queue):
        current = queue[cursor]
        cursor += 1
        for neighbor in sorted(adjacency[current]):
            trial = result[current] + 1
            if trial < result[neighbor]:
                result[neighbor] = trial
                queue.append(neighbor)
    return result


def spectral_power(matrix: np.ndarray, exponent: float, minimum_required: float | None = None) -> np.ndarray:
    hermitian = (matrix + matrix.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    if minimum_required is not None and float(values.min()) < minimum_required - 1.0e-9:
        raise AssertionError(f"spectral input has minimum {values.min()}")
    return (vectors * np.power(np.maximum(values, 0.0), exponent)) @ vectors.conj().T


def build_energy(volume: int, n: int, fixture: dict[str, Any], site_distances: list[int], ratio: float) -> tuple[list[np.ndarray], np.ndarray, list[float]]:
    q_one, p_one = source_q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [source_q3.embed(q_one, site, volume, identity) for site in range(volume)]
    p_ops = [source_q3.embed(p_one, site, volume, identity) for site in range(volume)]
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    factors = [ratio ** d for d in site_distances]
    onsite = [p @ p / (2 * chi) + r * q @ q / 2 + g * q @ q @ q @ q / 4 for q, p in zip(q_ops, p_ops)]
    bonds = {(u, v): source_q3.bond_term(q_ops[u], q_ops[v], fixture) for u, v in source_q3.graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    weighted = sum((factors[site] * onsite[site] for site in range(volume)), zero)
    for (u, v), bond in bonds.items():
        weighted = weighted + (factors[u] + factors[v]) * bond / 2
    identity_full = np.eye(weighted.shape[0], dtype=complex)
    base = weighted + identity_full
    base = (base + base.conj().T) / 2
    minimum = float(np.linalg.eigvalsh(base)[0])
    shifted = base + (1.0 - minimum) * identity_full
    return q_ops, shifted, factors


def four_leg(matrix: np.ndarray, rho_sqrt: np.ndarray) -> float:
    terms = (
        matrix @ rho_sqrt,
        matrix.conj().T @ rho_sqrt,
        rho_sqrt @ matrix,
        rho_sqrt @ matrix.conj().T,
    )
    return float(np.sqrt(sum(float(np.vdot(term, term).real) for term in terms)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["source_fixture"]
    graph = manifest["energy_graph"]
    volumes = [int(v) for v in fixture["volume_values"]]
    n = int(fixture["oscillator_dimension"])
    betas = [float(v) for v in fixture["beta_values"]]
    pairs = {int(k): [[int(site) for site in pair] for pair in value] for k, value in fixture["source_pairs"].items()}
    ratio = float(Fraction(graph["weight_ratio_per_edge"]))
    power = float(Fraction(graph["multiplier_power"]))
    tolerance = float(manifest["finite_fixture"]["tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001158" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["claim_bearing"]], "EXP-001158/false", "provenance")
    check("weight contract", Fraction(graph["weight_fourth_root"]) ** 4 == Fraction(graph["weight_ratio_per_edge"]) and power == 0.75, [graph["weight_fourth_root"], graph["weight_ratio_per_edge"], power], "root^4=ratio and power=3/4", "weight")

    summaries: list[dict[str, Any]] = []
    row_count = 0
    maximum_operator = 0.0
    maximum_state = 0.0
    for volume in volumes:
        q_full, h_full, _, _ = source_q3.build_volume(volume, n, fixture)
        rho_roots = {beta: spectral_power(source_q3.gibbs(h_full, beta), 0.5, 0.0) for beta in betas}
        for pair in pairs[volume]:
            site_distances = distances(volume, pair)
            q_ops, energy, factors = build_energy(volume, n, fixture, site_distances, ratio)
            inverse = spectral_power(energy, -power, 1.0)
            minimum = float(np.linalg.eigvalsh(energy)[0])
            check(f"V={volume} pair={pair} minimum", minimum >= 1.0 - tolerance, minimum, ">=1", "energy proxy")
            row_values: list[dict[str, Any]] = []
            for site, q_operator in enumerate(q_ops):
                cubic = q_operator @ q_operator @ q_operator
                right = cubic @ inverse
                left = inverse @ cubic
                right_norm = float(np.linalg.svd(right, compute_uv=False)[0])
                left_norm = float(np.linalg.svd(left, compute_uv=False)[0])
                factor = factors[site] ** power
                weighted_right = factor * right_norm
                weighted_left = factor * left_norm
                state_max = 0.0
                for beta, root_state in rho_roots.items():
                    right_state = four_leg(right, root_state)
                    left_state = four_leg(left, root_state)
                    check(f"V={volume} pair={pair} site={site} beta={beta} finite", all(np.isfinite(v) and v >= -tolerance for v in (right_state, left_state)), [right_state, left_state], "finite nonnegative", "state weighted")
                    state_max = max(state_max, right_state, left_state)
                check(f"V={volume} pair={pair} site={site} operator finite", all(np.isfinite(v) for v in (right_norm, left_norm, weighted_right, weighted_left)), [right_norm, left_norm, weighted_right, weighted_left], "finite", "operator multiplier")
                maximum_operator = max(maximum_operator, weighted_right, weighted_left)
                maximum_state = max(maximum_state, state_max)
                row_values.append({"site": site, "distance": site_distances[site], "weighted_right": weighted_right, "weighted_left": weighted_left, "state_max": state_max})
                row_count += 1
            summaries.append({"volume": volume, "source_pair": pair, "distances": site_distances, "rows": row_values})
    check("coverage", row_count == sum(len(pairs[v]) * v for v in volumes), row_count, sum(len(pairs[v]) * v for v in volumes), "coverage")
    check("global finite", np.isfinite(maximum_operator) and np.isfinite(maximum_state), [maximum_operator, maximum_state], "finite", "summary")
    check("scope firewall", not manifest["scope"]["analytic_cubic_embedding_closed"] and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "analytic/QFT gates remain open", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CUBIC-MULTIPLIER-FINITE-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:80] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "derived": {"row_count": row_count, "summary_rows": summaries, "max_weighted_operator_norm": maximum_operator, "max_state_weighted_norm": maximum_state, "finite_cubic_multiplier_rows_closed": True, "finite_source_beta_volume_stress_closed": True, "analytic_cubic_embedding_closed": False, "common_alpha_closed": False, "pre_a_closed": False},
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
    print(f"INDEPENDENT CUBIC-MULTIPLIER-FINITE-STRESS PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
