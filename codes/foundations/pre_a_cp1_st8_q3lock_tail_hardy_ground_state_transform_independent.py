#!/usr/bin/env python3
"""Non-importing reconstruction of the R-421 finite Hardy identity."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-tail-hardy-ground-state-transform-manifest.json"
SLUG = "tail_hardy_ground_state_transform"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}" / "independent.json"


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


def transform(pi: np.ndarray, conductance: np.ndarray, potential: np.ndarray, f: np.ndarray) -> tuple[float, float, float, float, np.ndarray]:
    weights = np.asarray(pi, dtype=float)
    c = np.asarray(conductance, dtype=float)
    v = np.asarray(potential, dtype=float)
    vector = np.asarray(f, dtype=float)
    if weights.ndim != 1 or c.shape != (weights.size, weights.size) or v.shape != weights.shape or vector.shape != weights.shape:
        raise AssertionError("independent shape mismatch")
    if not np.all(np.isfinite(weights)) or np.any(weights <= 0.0) or not np.all(np.isfinite(v)) or np.any(v <= 0.0):
        raise AssertionError("independent positivity failure")
    if not np.all(np.isfinite(c)) or np.max(np.abs(c - c.T)) > 1.0e-12 or np.min(c) < -1.0e-12:
        raise AssertionError("independent conductance failure")
    weights = weights / float(np.sum(weights))
    rate = -(c @ v - np.sum(c, axis=1) * v) / weights / v
    energy = 0.5 * float(np.sum(c * (vector[:, None] - vector[None, :]) ** 2))
    potential_term = float(np.sum(weights * rate * vector**2))
    remainder = 0.5 * float(np.sum(c * v[:, None] * v[None, :] * (vector[:, None] / v[:, None] - vector[None, :] / v[None, :]) ** 2))
    return energy, potential_term, remainder, energy - potential_term - remainder, rate


def fixtures() -> list[tuple[np.ndarray, np.ndarray, np.ndarray, float]]:
    """Build deterministic reversible graphs without importing the primary lane."""
    result: list[tuple[np.ndarray, np.ndarray, np.ndarray, float]] = []
    weights = np.array([4.0, 3.0, 2.0, 1.0], dtype=float)
    weights /= np.sum(weights)
    conductance = np.zeros((4, 4), dtype=float)
    conductance[0, 1] = conductance[1, 0] = 0.7
    conductance[1, 2] = conductance[2, 1] = 0.5
    conductance[2, 3] = conductance[3, 2] = 0.9
    potential = np.array([1.0, 1.4, 2.2, 5.0], dtype=float)
    result.append((weights, conductance, potential, 1.0))

    weights = np.array([4.0, 2.0, 3.0, 1.0, 0.5], dtype=float)
    weights /= np.sum(weights)
    conductance = np.zeros((5, 5), dtype=float)
    for i in range(4):
        conductance[i, i + 1] = conductance[i + 1, i] = (i + 2.0) / 5.0
    potential = np.array([3.0, 1.0, 1.5, 2.0, 6.0], dtype=float)
    result.append((weights, conductance, potential, 1.8))

    weights = np.arange(6, 0, -1, dtype=float)
    weights /= float(np.sum(weights))
    conductance = np.zeros((6, 6), dtype=float)
    for i in range(5):
        conductance[i, i + 1] = conductance[i + 1, i] = 0.3 + 0.05 * i
    potential = np.array([1.0, 1.2, 1.6, 2.1, 3.5, 7.0], dtype=float)
    result.append((weights, conductance, potential, 1.5))
    return result


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 180:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite = [
        "finite_ground_state_transform_identity_closed",
        "finite_tail_supported_hardy_control_closed",
        "finite_r419_selected_row_integration_closed",
        "finite_independent_reconstruction_closed",
        "finite_hostile_mutation_rejection_closed",
    ]
    promoted = {key: value for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in finite}
    check("identity", manifest["result_id"] == "R-421" and manifest["exploration_id"] == "EXP-001266" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-421/EXP-001266/false", "provenance")
    check("scope firewall", all(manifest["scope"][key] for key in finite) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    tolerance = float(manifest["finite_fixture"]["numerical_tolerance"])
    rate_floor = float(manifest["finite_fixture"]["rate_floor"])
    residuals: list[float] = []
    slacks: list[float] = []
    minimum_rates: list[float] = []
    remainder_values: list[float] = []
    vector_count = 0
    tail_count = 0

    for fixture_index, (weights, conductance, potential, threshold) in enumerate(fixtures()):
        logs = np.log(weights)
        phi = float(np.max(logs)) - logs
        tail = phi >= threshold
        rates = transform(weights, conductance, potential, np.zeros_like(weights))[4]
        check(f"fixture={fixture_index} symmetry", np.max(np.abs(conductance - conductance.T)) <= tolerance, float(np.max(np.abs(conductance - conductance.T))), f"<={tolerance}", "conductance")
        check(f"fixture={fixture_index} normalized", abs(float(np.sum(weights)) - 1.0) <= tolerance, float(np.sum(weights)), 1.0, "weights")
        check(f"fixture={fixture_index} tail", bool(np.any(tail)) and float(np.min(rates[tail])) > rate_floor, [int(np.sum(tail)), float(np.min(rates[tail]))], f"nonempty and rate>{rate_floor}", "tail drift")
        if not np.any(tail):
            continue
        tail_count += 1
        kappa = float(np.min(rates[tail]))
        minimum_rates.append(kappa)
        indices = np.arange(weights.size, dtype=float)
        vectors = [tail.astype(float), phi * tail, np.sin(indices + 1.0) * tail, np.where((indices.astype(int) % 2) == 0, 1.0, -1.0) * tail]
        for mode, vector in enumerate(vectors):
            energy, potential_term, remainder, residual, _ = transform(weights, conductance, potential, vector)
            slack = energy - kappa * float(np.sum(weights[tail] * vector[tail] ** 2))
            residuals.append(abs(residual))
            slacks.append(slack)
            remainder_values.append(remainder)
            vector_count += 1
            check(f"fixture={fixture_index} mode={mode} support", np.all(vector[~tail] == 0.0), "zero off tail", "zero off tail", "support")
            check(f"fixture={fixture_index} mode={mode} identity", abs(residual) <= tolerance * 100.0, abs(residual), f"<={tolerance * 100.0}", "ground-state transform")
            check(f"fixture={fixture_index} mode={mode} remainder", remainder >= -tolerance * 100.0, remainder, f">=-{tolerance * 100.0}", "remainder")
            check(f"fixture={fixture_index} mode={mode} Hardy", slack >= -tolerance * 100.0, slack, f">=-{tolerance * 100.0}", "tail Hardy")

    check("coverage", tail_count == len(fixtures()) and vector_count == 4 * tail_count, [tail_count, vector_count], "four vectors for every fixture", "coverage")
    check("aggregate residual", max(residuals, default=float("inf")) <= tolerance * 100.0, max(residuals, default=float("inf")), f"<={tolerance * 100.0}", "aggregate")
    check("aggregate remainder", min(remainder_values, default=-float("inf")) >= -tolerance * 100.0, min(remainder_values, default=-float("inf")), f">=-{tolerance * 100.0}", "aggregate")
    check("aggregate Hardy", min(slacks, default=-float("inf")) >= -tolerance * 100.0, min(slacks, default=-float("inf")), f">=-{tolerance * 100.0}", "aggregate")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r421-independent/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "independent",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": {
            "fixture_count": len(fixtures()),
            "tail_fixture_count": tail_count,
            "function_count": vector_count,
            "minimum_tail_rate": min(minimum_rates, default=float("inf")),
            "maximum_identity_residual": max(residuals, default=0.0),
            "minimum_remainder": min(remainder_values, default=0.0),
            "minimum_hardy_slack": min(slacks, default=0.0),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-421 INDEPENDENT PASS {assertion_count}/{assertion_count} assertions; fixtures={len(fixtures())} tail_fixtures={tail_count} functions={vector_count}; max_identity_residual={max(residuals, default=0.0):.3e}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
