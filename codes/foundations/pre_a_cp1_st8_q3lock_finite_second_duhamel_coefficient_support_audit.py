#!/usr/bin/env python3
"""Primary finite Q3 second Duhamel coefficient audit for EXP-001087."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_second_duhamel_coefficient_support_audit"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


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
    raise ValueError("EXP-001087 uses only the target edge and square face")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]: result = np.kron(result, factor)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (left @ left + right @ right) / 4.0


def build_hamiltonian(volume: int, n: int, fixture: dict[str, Any], bond_q: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q_single, p_single = oscillator(n); identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    bond_single = q_single if bond_q is None else bond_q
    bond_ops = [embed(bond_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = [bond_term(bond_ops[left], bond_ops[right], fixture) for left, right in graph_edges(volume)]
    raw = sum(onsite + bonds, np.zeros_like(q_ops[0]))
    return q_ops, (raw + raw.conj().T) / 2.0, bonds


def cut_coordinate(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0); scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0); weights = np.exp(-beta * (values - float(np.min(values)))); weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray: return left @ right - right @ left
def operator_norm(matrix: np.ndarray) -> float: return float(np.linalg.svd(matrix, compute_uv=False)[0])


def seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001087" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001087/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("two-site support", fixture["observable_support"] == [0, 1], fixture["observable_support"], [0, 1], "observable")
    check("finite graph", len(graph_edges(2)) == 1 and len(graph_edges(4)) == 4, [len(graph_edges(2)), len(graph_edges(4))], "1 and 4", "geometry")
    check("scope firewall", scope["finite_second_duhamel_coefficient_closed"] and scope["finite_modular_second_coefficient_closed"] and scope["source_character_commutation_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"], scope, "finite coefficient diagnostic", "scope")
    beta, hbar, amplitude = float(fixture["beta"]), float(fixture["hbar"]), float(fixture["character_amplitude"])
    tolerance = float(fixture["commutator_tolerance"]); tail_tolerance = float(fixture["tail_tolerance"])
    volume_rows: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        q_ops, hamiltonian, bonds = build_hamiltonian(volume, int(fixture["oscillator_dimension"]), fixture)
        rho = gibbs(hamiltonian, beta); observable = character(q_ops[0] + q_ops[1], amplitude, hbar); h_comm = commutator(hamiltonian, observable)
        q_single, _ = oscillator(int(fixture["oscillator_dimension"])); radius_rows: list[dict[str, Any]] = []
        for radius in map(float, fixture["radius_values"]):
            q_cut = cut_coordinate(q_single, radius); _, cut_hamiltonian, cut_bonds = build_hamiltonian(volume, int(fixture["oscillator_dimension"]), fixture, q_cut)
            tail_edges = [left - right for left, right in zip(bonds, cut_bonds)]; tail = sum(tail_edges, np.zeros_like(hamiltonian)); tail_norm = operator_norm(tail)
            source_commutator_norm = operator_norm(commutator(tail, observable)); base_d2 = -commutator(tail, h_comm) / (hbar * hbar)
            disjoint = [edge_tail for edge_tail, edge in zip(tail_edges, graph_edges(volume)) if set(edge).isdisjoint(set(fixture["observable_support"]))]
            disjoint_tail = sum(disjoint, np.zeros_like(hamiltonian)); disjoint_commutator_norm = operator_norm(commutator(disjoint_tail, observable))
            time_rows: list[dict[str, Any]] = []
            for sign in (-1, 1):
                h_sigma = hamiltonian + sign * tail; c_sigma = commutator(h_sigma, observable)
                direct_d2 = -(commutator(h_sigma, c_sigma) - commutator(hamiltonian, h_comm)) / (hbar * hbar)
                formula_d2 = sign * base_d2; identity_error = operator_norm(direct_d2 - formula_d2); modular_d2 = -beta * commutator(hamiltonian, direct_d2)
                values = {"D2_norm": seminorm(direct_d2, rho), "modular_D2_norm": seminorm(modular_d2, rho), "D2_operator_norm": operator_norm(direct_d2), "identity_error": identity_error}
                check(f"V={volume} L={radius} sign={sign} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "second coefficient")
                check(f"V={volume} L={radius} sign={sign} identity", identity_error <= tolerance, identity_error, f"<={tolerance}", "CCR identity")
                check(f"V={volume} L={radius} sign={sign} source commutation", source_commutator_norm <= tolerance, source_commutator_norm, f"<={tolerance}", "configuration commutation")
                time_rows.append({"sign": sign, "values": values})
            check(f"V={volume} L={radius} disjoint tail", disjoint_commutator_norm <= tolerance, disjoint_commutator_norm, f"<={tolerance}", "support locality")
            if radius == max(map(float, fixture["radius_values"])): check(f"V={volume} zero tail at largest radius", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "source_commutator_norm": source_commutator_norm, "disjoint_tail_commutator_norm": disjoint_commutator_norm, "times": time_rows})
        volume_rows.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "radius_rows": radius_rows})
        check(f"V={volume} radius sequence", [row["radius"] for row in radius_rows] == list(map(float, fixture["radius_values"])), [row["radius"] for row in radius_rows], fixture["radius_values"], "cutoff")
    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    summary: list[dict[str, Any]] = []
    for volume_row in volume_rows:
        samples = [entry["values"] for radius_row in volume_row["radius_rows"] for entry in radius_row["times"]]
        summary.append({"volume": volume_row["volume"], "max_D2_norm": max(item["D2_norm"] for item in samples), "max_modular_D2_norm": max(item["modular_D2_norm"] for item in samples), "max_identity_error": max(item["identity_error"] for item in samples)})
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SECOND-DUHAMEL-COEFFICIENT-SUPPORT-AUDIT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "summary": summary, "finite_second_duhamel_coefficient_closed": True, "finite_modular_second_coefficient_closed": True, "source_character_commutation_closed": True, "disjoint_tail_support_fixture_closed": True, "coefficient_scaling_diagnostic_closed": True, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "positive_time_history_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "group_law_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-SECOND-DUHAMEL-COEFFICIENT PASS {payload['passed']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
