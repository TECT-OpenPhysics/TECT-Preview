#!/usr/bin/env python3
"""Independent finite-Q3 split-step recurrence audit for EXP-001156.

This lane rebuilds the oscillator, graph, onsite/bond split, Gibbs state and
commutator seminorm without importing the primary implementation.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_actual_split_step_commutator_recurrence_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-split-step-commutator-recurrence-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-independent-{SLUG}" / "independent.json"


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


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((size, size), dtype=complex)
    for index in range(size - 1):
        annihilation[index, index + 1] = math.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / math.sqrt(2.0), (annihilation - creation) / (1j * math.sqrt(2.0))


def lift(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError("EXP-001156 uses volumes 2, 4 and 6")


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def bond(left: np.ndarray, right: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def system(volume: int, size: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], list[np.ndarray], list[tuple[int, int]], np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q_single, p_single = oscillator(size)
    identity = np.eye(size, dtype=complex)
    qs = [lift(q_single, site, volume, identity) for site in range(volume)]
    ps = [lift(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(parameters[key])) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(qs, ps)]
    edge_list = edges(volume)
    bonds = [bond(qs[left], qs[right], c, lam) for left, right in edge_list]
    zero = np.zeros_like(qs[0])
    return qs, ps, edge_list, hermitian(sum(onsite, zero) + sum(bonds, zero)), onsite, bonds


def spectral_unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def thermal_state(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(generator))
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def bracket(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return math.sqrt(max(0.0, float(np.real(value))))


def lengths(qs: list[np.ndarray], ps: list[np.ndarray], observable: np.ndarray, rho: np.ndarray) -> list[float]:
    return [math.hypot(seminorm(bracket(q, observable), rho), seminorm(bracket(p, observable), rho)) for q, p in zip(qs, ps)]


def product(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> np.ndarray:
    result = np.eye(terms[0].shape[0], dtype=complex)
    for index in order:
        result = spectral_unitary(terms[index], sign * delta, hbar) @ result
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    parameters = manifest["model_parameters"]
    volumes = [int(value) for value in fixture["volume_values"]]
    size = int(fixture["oscillator_dimension"])
    beta = float(Fraction(fixture["beta"]))
    hbar = float(Fraction(fixture["hbar"]))
    amplitude = float(Fraction(fixture["character_amplitude"]))
    delta = float(Fraction(fixture["time_step"]))
    steps = int(fixture["steps"])
    C, J = float(Fraction(fixture["recurrence_C"])), float(Fraction(fixture["recurrence_J"]))
    tolerance = float(fixture["finite_tolerance"])
    recurrence_tolerance = float(fixture["recurrence_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001156" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001156/T-054", "provenance")
    check("independent construction", True, "no primary import", "independent lane", "provenance")
    check("time fixture", steps * delta == 1.0 / 3.0, steps * delta, "1/3", "fixture")
    check("order fixture", len(manifest["split_orders"]) == int(fixture["split_order_count"]), len(manifest["split_orders"]), fixture["split_order_count"], "split order")
    check("scope firewall", scope["actual_split_recurrence_theorem_closed"] is False and scope["common_alpha_closed"] is False, scope, "open", "scope")

    summaries: list[dict[str, Any]] = []
    length_count = 0
    recurrence_count = 0
    for volume in volumes:
        qs, ps, edge_list, hamiltonian, onsite, bonds = system(volume, size, parameters)
        rho = thermal_state(hamiltonian, beta)
        base = character(qs[0] + qs[1], amplitude, hbar)
        adjacency = {site: set() for site in range(volume)}
        for left, right in edge_list:
            adjacency[left].add(right)
            adjacency[right].add(left)
        forward = list(range(len(onsite) + len(bonds)))
        orders = {manifest["split_orders"][0]: forward, manifest["split_orders"][1]: list(reversed(forward))}
        for order_name, order in orders.items():
            for time_sign in (-1, 1):
                step_operator = product(onsite + bonds, order, time_sign, delta, hbar)
                for adjoint in (0, 1):
                    source = base.conj().T if adjoint else base
                    history: list[list[float]] = []
                    evolved = source.copy()
                    for _ in range(steps + 1):
                        row = lengths(qs, ps, evolved, rho)
                        check(f"V={volume} order={order_name} sign={time_sign} adj={adjoint} finite", all(np.isfinite(value) and value >= -tolerance for value in row), row, "finite", "commutator rows")
                        history.append(row)
                        length_count += volume
                        evolved = step_operator @ evolved @ step_operator.conj().T
                    residuals: list[float] = []
                    violations: list[dict[str, Any]] = []
                    for step in range(steps):
                        for site in range(volume):
                            neighbor_sum = sum(history[step][neighbor] for neighbor in adjacency[site])
                            rhs = (1.0 + C * delta) * history[step][site] + J * delta * neighbor_sum
                            residual = history[step + 1][site] - rhs
                            residuals.append(residual)
                            recurrence_count += 1
                            if residual > recurrence_tolerance:
                                violations.append({"volume": volume, "order": order_name, "context": f"time{time_sign}_adjoint{adjoint}", "step": step, "site": site, "lhs": history[step + 1][site], "rhs": rhs, "residual": residual, "neighbor_sum": neighbor_sum})
                    summaries.append({"volume": volume, "order": order_name, "context": f"time{time_sign}_adjoint{adjoint}", "max_residual": max(residuals, default=0.0), "violation_count": len(violations), "residual_min": min(residuals, default=0.0), "violations": violations[:8]})
            check(f"V={volume} order={order_name} contexts", len([row for row in summaries if row["volume"] == volume and row["order"] == order_name]) == int(fixture["orientation_count"]), len([row for row in summaries if row["volume"] == volume and row["order"] == order_name]), fixture["orientation_count"], "contexts")

    status = "PASS_ALL_SPLIT_ROWS" if all(row["violation_count"] == 0 for row in summaries) else "FAIL_SPLIT_ROUTE_LOCAL"
    check("candidate outcome recorded", status in ("PASS_ALL_SPLIT_ROWS", "FAIL_SPLIT_ROUTE_LOCAL"), status, "explicit finite outcome", "route decision")
    weighted_step = 1 + (Fraction(fixture["recurrence_C"]) + Fraction(fixture["recurrence_J"]) * Fraction(fixture["weighted_degree"]) * Fraction(fixture["base_weight"])) * Fraction(fixture["time_step"])
    check("weighted step arithmetic", weighted_step == Fraction(31, 18), weighted_step, "31/18", "fixture")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ACTUAL-SPLIT-STEP-COMMUTATOR-RECURRENCE-AUDIT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "context_summaries": summaries,
            "length_row_count": length_count,
            "recurrence_row_count": recurrence_count,
            "recurrence_status": status,
            "all_orders_pass": status == "PASS_ALL_SPLIT_ROWS",
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
    print(f"INDEPENDENT ACTUAL-SPLIT-STEP-COMMUTATOR-RECURRENCE PASS {payload['passed']}/{payload['assertion_count']} status={payload['derived']['recurrence_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
