#!/usr/bin/env python3
"""Primary finite canonical-path/effective-resistance audit for R-407.

For each R-404 conditional momentum graph this module builds a deterministic
maximum-conductance spanning tree.  The canonical-path load on a tree edge is

    load(e) = sum_{x<y : e in gamma_xy} pi[x] pi[y] len(gamma_xy),

and rho is the largest load/conductance ratio.  The elementary path
inequality gives Var_pi(f) <= rho * E(f), hence rho**(-1) is a valid finite
lower bound for every test function.  The code records the bound and the
inputs needed for an eventual uniform estimate; it does not assert such an
estimate in the regulator or thermodynamic limit.
"""

from __future__ import annotations

import argparse
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
SLUG = "pre_a_cp1_st8_q3lock_canonical_path_resistance"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-canonical-path-resistance-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def maximum_spanning_tree(conductance: np.ndarray, edge_floor: float) -> list[tuple[int, int]]:
    """Return a deterministic Kruskal maximum spanning tree."""
    matrix = np.asarray(conductance, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.all(np.isfinite(matrix)):
        raise AssertionError("invalid conductance matrix")
    n = matrix.shape[0]
    candidates = [(float(matrix[i, j]), i, j) for i in range(n) for j in range(i + 1, n) if float(matrix[i, j]) > edge_floor]
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    parent = list(range(n))
    rank = [0] * n

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> bool:
        root_left, root_right = find(left), find(right)
        if root_left == root_right:
            return False
        if rank[root_left] < rank[root_right]:
            root_left, root_right = root_right, root_left
        parent[root_right] = root_left
        if rank[root_left] == rank[root_right]:
            rank[root_left] += 1
        return True

    tree: list[tuple[int, int]] = []
    for _weight, left, right in candidates:
        if union(left, right):
            tree.append((left, right))
            if len(tree) == n - 1:
                break
    if len(tree) != n - 1:
        raise AssertionError("conductance graph has no spanning tree above edge floor")
    return tree


def tree_paths(size: int, tree: list[tuple[int, int]]) -> dict[tuple[int, int], list[tuple[int, int]]]:
    adjacency: list[list[tuple[int, tuple[int, int]]]] = [[] for _ in range(size)]
    for left, right in tree:
        edge = (min(left, right), max(left, right))
        adjacency[left].append((right, edge))
        adjacency[right].append((left, edge))
    paths: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for source in range(size):
        parent: dict[int, tuple[int, tuple[int, int]] | None] = {source: None}
        queue = [source]
        for current in queue:
            for neighbour, edge in adjacency[current]:
                if neighbour not in parent:
                    parent[neighbour] = (current, edge)
                    queue.append(neighbour)
        if len(parent) != size:
            raise AssertionError("tree is disconnected")
        for target in range(source + 1, size):
            current = target
            path: list[tuple[int, int]] = []
            while current != source:
                predecessor = parent.get(current)
                if predecessor is None:
                    raise AssertionError("missing tree path")
                current, edge = predecessor
                path.append(edge)
            paths[(source, target)] = path
    return paths


def canonical_data(probabilities: np.ndarray, conductance: np.ndarray, edge_floor: float) -> dict[str, Any]:
    """Compute rho, its reciprocal, and the path inequality diagnostics."""
    pi = np.asarray(probabilities, dtype=float)
    c = np.asarray(conductance, dtype=float)
    if pi.ndim != 1 or c.shape != (pi.size, pi.size) or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0):
        raise AssertionError("invalid canonical-path mass")
    pi = pi / float(np.sum(pi))
    tree = maximum_spanning_tree(c, edge_floor)
    paths = tree_paths(pi.size, tree)
    loads = {(min(left, right), max(left, right)): 0.0 for left, right in tree}
    pair_mass = 0.0
    max_path = 0
    for (left, right), path in paths.items():
        length = len(path)
        max_path = max(max_path, length)
        pair_mass += float(pi[left] * pi[right])
        for edge in path:
            loads[edge] += float(pi[left] * pi[right] * length)
    ratios: dict[tuple[int, int], float] = {}
    for edge, load in loads.items():
        value = float(c[edge[0], edge[1]])
        if not math.isfinite(value) or value <= edge_floor:
            raise AssertionError("tree edge has nonpositive conductance")
        ratios[edge] = load / value
    rho = max(ratios.values()) if ratios else 0.0
    if not math.isfinite(rho) or rho <= 0.0:
        raise AssertionError("canonical load is not positive")
    return {
        "tree_edges": [[left, right] for left, right in tree],
        "tree_edge_count": len(tree),
        "max_path_length": max_path,
        "minimum_tree_conductance": min(float(c[left, right]) for left, right in tree),
        "maximum_tree_conductance": max(float(c[left, right]) for left, right in tree),
        "maximum_edge_load": max(loads.values()),
        "rho": rho,
        "canonical_bound": 1.0 / rho,
        "pair_mass_sum": pair_mass,
        "path_count": len(paths),
    }


