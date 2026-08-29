#!/usr/bin/env python3
"""Hostile mutation lane for the R-425 finite Schur stress."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-expanded-grid-schur-stress-manifest.json"
SLUG = "expanded_grid_schur_stress"
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


def validate_inputs(weights: np.ndarray, conductance: np.ndarray, blocks: list[np.ndarray]) -> None:
    pi = np.asarray(weights, dtype=float)
    c = np.asarray(conductance, dtype=float)
    if pi.ndim != 1 or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0) or abs(float(np.sum(pi)) - 1.0) > 1.0e-10:
        raise AssertionError("weights must be positive, finite and normalized")
    if c.shape != (len(pi), len(pi)) or not np.all(np.isfinite(c)) or np.any(c < 0.0) or not np.allclose(c, c.T, atol=1.0e-12):
        raise AssertionError("conductance must be symmetric and nonnegative")
    seen: set[int] = set()
    for block in blocks:
        values = np.asarray(block, dtype=int)
        if values.size < 2 or np.any(values < 0) or np.any(values >= len(pi)) or seen.intersection(int(value) for value in values):
            raise AssertionError("blocks must be disjoint and have size >=2")
        seen.update(int(value) for value in values)


def finite_split(weights: np.ndarray, conductance: np.ndarray, blocks: list[np.ndarray]) -> tuple[float, float, float]:
    validate_inputs(weights, conductance, blocks)
    pi = np.asarray(weights, dtype=float)
    c = np.asarray(conductance, dtype=float)
    n = len(pi)
    raw = np.zeros((n, len(blocks)), dtype=float)
    for column, block in enumerate(blocks):
        values = np.asarray(block, dtype=int)
        raw[values, column] = np.sqrt(pi[values] / float(np.sum(pi[values])))
    u, _ = np.linalg.qr(raw, mode="reduced")
    q, _ = np.linalg.qr(raw, mode="complete")
    v = q[:, len(blocks):]
    laplacian = np.diag(np.sum(c, axis=1)) - c
    inverse = 1.0 / np.sqrt(pi)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = (operator + operator.T) / 2.0
    residual = (v.T @ operator @ v + (v.T @ operator @ v).T) / 2.0
    values = np.linalg.eigvalsh(residual)
    if values.size == 0 or float(values[0]) <= 1.0e-10:
        raise AssertionError("residual block is singular or nonpositive")
    coupling = u.T @ operator @ v
    coarse = (u.T @ operator @ u + (u.T @ operator @ u).T) / 2.0
    schur = coarse - coupling @ np.linalg.solve(residual, coupling.T)
    harmonic = u - v @ np.linalg.solve(residual, coupling.T)
    mass = (harmonic.T @ harmonic + (harmonic.T @ harmonic).T) / 2.0
    mass_values, mass_vectors = np.linalg.eigh(mass)
    if float(np.min(mass_values)) <= 1.0e-10:
        raise AssertionError("harmonic mass is singular")
    mass_inverse = mass_vectors @ np.diag(1.0 / np.sqrt(mass_values)) @ mass_vectors.T
    coarse_values = np.linalg.eigvalsh((mass_inverse @ schur @ mass_inverse + (mass_inverse @ schur @ mass_inverse).T) / 2.0)
    if abs(float(coarse_values[0])) > 2.0e-7 or float(coarse_values[1]) <= 1.0e-10:
        raise AssertionError("coarse Schur is singular or nonpositive")
    coarse_gap = float(coarse_values[1])
    residual_gap = float(values[0])
    return coarse_gap, residual_gap, 0.5 * min(coarse_gap, residual_gap)


def validate_report(coarse: float, residual: float, combined: float) -> None:
    if not all(math.isfinite(value) and value > 0.0 for value in (coarse, residual, combined)):
        raise AssertionError("invalid finite gaps")
    if combined > 0.5 * min(coarse, residual) + 1.0e-12:
        raise AssertionError("combined envelope forged upward")


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    assertions = 0

    def check(name: str, fn: Callable[[], None], group: str) -> None:
        nonlocal assertions
        assertions += 1
        try:
            fn()
        except (AssertionError, ValueError, np.linalg.LinAlgError):
            checks.append({"name": name, "group": group, "status": "PASS", "expected": "mutation rejected"})
            return
        raise AssertionError(f"hostile mutation accepted: {name}")

    pi = np.array([0.40, 0.30, 0.20, 0.10], dtype=float)
    conductance = 0.7 * np.outer(pi, pi)
    np.fill_diagonal(conductance, 0.0)
    blocks = [np.array([0, 1]), np.array([2, 3])]
    coarse, residual, combined = finite_split(pi, conductance, blocks)
    validate_report(coarse, residual, combined)
    check("negative weight", lambda: validate_inputs(np.array([-0.4, 0.3, 0.2, 0.9]), conductance, blocks), "inputs")
    bad_asymmetry = conductance.copy(); bad_asymmetry[0, 2] += 0.1
    check("nonsymmetric conductance", lambda: validate_inputs(pi, bad_asymmetry, blocks), "inputs")
    bad_negative = conductance.copy(); bad_negative[0, 2] = bad_negative[2, 0] = -0.01
    check("negative conductance", lambda: validate_inputs(pi, bad_negative, blocks), "inputs")
    check("overlapping blocks", lambda: validate_inputs(pi, conductance, [np.array([0, 1]), np.array([1, 2])]), "support")
    check("undersized block", lambda: validate_inputs(pi, conductance, [np.array([0]), np.array([1, 2, 3])]), "support")
    check("forged combined envelope", lambda: validate_report(coarse, residual, 0.5 * min(coarse, residual) + 0.1), "envelope")
    disconnected = np.zeros_like(conductance); disconnected[0, 1] = disconnected[1, 0] = 0.1; disconnected[2, 3] = disconnected[3, 2] = 0.1
    check("singular residual graph", lambda: finite_split(pi, disconnected, blocks), "spectral")
    if not (manifest["result_id"] == "R-425" and manifest["exploration_id"] == "EXP-001270" and manifest["claim_bearing"] is False):
        raise AssertionError("manifest identity")
    payload: dict[str, Any] = {"schema": "tect/pre-a-r425-hostile/1.0", "result_id": manifest["result_id"], "exploration_id": manifest["exploration_id"], "claim_id": manifest["claim_ids"][0], "manifest": MANIFEST.relative_to(REPO).as_posix(), "run_kind": "hostile", "verdict": "PASS", "assertion_count": assertions, "assertions": checks, "controls": {"all_mutations_rejected": True, "mutation_count": assertions, "numeric_evaluation": False, "physical_promotion": False}, "non_claims": manifest["non_claims"]}
    atomic_json(output, payload)
    print(f"R-425 HOSTILE PASS {assertions}/{assertions} invalid mutations rejected")
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
