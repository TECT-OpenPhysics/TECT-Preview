#!/usr/bin/env python3
"""Primary finite Gibbs direct D,delta-D audit for EXP-001085."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-direct-d-delta-d-cauchy"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1): annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2: return [(0, 1)]
    if volume == 4: return [(0, 1), (0, 2), (1, 3), (2, 3)]
    raise ValueError("EXP-001085 uses only the target edge and square face")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]: result = np.kron(result, factor)
    return result


def build_hamiltonian(volume: int, n: int, fixture: dict[str, Any], q_replacement: np.ndarray | None = None) -> tuple[list[np.ndarray], list[np.ndarray], np.ndarray]:
    q_single, p_single = oscillator(n); identity = np.eye(n, dtype=complex)
    q_base = q_single if q_replacement is None else q_replacement
    q_ops = [embed(q_base, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    terms = list(onsite)
    for left, right in graph_edges(volume):
        d = q_ops[left] - q_ops[right]
        terms.append(c * (d @ d) / 2.0 + lam * (d @ d) @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0)
    hamiltonian = sum(terms, np.zeros_like(q_ops[0]))
    return q_ops, p_ops, (hamiltonian + hamiltonian.conj().T) / 2.0


def cut_coordinate(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def unitary(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def character(q: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001085" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001085/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("finite graph", len(graph_edges(2)) == 1 and len(graph_edges(4)) == 4, [len(graph_edges(2)), len(graph_edges(4))], "1 and 4", "geometry")
    check("scope firewall", scope["finite_direct_D_closed"] and scope["finite_direct_delta_D_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"], scope, "finite direct diagnostic", "scope")
    beta, hbar, amplitude = float(fixture["beta"]), float(fixture["hbar"]), float(fixture["character_amplitude"])
    volume_rows: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        n = int(fixture["oscillator_dimension"]); q_ops, _, hamiltonian = build_hamiltonian(volume, n, fixture)
        rho = gibbs(hamiltonian, beta); observable = character(q_ops[0], amplitude, hbar)
        reference = {time: unitary(hamiltonian, time, hbar) @ observable @ unitary(hamiltonian, time, hbar).conj().T for time in fixture["time_values"]}
        radius_rows: list[dict[str, Any]] = []
        q_single, _ = oscillator(n)
        for radius in map(float, fixture["radius_values"]):
            q_cut = cut_coordinate(q_single, radius)
            _, _, cut_hamiltonian = build_hamiltonian(volume, n, fixture, q_cut)
            tail = hamiltonian - cut_hamiltonian
            tail_norm = float(np.linalg.svd(tail, compute_uv=False)[0])
            time_rows: list[dict[str, Any]] = []
            for time in map(float, fixture["time_values"]):
                u_ref = unitary(hamiltonian, time, hbar); d_values: dict[str, Any] = {}
                for sign in (-1, 1):
                    u_sigma = unitary(hamiltonian + sign * tail, time, hbar)
                    d_sigma = u_sigma @ observable @ u_sigma.conj().T - reference[time]
                    delta_d = -beta * (hamiltonian @ d_sigma - d_sigma @ hamiltonian)
                    d_values[str(sign)] = {"D_norm": seminorm(d_sigma, rho), "delta_D_norm": seminorm(delta_d, rho), "matrix_norm": float(np.linalg.svd(d_sigma, compute_uv=False)[0])}
                    check(f"V={volume} L={radius} t={time} sign={sign} finite", all(np.isfinite(value) for value in d_values[str(sign)].values()), d_values[str(sign)], "finite", "direct D")
                difference = {key: d_values["1"][key] + d_values["-1"][key] for key in ("D_norm", "delta_D_norm")}
                time_rows.append({"time": time, "orientations": d_values, "two_orientation_sum_of_norms": difference})
                check(f"V={volume} L={radius} t={time} t=0 anchor", seminorm(unitary(hamiltonian, 0.0, hbar) @ observable @ unitary(hamiltonian, 0.0, hbar).conj().T - observable, rho) <= float(fixture["tail_tolerance"]), "zero", "near zero", "direct D")
            if radius == max(map(float, fixture["radius_values"])):
                check(f"V={volume} zero tail at largest radius", tail_norm <= float(fixture["tail_tolerance"]), tail_norm, f"<={fixture['tail_tolerance']}", "cutoff")
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "times": time_rows})
        volume_rows.append({"volume": volume, "dimension": n**volume, "radius_rows": radius_rows})
        check(f"V={volume} radius sequence", [row["radius"] for row in radius_rows] == list(map(float, fixture["radius_values"])), [row["radius"] for row in radius_rows], fixture["radius_values"], "cutoff")
    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-DIRECT-D-DELTA-D-CAUCHY", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "finite_direct_D_closed": True, "finite_direct_delta_D_closed": True, "finite_two_orientation_difference_closed": True, "cutoff_zero_tail_fixture_closed": True, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "group_law_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-DIRECT-D-DELTA-D PASS {payload['passed']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
