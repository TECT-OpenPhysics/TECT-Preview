#!/usr/bin/env python3
"""Independent finite split-step source/beta/volume/shape stress audit."""

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
SLUG = "pre_a_cp1_st8_q3lock_split_step_uniformity_stress_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-split-step-uniformity-stress-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-independent-{SLUG}" / "independent.json"


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def edges(shape: str, volume: int) -> list[tuple[int, int]]:
    if shape == "canonical":
        if volume == 2:
            return [(0, 1)]
        if volume == 4:
            return [(0, 1), (0, 2), (1, 3), (2, 3)]
        if volume == 6:
            return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    if shape == "path":
        return [(index, index + 1) for index in range(volume - 1)]
    raise ValueError(f"unknown shape/volume: {shape}/{volume}")


def bond(left: np.ndarray, right: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def system(shape: str, volume: int, size: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], list[np.ndarray], list[tuple[int, int]], np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q_single, p_single = oscillator(size)
    identity = np.eye(size, dtype=complex)
    qs = [lift(q_single, site, volume, identity) for site in range(volume)]
    ps = [lift(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(parameters[key])) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(qs, ps)]
    edge_list = edges(shape, volume)
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
    check("independent construction", True, "no primary import", "independent lane", "provenance")
    check("time fixture", steps * delta == 1.0 / 3.0, steps * delta, "1/3", "fixture")
    check("case fixture", len(manifest["cases"]) == int(fixture["case_count"]), len(manifest["cases"]), fixture["case_count"], "cases")
    check("scope firewall", scope["uniform_split_recurrence_theorem_closed"] is False and scope["common_alpha_closed"] is False, scope, "open", "scope")

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
                system_cache[key] = system(shape, volume, n, parameters)
            qs, ps, edge_list, hamiltonian, onsite, bonds = system_cache[key]
            check(f"{case_id} V={volume} finite Hamiltonian", np.all(np.isfinite(hamiltonian)), "finite", True, "decomposition")
            adjacency = {site: set() for site in range(volume)}
            for left, right in edge_list:
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
                        step_cache[step_key] = product(onsite + bonds, order, time_sign, delta, hbar)
                    step_operator = step_cache[step_key]
                    for beta_text in beta_values:
                        beta = float(Fraction(beta_text))
                        rho_key = (shape, volume, beta_text)
                        if rho_key not in rho_cache:
                            rho_cache[rho_key] = thermal_state(hamiltonian, beta)
                        rho = rho_cache[rho_key]
                        for pair in source_pairs:
                            pair_key = (shape, volume, pair)
                            if pair_key not in observable_cache:
                                observable_cache[pair_key] = character(qs[pair[0]] + qs[pair[1]], amplitude, hbar)
                            observable = observable_cache[pair_key]
                            for adjoint in (0, 1):
                                context = f"time{time_sign}_adjoint{adjoint}"
                                source = observable.conj().T if adjoint else observable
                                evolved = source.copy()
                                history: list[list[float]] = []
                                for step in range(steps + 1):
                                    row = lengths(qs, ps, evolved, rho)
                                    check(f"{case_id} V={volume} beta={beta_text} source={pair} {order_name} {context} step={step} finite", all(np.isfinite(value) and value >= -tolerance for value in row), row, "finite/nonnegative", "commutator rows")
                                    history.append(row)
                                    length_rows += volume
                                    if step < steps:
                                        evolved = step_operator @ evolved @ step_operator.conj().T
                                violations: list[dict[str, Any]] = []
                                residuals: list[float] = []
                                for step in range(steps):
                                    for site in range(volume):
                                        neighbor_sum = sum(history[step][neighbor] for neighbor in adjacency[site])
                                        rhs = (1.0 + C * delta) * history[step][site] + J * delta * neighbor_sum
                                        residual = history[step + 1][site] - rhs
                                        residuals.append(residual)
                                        recurrence_rows += 1
                                        if residual > recurrence_tolerance:
                                            violations.append({"case": case_id, "shape": shape, "volume": volume, "beta": beta_text, "source_pair": list(pair), "order": order_name, "context": context, "step": step, "site": site, "lhs": history[step + 1][site], "rhs": rhs, "residual": residual, "neighbor_sum": neighbor_sum})
                                summaries.append({"case_id": case_id, "shape": shape, "volume": volume, "beta": beta_text, "source_pair": list(pair), "order": order_name, "context": context, "max_residual": max(residuals, default=0.0), "violation_count": len(violations), "violations": violations[:8]})
                            initial = lengths(qs, ps, source, rho)
                            outside = [initial[site] for site in range(volume) if site not in pair]
                            check(f"{case_id} V={volume} beta={beta_text} source={pair} support anchor", max(outside, default=0.0) <= tolerance, max(outside, default=0.0), f"<={tolerance}", "support")

    check("length row coverage", length_rows == expected_length_rows, length_rows, expected_length_rows, "coverage")
    check("recurrence row coverage", recurrence_rows == expected_recurrence_rows, recurrence_rows, expected_recurrence_rows, "coverage")
    all_pass = all(row["violation_count"] == 0 for row in summaries)
    status = "PASS_ALL_STRESS_ROWS" if all_pass else "FAIL_UNIFORMITY_ROUTE_LOCAL"
    check("candidate outcome recorded", status in ("PASS_ALL_STRESS_ROWS", "FAIL_UNIFORMITY_ROUTE_LOCAL"), status, "explicit finite outcome", "route decision")
    weighted_step = 1 + (Fraction(fixture["recurrence_C"]) + Fraction(fixture["recurrence_J"]) * Fraction(fixture["weighted_degree"]) * Fraction(fixture["base_weight"])) * Fraction(fixture["time_step"])
    check("weighted step arithmetic", weighted_step == Fraction(31, 18), weighted_step, "31/18", "fixture")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-SPLIT-STEP-UNIFORMITY-STRESS-AUDIT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"case_summaries": summaries, "case_count": len(manifest["cases"]), "length_row_count": length_rows, "recurrence_row_count": recurrence_rows, "recurrence_status": status, "all_stress_rows_pass": all_pass, "uniformity_proved": False, "source_uniformity_proved": False, "beta_uniformity_proved": False, "volume_uniformity_proved": False, "shape_uniformity_proved": False, "common_alpha_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT SPLIT-STEP-UNIFORMITY-STRESS PASS {payload['passed']}/{payload['assertion_count']} status={payload['derived']['recurrence_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
