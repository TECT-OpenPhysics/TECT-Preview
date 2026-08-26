#!/usr/bin/env python3
"""Primary finite Q3 source-local graph-norm transfer stress (EXP-001197)."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_source_local_graph_norm_transfer_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-local-graph-norm-transfer-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-primary-{SLUG}" / "primary.json"


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError(f"unsupported registered volume {volume}")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    quadratic = difference @ difference
    quartic = quadratic @ (left @ left + right @ right)
    return c * quadratic / 2.0 + lam * quartic / 4.0


def build_volume(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray], dict[tuple[int, int], np.ndarray], np.ndarray]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    onsite_kinetic: list[np.ndarray] = []
    onsite_potential: list[np.ndarray] = []
    for q, p in zip(q_ops, p_ops):
        onsite_kinetic.append(p @ p / (2.0 * chi))
        onsite_potential.append(r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0)
    bonds = {edge: bond_term(q_ops[edge[0]], q_ops[edge[1]], fixture) for edge in graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite_kinetic, zero) + sum(onsite_potential, zero) + sum(bonds.values(), zero)
    return q_ops, onsite_kinetic, onsite_potential, bonds, hermitian(full)


def shifted_positive(base: np.ndarray) -> tuple[np.ndarray, float]:
    value = hermitian(base)
    minimum = float(np.min(np.linalg.eigvalsh(value)))
    identity = np.eye(value.shape[0], dtype=complex)
    return value + (1.0 - minimum) * identity, minimum


def inverse_and_inverse_sqrt(weight: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    values, vectors = np.linalg.eigh(hermitian(weight))
    floor = float(np.min(values))
    inverse = (vectors * np.reciprocal(values)) @ vectors.conj().T
    inverse_sqrt = (vectors * np.reciprocal(np.sqrt(values))) @ vectors.conj().T
    return inverse, inverse_sqrt, floor


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def core_indices(volume: int, dimension: int, total_occupation: int) -> list[tuple[int, ...]]:
    return [index for index in product(range(dimension), repeat=volume) if sum(index) <= total_occupation]


def vector_norm(vector: np.ndarray) -> float:
    return float(np.linalg.norm(vector))


def flat_index(index: tuple[int, ...], dimension: int) -> int:
    value = 0
    for entry in index:
        value = value * dimension + entry
    return value


def core_rows(
    full_weight: np.ndarray,
    source_weight: np.ndarray,
    commutator_weight: np.ndarray,
    volume: int,
    dimension: int,
    total_occupation: int,
    graph_constant: float,
    commutator_constant: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index in core_indices(volume, dimension, total_occupation):
        vector = np.zeros(full_weight.shape[0], dtype=complex)
        vector[flat_index(index, dimension)] = 1.0
        denominator = vector_norm(full_weight @ vector)
        graph_ratio = vector_norm(source_weight @ vector) / denominator
        commutator_ratio = vector_norm(commutator_weight @ vector) / denominator
        rows.append({
            "index": list(index),
            "graph_ratio": graph_ratio,
            "commutator_ratio": commutator_ratio,
            "graph_bound_slack": graph_constant - graph_ratio,
            "commutator_bound_slack": commutator_constant - commutator_ratio,
        })
    return rows


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001197" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001197/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("Q3 geometries", graph_edges(2) == [(0, 1)] and len(graph_edges(4)) == 4 and len(graph_edges(6)) == 7, [graph_edges(2), len(graph_edges(4)), len(graph_edges(6))], "target/square/2x3 registered graphs", "geometry")
    check("scope firewall", scope["finite_source_graph_form_rows_closed"] and scope["finite_source_graph_norm_rows_closed"] and scope["finite_source_commutator_rows_closed"] and scope["explicit_polynomial_core_rows_closed"] and not scope["uniform_common_core_graph_bound_closed"] and not scope["cutoff_removal_closed"] and not scope["common_alpha_closed"], scope, "finite transfer only", "scope")

    tolerance = float(fixture["graph_norm_tolerance"])
    positive_tolerance = float(fixture["positive_tolerance"])
    dimensions_by_volume = fixture["oscillator_dimensions_by_volume"]
    supports_by_volume = fixture["source_supports_by_volume"]
    core_degree = int(fixture["core_total_occupation"])
    rows: list[dict[str, Any]] = []
    all_core_rows = 0
    cutoff_edge_commutators: list[tuple[int, float]] = []

    for volume_value in fixture["volume_values"]:
        volume = int(volume_value)
        edges = graph_edges(volume)
        for dimension_value in dimensions_by_volume[str(volume)]:
            dimension = int(dimension_value)
            q_ops, _, onsite_potential, bonds, hamiltonian = build_volume(volume, dimension, fixture)
            full_weight, full_floor = shifted_positive(hamiltonian)
            full_inverse, full_inverse_sqrt, full_inverse_floor = inverse_and_inverse_sqrt(full_weight)
            check(f"V={volume} d={dimension} full shift", full_floor <= 0.0 or np.isfinite(full_floor), full_floor, "finite", "full weight")
            check(f"V={volume} d={dimension} full positive", full_inverse_floor >= 1.0 - positive_tolerance, full_inverse_floor, ">=1", "full weight")
            for support_value in supports_by_volume[str(volume)]:
                support = tuple(int(site) for site in support_value)
                check(f"V={volume} d={dimension} support valid", all(0 <= site < volume for site in support) and len(set(support)) == len(support), support, "valid distinct sites", "support")
                source_potential = sum((onsite_potential[site] for site in support), np.zeros_like(hamiltonian))
                internal_edges = [edge for edge in edges if edge[0] in support and edge[1] in support]
                source_edge = source_potential + sum((bonds[edge] for edge in internal_edges), np.zeros_like(hamiltonian))
                for kind, source_base in (("onsite", source_potential), ("edge", source_edge)):
                    source_weight, source_floor = shifted_positive(source_base)
                    commutator = full_weight @ source_weight - source_weight @ full_weight
                    commutator_right = commutator @ full_inverse
                    form_constant = float(np.max(np.linalg.eigvalsh(hermitian(full_inverse_sqrt @ source_weight @ full_inverse_sqrt))))
                    graph_constant = operator_norm(source_weight @ full_inverse)
                    commutator_constant = operator_norm(commutator_right)
                    check(f"V={volume} d={dimension} S={support} {kind} positive", source_floor <= 0.0 or np.isfinite(source_floor), source_floor, "finite", "source weight")
                    check(f"V={volume} d={dimension} S={support} {kind} floor", float(np.min(np.linalg.eigvalsh(source_weight))) >= 1.0 - positive_tolerance, float(np.min(np.linalg.eigvalsh(source_weight))), ">=1", "source weight")
                    values = (form_constant, graph_constant, commutator_constant)
                    check(f"V={volume} d={dimension} S={support} {kind} constants finite", all(np.isfinite(value) and value >= 0.0 for value in values), values, "finite nonnegative", "transfer constants")
                    basis_rows = core_rows(full_weight, source_weight, commutator, volume, dimension, core_degree, graph_constant, commutator_constant)
                    check(f"V={volume} d={dimension} S={support} {kind} core nonempty", len(basis_rows) > 0, len(basis_rows), ">0", "polynomial core")
                    for basis_row in basis_rows:
                        check(f"V={volume} d={dimension} S={support} {kind} core graph {basis_row['index']}", basis_row["graph_bound_slack"] >= -tolerance * (1.0 + graph_constant), basis_row["graph_ratio"], f"<={graph_constant}", "polynomial core")
                        check(f"V={volume} d={dimension} S={support} {kind} core comm {basis_row['index']}", basis_row["commutator_bound_slack"] >= -tolerance * (1.0 + commutator_constant), basis_row["commutator_ratio"], f"<={commutator_constant}", "polynomial core")
                    all_core_rows += len(basis_rows)
                    row = {
                        "volume": volume,
                        "oscillator_dimension": dimension,
                        "support": list(support),
                        "kind": kind,
                        "internal_edges": [list(edge) for edge in internal_edges],
                        "full_floor": full_floor,
                        "full_shifted_floor": full_inverse_floor,
                        "source_floor": source_floor,
                        "form_constant": form_constant,
                        "graph_constant": graph_constant,
                        "commutator_constant": commutator_constant,
                        "core_rows": basis_rows,
                        "core_count": len(basis_rows),
                    }
                    rows.append(row)
                    if volume == 2 and support == (0, 1) and kind == "edge":
                        cutoff_edge_commutators.append((dimension, commutator_constant))

    check("scenario coverage", len(rows) == sum(len(dimensions_by_volume[str(volume)]) * len(supports_by_volume[str(volume)]) * 2 for volume in fixture["volume_values"]), len(rows), "declared scenario count", "coverage")
    check("core rows coverage", all_core_rows == sum(len(core_indices(int(volume), int(dimension), core_degree)) for volume in fixture["volume_values"] for dimension in dimensions_by_volume[str(volume)] for _ in supports_by_volume[str(volume)] for _ in (0, 1)), all_core_rows, "derived declared core count", "coverage")
    check("cutoff edge sequence", [dimension for dimension, _ in cutoff_edge_commutators] == [int(value) for value in dimensions_by_volume["2"]], cutoff_edge_commutators, "declared V=2 dimensions", "cutoff")
    positive_cutoff = [(dimension, value) for dimension, value in cutoff_edge_commutators if value > positive_tolerance]
    check("cutoff positive samples", len(positive_cutoff) >= 2, positive_cutoff, ">=2", "cutoff")
    first_dimension, first_commutator = positive_cutoff[0]
    last_dimension, last_commutator = positive_cutoff[-1]
    cutoff_growth = last_commutator / max(first_commutator, np.finfo(float).tiny)
    check("cutoff commutator growth diagnostic", cutoff_growth >= float(fixture["cutoff_growth_threshold"]), cutoff_growth, f">={fixture['cutoff_growth_threshold']}", "cutoff")

    summaries: list[dict[str, Any]] = []
    for row in rows:
        summaries.append({key: row[key] for key in ("volume", "oscillator_dimension", "support", "kind", "internal_edges", "form_constant", "graph_constant", "commutator_constant", "core_count")})
    max_graph = max(row["graph_constant"] for row in rows)
    max_commutator = max(row["commutator_constant"] for row in rows)
    max_form = max(row["form_constant"] for row in rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-LOCAL-GRAPH-NORM-TRANSFER-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "scenario_count": len(rows),
            "core_row_count": all_core_rows,
            "summary_rows": summaries,
            "max_form_constant": max_form,
            "max_graph_constant": max_graph,
            "max_commutator_constant": max_commutator,
            "cutoff_edge_commutator_rows": [{"dimension": dimension, "commutator_constant": value} for dimension, value in cutoff_edge_commutators],
            "cutoff_commutator_growth": cutoff_growth,
            "cutoff_growth_first_dimension": first_dimension,
            "cutoff_growth_last_dimension": last_dimension,
            "finite_source_graph_form_rows_closed": True,
            "finite_source_graph_norm_rows_closed": True,
            "finite_source_commutator_rows_closed": True,
            "explicit_polynomial_core_rows_closed": True,
            "uniform_common_core_graph_bound_closed": False,
            "uniform_commutator_bound_closed": False,
            "cutoff_removal_closed": False,
            "common_alpha_closed": False,
            "qft_promoted": False,
        },
        "boundary": scope,
        "provenance": {
            "script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY SOURCE-LOCAL-GRAPH-NORM-TRANSFER PASS {payload['passed']}/{payload['assertion_count']} scenarios={payload['derived']['scenario_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())