#!/usr/bin/env python3
"""Execute the finite R-421 tail-supported ground-state transform.

The Q3 rows are inherited from the hash-pinned R-419 parent.  This script
checks an exact reversible identity and its tail-supported Hardy consequence;
it never treats the finite minimum as a uniform or physical bound.
"""

from __future__ import annotations

import argparse
import hashlib
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-tail-hardy-ground-state-transform-manifest.json"
PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
SLUG = "tail_hardy_ground_state_transform"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def hardy_identity(pi: np.ndarray, conductance: np.ndarray, potential: np.ndarray, f: np.ndarray) -> dict[str, float]:
    """Return E, the ground-state potential term, and the nonnegative remainder."""
    weights = np.asarray(pi, dtype=float)
    c = np.asarray(conductance, dtype=float)
    v = np.asarray(potential, dtype=float)
    vector = np.asarray(f, dtype=float)
    if weights.ndim != 1 or c.shape != (weights.size, weights.size) or v.shape != weights.shape or vector.shape != weights.shape:
        raise AssertionError("shape mismatch in Hardy identity")
    if not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise AssertionError("stationary weights must be positive")
    if not np.all(np.isfinite(c)) or np.max(np.abs(c - c.T)) > 1.0e-10 or np.min(c) < -1.0e-12:
        raise AssertionError("conductance must be symmetric and nonnegative")
    if not np.all(np.isfinite(v)) or np.any(v <= 0.0):
        raise AssertionError("ground-state vector must be positive")
    if not np.all(np.isfinite(vector)):
        raise AssertionError("test vector is nonfinite")
    weights = weights / float(np.sum(weights))
    lv = (c @ v - np.sum(c, axis=1) * v) / weights
    rate = -lv / v
    energy = 0.5 * float(np.sum(c * (vector[:, None] - vector[None, :]) ** 2))
    potential_term = float(np.sum(weights * rate * vector**2))
    remainder = 0.5 * float(np.sum(c * (v[:, None] * v[None, :]) * (vector[:, None] / v[:, None] - vector[None, :] / v[None, :]) ** 2))
    return {"energy": energy, "potential_term": potential_term, "remainder": remainder, "identity_residual": energy - potential_term - remainder, "rate_min": float(np.min(rate)), "rate_max": float(np.max(rate))}


