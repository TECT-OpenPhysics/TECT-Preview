#!/usr/bin/env python3
"""Primary finite Q3 word/time enlargement compatibility audit for EXP-001182."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-gns-word-time-compatibility"
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

    return {"volume": volume, "dimension": int(dimension**volume), "energies": shifted, "observables": observables, "transfer": transfer}


def word_vectors(state: dict[str, Any], beta: float, tau_fractions: list[float], word_kinds: list[str], hbar: float) -> tuple[list[np.ndarray], float]:
    period = beta * hbar
    weights = np.exp(-beta * state["energies"] / hbar)
    partition = float(np.sum(weights))
    q, p = state["observables"]["q"], state["observables"]["p"]
    operators = {"q": q, "p": p, "qp": q @ p, "pq": p @ q, "qpq": q @ p @ q}
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

    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001182", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001182/T-054/false", "provenance")
    check("graph fixture", list(fixture["graphs"]) == ["path2", "path3", "path4"], list(fixture["graphs"]), "path2/path3/path4", "fixture")
    check("word/time fixture", fixture["base_word_kinds"] == ["q", "p", "qp", "pq"] and fixture["added_word_kinds"] == ["qpq"] and fixture["base_tau_fractions"] == [0.125, 0.25] and fixture["translated_tau_fraction"] == 0.375, {key: fixture[key] for key in ("base_word_kinds", "added_word_kinds", "base_tau_fractions", "translated_tau_fraction")}, "base q/p/qp/pq; add qpq; translate to 0.375", "fixture")
    check("translation inside half period", max(fixture["base_tau_fractions"]) < fixture["translated_tau_fraction"] <= 0.5, fixture["translated_tau_fraction"], "max(base)<translated<=0.5", "fixture")
    check("nested pairs", fixture["nested_pairs"] == [["path2", "path3"], ["path3", "path4"]], fixture["nested_pairs"], "path2->path3 and path3->path4", "fixture")
    check("scope firewall", scope["finite_word_enlargement_time_translate_diagnostic_closed"] and scope["finite_base_polar_congruence_closed"] and scope["finite_expanded_polar_congruence_closed"] and not scope["word_product_star_action_intertwining_closed"] and not scope["common_os_hilbert_carrier_closed"], scope, "finite compatibility diagnostic only", "scope")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/R342.lean"), None)
    check("Lean declaration", declarations(LEAN) == [MARKER], declarations(LEAN), MARKER, "Lean")
    check("Lean registry hash", entry is not None and entry["sha256"] == normalized_sha256(LEAN), entry["sha256"] if entry else None, normalized_sha256(LEAN), "Lean")

    dimension = int(fixture["oscillator_dimension"])
    beta_values = [float(value) for value in fixture["beta_values"]]
    base_tau = [float(value) for value in fixture["base_tau_fractions"]]
    translated_tau = float(fixture["translated_tau_fraction"])
    expanded_tau = base_tau + [translated_tau]
    base_words = list(fixture["base_word_kinds"])
    expanded_words = base_words + list(fixture["added_word_kinds"])
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
    base_count, expanded_count = len(base_words) * len(base_tau), len(expanded_words) * len(expanded_tau)
    base_indices = [tau_index * len(expanded_words) + word_index for tau_index in range(len(base_tau)) for word_index in range(len(base_words))]
    translated_indices = [len(base_tau) * len(expanded_words) + word_index for word_index in range(len(base_words))]

    for small_name, large_name in fixture["nested_pairs"]:
        small, large = states[small_name], states[large_name]
        check(f"{small_name}->{large_name} dimensions", large["dimension"] == small["dimension"] * dimension, [small["dimension"], large["dimension"]], f"large={small['dimension']}*{dimension}", "tensor")
        for beta in beta_values:
            small_base_vectors, z_small = word_vectors(small, beta, base_tau, base_words, hbar)
            large_base_vectors, z_large = word_vectors(large, beta, base_tau, base_words, hbar)
            small_expanded_vectors, z_small_expanded = word_vectors(small, beta, expanded_tau, expanded_words, hbar)
            large_expanded_vectors, z_large_expanded = word_vectors(large, beta, expanded_tau, expanded_words, hbar)
            check(f"{small_name}->{large_name} beta={beta} partitions", min(z_small, z_large, z_small_expanded, z_large_expanded) > partition_floor, [z_small, z_large, z_small_expanded, z_large_expanded], f">{partition_floor}", "normalization")
            g_small, g_large = gram(small_base_vectors), gram(large_base_vectors)
            g_small_expanded, g_large_expanded = gram(small_expanded_vectors), gram(large_expanded_vectors)
            base_values_small, base_root_small, _ = positive_root(g_small, support_floor)
            base_values_large, base_root_large, base_inverse_large = positive_root(g_large, support_floor)
            expanded_values_small, expanded_root_small, _ = positive_root(g_small_expanded, support_floor)
            expanded_values_large, expanded_root_large, expanded_inverse_large = positive_root(g_large_expanded, support_floor)
            base_transport = base_inverse_large @ base_root_small
            expanded_transport = expanded_inverse_large @ expanded_root_small
            base_condition_small = float(np.max(base_values_small) / np.min(base_values_small))
            base_condition_large = float(np.max(base_values_large) / np.min(base_values_large))
            expanded_condition_small = float(np.max(expanded_values_small) / np.min(expanded_values_small))
            expanded_condition_large = float(np.max(expanded_values_large) / np.min(expanded_values_large))
            base_congruence = base_transport.conj().T @ g_large @ base_transport
            expanded_congruence = expanded_transport.conj().T @ g_large_expanded @ expanded_transport
            base_residual = np.linalg.norm(base_congruence - g_small, ord="fro") / max(np.linalg.norm(g_small, ord="fro"), partition_floor)
            expanded_residual = np.linalg.norm(expanded_congruence - g_small_expanded, ord="fro") / max(np.linalg.norm(g_small_expanded, ord="fro"), partition_floor)
            principal_base = g_large_expanded[np.ix_(base_indices, base_indices)]
            principal_small = g_small_expanded[np.ix_(base_indices, base_indices)]
            principal_residual = np.linalg.norm(principal_small - g_small, ord="fro") / max(np.linalg.norm(g_small, ord="fro"), partition_floor)
            restricted_transport = expanded_transport[np.ix_(base_indices, base_indices)]
            compatibility_residual = np.linalg.norm(restricted_transport - base_transport, ord="fro") / max(np.linalg.norm(base_transport, ord="fro"), partition_floor)
            translated_small = g_small_expanded[np.ix_(translated_indices, translated_indices)]
            translated_large = g_large_expanded[np.ix_(translated_indices, translated_indices)]
            translated_gram_delta = np.linalg.norm(translated_large - translated_small, ord="fro") / max(np.linalg.norm(translated_small, ord="fro"), partition_floor)
            translated_norms = [float(np.linalg.norm(small_expanded_vectors[index])) for index in translated_indices] + [float(np.linalg.norm(large_expanded_vectors[index])) for index in translated_indices]
            base_distance = np.linalg.norm(base_transport - np.eye(base_count), ord="fro")
            expanded_distance = np.linalg.norm(expanded_transport - np.eye(expanded_count), ord="fro")
            min_support = min(float(np.min(base_values_small)), float(np.min(base_values_large)), float(np.min(expanded_values_small)), float(np.min(expanded_values_large)))
            check(f"{small_name}->{large_name} beta={beta} support", min_support > support_floor, min_support, f">{support_floor}", "Gram support")
            check(f"{small_name}->{large_name} beta={beta} base congruence", base_residual <= matrix_tolerance, base_residual, f"<={matrix_tolerance}", "base polar transport")
            check(f"{small_name}->{large_name} beta={beta} expanded congruence", expanded_residual <= matrix_tolerance, expanded_residual, f"<={matrix_tolerance}", "expanded polar transport")
            check(f"{small_name}->{large_name} beta={beta} principal consistency", principal_residual <= matrix_tolerance, principal_residual, f"<={matrix_tolerance}", "word enlargement")
            check(f"{small_name}->{large_name} beta={beta} translated support", min(translated_norms) > witness_floor and all(np.isfinite(value) for value in translated_norms), translated_norms, f">{witness_floor} and finite", "time translation")
            rows.append({"small_graph": small_name, "large_graph": large_name, "beta": beta, "base_congruence_relative_residual": float(base_residual), "expanded_congruence_relative_residual": float(expanded_residual), "principal_base_consistency_residual": float(principal_residual), "restricted_transport_compatibility_residual": float(compatibility_residual), "translated_gram_delta_relative": float(translated_gram_delta), "base_transport_distance": float(base_distance), "expanded_transport_distance": float(expanded_distance), "min_support": float(min_support), "base_condition_small": base_condition_small, "base_condition_large": base_condition_large, "expanded_condition_small": expanded_condition_small, "expanded_condition_large": expanded_condition_large})
            support_rows.append({"small_graph": small_name, "large_graph": large_name, "beta": beta, "base_word_count": base_count, "expanded_word_count": expanded_count, "base_tau_count": len(base_tau), "expanded_tau_count": len(expanded_tau), "min_eigen_base_small": float(np.min(base_values_small)), "min_eigen_base_large": float(np.min(base_values_large)), "min_eigen_expanded_small": float(np.min(expanded_values_small)), "min_eigen_expanded_large": float(np.min(expanded_values_large)), "base_condition_small": base_condition_small, "base_condition_large": base_condition_large, "expanded_condition_small": expanded_condition_small, "expanded_condition_large": expanded_condition_large, "base_congruence_relative_residual": float(base_residual), "expanded_congruence_relative_residual": float(expanded_residual), "principal_base_consistency_residual": float(principal_residual), "restricted_transport_compatibility_residual": float(compatibility_residual), "translated_gram_delta_relative": float(translated_gram_delta), "base_transport_distance": float(base_distance), "expanded_transport_distance": float(expanded_distance), "translated_vector_norm_min": float(min(translated_norms)), "partition_small": z_small, "partition_large": z_large, "partition_small_expanded": z_small_expanded, "partition_large_expanded": z_large_expanded})

    numeric_fields = ("base_congruence_relative_residual", "expanded_congruence_relative_residual", "principal_base_consistency_residual", "restricted_transport_compatibility_residual", "translated_gram_delta_relative", "base_transport_distance", "expanded_transport_distance", "min_support", "base_condition_small", "base_condition_large", "expanded_condition_small", "expanded_condition_large")
    support_numeric_fields = tuple(key for key in support_rows[0] if key not in ("small_graph", "large_graph"))
    check("block coverage", len(rows) == len(fixture["nested_pairs"]) * len(beta_values), len(rows), len(fixture["nested_pairs"]) * len(beta_values), "coverage")
    check("support coverage", len(support_rows) == len(rows), len(support_rows), len(rows), "coverage")
    check("numeric fields", all(np.isfinite(row[key]) for row in rows for key in numeric_fields) and all(np.isfinite(row[key]) for row in support_rows for key in support_numeric_fields), len(rows), "all finite", "numerics")
    check("nonzero compatibility witness", max(row["restricted_transport_compatibility_residual"] for row in rows) >= witness_floor, max(row["restricted_transport_compatibility_residual"] for row in rows), f">={witness_floor}", "route diagnostic")
    check("nonzero translated Gram witness", max(row["translated_gram_delta_relative"] for row in rows) >= witness_floor, max(row["translated_gram_delta_relative"] for row in rows), f">={witness_floor}", "route diagnostic")
    downstream = ("word_product_star_action_intertwining_closed", "common_os_hilbert_carrier_closed", "source_volume_cutoff_beta_uniform_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("scope firewall", all(not scope[field] for field in downstream), {field: scope[field] for field in downstream}, "all downstream QFT gates open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GNS-WORD-TIME-COMPATIBILITY", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "rows": rows, "support_rows": support_rows, "scope": scope, "boundary": manifest["boundary"], "derived": {"row_count": len(rows), "max_restricted_transport_compatibility_residual": max(row["restricted_transport_compatibility_residual"] for row in rows), "max_translated_gram_delta_relative": max(row["translated_gram_delta_relative"] for row in rows), "max_base_congruence_residual": max(row["base_congruence_relative_residual"] for row in rows), "max_expanded_congruence_residual": max(row["expanded_congruence_relative_residual"] for row in rows), "max_base_transport_distance": max(row["base_transport_distance"] for row in rows), "max_expanded_transport_distance": max(row["expanded_transport_distance"] for row in rows), "min_support": min(row["min_support"] for row in rows), "max_base_condition": max(max(row["base_condition_small"], row["base_condition_large"]) for row in rows), "max_expanded_condition": max(max(row["expanded_condition_small"], row["expanded_condition_large"]) for row in rows), "lean_marker": MARKER}, "provenance": {"script_sha256": normalized_sha256(Path(__file__)), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN), "registry_sha256": normalized_sha256(REGISTRY)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY GNS-WORD-TIME-COMPATIBILITY PASS {payload['passed']}/{payload['assertion_count']} blocks={len(payload['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
