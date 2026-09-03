#!/usr/bin/env python3
"""Primary modular-centering stress for EXP-001214 / R-372."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-modular-centering-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress as base  # noqa: E402
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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def pvm(q_single: np.ndarray) -> list[np.ndarray]:
    _, vectors = np.linalg.eigh(hermitian(q_single))
    return [np.outer(vectors[:, index], vectors[:, index].conj()) for index in range(vectors.shape[1])]


def measured(reduced: np.ndarray, projectors: list[np.ndarray], tolerance: float) -> np.ndarray:
    values = np.array([float(np.trace(projector @ reduced).real) for projector in projectors])
    if float(np.min(values)) < -tolerance:
        raise AssertionError(f"negative probability {float(np.min(values))}")
    values = np.maximum(values, 0.0)
    return values / float(np.sum(values))


def witness(reference: np.ndarray, projectors: list[np.ndarray]) -> np.ndarray:
    dimension = projectors[0].shape[0] ** 2
    answer = np.zeros((dimension, dimension), dtype=complex)
    for probability, projector in zip(reference, projectors):
        answer += np.kron(projector, projector) / probability
    return hermitian(answer)


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def all_prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[tuple[int, np.ndarray]]:
    identity = np.eye(terms[0].shape[0], dtype=complex)
    current = identity.copy()
    rows: list[tuple[int, np.ndarray]] = []
    for position in range(len(order) + 1):
        rows.append((position, current.copy()))
        if position < len(order):
            current = unitary(terms[order[position]], sign * delta, hbar) @ current
    return rows


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    regimes = fixture["regimes"]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tolerance = float(fixture["finite_tolerance"])
    gap_tolerance = float(fixture["log_mean_gap_tolerance"])
    parameters = fixture["parameters"]
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 128:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001214" and manifest["result_id"] == "R-372", [manifest["exploration_id"], manifest["result_id"]], "EXP-001214/R-372", "provenance")
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["local_variance_uniformity_proved"] is False, manifest["scope"], "finite-modular-centering-only", "scope")
    context_count = 0
    max_gibbs_identity_error = 0.0
    max_centering_identity_error = 0.0
    max_shell_centering_error = 0.0
    max_variance_bound_violation = -float("inf")
    max_raw_bound_violation = -float("inf")
    max_raw_second_moment = 0.0
    max_modular_variance = 0.0
    min_modular_variance = float("inf")
    max_variance_to_raw_ratio = 0.0
    max_center_shift = 0.0
    max_weight_asymmetry = 0.0
    min_weight = float("inf")
    max_unitary_error = 0.0
    per_regime: list[dict[str, Any]] = []

    for regime in regimes:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        bond_indices = [int(value) for value in regime["bond_term_indices"]]
        regime_start = context_count
        regime_max_raw = 0.0
        regime_max_variance = 0.0
        bond_rows: dict[str, dict[str, Any]] = {}
        for size in cutoffs:
            qs, hamiltonian, terms = base.split_system(volume, size, parameters)
            if any(index < 0 or index >= len(terms) for index in bond_indices):
                raise AssertionError(f"invalid bond term index for V={volume}: {bond_indices}")
            q_single, _ = q3.oscillator(size)
            identity_single = np.eye(size, dtype=complex)
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            projectors = pvm(q_single)
            orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
            embedded = [[base.embed(projector, site, volume, identity_single) for projector in projectors] for site in sites]
            for beta_fraction in betas:
                beta = float(beta_fraction)
                rho = base.gibbs(hamiltonian, beta)
                omega = np.kron(rho, rho)
                for site in sites:
                    reference = measured(base.reduced_site(rho, size, volume, site), projectors, tolerance)
                    local_witness = witness(reference, embedded[sites.index(site)])
                    for bond_term_index in bond_indices:
                        generator = np.kron(terms[bond_term_index], identity_global) + np.kron(identity_global, terms[bond_term_index])
                        eigenvalues, eigenvectors = np.linalg.eigh(hermitian(generator))
                        bond_unitary = unitary(terms[bond_term_index], delta, hbar)
                        bond_two = np.kron(bond_unitary, bond_unitary)
                        max_unitary_error = max(max_unitary_error, float(np.linalg.norm(bond_two - unitary(generator, delta, hbar), ord="fro")))
                        probabilities = np.exp(-beta * (eigenvalues - float(np.min(eigenvalues))))
                        probabilities /= float(np.sum(probabilities))
                        log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
                        arithmetic = 0.5 * (probabilities[:, None] + probabilities[None, :])
                        kubo = np.empty_like(log_gap)
                        close_gap = np.abs(log_gap) <= gap_tolerance
                        np.divide(probabilities[:, None] - probabilities[None, :], log_gap, out=kubo, where=~close_gap)
                        kubo[close_gap] = arithmetic[close_gap]
                        kubo = hermitian(kubo)
                        key = f"d={size}/bond={bond_term_index}"
                        row = bond_rows.setdefault(key, {"cutoff": size, "bond_term_index": bond_term_index, "maximum_raw_second_moment": 0.0, "maximum_modular_variance": 0.0, "maximum_variance_to_raw_ratio": 0.0, "context_count": 0})
                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Gibbs normalization", np.isfinite(probabilities).all() and abs(float(np.sum(probabilities)) - 1.0) <= gap_tolerance, float(np.sum(probabilities)), 1.0, "Kubo--Mori state")
                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Kubo symmetry", float(np.max(np.abs(kubo - kubo.T))) <= gap_tolerance, float(np.max(np.abs(kubo - kubo.T))), f"<={gap_tolerance}", "Kubo--Mori state")
                        max_weight_asymmetry = max(max_weight_asymmetry, float(np.max(np.abs(kubo - kubo.T))))
                        min_weight = min(min_weight, float(np.min(kubo)))
                        for order_name, order in orders.items():
                            for sign in signs:
                                for prefix_length, prefix in all_prefixes(terms, order, sign, delta, hbar):
                                    for history_adjoint in adjoints:
                                        evolution = prefix if not history_adjoint else prefix.conj().T
                                        doubled = np.kron(evolution, evolution)
                                        moved = hermitian(doubled.conj().T @ local_witness @ doubled)
                                        transformed = eigenvectors.conj().T @ moved @ eigenvectors
                                        deltas = eigenvalues[:, None] - eigenvalues[None, :]
                                        identity_error = float(np.max(np.abs(kubo * np.abs(deltas) - np.abs(probabilities[:, None] - probabilities[None, :]) / beta)))
                                        bond_mean = float(np.sum(probabilities * np.real(np.diag(transformed))))
                                        centered = transformed - bond_mean * np.eye(transformed.shape[0], dtype=complex)
                                        raw_second = float(np.sum(probabilities[:, None] * np.abs(transformed) ** 2))
                                        variance = float(np.sum(probabilities[:, None] * np.abs(centered) ** 2))
                                        centering_error = abs(variance - (raw_second - bond_mean * bond_mean))
                                        shell_raw = float(2.0 * np.sum(kubo * np.abs(deltas) * np.abs(transformed) ** 2))
                                        shell_centered = float(2.0 * np.sum(kubo * np.abs(deltas) * np.abs(centered) ** 2))
                                        shell_error = abs(shell_centered - shell_raw)
                                        bound = (4.0 / beta) * variance
                                        raw_bound = (4.0 / beta) * raw_second
                                        variance_violation = shell_centered - bound
                                        raw_violation = shell_raw - raw_bound
                                        max_gibbs_identity_error = max(max_gibbs_identity_error, identity_error)
                                        max_centering_identity_error = max(max_centering_identity_error, centering_error)
                                        max_shell_centering_error = max(max_shell_centering_error, shell_error)
                                        max_variance_bound_violation = max(max_variance_bound_violation, variance_violation)
                                        max_raw_bound_violation = max(max_raw_bound_violation, raw_violation)
                                        max_raw_second_moment = max(max_raw_second_moment, raw_second)
                                        max_modular_variance = max(max_modular_variance, variance)
                                        min_modular_variance = min(min_modular_variance, variance)
                                        max_center_shift = max(max_center_shift, abs(bond_mean))
                                        ratio = variance / raw_second if raw_second > tolerance ** 2 else 0.0
                                        max_variance_to_raw_ratio = max(max_variance_to_raw_ratio, ratio)
                                        regime_max_raw = max(regime_max_raw, raw_second)
                                        regime_max_variance = max(regime_max_variance, variance)
                                        row["maximum_raw_second_moment"] = max(row["maximum_raw_second_moment"], raw_second)
                                        row["maximum_modular_variance"] = max(row["maximum_modular_variance"], variance)
                                        row["maximum_variance_to_raw_ratio"] = max(row["maximum_variance_to_raw_ratio"], ratio)
                                        row["context_count"] += 1
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Gibbs cancellation", identity_error <= tolerance * 800, identity_error, f"<={tolerance * 800}", "Gibbs cancellation")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} centering identity", centering_error <= tolerance * 800 * (1.0 + raw_second), centering_error, f"<={tolerance * 800 * (1.0 + raw_second)}", "modular centering")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} shell invariance", shell_error <= tolerance * 800 * (1.0 + shell_raw), shell_error, f"<={tolerance * 800 * (1.0 + shell_raw)}", "modular centering")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} variance nonnegative", variance >= -tolerance * 800, variance, f">={-tolerance * 800}", "thermal variance")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} variance bound", variance_violation <= tolerance * 800 * (1.0 + bound), [shell_centered, bound], "<= bound", "thermal variance")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} raw bound", raw_violation <= tolerance * 800 * (1.0 + raw_bound), [shell_raw, raw_bound], "<= bound", "thermal variance")
                                        context_count += 1
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * ((len(terms) if cutoffs else 0) + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_raw_second_moment": regime_max_raw, "maximum_modular_variance": regime_max_variance, "bond_rows": list(bond_rows.values())})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("Gibbs cancellation identity", max_gibbs_identity_error <= tolerance * 800, max_gibbs_identity_error, f"<={tolerance * 800}", "Gibbs cancellation")
    check("modular centering identity", max_centering_identity_error <= tolerance * 800 * (1.0 + max_raw_second_moment), max_centering_identity_error, f"<={tolerance * 800 * (1.0 + max_raw_second_moment)}", "modular centering")
    check("shell centering invariance", max_shell_centering_error <= tolerance * 800 * (1.0 + max_raw_second_moment), max_shell_centering_error, f"<={tolerance * 800 * (1.0 + max_raw_second_moment)}", "modular centering")
    check("Kubo weight floor", min_weight >= -gap_tolerance, min_weight, f">={-gap_tolerance}", "Kubo--Mori state")
    check("thermal variance nonnegative", min_modular_variance >= -tolerance * 800, min_modular_variance, f">={-tolerance * 800}", "thermal variance")
    check("thermal variance bound", max_variance_bound_violation <= tolerance * 800 * (1.0 + 4.0 * max_modular_variance), max_variance_bound_violation, f"<={tolerance * 800 * (1.0 + 4.0 * max_modular_variance)}", "thermal variance")
    check("raw bound", max_raw_bound_violation <= tolerance * 800 * (1.0 + 4.0 * max_raw_second_moment), max_raw_bound_violation, f"<={tolerance * 800 * (1.0 + 4.0 * max_raw_second_moment)}", "thermal variance")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-MODULAR-CENTERING",
        "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"],
        "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {
            "context_count": context_count, "expected_contexts": expected_contexts, "theta": float(Fraction(fixture["theta"])), "regimes": per_regime,
            "maximum_gibbs_theta_half_identity_error": max_gibbs_identity_error, "maximum_centering_identity_error": max_centering_identity_error,
            "maximum_shell_centering_invariance_error": max_shell_centering_error, "maximum_thermal_variance_bound_violation": max_variance_bound_violation,
            "maximum_raw_second_moment_bound_violation": max_raw_bound_violation, "maximum_raw_local_gibbs_second_moment": max_raw_second_moment,
            "maximum_modular_local_gibbs_variance": max_modular_variance, "minimum_modular_local_gibbs_variance": min_modular_variance,
            "maximum_variance_to_raw_second_moment_ratio": max_variance_to_raw_ratio, "maximum_bond_gibbs_center_shift": max_center_shift,
            "maximum_kubo_weight_asymmetry": max_weight_asymmetry, "minimum_kubo_weight": min_weight, "maximum_bond_unitary_factorization_error": max_unitary_error,
            "modular_centering_identity_finite_checked": True, "thermal_variance_bound_finite_checked": True, "shell_centering_invariance_finite_checked": True,
            "local_second_moment_uniformity_proved": False, "local_variance_uniformity_proved": False, "weighted_cutoff_uniformity_proved": False,
            "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False,
            "local_modular_dirichlet_comparison_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False,
            "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False
        },
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY MODULAR-CENTERING PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} variance={payload['derived']['maximum_modular_local_gibbs_variance']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

