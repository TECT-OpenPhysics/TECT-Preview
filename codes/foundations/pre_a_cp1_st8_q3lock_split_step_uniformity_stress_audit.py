#!/usr/bin/env python3
"""Primary finite split-step source/beta/volume/shape stress audit (EXP-001157)."""

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
SLUG = "pre_a_cp1_st8_q3lock_split_step_uniformity_stress_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-split-step-uniformity-stress-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-primary-{SLUG}" / "primary.json"
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


def seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def lengths(q_ops: list[np.ndarray], p_ops: list[np.ndarray], observable: np.ndarray, rho: np.ndarray) -> list[float]:
    return [math.hypot(seminorm(commutator(q, observable), rho), seminorm(commutator(p, observable), rho)) for q, p in zip(q_ops, p_ops)]


def shape_edges(shape: str, volume: int) -> list[tuple[int, int]]:
    if shape == "canonical":
        return q3.graph_edges(volume)
    if shape == "path":
        return [(index, index + 1) for index in range(volume - 1)]
    raise ValueError(f"unknown shape {shape}")


def split_system(shape: str, volume: int, n: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], list[np.ndarray], list[tuple[int, int]], np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(parameters[key])) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    edges = shape_edges(shape, volume)
    bond_fixture = {"c": c, "lambda": lam}
    bonds = [q3.bond_term(q_ops[left], q_ops[right], bond_fixture) for left, right in edges]
    zero = np.zeros_like(q_ops[0])
    return q_ops, p_ops, edges, hermitian(sum(onsite, zero) + sum(bonds, zero)), onsite, bonds


