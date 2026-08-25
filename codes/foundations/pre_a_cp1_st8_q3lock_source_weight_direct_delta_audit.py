#!/usr/bin/env python3
"""Finite actual-Q3 source-weighted direct D and delta_H D audit."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_source_weight_direct_delta_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-weight-direct-delta-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def weighted_legs(matrix: np.ndarray, weight: np.ndarray, rho_sqrt: np.ndarray) -> dict[str, float]:
    legs = {
        "left_D": weight @ matrix @ rho_sqrt,
        "left_D_star": weight @ matrix.conj().T @ rho_sqrt,
        "right_D": matrix @ weight @ rho_sqrt,
        "right_D_star": matrix.conj().T @ weight @ rho_sqrt,
    }
    values = {name: float(np.linalg.norm(value, ord="fro") ** 2) for name, value in legs.items()}
    values["four_leg_sum"] = float(sum(values.values()))
    return values


def gibbs_seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def source_weight(amplitude: float, sigma: float) -> float:
    return (1.0 + abs(amplitude)) * math.exp(sigma * abs(amplitude) ** 4)


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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, analytic, scope = manifest["finite_fixture"], manifest["analytic_fixture"], manifest["scope"]
    volumes = [int(value) for value in fixture["volume_values"]]
    betas = [float(value) for value in fixture["beta_values"]]
    amplitudes = [float(value) for value in fixture["amplitude_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    n = int(fixture["oscillator_dimension"])
    hbar = float(fixture["hbar"])
    tolerance = float(fixture["finite_tolerance"])
    commutator_tolerance = float(fixture["commutator_tolerance"])
    sigma = float(Fraction(analytic["sigma"]))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001149" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001149/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", [len(q3.graph_edges(volume)) for volume in volumes] == [1, 4, 7], volumes, "edge/square/six-site", "geometry")
    check("scope firewall", scope["actual_q3_direct_d_rows_closed"] and scope["actual_q3_direct_delta_d_rows_closed"] and scope["independent_trace_reconstruction_closed"] and scope["finite_source_weight_normalization_closed"] and not scope["volume_uniform_direct_d_cauchy_proved"] and not scope["pre_a_closed"], scope, "finite direct D/delta-D diagnostic", "scope")

    all_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    q_single, _ = q3.oscillator(n)
    for volume in volumes:
        q_ops, hamiltonian, local_hamiltonian, bonds = q3.build_volume(volume, n, fixture)
        local_weight = q3.positive_weight(local_hamiltonian)
        check(f"V={volume} local shift", float(np.min(np.linalg.eigvalsh(local_weight))) >= float(fixture["positive_shift"]) - tolerance, float(np.min(np.linalg.eigvalsh(local_weight))), f">={fixture['positive_shift']}", "weights")
        rho_by_beta = {beta: (q3.gibbs(hamiltonian, beta), None) for beta in betas}
        for beta in betas:
            rho_by_beta[beta] = (rho_by_beta[beta][0], q3.spectral_power(rho_by_beta[beta][0], 0.5))
        reference_units = {time: unitary(hamiltonian, time, hbar) for time in times}
        cut_data: dict[float, tuple[np.ndarray, float]] = {}
        for radius in radii:
            q_cut = q3.cut_coordinate(q_single, radius)
            _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, n, fixture, q_cut)
            zero = np.zeros_like(hamiltonian)
            tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
            cut_data[radius] = (tail, q3.operator_norm(tail))
        perturbed_units = {(radius, time, orientation): unitary(hamiltonian + orientation * cut_data[radius][0], time, hbar) for radius in radii for time in times for orientation in orientations}
        volume_rows: list[dict[str, Any]] = []
        for beta in betas:
            rho, rho_sqrt = rho_by_beta[beta]
            for amplitude in amplitudes:
                source_w = source_weight(amplitude, sigma)
                check(f"V={volume} beta={beta} a={amplitude} source weight", math.isfinite(source_w) and source_w >= 1.0, source_w, ">=1 finite", "source weight")
                observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
                for radius in radii:
                    tail, tail_norm = cut_data[radius]
                    source_commutator_norm = q3.operator_norm(q3.commutator(tail, observable))
                    check(f"V={volume} beta={beta} a={amplitude} L={radius} source", source_commutator_norm <= commutator_tolerance, source_commutator_norm, f"<={commutator_tolerance}", "support locality")
                    for time in times:
                        reference = reference_units[time] @ observable @ reference_units[time].conj().T
                        for orientation in orientations:
                            perturbed = perturbed_units[(radius, time, orientation)]
                            difference = perturbed @ observable @ perturbed.conj().T - reference
                            delta_difference = 1j * q3.commutator(hamiltonian, difference) / hbar
                            d_gibbs = gibbs_seminorm(difference, rho)
                            delta_gibbs = gibbs_seminorm(delta_difference, rho)
                            d_local_values = weighted_legs(difference, local_weight, rho_sqrt)
                            delta_local_values = weighted_legs(delta_difference, local_weight, rho_sqrt)
                            d_local = math.sqrt(max(d_local_values["four_leg_sum"], 0.0))
                            delta_local = math.sqrt(max(delta_local_values["four_leg_sum"], 0.0))
                            values = {
                                "D_gibbs_norm": d_gibbs,
                                "delta_H_D_gibbs_norm": delta_gibbs,
                                "D_local_four_leg_norm": d_local,
                                "delta_H_D_local_four_leg_norm": delta_local,
                                "D_gibbs_normalized": d_gibbs / source_w,
                                "delta_H_D_gibbs_normalized": delta_gibbs / source_w,
                                "D_local_normalized": d_local / source_w,
                                "delta_H_D_local_normalized": delta_local / source_w,
                                "D_local_legs": d_local_values,
                                "delta_H_D_local_legs": delta_local_values,
                                "source_weight": source_w,
                                "tail_operator_norm": tail_norm,
                                "source_commutator_norm": source_commutator_norm,
                            }
                            numeric = [value for key, value in values.items() if key not in ("D_local_legs", "delta_H_D_local_legs")]
                            check(f"V={volume} beta={beta} a={amplitude} L={radius} t={time} sign={orientation} finite", all(np.isfinite(value) for value in numeric), values, "finite", "direct D/delta-D")
                            nonnegative_values = [value for key, value in values.items() if key not in ("D_local_legs", "delta_H_D_local_legs", "source_commutator_norm", "tail_operator_norm")]
                            check(f"V={volume} beta={beta} a={amplitude} L={radius} t={time} sign={orientation} nonnegative", all(value >= -tolerance for value in nonnegative_values), values, ">=-tolerance", "norms")
                            row = {"volume": volume, "beta": beta, "amplitude": amplitude, "radius": radius, "time": time, "orientation": orientation, "values": values}
                            all_rows.append(row)
                            volume_rows.append(row)
        for amplitude in amplitudes:
            rows = [row for row in volume_rows if row["amplitude"] == amplitude]
            summary_rows.append({
                "volume": volume,
                "amplitude": amplitude,
                "max_D_gibbs_normalized": max(row["values"]["D_gibbs_normalized"] for row in rows),
                "max_delta_H_D_gibbs_normalized": max(row["values"]["delta_H_D_gibbs_normalized"] for row in rows),
                "max_D_local_normalized": max(row["values"]["D_local_normalized"] for row in rows),
                "max_delta_H_D_local_normalized": max(row["values"]["delta_H_D_local_normalized"] for row in rows),
            })
        check(f"V={volume} row coverage", len(volume_rows) == len(betas) * len(amplitudes) * len(radii) * len(times) * len(orientations), len(volume_rows), len(betas) * len(amplitudes) * len(radii) * len(times) * len(orientations), "coverage")

    expected_rows = len(volumes) * len(betas) * len(amplitudes) * len(radii) * len(times) * len(orientations)
    check("row coverage", len(all_rows) == expected_rows, len(all_rows), expected_rows, "coverage")
    def volume_max(field: str) -> list[float]:
        return [max(row[field] for row in summary_rows if row["volume"] == volume) for volume in volumes]
    d_gibbs_by_volume = volume_max("max_D_gibbs_normalized")
    delta_gibbs_by_volume = volume_max("max_delta_H_D_gibbs_normalized")
    d_local_by_volume = volume_max("max_D_local_normalized")
    delta_local_by_volume = volume_max("max_delta_H_D_local_normalized")
    check("normalized maxima finite", all(np.isfinite(value) for value in d_gibbs_by_volume + delta_gibbs_by_volume + d_local_by_volume + delta_local_by_volume), [d_gibbs_by_volume, delta_gibbs_by_volume, d_local_by_volume, delta_local_by_volume], "finite", "scaling")
    check("endpoint diagnostic", all(series[-1] >= series[0] for series in (d_gibbs_by_volume, delta_gibbs_by_volume, d_local_by_volume, delta_local_by_volume)), [d_gibbs_by_volume, delta_gibbs_by_volume, d_local_by_volume, delta_local_by_volume], "endpoint comparison only", "scaling")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-WEIGHT-DIRECT-DELTA-AUDIT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:56] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "derived": {
            "summary_rows": summary_rows,
            "row_count": len(all_rows),
            "sigma": sigma,
            "normalized_D_gibbs_maxima_by_volume": d_gibbs_by_volume,
            "normalized_delta_H_D_gibbs_maxima_by_volume": delta_gibbs_by_volume,
            "normalized_D_local_maxima_by_volume": d_local_by_volume,
            "normalized_delta_H_D_local_maxima_by_volume": delta_local_by_volume,
            "actual_q3_direct_d_rows_closed": True,
            "actual_q3_direct_delta_d_rows_closed": True,
            "finite_source_weight_normalization_closed": True,
            "volume_uniform_direct_d_cauchy_proved": False,
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
    print(f"PRIMARY SOURCE-WEIGHT-DIRECT-DELTA PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
