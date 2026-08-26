#!/usr/bin/env python3
"""Primary finite actual-Q3 split-step source-amplitude stress for EXP-001196."""
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
SLUG = "pre_a_cp1_st8_q3lock_split_step_amplitude_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-split-step-amplitude-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def split_system(volume: int, size: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], list[np.ndarray], list[tuple[int, int]], np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q_single, p_single = q3.oscillator(size)
    identity = np.eye(size, dtype=complex)
    qs = [embed(q_single, site, volume, identity) for site in range(volume)]
    ps = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(parameters[key])) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(qs, ps)]
    edges = q3.graph_edges(volume)
    bonds = [q3.bond_term(qs[left], qs[right], {"c": c, "lambda": lam}) for left, right in edges]
    zero = np.zeros_like(qs[0])
    return qs, ps, edges, hermitian(sum(onsite, zero) + sum(bonds, zero)), onsite, bonds


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def two_sided_norm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def local_lengths(qs: list[np.ndarray], ps: list[np.ndarray], observable: np.ndarray, rho: np.ndarray) -> list[float]:
    return [math.hypot(two_sided_norm(commutator(q, observable), rho), two_sided_norm(commutator(p, observable), rho)) for q, p in zip(qs, ps)]


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
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph geometry", q3.graph_edges(2) == [(0, 1)] and len(q3.graph_edges(4)) == 4 and len(q3.graph_edges(6)) == 7, [q3.graph_edges(2), len(q3.graph_edges(4)), len(q3.graph_edges(6))], "target/square/2x3", "geometry")
    check("amplitude counts", len(amplitudes) == 5 and len(supports) == 1 and len(betas) == 1, [len(amplitudes), len(supports), len(betas)], [5, 1, 1], "parameter grid")
    check("time fixture", Fraction(steps) * Fraction(fixture["time_step"]) == Fraction(1, 9) and fixture["time_horizon"] == "1/9", [steps, fixture["time_step"]], "2*(1/18)=1/9", "fixture")
    check("scope firewall", scope["finite_amplitude_rows_closed"] and scope["source_amplitude_stress_closed"] and scope["actual_split_recurrence_theorem_closed"] is False and scope["common_alpha_closed"] is False, scope, "finite amplitude stress only", "scope")

    context_summaries: list[dict[str, Any]] = []
    length_rows = 0
    recurrence_rows = 0
    order_names = list(manifest["split_orders"])
    expected_contexts = len(volumes) * len(amplitudes) * len(supports) * len(betas) * len(order_names) * 4
    for volume in volumes:
        qs, ps, edges, hamiltonian, onsite, bonds = split_system(volume, size, parameters)
        fixture_for_q3 = {key: float(Fraction(value)) for key, value in parameters.items()}
        fixture_for_q3["hbar"] = hbar
        _, full_reference, _, _ = q3.build_volume(volume, size, fixture_for_q3)
        decomposition_error = float(np.linalg.norm(hamiltonian - full_reference, ord=2))
        check(f"V={volume} split decomposition", decomposition_error <= tolerance, decomposition_error, f"<={tolerance}", "split decomposition")
        terms = onsite + bonds
        forward = list(range(len(terms)))
        orders = {order_names[0]: forward, order_names[1]: list(reversed(forward))}
        step_operators: dict[str, dict[int, np.ndarray]] = {}
        for order_name, order in orders.items():
            step_operators[order_name] = {}
            for sign in (-1, 1):
                operator = split_step(terms, order, sign, delta, hbar)
                error = float(np.linalg.norm(operator.conj().T @ operator - np.eye(operator.shape[0]), ord=2))
                check(f"V={volume} {order_name} sign={sign} unitary", error <= tolerance, error, f"<={tolerance}", "split product")
                step_operators[order_name][sign] = operator
        adjacency = {site: set() for site in range(volume)}
        for left, right in edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        for beta_fraction in betas:
            rho = q3.gibbs(hamiltonian, float(beta_fraction))
            trace_error = abs(float(np.trace(rho).real) - 1.0)
            check(f"V={volume} beta={beta_fraction} Gibbs state", trace_error <= tolerance and np.all(np.isfinite(rho)), trace_error, f"<={tolerance}", "Gibbs")
            for support in supports:
                generator = sum((qs[site] for site in support), np.zeros_like(qs[0]))
                for amplitude_fraction in amplitudes:
                    observable = q3.character(generator, float(amplitude_fraction), hbar)
                    initial = local_lengths(qs, ps, observable, rho)
                    outside = [initial[site] for site in range(volume) if site not in support]
                    check(f"V={volume} a={amplitude_fraction} support={support} locality", max(outside, default=0.0) <= tolerance, max(outside, default=0.0), f"<={tolerance}", "support locality")
                    for order_name in order_names:
                        for sign in (-1, 1):
                            operator = step_operators[order_name][sign]
                            for adjoint in (0, 1):
                                source = observable.conj().T if adjoint else observable
                                history: list[list[float]] = []
                                evolved = source.copy()
                                for step in range(steps + 1):
                                    lengths = local_lengths(qs, ps, evolved, rho)
                                    check(f"V={volume} a={amplitude_fraction} {order_name} sign={sign} adj={adjoint} step={step} finite", all(np.isfinite(value) and value >= -tolerance for value in lengths), lengths, "finite/nonnegative", "commutator rows")
                                    history.append(lengths)
                                    length_rows += volume
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
                                        recurrence_rows += 1
                                        if residual > recurrence_tolerance:
                                            violations.append({"volume": volume, "beta": str(beta_fraction), "amplitude": str(amplitude_fraction), "support": list(support), "order": order_name, "sign": sign, "adjoint": adjoint, "step": step, "site": site, "lhs": history[step + 1][site], "rhs": rhs, "residual": residual, "neighbor_sum": neighbor_sum})
                                context_summaries.append({"volume": volume, "beta": str(beta_fraction), "amplitude": str(amplitude_fraction), "support": list(support), "order": order_name, "context": f"sign{sign}_adjoint{adjoint}", "max_residual": max(residuals, default=0.0), "min_residual": min(residuals, default=0.0), "violation_count": len(violations), "violations": violations[:4]})
        check(f"V={volume} context coverage", len([row for row in context_summaries if row["volume"] == volume]) == len(amplitudes) * len(supports) * len(betas) * len(order_names) * 4, len([row for row in context_summaries if row["volume"] == volume]), len(amplitudes) * len(supports) * len(betas) * len(order_names) * 4, "coverage")
    check("context coverage", len(context_summaries) == expected_contexts, len(context_summaries), expected_contexts, "coverage")
    status = "PASS_ALL_AMPLITUDE_ROWS" if all(row["violation_count"] == 0 for row in context_summaries) else "FAIL_AMPLITUDE_ROUTE_LOCAL"
    check("candidate outcome recorded", status in ("PASS_ALL_AMPLITUDE_ROWS", "FAIL_AMPLITUDE_ROUTE_LOCAL"), status, "explicit finite outcome", "route decision")
    weighted_step = 1 + (Fraction(fixture["recurrence_C"]) + Fraction(fixture["recurrence_J"]) * Fraction(fixture["weighted_degree"]) * Fraction(fixture["base_weight"])) * Fraction(fixture["time_step"])
    check("weighted step arithmetic", weighted_step == Fraction(31, 18), weighted_step, "31/18", "fixture")
    maxima = {str(amplitude): max((float(row["max_residual"]) for row in context_summaries if row["amplitude"] == str(amplitude)), default=0.0) for amplitude in amplitudes}
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-SPLIT-STEP-AMPLITUDE-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "context_summaries": context_summaries,
            "length_row_count": length_rows,
            "recurrence_row_count": recurrence_rows,
            "parameter_context_count": len(context_summaries),
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
    print(f"PRIMARY ACTUAL-SPLIT-STEP AMPLITUDE STRESS PASS {payload['passed']}/{payload['assertion_count']} status={payload['derived']['recurrence_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())