#!/usr/bin/env python3
"""Primary finite harmonic-extension/Schur-complement audit for R-406.

The audit works on the actual finite Q3 conditional momentum graphs used by
R-405.  It does not infer a thermodynamic theorem.  For each graph it
eliminates the block-mean-zero variables by a Dirichlet (harmonic) minimizer,
checks the exact energy/variance split, and records the corrected coarse gap
alongside the uncorrected block-constant Ritz value.
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
from typing import Any, Iterable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_harmonic_schur_capacity"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-harmonic-schur-capacity-manifest.json"
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
    lower = np.arange(half, dtype=int)
    upper = np.arange(len(values) - half, len(values), dtype=int)
    neutral = np.setdiff1d(np.arange(len(values), dtype=int), np.concatenate((lower, upper)))
    if len(lower) < 2 or len(upper) < 2:
        raise AssertionError("phase sector too small")
    return lower, upper, neutral


def normalized_graph(pi: np.ndarray, momentum: np.ndarray, chi: float) -> tuple[float, np.ndarray]:
    weights = np.asarray(pi, dtype=float)
    total = float(np.sum(weights))
    if not math.isfinite(total) or total <= 0.0:
        raise AssertionError("invalid conditional mass")
    weights = weights / total
    if float(np.min(weights)) <= 0.0 or not np.all(np.isfinite(weights)):
        raise AssertionError("nonpositive conditional mass")
    p = np.asarray(momentum, dtype=complex)
    conductance = (weights[:, None] + weights[None, :]) * np.square(np.abs(p)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(weights)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    values = np.linalg.eigvalsh((operator + operator.T) / 2.0)
    if len(values) < 2 or abs(float(values[0])) > 1.0e-8 or float(values[1]) <= 0.0:
        raise AssertionError("intrinsic graph is disconnected")
    return float(values[1]), conductance


def block_basis(weights: np.ndarray, blocks: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Return an orthonormal block span U and its Euclidean complement V."""
    pi = np.asarray(weights, dtype=float)
    root = np.sqrt(pi)
    n = len(pi)
    raw = np.zeros((n, len(blocks)), dtype=float)
    masses: list[float] = []
    for column, indices in enumerate(blocks):
        mass = float(np.sum(pi[indices]))
        if not math.isfinite(mass) or mass <= 0.0:
            raise AssertionError("empty weighted block")
        masses.append(mass)
        raw[indices, column] = root[indices] / math.sqrt(mass)
    gram = raw.T @ raw
    if not np.allclose(gram, np.eye(len(blocks)), atol=2.0e-10, rtol=2.0e-10):
        raise AssertionError("block basis is not orthonormal")
    complete, _ = np.linalg.qr(raw, mode="complete")
    return complete[:, : len(blocks)], complete[:, len(blocks) :]


