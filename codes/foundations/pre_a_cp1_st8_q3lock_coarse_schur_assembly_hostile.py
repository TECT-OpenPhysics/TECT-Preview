#!/usr/bin/env python3
"""Hostile mutation lane for the finite harmonic coarse-Schur assembly."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-coarse-schur-assembly-manifest.json"
SLUG = "coarse_schur_assembly"
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


def validate_inputs(pi: np.ndarray, conductance: np.ndarray, blocks: list[np.ndarray]) -> None:
    weights = np.asarray(pi, dtype=float)
    matrix = np.asarray(conductance, dtype=float)
    if weights.ndim != 1 or not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise AssertionError("weights must be positive and finite")
    if abs(float(np.sum(weights)) - 1.0) > 1.0e-10:
        raise AssertionError("weights must be normalized")
    if matrix.shape != (len(weights), len(weights)) or not np.all(np.isfinite(matrix)):
        raise AssertionError("conductance shape/nonfinite defect")
    if np.any(matrix < 0.0) or np.max(np.abs(matrix - matrix.T)) > 1.0e-12:
        raise AssertionError("conductance must be symmetric and nonnegative")
    seen: set[int] = set()
    for block in blocks:
        values = np.asarray(block, dtype=int)
        if values.size < 2 or np.any(values < 0) or np.any(values >= len(weights)):
            raise AssertionError("blocks must be nonempty and in range")
        if seen.intersection(int(value) for value in values):
            raise AssertionError("blocks must be disjoint")
        seen.update(int(value) for value in values)


def split_gaps(pi: np.ndarray, conductance: np.ndarray, blocks: list[np.ndarray]) -> tuple[float, float, float]:
    validate_inputs(pi, conductance, blocks)
    weights = np.asarray(pi, dtype=float)
    matrix = np.asarray(conductance, dtype=float)
    laplacian = np.diag(np.sum(matrix, axis=1)) - matrix
    inverse = 1.0 / np.sqrt(weights)
    operator = (inverse[:, None] * laplacian * inverse[None, :])
    operator = (operator + operator.T) / 2.0
    root = np.sqrt(weights)
    raw = np.zeros((len(weights), len(blocks)), dtype=float)
    for column, block in enumerate(blocks):
        values = np.asarray(block, dtype=int)
        mass = float(np.sum(weights[values]))
        raw[values, column] = root[values] / math.sqrt(mass)
    u, _ = np.linalg.qr(raw, mode="reduced")
    v, _ = np.linalg.qr(np.column_stack((raw, np.eye(len(weights)))), mode="complete")
    # QR above includes the span of raw first; extract an orthogonal complement robustly.
    q, _ = np.linalg.qr(raw, mode="complete")
    u, v = q[:, : len(blocks)], q[:, len(blocks) :]
    residual_operator = (v.T @ operator @ v + (v.T @ operator @ v).T) / 2.0
    residual_values = np.linalg.eigvalsh(residual_operator)
    if residual_values.size == 0 or float(residual_values[0]) <= 1.0e-10:
        raise AssertionError("residual block is singular or nonpositive")
    coarse = (u.T @ operator @ u + (u.T @ operator @ u).T) / 2.0
    coupling = u.T @ operator @ v
    schur = coarse - coupling @ np.linalg.solve(residual_operator, coupling.T)
    harmonic = u - v @ np.linalg.solve(residual_operator, coupling.T)
    mass = (harmonic.T @ harmonic + (harmonic.T @ harmonic).T) / 2.0
    values, vectors = np.linalg.eigh(mass)
    if float(np.min(values)) <= 1.0e-10:
        raise AssertionError("harmonic mass is singular")
    inv = vectors @ np.diag(1.0 / np.sqrt(values)) @ vectors.T
    coarse_values = np.linalg.eigvalsh((inv @ schur @ inv + (inv @ schur @ inv).T) / 2.0)
    if abs(float(coarse_values[0])) > 2.0e-7 or float(coarse_values[1]) <= 1.0e-10:
        raise AssertionError("coarse Schur is singular or nonpositive")
    coarse_gap = float(coarse_values[1])
    residual_gap = float(residual_values[0])
    return coarse_gap, residual_gap, 0.5 * min(coarse_gap, residual_gap)


def validate_report(coarse: float, residual: float, combined: float) -> None:
    if not all(math.isfinite(value) and value > 0.0 for value in (coarse, residual, combined)):
        raise AssertionError("invalid reported finite gaps")
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
    coarse, residual, combined = split_gaps(pi, conductance, blocks)
    validate_report(coarse, residual, combined)
    check("negative weight", lambda: validate_inputs(np.array([-0.4, 0.3, 0.2, 0.9]), conductance, blocks), "inputs")
    bad_asymmetry = conductance.copy()
    bad_asymmetry[0, 2] += 0.1
    check("nonsymmetric conductance", lambda: validate_inputs(pi, bad_asymmetry, blocks), "inputs")
    bad_negative = conductance.copy()
    bad_negative[0, 2] = bad_negative[2, 0] = -0.01
    check("negative conductance", lambda: validate_inputs(pi, bad_negative, blocks), "inputs")
    check("overlapping blocks", lambda: validate_inputs(pi, conductance, [np.array([0, 1]), np.array([1, 2])]), "support")
    check("undersized block", lambda: validate_inputs(pi, conductance, [np.array([0]), np.array([1, 2, 3])]), "support")
    check("forged combined envelope", lambda: validate_report(coarse, residual, 0.5 * min(coarse, residual) + 0.1), "envelope")
    disconnected = np.zeros_like(conductance)
    disconnected[0, 1] = disconnected[1, 0] = 0.1
    disconnected[2, 3] = disconnected[3, 2] = 0.1
    check("singular residual graph", lambda: split_gaps(pi, disconnected, blocks), "spectral")

    if not (manifest["result_id"] == "R-424" and manifest["exploration_id"] == "EXP-001269" and manifest["claim_bearing"] is False):
        raise AssertionError("manifest identity")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r424-hostile/1.0",
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
    print(f"R-424 HOSTILE PASS {assertions}/{assertions} invalid mutations rejected")
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
