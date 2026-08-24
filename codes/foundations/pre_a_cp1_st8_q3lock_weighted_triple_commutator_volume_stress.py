#!/usr/bin/env python3
"""Primary finite actual-Q3 weighted triple-commutator volume stress test."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
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
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError("EXP-001088 uses only volumes 2, 4, and 6")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (left @ left + right @ right) / 4.0


def build_volume(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): bond_term(q_ops[left], q_ops[right], fixture) for left, right in graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite, zero) + sum(bonds.values(), zero)
    local = onsite[0] + onsite[1] + bonds[(0, 1)]
    return q_ops, (full + full.conj().T) / 2.0, (local + local.conj().T) / 2.0, bonds


def cut_coordinate(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    hermitian = (matrix + matrix.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    if float(np.min(values)) < -1.0e-9:
        raise ValueError(f"weight is not positive: min={float(np.min(values))}")
    values = np.maximum(values, 0.0)
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def positive_weight(base: np.ndarray) -> np.ndarray:
    hermitian = (base + base.conj().T) / 2.0
    minimum = float(np.min(np.linalg.eigvalsh(hermitian)))
    return hermitian - minimum * np.eye(base.shape[0], dtype=complex) + np.eye(base.shape[0], dtype=complex)


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def hs_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord="fro"))


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def two_sided_gibbs(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def weighted_two_sided(matrix: np.ndarray, weight_power: np.ndarray, rho_sqrt: np.ndarray) -> float:
    legs = (
        weight_power @ matrix @ rho_sqrt,
        weight_power @ matrix.conj().T @ rho_sqrt,
        matrix @ weight_power @ rho_sqrt,
        matrix.conj().T @ weight_power @ rho_sqrt,
    )
    return float(np.sqrt(sum(hs_norm(leg) ** 2 for leg in legs)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001088" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001088/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph geometry", graph_edges(2) == [(0, 1)] and len(graph_edges(4)) == 4 and len(graph_edges(6)) == 7, [graph_edges(2), len(graph_edges(4)), len(graph_edges(6))], "target/square/2x3", "geometry")
    check("scope firewall", scope["finite_triple_commutator_identity_closed"] and scope["finite_weighted_two_sided_rows_closed"] and scope["candidate_volume_growth_diagnostic_closed"] and not scope["candidate_volume_uniform_bound_closed"], scope, "finite weighted diagnostic", "scope")

    beta, hbar, amplitude = float(fixture["beta"]), float(fixture["hbar"]), float(fixture["character_amplitude"])
    tolerance, tail_tolerance = float(fixture["commutator_tolerance"]), float(fixture["tail_tolerance"])
    exponent = float(fixture["weight_exponent"])
    volume_rows: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        q_ops, hamiltonian, local_hamiltonian, bonds = build_volume(volume, int(fixture["oscillator_dimension"]), fixture)
        rho = gibbs(hamiltonian, beta)
        rho_sqrt = spectral_power(rho, 0.5)
        observable = character(q_ops[0] + q_ops[1], amplitude, hbar)
        h_comm = commutator(hamiltonian, observable)
        local_weight, full_weight = positive_weight(local_hamiltonian), positive_weight(hamiltonian)
        local_power, full_power = spectral_power(local_weight, exponent), spectral_power(full_weight, exponent)
        check(f"V={volume} local weight positive", float(np.min(np.linalg.eigvalsh(local_weight))) >= 1.0 - tolerance, float(np.min(np.linalg.eigvalsh(local_weight))), ">=1", "weight")
        check(f"V={volume} full weight positive", float(np.min(np.linalg.eigvalsh(full_weight))) >= 1.0 - tolerance, float(np.min(np.linalg.eigvalsh(full_weight))), ">=1", "weight")
        radius_rows: list[dict[str, Any]] = []
        q_single, _ = oscillator(int(fixture["oscillator_dimension"]))
        for radius in map(float, fixture["radius_values"]):
            q_cut = cut_coordinate(q_single, radius)
            # Rebuild cut bonds directly so onsite terms stay unchanged.
            _, _, _, cut_bonds = build_volume_with_bond_coordinate(volume, int(fixture["oscillator_dimension"]), fixture, q_cut)
            tail_edges = {edge: bonds[edge] - cut_bonds[edge] for edge in bonds}
            zero = np.zeros_like(hamiltonian)
            tail = sum(tail_edges.values(), zero)
            tail_norm = operator_norm(tail)
            source_commutator_norm = operator_norm(commutator(tail, observable))
            inner = commutator(tail, h_comm)
            base_d2 = -inner / (hbar * hbar)
            triple = commutator(hamiltonian, inner)
            modular_base = -beta * commutator(hamiltonian, base_d2)
            modular_formula = beta * triple / (hbar * hbar)
            modular_identity_error = operator_norm(modular_base - modular_formula)
            disjoint = [tail_edges[edge] for edge in graph_edges(volume) if set(edge).isdisjoint(set(fixture["observable_support"]))]
            disjoint_tail = sum(disjoint, zero)
            disjoint_commutator_norm = operator_norm(commutator(disjoint_tail, observable))
            check(f"V={volume} L={radius} modular identity", modular_identity_error <= tolerance, modular_identity_error, f"<={tolerance}", "triple identity")
            check(f"V={volume} L={radius} source commutation", source_commutator_norm <= tolerance, source_commutator_norm, f"<={tolerance}", "configuration commutation")
            check(f"V={volume} L={radius} disjoint tail", disjoint_commutator_norm <= tolerance, disjoint_commutator_norm, f"<={tolerance}", "support locality")
            if radius == max(map(float, fixture["radius_values"])):
                check(f"V={volume} zero tail at largest radius", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            weight_rows: dict[str, Any] = {}
            for kind, power in (("local", local_power), ("full", full_power)):
                d2_weight = weighted_two_sided(base_d2, power, rho_sqrt)
                modular_weight = weighted_two_sided(modular_base, power, rho_sqrt)
                d2_gibbs = two_sided_gibbs(base_d2, rho)
                modular_gibbs = two_sided_gibbs(modular_base, rho)
                values = {"D2_gibbs": d2_gibbs, "modular_D2_gibbs": modular_gibbs, "D2_weighted": d2_weight, "modular_weighted": modular_weight, "tail_operator_norm": tail_norm, "modular_identity_error": modular_identity_error}
                check(f"V={volume} L={radius} {kind} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "weighted triple")
                weight_rows[kind] = values
            radius_rows.append({"radius": radius, "source_commutator_norm": source_commutator_norm, "disjoint_tail_commutator_norm": disjoint_commutator_norm, "weights": weight_rows})
        volume_rows.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "radius_rows": radius_rows})
        check(f"V={volume} radius sequence", [row["radius"] for row in radius_rows] == list(map(float, fixture["radius_values"])), [row["radius"] for row in radius_rows], fixture["radius_values"], "cutoff")

    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    def maxima(kind: str, field: str) -> list[float]:
        return [max(item["weights"][kind][field] for item in row["radius_rows"]) for row in volume_rows]
    local_modular = maxima("local", "modular_weighted")
    full_modular = maxima("full", "modular_weighted")
    local_d2 = maxima("local", "D2_weighted")
    full_d2 = maxima("full", "D2_weighted")
    local_growth = local_modular[-1] / max(local_modular[0], np.finfo(float).tiny)
    full_growth = full_modular[-1] / max(full_modular[0], np.finfo(float).tiny)
    check("weighted maxima finite", all(np.isfinite(value) for value in local_modular + full_modular + local_d2 + full_d2), [local_modular, full_modular], "finite", "scaling")
    check("candidate growth diagnostic", local_growth >= float(fixture["growth_threshold"]) and full_growth >= float(fixture["growth_threshold"]), [local_growth, full_growth], f">={fixture['growth_threshold']}", "scaling")
    check("support commutators vanish", all(float(row["source_commutator_norm"]) <= tolerance and float(row["disjoint_tail_commutator_norm"]) <= tolerance for volume in volume_rows for row in volume["radius_rows"]), "all rows", "tolerance", "support locality")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-WEIGHTED-TRIPLE-COMMUTATOR-VOLUME-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "weight_exponent": exponent,
            "local_modular_weighted_maxima": local_modular,
            "full_modular_weighted_maxima": full_modular,
            "local_D2_weighted_maxima": local_d2,
            "full_D2_weighted_maxima": full_d2,
            "local_modular_volume_growth": local_growth,
            "full_modular_volume_growth": full_growth,
            "finite_triple_commutator_identity_closed": True,
            "finite_weighted_two_sided_rows_closed": True,
            "candidate_volume_growth_diagnostic_closed": True,
            "candidate_volume_uniform_bound_closed": False,
            "weighted_modular_domain_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "positive_time_history_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False
        },
        "boundary": scope
    }


def build_volume_with_bond_coordinate(volume: int, n: int, fixture: dict[str, Any], bond_q: np.ndarray) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    bond_ops = [embed(bond_q, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): bond_term(bond_ops[left], bond_ops[right], fixture) for left, right in graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite, zero) + sum(bonds.values(), zero)
    local = onsite[0] + onsite[1] + bonds[(0, 1)]
    return q_ops, (full + full.conj().T) / 2.0, (local + local.conj().T) / 2.0, bonds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY WEIGHTED-TRIPLE-COMMUTATOR-VOLUME-STRESS PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
