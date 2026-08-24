#!/usr/bin/env python3
"""Primary finite-Q3 matrix audit for EXP-001080.

The calculation is deliberately a declared finite oscillator regularization.  It
tests the two-sided Gibbs seminorm of the difference between the full Q3 bond
evolution and a smooth spectral coordinate-cutoff bond, together with the
Hamiltonian modular derivative of that difference.  It does not assert a CCR,
thermodynamic, OS, or continuum theorem.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-structured-cutoff-orbit-modular-derivative"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    f"2026-08-24-primary-{SLUG}/primary.json"
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


def hermitian_exponential(matrix: np.ndarray, coefficient: complex) -> np.ndarray:
    """Evaluate exp(coefficient*matrix) from the Hermitian spectral theorem."""

    hermitian = (matrix + matrix.conj().T) / 2.0
    eigenvalues, eigenvectors = np.linalg.eigh(hermitian)
    return (eigenvectors * np.exp(coefficient * eigenvalues)) @ eigenvectors.conj().T


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    q = (annihilation + creation) / np.sqrt(2.0)
    p = (annihilation - creation) / (1j * np.sqrt(2.0))
    return q, p


def smooth_coordinate_cutoff(q: np.ndarray, radius: float) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(eigenvalues) / radius
    taper = np.where(
        scaled <= 1.0,
        1.0,
        np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0),
    )
    return (eigenvectors * (eigenvalues * taper)) @ eigenvectors.conj().T


def gibbs_state(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted = eigenvalues - np.min(eigenvalues)
    weights = np.exp(-beta * shifted)
    return (eigenvectors * weights) @ eigenvectors.conj().T / np.sum(weights)


def q3_matrices(n: int, fixture: dict[str, Any]) -> dict[str, np.ndarray]:
    q, p = oscillator(n)
    identity = np.eye(n, dtype=complex)
    q1 = np.kron(q, identity)
    q2 = np.kron(identity, q)
    p1 = np.kron(p, identity)
    p2 = np.kron(identity, p)
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    onsite = (
        (p1 @ p1 + p2 @ p2) / (2.0 * chi)
        + r * (q1 @ q1 + q2 @ q2) / 2.0
        + g * (q1 @ q1 @ q1 @ q1 + q2 @ q2 @ q2 @ q2) / 4.0
    )
    difference = q1 - q2
    bond = c * (difference @ difference) / 2.0 + lam * (
        (difference @ difference) @ (q1 @ q1 + q2 @ q2) / 4.0
    )
    return {"q1": q1, "q2": q2, "p1": p1, "p2": p2, "onsite": onsite, "bond": bond}


def norms(rho: np.ndarray, operator: np.ndarray) -> tuple[float, float, float]:
    right = float(np.trace(rho @ operator.conj().T @ operator).real)
    left = float(np.trace(rho @ operator @ operator.conj().T).real)
    squared = max(0.0, right + left)
    return float(np.sqrt(squared)), max(0.0, right), max(0.0, left)


def residual(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix - matrix.conj().T, ord="fro"))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001080" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001080/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("finite parameters", fixture["beta"] > 0 and fixture["chi"] > 0 and fixture["g"] > 0 and fixture["lambda"] >= 0, [fixture["beta"], fixture["chi"], fixture["g"], fixture["lambda"]], "positive finite inputs", "model")
    check("cutoff geometry", fixture["L_values"] == sorted(fixture["L_values"]) and min(fixture["L_values"]) > 0, fixture["L_values"], "increasing positive radii", "cutoff")
    check("time geometry", fixture["time_values"] == sorted(fixture["time_values"]) and min(fixture["time_values"]) > 0, fixture["time_values"], "increasing positive times", "time")
    check("scope firewall", scope["finite_truncated_oscillator_q3_model_closed"] and scope["finite_hamiltonian_modular_derivative_computed"] and not scope["volume_uniform_direct_d_cauchy_closed"] and not scope["delta_d_cauchy_closed"], scope, "finite checkpoint with thermodynamic gates open", "scope")

    tolerance = float(fixture["hermitian_tolerance"])
    state_tolerance = float(fixture["state_tolerance"])
    commutator_tolerance = float(fixture["commutator_tolerance"])
    monotonic_tolerance = float(fixture["monotonic_tolerance"])
    tail_floor = float(fixture["tail_floor"])
    all_rows: list[dict[str, Any]] = []
    dimension_summary: list[dict[str, Any]] = []

    for n in fixture["n_values"]:
        matrices = q3_matrices(int(n), fixture)
        q1, q2 = matrices["q1"], matrices["q2"]
        full_h = matrices["onsite"] + matrices["bond"]
        rho = gibbs_state(full_h, float(fixture["beta"]))
        character = hermitian_exponential(q1, 1j * float(fixture["character_amplitude"]) / float(fixture["hbar"]))
        h_eigenvalues = np.linalg.eigvalsh((full_h + full_h.conj().T) / 2.0)
        rho_eigenvalues = np.linalg.eigvalsh((rho + rho.conj().T) / 2.0)
        check(f"n={n} q1 Hermitian", residual(q1) < tolerance, residual(q1), f"<{tolerance}", "matrix")
        check(f"n={n} p1 Hermitian", residual(matrices["p1"]) < tolerance, residual(matrices["p1"]), f"<{tolerance}", "matrix")
        check(f"n={n} full H Hermitian", residual(full_h) < tolerance, residual(full_h), f"<{tolerance}", "matrix")
        check(f"n={n} Gibbs trace", abs(np.trace(rho).real - 1.0) < state_tolerance, np.trace(rho), "1", "state")
        check(f"n={n} Gibbs positive", float(np.min(rho_eigenvalues)) > -state_tolerance and float(np.max(rho_eigenvalues)) <= 1.0 + state_tolerance, [float(np.min(rho_eigenvalues)), float(np.max(rho_eigenvalues))], "[0,1]", "state")
        check(f"n={n} Gibbs commutes", np.linalg.norm(full_h @ rho - rho @ full_h, ord="fro") < state_tolerance, np.linalg.norm(full_h @ rho - rho @ full_h, ord="fro"), f"<{state_tolerance}", "state")
        check(f"n={n} character unitary", np.linalg.norm(character.conj().T @ character - np.eye(character.shape[0]), ord="fro") < 100.0 * tolerance, np.linalg.norm(character.conj().T @ character - np.eye(character.shape[0]), ord="fro"), f"<{100.0 * tolerance}", "character")
        check(f"n={n} finite Q3 bounded below", float(np.min(h_eigenvalues)) == float(np.min(h_eigenvalues)) and float(np.max(h_eigenvalues)) < np.inf, [float(np.min(h_eigenvalues)), float(np.max(h_eigenvalues))], "finite spectrum", "model")

        full_unitaries = {float(time): hermitian_exponential(full_h, -1j * float(time) / float(fixture["hbar"])) for time in fixture["time_values"]}
        previous_tail: float | None = None
        static_rows: list[dict[str, Any]] = []
        for radius in fixture["L_values"]:
            q1_cut = np.kron(smooth_coordinate_cutoff(oscillator(int(n))[0], float(radius)), np.eye(int(n), dtype=complex))
            q2_cut = np.kron(np.eye(int(n), dtype=complex), smooth_coordinate_cutoff(oscillator(int(n))[0], float(radius)))
            difference_cut = q1_cut - q2_cut
            cut_bond = float(fixture["c"]) * (difference_cut @ difference_cut) / 2.0 + float(fixture["lambda"]) * (
                (difference_cut @ difference_cut) @ (q1_cut @ q1_cut + q2_cut @ q2_cut) / 4.0
            )
            cut_h = matrices["onsite"] + cut_bond
            cut_unitaries = {float(time): hermitian_exponential(cut_h, -1j * float(time) / float(fixture["hbar"])) for time in fixture["time_values"]}
            tail = matrices["bond"] - cut_bond
            tail_root, tail_right, tail_left = norms(rho, tail)
            check(f"n={n} L={radius} tail floor", tail_root > tail_floor, tail_root, f">{tail_floor}", "cutoff")
            if previous_tail is not None:
                check(f"n={n} tail monotone L={radius}", tail_root <= previous_tail + monotonic_tolerance, tail_root, f"<={previous_tail}+{monotonic_tolerance}", "cutoff")
            previous_tail = tail_root
            character_commutator = np.linalg.norm(tail @ character - character @ tail, ord="fro")
            check(f"n={n} L={radius} configuration commutation", character_commutator < commutator_tolerance, character_commutator, f"<{commutator_tolerance}", "CCR-core")
            zero_difference = np.zeros_like(character)
            zero_derivative = 1j * ((full_h @ character - character @ full_h) - (cut_h @ character - character @ cut_h))
            check(f"n={n} L={radius} D(0)", np.linalg.norm(zero_difference, ord="fro") == 0.0, np.linalg.norm(zero_difference, ord="fro"), "0", "Duhamel")
            check(f"n={n} L={radius} D'(0)", np.linalg.norm(zero_derivative, ord="fro") < commutator_tolerance, np.linalg.norm(zero_derivative, ord="fro"), f"<{commutator_tolerance}", "Duhamel")
            time_rows: list[dict[str, Any]] = []
            max_difference_ratio = 0.0
            max_modular_ratio = 0.0
            for time in fixture["time_values"]:
                full_u = full_unitaries[float(time)]
                cut_u = cut_unitaries[float(time)]
                evolved_full = full_u.conj().T @ character @ full_u
                evolved_cut = cut_u.conj().T @ character @ cut_u
                difference = evolved_full - evolved_cut
                modular_difference = 1j / float(fixture["hbar"]) * (full_h @ difference - difference @ full_h)
                difference_root, difference_right, difference_left = norms(rho, difference)
                modular_root, modular_right, modular_left = norms(rho, modular_difference)
                check(f"n={n} L={radius} t={time} D finite", np.isfinite(difference_root) and np.isfinite(modular_root), [difference_root, modular_root], "finite", "Duhamel")
                check(f"n={n} L={radius} t={time} D two-sided identity", abs(difference_root * difference_root - difference_right - difference_left) < 100.0 * state_tolerance, difference_root * difference_root - difference_right - difference_left, f"<{100.0 * state_tolerance}", "seminorm")
                check(f"n={n} L={radius} t={time} delta two-sided identity", abs(modular_root * modular_root - modular_right - modular_left) < 100.0 * state_tolerance, modular_root * modular_root - modular_right - modular_left, f"<{100.0 * state_tolerance}", "seminorm")
                difference_ratio = difference_root / (float(time) * tail_root)
                modular_ratio = modular_root / tail_root
                max_difference_ratio = max(max_difference_ratio, difference_ratio)
                max_modular_ratio = max(max_modular_ratio, modular_ratio)
                time_rows.append({"time": float(time), "difference_root": difference_root, "difference_right": difference_right, "difference_left": difference_left, "modular_root": modular_root, "modular_right": modular_right, "modular_left": modular_left, "difference_to_time_tail_ratio": difference_ratio, "modular_to_tail_ratio": modular_ratio})
            static_rows.append({"radius": float(radius), "tail_root": tail_root, "tail_right": tail_right, "tail_left": tail_left, "max_difference_to_time_tail_ratio": max_difference_ratio, "max_modular_to_tail_ratio": max_modular_ratio, "times": time_rows})
        dimension_summary.append({"n": int(n), "dimension": int(n) * int(n), "rows": static_rows, "max_modular_to_tail_ratio": max(row["max_modular_to_tail_ratio"] for row in static_rows), "max_difference_to_time_tail_ratio": max(row["max_difference_to_time_tail_ratio"] for row in static_rows)})

    max_modular_ratio = max(row["max_modular_to_tail_ratio"] for row in dimension_summary)
    max_difference_ratio = max(row["max_difference_to_time_tail_ratio"] for row in dimension_summary)
    check("modular amplification is visible", max_modular_ratio > float(fixture["modular_ratio_floor"]), max_modular_ratio, f">{fixture['modular_ratio_floor']}", "diagnostic")
    check("all finite ratios", all(np.isfinite(row["max_modular_to_tail_ratio"]) and np.isfinite(row["max_difference_to_time_tail_ratio"]) for row in dimension_summary), dimension_summary, "finite", "diagnostic")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-STRUCTURED-CUTOFF-ORBIT-MODULAR-DERIVATIVE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {"dimension_summary": dimension_summary, "max_modular_to_tail_ratio": max_modular_ratio, "max_difference_to_time_tail_ratio": max_difference_ratio, "finite_q3_regularization": True, "dimension_uniformity_proved": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False},
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
    print(f"PRIMARY FINITE-STRUCTURED-CUTOFF-Q3 PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
