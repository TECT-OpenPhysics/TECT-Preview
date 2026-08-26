#!/usr/bin/env python3
"""Primary finite-Q3 energy-fourth coercive quotient audit (EXP-001190).

The finite Euclidean tail moment from EXP-001189 is compared with a positive
shifted Hamiltonian.  For K=I+H+|Lambda|r^2/(4g)I and a self-adjoint tail W,
the finite quotient C=||K^(-2)W^4K^(-2)|| gives W^4 <= C K^4 by congruence.
The quotient and Gibbs K^4 moment are reported as finite diagnostics; no
uniform common-core estimate is asserted.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-energy-fourth-coercive-quotient"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    minimum = float(np.min(values))
    if minimum < -1.0e-9:
        raise ValueError(f"non-positive spectral input: min={minimum}")
    return (vectors * np.power(np.maximum(values, 0.0), exponent)) @ vectors.conj().T


def spectral_inverse_power(matrix: np.ndarray, exponent: float, floor: float) -> tuple[np.ndarray, float]:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    minimum = float(np.min(values))
    if minimum <= floor:
        raise ValueError(f"spectral floor not positive: min={minimum}, floor={floor}")
    return (vectors * np.power(values, -exponent)) @ vectors.conj().T, minimum


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
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        identity = np.eye(hamiltonian.shape[0], dtype=complex)
        shift = volume * r**2 / (4.0 * g)
        shifted_hamiltonian = hermitian(hamiltonian + (1.0 + shift) * identity)
        shifted_values, shifted_vectors = np.linalg.eigh(shifted_hamiltonian)
        min_shifted = float(np.min(shifted_values))
        check(f"V={volume} positive shifted form", min_shifted >= 1.0 - numerical_tolerance, min_shifted, ">=1", "positive shift")
        inverse_square, inverse_floor = spectral_inverse_power(shifted_hamiltonian, 2.0, 0.0)
        fourth_shifted = shifted_hamiltonian @ shifted_hamiltonian @ shifted_hamiltonian @ shifted_hamiltonian
        q_single = q3.oscillator(dimension)[0]
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
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                tail = hermitian(tail)
                tail_square = tail @ tail
                tail_fourth = tail_square @ tail_square
                two_slice = float(np.real(np.trace(rho_half @ tail_square @ rho_half @ tail_square)))
                equal_time = float(np.real(np.trace(rho @ tail_fourth)))
                quotient = hermitian(inverse_square @ tail_fourth @ inverse_square)
                quotient_constant = operator_norm(quotient)
                order_defect = hermitian(quotient_constant * fourth_shifted - tail_fourth)
                order_slack = float(np.min(np.linalg.eigvalsh(order_defect)))
                trace_bound = quotient_constant * energy_fourth_expectation
                trace_slack = trace_bound - equal_time
                order_scale = 1.0 + operator_norm(tail_fourth) + quotient_constant * operator_norm(fourth_shifted)
                values = {"shift_per_volume": shift, "shifted_floor": inverse_floor, "tail_operator_norm": operator_norm(tail), "two_slice": two_slice, "equal_time_fourth_moment": equal_time, "energy_fourth_moment": energy_fourth_expectation, "quotient_constant": quotient_constant, "trace_bound": trace_bound, "order_slack": order_slack, "trace_slack": trace_slack, "order_scale": order_scale}
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
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ENERGY-FOURTH-COERCIVE-QUOTIENT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"rows": all_rows, "summary_rows": summary_rows, "finite_positive_shift_closed": True, "finite_generalized_coercive_quotient_closed": True, "finite_operator_order_envelope_closed": True, "finite_gibbs_energy_fourth_transfer_closed": True, "quotient_volume_cutoff_uniform_closed": False, "energy_fourth_uniform_closed": False, "local_coercive_common_core_closed": False, "tail_fourth_moment_uniform_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "fixture_lineage": fixture_lineage}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-ENERGY-FOURTH-COERCIVE-QUOTIENT PASS {payload['passed']}/{payload['assertion_count']} rows={len(payload['derived']['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
