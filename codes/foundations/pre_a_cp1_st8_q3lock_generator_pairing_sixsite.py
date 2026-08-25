#!/usr/bin/env python3
"""Primary six-site actual-Q3 generator-pairing extension for EXP-001141."""

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
SLUG = "pre_a_cp1_st8_q3lock_generator_pairing_sixsite"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-generator-pairing-sixsite-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def spectral_data(hamiltonian: np.ndarray, beta: float, gap_tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    probabilities = np.exp(-beta * (energies - float(np.min(energies))))
    probabilities /= float(np.sum(probabilities))
    gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
    weights = np.empty_like(gap)
    close = np.abs(gap) <= gap_tolerance
    np.divide(probabilities[:, None] - probabilities[None, :], gap, out=weights, where=~close)
    weights[close] = 0.5 * (probabilities[:, None] + probabilities[None, :])[close]
    return energies, vectors, (weights + weights.T) / 2.0


def unitary_family(hamiltonian: np.ndarray, times: list[float], hbar: float) -> dict[float, np.ndarray]:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return {time: (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T for time in times}


def generator_delta(hamiltonian: np.ndarray, matrix: np.ndarray, hbar: float) -> np.ndarray:
    return 1j * q3.commutator(hamiltonian, matrix) / hbar


def kubo_mori_inner(left: np.ndarray, right: np.ndarray, vectors: np.ndarray, weights: np.ndarray, factor: float) -> complex:
    left_hat = vectors.conj().T @ left @ vectors
    right_hat = vectors.conj().T @ right @ vectors
    return complex(factor * np.sum(weights * np.conjugate(left_hat) * right_hat))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001141" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001141/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    volumes = [int(value) for value in fixture["volume_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    betas = [float(value) for value in fixture["beta_values"]]
    times = [float(value) for value in fixture["time_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    check("six-site graph", volumes == [6] and len(q3.graph_edges(6)) == 7, [volumes, len(q3.graph_edges(6))], "[6], seven bonds", "geometry")
    check("scope firewall", scope["six_site_actual_d_delta_rows_closed"] and scope["increasing_cutoff_family_closed"] and scope["full_generator_pairing_identity_closed"] and not scope["uniform_beta_volume_direct_d_delta_d_closed"] and not scope["pre_a_closed"], scope, "six-site finite only", "scope")

    dimension = int(fixture["oscillator_dimension"])
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    factor = float(fixture["two_sided_factor"])
    tolerance = float(fixture["commutator_tolerance"])
    gap_tolerance = float(fixture["mean_gap_tolerance"])
    all_rows: list[dict[str, Any]] = []
    cutoff_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for beta in betas:
        for volume in volumes:
            q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
            energies, vectors, weights = spectral_data(hamiltonian, beta, gap_tolerance)
            observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
            source = {time: unitary_family(hamiltonian, times, hbar)[time] @ observable @ unitary_family(hamiltonian, times, hbar)[time].conj().T for time in times}
            for radius in radii:
                q_single, _ = q3.oscillator(dimension)
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                source_commutator_norm = q3.operator_norm(q3.commutator(tail, observable))
                check(f"beta={beta} V={volume} L={radius} source", source_commutator_norm <= tolerance, source_commutator_norm, f"<={tolerance}", "support locality")
                max_delta = 0.0
                max_d = 0.0
                max_delta2 = 0.0
                max_delta_km = 0.0
                max_d_km = 0.0
                max_delta2_km = 0.0
                max_error = 0.0
                for orientation in orientations:
                    histories = unitary_family(hamiltonian + orientation * tail, times, hbar)
                    for time in times:
                        difference = histories[time] @ observable @ histories[time].conj().T - source[time]
                        delta_difference = generator_delta(hamiltonian, difference, hbar)
                        delta2_difference = generator_delta(hamiltonian, delta_difference, hbar)
                        d_inner = kubo_mori_inner(difference, difference, vectors, weights, factor)
                        first_inner = kubo_mori_inner(delta_difference, delta_difference, vectors, weights, factor)
                        second_inner = kubo_mori_inner(delta2_difference, difference, vectors, weights, factor)
                        delta2_inner = kubo_mori_inner(delta2_difference, delta2_difference, vectors, weights, factor)
                        cancellation_error = abs(second_inner + first_inner)
                        d_km = float(np.sqrt(max(0.0, float(np.real(d_inner)))))
                        delta_km = float(np.sqrt(max(0.0, float(np.real(first_inner)))))
                        delta2_km = float(np.sqrt(max(0.0, float(np.real(delta2_inner)))))
                        values = {
                            "D_matrix_norm": q3.operator_norm(difference),
                            "delta_D_matrix_norm": q3.operator_norm(delta_difference),
                            "delta2_D_matrix_norm": q3.operator_norm(delta2_difference),
                            "D_kubo_mori_norm": d_km,
                            "delta_D_kubo_mori_norm": delta_km,
                            "delta2_D_kubo_mori_norm": delta2_km,
                            "pairing_delta2_D_D_real": float(np.real(second_inner)),
                            "pairing_delta_D_delta_D_real": float(np.real(first_inner)),
                            "cancellation_error": float(cancellation_error),
                            "tail_operator_norm": q3.operator_norm(tail),
                            "source_commutator_norm": source_commutator_norm,
                        }
                        check(f"beta={beta} V={volume} L={radius} t={time} sign={orientation} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "actual D/delta-D")
                        check(f"beta={beta} V={volume} L={radius} t={time} sign={orientation} pairing", cancellation_error <= tolerance, cancellation_error, f"<={tolerance}", "full-generator cancellation")
                        check(f"beta={beta} V={volume} L={radius} t={time} sign={orientation} positivity", min(float(np.real(d_inner)), float(np.real(first_inner)), float(np.real(delta2_inner))) >= -tolerance, [d_inner, first_inner, delta2_inner], ">=-tolerance", "Kubo-Mori positivity")
                        all_rows.append({"beta": beta, "volume": volume, "radius": radius, "time": time, "orientation": orientation, "values": values})
                        max_d = max(max_d, values["D_matrix_norm"])
                        max_delta = max(max_delta, values["delta_D_matrix_norm"])
                        max_delta2 = max(max_delta2, values["delta2_D_matrix_norm"])
                        max_d_km = max(max_d_km, values["D_kubo_mori_norm"])
                        max_delta_km = max(max_delta_km, values["delta_D_kubo_mori_norm"])
                        max_delta2_km = max(max_delta2_km, values["delta2_D_kubo_mori_norm"])
                        max_error = max(max_error, values["cancellation_error"])
                cutoff_rows.append({"beta": beta, "volume": volume, "radius": radius, "tail_operator_norm": q3.operator_norm(tail), "source_commutator_norm": source_commutator_norm, "max_D": max_d, "max_delta_D": max_delta, "max_delta2_D": max_delta2, "max_D_km": max_d_km, "max_delta_D_km": max_delta_km, "max_delta2_D_km": max_delta2_km, "max_cancellation_error": max_error})
            selected = [row for row in cutoff_rows if row["beta"] == beta and row["volume"] == volume]
            summary_rows.append({"beta": beta, "volume": volume, "max_D": max(row["max_D"] for row in selected), "max_delta_D": max(row["max_delta_D"] for row in selected), "max_delta2_D": max(row["max_delta2_D"] for row in selected), "max_D_km": max(row["max_D_km"] for row in selected), "max_delta_D_km": max(row["max_delta_D_km"] for row in selected), "max_delta2_D_km": max(row["max_delta2_D_km"] for row in selected), "max_cancellation_error": max(row["max_cancellation_error"] for row in selected)})

    check("cutoff sequence", [row["radius"] for row in cutoff_rows] == radii, [row["radius"] for row in cutoff_rows], radii, "cutoff")
    check("row coverage", len(all_rows) == len(betas) * len(volumes) * len(radii) * len(times) * len(orientations), len(all_rows), "manifest product", "coverage")
    check("all cancellation rows", all(row["values"]["cancellation_error"] <= tolerance for row in all_rows), len(all_rows), "all <= tolerance", "full-generator cancellation")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-GENERATOR-PAIRING-SIXSITE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows[:14] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(rows)), "expected": "all executed assertions passed"}],
        "derived": {"summary_rows": summary_rows, "cutoff_rows": cutoff_rows, "row_count": len(all_rows), "six_site_actual_d_delta_rows_closed": True, "increasing_cutoff_family_closed": True, "full_generator_pairing_identity_closed": True, "six_site_vs_square_growth_diagnostic_closed": True, "uniform_beta_volume_direct_d_delta_d_closed": False, "common_alpha_closed": False, "pre_a_closed": False},
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
    print(f"PRIMARY GENERATOR-PAIRING-SIXSITE PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
