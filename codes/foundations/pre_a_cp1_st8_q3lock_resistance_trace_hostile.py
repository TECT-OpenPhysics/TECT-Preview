#!/usr/bin/env python3
"""Adversarial checks for the R-409 Green-trace identity."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-resistance-trace-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_resistance_trace" / "hostile.json"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_effective_resistance_hostile as r408h  # noqa: E402
import pre_a_cp1_st8_q3lock_resistance_trace as primary  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    primary.r408.r407.atomic_json(path, payload)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    selected: list[dict[str, Any]] = []
    for dimension in (3, 12):
        conditional, _likelihood, momentum, chi = r408h.selected_row(dimension, fixture)
        _gap, laplacian, _conductance = primary.r408.r407.intrinsic_graph(conditional, momentum, chi)
        data = primary.trace_identity_data(conditional, laplacian, eigen_floor, tolerance)
        eigenvalues = np.linalg.eigvalsh((laplacian + laplacian.T) / 2.0)
        raw_positive = eigenvalues[eigenvalues > tolerance]
        raw_trace = float(np.sum(1.0 / raw_positive))
        one_mode = 1.0 / data["minimum_positive_normalized_eigenvalue"]
        selected.append({
            "dimension": dimension,
            "trace_inverse": data["trace_inverse"],
            "resistance_average": data["resistance_average"],
            "identity_residual": data["identity_residual"],
            "directed_pair_average": 2.0 * data["resistance_average"],
            "raw_laplacian_trace": raw_trace,
            "one_mode_inverse": one_mode,
            "positive_normalized_eigenvalue_count": data["positive_normalized_eigenvalue_count"],
        })

    # Diagonal q has no off-diagonal entries, hence no kinetic graph edges.
    levels, _vectors, _momentum = primary.r402.coordinate_data(12)
    pi = np.full(len(levels), 1.0 / len(levels))
    mutated = (pi[:, None] + pi[None, :]) * np.square(np.abs(np.diag(levels))) / (2.0 * float(Fraction(str(fixture["chi"]))))
    np.fill_diagonal(mutated, 0.0)
    mutated_edges = int(np.count_nonzero(mutated > float(fixture["hostile_zero_threshold"])))
    mutated_laplacian = np.diag(np.sum(mutated, axis=1)) - mutated
    mutated_spectrum = np.linalg.eigvalsh(mutated_laplacian)
    mutated_positive = int(np.count_nonzero(mutated_spectrum > max(eigen_floor, tolerance)))

    checks = [
        {"name": "baseline pair/trace identity", "status": "PASS" if abs(selected[0]["identity_residual"]) <= tolerance else "FAIL", "actual": selected[0]["identity_residual"], "expected": f"abs <= {tolerance}"},
        {"name": "late pair/trace identity", "status": "PASS" if abs(selected[1]["identity_residual"]) <= tolerance else "FAIL", "actual": selected[1]["identity_residual"], "expected": f"abs <= {tolerance}"},
        {"name": "directed-pair doubling rejected", "status": "PASS" if all(abs(item["directed_pair_average"] - item["trace_inverse"]) > tolerance for item in selected) else "FAIL", "actual": [[item["directed_pair_average"], item["trace_inverse"]] for item in selected], "expected": "directed sum differs by factor two"},
        {"name": "unnormalized-L trace rejected", "status": "PASS" if all(abs(item["raw_laplacian_trace"] - item["trace_inverse"]) > tolerance for item in selected) else "FAIL", "actual": [[item["raw_laplacian_trace"], item["trace_inverse"]] for item in selected], "expected": "normalized trace only"},
        {"name": "one-mode shortcut rejected", "status": "PASS" if all(item["one_mode_inverse"] < item["trace_inverse"] - tolerance for item in selected) else "FAIL", "actual": [[item["one_mode_inverse"], item["trace_inverse"]] for item in selected], "expected": "full inverse-spectrum trace"},
        {"name": "q mutation deletes graph spectrum", "status": "PASS" if mutated_edges == 0 and mutated_positive == 0 and float(np.max(mutated)) <= float(fixture["hostile_zero_threshold"]) else "FAIL", "actual": [mutated_edges, mutated_positive, float(np.max(mutated))], "expected": "zero edges and positive eigenvalues"},
    ]
    if not all(row["status"] == "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r409-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-409", "exploration_id": "EXP-001254", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": {"selected": selected, "q_mutation": {"mutated_edge_count": mutated_edges, "positive_eigenvalue_count": mutated_positive, "maximum_edge": float(np.max(mutated))}, "mutation": "double_directed_pairs_use_unnormalized_laplacian_and_keep_only_fiedler_mode"}, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-409 HOSTILE PASS {len(checks)}/{len(checks)} baseline_trace={selected[0]['trace_inverse']:.6g} late_trace={selected[1]['trace_inverse']:.6g} q_edges={mutated_edges}")
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
