#!/usr/bin/env python3
"""Hostile mutations for the R-406 harmonic Schur route."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-harmonic-schur-capacity-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_harmonic_schur_capacity" / "hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_harmonic_schur_capacity as primary  # noqa: E402


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


def weighted_operator(pi: np.ndarray, edges: np.ndarray) -> np.ndarray:
    weights = np.asarray(pi, dtype=float)
    weights = weights / float(np.sum(weights))
    laplacian = np.diag(np.sum(edges, axis=1)) - edges
    inverse = 1.0 / np.sqrt(weights)
    return (inverse[:, None] * laplacian * inverse[None, :] + (inverse[:, None] * laplacian * inverse[None, :]).T) / 2.0


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    floor = float(fixture["probability_floor"])
    zero_threshold = float(fixture["eigen_zero_threshold"])
    gap_floor = float(fixture["gap_floor"])
    capacity_floor = 1.0e-14
    chi = float(Fraction(str(fixture["chi"])))
    volume, dimension, beta = 2, 12, 8.0
    _, hamiltonian, _ = r399.split_system(volume, dimension, fixture)
    basis = r399.coordinate_basis(dimension, volume)
    state = r399.gibbs(hamiltonian, beta)
    reference, raw = r399.coordinate_distribution(state, basis, dimension, volume)
    conditional = r399.marginal(reference, [0], dimension).reshape(-1)
    conditional = conditional / float(np.sum(conditional))
    levels, _single_basis, momentum = r402.coordinate_data(dimension)
    lower, upper, neutral = primary.phase_indices(levels)
    blocks = [lower, neutral, upper] if len(neutral) else [lower, upper]
    full_gap, edges = primary.normalized_graph(conditional, momentum, chi)
    data = primary.harmonic_split(conditional, edges, blocks)
    operator = weighted_operator(conditional, edges)
    values, vectors = np.linalg.eigh(operator)
    fiedler = vectors[:, 1]
    fiedler_energy = float(fiedler @ (operator @ fiedler))
    fiedler_variance = float(fiedler @ fiedler)
    naive_false_margin = data["naive_block_gap"] * fiedler_variance - fiedler_energy
    # Delete every inter-block edge.  The resulting graph must expose one
    # zero mode per disconnected block (neutral is absent in this fixture).
    disconnected = edges.copy()
    for left, block_left in enumerate(blocks):
        for right, block_right in enumerate(blocks):
            if left != right:
                disconnected[np.ix_(block_left, block_right)] = 0.0
    disconnected_values = np.linalg.eigvalsh(weighted_operator(conditional, disconnected))
    zero_count = int(np.count_nonzero(np.abs(disconnected_values) <= zero_threshold))
    diagonal_q = np.diag(levels.astype(complex))
    q_edges = (conditional[:, None] + conditional[None, :]) * np.square(np.abs(diagonal_q)) / (2.0 * chi)
    np.fill_diagonal(q_edges, 0.0)
    q_edge_count = int(np.count_nonzero(q_edges > capacity_floor))
    checks = [
        {"name": "reference mass", "status": "PASS" if raw >= -1.0e-8 and float(np.min(reference)) > floor else "FAIL", "actual": [raw, float(np.min(reference))], "expected": f"raw>=-1e-8 and min>{floor}"},
        {"name": "genuine graph connected", "status": "PASS" if full_gap > gap_floor else "FAIL", "actual": full_gap, "expected": f">{gap_floor}"},
        {"name": "harmonic Schur lower survives", "status": "PASS" if data["decomposition_gap"] > 0.0 and data["decomposition_gap"] <= full_gap + 2.0e-8 else "FAIL", "actual": [data["decomposition_gap"], full_gap], "expected": "0<corrected gap<=full gap"},
        {"name": "naive Ritz is not lower bound", "status": "PASS" if naive_false_margin > 1.0e-9 else "FAIL", "actual": naive_false_margin, "expected": ">1e-9"},
        {"name": "cross-block deletion exposes zeros", "status": "PASS" if zero_count >= len(blocks) else "FAIL", "actual": [zero_count, disconnected_values.tolist()], "expected": f">={len(blocks)} zero modes"},
        {"name": "q-for-p mutation has no edges", "status": "PASS" if q_edge_count == 0 else "FAIL", "actual": q_edge_count, "expected": 0},
    ]
    if not all(item["status"] == "PASS" for item in checks):
        raise AssertionError(checks)
    payload = {
        "schema": "tect/pre-a-r406-hostile/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-406",
        "exploration_id": "EXP-001251",
        "verdict": "PASS",
        "checks": checks,
        "assertion_count": len(checks),
        "derived": {
            "volume": volume,
            "dimension": dimension,
            "beta": beta,
            "full_gap": full_gap,
            "coarse_schur_gap": data["coarse_gap"],
            "residual_gap": data["residual_gap"],
            "decomposition_gap": data["decomposition_gap"],
            "naive_block_gap": data["naive_block_gap"],
            "naive_false_lower_bound_margin": naive_false_margin,
            "cross_deleted_zero_count": zero_count,
            "cross_deleted_spectrum": disconnected_values.tolist(),
            "q_mutation_edge_count": q_edge_count,
            "block_count": len(blocks),
        },
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-406 HOSTILE PASS {len(checks)}/{len(checks)} full={full_gap:.6g} corrected={data['decomposition_gap']:.6g} naive_margin={naive_false_margin:.6g} zero_modes={zero_count} q_edges={q_edge_count}")
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