def harmonic_split(weights: np.ndarray, conductance: np.ndarray, blocks: list[np.ndarray]) -> dict[str, Any]:
    """Compute Schur coarse/residual gaps and the exact harmonic decomposition."""
    pi = np.asarray(weights, dtype=float)
    pi = pi / float(np.sum(pi))
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    root = np.sqrt(pi)
    inverse = 1.0 / root
    operator = inverse[:, None] * laplacian * inverse[None, :]
    u, v = block_basis(pi, blocks)
    coarse = u.T @ operator @ u
    if v.shape[1] == 0:
        raise AssertionError("no residual complement")
    residual_operator = (v.T @ operator @ v + (v.T @ operator @ v).T) / 2.0
    residual_values = np.linalg.eigvalsh(residual_operator)
    if not np.all(np.isfinite(residual_values)) or float(residual_values[0]) <= 0.0:
        raise AssertionError("residual operator is not positive")
    coupling = u.T @ operator @ v
    schur = coarse - coupling @ np.linalg.solve(residual_operator, coupling.T)
    schur = (schur + schur.T) / 2.0
    harmonic_map = u - v @ np.linalg.solve(residual_operator, coupling.T)
    mass_matrix = (harmonic_map.T @ harmonic_map + (harmonic_map.T @ harmonic_map).T) / 2.0
    mass_values, mass_vectors = np.linalg.eigh(mass_matrix)
    if not np.all(np.isfinite(mass_values)) or float(np.min(mass_values)) <= 0.0:
        raise AssertionError("harmonic coarse mass is not positive")
    mass_inverse_sqrt = mass_vectors @ np.diag(1.0 / np.sqrt(mass_values)) @ mass_vectors.T
    coarse_weighted = mass_inverse_sqrt @ schur @ mass_inverse_sqrt
    coarse_values = np.linalg.eigvalsh((coarse_weighted + coarse_weighted.T) / 2.0)
    if len(coarse_values) < 2 or abs(float(coarse_values[0])) > 2.0e-7:
        raise AssertionError("Schur constant mode is not zero")
    if float(coarse_values[1]) <= 0.0:
        raise AssertionError("Schur coarse graph is not positive")
    naive_values = np.linalg.eigvalsh((coarse + coarse.T) / 2.0)
    if len(naive_values) < 2 or abs(float(naive_values[0])) > 2.0e-8 or float(naive_values[1]) <= 0.0:
        raise AssertionError("naive block restriction is not positive")
    full_values = np.linalg.eigvalsh((operator + operator.T) / 2.0)
    full_gap = float(full_values[1])
    coarse_gap = float(coarse_values[1])
    residual_gap = float(residual_values[0])
    naive_gap = float(naive_values[1])
    decomposition_gap = 0.5 * min(coarse_gap, residual_gap)

    # Deterministic centered probes exercise the orthogonal decomposition.
    probes: list[np.ndarray] = []
    indices = np.arange(len(pi), dtype=float)
    for phase in (0.0, 0.37, 0.91):
        probe = np.sin((indices + 1.0) * (1.0 + phase)) + 0.31 * np.cos((indices + 2.0) * (0.7 + phase))
        probe -= float(np.dot(pi, probe))
        probes.append(probe)
    split_rows: list[dict[str, float]] = []
    global_vector = root
    coarse_global = u.T @ global_vector
    max_energy_residual = 0.0
    max_variance_envelope_deficit = 0.0
    min_lower_margin = float("inf")
    for probe in probes:
        y = root * probe
        z = u.T @ y
        w = v.T @ y
        harmonic_w = -np.linalg.solve(residual_operator, coupling.T @ z)
        harmonic_y = u @ z + v @ harmonic_w
        residual_y = v @ (w - harmonic_w)
        energy = float(np.real(y @ (operator @ y)))
        harmonic_energy = float(np.real(harmonic_y @ (operator @ harmonic_y)))
        residual_energy = float(np.real(residual_y @ (operator @ residual_y)))
        variance = float(np.dot(y, y))
        coarse_variance = float(np.dot(z, z))
        harmonic_variance = float(np.dot(harmonic_y, harmonic_y))
        residual_variance = float(np.dot(residual_y, residual_y))
        energy_residual = abs(energy - harmonic_energy - residual_energy)
        variance_envelope_deficit = 2.0 * (harmonic_variance + residual_variance) - variance
        max_energy_residual = max(max_energy_residual, energy_residual)
        max_variance_envelope_deficit = max(max_variance_envelope_deficit, -variance_envelope_deficit)
        if abs(float(np.dot(z, coarse_global))) > 5.0e-8:
            raise AssertionError("centered probe has nonzero coarse constant")
        lower_margin = energy - decomposition_gap * variance
        min_lower_margin = min(min_lower_margin, lower_margin)
        split_rows.append({
            "energy": energy,
            "harmonic_energy": harmonic_energy,
            "residual_energy": residual_energy,
            "variance": variance,
            "coarse_variance": coarse_variance,
            "harmonic_variance": harmonic_variance,
            "residual_variance": residual_variance,
            "energy_residual": energy_residual,
            "variance_envelope_deficit": variance_envelope_deficit,
            "lower_bound_margin": lower_margin,
        })
    return {
        "full_gap": full_gap,
        "coarse_gap": coarse_gap,
        "residual_gap": residual_gap,
        "decomposition_gap": decomposition_gap,
        "naive_block_gap": naive_gap,
        "naive_exceeds_full": naive_gap > full_gap + 1.0e-9,
        "schur_min_eigenvalue": float(coarse_values[0]),
        "residual_min_eigenvalue": float(residual_values[0]),
        "max_energy_residual": max_energy_residual,
        "max_variance_envelope_deficit": max_variance_envelope_deficit,
        "minimum_lower_bound_margin": min_lower_margin,
        "probe_rows": split_rows,
    }


