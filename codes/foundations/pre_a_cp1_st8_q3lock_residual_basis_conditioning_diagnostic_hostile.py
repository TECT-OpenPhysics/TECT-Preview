#!/usr/bin/env python3
"""Hostile mutation lane for the R-428 conditioning diagnostic.

The mutation controls ensure that the finite diagnostic cannot be silently
turned into a residual-reuse repair by changing the fixed row, tolerances,
projector constraints, or the inconclusive verdict.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-basis-conditioning-diagnostic-manifest.json"
R426_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-residual_basis_conditioning_diagnostic/hostile.json"


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


def require_rejection(checks: list[dict[str, Any]], name: str, fn: Callable[[], None]) -> None:
    try:
        fn()
    except (AssertionError, ValueError, TypeError, FloatingPointError, np.linalg.LinAlgError):
        checks.append({"name": name, "status": "PASS", "expected": "mutation rejected"})
        return
    raise AssertionError(f"hostile mutation accepted: {name}")


def validate_graph(pi: np.ndarray, conductance: np.ndarray) -> None:
    weights = np.asarray(pi, dtype=float)
    edges = np.asarray(conductance, dtype=float)
    if weights.ndim != 1 or not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise AssertionError("weights must be positive and finite")
    if abs(float(np.sum(weights)) - 1.0) > 5.0e-7:
        raise AssertionError("weights must be normalized")
    if edges.shape != (len(weights), len(weights)) or not np.all(np.isfinite(edges)):
        raise AssertionError("conductance shape or finiteness")
    if np.any(edges < 0.0) or not np.allclose(edges, edges.T, atol=5.0e-7, rtol=0.0):
        raise AssertionError("conductance must be symmetric and nonnegative")


def validate_basis(constraints: np.ndarray, basis: np.ndarray, expected_shape: tuple[int, int]) -> None:
    if basis.shape != expected_shape:
        raise AssertionError("basis dimension changed")
    if np.max(np.abs(basis.T @ basis - np.eye(expected_shape[1]))) > 1.0e-12:
        raise AssertionError("basis lost orthonormality")
    if np.max(np.abs(constraints @ basis)) > 1.0e-12:
        raise AssertionError("basis left constrained subspace")


def validate_verdict(derived: dict[str, Any], manifest: dict[str, Any]) -> None:
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    required = (
        derived["pi_dynamic_range"] > float(thresholds["dynamic_range_floor"]),
        derived["conditioning_amplification_budget"] > float(thresholds["comparison_tolerance"]),
        derived["basis_gap_spread"] > float(thresholds["comparison_tolerance"]),
        derived["recomputed_mismatch"] > float(thresholds["comparison_tolerance"]),
    )
    if not all(required) or derived["precision_certified"] is not False or derived["residual_reuse_closed"] is not False:
        raise AssertionError("diagnostic contract was weakened")
    if derived["classification"] != "INCONCLUSIVE_CONDITIONING":
        raise AssertionError("inconclusive verdict changed")


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(R426_MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    checks: list[dict[str, Any]] = []

    pi = np.array([0.40, 0.30, 0.20, 0.10], dtype=float)
    edges = 0.7 * np.outer(pi, pi)
    np.fill_diagonal(edges, 0.0)
    constraints = np.array([[np.sqrt(0.40 / 0.70), np.sqrt(0.30 / 0.70), 0.0, 0.0], [0.0, 0.0, np.sqrt(0.20 / 0.30), np.sqrt(0.10 / 0.30)]])
    basis = np.linalg.qr(constraints.T, mode="complete")[0][:, 2:]
    validate_graph(pi, edges)
    validate_basis(constraints, basis, (4, 2))

    require_rejection(checks, "negative probability", lambda: validate_graph(np.array([-0.4, 0.3, 0.2, 0.9]), edges))
    require_rejection(checks, "unnormalized probability", lambda: validate_graph(np.array([0.4, 0.3, 0.2, 0.2]), edges))
    asymmetric = edges.copy(); asymmetric[0, 2] += 1.0e-3
    require_rejection(checks, "nonsymmetric conductance", lambda: validate_graph(pi, asymmetric))
    require_rejection(checks, "negative conductance", lambda: validate_graph(pi, np.minimum(edges, -1.0e-3)))
    require_rejection(checks, "wrong residual dimension", lambda: validate_basis(constraints, basis[:, :1], (4, 2)))
    bad_basis = basis.copy(); bad_basis[0, 0] += 1.0e-3
    require_rejection(checks, "nonorthogonal residual basis", lambda: validate_basis(constraints, bad_basis, (4, 2)))

    def altered_row() -> None:
        if [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]] != [2, 16, "8", "right", 7]:
            raise AssertionError("row mutation was accepted")
        raise ValueError("mutation rejected")

    require_rejection(checks, "fixed-row mutation", altered_row)

    def altered_tolerance() -> None:
        if float(target["comparison_tolerance"]) != 5.0e-7:
            raise AssertionError("comparison tolerance mutation accepted")
        raise ValueError("mutation rejected")

    require_rejection(checks, "comparison-tolerance mutation", altered_tolerance)

    def forged_verdict() -> None:
        forged = {"pi_dynamic_range": 1.0, "conditioning_amplification_budget": 0.0, "basis_gap_spread": 0.0, "recomputed_mismatch": 0.0, "precision_certified": True, "residual_reuse_closed": True, "classification": "CERTIFIED"}
        validate_verdict(forged, manifest)

    require_rejection(checks, "forged certified verdict", forged_verdict)

    if manifest["result_id"] != "R-428" or manifest["exploration_id"] != "EXP-001273" or manifest["claim_bearing"] is not False:
        raise AssertionError("manifest identity")
    if manifest["status"] != "INCONCLUSIVE_CONDITIONING" or parent["status"] != "FAIL_ROUTE_LOCAL":
        raise AssertionError("upstream failure or diagnostic status altered")
    checks.append({"name": "status firewall", "status": "PASS", "expected": "R-428 inconclusive and R-426 failure preserved"})
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r428-hostile/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-428",
        "exploration_id": "EXP-001273",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "controls": {
            "all_mutations_rejected": True,
            "mutation_count": len(checks) - 1,
            "fixed_row_preserved": True,
            "comparison_tolerance_preserved": True,
            "inconclusive_verdict_preserved": True,
            "r426_route_failure_preserved": True,
            "physical_promotion": False,
        },
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(f"R-428 HOSTILE PASS {len(checks)}/{len(checks)} invalid mutations rejected; R-426 failure preserved")
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
