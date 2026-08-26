#!/usr/bin/env python3
"""Non-importing independent lane for EXP-001187.

This file reconstructs the finite oscillator, Q3 Hamiltonian, Gibbs quarter
root, histories, and Schatten-4 envelope without importing the primary lane.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-sandwiched-holder-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


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


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        annihilation[index, index + 1] = math.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / math.sqrt(2.0), (annihilation - creation) / (1j * math.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    graphs = {2: [(0, 1)], 4: [(0, 1), (0, 2), (1, 3), (2, 3)], 6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]}
    if volume not in graphs:
        raise ValueError("declared finite fixture has volumes 2, 4, and 6 only")
    return graphs[volume]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    return float(fixture["c"]) * (difference @ difference) / 2.0 + float(fixture["lambda"]) * (difference @ difference) @ (left @ left + right @ right) / 4.0


def build_volume(volume: int, dimension: int, fixture: dict[str, Any], coordinate: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    bond_coordinate = q_single if coordinate is None else coordinate
    bond_ops = [embed(bond_coordinate, site, volume, identity) for site in range(volume)]
    onsite = [p @ p / (2.0 * float(fixture["chi"])) + float(fixture["r"]) * (q @ q) / 2.0 + float(fixture["g"]) * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): bond_term(bond_ops[left], bond_ops[right], fixture) for left, right in graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    hamiltonian = sum(onsite, zero) + sum(bonds.values(), zero)
    return q_ops, (hamiltonian + hamiltonian.conj().T) / 2.0, bonds


def cut_coordinate(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def schatten(matrix: np.ndarray, exponent: float) -> float:
    singular = np.linalg.svd(matrix, compute_uv=False)
    return float(np.power(np.sum(np.power(singular, exponent)), 1.0 / exponent))


def quarter_root(density: np.ndarray) -> tuple[np.ndarray, float]:
    values, vectors = np.linalg.eigh((density + density.conj().T) / 2.0)
    minimum = float(np.min(values))
    if minimum < -1.0e-8:
        raise ValueError(f"density is not positive: min={minimum}")
    return (vectors * np.power(np.maximum(values, 0.0), 0.25)) @ vectors.conj().T, minimum


def legs(matrix: np.ndarray, state_quarter: np.ndarray) -> tuple[float, float]:
    return schatten(state_quarter @ matrix, 4.0), schatten(matrix @ state_quarter, 4.0)


def sandwich(matrix: np.ndarray, state_quarter: np.ndarray) -> float:
    return float(np.linalg.norm(state_quarter @ matrix @ state_quarter, ord="fro"))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["holder_tolerance"])
    support_tolerance = float(fixture["support_tolerance"])
    floor = float(fixture["positivity_floor"])
    betas = [float(v) for v in fixture["beta_values"]]
    radii = [float(v) for v in fixture["radius_values"]]
    times = [float(v) for v in fixture["time_values"]]
    interpolation = [float(v) for v in fixture["interpolation_values"]]
    orientations = [int(v) for v in fixture["orientation_values"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001187" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001187/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_inverse_free_sandwiched_holder_closed"] and scope["finite_actual_q3_history_rows_closed"] and not scope["local_fourth_moment_uniform_closed"] and not scope["pre_a_closed"], scope, "finite Holder only; QFT gates open", "scope")

    history_rows: list[dict[str, Any]] = []
    support_rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        q_ops, hamiltonian, bonds = build_volume(volume, dimension, fixture)
        observable = character(q_ops[0] + q_ops[1], float(fixture["character_amplitude"]), float(fixture["hbar"]))
        energies, vectors = np.linalg.eigh(hamiltonian)
        shifted = energies - float(np.min(energies))
        for beta in betas:
            probabilities = np.exp(-beta * shifted)
            probabilities /= float(np.sum(probabilities))
            check(f"V={volume} beta={beta} Gibbs positivity", float(np.min(probabilities)) >= floor and np.isfinite(probabilities).all(), [float(np.min(probabilities)), float(np.max(probabilities))], f">={floor}", "state")
            density = (vectors * probabilities) @ vectors.conj().T
            state_quarter, density_min = quarter_root(density)
            check(f"V={volume} beta={beta} quarter root", density_min >= -support_tolerance and np.isfinite(state_quarter).all(), density_min, f">=-{support_tolerance}", "state")
            for radius in radii:
                cut = cut_coordinate(oscillator(dimension)[0], radius)
                _, _, cut_bonds = build_volume(volume, dimension, fixture, cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                tail = (tail + tail.conj().T) / 2.0
                source_commutator = operator_norm(commutator(tail, observable))
                disjoint = [bonds[edge] - cut_bonds[edge] for edge in bonds if set(edge).isdisjoint(set(fixture["observable_support"]))]
                disjoint_tail = sum(disjoint, zero)
                disjoint_commutator = operator_norm(commutator(disjoint_tail, observable))
                check(f"V={volume} beta={beta} L={radius} source support", source_commutator <= support_tolerance, source_commutator, f"<={support_tolerance}", "support")
                check(f"V={volume} beta={beta} L={radius} disjoint support", disjoint_commutator <= support_tolerance, disjoint_commutator, f"<={support_tolerance}", "support")
                support_rows.append({"volume": volume, "beta": beta, "radius": radius, "source_commutator": source_commutator, "disjoint_commutator": disjoint_commutator})
                tail_left, tail_right = legs(tail, state_quarter)
                for orientation in orientations:
                    for s_value in interpolation:
                        evolved = hamiltonian + orientation * s_value * tail
                        for time in times:
                            history = unitary(evolved, time, float(fixture["hbar"])) @ observable @ unitary(evolved, time, float(fixture["hbar"])).conj().T
                            adjoint_history = history.conj().T
                            current = commutator(tail, history)
                            current_star = commutator(tail, adjoint_history)
                            history_left, history_right = legs(history, state_quarter)
                            star_left, star_right = legs(adjoint_history, state_quarter)
                            bound = tail_left * history_right + history_left * tail_right
                            star_bound = tail_left * star_right + star_left * tail_right
                            lhs, star_lhs = sandwich(current, state_quarter), sandwich(current_star, state_quarter)
                            check_name = f"V={volume} beta={beta} L={radius} sign={orientation} s={s_value} t={time} Holder"
                            check(check_name, lhs <= bound + tolerance * (1.0 + bound) and star_lhs <= star_bound + tolerance * (1.0 + star_bound), [lhs, bound, star_lhs, star_bound], "two-sided lhs<=Holder envelope", "Schatten Holder")
                            check(check_name + " finite", all(np.isfinite(value) and value >= 0.0 for value in [lhs, bound, star_lhs, star_bound, tail_left, tail_right, history_left, history_right, star_left, star_right]), "finite nonnegative", "finite nonnegative", "Schatten Holder")
                            history_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "orientation": orientation, "interpolation": s_value, "time": time, "lhs": lhs, "bound": bound, "ratio": lhs / max(bound, np.finfo(float).tiny), "adjoint_lhs": star_lhs, "adjoint_bound": star_bound, "adjoint_ratio": star_lhs / max(star_bound, np.finfo(float).tiny), "tail_l4_left": tail_left, "tail_l4_right": tail_right})

    expected_history = len(fixture["scenarios"]) * len(betas) * len(radii) * len(orientations) * len(interpolation) * len(times)
    check("history coverage", len(history_rows) == expected_history, len(history_rows), expected_history, "coverage")
    check("support coverage", len(support_rows) == len(fixture["scenarios"]) * len(betas) * len(radii), len(support_rows), len(fixture["scenarios"]) * len(betas) * len(radii), "coverage")
    check("envelope residual", all(row["lhs"] <= row["bound"] + tolerance * (1.0 + row["bound"]) and row["adjoint_lhs"] <= row["adjoint_bound"] + tolerance * (1.0 + row["adjoint_bound"]) for row in history_rows), "all rows", "finite tolerance", "Schatten Holder")
    check("support residual", all(row["source_commutator"] <= support_tolerance and row["disjoint_commutator"] <= support_tolerance for row in support_rows), "all rows", "finite tolerance", "support")
    summary_rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        for beta in betas:
            members = [row for row in history_rows if row["volume"] == volume and row["beta"] == beta]
            summary_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "max_lhs": max(row["lhs"] for row in members), "max_bound": max(row["bound"] for row in members), "max_ratio": max(row["ratio"] for row in members), "max_adjoint_lhs": max(row["adjoint_lhs"] for row in members), "max_adjoint_bound": max(row["adjoint_bound"] for row in members), "max_adjoint_ratio": max(row["adjoint_ratio"] for row in members), "max_tail_l4_left": max(row["tail_l4_left"] for row in members), "max_tail_l4_right": max(row["tail_l4_right"] for row in members)})
    check("summary coverage", len(summary_rows) == len(fixture["scenarios"]) * len(betas), len(summary_rows), len(fixture["scenarios"]) * len(betas), "coverage")
    check("summary finite", all(np.isfinite(row["max_bound"]) and row["max_bound"] >= 0.0 for row in summary_rows), [row["max_bound"] for row in summary_rows], "finite nonnegative", "scaling")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SANDWICHED-HOLDER-ENVELOPE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"history_rows": history_rows, "support_rows": support_rows, "summary_rows": summary_rows, "max_ratio": max(row["ratio"] for row in history_rows), "max_adjoint_ratio": max(row["adjoint_ratio"] for row in history_rows), "finite_inverse_free_sandwiched_holder_closed": True, "finite_actual_q3_history_rows_closed": True, "finite_two_orientation_rows_closed": True, "local_fourth_moment_uniform_closed": False, "source_volume_cutoff_beta_uniform_closed": False, "common_core_closed": False, "qft_promoted": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-SANDWICHED-HOLDER-ENVELOPE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
