#!/usr/bin/env python3
"""Independent reconstruction of the finite analytic Q3 Trotter bound.

This lane deliberately does not import the primary audit.  It rebuilds the
finite oscillator embeddings, local support commutators, split products and
multiplier histories from the pinned fixture and checks the same inequalities.
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
SLUG = "pre_a_cp1_st8_q3lock_finite_analytic_trotter_defect"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-analytic-trotter-defect-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


def sha256(path: Path) -> str:
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


def h(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def exp_h(values: np.ndarray, vectors: np.ndarray, time: float) -> np.ndarray:
    return (vectors * np.exp(-1j * time * values)) @ vectors.conj().T


def graph_distance(volume: int, sources: list[int]) -> list[int]:
    adjacency = {site: set() for site in range(volume)}
    for left, right in q3.graph_edges(volume):
        adjacency[left].add(right)
        adjacency[right].add(left)
    distance = [volume + 10] * volume
    frontier = list(sources)
    for site in sources:
        distance[site] = 0
    cursor = 0
    while cursor < len(frontier):
        current = frontier[cursor]
        cursor += 1
        for neighbor in sorted(adjacency[current]):
            candidate = distance[current] + 1
            if candidate < distance[neighbor]:
                distance[neighbor] = candidate
                frontier.append(neighbor)
    return distance


def weighted(volume: int, n: int, fixture: dict[str, Any], distances: list[int], ratio: float) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    weights = np.asarray([ratio ** value for value in distances], dtype=float)
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in q3.graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    weighted_sum = sum((weights[site] * onsite[site] for site in range(volume)), zero)
    weighted_sum += sum((((weights[left] + weights[right]) / 2.0) * value for (left, right), value in bonds.items()), zero)
    return q_ops, q3.positive_weight(h(weighted_sum + np.eye(weighted_sum.shape[0], dtype=complex))), weights


def specs(volume: int) -> list[tuple[str, tuple[int, ...]]]:
    return [("onsite", (site,)) for site in range(volume)] + [("bond", (left, right)) for left, right in q3.graph_edges(volume)]


def split(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[tuple[str, tuple[int, ...]]], np.ndarray]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    terms = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    terms.extend(h(q3.bond_term(q_ops[left], q_ops[right], fixture)) for left, right in q3.graph_edges(volume))
    zero = np.zeros_like(q_ops[0])
    return terms, specs(volume), h(sum(terms, zero))


def local_term(spec: tuple[str, tuple[int, ...]], union: list[int], n: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = {site: q3.embed(q_single, index, len(union), identity) for index, site in enumerate(union)}
    p_ops = {site: q3.embed(p_single, index, len(union), identity) for index, site in enumerate(union)}
    kind, support = spec
    if kind == "onsite":
        q, p = q_ops[support[0]], p_ops[support[0]]
        chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
        return h(p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0)
    return h(q3.bond_term(q_ops[support[0]], q_ops[support[1]], fixture))


def local_commutator(spec_left: tuple[str, tuple[int, ...]], spec_right: tuple[str, tuple[int, ...]], n: int, fixture: dict[str, Any]) -> float:
    support_left, support_right = set(spec_left[1]), set(spec_right[1])
    if support_left.isdisjoint(support_right):
        return 0.0
    union = sorted(support_left | support_right)
    left, right = local_term(spec_left, union, n, fixture), local_term(spec_right, union, n, fixture)
    return norm(left @ right - right @ left)


def c_sum(terms: list[np.ndarray], term_specs: list[tuple[str, tuple[int, ...]]], n: int, fixture: dict[str, Any]) -> tuple[float, float]:
    total = 0.0
    residual = 0.0
    checked = False
    for left_index in range(len(term_specs)):
        for right_index in range(left_index + 1, len(term_specs)):
            value = local_commutator(term_specs[left_index], term_specs[right_index], n, fixture)
            if value == 0.0:
                continue
            total += value
            if not checked:
                full = norm(terms[left_index] @ terms[right_index] - terms[right_index] @ terms[left_index])
                residual = abs(full - value)
                checked = True
    return total, residual


def step(eigensystems: list[tuple[np.ndarray, np.ndarray]], order: list[int], sign: int, delta: float) -> np.ndarray:
    result = np.eye(eigensystems[0][1].shape[0], dtype=complex)
    for index in order:
        values, vectors = eigensystems[index]
        result = exp_h(values, vectors, sign * delta) @ result
    return result


def history(matrix: np.ndarray, unitary: np.ndarray, delta: float, count: int) -> np.ndarray:
    current = matrix.copy()
    result = np.zeros_like(matrix)
    for _ in range(count):
        result = result + delta * current
        current = unitary @ current @ unitary.conj().T
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent_path = REPO / manifest["source_fixture"]["manifest"]
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    source_path = REPO / parent["source_fixture"]["manifest"]
    source = json.loads(source_path.read_text(encoding="utf-8"))
    fixture_path = REPO / source["source_fixture"]["manifest"]
    fixture_manifest = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture = fixture_manifest["source_fixture"]
    analytic, finite, scope = manifest["analytic_fixture"], manifest["finite_fixture"], manifest["scope"]
    horizon = float(Fraction(analytic["horizon"]))
    counts = [int(value) for value in analytic["step_counts"]]
    volumes = [int(value) for value in manifest["source_fixture"]["volume_values"]]
    n = int(manifest["source_fixture"]["oscillator_dimension"])
    pairs = {int(key): [[int(site) for site in pair] for pair in value] for key, value in manifest["source_fixture"]["source_pairs"].items()}
    probes = {int(key): [int(site) for site in value] for key, value in manifest["source_fixture"]["probe_sites"].items()}
    ratio, power = float(Fraction(analytic["weight_ratio_per_edge"])), float(Fraction(analytic["multiplier_power"]))
    tolerance = float(finite["bound_slack_tolerance"])
    assert manifest["exploration_id"] == "EXP-001162" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False
    assert parent["exploration_id"] == "EXP-001161"
    assert counts == [3, 6, 12] and abs(horizon - 1.0 / 3.0) <= tolerance
    assert scope["finite_local_commutator_sum_closed"] and scope["finite_fixed_cutoff_volume_linear_envelope_closed"] and scope["finite_analytic_unitary_defect_closed"] and not scope["cutoff_uniform_volume_linear_bound_closed"] and not scope["volume_uniform_trotter_bound_closed"]
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    maximum_unitary_bound = 0.0
    maximum_history_bound = 0.0
    minimum_unitary_slack = float("inf")
    minimum_history_slack = float("inf")
    for volume in volumes:
        terms, term_specs, hamiltonian = split(volume, n, fixture)
        _, reference, _, _ = q3.build_volume(volume, n, fixture)
        assert norm(hamiltonian - reference) <= float(finite["decomposition_tolerance"])
        c_value, localization_residual = c_sum(terms, term_specs, n, fixture)
        assert np.isfinite(c_value) and c_value > float(finite["commutator_floor"])
        assert localization_residual <= float(finite["localization_tolerance"])
        overlap_count = sum(1 for left_index in range(len(term_specs)) for right_index in range(left_index + 1, len(term_specs)) if not set(term_specs[left_index][1]).isdisjoint(set(term_specs[right_index][1])))
        term_norm_max = max(norm(term) for term in terms)
        coarse_volume_bound = 2.0 * overlap_count * term_norm_max * term_norm_max
        assert c_value <= coarse_volume_bound + tolerance * (1.0 + coarse_volume_bound)
        h_values, h_vectors = np.linalg.eigh(hamiltonian)
        term_eigensystems = [np.linalg.eigh(h(term)) for term in terms]
        volume_max_final = 0.0
        volume_max_bound = 0.0
        volume_max_history = 0.0
        volume_max_history_bound = 0.0
        row_count = 0
        for pair in pairs[volume]:
            distances = graph_distance(volume, pair)
            q_ops, energy, weights = weighted(volume, n, fixture, distances, ratio)
            assert float(np.min(np.linalg.eigvalsh(energy))) >= float(finite["positive_energy_floor"]) - tolerance
            inverse = q3.spectral_power(energy, -power)
            cubic = q_ops[probes[volume][0]] @ q_ops[probes[volume][0]] @ q_ops[probes[volume][0]]
            factor = float(weights[probes[volume][0]] ** power)
            multipliers = {"right": factor * cubic @ inverse, "left": factor * inverse @ cubic}
            multipliers["commutator"] = multipliers["right"] - multipliers["left"]
            multiplier_norms = {key: norm(value) for key, value in multipliers.items()}
            assert multiplier_norms["commutator"] > float(finite["commutator_floor"])
            for order_name, order in ((analytic["orders"][0], list(range(len(terms)))), (analytic["orders"][1], list(reversed(range(len(terms)))))):
                for sign in analytic["time_signs"]:
                    exact = exp_h(h_values, h_vectors, int(sign) * horizon)
                    for count in counts:
                        delta = horizon / count
                        split_unitary = step(term_eigensystems, order, int(sign), delta)
                        assert norm(split_unitary.conj().T @ split_unitary - np.eye(split_unitary.shape[0])) <= float(finite["unitarity_tolerance"])
                        final_error = norm(np.linalg.matrix_power(split_unitary, count) - exact)
                        unitary_bound = horizon * horizon * c_value / (2.0 * count)
                        unitary_slack = unitary_bound - final_error
                        assert unitary_slack >= -tolerance * (1.0 + unitary_bound)
                        exact_increment = exp_h(h_values, h_vectors, int(sign) * delta)
                        for orientation, multiplier in multipliers.items():
                            observed = norm(history(multiplier, split_unitary, delta, count) - history(multiplier, exact_increment, delta, count))
                            bound = delta**3 * c_value * count * (count - 1) * multiplier_norms[orientation] / 2.0
                            slack = bound - observed
                            assert slack >= -tolerance * (1.0 + bound)
                            rows.append({"volume": volume, "order": order_name, "time_sign": int(sign), "step_count": count, "orientation": orientation, "commutator_sum": c_value, "final_unitary_error": final_error, "unitary_bound": unitary_bound, "unitary_slack": unitary_slack, "history_error": observed, "history_bound": bound, "history_slack": slack})
                            row_count += 1
                            volume_max_history = max(volume_max_history, observed)
                            volume_max_history_bound = max(volume_max_history_bound, bound)
                            maximum_history_bound = max(maximum_history_bound, bound)
                            minimum_history_slack = min(minimum_history_slack, slack)
                        volume_max_final = max(volume_max_final, final_error)
                        volume_max_bound = max(volume_max_bound, unitary_bound)
                        maximum_unitary_bound = max(maximum_unitary_bound, unitary_bound)
                        minimum_unitary_slack = min(minimum_unitary_slack, unitary_slack)
        expected = len(pairs[volume]) * len(analytic["orders"]) * len(analytic["time_signs"]) * len(counts) * 3
        assert row_count == expected
        summaries.append({"volume": volume, "term_count": len(terms), "dimension": n**volume, "commutator_sum": c_value, "commutator_sum_per_site": c_value / volume, "localization_residual": localization_residual, "overlap_pair_count": overlap_count, "term_norm_max": term_norm_max, "coarse_volume_commutator_bound": coarse_volume_bound, "max_final_unitary_error": volume_max_final, "max_unitary_bound": volume_max_bound, "max_history_error": volume_max_history, "max_history_bound": volume_max_history_bound, "row_count": row_count})
    assert [item["volume"] for item in summaries] == volumes
    assert np.isfinite(minimum_unitary_slack) and np.isfinite(minimum_history_slack)
    assert not scope["volume_uniform_trotter_bound_closed"] and not scope["analytic_infinite_dimensional_trotter_rate_closed"] and not scope["common_alpha_closed"]
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ANALYTIC-TROTTER-DEFECT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": [{"status": "PASS", "name": "independent finite analytic bound rows", "actual": str(len(rows)), "expected": "all rows"}],
        "derived": {
            "source_manifest_sha256": sha256(source_path),
            "parent_manifest_sha256": sha256(parent_path),
            "row_count": len(rows),
            "volume_summaries": summaries,
            "commutator_sum_by_volume": {str(item["volume"]): item["commutator_sum"] for item in summaries},
            "commutator_sum_per_site_by_volume": {str(item["volume"]): item["commutator_sum_per_site"] for item in summaries},
            "max_unitary_bound": maximum_unitary_bound,
            "max_history_bound": maximum_history_bound,
            "minimum_unitary_slack": minimum_unitary_slack,
            "minimum_history_slack": minimum_history_slack,
            "finite_local_commutator_sum_closed": True,
            "finite_fixed_cutoff_volume_linear_envelope_closed": True,
            "finite_analytic_unitary_defect_closed": True,
            "finite_two_orientation_history_bound_closed": True,
            "finite_bound_both_orders_and_signs_closed": True,
            "volume_uniform_trotter_bound_closed": False,
            "cutoff_uniform_volume_linear_bound_closed": False,
            "analytic_infinite_dimensional_trotter_rate_closed": False,
            "operator_domain_embedding_closed": False,
            "actual_q3_thermodynamic_history_closed": False,
            "direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "source_volume_beta_uniformity_closed": False,
            "exhaustion_independence_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
        },
        "boundary": scope,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT ANALYTIC-TROTTER-DEFECT PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
