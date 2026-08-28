#!/usr/bin/env python3
"""Hostile structural mutations for R-405."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-phase-conditioned-intrinsic-gap-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_phase_conditioned_intrinsic_gap" / "hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402


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


def conductance(pi: np.ndarray, momentum: np.ndarray, chi: float) -> np.ndarray:
    weights = np.asarray(pi, dtype=float)
    weights = weights / float(np.sum(weights))
    matrix = np.asarray(momentum, dtype=complex)
    result = (weights[:, None] + weights[None, :]) * np.square(np.abs(matrix)) / (2.0 * chi)
    np.fill_diagonal(result, 0.0)
    return result


def spectral_gap(pi: np.ndarray, edges: np.ndarray) -> tuple[float, np.ndarray]:
    weights = np.asarray(pi, dtype=float)
    weights = weights / float(np.sum(weights))
    laplacian = np.diag(np.sum(edges, axis=1)) - edges
    inverse = 1.0 / np.sqrt(weights)
    weighted = inverse[:, None] * laplacian * inverse[None, :]
    values = np.linalg.eigvalsh((weighted + weighted.T) / 2.0)
    return (float(values[1]) if len(values) > 1 else float("nan")), values


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    chi = float(Fraction(str(fixture["chi"])))
    gap_floor = float(fixture["gap_floor"])
    capacity_floor = float(fixture["capacity_floor"])
    zero_threshold = float(fixture["eigen_zero_threshold"])
    floor = float(fixture["probability_floor"])
    volume, dimension, beta = 2, 12, 8.0
    _, hamiltonian, _ = r399.split_system(volume, dimension, fixture)
    basis = r399.coordinate_basis(dimension, volume)
    state = r399.gibbs(hamiltonian, beta)
    reference, raw = r399.coordinate_distribution(state, basis, dimension, volume)
    levels, _vectors, momentum = r402.coordinate_data(dimension)
    minus = np.arange(dimension // 2, dtype=int)
    plus = np.arange(dimension - dimension // 2, dimension, dtype=int)
    conditional = r399.marginal(reference, [0], dimension).reshape(-1)
    conditional = conditional / float(np.sum(conditional))
    edges = conductance(conditional, momentum, chi)
    genuine_gap, genuine_values = spectral_gap(conditional, edges)
    cross_capacity = float(np.sum(edges[np.ix_(minus, plus)]))
    minus_mass = float(np.sum(conditional[minus]))
    plus_mass = float(np.sum(conditional[plus]))
    diagonal_q = np.diag(levels.astype(complex))
    q_edges = conductance(conditional, diagonal_q, chi)
    q_edge_count = int(np.count_nonzero(q_edges > float(fixture["capacity_floor"])))
    disconnected = edges.copy()
    disconnected[np.ix_(minus, plus)] = 0.0
    disconnected[np.ix_(plus, minus)] = 0.0
    disconnected_gap, disconnected_values = spectral_gap(conditional, disconnected)
    checks = [
        {"name": "genuine graph positive", "status": "PASS" if math.isfinite(genuine_gap) and genuine_gap > gap_floor else "FAIL", "actual": genuine_gap, "expected": f">{gap_floor}"},
        {"name": "q-for-p has no edges", "status": "PASS" if q_edge_count == 0 else "FAIL", "actual": q_edge_count, "expected": 0},
        {"name": "cross-edge deletion exposes second zero mode", "status": "PASS" if math.isfinite(disconnected_gap) and disconnected_gap <= zero_threshold else "FAIL", "actual": disconnected_gap, "expected": f"<={zero_threshold}"},
        {"name": "genuine cross capacity positive", "status": "PASS" if cross_capacity > capacity_floor else "FAIL", "actual": cross_capacity, "expected": f">{capacity_floor}"},
        {"name": "both phase masses positive", "status": "PASS" if min(minus_mass, plus_mass) > floor else "FAIL", "actual": [minus_mass, plus_mass], "expected": f">{floor}"},
    ]
    if not all(item["status"] == "PASS" for item in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r405-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-405", "exploration_id": "EXP-001250", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": {"volume": volume, "dimension": dimension, "beta": beta, "raw_reference_minimum": raw, "genuine_gap": genuine_gap, "genuine_zero_eigenvalue": float(genuine_values[0]), "cross_capacity": cross_capacity, "phase_masses": [minus_mass, plus_mass], "q_mutation_edge_count": q_edge_count, "cross_deleted_gap": disconnected_gap, "cross_deleted_eigenvalues": [float(value) for value in disconnected_values[:3]], "mutation": "p_to_q_and_cross_edge_deletion"}, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-405 HOSTILE PASS {len(checks)}/{len(checks)} genuine_gap={genuine_gap:.6g} cross={cross_capacity:.6g} q_edges={q_edge_count} deleted_gap={disconnected_gap:.6g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
