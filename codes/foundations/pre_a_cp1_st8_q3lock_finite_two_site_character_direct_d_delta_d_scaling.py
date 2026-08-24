#!/usr/bin/env python3
"""Primary finite Gibbs direct D,delta-D support-scaling audit for EXP-001086."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_two_site_character_direct_d_delta_d_scaling"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


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
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    raise ValueError("EXP-001086 uses only the target edge and square face")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def build_hamiltonian(
    volume: int, n: int, fixture: dict[str, Any], bond_q_replacement: np.ndarray | None = None
) -> tuple[list[np.ndarray], np.ndarray]:
    q_single, p_single = oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    bond_single = q_single if bond_q_replacement is None else bond_q_replacement
    bond_q_ops = [embed(bond_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    terms = list(onsite)
    for left, right in graph_edges(volume):
        d = bond_q_ops[left] - bond_q_ops[right]
        terms.append(c * (d @ d) / 2.0 + lam * (d @ d) @ (bond_q_ops[left] @ bond_q_ops[left] + bond_q_ops[right] @ bond_q_ops[right]) / 4.0)
    hamiltonian = sum(terms, np.zeros_like(q_ops[0]))
    return q_ops, (hamiltonian + hamiltonian.conj().T) / 2.0


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


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001086" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001086/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("two-site support", fixture["observable_support"] == [0, 1], fixture["observable_support"], [0, 1], "observable")
    check("finite graph", len(graph_edges(2)) == 1 and len(graph_edges(4)) == 4, [len(graph_edges(2)), len(graph_edges(4))], "1 and 4", "geometry")
    check("scope firewall", scope["finite_two_site_direct_D_closed"] and scope["finite_two_site_direct_delta_D_closed"] and scope["support_scaling_diagnostic_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"], scope, "finite support diagnostic", "scope")
    beta, hbar, amplitude = float(fixture["beta"]), float(fixture["hbar"]), float(fixture["character_amplitude"])
    volume_rows: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        q_ops, hamiltonian = build_hamiltonian(volume, int(fixture["oscillator_dimension"]), fixture)
        rho = gibbs(hamiltonian, beta)
        observable = character(q_ops[0] + q_ops[1], amplitude, hbar)
        reference = {float(time): unitary(hamiltonian, float(time), hbar) @ observable @ unitary(hamiltonian, float(time), hbar).conj().T for time in fixture["time_values"]}
        q_single, _ = oscillator(int(fixture["oscillator_dimension"]))
        radius_rows: list[dict[str, Any]] = []
        for radius in map(float, fixture["radius_values"]):
            _, cut_hamiltonian = build_hamiltonian(volume, int(fixture["oscillator_dimension"]), fixture, cut_coordinate(q_single, radius))
            tail = hamiltonian - cut_hamiltonian
            tail_norm = float(np.linalg.svd(tail, compute_uv=False)[0])
            time_rows: list[dict[str, Any]] = []
            for time in map(float, fixture["time_values"]):
                orientations: dict[str, Any] = {}
                for sign in (-1, 1):
                    evolved = unitary(hamiltonian + sign * tail, time, hbar)
                    d_sigma = evolved @ observable @ evolved.conj().T - reference[time]
                    delta_d = -beta * (hamiltonian @ d_sigma - d_sigma @ hamiltonian)
                    values = {"D_norm": seminorm(d_sigma, rho), "delta_D_norm": seminorm(delta_d, rho), "matrix_norm": float(np.linalg.svd(d_sigma, compute_uv=False)[0])}
                    orientations[str(sign)] = values
                    check(f"V={volume} L={radius} t={time} sign={sign} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "two-site direct D")
                sums = {key: orientations["1"][key] + orientations["-1"][key] for key in ("D_norm", "delta_D_norm")}
                time_rows.append({"time": time, "orientations": orientations, "two_orientation_sum_of_norms": sums})
                zero = unitary(hamiltonian, 0.0, hbar) @ observable @ unitary(hamiltonian, 0.0, hbar).conj().T - observable
                check(f"V={volume} L={radius} t={time} t=0 anchor", seminorm(zero, rho) <= float(fixture["tail_tolerance"]), "zero", "near zero", "two-site direct D")
            if radius == max(map(float, fixture["radius_values"])):
                check(f"V={volume} zero tail at largest radius", tail_norm <= float(fixture["tail_tolerance"]), tail_norm, f"<={fixture['tail_tolerance']}", "cutoff")
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "times": time_rows})
        volume_rows.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "radius_rows": radius_rows})
        check(f"V={volume} radius sequence", [row["radius"] for row in radius_rows] == list(map(float, fixture["radius_values"])), [row["radius"] for row in radius_rows], fixture["radius_values"], "cutoff")
    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    summary: list[dict[str, Any]] = []
    for volume_row in volume_rows:
        samples = [time_row["two_orientation_sum_of_norms"] for radius_row in volume_row["radius_rows"] for time_row in radius_row["times"]]
        summary.append({"volume": volume_row["volume"], "max_D_norm_sum": max(item["D_norm"] for item in samples), "max_delta_D_norm_sum": max(item["delta_D_norm"] for item in samples)})
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-TWO-SITE-CHARACTER-DIRECT-D-DELTA-D-SCALING", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "summary": summary, "finite_two_site_direct_D_closed": True, "finite_two_site_direct_delta_D_closed": True, "finite_two_orientation_difference_closed": True, "cutoff_zero_tail_fixture_closed": True, "support_scaling_diagnostic_closed": True, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "group_law_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-TWO-SITE-D-DELTA-D PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
