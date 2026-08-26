#!/usr/bin/env python3
"""Primary finite-Q3 inverse-free sandwiched Schatten-Holder audit (EXP-001187).

For a finite Gibbs density rho and S=rho**(1/4), the exact finite
factorisation

    S [W,A] S = (S W)(A S) - (S A)(W S)

and Schatten Holder give a two-sided state-norm envelope without forming an
inverse Gibbs power.  The rows are a finite Q3 diagnostic; they do not assert
that the four Schatten-4 factors are uniform on an unbounded common core.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-sandwiched-holder-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"

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


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def positive_power(matrix: np.ndarray, exponent: float) -> tuple[np.ndarray, float]:
    hermitian = (matrix + matrix.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    minimum = float(np.min(values))
    if minimum < -1.0e-8:
        raise ValueError(f"state is not positive: min={minimum}")
    clipped = np.maximum(values, 0.0)
    return (vectors * np.power(clipped, exponent)) @ vectors.conj().T, minimum


def schatten(matrix: np.ndarray, exponent: float) -> float:
    singular = np.linalg.svd(matrix, compute_uv=False)
    return float(np.power(np.sum(np.power(singular, exponent)), 1.0 / exponent))


def holder_legs(matrix: np.ndarray, state_quarter: np.ndarray) -> tuple[float, float]:
    return schatten(state_quarter @ matrix, 4.0), schatten(matrix @ state_quarter, 4.0)


def sandwich_two(matrix: np.ndarray, state_quarter: np.ndarray) -> float:
    return float(np.linalg.norm(state_quarter @ matrix @ state_quarter, ord="fro"))


def holder_envelope(left: np.ndarray, right: np.ndarray, state_quarter: np.ndarray) -> tuple[float, dict[str, float]]:
    left_left, left_right = holder_legs(left, state_quarter)
    right_left, right_right = holder_legs(right, state_quarter)
    first = left_left * right_right
    second = right_left * left_right
    return first + second, {
        "left_left": left_left,
        "left_right": left_right,
        "right_left": right_left,
        "right_right": right_right,
        "first_product": first,
        "second_product": second,
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["holder_tolerance"])
    support_tolerance = float(fixture["support_tolerance"])
    positivity_floor = float(fixture["positivity_floor"])
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    interpolation = [float(value) for value in fixture["interpolation_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    scenarios = fixture["scenarios"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001187" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001187/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_inverse_free_sandwiched_holder_closed"] and scope["finite_actual_q3_history_rows_closed"] and not scope["local_fourth_moment_uniform_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite Holder only; QFT gates open", "scope")
    check("fixture coverage", len(scenarios) == 3 and betas == [0.125, 0.25, 0.5, 1.0, 2.0] and radii == [0.5, 1.0] and orientations == [-1, 1], [len(scenarios), betas, radii, orientations], "declared grid", "fixture")

    history_rows: list[dict[str, Any]] = []
    support_rows: list[dict[str, Any]] = []
    q_cache: dict[int, np.ndarray] = {}
    for scenario in scenarios:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        q_single = q_cache.setdefault(dimension, q3.oscillator(dimension)[0])
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        observable = q3.character(q_ops[0] + q_ops[1], float(fixture["character_amplitude"]), float(fixture["hbar"]))
        energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
        shifted = energies - float(np.min(energies))
        for beta in betas:
            probabilities = np.exp(-beta * shifted)
            probabilities /= float(np.sum(probabilities))
            check(f"V={volume} beta={beta} Gibbs positivity", float(np.min(probabilities)) >= positivity_floor and np.isfinite(probabilities).all(), [float(np.min(probabilities)), float(np.max(probabilities))], f">={positivity_floor}", "state")
            rho = (vectors * probabilities) @ vectors.conj().T
            state_quarter, rho_min = positive_power(rho, 0.25)
            check(f"V={volume} beta={beta} quarter root", rho_min >= -support_tolerance and np.isfinite(state_quarter).all(), rho_min, f">=-{support_tolerance}", "state")
            for radius in radii:
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                tail = (tail + tail.conj().T) / 2.0
                source_commutator = q3.operator_norm(q3.commutator(tail, observable))
                disjoint = [bonds[edge] - cut_bonds[edge] for edge in bonds if set(edge).isdisjoint(set(fixture["observable_support"]))]
                disjoint_tail = sum(disjoint, zero)
                disjoint_commutator = q3.operator_norm(q3.commutator(disjoint_tail, observable))
                check(f"V={volume} beta={beta} L={radius} source support", source_commutator <= support_tolerance, source_commutator, f"<={support_tolerance}", "support")
                check(f"V={volume} beta={beta} L={radius} disjoint support", disjoint_commutator <= support_tolerance, disjoint_commutator, f"<={support_tolerance}", "support")
                support_rows.append({"volume": volume, "beta": beta, "radius": radius, "source_commutator": source_commutator, "disjoint_commutator": disjoint_commutator})
                tail_left, tail_right = holder_legs(tail, state_quarter)
                for orientation in orientations:
                    for s_value in interpolation:
                        evolved = hamiltonian + orientation * s_value * tail
                        for time in times:
                            propagator = unitary(evolved, time, float(fixture["hbar"]))
                            history = propagator @ observable @ propagator.conj().T
                            commutator = q3.commutator(tail, history)
                            bound, legs = holder_envelope(tail, history, state_quarter)
                            lhs = sandwich_two(commutator, state_quarter)
                            adjoint_commutator = q3.commutator(tail, history.conj().T)
                            adjoint_bound, adjoint_legs = holder_envelope(tail, history.conj().T, state_quarter)
                            adjoint_lhs = sandwich_two(adjoint_commutator, state_quarter)
                            check_name = f"V={volume} beta={beta} L={radius} sign={orientation} s={s_value} t={time} Holder"
                            check(check_name, lhs <= bound + tolerance * (1.0 + bound) and adjoint_lhs <= adjoint_bound + tolerance * (1.0 + adjoint_bound), [lhs, bound, adjoint_lhs, adjoint_bound], "two-sided lhs<=Holder envelope", "Schatten Holder")
                            check(check_name + " finite", all(np.isfinite(value) and value >= 0.0 for value in [lhs, bound, adjoint_lhs, adjoint_bound, *legs.values(), *adjoint_legs.values()]), "finite nonnegative", "finite nonnegative", "Schatten Holder")
                            history_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "orientation": orientation, "interpolation": s_value, "time": time, "lhs": lhs, "bound": bound, "ratio": lhs / max(bound, np.finfo(float).tiny), "adjoint_lhs": adjoint_lhs, "adjoint_bound": adjoint_bound, "adjoint_ratio": adjoint_lhs / max(adjoint_bound, np.finfo(float).tiny), "tail_l4_left": tail_left, "tail_l4_right": tail_right, "legs": legs, "adjoint_legs": adjoint_legs})

    expected_history = sum(1 for _ in scenarios) * len(betas) * len(radii) * len(orientations) * len(interpolation) * len(times)
    check("history coverage", len(history_rows) == expected_history, len(history_rows), expected_history, "coverage")
    check("support coverage", len(support_rows) == len(scenarios) * len(betas) * len(radii), len(support_rows), len(scenarios) * len(betas) * len(radii), "coverage")
    check("envelope residual", all(row["lhs"] <= row["bound"] + tolerance * (1.0 + row["bound"]) and row["adjoint_lhs"] <= row["adjoint_bound"] + tolerance * (1.0 + row["adjoint_bound"]) for row in history_rows), "all rows", "finite tolerance", "Schatten Holder")
    check("support residual", all(row["source_commutator"] <= support_tolerance and row["disjoint_commutator"] <= support_tolerance for row in support_rows), "all rows", "finite tolerance", "support")

    summary_rows: list[dict[str, Any]] = []
    for volume in [int(item["volume"]) for item in scenarios]:
        dimension = next(int(item["oscillator_dimension"]) for item in scenarios if int(item["volume"]) == volume)
        for beta in betas:
            members = [row for row in history_rows if row["volume"] == volume and row["beta"] == beta]
            summary_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "max_lhs": max(row["lhs"] for row in members), "max_bound": max(row["bound"] for row in members), "max_ratio": max(row["ratio"] for row in members), "max_adjoint_lhs": max(row["adjoint_lhs"] for row in members), "max_adjoint_bound": max(row["adjoint_bound"] for row in members), "max_adjoint_ratio": max(row["adjoint_ratio"] for row in members), "max_tail_l4_left": max(row["tail_l4_left"] for row in members), "max_tail_l4_right": max(row["tail_l4_right"] for row in members)})
    check("summary coverage", len(summary_rows) == len(scenarios) * len(betas), len(summary_rows), len(scenarios) * len(betas), "coverage")
    maxima = [row["max_bound"] for row in summary_rows]
    check("summary finite", all(np.isfinite(value) and value >= 0.0 for value in maxima), maxima, "finite nonnegative", "scaling")
    volume_maxima = [max(row["max_bound"] for row in summary_rows if row["volume"] == volume) for volume in [int(item["volume"]) for item in scenarios]]
    beta_maxima = [max(row["max_bound"] for row in summary_rows if row["beta"] == beta) for beta in betas]
    check("uniformity remains undecided", scope["local_fourth_moment_uniform_closed"] is False and scope["source_volume_cutoff_beta_uniform_closed"] is False, scope, "false", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SANDWICHED-HOLDER-ENVELOPE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"history_rows": history_rows, "support_rows": support_rows, "summary_rows": summary_rows, "volume_max_bound": volume_maxima, "beta_max_bound": beta_maxima, "max_ratio": max(row["ratio"] for row in history_rows), "max_adjoint_ratio": max(row["adjoint_ratio"] for row in history_rows), "finite_inverse_free_sandwiched_holder_closed": True, "finite_actual_q3_history_rows_closed": True, "finite_two_orientation_rows_closed": True, "local_fourth_moment_uniform_closed": False, "source_volume_cutoff_beta_uniform_closed": False, "common_core_closed": False, "qft_promoted": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-SANDWICHED-HOLDER-ENVELOPE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
