#!/usr/bin/env python3
"""Finite local-marginal spectral-window transfer stress for R-390.

The global finite Gibbs matrix is reduced to each adjacent local pair before a
fixed local spectral projector is applied.  The package checks exact finite
trace duality, positivity and mass splitting, and records volume/cutoff
profiles.  It is a diagnostic only: no thermodynamic or common-core theorem
is asserted.
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
SLUG = "pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-marginal-spectral-window-transfer-manifest.json"
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


def lift(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def build_system(dimension: int, volume: int, fixture: dict[str, Any]) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [lift(q_single, site, volume, identity) for site in range(volume)]
    momenta = [lift(p_single, site, volume, identity) for site in range(volume)]
    hamiltonian = np.zeros((dimension**volume, dimension**volume), dtype=complex)
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    for site in range(volume):
        q = coordinates[site]
        p = momenta[site]
        hamiltonian += p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0
    for site in range(volume - 1):
        difference = coordinates[site] - coordinates[site + 1]
        difference2 = difference @ difference
        hamiltonian += c * difference2 / 2.0 + lam * difference2 @ (coordinates[site] @ coordinates[site] + coordinates[site + 1] @ coordinates[site + 1]) / 4.0
    return hermitian(hamiltonian), coordinates, momenta


def partial_trace_pair(state: np.ndarray, dimension: int, volume: int, start: int) -> np.ndarray:
    keep = [start, start + 1]
    rest = [index for index in range(volume) if index not in keep]
    axes = keep + rest + [index + volume for index in keep] + [index + volume for index in rest]
    tensor = np.transpose(state.reshape([dimension] * (2 * volume)), axes)
    for _ in rest:
        half = tensor.ndim // 2
        tensor = np.trace(tensor, axis1=2, axis2=half + 2)
    return tensor.reshape(dimension * dimension, dimension * dimension)


def embed_pair(operator: np.ndarray, dimension: int, volume: int, start: int) -> np.ndarray:
    left = np.eye(dimension**start, dtype=complex)
    right = np.eye(dimension ** (volume - start - 2), dtype=complex)
    return np.kron(np.kron(left, operator), right)


def gibbs_from_spectrum(values: np.ndarray, vectors: np.ndarray, beta: float) -> np.ndarray:
    shifted = values - float(np.min(values))
    weights = np.exp(-beta * shifted)
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def local_kinetic_targets(dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], dict[float, np.ndarray], dict[tuple[float, int, int], np.ndarray]]:
    local, coordinates, momenta = build_system(dimension, 2, fixture)
    del local
    identity = np.eye(dimension * dimension, dtype=complex)
    kinetic = hermitian((momenta[0] @ momenta[0] + momenta[1] @ momenta[1]) / (2.0 * float(fixture["chi"])))
    difference = coordinates[0] - coordinates[1]
    difference2 = difference @ difference
    boundary = hermitian(float(fixture["c"]) * difference2 / 2.0 + float(fixture["lambda"]) * difference2 @ (coordinates[0] @ coordinates[0] + coordinates[1] @ coordinates[1]) / 4.0)
    local_values, local_vectors = np.linalg.eigh(hermitian(build_system(dimension, 2, fixture)[0]))
    shifted = local_values - float(np.min(local_values))
    selection_tolerance = float(fixture["positivity_tolerance"])
    projectors = {float(Fraction(raw)): local_vectors[:, shifted <= float(Fraction(raw)) + selection_tolerance] @ local_vectors[:, shifted <= float(Fraction(raw)) + selection_tolerance].conj().T for raw in fixture["energy_windows"]}
    targets: dict[tuple[float, int, int], np.ndarray] = {}
    for eta in [float(Fraction(raw)) for raw in fixture["resolvent_imaginary_values"]]:
        for site, coordinate in enumerate(coordinates):
            seed = np.linalg.inv(1j * eta * identity - coordinate)
            for adjoint in range(2):
                observable = seed if adjoint == 0 else seed.conj().T
                targets[(eta, site, adjoint)] = commutator(boundary, commutator(kinetic, observable))
    return coordinates, momenta, projectors, targets


def boundary_class(start: int, volume: int) -> str:
    return "boundary" if start in (0, volume - 2) else "interior"


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001233" and manifest["result_id"] == "R-390" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001233/R-390/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all declared local pairs and duality rows", "coverage")
    finite_flags = ("finite_local_partial_trace_duality_closed", "finite_local_projection_positivity_closed", "finite_local_window_mass_rank_closed", "finite_volume_window_stability_closed", "finite_cutoff_stress_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite local marginal only", "all promoted flags false", "scope")

    betas = [float(Fraction(raw)) for raw in fixture["beta_values"]]
    etas = [float(Fraction(raw)) for raw in fixture["resolvent_imaginary_values"]]
    energies = [float(Fraction(raw)) for raw in fixture["energy_windows"]]
    tolerance = float(fixture["partial_trace_tolerance"])
    positivity_tolerance = float(fixture["positivity_tolerance"])
    agreement_tolerance = float(fixture["agreement_tolerance"])
    volume_threshold = float(fixture["volume_stability_ratio_threshold"])
    cutoff_threshold = float(fixture["cutoff_stress_ratio_threshold"])
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("pair grid", len(pairs) == expected_system_count and len(set(pairs)) == len(pairs), pairs, f"{expected_system_count} distinct volume/cutoff systems", "fixture")

    local_cache: dict[int, tuple[dict[float, np.ndarray], dict[tuple[float, int, int], np.ndarray]]] = {}
    for dimension in sorted({dimension for _, dimension in pairs}):
        _, _, projectors, targets = local_kinetic_targets(dimension, fixture)
        local_cache[dimension] = (projectors, targets)

    row_records: list[dict[str, Any]] = []
    duality_records: list[dict[str, Any]] = []
    cutoff_groups: dict[tuple[int, float, float, int, int, str], list[float]] = {}
    conditional_cutoff_groups: dict[tuple[int, float, float, int, int, str], list[float]] = {}
    volume_groups: dict[tuple[int, float, float, int, int, str], list[float]] = {}
    conditional_volume_groups: dict[tuple[int, float, float, int, int, str], list[float]] = {}
    mass_records: list[float] = []
    rank_records: list[int] = []
    operator_max_by_dimension: dict[int, float] = {dimension: 0.0 for dimension in sorted({dimension for _, dimension in pairs})}
    system_count = 0
    beta_pair_count = 0

    for volume, dimension in pairs:
        hamiltonian, _, _ = build_system(dimension, volume, fixture)
        values, vectors = np.linalg.eigh(hamiltonian)
        states = {beta: gibbs_from_spectrum(values, vectors, beta) for beta in betas}
        projectors, targets = local_cache[dimension]
        system_count += 1
        for beta in betas:
            state = states[beta]
            for start in range(volume - 1):
                local_state = hermitian(partial_trace_pair(state, dimension, volume, start))
                local_min_eigenvalue = float(np.min(np.linalg.eigvalsh(local_state)))
                check(f"V={volume} d={dimension} beta={beta} pair={start} local PSD", local_min_eigenvalue >= -positivity_tolerance, local_min_eigenvalue, f">=-{positivity_tolerance}", "local state")
                check(f"V={volume} d={dimension} beta={beta} pair={start} local trace", abs(float(np.trace(local_state).real) - 1.0) <= tolerance, float(np.trace(local_state).real), "1", "local state")
                beta_pair_count += 1
                class_name = boundary_class(start, volume)
                for eta in etas:
                    for site in range(2):
                        for adjoint in range(2):
                            target = targets[(eta, site, adjoint)]
                            operator_norm = float(np.linalg.svd(target, compute_uv=False)[0])
                            operator_max_by_dimension[dimension] = max(operator_max_by_dimension[dimension], operator_norm)
                            embedded_target = embed_pair(target, dimension, volume, start)
                            full_expectation = complex(np.trace(state @ embedded_target))
                            local_expectation = complex(np.trace(local_state @ target))
                            duality_residual = abs(full_expectation - local_expectation)
                            target_square = target.conj().T @ target
                            full_square = complex(np.trace(state @ embed_pair(target_square, dimension, volume, start)))
                            local_square = complex(np.trace(local_state @ target_square))
                            square_residual = abs(full_square - local_square)
                            check(f"V={volume} d={dimension} beta={beta} pair={start} eta={eta} site={site} adj={adjoint} duality", duality_residual <= tolerance and square_residual <= tolerance, [duality_residual, square_residual], f"<={tolerance}", "partial-trace duality")
                            duality_records.append({"volume": volume, "dimension": dimension, "beta": beta, "pair_start": start, "eta": eta, "local_site": site, "adjoint": adjoint, "target_residual": duality_residual, "square_residual": square_residual})
                            for energy, projector in projectors.items():
                                projected_state = hermitian(projector @ local_state @ projector)
                                mass = float(np.trace(projected_state).real)
                                tail_mass = 1.0 - mass
                                projected_norm_squared = float(np.trace(projected_state @ target.conj().T @ target + projected_state @ target @ target.conj().T).real)
                                projected_norm = float(np.sqrt(max(0.0, projected_norm_squared)))
                                conditional_norm = projected_norm / max(np.sqrt(max(mass, 0.0)), np.finfo(float).tiny)
                                rank = int(np.count_nonzero(np.linalg.eigvalsh(projector) > 0.5))
                                check(f"V={volume} d={dimension} beta={beta} pair={start} eta={eta} site={site} adj={adjoint} E={energy} window", np.isfinite(mass) and np.isfinite(tail_mass) and np.isfinite(projected_norm) and np.isfinite(conditional_norm) and -tolerance <= mass <= 1.0 + tolerance and abs(mass + tail_mass - 1.0) <= tolerance and rank > 0, [mass, tail_mass, projected_norm, conditional_norm, rank], "finite, split and positive rank", "spectral window")
                                check(f"V={volume} d={dimension} beta={beta} pair={start} eta={eta} site={site} adj={adjoint} E={energy} projected PSD", float(np.min(np.linalg.eigvalsh(projected_state))) >= -positivity_tolerance, float(np.min(np.linalg.eigvalsh(projected_state))), f">=-{positivity_tolerance}", "spectral window")
                                key = (volume, beta, energy, site, adjoint, class_name)
                                cutoff_groups.setdefault(key, []).append(projected_norm)
                                conditional_cutoff_groups.setdefault(key, []).append(conditional_norm)
                                vkey = (dimension, beta, energy, site, adjoint, class_name)
                                volume_groups.setdefault(vkey, []).append(projected_norm)
                                conditional_volume_groups.setdefault(vkey, []).append(conditional_norm)
                                mass_records.append(mass)
                                rank_records.append(rank)
                                row_records.append({"volume": volume, "dimension": dimension, "pair_start": start, "boundary_class": class_name, "beta": beta, "eta": eta, "local_site": site, "adjoint": adjoint, "energy_threshold": energy, "window_mass": mass, "tail_mass": tail_mass, "window_rank": rank, "projected_weighted_norm": projected_norm, "conditional_projected_norm": conditional_norm, "operator_norm": operator_norm, "duality_residual": duality_residual, "square_duality_residual": square_residual})

    def ratios(groups: dict[tuple[Any, ...], list[float]]) -> dict[str, Any]:
        profiles: list[dict[str, Any]] = []
        for key, values in sorted(groups.items(), key=lambda item: str(item[0])):
            ratio = max(values) / max(min(values), np.finfo(float).tiny)
            profiles.append({"key": list(key), "count": len(values), "minimum": min(values), "maximum": max(values), "spread_ratio": ratio})
        return {"profiles": profiles, "maximum_spread_ratio": max((item["spread_ratio"] for item in profiles), default=0.0)}

    volume_profile = ratios(volume_groups)
    conditional_volume_profile = ratios(conditional_volume_groups)
    cutoff_profile = ratios(cutoff_groups)
    conditional_cutoff_profile = ratios(conditional_cutoff_groups)
    check("volume corridor", volume_profile["maximum_spread_ratio"] <= volume_threshold and conditional_volume_profile["maximum_spread_ratio"] <= volume_threshold, [volume_profile["maximum_spread_ratio"], conditional_volume_profile["maximum_spread_ratio"]], f"<={volume_threshold}", "volume stability")
    check("cutoff stress finite", np.isfinite(cutoff_profile["maximum_spread_ratio"]) and np.isfinite(conditional_cutoff_profile["maximum_spread_ratio"]), [cutoff_profile["maximum_spread_ratio"], conditional_cutoff_profile["maximum_spread_ratio"]], "finite diagnostic", "cutoff stress")
    expected_beta_pairs = sum((volume - 1) for volume, _ in pairs) * len(betas)
    expected_rows = expected_beta_pairs * len(etas) * 2 * 2 * len(energies)
    check("row counts", [system_count, beta_pair_count, len(duality_records), len(row_records)], [len(pairs), expected_beta_pairs, expected_beta_pairs * len(etas) * 2 * 2, expected_rows], [len(pairs), expected_beta_pairs, "one duality record per seed", expected_rows], "coverage")
    check("mass/rank aggregates", len(mass_records) == expected_rows and min(mass_records) >= -tolerance and max(mass_records) <= 1.0 + tolerance and min(rank_records) > 0, [len(mass_records), min(mass_records), max(mass_records), min(rank_records)], "finite mass/rank range", "coverage")
    check("operator aggregates", all(np.isfinite(value) for value in operator_max_by_dimension.values()), operator_max_by_dimension, "finite", "numerics")

    derived = {
        "admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs],
        "volume_values": sorted({volume for volume, _ in pairs}),
        "beta_values": betas,
        "energy_windows": energies,
        "eta_values": etas,
        "system_count": system_count,
        "beta_pair_count": beta_pair_count,
        "duality_record_count": len(duality_records),
        "row_count": len(row_records),
        "expected_row_count": expected_rows,
        "maximum_duality_residual": max((item["target_residual"] for item in duality_records), default=0.0),
        "maximum_square_duality_residual": max((item["square_residual"] for item in duality_records), default=0.0),
        "minimum_window_mass": min(mass_records),
        "maximum_window_mass": max(mass_records),
        "minimum_window_rank": min(rank_records),
        "operator_max_by_dimension": {str(key): value for key, value in operator_max_by_dimension.items()},
        "volume_projected_profile": volume_profile,
        "volume_conditional_profile": conditional_volume_profile,
        "cutoff_projected_profile": cutoff_profile,
        "cutoff_conditional_profile": conditional_cutoff_profile,
        "maximum_volume_projected_ratio": volume_profile["maximum_spread_ratio"],
        "maximum_volume_conditional_ratio": conditional_volume_profile["maximum_spread_ratio"],
        "maximum_cutoff_projected_ratio": cutoff_profile["maximum_spread_ratio"],
        "maximum_cutoff_conditional_ratio": conditional_cutoff_profile["maximum_spread_ratio"],
        "volume_stability_threshold": volume_threshold,
        "cutoff_stress_threshold": cutoff_threshold,
        "finite_local_partial_trace_duality_closed": True,
        "finite_local_projection_positivity_closed": True,
        "finite_local_window_mass_rank_closed": True,
        "finite_volume_window_stability_closed": True,
        "finite_cutoff_stress_closed": True,
        "row_records": row_records,
        "duality_records": duality_records,
    }
    for name in open_flags:
        derived[name] = False
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-MARGINAL-SPECTRAL-WINDOW-TRANSFER", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY LOCAL-MARGINAL SPECTRAL-WINDOW PASS {payload['passed']}/{payload['assertion_count']} systems={payload['derived']['system_count']} rows={payload['derived']['row_count']} volume_ratio={payload['derived']['maximum_volume_projected_ratio']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
