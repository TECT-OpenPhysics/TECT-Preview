#!/usr/bin/env python3
"""Independent finite-matrix check of the EXP-001092 Duhamel bounds.

This intentionally reconstructs the Q3 fixture instead of importing the
primary script.  It is a numerical cross-check only; no unbounded or uniform
QFT conclusion is inferred.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_volume_operator_norm_cutoff_duhamel_bound"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


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


def oscillator(n: int) -> np.ndarray:
    lowering = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        lowering[index, index + 1] = math.sqrt(index + 1.0)
    return (lowering + lowering.conj().T) / math.sqrt(2.0)


def momentum(n: int) -> np.ndarray:
    lowering = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        lowering[index, index + 1] = math.sqrt(index + 1.0)
    return (lowering - lowering.conj().T) / (1j * math.sqrt(2.0))


def edges(volume: int) -> list[tuple[int, int]]:
    table = {
        2: [(0, 1)],
        4: [(0, 1), (0, 2), (1, 3), (2, 3)],
        6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)],
    }
    return table[volume]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = single if site == 0 else identity
    for current in range(1, volume):
        factor = single if current == site else identity
        result = np.kron(result, factor)
    return result


def bond(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return float(fixture["c"]) * square / 2.0 + float(fixture["lambda"]) * square @ (left @ left + right @ right) / 4.0


def hamiltonian(volume: int, n: int, fixture: dict[str, Any], bond_coordinate: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(n), momentum(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    bond_q = q_single if bond_coordinate is None else bond_coordinate
    bond_ops = [embed(bond_q, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    bond_terms = {(left, right): bond(bond_ops[left], bond_ops[right], fixture) for left, right in edges(volume)}
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite, zero) + sum(bond_terms.values(), zero)
    return q_ops, (full + full.conj().T) / 2.0, bond_terms


def cut_coordinate(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def opnorm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


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
    check("scope firewall", scope["finite_matrix_duhamel_identity_closed"] and scope["finite_modular_companion_bound_closed"] and not scope["actual_q3_unbounded_tail_comparison_closed"] and not scope["common_alpha_closed"], scope, "finite bound only", "scope")

    beta, hbar = float(fixture["beta"]), float(fixture["hbar"])
    amplitude, tolerance = float(fixture["character_amplitude"]), float(fixture["operator_tolerance"])
    n = int(fixture["oscillator_dimension"])
    volumes = [int(value) for value in fixture["volume_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    volume_rows: list[dict[str, Any]] = []
    q_single = oscillator(n)

    for volume in volumes:
        q_ops, h_full, full_bonds = hamiltonian(volume, n, fixture)
        observable = character(q_ops[0] + q_ops[1], amplitude, hbar)
        h_norm = opnorm(h_full)
        check(f"V={volume} H finite", math.isfinite(h_norm), h_norm, "finite", "finite matrix")
        radius_rows: list[dict[str, Any]] = []
        for radius in radii:
            _, _, cut_bonds = hamiltonian(volume, n, fixture, cut_coordinate(q_single, radius))
            zero = np.zeros_like(h_full)
            tail = sum((full_bonds[edge] - cut_bonds[edge] for edge in full_bonds), zero)
            tail_norm = opnorm(tail)
            check(f"V={volume} L={radius} tail finite", math.isfinite(tail_norm), tail_norm, "finite", "cutoff")
            time_rows: list[dict[str, Any]] = []
            for time in times:
                reference = unitary(h_full, time, hbar)
                orientations: list[dict[str, Any]] = []
                for sign in (-1, 1):
                    evolution = unitary(h_full + sign * tail, time, hbar)
                    unitary_error = opnorm(evolution.conj().T @ evolution - np.eye(evolution.shape[0], dtype=complex))
                    relative_norm = opnorm(evolution - reference)
                    duhamel_bound = abs(time) * tail_norm / hbar
                    difference = evolution @ observable @ evolution.conj().T - reference @ observable @ reference.conj().T
                    d_norm = opnorm(difference)
                    modular_norm = opnorm(-beta * (h_full @ difference - difference @ h_full))
                    d_bound = 2.0 * abs(time) * opnorm(observable) * tail_norm / hbar
                    modular_bound = 4.0 * beta * abs(time) * h_norm * opnorm(observable) * tail_norm / hbar
                    check(f"V={volume} L={radius} t={time} sign={sign} unitary", unitary_error <= tolerance, unitary_error, f"<={tolerance}", "finite evolution")
                    check(f"V={volume} L={radius} t={time} sign={sign} Duhamel", relative_norm <= duhamel_bound + tolerance, relative_norm, f"<={duhamel_bound}+tol", "Duhamel")
                    check(f"V={volume} L={radius} t={time} sign={sign} D bound", d_norm <= d_bound + tolerance, d_norm, f"<={d_bound}+tol", "operator D")
                    check(f"V={volume} L={radius} t={time} sign={sign} modular bound", modular_norm <= modular_bound + tolerance, modular_norm, f"<={modular_bound}+tol", "operator delta-D")
                    orientations.append({"sign": sign, "relative_unitary_norm": relative_norm, "unitary_error": unitary_error, "duhamel_bound": duhamel_bound, "D_operator_norm": d_norm, "D_bound": d_bound, "delta_D_operator_norm": modular_norm, "delta_D_bound": modular_bound})
                time_rows.append({"time": time, "orientations": orientations})
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "times": time_rows})
        volume_rows.append({"volume": volume, "dimension": n ** volume, "H_operator_norm": h_norm, "radius_rows": radius_rows})
        check(f"V={volume} radius sequence", [row["radius"] for row in radius_rows] == radii, [row["radius"] for row in radius_rows], radii, "cutoff")

    check("volume sequence", [row["volume"] for row in volume_rows] == volumes, [row["volume"] for row in volume_rows], volumes, "volume")
    check("largest cutoff vanishes in fixture", all(row["radius_rows"][-1]["tail_operator_norm"] <= tolerance for row in volume_rows), [row["radius_rows"][-1]["tail_operator_norm"] for row in volume_rows], f"<={tolerance}", "fixed regulator")
    check("two-sign rows present", all(len(item["orientations"]) == 2 for volume in volume_rows for radius in volume["radius_rows"] for item in radius["times"]), "all rows", 2, "two orientations")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-VOLUME-OPERATOR-NORM-CUTOFF-DUHAMEL-BOUND", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "total": len(rows), "failed": 0, "assertions": rows, "derived": {"volume_rows": volume_rows, "finite_matrix_duhamel_identity_closed": True, "finite_two_sign_operator_norm_bound_closed": True, "finite_modular_companion_bound_closed": True, "fixed_regulator_cutoff_limit_closed": True, "actual_q3_unbounded_tail_comparison_closed": False, "volume_uniform_direct_d_delta_d_closed": False, "modular_history_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-VOLUME-DUHAMEL-BOUND PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
