#!/usr/bin/env python3
"""Primary finite checkpoint for the relative-modular cocycle route.

The calculation is deliberately bounded: every Hamiltonian is a finite
oscillator truncation and every assertion is about an exact matrix identity
or a finite Gibbs-weighted diagnostic.  It does not estimate a thermodynamic
shell coefficient.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_relative_modular_cocycle_resolvent_cook_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-relative-modular-cocycle-resolvent-cook-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def zero_like(matrix: np.ndarray) -> np.ndarray:
    return np.zeros_like(matrix, dtype=complex)


def sum_indices(terms: list[np.ndarray], indices: list[int]) -> np.ndarray:
    result = zero_like(terms[0])
    for index in indices:
        result = result + terms[index]
    return hermitian(result)


def evolution(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def alpha(hamiltonian: np.ndarray, operator: np.ndarray, time: float, hbar: float) -> np.ndarray:
    forward = evolution(hamiltonian, -time, hbar)
    backward = evolution(hamiltonian, time, hbar)
    return forward @ operator @ backward


def relative_cocycle(hamiltonian: np.ndarray, hamiltonian_prime: np.ndarray, time: float, hbar: float) -> np.ndarray:
    return evolution(hamiltonian_prime, -time, hbar) @ evolution(hamiltonian, time, hbar)


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    shifted = values - float(np.min(values))
    weights = np.exp(-beta * shifted)
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def resolvent(q_operator: np.ndarray, imaginary: float) -> np.ndarray:
    identity = np.eye(q_operator.shape[0], dtype=complex)
    return np.linalg.inv(1j * imaginary * identity - q_operator)


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def two_sided_gibbs_norm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001228" and manifest["result_id"] == "R-385" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001228/R-385/false", "provenance")
    check("fixture volumes", fixture["volume_values"] == [2, 4], fixture["volume_values"], [2, 4], "fixture")
    check("fixture beta", fixture["beta_values"] == ["1/2", "1"], fixture["beta_values"], ["1/2", "1"], "fixture")
    check("fixture orders", manifest["coverage"]["orders"] == ["forward", "reverse"], manifest["coverage"]["orders"], "both orders", "fixture")
    check("scope firewall", all(manifest["scope"][key] for key in ("finite_relative_cocycle_identity_closed", "finite_cocycle_derivative_identity_closed", "finite_cocycle_composition_closed", "finite_resolvent_identity_closed", "finite_two_orientation_state_weighted_rows_closed", "finite_all_prefix_order_sign_beta_seed_grid_closed")) and not any(manifest["scope"][key] for key in ("boundary_shell_l1_closed", "phase_local_bkm_estimate_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), "finite identities / open limits", "scope", "scope")

    hbar = float(Fraction(fixture["hbar"]))
    beta_values = [float(Fraction(value)) for value in fixture["beta_values"]]
    eta_values = [float(Fraction(value)) for value in fixture["resolvent_imaginary_values"]]
    magnitudes = [float(Fraction(value)) for value in fixture["time_magnitudes"]]
    composition_pairs = [(float(Fraction(left)), float(Fraction(right))) for left, right in fixture["composition_pairs"]]
    derivative_step = float(Fraction(fixture["derivative_step"]))
    alpha_tolerance = float(fixture["alpha_tolerance"])
    cocycle_tolerance = float(fixture["cocycle_tolerance"])
    resolvent_tolerance = float(fixture["resolvent_tolerance"])
    unitarity_tolerance = float(fixture["unitarity_tolerance"])
    derivative_tolerance = float(fixture["derivative_tolerance"])
    commutator_floor = float(fixture["commutator_floor"])

    maximums = {
        "alpha_intertwining_residual": 0.0,
        "cocycle_residual": 0.0,
        "derivative_residual": 0.0,
        "resolvent_residual": 0.0,
        "unitarity_residual": 0.0,
        "commutator_norm": 0.0,
        "weighted_left": 0.0,
        "weighted_right": 0.0,
        "weighted_commutator": 0.0,
        "weighted_adjoint_commutator": 0.0,
    }
    volume_summaries: list[dict[str, Any]] = []
    context_count = 0
    alpha_rows = 0
    composition_rows = 0
    derivative_rows = 0
    resolvent_rows = 0
    prefix_count = 0
    bond_prefix_count = 0

    for volume in (int(value) for value in fixture["volume_values"]):
        q_ops, specs, terms = build_terms(volume, int(fixture["oscillator_dimension"]), fixture)
        term_count = len(terms)
        order_map = {"forward": list(range(term_count)), "reverse": list(reversed(range(term_count)))}
        volume_contexts = 0
        volume_max = {key: 0.0 for key in maximums}
        volume_prefixes = 0
        for order_name in manifest["coverage"]["orders"]:
            order = order_map[order_name]
            for prefix_position, term_index in enumerate(order):
                prefix_count += 1
                volume_prefixes += 1
                if specs[term_index]["kind"] == "bond":
                    bond_prefix_count += 1
                hamiltonian = sum_indices(terms, order[:prefix_position])
                boundary_term = terms[term_index]
                hamiltonian_prime = hermitian(hamiltonian + boundary_term)
                times = sorted(set(magnitudes + [-value for value in magnitudes]))
                composition_times = [sum(pair) for pair in composition_pairs]
                derivative_times = [time + derivative_step for time in times] + [time - derivative_step for time in times]
                cache_times = sorted(set(times + composition_times + derivative_times))
                unitary_cache = {time: evolution(hamiltonian, time, hbar) for time in cache_times}
                prime_cache = {time: evolution(hamiltonian_prime, time, hbar) for time in cache_times}
                relative_cache = {time: prime_cache[-time] @ unitary_cache[time] for time in unitary_cache}

                for sign in (-1, 1):
                    for magnitude in magnitudes:
                        time = sign * magnitude
                        u = relative_cache[time]
                        identity = np.eye(u.shape[0], dtype=complex)
                        unitary_residual = max(operator_norm(u.conj().T @ u - identity), operator_norm(u @ u.conj().T - identity))
                        maximums["unitarity_residual"] = max(maximums["unitarity_residual"], unitary_residual)
                        volume_max["unitarity_residual"] = max(volume_max["unitarity_residual"], unitary_residual)
                        check(f"V={volume} {order_name} prefix={prefix_position} sign={sign} unitary", unitary_residual <= unitarity_tolerance, unitary_residual, f"<={unitarity_tolerance}", "relative cocycle")
                        derivative = (relative_cache[time + derivative_step] - relative_cache[time - derivative_step]) / (2.0 * derivative_step)
                        expected_derivative = (1j / hbar) * alpha(hamiltonian_prime, boundary_term, time, hbar) @ u
                        derivative_residual = operator_norm(derivative - expected_derivative)
                        maximums["derivative_residual"] = max(maximums["derivative_residual"], derivative_residual)
                        volume_max["derivative_residual"] = max(volume_max["derivative_residual"], derivative_residual)
                        derivative_rows += 1
                        check(f"V={volume} {order_name} prefix={prefix_position} sign={sign} derivative", derivative_residual <= derivative_tolerance, derivative_residual, f"<={derivative_tolerance}", "relative cocycle")

                    for left_value, right_value in composition_pairs:
                        lhs = relative_cache[left_value + right_value]
                        rhs = relative_cache[left_value] @ alpha(hamiltonian, relative_cache[right_value], left_value, hbar)
                        cocycle_residual = operator_norm(lhs - rhs)
                        maximums["cocycle_residual"] = max(maximums["cocycle_residual"], cocycle_residual)
                        volume_max["cocycle_residual"] = max(volume_max["cocycle_residual"], cocycle_residual)
                        composition_rows += 1
                        check(f"V={volume} {order_name} prefix={prefix_position} cocycle {left_value},{right_value}", cocycle_residual <= cocycle_tolerance, cocycle_residual, f"<={cocycle_tolerance}", "relative cocycle")

                seed_cache = {(site, eta): resolvent(q_ops[site], eta) for site in range(volume) for eta in eta_values}
                for site in range(volume):
                    for eta in eta_values:
                        seed = seed_cache[(site, eta)]
                        for other_eta in eta_values:
                            other_seed = seed_cache[(site, other_eta)]
                            z, w = 1j * eta, 1j * other_eta
                            resolvent_residual = operator_norm(seed - other_seed - (w - z) * seed @ other_seed)
                            maximums["resolvent_residual"] = max(maximums["resolvent_residual"], resolvent_residual)
                            volume_max["resolvent_residual"] = max(volume_max["resolvent_residual"], resolvent_residual)
                            resolvent_rows += 1
                            check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta}/{other_eta} resolvent", resolvent_residual <= resolvent_tolerance, resolvent_residual, f"<={resolvent_tolerance}", "resolvent core")
                        for beta in beta_values:
                            rho = gibbs(hamiltonian_prime, beta)
                            for adjoint_name, observable in (("A", seed), ("A_star", seed.conj().T)):
                                context_count += 1
                                volume_contexts += 1
                                left_product = boundary_term @ observable
                                right_product = observable @ boundary_term
                                comm = left_product - right_product
                                values = {
                                    "left": two_sided_gibbs_norm(left_product, rho),
                                    "right": two_sided_gibbs_norm(right_product, rho),
                                    "commutator": two_sided_gibbs_norm(comm, rho),
                                    "commutator_matrix": operator_norm(comm),
                                }
                                maximums["weighted_left"] = max(maximums["weighted_left"], values["left"])
                                maximums["weighted_right"] = max(maximums["weighted_right"], values["right"])
                                maximums["weighted_commutator"] = max(maximums["weighted_commutator"], values["commutator"])
                                maximums["commutator_norm"] = max(maximums["commutator_norm"], values["commutator_matrix"])
                                volume_max["weighted_left"] = max(volume_max["weighted_left"], values["left"])
                                volume_max["weighted_right"] = max(volume_max["weighted_right"], values["right"])
                                volume_max["weighted_commutator"] = max(volume_max["weighted_commutator"], values["commutator"])
                                volume_max["commutator_norm"] = max(volume_max["commutator_norm"], values["commutator_matrix"])
                                maximums["weighted_adjoint_commutator"] = max(maximums["weighted_adjoint_commutator"], values["commutator"] if adjoint_name == "A_star" else 0.0)
                                volume_max["weighted_adjoint_commutator"] = max(volume_max["weighted_adjoint_commutator"], values["commutator"] if adjoint_name == "A_star" else 0.0)
                                check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta} beta={beta} {adjoint_name} finite", all(np.isfinite(value) and value >= -resolvent_tolerance for value in values.values()), values, "finite nonnegative weighted rows", "state weight")
                                for sign in (-1, 1):
                                    for magnitude in magnitudes:
                                        time = sign * magnitude
                                        intertwined = alpha(hamiltonian_prime, observable, time, hbar) - relative_cache[time] @ alpha(hamiltonian, observable, time, hbar) @ relative_cache[time].conj().T
                                        alpha_residual = operator_norm(intertwined)
                                        maximums["alpha_intertwining_residual"] = max(maximums["alpha_intertwining_residual"], alpha_residual)
                                        volume_max["alpha_intertwining_residual"] = max(volume_max["alpha_intertwining_residual"], alpha_residual)
                                        alpha_rows += 1
                                        check(f"V={volume} {order_name} prefix={prefix_position} site={site} eta={eta} beta={beta} {adjoint_name} sign={sign} alpha", alpha_residual <= alpha_tolerance, alpha_residual, f"<={alpha_tolerance}", "intertwining")

        check(f"V={volume} prefix coverage", volume_prefixes == 2 * term_count, volume_prefixes, 2 * term_count, "coverage")
        check(f"V={volume} context coverage", volume_contexts == 2 * term_count * len(beta_values) * len(eta_values) * volume * 2, volume_contexts, 2 * term_count * len(beta_values) * len(eta_values) * volume * 2, "coverage")
        volume_summaries.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "term_count": term_count, "prefix_count": volume_prefixes, "bond_prefix_count": sum(1 for spec in specs if spec["kind"] == "bond") * 2, "context_count": volume_contexts, "maximums": volume_max})

    expected_contexts = sum(2 * len(specs := build_terms(volume, int(fixture["oscillator_dimension"]), fixture)[1]) * len(beta_values) * len(eta_values) * volume * 2 for volume in (int(value) for value in fixture["volume_values"]))
    check("global context coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("nontrivial commutator witness", maximums["commutator_norm"] > commutator_floor, maximums["commutator_norm"], f">{commutator_floor}", "state weight")
    check("finite maxima", all(np.isfinite(value) and value >= 0.0 for value in maximums.values()), maximums, "finite nonnegative", "summary")

    derived = {
        **maximums,
        "volume_summaries": volume_summaries,
        "volume_count": len(volume_summaries),
        "prefix_count": prefix_count,
        "bond_prefix_count": bond_prefix_count,
        "context_count": context_count,
        "expected_contexts": expected_contexts,
        "alpha_row_count": alpha_rows,
        "composition_row_count": composition_rows,
        "derivative_row_count": derivative_rows,
        "resolvent_row_count": resolvent_rows,
        "finite_relative_cocycle_identity_closed": True,
        "finite_cocycle_derivative_identity_closed": True,
        "finite_cocycle_composition_closed": True,
        "finite_resolvent_identity_closed": True,
        "finite_two_orientation_state_weighted_rows_closed": True,
        "finite_all_prefix_order_sign_beta_seed_grid_closed": True,
        "boundary_shell_l1_closed": False,
        "phase_local_bkm_estimate_closed": False,
        "cutoff_uniformity_closed": False,
        "source_uniformity_closed": False,
        "volume_uniformity_closed": False,
        "shape_uniformity_closed": False,
        "operator_domain_embedding_closed": False,
        "direct_D_cauchy_closed": False,
        "delta_D_cauchy_closed": False,
        "common_alpha_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False,
    }
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RELATIVE-MODULAR-COCYCLE-RESOLVENT-COOK-FINITE-CHECKPOINT",
        "claim_id": manifest["claim_ids"][0],
        "result_id": manifest["result_id"],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "boundary": manifest["boundary"],
        "provenance": {"script": str(Path(__file__).relative_to(REPO)).replace("\\", "/"), "script_sha256": normalized_sha256(Path(__file__)), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": normalized_sha256(MANIFEST)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY RELATIVE-MODULAR-COCYCLE-COOK PASS {payload['passed']}/{payload['assertion_count']} contexts={payload['derived']['context_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
