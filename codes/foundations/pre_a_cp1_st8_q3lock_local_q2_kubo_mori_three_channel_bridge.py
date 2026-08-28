#!/usr/bin/env python3
"""Primary three-channel half-density audit for EXP-001221 / R-379."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_three_channel_bridge"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-three-channel-bridge-manifest.json"
SOURCE_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-28-integrated-pre_a_cp1_st8_q3lock_local_q2_kubo_mori_half_density_bridge/integrated.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering as prior  # noqa: E402


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
        if len(checks) < 160:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001221" and manifest["result_id"] == "R-379", [manifest["exploration_id"], manifest["result_id"]], "EXP-001221/R-379", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite-three-channel-only", "scope")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("R-378 source", source.get("verdict") == "PASS" and source.get("derived", {}).get("primary", {}).get("context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("primary", {}).get("context_count")], "R-378 PASS and expected contexts", "source linkage")

    context_count = 0
    max_anticommutator_residual = 0.0
    max_commutator_residual = 0.0
    max_sum_residual = 0.0
    max_two_slice_spectral_residual = 0.0
    max_left_spectral_residual = 0.0
    max_right_spectral_residual = 0.0
    max_cross_envelope_violation = -float("inf")
    max_commutator_nonnegative_violation = -float("inf")
    max_anticommutator_nonnegative_violation = -float("inf")
    max_cross_fraction = 0.0
    max_left_leg = 0.0
    max_right_leg = 0.0
    max_two_slice_leg = 0.0
    max_commutator_leg = 0.0
    max_anticommutator_leg = 0.0
    min_two_slice_leg = float("inf")
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
        regime_max_left = 0.0
        regime_max_right = 0.0
        regime_max_two_slice = 0.0
        regime_max_commutator = 0.0
        regime_max_anticommutator = 0.0
        for size in cutoffs:
            _, hamiltonian, terms = prior.base.split_system(volume, size, parameters)
            q_single, _ = prior.q3.oscillator(size)
            identity_single = np.eye(size, dtype=complex)
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            pvm = prior.pvm(q_single)
            orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
            embedded = [[prior.base.embed(projector, site, volume, identity_single) for projector in pvm] for site in sites]
            for beta_fraction in betas:
                beta = float(beta_fraction)
                rho = prior.base.gibbs(hamiltonian, beta)
                for site in sites:
                    reference = prior.measured(prior.base.reduced_site(rho, size, volume, site), pvm, tolerance)
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
                        fourth_roots = np.sqrt(square_roots)
                        rho_half = np.diag(square_roots)
                        rho_quarter = np.diag(fourth_roots)
                        log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
                        arithmetic = 0.5 * (probabilities[:, None] + probabilities[None, :])
                        kubo = np.empty_like(log_gap)
                        close_gap = np.abs(log_gap) <= gap_tolerance
                        np.divide(probabilities[:, None] - probabilities[None, :], log_gap, out=kubo, where=~close_gap)
                        kubo[close_gap] = arithmetic[close_gap]
                        kubo = prior.hermitian(kubo)
                        max_weight_asymmetry = max(max_weight_asymmetry, float(np.max(np.abs(kubo - kubo.T))))
                        min_weight = min(min_weight, float(np.min(kubo)))
                        for order_name, order in orders.items():
                            for sign in signs:
                                for prefix_length, prefix in prior.all_prefixes(terms, order, sign, delta_t, hbar):
                                    for history_adjoint in adjoints:
                                        evolution = prefix if not history_adjoint else prefix.conj().T
                                        doubled = np.kron(evolution, evolution)
                                        moved = prior.hermitian(doubled.conj().T @ local_witness @ doubled)
                                        transformed = eigenvectors.conj().T @ moved @ eigenvectors
                                        center = float(np.sum(probabilities * np.real(np.diag(transformed))))
                                        centered = transformed - center * np.eye(transformed.shape[0], dtype=complex)
                                        left_matrix = rho_half @ centered
                                        right_matrix = centered @ rho_half
                                        two_slice_matrix = rho_quarter @ centered @ rho_quarter
                                        commutator = left_matrix - right_matrix
                                        anticommutator = left_matrix + right_matrix
                                        left_leg = float(np.linalg.norm(left_matrix, ord="fro") ** 2)
                                        right_leg = float(np.linalg.norm(right_matrix, ord="fro") ** 2)
                                        two_slice_leg = float(np.linalg.norm(two_slice_matrix, ord="fro") ** 2)
                                        commutator_leg = float(np.linalg.norm(commutator, ord="fro") ** 2)
                                        anticommutator_leg = float(np.linalg.norm(anticommutator, ord="fro") ** 2)
                                        entries = np.abs(centered) ** 2
                                        left_spectral = float(np.sum(probabilities[:, None] * entries))
                                        right_spectral = float(np.sum(probabilities[None, :] * entries))
                                        two_slice_spectral = float(np.sum(np.sqrt(probabilities[:, None] * probabilities[None, :]) * entries))
                                        commutator_formula = left_leg + right_leg - 2.0 * two_slice_leg
                                        anticommutator_formula = left_leg + right_leg + 2.0 * two_slice_leg
                                        sum_formula = commutator_leg + anticommutator_leg - 2.0 * (left_leg + right_leg)
                                        cross_envelope_violation = two_slice_leg - 0.5 * (left_leg + right_leg)
                                        commutator_nonnegative_violation = -commutator_leg
                                        anticommutator_nonnegative_violation = -anticommutator_leg
                                        commutator_residual = abs(commutator_leg - commutator_formula)
                                        anticommutator_residual = abs(anticommutator_leg - anticommutator_formula)
                                        sum_residual = abs(sum_formula)
                                        max_anticommutator_residual = max(max_anticommutator_residual, anticommutator_residual)
                                        max_commutator_residual = max(max_commutator_residual, commutator_residual)
                                        max_sum_residual = max(max_sum_residual, sum_residual)
                                        max_two_slice_spectral_residual = max(max_two_slice_spectral_residual, abs(two_slice_leg - two_slice_spectral))
                                        max_left_spectral_residual = max(max_left_spectral_residual, abs(left_leg - left_spectral))
                                        max_right_spectral_residual = max(max_right_spectral_residual, abs(right_leg - right_spectral))
                                        max_cross_envelope_violation = max(max_cross_envelope_violation, cross_envelope_violation)
                                        max_commutator_nonnegative_violation = max(max_commutator_nonnegative_violation, commutator_nonnegative_violation)
                                        max_anticommutator_nonnegative_violation = max(max_anticommutator_nonnegative_violation, anticommutator_nonnegative_violation)
                                        max_cross_fraction = max(max_cross_fraction, two_slice_leg / (0.5 * (left_leg + right_leg)) if left_leg + right_leg > tolerance ** 2 else 0.0)
                                        max_left_leg = max(max_left_leg, left_leg)
                                        max_right_leg = max(max_right_leg, right_leg)
                                        max_two_slice_leg = max(max_two_slice_leg, two_slice_leg)
                                        max_commutator_leg = max(max_commutator_leg, commutator_leg)
                                        max_anticommutator_leg = max(max_anticommutator_leg, anticommutator_leg)
                                        min_two_slice_leg = min(min_two_slice_leg, two_slice_leg)
                                        max_centering_error = max(max_centering_error, abs(float(np.sum(probabilities * np.real(np.diag(centered))))))
                                        regime_max_left = max(regime_max_left, left_leg)
                                        regime_max_right = max(regime_max_right, right_leg)
                                        regime_max_two_slice = max(regime_max_two_slice, two_slice_leg)
                                        regime_max_commutator = max(regime_max_commutator, commutator_leg)
                                        regime_max_anticommutator = max(regime_max_anticommutator, anticommutator_leg)
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} left spectral form", abs(left_leg - left_spectral) <= tolerance * 800 * (1.0 + left_leg), abs(left_leg - left_spectral), "spectral left leg", "three-channel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} right spectral form", abs(right_leg - right_spectral) <= tolerance * 800 * (1.0 + right_leg), abs(right_leg - right_spectral), "spectral right leg", "three-channel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} two-slice spectral form", abs(two_slice_leg - two_slice_spectral) <= tolerance * 800 * (1.0 + two_slice_leg), abs(two_slice_leg - two_slice_spectral), "spectral two-slice leg", "three-channel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} commutator decomposition", commutator_residual <= tolerance * 800 * (1.0 + commutator_leg), commutator_residual, "L+R-2T", "three-channel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} anticommutator decomposition", anticommutator_residual <= tolerance * 800 * (1.0 + anticommutator_leg), anticommutator_residual, "L+R+2T", "three-channel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} sum decomposition", sum_residual <= tolerance * 800 * (1.0 + left_leg + right_leg), sum_residual, "2(L+R)", "three-channel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} two-slice envelope", cross_envelope_violation <= tolerance * 800 * (1.0 + left_leg + right_leg), cross_envelope_violation, "<= (L+R)/2", "three-channel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} commutator nonnegative", commutator_nonnegative_violation <= tolerance * 800, commutator_nonnegative_violation, ">=0", "three-channel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} anticommutator nonnegative", anticommutator_nonnegative_violation <= tolerance * 800, anticommutator_nonnegative_violation, ">=0", "three-channel")
                                        context_count += 1
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_left_leg": regime_max_left, "maximum_right_leg": regime_max_right, "maximum_two_slice_leg": regime_max_two_slice, "maximum_commutator_leg": regime_max_commutator, "maximum_anticommutator_leg": regime_max_anticommutator})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("commutator decomposition", max_commutator_residual <= tolerance * 800 * (1.0 + max_commutator_leg), max_commutator_residual, "decomposition", "three-channel")
    check("anticommutator decomposition", max_anticommutator_residual <= tolerance * 800 * (1.0 + max_anticommutator_leg), max_anticommutator_residual, "decomposition", "three-channel")
    check("sum decomposition", max_sum_residual <= tolerance * 800 * (1.0 + max_left_leg + max_right_leg), max_sum_residual, "2(L+R)", "three-channel")
    check("two-slice envelope", max_cross_envelope_violation <= tolerance * 800 * (1.0 + max_left_leg + max_right_leg), max_cross_envelope_violation, "<= (L+R)/2", "three-channel")
    check("two-slice positivity", min_two_slice_leg >= -tolerance * 800, min_two_slice_leg, ">=0", "three-channel")
    check("Kubo weight floor", min_weight >= -gap_tolerance, min_weight, f">={-gap_tolerance}", "Kubo--Mori state")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-THREE-CHANNEL-BRIDGE",
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
            "maximum_anticommutator_decomposition_residual": max_anticommutator_residual,
            "maximum_commutator_decomposition_residual": max_commutator_residual,
            "maximum_sum_decomposition_residual": max_sum_residual,
            "maximum_two_slice_spectral_residual": max_two_slice_spectral_residual,
            "maximum_left_spectral_residual": max_left_spectral_residual,
            "maximum_right_spectral_residual": max_right_spectral_residual,
            "maximum_two_slice_envelope_violation": max_cross_envelope_violation,
            "maximum_commutator_nonnegative_violation": max_commutator_nonnegative_violation,
            "maximum_anticommutator_nonnegative_violation": max_anticommutator_nonnegative_violation,
            "maximum_two_slice_fraction": max_cross_fraction,
            "maximum_left_leg": max_left_leg,
            "maximum_right_leg": max_right_leg,
            "maximum_two_slice_leg": max_two_slice_leg,
            "maximum_commutator_leg": max_commutator_leg,
            "maximum_anticommutator_leg": max_anticommutator_leg,
            "minimum_two_slice_leg": min_two_slice_leg,
            "maximum_bond_gibbs_centering_error": max_centering_error,
            "maximum_bond_unitary_factorization_error": max_unitary_error,
            "maximum_kubo_weight_asymmetry": max_weight_asymmetry,
            "minimum_kubo_weight": min_weight,
            "three_channel_anticommutator_finite_checked": True,
            "three_channel_commutator_finite_checked": True,
            "two_slice_cross_envelope_finite_checked": True,
            "left_right_gns_separation_finite_checked": True,
            "beta_half_two_slice_interface_finite_checked": True,
            "uniform_half_density_channels_proved": False,
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
    print(f"PRIMARY THREE-CHANNEL-BRIDGE PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} cross_fraction={payload['derived']['maximum_two_slice_fraction']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
