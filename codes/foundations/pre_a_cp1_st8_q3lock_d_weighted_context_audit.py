#!/usr/bin/env python3
"""Primary actual-Q3 four-context D-weighted energy audit for EXP-001145."""

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
SLUG = "pre_a_cp1_st8_q3lock_d_weighted_context_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-d-weighted-context-audit-manifest.json"
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
    volumes = [int(v) for v in fixture["volume_values"]]
    betas = [float(v) for v in fixture["beta_values"]]
    times = [float(v) for v in fixture["time_values"]]
    radii = [float(v) for v in fixture["radius_values"]]
    orientations = [int(v) for v in fixture["orientation_values"]]
    dimension = int(fixture["oscillator_dimension"])
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
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

    check("provenance", manifest["exploration_id"] == "EXP-001145" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001145/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", volumes == [2, 4, 6] and [len(q3.graph_edges(v)) for v in volumes] == [1, 4, 7], volumes, "edge/square/six-site", "geometry")
    check("scope firewall", scope["finite_d_weighted_transfer_closed"] and scope["four_context_decomposition_closed"] and not scope["uniform_d_weighted_context_common_core_closed"] and not scope["pre_a_closed"], scope, "finite weighted context only", "scope")

    all_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for volume in volumes:
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        for beta in betas:
            energies, vectors, weights, probabilities = spectral_data(hamiltonian, beta, mean_gap_tolerance)
            shifted = energies - float(np.min(energies)) + shift_constant
            m2 = float(np.sum(probabilities * shifted**2))
            trace_k2 = float(np.sum(shifted**2))
            mean_slack = 0.5 * (probabilities[:, None] + probabilities[None, :]) - weights
            check(f"V={volume} beta={beta} mean bound", float(np.min(mean_slack)) >= -mean_gap_tolerance, float(np.min(mean_slack)), ">=-tolerance", "Kubo-Mori weights")
            check(f"V={volume} beta={beta} shifted spectrum", float(np.min(shifted)) >= shift_constant - transfer_tolerance, float(np.min(shifted)), f">={shift_constant}", "energy shift")
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
                        terms = np.abs(matrix_hat) ** 2
                        spectral_moment = float(np.real(np.sum(factor * weights * gaps**2 * terms)))
                        context_a = float(np.sum(probabilities[:, None] * shifted[:, None]**2 * terms))
                        context_b = float(np.sum(probabilities[:, None] * shifted[None, :]**2 * terms))
                        context_c = float(np.sum(probabilities[None, :] * shifted[:, None]**2 * terms))
                        context_d = float(np.sum(probabilities[None, :] * shifted[None, :]**2 * terms))
                        weighted_rhs = float(factor * (context_a + context_b + context_c + context_d))
                        op_norm = q3.operator_norm(difference)
                        coarse_bound = float(4.0 * (m2 + trace_k2) * op_norm**2)
                        gap_slack = 2.0 * (shifted[:, None]**2 + shifted[None, :]**2) - (shifted[:, None] - shifted[None, :])**2
                        values = {
                            "M2": m2,
                            "TrK2": trace_k2,
                            "spectral_second_moment": spectral_moment,
                            "context_A": context_a,
                            "context_B": context_b,
                            "context_C": context_c,
                            "context_D": context_d,
                            "weighted_rhs": weighted_rhs,
                            "operator_norm": op_norm,
                            "coarse_trace_bound": coarse_bound,
                            "weighted_ratio_to_M2_norm": weighted_rhs / max(m2 * op_norm**2, np.finfo(float).tiny),
                            "source_commutator_norm": source_commutator_norm,
                            "min_gap_square_slack": float(np.min(gap_slack)),
                            "min_mean_slack": float(np.min(mean_slack)),
                        }
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "weighted contexts")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} context transfer", spectral_moment >= -transfer_tolerance and spectral_moment <= weighted_rhs + transfer_tolerance, [spectral_moment, weighted_rhs], "0<=S<=2(A+B+C+D)", "corrected transfer")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} coarse bound", weighted_rhs <= coarse_bound + transfer_tolerance, [weighted_rhs, coarse_bound], "weighted RHS<=coarse trace bound", "coarse fallback")
                        all_rows.append({"volume": volume, "beta": beta, "radius": radius, "time": time, "orientation": orientation, "values": values})
            selected = [row for row in all_rows if row["volume"] == volume and row["beta"] == beta]
            summary_rows.append({
                "volume": volume,
                "beta": beta,
                "M2": m2,
                "TrK2": trace_k2,
                "max_spectral_second_moment": max(row["values"]["spectral_second_moment"] for row in selected),
                "max_context_A": max(row["values"]["context_A"] for row in selected),
                "max_context_B": max(row["values"]["context_B"] for row in selected),
                "max_context_C": max(row["values"]["context_C"] for row in selected),
                "max_context_D": max(row["values"]["context_D"] for row in selected),
                "max_weighted_rhs": max(row["values"]["weighted_rhs"] for row in selected),
                "max_weighted_ratio_to_M2_norm": max(row["values"]["weighted_ratio_to_M2_norm"] for row in selected),
                "max_coarse_trace_bound": max(row["values"]["coarse_trace_bound"] for row in selected)
            })

    expected_rows = len(volumes) * len(betas) * len(radii) * len(times) * len(orientations)
    check("row coverage", len(all_rows) == expected_rows, len(all_rows), expected_rows, "coverage")
    check("all corrected transfers", all(row["values"]["spectral_second_moment"] <= row["values"]["weighted_rhs"] + transfer_tolerance for row in all_rows), len(all_rows), "all <= weighted RHS", "corrected transfer")
    check("all coarse fallbacks", all(row["values"]["weighted_rhs"] <= row["values"]["coarse_trace_bound"] + transfer_tolerance for row in all_rows), len(all_rows), "all <= coarse bound", "coarse fallback")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-D-WEIGHTED-CONTEXT-AUDIT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:24] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "derived": {
            "summary_rows": summary_rows,
            "row_count": len(all_rows),
            "finite_d_weighted_transfer_closed": True,
            "four_context_decomposition_closed": True,
            "actual_q3_rows_closed": True,
            "two_orientation_history_closed": True,
            "coarse_trace_fallback_closed": True,
            "uniform_d_weighted_context_common_core_closed": False,
            "uniform_beta_volume_direct_d_delta_d_closed": False,
            "modular_domain_transfer_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY D-WEIGHTED-CONTEXT-AUDIT PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
