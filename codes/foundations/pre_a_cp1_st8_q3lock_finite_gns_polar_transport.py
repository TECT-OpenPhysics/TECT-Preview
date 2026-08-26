#!/usr/bin/env python3
"""Primary finite Q3 state-dependent Gram-polar transport audit for EXP-001181."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-gns-polar-transport"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
LEAN = REPO / "verification" / "lean" / "Tect" / "R342.lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
MARKER = "gram_transport_congruence"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_finite_euclidean_os_gram_kms_bridge as model  # noqa: E402
import pre_a_cp1_st8_q3lock_finite_split_gibbs_kms_residual as base  # noqa: E402


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


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def declarations(path: Path) -> list[str]:
    import re

    return re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", path.read_text(encoding="utf-8"))


def finite_state(declaration: dict[str, Any], dimension: int, parameters: dict[str, str], amplitude: float, hbar: float) -> dict[str, Any]:
    volume = int(declaration["vertices"])
    edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
    terms, q_single, p_single = model.periodic_terms(edges, volume, dimension, parameters)
    hamiltonian = base.hermitian(sum(terms, np.zeros_like(terms[0])))
    energies, eigenvectors = base.eigensystem(hamiltonian)
    shifted = energies - float(np.min(energies))
    identity = np.eye(dimension, dtype=complex)
    observables = {
        kind: base.embed(base.character(q_single if kind == "q" else p_single, amplitude, hbar), 0, volume, identity)
        for kind in ("q", "p")
    }

    def transfer(seconds: float) -> np.ndarray:
        return eigenvectors @ np.diag(np.exp(-seconds * shifted / hbar)) @ eigenvectors.conj().T

    return {"volume": volume, "dimension": int(dimension**volume), "energies": shifted, "eigenvectors": eigenvectors, "observables": observables, "transfer": transfer}


def word_vectors(state: dict[str, Any], beta: float, tau_fractions: list[float], word_kinds: list[str], hbar: float) -> tuple[list[np.ndarray], float]:
    period = beta * hbar
    weights = np.exp(-beta * state["energies"] / hbar)
    partition = float(np.sum(weights))
    q, p = state["observables"]["q"], state["observables"]["p"]
    operators = {"q": q, "p": p, "qp": q @ p, "pq": p @ q}
    vectors: list[np.ndarray] = []
    for tau_fraction in tau_fractions:
        tau = tau_fraction * period
        left = state["transfer"](period / 2.0 - tau)
        right = state["transfer"](tau)
        for kind in word_kinds:
            vectors.append((left @ operators[kind] @ right).reshape(-1) / np.sqrt(partition))
    return vectors, partition


def gram(vectors: list[np.ndarray]) -> np.ndarray:
    return np.array([[np.vdot(first, second) for second in vectors] for first in vectors], dtype=complex)


def positive_root(matrix: np.ndarray, support_floor: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    hermitian = (matrix + matrix.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    if float(np.min(values)) <= support_floor:
        raise AssertionError(f"Gram support below floor: {float(np.min(values))} <= {support_floor}")
    root = vectors @ np.diag(np.sqrt(values)) @ vectors.conj().T
    inverse_root = vectors @ np.diag(1.0 / np.sqrt(values)) @ vectors.conj().T
    return values, root, inverse_root


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001181", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001181/T-054/false", "provenance")
    check("graph fixture", list(fixture["graphs"]) == ["path2", "path3", "path4"], list(fixture["graphs"]), "path2/path3/path4", "fixture")
    check("word fixture", fixture["word_kinds"] == ["q", "p", "qp", "pq"] and len(fixture["tau_fractions"]) == 2, fixture["word_kinds"], "q/p/qp/pq at two tau values", "fixture")
    check("nested pairs", fixture["nested_pairs"] == [["path2", "path3"], ["path3", "path4"]], fixture["nested_pairs"], "path2->path3 and path3->path4", "fixture")
    check("scope firewall", scope["finite_q3_nested_word_blocks_closed"] and scope["finite_state_dependent_polar_congruence_closed"] and not scope["word_product_star_action_intertwining_closed"] and not scope["common_os_hilbert_carrier_closed"], scope, "finite GNS block only", "scope")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/R342.lean"), None)
    check("Lean declaration", declarations(LEAN) == [MARKER], declarations(LEAN), MARKER, "Lean")
    check("Lean registry hash", entry is not None and entry["sha256"] == normalized_sha256(LEAN), entry["sha256"] if entry else None, normalized_sha256(LEAN), "Lean")

    dimension = int(fixture["oscillator_dimension"])
    beta_values = [float(value) for value in fixture["beta_values"]]
    tau_fractions = [float(value) for value in fixture["tau_fractions"]]
    word_kinds = list(fixture["word_kinds"])
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    support_floor = float(fixture["support_floor"])
    matrix_tolerance = float(fixture["matrix_tolerance"])
    partition_floor = float(fixture["positive_partition_floor"])
    witness_floor = float(fixture["witness_floor"])
    parameters = manifest["model_parameters"]
    states = {name: finite_state(declaration, dimension, parameters, amplitude, hbar) for name, declaration in fixture["graphs"].items()}
    rows: list[dict[str, Any]] = []
    support_rows: list[dict[str, Any]] = []
    transport_by_beta: dict[tuple[str, float], np.ndarray] = {}
    sub_indices = [0, 1, len(word_kinds), len(word_kinds) + 1]

    for small_name, large_name in fixture["nested_pairs"]:
        small, large = states[small_name], states[large_name]
        check(f"{small_name}->{large_name} dimensions", large["dimension"] == small["dimension"] * dimension, [small["dimension"], large["dimension"]], f"large={small['dimension']}*{dimension}", "tensor")
        for beta in beta_values:
            small_vectors, z_small = word_vectors(small, beta, tau_fractions, word_kinds, hbar)
            large_vectors, z_large = word_vectors(large, beta, tau_fractions, word_kinds, hbar)
            check(f"{small_name}->{large_name} beta={beta} partitions", z_small > partition_floor and z_large > partition_floor, [z_small, z_large], f">{partition_floor}", "normalization")
            g_small, g_large = gram(small_vectors), gram(large_vectors)
            small_values, small_root, _ = positive_root(g_small, support_floor)
            large_values, large_root, large_inverse_root = positive_root(g_large, support_floor)
            transport = large_inverse_root @ small_root
            transport_by_beta[(f"{small_name}->{large_name}", beta)] = transport
            congruence = transport.conj().T @ g_large @ transport
            residual = np.linalg.norm(congruence - g_small, ord="fro") / max(np.linalg.norm(g_small, ord="fro"), partition_floor)
            gram_delta = np.linalg.norm(g_large - g_small, ord="fro") / max(np.linalg.norm(g_small, ord="fro"), partition_floor)
            transport_distance = np.linalg.norm(transport - np.eye(len(word_kinds) * len(tau_fractions)), ord="fro")
            condition_small = float(np.max(small_values) / np.min(small_values))
            condition_large = float(np.max(large_values) / np.min(large_values))
            check(f"{small_name}->{large_name} beta={beta} support", float(np.min(small_values)) > support_floor and float(np.min(large_values)) > support_floor, [float(np.min(small_values)), float(np.min(large_values))], f">{support_floor}", "Gram support")
            check(f"{small_name}->{large_name} beta={beta} congruence", residual <= matrix_tolerance, residual, f"<={matrix_tolerance}", "polar transport")
            sub_transport = large_inverse_root[np.ix_(sub_indices, sub_indices)] @ small_root[np.ix_(sub_indices, sub_indices)]
            sub_small = g_small[np.ix_(sub_indices, sub_indices)]
            sub_large = g_large[np.ix_(sub_indices, sub_indices)]
            sub_values, sub_root, sub_inverse_root = positive_root(sub_small, support_floor)
            sub_polar = sub_inverse_root @ sub_root
            block_dependence = np.linalg.norm(sub_transport - sub_polar, ord="fro")
            block_congruence = np.linalg.norm(sub_polar.conj().T @ sub_large @ sub_polar - sub_small, ord="fro") / max(np.linalg.norm(sub_small, ord="fro"), partition_floor)
            support_rows.append({"small_graph": small_name, "large_graph": large_name, "beta": beta, "word_count": len(small_vectors), "min_eigen_small": float(np.min(small_values)), "min_eigen_large": float(np.min(large_values)), "condition_small": condition_small, "condition_large": condition_large, "gram_delta_relative": float(gram_delta), "congruence_relative_residual": float(residual), "transport_distance": float(transport_distance), "subblock_transport_dependence": float(block_dependence), "subblock_congruence_residual": float(block_congruence), "partition_small": z_small, "partition_large": z_large})
            rows.append({"small_graph": small_name, "large_graph": large_name, "beta": beta, "gram_delta_relative": float(gram_delta), "congruence_relative_residual": float(residual), "transport_distance": float(transport_distance), "min_eigen_small": float(np.min(small_values)), "min_eigen_large": float(np.min(large_values)), "condition_small": condition_small, "condition_large": condition_large, "subblock_transport_dependence": float(block_dependence), "subblock_congruence_residual": float(block_congruence)})

    for pair in [f"{a}->{b}" for a, b in fixture["nested_pairs"]]:
        if len(beta_values) >= 2:
            delta_beta = np.linalg.norm(transport_by_beta[(pair, beta_values[1])] - transport_by_beta[(pair, beta_values[0])], ord="fro")
            check(f"{pair} beta transport finite", np.isfinite(delta_beta), delta_beta, "finite", "state dependence")
    check("block coverage", len(rows) == len(fixture["nested_pairs"]) * len(beta_values), len(rows), len(fixture["nested_pairs"]) * len(beta_values), "coverage")
    check("support coverage", len(support_rows) == len(rows), len(support_rows), len(rows), "coverage")
    check("numeric fields", all(np.isfinite(row[key]) for row in support_rows for key in ("min_eigen_small", "min_eigen_large", "condition_small", "condition_large", "gram_delta_relative", "congruence_relative_residual", "transport_distance", "subblock_transport_dependence", "subblock_congruence_residual", "partition_small", "partition_large")), len(support_rows), "all finite", "numerics")
    check("nonzero Gram delta witness", max(row["gram_delta_relative"] for row in rows) >= witness_floor, max(row["gram_delta_relative"] for row in rows), f">={witness_floor}", "route diagnostic")
    check("nonzero block dependence witness", max(row["subblock_transport_dependence"] for row in rows) >= witness_floor, max(row["subblock_transport_dependence"] for row in rows), f">={witness_floor}", "route diagnostic")
    downstream = ("word_product_star_action_intertwining_closed", "common_os_hilbert_carrier_closed", "source_volume_cutoff_beta_uniform_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("scope firewall", all(not scope[field] for field in downstream), {field: scope[field] for field in downstream}, "all downstream QFT gates open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GNS-POLAR-TRANSPORT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "rows": rows, "support_rows": support_rows, "scope": scope, "boundary": manifest["boundary"], "derived": {"row_count": len(rows), "max_gram_delta_relative": max(row["gram_delta_relative"] for row in rows), "max_congruence_residual": max(row["congruence_relative_residual"] for row in rows), "max_transport_distance": max(row["transport_distance"] for row in rows), "max_block_dependence": max(row["subblock_transport_dependence"] for row in rows), "min_gram_eigenvalue": min(min(row["min_eigen_small"], row["min_eigen_large"]) for row in rows), "lean_marker": MARKER}, "provenance": {"script_sha256": normalized_sha256(Path(__file__)), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN), "registry_sha256": normalized_sha256(REGISTRY)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-GNS-POLAR-TRANSPORT PASS {payload['passed']}/{payload['assertion_count']} blocks={len(payload['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
