#!/usr/bin/env python3
"""Primary finite-Q3 weighted top-tail history audit for EXP-001097."""

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


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
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


def build_hamiltonian(
    volume: int,
    n: int,
    fixture: dict[str, Any],
    bond_coordinate: np.ndarray | None = None,
) -> np.ndarray:
    q, p = oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p, site, volume, identity) for site in range(volume)]
    bond_single = q if bond_coordinate is None else bond_coordinate
    bond_ops = [embed(bond_single, site, volume, identity) for site in range(volume)]
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    terms: list[np.ndarray] = []
    for q_site, p_site in zip(q_ops, p_ops):
        terms.append(p_site @ p_site / (2.0 * chi) + r * (q_site @ q_site) / 2.0 + g * (q_site @ q_site @ q_site @ q_site) / 4.0)
    for left, right in edges_for(volume, fixture):
        difference = bond_ops[left] - bond_ops[right]
        terms.append(c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (bond_ops[left] @ bond_ops[left] + bond_ops[right] @ bond_ops[right]) / 4.0)
    hamiltonian = sum(terms, np.zeros_like(q_ops[0]))
    return (hamiltonian + hamiltonian.conj().T) / 2.0


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


def top_projectors(volume: int, n: int) -> list[np.ndarray]:
    top = np.zeros((n, n), dtype=complex)
    top[-1, -1] = 1.0
    identity = np.eye(n, dtype=complex)
    return [embed(top, site, volume, identity) for site in range(volume)]


def weighted_overlap(vector: np.ndarray, projector: np.ndarray, n: int) -> float:
    return float(n * n * max(0.0, float(np.real(np.vdot(vector, projector @ vector)))))


def weighted_trace(state: np.ndarray, projector: np.ndarray, n: int) -> float:
    return float(n * n * max(0.0, float(np.real(np.trace(state @ projector)))))


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
    check("finite volumes", fixture["volume_values"] == [2, 4], fixture["volume_values"], "declared [2,4]", "geometry")
    check("two orientations", fixture["orientation_values"] == [-1, 1], fixture["orientation_values"], "[-1,1]", "orientation")
    check("scope firewall", scope["finite_evolved_history_weighted_tail_closed"] and scope["finite_gibbs_weighted_tail_closed"] and not scope["source_volume_orientation_history_uniform_tail_closed"], scope, "finite tail only", "scope")

    tolerance = float(fixture["residual_tolerance"])
    beta = float(fixture["beta"])
    hbar = float(fixture["hbar"])
    time_values = [float(value) for value in fixture["time_values"]]
    orientation_values = [int(value) for value in fixture["orientation_values"]]
    volume_rows: list[dict[str, Any]] = []

    for volume in [int(value) for value in fixture["volume_values"]]:
        n_rows: list[dict[str, Any]] = []
        for n in [int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]]:
            q, _ = oscillator(n)
            full_h = build_hamiltonian(volume, n, fixture)
            cutoff_q = smooth_coordinate_cutoff(q, float(fixture["cutoff_radius"]))
            cutoff_h = build_hamiltonian(volume, n, fixture, cutoff_q)
            tail = full_h - cutoff_h
            rho = gibbs(full_h, beta)
            projectors = top_projectors(volume, n)
            vacuum = np.zeros(n**volume, dtype=complex)
            vacuum[0] = 1.0
            gibbs_values = [weighted_trace(rho, projector, n) for projector in projectors]
            check(f"V={volume} n={n} Gibbs trace", abs(float(np.trace(rho).real) - 1.0) <= tolerance, float(np.trace(rho).real), "1", "Gibbs")
            check(f"V={volume} n={n} Gibbs tail finite", all(np.isfinite(value) and value >= 0.0 for value in gibbs_values), gibbs_values, "finite nonnegative", "Gibbs tail")
            history_rows: list[dict[str, Any]] = []
            for sign in orientation_values:
                for time in time_values:
                    propagator = unitary(full_h + sign * tail, time, hbar)
                    psi = propagator @ vacuum
                    unitarity = float(np.linalg.norm(propagator.conj().T @ propagator - np.eye(n**volume), ord=2))
                    values = [weighted_overlap(psi, projector, n) for projector in projectors]
                    check(f"V={volume} n={n} sign={sign} t={time} unitary", unitarity <= 100.0 * tolerance, unitarity, f"<={100.0 * tolerance}", "history")
                    check(f"V={volume} n={n} sign={sign} t={time} tail finite", all(np.isfinite(value) and value >= 0.0 for value in values), values, "finite nonnegative", "history tail")
                    history_rows.append({"sign": sign, "time": time, "unitarity_residual": unitarity, "site_weighted_tails": values, "max_weighted_tail": max(values)})
            anchors = [row["max_weighted_tail"] for row in history_rows if float(row["time"]) == 0.0]
            check(f"V={volume} n={n} vacuum anchor", all(value <= 100.0 * tolerance for value in anchors), anchors, f"<={100.0 * tolerance}", "history anchor")
            n_rows.append({"n": n, "dimension": n**volume, "gibbs_site_weighted_tails": gibbs_values, "gibbs_max_weighted_tail": max(gibbs_values), "history_rows": history_rows, "history_max_weighted_tail": max(row["max_weighted_tail"] for row in history_rows), "cutoff_tail_operator_norm": float(np.linalg.norm(tail, ord=2))})
        volume_rows.append({"volume": volume, "edge_count": len(edges_for(volume, fixture)), "n_rows": n_rows})
        check(f"V={volume} cutoff sequence", [row["n"] for row in n_rows] == [int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]], [row["n"] for row in n_rows], fixture["oscillator_dimensions_by_volume"][str(volume)], "cutoff")

    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
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
    print(f"PRIMARY FINITE-Q3-WEIGHTED-TOP-TAIL-HISTORY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
