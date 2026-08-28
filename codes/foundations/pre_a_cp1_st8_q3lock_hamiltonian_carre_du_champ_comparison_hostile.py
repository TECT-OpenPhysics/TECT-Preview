#!/usr/bin/env python3
"""Adversarial lane for R-402.

The mutation replaces the Hamiltonian momentum p by the coordinate q.  Since
both q and the likelihood multiplier F=f(q) are diagonal in the q basis, the
mutated carré-du-champ must vanish while the genuine kinetic form is nonzero
on at least one actual history row.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-carre-du-champ-comparison-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison" / "hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as primary  # noqa: E402
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
    volume, dimension = 2, max(int(value) for item in fixture["admissible_pairs"] if int(item["volume"]) == 2 for value in item["cutoff_dimensions"])
    beta = max(float(Fraction(value)) for value in fixture["beta_values"])
    q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
    basis = r399.coordinate_basis(dimension, volume)
    levels, _, p_coordinate = primary.coordinate_data(dimension)
    spacings = np.diff(levels)
    state = r399.gibbs(hamiltonian, beta)
    reference, raw_reference = r399.coordinate_distribution(state, basis, dimension, volume)
    if raw_reference < -float(fixture["numerical_tolerance"]):
        raise AssertionError("reference coordinate roundoff")
    support = (0,)
    generator = q_ops[0]
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    source = q3.character(generator, amplitude, hbar)
    seeded = r399.hermitian(source @ state @ source.conj().T)
    best: dict[str, Any] | None = None
    floor = float(fixture["probability_tolerance"])
    for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms)))))):
        for history_sign in (int(value) for value in fixture["history_sign_values"]):
            for prefix_length, prefix in r399.all_prefixes(terms, order, history_sign, float(Fraction(str(fixture["time_step"]))), hbar):
                for history_adjoint in (int(value) for value in fixture["history_adjoint_values"]):
                    evolved = r399.hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else r399.hermitian(prefix.conj().T @ seeded @ prefix)
                    sample, raw_sample = r399.coordinate_distribution(evolved, basis, dimension, volume)
                    if raw_sample < -float(fixture["numerical_tolerance"]):
                        raise AssertionError("sample coordinate roundoff")
                    for orientation in fixture["orientations"]:
                        order_sites = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                        for radius, conditional, likelihood in primary.conditional_rows(reference, sample, order_sites, dimension, floor):
                            coordinate_energy = primary.coordinate_form(conditional, likelihood, spacings)
                            genuine = primary.kinetic_form(conditional, likelihood, p_coordinate, float(Fraction(str(fixture["chi"]))))
                            mutated = q_mutation(conditional, likelihood, levels, float(Fraction(str(fixture["chi"]))))
                            candidate = {"radius": radius, "coordinate_form": coordinate_energy, "genuine_kinetic_form": genuine, "mutated_q_form": mutated, "order": order_name, "history_sign": history_sign, "prefix_length": prefix_length, "history_adjoint": history_adjoint, "orientation": orientation}
                            if best is None or genuine > float(best["genuine_kinetic_form"]):
                                best = candidate
    if best is None:
        raise AssertionError("no hostile candidate")
    energy_floor = float(fixture["hostile_energy_floor"])
    zero_threshold = float(fixture["hostile_zero_threshold"])
    checks = [
        {"name": "genuine kinetic row is nonzero", "status": "PASS" if math.isfinite(float(best["genuine_kinetic_form"])) and float(best["genuine_kinetic_form"]) > energy_floor else "FAIL", "actual": best["genuine_kinetic_form"], "expected": f">{energy_floor}"},
        {"name": "coordinate form is finite", "status": "PASS" if math.isfinite(float(best["coordinate_form"])) and float(best["coordinate_form"]) >= 0.0 else "FAIL", "actual": best["coordinate_form"], "expected": ">=0"},
        {"name": "q-for-p mutation vanishes", "status": "PASS" if math.isfinite(float(best["mutated_q_form"])) and float(best["mutated_q_form"]) <= zero_threshold else "FAIL", "actual": best["mutated_q_form"], "expected": f"<={zero_threshold}"},
        {"name": "mutation separates forms", "status": "PASS" if float(best["genuine_kinetic_form"]) - float(best["mutated_q_form"]) > energy_floor else "FAIL", "actual": float(best["genuine_kinetic_form"]) - float(best["mutated_q_form"]), "expected": f">{energy_floor}"},
    ]
    if not all(row["status"] == "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r402-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-402", "exploration_id": "EXP-001247", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": {"volume": volume, "dimension": dimension, "beta": beta, "mutation": "replace_p_by_q", **best}, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-402 HOSTILE PASS {len(checks)}/{len(checks)} genuine={best['genuine_kinetic_form']:.6g} mutated={best['mutated_q_form']:.6g}")
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
