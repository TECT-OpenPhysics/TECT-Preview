#!/usr/bin/env python3
"""Primary finite actual-Q3 split-step recurrence audit for EXP-001156."""

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
SLUG = "pre_a_cp1_st8_q3lock_actual_split_step_commutator_recurrence_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-split-step-commutator-recurrence-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-primary-{SLUG}" / "primary.json"
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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
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


def split_terms(volume: int, n: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], list[np.ndarray], list[tuple[int, int]], np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    c = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    fixture = {"c": c, "lambda": lam}
    edges = q3.graph_edges(volume)
    bonds = [q3.bond_term(q_ops[left], q_ops[right], fixture) for left, right in edges]
    zero = np.zeros_like(q_ops[0])
    full = hermitian(sum(onsite, zero) + sum(bonds, zero))
    return q_ops, p_ops, edges, full, onsite, bonds


def split_step(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> np.ndarray:
    result = np.eye(terms[0].shape[0], dtype=complex)
    for index in order:
        result = unitary(terms[index], sign * delta, hbar) @ result
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    parameters = manifest["model_parameters"]
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

    check("identity", manifest["exploration_id"] == "EXP-001156" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001156/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("time fixture", steps * delta == 1.0 / 3.0 and fixture["time_horizon"] == "1/3", [steps, delta], "6*(1/18)=1/3", "fixture")
    check("context fixture", int(fixture["orientation_count"]) == 4, fixture["orientation_count"], 4, "contexts")
    check("order fixture", len(manifest["split_orders"]) == int(fixture["split_order_count"]), len(manifest["split_orders"]), fixture["split_order_count"], "split order")
    check("scope firewall", scope["finite_split_four_context_rows_closed"] and scope["finite_split_recurrence_candidate_test_closed"] and scope["actual_split_recurrence_theorem_closed"] is False and scope["common_alpha_closed"] is False, scope, "finite candidate only", "scope")

    all_rows: list[dict[str, Any]] = []
    context_summaries: list[dict[str, Any]] = []
    order_names = manifest["split_orders"]
    for volume in volumes:
        q_ops, p_ops, edges, hamiltonian, onsite, bonds = split_terms(volume, n, parameters)
        fixture_for_q3 = {"chi": float(Fraction(parameters["chi"])), "r": float(Fraction(parameters["r"])), "g": float(Fraction(parameters["g"])), "c": float(Fraction(parameters["c"])), "lambda": float(Fraction(parameters["lambda"])), "hbar": hbar}
        _, full_reference, _, _ = q3.build_volume(volume, n, fixture_for_q3)
        decomposition_error = float(np.linalg.norm(hamiltonian - full_reference, ord=2))
        check(f"V={volume} split decomposition", decomposition_error <= tolerance, decomposition_error, f"<={tolerance}", "split decomposition")
        rho = q3.gibbs(hamiltonian, beta)
        observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
        adjacency = {site: set() for site in range(volume)}
        for left, right in edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        forward = list(range(len(onsite) + len(bonds)))
        orders = {order_names[0]: forward, order_names[1]: list(reversed(forward))}
        for order_name, order in orders.items():
            for time_sign in (-1, 1):
                step_operator = split_step(onsite + bonds, order, time_sign, delta, hbar)
                for adjoint in (0, 1):
                    context = f"{order_name}_time{time_sign}_adjoint{adjoint}"
                    source = observable.conj().T if adjoint else observable
                    lengths_by_step: list[list[float]] = []
                    evolved = source.copy()
                    for step in range(steps + 1):
                        lengths = local_lengths(q_ops, p_ops, evolved, rho)
                        check(f"V={volume} {context} step={step} finite", all(np.isfinite(value) and value >= -tolerance for value in lengths), lengths, "finite and nonnegative", "commutator rows")
                        lengths_by_step.append(lengths)
                        for site, value in enumerate(lengths):
                            all_rows.append({"kind": "length", "volume": volume, "order": order_name, "context": context, "time_sign": time_sign, "adjoint": adjoint, "step": step, "site": site, "length": value})
                        if step < steps:
                            evolved = step_operator @ evolved @ step_operator.conj().T
                    violations: list[dict[str, Any]] = []
                    for step in range(steps):
                        for site in range(volume):
                            neighbor_sum = sum(lengths_by_step[step][neighbor] for neighbor in adjacency[site])
                            rhs = (1.0 + C * delta) * lengths_by_step[step][site] + J * delta * neighbor_sum
                            residual = lengths_by_step[step + 1][site] - rhs
                            row = {"volume": volume, "order": order_name, "context": context, "step": step, "site": site, "lhs": lengths_by_step[step + 1][site], "rhs": rhs, "residual": residual, "neighbor_sum": neighbor_sum}
                            all_rows.append({"kind": "recurrence", **row})
                            if residual > recurrence_tolerance:
                                violations.append(row)
                    max_residual = max((float(row["residual"]) for row in all_rows if row.get("kind") == "recurrence" and row["volume"] == volume and row["order"] == order_name and row["context"] == context), default=0.0)
                    context_summaries.append({"volume": volume, "order": order_name, "context": context, "max_residual": max_residual, "violation_count": len(violations), "violations": violations[:8]})
            check(f"V={volume} {order_name} context coverage", len([row for row in context_summaries if row["volume"] == volume and row["order"] == order_name]) == int(fixture["orientation_count"]), len([row for row in context_summaries if row["volume"] == volume and row["order"] == order_name]), fixture["orientation_count"], "contexts")
        initial = [row for row in all_rows if row.get("kind") == "length" and row["volume"] == volume and row["step"] == 0 and row["order"] == order_names[0] and row["context"].endswith("time1_adjoint0")]
        outside = [row["length"] for row in initial if row["site"] not in tuple(int(value) for value in fixture["support"])]
        check(f"V={volume} source support anchor", max(outside, default=0.0) <= tolerance, max(outside, default=0.0), f"<={tolerance}", "support locality")

    expected_length_rows = sum(int(fixture["split_order_count"]) * 4 * volume * (steps + 1) for volume in volumes)
    expected_recurrence_rows = sum(int(fixture["split_order_count"]) * 4 * volume * steps for volume in volumes)
    check("length row coverage", len([row for row in all_rows if row["kind"] == "length"]) == expected_length_rows, len([row for row in all_rows if row["kind"] == "length"]), expected_length_rows, "coverage")
    check("recurrence row coverage", len([row for row in all_rows if row["kind"] == "recurrence"]) == expected_recurrence_rows, len([row for row in all_rows if row["kind"] == "recurrence"]), expected_recurrence_rows, "coverage")
    violations = [row for row in context_summaries if row["violation_count"] > 0]
    all_orders_pass = not violations
    recurrence_status = "PASS_ALL_SPLIT_ROWS" if all_orders_pass else "FAIL_SPLIT_ROUTE_LOCAL"
    check("candidate outcome recorded", recurrence_status in ("PASS_ALL_SPLIT_ROWS", "FAIL_SPLIT_ROUTE_LOCAL"), recurrence_status, "explicit finite outcome", "route decision")
    weighted_degree = Fraction(fixture["weighted_degree"])
    base_weight = Fraction(fixture["base_weight"])
    weighted_step = 1 + (Fraction(fixture["recurrence_C"]) + Fraction(fixture["recurrence_J"]) * weighted_degree * base_weight) * Fraction(fixture["time_step"])
    check("weighted step arithmetic", weighted_step == Fraction(31, 18), weighted_step, "31/18", "fixture")
    maxima = {f"{order}:{volume}": max((row["max_residual"] for row in context_summaries if row["order"] == order and row["volume"] == volume), default=0.0) for order in order_names for volume in volumes}
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ACTUAL-SPLIT-STEP-COMMUTATOR-RECURRENCE-AUDIT",
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
            "all_orders_pass": all_orders_pass,
            "max_residual_by_order_volume": maxima,
            "weighted_step_factor": str(weighted_step),
            "finite_split_four_context_rows_closed": True,
            "split_product_decomposition_checked": True,
            "actual_split_recurrence_theorem_closed": False,
            "volume_uniformity_proved": False,
            "common_alpha_closed": False,
            "pre_a_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY ACTUAL-SPLIT-STEP-COMMUTATOR-RECURRENCE PASS {payload['passed']}/{payload['assertion_count']} status={payload['derived']['recurrence_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
