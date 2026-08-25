#!/usr/bin/env python3
"""Independent eigenbasis energy-moment reproduction for EXP-001143."""

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
SLUG = "pre_a_cp1_st8_q3lock_finite_energy_moment_transfer"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-energy-moment-transfer-manifest.json"
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


def diagonal_data(hamiltonian: np.ndarray, beta: float, gap_tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted = eigenvalues - float(np.min(eigenvalues))
    probabilities = np.exp(-beta * shifted)
    probabilities /= float(np.sum(probabilities))
    log_ratio = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
    mean = np.empty_like(log_ratio)
    equal = np.abs(log_ratio) <= gap_tolerance
    np.divide(probabilities[:, None] - probabilities[None, :], log_ratio, out=mean, where=~equal)
    mean[equal] = 0.5 * (probabilities[:, None] + probabilities[None, :])[equal]
    return eigenvalues, eigenvectors, (mean + mean.T) / 2.0, probabilities


def spectral_unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (eigenvectors * np.exp(-1j * time * eigenvalues / hbar)) @ eigenvectors.conj().T


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
    commutator_tolerance = float(fixture["commutator_tolerance"])
    transfer_tolerance = float(fixture["transfer_tolerance"])
    mean_gap_tolerance = float(fixture["mean_gap_tolerance"])
    shift_constant = float(fixture["shift_constant"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("provenance", manifest["exploration_id"] == "EXP-001143" and manifest["claim_bearing"] is False, manifest["exploration_id"], "EXP-001143/nonbearing", "provenance")
    check("geometry", volumes == [2, 4, 6] and [len(q3.graph_edges(value)) for value in volumes] == [1, 4, 7], volumes, "edge/square/six-site", "geometry")
    check("scope firewall", scope["finite_energy_moment_transfer_closed"] and scope["termwise_arithmetic_mean_bound_closed"] and not scope["uniform_local_M2_common_core_closed"] and not scope["pre_a_closed"], scope, "finite transfer only", "scope")

    rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for volume in volumes:
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        for beta in betas:
            eigenvalues, eigenvectors, mean_weights, probabilities = diagonal_data(hamiltonian, beta, mean_gap_tolerance)
            shifted = eigenvalues - float(np.min(eigenvalues)) + shift_constant
            m2 = float(np.dot(probabilities, shifted**2))
            check(f"V={volume} beta={beta} shifted energy", float(np.min(shifted)) >= shift_constant - transfer_tolerance, float(np.min(shifted)), f">={shift_constant}", "energy moment")
            mean_slack = 0.5 * (probabilities[:, None] + probabilities[None, :]) - mean_weights
            check(f"V={volume} beta={beta} mean bound", float(np.min(mean_slack)) >= -mean_gap_tolerance, float(np.min(mean_slack)), ">=-tolerance", "Kubo-Mori weights")
            observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
            reference = {time: spectral_unitary(hamiltonian, time, hbar) @ observable @ spectral_unitary(hamiltonian, time, hbar).conj().T for time in times}
            for radius in radii:
                q_single, _ = q3.oscillator(dimension)
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                source_commutator_norm = q3.operator_norm(q3.commutator(tail, observable))
                check(f"V={volume} beta={beta} radius={radius} source", source_commutator_norm <= commutator_tolerance, source_commutator_norm, f"<={commutator_tolerance}", "support locality")
                for time in times:
                    for orientation in orientations:
                        evolution = spectral_unitary(hamiltonian + orientation * tail, time, hbar)
                        difference = evolution @ observable @ evolution.conj().T - reference[time]
                        matrix_eigen = eigenvectors.conj().T @ difference @ eigenvectors
                        gap = (eigenvalues[:, None] - eigenvalues[None, :]) / hbar
                        moment = float(np.real(np.sum(factor * mean_weights * gap**2 * np.abs(matrix_eigen) ** 2)))
                        op_norm = float(np.linalg.svd(difference, compute_uv=False)[0])
                        hs_norm = float(np.linalg.norm(difference, ord="fro"))
                        gap_slack = 2.0 * (shifted[:, None] ** 2 + shifted[None, :] ** 2) - (shifted[:, None] - shifted[None, :]) ** 2
                        candidate_bound = float(8.0 * m2 * op_norm**2)
                        safe_bound = float(8.0 * m2 * hs_norm**2)
                        values = {
                            "M2": m2,
                            "spectral_second_moment": moment,
                            "D_operator_norm": op_norm,
                            "D_hilbert_schmidt_norm": hs_norm,
                            "candidate_operator_bound": candidate_bound,
                            "safe_hilbert_schmidt_bound": safe_bound,
                            "operator_transfer_ratio": moment / max(m2 * op_norm**2, np.finfo(float).tiny),
                            "hilbert_schmidt_transfer_ratio": moment / max(m2 * hs_norm**2, np.finfo(float).tiny),
                            "source_commutator_norm": source_commutator_norm,
                            "min_gap_square_slack": float(np.min(gap_slack)),
                            "min_mean_slack": float(np.min(mean_slack)),
                        }
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "energy-moment rows")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} termwise", values["min_gap_square_slack"] >= -transfer_tolerance and values["min_mean_slack"] >= -mean_gap_tolerance, [values["min_gap_square_slack"], values["min_mean_slack"]], ">=-tolerance", "termwise arithmetic bounds")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} safe transfer", moment >= -transfer_tolerance and moment <= safe_bound + transfer_tolerance, [moment, safe_bound], "0<=S<=safe bound", "finite Hilbert-Schmidt transfer")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} operator candidate", moment <= candidate_bound + transfer_tolerance, [moment, candidate_bound], "S<=candidate bound on this row", "finite operator-norm diagnostic")
                        rows.append({"volume": volume, "beta": beta, "radius": radius, "time": time, "orientation": orientation, "values": values})
            selected = [row for row in rows if row["volume"] == volume and row["beta"] == beta]
            summary_rows.append({
                "volume": volume,
                "beta": beta,
                "M2": m2,
                "max_spectral_second_moment": max(row["values"]["spectral_second_moment"] for row in selected),
                "max_operator_candidate_bound": max(row["values"]["candidate_operator_bound"] for row in selected),
                "max_safe_hilbert_schmidt_bound": max(row["values"]["safe_hilbert_schmidt_bound"] for row in selected),
                "max_operator_transfer_ratio": max(row["values"]["operator_transfer_ratio"] for row in selected),
                "max_hilbert_schmidt_transfer_ratio": max(row["values"]["hilbert_schmidt_transfer_ratio"] for row in selected),
                "min_gap_square_slack": min(row["values"]["min_gap_square_slack"] for row in selected),
                "min_mean_slack": min(row["values"]["min_mean_slack"] for row in selected),
            })

    expected_rows = len(volumes) * len(betas) * len(radii) * len(times) * len(orientations)
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ENERGY-MOMENT-TRANSFER",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:20] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "derived": {
            "summary_rows": summary_rows,
            "row_count": len(rows),
            "finite_energy_moment_transfer_closed": True,
            "termwise_arithmetic_mean_bound_closed": True,
            "actual_q3_rows_closed": True,
            "two_orientation_history_closed": True,
            "finite_hilbert_schmidt_transfer_closed": True,
            "finite_operator_norm_candidate_rows_closed": True,
            "general_operator_norm_transfer_theorem_closed": False,
            "uniform_local_M2_common_core_closed": False,
            "uniform_beta_volume_direct_d_delta_d_closed": False,
            "modular_domain_transfer_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
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
    print(f"INDEPENDENT FINITE-ENERGY-MOMENT-TRANSFER PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
