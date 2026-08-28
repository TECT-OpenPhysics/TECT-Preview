#!/usr/bin/env python3
"""Finite phase-conditioned split of the R-404 intrinsic kinetic graph."""

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
SLUG = "pre_a_cp1_st8_q3lock_phase_conditioned_intrinsic_gap"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-phase-conditioned-intrinsic-gap-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402


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


def phase_indices(levels: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = np.asarray(levels, dtype=float)
    if values.ndim != 1 or len(values) < 4 or not np.all(np.diff(values) > 0.0):
        raise AssertionError("coordinate levels are not strictly ordered")
    half = len(values) // 2
    minus = np.arange(half, dtype=int)
    plus = np.arange(len(values) - half, len(values), dtype=int)
    neutral = np.setdiff1d(np.arange(len(values), dtype=int), np.concatenate((minus, plus)))
    if len(minus) < 2 or len(plus) < 2:
        raise AssertionError("phase sector too small")
    return minus, plus, neutral


def graph_data(pi: np.ndarray, momentum: np.ndarray, chi: float) -> tuple[float, np.ndarray, np.ndarray]:
    weights = np.asarray(pi, dtype=float)
    total = float(np.sum(weights))
    if not math.isfinite(total) or total <= 0.0:
        raise AssertionError("invalid phase mass")
    weights = weights / total
    if float(np.min(weights)) <= 0.0:
        raise AssertionError("nonpositive graph mass")
    matrix = np.asarray(momentum, dtype=complex)
    conductance = (weights[:, None] + weights[None, :]) * np.square(np.abs(matrix)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse_sqrt = 1.0 / np.sqrt(weights)
    weighted = inverse_sqrt[:, None] * laplacian * inverse_sqrt[None, :]
    eigenvalues = np.linalg.eigvalsh((weighted + weighted.T) / 2.0)
    if len(eigenvalues) < 2 or not math.isfinite(float(eigenvalues[1])) or float(eigenvalues[1]) <= 0.0:
        raise AssertionError("intrinsic graph is disconnected")
    if abs(float(eigenvalues[0])) > 1.0e-8:
        raise AssertionError("constant graph mode is not zero")
    return float(eigenvalues[1]), conductance, eigenvalues


def conditional_rows(reference: np.ndarray, order: list[int], dimension: int, floor: float):
    for radius in range(len(order)):
        prefix = r399.marginal(reference, order[: radius + 1], dimension)
        parent = np.ones((1,), dtype=float) if radius == 0 else r399.marginal(reference, order[:radius], dimension).reshape(-1)
        if float(np.min(prefix)) <= floor or float(np.min(parent)) <= floor:
            raise AssertionError("reference marginal floor")
        for mass, row in zip(parent, prefix.reshape(-1, dimension)):
            conditional = row / float(mass)
            conditional /= float(np.sum(conditional))
            if float(np.min(conditional)) <= 0.0 or not np.all(np.isfinite(conditional)):
                raise AssertionError("invalid conditional row")
            yield conditional


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    floor = float(fixture["probability_floor"])
    gap_floor = float(fixture["gap_floor"])
    capacity_floor = float(fixture["capacity_floor"])
    chi = float(Fraction(str(fixture["chi"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 240:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-405" and manifest["exploration_id"] == "EXP-001250" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-405/EXP-001250/false", "provenance")
    finite_flags = ("finite_phase_partition_closed", "finite_full_intrinsic_gap_closed", "finite_within_phase_gap_closed", "finite_cross_phase_capacity_closed", "finite_beta_stress_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite phase split only", "all promoted flags false", "scope")
    check("system grid", len(pairs) == 8 and len(set(pairs)) == len(pairs), pairs, "8 distinct systems", "fixture")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")

    records: list[dict[str, Any]] = []
    beta_profiles: dict[str, dict[str, Any]] = {}
    all_full: list[float] = []
    all_phase: list[float] = []
    all_cross: list[float] = []
    all_phase_mass: list[float] = []
    all_neutral_mass: list[float] = []
    total_rows = 0
    for volume, dimension in pairs:
        _, hamiltonian, _ = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels, _single_basis, momentum = r402.coordinate_data(dimension)
        minus, plus, neutral = phase_indices(levels)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        check(f"V={volume} d={dimension} partition", len(minus) + len(plus) + len(neutral) == dimension and len(minus) >= 2 and len(plus) >= 2, [len(minus), len(plus), len(neutral)], "complete disjoint sectors", "phase partition")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        for beta in betas:
            reference, raw_reference = r399.coordinate_distribution(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -1.0e-8, [float(np.min(reference)), raw_reference], f">{floor} and nonnegative", "Gibbs")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, "row_count": 0, "minimum_full_gap": float("inf"), "maximum_full_gap": 0.0, "minimum_sector_gap": float("inf"), "maximum_sector_gap": 0.0, "minimum_cross_capacity": float("inf"), "maximum_cross_capacity": 0.0, "minimum_phase_mass": float("inf"), "maximum_neutral_mass": 0.0}
                for conditional in conditional_rows(reference, order, dimension, floor):
                    full_gap, conductance, eigenvalues = graph_data(conditional, momentum, chi)
                    minus_mass = float(np.sum(conditional[minus]))
                    plus_mass = float(np.sum(conditional[plus]))
                    neutral_mass = float(np.sum(conditional[neutral]))
                    if minus_mass <= floor or plus_mass <= floor:
                        raise AssertionError("phase mass floor")
                    minus_gap, _minus_c, _ = graph_data(conditional[minus], momentum[np.ix_(minus, minus)], chi)
                    plus_gap, _plus_c, _ = graph_data(conditional[plus], momentum[np.ix_(plus, plus)], chi)
                    sector_gap = min(minus_gap, plus_gap)
                    cross_capacity = float(np.sum(conductance[np.ix_(minus, plus)]))
                    check(f"V={volume} d={dimension} beta={beta} {orientation} row", full_gap > gap_floor and sector_gap > gap_floor and cross_capacity > capacity_floor, [full_gap, sector_gap, cross_capacity], f">{gap_floor}, >{gap_floor}, >{capacity_floor}", "phase graph")
                    profile["row_count"] += 1
                    profile["minimum_full_gap"] = min(profile["minimum_full_gap"], full_gap)
                    profile["maximum_full_gap"] = max(profile["maximum_full_gap"], full_gap)
                    profile["minimum_sector_gap"] = min(profile["minimum_sector_gap"], sector_gap)
                    profile["maximum_sector_gap"] = max(profile["maximum_sector_gap"], sector_gap)
                    profile["minimum_cross_capacity"] = min(profile["minimum_cross_capacity"], cross_capacity)
                    profile["maximum_cross_capacity"] = max(profile["maximum_cross_capacity"], cross_capacity)
                    profile["minimum_phase_mass"] = min(profile["minimum_phase_mass"], minus_mass, plus_mass)
                    profile["maximum_neutral_mass"] = max(profile["maximum_neutral_mass"], neutral_mass)
                    all_full.append(full_gap)
                    all_phase.append(sector_gap)
                    all_cross.append(cross_capacity)
                    all_phase_mass.append(minus_mass)
                    all_phase_mass.append(plus_mass)
                    all_neutral_mass.append(neutral_mass)
                    total_rows += 1
                check(f"V={volume} d={dimension} beta={beta} {orientation} coverage", profile["row_count"] > 0 and profile["minimum_full_gap"] > gap_floor and profile["minimum_sector_gap"] > gap_floor and profile["minimum_cross_capacity"] > capacity_floor, profile, "positive finite profile", "coverage")
                records.append(profile)
                beta_key = str(beta)
                aggregate = beta_profiles.setdefault(beta_key, {"beta": beta, "minimum_full_gap": float("inf"), "minimum_sector_gap": float("inf"), "minimum_cross_capacity": float("inf"), "maximum_neutral_mass": 0.0, "profile_count": 0})
                aggregate["minimum_full_gap"] = min(aggregate["minimum_full_gap"], profile["minimum_full_gap"])
                aggregate["minimum_sector_gap"] = min(aggregate["minimum_sector_gap"], profile["minimum_sector_gap"])
                aggregate["minimum_cross_capacity"] = min(aggregate["minimum_cross_capacity"], profile["minimum_cross_capacity"])
                aggregate["maximum_neutral_mass"] = max(aggregate["maximum_neutral_mass"], profile["maximum_neutral_mass"])
                aggregate["profile_count"] += 1

    check("profile coverage", len(records) == len(pairs) * len(betas) * len(orientations), len(records), len(pairs) * len(betas) * len(orientations), "coverage")
    check("row coverage", total_rows > len(records) and total_rows > 0, total_rows, f">{len(records)}", "coverage")
    check("full gaps positive", all(math.isfinite(value) and value > gap_floor for value in all_full), [min(all_full), max(all_full)], f">{gap_floor}", "full graph")
    check("sector gaps positive", all(math.isfinite(value) and value > gap_floor for value in all_phase), [min(all_phase), max(all_phase)], f">{gap_floor}", "within phase")
    check("cross capacities positive", all(math.isfinite(value) and value > capacity_floor for value in all_cross), [min(all_cross), max(all_cross)], f">{capacity_floor}", "phase bottleneck")
    check("phase masses positive", all(math.isfinite(value) and value > floor for value in all_phase_mass), min(all_phase_mass), f">{floor}", "phase partition")
    check("neutral mass bounded", all(math.isfinite(value) and 0.0 <= value < 1.0 for value in all_neutral_mass), [min(all_neutral_mass), max(all_neutral_mass)], "[0,1)", "phase partition")
    check("phase separation observed", min(all_phase) > min(all_full), [min(all_full), min(all_phase)], "within-phase floor exceeds global minimum on finite grid", "route split")
    derived = {
        "system_count": len(pairs),
        "profile_count": len(records),
        "row_count": total_rows,
        "minimum_full_gap": min(all_full),
        "maximum_full_gap": max(all_full),
        "minimum_sector_gap": min(all_phase),
        "maximum_sector_gap": max(all_phase),
        "minimum_cross_capacity": min(all_cross),
        "maximum_cross_capacity": max(all_cross),
        "minimum_phase_mass": min(all_phase_mass),
        "maximum_neutral_mass": max(all_neutral_mass),
        "profiles": records,
        "beta_profiles": beta_profiles,
        "finite_phase_partition_closed": True,
        "finite_full_intrinsic_gap_closed": True,
        "finite_within_phase_gap_closed": True,
        "finite_cross_phase_capacity_closed": True,
        "finite_beta_stress_closed": True,
        "cutoff_independent_sector_gap_closed": False,
        "volume_independent_sector_gap_closed": False,
        "phase_conditioned_uniformity_closed": False,
        "cross_phase_capacity_control_closed": False,
        "source_uniformity_closed": False,
        "exhaustion_uniformity_closed": False,
        "common_core_closed": False,
        "common_alpha_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False
    }
    payload = {"schema": "tect/pre-a-r405-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-405", "exploration_id": "EXP-001250", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-405 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} profiles={len(records)} rows={total_rows} full=[{min(all_full):.6g},{max(all_full):.6g}] sector=[{min(all_phase):.6g},{max(all_phase):.6g}] cross=[{min(all_cross):.6g},{max(all_cross):.6g}]")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
