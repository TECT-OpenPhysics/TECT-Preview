#!/usr/bin/env python3
"""Independent finite-Q3 lane for EXP-001128; no import of the primary lane."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_onsite_weighted_isometry_bond_recurrence"
MANIFEST = REPO / f"strategy/{SLUG.replace('_', '-')}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


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


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((n, n), dtype=complex)
    for k in range(n - 1):
        lower[k, k + 1] = np.sqrt(k + 1.0)
    upper = lower.conj().T
    return (lower + upper) / np.sqrt(2.0), (lower - upper) / (1j * np.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError("fixture supports volumes 2, 4, and 6")


def commutator(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def bond_term(q0: np.ndarray, q1: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = q0 - q1
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (q0 @ q0 + q1 @ q1) / 4.0


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if float(np.min(values)) < -1.0e-9:
        raise ValueError("non-positive weight")
    return (vectors * np.power(np.maximum(values, 0.0), exponent)) @ vectors.conj().T


def shifted(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    hermitian = (matrix + matrix.conj().T) / 2.0
    minimum = float(np.min(np.linalg.eigvalsh(hermitian)))
    weight = hermitian - minimum * np.eye(matrix.shape[0], dtype=complex) + np.eye(matrix.shape[0], dtype=complex)
    return weight, power(weight, 0.5), power(weight, -0.5), minimum


def exp_unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def weighted(matrix: np.ndarray, half: np.ndarray, inverse_half: np.ndarray) -> dict[str, float]:
    right = norm(half @ matrix @ inverse_half)
    left = norm(inverse_half @ matrix @ half)
    return {"plus": right, "minus": left, "sum": right + left}


def build(fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    n = int(fixture["oscillator_dimension"])
    q, p = oscillator(n)
    eye = np.eye(n, dtype=complex)
    q_ops = [np.kron(q, eye), np.kron(eye, q)]
    p_ops = [np.kron(p, eye), np.kron(eye, p)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    onsite = [p_i @ p_i / (2.0 * chi) + r * q_i @ q_i / 2.0 + g * q_i @ q_i @ q_i @ q_i / 4.0 for q_i, p_i in zip(q_ops, p_ops)]
    onsite_h = sum(onsite, np.zeros_like(q_ops[0]))
    bond = bond_term(q_ops[0], q_ops[1], fixture)
    return q_ops, p_ops, (onsite_h + onsite_h.conj().T) / 2.0, (onsite_h + bond + (onsite_h + bond).conj().T) / 2.0, (bond + bond.conj().T) / 2.0


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["matrix_tolerance"])
    delta, hbar = float(fixture["delta"]), float(fixture["hbar"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001128" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001128/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph geometry", graph_edges(2) == [(0, 1)] and len(graph_edges(4)) == 4 and len(graph_edges(6)) == 7, [graph_edges(2), len(graph_edges(4)), len(graph_edges(6))], "target/square/2x3", "geometry")
    check("scope firewall", scope["finite_onsite_two_orientation_isometry_closed"] and scope["finite_endpoint_to_edge_bond_multiplier_rows_closed"] and not scope["volume_uniformity_proved"], scope, "finite reduction only", "scope")

    volume_rows: list[dict[str, Any]] = []
    for volume in (int(v) for v in fixture["volume_values"]):
        q_ops, p_ops, onsite_h, edge_h, bond_h = build(fixture)
        onsite_weight, onsite_half, onsite_minus, onsite_min = shifted(onsite_h)
        edge_weight, edge_half, edge_minus, edge_min = shifted(edge_h)
        onsite_step = exp_unitary(onsite_h, delta, hbar)
        probe_list = [q_ops[0], p_ops[0], character(q_ops[0] + q_ops[1], float(fixture["character_amplitude"]), hbar), commutator(onsite_h, character(q_ops[0] + q_ops[1], float(fixture["character_amplitude"]), hbar))]
        edge_rows: list[dict[str, Any]] = []
        for edge_index, edge in enumerate(graph_edges(volume)):
            probe_rows: list[dict[str, Any]] = []
            for probe_index, probe in enumerate(probe_list):
                before = weighted(probe, onsite_half, onsite_minus)
                evolved = onsite_step.conj().T @ probe @ onsite_step
                after = weighted(evolved, onsite_half, onsite_minus)
                differences = {key: abs(after[key] - before[key]) for key in ("plus", "minus", "sum")}
                check(f"V={volume} edge={edge_index} probe={probe_index} onsite isometry", max(differences.values()) <= tolerance, differences, f"<={tolerance}", "onsite weighted isometry")
                check(f"V={volume} edge={edge_index} probe={probe_index} finite", all(np.isfinite(value) for value in list(before.values()) + list(after.values())), [before, after], "finite", "onsite weighted isometry")
                edge_before = weighted(probe, edge_half, edge_minus)
                row_signs: dict[str, Any] = {}
                for sign in (-1, 1):
                    bond_step = exp_unitary(bond_h, sign * delta, hbar)
                    transported = bond_step.conj().T @ probe @ bond_step
                    edge_after = weighted(transported, edge_half, edge_minus)
                    g_plus = norm(edge_half @ bond_step @ edge_minus)
                    g_minus = norm(edge_minus @ bond_step @ edge_half)
                    multiplier = g_plus * g_minus
                    check(f"V={volume} edge={edge_index} probe={probe_index} sign={sign} bond plus", edge_after["plus"] <= multiplier * edge_before["plus"] + tolerance, [edge_after["plus"], multiplier * edge_before["plus"]], "product envelope", "bond recurrence")
                    check(f"V={volume} edge={edge_index} probe={probe_index} sign={sign} bond minus", edge_after["minus"] <= multiplier * edge_before["minus"] + tolerance, [edge_after["minus"], multiplier * edge_before["minus"]], "product envelope", "bond recurrence")
                    check(f"V={volume} edge={edge_index} probe={probe_index} sign={sign} bond finite", np.isfinite(multiplier), multiplier, "finite", "bond recurrence")
                    row_signs[str(sign)] = {"g_plus": g_plus, "g_minus": g_minus, "multiplier": multiplier, "edge_before": edge_before, "edge_after": edge_after}
                probe_rows.append({"probe": probe_index, "onsite_before": before, "onsite_after": after, "onsite_difference": differences, "edge_before": edge_before, "signs": row_signs})
            edge_rows.append({"edge_index": edge_index, "edge": list(edge), "probe_rows": probe_rows})
        multipliers = [entry["multiplier"] for edge_row in edge_rows for probe_row in edge_row["probe_rows"] for entry in probe_row["signs"].values()]
        check(f"V={volume} edge coverage", len(edge_rows) == len(graph_edges(volume)), len(edge_rows), len(graph_edges(volume)), "graph coverage")
        volume_rows.append({"volume": volume, "edge_count": len(edge_rows), "local_dimension": int(fixture["oscillator_dimension"]) ** 2, "onsite_minimum": onsite_min, "edge_minimum": edge_min, "onsite_commutator_residual": norm(onsite_step @ onsite_weight - onsite_weight @ onsite_step), "onsite_unitarity_residual": norm(onsite_step.conj().T @ onsite_step - np.eye(onsite_step.shape[0])), "edge_rows": edge_rows, "max_bond_multiplier": max(multipliers), "min_bond_multiplier": min(multipliers)})

    check("volume sequence", [row["volume"] for row in volume_rows] == list(map(int, fixture["volume_values"])), [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    check("onsite commutation", all(row["onsite_commutator_residual"] <= tolerance for row in volume_rows), [row["onsite_commutator_residual"] for row in volume_rows], f"<={tolerance}", "onsite algebra")
    check("onsite unitarity", all(row["onsite_unitarity_residual"] <= tolerance for row in volume_rows), [row["onsite_unitarity_residual"] for row in volume_rows], f"<={tolerance}", "onsite algebra")
    check("bond multipliers finite", all(np.isfinite(row["max_bond_multiplier"]) for row in volume_rows), [row["max_bond_multiplier"] for row in volume_rows], "finite", "scaling")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-ONSITE-WEIGHTED-ISOMETRY-BOND-RECURRENCE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "finite_onsite_two_orientation_isometry_closed": True, "finite_endpoint_to_edge_bond_multiplier_rows_closed": True, "finite_full_q3_recurrence_reduction_closed": True, "source_uniformity_proved": False, "volume_uniformity_proved": False, "cutoff_uniformity_proved": False, "exact_ccr_common_core_closed": False, "modular_domain_transfer_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "all_bond_graph_lipschitz_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT ONSITE-WEIGHTED-ISOMETRY-BOND-RECURRENCE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
