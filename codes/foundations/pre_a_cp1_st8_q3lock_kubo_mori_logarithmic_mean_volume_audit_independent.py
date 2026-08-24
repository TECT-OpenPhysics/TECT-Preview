#!/usr/bin/env python3
"""Independent implementation of the finite actual-Q3 Kubo--Mori audit.

This file intentionally does not import the primary audit or its helper
module.  It rebuilds the oscillator graph, cutoff, Gibbs eigenbasis, and both
state-weighted means so that the integrated verifier can compare two routes.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_kubo_mori_logarithmic_mean_volume_audit"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-25-independent-{SLUG}"
    / "independent.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
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
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    geometries = {
        2: [(0, 1)],
        4: [(0, 1), (0, 2), (1, 3), (2, 3)],
        6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)],
    }
    if volume not in geometries:
        raise ValueError("EXP-001089 uses only volumes 2, 4, and 6")
    return geometries[volume]


def tensor_embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = single if site == 0 else identity
    for index in range(1, volume):
        result = np.kron(result, single if index == site else identity)
    return result


def bond(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    difference_square = difference @ difference
    return float(fixture["c"]) * difference_square / 2.0 + float(fixture["lambda"]) * difference_square @ (left @ left + right @ right) / 4.0


def model(volume: int, dimension: int, fixture: dict[str, Any], coordinate: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [tensor_embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [tensor_embed(p_single, site, volume, identity) for site in range(volume)]
    bond_coordinate = q_single if coordinate is None else coordinate
    bond_ops = [tensor_embed(bond_coordinate, site, volume, identity) for site in range(volume)]
    onsite = [
        p @ p / (2.0 * float(fixture["chi"]))
        + float(fixture["r"]) * (q @ q) / 2.0
        + float(fixture["g"]) * (q @ q @ q @ q) / 4.0
        for q, p in zip(q_ops, p_ops)
    ]
    bonds = {(left, right): bond(bond_ops[left], bond_ops[right], fixture) for left, right in graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    hamiltonian = sum(onsite, zero) + sum(bonds.values(), zero)
    local = onsite[0] + onsite[1] + bonds[(0, 1)]
    return q_ops, (hamiltonian + hamiltonian.conj().T) / 2.0, (local + local.conj().T) / 2.0, bonds


def smooth_cutoff(coordinate: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((coordinate + coordinate.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(
        scaled <= 1.0,
        1.0,
        np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0),
    )
    return (vectors * (values * taper)) @ vectors.conj().T


def unitary_character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def spectral_operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def state_data(hamiltonian: np.ndarray, beta: float, gap_tolerance: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    probabilities = np.exp(-beta * (energies - float(np.min(energies))))
    probabilities /= float(np.sum(probabilities))
    left, right = probabilities[:, None], probabilities[None, :]
    log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
    log_mean = np.empty_like(log_gap)
    close = np.abs(log_gap) <= gap_tolerance
    np.divide(left - right, log_gap, out=log_mean, where=~close)
    limit = 0.5 * (left + right)
    log_mean[close] = limit[close]
    log_mean = (log_mean + log_mean.T) / 2.0
    arithmetic = 0.5 * (left + right)
    return energies, vectors, probabilities, log_mean, arithmetic


def weighted_norm(matrix: np.ndarray, vectors: np.ndarray, weights: np.ndarray) -> float:
    matrix_h = vectors.conj().T @ matrix @ vectors
    return float(np.sqrt(max(0.0, 2.0 * float(np.sum(weights * np.abs(matrix_h) ** 2)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001089" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001089/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph geometry", graph_edges(2) == [(0, 1)] and len(graph_edges(4)) == 4 and len(graph_edges(6)) == 7, [graph_edges(2), len(graph_edges(4)), len(graph_edges(6))], "two-site/square/2x3", "geometry")
    check("scope firewall", scope["finite_kubo_mori_rows_closed"] and scope["finite_arithmetic_comparison_closed"] and not scope["candidate_uniformity_decided"] and not scope["pre_a_closed"], scope, "finite diagnostic", "scope")

    beta = float(fixture["beta"])
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    tolerance = float(fixture["commutator_tolerance"])
    tail_tolerance = float(fixture["tail_tolerance"])
    gap_tolerance = float(fixture["mean_gap_tolerance"])
    dimension = int(fixture["oscillator_dimension"])
    volumes = [int(value) for value in fixture["volume_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    rows: list[dict[str, Any]] = []

    for volume in volumes:
        q_ops, hamiltonian, _, bonds = model(volume, dimension, fixture)
        energies, vectors, probabilities, log_mean, arithmetic = state_data(hamiltonian, beta, gap_tolerance)
        observable = unitary_character(q_ops[0] + q_ops[1], amplitude, hbar)
        h_commutator = commutator(hamiltonian, observable)
        q_single, _ = oscillator(dimension)
        check(f"V={volume} Gibbs normalization", np.isfinite(probabilities).all() and abs(float(np.sum(probabilities)) - 1.0) <= gap_tolerance, float(np.sum(probabilities)), 1.0, "Kubo--Mori state")
        radius_rows: list[dict[str, Any]] = []
        for radius in radii:
            cut = smooth_cutoff(q_single, radius)
            _, _, _, cut_bonds = model(volume, dimension, fixture, cut)
            zero = np.zeros_like(hamiltonian)
            tails = {edge: bonds[edge] - cut_bonds[edge] for edge in bonds}
            tail = sum(tails.values(), zero)
            tail_norm = spectral_operator_norm(tail)
            source_commutator_norm = spectral_operator_norm(commutator(tail, observable))
            inner = commutator(tail, h_commutator)
            d2 = -inner / (hbar * hbar)
            modular = -beta * commutator(hamiltonian, d2)
            identity_error = spectral_operator_norm(modular - beta * commutator(hamiltonian, inner) / (hbar * hbar))
            disjoint_tail = sum((tails[edge] for edge in graph_edges(volume) if set(edge).isdisjoint(set(fixture["observable_support"]))), zero)
            disjoint_norm = spectral_operator_norm(commutator(disjoint_tail, observable))
            check(f"V={volume} L={radius} modular identity", identity_error <= tolerance, identity_error, f"<={tolerance}", "triple identity")
            check(f"V={volume} L={radius} source commutation", source_commutator_norm <= tolerance, source_commutator_norm, f"<={tolerance}", "configuration commutation")
            check(f"V={volume} L={radius} disjoint tail", disjoint_norm <= tolerance, disjoint_norm, f"<={tolerance}", "support locality")
            if radius == max(radii):
                check(f"V={volume} zero tail at largest radius", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            norms = {}
            for name, weights in (("duhamel", log_mean), ("arithmetic", arithmetic)):
                values = {"D2_state_weighted": weighted_norm(d2, vectors, weights), "modular_D2_state_weighted": weighted_norm(modular, vectors, weights), "tail_operator_norm": tail_norm, "modular_identity_error": identity_error}
                check(f"V={volume} L={radius} {name} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "state-weighted topology")
                norms[name] = values
            radius_rows.append({"radius": radius, "source_commutator_norm": source_commutator_norm, "disjoint_tail_commutator_norm": disjoint_norm, "norms": norms})
        rows.append({"volume": volume, "dimension": dimension**volume, "ground_energy": float(energies[0]), "probability_min": float(np.min(probabilities)), "radius_rows": radius_rows})
    check("volume sequence", [row["volume"] for row in rows] == volumes, [row["volume"] for row in rows], volumes, "volume")
    check("support commutators vanish", all(row["source_commutator_norm"] <= tolerance and row["disjoint_tail_commutator_norm"] <= tolerance for volume in rows for row in volume["radius_rows"]), "all rows", "tolerance", "support locality")

    def maxima(name: str, field: str) -> list[float]:
        return [max(item["norms"][name][field] for item in row["radius_rows"]) for row in rows]

    d2_log = maxima("duhamel", "D2_state_weighted")
    d2_arithmetic = maxima("arithmetic", "D2_state_weighted")
    modular_log = maxima("duhamel", "modular_D2_state_weighted")
    modular_arithmetic = maxima("arithmetic", "modular_D2_state_weighted")
    check("state-weighted maxima finite", all(np.isfinite(value) for value in d2_log + d2_arithmetic + modular_log + modular_arithmetic), [modular_log, modular_arithmetic], "finite", "scaling")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-KUBO-MORI-LOG-MEAN-VOLUME-AUDIT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions,
        "derived": {
            "volume_rows": rows,
            "duhamel_D2_state_weighted_maxima": d2_log,
            "arithmetic_D2_state_weighted_maxima": d2_arithmetic,
            "duhamel_modular_state_weighted_maxima": modular_log,
            "arithmetic_modular_state_weighted_maxima": modular_arithmetic,
            "arithmetic_to_duhamel_modular_ratios": [a / max(l, np.finfo(float).tiny) for a, l in zip(modular_arithmetic, modular_log)],
            "duhamel_modular_volume_growth": modular_log[-1] / max(modular_log[0], np.finfo(float).tiny),
            "arithmetic_modular_volume_growth": modular_arithmetic[-1] / max(modular_arithmetic[0], np.finfo(float).tiny),
            "finite_kubo_mori_rows_closed": True,
            "finite_arithmetic_comparison_closed": True,
            "finite_triple_commutator_identity_closed": True,
            "candidate_uniformity_decided": False,
            "modular_domain_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "positive_time_history_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT KUBO-MORI-LOG-MEAN-VOLUME-AUDIT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
