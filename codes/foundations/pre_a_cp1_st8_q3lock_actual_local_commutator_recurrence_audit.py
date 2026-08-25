#!/usr/bin/env python3
"""Primary finite actual-Q3 recurrence audit for EXP-001155.

The recurrence is tested as a candidate on a declared finite Gibbs
commutator seminorm.  A failed row is recorded as route-local evidence; it is
not promoted to a theorem about every possible Q3 common-core topology.
"""

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
SLUG = "pre_a_cp1_st8_q3lock_actual_local_commutator_recurrence_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-local-commutator-recurrence-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
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


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def two_sided_norm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def local_lengths(q_ops: list[np.ndarray], p_ops: list[np.ndarray], observable: np.ndarray, rho: np.ndarray) -> list[float]:
    return [
        math.hypot(two_sided_norm(commutator(q, observable), rho), two_sided_norm(commutator(p, observable), rho))
        for q, p in zip(q_ops, p_ops)
    ]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    volumes = [int(value) for value in fixture["volume_values"]]
    n = int(fixture["oscillator_dimension"])
    beta = float(Fraction(fixture["beta"]))
    amplitude = float(Fraction(fixture["character_amplitude"]))
    hbar = float(Fraction(fixture["hbar"]))
    delta = float(Fraction(fixture["time_step"]))
    steps = int(fixture["steps"])
    C = float(Fraction(fixture["recurrence_C"]))
    J = float(Fraction(fixture["recurrence_J"]))
    tolerance = float(fixture["finite_tolerance"])
    recurrence_tolerance = float(fixture["recurrence_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001155" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001155/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("time fixture", steps * delta == 1.0 / 3.0 and fixture["time_horizon"] == "1/3", [steps, delta], "6*(1/18)=1/3", "fixture")
    check("context fixture", int(fixture["orientation_count"]) == 4, fixture["orientation_count"], 4, "contexts")
    check("scope firewall", scope["finite_actual_four_context_rows_closed"] and scope["finite_recurrence_candidate_test_closed"] and scope["actual_q3_recurrence_theorem_closed"] is False and scope["common_alpha_closed"] is False, scope, "finite candidate only", "scope")

    all_rows: list[dict[str, Any]] = []
    context_summaries: list[dict[str, Any]] = []
    for volume in volumes:
        fixture_for_q3 = {
            "chi": 1.0,
            "r": -1.0,
            "g": 0.6,
            "c": 0.6,
            "lambda": 0.1,
            "hbar": hbar,
        }
        q_ops, hamiltonian, _, _ = q3.build_volume(volume, n, fixture_for_q3)
        q_single, p_single = q3.oscillator(n)
        identity = np.eye(n, dtype=complex)
        p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
        rho = q3.gibbs(hamiltonian, beta)
        observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
        edges = q3.graph_edges(volume)
        adjacency = {site: set() for site in range(volume)}
        for left, right in edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        context_max_violation: dict[str, float] = {}
        for time_sign in (-1, 1):
            for adjoint in (0, 1):
                context = f"time{time_sign}_adjoint{adjoint}"
                context_observable = observable.conj().T if adjoint else observable
                lengths_by_step: list[list[float]] = []
                for step in range(steps + 1):
                    time = step * delta
                    evolved = unitary(hamiltonian, time_sign * time, hbar) @ context_observable @ unitary(hamiltonian, time_sign * time, hbar).conj().T
                    lengths = local_lengths(q_ops, p_ops, evolved, rho)
                    check(f"V={volume} {context} step={step} finite", all(np.isfinite(value) and value >= -tolerance for value in lengths), lengths, "finite and nonnegative", "commutator rows")
                    lengths_by_step.append(lengths)
                    for site, value in enumerate(lengths):
                        all_rows.append({"volume": volume, "context": context, "time_sign": time_sign, "adjoint": adjoint, "step": step, "site": site, "length": value})
                violations: list[dict[str, Any]] = []
                for step in range(steps):
                    for site in range(volume):
                        neighbor_sum = sum((lengths_by_step[step][neighbor] for neighbor in adjacency[site]), 0.0)
                        rhs = (1.0 + C * delta) * lengths_by_step[step][site] + J * delta * neighbor_sum
                        residual = lengths_by_step[step + 1][site] - rhs
                        row = {"volume": volume, "context": context, "step": step, "site": site, "lhs": lengths_by_step[step + 1][site], "rhs": rhs, "residual": residual, "neighbor_sum": neighbor_sum}
                        all_rows.append({"kind": "recurrence", **row})
                        if residual > recurrence_tolerance:
                            violations.append(row)
                max_residual = max((float(row["residual"]) for row in all_rows if row.get("kind") == "recurrence" and row["volume"] == volume and row["context"] == context), default=0.0)
                context_max_violation[context] = max_residual
                context_summaries.append({"volume": volume, "context": context, "max_residual": max_residual, "violation_count": len(violations), "violations": violations[:8]})
        check(f"V={volume} context coverage", len([row for row in context_summaries if row["volume"] == volume]) == 4, len([row for row in context_summaries if row["volume"] == volume]), 4, "contexts")
        initial = [row for row in all_rows if row.get("volume") == volume and row.get("step") == 0 and "length" in row and row.get("context") == "time1_adjoint0"]
        outside = [row["length"] for row in initial if row["site"] not in tuple(int(value) for value in fixture["support"])]
        check(f"V={volume} source support anchor", max(outside, default=0.0) <= tolerance, max(outside, default=0.0), f"<={tolerance}", "support locality")

    expected_length_rows = sum(4 * volume * (steps + 1) for volume in volumes)
    expected_recurrence_rows = sum(4 * volume * steps for volume in volumes)
    check("length row coverage", len([row for row in all_rows if "length" in row]) == expected_length_rows, len([row for row in all_rows if "length" in row]), expected_length_rows, "coverage")
    check("recurrence row coverage", len([row for row in all_rows if row.get("kind") == "recurrence"]) == expected_recurrence_rows, len([row for row in all_rows if row.get("kind") == "recurrence"]), expected_recurrence_rows, "coverage")
    violations = [row for row in context_summaries if row["violation_count"] > 0]
    recurrence_status = "PASS_ON_GRID" if not violations else "FAIL_ON_GRID_ROUTE_LOCAL"
    check("candidate outcome recorded", recurrence_status in ("PASS_ON_GRID", "FAIL_ON_GRID_ROUTE_LOCAL"), recurrence_status, "explicit finite outcome", "route decision")
    maxima = {str(volume): max((row["max_residual"] for row in context_summaries if row["volume"] == volume), default=0.0) for volume in volumes}
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ACTUAL-LOCAL-COMMUTATOR-RECURRENCE-AUDIT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "context_summaries": context_summaries,
            "row_count": len(all_rows),
            "length_row_count": expected_length_rows,
            "recurrence_row_count": expected_recurrence_rows,
            "recurrence_status": recurrence_status,
            "max_residual_by_volume": maxima,
            "weighted_step_factor": "31/18",
            "actual_q3_recurrence_theorem_closed": False,
            "volume_uniformity_proved": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY ACTUAL-LOCAL-COMMUTATOR-RECURRENCE PASS {payload['passed']}/{payload['assertion_count']} status={payload['derived']['recurrence_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
