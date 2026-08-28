#!/usr/bin/env python3
"""Independent finite reconstruction for R-405."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-phase-conditioned-intrinsic-gap-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_phase_conditioned_intrinsic_gap" / "independent.json"
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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def model(volume: int, dimension: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = q3.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [embed(q_single, site, volume, identity) for site in range(volume)]
    momenta = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(fixture[key]))) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(str(fixture[key]))) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(coordinates, momenta)]
    bonds: list[np.ndarray] = []
    for left in range(volume - 1):
        difference = coordinates[left] - coordinates[left + 1]
        difference2 = difference @ difference
        bonds.append(c * difference2 / 2.0 + lam * difference2 @ (coordinates[left] @ coordinates[left] + coordinates[left + 1] @ coordinates[left + 1]) / 4.0)
    zero = np.zeros_like(coordinates[0])
    return hermitian(sum(onsite + bonds, zero))


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def coordinate_basis(dimension: int, volume: int) -> np.ndarray:
    q_single, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(hermitian(q_single))
    result = vectors
    for _ in range(volume - 1):
        result = np.kron(result, vectors)
    return result


def distribution(state: np.ndarray, basis: np.ndarray, dimension: int, volume: int) -> np.ndarray:
    diagonal = np.real(np.diag(basis.conj().T @ state @ basis))
    values = np.maximum(diagonal, 0.0)
    total = float(np.sum(values))
    if total <= 0.0:
        raise AssertionError("zero coordinate mass")
    return (values / total).reshape((dimension,) * volume)


def marginal(values: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    rest = [site for site in range(values.ndim) if site not in sites]
    moved = np.transpose(values, sites + rest)
    return moved.reshape(dimension ** len(sites), -1).sum(axis=1).reshape((dimension,) * len(sites))


def graph(pi: np.ndarray, momentum: np.ndarray, chi: float) -> tuple[float, np.ndarray]:
    weights = np.asarray(pi, dtype=float)
    weights = weights / float(np.sum(weights))
    if float(np.min(weights)) <= 0.0:
        raise AssertionError("nonpositive mass")
    p = np.asarray(momentum, dtype=complex)
    conductance = (weights[:, None] + weights[None, :]) * np.square(np.abs(p)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inv = 1.0 / np.sqrt(weights)
    weighted = inv[:, None] * laplacian * inv[None, :]
    eigenvalues = np.linalg.eigvalsh((weighted + weighted.T) / 2.0)
    if len(eigenvalues) < 2 or abs(float(eigenvalues[0])) > 1.0e-8 or float(eigenvalues[1]) <= 0.0:
        raise AssertionError("disconnected graph")
    return float(eigenvalues[1]), conductance


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    floor = float(fixture["probability_floor"])
    gap_floor = float(fixture["gap_floor"])
    capacity_floor = float(fixture["capacity_floor"])
    chi = float(Fraction(str(fixture["chi"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    orientations = list(fixture["orientations"])
    checks: list[dict[str, Any]] = []
    count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        nonlocal count
        count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 220:
            checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-405" and manifest["exploration_id"] == "EXP-001250" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-405/EXP-001250/false")
    finite_flags = ("finite_phase_partition_closed", "finite_full_intrinsic_gap_closed", "finite_within_phase_gap_closed", "finite_cross_phase_capacity_closed", "finite_beta_stress_closed")
    check("scope", all(scope[key] for key in finite_flags) and not any(value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags), scope, "finite split only")
    summary: dict[str, dict[str, Any]] = {}
    full_values: list[float] = []
    sector_values: list[float] = []
    cross_values: list[float] = []
    phase_masses: list[float] = []
    neutral_masses: list[float] = []
    profiles: list[dict[str, Any]] = []
    row_count = 0
    for volume, dimension in pairs:
        hamiltonian = model(volume, dimension, fixture)
        basis = coordinate_basis(dimension, volume)
        q_single, p_single = q3.oscillator(dimension)
        levels, vectors = np.linalg.eigh(hermitian(q_single))
        momentum = hermitian(vectors.conj().T @ p_single @ vectors)
        half = dimension // 2
        minus = np.arange(half, dtype=int)
        plus = np.arange(dimension - half, dimension, dtype=int)
        neutral = np.setdiff1d(np.arange(dimension, dtype=int), np.concatenate((minus, plus)))
        check(f"V={volume} d={dimension} partition", len(minus) >= 2 and len(plus) >= 2 and len(minus) + len(plus) + len(neutral) == dimension, [len(minus), len(plus), len(neutral)], "complete phase partition")
        states = {beta: gibbs(hamiltonian, beta) for beta in betas}
        for beta in betas:
            reference = distribution(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} mass", float(np.min(reference)) > floor, float(np.min(reference)), f">{floor}")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, "row_count": 0, "minimum_full_gap": float("inf"), "minimum_sector_gap": float("inf"), "minimum_cross_capacity": float("inf"), "maximum_neutral_mass": 0.0}
                for radius in range(volume):
                    prefix = marginal(reference, order[: radius + 1], dimension)
                    parent = np.ones((1,), dtype=float) if radius == 0 else marginal(reference, order[:radius], dimension).reshape(-1)
                    if float(np.min(prefix)) <= floor or float(np.min(parent)) <= floor:
                        raise AssertionError("marginal floor")
                    for mass, row in zip(parent, prefix.reshape(-1, dimension)):
                        pi = row / float(mass)
                        pi /= float(np.sum(pi))
                        full_gap, conductance = graph(pi, momentum, chi)
                        minus_gap, _ = graph(pi[minus], momentum[np.ix_(minus, minus)], chi)
                        plus_gap, _ = graph(pi[plus], momentum[np.ix_(plus, plus)], chi)
                        sector_gap = min(minus_gap, plus_gap)
                        cross = float(np.sum(conductance[np.ix_(minus, plus)]))
                        mminus, mplus = float(np.sum(pi[minus])), float(np.sum(pi[plus]))
                        neutral_mass = float(np.sum(pi[neutral]))
                        check(f"V={volume} d={dimension} beta={beta} {orientation} row", full_gap > gap_floor and sector_gap > gap_floor and cross > capacity_floor and mminus > floor and mplus > floor, [full_gap, sector_gap, cross, mminus, mplus], "positive")
                        profile["row_count"] += 1
                        profile["minimum_full_gap"] = min(profile["minimum_full_gap"], full_gap)
                        profile["minimum_sector_gap"] = min(profile["minimum_sector_gap"], sector_gap)
                        profile["minimum_cross_capacity"] = min(profile["minimum_cross_capacity"], cross)
                        profile["maximum_neutral_mass"] = max(profile["maximum_neutral_mass"], neutral_mass)
                        full_values.append(full_gap)
                        sector_values.append(sector_gap)
                        cross_values.append(cross)
                        phase_masses.extend((mminus, mplus))
                        neutral_masses.append(neutral_mass)
                        row_count += 1
                profiles.append(profile)
                entry = summary.setdefault(str(beta), {"beta": beta, "profile_count": 0, "minimum_full_gap": float("inf"), "minimum_sector_gap": float("inf"), "minimum_cross_capacity": float("inf"), "maximum_neutral_mass": 0.0})
                entry["profile_count"] += 1
                entry["minimum_full_gap"] = min(entry["minimum_full_gap"], profile["minimum_full_gap"])
                entry["minimum_sector_gap"] = min(entry["minimum_sector_gap"], profile["minimum_sector_gap"])
                entry["minimum_cross_capacity"] = min(entry["minimum_cross_capacity"], profile["minimum_cross_capacity"])
                entry["maximum_neutral_mass"] = max(entry["maximum_neutral_mass"], profile["maximum_neutral_mass"])
    check("profiles", len(profiles) == len(pairs) * len(betas) * len(orientations), len(profiles), len(pairs) * len(betas) * len(orientations))
    check("rows", row_count > len(profiles), row_count, f">{len(profiles)}")
    check("full gaps", all(math.isfinite(value) and value > gap_floor for value in full_values), [min(full_values), max(full_values)], "positive")
    check("sector gaps", all(math.isfinite(value) and value > gap_floor for value in sector_values), [min(sector_values), max(sector_values)], "positive")
    check("cross capacities", all(math.isfinite(value) and value > capacity_floor for value in cross_values), [min(cross_values), max(cross_values)], "positive")
    check("phase masses", all(math.isfinite(value) and value > floor for value in phase_masses), min(phase_masses), "positive")
    check("neutral masses", all(math.isfinite(value) and 0.0 <= value < 1.0 for value in neutral_masses), [min(neutral_masses), max(neutral_masses)], "bounded")
    check("split", min(sector_values) > min(full_values), [min(full_values), min(sector_values)], "sector floor above global floor")
    derived = {"system_count": len(pairs), "profile_count": len(profiles), "row_count": row_count, "minimum_full_gap": min(full_values), "maximum_full_gap": max(full_values), "minimum_sector_gap": min(sector_values), "maximum_sector_gap": max(sector_values), "minimum_cross_capacity": min(cross_values), "maximum_cross_capacity": max(cross_values), "minimum_phase_mass": min(phase_masses), "maximum_neutral_mass": max(neutral_masses), "profiles": profiles, "beta_profiles": summary, "finite_phase_partition_closed": True, "finite_full_intrinsic_gap_closed": True, "finite_within_phase_gap_closed": True, "finite_cross_phase_capacity_closed": True, "finite_beta_stress_closed": True, "cutoff_independent_sector_gap_closed": False, "volume_independent_sector_gap_closed": False, "phase_conditioned_uniformity_closed": False, "cross_phase_capacity_control_closed": False, "source_uniformity_closed": False, "exhaustion_uniformity_closed": False, "common_core_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}
    payload = {"schema": "tect/pre-a-r405-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-405", "exploration_id": "EXP-001250", "verdict": "PASS", "checks": checks, "assertion_count": count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-405 INDEPENDENT PASS {count}/{count} systems={len(pairs)} profiles={len(profiles)} rows={row_count} full=[{min(full_values):.6g},{max(full_values):.6g}] sector=[{min(sector_values):.6g},{max(sector_values):.6g}] cross=[{min(cross_values):.6g},{max(cross_values):.6g}]")
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
