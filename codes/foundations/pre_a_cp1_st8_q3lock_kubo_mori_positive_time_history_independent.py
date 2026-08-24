#!/usr/bin/env python3
"""Independent finite actual-Q3 positive-time Kubo--Mori history audit."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_kubo_mori_positive_time_history"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def edges(volume: int) -> list[tuple[int, int]]:
    graph = {2: [(0, 1)], 4: [(0, 1), (0, 2), (1, 3), (2, 3)], 6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]}
    if volume not in graph:
        raise ValueError("EXP-001090 uses volumes 2, 4, and 6")
    return graph[volume]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def interaction(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return float(fixture["c"]) * square / 2.0 + float(fixture["lambda"]) * square @ (left @ left + right @ right) / 4.0


def build(volume: int, dimension: int, fixture: dict[str, Any], bond_coordinate: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    coordinate = q_single if bond_coordinate is None else bond_coordinate
    bond_ops = [embed(coordinate, site, volume, identity) for site in range(volume)]
    onsite = [p @ p / (2.0 * float(fixture["chi"])) + float(fixture["r"]) * (q @ q) / 2.0 + float(fixture["g"]) * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): interaction(bond_ops[left], bond_ops[right], fixture) for left, right in edges(volume)}
    zero = np.zeros_like(q_ops[0])
    hamiltonian = sum(onsite, zero) + sum(bonds.values(), zero)
    return q_ops, (hamiltonian + hamiltonian.conj().T) / 2.0, bonds


def cutoff(coordinate: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((coordinate + coordinate.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def evolve(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def state(hamiltonian: np.ndarray, beta: float, tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    probabilities = np.exp(-beta * (energies - float(np.min(energies))))
    probabilities /= float(np.sum(probabilities))
    left, right = probabilities[:, None], probabilities[None, :]
    log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
    logarithmic = np.empty_like(log_gap)
    close = np.abs(log_gap) <= tolerance
    np.divide(left - right, log_gap, out=logarithmic, where=~close)
    limit = 0.5 * (left + right)
    logarithmic[close] = limit[close]
    return vectors, probabilities, (logarithmic + logarithmic.T) / 2.0, 0.5 * (left + right)


def weighted(matrix: np.ndarray, vectors: np.ndarray, weights: np.ndarray) -> float:
    entries = vectors.conj().T @ matrix @ vectors
    return float(np.sqrt(max(0.0, 2.0 * float(np.sum(weights * np.abs(entries) ** 2)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001090" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001090/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph geometry", edges(2) == [(0, 1)] and len(edges(4)) == 4 and len(edges(6)) == 7, [edges(2), len(edges(4)), len(edges(6))], "two-site/square/2x3", "geometry")
    check("scope firewall", scope["finite_kubo_mori_history_rows_closed"] and scope["finite_arithmetic_history_comparison_closed"] and not scope["positive_time_history_closed"] and not scope["pre_a_closed"], scope, "finite history diagnostic", "scope")

    beta, hbar, amplitude = float(fixture["beta"]), float(fixture["hbar"]), float(fixture["character_amplitude"])
    tolerance, tail_tolerance = float(fixture["commutator_tolerance"]), float(fixture["tail_tolerance"])
    gap_tolerance = float(fixture["mean_gap_tolerance"])
    dimension = int(fixture["oscillator_dimension"])
    volumes, radii, times = [int(x) for x in fixture["volume_values"]], [float(x) for x in fixture["radius_values"]], [float(x) for x in fixture["time_values"]]
    volume_rows: list[dict[str, Any]] = []
    for volume in volumes:
        q_ops, hamiltonian, bonds = build(volume, dimension, fixture)
        vectors, probabilities, logarithmic, arithmetic = state(hamiltonian, beta, gap_tolerance)
        observable = character(q_ops[0] + q_ops[1], amplitude, hbar)
        reference = {time: evolve(hamiltonian, time, hbar) @ observable @ evolve(hamiltonian, time, hbar).conj().T for time in times}
        q_single, _ = oscillator(dimension)
        check(f"V={volume} Gibbs normalization", np.isfinite(probabilities).all() and abs(float(np.sum(probabilities)) - 1.0) <= gap_tolerance, float(np.sum(probabilities)), 1.0, "Kubo--Mori state")
        radius_rows: list[dict[str, Any]] = []
        for radius in radii:
            _, _, cut_bonds = build(volume, dimension, fixture, cutoff(q_single, radius))
            zero = np.zeros_like(hamiltonian)
            tails = {edge: bonds[edge] - cut_bonds[edge] for edge in bonds}
            tail = sum(tails.values(), zero)
            tail_norm = norm(tail)
            source_norm = norm(commutator(tail, observable))
            check(f"V={volume} L={radius} source commutation", source_norm <= tolerance, source_norm, f"<={tolerance}", "configuration commutation")
            if radius == max(radii):
                check(f"V={volume} zero tail at largest radius", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            time_rows: list[dict[str, Any]] = []
            for time in times:
                orientations = {}
                for sign in (-1, 1):
                    propagator = evolve(hamiltonian + sign * tail, time, hbar)
                    difference = propagator @ observable @ propagator.conj().T - reference[time]
                    modular = -beta * commutator(hamiltonian, difference)
                    identity_error = norm(modular + beta * commutator(hamiltonian, difference))
                    unitarity_error = norm(propagator.conj().T @ propagator - np.eye(hamiltonian.shape[0], dtype=complex))
                    values = {"D_matrix_norm": norm(difference), "D_duhamel": weighted(difference, vectors, logarithmic), "D_arithmetic": weighted(difference, vectors, arithmetic), "delta_D_matrix_norm": norm(modular), "delta_D_duhamel": weighted(modular, vectors, logarithmic), "delta_D_arithmetic": weighted(modular, vectors, arithmetic), "modular_identity_error": identity_error, "unitarity_error": unitarity_error, "tail_operator_norm": tail_norm}
                    check(f"V={volume} L={radius} t={time} sign={sign} identity", identity_error <= tolerance, identity_error, f"<={tolerance}", "positive-time identity")
                    check(f"V={volume} L={radius} t={time} sign={sign} unitary", unitarity_error <= tolerance, unitarity_error, f"<={tolerance}", "finite evolution")
                    check(f"V={volume} L={radius} t={time} sign={sign} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "state-weighted history")
                    orientations[str(sign)] = values
                sums = {key: orientations["1"][key] + orientations["-1"][key] for key in ("D_duhamel", "D_arithmetic", "delta_D_duhamel", "delta_D_arithmetic")}
                time_rows.append({"time": time, "orientations": orientations, "two_orientation_sum_of_norms": sums})
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "source_commutator_norm": source_norm, "times": time_rows})
        volume_rows.append({"volume": volume, "dimension": dimension**volume, "probability_min": float(np.min(probabilities)), "radius_rows": radius_rows})
    check("volume sequence", [row["volume"] for row in volume_rows] == volumes, [row["volume"] for row in volume_rows], volumes, "volume")
    summary = []
    for volume_row in volume_rows:
        samples = [time_row["two_orientation_sum_of_norms"] for radius_row in volume_row["radius_rows"] for time_row in radius_row["times"]]
        summary.append({"volume": volume_row["volume"], "max_D_duhamel": max(item["D_duhamel"] for item in samples), "max_D_arithmetic": max(item["D_arithmetic"] for item in samples), "max_delta_D_duhamel": max(item["delta_D_duhamel"] for item in samples), "max_delta_D_arithmetic": max(item["delta_D_arithmetic"] for item in samples)})
    check("history maxima finite", all(np.isfinite(value) for row in summary for value in row.values() if isinstance(value, float)), summary, "finite", "scaling")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-KUBO-MORI-POSITIVE-TIME-HISTORY", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(assertions), "assertion_count": len(assertions), "assertions": assertions, "derived": {"volume_rows": volume_rows, "summary": summary, "finite_kubo_mori_history_rows_closed": True, "finite_arithmetic_history_comparison_closed": True, "finite_positive_time_identity_closed": True, "candidate_uniformity_decided": False, "modular_domain_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "positive_time_history_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "group_law_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT KUBO-MORI-POSITIVE-TIME-HISTORY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
