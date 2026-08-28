#!/usr/bin/env python3
"""Hostile mutation lane for the R-385 cocycle orientation.

The lane intentionally reverses the relative product.  It passes only when
that mutation is detected by a nonzero intertwining residual, preventing a
commuting surrogate from masquerading as the declared ordered cocycle.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "strategy/pre-a-cp1-st8-q3lock-relative-modular-cocycle-resolvent-cook-finite-checkpoint-manifest.json"
DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_relative_modular_cocycle_resolvent_cook_finite_checkpoint" / "hostile.json"


def save(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def h(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((size, size), dtype=complex)
    for index in range(size - 1): a[index, index + 1] = np.sqrt(index + 1.0)
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def lift(local: np.ndarray, site: int, identity: np.ndarray) -> np.ndarray:
    return np.kron(local if site == 0 else identity, identity if site == 0 else local)


def evolution(generator: np.ndarray, time: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(h(generator))
    return (vectors * np.exp(-1j * time * values)) @ vectors.conj().T


def alpha(generator: np.ndarray, operator: np.ndarray, time: float) -> np.ndarray:
    return evolution(generator, -time) @ operator @ evolution(generator, time)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(CONFIG.read_text(encoding="utf-8"))
    f = manifest["finite_fixture"]
    n = int(f["oscillator_dimension"]); q0, p0 = oscillator(n); identity = np.eye(n, dtype=complex)
    selected_edge = tuple(int(site) for site in f["graph_edges_by_volume"]["2"][0])
    if selected_edge != (0, 1): raise AssertionError(selected_edge)
    q_ops = [np.kron(q0, identity), np.kron(identity, q0)]
    p_ops = [np.kron(p0, identity), np.kron(identity, p0)]
    q_left, q_right = q_ops[selected_edge[0]], q_ops[selected_edge[1]]
    p_left, p_right = p_ops[selected_edge[0]], p_ops[selected_edge[1]]
    chi, r, g, c, lam = (float(f[key]) for key in ("chi", "r", "g", "c", "lambda"))
    onsite_left = p_left @ p_left / (2.0 * chi) + r * q_left @ q_left / 2.0 + g * q_left @ q_left @ q_left @ q_left / 4.0
    onsite_right = p_right @ p_right / (2.0 * chi) + r * q_right @ q_right / 2.0 + g * q_right @ q_right @ q_right @ q_right / 4.0
    difference = q_left - q_right; square = difference @ difference
    bond = c * square / 2.0 + lam * square @ (q_left @ q_left + q_right @ q_right) / 4.0
    base = h(onsite_left + onsite_right); extension = h(base + h(bond)); time = float(Fraction(f["time_magnitudes"][1])); eta = float(Fraction(f["resolvent_imaginary_values"][0]))
    seed = np.linalg.inv(1j * eta * np.eye(base.shape[0], dtype=complex) - q_left)
    correct = evolution(extension, -time) @ evolution(base, time)
    wrong = evolution(base, -time) @ evolution(extension, time)
    correct_residual = norm(alpha(extension, seed, time) - correct @ alpha(base, seed, time) @ correct.conj().T)
    wrong_residual = norm(alpha(extension, seed, time) - wrong @ alpha(base, seed, time) @ wrong.conj().T)
    threshold = float(f["alpha_tolerance"]) * 100.0
    if not correct_residual <= float(f["alpha_tolerance"]): raise AssertionError(correct_residual)
    if not wrong_residual > threshold: raise AssertionError({"wrong_residual": wrong_residual, "threshold": threshold})
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "hostile", "audit_id": "PA-CP1-ST8-Q3LOCK-RELATIVE-MODULAR-COCYCLE-RESOLVENT-COOK-FINITE-CHECKPOINT-HOSTILE", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertions": [{"name": "declared orientation", "status": "PASS", "actual": correct_residual, "expected": f"<={f['alpha_tolerance']}"}, {"name": "reversed orientation caught", "status": "PASS", "actual": wrong_residual, "expected": f">{threshold}"}], "derived": {"correct_residual": correct_residual, "wrong_orientation_residual": wrong_residual, "mutation_threshold": threshold, "wrong_orientation_rejected": True, "finite_only": True}, "boundary": "Hostile finite mutation check only; no Q3 limit or common dynamics conclusion."}
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: save(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"HOSTILE RELATIVE-MODULAR-COCYCLE MUTATION CAUGHT wrong={payload['derived']['wrong_orientation_residual']:.3e}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
