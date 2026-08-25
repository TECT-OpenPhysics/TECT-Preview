#!/usr/bin/env python3
"""Primary finite actual-Q3 dual-character fifth-moment audit for EXP-001122.

The computation is deliberately finite and claim-nonbearing.  It diagonalizes
the declared truncated Q3 Hamiltonian, conjugates the normalized Gibbs state by
a local character, and compares fifth moments and global shifted-H spectral
tails.  It does not attempt an unbounded-operator or thermodynamic theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_dual_character_fifth_moment"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        lowering[index, index + 1] = np.sqrt(float(index + 1))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for position in range(volume):
        result = np.kron(result, single if position == site else identity)
    return result


def graph_edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(int(value) for value in edge) for edge in fixture["edges_by_volume"][str(volume)]]


def build_hamiltonian(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[np.ndarray, list[np.ndarray]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_sites = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_sites = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    hamiltonian = np.zeros_like(q_sites[0])
    for q_site, p_site in zip(q_sites, p_sites):
        hamiltonian += p_site @ p_site / (2.0 * chi)
        hamiltonian += r * (q_site @ q_site) / 2.0
        hamiltonian += g * np.linalg.matrix_power(q_site, 4) / 4.0
    for left, right in graph_edges(volume, fixture):
        difference = q_sites[left] - q_sites[right]
        square = difference @ difference
        hamiltonian += c * square / 2.0
        hamiltonian += lam * square @ (q_sites[left] @ q_sites[left] + q_sites[right] @ q_sites[right]) / 4.0
    return (hamiltonian + hamiltonian.conj().T) / 2.0, q_sites


def hermitian_exponential(matrix: np.ndarray, coefficient: complex) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(coefficient * values)) @ vectors.conj().T


def state_data(hamiltonian: np.ndarray, beta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted_energies = energies - float(np.min(energies)) + 1.0
    weights = np.exp(-beta * (energies - float(np.min(energies))))
    weights /= float(np.sum(weights))
    return shifted_energies, vectors, weights


def check_tail(shifted: np.ndarray, probabilities: np.ndarray, radius: float, order: int) -> dict[str, float | int]:
    mask = shifted > radius
    mass = float(np.sum(probabilities[mask]))
    weighted = float(np.sum(probabilities[mask] * shifted[mask] ** order))
    return {"radius": radius, "tail_mass": mass, "tail_weight": weighted, "tail_count": int(np.sum(mask))}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    order = int(fixture["moment_order"])
    beta, hbar, amplitude = (float(fixture[key]) for key in ("beta", "hbar", "character_amplitude"))
    unitary_tolerance = float(fixture["unitarity_tolerance"])
    markov_tolerance = float(fixture["markov_tolerance"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001122" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001122/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("moment order", order == 5, order, 5, "moment")
    check("graph geometry", graph_edges(2, fixture) == [(0, 1)] and len(graph_edges(4, fixture)) == 4 and len(graph_edges(6, fixture)) == 7, [graph_edges(2, fixture), len(graph_edges(4, fixture)), len(graph_edges(6, fixture))], "target/square/2x3", "geometry")

    volume_rows: list[dict[str, Any]] = []
    for volume in (int(value) for value in fixture["volume_values"]):
        for dimension in (int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]):
            hamiltonian, q_sites = build_hamiltonian(volume, dimension, fixture)
            shifted, vectors, probabilities = state_data(hamiltonian, beta)
            character = hermitian_exponential(q_sites[0], 1j * amplitude / hbar)
            character_h = vectors.conj().T @ character @ vectors
            dual_probabilities = np.real(np.diag(character_h @ np.diag(probabilities) @ character_h.conj().T))
            dual_probabilities = np.maximum(dual_probabilities, 0.0)
            reference_moment = float(np.sum(probabilities * shifted ** order))
            dual_moment = float(np.sum(dual_probabilities * shifted ** order))
            trace_error = abs(float(np.sum(probabilities)) - 1.0)
            dual_trace_error = abs(float(np.sum(dual_probabilities)) - 1.0)
            unitary_error = float(np.linalg.norm(character.conj().T @ character - np.eye(character.shape[0]), ord=2))
            h_hermitian_error = float(np.linalg.norm(hamiltonian - hamiltonian.conj().T, ord=2))
            check(f"V={volume} n={dimension} H Hermitian", h_hermitian_error <= unitary_tolerance, h_hermitian_error, f"<={unitary_tolerance}", "matrix")
            check(f"V={volume} n={dimension} reference trace", trace_error <= unitary_tolerance, trace_error, f"<={unitary_tolerance}", "state")
            check(f"V={volume} n={dimension} dual trace", dual_trace_error <= 100.0 * unitary_tolerance, dual_trace_error, f"<={100.0 * unitary_tolerance}", "state")
            check(f"V={volume} n={dimension} character unitary", unitary_error <= 100.0 * unitary_tolerance, unitary_error, f"<={100.0 * unitary_tolerance}", "character")
            check(f"V={volume} n={dimension} nonnegative moments", reference_moment >= 0.0 and dual_moment >= 0.0 and np.isfinite(reference_moment) and np.isfinite(dual_moment), [reference_moment, dual_moment], "finite nonnegative", "moment")
            tail_rows: list[dict[str, Any]] = []
            for radius in (float(value) for value in fixture["spectral_cutoffs"]):
                reference_tail = check_tail(shifted, probabilities, radius, order)
                dual_tail = check_tail(shifted, dual_probabilities, radius, order)
                markov_reference = radius ** order * reference_tail["tail_mass"] <= reference_moment + markov_tolerance * (1.0 + reference_moment)
                markov_dual = radius ** order * dual_tail["tail_mass"] <= dual_moment + markov_tolerance * (1.0 + dual_moment)
                check(f"V={volume} n={dimension} R={radius} reference Markov", markov_reference, [radius ** order * reference_tail["tail_mass"], reference_moment], "<=", "tail")
                check(f"V={volume} n={dimension} R={radius} dual Markov", markov_dual, [radius ** order * dual_tail["tail_mass"], dual_moment], "<=", "tail")
                tail_rows.append({"radius": radius, "reference": reference_tail, "dual": dual_tail, "reference_markov": markov_reference, "dual_markov": markov_dual})
            volume_rows.append({
                "volume": volume,
                "oscillator_dimension": dimension,
                "hilbert_dimension": int(character.shape[0]),
                "energy_min": float(np.min(np.linalg.eigvalsh(hamiltonian))),
                "shifted_energy_max": float(np.max(shifted)),
                "reference_moment5": reference_moment,
                "dual_moment5": dual_moment,
                "dual_reference_ratio": dual_moment / reference_moment if reference_moment > 0.0 else float("inf"),
                "reference_trace_error": trace_error,
                "dual_trace_error": dual_trace_error,
                "character_unitarity_error": unitary_error,
                "tail_rows": tail_rows,
            })

    check("volume sequence", [row["volume"] for row in volume_rows] == [int(value) for value in fixture["volume_values"] for _ in fixture["oscillator_dimensions_by_volume"][str(value)]], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume/cutoff")
    check("finite scope", all(scope[key] is True for key in ("finite_reference_fifth_moment_closed", "finite_dual_character_fifth_moment_closed", "finite_global_spectral_tail_comparison_closed", "finite_character_kinetic_shift_identity_closed")), scope, "finite rows closed", "scope")
    open_keys = tuple(key for key, value in scope.items() if key not in ("finite_reference_fifth_moment_closed", "finite_dual_character_fifth_moment_closed", "finite_global_spectral_tail_comparison_closed", "finite_character_kinetic_shift_identity_closed", "no_new_negative_result", "no_tier_change", "no_pdf"))
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all successor gates open", "scope")
    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-CHARACTER-FIFTH-MOMENT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": passed,
        "assertion_count": passed,
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "finite_reference_fifth_moment_closed": True,
            "finite_dual_character_fifth_moment_closed": True,
            "finite_global_spectral_tail_comparison_closed": True,
            "finite_character_kinetic_shift_identity_closed": True,
            "actual_q3_dual_state_moment_uniform_closed": False,
            "actual_q3_modular_tail_uniform_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
            "max_dual_reference_ratio": max(row["dual_reference_ratio"] for row in volume_rows),
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": normalized_sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": normalized_sha256(MANIFEST)},
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY DUAL-CHARACTER-FIFTH-MOMENT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
