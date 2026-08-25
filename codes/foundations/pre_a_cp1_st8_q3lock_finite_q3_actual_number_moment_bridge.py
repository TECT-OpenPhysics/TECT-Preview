#!/usr/bin/env python3
"""Primary finite-Q3 actual harmonic-number moment bridge for EXP-001106."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def edges_for(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(int(value) for value in edge) for edge in fixture["edges_by_volume"][str(volume)]]


def build_hamiltonian(volume: int, dimension: int, fixture: dict[str, Any], bond_coordinate: np.ndarray | None = None) -> np.ndarray:
    q, p = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_sites = [embed(q, site, volume, identity) for site in range(volume)]
    p_sites = [embed(p, site, volume, identity) for site in range(volume)]
    bond_single = q if bond_coordinate is None else bond_coordinate
    bond_sites = [embed(bond_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    terms: list[np.ndarray] = []
    for q_site, p_site in zip(q_sites, p_sites):
        terms.append(p_site @ p_site / (2.0 * chi) + r * (q_site @ q_site) / 2.0 + g * np.linalg.matrix_power(q_site, 4) / 4.0)
    for left, right in edges_for(volume, fixture):
        difference = bond_sites[left] - bond_sites[right]
        terms.append(c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (bond_sites[left] @ bond_sites[left] + bond_sites[right] @ bond_sites[right]) / 4.0)
    hamiltonian = sum(terms, np.zeros_like(q_sites[0]))
    return (hamiltonian + hamiltonian.conj().T) / 2.0


def local_onsite(dimension: int, fixture: dict[str, Any]) -> np.ndarray:
    q, p = oscillator(dimension)
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    shift = float(fixture["onsite_shift"])
    return (p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * np.linalg.matrix_power(q, 4) / 4.0 + shift * np.eye(dimension, dtype=complex))


def smooth_coordinate_cutoff(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted = values - float(np.min(values))
    weights = np.exp(-beta * shifted)
    return (vectors * weights) @ vectors.conj().T / float(np.sum(weights))


def number_site(dimension: int, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    diagonal = np.diag(np.arange(dimension, dtype=float)).astype(complex)
    return embed(diagonal, site, volume, identity)


def top_site(dimension: int, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    diagonal = np.zeros((dimension, dimension), dtype=complex)
    diagonal[-1, -1] = 1.0
    return embed(diagonal, site, volume, identity)


def expectation_state(state: np.ndarray, operator: np.ndarray) -> float:
    return float(np.real(np.trace(state @ operator)))


def expectation_vector(vector: np.ndarray, operator: np.ndarray) -> float:
    return float(np.real(np.vdot(vector, operator @ vector)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    tolerance = float(fixture["residual_tolerance"])
    moment_order = int(fixture["moment_order"])
    weighted_power = int(fixture["weighted_tail_power"])
    beta = float(fixture["beta"])
    hbar = float(fixture["hbar"])
    times = [float(value) for value in fixture["time_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001106" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001106/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("moment order", moment_order == 5 and weighted_power == 2, [moment_order, weighted_power], "[5,2]", "moment")
    check("two orientations", orientations == [-1, 1], orientations, "[-1,1]", "orientation")
    check("scope firewall", scope["finite_actual_gibbs_number_moment_closed"] and scope["finite_actual_history_number_moment_closed"] and not scope["energy_to_number_uniform_form_domination_closed"], scope, "finite only", "scope")

    volume_rows: list[dict[str, Any]] = []
    for volume in [int(value) for value in fixture["volume_values"]]:
        n_rows: list[dict[str, Any]] = []
        for dimension in [int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]]:
            identity = np.eye(dimension, dtype=complex)
            full_h = build_hamiltonian(volume, dimension, fixture)
            cutoff_q = smooth_coordinate_cutoff(oscillator(dimension)[0], float(fixture["cutoff_radius"]))
            cutoff_h = build_hamiltonian(volume, dimension, fixture, cutoff_q)
            tail = full_h - cutoff_h
            rho = gibbs(full_h, beta)
            local_k = local_onsite(dimension, fixture)
            local_k_power = np.linalg.matrix_power(local_k, moment_order)
            local_n = np.diag(np.arange(dimension, dtype=float)).astype(complex)
            local_n_power = np.linalg.matrix_power(local_n, moment_order)
            local_min = float(np.min(np.linalg.eigvalsh((local_k + local_k.conj().T) / 2.0)))
            check(f"V={volume} n={dimension} local k positive", local_min > 0.0, local_min, ">0", "onsite")
            number_moment_sites = [embed(local_n_power, site, volume, identity) for site in range(volume)]
            energy_moment_sites = [embed(local_k_power, site, volume, identity) for site in range(volume)]
            top_sites = [top_site(dimension, site, volume, identity) for site in range(volume)]
            gibbs_rows: list[dict[str, Any]] = []
            for site in range(volume):
                top_probability = max(0.0, expectation_state(rho, top_sites[site]))
                n_moment = expectation_state(rho, number_moment_sites[site])
                k_moment = expectation_state(rho, energy_moment_sites[site])
                markov_ratio = float((dimension - 1) ** moment_order * top_probability / n_moment) if n_moment > 100.0 * tolerance else 0.0
                check(f"V={volume} n={dimension} Gibbs trace", abs(float(np.trace(rho).real) - 1.0) <= tolerance, float(np.trace(rho).real), "1", "Gibbs")
                check(f"V={volume} n={dimension} Gibbs Markov site={site}", (dimension - 1) ** moment_order * top_probability <= n_moment + 100.0 * tolerance, [(dimension - 1) ** moment_order * top_probability, n_moment], "<=", "Markov")
                check(f"V={volume} n={dimension} Gibbs moments site={site}", np.isfinite(n_moment) and np.isfinite(k_moment) and n_moment >= -tolerance and k_moment >= -tolerance, [n_moment, k_moment], "finite nonnegative", "moments")
                gibbs_rows.append({"site": site, "top_probability": top_probability, "weighted_top_tail": float(dimension ** weighted_power * top_probability), "n_moment": n_moment, "k_moment": k_moment, "markov_ratio": markov_ratio, "n_to_k_ratio": float(n_moment / (1.0 + k_moment))})
            vacuum = np.zeros(dimension**volume, dtype=complex)
            vacuum[0] = 1.0
            history_rows: list[dict[str, Any]] = []
            for sign in orientations:
                for time in times:
                    propagator = unitary(full_h + sign * tail, time, hbar)
                    vector = propagator @ vacuum
                    unitarity = float(np.linalg.norm(propagator.conj().T @ propagator - np.eye(dimension**volume), ord=2))
                    check(f"V={volume} n={dimension} sign={sign} t={time} unitary", unitarity <= 100.0 * tolerance, unitarity, f"<={100.0 * tolerance}", "history")
                    site_rows: list[dict[str, Any]] = []
                    for site in range(volume):
                        top_probability = max(0.0, expectation_vector(vector, top_sites[site]))
                        n_moment = expectation_vector(vector, number_moment_sites[site])
                        k_moment = expectation_vector(vector, energy_moment_sites[site])
                        markov_ratio = float((dimension - 1) ** moment_order * top_probability / n_moment) if n_moment > 100.0 * tolerance else 0.0
                        check(f"V={volume} n={dimension} sign={sign} t={time} history Markov site={site}", (dimension - 1) ** moment_order * top_probability <= n_moment + 100.0 * tolerance, [(dimension - 1) ** moment_order * top_probability, n_moment], "<=", "Markov")
                        check(f"V={volume} n={dimension} sign={sign} t={time} history moments site={site}", np.isfinite(n_moment) and np.isfinite(k_moment) and n_moment >= -tolerance and k_moment >= -tolerance, [n_moment, k_moment], "finite nonnegative", "moments")
                        site_rows.append({"site": site, "top_probability": top_probability, "weighted_top_tail": float(dimension ** weighted_power * top_probability), "n_moment": n_moment, "k_moment": k_moment, "markov_ratio": markov_ratio, "n_to_k_ratio": float(n_moment / (1.0 + k_moment))})
                    history_rows.append({"sign": sign, "time": time, "unitarity_residual": unitarity, "site_rows": site_rows})
            n_rows.append({"n": dimension, "dimension": dimension**volume, "local_k_min": local_min, "gibbs_rows": gibbs_rows, "history_rows": history_rows, "gibbs_max_n_to_k_ratio": max(row["n_to_k_ratio"] for row in gibbs_rows), "history_max_n_to_k_ratio": max(row["n_to_k_ratio"] for history in history_rows for row in history["site_rows"])})
        volume_rows.append({"volume": volume, "edge_count": len(edges_for(volume, fixture)), "n_rows": n_rows})
        check(f"V={volume} cutoff sequence", [row["n"] for row in n_rows] == [int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]], [row["n"] for row in n_rows], fixture["oscillator_dimensions_by_volume"][str(volume)], "cutoff")
    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-Q3-ACTUAL-NUMBER-MOMENT-BRIDGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {"volume_rows": volume_rows, "finite_actual_gibbs_number_moment_closed": True, "finite_actual_history_number_moment_closed": True, "finite_markov_top_tail_bridge_closed": True, "finite_shifted_onsite_energy_comparison_closed": True, "energy_to_number_uniform_form_domination_closed": False, "q3_gibbs_weighted_tail_uniformity_closed": False, "q3_evolved_history_weighted_tail_uniformity_closed": False, "actual_unbounded_q3_domain_transfer_closed": False, "source_volume_orientation_history_uniform_closed": False, "direct_d_delta_d_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False},
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
    print(f"PRIMARY FINITE-Q3-ACTUAL-NUMBER-MOMENT-BRIDGE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
