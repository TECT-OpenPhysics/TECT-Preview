#!/usr/bin/env python3
"""Independent reconstruction of the R-386 finite coordinate-resolvent audit."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "independent.json"


def save_json(path: Path, payload: dict[str, Any]) -> None:
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


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) * 0.5


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    ladder = np.diag(np.sqrt(np.arange(1.0, float(size))), 1).astype(complex)
    return (ladder + ladder.conj().T) / np.sqrt(2.0), (ladder - ladder.conj().T) / (1j * np.sqrt(2.0))


def kron_site(local: np.ndarray, site: int, volume: int, size: int) -> np.ndarray:
    answer = np.array([[1.0 + 0.0j]])
    eye = np.eye(size, dtype=complex)
    for index in range(volume):
        answer = np.kron(answer, local if index == site else eye)
    return answer


def edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(map(int, edge)) for edge in fixture["graph_edges_by_volume"][str(volume)]]


def model(volume: int, size: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[dict[str, Any]], list[np.ndarray]]:
    q_local, p_local = oscillator(size)
    q = [kron_site(q_local, site, volume, size) for site in range(volume)]
    p = [kron_site(p_local, site, volume, size) for site in range(volume)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    terms = [sym(p_i @ p_i / (2.0 * chi) + r * (q_i @ q_i) / 2.0 + g * (q_i @ q_i @ q_i @ q_i) / 4.0) for q_i, p_i in zip(q, p)]
    specs = [{"kind": "onsite", "support": [site]} for site in range(volume)]
    for left, right in edges(volume, fixture):
        d = q[left] - q[right]
        terms.append(sym(c * (d @ d) / 2.0 + lam * (d @ d) @ (q[left] @ q[left] + q[right] @ q[right]) / 4.0))
        specs.append({"kind": "bond", "support": [left, right]})
    return q, specs, terms


def add_terms(terms: list[np.ndarray], selected: list[int]) -> np.ndarray:
    result = np.zeros_like(terms[0])
    for index in selected:
        result += terms[index]
    return sym(result)


def exp_i(hamiltonian: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(hamiltonian))
    return (vectors * np.exp(1j * time * values / hbar)) @ vectors.conj().T


def evolve(hamiltonian: np.ndarray, operator: np.ndarray, time: float, hbar: float) -> np.ndarray:
    return exp_i(hamiltonian, time, hbar) @ operator @ exp_i(hamiltonian, -time, hbar)


def bracket(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def state(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return sym((vectors * weights) @ vectors.conj().T)


def weighted_norm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    beta_values = [float(Fraction(item)) for item in fixture["beta_values"]]
    eta_values = [float(Fraction(item)) for item in fixture["resolvent_imaginary_values"]]
    time_values = [float(Fraction(item)) for item in fixture["time_values"]]
    hbar = float(Fraction(fixture["hbar"]))
    h = float(Fraction(fixture["derivative_step"]))
    h2 = float(Fraction(fixture["second_derivative_step"]))
    tolerances = {key: float(fixture[key]) for key in ("zero_commutator_tolerance", "first_derivative_tolerance", "second_derivative_tolerance", "modular_first_derivative_tolerance")}
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001229" and manifest["result_id"] == "R-386" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001229/R-386/false", "provenance")
    maximums = {"zero_commutator_residual": 0.0, "first_variation_residual": 0.0, "second_variation_residual": 0.0, "second_reduction_residual": 0.0, "modular_first_variation_residual": 0.0, "dynamic_norm": 0.0, "dynamic_norm_over_time_squared": 0.0}
    volume_summaries: list[dict[str, Any]] = []
    context_count = zero_rows = first_rows = second_rows = modular_rows = dynamic_rows = bond_prefix_count = 0

    for volume in map(int, fixture["volume_values"]):
        q_ops, specs, terms = model(volume, int(fixture["oscillator_dimension"]), fixture)
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        volume_max = {key: 0.0 for key in maximums}
        volume_contexts = volume_bonds = 0
        for order_name, order in orders.items():
            for position, term_index in enumerate(order):
                if specs[term_index]["kind"] != "bond":
                    continue
                bond_prefix_count += 1
                volume_bonds += 1
                base = add_terms(terms, order[:position])
                boundary = terms[term_index]
                perturbed = sym(base + boundary)
                for site in range(volume):
                    for eta in eta_values:
                        eye = np.eye(q_ops[site].shape[0], dtype=complex)
                        seed = np.linalg.inv(1j * eta * eye - q_ops[site])
                        for seed_name, observable in (("A", seed), ("A_star", seed.conj().T)):
                            c0 = bracket(boundary, observable)
                            c0_norm = norm(c0)
                            maximums["zero_commutator_residual"] = max(maximums["zero_commutator_residual"], c0_norm)
                            volume_max["zero_commutator_residual"] = max(volume_max["zero_commutator_residual"], c0_norm)
                            zero_rows += 1
                            check(f"V={volume} {order_name} pos={position} site={site} eta={eta} {seed_name} commute", c0_norm <= tolerances["zero_commutator_tolerance"], c0_norm, tolerances["zero_commutator_tolerance"], "zero-time anchor")
                            first_target = (1j / hbar) * c0
                            d0 = evolve(perturbed, observable, 0.0, hbar) - evolve(base, observable, 0.0, hbar)
                            dplus = evolve(perturbed, observable, h, hbar) - evolve(base, observable, h, hbar)
                            dminus = evolve(perturbed, observable, -h, hbar) - evolve(base, observable, -h, hbar)
                            first_error = norm((dplus - dminus) / (2.0 * h) - first_target)
                            maximums["first_variation_residual"] = max(maximums["first_variation_residual"], first_error)
                            volume_max["first_variation_residual"] = max(volume_max["first_variation_residual"], first_error)
                            first_rows += 1
                            check(f"V={volume} {order_name} pos={position} site={site} eta={eta} {seed_name} first", first_error <= tolerances["first_derivative_tolerance"], first_error, tolerances["first_derivative_tolerance"], "zero-time anchor")
                            dplus2 = evolve(perturbed, observable, h2, hbar) - evolve(base, observable, h2, hbar)
                            dminus2 = evolve(perturbed, observable, -h2, hbar) - evolve(base, observable, -h2, hbar)
                            full_second = -(bracket(perturbed, bracket(perturbed, observable)) - bracket(base, bracket(base, observable))) / (hbar * hbar)
                            reduced_second = -bracket(boundary, bracket(base, observable)) / (hbar * hbar)
                            second_error = norm((dplus2 - 2.0 * d0 + dminus2) / (h2 * h2) - full_second)
                            reduction_error = norm(full_second - reduced_second)
                            maximums["second_variation_residual"] = max(maximums["second_variation_residual"], second_error)
                            maximums["second_reduction_residual"] = max(maximums["second_reduction_residual"], reduction_error)
                            volume_max["second_variation_residual"] = max(volume_max["second_variation_residual"], second_error)
                            volume_max["second_reduction_residual"] = max(volume_max["second_reduction_residual"], reduction_error)
                            second_rows += 1
                            check(f"V={volume} {order_name} pos={position} site={site} eta={eta} {seed_name} second", second_error <= tolerances["second_derivative_tolerance"], second_error, tolerances["second_derivative_tolerance"], "second variation")
                            check(f"V={volume} {order_name} pos={position} site={site} eta={eta} {seed_name} reduction", reduction_error <= tolerances["second_derivative_tolerance"], reduction_error, tolerances["second_derivative_tolerance"], "second variation")
                            for beta in beta_values:
                                rho = state(base, beta)
                                context_count += 1
                                volume_contexts += 1
                                modular_first = (1j / hbar) * bracket(base, first_target)
                                modular_plus = (1j / hbar) * bracket(base, dplus)
                                modular_minus = (1j / hbar) * bracket(base, dminus)
                                modular_error = norm((modular_plus - modular_minus) / (2.0 * h) - modular_first)
                                maximums["modular_first_variation_residual"] = max(maximums["modular_first_variation_residual"], modular_error)
                                volume_max["modular_first_variation_residual"] = max(volume_max["modular_first_variation_residual"], modular_error)
                                modular_rows += 1
                                check(f"V={volume} {order_name} pos={position} site={site} eta={eta} beta={beta} {seed_name} modular", modular_error <= tolerances["modular_first_derivative_tolerance"], modular_error, tolerances["modular_first_derivative_tolerance"], "modular anchor")
                                for sign in (-1, 1):
                                    for magnitude in time_values:
                                        t = sign * magnitude
                                        delta = evolve(perturbed, observable, t, hbar) - evolve(base, observable, t, hbar)
                                        value = weighted_norm(delta, rho)
                                        ratio = value / (t * t)
                                        maximums["dynamic_norm"] = max(maximums["dynamic_norm"], value)
                                        maximums["dynamic_norm_over_time_squared"] = max(maximums["dynamic_norm_over_time_squared"], ratio)
                                        volume_max["dynamic_norm"] = max(volume_max["dynamic_norm"], value)
                                        volume_max["dynamic_norm_over_time_squared"] = max(volume_max["dynamic_norm_over_time_squared"], ratio)
                                        dynamic_rows += 1
                                        check(f"V={volume} {order_name} pos={position} site={site} eta={eta} beta={beta} t={t} {seed_name} dynamic", np.isfinite(value) and np.isfinite(ratio), [value, ratio], "finite", "quadratic-time diagnostic")
        expected_volume_contexts = 2 * len(edges(volume, fixture)) * volume * len(eta_values) * len(beta_values) * 2
        check(f"V={volume} context count", volume_contexts == expected_volume_contexts, volume_contexts, expected_volume_contexts, "coverage")
        volume_summaries.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "term_count": len(terms), "bond_prefix_count": volume_bonds, "context_count": volume_contexts, "maximums": volume_max})
    expected_contexts = sum(2 * len(edges(int(volume), fixture)) * int(volume) * len(eta_values) * len(beta_values) * 2 for volume in fixture["volume_values"])
    expected_seeds = sum(2 * len(edges(int(volume), fixture)) * int(volume) * len(eta_values) * 2 for volume in fixture["volume_values"])
    check("global context count", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("row counts", zero_rows == first_rows == second_rows == expected_seeds and modular_rows == context_count and dynamic_rows == context_count * len(time_values) * 2, [zero_rows, first_rows, second_rows, modular_rows, dynamic_rows], [expected_seeds, expected_seeds, expected_seeds, expected_contexts, expected_contexts * len(time_values) * 2], "coverage")
    check("finite maxima", all(np.isfinite(value) for value in maximums.values()), maximums, "finite", "numerics")
    derived = {"context_count": context_count, "expected_contexts": expected_contexts, "bond_prefix_count": bond_prefix_count, "zero_commutator_rows": zero_rows, "first_variation_rows": first_rows, "second_variation_rows": second_rows, "modular_first_variation_rows": modular_rows, "dynamic_rows": dynamic_rows, "maximums": maximums, "volume_summaries": volume_summaries, "finite_position_boundary_commutes_with_coordinate_resolvent_closed": True, "finite_zero_first_variation_closed": True, "finite_second_variation_reduction_closed": True, "finite_modular_zero_first_variation_closed": True, "finite_quadratic_time_diagnostic_closed": True, "phase_local_bkm_estimate_closed": False, "boundary_shell_l1_closed": False, "cutoff_uniformity_closed": False, "source_uniformity_closed": False, "volume_uniformity_closed": False, "shape_uniformity_closed": False, "operator_domain_embedding_closed": False, "direct_D_cauchy_closed": False, "delta_D_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-RELATIVE-COCYCLE-COORDINATE-RESOLVENT-ZERO-TIME-ANCHOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT RELATIVE-COCYCLE ZERO-TIME-ANCHOR PASS {payload['passed']}/{payload['assertion_count']} contexts={payload['derived']['context_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
