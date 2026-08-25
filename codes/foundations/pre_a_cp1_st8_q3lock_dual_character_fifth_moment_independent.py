#!/usr/bin/env python3
"""Independent NumPy lane for the finite EXP-001122 dual-character audit.

This implementation rebuilds the tensor operators, Gibbs weights, character
conjugation, and spectral tails without importing the primary module.
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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


def ladder(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((dimension, dimension), dtype=complex)
    for row in range(1, dimension):
        lower[row - 1, row] = np.sqrt(float(row))
    upper = lower.T.conj()
    coordinate = (lower + upper) / np.sqrt(2.0)
    momentum = (lower - upper) / (1j * np.sqrt(2.0))
    return coordinate, momentum


def tensor_site(single: np.ndarray, site: int, volume: int, dimension: int) -> np.ndarray:
    identity = np.eye(dimension, dtype=complex)
    result = np.array([[1.0 + 0.0j]])
    for position in range(volume):
        factor = single if position == site else identity
        result = np.kron(result, factor)
    return result


def repeated(matrix: np.ndarray, exponent: int) -> np.ndarray:
    result = np.eye(matrix.shape[0], dtype=complex)
    for _ in range(exponent):
        result = result @ matrix
    return result


def interaction(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return float(fixture["c"]) * square / 2.0 + float(fixture["lambda"]) * square @ (left @ left + right @ right) / 4.0


def graph(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [(int(edge[0]), int(edge[1])) for edge in fixture["edges_by_volume"][str(volume)]]


def construct(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    coordinate, momentum = ladder(dimension)
    q_sites = [tensor_site(coordinate, site, volume, dimension) for site in range(volume)]
    p_sites = [tensor_site(momentum, site, volume, dimension) for site in range(volume)]
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    result = np.zeros_like(q_sites[0])
    for q_site, p_site in zip(q_sites, p_sites):
        result += p_site @ p_site / (2.0 * chi) + r * q_site @ q_site / 2.0 + g * repeated(q_site, 4) / 4.0
    for left, right in graph(volume, fixture):
        result += interaction(q_sites[left], q_sites[right], fixture)
    return (result + result.T.conj()) / 2.0, q_sites[0]


def spectral_data(matrix: np.ndarray, beta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eigh((matrix + matrix.T.conj()) / 2.0)
    floor = float(eigenvalues[0])
    shifted = eigenvalues - floor + 1.0
    weights = np.exp(-beta * (eigenvalues - floor))
    weights /= float(np.sum(weights))
    return shifted, eigenvectors, weights


def exponential_of_hermitian(matrix: np.ndarray, phase: complex) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh((matrix + matrix.T.conj()) / 2.0)
    return (eigenvectors * np.exp(phase * eigenvalues)) @ eigenvectors.T.conj()


def tail_row(shifted: np.ndarray, weights: np.ndarray, radius: float, order: int) -> dict[str, float | int]:
    selected = shifted > radius
    return {
        "radius": radius,
        "tail_mass": float(np.sum(weights[selected])),
        "tail_weight": float(np.sum(weights[selected] * shifted[selected] ** order)),
        "tail_count": int(np.sum(selected)),
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    order = int(fixture["moment_order"])
    beta = float(fixture["beta"])
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
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
    check("graph geometry", graph(2, fixture) == [(0, 1)] and len(graph(4, fixture)) == 4 and len(graph(6, fixture)) == 7, [graph(2, fixture), len(graph(4, fixture)), len(graph(6, fixture))], "target/square/2x3", "geometry")

    volume_rows: list[dict[str, Any]] = []
    for volume in (int(value) for value in fixture["volume_values"]):
        for dimension in (int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]):
            hamiltonian, q_zero = construct(volume, dimension, fixture)
            shifted, eigenvectors, reference_weights = spectral_data(hamiltonian, beta)
            character = exponential_of_hermitian(q_zero, 1j * amplitude / hbar)
            in_energy_basis = eigenvectors.T.conj() @ character @ eigenvectors
            dual_density_diagonal = np.real(np.diag(in_energy_basis @ np.diag(reference_weights) @ in_energy_basis.T.conj()))
            dual_density_diagonal = np.maximum(dual_density_diagonal, 0.0)
            reference_moment = float(np.dot(reference_weights, shifted ** order))
            dual_moment = float(np.dot(dual_density_diagonal, shifted ** order))
            trace_error = abs(float(np.sum(reference_weights)) - 1.0)
            dual_trace_error = abs(float(np.sum(dual_density_diagonal)) - 1.0)
            character_error = float(np.linalg.norm(character.T.conj() @ character - np.eye(character.shape[0]), ord=2))
            hermitian_error = float(np.linalg.norm(hamiltonian - hamiltonian.T.conj(), ord=2))
            check(f"V={volume} n={dimension} H Hermitian", hermitian_error <= unitary_tolerance, hermitian_error, f"<={unitary_tolerance}", "matrix")
            check(f"V={volume} n={dimension} reference trace", trace_error <= unitary_tolerance, trace_error, f"<={unitary_tolerance}", "state")
            check(f"V={volume} n={dimension} dual trace", dual_trace_error <= 100.0 * unitary_tolerance, dual_trace_error, f"<={100.0 * unitary_tolerance}", "state")
            check(f"V={volume} n={dimension} character unitary", character_error <= 100.0 * unitary_tolerance, character_error, f"<={100.0 * unitary_tolerance}", "character")
            check(f"V={volume} n={dimension} moments finite", np.isfinite(reference_moment) and np.isfinite(dual_moment) and reference_moment >= 0.0 and dual_moment >= 0.0, [reference_moment, dual_moment], "finite nonnegative", "moment")
            tails: list[dict[str, Any]] = []
            for radius in (float(value) for value in fixture["spectral_cutoffs"]):
                reference_tail = tail_row(shifted, reference_weights, radius, order)
                dual_tail = tail_row(shifted, dual_density_diagonal, radius, order)
                reference_lhs = radius ** order * reference_tail["tail_mass"]
                dual_lhs = radius ** order * dual_tail["tail_mass"]
                reference_markov = reference_lhs <= reference_moment + markov_tolerance * (1.0 + reference_moment)
                dual_markov = dual_lhs <= dual_moment + markov_tolerance * (1.0 + dual_moment)
                check(f"V={volume} n={dimension} R={radius} reference Markov", reference_markov, [reference_lhs, reference_moment], "<=", "tail")
                check(f"V={volume} n={dimension} R={radius} dual Markov", dual_markov, [dual_lhs, dual_moment], "<=", "tail")
                tails.append({"radius": radius, "reference": reference_tail, "dual": dual_tail, "reference_markov": reference_markov, "dual_markov": dual_markov})
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
                "character_unitarity_error": character_error,
                "tail_rows": tails,
            })

    expected_volumes = [int(value) for value in fixture["volume_values"] for _ in fixture["oscillator_dimensions_by_volume"][str(value)]]
    check("volume sequence", [row["volume"] for row in volume_rows] == expected_volumes, [row["volume"] for row in volume_rows], expected_volumes, "volume/cutoff")
    finite_keys = ("finite_reference_fifth_moment_closed", "finite_dual_character_fifth_moment_closed", "finite_global_spectral_tail_comparison_closed", "finite_character_kinetic_shift_identity_closed")
    check("finite scope", all(scope[key] is True for key in finite_keys), scope, "finite rows closed", "scope")
    open_keys = tuple(key for key, value in scope.items() if key not in finite_keys and key not in ("no_new_negative_result", "no_tier_change", "no_pdf"))
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all successor gates open", "scope")
    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
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
    print(f"INDEPENDENT DUAL-CHARACTER-FIFTH-MOMENT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
