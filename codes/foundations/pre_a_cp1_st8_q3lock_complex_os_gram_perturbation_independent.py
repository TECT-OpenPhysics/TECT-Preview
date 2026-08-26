#!/usr/bin/env python3
"""Independent finite Q3 Complex Hilbert-Schmidt Gram perturbation audit for EXP-001179."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-complex-os-gram-perturbation"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
LEAN = REPO / "verification" / "lean" / "Tect" / "R340.lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"
MARKER = "finite_complex_gram_entry_perturbation"


def save_json(path: Path, payload: dict[str, Any]) -> None:
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


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=complex)
    for index in range(size - 1):
        lowering[index, index + 1] = np.sqrt(float(index + 1))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def tensor_at(local: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result: np.ndarray | None = None
    for index in range(volume):
        factor = local if index == site else identity
        result = factor if result is None else np.kron(result, factor)
    assert result is not None
    return result


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) * 0.5


def spectrum(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(hermitian(matrix))


def bond(left: np.ndarray, right: np.ndarray, parameters: dict[str, str]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    coupling = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    return coupling * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def q3_terms(edges: list[tuple[int, int]], volume: int, size: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_ops = [tensor_at(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [tensor_at(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    onsite = [p_op @ p_op / (2.0 * chi) + r * q_op @ q_op / 2.0 + g * q_op @ q_op @ q_op @ q_op / 4.0 for q_op, p_op in zip(q_ops, p_ops)]
    return onsite + [bond(q_ops[left], q_ops[right], parameters) for left, right in edges], q_single, p_single


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = spectrum(generator)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def sha_declarations(path: Path) -> list[str]:
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

    check("identity", (manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing")) == ("EXP-001179", "T-054", False), [manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing")], ["EXP-001179", "T-054", False], "provenance")
    check("graph fixture", list(fixture["graphs"]) == ["bond2", "square4", "grid2x3"], list(fixture["graphs"]), "bond2/square4/grid2x3", "fixture")
    check("scope firewall", scope["r340_complex_gram_bound_closed"] and scope["finite_q3_os_transfer_word_factorization_closed"] and not scope["thermodynamic_common_os_hilbert_carrier_closed"] and not scope["pre_a_closed"], scope, "finite bridge only", "scope")
    source_lines = LEAN.read_text(encoding="utf-8").splitlines()
    check("Lean declarations", sha_declarations(LEAN) == [MARKER], sha_declarations(LEAN), [MARKER], "Lean")
    forbidden = {token: sum(1 for line in source_lines if re.search(rf"\b{re.escape(token)}\b", line)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check("forbidden Lean tokens", all(value == 0 for value in forbidden.values()), forbidden, {token: 0 for token in forbidden}, "Lean")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    matches = [item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/R340.lean"]
    check("registry uniqueness", len(matches) == 1, len(matches), 1, "registry")
    check("registry hash", matches[0]["sha256"] == normalized_sha256(LEAN), matches[0]["sha256"], normalized_sha256(LEAN), "registry")

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
        edges = tuple(tuple(int(value) for value in edge) for edge in declaration["edges"])
        sources = tuple(int(value) for value in declaration["source_sites"])
        terms, q_single, p_single = q3_terms(list(edges), volume, dimension, parameters)
        hamiltonian = hermitian(sum(terms, np.zeros_like(terms[0])))
        energies, eigenvectors = spectrum(hamiltonian)
        shifted = energies - float(np.min(energies))
        witness = float(np.linalg.norm(hamiltonian @ terms[0] - terms[0] @ hamiltonian, ord=2))
        check(f"{graph} noncommutation witness", np.isfinite(witness) and witness >= noncommutation_floor, witness, f">={noncommutation_floor}", "Q3 dynamics")
        identity = np.eye(dimension, dtype=complex)
        observables = {
            site: {
                kind: eigenvectors.conj().T @ tensor_at(character(q_single if kind == "q" else p_single, amplitude, hbar), site, volume, identity) @ eigenvectors
                for kind in fixture["observable_kinds"]
            }
            for site in sources
        }
        for beta in beta_values:
            period = beta * hbar
            partition = float(np.sum(np.exp(-period * shifted / hbar)))
            check(f"{graph} beta={beta} partition", np.isfinite(partition) and partition > scale_floor, partition, f">{scale_floor}", "normalization")
            tau_values = tuple(fraction * period for fraction in tau_fractions)
            transfer_f = (np.exp(-(period / 2.0 - tau_values[0]) * shifted / hbar), np.exp(-tau_values[0] * shifted / hbar))
            transfer_g = (np.exp(-(period / 2.0 - tau_values[1]) * shifted / hbar), np.exp(-tau_values[1] * shifted / hbar))
            for site in sources:
                f_vectors = tuple((transfer_f[0][:, None] * observables[site][kind] * transfer_f[1][None, :]).reshape(-1) for kind in fixture["observable_kinds"])
                g_vectors = tuple((transfer_g[0][:, None] * observables[site][kind] * transfer_g[1][None, :]).reshape(-1) for kind in fixture["observable_kinds"])
                vector_dimension = len(f_vectors[0])
                check(f"{graph} site={site} beta={beta} vector shape", len({len(vector) for vector in f_vectors + g_vectors}) == 1, [len(vector) for vector in f_vectors + g_vectors], vector_dimension, "Hilbert-Schmidt")
                for i, (first_f, first_g) in enumerate(zip(f_vectors, g_vectors)):
                    for j, (second_f, second_g) in enumerate(zip(f_vectors, g_vectors)):
                        gram_f = sum(np.conj(first_f[index]) * second_f[index] for index in range(vector_dimension))
                        gram_g = sum(np.conj(first_g[index]) * second_g[index] for index in range(vector_dimension))
                        decomposition = sum(np.conj(first_f[index] - first_g[index]) * second_f[index] + np.conj(first_g[index]) * (second_f[index] - second_g[index]) for index in range(vector_dimension))
                        raw_lhs = float(abs(gram_f - gram_g))
                        raw_left = float(sum(abs(first_f[index] - first_g[index]) * abs(second_f[index]) for index in range(vector_dimension)))
                        raw_right = float(sum(abs(first_g[index]) * abs(second_f[index] - second_g[index]) for index in range(vector_dimension)))
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
    check("finite rows", all(np.isfinite(row[key]) for row in rows for key in ("partition", "raw_lhs", "raw_rhs", "normalized_lhs", "normalized_rhs", "normalized_slack", "identity_residual", "normalized_identity_residual", "tolerance")), len(rows), "all numeric fields finite", "numerics")
    check("scope firewall", all(not scope[field] for field in ("thermodynamic_common_os_hilbert_carrier_closed", "source_volume_cutoff_beta_uniform_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "downstream QFT gates open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-COMPLEX-OS-GRAM-PERTURBATION", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "formal_checks": [MARKER], "rows": rows, "scope": scope, "boundary": manifest["boundary"], "provenance": {"script_sha256": normalized_sha256(Path(__file__)), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN), "registry_sha256": normalized_sha256(REGISTRY)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT COMPLEX-OS-GRAM-PERTURBATION PASS {payload['passed']}/{payload['assertion_count']} rows={len(payload['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())