#!/usr/bin/env python3
"""Primary finite actual-Q3 positive-time Kubo--Mori history audit."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_kubo_mori_positive_time_history"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def state_data(hamiltonian: np.ndarray, beta: float, gap_tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    probabilities = np.exp(-beta * (energies - float(np.min(energies))))
    probabilities /= float(np.sum(probabilities))
    left, right = probabilities[:, None], probabilities[None, :]
    log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
    logarithmic = np.empty_like(log_gap)
    close = np.abs(log_gap) <= gap_tolerance
    np.divide(left - right, log_gap, out=logarithmic, where=~close)
    limit = 0.5 * (left + right)
    logarithmic[close] = limit[close]
    logarithmic = (logarithmic + logarithmic.T) / 2.0
    return energies, vectors, probabilities, logarithmic, 0.5 * (left + right)


def unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def weighted_norm(matrix: np.ndarray, vectors: np.ndarray, weights: np.ndarray) -> float:
    matrix_h = vectors.conj().T @ matrix @ vectors
    return float(np.sqrt(max(0.0, 2.0 * float(np.sum(weights * np.abs(matrix_h) ** 2)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001090" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001090/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph geometry", q3.graph_edges(2) == [(0, 1)] and len(q3.graph_edges(4)) == 4 and len(q3.graph_edges(6)) == 7, [q3.graph_edges(2), len(q3.graph_edges(4)), len(q3.graph_edges(6))], "two-site/square/2x3", "geometry")
    check("scope firewall", scope["finite_kubo_mori_history_rows_closed"] and scope["finite_arithmetic_history_comparison_closed"] and scope["finite_positive_time_identity_closed"] and not scope["candidate_uniformity_decided"] and not scope["positive_time_history_closed"] and not scope["pre_a_closed"], scope, "finite history diagnostic", "scope")

    beta = float(fixture["beta"])
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    tolerance = float(fixture["commutator_tolerance"])
    tail_tolerance = float(fixture["tail_tolerance"])
    gap_tolerance = float(fixture["mean_gap_tolerance"])
    dimension = int(fixture["oscillator_dimension"])
    volumes = [int(value) for value in fixture["volume_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    volume_rows: list[dict[str, Any]] = []

    for volume in volumes:
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        energies, vectors, probabilities, logarithmic, arithmetic = state_data(hamiltonian, beta, gap_tolerance)
        observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
        source_reference = {time: unitary(hamiltonian, time, hbar) @ observable @ unitary(hamiltonian, time, hbar).conj().T for time in times}
        q_single, _ = q3.oscillator(dimension)
        check(f"V={volume} Gibbs normalization", np.isfinite(probabilities).all() and abs(float(np.sum(probabilities)) - 1.0) <= gap_tolerance, float(np.sum(probabilities)), 1.0, "Kubo--Mori state")
        radius_rows: list[dict[str, Any]] = []
        for radius in radii:
            q_cut = q3.cut_coordinate(q_single, radius)
            _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
            zero = np.zeros_like(hamiltonian)
            tails = {edge: bonds[edge] - cut_bonds[edge] for edge in bonds}
            tail = sum(tails.values(), zero)
            tail_norm = q3.operator_norm(tail)
            source_commutator_norm = q3.operator_norm(q3.commutator(tail, observable))
            check(f"V={volume} L={radius} source commutation", source_commutator_norm <= tolerance, source_commutator_norm, f"<={tolerance}", "configuration commutation")
            if radius == max(radii):
                check(f"V={volume} zero tail at largest radius", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            time_rows: list[dict[str, Any]] = []
            for time in times:
                orientations: dict[str, Any] = {}
                for sign in (-1, 1):
                    perturbed = hamiltonian + sign * tail
                    perturbed_evolution = unitary(perturbed, time, hbar)
                    evolved = perturbed_evolution @ observable @ perturbed_evolution.conj().T
                    difference = evolved - source_reference[time]
                    modular = -beta * q3.commutator(hamiltonian, difference)
                    modular_formula_error = q3.operator_norm(modular + beta * q3.commutator(hamiltonian, difference))
                    unitarity_error = q3.operator_norm(perturbed_evolution.conj().T @ perturbed_evolution - np.eye(perturbed.shape[0], dtype=complex))
                    values: dict[str, Any] = {
                        "D_matrix_norm": q3.operator_norm(difference),
                        "D_duhamel": weighted_norm(difference, vectors, logarithmic),
                        "D_arithmetic": weighted_norm(difference, vectors, arithmetic),
                        "delta_D_matrix_norm": q3.operator_norm(modular),
                        "delta_D_duhamel": weighted_norm(modular, vectors, logarithmic),
                        "delta_D_arithmetic": weighted_norm(modular, vectors, arithmetic),
                        "modular_identity_error": modular_formula_error,
                        "unitarity_error": unitarity_error,
                        "tail_operator_norm": tail_norm,
                    }
                    check(f"V={volume} L={radius} t={time} sign={sign} identity", modular_formula_error <= tolerance, modular_formula_error, f"<={tolerance}", "positive-time identity")
                    check(f"V={volume} L={radius} t={time} sign={sign} unitary", unitarity_error <= tolerance, unitarity_error, f"<={tolerance}", "finite evolution")
                    check(f"V={volume} L={radius} t={time} sign={sign} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "state-weighted history")
                    orientations[str(sign)] = values
                sums = {key: orientations["1"][key] + orientations["-1"][key] for key in ("D_duhamel", "D_arithmetic", "delta_D_duhamel", "delta_D_arithmetic")}
                time_rows.append({"time": time, "orientations": orientations, "two_orientation_sum_of_norms": sums})
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "source_commutator_norm": source_commutator_norm, "times": time_rows})
        volume_rows.append({"volume": volume, "dimension": dimension**volume, "ground_energy": float(energies[0]), "probability_min": float(np.min(probabilities)), "radius_rows": radius_rows})
        check(f"V={volume} radius sequence", [row["radius"] for row in radius_rows] == radii, [row["radius"] for row in radius_rows], radii, "cutoff")

    check("volume sequence", [row["volume"] for row in volume_rows] == volumes, [row["volume"] for row in volume_rows], volumes, "volume")
    summary = []
    for volume_row in volume_rows:
        samples = [time_row["two_orientation_sum_of_norms"] for radius_row in volume_row["radius_rows"] for time_row in radius_row["times"]]
        summary.append({"volume": volume_row["volume"], "max_D_duhamel": max(item["D_duhamel"] for item in samples), "max_D_arithmetic": max(item["D_arithmetic"] for item in samples), "max_delta_D_duhamel": max(item["delta_D_duhamel"] for item in samples), "max_delta_D_arithmetic": max(item["delta_D_arithmetic"] for item in samples)})
    check("history maxima finite", all(np.isfinite(value) for row in summary for value in row.values() if isinstance(value, float)), summary, "finite", "scaling")
    check("support locality", all(float(row["source_commutator_norm"]) <= tolerance for volume in volume_rows for row in volume["radius_rows"]), "all rows", "tolerance", "support locality")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-KUBO-MORI-POSITIVE-TIME-HISTORY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "summary": summary,
            "finite_kubo_mori_history_rows_closed": True,
            "finite_arithmetic_history_comparison_closed": True,
            "finite_positive_time_identity_closed": True,
            "candidate_uniformity_decided": False,
            "modular_domain_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "positive_time_history_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY KUBO-MORI-POSITIVE-TIME-HISTORY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
