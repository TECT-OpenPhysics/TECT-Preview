#!/usr/bin/env python3
"""Adversarial mutations for the R-400 static cutoff stress.

The mutation lane checks two tempting but invalid shortcuts: reusing a
low-cutoff gap as if it were cutoff independent, and replacing conditional
prefix laws by the unconditional one-site marginal.  Both are required to be
detectably different from the declared finite calculation.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-conditional-gap-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-30-hostile-pre_a_cp1_st8_q3lock_conditional_gap_cutoff_stress"
) / "hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_gap_cutoff_stress as primary  # noqa: E402
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402


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


def conditional_rows(reference: np.ndarray, dimension: int, orientation: str) -> tuple[list[np.ndarray], np.ndarray]:
    order = list(range(reference.ndim)) if orientation == "right" else list(reversed(range(reference.ndim)))
    rows: list[np.ndarray] = []
    for radius in range(1, len(order)):
        prefix = r399.marginal(reference, order[: radius + 1], dimension)
        parent = r399.marginal(reference, order[:radius], dimension)
        for parent_mass, row in zip(parent.reshape(-1), prefix.reshape(-1, dimension)):
            conditional = row / float(parent_mass)
            conditional /= float(np.sum(conditional))
            rows.append(conditional)
    return rows, r399.marginal(reference, [order[0]], dimension).reshape(-1)


def reference_for(volume: int, dimension: int, beta: float, fixture: dict[str, Any]) -> np.ndarray:
    _, hamiltonian, _ = r399.split_system(volume, dimension, fixture)
    basis = r399.coordinate_basis(dimension, volume)
    return r399.coordinate_distribution(r399.gibbs(hamiltonian, beta), basis, dimension, volume)[0]


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    dimensions = [int(dimension) for item in fixture["admissible_pairs"] if int(item["volume"]) == 2 for dimension in item["cutoff_dimensions"]]
    if not dimensions:
        raise AssertionError("hostile lane needs a volume-two cutoff ladder")
    beta = max(float(Fraction(value)) for value in fixture["beta_values"])
    target_dimension = max(dimensions)
    baseline_dimension = min(dimensions)
    target_reference = reference_for(2, target_dimension, beta, fixture)
    baseline_reference = reference_for(2, baseline_dimension, beta, fixture)
    rows, unconditional = conditional_rows(target_reference, target_dimension, "right")
    baseline_rows, _ = conditional_rows(baseline_reference, baseline_dimension, "right")
    if not rows or not baseline_rows:
        raise AssertionError("hostile lane has no conditional rows")
    genuine_gaps = [r399.birth_death_gap(row) for row in rows]
    baseline_gaps = [r399.birth_death_gap(row) for row in baseline_rows]
    actual_gap = min(genuine_gaps)
    fixed_gap = min(baseline_gaps)
    naive_deficit = fixed_gap - actual_gap
    unconditional_gap = r399.birth_death_gap(unconditional / float(np.sum(unconditional)))
    wrong_parent_mismatch = max(abs(unconditional_gap - gap_value) for gap_value in genuine_gaps)
    threshold = float(fixture["hostile_threshold"])
    checks = [
        {"name": "genuine finite gap", "status": "PASS" if actual_gap > 0.0 else "FAIL", "actual": actual_gap, "expected": ">0"},
        {"name": "fixed low-cutoff mutation detected", "status": "PASS" if naive_deficit > threshold else "FAIL", "actual": naive_deficit, "expected": f">{threshold}"},
        {"name": "unconditional-parent mutation detected", "status": "PASS" if wrong_parent_mismatch > threshold else "FAIL", "actual": wrong_parent_mismatch, "expected": f">{threshold}"},
    ]
    if not all(item["status"] == "PASS" for item in checks):
        raise AssertionError(checks)
    payload = {
        "schema": "tect/pre-a-r400-hostile/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-400",
        "exploration_id": "EXP-001245",
        "verdict": "PASS",
        "checks": checks,
        "assertion_count": len(checks),
        "derived": {
            "target_dimension": target_dimension,
            "baseline_dimension": baseline_dimension,
            "beta": beta,
            "genuine_minimum_gap": actual_gap,
            "fixed_low_cutoff_gap": fixed_gap,
            "naive_deficit": naive_deficit,
            "unconditional_gap": unconditional_gap,
            "wrong_parent_mismatch": wrong_parent_mismatch,
            "genuine_gap_count": len(genuine_gaps),
            "finite": all(math.isfinite(value) for value in genuine_gaps + baseline_gaps),
        },
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-400 HOSTILE PASS {len(checks)}/{len(checks)} naive_deficit={naive_deficit:.6g} wrong_parent={wrong_parent_mismatch:.6g}")
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
