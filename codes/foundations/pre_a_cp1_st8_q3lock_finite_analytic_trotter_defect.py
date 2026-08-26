#!/usr/bin/env python3
"""Primary finite analytic commutator-sum Lie--Trotter audit.

For the declared finite Q3 oscillator graphs this script evaluates the exact
local commutator sum

    C_V = sum_{j<k} ||[H_j,H_k]||

and checks the bounded-matrix estimates

    ||S_delta^N - exp(-i sign*t H)|| <= t^2 C_V/(2 N)

and, for each multiplier history M,

    ||V_split(M)-V_exact(M)||
      <= delta^3 C_V N(N-1)||M||/2.

The estimates are finite-dimensional consequences of a unitary Duhamel
interpolation and unitary telescoping.  No volume-uniform or unbounded-domain
claim is made here.
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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def eigensystem(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(hermitian(matrix))


def exponential(values: np.ndarray, vectors: np.ndarray, time: float) -> np.ndarray:
    return (vectors * np.exp(-1j * time * values)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


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
            candidate = distances[current] + 1
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
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
    weighted += sum((((weights[left] + weights[right]) / 2.0) * bond for (left, right), bond in bonds.items()), zero)
    base = hermitian(weighted + np.eye(weighted.shape[0], dtype=complex))
    return q_ops, q3.positive_weight(base), weights


def term_specs(volume: int) -> list[dict[str, Any]]:
    specs = [{"kind": "onsite", "support": [site]} for site in range(volume)]
    specs.extend({"kind": "bond", "support": [left, right]} for left, right in q3.graph_edges(volume))
    return specs


def split_terms(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[dict[str, Any]], np.ndarray]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [
        p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0
        for q, p in zip(q_ops, p_ops)
    ]
    bonds = [hermitian(q3.bond_term(q_ops[left], q_ops[right], fixture)) for left, right in q3.graph_edges(volume)]
    terms = onsite + bonds
    zero = np.zeros_like(q_ops[0])
    full = hermitian(sum(terms, zero))
    return terms, term_specs(volume), full


def local_support_term(spec: dict[str, Any], union: list[int], n: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = {site: q3.embed(q_single, index, len(union), identity) for index, site in enumerate(union)}
    p_ops = {site: q3.embed(p_single, index, len(union), identity) for index, site in enumerate(union)}
    if spec["kind"] == "onsite":
        site = int(spec["support"][0])
        q, p = q_ops[site], p_ops[site]
        chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
        return hermitian(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0)
    left, right = (int(value) for value in spec["support"])
    return hermitian(q3.bond_term(q_ops[left], q_ops[right], fixture))


def local_commutator_norm(spec_left: dict[str, Any], spec_right: dict[str, Any], n: int, fixture: dict[str, Any]) -> tuple[float, bool]:
    support_left = set(int(value) for value in spec_left["support"])
    support_right = set(int(value) for value in spec_right["support"])
    if support_left.isdisjoint(support_right):
        return 0.0, True
    union = sorted(support_left | support_right)
    left = local_support_term(spec_left, union, n, fixture)
    right = local_support_term(spec_right, union, n, fixture)
    return operator_norm(commutator(left, right)), False


def commutator_sum(
    terms: list[np.ndarray],
    specs: list[dict[str, Any]],
    volume: int,
    n: int,
    fixture: dict[str, Any],
    localization_tolerance: float,
) -> tuple[float, list[dict[str, Any]], float]:
    total = 0.0
    details: list[dict[str, Any]] = []
    first_overlap_residual = 0.0
    checked_localization = False
    for left_index in range(len(specs)):
        for right_index in range(left_index + 1, len(specs)):
            local_norm, disjoint = local_commutator_norm(specs[left_index], specs[right_index], n, fixture)
            if disjoint:
                details.append({"left": left_index, "right": right_index, "disjoint": True, "norm": 0.0})
                continue
            total += local_norm
            full_norm = operator_norm(commutator(terms[left_index], terms[right_index]))
            residual = abs(full_norm - local_norm)
            if not checked_localization:
                first_overlap_residual = residual
                checked_localization = True
            if residual > localization_tolerance:
                raise AssertionError(
                    f"V={volume} pair=({left_index},{right_index}) local tensor norm residual {residual} > {localization_tolerance}"
                )
            details.append({"left": left_index, "right": right_index, "disjoint": False, "norm": local_norm, "full_norm": full_norm, "residual": residual})
    return total, details, first_overlap_residual


def ordered_step(term_eigensystems: list[tuple[np.ndarray, np.ndarray]], order: list[int], sign: int, delta: float) -> np.ndarray:
    result = np.eye(term_eigensystems[0][1].shape[0], dtype=complex)
    for index in order:
        values, vectors = term_eigensystems[index]
        result = exponential(values, vectors, sign * delta) @ result
    return result


def discrete_history(matrix: np.ndarray, step: np.ndarray, delta: float, count: int) -> np.ndarray:
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
    fixture_path = REPO / source["source_fixture"]["manifest"]
    fixture_manifest = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture = fixture_manifest["source_fixture"]
    analytic = manifest["analytic_fixture"]
    finite = manifest["finite_fixture"]
    tolerance = float(finite["bound_slack_tolerance"])
    decomposition_tolerance = float(finite["decomposition_tolerance"])
    localization_tolerance = float(finite["localization_tolerance"])
    unitarity_tolerance = float(finite["unitarity_tolerance"])
    horizon = float(Fraction(analytic["horizon"]))
    counts = [int(value) for value in analytic["step_counts"]]
    volumes = [int(value) for value in manifest["source_fixture"]["volume_values"]]
    n = int(manifest["source_fixture"]["oscillator_dimension"])
    pairs = {int(key): [[int(site) for site in pair] for pair in value] for key, value in manifest["source_fixture"]["source_pairs"].items()}
    probes = {int(key): [int(site) for site in value] for key, value in manifest["source_fixture"]["probe_sites"].items()}
    ratio = float(Fraction(analytic["weight_ratio_per_edge"]))
    power = float(Fraction(analytic["multiplier_power"]))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check(
        "identity",
        manifest["exploration_id"] == "EXP-001162" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False,
        [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]],
        "EXP-001162/T-054/false",
        "provenance",
    )
    check("parent authority", parent["exploration_id"] == "EXP-001161" and parent["task_id"] == "T-054", [parent["exploration_id"], parent["task_id"]], "EXP-001161/T-054", "provenance")
    check("analytic fixture", counts == [3, 6, 12] and abs(horizon - 1.0 / 3.0) <= tolerance, [counts, horizon], "3,6,12 and horizon 1/3", "fixture")
    check("order/sign grid", analytic["orders"] == ["onsite_then_lexicographic_bonds", "reverse_term_order"] and analytic["time_signs"] == [-1, 1], analytic, "two orders and two signs", "fixture")
    scope = manifest["scope"]
    check(
        "scope firewall",
        scope["finite_local_commutator_sum_closed"] and scope["finite_analytic_unitary_defect_closed"] and scope["finite_two_orientation_history_bound_closed"] and not scope["volume_uniform_trotter_bound_closed"] and not scope["pre_a_closed"],
        scope,
        "finite analytic bound only",
        "scope",
    )

    rows: list[dict[str, Any]] = []
    volume_summaries: list[dict[str, Any]] = []
    max_unitary_bound = 0.0
    max_history_bound = 0.0
    minimum_unitary_slack = float("inf")
    minimum_history_slack = float("inf")
    for volume in volumes:
        terms, specs, hamiltonian = split_terms(volume, n, fixture)
        _, reference, _, _ = q3.build_volume(volume, n, fixture)
        decomposition_error = operator_norm(hamiltonian - reference)
        check(f"V={volume} full decomposition", decomposition_error <= decomposition_tolerance, decomposition_error, f"<={decomposition_tolerance}", "decomposition")
        c_sum, pair_details, localization_residual = commutator_sum(terms, specs, volume, n, fixture, localization_tolerance)
        check(f"V={volume} local commutator sum finite", np.isfinite(c_sum) and c_sum > float(finite["commutator_floor"]), c_sum, f">{finite['commutator_floor']}", "commutator")
        check(f"V={volume} tensor localization", localization_residual <= localization_tolerance, localization_residual, f"<={localization_tolerance}", "commutator")
        overlap_count = sum(1 for item in pair_details if not item["disjoint"])
        term_norm_max = max(operator_norm(term) for term in terms)
        coarse_volume_bound = 2.0 * overlap_count * term_norm_max * term_norm_max
        check(f"V={volume} fixed-cutoff volume envelope", c_sum <= coarse_volume_bound + tolerance * (1.0 + coarse_volume_bound), [c_sum, coarse_volume_bound, overlap_count, term_norm_max], "C_V<=2*overlap_pairs*K_n^2", "fixed cutoff")
        h_values, h_vectors = eigensystem(hamiltonian)
        term_eigensystems = [eigensystem(term) for term in terms]
        volume_row_count = 0
        volume_max_error = 0.0
        volume_max_bound = 0.0
        volume_max_history_error = 0.0
        volume_max_history_bound = 0.0
        for pair in pairs[volume]:
            distances = graph_distance(volume, pair)
            q_ops, energy, weights = weighted_energy(volume, n, fixture, distances, ratio)
            energy_minimum = float(np.min(np.linalg.eigvalsh(energy)))
            check(f"V={volume} pair={pair} positive energy", energy_minimum >= float(finite["positive_energy_floor"]) - tolerance, energy_minimum, f">={finite['positive_energy_floor']}", "energy")
            inverse = q3.spectral_power(energy, -power)
            site = probes[volume][0]
            cubic = q_ops[site] @ q_ops[site] @ q_ops[site]
            factor = float(weights[site] ** power)
            right = factor * (cubic @ inverse)
            left = factor * (inverse @ cubic)
            comm = right - left
            multipliers = {"right": right, "left": left, "commutator": comm}
            multiplier_norms = {name: operator_norm(value) for name, value in multipliers.items()}
            check(f"V={volume} pair={pair} multiplier noncommutation", multiplier_norms["commutator"] > float(finite["commutator_floor"]), multiplier_norms["commutator"], f">{finite['commutator_floor']}", "orientation")
            for order_name, order in ((analytic["orders"][0], list(range(len(terms)))), (analytic["orders"][1], list(reversed(range(len(terms)))))):
                for sign in analytic["time_signs"]:
                    exact_target = exponential(h_values, h_vectors, int(sign) * horizon)
                    exact_errors: list[float] = []
                    for count in counts:
                        delta = horizon / count
                        step = ordered_step(term_eigensystems, order, int(sign), delta)
                        identity = np.eye(step.shape[0], dtype=complex)
                        unitary_error = operator_norm(step.conj().T @ step - identity)
                        split_target = np.linalg.matrix_power(step, count)
                        final_error = operator_norm(split_target - exact_target)
                        exact_increment = exponential(h_values, h_vectors, int(sign) * delta)
                        unitary_bound = horizon * horizon * c_sum / (2.0 * count)
                        unitary_slack = unitary_bound - final_error
                        check(f"V={volume} {order_name} sign={sign} N={count} unitary", unitary_error <= unitarity_tolerance, unitary_error, f"<={unitarity_tolerance}", "split")
                        check(f"V={volume} {order_name} sign={sign} N={count} analytic unitary bound", unitary_slack >= -tolerance * (1.0 + unitary_bound), [final_error, unitary_bound, unitary_slack], "final<=t^2*C/(2N)", "analytic Trotter")
                        for orientation, multiplier in multipliers.items():
                            split_history = discrete_history(multiplier, step, delta, count)
                            exact_history = discrete_history(multiplier, exact_increment, delta, count)
                            history_error = operator_norm(split_history - exact_history)
                            history_bound = delta**3 * c_sum * count * (count - 1) * multiplier_norms[orientation] / 2.0
                            history_slack = history_bound - history_error
                            check(f"V={volume} {order_name} sign={sign} N={count} {orientation} history bound", history_slack >= -tolerance * (1.0 + history_bound), [history_error, history_bound, history_slack], "history<=delta^3*C*N*(N-1)||M||/2", "analytic history")
                            rows.append({"volume": volume, "source_pair": pair, "probe_site": site, "order": order_name, "time_sign": int(sign), "step_count": count, "orientation": orientation, "delta": delta, "commutator_sum": c_sum, "multiplier_norm": multiplier_norms[orientation], "final_unitary_error": final_error, "unitary_bound": unitary_bound, "unitary_slack": unitary_slack, "history_error": history_error, "history_bound": history_bound, "history_slack": history_slack, "unitary_step_error": unitary_error})
                            volume_row_count += 1
                            volume_max_history_error = max(volume_max_history_error, history_error)
                            volume_max_history_bound = max(volume_max_history_bound, history_bound)
                            max_history_bound = max(max_history_bound, history_bound)
                            minimum_history_slack = min(minimum_history_slack, history_slack)
                        exact_errors.append(final_error)
                        volume_max_error = max(volume_max_error, final_error)
                        volume_max_bound = max(volume_max_bound, unitary_bound)
                        max_unitary_bound = max(max_unitary_bound, unitary_bound)
                        minimum_unitary_slack = min(minimum_unitary_slack, unitary_slack)
                    check(f"V={volume} {order_name} sign={sign} bound refinement", all(counts[index] < counts[index + 1] for index in range(len(counts) - 1)) and all((horizon * horizon * c_sum / (2.0 * counts[index])) >= (horizon * horizon * c_sum / (2.0 * counts[index + 1])) for index in range(len(counts) - 1)), counts, "analytic bound decreases with N", "analytic Trotter")
            check(f"V={volume} pair={pair} multiplier norms finite", all(np.isfinite(value) for value in multiplier_norms.values()), multiplier_norms, "finite", "orientation")
        expected_volume_rows = len(pairs[volume]) * len(analytic["orders"]) * len(analytic["time_signs"]) * len(counts) * 3
        check(f"V={volume} row coverage", volume_row_count == expected_volume_rows, volume_row_count, expected_volume_rows, "coverage")
        volume_summaries.append({"volume": volume, "term_count": len(terms), "dimension": n**volume, "commutator_sum": c_sum, "commutator_sum_per_site": c_sum / volume, "pair_details": pair_details, "overlap_pair_count": overlap_count, "term_norm_max": term_norm_max, "coarse_volume_commutator_bound": coarse_volume_bound, "max_final_unitary_error": volume_max_error, "max_unitary_bound": volume_max_bound, "max_history_error": volume_max_history_error, "max_history_bound": volume_max_history_bound, "row_count": volume_row_count})

    check("volume sequence", [item["volume"] for item in volume_summaries] == volumes, [item["volume"] for item in volume_summaries], volumes, "volume")
    check("all analytic slacks finite", np.isfinite(minimum_unitary_slack) and np.isfinite(minimum_history_slack), [minimum_unitary_slack, minimum_history_slack], "finite", "summary")
    check("analytic finite flags", scope["finite_local_commutator_sum_closed"] and scope["finite_fixed_cutoff_volume_linear_envelope_closed"] and scope["finite_analytic_unitary_defect_closed"] and scope["finite_two_orientation_history_bound_closed"] and scope["finite_bound_both_orders_and_signs_closed"], scope, "finite flags true", "summary")
    check("QFT firewall", not scope["volume_uniform_trotter_bound_closed"] and not scope["cutoff_uniform_volume_linear_bound_closed"] and not scope["analytic_infinite_dimensional_trotter_rate_closed"] and not scope["operator_domain_embedding_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "uniform/domain/QFT gates remain open", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ANALYTIC-TROTTER-DEFECT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "source_manifest_sha256": normalized_sha256(source_path),
            "parent_manifest_sha256": normalized_sha256(parent_path),
            "row_count": len(rows),
            "volume_summaries": volume_summaries,
            "commutator_sum_by_volume": {str(item["volume"]): item["commutator_sum"] for item in volume_summaries},
            "commutator_sum_per_site_by_volume": {str(item["volume"]): item["commutator_sum_per_site"] for item in volume_summaries},
            "max_unitary_bound": max_unitary_bound,
            "max_history_bound": max_history_bound,
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
    print(f"PRIMARY ANALYTIC-TROTTER-DEFECT PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
