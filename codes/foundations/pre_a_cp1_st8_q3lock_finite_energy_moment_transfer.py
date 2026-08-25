#!/usr/bin/env python3
"""Primary finite energy-moment transfer audit for EXP-001143.

The numerical lane evaluates the proposed operator-norm transfer bound on the
actual finite Q3 histories.  The Hilbert--Schmidt version is retained as the
safe finite-dimensional comparison; neither lane is promoted to a uniform
common-core theorem.
"""

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


def spectral_data(hamiltonian: np.ndarray, beta: float, gap_tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted = energies - float(np.min(energies))
    probabilities = np.exp(-beta * shifted)
    probabilities /= float(np.sum(probabilities))
    log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
    weights = np.empty_like(log_gap)
    close = np.abs(log_gap) <= gap_tolerance
    np.divide(probabilities[:, None] - probabilities[None, :], log_gap, out=weights, where=~close)
    weights[close] = 0.5 * (probabilities[:, None] + probabilities[None, :])[close]
    return energies, vectors, (weights + weights.T) / 2.0, probabilities


def unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


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
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("provenance", manifest["exploration_id"] == "EXP-001143" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001143/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    edge_counts = [len(q3.graph_edges(volume)) for volume in volumes]
    check("registered graph family", volumes == [2, 4, 6] and edge_counts == [1, 4, 7], [volumes, edge_counts], "edge/square/six-site", "geometry")
    check("scope firewall", scope["finite_energy_moment_transfer_closed"] and scope["termwise_arithmetic_mean_bound_closed"] and not scope["uniform_local_M2_common_core_closed"] and not scope["pre_a_closed"], scope, "finite transfer only", "scope")

    all_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for volume in volumes:
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        for beta in betas:
            energies, vectors, weights, probabilities = spectral_data(hamiltonian, beta, mean_gap_tolerance)
            minimum = float(np.min(energies))
            shifted = energies - minimum + shift_constant
            m2 = float(np.sum(probabilities * shifted**2))
            check(f"V={volume} beta={beta} shifted energy", float(np.min(shifted)) >= shift_constant - transfer_tolerance, float(np.min(shifted)), f">={shift_constant}", "energy moment")
            check(f"V={volume} beta={beta} Gibbs probabilities", abs(float(np.sum(probabilities)) - 1.0) <= transfer_tolerance and np.all(probabilities > 0.0), float(np.sum(probabilities)), "positive and normalized", "Gibbs state")
            check(f"V={volume} beta={beta} logarithmic mean", float(np.min(0.5 * (probabilities[:, None] + probabilities[None, :]) - weights)) >= -mean_gap_tolerance, float(np.min(0.5 * (probabilities[:, None] + probabilities[None, :]) - weights)), ">=-tolerance", "Kubo-Mori weights")
            observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
            reference = {time: unitary(hamiltonian, time, hbar) @ observable @ unitary(hamiltonian, time, hbar).conj().T for time in times}
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
                        perturbed = unitary(hamiltonian + orientation * tail, time, hbar)
                        difference = perturbed @ observable @ perturbed.conj().T - reference[time]
                        matrix_hat = vectors.conj().T @ difference @ vectors
                        gaps = (energies[:, None] - energies[None, :]) / hbar
                        spectral_moment = float(np.real(np.sum(factor * weights * gaps**2 * np.abs(matrix_hat) ** 2)))
                        op_norm = q3.operator_norm(difference)
                        hs_norm = float(np.linalg.norm(difference, ord="fro"))
                        candidate_bound = float(8.0 * m2 * op_norm**2)
                        safe_bound = float(8.0 * m2 * hs_norm**2)
                        gap_slack = 2.0 * (shifted[:, None] ** 2 + shifted[None, :] ** 2) - (shifted[:, None] - shifted[None, :]) ** 2
                        values = {
                            "M2": m2,
                            "spectral_second_moment": spectral_moment,
                            "D_operator_norm": op_norm,
                            "D_hilbert_schmidt_norm": hs_norm,
                            "candidate_operator_bound": candidate_bound,
                            "safe_hilbert_schmidt_bound": safe_bound,
                            "operator_transfer_ratio": spectral_moment / max(m2 * op_norm**2, np.finfo(float).tiny),
                            "hilbert_schmidt_transfer_ratio": spectral_moment / max(m2 * hs_norm**2, np.finfo(float).tiny),
                            "source_commutator_norm": source_commutator_norm,
                            "min_gap_square_slack": float(np.min(gap_slack)),
                            "min_mean_slack": float(np.min(0.5 * (probabilities[:, None] + probabilities[None, :]) - weights)),
                        }
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "energy-moment rows")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} termwise", values["min_gap_square_slack"] >= -transfer_tolerance and values["min_mean_slack"] >= -mean_gap_tolerance, [values["min_gap_square_slack"], values["min_mean_slack"]], ">=-tolerance", "termwise arithmetic bounds")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} safe transfer", spectral_moment >= -transfer_tolerance and spectral_moment <= safe_bound + transfer_tolerance, [spectral_moment, safe_bound], "0<=S<=safe bound", "finite Hilbert-Schmidt transfer")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} operator candidate", spectral_moment <= candidate_bound + transfer_tolerance, [spectral_moment, candidate_bound], "S<=candidate bound on this row", "finite operator-norm diagnostic")
                        all_rows.append({"volume": volume, "beta": beta, "radius": radius, "time": time, "orientation": orientation, "values": values})
            selected = [row for row in all_rows if row["volume"] == volume and row["beta"] == beta]
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
    check("row coverage", len(all_rows) == expected_rows, len(all_rows), expected_rows, "coverage")
    check("all finite transfers", all(row["values"]["spectral_second_moment"] <= row["values"]["safe_hilbert_schmidt_bound"] + transfer_tolerance for row in all_rows), len(all_rows), "all <= safe bound", "finite transfer")
    check("all operator candidates", all(row["values"]["spectral_second_moment"] <= row["values"]["candidate_operator_bound"] + transfer_tolerance for row in all_rows), len(all_rows), "all <= candidate on declared rows", "finite diagnostic")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ENERGY-MOMENT-TRANSFER",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows[:20] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(rows)), "expected": "all executed assertions passed"}],
        "derived": {
            "summary_rows": summary_rows,
            "row_count": len(all_rows),
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
    print(f"PRIMARY FINITE-ENERGY-MOMENT-TRANSFER PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
