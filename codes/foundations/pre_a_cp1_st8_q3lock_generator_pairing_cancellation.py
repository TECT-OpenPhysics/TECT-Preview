#!/usr/bin/env python3
"""Primary finite actual-Q3 full-generator pairing audit for EXP-001140."""

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
SLUG = "pre_a_cp1_st8_q3lock_generator_pairing_cancellation"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-generator-pairing-cancellation-manifest.json"
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


def gibbs_kubo_mori(hamiltonian: np.ndarray, beta: float, gap_tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    probabilities = np.exp(-beta * (energies - float(np.min(energies))))
    probabilities /= float(np.sum(probabilities))
    left, right = probabilities[:, None], probabilities[None, :]
    log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
    weights = np.empty_like(log_gap)
    close = np.abs(log_gap) <= gap_tolerance
    np.divide(left - right, log_gap, out=weights, where=~close)
    weights[close] = 0.5 * (left + right)[close]
    weights = (weights + weights.T) / 2.0
    return energies, vectors, weights


def generator_delta(hamiltonian: np.ndarray, matrix: np.ndarray, hbar: float) -> np.ndarray:
    return 1j * q3.commutator(hamiltonian, matrix) / hbar


def unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T

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

    check("identity", manifest["exploration_id"] == "EXP-001140" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001140/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    volumes = [int(value) for value in fixture["volume_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    check("graph geometry", q3.graph_edges(volumes[0]) == [(0, 1)] and len(q3.graph_edges(volumes[-1])) == 4, [q3.graph_edges(volumes[0]), len(q3.graph_edges(volumes[-1]))], "edge and square", "geometry")
    check("scope firewall", scope["finite_actual_d_delta_rows_closed"] and scope["full_generator_pairing_identity_closed"] and scope["two_orientation_history_closed"] and not scope["uniform_beta_volume_direct_d_delta_d_closed"] and not scope["pre_a_closed"], scope, "finite pairing only", "scope")

    beta_values = [float(value) for value in fixture["beta_values"]]
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    tolerance = float(fixture["commutator_tolerance"])
    gap_tolerance = float(fixture["mean_gap_tolerance"])
    dimension = int(fixture["oscillator_dimension"])
    times = [float(value) for value in fixture["time_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    factor = float(fixture["two_sided_factor"])
    all_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for beta in beta_values:
        for volume in volumes:
            q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
            energies, vectors, weights = gibbs_kubo_mori(hamiltonian, beta, gap_tolerance)
            observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
            source = {time: unitary(hamiltonian, time, hbar) @ observable @ unitary(hamiltonian, time, hbar).conj().T for time in times}
            volume_rows: list[dict[str, Any]] = []
            for radius in radii:
                q_single, _ = q3.oscillator(dimension)
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                source_commutator_norm = q3.operator_norm(q3.commutator(tail, observable))
                check(f"beta={beta} V={volume} L={radius} source commutation", source_commutator_norm <= tolerance, source_commutator_norm, f"<={tolerance}", "support locality")
                radius_rows: list[dict[str, Any]] = []
                for time in times:
                    for orientation in orientations:
                        perturbed = hamiltonian + orientation * tail
                        evolution = unitary(perturbed, time, hbar)
                        difference = evolution @ observable @ evolution.conj().T - source[time]
                        delta_difference = generator_delta(hamiltonian, difference, hbar)
                        delta2_difference = generator_delta(hamiltonian, delta_difference, hbar)
                        d_inner = kubo_mori_inner(difference, difference, vectors, weights, factor)
                        first_inner = kubo_mori_inner(delta_difference, delta_difference, vectors, weights, factor)
                        second_inner = kubo_mori_inner(delta2_difference, difference, vectors, weights, factor)
                        delta2_inner = kubo_mori_inner(delta2_difference, delta2_difference, vectors, weights, factor)
                        cancellation_error = abs(second_inner + first_inner)
                        values = {
                            "D_kubo_mori_norm": float(np.sqrt(max(0.0, float(np.real(d_inner))))),
                            "delta_D_kubo_mori_norm": float(np.sqrt(max(0.0, float(np.real(first_inner))))),
                            "delta2_D_kubo_mori_norm": float(np.sqrt(max(0.0, float(np.real(delta2_inner))))),
                            "D_matrix_norm": q3.operator_norm(difference),
                            "delta_D_matrix_norm": q3.operator_norm(delta_difference),
                            "delta2_D_matrix_norm": q3.operator_norm(delta2_difference),
                            "pairing_delta2_D_D_real": float(np.real(second_inner)),
                            "pairing_delta2_D_D_imag": float(np.imag(second_inner)),
                            "pairing_delta_D_delta_D_real": float(np.real(first_inner)),
                            "pairing_delta_D_delta_D_imag": float(np.imag(first_inner)),
                            "cancellation_error": float(cancellation_error),
                            "tail_operator_norm": q3.operator_norm(tail),
                            "source_commutator_norm": source_commutator_norm,
                        }
                        check(f"beta={beta} V={volume} L={radius} t={time} sign={orientation} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "actual D/delta-D")
                        check(f"beta={beta} V={volume} L={radius} t={time} sign={orientation} pairing", cancellation_error <= tolerance, cancellation_error, f"<={tolerance}", "full-generator cancellation")
                        check(f"beta={beta} V={volume} L={radius} t={time} sign={orientation} positivity", float(np.real(first_inner)) >= -tolerance, first_inner, ">=-tolerance", "Kubo-Mori positivity")
                        check(f"beta={beta} V={volume} L={radius} t={time} sign={orientation} D positivity", float(np.real(d_inner)) >= -tolerance and float(np.real(delta2_inner)) >= -tolerance, [d_inner, delta2_inner], ">=-tolerance", "Kubo-Mori positivity")
                        all_rows.append({"beta": beta, "volume": volume, "radius": radius, "time": time, "orientation": orientation, "values": values})
                        radius_rows.append({"time": time, "orientation": orientation, "values": values})
                volume_rows.append({"radius": radius, "source_commutator_norm": source_commutator_norm, "rows": radius_rows})
            summary_rows.append({"beta": beta, "volume": volume, "max_D": max(row["values"]["D_matrix_norm"] for row in all_rows if row["beta"] == beta and row["volume"] == volume), "max_delta_D": max(row["values"]["delta_D_matrix_norm"] for row in all_rows if row["beta"] == beta and row["volume"] == volume), "max_delta2_D": max(row["values"]["delta2_D_matrix_norm"] for row in all_rows if row["beta"] == beta and row["volume"] == volume), "max_D_km": max(row["values"]["D_kubo_mori_norm"] for row in all_rows if row["beta"] == beta and row["volume"] == volume), "max_delta_D_km": max(row["values"]["delta_D_kubo_mori_norm"] for row in all_rows if row["beta"] == beta and row["volume"] == volume), "max_delta2_D_km": max(row["values"]["delta2_D_kubo_mori_norm"] for row in all_rows if row["beta"] == beta and row["volume"] == volume), "max_cancellation_error": max(row["values"]["cancellation_error"] for row in all_rows if row["beta"] == beta and row["volume"] == volume)})

    growth_rows: list[dict[str, Any]] = []
    for beta in beta_values:
        edge = next(row for row in summary_rows if row["beta"] == beta and row["volume"] == volumes[0])
        square = next(row for row in summary_rows if row["beta"] == beta and row["volume"] == volumes[-1])
        ratio = square["max_delta_D_km"] / max(edge["max_delta_D_km"], np.finfo(float).tiny)
        growth_rows.append({"beta": beta, "edge_max_delta_D_km": edge["max_delta_D_km"], "square_max_delta_D_km": square["max_delta_D_km"], "square_over_edge_ratio": ratio})
        check(f"beta={beta} finite growth report", np.isfinite(ratio), ratio, "finite", "volume diagnostic")

    check("all cancellation rows", all(row["values"]["cancellation_error"] <= tolerance for row in all_rows), len(all_rows), "all <= tolerance", "full-generator cancellation")
    check("all orientation rows", sorted(set(row["orientation"] for row in all_rows)) == sorted(orientations), sorted(set(row["orientation"] for row in all_rows)), orientations, "orientation")
    check("all beta rows", sorted(set(row["beta"] for row in all_rows)) == sorted(beta_values), sorted(set(row["beta"] for row in all_rows)), beta_values, "beta")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-GENERATOR-PAIRING-CANCELLATION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows[:14] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(rows)), "expected": "all executed assertions passed"}],
        "derived": {
            "summary_rows": summary_rows,
            "growth_rows": growth_rows,
            "row_count": len(all_rows),
            "finite_actual_d_delta_rows_closed": True,
            "full_generator_pairing_identity_closed": True,
            "two_orientation_history_closed": True,
            "finite_volume_growth_diagnostic_closed": True,
            "uniform_beta_volume_direct_d_delta_d_closed": False,
            "modular_domain_closed": False,
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
    print(f"PRIMARY GENERATOR-PAIRING-CANCELLATION PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
