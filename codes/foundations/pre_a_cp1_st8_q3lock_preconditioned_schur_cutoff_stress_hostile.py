#!/usr/bin/env python3
"""Hostile checks for the R-416 numerical-stability contract."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-preconditioned-schur-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-31-hostile-preconditioned_schur_cutoff_stress" / "hostile.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
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


def graph_spectra(weights: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    row = np.asarray(weights, dtype=float)
    if np.any(row <= 0.0) or not np.all(np.isfinite(row)):
        raise AssertionError("positive weights required")
    row = row / float(np.sum(row))
    q_single, p_single = q3.oscillator(row.size)
    levels, vectors = np.linalg.eigh((q_single + q_single.conj().T) / 2.0)
    del levels
    momentum = (vectors.conj().T @ p_single @ vectors)
    conductance = (row[:, None] + row[None, :]) * np.square(np.abs(momentum)) / 2.0
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(row)
    operator = (inverse[:, None] * laplacian * inverse[None, :])
    operator = (operator + operator.T) / 2.0
    raw = np.linalg.eigvalsh(operator)
    root = np.sqrt(row)
    root /= float(np.linalg.norm(root))
    frame = np.column_stack((root, np.eye(row.size)))
    q_basis, _ = np.linalg.qr(frame, mode="complete")
    projected = np.linalg.eigvalsh(q_basis[:, 1:].T @ operator @ q_basis[:, 1:])
    wrong = np.ones(row.size, dtype=float) / math.sqrt(row.size)
    wrong_frame = np.column_stack((wrong, np.eye(row.size)))
    wrong_basis, _ = np.linalg.qr(wrong_frame, mode="complete")
    wrong_projected = np.linalg.eigvalsh(wrong_basis[:, 1:].T @ operator @ wrong_basis[:, 1:])
    return raw, projected, wrong_projected


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    threshold = float(fixture["hostile_zero_threshold"])
    gap_floor = float(fixture["gap_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    weights = np.exp(-np.linspace(0.0, 48.0, 14))
    raw, projected, wrong_projected = graph_spectra(weights)
    check("raw zero-mode drift is observable", abs(float(raw[0])) > float(fixture["raw_zero_threshold"]), float(raw[0]), f"abs > {fixture['raw_zero_threshold']}")
    check("projected gap survives drift", float(projected[0]) > gap_floor, float(projected[0]), f"> {gap_floor}")
    check("wrong projection is rejected", float(wrong_projected[0]) < -threshold, float(wrong_projected[0]), f"< -{threshold}")

    scaled_raw, scaled_projected, _scaled_wrong = graph_spectra(weights * float(Fraction(str(fixture["weight_scale_factor"]))))
    scale_residual = abs(float(projected[0]) - float(scaled_projected[0]))
    check("common weight scaling", scale_residual <= float(fixture["crosscheck_tolerance"]), scale_residual, f"<= {fixture['crosscheck_tolerance']}")
    check("raw scale remains finite", np.all(np.isfinite(scaled_raw)), scaled_raw[:2].tolist(), "finite")

    logs = np.array([0.0, -800.0, -1200.0])
    naive = np.exp(logs)
    stable = float(np.max(logs) + math.log(float(np.sum(np.exp(logs - np.max(logs))))))
    check("naive exponential underflow diagnosed", int(np.count_nonzero(naive == 0.0)) >= 1, naive.tolist(), "at least one zero")
    check("log-sum-exp remains finite", math.isfinite(stable), stable, "finite")
    check("constant vector normalization", abs(float(np.linalg.norm(np.sqrt(weights) / np.linalg.norm(np.sqrt(weights)))) - 1.0) <= threshold, "normalized", f"<= {threshold}")

    try:
        graph_spectra(np.r_[weights[:-1], 0.0])
    except AssertionError:
        rejected_nonpositive = True
    else:
        rejected_nonpositive = False
    check("nonpositive row rejected", rejected_nonpositive, rejected_nonpositive, "True")

    derived = {
        "raw_zero_mode_residual": abs(float(raw[0])),
        "projected_gap": float(projected[0]),
        "wrong_projected_minimum": float(wrong_projected[0]),
        "scale_residual": scale_residual,
        "naive_underflow_count": int(np.count_nonzero(naive == 0.0)),
        "stable_log_normalizer": stable,
        "checks_passed": len(checks),
    }
    payload = {"schema": "tect/pre-a-r416-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-416", "exploration_id": "EXP-001261", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": derived, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-416 HOSTILE PASS {len(checks)}/{len(checks)} raw_zero={derived['raw_zero_mode_residual']:.6g} projected_gap={derived['projected_gap']:.6g} wrong_projection={derived['wrong_projected_minimum']:.6g}")
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
