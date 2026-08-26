#!/usr/bin/env python3
"""Non-importing independent lane for EXP-001190."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-energy-fourth-coercive-quotient"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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


def load_fixture(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    current = manifest
    lineage: list[str] = []
    while "finite_fixture" not in current:
        lineage.append(str(current.get("exploration_id", "unknown")))
        current = json.loads((REPO / current["fixture_source"]).read_text(encoding="utf-8"))
    lineage.append(str(current.get("exploration_id", "unknown")))
    return current["finite_fixture"], lineage


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = math.sqrt(index + 1.0)
    return (annihilation + annihilation.conj().T) / math.sqrt(2.0), (annihilation - annihilation.conj().T) / (1j * math.sqrt(2.0))


def edges(volume: int) -> list[tuple[int, int]]:
    declared = {2: [(0, 1)], 4: [(0, 1), (0, 2), (1, 3), (2, 3)], 6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]}
    if volume not in declared:
        raise ValueError("finite fixture volume not declared")
    return declared[volume]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    return float(fixture["c"]) * (difference @ difference) / 2.0 + float(fixture["lambda"]) * (difference @ difference) @ (left @ left + right @ right) / 4.0


def build(volume: int, dimension: int, fixture: dict[str, Any], coordinate: np.ndarray | None = None) -> tuple[np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    bond_coordinate = q_single if coordinate is None else coordinate
    bond_ops = [embed(bond_coordinate, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): bond(bond_ops[left], bond_ops[right], fixture) for left, right in edges(volume)}
    zero = np.zeros_like(q_ops[0])
    hamiltonian = sum(onsite, zero) + sum(bonds.values(), zero)
    return hermitian(hamiltonian), bonds


def cut_coordinate(coordinate: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(coordinate))
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, fixture_lineage = load_fixture(manifest)
    scope = manifest["scope"]
    identity_tolerance = float(fixture["holder_tolerance"])
    positivity_floor = float(fixture["positivity_floor"])
    numerical_tolerance = float(fixture["unitary_tolerance"])
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    g = float(fixture["g"])
    r = float(fixture["r"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001190" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001190/T-054", "provenance")
    check("fixture lineage", fixture_lineage[-1] == "EXP-001188", fixture_lineage, "EXP-001189 -> EXP-001188", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_positive_shift_closed"] and scope["finite_generalized_coercive_quotient_closed"] and scope["finite_operator_order_envelope_closed"] and scope["finite_gibbs_energy_fourth_transfer_closed"] and not scope["quotient_volume_cutoff_uniform_closed"] and not scope["energy_fourth_uniform_closed"] and not scope["local_coercive_common_core_closed"] and not scope["pre_a_closed"], scope, "finite energy quotient; QFT gates open", "scope")

    all_rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        hamiltonian, bonds = build(volume, dimension, fixture)
        identity = np.eye(hamiltonian.shape[0], dtype=complex)
        shift = volume * r**2 / (4.0 * g)
        shifted_hamiltonian = hermitian(hamiltonian + (1.0 + shift) * identity)
        shifted_values, shifted_vectors = np.linalg.eigh(shifted_hamiltonian)
        min_shifted = float(np.min(shifted_values))
        check(f"V={volume} positive shifted form", min_shifted >= 1.0 - numerical_tolerance, min_shifted, ">=1", "positive shift")
        inverse_square = (shifted_vectors * np.power(shifted_values, -2.0)) @ shifted_vectors.conj().T
        fourth_shifted = shifted_hamiltonian @ shifted_hamiltonian @ shifted_hamiltonian @ shifted_hamiltonian
        q_single = oscillator(dimension)[0]
        energy_values, energy_vectors = np.linalg.eigh(hermitian(hamiltonian))
        shifted_energy = energy_values - float(np.min(energy_values))
        for beta in betas:
            gibbs_weights = np.exp(-beta * shifted_energy)
            probabilities = gibbs_weights / float(np.sum(gibbs_weights))
            rho = (energy_vectors * probabilities) @ energy_vectors.conj().T
            rho_half = (energy_vectors * np.sqrt(probabilities)) @ energy_vectors.conj().T
            check(f"V={volume} beta={beta} Gibbs state", abs(float(np.trace(rho).real) - 1.0) <= numerical_tolerance and np.isfinite(probabilities).all() and float(np.min(probabilities)) >= positivity_floor, [float(np.trace(rho).real), float(np.min(probabilities))], "normalized positive", "state")
            energy_fourth_expectation = float(np.real(np.trace(rho @ fourth_shifted)))
            for radius in radii:
                q_cut = cut_coordinate(q_single, radius)
                _, cut_bonds = build(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                tail = hermitian(tail)
                tail_square = tail @ tail
                tail_fourth = tail_square @ tail_square
                two_slice = float(np.real(np.trace(rho_half @ tail_square @ rho_half @ tail_square)))
                equal_time = float(np.real(np.trace(rho @ tail_fourth)))
                quotient = hermitian(inverse_square @ tail_fourth @ inverse_square)
                quotient_constant = operator_norm(quotient)
                order_slack = float(np.min(np.linalg.eigvalsh(hermitian(quotient_constant * fourth_shifted - tail_fourth))))
                trace_bound = quotient_constant * energy_fourth_expectation
                trace_slack = trace_bound - equal_time
                order_scale = 1.0 + operator_norm(tail_fourth) + quotient_constant * operator_norm(fourth_shifted)
                values = {"shift_per_volume": shift, "shifted_floor": min_shifted, "tail_operator_norm": operator_norm(tail), "two_slice": two_slice, "equal_time_fourth_moment": equal_time, "energy_fourth_moment": energy_fourth_expectation, "quotient_constant": quotient_constant, "trace_bound": trace_bound, "order_slack": order_slack, "trace_slack": trace_slack, "order_scale": order_scale}
                check(f"V={volume} beta={beta} L={radius} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "quotient")
                check(f"V={volume} beta={beta} L={radius} two-slice transfer", two_slice >= -identity_tolerance and equal_time >= -identity_tolerance and equal_time - two_slice >= -identity_tolerance * (1.0 + equal_time), [two_slice, equal_time], "0<=two_slice<=Tr(rho W^4)", "Euclidean transfer")
                check(f"V={volume} beta={beta} L={radius} quotient order", order_slack >= -numerical_tolerance * order_scale, [order_slack, order_scale], ">=-finite tolerance", "operator order")
                check(f"V={volume} beta={beta} L={radius} Gibbs energy transfer", trace_slack >= -numerical_tolerance * (1.0 + trace_bound), [equal_time, trace_bound], "Tr(rho W^4)<=C Tr(rho K^4)", "Gibbs transfer")
                all_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, **values})

    expected_rows = len(fixture["scenarios"]) * len(betas) * len(radii)
    check("row coverage", len(all_rows) == expected_rows, len(all_rows), expected_rows, "coverage")
    check("all quotient orders", all(row["order_slack"] >= -numerical_tolerance * row["order_scale"] for row in all_rows), len(all_rows), "finite congruence tolerance", "operator order")
    check("all Gibbs transfers", all(row["trace_slack"] >= -numerical_tolerance * (1.0 + row["trace_bound"]) for row in all_rows), len(all_rows), "finite trace tolerance", "Gibbs transfer")
    summary_rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        for beta in betas:
            members = [row for row in all_rows if row["volume"] == volume and row["beta"] == beta]
            summary_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "max_quotient_constant": max(row["quotient_constant"] for row in members), "max_two_slice": max(row["two_slice"] for row in members), "max_equal_time_fourth_moment": max(row["equal_time_fourth_moment"] for row in members), "energy_fourth_moment": members[0]["energy_fourth_moment"], "max_trace_bound": max(row["trace_bound"] for row in members), "min_order_slack": min(row["order_slack"] for row in members), "min_trace_slack": min(row["trace_slack"] for row in members)})
    check("summary coverage", len(summary_rows) == len(fixture["scenarios"]) * len(betas), len(summary_rows), len(fixture["scenarios"]) * len(betas), "coverage")
    check("finite diagnostic", all(row["max_quotient_constant"] >= 0.0 and row["max_two_slice"] >= -identity_tolerance and row["energy_fourth_moment"] >= 0.0 for row in summary_rows), [row["max_quotient_constant"] for row in summary_rows], "finite nonnegative diagnostics", "summary")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ENERGY-FOURTH-COERCIVE-QUOTIENT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"rows": all_rows, "summary_rows": summary_rows, "finite_positive_shift_closed": True, "finite_generalized_coercive_quotient_closed": True, "finite_operator_order_envelope_closed": True, "finite_gibbs_energy_fourth_transfer_closed": True, "quotient_volume_cutoff_uniform_closed": False, "energy_fourth_uniform_closed": False, "local_coercive_common_core_closed": False, "tail_fourth_moment_uniform_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "fixture_lineage": fixture_lineage}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-ENERGY-FOURTH-COERCIVE-QUOTIENT PASS {payload['passed']}/{payload['assertion_count']} rows={len(payload['derived']['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
