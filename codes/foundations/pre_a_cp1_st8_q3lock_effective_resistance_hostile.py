#!/usr/bin/env python3
"""Adversarial checks for the R-408 effective-resistance certificate."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-effective-resistance-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_effective_resistance" / "hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_effective_resistance as primary  # noqa: E402
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
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


def selected_row(dimension: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    volume = 2
    beta = max(float(Fraction(value)) for value in fixture["beta_values"])
    source_sign = max(int(value) for value in fixture["source_sign_values"])
    history_sign = max(int(value) for value in fixture["history_sign_values"])
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    chi = float(Fraction(str(fixture["chi"])))
    q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
    basis = r399.coordinate_basis(dimension, volume)
    _levels, _vectors, momentum = r402.coordinate_data(dimension)
    state = r399.gibbs(hamiltonian, beta)
    reference, _raw = r399.coordinate_distribution(state, basis, dimension, volume)
    source = q3.character(q_ops[0], source_sign * amplitude, hbar)
    seeded = r399.hermitian(source @ state @ source.conj().T)
    prefix = r399.all_prefixes(terms, list(range(len(terms))), history_sign, delta, hbar)[-1][1]
    evolved = r399.hermitian(prefix @ seeded @ prefix.conj().T)
    sample, _raw_sample = r399.coordinate_distribution(evolved, basis, dimension, volume)
    floor = float(fixture["probability_floor"])
    for _radius, conditional, likelihood in r402.conditional_rows(reference, sample, [0, 1], dimension, floor):
        pi = conditional / float(np.sum(conditional))
        mean = float(np.sum(pi * likelihood))
        variance = float(np.sum(pi * np.square(likelihood - mean)))
        if variance > float(fixture["variance_floor"]):
            return conditional, likelihood, momentum, chi
    raise AssertionError(f"no nonconstant row at d={dimension}")


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    selected: list[dict[str, Any]] = []
    for dimension in (3, 12):
        conditional, likelihood, momentum, chi = selected_row(dimension, fixture)
        gap, laplacian, conductance = primary.r407.intrinsic_graph(conditional, momentum, chi)
        data = primary.effective_resistance_data(conditional, laplacian, eigen_floor)
        pi = conditional / float(np.sum(conditional))
        energy = float(np.real(likelihood @ laplacian @ likelihood))
        mean = float(np.sum(pi * likelihood))
        variance = float(np.sum(pi * np.square(likelihood - mean)))
        selected.append({
            "dimension": dimension,
            "exact_gap": gap,
            "resistance_bound": data["resistance_bound"],
            "resistance_average": data["resistance_average"],
            "energy": energy,
            "variance": variance,
            "residual": energy - data["resistance_bound"] * variance,
            "positive_eigenvalue_count": data["positive_eigenvalue_count"],
            "maximum_effective_resistance": data["maximum_effective_resistance"],
        })

    # q is diagonal in its own coordinate basis.  Substituting q for p makes
    # every off-diagonal conductance vanish; a zero-mode pseudoinverse must not
    # silently be treated as a connected graph.
    levels, _vectors, _momentum = r402.coordinate_data(12)
    pi = np.full(len(levels), 1.0 / len(levels))
    mutated = (pi[:, None] + pi[None, :]) * np.square(np.abs(np.diag(levels))) / (2.0 * float(Fraction(str(fixture["chi"]))))
    np.fill_diagonal(mutated, 0.0)
    mutated_edges = int(np.count_nonzero(mutated > float(fixture["hostile_zero_threshold"])))
    mutated_laplacian = np.diag(np.sum(mutated, axis=1)) - mutated
    mutated_spectrum = np.linalg.eigvalsh(mutated_laplacian)
    mutated_positive = int(np.count_nonzero(mutated_spectrum > eigen_floor))

    # The unordered-pair convention is load-bearing.  On a three-node unit
    # path, Rbar=(1+1+2)/9=4/9 and the correct bound is 9/4.  Doubling that
    # bound violates the test function inequality.
    toy_pi = np.full(3, 1.0 / 3.0)
    toy_laplacian = np.array([[1.0, -1.0, 0.0], [-1.0, 2.0, -1.0], [0.0, -1.0, 1.0]])
    toy = primary.effective_resistance_data(toy_pi, toy_laplacian, eigen_floor)
    toy_values = np.array([1.0, 0.0, -1.0])
    toy_energy = float(toy_values @ toy_laplacian @ toy_values)
    toy_mean = float(np.sum(toy_pi * toy_values))
    toy_variance = float(np.sum(toy_pi * np.square(toy_values - toy_mean)))
    doubled_residual = toy_energy - 2.0 * toy["resistance_bound"] * toy_variance

    checks = [
        {"name": "baseline resistance bound positive", "status": "PASS" if selected[0]["resistance_bound"] > 0.0 else "FAIL", "actual": selected[0]["resistance_bound"], "expected": ">0"},
        {"name": "late resistance bound positive", "status": "PASS" if selected[1]["resistance_bound"] > 0.0 else "FAIL", "actual": selected[1]["resistance_bound"], "expected": ">0"},
        {"name": "resistance bound is valid", "status": "PASS" if all(item["residual"] >= -tolerance and item["resistance_bound"] <= item["exact_gap"] + tolerance for item in selected) else "FAIL", "actual": [[item["residual"], item["resistance_bound"], item["exact_gap"]] for item in selected], "expected": "nonnegative residual and bound <= exact gap"},
        {"name": "q mutation deletes edges and connectivity", "status": "PASS" if mutated_edges == 0 and mutated_positive == 0 and float(np.max(mutated)) <= float(fixture["hostile_zero_threshold"]) else "FAIL", "actual": [mutated_edges, mutated_positive, float(np.max(mutated))], "expected": "zero edges and positive eigenvalues"},
        {"name": "pseudoinverse pair normalization", "status": "PASS" if abs(toy["resistance_average"] - 4.0 / 9.0) <= tolerance and abs(toy["resistance_bound"] - 9.0 / 4.0) <= tolerance else "FAIL", "actual": [toy["resistance_average"], toy["resistance_bound"]], "expected": [4.0 / 9.0, 9.0 / 4.0]},
        {"name": "doubled bound rejected", "status": "PASS" if doubled_residual < -tolerance else "FAIL", "actual": doubled_residual, "expected": f"<-{tolerance}"},
    ]
    if not all(row["status"] == "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r408-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-408", "exploration_id": "EXP-001253", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": {"selected": selected, "q_mutation": {"mutated_edge_count": mutated_edges, "positive_eigenvalue_count": mutated_positive, "maximum_edge": float(np.max(mutated))}, "factor_audit": {"toy_resistance_average": toy["resistance_average"], "toy_correct_bound": toy["resistance_bound"], "toy_doubled_residual": doubled_residual}, "mutation": "replace_p_by_q_and_double_unordered_pair_bound"}, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-408 HOSTILE PASS {len(checks)}/{len(checks)} baseline_bound={selected[0]['resistance_bound']:.6g} late_bound={selected[1]['resistance_bound']:.6g} q_edges={mutated_edges} doubled_residual={doubled_residual:.6g}")
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