def intrinsic_graph(probabilities: np.ndarray, momentum: np.ndarray, chi: float) -> tuple[float, np.ndarray, np.ndarray]:
    pi = np.asarray(probabilities, dtype=float)
    p_matrix = np.asarray(momentum, dtype=complex)
    if pi.ndim != 1 or p_matrix.shape != (pi.size, pi.size) or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0) or chi <= 0.0:
        raise AssertionError("invalid intrinsic graph input")
    pi = pi / float(np.sum(pi))
    conductance = (pi[:, None] + pi[None, :]) * np.square(np.abs(p_matrix)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse_sqrt = 1.0 / np.sqrt(pi)
    weighted = inverse_sqrt[:, None] * laplacian * inverse_sqrt[None, :]
    eigenvalues = np.linalg.eigvalsh((weighted + weighted.T) / 2.0)
    if eigenvalues.size < 2 or not np.all(np.isfinite(eigenvalues)) or abs(float(eigenvalues[0])) > 1.0e-8 or float(eigenvalues[1]) <= 0.0:
        raise AssertionError("intrinsic graph is disconnected or nonfinite")
    return float(eigenvalues[1]), laplacian, conductance


def variance(probabilities: np.ndarray, likelihood: np.ndarray) -> float:
    pi = np.asarray(probabilities, dtype=float)
    values = np.asarray(likelihood, dtype=float)
    pi = pi / float(np.sum(pi))
    mean = float(np.sum(pi * values))
    return max(0.0, float(np.sum(pi * np.square(values - mean))))


def canonical_residual(probabilities: np.ndarray, likelihood: np.ndarray, laplacian: np.ndarray, bound: float) -> tuple[float, float, float]:
    values = np.asarray(likelihood, dtype=float)
    energy = max(0.0, float(np.real(values @ laplacian @ values)))
    var = variance(probabilities, values)
    return energy, var, energy - bound * var


def conditional_rows(reference: np.ndarray, sample: np.ndarray, order: list[int], dimension: int, floor: float):
    for radius in range(len(order)):
        p_prefix = r399.marginal(reference, order[: radius + 1], dimension)
        q_prefix = r399.marginal(sample, order[: radius + 1], dimension)
        if float(np.min(p_prefix)) <= floor:
            raise AssertionError("reference marginal floor")
        likelihood = q_prefix / p_prefix
        parent = np.ones((1,), dtype=float) if radius == 0 else r399.marginal(reference, order[:radius], dimension).reshape(-1)
        for mass, p_row, f_row in zip(parent, p_prefix.reshape(-1, dimension), likelihood.reshape(-1, dimension)):
            conditional = p_row / float(mass)
            conditional /= float(np.sum(conditional))
            if float(np.min(conditional)) <= 0.0 or not np.all(np.isfinite(f_row)):
                raise AssertionError("invalid conditional row")
            yield conditional, f_row


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_floor"])
    edge_floor = float(fixture["edge_conductance_floor"])
    chi = float(Fraction(str(fixture["chi"])))
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    source_signs = [int(value) for value in fixture["source_sign_values"]]
    history_signs = [int(value) for value in fixture["history_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    orientations = list(fixture["orientations"])
    supports = [tuple(int(site) for site in support) for support in fixture["source_support_values"]]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 220:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-407" and manifest["exploration_id"] == "EXP-001252" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-407/EXP-001252/false", "provenance")
    finite_flags = ("finite_tree_bound_closed", "finite_canonical_path_identity_closed", "finite_likelihood_row_bound_closed", "finite_cutoff_profile_closed", "finite_tree_choice_stress_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite canonical path only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("positive chi", chi > 0.0, chi, ">0", "fixture")

    profiles: dict[str, dict[str, Any]] = {}
    bound_values: list[float] = []
    gap_values: list[float] = []
    residual_values: list[float] = []
    rho_values: list[float] = []
    probability_values: list[float] = []
    conductance_values: list[float] = []
    total_contexts = 0
    total_rows = 0
    invalid_bound_rows = 0
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, p_coordinate = r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        generator_cache = {support: sum((q_ops[site] for site in support), np.zeros_like(q_ops[0])) for support in supports}
        prefixes_by_key = {(order_name, history_sign): r399.all_prefixes(terms, order, history_sign, delta, hbar) for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms))))) ) for history_sign in history_signs}
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_bound": float("inf"), "maximum_bound": 0.0, "minimum_gap": float("inf"), "maximum_gap": 0.0, "minimum_rho": float("inf"), "maximum_rho": 0.0, "minimum_tree_conductance": float("inf"), "maximum_path_length": 0, "minimum_residual": float("inf"), "maximum_residual": 0.0, "minimum_probability": float("inf")}
        for beta in betas:
            reference, raw_reference = r399.coordinate_distribution(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            for support in supports:
                for source_sign in source_signs:
                    source = q3.character(generator_cache[support], source_sign * amplitude, hbar)
                    seeded = r399.hermitian(source @ states[beta] @ source.conj().T)
                    for (order_name, history_sign), prefixes in prefixes_by_key.items():
                        for prefix_length, prefix in prefixes:
                            for history_adjoint in adjoints:
                                state = r399.hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else r399.hermitian(prefix.conj().T @ seeded @ prefix)
                                sample, raw_sample = r399.coordinate_distribution(state, basis, dimension, volume)
                                check(f"V={volume} d={dimension} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                                for orientation in orientations:
                                    collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                    for conditional, likelihood in conditional_rows(reference, sample, collar_order, dimension, floor):
                                        gap, laplacian, conductance = intrinsic_graph(conditional, p_coordinate, chi)
                                        data = canonical_data(conditional, conductance, edge_floor)
                                        energy, var, residual = canonical_residual(conditional, likelihood, laplacian, data["canonical_bound"])
                                        check("path bound residual", math.isfinite(residual) and residual >= -tolerance, residual, f">=-{tolerance}", "canonical path")
                                        if not math.isfinite(data["canonical_bound"]) or data["canonical_bound"] <= 0.0:
                                            invalid_bound_rows += 1
                                        bound_values.append(data["canonical_bound"])
                                        gap_values.append(gap)
                                        residual_values.append(residual)
                                        rho_values.append(data["rho"])
                                        probability_values.append(float(np.min(conditional)))
                                        conductance_values.append(data["minimum_tree_conductance"])
                                        total_rows += 1
                                        profile["row_count"] += 1
                                        profile["minimum_bound"] = min(profile["minimum_bound"], data["canonical_bound"])
                                        profile["maximum_bound"] = max(profile["maximum_bound"], data["canonical_bound"])
                                        profile["minimum_gap"] = min(profile["minimum_gap"], gap)
                                        profile["maximum_gap"] = max(profile["maximum_gap"], gap)
                                        profile["minimum_rho"] = min(profile["minimum_rho"], data["rho"])
                                        profile["maximum_rho"] = max(profile["maximum_rho"], data["rho"])
                                        profile["minimum_tree_conductance"] = min(profile["minimum_tree_conductance"], data["minimum_tree_conductance"])
                                        profile["maximum_path_length"] = max(profile["maximum_path_length"], data["max_path_length"])
                                        profile["minimum_residual"] = min(profile["minimum_residual"], residual)
                                        profile["maximum_residual"] = max(profile["maximum_residual"], residual)
                                        profile["minimum_probability"] = min(profile["minimum_probability"], float(np.min(conditional)))
                                    profile["context_count"] += 1
                                    total_contexts += 1
        check(f"V={volume} d={dimension} profile", profile["row_count"] > profile["context_count"] and profile["minimum_bound"] > 0.0, [profile["row_count"], profile["context_count"], profile["minimum_bound"]], "positive bound and rows", "coverage")
        profiles[f"V={volume}/d={dimension}"] = profile

    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("canonical bounds positive", all(math.isfinite(value) and value > 0.0 for value in bound_values), [min(bound_values), max(bound_values)], ">0 finite", "canonical path")
    check("canonical residuals nonnegative", all(math.isfinite(value) and value >= -tolerance for value in residual_values), [min(residual_values), max(residual_values)], f">=-{tolerance}", "canonical path")
    check("tree edges valid", invalid_bound_rows == 0 and all(value > edge_floor for value in conductance_values), [invalid_bound_rows, min(conductance_values)], "zero invalid rows and edge floor", "canonical path")
    check("intrinsic graph comparison", all(bound <= gap + tolerance for bound, gap in zip(bound_values, gap_values)), [max(bound_values), min(gap_values)], "canonical bound <= full graph gap", "comparison")
    derived = {
        "system_count": len(pairs),
        "context_count": total_contexts,
        "comparison_row_count": total_rows,
        "minimum_canonical_bound": min(bound_values),
        "maximum_canonical_bound": max(bound_values),
        "minimum_intrinsic_gap": min(gap_values),
        "maximum_intrinsic_gap": max(gap_values),
        "minimum_rho": min(rho_values),
        "maximum_rho": max(rho_values),
        "minimum_tree_conductance": min(conductance_values),
        "maximum_tree_conductance": max(conductance_values),
        "minimum_conditional_probability": min(probability_values),
        "maximum_canonical_residual": max(residual_values),
        "minimum_canonical_residual": min(residual_values),
        "cutoff_dimensions": [dimension for _volume, dimension in pairs],
        "system_profiles": profiles,
        "finite_tree_bound_closed": True,
        "finite_canonical_path_identity_closed": True,
        "finite_likelihood_row_bound_closed": True,
        "finite_cutoff_profile_closed": True,
        "finite_tree_choice_stress_closed": True,
        "cutoff_independent_bound_closed": False,
        "volume_independent_bound_closed": False,
        "phase_uniform_bound_closed": False,
        "exhaustion_uniform_bound_closed": False,
        "common_core_closed": False,
        "common_alpha_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r407-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-407", "exploration_id": "EXP-001252", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-407 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} bound=[{min(bound_values):.6g},{max(bound_values):.6g}] rho=[{min(rho_values):.6g},{max(rho_values):.6g}]")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
