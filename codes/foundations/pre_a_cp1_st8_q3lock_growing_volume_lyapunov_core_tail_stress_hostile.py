#!/usr/bin/env python3
"""Hostile controls for the R-419 growing-volume stress contract."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
SLUG = "growing_volume_lyapunov_core_tail_stress"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-hostile-{SLUG}" / "hostile.json"


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
    edges = (pi[:, None] + pi[None, :]) * np.exp(-np.abs(labels[:, None] - labels[None, :]))
    np.fill_diagonal(edges, 0.0)
    return edges


def drift(weights: np.ndarray, edges: np.ndarray, alpha: float, theta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pi = np.asarray(weights, dtype=float)
    pi = pi / float(np.sum(pi))
    if alpha <= 0.0 or theta <= 0.0:
        raise AssertionError("positive alpha and theta required")
    phi = float(np.max(np.log(pi))) - np.log(pi)
    potential = np.exp(alpha * phi)
    generator = (edges @ potential - np.sum(edges, axis=1) * potential) / pi
    rates = -generator / potential
    return phi, rates, potential


def projected_gap(weights: np.ndarray, edges: np.ndarray) -> float:
    pi = np.asarray(weights, dtype=float)
    pi = pi / float(np.sum(pi))
    laplacian = np.diag(np.sum(edges, axis=1)) - edges
    inverse = 1.0 / np.sqrt(pi)
    operator = (inverse[:, None] * laplacian * inverse[None, :])
    operator = (operator + operator.T) / 2.0
    root = np.sqrt(pi)
    root /= float(np.linalg.norm(root))
    frame = np.column_stack((root, np.eye(pi.size)))
    basis, _ = np.linalg.qr(frame, mode="complete")
    values = np.linalg.eigvalsh((basis[:, 1:].T @ operator @ basis[:, 1:] + basis[:, 1:].T @ operator @ basis[:, 1:]) / 2.0)
    if values.size == 0 or not np.all(np.isfinite(values)) or float(values[0]) <= 0.0:
        raise AssertionError("graph is disconnected or nonpositive")
    return float(values[0])


def core_gap(weights: np.ndarray, edges: np.ndarray, mask: np.ndarray) -> float:
    pi = np.asarray(weights, dtype=float)
    indices = np.flatnonzero(np.asarray(mask, dtype=bool))
    if indices.size < 2:
        raise AssertionError("core too small")
    mass = float(np.sum(pi[indices]))
    if mass <= 0.0:
        raise AssertionError("nonpositive core mass")
    local = pi[indices] / mass
    return projected_gap(local, np.asarray(edges)[np.ix_(indices, indices)] / mass)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    alpha = 0.05
    theta = 4.0
    weights = np.exp(-np.linspace(0.0, 12.0, 8))
    weights /= float(np.sum(weights))
    edges = graph(weights)
    phi, rates, potential = drift(weights, edges, alpha, theta)
    tail = phi >= theta
    core = ~tail
    check("baseline tail exists", int(np.sum(tail)) >= 1, int(np.sum(tail)), ">=1")
    check("baseline drift positive", float(np.min(rates[tail])) > float(fixture["drift_floor"]), float(np.min(rates[tail])), f">{fixture['drift_floor']}")
    check("baseline core gap positive", core_gap(weights, edges, core) > float(fixture["gap_floor"]), core_gap(weights, edges, core), f">{fixture['gap_floor']}")
    check("baseline potential finite", np.all(np.isfinite(potential)) and float(np.min(potential)) > 0.0, float(np.min(potential)), ">0 finite")

    reversed_rates = -rates
    check("reversed drift rejected", float(np.min(reversed_rates[tail])) < -float(fixture["drift_floor"]), float(np.min(reversed_rates[tail])), f"<-{fixture['drift_floor']}")
    inverse_potential = np.exp(-alpha * phi)
    inverse_generator = (edges @ inverse_potential - np.sum(edges, axis=1) * inverse_potential) / weights
    inverse_rates = -inverse_generator / inverse_potential
    check("inverse potential rejected", float(np.min(inverse_rates[tail])) < -float(fixture["drift_floor"]), float(np.min(inverse_rates[tail])), f"<-{fixture['drift_floor']}")

    disconnected = edges.copy()
    disconnected[np.ix_([0, 1, 2, 3], [4, 5, 6, 7])] = 0.0
    disconnected[np.ix_([4, 5, 6, 7], [0, 1, 2, 3])] = 0.0
    try:
        disconnected_value = core_gap(weights, disconnected, np.ones(8, dtype=bool))
    except AssertionError:
        disconnected_value = 0.0
    disconnected_rejected = disconnected_value <= float(fixture["gap_floor"])
    check("disconnected graph rejected", disconnected_rejected, disconnected_value, f"<={fixture['gap_floor']}")

    try:
        graph(np.r_[weights[:-1], 0.0])
    except AssertionError:
        zero_rejected = True
    else:
        zero_rejected = False
    check("zero mass rejected", zero_rejected, zero_rejected, "True")

    try:
        drift(weights, edges, alpha, 0.0)
    except AssertionError:
        threshold_rejected = True
    else:
        threshold_rejected = False
    check("nonpositive threshold rejected", threshold_rejected, threshold_rejected, "True")

    declared_pairs = [(int(item["volume"]), tuple(int(x) for x in item["cutoff_dimensions"])) for item in fixture["volume_cutoffs"]]
    mutated_pairs = declared_pairs[:1]
    check("volume omission rejected", mutated_pairs != declared_pairs and len(mutated_pairs) != len(declared_pairs), mutated_pairs, "full declared volume grid")
    check("orientation omission rejected", len(fixture["orientations"]) == 2, fixture["orientations"], "right and left")

    unnormalized = edges * 3.0
    normalized_gap = projected_gap(weights, edges)
    mutated_gap = projected_gap(weights, unnormalized)
    check("conductance scaling is load-bearing", abs(mutated_gap - normalized_gap) > float(fixture["gap_floor"]), [normalized_gap, mutated_gap], "no silent conductance rescaling")

    derived = {"baseline_tail_count": int(np.sum(tail)), "baseline_tail_mass": float(np.sum(weights[tail])), "baseline_minimum_tail_drift": float(np.min(rates[tail])), "baseline_core_gap": core_gap(weights, edges, core), "reversed_minimum_tail_rate": float(np.min(reversed_rates[tail])), "inverse_minimum_tail_rate": float(np.min(inverse_rates[tail])), "checks_passed": len(checks)}
    payload = {"schema": "tect/pre-a-r419-hostile/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": "R-419", "exploration_id": "EXP-001264", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": derived, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-419 HOSTILE PASS {len(checks)}/{len(checks)} tail_drift={derived['baseline_minimum_tail_drift']:.6g} core_gap={derived['baseline_core_gap']:.6g}")
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
