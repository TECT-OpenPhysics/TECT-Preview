#!/usr/bin/env python3
"""Hostile control for R-388: use a momentum resolvent instead of a coordinate one."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-state-weighted-kinetic-resolvent-corridor-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_state_weighted_kinetic_resolvent_corridor_finite_checkpoint/hostile.json"


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def hermitian(x: np.ndarray) -> np.ndarray:
    return (x + x.conj().T) / 2.0


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((dimension, dimension), dtype=complex)
    for n in range(dimension - 1):
        a[n, n + 1] = np.sqrt(n + 1.0)
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, dimension: int) -> np.ndarray:
    identity = np.eye(dimension, dtype=complex)
    return np.kron(single, identity) if site == 0 else np.kron(identity, single)


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(x: np.ndarray) -> float:
    return float(np.linalg.svd(x, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    dimensions = [int(x) for x in fixture["cutoff_dimensions"]]
    eta_values = [float(Fraction(x)) for x in fixture["resolvent_imaginary_values"]]
    threshold = float(fixture["hostile_threshold"])
    wrong: list[float] = []
    coordinate_values: list[float] = []
    rows = 0
    for dimension in dimensions:
        q_single, p_single = oscillator(dimension)
        q0, q1 = lift(q_single, 0, dimension), lift(q_single, 1, dimension)
        p0, p1 = lift(p_single, 0, dimension), lift(p_single, 1, dimension)
        delta = q0 - q1
        boundary = hermitian(float(fixture["c"]) * delta @ delta / 2.0 + float(fixture["lambda"]) * (delta @ delta) @ (q0 @ q0 + q1 @ q1) / 4.0)
        identity = np.eye(dimension * dimension, dtype=complex)
        for momentum in (p0, p1):
            for eta in eta_values:
                resolvent = np.linalg.inv(1j * eta * identity - momentum)
                for observable in (resolvent, resolvent.conj().T):
                    value = operator_norm(commutator(boundary, observable))
                    wrong.append(value)
                    rows += 1
        for q_operator in (q0, q1):
            for eta in eta_values:
                resolvent = np.linalg.inv(1j * eta * identity - q_operator)
                for observable in (resolvent, resolvent.conj().T):
                    coordinate_values.append(operator_norm(commutator(boundary, observable)))
    if min(wrong) <= threshold:
        raise AssertionError(f"momentum seed was not separated: {min(wrong)}")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "hostile", "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-KINETIC-RESOLVENT-CORRIDOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": rows + 2, "assertions": [{"name": "momentum resolvent separated", "status": "PASS"}, {"name": "threshold", "status": "PASS"}], "derived": {"samples": rows, "correct_coordinate_commutator_max": max(coordinate_values), "wrong_momentum_commutator_min": min(wrong), "wrong_momentum_commutator_max": max(wrong), "hostile_threshold": threshold, "wrong_orientation_rejected": True, "mutation": "coordinate resolvent -> momentum resolvent"}, "boundary": manifest["boundary"]}
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOSTILE STATE-WEIGHTED KINETIC-RESOLVENT CORRIDOR CAUGHT wrong={payload['derived']['wrong_momentum_commutator_min']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
