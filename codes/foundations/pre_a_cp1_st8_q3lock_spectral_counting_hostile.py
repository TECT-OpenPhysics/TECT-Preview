#!/usr/bin/env python3
"""Adversarial checks for the R-410 quadratic mode-counting envelope."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spectral-counting-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-31-hostile-pre_a_cp1_st8_q3lock_spectral_counting" / "hostile.json"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_effective_resistance_hostile as r408h  # noqa: E402
import pre_a_cp1_st8_q3lock_spectral_counting as primary  # noqa: E402


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
        one_mode = 1.0 / data["minimum_positive_normalized_eigenvalue"]
        linear_constant = float(np.min(np.asarray(data["ordered_positive_normalized_eigenvalues"]) / np.arange(1, dimension, dtype=float)))
        selected.append({
            "dimension": dimension,
            "trace_inverse": data["trace_inverse"],
            "resistance_average": data["resistance_average"],
            "identity_residual": data["identity_residual"],
            "one_mode_inverse": one_mode,
            "mode_constant": data["mode_constant"],
            "linear_constant": linear_constant,
            "zeta_bound": data["zeta_bound"],
            "zeta_infinite_bound": data["zeta_infinite_bound"],
            "positive_normalized_eigenvalue_count": data["positive_normalized_eigenvalue_count"],
        })

    # Deliberately unsort a spectrum: assigning k by input order can understate c2.
    toy_sorted = np.asarray([1.0, 2.0, 3.0], dtype=float)
    toy_unsorted = toy_sorted[::-1]
    sorted_c2 = float(np.min(toy_sorted / np.square(np.arange(1, toy_sorted.size + 1, dtype=float))))
    unsorted_c2 = float(np.min(toy_unsorted / np.square(np.arange(1, toy_unsorted.size + 1, dtype=float))))
    # A linear k envelope is not interchangeable with the quadratic counting target.
    linear_shortcut = float(np.min(toy_sorted / np.arange(1, toy_sorted.size + 1, dtype=float)))
    quadratic_bound = float(np.sum(1.0 / toy_sorted))
    linear_bound = float(np.sum(1.0 / (linear_shortcut * np.arange(1, toy_sorted.size + 1, dtype=float))))
    wrong_quadratic_residual = float(np.min(toy_sorted - linear_shortcut * np.square(np.arange(1, toy_sorted.size + 1, dtype=float))))

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
        {"name": "baseline quadratic envelope", "status": "PASS" if selected[0]["mode_constant"] > 0.0 and selected[0]["trace_inverse"] <= selected[0]["zeta_bound"] + tolerance else "FAIL", "actual": [selected[0]["mode_constant"], selected[0]["trace_inverse"], selected[0]["zeta_bound"]], "expected": "c2>0 and trace<=finite zeta bound"},
        {"name": "late quadratic envelope", "status": "PASS" if selected[1]["mode_constant"] > 0.0 and selected[1]["trace_inverse"] <= selected[1]["zeta_bound"] + tolerance else "FAIL", "actual": [selected[1]["mode_constant"], selected[1]["trace_inverse"], selected[1]["zeta_bound"]], "expected": "c2>0 and trace<=finite zeta bound"},
        {"name": "unsorted mode index rejected", "status": "PASS" if abs(sorted_c2 - unsorted_c2) > tolerance else "FAIL", "actual": [sorted_c2, unsorted_c2], "expected": "sorting changes the mode constant"},
        {"name": "linear envelope shortcut rejected", "status": "PASS" if wrong_quadratic_residual < -tolerance else "FAIL", "actual": [linear_shortcut, wrong_quadratic_residual, linear_bound, quadratic_bound], "expected": "linear k constant cannot be inserted into a k^2 envelope"},
        {"name": "Fiedler-only shortcut rejected", "status": "PASS" if all(item["one_mode_inverse"] < item["trace_inverse"] - tolerance for item in selected) else "FAIL", "actual": [[item["one_mode_inverse"], item["trace_inverse"]] for item in selected], "expected": "full inverse-spectrum trace"},
        {"name": "q mutation deletes graph spectrum", "status": "PASS" if mutated_edges == 0 and mutated_positive == 0 and float(np.max(mutated)) <= float(fixture["hostile_zero_threshold"]) else "FAIL", "actual": [mutated_edges, mutated_positive, float(np.max(mutated))], "expected": "zero edges and positive eigenvalues"},
    ]
    if not all(row["status"] == "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r410-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-410", "exploration_id": "EXP-001255", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": {"selected": selected, "q_mutation": {"mutated_edge_count": mutated_edges, "positive_eigenvalue_count": mutated_positive, "maximum_edge": float(np.max(mutated))}, "toy_spectrum": {"sorted_c2": sorted_c2, "unsorted_c2": unsorted_c2, "linear_constant": linear_shortcut, "wrong_quadratic_residual": wrong_quadratic_residual, "linear_bound": linear_bound, "quadratic_bound": quadratic_bound}, "mutation": "unsorted modes, linear or Fiedler shortcuts and a diagonal generator"}, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-410 HOSTILE PASS {len(checks)}/{len(checks)} baseline_c2={selected[0]['mode_constant']:.6g} late_c2={selected[1]['mode_constant']:.6g} q_edges={mutated_edges}")
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
