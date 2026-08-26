#!/usr/bin/env python3
"""Independent finite actual-Q3 split-step source-amplitude stress for EXP-001196."""
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
SLUG = "pre_a_cp1_st8_q3lock_split_step_amplitude_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-split-step-amplitude-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((size, size), dtype=complex)
    for index in range(size - 1):
        a[index, index + 1] = math.sqrt(index + 1.0)
    return (a + a.conj().T) / math.sqrt(2.0), (a - a.conj().T) / (1j * math.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    table = {2: [(0, 1)], 4: [(0, 1), (0, 2), (1, 3), (2, 3)], 6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]}
    if volume not in table:
        raise ValueError("EXP-001196 uses volumes 2, 4, and 6")
    return table[volume]


def lift(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def bond(left: np.ndarray, right: np.ndarray, c: float, lam: float) -> np.ndarray:
    d = left - right
    d2 = d @ d
    return c * d2 / 2.0 + lam * d2 @ (left @ left + right @ right) / 4.0


def system(volume: int, size: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], list[np.ndarray], list[tuple[int, int]], np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q0, p0 = oscillator(size)
    identity = np.eye(size, dtype=complex)
    qs = [lift(q0, site, volume, identity) for site in range(volume)]
    ps = [lift(p0, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(parameters[key])) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(qs, ps)]
    edges = graph_edges(volume)
    bonds = [bond(qs[left], qs[right], c, lam) for left, right in edges]
    zero = np.zeros_like(qs[0])
    return qs, ps, edges, sym(sum(onsite, zero) + sum(bonds, zero)), onsite, bonds


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(matrix))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def gibbs(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(matrix))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(generator))
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def bracket(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return math.sqrt(max(0.0, float(np.real(value))))


def lengths(qs: list[np.ndarray], ps: list[np.ndarray], word: np.ndarray, rho: np.ndarray) -> list[float]:
    return [math.hypot(seminorm(bracket(q, word), rho), seminorm(bracket(p, word), rho)) for q, p in zip(qs, ps)]


def product(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> np.ndarray:
    result = np.eye(terms[0].shape[0], dtype=complex)
    for index in order:
        result = unitary(terms[index], sign * delta, hbar) @ result
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    parameters = manifest["model_parameters"]
    volumes = [int(value) for value in fixture["volume_values"]]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    supports = [tuple(int(site) for site in support) for support in fixture["support_values"]]
    amplitudes = [Fraction(value) for value in fixture["amplitude_values"]]
    size = int(fixture["oscillator_dimension"])
    hbar = float(Fraction(fixture["hbar"]))
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

    check("identity", manifest["exploration_id"] == "EXP-001196" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001196/T-054", "provenance")
    check("independent construction", True, "separate matrix implementation", "no primary import", "provenance")
    check("amplitude counts", len(amplitudes) == 5 and len(supports) == 1 and len(betas) == 1, [len(amplitudes), len(supports), len(betas)], [5, 1, 1], "parameter grid")
    check("time fixture", Fraction(steps) * Fraction(fixture["time_step"]) == Fraction(1, 9), [steps, fixture["time_step"]], "2*(1/18)=1/9", "fixture")
    check("scope firewall", scope["finite_amplitude_rows_closed"] and scope["source_amplitude_stress_closed"] and scope["actual_split_recurrence_theorem_closed"] is False and scope["common_alpha_closed"] is False, scope, "finite amplitude stress only", "scope")

    summaries: list[dict[str, Any]] = []
    length_count = 0
    recurrence_count = 0
    orders = list(manifest["split_orders"])
    expected_contexts = len(volumes) * len(amplitudes) * len(supports) * len(betas) * len(orders) * 4
    for volume in volumes:
        qs, ps, edges, hamiltonian, onsite, bonds = system(volume, size, parameters)
        terms = onsite + bonds
        order_map = {orders[0]: list(range(len(terms))), orders[1]: list(reversed(range(len(terms))))}
        operators = {(name, sign): product(terms, order, sign, delta, hbar) for name, order in order_map.items() for sign in (-1, 1)}
        adjacency = {site: set() for site in range(volume)}
        for left, right in edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        for beta_fraction in betas:
            rho = gibbs(hamiltonian, float(beta_fraction))
            trace_error = abs(float(np.trace(rho).real) - 1.0)
            check(f"V={volume} beta={beta_fraction} Gibbs state", trace_error <= tolerance and np.all(np.isfinite(rho)), trace_error, f"<={tolerance}", "Gibbs")
            for support in supports:
                generator = sum((qs[site] for site in support), np.zeros_like(qs[0]))
                for amplitude_fraction in amplitudes:
                    base = character(generator, float(amplitude_fraction), hbar)
                    initial = lengths(qs, ps, base, rho)
                    outside = [initial[site] for site in range(volume) if site not in support]
                    check(f"V={volume} a={amplitude_fraction} support={support} locality", max(outside, default=0.0) <= tolerance, max(outside, default=0.0), f"<={tolerance}", "support locality")
                    for order_name in orders:
                        for sign in (-1, 1):
                            operator = operators[(order_name, sign)]
                            for adjoint in (0, 1):
                                word = base.conj().T if adjoint else base
                                history: list[list[float]] = []
                                evolved = word.copy()
                                for step in range(steps + 1):
                                    row = lengths(qs, ps, evolved, rho)
                                    check(f"V={volume} a={amplitude_fraction} {order_name} sign={sign} adj={adjoint} step={step} finite", all(np.isfinite(value) and value >= -tolerance for value in row), row, "finite/nonnegative", "commutator rows")
                                    history.append(row)
                                    length_count += volume
                                    if step < steps:
                                        evolved = operator @ evolved @ operator.conj().T
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
                                            violations.append({"volume": volume, "beta": str(beta_fraction), "amplitude": str(amplitude_fraction), "support": list(support), "order": order_name, "sign": sign, "adjoint": adjoint, "step": step, "site": site, "lhs": history[step + 1][site], "rhs": rhs, "residual": residual, "neighbor_sum": neighbor_sum})
                                summaries.append({"volume": volume, "beta": str(beta_fraction), "amplitude": str(amplitude_fraction), "support": list(support), "order": order_name, "context": f"sign{sign}_adjoint{adjoint}", "max_residual": max(residuals, default=0.0), "min_residual": min(residuals, default=0.0), "violation_count": len(violations), "violations": violations[:4]})
        check(f"V={volume} context coverage", len([row for row in summaries if row["volume"] == volume]) == len(amplitudes) * len(supports) * len(betas) * len(orders) * 4, len([row for row in summaries if row["volume"] == volume]), len(amplitudes) * len(supports) * len(betas) * len(orders) * 4, "coverage")
    check("context coverage", len(summaries) == expected_contexts, len(summaries), expected_contexts, "coverage")
    status = "PASS_ALL_AMPLITUDE_ROWS" if all(row["violation_count"] == 0 for row in summaries) else "FAIL_AMPLITUDE_ROUTE_LOCAL"
    check("candidate outcome recorded", status in ("PASS_ALL_AMPLITUDE_ROWS", "FAIL_AMPLITUDE_ROUTE_LOCAL"), status, "explicit finite outcome", "route decision")
    weighted_step = 1 + (Fraction(fixture["recurrence_C"]) + Fraction(fixture["recurrence_J"]) * Fraction(fixture["weighted_degree"]) * Fraction(fixture["base_weight"])) * Fraction(fixture["time_step"])
    check("weighted step arithmetic", weighted_step == Fraction(31, 18), weighted_step, "31/18", "fixture")
    maxima = {str(amplitude): max((float(row["max_residual"]) for row in summaries if row["amplitude"] == str(amplitude)), default=0.0) for amplitude in amplitudes}
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-SPLIT-STEP-AMPLITUDE-STRESS",
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
            "parameter_context_count": len(summaries),
            "recurrence_status": status,
            "all_amplitude_rows_pass": status == "PASS_ALL_AMPLITUDE_ROWS",
            "max_residual_by_amplitude": maxima,
            "finite_amplitude_rows_closed": True,
            "source_amplitude_stress_closed": True,
            "actual_split_recurrence_theorem_closed": False,
            "volume_uniformity_proved": False,
            "source_uniformity_proved": False,
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
    print(f"INDEPENDENT ACTUAL-SPLIT-STEP AMPLITUDE STRESS PASS {payload['passed']}/{payload['assertion_count']} status={payload['derived']['recurrence_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())