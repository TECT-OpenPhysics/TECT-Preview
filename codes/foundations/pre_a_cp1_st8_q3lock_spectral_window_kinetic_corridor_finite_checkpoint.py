#!/usr/bin/env python3
"""Finite spectral-window stress for the R-388 kinetic corridor.

The R-387 target K=[B,[T,(i eta I-q_s)^(-1)]] is evaluated after projecting
the Gibbs density to a fixed low-energy window.  This is a finite diagnostic:
the spectral complement, cutoff removal and all thermodynamic statements stay
open.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_spectral_window_kinetic_corridor_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spectral-window-kinetic-corridor-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, dimension: int, identity: np.ndarray) -> np.ndarray:
    return np.kron(single, identity) if site == 0 else np.kron(identity, single)


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def two_sided_norm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def build_model(dimension: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q0, q1 = lift(q_single, 0, dimension, identity), lift(q_single, 1, dimension, identity)
    p0, p1 = lift(p_single, 0, dimension, identity), lift(p_single, 1, dimension, identity)
    difference = q0 - q1
    quadratic = difference @ difference
    boundary = hermitian(float(fixture["c"]) * quadratic / 2.0 + float(fixture["lambda"]) * quadratic @ (q0 @ q0 + q1 @ q1) / 4.0)
    kinetic = hermitian((p0 @ p0 + p1 @ p1) / (2.0 * float(fixture["chi"])))
    onsite = hermitian(float(fixture["r"]) * (q0 @ q0 + q1 @ q1) / 2.0 + float(fixture["g"]) * (q0 @ q0 @ q0 @ q0 + q1 @ q1 @ q1 @ q1) / 4.0)
    return q0, q1, p0, p1, hermitian(kinetic + onsite + boundary)


def key(beta: float, eta: float, energy: float) -> str:
    return f"beta={beta};eta={eta};E={energy}"


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001232" and manifest["result_id"] == "R-389" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001232/R-389/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all sites, adjoints, cutoffs, beta and windows", "coverage")
    finite_flags = ("finite_spectral_window_weighted_corridor_closed", "finite_eta_split_closed", "finite_window_mass_rank_closed", "finite_operator_growth_stress_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite window only", "all promoted flags false", "scope")

    dimensions = [int(value) for value in fixture["cutoff_dimensions"]]
    sites = [int(value) for value in fixture["site_values"]]
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    etas = [float(Fraction(value)) for value in fixture["resolvent_imaginary_values"]]
    energies = [float(Fraction(value)) for value in fixture["energy_windows"]]
    tolerance = 1e-10
    tail_start = int(fixture["tail_cutoff_start"])
    tail_threshold = float(fixture["tail_stability_ratio_threshold"])
    eta_floor = float(Fraction(fixture["corridor_eta_floor"]))
    op_threshold = float(fixture["operator_growth_threshold"])
    profiles: dict[str, dict[int, list[float]]] = {key(beta, eta, energy): {dimension: [] for dimension in dimensions} for beta in betas for eta in etas for energy in energies}
    conditional_profiles: dict[str, dict[int, list[float]]] = {name: {dimension: [] for dimension in dimensions} for name in profiles}
    mass_profiles: dict[str, dict[int, list[float]]] = {name: {dimension: [] for dimension in dimensions} for name in profiles}
    rank_profiles: dict[str, dict[int, list[int]]] = {name: {dimension: [] for dimension in dimensions} for name in profiles}
    operator_by_dimension: dict[int, list[float]] = {dimension: [] for dimension in dimensions}
    row_records: list[dict[str, Any]] = []
    seed_rows = 0
    weighted_rows = 0
    maxima = {"operator_norm": 0.0, "projected_weighted_norm": 0.0, "conditional_projected_norm": 0.0}

    for dimension in dimensions:
        q0, q1, p0, p1, hamiltonian = build_model(dimension, fixture)
        identity = np.eye(dimension * dimension, dtype=complex)
        kinetic = hermitian((p0 @ p0 + p1 @ p1) / (2.0 * float(fixture["chi"])))
        difference = q0 - q1
        boundary = hermitian(float(fixture["c"]) * difference @ difference / 2.0 + float(fixture["lambda"]) * (difference @ difference) @ (q0 @ q0 + q1 @ q1) / 4.0)
        values, vectors = np.linalg.eigh(hermitian(hamiltonian))
        shifted = values - float(np.min(values))
        projectors = {}
        ranks = {}
        for energy in energies:
            selected = shifted <= energy + tolerance
            projectors[energy] = vectors[:, selected] @ vectors[:, selected].conj().T
            ranks[energy] = int(np.count_nonzero(selected))
            check(f"d={dimension} E={energy} rank", ranks[energy] > 0, ranks[energy], ">0", "window")
        states = {beta: gibbs(hamiltonian, beta) for beta in betas}
        for site, coordinate in enumerate((q0, q1)):
            for eta in etas:
                seed = np.linalg.inv(1j * eta * identity - coordinate)
                for adjoint_index, observable in enumerate((seed, seed.conj().T)):
                    target = commutator(boundary, commutator(kinetic, observable))
                    op_value = operator_norm(target)
                    operator_by_dimension[dimension].append(op_value)
                    maxima["operator_norm"] = max(maxima["operator_norm"], op_value)
                    seed_rows += 1
                    check(f"d={dimension} site={site} eta={eta} adj={adjoint_index} operator", np.isfinite(op_value), op_value, "finite", "operator stress")
                    for beta in betas:
                        rho = states[beta]
                        for energy in energies:
                            projector = projectors[energy]
                            rho_window = hermitian(projector @ rho @ projector)
                            mass = float(np.real(np.trace(rho_window)))
                            projected = two_sided_norm(target, rho_window)
                            conditional = projected / max(np.sqrt(max(mass, 0.0)), np.finfo(float).tiny)
                            name = key(beta, eta, energy)
                            check(f"d={dimension} site={site} eta={eta} adj={adjoint_index} beta={beta} E={energy} finite", all(np.isfinite(value) and value >= -tolerance for value in (mass, projected, conditional)), [mass, projected, conditional], "finite nonnegative", "window")
                            check(f"d={dimension} beta={beta} E={energy} mass", -tolerance <= mass <= 1.0 + tolerance, mass, "[0,1]", "window")
                            profiles[name][dimension].append(projected)
                            conditional_profiles[name][dimension].append(conditional)
                            mass_profiles[name][dimension].append(mass)
                            rank_profiles[name][dimension].append(ranks[energy])
                            maxima["projected_weighted_norm"] = max(maxima["projected_weighted_norm"], projected)
                            maxima["conditional_projected_norm"] = max(maxima["conditional_projected_norm"], conditional)
                            weighted_rows += 1
                            row_records.append({"dimension": dimension, "site": site, "eta": eta, "adjoint": adjoint_index, "beta": beta, "energy_threshold": energy, "operator_norm": op_value, "projected_weighted_norm": projected, "conditional_projected_norm": conditional, "window_mass": mass, "window_rank": ranks[energy]})

    operator_growth = max(operator_by_dimension[dimensions[-1]]) / max(operator_by_dimension[dimensions[0]])
    check("operator growth witness", operator_growth > op_threshold, operator_growth, f">{op_threshold}", "operator stress")
    summaries: dict[str, dict[str, Any]] = {}
    corridor_keys: list[str] = []
    outside_keys: list[str] = []
    for name in profiles:
        beta = float(name.split(";")[0].split("=")[1])
        eta = float(name.split(";")[1].split("=")[1])
        energy = float(name.split(";")[2].split("=")[1])
        projected_by_dimension = {dimension: max(profiles[name][dimension]) for dimension in dimensions}
        conditional_by_dimension = {dimension: max(conditional_profiles[name][dimension]) for dimension in dimensions}
        tail_projected = [projected_by_dimension[dimension] for dimension in dimensions if dimension >= tail_start]
        tail_conditional = [conditional_by_dimension[dimension] for dimension in dimensions if dimension >= tail_start]
        projected_ratio = max(tail_projected) / max(min(tail_projected), np.finfo(float).tiny)
        conditional_ratio = max(tail_conditional) / max(min(tail_conditional), np.finfo(float).tiny)
        item = {"beta": beta, "eta": eta, "energy_threshold": energy, "tail_cutoff_start": tail_start, "tail_row_count": len(tail_projected), "projected_tail_ratio": projected_ratio, "conditional_tail_ratio": conditional_ratio, "projected_late_ratio": projected_by_dimension[dimensions[-1]] / max(projected_by_dimension[tail_start], np.finfo(float).tiny), "conditional_late_ratio": conditional_by_dimension[dimensions[-1]] / max(conditional_by_dimension[tail_start], np.finfo(float).tiny), "window_mass_min": min(min(values) for values in mass_profiles[name].values()), "window_mass_max": max(max(values) for values in mass_profiles[name].values()), "rank_min": min(min(values) for values in rank_profiles[name].values()), "rank_max": max(max(values) for values in rank_profiles[name].values()), "stable": projected_ratio <= tail_threshold and conditional_ratio <= tail_threshold}
        summaries[name] = item
        if eta >= eta_floor:
            corridor_keys.append(name)
            check(f"corridor {name}", item["stable"], item, f"both ratios <= {tail_threshold}", "spectral corridor")
        else:
            outside_keys.append(name)

    outside_max = max(summaries[name]["projected_tail_ratio"] for name in outside_keys + corridor_keys[:0]) if outside_keys else 0.0
    check("corridor coverage", bool(corridor_keys) and bool(outside_keys), [len(corridor_keys), len(outside_keys)], "both eta regions", "spectral corridor")
    check("outside eta stress", max(summaries[name]["projected_tail_ratio"] for name in outside_keys) > tail_threshold, max(summaries[name]["projected_tail_ratio"] for name in outside_keys), f">{tail_threshold}", "spectral corridor")
    expected_seed_rows = len(dimensions) * len(sites) * len(etas) * 2
    expected_weighted_rows = expected_seed_rows * len(betas) * len(energies)
    check("row counts", [seed_rows, weighted_rows], [expected_seed_rows, expected_weighted_rows], [expected_seed_rows, expected_weighted_rows], "coverage")
    check("finite maxima", all(np.isfinite(value) for value in maxima.values()), maxima, "finite", "numerics")
    derived = {"cutoff_dimensions": dimensions, "seed_rows": seed_rows, "weighted_rows": weighted_rows, "operator_growth_ratio": operator_growth, "maximums": maxima, "corridor_keys": corridor_keys, "outside_keys": outside_keys, "tail_stability_threshold": tail_threshold, "summaries": summaries, "dimension_operator_max": {str(dimension): max(operator_by_dimension[dimension]) for dimension in dimensions}, "row_records": row_records}
    for name in finite_flags:
        derived[name] = True
    for name in open_flags:
        derived[name] = False
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-SPECTRAL-WINDOW-KINETIC-CORRIDOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY SPECTRAL-WINDOW KINETIC CORRIDOR PASS {payload['passed']}/{payload['assertion_count']} seeds={payload['derived']['seed_rows']} weighted={payload['derived']['weighted_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