def test_vectors(phi: np.ndarray, tail: np.ndarray) -> list[np.ndarray]:
    indices = np.arange(phi.size, dtype=float)
    vectors = [
        tail.astype(float),
        phi * tail,
        np.sin(indices + 1.0) * tail,
        np.where((indices.astype(int) % 2) == 0, 1.0, -1.0) * tail,
    ]
    return [np.asarray(vector, dtype=float) for vector in vectors]


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    fixture = parent["finite_fixture"]
    local_fixture = manifest["finite_fixture"]
    tolerance = float(local_fixture["numerical_tolerance"])
    crosscheck_tolerance = float(local_fixture["crosscheck_tolerance"])
    probability_floor = float(local_fixture["probability_floor"])
    rate_floor = float(local_fixture["rate_floor"])
    alpha = float(Fraction(str(local_fixture["alpha"])))
    theta = float(Fraction(str(local_fixture["tail_threshold"])))
    chi = float(Fraction(str(fixture["chi"])))
    betas = [float(Fraction(value)) for value in local_fixture["beta_values"]]
    orientations = list(local_fixture["orientations"])
    pairs = [(int(item["volume"]), int(dimension)) for item in local_fixture["q3_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 520:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    expected_finite = [
        "finite_ground_state_transform_identity_closed",
        "finite_tail_supported_hardy_control_closed",
        "finite_r419_selected_row_integration_closed",
        "finite_independent_reconstruction_closed",
        "finite_hostile_mutation_rejection_closed",
    ]
    promoted = {key: value for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in expected_finite}
    check("identity", manifest["result_id"] == "R-421" and manifest["exploration_id"] == "EXP-001266" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-421/EXP-001266/false", "provenance")
    check("parent hash", sha256(PARENT) == manifest["upstream_authority"]["sha256"], sha256(PARENT), manifest["upstream_authority"]["sha256"], "authority")
    check("scope firewall", all(manifest["scope"][key] for key in expected_finite) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("fixture", pairs == [(2, 3), (2, 6), (2, 12), (3, 3), (3, 4), (4, 4)], pairs, "selected R-419 Q3 systems", "fixture")
    check("beta/orientation", betas == [0.5, 2.0, 8.0] and orientations == ["right", "left"], [betas, orientations], "fixed R-419 grid", "fixture")
    check("positive parameters", alpha > 0.0 and theta > 0.0 and chi > 0.0 and rate_floor > 0.0, [alpha, theta, chi, rate_floor], ">0", "fixture")

    row_count = 0
    function_count = 0
    tail_row_count = 0
    identity_residuals: list[float] = []
    hardy_slacks: list[float] = []
    rate_minima: list[float] = []
    remainder_minima: list[float] = []
    systems: list[dict[str, Any]] = []

    for volume, dimension in pairs:
        _q_ops, hamiltonian, _terms = r419.r399.split_system(volume, dimension, fixture)
        basis = r419.r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        system_rows = 0
        for beta in betas:
            log_reference, _direct, _shifted = r416.log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} normalized", np.all(np.isfinite(log_reference)) and abs(float(np.sum(np.exp(log_reference))) - 1.0) <= crosscheck_tolerance, float(np.sum(np.exp(log_reference))), 1.0, "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                for weights, minimum_log_row in r416.conditional_rows(log_reference, order, dimension, probability_floor):
                    row_count += 1
                    system_rows += 1
                    check(f"V={volume} d={dimension} {orientation} row positivity", math.isfinite(minimum_log_row) and np.all(np.isfinite(weights)) and float(np.min(weights)) > 0.0, minimum_log_row, "finite positive conditional row", "rows")
                    graph = r416.projected_graph(weights, momentum, chi)
                    pi = np.asarray(graph["weights"], dtype=float)
                    conductance = np.asarray(graph["conductance"], dtype=float)
                    logs = np.log(pi)
                    phi = float(np.max(logs)) - logs
                    potential = np.exp(alpha * phi)
                    tail = phi >= theta
                    check(f"V={volume} d={dimension} {orientation} symmetric c", np.max(np.abs(conductance - conductance.T)) <= tolerance and float(np.min(conductance)) >= -tolerance, float(np.max(np.abs(conductance - conductance.T))), f"<={tolerance}", "conductance")
                    rate_data = hardy_identity(pi, conductance, potential, np.zeros_like(pi))
                    rates = np.empty_like(pi)
                    lv = (conductance @ potential - np.sum(conductance, axis=1) * potential) / pi
                    rates[:] = -lv / potential
                    if bool(np.any(tail)):
                        tail_row_count += 1
                        kappa = float(np.min(rates[tail]))
                        check(f"V={volume} d={dimension} {orientation} tail rate", kappa > rate_floor, kappa, f">{rate_floor}", "tail drift")
                        rate_minima.append(kappa)
                        for mode, vector in enumerate(test_vectors(phi, tail)):
                            check(f"V={volume} d={dimension} {orientation} row={row_count} mode={mode} support", np.all(vector[~tail] == 0.0), "zero off tail", "zero off tail", "support")
                            terms = hardy_identity(pi, conductance, potential, vector)
                            residual = abs(float(terms["identity_residual"]))
                            hardy_slack = float(terms["energy"] - kappa * np.sum(pi[tail] * vector[tail] ** 2))
                            identity_residuals.append(residual)
                            hardy_slacks.append(hardy_slack)
                            remainder_minima.append(float(terms["remainder"]))
                            check(f"V={volume} d={dimension} {orientation} row={row_count} mode={mode} identity", residual <= tolerance * 100.0, residual, f"<={tolerance * 100.0}", "ground-state transform")
                            check(f"V={volume} d={dimension} {orientation} row={row_count} mode={mode} remainder", terms["remainder"] >= -tolerance * 100.0, terms["remainder"], f">=-{tolerance * 100.0}", "remainder")
                            check(f"V={volume} d={dimension} {orientation} row={row_count} mode={mode} Hardy", hardy_slack >= -tolerance * 100.0, hardy_slack, f">=-{tolerance * 100.0}", "tail Hardy")
                            function_count += 1
        systems.append({"volume": volume, "dimension": dimension, "row_count": system_rows})

    check("rows covered", row_count > 0 and tail_row_count > 0 and function_count == 4 * tail_row_count, [row_count, tail_row_count, function_count], "positive rows and four vectors per tail row", "coverage")
    check("identity aggregate", max(identity_residuals, default=float("inf")) <= tolerance * 100.0, max(identity_residuals, default=float("inf")), f"<={tolerance * 100.0}", "aggregate")
    check("remainder aggregate", min(remainder_minima, default=-float("inf")) >= -tolerance * 100.0, min(remainder_minima, default=-float("inf")), f">=-{tolerance * 100.0}", "aggregate")
    check("Hardy aggregate", min(hardy_slacks, default=-float("inf")) >= -tolerance * 100.0, min(hardy_slacks, default=-float("inf")), f">=-{tolerance * 100.0}", "aggregate")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r421-primary/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "primary",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": {
            "system_count": len(pairs),
            "conditional_row_count": row_count,
            "tail_row_count": tail_row_count,
            "function_count": function_count,
            "alpha": alpha,
            "tail_threshold": theta,
            "minimum_tail_rate": min(rate_minima, default=float("inf")),
            "maximum_identity_residual": max(identity_residuals, default=0.0),
            "minimum_remainder": min(remainder_minima, default=0.0),
            "minimum_hardy_slack": min(hardy_slacks, default=0.0),
            "systems": systems,
        },
        "source_hashes": {
            "primary": sha256(Path(__file__)),
            "manifest": sha256(MANIFEST),
            "upstream_manifest": sha256(PARENT),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-421 PRIMARY PASS {assertion_count}/{assertion_count} assertions; rows={row_count} tail_rows={tail_row_count} functions={function_count}; max_identity_residual={max(identity_residuals, default=0.0):.3e}; min_tail_rate={min(rate_minima, default=float('inf')):.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
