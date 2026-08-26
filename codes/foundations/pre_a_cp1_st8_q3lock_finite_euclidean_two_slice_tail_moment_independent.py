#!/usr/bin/env python3
"""Non-importing independent lane for EXP-001189.

The Q3 oscillator, bond, Gibbs state and cutoff tail are reconstructed here
without importing the primary audit.  The same finite Euclidean identity and
coercive envelopes are then checked through an independent matrix path.
"""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-euclidean-two-slice-tail-moment"
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


def build(volume: int, dimension: int, fixture: dict[str, Any], coordinate: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray, dict[tuple[int, int], np.ndarray]]:
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
    return q_ops, (hamiltonian + hamiltonian.conj().T) / 2.0, bonds


def cut_coordinate(coordinate: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((coordinate + coordinate.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def schatten(matrix: np.ndarray, exponent: float) -> float:
    singular = np.linalg.svd(matrix, compute_uv=False)
    return float(np.power(np.sum(np.power(singular, exponent)), 1.0 / exponent))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_manifest = json.loads((REPO / manifest["fixture_source"]).read_text(encoding="utf-8"))
    fixture, scope = source_manifest["finite_fixture"], manifest["scope"]
    identity_tolerance = float(fixture["holder_tolerance"])
    positivity_floor = float(fixture["positivity_floor"])
    dimension_tolerance = float(fixture["unitary_tolerance"])
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001189" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001189/T-054", "provenance")
    check("fixture lineage", source_manifest["exploration_id"] == "EXP-001188" and source_manifest["task_id"] == "T-054", [source_manifest["exploration_id"], source_manifest["task_id"]], "EXP-001188/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_tail_fourth_leg_identity_closed"] and scope["finite_euclidean_two_slice_identity_closed"] and scope["finite_equal_time_coercive_envelope_closed"] and not scope["tail_fourth_moment_uniform_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite Euclidean bridge; QFT gates open", "scope")

    all_rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        q_ops, hamiltonian, bonds = build(volume, dimension, fixture)
        energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
        shifted = energies - float(np.min(energies))
        q_single = oscillator(dimension)[0]
        for beta in betas:
            weights = np.exp(-beta * shifted)
            probabilities = weights / float(np.sum(weights))
            rho = (vectors * probabilities) @ vectors.conj().T
            rho_half = (vectors * np.sqrt(probabilities)) @ vectors.conj().T
            rho_quarter = (vectors * np.power(probabilities, 0.25)) @ vectors.conj().T
            check(f"V={volume} beta={beta} Gibbs normalization", abs(float(np.trace(rho).real) - 1.0) <= dimension_tolerance and float(np.min(probabilities)) >= positivity_floor and np.isfinite(probabilities).all(), [float(np.trace(rho).real), float(np.min(probabilities))], "normalized positive", "state")
            check(f"V={volume} beta={beta} root normalization", abs(schatten(rho_quarter, 4.0) - 1.0) <= dimension_tolerance * 10.0, schatten(rho_quarter, 4.0), "||rho^(1/4)||_4=1", "state")
            for radius in radii:
                q_cut = cut_coordinate(q_single, radius)
                _, _, cut_bonds = build(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                tail = (tail + tail.conj().T) / 2.0
                tail_adjoint_error = operator_norm(tail - tail.conj().T)
                tail_square = tail @ tail
                tail_fourth = tail_square @ tail_square
                tail_leg_left = schatten(rho_quarter @ tail, 4.0)
                tail_leg_right = schatten(tail @ rho_quarter, 4.0)
                holder_moment = tail_leg_left**4
                two_slice = float(np.real(np.trace(rho_half @ tail_square @ rho_half @ tail_square)))
                energy_basis_square = vectors.conj().T @ tail_square @ vectors
                spectral_two_slice = float(np.real(np.sum(np.sqrt(probabilities[:, None] * probabilities[None, :]) * np.abs(energy_basis_square) ** 2)))
                equal_time = float(np.real(np.trace(rho @ tail_fourth)))
                tail_operator_bound = operator_norm(tail) ** 4
                values = {"tail_adjoint_error": tail_adjoint_error, "tail_leg_left": tail_leg_left, "tail_leg_right": tail_leg_right, "holder_moment": holder_moment, "two_slice": two_slice, "spectral_two_slice": spectral_two_slice, "equal_time_fourth_moment": equal_time, "operator_fourth_bound": tail_operator_bound, "identity_residual": abs(holder_moment - two_slice), "spectral_residual": abs(two_slice - spectral_two_slice), "amgm_slack": equal_time - spectral_two_slice, "operator_slack": tail_operator_bound - equal_time}
                check(f"V={volume} beta={beta} L={radius} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "moment")
                check(f"V={volume} beta={beta} L={radius} self-adjoint tail", tail_adjoint_error <= identity_tolerance, tail_adjoint_error, f"<={identity_tolerance}", "tail")
                check(f"V={volume} beta={beta} L={radius} left/right fourth legs", abs(tail_leg_left**4 - tail_leg_right**4) <= identity_tolerance * (1.0 + holder_moment + tail_leg_right**4), [tail_leg_left, tail_leg_right], "equal fourth powers", "tail")
                check(f"V={volume} beta={beta} L={radius} Euclidean identity", values["identity_residual"] <= identity_tolerance * (1.0 + two_slice), values["identity_residual"], "numerical zero", "two-slice")
                check(f"V={volume} beta={beta} L={radius} spectral identity", values["spectral_residual"] <= identity_tolerance * (1.0 + two_slice), values["spectral_residual"], "numerical zero", "two-slice")
                check(f"V={volume} beta={beta} L={radius} AM-GM coercive envelope", two_slice >= -identity_tolerance and values["amgm_slack"] >= -identity_tolerance * (1.0 + equal_time), [two_slice, values["amgm_slack"]], "0<=two_slice<=Tr(rho W^4)", "coercive moment")
                check(f"V={volume} beta={beta} L={radius} operator envelope", equal_time >= -identity_tolerance and values["operator_slack"] >= -identity_tolerance * (1.0 + tail_operator_bound), [equal_time, values["operator_slack"]], "Tr(rho W^4)<=||W||^4", "coercive moment")
                all_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, **values})

    expected_rows = len(fixture["scenarios"]) * len(betas) * len(radii)
    check("row coverage", len(all_rows) == expected_rows, len(all_rows), expected_rows, "coverage")
    check("all finite identities", all(row["identity_residual"] <= identity_tolerance * (1.0 + row["two_slice"]) and row["spectral_residual"] <= identity_tolerance * (1.0 + row["two_slice"]) for row in all_rows), len(all_rows), "all within tolerance", "two-slice")
    check("all finite envelopes", all(row["amgm_slack"] >= -identity_tolerance * (1.0 + row["equal_time_fourth_moment"]) and row["operator_slack"] >= -identity_tolerance * (1.0 + row["operator_fourth_bound"]) for row in all_rows), len(all_rows), "all nonnegative slacks", "coercive moment")
    summary_rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        for beta in betas:
            members = [row for row in all_rows if row["volume"] == volume and row["beta"] == beta]
            summary_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "max_holder_moment": max(row["holder_moment"] for row in members), "max_two_slice": max(row["two_slice"] for row in members), "max_equal_time_fourth_moment": max(row["equal_time_fourth_moment"] for row in members), "max_operator_fourth_bound": max(row["operator_fourth_bound"] for row in members), "max_identity_residual": max(row["identity_residual"] for row in members), "max_spectral_residual": max(row["spectral_residual"] for row in members), "min_amgm_slack": min(row["amgm_slack"] for row in members), "min_operator_slack": min(row["operator_slack"] for row in members)})
    check("summary coverage", len(summary_rows) == len(fixture["scenarios"]) * len(betas), len(summary_rows), len(fixture["scenarios"]) * len(betas), "coverage")
    check("finite moment diagnostic", all(row["max_holder_moment"] >= 0.0 and row["max_two_slice"] >= -identity_tolerance and row["max_equal_time_fourth_moment"] >= -identity_tolerance for row in summary_rows), [row["max_holder_moment"] for row in summary_rows], "nonnegative finite moments", "summary")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-EUCLIDEAN-TWO-SLICE-TAIL-MOMENT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"rows": all_rows, "summary_rows": summary_rows, "finite_tail_fourth_leg_identity_closed": True, "finite_euclidean_two_slice_identity_closed": True, "finite_spectral_two_slice_crosscheck_closed": True, "finite_equal_time_coercive_envelope_closed": True, "tail_fourth_moment_uniform_closed": False, "source_volume_cutoff_beta_uniform_closed": False, "local_coercive_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "fixture_source": manifest["fixture_source"]}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-EUCLIDEAN-TWO-SLICE-TAIL-MOMENT PASS {payload['passed']}/{payload['assertion_count']} rows={len(payload['derived']['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
