#!/usr/bin/env python3
"""Non-importing independent lane for EXP-001188."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-unitary-tail-holder-corollary"
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
    a = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        a[index, index + 1] = math.sqrt(index + 1.0)
    return (a + a.conj().T) / math.sqrt(2.0), (a - a.conj().T) / (1j * math.sqrt(2.0))


def edges(volume: int) -> list[tuple[int, int]]:
    values = {2: [(0, 1)], 4: [(0, 1), (0, 2), (1, 3), (2, 3)], 6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]}
    if volume not in values:
        raise ValueError("finite fixture volume not declared")
    return values[volume]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    d = left - right
    return float(fixture["c"]) * (d @ d) / 2.0 + float(fixture["lambda"]) * (d @ d) @ (left @ left + right @ right) / 4.0


def build(volume: int, dimension: int, fixture: dict[str, Any], coordinate: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q, p = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p, site, volume, identity) for site in range(volume)]
    coordinate = q if coordinate is None else coordinate
    b_ops = [embed(coordinate, site, volume, identity) for site in range(volume)]
    onsite = [p_i @ p_i / (2.0 * float(fixture["chi"])) + float(fixture["r"]) * (q_i @ q_i) / 2.0 + float(fixture["g"]) * (q_i @ q_i @ q_i @ q_i) / 4.0 for q_i, p_i in zip(q_ops, p_ops)]
    bonds = {(u, v): bond(b_ops[u], b_ops[v], fixture) for u, v in edges(volume)}
    zero = np.zeros_like(q_ops[0])
    h = sum(onsite, zero) + sum(bonds.values(), zero)
    return q_ops, (h + h.conj().T) / 2.0, bonds


def cut(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def evolve(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def comm(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def opnorm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def schatten4(matrix: np.ndarray) -> float:
    values = np.linalg.svd(matrix, compute_uv=False)
    return float(np.power(np.sum(values**4), 0.25))


def root_quarter(density: np.ndarray) -> tuple[np.ndarray, float]:
    values, vectors = np.linalg.eigh((density + density.conj().T) / 2.0)
    minimum = float(np.min(values))
    if minimum < -1.0e-8:
        raise ValueError(f"negative density eigenvalue {minimum}")
    return (vectors * np.power(np.maximum(values, 0.0), 0.25)) @ vectors.conj().T, minimum


def sandwich(matrix: np.ndarray, root: np.ndarray) -> float:
    return float(np.linalg.norm(root @ matrix @ root, ord="fro"))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    holder_tolerance = float(fixture["holder_tolerance"])
    support_tolerance = float(fixture["support_tolerance"])
    unitary_tolerance = float(fixture["unitary_tolerance"])
    floor = float(fixture["positivity_floor"])
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    interpolation = [float(value) for value in fixture["interpolation_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001188" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001188/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_unitary_history_holder_corollary_closed"] and scope["history_side_l4_uniformity_closed"] and not scope["tail_fourth_moment_uniform_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite unitary corollary; QFT gates open", "scope")

    history_rows: list[dict[str, Any]] = []
    support_rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        q_ops, hamiltonian, full_bonds = build(volume, dimension, fixture)
        observable = character(q_ops[0] + q_ops[1], float(fixture["character_amplitude"]), float(fixture["hbar"]))
        energies, vectors = np.linalg.eigh(hamiltonian)
        shifted = energies - float(np.min(energies))
        for beta in betas:
            probabilities = np.exp(-beta * shifted)
            probabilities /= float(np.sum(probabilities))
            check(f"V={volume} beta={beta} Gibbs positivity", float(np.min(probabilities)) >= floor and np.isfinite(probabilities).all(), [float(np.min(probabilities)), float(np.max(probabilities))], f">={floor}", "state")
            density = (vectors * probabilities) @ vectors.conj().T
            root, density_min = root_quarter(density)
            state_four = schatten4(root)
            check(f"V={volume} beta={beta} normalized quarter root", density_min >= -unitary_tolerance and abs(state_four - 1.0) <= unitary_tolerance * 10.0, [density_min, state_four], "root finite; ||S||_4=1", "state")
            for radius in radii:
                coordinate = cut(oscillator(dimension)[0], radius)
                _, _, cut_bonds = build(volume, dimension, fixture, coordinate)
                zero = np.zeros_like(hamiltonian)
                tail = sum((full_bonds[edge] - cut_bonds[edge] for edge in full_bonds), zero)
                tail = (tail + tail.conj().T) / 2.0
                tail_left, tail_right = schatten4(root @ tail), schatten4(tail @ root)
                check(f"V={volume} beta={beta} L={radius} tail leg symmetry", abs(tail_left - tail_right) <= holder_tolerance * (1.0 + tail_left + tail_right), [tail_left, tail_right], "equal within tolerance", "tail")
                source_commutator = opnorm(comm(tail, observable))
                disjoint = [full_bonds[edge] - cut_bonds[edge] for edge in full_bonds if set(edge).isdisjoint(set(fixture["observable_support"]))]
                disjoint_tail = sum(disjoint, zero)
                disjoint_commutator = opnorm(comm(disjoint_tail, observable))
                check(f"V={volume} beta={beta} L={radius} source support", source_commutator <= support_tolerance, source_commutator, f"<={support_tolerance}", "support")
                check(f"V={volume} beta={beta} L={radius} disjoint support", disjoint_commutator <= support_tolerance, disjoint_commutator, f"<={support_tolerance}", "support")
                support_rows.append({"volume": volume, "beta": beta, "radius": radius, "source_commutator": source_commutator, "disjoint_commutator": disjoint_commutator})
                for orientation in orientations:
                    for s_value in interpolation:
                        evolved = hamiltonian + orientation * s_value * tail
                        for time in times:
                            propagator = evolve(evolved, time, float(fixture["hbar"]))
                            history = propagator @ observable @ propagator.conj().T
                            history_star = history.conj().T
                            residual = max(opnorm(history.conj().T @ history - np.eye(history.shape[0])), opnorm(history @ history.conj().T - np.eye(history.shape[0])))
                            history_left, history_right = schatten4(root @ history), schatten4(history @ root)
                            star_left, star_right = schatten4(root @ history_star), schatten4(history_star @ root)
                            check_name = f"V={volume} beta={beta} L={radius} sign={orientation} s={s_value} t={time} unitary history"
                            check(check_name, residual <= unitary_tolerance and history_left <= state_four + unitary_tolerance and history_right <= state_four + unitary_tolerance and star_left <= state_four + unitary_tolerance and star_right <= state_four + unitary_tolerance, [residual, history_left, history_right, star_left, star_right], "unitary residual and four history legs bounded", "unitary")
                            lhs = sandwich(comm(tail, history), root)
                            lhs_star = sandwich(comm(tail, history_star), root)
                            general_bound = tail_left * history_right + history_left * tail_right
                            general_bound_star = tail_left * star_right + star_left * tail_right
                            reduced_bound = 2.0 * tail_left * state_four
                            check(check_name + " Holder corollary", lhs <= reduced_bound + holder_tolerance * (1.0 + reduced_bound) and lhs_star <= reduced_bound + holder_tolerance * (1.0 + reduced_bound) and lhs <= general_bound + holder_tolerance * (1.0 + general_bound) and lhs_star <= general_bound_star + holder_tolerance * (1.0 + general_bound_star), [lhs, reduced_bound, general_bound, lhs_star, general_bound_star], "lhs<=2*tail fourth leg", "Schatten Holder")
                            history_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "orientation": orientation, "interpolation": s_value, "time": time, "unitary_residual": residual, "tail_l4_left": tail_left, "tail_l4_right": tail_right, "history_l4_left": history_left, "history_l4_right": history_right, "adjoint_history_l4_left": star_left, "adjoint_history_l4_right": star_right, "lhs": lhs, "bound": reduced_bound, "general_bound": general_bound, "ratio": lhs / max(reduced_bound, np.finfo(float).tiny), "adjoint_lhs": lhs_star, "adjoint_bound": reduced_bound, "adjoint_general_bound": general_bound_star, "adjoint_ratio": lhs_star / max(reduced_bound, np.finfo(float).tiny)})

    expected_history = len(fixture["scenarios"]) * len(betas) * len(radii) * len(orientations) * len(interpolation) * len(times)
    check("history coverage", len(history_rows) == expected_history, len(history_rows), expected_history, "coverage")
    check("support coverage", len(support_rows) == len(fixture["scenarios"]) * len(betas) * len(radii), len(support_rows), len(fixture["scenarios"]) * len(betas) * len(radii), "coverage")
    check("corollary residual", all(row["lhs"] <= row["bound"] + holder_tolerance * (1.0 + row["bound"]) and row["adjoint_lhs"] <= row["adjoint_bound"] + holder_tolerance * (1.0 + row["adjoint_bound"]) for row in history_rows), "all rows", "finite tolerance", "Schatten Holder")
    check("support residual", all(row["source_commutator"] <= support_tolerance and row["disjoint_commutator"] <= support_tolerance for row in support_rows), "all rows", "finite tolerance", "support")
    summary_rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        for beta in betas:
            members = [row for row in history_rows if row["volume"] == volume and row["beta"] == beta]
            summary_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "max_tail_l4_left": max(row["tail_l4_left"] for row in members), "max_tail_l4_right": max(row["tail_l4_right"] for row in members), "max_history_l4_left": max(row["history_l4_left"] for row in members), "max_history_l4_right": max(row["history_l4_right"] for row in members), "max_adjoint_history_l4_left": max(row["adjoint_history_l4_left"] for row in members), "max_adjoint_history_l4_right": max(row["adjoint_history_l4_right"] for row in members), "max_lhs": max(row["lhs"] for row in members), "max_bound": max(row["bound"] for row in members), "max_ratio": max(row["ratio"] for row in members), "max_unitary_residual": max(row["unitary_residual"] for row in members)})
    check("summary coverage", len(summary_rows) == len(fixture["scenarios"]) * len(betas), len(summary_rows), len(fixture["scenarios"]) * len(betas), "coverage")
    check("history-side uniformity", all(row["max_history_l4_left"] <= 1.0 + unitary_tolerance * 10.0 and row["max_history_l4_right"] <= 1.0 + unitary_tolerance * 10.0 and row["max_adjoint_history_l4_left"] <= 1.0 + unitary_tolerance * 10.0 and row["max_adjoint_history_l4_right"] <= 1.0 + unitary_tolerance * 10.0 for row in summary_rows), [row["max_history_l4_left"] for row in summary_rows], "<=1", "unitary")
    check("tail diagnostic finite", all(np.isfinite(row["max_tail_l4_left"]) and row["max_tail_l4_left"] >= 0.0 for row in summary_rows), [row["max_tail_l4_left"] for row in summary_rows], "finite nonnegative", "tail")
    check("uniformity remains open", scope["tail_fourth_moment_uniform_closed"] is False and scope["source_volume_cutoff_beta_uniform_closed"] is False, scope, "false", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-UNITARY-TAIL-HOLDER-COROLLARY", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"history_rows": history_rows, "support_rows": support_rows, "summary_rows": summary_rows, "max_ratio": max(row["ratio"] for row in history_rows), "max_adjoint_ratio": max(row["adjoint_ratio"] for row in history_rows), "max_tail_l4": max(row["tail_l4_left"] for row in history_rows), "finite_unitary_history_holder_corollary_closed": True, "finite_tail_leg_symmetry_closed": True, "history_side_l4_uniformity_closed": True, "tail_fourth_moment_uniform_closed": False, "source_volume_cutoff_beta_uniform_closed": False, "common_core_closed": False, "qft_promoted": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-UNITARY-TAIL-HOLDER-COROLLARY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
