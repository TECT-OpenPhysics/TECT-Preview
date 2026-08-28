#!/usr/bin/env python3
"""Adversarial lane for the R-401 physical-coordinate metric.

The mutation deliberately drops the coordinate-spacing factor and reuses the
level-index gap.  The selected high-cutoff context must show that this is not
an innocuous reparametrization.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-coordinate-metric-gap-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-pre_a_cp1_st8_q3lock_coordinate_metric_gap/hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_coordinate_metric_gap as primary  # noqa: E402
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


def conditional_rows(reference: np.ndarray, dimension: int, orientation: str) -> list[np.ndarray]:
    order = list(range(reference.ndim)) if orientation == "right" else list(reversed(range(reference.ndim)))
    rows: list[np.ndarray] = []
    for radius in range(1, len(order)):
        prefix = r399.marginal(reference, order[: radius + 1], dimension)
        parent = r399.marginal(reference, order[:radius], dimension)
        for parent_mass, row in zip(parent.reshape(-1), prefix.reshape(-1, dimension)):
            conditional = row / float(parent_mass)
            conditional /= float(np.sum(conditional))
            rows.append(conditional)
    return rows


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    dimensions = [int(dimension) for item in fixture["admissible_pairs"] if int(item["volume"]) == 2 for dimension in item["cutoff_dimensions"]]
    target_dimension = max(dimensions)
    target_beta = max(float(Fraction(value)) for value in fixture["beta_values"])
    _, hamiltonian, _ = r399.split_system(2, target_dimension, fixture)
    basis = r399.coordinate_basis(target_dimension, 2)
    reference, raw_minimum = r399.coordinate_distribution(r399.gibbs(hamiltonian, target_beta), basis, target_dimension, 2)
    if raw_minimum < -float(fixture["numerical_tolerance"]):
        raise AssertionError("coordinate probability roundoff")
    levels = primary.coordinate_levels(target_dimension)
    spacings = np.diff(levels)
    rows = conditional_rows(reference, target_dimension, "right")
    if not rows:
        raise AssertionError("no target conditional rows")
    index_gaps = [r399.birth_death_gap(row) for row in rows]
    coordinate_gaps = [primary.metric_gap(row, spacings, Fraction(str(fixture["edge_spacing_power"]))) for row in rows]
    index_gap = min(index_gaps)
    coordinate_gap = min(coordinate_gaps)
    metric_gain = coordinate_gap / index_gap
    threshold = float(fixture["hostile_ratio_threshold"])
    checks = [
        {"name": "index gap finite", "status": "PASS" if math.isfinite(index_gap) and index_gap > 0.0 else "FAIL", "actual": index_gap, "expected": ">0"},
        {"name": "coordinate gap finite", "status": "PASS" if math.isfinite(coordinate_gap) and coordinate_gap > 0.0 else "FAIL", "actual": coordinate_gap, "expected": ">0"},
        {"name": "index-metric mutation detected", "status": "PASS" if metric_gain > threshold else "FAIL", "actual": metric_gain, "expected": f">{threshold}"},
    ]
    if not all(item["status"] == "PASS" for item in checks):
        raise AssertionError(checks)
    payload = {
        "schema": "tect/pre-a-r401-hostile/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-401",
        "exploration_id": "EXP-001246",
        "verdict": "PASS",
        "checks": checks,
        "assertion_count": len(checks),
        "derived": {
            "volume": 2,
            "target_dimension": target_dimension,
            "beta": target_beta,
            "index_gap": index_gap,
            "coordinate_gap": coordinate_gap,
            "metric_gain": metric_gain,
            "minimum_spacing": float(np.min(spacings)),
            "row_count": len(rows),
            "mutation": "drop_coordinate_spacing_factor",
        },
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-401 HOSTILE PASS {len(checks)}/{len(checks)} index_gap={index_gap:.6g} coordinate_gap={coordinate_gap:.6g} gain={metric_gain:.6g}")
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
