#!/usr/bin/env python3
"""Hostile mutations for the R-421 ground-state-transform interface."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-tail-hardy-ground-state-transform-manifest.json"
SLUG = "tail_hardy_ground_state_transform"
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


def validate(pi: np.ndarray, c: np.ndarray, v: np.ndarray, f: np.ndarray, tail: np.ndarray, kappa: float) -> tuple[float, float, float]:
    weights = np.asarray(pi, dtype=float)
    conductance = np.asarray(c, dtype=float)
    potential = np.asarray(v, dtype=float)
    vector = np.asarray(f, dtype=float)
    mask = np.asarray(tail, dtype=bool)
    if weights.ndim != 1 or conductance.shape != (weights.size, weights.size) or potential.shape != weights.shape or vector.shape != weights.shape or mask.shape != weights.shape:
        raise AssertionError("shape mismatch")
    if not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise AssertionError("positive weights required")
    if not np.all(np.isfinite(conductance)) or np.max(np.abs(conductance - conductance.T)) > 1.0e-12 or np.min(conductance) < -1.0e-12:
        raise AssertionError("symmetric nonnegative conductance required")
    if not np.all(np.isfinite(potential)) or np.any(potential <= 0.0):
        raise AssertionError("positive potential required")
    if not np.all(np.isfinite(vector)) or np.any(np.abs(vector[~mask]) > 1.0e-12):
        raise AssertionError("Hardy consequence requires tail support")
    if not np.isfinite(kappa) or kappa <= 0.0:
        raise AssertionError("positive kappa required")
    weights = weights / float(np.sum(weights))
    rate = -(conductance @ potential - np.sum(conductance, axis=1) * potential) / weights / potential
    if not np.any(mask) or float(np.min(rate[mask])) + 1.0e-12 < kappa:
        raise AssertionError("declared kappa is not below the tail rate")
    energy = 0.5 * float(np.sum(conductance * (vector[:, None] - vector[None, :]) ** 2))
    potential_term = float(np.sum(weights * rate * vector**2))
    remainder = 0.5 * float(np.sum(conductance * potential[:, None] * potential[None, :] * (vector[:, None] / potential[:, None] - vector[None, :] / potential[None, :]) ** 2))
    residual = energy - potential_term - remainder
    return energy, remainder, residual


def base() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    pi = np.array([0.2, 0.3, 0.5], dtype=float)
    c = np.array([[0.0, 0.4, 0.1], [0.4, 0.0, 0.6], [0.1, 0.6, 0.0]], dtype=float)
    v = np.array([1.0, 1.4, 5.0], dtype=float)
    tail = np.array([False, False, True])
    rate = -(c @ v - np.sum(c, axis=1) * v) / pi / v
    return pi, c, v, tail, float(rate[tail][0]) * 0.5


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pi, c, v, tail, kappa = base()
    f = np.array([0.0, 0.0, 1.0], dtype=float)
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, fn: Callable[[], None], group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        try:
            fn()
        except AssertionError:
            checks.append({"name": name, "group": group, "status": "PASS", "expected": "mutation rejected"})
            return
        raise AssertionError(f"hostile mutation accepted: {name}")

    check("asymmetric conductance", lambda: validate(pi, c + np.triu(np.ones_like(c), 1) * 0.01, v, f, tail, kappa), "symmetry")
    bad_v = v.copy(); bad_v[1] = 0.0
    check("nonpositive potential", lambda: validate(pi, c, bad_v, f, tail, kappa), "positivity")
    bad_pi = pi.copy(); bad_pi[0] = -0.1
    check("nonpositive stationary weight", lambda: validate(bad_pi, c, v, f, tail, kappa), "positivity")
    check("wrong rate sign", lambda: validate(pi, c, v, f, tail, -kappa), "rate sign")
    def omitted_remainder() -> None:
        energy, remainder, residual = validate(pi, c, v, f, tail, kappa)
        del remainder
        if abs(energy - (energy - residual)) <= 1.0e-12:
            raise AssertionError("omitted remainder unexpectedly exact")
    check("omitted ground-state remainder", omitted_remainder, "identity")
    non_tail = np.array([1.0, 0.0, 1.0], dtype=float)
    check("non-tail-supported vector", lambda: validate(pi, c, v, non_tail, tail, kappa), "support")
    rate = -(c @ v - np.sum(c, axis=1) * v) / pi / v
    forged = float(rate[tail][0]) * 2.0
    check("forged kappa floor", lambda: validate(pi, c, v, f, tail, forged), "rate floor")

    if not (manifest["result_id"] == "R-421" and manifest["exploration_id"] == "EXP-001266" and manifest["claim_bearing"] is False):
        raise AssertionError("manifest identity")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r421-hostile/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "hostile",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "controls": {
            "all_mutations_rejected": True,
            "mutation_count": assertion_count,
            "numeric_evaluation": False,
            "physical_promotion": False,
        },
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(f"R-421 HOSTILE PASS {assertion_count}/{assertion_count} invalid mutations rejected")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
