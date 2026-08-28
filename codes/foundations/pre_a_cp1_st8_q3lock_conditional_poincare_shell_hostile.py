#!/usr/bin/env python3
"""Hostile mutations for the R-399 conditional Poincare route.

The finite transfer is deliberately easy to overstate.  This lane checks
that dropping the conditional spectral-gap denominator and replacing the
conditional parent by an unconditional one are both detected on a fixed
actual-Q3 context.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-conditional-poincare-shell-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_conditional_poincare_shell.py"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_conditional_poincare_shell" / "hostile.json"


def load_primary():
    spec = importlib.util.spec_from_file_location("r399_primary_hostile", PRIMARY)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R-399 finite primitives")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atomic_json(path: Path, payload: dict) -> None:
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


def run(output: Path = DEFAULT_OUTPUT) -> dict:
    primary = load_primary()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    threshold = float(fixture["hostile_threshold"])
    probability_floor = float(fixture["probability_tolerance"])
    volume, dimension = 3, 4
    beta = min(float(Fraction(value)) for value in fixture["beta_values"])
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    delta = float(Fraction(str(fixture["time_step"])))
    mu = float(Fraction(str(fixture["shell_weight_mu"])))
    qs, hamiltonian, terms = primary.split_system(volume, dimension, fixture)
    basis = primary.coordinate_basis(dimension, volume)
    reference_state = primary.gibbs(hamiltonian, beta)
    reference, _ = primary.coordinate_distribution(reference_state, basis, dimension, volume)
    source = primary.q3.character(qs[0] + qs[1], -amplitude, hbar)
    seeded = primary.hermitian(source @ reference_state @ source.conj().T)
    order = list(reversed(range(len(terms))))
    prefixes = primary.all_prefixes(terms, order, 1, delta, hbar)
    prefix = prefixes[4][1]
    state = primary.hermitian(prefix.conj().T @ seeded @ prefix)
    sample, raw_minimum = primary.coordinate_distribution(state, basis, dimension, volume)
    collar = list(range(volume))
    metrics = primary.shell_metrics(reference, sample, collar, dimension, mu, probability_floor)
    genuine_deficit = metrics["poincare_residual"]
    weighted_deficit = metrics["weighted_poincare_residual"]
    naive_gradient_bound = float(sum(row["conditional_gradient_energy"] for row in metrics["shell_rows"][1:]))
    naive_weighted_gradient_bound = float(sum(math.exp(2.0 * mu * row["radius"]) * row["conditional_gradient_energy"] for row in metrics["shell_rows"][1:]))
    naive_deficit = metrics["shell_energy"] - naive_gradient_bound
    naive_weighted_deficit = metrics["weighted_shell_energy"] - naive_weighted_gradient_bound
    wrong_parent_shell = 0.0
    for radius in range(1, volume):
        sites = collar[: radius + 1]
        p = primary.marginal(reference, sites, dimension)
        q = primary.marginal(sample, sites, dimension)
        ratio = q / p
        wrong_parent_shell += float(np.sum(p * (ratio - 1.0) ** 2))
    wrong_parent_gap = abs(wrong_parent_shell - metrics["shell_energy"])
    checks = [
        {"name": "genuine Poincare transfer", "status": "PASS" if genuine_deficit >= -tolerance and weighted_deficit >= -tolerance else "FAIL", "actual": [genuine_deficit, weighted_deficit], "expected": f">=-{tolerance}"},
        {"name": "gap denominator mutation caught", "status": "PASS" if naive_deficit > threshold and naive_weighted_deficit > threshold else "FAIL", "actual": [naive_deficit, naive_weighted_deficit], "expected": f">{threshold}"},
        {"name": "conditional parent mutation caught", "status": "PASS" if wrong_parent_gap > threshold else "FAIL", "actual": wrong_parent_gap, "expected": f">{threshold}"},
        {"name": "positive finite gap", "status": "PASS" if metrics["minimum_conditional_gap"] > 0.0 else "FAIL", "actual": metrics["minimum_conditional_gap"], "expected": ">0"},
        {"name": "coordinate probabilities finite", "status": "PASS" if np.isfinite(raw_minimum) else "FAIL", "actual": raw_minimum, "expected": "finite"},
    ]
    if any(item["status"] != "PASS" for item in checks):
        raise AssertionError(checks)
    payload = {
        "schema": "tect/pre-a-r399-hostile/1.0",
        "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "result_id": "R-399",
        "exploration_id": "EXP-001244",
        "verdict": "PASS",
        "checks": checks,
        "derived": {
            "volume": volume,
            "dimension": dimension,
            "beta": beta,
            "prefix_length": 4,
            "orientation": "right",
            "shell_energy": metrics["shell_energy"],
            "weighted_shell_energy": metrics["weighted_shell_energy"],
            "poincare_bound": metrics["poincare_bound"],
            "weighted_poincare_bound": metrics["weighted_poincare_bound"],
            "minimum_conditional_gap": metrics["minimum_conditional_gap"],
            "genuine_deficit": genuine_deficit,
            "weighted_deficit": weighted_deficit,
            "naive_gradient_bound": naive_gradient_bound,
            "naive_weighted_gradient_bound": naive_weighted_gradient_bound,
            "naive_deficit": naive_deficit,
            "naive_weighted_deficit": naive_weighted_deficit,
            "wrong_parent_shell": wrong_parent_shell,
            "wrong_parent_gap": wrong_parent_gap,
            "raw_coordinate_minimum": raw_minimum,
        },
    }
    atomic_json(output, payload)
    print(f"R-399 HOSTILE PASS {len(checks)}/{len(checks)} naive_deficit={naive_deficit:.6g} parent_gap={wrong_parent_gap:.6g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
