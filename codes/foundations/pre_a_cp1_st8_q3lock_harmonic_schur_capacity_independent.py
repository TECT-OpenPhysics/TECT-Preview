#!/usr/bin/env python3
"""Independent finite reconstruction for R-406.

This lane rebuilds the oscillator Hamiltonian, coordinate law and harmonic
Schur calculation without importing the primary R-406 implementation.
"""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-harmonic-schur-capacity-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_harmonic_schur_capacity" / "independent.json"
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
    zero = np.zeros_like(coordinates[0])
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(coordinates, momenta)]
    bonds: list[np.ndarray] = []
    for left in range(volume - 1):
        difference = coordinates[left] - coordinates[left + 1]
        difference2 = difference @ difference
        bonds.append(c * difference2 / 2.0 + lam * difference2 @ (coordinates[left] @ coordinates[left] + coordinates[left + 1] @ coordinates[left + 1]) / 4.0)
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


def phase_indices(levels: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = np.asarray(levels, dtype=float)
    if len(values) < 4 or not np.all(np.diff(values) > 0.0):
        raise AssertionError("invalid coordinate spectrum")
    half = len(values) // 2
    lower = np.arange(half, dtype=int)
    upper = np.arange(len(values) - half, len(values), dtype=int)
    neutral = np.setdiff1d(np.arange(len(values), dtype=int), np.concatenate((lower, upper)))
    if len(lower) < 2 or len(upper) < 2:
        raise AssertionError("phase sector too small")
    return lower, upper, neutral


def graph(pi: np.ndarray, momentum: np.ndarray, chi: float) -> tuple[float, np.ndarray]:
    weights = np.asarray(pi, dtype=float)
    weights = weights / float(np.sum(weights))
    if float(np.min(weights)) <= 0.0:
        raise AssertionError("nonpositive graph law")
    p = np.asarray(momentum, dtype=complex)
    conductance = (weights[:, None] + weights[None, :]) * np.square(np.abs(p)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(weights)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    values = np.linalg.eigvalsh(hermitian(operator))
    if len(values) < 2 or abs(float(values[0])) > 1.0e-8 or float(values[1]) <= 0.0:
        raise AssertionError("disconnected graph")
    return float(values[1]), conductance


def harmonic(weights: np.ndarray, edges: np.ndarray, blocks: list[np.ndarray]) -> dict[str, float]:
    pi = np.asarray(weights, dtype=float)
    pi = pi / float(np.sum(pi))
    laplacian = np.diag(np.sum(edges, axis=1)) - edges
    root = np.sqrt(pi)
    inv = 1.0 / root
    operator = inv[:, None] * laplacian * inv[None, :]
    raw = np.zeros((len(pi), len(blocks)), dtype=float)
    for col, indices in enumerate(blocks):
        mass = float(np.sum(pi[indices]))
        if mass <= 0.0:
            raise AssertionError("empty block")
        raw[indices, col] = root[indices] / math.sqrt(mass)
    if not np.allclose(raw.T @ raw, np.eye(len(blocks)), atol=2.0e-10, rtol=2.0e-10):
        raise AssertionError("block basis")
    complete, _ = np.linalg.qr(raw, mode="complete")
    u, v = complete[:, : len(blocks)], complete[:, len(blocks) :]
    if v.shape[1] == 0:
        raise AssertionError("empty residual")
    avv = hermitian(v.T @ operator @ v)
    residual_values = np.linalg.eigvalsh(avv)
    if float(residual_values[0]) <= 0.0:
        raise AssertionError("residual not positive")
    auu = hermitian(u.T @ operator @ u)
    auv = u.T @ operator @ v
    schur = hermitian(auu - auv @ np.linalg.solve(avv, auv.T))
    harmonic_map = u - v @ np.linalg.solve(avv, auv.T)
    mass = hermitian(harmonic_map.T @ harmonic_map)
    mass_values, mass_vectors = np.linalg.eigh(mass)
    if float(np.min(mass_values)) <= 0.0:
        raise AssertionError("coarse mass not positive")
    invsqrt = mass_vectors @ np.diag(1.0 / np.sqrt(mass_values)) @ mass_vectors.T
    coarse_values = np.linalg.eigvalsh(hermitian(invsqrt @ schur @ invsqrt))
    naive_values = np.linalg.eigvalsh(auu)
    full_values = np.linalg.eigvalsh(hermitian(operator))
    return {
        "full_gap": float(full_values[1]),
        "coarse_gap": float(coarse_values[1]),
        "residual_gap": float(residual_values[0]),
        "decomposition_gap": 0.5 * min(float(coarse_values[1]), float(residual_values[0])),
        "naive_block_gap": float(naive_values[1]),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    floor = float(fixture["probability_floor"])
    gap_floor = float(fixture["gap_floor"])
    chi = float(Fraction(str(fixture["chi"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    orientations = list(fixture["orientations"])
    count = 0
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        nonlocal count
        count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 240:
            checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-406" and manifest["exploration_id"] == "EXP-001251" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-406/EXP-001251/false")
    finite = ("finite_harmonic_extension_closed", "finite_schur_capacity_closed", "finite_residual_gap_closed", "finite_energy_variance_split_closed", "finite_naive_block_gap_obstruction_closed")
    check("scope", all(scope[key] for key in finite) and not any(value for key, value in scope.items() if key.endswith("_closed") and key not in finite), scope, "finite split only")
    full_values: list[float] = []
    coarse_values: list[float] = []
    residual_values: list[float] = []
    decomposition_values: list[float] = []
    naive_values: list[float] = []
    profile_rows: list[dict[str, Any]] = []
    row_count = 0
    naive_obstructions = 0
    for volume, dimension in pairs:
        hamiltonian = model(volume, dimension, fixture)
        basis = coordinate_basis(dimension, volume)
        q_single, p_single = q3.oscillator(dimension)
        levels, vectors = np.linalg.eigh(hermitian(q_single))
        momentum = hermitian(vectors.conj().T @ p_single @ vectors)
        lower, upper, neutral = phase_indices(levels)
        blocks = [lower, neutral, upper] if len(neutral) else [lower, upper]
        check(f"V={volume} d={dimension} partition", sum(len(block) for block in blocks) == dimension, [len(block) for block in blocks], "complete partition")
        for beta in betas:
            reference = distribution(gibbs(hamiltonian, beta), basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} mass", float(np.min(reference)) > floor, float(np.min(reference)), f">{floor}")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, "row_count": 0, "minimum_full_gap": float("inf"), "minimum_coarse_gap": float("inf"), "minimum_residual_gap": float("inf"), "minimum_decomposition_gap": float("inf"), "minimum_naive_gap": float("inf")}
                for radius in range(volume):
                    prefix = marginal(reference, order[: radius + 1], dimension)
                    parent = np.ones((1,), dtype=float) if radius == 0 else marginal(reference, order[:radius], dimension).reshape(-1)
                    if float(np.min(prefix)) <= floor or float(np.min(parent)) <= floor:
                        raise AssertionError("marginal floor")
                    for mass, row in zip(parent, prefix.reshape(-1, dimension)):
                        pi = row / float(mass)
                        pi /= float(np.sum(pi))
                        full_gap, edges = graph(pi, momentum, chi)
                        data = harmonic(pi, edges, blocks)
                        check(f"V={volume} d={dimension} beta={beta} {orientation} row", data["full_gap"] > gap_floor and data["coarse_gap"] > gap_floor and data["residual_gap"] > gap_floor and data["decomposition_gap"] > gap_floor, [data["full_gap"], data["coarse_gap"], data["residual_gap"], data["decomposition_gap"]], f">{gap_floor}")
                        check(f"V={volume} d={dimension} beta={beta} {orientation} Schur bound", data["decomposition_gap"] <= full_gap + 2.0e-8 and data["naive_block_gap"] + 2.0e-8 >= full_gap, [data["decomposition_gap"], full_gap, data["naive_block_gap"]], "corrected lower and Ritz upper")
                        for key, values in (("full_gap", full_values), ("coarse_gap", coarse_values), ("residual_gap", residual_values), ("decomposition_gap", decomposition_values), ("naive_block_gap", naive_values)):
                            values.append(data[key])
                        if data["naive_block_gap"] > full_gap + 1.0e-9:
                            naive_obstructions += 1
                        profile["row_count"] += 1
                        profile["minimum_full_gap"] = min(profile["minimum_full_gap"], data["full_gap"])
                        profile["minimum_coarse_gap"] = min(profile["minimum_coarse_gap"], data["coarse_gap"])
                        profile["minimum_residual_gap"] = min(profile["minimum_residual_gap"], data["residual_gap"])
                        profile["minimum_decomposition_gap"] = min(profile["minimum_decomposition_gap"], data["decomposition_gap"])
                        profile["minimum_naive_gap"] = min(profile["minimum_naive_gap"], data["naive_block_gap"])
                        row_count += 1
                profile_rows.append(profile)
    check("profiles", len(profile_rows) == len(pairs) * len(betas) * len(orientations), len(profile_rows), len(pairs) * len(betas) * len(orientations))
    check("rows", row_count > len(profile_rows), row_count, f">{len(profile_rows)}")
    check("positive", min(decomposition_values) > gap_floor, [min(full_values), min(coarse_values), min(residual_values), min(decomposition_values)], f">{gap_floor}")
    check("naive obstruction", naive_obstructions > 0 and max(naive_values) > max(full_values), [naive_obstructions, max(naive_values), max(full_values)], "strict Ritz-over-full row")
    derived = {"system_count": len(pairs), "profile_count": len(profile_rows), "row_count": row_count, "minimum_full_gap": min(full_values), "maximum_full_gap": max(full_values), "minimum_coarse_schur_gap": min(coarse_values), "maximum_coarse_schur_gap": max(coarse_values), "minimum_residual_gap": min(residual_values), "maximum_residual_gap": max(residual_values), "minimum_decomposition_gap": min(decomposition_values), "maximum_decomposition_gap": max(decomposition_values), "minimum_naive_block_gap": min(naive_values), "maximum_naive_block_gap": max(naive_values), "naive_obstruction_rows": naive_obstructions, "profiles": profile_rows, "finite_harmonic_extension_closed": True, "finite_schur_capacity_closed": True, "finite_residual_gap_closed": True, "finite_energy_variance_split_closed": True, "finite_naive_block_gap_obstruction_closed": True, "cutoff_independent_schur_gap_closed": False, "volume_independent_schur_gap_closed": False, "phase_conditioned_uniformity_closed": False, "cross_phase_capacity_control_closed": False, "source_uniformity_closed": False, "exhaustion_uniformity_closed": False, "common_core_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}
    payload = {"schema": "tect/pre-a-r406-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-406", "exploration_id": "EXP-001251", "verdict": "PASS", "checks": checks, "assertion_count": count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-406 INDEPENDENT PASS {count}/{count} systems={len(pairs)} profiles={len(profile_rows)} rows={row_count} full=[{min(full_values):.6g},{max(full_values):.6g}] coarse=[{min(coarse_values):.6g},{max(coarse_values):.6g}] residual=[{min(residual_values):.6g},{max(residual_values):.6g}] naive_obstructions={naive_obstructions}")
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