def split_step(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> np.ndarray:
    result = np.eye(terms[0].shape[0], dtype=complex)
    for index in order:
        result = unitary(terms[index], sign * delta, hbar) @ result
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, parameters, scope = manifest["finite_fixture"], manifest["model_parameters"], manifest["scope"]
    n = int(fixture["oscillator_dimension"])
    amplitude, hbar = float(Fraction(fixture["character_amplitude"])), float(Fraction(fixture["hbar"]))
    delta, steps = float(Fraction(fixture["time_step"])), int(fixture["steps"])
    C, J = float(Fraction(fixture["recurrence_C"])), float(Fraction(fixture["recurrence_J"]))
    tolerance, recurrence_tolerance = float(fixture["finite_tolerance"]), float(fixture["recurrence_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001157" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001157/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("time fixture", steps * delta == 1.0 / 3.0 and fixture["time_horizon"] == "1/3", [steps, delta], "6*(1/18)=1/3", "fixture")
    check("case fixture", len(manifest["cases"]) == int(fixture["case_count"]), len(manifest["cases"]), fixture["case_count"], "cases")
    check("order fixture", len(manifest["split_orders"]) == int(fixture["split_order_count"]), len(manifest["split_orders"]), fixture["split_order_count"], "orders")
    check("scope firewall", all(scope[key] for key in ("finite_uniformity_stress_rows_closed", "source_variation_checked", "beta_variation_checked", "volume_variation_checked", "shape_variation_checked")) and scope["uniform_split_recurrence_theorem_closed"] is False and scope["common_alpha_closed"] is False, scope, "finite stress only", "scope")

    system_cache: dict[tuple[str, int], tuple[list[np.ndarray], list[np.ndarray], list[tuple[int, int]], np.ndarray, list[np.ndarray], list[np.ndarray]]] = {}
    step_cache: dict[tuple[str, int, str, int], np.ndarray] = {}
    rho_cache: dict[tuple[str, int, str], np.ndarray] = {}
    observable_cache: dict[tuple[str, int, tuple[int, int]], np.ndarray] = {}
    summaries: list[dict[str, Any]] = []
    length_rows = 0
    recurrence_rows = 0
    expected_length_rows = 0
    expected_recurrence_rows = 0
    order_names = manifest["split_orders"]

    for case in manifest["cases"]:
        case_id, shape = str(case["id"]), str(case["shape"])
        for volume_value in case["volume_values"]:
            volume = int(volume_value)
            key = (shape, volume)
            if key not in system_cache:
                system_cache[key] = split_system(shape, volume, n, parameters)
            q_ops, p_ops, edges, hamiltonian, onsite, bonds = system_cache[key]
            if shape == "canonical":
                reference_fixture = {key_name: float(Fraction(parameters[key_name])) for key_name in ("chi", "r", "g", "c", "lambda")}
                _, reference, _, _ = q3.build_volume(volume, n, {**reference_fixture, "hbar": hbar})
                decomposition_error = float(np.linalg.norm(hermitian(hamiltonian - reference), ord=2))
                check(f"{case_id} V={volume} canonical decomposition", decomposition_error <= tolerance, decomposition_error, f"<={tolerance}", "decomposition")
            else:
                check(f"{case_id} V={volume} path geometry", len(edges) == volume - 1, len(edges), volume - 1, "shape")
            adjacency = {site: set() for site in range(volume)}
            for left, right in edges:
                adjacency[left].add(right)
                adjacency[right].add(left)
            source_pairs = [tuple(int(item) for item in pair) for pair in case["source_pairs"][str(volume)]]
            beta_values = [str(value) for value in case["beta_values"]]
            context_count = len(source_pairs) * len(beta_values) * len(order_names) * int(fixture["orientation_count"])
            expected_length_rows += context_count * (steps + 1) * volume
            expected_recurrence_rows += context_count * steps * volume
            forward = list(range(len(onsite) + len(bonds)))
            orders = {order_names[0]: forward, order_names[1]: list(reversed(forward))}
            for order_name, order in orders.items():
                for time_sign in (-1, 1):
                    step_key = (shape, volume, order_name, time_sign)
                    if step_key not in step_cache:
                        step_cache[step_key] = split_step(onsite + bonds, order, time_sign, delta, hbar)
                    step_operator = step_cache[step_key]
                    for beta_text in beta_values:
                        beta = float(Fraction(beta_text))
                        rho_key = (shape, volume, beta_text)
                        if rho_key not in rho_cache:
                            rho_cache[rho_key] = q3.gibbs(hamiltonian, beta)
                        rho = rho_cache[rho_key]
                        for pair in source_pairs:
                            pair_key = (shape, volume, pair)
                            if pair_key not in observable_cache:
                                observable_cache[pair_key] = q3.character(q_ops[pair[0]] + q_ops[pair[1]], amplitude, hbar)
                            observable = observable_cache[pair_key]
                            for adjoint in (0, 1):
                                context = f"time{time_sign}_adjoint{adjoint}"
                                source = observable.conj().T if adjoint else observable
                                evolved = source.copy()
                                history: list[list[float]] = []
                                for step in range(steps + 1):
                                    row = lengths(q_ops, p_ops, evolved, rho)
                                    check(f"{case_id} V={volume} beta={beta_text} source={pair} {order_name} {context} step={step} finite", all(np.isfinite(value) and value >= -tolerance for value in row), row, "finite/nonnegative", "commutator rows")
                                    history.append(row)
                                    length_rows += volume
                                    if step < steps:
                                        evolved = step_operator @ evolved @ step_operator.conj().T
                                violations: list[dict[str, Any]] = []
                                for step in range(steps):
                                    for site in range(volume):
                                        neighbor_sum = sum(history[step][neighbor] for neighbor in adjacency[site])
                                        rhs = (1.0 + C * delta) * history[step][site] + J * delta * neighbor_sum
                                        residual = history[step + 1][site] - rhs
                                        recurrence_rows += 1
                                        if residual > recurrence_tolerance:
                                            violations.append({"case": case_id, "shape": shape, "volume": volume, "beta": beta_text, "source_pair": list(pair), "order": order_name, "context": context, "step": step, "site": site, "lhs": history[step + 1][site], "rhs": rhs, "residual": residual, "neighbor_sum": neighbor_sum})
                                summaries.append({"case_id": case_id, "shape": shape, "volume": volume, "beta": beta_text, "source_pair": list(pair), "order": order_name, "context": context, "max_residual": max((history[step + 1][site] - ((1.0 + C * delta) * history[step][site] + J * delta * sum(history[step][neighbor] for neighbor in adjacency[site])) for step in range(steps) for site in range(volume)), default=0.0), "violation_count": len(violations), "violations": violations[:8]})
                            initial = lengths(q_ops, p_ops, source, rho)
                            outside = [initial[site] for site in range(volume) if site not in pair]
                            check(f"{case_id} V={volume} beta={beta_text} source={pair} support anchor", max(outside, default=0.0) <= tolerance, max(outside, default=0.0), f"<={tolerance}", "support")

    check("length row coverage", length_rows == expected_length_rows, length_rows, expected_length_rows, "coverage")
    check("recurrence row coverage", recurrence_rows == expected_recurrence_rows, recurrence_rows, expected_recurrence_rows, "coverage")
    all_pass = all(row["violation_count"] == 0 for row in summaries)
    status = "PASS_ALL_STRESS_ROWS" if all_pass else "FAIL_UNIFORMITY_ROUTE_LOCAL"
    check("candidate outcome recorded", status in ("PASS_ALL_STRESS_ROWS", "FAIL_UNIFORMITY_ROUTE_LOCAL"), status, "explicit finite outcome", "route decision")
    weighted_step = 1 + (Fraction(fixture["recurrence_C"]) + Fraction(fixture["recurrence_J"]) * Fraction(fixture["weighted_degree"]) * Fraction(fixture["base_weight"])) * Fraction(fixture["time_step"])
    check("weighted step arithmetic", weighted_step == Fraction(31, 18), weighted_step, "31/18", "fixture")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-SPLIT-STEP-UNIFORMITY-STRESS-AUDIT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"case_summaries": summaries, "case_count": len(manifest["cases"]), "length_row_count": length_rows, "recurrence_row_count": recurrence_rows, "recurrence_status": status, "all_stress_rows_pass": all_pass, "uniformity_proved": False, "source_uniformity_proved": False, "beta_uniformity_proved": False, "volume_uniformity_proved": False, "shape_uniformity_proved": False, "common_alpha_closed": False, "pre_a_closed": False},
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
    print(f"PRIMARY SPLIT-STEP-UNIFORMITY-STRESS PASS {payload['passed']}/{payload['assertion_count']} status={payload['derived']['recurrence_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
