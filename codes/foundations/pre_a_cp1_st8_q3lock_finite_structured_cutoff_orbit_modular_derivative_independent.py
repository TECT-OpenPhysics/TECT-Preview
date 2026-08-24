#!/usr/bin/env python3
"""Independent numpy reconstruction of EXP-001080.

This lane intentionally rebuilds the oscillator, Q3 bond, smooth spectral
cutoff, Gibbs state, and two-sided roots without importing the primary lane.
It remains a finite regularized diagnostic rather than a continuum theorem.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-structured-cutoff-orbit-modular-derivative"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    f"2026-08-24-independent-{SLUG}/independent.json"
)


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


def spectral_exp(matrix: np.ndarray, coefficient: complex) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) * 0.5)
    diagonal = np.diag(np.exp(coefficient * values))
    return vectors @ diagonal @ vectors.conj().T


def oscillator_pair(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=np.complex128)
    for row in range(size - 1):
        lowering[row, row + 1] = np.sqrt(float(row + 1))
    raising = lowering.T.conj()
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def taper_coordinate(operator: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((operator + operator.conj().T) * 0.5)
    scaled = np.abs(values) / float(radius)
    coefficients = np.ones_like(scaled)
    high = scaled >= 2.0
    middle = (scaled > 1.0) & (scaled < 2.0)
    coefficients[high] = 0.0
    coefficients[middle] = 0.5 * (1.0 + np.cos(np.pi * (scaled[middle] - 1.0)))
    return vectors @ np.diag(values * coefficients) @ vectors.conj().T


def state_for(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) * 0.5)
    weights = np.exp(-float(beta) * (values - values.min()))
    return vectors @ np.diag(weights / weights.sum()) @ vectors.conj().T


def seminorm_parts(state: np.ndarray, operator: np.ndarray) -> tuple[float, float, float]:
    right = float(np.trace(state @ operator.conj().T @ operator).real)
    left = float(np.trace(state @ operator @ operator.conj().T).real)
    return float(np.sqrt(max(0.0, right + left))), max(0.0, right), max(0.0, left)


def build(size: int, values: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q, p = oscillator_pair(size)
    eye = np.eye(size, dtype=np.complex128)
    q_left, q_right = np.kron(q, eye), np.kron(eye, q)
    p_left, p_right = np.kron(p, eye), np.kron(eye, p)
    chi, r, g = float(values["chi"]), float(values["r"]), float(values["g"])
    c, lam = float(values["c"]), float(values["lambda"])
    onsite = (p_left @ p_left + p_right @ p_right) / (2.0 * chi)
    onsite += r * (q_left @ q_left + q_right @ q_right) / 2.0
    onsite += g * (q_left @ q_left @ q_left @ q_left + q_right @ q_right @ q_right @ q_right) / 4.0
    gap = q_left - q_right
    bond = c * (gap @ gap) / 2.0 + lam * (gap @ gap) @ (q_left @ q_left + q_right @ q_right) / 4.0
    return q_left, q_right, onsite, bond


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001080" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001080/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive model", fixture["beta"] > 0 and fixture["chi"] > 0 and fixture["g"] > 0 and fixture["lambda"] >= 0, [fixture["beta"], fixture["chi"], fixture["g"], fixture["lambda"]], "positive parameters", "model")
    check("scope firewall", scope["finite_truncated_oscillator_q3_model_closed"] and scope["finite_hamiltonian_modular_derivative_computed"] and not scope["volume_uniform_direct_d_cauchy_closed"] and not scope["delta_d_cauchy_closed"], scope, "finite only", "scope")

    matrix_tolerance = float(fixture["hermitian_tolerance"])
    state_tolerance = float(fixture["state_tolerance"])
    commutator_tolerance = float(fixture["commutator_tolerance"])
    monotonic_tolerance = float(fixture["monotonic_tolerance"])
    tail_floor = float(fixture["tail_floor"])
    summaries: list[dict[str, Any]] = []
    for size in fixture["n_values"]:
        q_left, q_right, onsite, bond = build(int(size), fixture)
        hamiltonian = onsite + bond
        state = state_for(hamiltonian, float(fixture["beta"]))
        character = spectral_exp(q_left, 1j * float(fixture["character_amplitude"]) / float(fixture["hbar"]))
        hermitian_error = float(np.linalg.norm(hamiltonian - hamiltonian.conj().T, ord="fro"))
        check(f"n={size} H Hermitian", hermitian_error < matrix_tolerance, hermitian_error, f"<{matrix_tolerance}", "matrix")
        trace_error = abs(float(np.trace(state).real) - 1.0)
        state_eigenvalues = np.linalg.eigvalsh((state + state.conj().T) * 0.5)
        check(f"n={size} state trace", trace_error < state_tolerance, trace_error, f"<{state_tolerance}", "state")
        check(f"n={size} state positive", float(state_eigenvalues.min()) > -state_tolerance, float(state_eigenvalues.min()), f">-{state_tolerance}", "state")
        check(f"n={size} state invariant", np.linalg.norm(hamiltonian @ state - state @ hamiltonian, ord="fro") < state_tolerance, np.linalg.norm(hamiltonian @ state - state @ hamiltonian, ord="fro"), f"<{state_tolerance}", "state")
        previous_tail: float | None = None
        radius_rows: list[dict[str, Any]] = []
        full_u = {float(time): spectral_exp(hamiltonian, -1j * float(time) / float(fixture["hbar"])) for time in fixture["time_values"]}
        for radius in fixture["L_values"]:
            q_left_cut = np.kron(taper_coordinate(oscillator_pair(int(size))[0], float(radius)), np.eye(int(size), dtype=np.complex128))
            q_right_cut = np.kron(np.eye(int(size), dtype=np.complex128), taper_coordinate(oscillator_pair(int(size))[0], float(radius)))
            cut_gap = q_left_cut - q_right_cut
            cut_bond = float(fixture["c"]) * (cut_gap @ cut_gap) / 2.0 + float(fixture["lambda"]) * (cut_gap @ cut_gap) @ (q_left_cut @ q_left_cut + q_right_cut @ q_right_cut) / 4.0
            cut_hamiltonian = onsite + cut_bond
            tail = bond - cut_bond
            tail_root, tail_right, tail_left = seminorm_parts(state, tail)
            check(f"n={size} L={radius} tail positive", tail_root > tail_floor, tail_root, f">{tail_floor}", "cutoff")
            if previous_tail is not None:
                check(f"n={size} L={radius} tail decreasing", tail_root <= previous_tail + monotonic_tolerance, tail_root, f"<={previous_tail}+{monotonic_tolerance}", "cutoff")
            previous_tail = tail_root
            check(f"n={size} L={radius} commutator", np.linalg.norm(tail @ character - character @ tail, ord="fro") < commutator_tolerance, np.linalg.norm(tail @ character - character @ tail, ord="fro"), f"<{commutator_tolerance}", "CCR-core")
            cut_u = {float(time): spectral_exp(cut_hamiltonian, -1j * float(time) / float(fixture["hbar"])) for time in fixture["time_values"]}
            time_rows: list[dict[str, Any]] = []
            max_difference_ratio = 0.0
            max_modular_ratio = 0.0
            for time in fixture["time_values"]:
                evolved_full = full_u[float(time)].conj().T @ character @ full_u[float(time)]
                evolved_cut = cut_u[float(time)].conj().T @ character @ cut_u[float(time)]
                difference = evolved_full - evolved_cut
                modular_difference = 1j / float(fixture["hbar"]) * (hamiltonian @ difference - difference @ hamiltonian)
                difference_root, difference_right, difference_left = seminorm_parts(state, difference)
                modular_root, modular_right, modular_left = seminorm_parts(state, modular_difference)
                check(f"n={size} L={radius} t={time} finite", np.isfinite(difference_root) and np.isfinite(modular_root), [difference_root, modular_root], "finite", "Duhamel")
                check(f"n={size} L={radius} t={time} two-sided D", abs(difference_root * difference_root - difference_right - difference_left) < 100.0 * state_tolerance, difference_root * difference_root - difference_right - difference_left, f"<{100.0 * state_tolerance}", "seminorm")
                check(f"n={size} L={radius} t={time} two-sided delta", abs(modular_root * modular_root - modular_right - modular_left) < 100.0 * state_tolerance, modular_root * modular_root - modular_right - modular_left, f"<{100.0 * state_tolerance}", "seminorm")
                difference_ratio = difference_root / (float(time) * tail_root)
                modular_ratio = modular_root / tail_root
                max_difference_ratio = max(max_difference_ratio, difference_ratio)
                max_modular_ratio = max(max_modular_ratio, modular_ratio)
                time_rows.append({"time": float(time), "difference_root": difference_root, "difference_right": difference_right, "difference_left": difference_left, "modular_root": modular_root, "modular_right": modular_right, "modular_left": modular_left, "difference_to_time_tail_ratio": difference_ratio, "modular_to_tail_ratio": modular_ratio})
            radius_rows.append({"radius": float(radius), "tail_root": tail_root, "tail_right": tail_right, "tail_left": tail_left, "max_difference_to_time_tail_ratio": max_difference_ratio, "max_modular_to_tail_ratio": max_modular_ratio, "times": time_rows})
        summaries.append({"n": int(size), "dimension": int(size) * int(size), "rows": radius_rows, "max_modular_to_tail_ratio": max(row["max_modular_to_tail_ratio"] for row in radius_rows), "max_difference_to_time_tail_ratio": max(row["max_difference_to_time_tail_ratio"] for row in radius_rows)})
    max_modular_ratio = max(row["max_modular_to_tail_ratio"] for row in summaries)
    max_difference_ratio = max(row["max_difference_to_time_tail_ratio"] for row in summaries)
    check("modular diagnostic", max_modular_ratio > float(fixture["modular_ratio_floor"]), max_modular_ratio, f">{fixture['modular_ratio_floor']}", "diagnostic")
    check("finite diagnostic ratios", all(np.isfinite(row["max_modular_to_tail_ratio"]) for row in summaries), summaries, "finite", "diagnostic")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-STRUCTURED-CUTOFF-ORBIT-MODULAR-DERIVATIVE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"dimension_summary": summaries, "max_modular_to_tail_ratio": max_modular_ratio, "max_difference_to_time_tail_ratio": max_difference_ratio, "finite_q3_regularization": True, "dimension_uniformity_proved": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False},
        "boundary": scope,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT FINITE-STRUCTURED-CUTOFF-Q3 PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
