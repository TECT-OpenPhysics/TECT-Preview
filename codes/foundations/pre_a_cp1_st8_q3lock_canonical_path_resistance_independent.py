#!/usr/bin/env python3
"""Independent finite reconstruction for the R-407 path certificate.

The Hamiltonian, Gibbs states, histories, conditional rows, tree construction
and path loads are rebuilt here without importing the R-407 primary module.
Only the shared oscillator primitive is imported as a fixture source.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-canonical-path-resistance-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_canonical_path_resistance" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def model(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q_single, p_single = q3.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_sites = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_sites = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(fixture[key]))) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(str(fixture[key]))) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_sites, p_sites)]
    bonds: list[np.ndarray] = []
    for left in range(volume - 1):
        difference = q_sites[left] - q_sites[left + 1]
        difference2 = difference @ difference
        bonds.append(c * difference2 / 2.0 + lam * difference2 @ (q_sites[left] @ q_sites[left] + q_sites[left + 1] @ q_sites[left + 1]) / 4.0)
    zero = np.zeros_like(q_sites[0])
    return q_sites, hermitian(sum(onsite + bonds, zero)), onsite + bonds


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return hermitian((vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T)


def prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[tuple[int, np.ndarray]]:
    current = np.eye(terms[0].shape[0], dtype=complex)
    result = [(0, current.copy())]
    for position, index in enumerate(order, start=1):
        current = unitary(terms[index], sign * delta, hbar) @ current
        result.append((position, current.copy()))
    return result


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def coordinate_basis(dimension: int, volume: int) -> np.ndarray:
    q_single, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(hermitian(q_single))
    result = vectors
    for _ in range(volume - 1):
        result = np.kron(result, vectors)
    return result


def probabilities(state: np.ndarray, basis: np.ndarray, dimension: int, volume: int) -> tuple[np.ndarray, float]:
    diagonal = np.real(np.diag(basis.conj().T @ state @ basis))
    raw_minimum = float(np.min(diagonal))
    values = np.maximum(diagonal, 0.0)
    values /= float(np.sum(values))
    return values.reshape((dimension,) * volume), raw_minimum


def marginal(values: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    rest = [site for site in range(values.ndim) if site not in sites]
    moved = np.transpose(values, sites + rest)
    return moved.reshape(dimension ** len(sites), -1).sum(axis=1).reshape((dimension,) * len(sites))


def coordinate_data(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    q_single, p_single = q3.oscillator(dimension)
    levels, vectors = np.linalg.eigh(hermitian(q_single))
    return levels.real, hermitian(vectors.conj().T @ p_single @ vectors)


def intrinsic_graph(probabilities_row: np.ndarray, momentum: np.ndarray, chi: float) -> tuple[float, np.ndarray, np.ndarray]:
    pi = np.asarray(probabilities_row, dtype=float)
    p_matrix = np.asarray(momentum, dtype=complex)
    if pi.ndim != 1 or p_matrix.shape != (pi.size, pi.size) or np.any(pi <= 0.0) or not np.all(np.isfinite(pi)):
        raise AssertionError("invalid graph input")
    pi = pi / float(np.sum(pi))
    conductance = (pi[:, None] + pi[None, :]) * np.square(np.abs(p_matrix)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(pi)
    weighted = inverse[:, None] * laplacian * inverse[None, :]
    eigenvalues = np.linalg.eigvalsh((weighted + weighted.T) / 2.0)
    if eigenvalues.size < 2 or abs(float(eigenvalues[0])) > 1.0e-8 or float(eigenvalues[1]) <= 0.0:
        raise AssertionError("graph disconnected")
    return float(eigenvalues[1]), laplacian, conductance


def maximum_spanning_tree(conductance: np.ndarray, edge_floor: float) -> list[tuple[int, int]]:
    matrix = np.asarray(conductance, dtype=float)
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

    tree: list[tuple[int, int]] = []
    for _weight, left, right in candidates:
        a, b = find(left), find(right)
        if a == b:
            continue
        if rank[a] < rank[b]:
            a, b = b, a
        parent[b] = a
        if rank[a] == rank[b]:
            rank[a] += 1
        tree.append((left, right))
        if len(tree) == n - 1:
            break
    if len(tree) != n - 1:
        raise AssertionError("no spanning tree")
    return tree


def path_map(size: int, tree: list[tuple[int, int]]) -> dict[tuple[int, int], list[tuple[int, int]]]:
    adjacency: list[list[tuple[int, tuple[int, int]]]] = [[] for _ in range(size)]
    for left, right in tree:
        edge = (min(left, right), max(left, right))
        adjacency[left].append((right, edge))
        adjacency[right].append((left, edge))
    output: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for source in range(size):
        parent: dict[int, tuple[int, tuple[int, int]] | None] = {source: None}
        queue = [source]
        for current in queue:
            for neighbour, edge in adjacency[current]:
                if neighbour not in parent:
                    parent[neighbour] = (current, edge)
                    queue.append(neighbour)
        if len(parent) != size:
            raise AssertionError("disconnected tree")
        for target in range(source + 1, size):
            current = target
            path: list[tuple[int, int]] = []
            while current != source:
                predecessor = parent.get(current)
                if predecessor is None:
                    raise AssertionError("missing path")
                current, edge = predecessor
                path.append(edge)
            output[(source, target)] = path
    return output


def canonical_data(probabilities_row: np.ndarray, conductance: np.ndarray, edge_floor: float) -> dict[str, Any]:
    pi = np.asarray(probabilities_row, dtype=float)
    pi = pi / float(np.sum(pi))
    tree = maximum_spanning_tree(conductance, edge_floor)
    paths = path_map(pi.size, tree)
    loads = {(min(left, right), max(left, right)): 0.0 for left, right in tree}
    maximum_path_length = 0
    for (left, right), path in paths.items():
        length = len(path)
        maximum_path_length = max(maximum_path_length, length)
        for edge in path:
            loads[edge] += float(pi[left] * pi[right] * length)
    ratios = {edge: load / float(conductance[edge[0], edge[1]]) for edge, load in loads.items()}
    rho = max(ratios.values())
    if not math.isfinite(rho) or rho <= 0.0:
        raise AssertionError("invalid rho")
    return {
        "tree_edges": [[left, right] for left, right in tree],
        "tree_edge_count": len(tree),
        "max_path_length": maximum_path_length,
        "minimum_tree_conductance": min(float(conductance[left, right]) for left, right in tree),
        "maximum_tree_conductance": max(float(conductance[left, right]) for left, right in tree),
        "maximum_edge_load": max(loads.values()),
        "rho": rho,
        "canonical_bound": 1.0 / rho,
        "path_count": len(paths),
    }


def conditional_rows(reference: np.ndarray, sample: np.ndarray, order: list[int], dimension: int, floor: float):
    for radius in range(len(order)):
        p_prefix = marginal(reference, order[: radius + 1], dimension)
        q_prefix = marginal(sample, order[: radius + 1], dimension)
        if float(np.min(p_prefix)) <= floor:
            raise AssertionError("reference floor")
        likelihood = q_prefix / p_prefix
        parent = np.ones((1,), dtype=float) if radius == 0 else marginal(reference, order[:radius], dimension).reshape(-1)
        for mass, p_row, f_row in zip(parent, p_prefix.reshape(-1, dimension), likelihood.reshape(-1, dimension)):
            conditional = p_row / float(mass)
            conditional /= float(np.sum(conditional))
            if float(np.min(conditional)) <= 0.0 or not np.all(np.isfinite(f_row)):
                raise AssertionError("invalid conditional row")
            yield conditional, f_row


def variance(probabilities_row: np.ndarray, values: np.ndarray) -> float:
    pi = np.asarray(probabilities_row, dtype=float)
    pi = pi / float(np.sum(pi))
    centered = values - float(np.sum(pi * values))
    return max(0.0, float(np.sum(pi * centered * centered)))


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

    profiles: dict[str, dict[str, Any]] = {}
    bounds: list[float] = []
    gaps: list[float] = []
    residuals: list[float] = []
    rhos: list[float] = []
    conductances: list[float] = []
    probabilities_min: list[float] = []
    total_contexts = 0
    total_rows = 0
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = model(volume, dimension, fixture)
        basis = coordinate_basis(dimension, volume)
        _levels, momentum = coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        states = {beta: gibbs(hamiltonian, beta) for beta in betas}
        generator = q_ops[0]
        prefix_cache = {(name, sign): prefixes(terms, order, sign, delta, hbar) for name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms))))) ) for sign in history_signs}
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_bound": float("inf"), "maximum_bound": 0.0, "minimum_gap": float("inf"), "maximum_gap": 0.0, "minimum_rho": float("inf"), "maximum_rho": 0.0, "minimum_tree_conductance": float("inf"), "maximum_path_length": 0, "minimum_residual": float("inf"), "maximum_residual": 0.0, "minimum_probability": float("inf")}
        for beta in betas:
            reference, raw_reference = probabilities(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            for support in supports:
                for source_sign in source_signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = hermitian(source @ states[beta] @ source.conj().T)
                    for (_order_name, history_sign), cached_prefixes in prefix_cache.items():
                        for prefix_length, prefix in cached_prefixes:
                            for history_adjoint in adjoints:
                                state = hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else hermitian(prefix.conj().T @ seeded @ prefix)
                                sample, raw_sample = probabilities(state, basis, dimension, volume)
                                check(f"d={dimension} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                                for orientation in orientations:
                                    order_sites = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                    for conditional, likelihood in conditional_rows(reference, sample, order_sites, dimension, floor):
                                        gap, laplacian, conductance = intrinsic_graph(conditional, momentum, chi)
                                        data = canonical_data(conditional, conductance, edge_floor)
                                        energy = max(0.0, float(np.real(likelihood @ laplacian @ likelihood)))
                                        var = variance(conditional, likelihood)
                                        residual = energy - data["canonical_bound"] * var
                                        check("path bound residual", math.isfinite(residual) and residual >= -tolerance, residual, f">=-{tolerance}", "canonical path")
                                        bounds.append(data["canonical_bound"])
                                        gaps.append(gap)
                                        residuals.append(residual)
                                        rhos.append(data["rho"])
                                        conductances.append(data["minimum_tree_conductance"])
                                        probabilities_min.append(float(np.min(conditional)))
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
    check("canonical bounds positive", all(math.isfinite(value) and value > 0.0 for value in bounds), [min(bounds), max(bounds)], ">0 finite", "canonical path")
    check("canonical residuals nonnegative", all(math.isfinite(value) and value >= -tolerance for value in residuals), [min(residuals), max(residuals)], f">=-{tolerance}", "canonical path")
    check("tree edge floors", all(value > edge_floor for value in conductances), [min(conductances), edge_floor], ">edge floor", "canonical path")
    check("bounds below exact gaps", all(bound <= gap + tolerance for bound, gap in zip(bounds, gaps)), [max(bounds), min(gaps)], "bound <= exact gap", "comparison")
    derived = {
        "system_count": len(pairs),
        "context_count": total_contexts,
        "comparison_row_count": total_rows,
        "minimum_canonical_bound": min(bounds),
        "maximum_canonical_bound": max(bounds),
        "minimum_intrinsic_gap": min(gaps),
        "maximum_intrinsic_gap": max(gaps),
        "minimum_rho": min(rhos),
        "maximum_rho": max(rhos),
        "minimum_tree_conductance": min(conductances),
        "minimum_conditional_probability": min(probabilities_min),
        "minimum_canonical_residual": min(residuals),
        "maximum_canonical_residual": max(residuals),
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
    payload = {"schema": "tect/pre-a-r407-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-407", "exploration_id": "EXP-001252", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-407 INDEPENDENT PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} bound=[{min(bounds):.6g},{max(bounds):.6g}] rho=[{min(rhos):.6g},{max(rhos):.6g}]")
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
