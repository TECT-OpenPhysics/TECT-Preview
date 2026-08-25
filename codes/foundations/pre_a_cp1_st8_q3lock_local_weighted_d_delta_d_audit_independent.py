#!/usr/bin/env python3
"""Independent trace reconstruction for the actual-Q3 local-weighted D audit."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_weighted_d_delta_d_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-weighted-d-delta-d-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"
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


def trace_leg_values(matrix: np.ndarray, weight: np.ndarray, rho: np.ndarray) -> dict[str, float]:
    weight_square = weight @ weight
    values = {
        "left_D": float(np.real(np.trace(rho @ matrix.conj().T @ weight_square @ matrix))),
        "left_D_star": float(np.real(np.trace(rho @ matrix @ weight_square @ matrix.conj().T))),
        "right_D": float(np.real(np.trace(rho @ weight @ matrix.conj().T @ matrix @ weight))),
        "right_D_star": float(np.real(np.trace(rho @ weight @ matrix @ matrix.conj().T @ weight))),
    }
    values["four_leg_sum"] = float(sum(values.values()))
    return values


def unitary_from_eigenbasis(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    phases = np.exp(-1j * time * values / hbar)
    return (vectors * phases) @ vectors.conj().T


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    volumes = [int(value) for value in fixture["volume_values"]]
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    n = int(fixture["oscillator_dimension"])
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    tolerance = float(fixture["finite_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001147" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001147/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["actual_q3_local_four_leg_rows_closed"] and scope["independent_trace_reconstruction_closed"] and not scope["local_weight_volume_uniformity_proved"] and not scope["pre_a_closed"], scope, "finite local-weight diagnostic", "scope")

    all_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    q_single, _ = q3.oscillator(n)
    for volume in volumes:
        q_ops, hamiltonian, local_hamiltonian, bonds = q3.build_volume(volume, n, fixture)
        full_weight = q3.positive_weight(hamiltonian)
        local_weight = q3.positive_weight(local_hamiltonian)
        observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
        for beta in betas:
            rho = q3.gibbs(hamiltonian, beta)
            reference = {time: unitary_from_eigenbasis(hamiltonian, time, hbar) @ observable @ unitary_from_eigenbasis(hamiltonian, time, hbar).conj().T for time in times}
            beta_rows: list[dict[str, Any]] = []
            for radius in radii:
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, n, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                for time in times:
                    for orientation in orientations:
                        perturbed = unitary_from_eigenbasis(hamiltonian + orientation * tail, time, hbar)
                        difference = perturbed @ observable @ perturbed.conj().T - reference[time]
                        local_values = trace_leg_values(difference, local_weight, rho)
                        full_values = trace_leg_values(difference, full_weight, rho)
                        flat = list(local_values.values()) + list(full_values.values())
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} finite", all(np.isfinite(value) for value in flat), flat, "finite", "trace legs")
                        check(f"V={volume} beta={beta} L={radius} t={time} sign={orientation} nonnegative", all(value >= -tolerance for value in flat), flat, ">=-tolerance", "trace legs")
                        row = {"volume": volume, "beta": beta, "radius": radius, "time": time, "orientation": orientation, "values": {"local": local_values, "full": full_values}}
                        all_rows.append(row)
                        beta_rows.append(row)
            summary_rows.append({
                "volume": volume,
                "beta": beta,
                "max_local_four_leg_sum": max(row["values"]["local"]["four_leg_sum"] for row in beta_rows),
                "max_full_four_leg_sum": max(row["values"]["full"]["four_leg_sum"] for row in beta_rows),
                "max_local_left_D": max(row["values"]["local"]["left_D"] for row in beta_rows),
                "max_local_right_D": max(row["values"]["local"]["right_D"] for row in beta_rows),
                "max_full_left_D": max(row["values"]["full"]["left_D"] for row in beta_rows),
                "max_full_right_D": max(row["values"]["full"]["right_D"] for row in beta_rows),
            })

    expected_rows = len(volumes) * len(betas) * len(radii) * len(times) * len(orientations)
    check("row coverage", len(all_rows) == expected_rows, len(all_rows), expected_rows, "coverage")
    local_maxima = [row["max_local_four_leg_sum"] for row in summary_rows]
    full_maxima = [row["max_full_four_leg_sum"] for row in summary_rows]
    check("maxima finite", all(np.isfinite(value) for value in local_maxima + full_maxima), [local_maxima, full_maxima], "finite", "scaling")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-WEIGHTED-D-DELTA-D-AUDIT",
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
            "local_four_leg_rows_closed": True,
            "full_global_baseline_closed": True,
            "local_weight_volume_uniformity_proved": False,
            "global_weight_volume_uniformity_proved": False,
            "direct_d_delta_d_cauchy_closed": False,
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
    print(f"INDEPENDENT LOCAL-WEIGHTED-D-DELTA-D-AUDIT PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
