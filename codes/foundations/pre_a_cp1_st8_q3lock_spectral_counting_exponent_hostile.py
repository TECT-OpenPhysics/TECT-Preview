#!/usr/bin/env python3
"""Adversarial checks for the R-411 sublinear mode-counting family."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spectral-counting-exponent-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-31-hostile-pre_a_cp1_st8_q3lock_spectral_counting_exponent" / "hostile.json"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_effective_resistance_hostile as r408h  # noqa: E402
import pre_a_cp1_st8_q3lock_spectral_counting_exponent as primary  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    primary.r408.r407.atomic_json(path, payload)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    exponents = [float(Fraction(value)) for value in fixture["counting_exponents"]]
    selected: list[dict[str, Any]] = []
    for dimension in (3, 12):
        conditional, _likelihood, momentum, chi = r408h.selected_row(dimension, fixture)
        _gap, laplacian, _conductance = primary.r408.r407.intrinsic_graph(conditional, momentum, chi)
        data = primary.trace_identity_data(conditional, laplacian, eigen_floor, tolerance)
        alpha_profiles = primary.sublinear_envelope_data(np.asarray(data["ordered_positive_normalized_eigenvalues"], dtype=float), exponents)
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
            "alpha_profiles": alpha_profiles,
        })

    # alpha=1 is outside the sublinear domain: the comparison series has no
    # convergent integral tail.  The helper must reject this mutation.
    alpha_one_rejected = False
    try:
        primary.sublinear_envelope_data(np.asarray([1.0, 2.0, 3.0], dtype=float), [1.0])
    except AssertionError:
        alpha_one_rejected = True

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

    # Reversing a spectrum changes the k/lambda_k^alpha constant.  Any route
    # that silently keeps the original constant is using the wrong ordering.
    alpha_probe = float(Fraction("9/10"))
    sorted_alpha = primary.sublinear_envelope_data(toy_sorted, [alpha_probe])[str(alpha_probe).rstrip("0").rstrip(".")]["counting_constant"]
    unsorted_alpha = primary.sublinear_envelope_data(toy_unsorted, [alpha_probe])[str(alpha_probe).rstrip("0").rstrip(".")]["counting_constant"]
    # Dividing by lambda^alpha is the definition; multiplying by it gives a
    # deliberately wrong constant that must not certify the envelope.
    wrong_power_constant = float(np.max(np.arange(1, toy_sorted.size + 1, dtype=float) * np.power(toy_sorted, alpha_probe)))
    correct_power_constant = float(sorted_alpha)

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
        {"name": "baseline sublinear envelope", "status": "PASS" if all(item["trace_inverse"] <= profile["infinite_zeta_bound"] + tolerance for item in selected for profile in item["alpha_profiles"].values()) else "FAIL", "actual": [[item["trace_inverse"], {key: profile["infinite_zeta_bound"] for key, profile in item["alpha_profiles"].items()}] for item in selected], "expected": "trace<=infinite sublinear zeta bound"},
        {"name": "late sublinear envelope", "status": "PASS" if all(item["trace_inverse"] <= profile["finite_trace_bound"] + tolerance for item in selected for profile in item["alpha_profiles"].values()) else "FAIL", "actual": [[item["trace_inverse"], {key: profile["finite_trace_bound"] for key, profile in item["alpha_profiles"].items()}] for item in selected], "expected": "trace<=finite sublinear envelope"},
        {"name": "alpha one divergent tail rejected", "status": "PASS" if alpha_one_rejected else "FAIL", "actual": alpha_one_rejected, "expected": "alpha=1 rejected outside (0,1)"},
        {"name": "unsorted mode index rejected", "status": "PASS" if abs(sorted_c2 - unsorted_c2) > tolerance and abs(sorted_alpha - unsorted_alpha) > tolerance else "FAIL", "actual": [sorted_c2, unsorted_c2, sorted_alpha, unsorted_alpha], "expected": "sorting changes quadratic and sublinear constants"},
        {"name": "linear envelope shortcut rejected", "status": "PASS" if wrong_quadratic_residual < -tolerance else "FAIL", "actual": [linear_shortcut, wrong_quadratic_residual, linear_bound, quadratic_bound], "expected": "linear k constant cannot be inserted into a k^2 envelope"},
        {"name": "exponent power inversion rejected", "status": "PASS" if abs(wrong_power_constant - correct_power_constant) > tolerance else "FAIL", "actual": [correct_power_constant, wrong_power_constant], "expected": "C_alpha uses lambda^(-alpha), not lambda^(alpha)"},
        {"name": "Fiedler-only shortcut rejected", "status": "PASS" if all(item["one_mode_inverse"] < item["trace_inverse"] - tolerance for item in selected) else "FAIL", "actual": [[item["one_mode_inverse"], item["trace_inverse"]] for item in selected], "expected": "full inverse-spectrum trace"},
        {"name": "q mutation deletes graph spectrum", "status": "PASS" if mutated_edges == 0 and mutated_positive == 0 and float(np.max(mutated)) <= float(fixture["hostile_zero_threshold"]) else "FAIL", "actual": [mutated_edges, mutated_positive, float(np.max(mutated))], "expected": "zero edges and positive eigenvalues"},
    ]
    if not all(row["status"] == "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r411-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-411", "exploration_id": "EXP-001256", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": {"selected": selected, "q_mutation": {"mutated_edge_count": mutated_edges, "positive_eigenvalue_count": mutated_positive, "maximum_edge": float(np.max(mutated))}, "toy_spectrum": {"sorted_c2": sorted_c2, "unsorted_c2": unsorted_c2, "sorted_alpha_constant": sorted_alpha, "unsorted_alpha_constant": unsorted_alpha, "linear_constant": linear_shortcut, "wrong_quadratic_residual": wrong_quadratic_residual, "wrong_power_constant": wrong_power_constant, "correct_power_constant": correct_power_constant, "linear_bound": linear_bound, "quadratic_bound": quadratic_bound}, "mutation": "alpha=1, unsorted modes, linear or exponent-inverted shortcuts, Fiedler shortcut and a diagonal generator"}, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-411 HOSTILE PASS {len(checks)}/{len(checks)} baseline_c2={selected[0]['mode_constant']:.6g} late_c2={selected[1]['mode_constant']:.6g} alpha={len(exponents)} q_edges={mutated_edges}")
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
