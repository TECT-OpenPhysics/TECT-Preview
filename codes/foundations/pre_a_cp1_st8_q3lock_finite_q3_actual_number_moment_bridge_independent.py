#!/usr/bin/env python3
"""Independent finite-Q3 actual harmonic-number moment bridge for EXP-001106."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_q3_actual_number_moment_bridge"
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
    return (lower + upper) / np.sqrt(2.0), (lower - upper) / (1j * np.sqrt(2.0))


def tensor_site(single: np.ndarray, site: int, volume: int, dimension: int) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    identity = np.eye(dimension, dtype=complex)
    for position in range(volume):
        result = np.kron(result, single if position == site else identity)
    return result


def repeated_power(matrix: np.ndarray, order: int) -> np.ndarray:
    result = np.eye(matrix.shape[0], dtype=complex)
    for _ in range(order):
        result = result @ matrix
    return result


def graph(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [(int(edge[0]), int(edge[1])) for edge in fixture["edges_by_volume"][str(volume)]]


def hamiltonian(volume: int, dimension: int, fixture: dict[str, Any], cutoff: np.ndarray | None = None) -> np.ndarray:
    coordinate, momentum = ladder(dimension)
    q_sites = [tensor_site(coordinate, site, volume, dimension) for site in range(volume)]
    p_sites = [tensor_site(momentum, site, volume, dimension) for site in range(volume)]
    bond_coordinate = coordinate if cutoff is None else cutoff
    bond_sites = [tensor_site(bond_coordinate, site, volume, dimension) for site in range(volume)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    result = np.zeros((dimension**volume, dimension**volume), dtype=complex)
    for q_site, p_site in zip(q_sites, p_sites):
        result += p_site @ p_site / (2.0 * chi) + r * (q_site @ q_site) / 2.0 + g * repeated_power(q_site, 4) / 4.0
    for left, right in graph(volume, fixture):
        difference = bond_sites[left] - bond_sites[right]
        result += c * difference @ difference / 2.0 + lam * difference @ difference @ (bond_sites[left] @ bond_sites[left] + bond_sites[right] @ bond_sites[right]) / 4.0
    return (result + result.T.conj()) / 2.0


def onsite(dimension: int, fixture: dict[str, Any]) -> np.ndarray:
    coordinate, momentum = ladder(dimension)
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    shift = float(fixture["onsite_shift"])
    return momentum @ momentum / (2.0 * chi) + r * coordinate @ coordinate / 2.0 + g * repeated_power(coordinate, 4) / 4.0 + shift * np.eye(dimension, dtype=complex)


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


def expectation_density(state: np.ndarray, operator: np.ndarray) -> float:
    return float(np.real(np.trace(state @ operator)))


def expectation_vector(vector: np.ndarray, operator: np.ndarray) -> float:
    return float(np.real(np.vdot(vector, operator @ vector)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["residual_tolerance"])
    order, weight_power = int(fixture["moment_order"]), int(fixture["weighted_tail_power"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001106" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001106/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("moment order", order == 5 and weight_power == 2, [order, weight_power], "[5,2]", "moment")
    check("scope firewall", scope["finite_actual_gibbs_number_moment_closed"] and scope["finite_actual_history_number_moment_closed"] and not scope["energy_to_number_uniform_form_domination_closed"], scope, "finite only", "scope")
    volume_rows: list[dict[str, Any]] = []
    for volume in [int(value) for value in fixture["volume_values"]]:
        n_rows: list[dict[str, Any]] = []
        for dimension in [int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]]:
            coordinate, _ = ladder(dimension)
            identity = np.eye(dimension, dtype=complex)
            full = hamiltonian(volume, dimension, fixture)
            cut = hamiltonian(volume, dimension, fixture, cutoff_coordinate(coordinate, float(fixture["cutoff_radius"])))
            perturbation = full - cut
            density = normalized_gibbs(full, float(fixture["beta"]))
            k_single = onsite(dimension, fixture)
            n_single = np.diag(np.arange(dimension, dtype=float)).astype(complex)
            k_power, n_power = repeated_power(k_single, order), repeated_power(n_single, order)
            k_min = float(np.min(np.linalg.eigvalsh((k_single + k_single.T.conj()) / 2.0)))
            check(f"V={volume} n={dimension} local k positive", k_min > 0.0, k_min, ">0", "onsite")
            n_ops = [tensor_site(n_power, site, volume, dimension) for site in range(volume)]
            k_ops = [tensor_site(k_power, site, volume, dimension) for site in range(volume)]
            top_single = np.zeros((dimension, dimension), dtype=complex)
            top_single[-1, -1] = 1.0
            top_ops = [tensor_site(top_single, site, volume, dimension) for site in range(volume)]
            gibbs_rows: list[dict[str, Any]] = []
            for site, (top_op, n_op, k_op) in enumerate(zip(top_ops, n_ops, k_ops)):
                top_probability = max(0.0, expectation_density(density, top_op))
                n_moment, k_moment = expectation_density(density, n_op), expectation_density(density, k_op)
                bound = float((dimension - 1) ** order * top_probability)
                check(f"V={volume} n={dimension} Gibbs Markov site={site}", bound <= n_moment + 100.0 * tolerance, [bound, n_moment], "<=", "Markov")
                check(f"V={volume} n={dimension} Gibbs moments site={site}", np.isfinite(n_moment) and np.isfinite(k_moment) and n_moment >= -tolerance and k_moment >= -tolerance, [n_moment, k_moment], "finite nonnegative", "moments")
                gibbs_rows.append({"site": site, "top_probability": top_probability, "weighted_top_tail": float(dimension**weight_power * top_probability), "n_moment": n_moment, "k_moment": k_moment, "markov_ratio": float(bound / n_moment) if n_moment > 100.0 * tolerance else 0.0, "n_to_k_ratio": float(n_moment / (1.0 + k_moment))})
            vacuum = np.zeros(dimension**volume, dtype=complex)
            vacuum[0] = 1.0
            history_rows: list[dict[str, Any]] = []
            for sign in [int(value) for value in fixture["orientation_values"]]:
                for time in [float(value) for value in fixture["time_values"]]:
                    evolution = spectral_unitary(full + sign * perturbation, time, float(fixture["hbar"]))
                    vector = evolution @ vacuum
                    residual = float(np.linalg.norm(evolution.T.conj() @ evolution - np.eye(dimension**volume), ord=2))
                    check(f"V={volume} n={dimension} sign={sign} t={time} unitary", residual <= 100.0 * tolerance, residual, f"<={100.0 * tolerance}", "history")
                    site_rows: list[dict[str, Any]] = []
                    for site, (top_op, n_op, k_op) in enumerate(zip(top_ops, n_ops, k_ops)):
                        top_probability = max(0.0, expectation_vector(vector, top_op))
                        n_moment, k_moment = expectation_vector(vector, n_op), expectation_vector(vector, k_op)
                        bound = float((dimension - 1) ** order * top_probability)
                        check(f"V={volume} n={dimension} sign={sign} t={time} history Markov site={site}", bound <= n_moment + 100.0 * tolerance, [bound, n_moment], "<=", "Markov")
                        check(f"V={volume} n={dimension} sign={sign} t={time} history moments site={site}", np.isfinite(n_moment) and np.isfinite(k_moment) and n_moment >= -tolerance and k_moment >= -tolerance, [n_moment, k_moment], "finite nonnegative", "moments")
                        site_rows.append({"site": site, "top_probability": top_probability, "weighted_top_tail": float(dimension**weight_power * top_probability), "n_moment": n_moment, "k_moment": k_moment, "markov_ratio": float(bound / n_moment) if n_moment > 100.0 * tolerance else 0.0, "n_to_k_ratio": float(n_moment / (1.0 + k_moment))})
                    history_rows.append({"sign": sign, "time": time, "unitarity_residual": residual, "site_rows": site_rows})
            n_rows.append({"n": dimension, "dimension": dimension**volume, "local_k_min": k_min, "gibbs_rows": gibbs_rows, "history_rows": history_rows, "gibbs_max_n_to_k_ratio": max(item["n_to_k_ratio"] for item in gibbs_rows), "history_max_n_to_k_ratio": max(item["n_to_k_ratio"] for history in history_rows for item in history["site_rows"])})
        volume_rows.append({"volume": volume, "edge_count": len(graph(volume, fixture)), "n_rows": n_rows})
        check(f"V={volume} cutoff sequence", [row["n"] for row in n_rows] == [int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]], [row["n"] for row in n_rows], fixture["oscillator_dimensions_by_volume"][str(volume)], "cutoff")
    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-Q3-ACTUAL-NUMBER-MOMENT-BRIDGE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "finite_actual_gibbs_number_moment_closed": True, "finite_actual_history_number_moment_closed": True, "finite_markov_top_tail_bridge_closed": True, "finite_shifted_onsite_energy_comparison_closed": True, "energy_to_number_uniform_form_domination_closed": False, "q3_gibbs_weighted_tail_uniformity_closed": False, "q3_evolved_history_weighted_tail_uniformity_closed": False, "actual_unbounded_q3_domain_transfer_closed": False, "source_volume_orientation_history_uniform_closed": False, "direct_d_delta_d_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-Q3-ACTUAL-NUMBER-MOMENT-BRIDGE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
