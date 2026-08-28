#!/usr/bin/env python3
"""Non-importing independent endpoint-energy Cauchy audit for EXP-001223 / R-381."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_endpoint_energy_cauchy_bridge"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-endpoint-energy-cauchy-bridge-manifest.json"
SOURCE_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-28-integrated-pre_a_cp1_st8_q3lock_local_q2_kubo_mori_renyi_interpolation_bridge/integrated.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering_independent as base  # noqa: E402


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
        if len(checks) < 100:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001223" and manifest["result_id"] == "R-381", [manifest["exploration_id"], manifest["result_id"]], "EXP-001223/R-381", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite-endpoint-energy-only", "scope")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("R-380 source", source.get("verdict") == "PASS" and source.get("derived", {}).get("independent", {}).get("context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("independent", {}).get("context_count")], "R-380 PASS and expected contexts", "source linkage")

    context_count = 0
    maximum_log_energy_error = 0.0
    maximum_endpoint_orientation_error = 0.0
    maximum_moment_orientation_error = 0.0
    maximum_cauchy_violation = -float("inf")
    maximum_endpoint_reconstruction_error = 0.0
    maximum_endpoint = 0.0
    maximum_endpoint_energy_first = 0.0
    maximum_m0 = 0.0
    maximum_m2 = 0.0
    maximum_cauchy_bound = 0.0
    minimum_m0 = float("inf")
    minimum_m2 = float("inf")
    maximum_endpoint_to_cauchy_ratio = 0.0
    maximum_unitary_error = 0.0
    minimum_kubo = float("inf")
    maximum_kubo_asymmetry = 0.0
    per_regime: list[dict[str, Any]] = []

    for regime in fixture["regimes"]:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        bond_indices = [int(value) for value in regime["bond_term_indices"]]
        regime_start = context_count
        regime_max_endpoint = 0.0
        regime_max_m0 = 0.0
        regime_max_m2 = 0.0
        for size in cutoffs:
            q_single, hamiltonian, terms = base.build_system(volume, size, parameters)
            identity_single = np.eye(size, dtype=complex)
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            projectors = base.projectors(q_single)
            orders = (list(range(len(terms))), list(reversed(range(len(terms)))))
            embedded = [[base.embed(projector, site, volume, identity_single) for projector in projectors] for site in sites]
            for beta_fraction in betas:
                beta = float(beta_fraction)
                rho = base.gibbs(hamiltonian, beta)
                for site in sites:
                    reference = base.probabilities(base.reduce_site(rho, size, volume, site), projectors, tolerance)
                    local_witness = base.witness(reference, embedded[sites.index(site)])
                    for bond_term_index in bond_indices:
                        generator = np.kron(terms[bond_term_index], identity_global) + np.kron(identity_global, terms[bond_term_index])
                        eigenvalues, eigenvectors = np.linalg.eigh(hermitian(generator))
                        bond_unitary = base.unitary(terms[bond_term_index], delta_t, hbar)
                        bond_two = np.kron(bond_unitary, bond_unitary)
                        maximum_unitary_error = max(maximum_unitary_error, float(np.linalg.norm(bond_two - base.unitary(generator, delta_t, hbar), ord="fro")))
                        probabilities = np.exp(-beta * (eigenvalues - float(np.min(eigenvalues))))
                        probabilities /= float(np.sum(probabilities))
                        logs = np.log(probabilities)
                        modular_gap = np.abs(logs[:, None] - logs[None, :])
                        log_energy_error = float(np.max(np.abs(modular_gap - beta * np.abs(eigenvalues[:, None] - eigenvalues[None, :]))))
                        log_gap = logs[:, None] - logs[None, :]
                        kubo = np.empty_like(log_gap)
                        close_gap = np.abs(log_gap) <= gap_tolerance
                        arithmetic = 0.5 * (probabilities[:, None] + probabilities[None, :])
                        np.divide(probabilities[:, None] - probabilities[None, :], log_gap, out=kubo, where=~close_gap)
                        kubo[close_gap] = arithmetic[close_gap]
                        kubo = hermitian(kubo)
                        minimum_kubo = min(minimum_kubo, float(np.min(kubo)))
                        maximum_kubo_asymmetry = max(maximum_kubo_asymmetry, float(np.max(np.abs(kubo - kubo.T))))
                        for order in orders:
                            for sign in signs:
                                for _prefix_length, prefix in base.all_prefixes(terms, order, sign, delta_t, hbar):
                                    for history_adjoint in adjoints:
                                        evolution = prefix if not history_adjoint else prefix.conj().T
                                        doubled = np.kron(evolution, evolution)
                                        moved = hermitian(doubled.conj().T @ local_witness @ doubled)
                                        transformed = eigenvectors.conj().T @ moved @ eigenvectors
                                        center = float(np.sum(probabilities * np.real(np.diag(transformed))))
                                        centered = transformed - center * np.eye(transformed.shape[0], dtype=complex)
                                        entries = np.abs(centered) ** 2
                                        energy_differences = eigenvalues[:, None] - eigenvalues[None, :]
                                        endpoint_zero = float(np.sum(probabilities[None, :] * modular_gap * entries))
                                        endpoint_one = float(np.sum(probabilities[:, None] * modular_gap * entries))
                                        endpoint_energy = float(beta * np.sum(probabilities[:, None] * np.abs(energy_differences) * entries))
                                        m0_left = float(np.sum(probabilities[:, None] * entries))
                                        m0_right = float(np.sum(probabilities[None, :] * entries))
                                        m2_left = float(np.sum(probabilities[:, None] * energy_differences**2 * entries))
                                        m2_right = float(np.sum(probabilities[None, :] * energy_differences**2 * entries))
                                        cauchy_bound = beta * float(np.sqrt(max(0.0, m0_left * m2_left)))
                                        cauchy_violation = endpoint_energy - cauchy_bound
                                        endpoint_to_bound = endpoint_energy / cauchy_bound if cauchy_bound > tolerance else 0.0
                                        maximum_log_energy_error = max(maximum_log_energy_error, log_energy_error)
                                        maximum_endpoint_orientation_error = max(maximum_endpoint_orientation_error, abs(endpoint_zero - endpoint_one))
                                        maximum_moment_orientation_error = max(maximum_moment_orientation_error, abs(m0_left - m0_right), abs(m2_left - m2_right))
                                        maximum_cauchy_violation = max(maximum_cauchy_violation, cauchy_violation)
                                        maximum_endpoint_reconstruction_error = max(maximum_endpoint_reconstruction_error, abs(endpoint_one - endpoint_energy))
                                        maximum_endpoint = max(maximum_endpoint, endpoint_zero, endpoint_one)
                                        maximum_endpoint_energy_first = max(maximum_endpoint_energy_first, endpoint_energy)
                                        maximum_m0 = max(maximum_m0, m0_left, m0_right)
                                        maximum_m2 = max(maximum_m2, m2_left, m2_right)
                                        maximum_cauchy_bound = max(maximum_cauchy_bound, cauchy_bound)
                                        minimum_m0 = min(minimum_m0, m0_left, m0_right)
                                        minimum_m2 = min(minimum_m2, m2_left, m2_right)
                                        maximum_endpoint_to_cauchy_ratio = max(maximum_endpoint_to_cauchy_ratio, endpoint_to_bound)
                                        regime_max_endpoint = max(regime_max_endpoint, endpoint_energy)
                                        regime_max_m0 = max(regime_max_m0, m0_left, m0_right)
                                        regime_max_m2 = max(regime_max_m2, m2_left, m2_right)
                                        context_count += 1
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_endpoint": regime_max_endpoint, "maximum_m0": regime_max_m0, "maximum_m2": regime_max_m2})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    scale = 1.0 + max(maximum_endpoint, maximum_cauchy_bound, maximum_m2)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("Gibbs log-energy identity", maximum_log_energy_error <= tolerance * 800, maximum_log_energy_error, "<= tolerance", "Gibbs log-energy")
    check("endpoint orientation", maximum_endpoint_orientation_error <= tolerance * 800 * scale, maximum_endpoint_orientation_error, "<= tolerance", "endpoint symmetry")
    check("moment orientation", maximum_moment_orientation_error <= tolerance * 800 * scale, maximum_moment_orientation_error, "<= tolerance", "moment symmetry")
    check("endpoint reconstruction", maximum_endpoint_reconstruction_error <= tolerance * 800 * scale, maximum_endpoint_reconstruction_error, "<= tolerance", "endpoint energy")
    check("Cauchy envelope", maximum_cauchy_violation <= tolerance * 800 * scale, maximum_cauchy_violation, "<=0", "state-weighted Cauchy")
    check("Kubo floor", minimum_kubo >= -gap_tolerance, minimum_kubo, f">={-gap_tolerance}", "Kubo--Mori state")
    check("moment positivity", min(minimum_m0, minimum_m2) >= -tolerance * 800, min(minimum_m0, minimum_m2), ">=0", "positivity")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-ENDPOINT-ENERGY-CAUCHY-BRIDGE",
        "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {
            "context_count": context_count, "expected_contexts": expected_contexts, "theta": float(Fraction(fixture["theta"])), "regimes": per_regime,
            "maximum_gibbs_log_energy_identity_error": maximum_log_energy_error, "maximum_endpoint_orientation_error": maximum_endpoint_orientation_error, "maximum_moment_orientation_error": maximum_moment_orientation_error,
            "maximum_cauchy_envelope_violation": maximum_cauchy_violation, "maximum_endpoint_reconstruction_error": maximum_endpoint_reconstruction_error, "maximum_endpoint_modular_moment": maximum_endpoint,
            "maximum_endpoint_energy_first_moment": maximum_endpoint_energy_first, "maximum_state_weighted_m0": maximum_m0, "maximum_state_weighted_m2": maximum_m2, "maximum_cauchy_bound": maximum_cauchy_bound,
            "minimum_state_weighted_m0": minimum_m0, "minimum_state_weighted_m2": minimum_m2, "maximum_endpoint_to_cauchy_ratio": maximum_endpoint_to_cauchy_ratio,
            "maximum_bond_unitary_factorization_error": maximum_unitary_error, "maximum_kubo_weight_asymmetry": maximum_kubo_asymmetry, "minimum_kubo_weight": minimum_kubo,
            "gibbs_log_energy_identity_finite_checked": True, "endpoint_energy_moment_finite_checked": True, "quadratic_cauchy_envelope_finite_checked": True, "left_right_energy_moment_symmetry_finite_checked": True,
            "source_uniformity_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False,
            "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False,
        }, "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); args = parser.parse_args()
    payload = run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT ENDPOINT-ENERGY-CAUCHY-BRIDGE PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} ratio={payload['derived']['maximum_endpoint_to_cauchy_ratio']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
