#!/usr/bin/env python3
"""Finite kinetic-isolation checkpoint for the anchored Q3 resolvent route.

For a bond prefix H=T+V with T the quadratic momentum part and V a polynomial
of commuting coordinates, the coordinate resolvent A_z commutes with V and
with the position-only boundary B.  The anchored second commutator therefore
reduces exactly to [B,[T,A_z]].  This is a bounded finite diagnostic only: it
does not estimate an unbounded form-domain or any thermodynamic limit.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_anchored_nested_commutator_kinetic_isolation_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-anchored-nested-commutator-kinetic-isolation-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"


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


def graph_edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(int(site) for site in edge) for edge in fixture["graph_edges_by_volume"][str(volume)]]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    quadratic = difference @ difference
    quartic = quadratic @ (left @ left + right @ right)
    return hermitian(float(fixture["c"]) * quadratic / 2.0 + float(fixture["lambda"]) * quartic / 4.0)


def build_terms(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], list[dict[str, Any]]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    records: list[dict[str, Any]] = []
    for site, (q, p) in enumerate(zip(q_ops, p_ops)):
        kinetic = hermitian(p @ p / (2.0 * float(fixture["chi"])))
        potential = hermitian(float(fixture["r"]) * (q @ q) / 2.0 + float(fixture["g"]) * (q @ q @ q @ q) / 4.0)
        records.append({"kind": "onsite", "support": [site], "total": hermitian(kinetic + potential), "kinetic": kinetic, "potential": potential})
    for left, right in graph_edges(volume, fixture):
        potential = bond_term(q_ops[left], q_ops[right], fixture)
        records.append({"kind": "bond", "support": [left, right], "total": potential, "kinetic": np.zeros_like(potential), "potential": potential})
    return q_ops, p_ops, records


def sum_field(records: list[dict[str, Any]], indices: list[int], field: str) -> np.ndarray:
    result = np.zeros_like(records[0][field], dtype=complex)
    for index in indices:
        result = result + records[index][field]
    return hermitian(result)


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def two_sided_norm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001230" and manifest["result_id"] == "R-387" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001230/R-387/false", "provenance")
    check("coverage", coverage["all_bond_prefixes"] and coverage["both_orders"] and coverage["both_adjoint_seeds"], coverage, "all bond prefixes, orders and adjoints", "coverage")
    finite_flags = ("finite_coordinate_potential_commutation_closed", "finite_kinetic_isolation_closed", "finite_potential_scale_invariance_closed", "finite_weighted_isolation_closed")
    open_flags = ("phase_local_bkm_estimate_closed", "boundary_shell_l1_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(scope[key] for key in open_flags), "finite isolation / all limits open", "scope", "scope")

    beta_values = [float(Fraction(value)) for value in fixture["beta_values"]]
    eta_values = [float(Fraction(value)) for value in fixture["resolvent_imaginary_values"]]
    tolerance = float(fixture["isolation_tolerance"])
    weighted_tolerance = float(fixture["weighted_isolation_tolerance"])
    scale_values = [float(Fraction(value)) for value in fixture["potential_scale_values"]]
    maxima = {"potential_commutator_residual": 0.0, "boundary_commutator_residual": 0.0, "inner_isolation_residual": 0.0, "nested_isolation_residual": 0.0, "scale_invariance_residual": 0.0, "weighted_isolation_residual": 0.0}
    volume_summaries: list[dict[str, Any]] = []
    context_count = 0
    bond_prefix_count = 0
    seed_rows = 0
    weighted_rows = 0

    for volume in (int(value) for value in fixture["volume_values"]):
        q_ops, p_ops, records = build_terms(volume, int(fixture["oscillator_dimension"]), fixture)
        term_count = len(records)
        order_map = {"forward": list(range(term_count)), "reverse": list(reversed(range(term_count)))}
        volume_max = {key: 0.0 for key in maxima}
        volume_contexts = 0
        volume_bonds = 0
        for order_name in coverage["orders"]:
            order = order_map[order_name]
            for prefix_position, term_index in enumerate(order):
                if records[term_index]["kind"] != "bond":
                    continue
                bond_prefix_count += 1
                volume_bonds += 1
                prefix = order[:prefix_position]
                hamiltonian = sum_field(records, prefix, "total")
                kinetic = sum_field(records, prefix, "kinetic") if prefix else np.zeros_like(hamiltonian)
                potential = sum_field(records, prefix, "potential") if prefix else np.zeros_like(hamiltonian)
                boundary = records[term_index]["total"]
                for site in range(volume):
                    identity = np.eye(q_ops[site].shape[0], dtype=complex)
                    for eta in eta_values:
                        observable = np.linalg.inv(1j * eta * identity - q_ops[site])
                        for seed_name, seed in (("A", observable), ("A_star", observable.conj().T)):
                            potential_residual = operator_norm(commutator(potential, seed))
                            boundary_residual = operator_norm(commutator(boundary, seed))
                            inner_residual = operator_norm(commutator(hamiltonian, seed) - commutator(kinetic, seed))
                            nested_residual = operator_norm(commutator(boundary, commutator(hamiltonian, seed)) - commutator(boundary, commutator(kinetic, seed)))
                            scale_residual = 0.0
                            for scale in scale_values:
                                scaled_h = hermitian(kinetic + scale * potential)
                                scale_residual = max(scale_residual, operator_norm(commutator(boundary, commutator(scaled_h, seed)) - commutator(boundary, commutator(kinetic, seed))))
                            for key, value in (("potential_commutator_residual", potential_residual), ("boundary_commutator_residual", boundary_residual), ("inner_isolation_residual", inner_residual), ("nested_isolation_residual", nested_residual), ("scale_invariance_residual", scale_residual)):
                                maxima[key] = max(maxima[key], value)
                                volume_max[key] = max(volume_max[key], value)
                            seed_rows += 1
                            check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta} {seed_name} potential", potential_residual <= tolerance, potential_residual, f"<={tolerance}", "coordinate potential")
                            check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta} {seed_name} boundary", boundary_residual <= tolerance, boundary_residual, f"<={tolerance}", "coordinate boundary")
                            check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta} {seed_name} inner", inner_residual <= tolerance, inner_residual, f"<={tolerance}", "kinetic isolation")
                            check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta} {seed_name} nested", nested_residual <= tolerance, nested_residual, f"<={tolerance}", "kinetic isolation")
                            check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta} {seed_name} scale", scale_residual <= tolerance, scale_residual, f"<={tolerance}", "potential scale")
                            for beta in beta_values:
                                rho = gibbs(hermitian(hamiltonian), beta)
                                weighted = two_sided_norm(commutator(boundary, commutator(hamiltonian, seed)) - commutator(boundary, commutator(kinetic, seed)), rho)
                                maxima["weighted_isolation_residual"] = max(maxima["weighted_isolation_residual"], weighted)
                                volume_max["weighted_isolation_residual"] = max(volume_max["weighted_isolation_residual"], weighted)
                                weighted_rows += 1
                                volume_contexts += 1
                                context_count += 1
                                check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta} beta={beta} {seed_name} weighted", weighted <= weighted_tolerance, weighted, f"<={weighted_tolerance}", "weighted isolation")
        expected_volume_seeds = 2 * len(graph_edges(volume, fixture)) * volume * len(eta_values) * 2
        expected_volume_contexts = expected_volume_seeds * len(beta_values)
        check(f"V={volume} seed count", seed_rows >= 0 and volume_bonds * volume * len(eta_values) * 2 == expected_volume_seeds, [volume_bonds, expected_volume_seeds], "bond-prefix grid", "coverage")
        check(f"V={volume} context count", volume_contexts == expected_volume_contexts, volume_contexts, expected_volume_contexts, "coverage")
        volume_summaries.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "term_count": term_count, "bond_prefix_count": volume_bonds, "context_count": volume_contexts, "maximums": volume_max})

    expected_bond_prefixes = sum(2 * len(graph_edges(int(volume), fixture)) for volume in fixture["volume_values"])
    expected_seeds = sum(2 * len(graph_edges(int(volume), fixture)) * int(volume) * len(eta_values) * 2 for volume in fixture["volume_values"])
    expected_contexts = expected_seeds * len(beta_values)
    check("global bond prefixes", bond_prefix_count == expected_bond_prefixes, bond_prefix_count, expected_bond_prefixes, "coverage")
    check("global seed rows", seed_rows == expected_seeds, seed_rows, expected_seeds, "coverage")
    check("global weighted rows", weighted_rows == context_count == expected_contexts, [weighted_rows, context_count], expected_contexts, "coverage")
    check("finite maxima", all(np.isfinite(value) for value in maxima.values()), maxima, "finite", "numerics")
    derived = {"context_count": context_count, "expected_contexts": expected_contexts, "bond_prefix_count": bond_prefix_count, "seed_rows": seed_rows, "weighted_rows": weighted_rows, "maximums": maxima, "volume_summaries": volume_summaries}
    for key in finite_flags:
        derived[key] = True
    for key in open_flags:
        derived[key] = False
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-ANCHORED-NESTED-COMMUTATOR-KINETIC-ISOLATION-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    output = args.output if args.output.is_absolute() else REPO / args.output
    atomic_json(output, payload)
    print(f"PRIMARY ANCHORED NESTED-COMMUTATOR KINETIC-ISOLATION PASS {payload['passed']}/{payload['assertion_count']} contexts={payload['derived']['context_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
