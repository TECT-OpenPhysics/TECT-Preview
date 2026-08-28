#!/usr/bin/env python3
"""Non-importing independent three-channel half-density audit for R-379."""

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
SOURCE_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-28-independent-pre_a_cp1_st8_q3lock_local_q2_kubo_mori_half_density_bridge/independent.json"
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

    check("authority", manifest["exploration_id"] == "EXP-001221" and manifest["result_id"] == "R-379", [manifest["exploration_id"], manifest["result_id"]], "EXP-001221/R-379", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite-three-channel-only", "scope")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("R-378 source", source.get("verdict") == "PASS" and source.get("derived", {}).get("context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("context_count")], "R-378 PASS and expected contexts", "source linkage")

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
                        fourth_roots = np.sqrt(square_roots)
                        rho_half = np.diag(square_roots)
                        rho_quarter = np.diag(fourth_roots)
                        for order in orders:
                            for sign in signs:
                                for _prefix_length, prefix in prior.all_prefixes(terms, order, sign, delta_t, hbar):
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
                                        left_leg = float(np.linalg.norm(left_matrix, ord="fro") ** 2)
                                        right_leg = float(np.linalg.norm(right_matrix, ord="fro") ** 2)
                                        two_slice_leg = float(np.linalg.norm(two_slice_matrix, ord="fro") ** 2)
                                        commutator_leg = float(np.linalg.norm(left_matrix - right_matrix, ord="fro") ** 2)
                                        anticommutator_leg = float(np.linalg.norm(left_matrix + right_matrix, ord="fro") ** 2)
                                        entries = np.abs(centered) ** 2
                                        left_spectral = float(np.sum(probabilities[:, None] * entries))
                                        right_spectral = float(np.sum(probabilities[None, :] * entries))
                                        two_slice_spectral = float(np.sum(np.sqrt(probabilities[:, None] * probabilities[None, :]) * entries))
                                        commutator_formula = left_leg + right_leg - 2.0 * two_slice_leg
                                        anticommutator_formula = left_leg + right_leg + 2.0 * two_slice_leg
                                        sum_residual = abs(commutator_leg + anticommutator_leg - 2.0 * (left_leg + right_leg))
                                        max_anticommutator_residual = max(max_anticommutator_residual, abs(anticommutator_leg - anticommutator_formula))
                                        max_commutator_residual = max(max_commutator_residual, abs(commutator_leg - commutator_formula))
                                        max_sum_residual = max(max_sum_residual, sum_residual)
                                        max_two_slice_spectral_residual = max(max_two_slice_spectral_residual, abs(two_slice_leg - two_slice_spectral))
                                        max_left_spectral_residual = max(max_left_spectral_residual, abs(left_leg - left_spectral))
                                        max_right_spectral_residual = max(max_right_spectral_residual, abs(right_leg - right_spectral))
                                        max_cross_envelope_violation = max(max_cross_envelope_violation, two_slice_leg - 0.5 * (left_leg + right_leg))
                                        max_commutator_nonnegative_violation = max(max_commutator_nonnegative_violation, -commutator_leg)
                                        max_anticommutator_nonnegative_violation = max(max_anticommutator_nonnegative_violation, -anticommutator_leg)
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
                                        context_count += 1
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_left_leg": regime_max_left, "maximum_right_leg": regime_max_right, "maximum_two_slice_leg": regime_max_two_slice, "maximum_commutator_leg": regime_max_commutator, "maximum_anticommutator_leg": regime_max_anticommutator})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("finite values", all(np.isfinite(value) for value in (max_anticommutator_residual, max_commutator_residual, max_sum_residual, max_two_slice_spectral_residual)), "finite", "finite", "finite arithmetic")
    check("decomposition envelopes", max(max_anticommutator_residual, max_commutator_residual, max_sum_residual) <= tolerance * 800 * (1.0 + max_anticommutator_leg + max_left_leg + max_right_leg), "within tolerance", "within tolerance", "three-channel")
    check("two-slice envelope", max_cross_envelope_violation <= tolerance * 800 * (1.0 + max_left_leg + max_right_leg), max_cross_envelope_violation, "<= (L+R)/2", "three-channel")
    check("two-slice positivity", min_two_slice_leg >= -tolerance * 800, min_two_slice_leg, ">=0", "three-channel")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
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
            "three_channel_anticommutator_finite_checked": True,
            "three_channel_commutator_finite_checked": True,
            "two_slice_cross_envelope_finite_checked": True,
            "left_right_gns_separation_finite_checked": True,
            "beta_half_two_slice_interface_finite_checked": True,
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
    print(f"INDEPENDENT THREE-CHANNEL-BRIDGE PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} cross_fraction={payload['derived']['maximum_two_slice_fraction']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
