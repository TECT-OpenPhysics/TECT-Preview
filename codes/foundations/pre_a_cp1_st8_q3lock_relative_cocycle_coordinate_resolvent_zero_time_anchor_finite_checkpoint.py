#!/usr/bin/env python3
"""Finite zero-time coordinate-resolvent anchor for the relative cocycle.

The boundary addition is a position-only Q3 bond.  A coordinate resolvent
therefore commutes with it at time zero, so the relative-dynamics difference
has a vanishing first variation.  This file checks that algebra and a finite
second-variation reduction; it does not estimate an infinite-volume Cook
remainder.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_relative_cocycle_coordinate_resolvent_zero_time_anchor_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-relative-cocycle-coordinate-resolvent-zero-time-anchor-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def graph_edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(int(site) for site in edge) for edge in fixture["graph_edges_by_volume"][str(volume)]]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    quadratic = difference @ difference
    quartic = quadratic @ (left @ left + right @ right)
    return hermitian(float(fixture["c"]) * quadratic / 2.0 + float(fixture["lambda"]) * quartic / 4.0)


def build_terms(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[dict[str, Any]], list[np.ndarray]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    onsite: list[np.ndarray] = []
    for q, p in zip(q_ops, p_ops):
        onsite.append(hermitian(p @ p / (2.0 * float(fixture["chi"])) + float(fixture["r"]) * (q @ q) / 2.0 + float(fixture["g"]) * (q @ q @ q @ q) / 4.0))
    specs: list[dict[str, Any]] = [{"kind": "onsite", "support": [site]} for site in range(volume)]
    bonds: list[np.ndarray] = []
    for left, right in graph_edges(volume, fixture):
        bonds.append(bond_term(q_ops[left], q_ops[right], fixture))
        specs.append({"kind": "bond", "support": [left, right]})
    return q_ops, specs, onsite + bonds


def sum_indices(terms: list[np.ndarray], indices: list[int]) -> np.ndarray:
    result = np.zeros_like(terms[0], dtype=complex)
    for index in indices:
        result = result + terms[index]
    return hermitian(result)


def evolution(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def alpha(hamiltonian: np.ndarray, operator: np.ndarray, time: float, hbar: float) -> np.ndarray:
    return evolution(hamiltonian, -time, hbar) @ operator @ evolution(hamiltonian, time, hbar)


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def two_sided_norm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001229" and manifest["result_id"] == "R-386" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001229/R-386/false", "provenance")
    check("coverage orders", coverage["orders"] == ["forward", "reverse"], coverage["orders"], "both orders", "coverage")
    check("coverage bond prefixes", coverage["all_bond_prefixes"] and coverage["both_adjoint_seeds"], coverage, "all bond prefixes and adjoints", "coverage")
    finite_flags = ("finite_position_boundary_commutes_with_coordinate_resolvent_closed", "finite_zero_first_variation_closed", "finite_second_variation_reduction_closed", "finite_modular_zero_first_variation_closed", "finite_quadratic_time_diagnostic_closed")
    open_flags = ("phase_local_bkm_estimate_closed", "boundary_shell_l1_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(scope[key] for key in open_flags), "finite anchor / all limits open", "scope", "scope")

    hbar = float(Fraction(fixture["hbar"]))
    beta_values = [float(Fraction(value)) for value in fixture["beta_values"]]
    eta_values = [float(Fraction(value)) for value in fixture["resolvent_imaginary_values"]]
    times = [float(Fraction(value)) for value in fixture["time_values"]]
    derivative_step = float(Fraction(fixture["derivative_step"]))
    second_step = float(Fraction(fixture["second_derivative_step"]))
    alpha_tolerance = float(fixture["alpha_tolerance"])
    zero_tolerance = float(fixture["zero_commutator_tolerance"])
    first_tolerance = float(fixture["first_derivative_tolerance"])
    second_tolerance = float(fixture["second_derivative_tolerance"])
    modular_tolerance = float(fixture["modular_first_derivative_tolerance"])

    maximums = {"zero_commutator_residual": 0.0, "first_variation_residual": 0.0, "second_variation_residual": 0.0, "second_reduction_residual": 0.0, "modular_first_variation_residual": 0.0, "dynamic_norm": 0.0, "dynamic_norm_over_time_squared": 0.0}
    volume_summaries: list[dict[str, Any]] = []
    context_count = 0
    bond_prefix_count = 0
    zero_rows = 0
    first_rows = 0
    second_rows = 0
    modular_rows = 0
    dynamic_rows = 0

    for volume in (int(value) for value in fixture["volume_values"]):
        q_ops, specs, terms = build_terms(volume, int(fixture["oscillator_dimension"]), fixture)
        term_count = len(terms)
        order_map = {"forward": list(range(term_count)), "reverse": list(reversed(range(term_count)))}
        volume_max = {key: 0.0 for key in maximums}
        volume_contexts = 0
        volume_bonds = 0
        for order_name in coverage["orders"]:
            order = order_map[order_name]
            for prefix_position, term_index in enumerate(order):
                if specs[term_index]["kind"] != "bond":
                    continue
                bond_prefix_count += 1
                volume_bonds += 1
                hamiltonian = sum_indices(terms, order[:prefix_position])
                boundary = terms[term_index]
                hamiltonian_prime = hermitian(hamiltonian + boundary)
                rho_cache = {beta: gibbs(hamiltonian, beta) for beta in beta_values}
                for site in range(volume):
                    for eta in eta_values:
                        identity = np.eye(q_ops[site].shape[0], dtype=complex)
                        seed = np.linalg.inv(1j * eta * identity - q_ops[site])
                        for seed_name, observable in (("A", seed), ("A_star", seed.conj().T)):
                            comm0 = commutator(boundary, observable)
                            comm0_residual = operator_norm(comm0)
                            maximums["zero_commutator_residual"] = max(maximums["zero_commutator_residual"], comm0_residual)
                            volume_max["zero_commutator_residual"] = max(volume_max["zero_commutator_residual"], comm0_residual)
                            zero_rows += 1
                            check(f"V={volume} {order_name} bondprefix={prefix_position} site={site} eta={eta} {seed_name} commute", comm0_residual <= zero_tolerance, comm0_residual, f"<={zero_tolerance}", "zero-time anchor")
                            first_exact = (1j / hbar) * comm0
                            d_zero = alpha(hamiltonian_prime, observable, 0.0, hbar) - alpha(hamiltonian, observable, 0.0, hbar)
                            first_plus = alpha(hamiltonian_prime, observable, derivative_step, hbar) - alpha(hamiltonian, observable, derivative_step, hbar)
                            first_minus = alpha(hamiltonian_prime, observable, -derivative_step, hbar) - alpha(hamiltonian, observable, -derivative_step, hbar)
                            first_fd = (first_plus - first_minus) / (2.0 * derivative_step)
                            first_residual = operator_norm(first_fd - first_exact)
                            maximums["first_variation_residual"] = max(maximums["first_variation_residual"], first_residual)
                            volume_max["first_variation_residual"] = max(volume_max["first_variation_residual"], first_residual)
                            first_rows += 1
                            check(f"V={volume} {order_name} bondprefix={prefix_position} site={site} eta={eta} {seed_name} first", first_residual <= first_tolerance, first_residual, f"<={first_tolerance}", "zero-time anchor")
                            h2 = second_step
                            second_plus = alpha(hamiltonian_prime, observable, h2, hbar) - alpha(hamiltonian, observable, h2, hbar)
                            second_minus = alpha(hamiltonian_prime, observable, -h2, hbar) - alpha(hamiltonian, observable, -h2, hbar)
                            second_fd = (second_plus - 2.0 * d_zero + second_minus) / (h2 * h2)
                            full_second = -(commutator(hamiltonian_prime, commutator(hamiltonian_prime, observable)) - commutator(hamiltonian, commutator(hamiltonian, observable))) / (hbar * hbar)
                            reduced_second = -commutator(boundary, commutator(hamiltonian, observable)) / (hbar * hbar)
                            second_residual = operator_norm(second_fd - full_second)
                            reduction_residual = operator_norm(full_second - reduced_second)
                            maximums["second_variation_residual"] = max(maximums["second_variation_residual"], second_residual)
                            maximums["second_reduction_residual"] = max(maximums["second_reduction_residual"], reduction_residual)
                            volume_max["second_variation_residual"] = max(volume_max["second_variation_residual"], second_residual)
                            volume_max["second_reduction_residual"] = max(volume_max["second_reduction_residual"], reduction_residual)
                            second_rows += 1
                            check(f"V={volume} {order_name} bondprefix={prefix_position} site={site} eta={eta} {seed_name} second", second_residual <= second_tolerance, second_residual, f"<={second_tolerance}", "second variation")
                            check(f"V={volume} {order_name} bondprefix={prefix_position} site={site} eta={eta} {seed_name} reduction", reduction_residual <= second_tolerance, reduction_residual, f"<={second_tolerance}", "second variation")
                            for beta in beta_values:
                                rho = rho_cache[beta]
                                context_count += 1
                                volume_contexts += 1
                                modular_plus = (1j / hbar) * commutator(hamiltonian, first_plus)
                                modular_minus = (1j / hbar) * commutator(hamiltonian, first_minus)
                                modular_fd = (modular_plus - modular_minus) / (2.0 * derivative_step)
                                modular_exact = (1j / hbar) * commutator(hamiltonian, first_exact)
                                modular_residual = operator_norm(modular_fd - modular_exact)
                                maximums["modular_first_variation_residual"] = max(maximums["modular_first_variation_residual"], modular_residual)
                                volume_max["modular_first_variation_residual"] = max(volume_max["modular_first_variation_residual"], modular_residual)
                                modular_rows += 1
                                check(f"V={volume} {order_name} bondprefix={prefix_position} site={site} eta={eta} beta={beta} {seed_name} modular", modular_residual <= modular_tolerance, modular_residual, f"<={modular_tolerance}", "modular anchor")
                                for sign in (-1, 1):
                                    for magnitude in times:
                                        time = sign * magnitude
                                        delta = alpha(hamiltonian_prime, observable, time, hbar) - alpha(hamiltonian, observable, time, hbar)
                                        dynamic_norm = two_sided_norm(delta, rho)
                                        ratio = dynamic_norm / (time * time)
                                        maximums["dynamic_norm"] = max(maximums["dynamic_norm"], dynamic_norm)
                                        maximums["dynamic_norm_over_time_squared"] = max(maximums["dynamic_norm_over_time_squared"], ratio)
                                        volume_max["dynamic_norm"] = max(volume_max["dynamic_norm"], dynamic_norm)
                                        volume_max["dynamic_norm_over_time_squared"] = max(volume_max["dynamic_norm_over_time_squared"], ratio)
                                        dynamic_rows += 1
                                        check(f"V={volume} {order_name} bondprefix={prefix_position} site={site} eta={eta} beta={beta} t={time} {seed_name} dynamic", np.isfinite(dynamic_norm) and np.isfinite(ratio), [dynamic_norm, ratio], "finite", "quadratic-time diagnostic")
        expected_volume_contexts = 2 * len(graph_edges(volume, fixture)) * volume * len(eta_values) * len(beta_values) * 2
        check(f"V={volume} context count", volume_contexts == expected_volume_contexts, volume_contexts, expected_volume_contexts, "coverage")
        volume_summaries.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "term_count": term_count, "bond_prefix_count": volume_bonds, "context_count": volume_contexts, "maximums": volume_max})
    expected_contexts = sum(2 * len(graph_edges(int(volume), fixture)) * int(volume) * len(eta_values) * len(beta_values) * 2 for volume in fixture["volume_values"])
    check("global context count", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    expected_seed_rows = sum(2 * len(graph_edges(int(volume), fixture)) * int(volume) * len(eta_values) * 2 for volume in fixture["volume_values"])
    check("row counts", zero_rows == first_rows == second_rows == expected_seed_rows and modular_rows == context_count and dynamic_rows == context_count * len(times) * 2, [zero_rows, first_rows, second_rows, modular_rows, dynamic_rows], [expected_seed_rows, expected_seed_rows, expected_seed_rows, expected_contexts, expected_contexts * len(times) * 2], "coverage")
    check("finite maxima", all(np.isfinite(value) for value in maximums.values()), maximums, "finite", "numerics")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-RELATIVE-COCYCLE-COORDINATE-RESOLVENT-ZERO-TIME-ANCHOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"context_count": context_count, "expected_contexts": expected_contexts, "bond_prefix_count": bond_prefix_count, "zero_commutator_rows": zero_rows, "first_variation_rows": first_rows, "second_variation_rows": second_rows, "modular_first_variation_rows": modular_rows, "dynamic_rows": dynamic_rows, "maximums": maximums, "volume_summaries": volume_summaries, "finite_position_boundary_commutes_with_coordinate_resolvent_closed": True, "finite_zero_first_variation_closed": True, "finite_second_variation_reduction_closed": True, "finite_modular_zero_first_variation_closed": True, "finite_quadratic_time_diagnostic_closed": True, "phase_local_bkm_estimate_closed": False, "boundary_shell_l1_closed": False, "cutoff_uniformity_closed": False, "source_uniformity_closed": False, "volume_uniformity_closed": False, "shape_uniformity_closed": False, "operator_domain_embedding_closed": False, "direct_D_cauchy_closed": False, "delta_D_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY RELATIVE-COCYCLE ZERO-TIME-ANCHOR PASS {payload['passed']}/{payload['assertion_count']} contexts={payload['derived']['context_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
