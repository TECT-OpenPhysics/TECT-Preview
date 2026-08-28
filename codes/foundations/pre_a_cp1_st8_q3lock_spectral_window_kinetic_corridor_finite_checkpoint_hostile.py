#!/usr/bin/env python3
"""Hostile control for R-389: replace q-resolvent by p-resolvent."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spectral-window-kinetic-corridor-finite-checkpoint-manifest.json"
SLUG = "pre_a_cp1_st8_q3lock_spectral_window_kinetic_corridor_finite_checkpoint"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "hostile.json"


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


def sym(a: np.ndarray) -> np.ndarray:
    return (a + a.conj().T) / 2.0


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((n, n), dtype=complex)
    for j in range(1, n):
        lower[j - 1, j] = np.sqrt(float(j))
    upper = lower.conj().T
    return (lower + upper) / np.sqrt(2.0), (lower - upper) / (1j * np.sqrt(2.0))


def lift(a: np.ndarray, site: int, n: int) -> np.ndarray:
    eye = np.eye(n, dtype=complex)
    return np.kron(a, eye) if site == 0 else np.kron(eye, a)


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def build(n: int, f: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q, p = oscillator(n)
    q0, q1, p0, p1 = lift(q, 0, n), lift(q, 1, n), lift(p, 0, n), lift(p, 1, n)
    delta = q0 - q1
    delta2 = delta @ delta
    boundary = sym(float(f["c"]) * delta2 / 2.0 + float(f["lambda"]) * delta2 @ (q0 @ q0 + q1 @ q1) / 4.0)
    return q0, q1, p0, p1, boundary


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    f, coverage = manifest["finite_fixture"], manifest["coverage"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001232" and manifest["result_id"] == "R-389" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"]], "EXP-001232/R-389/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all coverage flags", "coverage")
    dimensions = [int(x) for x in f["cutoff_dimensions"]]
    sites = [int(x) for x in f["site_values"]]
    etas = [float(Fraction(x)) for x in f["resolvent_imaginary_values"]]
    threshold = float(f["hostile_threshold"])
    coordinate_residuals: list[float] = []
    momentum_residuals: list[float] = []
    samples = 0
    for n in dimensions:
        q0, q1, p0, p1, B = build(n, f)
        I = np.eye(n * n, dtype=complex)
        for site, (q, p) in enumerate(((q0, p0), (q1, p1))):
            for eta in etas:
                coordinate_seed = np.linalg.solve(1j * eta * I - q, I)
                momentum_seed = np.linalg.solve(1j * eta * I - p, I)
                for adjoint, (coordinate, momentum) in enumerate(((coordinate_seed, momentum_seed), (coordinate_seed.conj().T, momentum_seed.conj().T))):
                    good = float(np.linalg.svd(comm(B, coordinate), compute_uv=False)[0])
                    wrong = float(np.linalg.svd(comm(B, momentum), compute_uv=False)[0])
                    coordinate_residuals.append(good)
                    momentum_residuals.append(wrong)
                    samples += 1
                    check(f"d={n} site={site} eta={eta} adj={adjoint} finite", np.isfinite(good) and np.isfinite(wrong), [good, wrong], "finite", "hostile")
    check("coordinate anchor", max(coordinate_residuals) <= threshold, max(coordinate_residuals), f"<={threshold}", "hostile")
    check("momentum mutation separated", min(momentum_residuals) > threshold, min(momentum_residuals), f">{threshold}", "hostile")
    expected = len(dimensions) * len(sites) * len(etas) * 2
    check("sample count", samples == expected, samples, expected, "coverage")
    derived = {"mutation": "coordinate resolvent -> momentum resolvent", "samples": samples, "correct_coordinate_commutator_max": max(coordinate_residuals), "wrong_momentum_commutator_min": min(momentum_residuals), "wrong_momentum_commutator_max": max(momentum_residuals), "hostile_threshold": threshold, "wrong_orientation_rejected": min(momentum_residuals) > threshold}
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "hostile", "audit_id": "PA-CP1-ST8-Q3LOCK-SPECTRAL-WINDOW-KINETIC-CORRIDOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOSTILE SPECTRAL-WINDOW KINETIC CORRIDOR CAUGHT wrong_min={payload['derived']['wrong_momentum_commutator_min']:.6e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
