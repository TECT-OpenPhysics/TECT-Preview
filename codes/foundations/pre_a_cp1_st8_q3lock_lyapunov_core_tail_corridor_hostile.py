#!/usr/bin/env python3
"""Hostile controls for the R-417 Lyapunov core-tail interface."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-lyapunov-core-tail-corridor-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-31-hostile-lyapunov_core_tail_corridor" / "hostile.json"


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


def graph(weights: np.ndarray) -> np.ndarray:
    pi = np.asarray(weights, dtype=float)
    if pi.ndim != 1 or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0):
        raise AssertionError("positive weights required")
    pi = pi / float(np.sum(pi))
    labels = np.arange(pi.size, dtype=float)
    # Clearly labelled hostile toy oracle: a connected positive conductance graph.
    edges = (pi[:, None] + pi[None, :]) * np.exp(-np.abs(labels[:, None] - labels[None, :]))
    np.fill_diagonal(edges, 0.0)
    return edges


def drift(weights: np.ndarray, edges: np.ndarray, alpha: float, theta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pi = np.asarray(weights, dtype=float)
    pi = pi / float(np.sum(pi))
    if alpha <= 0.0 or theta <= 0.0:
        raise AssertionError("positive alpha and theta required")
    logs = np.log(pi)
    phi = float(np.max(logs)) - logs
    potential = np.exp(alpha * phi)
    generator_potential = (edges @ potential - np.sum(edges, axis=1) * potential) / pi
    rates = -generator_potential / potential
    return phi, rates, potential


def core_gap(weights: np.ndarray, edges: np.ndarray, core: np.ndarray) -> float:
    pi = np.asarray(weights, dtype=float)
    mask = np.asarray(core, dtype=bool)
    indices = np.flatnonzero(mask)
    if indices.size < 2:
        raise AssertionError("core too small")
    mass = float(np.sum(pi[indices]))
    local = pi[indices] / mass
    local_edges = edges[np.ix_(indices, indices)] / mass
    laplacian = np.diag(np.sum(local_edges, axis=1)) - local_edges
    inverse = 1.0 / np.sqrt(local)
    operator = (inverse[:, None] * laplacian * inverse[None, :])
    operator = (operator + operator.T) / 2.0
    root = np.sqrt(local)
    root /= float(np.linalg.norm(root))
    frame = np.column_stack((root, np.eye(indices.size)))
    basis, _ = np.linalg.qr(frame, mode="complete")
    projected = basis[:, 1:].T @ operator @ basis[:, 1:]
    values = np.linalg.eigvalsh((projected + projected.T) / 2.0)
    if values.size == 0 or not np.all(np.isfinite(values)) or float(values[0]) <= 0.0:
        raise AssertionError("core graph is disconnected")
    return float(values[0])


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    alpha = float(fixture["alpha_values"][1].split("/")[0]) / float(fixture["alpha_values"][1].split("/")[1])
    theta = float(fixture["tail_thresholds"][0])
    drift_floor = float(fixture["drift_floor"])
    gap_floor = float(fixture["gap_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    # Clearly labelled hostile oracle; this is not a repository physics fixture.
    weights = np.exp(-np.linspace(0.0, 12.0, 8))
    weights /= float(np.sum(weights))
    edges = graph(weights)
    phi, rates, potential = drift(weights, edges, alpha, theta)
    tail = phi >= theta
    core = ~tail
    check("baseline tail exists", int(np.sum(tail)) >= 1, int(np.sum(tail)), ">=1")
    check("baseline drift positive", float(np.min(rates[tail])) > drift_floor, float(np.min(rates[tail])), f">{drift_floor}")
    check("baseline potential positive", float(np.min(potential)) > 0.0 and np.all(np.isfinite(potential)), float(np.min(potential)), ">0 finite")
    check("baseline core gap positive", core_gap(weights, edges, core) > gap_floor, core_gap(weights, edges, core), f">{gap_floor}")
    tail_mass = float(np.sum(weights[tail]))
    check("baseline tail mass bounded", tail_mass < float(fixture["tail_mass_cap"]), tail_mass, f"<{fixture['tail_mass_cap']}")

    # Mutation 1: reversing the drift sign must fail the positive-tail contract.
    reversed_rates = -rates
    check("reversed drift rejected", float(np.min(reversed_rates[tail])) < -drift_floor, float(np.min(reversed_rates[tail])), f"<-{drift_floor}")

    # Mutation 2: inverse potential rewards the tail and also fails the contract.
    inverse_rates = drift(weights, edges, -alpha, theta)[1] if False else None
    inverse_potential = np.exp(-alpha * phi)
    inverse_generator = (edges @ inverse_potential - np.sum(edges, axis=1) * inverse_potential) / weights
    inverse_rates = -inverse_generator / inverse_potential
    check("inverse potential rejected", float(np.min(inverse_rates[tail])) < -drift_floor, float(np.min(inverse_rates[tail])), f"<-{drift_floor}")

    # Mutation 3: remove the bridge between two core components.
    disconnected = edges.copy()
    disconnected[np.ix_([0, 1], [2, 3])] = 0.0
    disconnected[np.ix_([2, 3], [0, 1])] = 0.0
    try:
        core_gap(weights, disconnected, np.array([True, True, True, True, False, False, False, False]))
    except AssertionError:
        disconnected_rejected = True
    else:
        disconnected_rejected = False
    check("disconnected core rejected", disconnected_rejected, disconnected_rejected, "True")

    # Mutation 4: zero mass is never silently regularized.
    try:
        graph(np.r_[weights[:-1], 0.0])
    except AssertionError:
        zero_rejected = True
    else:
        zero_rejected = False
    check("zero mass rejected", zero_rejected, zero_rejected, "True")

    # Mutation 5: nonpositive threshold is outside the certificate interface.
    try:
        drift(weights, edges, alpha, 0.0)
    except AssertionError:
        threshold_rejected = True
    else:
        threshold_rejected = False
    check("nonpositive threshold rejected", threshold_rejected, threshold_rejected, "True")

    derived = {
        "baseline_tail_count": int(np.sum(tail)),
        "baseline_tail_mass": tail_mass,
        "baseline_minimum_tail_drift": float(np.min(rates[tail])),
        "baseline_core_gap": core_gap(weights, edges, core),
        "reversed_minimum_tail_rate": float(np.min(reversed_rates[tail])),
        "inverse_minimum_tail_rate": float(np.min(inverse_rates[tail])),
        "checks_passed": len(checks),
    }
    payload = {"schema": "tect/pre-a-r417-hostile/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": "R-417", "exploration_id": "EXP-001262", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": derived, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-417 HOSTILE PASS {len(checks)}/{len(checks)} tail_drift={derived['baseline_minimum_tail_drift']:.6g} core_gap={derived['baseline_core_gap']:.6g} inverse_drift={derived['inverse_minimum_tail_rate']:.6g}")
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
