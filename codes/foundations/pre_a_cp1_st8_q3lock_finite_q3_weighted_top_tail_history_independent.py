#!/usr/bin/env python3
"""Independent finite-Q3 weighted top-tail history audit for EXP-001097."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_q3_weighted_top_tail_history"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


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


def ladder(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((dimension, dimension), dtype=complex)
    for row in range(1, dimension):
        lower[row - 1, row] = np.sqrt(float(row))
    upper = lower.T.conj()
    coordinate = (lower + upper) / np.sqrt(2.0)
    momentum = (lower - upper) / (1j * np.sqrt(2.0))
    return coordinate, momentum


def site_operator(single: np.ndarray, site: int, volume: int, dimension: int) -> np.ndarray:
    identity = np.eye(dimension, dtype=complex)
    result = np.array([[1.0 + 0.0j]])
    for position in range(volume):
        result = np.kron(result, single if position == site else identity)
    return result


def graph(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [(int(edge[0]), int(edge[1])) for edge in fixture["edges_by_volume"][str(volume)]]


def hamiltonian(volume: int, dimension: int, fixture: dict[str, Any], bond_coordinate: np.ndarray | None = None) -> np.ndarray:
    coordinate, momentum = ladder(dimension)
    q_sites = [site_operator(coordinate, site, volume, dimension) for site in range(volume)]
    p_sites = [site_operator(momentum, site, volume, dimension) for site in range(volume)]
    bond_single = coordinate if bond_coordinate is None else bond_coordinate
    bond_sites = [site_operator(bond_single, site, volume, dimension) for site in range(volume)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    size = dimension**volume
    result = np.zeros((size, size), dtype=complex)
    for q_site, p_site in zip(q_sites, p_sites):
        result += p_site @ p_site / (2.0 * chi)
        result += r * q_site @ q_site / 2.0
        result += g * q_site @ q_site @ q_site @ q_site / 4.0
    for left, right in graph(volume, fixture):
        difference = bond_sites[left] - bond_sites[right]
        result += c * difference @ difference / 2.0
        result += lam * difference @ difference @ (bond_sites[left] @ bond_sites[left] + bond_sites[right] @ bond_sites[right]) / 4.0
    return (result + result.T.conj()) / 2.0


def cutoff_coordinate(coordinate: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((coordinate + coordinate.T.conj()) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.ones_like(values)
    taper[scaled >= 2.0] = 0.0
    middle = (scaled > 1.0) & (scaled < 2.0)
    taper[middle] = 0.5 * (1.0 + np.cos(np.pi * (scaled[middle] - 1.0)))
    return (vectors * (values * taper)) @ vectors.T.conj()


def spectral_unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T.conj()) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.T.conj()


def normalized_gibbs(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T.conj()) / 2.0)
    weights = np.exp(-beta * (values - values[0]))
    return (vectors * weights) @ vectors.T.conj() / np.sum(weights)


def top_site_projectors(volume: int, dimension: int) -> list[np.ndarray]:
    top = np.zeros((dimension, dimension), dtype=complex)
    top[dimension - 1, dimension - 1] = 1.0
    return [site_operator(top, site, volume, dimension) for site in range(volume)]


def weighted_vector_tail(vector: np.ndarray, projector: np.ndarray, dimension: int) -> float:
    overlap = float(np.real(np.vdot(vector, projector @ vector)))
    return float(dimension * dimension * max(0.0, overlap))


def weighted_state_tail(state: np.ndarray, projector: np.ndarray, dimension: int) -> float:
    overlap = float(np.real(np.trace(state @ projector)))
    return float(dimension * dimension * max(0.0, overlap))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001097" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001097/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("orientation list", fixture["orientation_values"] == [-1, 1], fixture["orientation_values"], "[-1,1]", "orientation")
    check("scope firewall", scope["finite_evolved_history_weighted_tail_closed"] and scope["finite_gibbs_weighted_tail_closed"] and not scope["source_volume_orientation_history_uniform_tail_closed"], scope, "finite only", "scope")

    tolerance = float(fixture["residual_tolerance"])
    beta = float(fixture["beta"])
    hbar = float(fixture["hbar"])
    times = [float(value) for value in fixture["time_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    volume_rows: list[dict[str, Any]] = []
    for volume in [int(value) for value in fixture["volume_values"]]:
        n_rows: list[dict[str, Any]] = []
        for dimension in [int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]]:
            coordinate, _ = ladder(dimension)
            full = hamiltonian(volume, dimension, fixture)
            cut = hamiltonian(volume, dimension, fixture, cutoff_coordinate(coordinate, float(fixture["cutoff_radius"])))
            perturbation = full - cut
            state = normalized_gibbs(full, beta)
            projectors = top_site_projectors(volume, dimension)
            vacuum = np.zeros(dimension**volume, dtype=complex)
            vacuum[0] = 1.0
            gibbs_tails = [weighted_state_tail(state, projector, dimension) for projector in projectors]
            check(f"V={volume} n={dimension} trace", abs(float(np.trace(state).real) - 1.0) <= tolerance, float(np.trace(state).real), "1", "Gibbs")
            check(f"V={volume} n={dimension} Gibbs finite", all(np.isfinite(value) and value >= 0.0 for value in gibbs_tails), gibbs_tails, "finite nonnegative", "Gibbs tail")
            history_rows: list[dict[str, Any]] = []
            for orientation in orientations:
                for time in times:
                    evolution = spectral_unitary(full + orientation * perturbation, time, hbar)
                    vector = evolution @ vacuum
                    residual = float(np.linalg.norm(evolution.T.conj() @ evolution - np.eye(dimension**volume), ord=2))
                    tails = [weighted_vector_tail(vector, projector, dimension) for projector in projectors]
                    check(f"V={volume} n={dimension} sign={orientation} t={time} unitary", residual <= 100.0 * tolerance, residual, f"<={100.0 * tolerance}", "history")
                    check(f"V={volume} n={dimension} sign={orientation} t={time} finite", all(np.isfinite(value) and value >= 0.0 for value in tails), tails, "finite nonnegative", "history tail")
                    history_rows.append({"sign": orientation, "time": time, "unitarity_residual": residual, "site_weighted_tails": tails, "max_weighted_tail": max(tails)})
            zero_time = [row["max_weighted_tail"] for row in history_rows if float(row["time"]) == 0.0]
            check(f"V={volume} n={dimension} vacuum anchor", all(value <= 100.0 * tolerance for value in zero_time), zero_time, f"<={100.0 * tolerance}", "history anchor")
            n_rows.append({"n": dimension, "dimension": dimension**volume, "gibbs_site_weighted_tails": gibbs_tails, "gibbs_max_weighted_tail": max(gibbs_tails), "history_rows": history_rows, "history_max_weighted_tail": max(row["max_weighted_tail"] for row in history_rows), "cutoff_tail_operator_norm": float(np.linalg.norm(perturbation, ord=2))})
        volume_rows.append({"volume": volume, "edge_count": len(graph(volume, fixture)), "n_rows": n_rows})
        check(f"V={volume} dimensions", [row["n"] for row in n_rows] == [int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]], [row["n"] for row in n_rows], fixture["oscillator_dimensions_by_volume"][str(volume)], "cutoff")

    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-Q3-WEIGHTED-TOP-TAIL-HISTORY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "finite_evolved_history_weighted_tail_closed": True,
            "finite_gibbs_weighted_tail_closed": True,
            "two_orientation_fixture_closed": True,
            "positive_time_fixture_closed": True,
            "source_volume_orientation_history_uniform_tail_closed": False,
            "actual_unbounded_q3_domain_transfer_closed": False,
            "source_volume_uniform_modular_history_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-Q3-WEIGHTED-TOP-TAIL-HISTORY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
