#!/usr/bin/env python3
"""Adversarial lane for the R-403 increasing-cutoff stress.

The hostile lane checks two easy ways a cutoff profile can be misread: a
nonzero ratio must not be created by a zero coordinate denominator, and the
Hamiltonian momentum must not be silently replaced by the commuting
coordinate multiplier.  It also requires the reported late-cutoff growth to
be visible on the same finite fixture.
"""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-carre-du-champ-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_cutoff_stress" / "hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
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


def q_mutation(probabilities: np.ndarray, likelihood: np.ndarray, levels: np.ndarray, chi: float) -> float:
    """Replace p by q; q and F(q) commute, so the mutated form is zero."""
    pi = np.asarray(probabilities, dtype=float)
    f = np.asarray(likelihood, dtype=float)
    q_coordinate = np.diag(levels.astype(complex))
    multiplier = np.diag(f.astype(complex))
    commutator = q_coordinate @ multiplier - multiplier @ q_coordinate
    gram = commutator.conj().T @ commutator
    return max(0.0, float(np.real(np.sum((pi / float(np.sum(pi))) * np.diag(gram)))) / (2.0 * chi))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    dimensions = [int(dimension) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    volume = 2
    beta = max(float(Fraction(value)) for value in fixture["beta_values"])
    floor = float(fixture["probability_tolerance"])
    tolerance = float(fixture["numerical_tolerance"])
    chi = float(Fraction(str(fixture["chi"])))
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    source_sign = 1
    history_sign = 1
    history_adjoint = 0
    order_name = "forward"
    orientation = "right"
    maxima: list[dict[str, Any]] = []
    for dimension in dimensions:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels, _, p_coordinate = r402.coordinate_data(dimension)
        spacings = np.diff(levels)
        state = r399.gibbs(hamiltonian, beta)
        reference, raw_reference = r399.coordinate_distribution(state, basis, dimension, volume)
        if raw_reference < -tolerance:
            raise AssertionError("reference coordinate roundoff")
        source = q3.character(q_ops[0], source_sign * amplitude, hbar)
        seeded = r399.hermitian(source @ state @ source.conj().T)
        prefixes = r399.all_prefixes(terms, list(range(len(terms))), history_sign, delta, hbar)
        best: dict[str, Any] | None = None
        for prefix_length, prefix in prefixes:
            evolved = r399.hermitian(prefix @ seeded @ prefix.conj().T)
            sample, raw_sample = r399.coordinate_distribution(evolved, basis, dimension, volume)
            if raw_sample < -tolerance:
                raise AssertionError("sample coordinate roundoff")
            for radius, conditional, likelihood in r402.conditional_rows(reference, sample, list(range(volume)), dimension, floor):
                coordinate_energy = r402.coordinate_form(conditional, likelihood, spacings)
                genuine = r402.kinetic_form(conditional, likelihood, p_coordinate, chi)
                mutated = q_mutation(conditional, likelihood, levels, chi)
                candidate = {
                    "dimension": dimension,
                    "radius": radius,
                    "prefix_length": prefix_length,
                    "coordinate_form": coordinate_energy,
                    "genuine_kinetic_form": genuine,
                    "mutated_q_form": mutated,
                }
                if coordinate_energy > float(fixture["ratio_floor"]):
                    candidate["ratio"] = genuine / coordinate_energy
                    if best is None or float(candidate["ratio"]) > float(best["ratio"]):
                        best = candidate
        if best is None:
            raise AssertionError(f"no nonzero ratio row at d={dimension}")
        maxima.append(best)
    baseline = maxima[0]
    late = maxima[-1]
    growth = float(late["ratio"]) / float(baseline["ratio"])
    energy_floor = float(fixture["hostile_energy_floor"])
    zero_threshold = float(fixture["hostile_zero_threshold"])
    checks = [
        {"name": "baseline ratio is finite and positive", "status": "PASS" if math.isfinite(float(baseline["ratio"])) and float(baseline["ratio"]) > 0.0 else "FAIL", "actual": baseline["ratio"], "expected": ">0 finite"},
        {"name": "late ratio is finite and positive", "status": "PASS" if math.isfinite(float(late["ratio"])) and float(late["ratio"]) > 0.0 else "FAIL", "actual": late["ratio"], "expected": ">0 finite"},
        {"name": "late profile growth is visible", "status": "PASS" if growth > float(fixture["late_growth_threshold"]) else "FAIL", "actual": growth, "expected": f">{fixture['late_growth_threshold']}"},
        {"name": "genuine late kinetic row is nonzero", "status": "PASS" if float(late["genuine_kinetic_form"]) > energy_floor else "FAIL", "actual": late["genuine_kinetic_form"], "expected": f">{energy_floor}"},
        {"name": "q-for-p mutation vanishes", "status": "PASS" if math.isfinite(float(late["mutated_q_form"])) and float(late["mutated_q_form"]) <= zero_threshold else "FAIL", "actual": late["mutated_q_form"], "expected": f"<={zero_threshold}"},
        {"name": "mutation separates forms", "status": "PASS" if float(late["genuine_kinetic_form"]) - float(late["mutated_q_form"]) > energy_floor else "FAIL", "actual": float(late["genuine_kinetic_form"]) - float(late["mutated_q_form"]), "expected": f">{energy_floor}"},
        {"name": "finite profile has no zero-denominator claim", "status": "PASS" if all(float(item["coordinate_form"]) > float(fixture["ratio_floor"]) for item in maxima) else "FAIL", "actual": [item["coordinate_form"] for item in maxima], "expected": f">{fixture['ratio_floor']}"},
    ]
    if not all(row["status"] == "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {
        "schema": "tect/pre-a-r403-hostile/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-403",
        "exploration_id": "EXP-001248",
        "verdict": "PASS",
        "checks": checks,
        "assertion_count": len(checks),
        "derived": {"volume": volume, "beta": beta, "order": order_name, "history_sign": history_sign, "history_adjoint": history_adjoint, "orientation": orientation, "baseline": baseline, "late": late, "late_upper_profile_growth_ratio": growth, "dimension_maxima": maxima, "mutation": "replace_p_by_q"},
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-403 HOSTILE PASS {len(checks)}/{len(checks)} baseline={baseline['ratio']:.6g} late={late['ratio']:.6g} growth={growth:.6g}")
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
