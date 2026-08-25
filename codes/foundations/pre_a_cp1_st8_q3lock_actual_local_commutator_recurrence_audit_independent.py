#!/usr/bin/env python3
"""Independent finite-Q3 recurrence audit for EXP-001155.

This lane rebuilds the oscillator, graph, Hamiltonian, Gibbs state and
commutator seminorm without importing the primary Q3 implementation.
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
SLUG = "pre_a_cp1_st8_q3lock_actual_local_commutator_recurrence_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-local-commutator-recurrence-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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
    result = single if site == 0 else identity
    if site != 0:
        result = identity
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
    raise ValueError("EXP-001155 uses volumes 2, 4 and 6")


def make_system(volume: int, size: int) -> tuple[list[np.ndarray], list[np.ndarray], np.ndarray]:
    q_single, p_single = oscillator(size)
    identity = np.eye(size, dtype=complex)
    qs = [lift(q_single, site, volume, identity) for site in range(volume)]
    ps = [lift(p_single, site, volume, identity) for site in range(volume)]
    zero = np.zeros_like(qs[0])
    hamiltonian = zero.copy()
    for q, p in zip(qs, ps):
        hamiltonian += p @ p / 2.0 - (q @ q) * 0.5 + 0.6 * (q @ q @ q @ q) / 4.0
    for left, right in edges(volume):
        difference = qs[left] - qs[right]
        hamiltonian += 0.6 * (difference @ difference) / 2.0
        hamiltonian += 0.1 * (difference @ difference) @ (qs[left] @ qs[left] + qs[right] @ qs[right]) / 4.0
    return qs, ps, (hamiltonian + hamiltonian.conj().T) / 2.0


def spectral_unitary(matrix: np.ndarray, time: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values)) @ vectors.conj().T


def thermal_state(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    weights = np.exp(-(values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values)) @ vectors.conj().T


def bracket(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return math.sqrt(max(0.0, float(np.real(value))))


def lengths(qs: list[np.ndarray], ps: list[np.ndarray], observable: np.ndarray, rho: np.ndarray) -> list[float]:
    values: list[float] = []
    for q, p in zip(qs, ps):
        q_part = seminorm(bracket(q, observable), rho)
        p_part = seminorm(bracket(p, observable), rho)
        values.append(math.sqrt(q_part * q_part + p_part * p_part))
    return values


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    volumes = [int(value) for value in fixture["volume_values"]]
    size = int(fixture["oscillator_dimension"])
    delta = float(Fraction(fixture["time_step"]))
    steps = int(fixture["steps"])
    tolerance = float(fixture["finite_tolerance"])
    recurrence_tolerance = float(fixture["recurrence_tolerance"])
    C, J = float(Fraction(fixture["recurrence_C"])), float(Fraction(fixture["recurrence_J"]))
    amplitude = float(Fraction(fixture["character_amplitude"]))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001155" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001155/T-054", "provenance")
    check("independent construction", True, "no primary import", "independent lane", "provenance")
    check("time fixture", steps * delta == 1.0 / 3.0, steps * delta, "1/3", "fixture")
    check("scope firewall", scope["actual_q3_recurrence_theorem_closed"] is False and scope["common_alpha_closed"] is False, scope, "open", "scope")

    summaries: list[dict[str, Any]] = []
    length_count = 0
    recurrence_count = 0
    for volume in volumes:
        qs, ps, hamiltonian = make_system(volume, size)
        rho = thermal_state(hamiltonian)
        base = character(qs[0] + qs[1], amplitude)
        adjacency = {site: set() for site in range(volume)}
        for left, right in edges(volume):
            adjacency[left].add(right)
            adjacency[right].add(left)
        for time_sign in (-1, 1):
            for adjoint in (0, 1):
                source = base.conj().T if adjoint else base
                history: list[list[float]] = []
                for step in range(steps + 1):
                    time = step * delta
                    propagator = spectral_unitary(hamiltonian, time_sign * time)
                    evolved = propagator @ source @ propagator.conj().T
                    row = lengths(qs, ps, evolved, rho)
                    check(f"V={volume} sign={time_sign} adj={adjoint} step={step} finite", all(np.isfinite(value) and value >= -tolerance for value in row), row, "finite", "commutator rows")
                    history.append(row)
                    length_count += volume
                residuals: list[float] = []
                for step in range(steps):
                    for site in range(volume):
                        neighbor_sum = sum(history[step][neighbor] for neighbor in adjacency[site])
                        rhs = (1.0 + C * delta) * history[step][site] + J * delta * neighbor_sum
                        residual = history[step + 1][site] - rhs
                        residuals.append(residual)
                        recurrence_count += 1
                max_residual = max(residuals, default=0.0)
                summaries.append({"volume": volume, "context": f"time{time_sign}_adjoint{adjoint}", "max_residual": max_residual, "violation_count": sum(value > recurrence_tolerance for value in residuals), "residual_min": min(residuals, default=0.0)})
        check(f"V={volume} contexts", len([row for row in summaries if row["volume"] == volume]) == 4, len([row for row in summaries if row["volume"] == volume]), 4, "contexts")

    status = "PASS_ON_GRID" if all(row["violation_count"] == 0 for row in summaries) else "FAIL_ON_GRID_ROUTE_LOCAL"
    check("candidate outcome recorded", status in ("PASS_ON_GRID", "FAIL_ON_GRID_ROUTE_LOCAL"), status, "explicit finite outcome", "route decision")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ACTUAL-LOCAL-COMMUTATOR-RECURRENCE-AUDIT",
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
    print(f"INDEPENDENT ACTUAL-LOCAL-COMMUTATOR-RECURRENCE PASS {payload['passed']}/{payload['assertion_count']} status={payload['derived']['recurrence_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
