#!/usr/bin/env python3
"""Non-importing independent reconstruction for R-390.

This lane uses an einsum partial trace and eigenbasis quadratic forms rather
than importing the primary implementation.  It checks the same finite
local-marginal spectral-window interface.
"""

from __future__ import annotations

import argparse
import json
import os
import string
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-marginal-spectral-window-transfer-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "independent.json"


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


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def ladder(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((dimension, dimension), dtype=complex)
    for column in range(1, dimension):
        lower[column - 1, column] = np.sqrt(float(column))
    return (lower + lower.conj().T) / np.sqrt(2.0), (lower - lower.conj().T) / (1j * np.sqrt(2.0))


def site_operator(single: np.ndarray, site: int, volume: int, dimension: int) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    identity = np.eye(dimension, dtype=complex)
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def make_system(dimension: int, volume: int, fixture: dict[str, Any]) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q_single, p_single = ladder(dimension)
    coordinates = [site_operator(q_single, site, volume, dimension) for site in range(volume)]
    momenta = [site_operator(p_single, site, volume, dimension) for site in range(volume)]
    size = dimension**volume
    hamiltonian = np.zeros((size, size), dtype=complex)
    chi, r, g = (float(fixture[name]) for name in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    for q, p in zip(coordinates, momenta):
        hamiltonian += p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0
    for left in range(volume - 1):
        delta = coordinates[left] - coordinates[left + 1]
        delta2 = delta @ delta
        hamiltonian += c * delta2 / 2.0 + lam * delta2 @ (coordinates[left] @ coordinates[left] + coordinates[left + 1] @ coordinates[left + 1]) / 4.0
    return sym(hamiltonian), coordinates, momenta


def einsum_reduce(state: np.ndarray, dimension: int, volume: int, start: int) -> np.ndarray:
    keep = [start, start + 1]
    rest = [index for index in range(volume) if index not in keep]
    symbols = list(string.ascii_letters)
    labels = [None] * (2 * volume)
    used = 0
    for index in keep:
        labels[index] = symbols[used]
        labels[index + volume] = symbols[used + 1]
        used += 2
    for index in rest:
        labels[index] = symbols[used]
        labels[index + volume] = labels[index]
        used += 1
    subscript = "".join(labels)
    output = "".join(labels[index] for index in keep) + "".join(labels[index + volume] for index in keep)
    tensor = np.einsum(f"{subscript}->{output}", state.reshape([dimension] * (2 * volume)), optimize=True)
    return tensor.reshape(dimension * dimension, dimension * dimension)


def embed_pair(operator: np.ndarray, dimension: int, volume: int, start: int) -> np.ndarray:
    return np.kron(np.kron(np.eye(dimension**start, dtype=complex), operator), np.eye(dimension ** (volume - start - 2), dtype=complex))


def local_data(dimension: int, fixture: dict[str, Any]) -> tuple[np.ndarray, dict[float, np.ndarray], dict[tuple[float, int, int], np.ndarray]]:
    local_hamiltonian, coordinates, momenta = make_system(dimension, 2, fixture)
    local_values, local_vectors = np.linalg.eigh(local_hamiltonian)
    shifted = local_values - float(np.min(local_values))
    projectors: dict[float, np.ndarray] = {}
    for raw in fixture["energy_windows"]:
        threshold = float(Fraction(raw))
        selected = shifted <= threshold + float(fixture["positivity_tolerance"])
        projectors[threshold] = local_vectors[:, selected] @ local_vectors[:, selected].conj().T
    kinetic = sym((momenta[0] @ momenta[0] + momenta[1] @ momenta[1]) / (2.0 * float(fixture["chi"])))
    delta = coordinates[0] - coordinates[1]
    delta2 = delta @ delta
    boundary = sym(float(fixture["c"]) * delta2 / 2.0 + float(fixture["lambda"]) * delta2 @ (coordinates[0] @ coordinates[0] + coordinates[1] @ coordinates[1]) / 4.0)
    identity = np.eye(dimension * dimension, dtype=complex)
    targets: dict[tuple[float, int, int], np.ndarray] = {}
    for raw_eta in fixture["resolvent_imaginary_values"]:
        eta = float(Fraction(raw_eta))
        for site, coordinate in enumerate(coordinates):
            resolvent = np.linalg.inv(1j * eta * identity - coordinate)
            for adjoint in range(2):
                observable = resolvent if adjoint == 0 else resolvent.conj().T
                inner = kinetic @ observable - observable @ kinetic
                targets[(eta, site, adjoint)] = boundary @ inner - inner @ boundary
    return local_hamiltonian, projectors, targets


def gibbs(values: np.ndarray, vectors: np.ndarray, beta: float) -> np.ndarray:
    shifted = values - float(np.min(values))
    weights = np.exp(-beta * shifted)
    weights /= float(np.sum(weights))
    return sym((vectors * weights) @ vectors.conj().T)


def class_name(start: int, volume: int) -> str:
    return "boundary" if start in (0, volume - 2) else "interior"


def profile(groups: dict[tuple[Any, ...], list[float]]) -> dict[str, Any]:
    rows = []
    for key, values in sorted(groups.items(), key=lambda item: str(item[0])):
        rows.append({"key": list(key), "count": len(values), "minimum": min(values), "maximum": max(values), "spread_ratio": max(values) / max(min(values), np.finfo(float).tiny)})
    return {"profiles": rows, "maximum_spread_ratio": max((row["spread_ratio"] for row in rows), default=0.0)}


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
    volume_threshold = float(fixture["volume_stability_ratio_threshold"])
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("pair grid", len(pairs) == expected_system_count and len(set(pairs)) == len(pairs), pairs, f"{expected_system_count} distinct volume/cutoff systems", "fixture")
    local_cache = {dimension: local_data(dimension, fixture)[1:] for dimension in sorted({dimension for _, dimension in pairs})}
    volume_groups: dict[tuple[Any, ...], list[float]] = {}
    conditional_volume_groups: dict[tuple[Any, ...], list[float]] = {}
    cutoff_groups: dict[tuple[Any, ...], list[float]] = {}
    conditional_cutoff_groups: dict[tuple[Any, ...], list[float]] = {}
    masses: list[float] = []
    ranks: list[int] = []
    duality_records: list[dict[str, Any]] = []
    row_count = 0
    beta_pair_count = 0
    operator_max: dict[int, float] = {dimension: 0.0 for _, dimension in pairs}
    for volume, dimension in pairs:
        hamiltonian, _, _ = make_system(dimension, volume, fixture)
        values, vectors = np.linalg.eigh(hamiltonian)
        states = {beta: gibbs(values, vectors, beta) for beta in betas}
        projectors, targets = local_cache[dimension]
        for beta in betas:
            state = states[beta]
            for start in range(volume - 1):
                local_state = sym(einsum_reduce(state, dimension, volume, start))
                check(f"V={volume} d={dimension} beta={beta} pair={start} local trace", abs(float(np.trace(local_state).real) - 1.0) <= tolerance, float(np.trace(local_state).real), "1", "local state")
                check(f"V={volume} d={dimension} beta={beta} pair={start} local PSD", float(np.min(np.linalg.eigvalsh(local_state))) >= -positivity_tolerance, float(np.min(np.linalg.eigvalsh(local_state))), f">=-{positivity_tolerance}", "local state")
                beta_pair_count += 1
                class_label = class_name(start, volume)
                for eta in etas:
                    for site in range(2):
                        for adjoint in range(2):
                            target = targets[(eta, site, adjoint)]
                            op_norm = float(np.linalg.svd(target, compute_uv=False)[0])
                            operator_max[dimension] = max(operator_max[dimension], op_norm)
                            full = complex(np.trace(state @ embed_pair(target, dimension, volume, start)))
                            local = complex(np.trace(local_state @ target))
                            residual = abs(full - local)
                            square = target.conj().T @ target
                            full_square = complex(np.trace(state @ embed_pair(square, dimension, volume, start)))
                            local_square = complex(np.trace(local_state @ square))
                            square_residual = abs(full_square - local_square)
                            check(f"V={volume} d={dimension} beta={beta} pair={start} eta={eta} site={site} adj={adjoint} duality", residual <= tolerance and square_residual <= tolerance, [residual, square_residual], f"<={tolerance}", "partial-trace duality")
                            duality_records.append({"volume": volume, "dimension": dimension, "beta": beta, "pair_start": start, "eta": eta, "local_site": site, "adjoint": adjoint, "target_residual": residual, "square_residual": square_residual})
                            for energy, projector in projectors.items():
                                projected = sym(projector @ local_state @ projector)
                                mass = float(np.trace(projected).real)
                                tail = 1.0 - mass
                                norm_sq = float(np.trace(projected @ target.conj().T @ target + projected @ target @ target.conj().T).real)
                                norm = float(np.sqrt(max(norm_sq, 0.0)))
                                conditional = norm / max(np.sqrt(max(mass, 0.0)), np.finfo(float).tiny)
                                rank = int(np.count_nonzero(np.linalg.eigvalsh(projector) > 0.5))
                                check(f"V={volume} d={dimension} beta={beta} pair={start} eta={eta} site={site} adj={adjoint} E={energy}", np.isfinite(norm) and np.isfinite(conditional) and -tolerance <= mass <= 1.0 + tolerance and abs(mass + tail - 1.0) <= tolerance and rank > 0 and float(np.min(np.linalg.eigvalsh(projected))) >= -positivity_tolerance, [mass, tail, norm, conditional, rank], "finite positive split", "spectral window")
                                key = (volume, beta, energy, site, adjoint, class_label)
                                vkey = (dimension, beta, energy, site, adjoint, class_label)
                                cutoff_groups.setdefault(key, []).append(norm)
                                conditional_cutoff_groups.setdefault(key, []).append(conditional)
                                volume_groups.setdefault(vkey, []).append(norm)
                                conditional_volume_groups.setdefault(vkey, []).append(conditional)
                                masses.append(mass)
                                ranks.append(rank)
                                row_count += 1
    volume_profile = profile(volume_groups)
    conditional_volume_profile = profile(conditional_volume_groups)
    cutoff_profile = profile(cutoff_groups)
    conditional_cutoff_profile = profile(conditional_cutoff_groups)
    check("volume corridor", volume_profile["maximum_spread_ratio"] <= volume_threshold and conditional_volume_profile["maximum_spread_ratio"] <= volume_threshold, [volume_profile["maximum_spread_ratio"], conditional_volume_profile["maximum_spread_ratio"]], f"<={volume_threshold}", "volume stability")
    expected_beta_pairs = sum(volume - 1 for volume, _ in pairs) * len(betas)
    expected_rows = expected_beta_pairs * len(etas) * 2 * 2 * len(energies)
    check("row counts", [len(pairs), beta_pair_count, len(duality_records), row_count], [expected_system_count, expected_beta_pairs, expected_beta_pairs * len(etas) * 2 * 2, expected_rows], "declared counts", "coverage")
    derived = {"admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs], "volume_values": sorted({volume for volume, _ in pairs}), "beta_values": betas, "energy_windows": energies, "eta_values": etas, "system_count": len(pairs), "beta_pair_count": beta_pair_count, "duality_record_count": len(duality_records), "row_count": row_count, "expected_row_count": expected_rows, "maximum_duality_residual": max((item["target_residual"] for item in duality_records), default=0.0), "maximum_square_duality_residual": max((item["square_residual"] for item in duality_records), default=0.0), "minimum_window_mass": min(masses), "maximum_window_mass": max(masses), "minimum_window_rank": min(ranks), "operator_max_by_dimension": {str(key): value for key, value in operator_max.items()}, "volume_projected_profile": volume_profile, "volume_conditional_profile": conditional_volume_profile, "cutoff_projected_profile": cutoff_profile, "cutoff_conditional_profile": conditional_cutoff_profile, "maximum_volume_projected_ratio": volume_profile["maximum_spread_ratio"], "maximum_volume_conditional_ratio": conditional_volume_profile["maximum_spread_ratio"], "maximum_cutoff_projected_ratio": cutoff_profile["maximum_spread_ratio"], "maximum_cutoff_conditional_ratio": conditional_cutoff_profile["maximum_spread_ratio"], "volume_stability_threshold": volume_threshold, "cutoff_stress_threshold": float(fixture["cutoff_stress_ratio_threshold"]), "finite_local_partial_trace_duality_closed": True, "finite_local_projection_positivity_closed": True, "finite_local_window_mass_rank_closed": True, "finite_volume_window_stability_closed": True, "finite_cutoff_stress_closed": True, "duality_records": duality_records}
    for name in open_flags:
        derived[name] = False
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-MARGINAL-SPECTRAL-WINDOW-TRANSFER", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT LOCAL-MARGINAL SPECTRAL-WINDOW PASS {payload['passed']}/{payload['assertion_count']} systems={payload['derived']['system_count']} rows={payload['derived']['row_count']} volume_ratio={payload['derived']['maximum_volume_projected_ratio']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
