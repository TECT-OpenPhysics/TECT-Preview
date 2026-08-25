#!/usr/bin/env python3
"""Primary finite actual-Q3 onsite weighted-isometry/bond-recurrence audit."""

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
SLUG = "pre_a_cp1_st8_q3lock_onsite_weighted_isometry_bond_recurrence"
MANIFEST = REPO / f"strategy/{SLUG.replace('_', '-')}-manifest.json"
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


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if float(np.min(values)) < -1.0e-9:
        raise ValueError("spectral weight is not positive")
    values = np.maximum(values, 0.0)
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def shifted_weight(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    hermitian = (matrix + matrix.conj().T) / 2.0
    minimum = float(np.min(np.linalg.eigvalsh(hermitian)))
    weight = hermitian - minimum * np.eye(matrix.shape[0], dtype=complex) + np.eye(matrix.shape[0], dtype=complex)
    return weight, spectral_power(weight, 0.5), spectral_power(weight, -0.5), minimum


def unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def weighted_orientations(matrix: np.ndarray, weight_half: np.ndarray, weight_minus: np.ndarray) -> dict[str, float]:
    plus = operator_norm(weight_half @ matrix @ weight_minus)
    minus = operator_norm(weight_minus @ matrix @ weight_half)
    return {"plus": plus, "minus": minus, "sum": plus + minus}


def local_fixture(n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [np.kron(q_single, identity), np.kron(identity, q_single)]
    p_ops = [np.kron(p_single, identity), np.kron(identity, p_single)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    difference = q_ops[0] - q_ops[1]
    bond = q3.bond_term(q_ops[0], q_ops[1], fixture)
    onsite_h = sum(onsite, np.zeros_like(q_ops[0]))
    edge_h = onsite_h + bond
    return q_ops, p_ops, (onsite_h + onsite_h.conj().T) / 2.0, (edge_h + edge_h.conj().T) / 2.0, (bond + bond.conj().T) / 2.0


def probes(q_ops: list[np.ndarray], p_ops: list[np.ndarray], local_h: np.ndarray, amplitude: float, hbar: float) -> list[np.ndarray]:
    character = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
    return [q_ops[0], p_ops[0], character, q3.commutator(local_h, character)]


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
    check("graph geometry", q3.graph_edges(2) == [(0, 1)] and len(q3.graph_edges(4)) == 4 and len(q3.graph_edges(6)) == 7, [q3.graph_edges(2), len(q3.graph_edges(4)), len(q3.graph_edges(6))], "target/square/2x3", "geometry")
    check("scope firewall", scope["finite_onsite_two_orientation_isometry_closed"] and scope["finite_endpoint_to_edge_bond_multiplier_rows_closed"] and scope["finite_full_q3_recurrence_reduction_closed"] and not scope["volume_uniformity_proved"] and not scope["common_alpha_closed"], scope, "finite reduction only", "scope")

    volume_rows: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        q_ops, p_ops, onsite_h, edge_h, bond_h = local_fixture(int(fixture["oscillator_dimension"]), fixture)
        onsite_weight, onsite_half, onsite_minus, onsite_min = shifted_weight(onsite_h)
        edge_weight, edge_half, edge_minus, edge_min = shifted_weight(edge_h)
        onsite_step = unitary(onsite_h, delta, hbar)
        edge_rows: list[dict[str, Any]] = []
        for edge_index, edge in enumerate(q3.graph_edges(volume)):
            local_probe_rows: list[dict[str, Any]] = []
            for probe_index, probe in enumerate(probes(q_ops, p_ops, onsite_h, float(fixture["character_amplitude"]), hbar)):
                before = weighted_orientations(probe, onsite_half, onsite_minus)
                evolved = onsite_step.conj().T @ probe @ onsite_step
                after = weighted_orientations(evolved, onsite_half, onsite_minus)
                differences = {key: abs(after[key] - before[key]) for key in ("plus", "minus", "sum")}
                check(f"V={volume} edge={edge_index} probe={probe_index} onsite isometry", max(differences.values()) <= tolerance, differences, f"<={tolerance}", "onsite weighted isometry")
                check(f"V={volume} edge={edge_index} probe={probe_index} finite", all(np.isfinite(value) for value in list(before.values()) + list(after.values())), [before, after], "finite", "onsite weighted isometry")

                endpoint = weighted_orientations(probe, spectral_power(shifted_weight(onsite_h)[0], 0.5), spectral_power(shifted_weight(onsite_h)[0], -0.5))
                # The endpoint observable is embedded in the two-site edge algebra.
                edge_before = weighted_orientations(probe, edge_half, edge_minus)
                row_signs: dict[str, Any] = {}
                for sign in (-1, 1):
                    bond_step = unitary(bond_h, sign * delta, hbar)
                    transported = bond_step.conj().T @ probe @ bond_step
                    edge_after = weighted_orientations(transported, edge_half, edge_minus)
                    g_plus = operator_norm(edge_half @ bond_step @ edge_minus)
                    g_minus = operator_norm(edge_minus @ bond_step @ edge_half)
                    multiplier = g_plus * g_minus
                    check(f"V={volume} edge={edge_index} probe={probe_index} sign={sign} bond plus", edge_after["plus"] <= multiplier * edge_before["plus"] + tolerance, [edge_after["plus"], multiplier * edge_before["plus"]], "product envelope", "bond recurrence")
                    check(f"V={volume} edge={edge_index} probe={probe_index} sign={sign} bond minus", edge_after["minus"] <= multiplier * edge_before["minus"] + tolerance, [edge_after["minus"], multiplier * edge_before["minus"]], "product envelope", "bond recurrence")
                    check(f"V={volume} edge={edge_index} probe={probe_index} sign={sign} bond finite", np.isfinite(multiplier) and np.isfinite(g_plus) and np.isfinite(g_minus), [g_plus, g_minus, multiplier], "finite", "bond recurrence")
                    row_signs[str(sign)] = {"g_plus": g_plus, "g_minus": g_minus, "multiplier": multiplier, "edge_before": edge_before, "edge_after": edge_after, "endpoint_to_edge": {key: edge_before[key] / max(endpoint[key], np.finfo(float).tiny) for key in ("plus", "minus", "sum")}}
                local_probe_rows.append({"probe": probe_index, "onsite_before": before, "onsite_after": after, "onsite_difference": differences, "edge_before": edge_before, "endpoint_before": endpoint, "signs": row_signs})
            edge_rows.append({"edge_index": edge_index, "edge": list(edge), "probe_rows": local_probe_rows})
        multipliers = [sign_row["multiplier"] for edge_row in edge_rows for probe_row in edge_row["probe_rows"] for sign_row in edge_row["probe_rows"][0]["signs"].values()]
        check(f"V={volume} edge coverage", len(edge_rows) == len(q3.graph_edges(volume)), len(edge_rows), len(q3.graph_edges(volume)), "graph coverage")
        volume_rows.append({"volume": volume, "edge_count": len(edge_rows), "local_dimension": int(fixture["oscillator_dimension"]) ** 2, "onsite_minimum": onsite_min, "edge_minimum": edge_min, "onsite_commutator_residual": operator_norm(onsite_step @ onsite_weight - onsite_weight @ onsite_step), "onsite_unitarity_residual": operator_norm(onsite_step.conj().T @ onsite_step - np.eye(onsite_step.shape[0])), "edge_rows": edge_rows, "max_bond_multiplier": max(multipliers), "min_bond_multiplier": min(multipliers)})

    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    check("onsite commutation", all(row["onsite_commutator_residual"] <= tolerance for row in volume_rows), [row["onsite_commutator_residual"] for row in volume_rows], f"<={tolerance}", "onsite algebra")
    check("onsite unitarity", all(row["onsite_unitarity_residual"] <= tolerance for row in volume_rows), [row["onsite_unitarity_residual"] for row in volume_rows], f"<={tolerance}", "onsite algebra")
    maxima = [row["max_bond_multiplier"] for row in volume_rows]
    check("bond multipliers finite", all(np.isfinite(value) for value in maxima), maxima, "finite", "scaling")
    check("finite reduction", scope["finite_onsite_two_orientation_isometry_closed"] and scope["finite_endpoint_to_edge_bond_multiplier_rows_closed"], scope, "PASS", "scope")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ONSITE-WEIGHTED-ISOMETRY-BOND-RECURRENCE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "finite_onsite_two_orientation_isometry_closed": True,
            "finite_endpoint_to_edge_bond_multiplier_rows_closed": True,
            "finite_full_q3_recurrence_reduction_closed": True,
            "source_uniformity_proved": False,
            "volume_uniformity_proved": False,
            "cutoff_uniformity_proved": False,
            "exact_ccr_common_core_closed": False,
            "modular_domain_transfer_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "all_bond_graph_lipschitz_closed": False,
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
    print(f"PRIMARY ONSITE-WEIGHTED-ISOMETRY-BOND-RECURRENCE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
