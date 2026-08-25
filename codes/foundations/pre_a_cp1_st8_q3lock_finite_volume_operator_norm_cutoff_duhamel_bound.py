#!/usr/bin/env python3
"""Finite-regulator operator-norm Duhamel bound for the actual Q3 cutoff.

This is deliberately a finite-dimensional theorem/fixture.  It records the
exact unitary perturbation estimate and the induced finite Hamiltonian modular
commutator estimate without promoting either to a uniform Q3 thermodynamic
statement.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_volume_operator_norm_cutoff_duhamel_bound"
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


def unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    """Evaluate exp(-i*time*H/hbar) from the Hermitian spectral theorem."""
    hermitian = (hamiltonian + hamiltonian.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001092" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001092/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_matrix_duhamel_identity_closed"] and scope["finite_two_sign_operator_norm_bound_closed"] and not scope["actual_q3_unbounded_tail_comparison_closed"] and not scope["common_alpha_closed"], scope, "finite bound only", "scope")

    beta = float(fixture["beta"])
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    tolerance = float(fixture["operator_tolerance"])
    dimension = int(fixture["oscillator_dimension"])
    volumes = [int(value) for value in fixture["volume_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    volume_rows: list[dict[str, Any]] = []

    for volume in volumes:
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
        h_norm = q3.operator_norm(hamiltonian)
        check(f"V={volume} H finite", math.isfinite(h_norm), h_norm, "finite", "finite matrix")
        q_single, _ = q3.oscillator(dimension)
        radius_rows: list[dict[str, Any]] = []
        for radius in radii:
            q_cut = q3.cut_coordinate(q_single, radius)
            _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
            zero = np.zeros_like(hamiltonian)
            tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
            tail_norm = q3.operator_norm(tail)
            check(f"V={volume} L={radius} tail finite", math.isfinite(tail_norm), tail_norm, "finite", "cutoff")
            time_rows: list[dict[str, Any]] = []
            for time in times:
                reference = unitary(hamiltonian, time, hbar)
                reference_difference_rows: list[dict[str, Any]] = []
                for sign in (-1, 1):
                    perturbed = hamiltonian + sign * tail
                    evolution = unitary(perturbed, time, hbar)
                    unitary_error = q3.operator_norm(evolution.conj().T @ evolution - np.eye(evolution.shape[0], dtype=complex))
                    relative = evolution - reference
                    relative_norm = q3.operator_norm(relative)
                    duhamel_bound = abs(time) * tail_norm / hbar
                    check(f"V={volume} L={radius} t={time} sign={sign} unitary", unitary_error <= tolerance, unitary_error, f"<={tolerance}", "finite evolution")
                    check(f"V={volume} L={radius} t={time} sign={sign} Duhamel", relative_norm <= duhamel_bound + tolerance, relative_norm, f"<={duhamel_bound}+tol", "Duhamel")
                    evolved = evolution @ observable @ evolution.conj().T
                    reference_evolved = reference @ observable @ reference.conj().T
                    difference = evolved - reference_evolved
                    d_norm = q3.operator_norm(difference)
                    modular = -beta * q3.commutator(hamiltonian, difference)
                    modular_norm = q3.operator_norm(modular)
                    observable_bound = 2.0 * abs(time) * q3.operator_norm(observable) * tail_norm / hbar
                    modular_bound = 4.0 * beta * abs(time) * h_norm * q3.operator_norm(observable) * tail_norm / hbar
                    check(f"V={volume} L={radius} t={time} sign={sign} D bound", d_norm <= observable_bound + tolerance, d_norm, f"<={observable_bound}+tol", "operator D")
                    check(f"V={volume} L={radius} t={time} sign={sign} modular bound", modular_norm <= modular_bound + tolerance, modular_norm, f"<={modular_bound}+tol", "operator delta-D")
                    reference_difference_rows.append({
                        "sign": sign,
                        "relative_unitary_norm": relative_norm,
                        "unitary_error": unitary_error,
                        "duhamel_bound": duhamel_bound,
                        "D_operator_norm": d_norm,
                        "D_bound": observable_bound,
                        "delta_D_operator_norm": modular_norm,
                        "delta_D_bound": modular_bound,
                    })
                time_rows.append({"time": time, "orientations": reference_difference_rows})
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "times": time_rows})
        volume_rows.append({"volume": volume, "dimension": dimension ** volume, "H_operator_norm": h_norm, "radius_rows": radius_rows})
        check(f"V={volume} radius sequence", [row["radius"] for row in radius_rows] == radii, [row["radius"] for row in radius_rows], radii, "cutoff")

    check("volume sequence", [row["volume"] for row in volume_rows] == volumes, [row["volume"] for row in volume_rows], volumes, "volume")
    check("largest cutoff vanishes in fixture", all(row["radius_rows"][-1]["tail_operator_norm"] <= tolerance for row in volume_rows), [row["radius_rows"][-1]["tail_operator_norm"] for row in volume_rows], f"<={tolerance}", "fixed regulator")
    check("two-sign rows present", all(len(time_row["orientations"]) == 2 for volume in volume_rows for radius in volume["radius_rows"] for time_row in radius["times"]), "all rows", 2, "two orientations")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-VOLUME-OPERATOR-NORM-CUTOFF-DUHAMEL-BOUND",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "total": len(rows),
        "failed": 0,
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "finite_matrix_duhamel_identity_closed": True,
            "finite_two_sign_operator_norm_bound_closed": True,
            "finite_modular_companion_bound_closed": True,
            "fixed_regulator_cutoff_limit_closed": True,
            "actual_q3_unbounded_tail_comparison_closed": False,
            "volume_uniform_direct_d_delta_d_closed": False,
            "modular_history_closed": False,
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
    print(f"PRIMARY FINITE-VOLUME-DUHAMEL-BOUND PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
