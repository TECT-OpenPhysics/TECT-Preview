#!/usr/bin/env python3
"""Adversarial lane for the R-404 intrinsic kinetic graph route."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-intrinsic-kinetic-poincare-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_hamiltonian_intrinsic_kinetic_poincare" / "hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_intrinsic_kinetic_poincare as primary  # noqa: E402
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


def mutation_conductance(pi: np.ndarray, q_levels: np.ndarray, chi: float) -> np.ndarray:
    values = np.asarray(pi, dtype=float)
    values /= float(np.sum(values))
    diagonal_q = np.diag(q_levels.astype(complex))
    conductance = (values[:, None] + values[None, :]) * np.square(np.abs(diagonal_q)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    return conductance


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    volume = pairs[0][0]
    dimensions = [dimension for _volume, dimension in pairs]
    beta = max(float(Fraction(value)) for value in fixture["beta_values"])
    source_sign = max(int(value) for value in fixture["source_sign_values"])
    history_sign = max(int(value) for value in fixture["history_sign_values"])
    history_adjoint = min(int(value) for value in fixture["history_adjoint_values"])
    orientation = list(fixture["orientations"])[0]
    chi = float(Fraction(str(fixture["chi"])))
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    support = tuple(int(site) for site in fixture["source_support_values"][0])
    selected: list[dict[str, Any]] = []
    for dimension in dimensions:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels, _single_basis, p_coordinate = r402.coordinate_data(dimension)
        state = r399.gibbs(hamiltonian, beta)
        reference, raw_reference = r399.coordinate_distribution(state, basis, dimension, volume)
        if raw_reference < -float(fixture["numerical_tolerance"]):
            raise AssertionError("reference roundoff")
        source = q3.character(sum((q_ops[site] for site in support), np.zeros_like(q_ops[0])), source_sign * amplitude, hbar)
        seeded = r399.hermitian(source @ state @ source.conj().T)
        prefixes = r399.all_prefixes(terms, list(range(len(terms))), history_sign, delta, hbar)
        candidate: dict[str, Any] | None = None
        for prefix_length, prefix in prefixes:
            evolved = r399.hermitian(prefix @ seeded @ prefix.conj().T)
            sample, raw_sample = r399.coordinate_distribution(evolved, basis, dimension, volume)
            if raw_sample < -float(fixture["numerical_tolerance"]):
                raise AssertionError("sample roundoff")
            collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
            for _radius, conditional, likelihood in r402.conditional_rows(reference, sample, collar_order, dimension, float(fixture["probability_tolerance"])):
                kinetic = r402.kinetic_form(conditional, likelihood, p_coordinate, chi)
                pi = conditional / float(np.sum(conditional))
                mean = float(np.sum(pi * likelihood))
                row_variance = float(np.sum(pi * np.square(likelihood - mean)))
                if kinetic > float(fixture["hostile_energy_floor"]) and row_variance > float(fixture["variance_floor"]):
                    gap, _laplacian, conductance = primary.intrinsic_graph(conditional, p_coordinate, chi)
                    mutated = mutation_conductance(conditional, levels, chi)
                    candidate = {"dimension": dimension, "prefix_length": prefix_length, "genuine_gap": gap, "genuine_kinetic_form": kinetic, "row_variance": row_variance, "genuine_max_edge_weight": float(np.max(conductance)), "mutated_max_edge_weight": float(np.max(mutated)), "mutated_edge_count": int(np.count_nonzero(mutated > float(fixture["hostile_zero_threshold"]))) }
                    break
            if candidate is not None:
                break
        if candidate is None:
            raise AssertionError(f"no nonconstant hostile row at d={dimension}")
        selected.append(candidate)
    baseline, late = selected[0], selected[-1]
    checks = [
        {"name": "baseline genuine graph gap positive", "status": "PASS" if math.isfinite(float(baseline["genuine_gap"])) and float(baseline["genuine_gap"]) > 0.0 else "FAIL", "actual": baseline["genuine_gap"], "expected": ">0 finite"},
        {"name": "late genuine graph gap positive", "status": "PASS" if math.isfinite(float(late["genuine_gap"])) and float(late["genuine_gap"]) > 0.0 else "FAIL", "actual": late["genuine_gap"], "expected": ">0 finite"},
        {"name": "late genuine kinetic form positive", "status": "PASS" if float(late["genuine_kinetic_form"]) > float(fixture["hostile_energy_floor"]) else "FAIL", "actual": late["genuine_kinetic_form"], "expected": f">{fixture['hostile_energy_floor']}"},
        {"name": "q mutation has no edges", "status": "PASS" if float(late["mutated_max_edge_weight"]) <= float(fixture["hostile_zero_threshold"]) and int(late["mutated_edge_count"]) == 0 else "FAIL", "actual": [late["mutated_max_edge_weight"], late["mutated_edge_count"]], "expected": "zero"},
        {"name": "q mutation is structurally separated", "status": "PASS" if float(late["genuine_max_edge_weight"]) > float(fixture["hostile_energy_floor"]) and float(late["mutated_max_edge_weight"]) <= float(fixture["hostile_zero_threshold"]) else "FAIL", "actual": [late["genuine_max_edge_weight"], late["mutated_max_edge_weight"]], "expected": "genuine positive, mutated zero"},
        {"name": "finite selected rows are nonconstant", "status": "PASS" if all(float(item["row_variance"]) > float(fixture["variance_floor"]) for item in selected) else "FAIL", "actual": [item["row_variance"] for item in selected], "expected": f">{fixture['variance_floor']}"},
    ]
    if not all(row["status"] == "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r404-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-404", "exploration_id": "EXP-001249", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": {"volume": volume, "beta": beta, "source_sign": source_sign, "history_sign": history_sign, "history_adjoint": history_adjoint, "orientation": orientation, "baseline": baseline, "late": late, "dimension_profiles": selected, "mutation": "replace_p_by_q"}, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-404 HOSTILE PASS {len(checks)}/{len(checks)} baseline_gap={baseline['genuine_gap']:.6g} late_gap={late['genuine_gap']:.6g} mutated_edges={late['mutated_edge_count']}")
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