def conditional_rows(reference: np.ndarray, order: list[int], dimension: int, floor: float) -> Iterable[np.ndarray]:
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
    decomposition_tolerance = float(fixture["decomposition_tolerance"])
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
        if len(checks) < 260:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-406" and manifest["exploration_id"] == "EXP-001251" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-406/EXP-001251/false", "provenance")
    finite_flags = ("finite_harmonic_extension_closed", "finite_schur_capacity_closed", "finite_residual_gap_closed", "finite_energy_variance_split_closed", "finite_naive_block_gap_obstruction_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite Schur split only", "all promoted flags false", "scope")
    check("system grid", len(pairs) == 8 and len(set(pairs)) == len(pairs), pairs, "8 distinct systems", "fixture")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")

    records: list[dict[str, Any]] = []
    all_full: list[float] = []
    all_coarse: list[float] = []
    all_residual: list[float] = []
    all_decomposition: list[float] = []
    all_naive: list[float] = []
    naive_obstructions = 0
    total_rows = 0
    for volume, dimension in pairs:
        _, hamiltonian, _ = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels, _single_basis, momentum = r402.coordinate_data(dimension)
        lower, upper, neutral = phase_indices(levels)
        blocks = [lower, neutral, upper] if len(neutral) else [lower, upper]
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        check(f"V={volume} d={dimension} blocks", sum(len(block) for block in blocks) == dimension and all(len(block) >= 2 for block in (lower, upper)), [len(block) for block in blocks], "complete lower/neutral/upper partition", "partition")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        for beta in betas:
            reference, raw_reference = r399.coordinate_distribution(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -1.0e-8, [float(np.min(reference)), raw_reference], f">{floor} and nonnegative", "Gibbs")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, "row_count": 0, "minimum_full_gap": float("inf"), "minimum_coarse_gap": float("inf"), "minimum_residual_gap": float("inf"), "minimum_decomposition_gap": float("inf"), "minimum_naive_gap": float("inf"), "maximum_energy_residual": 0.0, "maximum_variance_envelope_deficit": 0.0}
                for conditional in conditional_rows(reference, order, dimension, floor):
                    full_gap, conductance = normalized_graph(conditional, momentum, chi)
                    data = harmonic_split(conditional, conductance, blocks)
                    check(f"V={volume} d={dimension} beta={beta} {orientation} row", data["full_gap"] > gap_floor and data["coarse_gap"] > gap_floor and data["residual_gap"] > gap_floor and data["decomposition_gap"] > gap_floor, [data["full_gap"], data["coarse_gap"], data["residual_gap"], data["decomposition_gap"]], f">{gap_floor}", "Schur graph")
                    check(f"V={volume} d={dimension} beta={beta} {orientation} energy split", data["max_energy_residual"] <= decomposition_tolerance and data["max_variance_envelope_deficit"] <= decomposition_tolerance and data["minimum_lower_bound_margin"] >= -decomposition_tolerance, [data["max_energy_residual"], data["max_variance_envelope_deficit"], data["minimum_lower_bound_margin"]], f"energy/envelope residuals <= {decomposition_tolerance}", "harmonic decomposition")
                    check(f"V={volume} d={dimension} beta={beta} {orientation} Schur lower", data["decomposition_gap"] <= full_gap + decomposition_tolerance, [data["decomposition_gap"], full_gap], f"<= full gap + {decomposition_tolerance}", "variational lower bound")
                    check(f"V={volume} d={dimension} beta={beta} {orientation} Ritz warning", data["naive_block_gap"] + decomposition_tolerance >= full_gap, [data["naive_block_gap"], full_gap], f"Ritz restriction >= full gap - {decomposition_tolerance}", "shortcut audit")
                    profile["row_count"] += 1
                    profile["minimum_full_gap"] = min(profile["minimum_full_gap"], data["full_gap"])
                    profile["minimum_coarse_gap"] = min(profile["minimum_coarse_gap"], data["coarse_gap"])
                    profile["minimum_residual_gap"] = min(profile["minimum_residual_gap"], data["residual_gap"])
                    profile["minimum_decomposition_gap"] = min(profile["minimum_decomposition_gap"], data["decomposition_gap"])
                    profile["minimum_naive_gap"] = min(profile["minimum_naive_gap"], data["naive_block_gap"])
                    profile["maximum_energy_residual"] = max(profile["maximum_energy_residual"], data["max_energy_residual"])
                    profile["maximum_variance_envelope_deficit"] = max(profile["maximum_variance_envelope_deficit"], data["max_variance_envelope_deficit"])
                    all_full.append(data["full_gap"])
                    all_coarse.append(data["coarse_gap"])
                    all_residual.append(data["residual_gap"])
                    all_decomposition.append(data["decomposition_gap"])
                    all_naive.append(data["naive_block_gap"])
                    if data["naive_exceeds_full"]:
                        naive_obstructions += 1
                    total_rows += 1
                check(f"V={volume} d={dimension} beta={beta} {orientation} coverage", profile["row_count"] > 0 and profile["minimum_decomposition_gap"] > gap_floor, profile, "positive Schur profile", "coverage")
                records.append(profile)

    check("profile coverage", len(records) == len(pairs) * len(betas) * len(orientations), len(records), len(pairs) * len(betas) * len(orientations), "coverage")
    check("row coverage", total_rows > len(records) and total_rows > 0, total_rows, f">{len(records)}", "coverage")
    check("full gaps positive", all(value > gap_floor for value in all_full), [min(all_full), max(all_full)], f">{gap_floor}", "full graph")
    check("coarse Schur gaps positive", all(value > gap_floor for value in all_coarse), [min(all_coarse), max(all_coarse)], f">{gap_floor}", "Schur coarse")
    check("residual gaps positive", all(value > gap_floor for value in all_residual), [min(all_residual), max(all_residual)], f">{gap_floor}", "residual")
    check("decomposition lower values positive", all(value > gap_floor for value in all_decomposition), [min(all_decomposition), max(all_decomposition)], f">{gap_floor}", "finite lower bound")
    check("naive shortcut obstructed", naive_obstructions > 0 and max(all_naive) > max(all_full), [naive_obstructions, max(all_naive), max(all_full)], "at least one strict Ritz-over-full row", "shortcut audit")
    derived = {
        "system_count": len(pairs),
        "profile_count": len(records),
        "row_count": total_rows,
        "minimum_full_gap": min(all_full),
        "maximum_full_gap": max(all_full),
        "minimum_coarse_schur_gap": min(all_coarse),
        "maximum_coarse_schur_gap": max(all_coarse),
        "minimum_residual_gap": min(all_residual),
        "maximum_residual_gap": max(all_residual),
        "minimum_decomposition_gap": min(all_decomposition),
        "maximum_decomposition_gap": max(all_decomposition),
        "minimum_naive_block_gap": min(all_naive),
        "maximum_naive_block_gap": max(all_naive),
        "naive_obstruction_rows": naive_obstructions,
        "profiles": records,
        "finite_harmonic_extension_closed": True,
        "finite_schur_capacity_closed": True,
        "finite_residual_gap_closed": True,
        "finite_energy_variance_split_closed": True,
        "finite_naive_block_gap_obstruction_closed": True,
        "cutoff_independent_schur_gap_closed": False,
        "volume_independent_schur_gap_closed": False,
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
        "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r406-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-406", "exploration_id": "EXP-001251", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-406 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} profiles={len(records)} rows={total_rows} full=[{min(all_full):.6g},{max(all_full):.6g}] coarse=[{min(all_coarse):.6g},{max(all_coarse):.6g}] residual=[{min(all_residual):.6g},{max(all_residual):.6g}] naive_obstructions={naive_obstructions}")
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
