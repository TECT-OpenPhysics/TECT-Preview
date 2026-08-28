#!/usr/bin/env python3
"""Hostile mutations for the R-398 conditioned-collar decomposition.

The selected finite row checks that the genuine Doob increments are retained.
Two intentionally wrong reconstructions (calling the full chi-square a shell
cost and dropping the local term) must be separated from the exact identity.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-conditioned-collar-martingale-influence-finite-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_conditioned_collar_martingale_influence.py"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_conditioned_collar_martingale_influence" / "hostile.json"


def load_primary():
    import importlib.util

    spec = importlib.util.spec_from_file_location("r398_primary_hostile", PRIMARY)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R-398 finite primitives")
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
    volume, dimension, beta = 3, 4, min(float(Fraction(value)) for value in fixture["beta_values"])
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    delta = float(Fraction(str(fixture["time_step"])))
    mu = float(Fraction(str(fixture["shell_weight_mu"])))
    qs, hamiltonian, terms = primary.split_system(volume, dimension, fixture)
    basis = primary.coordinate_basis(dimension, volume)
    reference_state = primary.gibbs(hamiltonian, beta)
    reference, _ = primary.coordinate_distribution(reference_state, basis, dimension, volume)
    generator = qs[0]
    source = primary.q3.character(generator, -amplitude, hbar)
    seeded = primary.hermitian(source @ reference_state @ source.conj().T)
    order = list(reversed(range(len(terms))))
    prefixes = primary.all_prefixes(terms, order, -1, delta, hbar)
    prefix_length, prefix = prefixes[2]
    state = primary.hermitian(prefix.conj().T @ seeded @ prefix)
    sample, raw_minimum = primary.coordinate_distribution(state, basis, dimension, volume)
    metrics = primary.conditioned_metrics(reference, sample, list(reversed(range(volume))), dimension, mu, float(fixture["probability_tolerance"]))
    omitted_local_shell = metrics["global_chi2"]
    mutation_gap = abs(omitted_local_shell - metrics["shell_energy"])
    wrong_parent_shell = 0.0
    parent = np.ones((dimension,), dtype=float)
    for radius in range(1, volume):
        sites = list(reversed(range(volume)))[: radius + 1]
        p = primary.marginal(reference, sites, dimension)
        q = primary.marginal(sample, sites, dimension)
        ratio = q / p
        wrong_parent_shell += float(np.sum(p * (ratio - 1.0) ** 2))
        parent = ratio
    parent_mutation_gap = abs(wrong_parent_shell - metrics["shell_energy"])
    checks = [
        {"name": "genuine identity", "status": "PASS" if metrics["identity_residual"] <= tolerance else "FAIL", "actual": metrics["identity_residual"], "expected": f"<={tolerance}"},
        {"name": "genuine shell positivity", "status": "PASS" if metrics["shell_energy"] >= -tolerance else "FAIL", "actual": metrics["shell_energy"], "expected": f">=-{tolerance}"},
        {"name": "omitted local term caught", "status": "PASS" if mutation_gap > threshold else "FAIL", "actual": mutation_gap, "expected": f">{threshold}"},
        {"name": "unconditioned parent caught", "status": "PASS" if parent_mutation_gap > threshold else "FAIL", "actual": parent_mutation_gap, "expected": f">{threshold}"},
        {"name": "coordinate probabilities finite", "status": "PASS" if np.isfinite(raw_minimum) else "FAIL", "actual": raw_minimum, "expected": "finite"},
    ]
    if any(item["status"] != "PASS" for item in checks):
        raise AssertionError(checks)
    derived = {
        "volume": volume,
        "dimension": dimension,
        "beta": beta,
        "prefix_length": prefix_length,
        "orientation": "left",
        "local_q2": metrics["local_q2"],
        "local_chi2": metrics["local_chi2"],
        "global_chi2": metrics["global_chi2"],
        "shell_energy": metrics["shell_energy"],
        "weighted_shell_energy": metrics["weighted_shell_energy"],
        "identity_residual": metrics["identity_residual"],
        "omitted_local_shell": omitted_local_shell,
        "mutation_gap": mutation_gap,
        "wrong_parent_shell": wrong_parent_shell,
        "parent_mutation_gap": parent_mutation_gap,
        "raw_coordinate_minimum": raw_minimum,
    }
    payload = {"schema": "tect/pre-a-r398-hostile/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-398", "exploration_id": "EXP-001242", "verdict": "PASS", "checks": checks, "derived": derived}
    atomic_json(output, payload)
    print(f"R-398 HOSTILE PASS {len(checks)}/{len(checks)} mutation_gap={mutation_gap:.6g} parent_gap={parent_mutation_gap:.6g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
