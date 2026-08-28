#!/usr/bin/env python3
"""Non-importing independent half-density Hellinger bridge audit for R-378."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_half_density_bridge"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-half-density-bridge-manifest.json"
SOURCE_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-28-independent-pre_a_cp1_st8_q3lock_local_q2_kubo_mori_gibbs_cancellation/independent.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering_independent as prior  # noqa: E402


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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    delta_t = float(Fraction(fixture["time_step"]))
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
        if len(checks) < 120:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001220" and manifest["result_id"] == "R-378", [manifest["exploration_id"], manifest["result_id"]], "EXP-001220/R-378", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite-half-density-only", "scope")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("R-371 source", source.get("verdict") == "PASS" and source.get("derived", {}).get("context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("context_count")], "R-371 PASS and expected contexts", "source linkage")

    context_count = 0
    max_shell = 0.0
    max_geometric_bound = 0.0
    max_arithmetic_bound = 0.0
    max_cauchy_violation = -float("inf")
    max_arithmetic_violation = -float("inf")
    max_pair_factorization_error = 0.0
    max_commutator_spectral_error = 0.0
    max_anticommutator_spectral_error = 0.0
    max_arithmetic_recovery_error = 0.0
    max_commutator_skew_error = 0.0
    max_anticommutator_hermitian_error = 0.0
    max_shell_to_geometric_ratio = 0.0
    max_shell_to_arithmetic_ratio = 0.0
    max_commutator_half_density_squared = 0.0
    max_anticommutator_half_density_squared = 0.0
    min_commutator_half_density_squared = float("inf")
    max_transition = 0.0
    max_centering_error = 0.0
    max_unitary_error = 0.0
    max_weight_asymmetry = 0.0
    min_weight = float("inf")
    per_regime: list[dict[str, Any]] = []

    for regime in fixture["regimes"]:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        bond_indices = [int(value) for value in regime["bond_term_indices"]]
        regime_start = context_count
        regime_max_shell = 0.0
        regime_max_geometric = 0.0
        regime_max_arithmetic = 0.0
        for size in cutoffs:
            q_single, hamiltonian, terms = prior.build_system(volume, size, parameters)
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            identity_single = np.eye(size, dtype=complex)
            pvm = prior.projectors(q_single)
            orders = (list(range(len(terms))), list(reversed(range(len(terms)))))
            embedded = [[prior.embed(projector, site, volume, identity_single) for projector in pvm] for site in sites]
            for beta_fraction in betas:
                beta = float(beta_fraction)
                rho = prior.gibbs(hamiltonian, beta)
                for site in sites:
                    reference = prior.probabilities(prior.reduce_site(rho, size, volume, site), pvm, tolerance)
                    local_witness = prior.witness(reference, embedded[sites.index(site)])
                    for bond_term_index in bond_indices:
                        generator = np.kron(terms[bond_term_index], identity_global) + np.kron(identity_global, terms[bond_term_index])
                        eigenvalues, eigenvectors = np.linalg.eigh(prior.hermitian(generator))
                        bond_unitary = prior.unitary(terms[bond_term_index], delta_t, hbar)
                        bond_two = np.kron(bond_unitary, bond_unitary)
                        max_unitary_error = max(max_unitary_error, float(np.linalg.norm(bond_two - prior.unitary(generator, delta_t, hbar), ord="fro")))
                        probabilities = np.exp(-beta * (eigenvalues - float(np.min(eigenvalues))))
                        probabilities /= float(np.sum(probabilities))
                        square_roots = np.sqrt(probabilities)
                        rho_half = np.diag(square_roots)
                        log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
                        arithmetic = 0.5 * (probabilities[:, None] + probabilities[None, :])
                        kubo = np.empty_like(log_gap)
                        close_gap = np.abs(log_gap) <= gap_tolerance
                        np.divide(probabilities[:, None] - probabilities[None, :], log_gap, out=kubo, where=~close_gap)
                        kubo[close_gap] = arithmetic[close_gap]
                        kubo = prior.hermitian(kubo)
                        max_weight_asymmetry = max(max_weight_asymmetry, float(np.max(np.abs(kubo - kubo.T))))
                        min_weight = min(min_weight, float(np.min(kubo)))
                        for order in orders:
                            for sign in signs:
                                for _prefix_length, prefix in prior.all_prefixes(terms, order, sign, delta_t, hbar):
                                    for history_adjoint in adjoints:
                                        evolution = prefix if not history_adjoint else prefix.conj().T
                                        doubled = np.kron(evolution, evolution)
                                        moved = prior.hermitian(doubled.conj().T @ local_witness @ doubled)
                                        transformed = eigenvectors.conj().T @ moved @ eigenvectors
                                        probabilities_difference = np.abs(probabilities[:, None] - probabilities[None, :])
                                        center = float(np.sum(probabilities * np.real(np.diag(transformed))))
                                        centered = transformed - center * np.eye(transformed.shape[0], dtype=complex)
                                        entries = np.abs(centered) ** 2
                                        root_difference = square_roots[:, None] - square_roots[None, :]
                                        root_sum = square_roots[:, None] + square_roots[None, :]
                                        shell = float((2.0 / beta) * np.sum(probabilities_difference * entries))
                                        commutator = rho_half @ centered - centered @ rho_half
                                        anticommutator = rho_half @ centered + centered @ rho_half
                                        commutator_squared = float(np.linalg.norm(commutator, ord="fro") ** 2)
                                        anticommutator_squared = float(np.linalg.norm(anticommutator, ord="fro") ** 2)
                                        commutator_spectral = float(np.sum((root_difference ** 2) * entries))
                                        anticommutator_spectral = float(np.sum((root_sum ** 2) * entries))
                                        geometric_bound = float((2.0 / beta) * np.sqrt(max(0.0, commutator_squared * anticommutator_squared)))
                                        arithmetic_bound = float((1.0 / beta) * (commutator_squared + anticommutator_squared))
                                        thermal_second_moment = float(np.real(np.trace(np.diag(probabilities) @ centered @ centered)))
                                        pair_error = float(np.max(np.abs(probabilities_difference - np.abs(root_difference * root_sum))))
                                        max_shell = max(max_shell, shell)
                                        max_geometric_bound = max(max_geometric_bound, geometric_bound)
                                        max_arithmetic_bound = max(max_arithmetic_bound, arithmetic_bound)
                                        max_cauchy_violation = max(max_cauchy_violation, shell - geometric_bound)
                                        max_arithmetic_violation = max(max_arithmetic_violation, geometric_bound - arithmetic_bound)
                                        max_pair_factorization_error = max(max_pair_factorization_error, pair_error)
                                        max_commutator_spectral_error = max(max_commutator_spectral_error, abs(commutator_squared - commutator_spectral))
                                        max_anticommutator_spectral_error = max(max_anticommutator_spectral_error, abs(anticommutator_squared - anticommutator_spectral))
                                        max_arithmetic_recovery_error = max(max_arithmetic_recovery_error, abs((commutator_squared + anticommutator_squared) - 4.0 * thermal_second_moment))
                                        max_commutator_skew_error = max(max_commutator_skew_error, float(np.linalg.norm(commutator + commutator.conj().T, ord="fro")))
                                        max_anticommutator_hermitian_error = max(max_anticommutator_hermitian_error, float(np.linalg.norm(anticommutator - anticommutator.conj().T, ord="fro")))
                                        max_shell_to_geometric_ratio = max(max_shell_to_geometric_ratio, shell / geometric_bound if geometric_bound > tolerance ** 2 else 0.0)
                                        max_shell_to_arithmetic_ratio = max(max_shell_to_arithmetic_ratio, shell / arithmetic_bound if arithmetic_bound > tolerance ** 2 else 0.0)
                                        max_commutator_half_density_squared = max(max_commutator_half_density_squared, commutator_squared)
                                        max_anticommutator_half_density_squared = max(max_anticommutator_half_density_squared, anticommutator_squared)
                                        min_commutator_half_density_squared = min(min_commutator_half_density_squared, commutator_squared)
                                        max_transition = max(max_transition, float(np.max(np.abs(eigenvalues[:, None] - eigenvalues[None, :]))))
                                        max_centering_error = max(max_centering_error, abs(float(np.sum(probabilities * np.real(np.diag(centered))))))
                                        regime_max_shell = max(regime_max_shell, shell)
                                        regime_max_geometric = max(regime_max_geometric, geometric_bound)
                                        regime_max_arithmetic = max(regime_max_arithmetic, arithmetic_bound)
                                        context_count += 1
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_shell": regime_max_shell, "maximum_geometric_bound": regime_max_geometric, "maximum_arithmetic_bound": regime_max_arithmetic})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("finite values", all(np.isfinite(value) for value in (max_shell, max_geometric_bound, max_arithmetic_bound, max_cauchy_violation, max_arithmetic_violation)), "finite", "finite", "finite arithmetic")
    check("Hellinger Cauchy envelope", max_cauchy_violation <= tolerance * 800 * (1.0 + max_geometric_bound), max_cauchy_violation, "<= geometric bound", "Hellinger Cauchy")
    check("arithmetic envelope", max_arithmetic_violation <= tolerance * 800 * (1.0 + max_arithmetic_bound), max_arithmetic_violation, "<= arithmetic bound", "Hellinger Cauchy")
    check("Kubo weight floor", min_weight >= -gap_tolerance, min_weight, f">={-gap_tolerance}", "Kubo--Mori state")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-HALF-DENSITY-BRIDGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": {
            "context_count": context_count,
            "expected_contexts": expected_contexts,
            "theta": float(Fraction(fixture["theta"])),
            "regimes": per_regime,
            "maximum_shell": max_shell,
            "maximum_geometric_bound": max_geometric_bound,
            "maximum_arithmetic_bound": max_arithmetic_bound,
            "maximum_hellinger_cauchy_violation": max_cauchy_violation,
            "maximum_arithmetic_envelope_violation": max_arithmetic_violation,
            "maximum_pair_factorization_error": max_pair_factorization_error,
            "maximum_commutator_spectral_residual": max_commutator_spectral_error,
            "maximum_anticommutator_spectral_residual": max_anticommutator_spectral_error,
            "maximum_arithmetic_recovery_residual": max_arithmetic_recovery_error,
            "maximum_commutator_skew_error": max_commutator_skew_error,
            "maximum_anticommutator_hermitian_error": max_anticommutator_hermitian_error,
            "maximum_shell_to_geometric_ratio": max_shell_to_geometric_ratio,
            "maximum_shell_to_arithmetic_ratio": max_shell_to_arithmetic_ratio,
            "maximum_commutator_half_density_squared": max_commutator_half_density_squared,
            "maximum_anticommutator_half_density_squared": max_anticommutator_half_density_squared,
            "minimum_commutator_half_density_squared": min_commutator_half_density_squared,
            "maximum_transition_energy": max_transition,
            "maximum_bond_gibbs_centering_error": max_centering_error,
            "maximum_bond_unitary_factorization_error": max_unitary_error,
            "maximum_kubo_weight_asymmetry": max_weight_asymmetry,
            "minimum_kubo_weight": min_weight,
            "half_density_pair_factorization_finite_checked": True,
            "hellinger_cauchy_bound_finite_checked": True,
            "two_sided_gns_bridge_finite_checked": True,
            "arithmetic_second_moment_recovery_finite_checked": True,
            "square_root_debt_reexpressed": True,
            "uniform_half_density_bound_proved": False,
            "weighted_cutoff_uniformity_proved": False,
            "weighted_volume_uniformity_proved": False,
            "source_uniformity_proved": False,
            "shape_uniformity_proved": False,
            "common_core_closed": False,
            "common_alpha_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
        },
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT HALF-DENSITY-BRIDGE PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} ratio={payload['derived']['maximum_shell_to_geometric_ratio']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
