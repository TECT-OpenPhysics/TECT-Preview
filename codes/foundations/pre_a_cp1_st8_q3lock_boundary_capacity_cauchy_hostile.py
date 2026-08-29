#!/usr/bin/env python3
"""Hostile mutation lane for the R-423 capacity envelope."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-boundary-capacity-cauchy-manifest.json"
SLUG = "boundary_capacity_cauchy"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-hostile-{SLUG}" / "hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate(pi: np.ndarray, conductance: np.ndarray, core: np.ndarray, tail: np.ndarray) -> float:
    weights = np.asarray(pi, dtype=float)
    matrix = np.asarray(conductance, dtype=float)
    core = np.asarray(core, dtype=int)
    tail = np.asarray(tail, dtype=int)
    if weights.ndim != 1 or not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise AssertionError("invalid weights")
    if matrix.shape != (len(weights), len(weights)) or not np.all(np.isfinite(matrix)) or np.any(matrix < 0.0):
        raise AssertionError("invalid conductance")
    if np.max(np.abs(matrix - matrix.T)) > 1.0e-12:
        raise AssertionError("conductance not symmetric")
    if np.any(core < 0) or np.any(tail < 0) or np.any(core >= len(weights)) or np.any(tail >= len(weights)):
        raise AssertionError("support index out of range")
    if np.intersect1d(core, tail).size == 0 and (core.size == 0 or tail.size == 0):
        raise AssertionError("empty boundary support")
    if np.intersect1d(core, tail).size:
        raise AssertionError("overlapping support")
    block = matrix[np.ix_(core, tail)]
    rho_core = float(np.max(np.sum(block, axis=1) / weights[core]))
    rho_tail = float(np.max(np.sum(block, axis=0) / weights[tail]))
    return math.sqrt(rho_core * rho_tail)


def validate_cross(cross_norm: float, capacity: float) -> None:
    if not math.isfinite(cross_norm) or cross_norm < 0.0 or not math.isfinite(capacity) or capacity < 0.0:
        raise AssertionError("invalid cross/capacity")
    if cross_norm > capacity + 1.0e-12:
        raise AssertionError("cross norm exceeds capacity")


def validate_reserve(a: float, kappa: float, capacity_value: float, claimed: float) -> None:
    if not all(math.isfinite(value) and value >= 0.0 for value in (a, kappa, capacity_value, claimed)):
        raise AssertionError("invalid reserve inputs")
    if claimed > min(a, kappa) - capacity_value + 1.0e-12:
        raise AssertionError("forged reserve")


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    assertions = 0

    def check(name: str, fn: Callable[[], None], group: str) -> None:
        nonlocal assertions
        assertions += 1
        try:
            fn()
        except AssertionError:
            checks.append({"name": name, "group": group, "status": "PASS", "expected": "mutation rejected"})
            return
        raise AssertionError(f"hostile mutation accepted: {name}")

    pi = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    conductance = 0.05 * np.outer(pi, pi)
    np.fill_diagonal(conductance, 0.0)
    core = np.array([0, 1])
    tail = np.array([2, 3])
    cap = validate(pi, conductance, core, tail)
    check("negative weight", lambda: validate(np.array([-0.4, 0.3, 0.2, 0.1]), conductance, core, tail), "inputs")
    bad_c = conductance.copy()
    bad_c[0, 2] = bad_c[2, 0] = -0.01
    check("negative conductance", lambda: validate(pi, bad_c, core, tail), "inputs")
    check("overlapping support", lambda: validate(pi, conductance, np.array([0, 1]), np.array([1, 2])), "support")
    check("nonfinite capacity", lambda: validate(pi, conductance, core, np.array([2, 99])), "support")
    check("cross above capacity", lambda: validate_cross(cap + 0.1, cap), "cross envelope")
    check("negative cross norm", lambda: validate_cross(-0.1, cap), "cross envelope")
    check("forged upward reserve", lambda: validate_reserve(0.8, 0.6, cap, min(0.8, 0.6) - cap + 0.1), "reserve")

    if not (manifest["result_id"] == "R-423" and manifest["exploration_id"] == "EXP-001268" and manifest["claim_bearing"] is False):
        raise AssertionError("manifest identity")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r423-hostile/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "hostile",
        "verdict": "PASS",
        "assertion_count": assertions,
        "assertions": checks,
        "controls": {"all_mutations_rejected": True, "mutation_count": assertions, "numeric_evaluation": False, "physical_promotion": False},
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(f"R-423 HOSTILE PASS {assertions}/{assertions} invalid mutations rejected")
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
