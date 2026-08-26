#!/usr/bin/env python3
"""Primary finite Q3 Complex Hilbert-Schmidt Gram perturbation audit for EXP-001179."""

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
SLUG = "pre-a-cp1-st8-q3lock-complex-os-gram-perturbation"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
LEAN = REPO / "verification" / "lean" / "Tect" / "R340.lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
MARKER = "finite_complex_gram_entry_perturbation"
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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", (manifest["exploration_id"], manifest["task_id"]) == ("EXP-001179", "T-054"), [manifest["exploration_id"], manifest["task_id"]], "EXP-001179/T-054", "provenance")
    check("claim firewall", manifest["claim_bearing"] is False and not scope["thermodynamic_common_os_hilbert_carrier_closed"] and not scope["pre_a_closed"], [manifest["claim_bearing"], scope["thermodynamic_common_os_hilbert_carrier_closed"], scope["pre_a_closed"]], "finite-only/open", "scope")
    graph_names = list(fixture["graphs"])
    check("graph fixture", graph_names == ["bond2", "square4", "grid2x3"], graph_names, "bond2/square4/grid2x3", "fixture")
    check("observable fixture", fixture["observable_kinds"] == ["q", "p"] and len(fixture["tau_pair_fractions"]) == 2, fixture["observable_kinds"], "q,p with two tau values", "fixture")
    lean_registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in lean_registry["entrypoints"] if item["path"] == "verification/lean/Tect/R340.lean"), None)
    check("Lean declaration", MARKER in declarations(LEAN), declarations(LEAN), MARKER, "Lean")
    check("Lean registry hash", entry is not None and entry["sha256"] == normalized_sha256(LEAN), entry["sha256"] if entry else None, normalized_sha256(LEAN), "Lean")

    dimension = int(fixture["oscillator_dimension"])
    beta_values = [float(value) for value in fixture["beta_values"]]
    tau_fractions = [float(value) for value in fixture["tau_pair_fractions"]]
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    absolute_tolerance = float(fixture["absolute_tolerance"])
    relative_tolerance = float(fixture["relative_tolerance"])
    scale_floor = float(fixture["positive_partition_floor"])
    noncommutation_floor = float(fixture["noncommutation_witness_floor"])
    parameters = manifest["model_parameters"]
    rows: list[dict[str, Any]] = []

    for graph, declaration in fixture["graphs"].items():
        volume = int(declaration["vertices"])
        edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
        sources = [int(value) for value in declaration["source_sites"]]
        terms, q_single, p_single = model.periodic_terms(edges, volume, dimension, parameters)
        hamiltonian = base.hermitian(sum(terms, np.zeros_like(terms[0])))
        energies, eigenvectors = base.eigensystem(hamiltonian)
        shifted = energies - float(np.min(energies))
        noncommutation = base.operator_norm(hamiltonian @ terms[0] - terms[0] @ hamiltonian)
        check(f"{graph} noncommutation witness", np.isfinite(noncommutation) and noncommutation >= noncommutation_floor, noncommutation, f">={noncommutation_floor}", "Q3 dynamics")
        identity = np.eye(dimension, dtype=complex)
        observables = {
            site: {
                kind: eigenvectors.conj().T @ base.embed(base.character(q_single if kind == "q" else p_single, amplitude, hbar), site, volume, identity) @ eigenvectors
                for kind in fixture["observable_kinds"]
            }
            for site in sources
        }
        for beta in beta_values:
            period = beta * hbar
            weights = np.exp(-period * shifted / hbar)
            partition = float(np.sum(weights))
            check(f"{graph} beta={beta} partition", np.isfinite(partition) and partition > scale_floor, partition, f">{scale_floor}", "normalization")
            tau_values = [fraction * period for fraction in tau_fractions]
            left_f = np.exp(-(period / 2.0 - tau_values[0]) * shifted / hbar)
            right_f = np.exp(-tau_values[0] * shifted / hbar)
            left_g = np.exp(-(period / 2.0 - tau_values[1]) * shifted / hbar)
            right_g = np.exp(-tau_values[1] * shifted / hbar)
            for site in sources:
                f_vectors = [left_f[:, None] * observables[site][kind] * right_f[None, :] for kind in fixture["observable_kinds"]]
                g_vectors = [left_g[:, None] * observables[site][kind] * right_g[None, :] for kind in fixture["observable_kinds"]]
                vector_dimension = int(f_vectors[0].size)
                check(f"{graph} site={site} beta={beta} vector shape", all(vector.shape == f_vectors[0].shape for vector in f_vectors + g_vectors), [vector.shape for vector in f_vectors + g_vectors], f"{vector_dimension} coordinates", "Hilbert-Schmidt")
                for i in range(len(f_vectors)):
                    for j in range(len(f_vectors)):
                        first_f, first_g = f_vectors[i].reshape(-1), g_vectors[i].reshape(-1)
                        second_f, second_g = f_vectors[j].reshape(-1), g_vectors[j].reshape(-1)
                        gram_f = np.vdot(first_f, second_f)
                        gram_g = np.vdot(first_g, second_g)
                        decomposition = np.vdot(first_f - first_g, second_f) + np.vdot(first_g, second_f - second_g)
                        raw_lhs = float(abs(gram_f - gram_g))
                        raw_left = float(np.sum(np.abs(first_f - first_g) * np.abs(second_f)))
                        raw_right = float(np.sum(np.abs(first_g) * np.abs(second_f - second_g)))
                        raw_rhs = raw_left + raw_right
                        identity_residual = float(abs((gram_f - gram_g) - decomposition))
                        lhs = raw_lhs / partition
                        rhs = raw_rhs / partition
                        normalized_identity_residual = identity_residual / partition
                        tolerance = absolute_tolerance + relative_tolerance * max(scale_floor, rhs)
                        check(f"{graph} site={site} beta={beta} pair=({i},{j}) decomposition", normalized_identity_residual <= tolerance, normalized_identity_residual, tolerance, "R340 instantiation")
                        check(f"{graph} site={site} beta={beta} pair=({i},{j}) bound", lhs <= rhs + tolerance, [lhs, rhs], f"lhs<=rhs+{tolerance}", "R340 instantiation")
                        rows.append({"graph": graph, "volume": volume, "source_site": site, "beta": beta, "tau_f": tau_values[0], "tau_g": tau_values[1], "i": i, "j": j, "vector_dimension": vector_dimension, "partition": partition, "raw_lhs": raw_lhs, "raw_left_term": raw_left, "raw_right_term": raw_right, "raw_rhs": raw_rhs, "normalized_lhs": lhs, "normalized_rhs": rhs, "normalized_slack": rhs - lhs, "identity_residual": identity_residual, "normalized_identity_residual": normalized_identity_residual, "tolerance": tolerance})

    expected_rows = sum(len(declaration["source_sites"]) for declaration in fixture["graphs"].values()) * len(beta_values) * len(fixture["observable_kinds"]) ** 2
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    check("finite rows", all(np.isfinite(row[key]) for row in rows for key in ("partition", "raw_lhs", "raw_rhs", "normalized_lhs", "normalized_rhs", "normalized_slack", "identity_residual", "tolerance")), len(rows), "all numeric fields finite", "numerics")
    check("scope firewall", all(not scope[field] for field in ("thermodynamic_common_os_hilbert_carrier_closed", "source_volume_cutoff_beta_uniform_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "downstream QFT gates open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-COMPLEX-OS-GRAM-PERTURBATION", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "formal_checks": [MARKER], "rows": rows, "scope": scope, "boundary": manifest["boundary"], "provenance": {"script_sha256": normalized_sha256(Path(__file__)), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN), "registry_sha256": normalized_sha256(REGISTRY)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY COMPLEX-OS-GRAM-PERTURBATION PASS {payload['passed']}/{payload['assertion_count']} rows={len(payload['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())