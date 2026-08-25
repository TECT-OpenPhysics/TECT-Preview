#!/usr/bin/env python3
"""Independent eigenbasis reproduction for EXP-001142."""

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
SLUG = "pre_a_cp1_st8_q3lock_finite_spectral_pairing_sum"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-spectral-pairing-sum-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"
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


def diagonal_data(hamiltonian: np.ndarray, beta: float, gap_tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    probabilities = np.exp(-beta * (energies - float(np.min(energies))))
    probabilities /= float(np.sum(probabilities))
    log_ratio = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
    mean = np.empty_like(log_ratio)
    equal = np.abs(log_ratio) <= gap_tolerance
    np.divide(probabilities[:, None] - probabilities[None, :], log_ratio, out=mean, where=~equal)
    mean[equal] = 0.5 * (probabilities[:, None] + probabilities[None, :])[equal]
    return energies, vectors, (mean + mean.T) / 2.0


def spectral_unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    phases = np.exp(-1j * time * eigenvalues / hbar)
    return (eigenvectors * phases) @ eigenvectors.conj().T


def spectral_delta(energies: np.ndarray, vectors: np.ndarray, matrix: np.ndarray, hbar: float) -> np.ndarray:
    matrix_eigen = vectors.conj().T @ matrix @ vectors
    gap = energies[:, None] - energies[None, :]
    return vectors @ (1j * gap * matrix_eigen / hbar) @ vectors.conj().T


def form(left: np.ndarray, right: np.ndarray, vectors: np.ndarray, weights: np.ndarray, factor: float) -> complex:
    left_eigen = vectors.conj().T @ left @ vectors
    right_eigen = vectors.conj().T @ right @ vectors
    return complex(factor * np.sum(weights * np.conjugate(left_eigen) * right_eigen))


def spectral_sum(matrix: np.ndarray, energies: np.ndarray, vectors: np.ndarray, weights: np.ndarray, factor: float, hbar: float) -> float:
    matrix_eigen = vectors.conj().T @ matrix @ vectors
    gap = (energies[:, None] - energies[None, :]) / hbar
    return float(np.real(np.sum(factor * weights * gap**2 * np.abs(matrix_eigen) ** 2)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    volumes = [int(value) for value in fixture["volume_values"]]
    betas = [float(value) for value in fixture["beta_values"]]
    times = [float(value) for value in fixture["time_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    dimension = int(fixture["oscillator_dimension"])
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    factor = float(fixture["two_sided_factor"])
    tolerance = float(fixture["commutator_tolerance"])
    spectral_tolerance = float(fixture["spectral_sum_tolerance"])
    gap_tolerance = float(fixture["mean_gap_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("provenance", manifest["exploration_id"] == "EXP-001142" and manifest["claim_bearing"] is False, manifest["exploration_id"], "EXP-001142/nonbearing", "provenance")
    check("geometry", volumes == [2, 4, 6] and [len(q3.graph_edges(value)) for value in volumes] == [1, 4, 7], volumes, "edge/square/six-site", "geometry")
    check("scope firewall", scope["finite_spectral_sum_identity_closed"] and scope["nonnegative_spectral_second_moment_closed"] and not scope["uniform_beta_volume_direct_d_delta_d_closed"] and not scope["pre_a_closed"], scope, "finite spectral identity only", "scope")

    rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for volume in volumes:
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        for beta in betas:
            energies, vectors, weights = diagonal_data(hamiltonian, beta, gap_tolerance)
            observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
            reference = {time: spectral_unitary(hamiltonian, time, hbar) @ observable @ spectral_unitary(hamiltonian, time, hbar).conj().T for time in times}
            for radius in radii:
                q_single, _ = q3.oscillator(dimension)
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                source_commutator_norm = q3.operator_norm(q3.commutator(tail, observable))
                check(f"V={volume} beta={beta} radius={radius} source", source_commutator_norm <= tolerance, source_commutator_norm, f"<={tolerance}", "support locality")
                for time in times:
                    for orientation in orientations:
                        evolution = spectral_unitary(hamiltonian + orientation * tail, time, hbar)
                        difference = evolution @ observable @ evolution.conj().T - reference[time]
                        delta_difference = spectral_delta(energies, vectors, difference, hbar)
                        delta2_difference = spectral_delta(energies, vectors, delta_difference, hbar)
                        d_inner = form(difference, difference, vectors, weights, factor)
                        first_inner = form(delta_difference, delta_difference, vectors, weights, factor)
                        second_inner = form(delta2_difference, difference, vectors, weights, factor)
                        delta2_inner = form(delta2_difference, delta2_difference, vectors, weights, factor)
                        moment = spectral_sum(difference, energies, vectors, weights, factor, hbar)
                        identity_error = abs(second_inner + first_inner)
                        spectral_error = abs(float(np.real(first_inner)) - moment)
                        signed_spectral_error = abs(float(np.real(second_inner)) + moment)
                        values = {
                            "D_km_norm": float(np.sqrt(max(0.0, float(np.real(d_inner))))),
                            "delta_D_km_norm": float(np.sqrt(max(0.0, float(np.real(first_inner))))),
                            "delta2_D_km_norm": float(np.sqrt(max(0.0, float(np.real(delta2_inner))))),
                            "spectral_second_moment": moment,
                            "pairing_delta2_D_D_real": float(np.real(second_inner)),
                            "pairing_delta_D_delta_D_real": float(np.real(first_inner)),
                            "pairing_identity_error": float(identity_error),
                            "spectral_sum_error": float(spectral_error),
                            "signed_spectral_error": float(signed_spectral_error),
                            "source_commutator_norm": source_commutator_norm,
                            "D_matrix_norm": q3.operator_norm(difference),
                            "delta_D_matrix_norm": q3.operator_norm(delta_difference),
                        }
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "spectral rows")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} pairing", identity_error <= tolerance, identity_error, f"<={tolerance}", "full-generator pairing")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} spectral", spectral_error <= spectral_tolerance and signed_spectral_error <= spectral_tolerance, [spectral_error, signed_spectral_error], f"<={spectral_tolerance}", "spectral sum")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} positivity", moment >= -spectral_tolerance and float(np.real(first_inner)) >= -spectral_tolerance and float(np.real(delta2_inner)) >= -spectral_tolerance, [moment, first_inner, delta2_inner], ">=-tolerance", "nonnegative spectral moment")
                        rows.append({"volume": volume, "beta": beta, "radius": radius, "time": time, "orientation": orientation, "values": values})
            selected = [row for row in rows if row["volume"] == volume and row["beta"] == beta]
            summary_rows.append({"volume": volume, "beta": beta, "max_D_km_norm": max(row["values"]["D_km_norm"] for row in selected), "max_delta_D_km_norm": max(row["values"]["delta_D_km_norm"] for row in selected), "max_spectral_second_moment": max(row["values"]["spectral_second_moment"] for row in selected), "max_pairing_identity_error": max(row["values"]["pairing_identity_error"] for row in selected), "max_spectral_sum_error": max(row["values"]["spectral_sum_error"] for row in selected)})

    expected_rows = len(volumes) * len(betas) * len(radii) * len(times) * len(orientations)
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SPECTRAL-PAIRING-SUM", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks[:16] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}], "derived": {"summary_rows": summary_rows, "row_count": len(rows), "finite_spectral_sum_identity_closed": True, "nonnegative_spectral_second_moment_closed": True, "edge_square_sixsite_rows_closed": True, "two_orientation_history_closed": True, "uniform_beta_volume_direct_d_delta_d_closed": False, "common_core_spectral_tail_closed": False, "common_alpha_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-SPECTRAL-PAIRING-SUM PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
