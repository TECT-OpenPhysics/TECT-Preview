#!/usr/bin/env python3
"""Primary two-scale filter-removal corridor audit for EXP-001226 / R-384."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_two_scale_filter_removal_corridor"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-two-scale-filter-removal-corridor-manifest.json"
SOURCE_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-28-integrated-pre_a_cp1_st8_q3lock_local_q2_kubo_mori_frequency_adapted_endpoint_filter/integrated.json"
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
    reference_power = float(Fraction(fixture["filter_power"]))
    filters = [(str(fixture["filter_power"]), reference_power)]
    energy_windows = [(str(raw), float(Fraction(raw))) for raw in fixture["energy_windows"]]
    parameters = fixture["parameters"]
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 180:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001226" and manifest["result_id"] == "R-384", [manifest["exploration_id"], manifest["result_id"]], "EXP-001226/R-384", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite-endpoint-energy-only", "scope")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("R-382 source", source.get("verdict") == "PASS" and source.get("derived", {}).get("primary", {}).get("context_count") == int(fixture["expected_parent_contexts"]), [source.get("verdict"), source.get("derived", {}).get("primary", {}).get("context_count")], "R-383 PASS and expected parent contexts", "source linkage")

    context_count = 0
    max_log_energy_error = 0.0
    max_endpoint_orientation_error = 0.0
    max_moment_orientation_error = 0.0
    max_cauchy_violation = -float("inf")
    max_endpoint_reconstruction_error = 0.0
    max_endpoint = 0.0
    max_energy_first = 0.0
    max_m0 = 0.0
    max_m2 = 0.0
    max_cauchy_bound = 0.0
    min_m0 = float("inf")
    min_m2 = float("inf")
    max_endpoint_to_bound_ratio = 0.0
    max_unitary_error = 0.0
    min_kubo = float("inf")
    max_kubo_asymmetry = 0.0
    per_regime: list[dict[str, Any]] = []
    cutoff_profiles: list[dict[str, Any]] = []
    filtered_profiles: list[dict[str, Any]] = []
    corridor_profiles: list[dict[str, Any]] = []

    for regime in fixture["regimes"]:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        bond_indices = [int(value) for value in regime["bond_term_indices"]]
        regime_start = context_count
        regime_profile_start = len(cutoff_profiles)
        regime_filter_start = len(filtered_profiles)
        regime_corridor_start = len(corridor_profiles)
        regime_max_endpoint = 0.0
        regime_max_first = 0.0
        regime_max_m0 = 0.0
        regime_max_m2 = 0.0
        for size in cutoffs:
            cutoff_context_start = context_count
            cutoff_max_endpoint = 0.0
            cutoff_max_m0 = 0.0
            cutoff_max_m2 = 0.0
            cutoff_max_cauchy = 0.0
            cutoff_max_ratio = 0.0
            cutoff_filter_profiles = {
                label: {"power": power, "contexts": 0, "maximum_endpoint": 0.0, "maximum_m0": 0.0, "maximum_m2": 0.0, "maximum_cauchy_bound": 0.0, "maximum_endpoint_to_cauchy_ratio": 0.0}
                for label, power in filters
            }
            cutoff_corridor_profiles = {
                label: {"energy_window": window, "contexts": 0, "maximum_low_m0": 0.0, "maximum_high_m0": 0.0, "maximum_low_m2": 0.0, "maximum_high_m2": 0.0, "maximum_removal_m0": 0.0, "maximum_removal_m0_envelope": 0.0, "maximum_endpoint_removal": 0.0, "maximum_endpoint_removal_envelope": 0.0, "maximum_partition_error_m0": 0.0, "maximum_partition_error_m2": 0.0}
                for label, window in energy_windows
            }
            _, hamiltonian, terms = prior.base.split_system(volume, size, parameters)
            q_single, _ = prior.q3.oscillator(size)
            identity_single = np.eye(size, dtype=complex)
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            projectors = prior.pvm(q_single)
            orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
            embedded = [[prior.base.embed(projector, site, volume, identity_single) for projector in projectors] for site in sites]
            for beta_fraction in betas:
                beta = float(beta_fraction)
                rho = prior.base.gibbs(hamiltonian, beta)
                for site in sites:
                    reference = prior.measured(prior.base.reduced_site(rho, size, volume, site), projectors, tolerance)
                    local_witness = prior.witness(reference, embedded[sites.index(site)])
                    for bond_term_index in bond_indices:
                        generator = np.kron(terms[bond_term_index], identity_global) + np.kron(identity_global, terms[bond_term_index])
                        eigenvalues, eigenvectors = np.linalg.eigh(prior.hermitian(generator))
                        bond_unitary = prior.unitary(terms[bond_term_index], delta_t, hbar)
                        bond_two = np.kron(bond_unitary, bond_unitary)
                        max_unitary_error = max(max_unitary_error, float(np.linalg.norm(bond_two - prior.unitary(generator, delta_t, hbar), ord="fro")))
                        probabilities = np.exp(-beta * (eigenvalues - float(np.min(eigenvalues))))
                        probabilities /= float(np.sum(probabilities))
                        logs = np.log(probabilities)
                        log_gap = logs[:, None] - logs[None, :]
                        modular_gap = np.abs(log_gap)
                        arithmetic = 0.5 * (probabilities[:, None] + probabilities[None, :])
                        kubo = np.empty_like(log_gap)
                        close_gap = np.abs(log_gap) <= gap_tolerance
                        np.divide(probabilities[:, None] - probabilities[None, :], log_gap, out=kubo, where=~close_gap)
                        kubo[close_gap] = arithmetic[close_gap]
                        kubo = prior.hermitian(kubo)
                        min_kubo = min(min_kubo, float(np.min(kubo)))
                        max_kubo_asymmetry = max(max_kubo_asymmetry, float(np.max(np.abs(kubo - kubo.T))))
                        log_energy_error = float(np.max(np.abs(modular_gap - beta * np.abs(eigenvalues[:, None] - eigenvalues[None, :]))))
                        for order in orders.values():
                            for sign in signs:
                                for _prefix_length, prefix in prior.all_prefixes(terms, order, sign, delta_t, hbar):
                                    for history_adjoint in adjoints:
                                        evolution = prefix if not history_adjoint else prefix.conj().T
                                        doubled = np.kron(evolution, evolution)
                                        moved = prior.hermitian(doubled.conj().T @ local_witness @ doubled)
                                        transformed = eigenvectors.conj().T @ moved @ eigenvectors
                                        center = float(np.sum(probabilities * np.real(np.diag(transformed))))
                                        centered = transformed - center * np.eye(transformed.shape[0], dtype=complex)
                                        entries = np.abs(centered) ** 2
                                        raw_m0_left = float(np.sum(probabilities[:, None] * entries))
                                        energy_differences = eigenvalues[:, None] - eigenvalues[None, :]
                                        absolute_energy_differences = np.abs(energy_differences)
                                        for filter_label, filter_power in filters:
                                            filter_weight = np.power(1.0 + absolute_energy_differences, -2.0 * filter_power)
                                            filtered_entries = entries * filter_weight
                                            filtered_endpoint = float(beta * np.sum(probabilities[:, None] * absolute_energy_differences * filtered_entries))
                                            filtered_m0 = float(np.sum(probabilities[:, None] * filtered_entries))
                                            filtered_m2 = float(np.sum(probabilities[:, None] * energy_differences ** 2 * filtered_entries))
                                            filtered_cauchy = beta * float(np.sqrt(max(0.0, filtered_m0 * filtered_m2)))
                                            filtered_ratio = filtered_endpoint / filtered_cauchy if filtered_cauchy > tolerance else 0.0
                                            profile = cutoff_filter_profiles[filter_label]
                                            profile["contexts"] += 1
                                            profile["maximum_endpoint"] = max(profile["maximum_endpoint"], filtered_endpoint)
                                            profile["maximum_m0"] = max(profile["maximum_m0"], filtered_m0)
                                            profile["maximum_m2"] = max(profile["maximum_m2"], filtered_m2)
                                            profile["maximum_cauchy_bound"] = max(profile["maximum_cauchy_bound"], filtered_cauchy)
                                            profile["maximum_endpoint_to_cauchy_ratio"] = max(profile["maximum_endpoint_to_cauchy_ratio"], filtered_ratio)
                                            filter_scale = 1.0 + max(filtered_endpoint, filtered_cauchy, filtered_m0, filtered_m2, raw_m0_left)
                                            check("filtered finite values", all(np.isfinite(value) for value in [filtered_endpoint, filtered_m0, filtered_m2, filtered_cauchy]), "finite", "finite", "filtered endpoint shell")
                                            check("filtered M0 contraction", filtered_m0 <= raw_m0_left + tolerance * 800 * filter_scale, filtered_m0, "<= raw M0", "filtered envelope")
                                            check("filtered Cauchy envelope", filtered_endpoint - filtered_cauchy <= tolerance * 800 * filter_scale, filtered_endpoint - filtered_cauchy, "<=0", "filtered Cauchy")
                                            if filter_power >= 0.5:
                                                check("filtered endpoint scalar envelope", filtered_endpoint <= beta * raw_m0_left + tolerance * 800 * filter_scale, filtered_endpoint, "<= beta*M0", "filtered endpoint")
                                            if filter_power >= 1.0:
                                                check("filtered M2 scalar envelope", filtered_m2 <= raw_m0_left + tolerance * 800 * filter_scale, filtered_m2, "<= raw M0", "filtered energy envelope")
                                        endpoint_zero = float(np.sum(probabilities[None, :] * modular_gap * entries))
                                        endpoint_one = float(np.sum(probabilities[:, None] * modular_gap * entries))
                                        endpoint_energy = float(beta * np.sum(probabilities[:, None] * absolute_energy_differences * entries))
                                        m0_left = float(np.sum(probabilities[:, None] * entries))
                                        m0_right = float(np.sum(probabilities[None, :] * entries))
                                        m2_left = float(np.sum(probabilities[:, None] * energy_differences ** 2 * entries))
                                        m2_right = float(np.sum(probabilities[None, :] * energy_differences ** 2 * entries))
                                        reference_filter_weight = np.power(1.0 + absolute_energy_differences, -2.0 * reference_power)
                                        reference_filter_difference = 1.0 - reference_filter_weight
                                        reference_endpoint = float(beta * np.sum(probabilities[:, None] * absolute_energy_differences * reference_filter_weight * entries))
                                        endpoint_removal_actual = max(0.0, endpoint_energy - reference_endpoint)
                                        for window_label, energy_window in energy_windows:
                                            low_mask = absolute_energy_differences <= energy_window + gap_tolerance
                                            high_mask = ~low_mask
                                            low_m0 = float(np.sum(probabilities[:, None] * entries * low_mask))
                                            high_m0 = float(np.sum(probabilities[:, None] * entries * high_mask))
                                            low_m2 = float(np.sum(probabilities[:, None] * energy_differences ** 2 * entries * low_mask))
                                            high_m2 = float(np.sum(probabilities[:, None] * energy_differences ** 2 * entries * high_mask))
                                            removal_m0_actual = float(np.sum(probabilities[:, None] * reference_filter_difference ** 2 * entries))
                                            removal_m0_envelope = energy_window ** 2 * low_m0 + high_m2 / energy_window ** 2
                                            endpoint_removal_envelope = beta * (2.0 * low_m2 + high_m2 / energy_window)
                                            partition_error_m0 = abs(m0_left - low_m0 - high_m0)
                                            partition_error_m2 = abs(m2_left - low_m2 - high_m2)
                                            profile = cutoff_corridor_profiles[window_label]
                                            profile["contexts"] += 1
                                            profile["maximum_low_m0"] = max(profile["maximum_low_m0"], low_m0)
                                            profile["maximum_high_m0"] = max(profile["maximum_high_m0"], high_m0)
                                            profile["maximum_low_m2"] = max(profile["maximum_low_m2"], low_m2)
                                            profile["maximum_high_m2"] = max(profile["maximum_high_m2"], high_m2)
                                            profile["maximum_removal_m0"] = max(profile["maximum_removal_m0"], removal_m0_actual)
                                            profile["maximum_removal_m0_envelope"] = max(profile["maximum_removal_m0_envelope"], removal_m0_envelope)
                                            profile["maximum_endpoint_removal"] = max(profile["maximum_endpoint_removal"], endpoint_removal_actual)
                                            profile["maximum_endpoint_removal_envelope"] = max(profile["maximum_endpoint_removal_envelope"], endpoint_removal_envelope)
                                            profile["maximum_partition_error_m0"] = max(profile["maximum_partition_error_m0"], partition_error_m0)
                                            profile["maximum_partition_error_m2"] = max(profile["maximum_partition_error_m2"], partition_error_m2)
                                            scale_corridor = 1.0 + max(removal_m0_actual, removal_m0_envelope, endpoint_removal_actual, endpoint_removal_envelope)
                                            check("low/high M0 partition", partition_error_m0 <= tolerance * 800 * scale_corridor, partition_error_m0, "<= tolerance", "two-scale partition")
                                            check("low/high M2 partition", partition_error_m2 <= tolerance * 800 * scale_corridor, partition_error_m2, "<= tolerance", "two-scale partition")
                                            check("filter-removal M0 envelope", removal_m0_actual <= removal_m0_envelope + tolerance * 800 * scale_corridor, removal_m0_actual, "<= envelope", "filter-removal corridor")
                                            check("endpoint-removal envelope", endpoint_removal_actual <= endpoint_removal_envelope + tolerance * 800 * scale_corridor, endpoint_removal_actual, "<= envelope", "endpoint-removal corridor")
                                        cauchy_bound = beta * float(np.sqrt(max(0.0, m0_left * m2_left)))
                                        endpoint_reconstruction_error = abs(endpoint_one - endpoint_energy)
                                        endpoint_orientation_error = abs(endpoint_zero - endpoint_one)
                                        moment_orientation_error = max(abs(m0_left - m0_right), abs(m2_left - m2_right))
                                        cauchy_violation = endpoint_energy - cauchy_bound
                                        endpoint_to_bound = endpoint_energy / cauchy_bound if cauchy_bound > tolerance else 0.0
                                        max_log_energy_error = max(max_log_energy_error, log_energy_error)
                                        max_endpoint_orientation_error = max(max_endpoint_orientation_error, endpoint_orientation_error)
                                        max_moment_orientation_error = max(max_moment_orientation_error, moment_orientation_error)
                                        max_cauchy_violation = max(max_cauchy_violation, cauchy_violation)
                                        max_endpoint_reconstruction_error = max(max_endpoint_reconstruction_error, endpoint_reconstruction_error)
                                        max_endpoint = max(max_endpoint, endpoint_zero, endpoint_one)
                                        max_energy_first = max(max_energy_first, endpoint_energy)
                                        max_m0 = max(max_m0, m0_left, m0_right)
                                        max_m2 = max(max_m2, m2_left, m2_right)
                                        max_cauchy_bound = max(max_cauchy_bound, cauchy_bound)
                                        min_m0 = min(min_m0, m0_left, m0_right)
                                        min_m2 = min(min_m2, m2_left, m2_right)
                                        max_endpoint_to_bound_ratio = max(max_endpoint_to_bound_ratio, endpoint_to_bound)
                                        regime_max_endpoint = max(regime_max_endpoint, endpoint_energy)
                                        regime_max_first = max(regime_max_first, endpoint_energy)
                                        regime_max_m0 = max(regime_max_m0, m0_left, m0_right)
                                        regime_max_m2 = max(regime_max_m2, m2_left, m2_right)
                                        cutoff_max_endpoint = max(cutoff_max_endpoint, endpoint_energy)
                                        cutoff_max_m0 = max(cutoff_max_m0, m0_left, m0_right)
                                        cutoff_max_m2 = max(cutoff_max_m2, m2_left, m2_right)
                                        cutoff_max_cauchy = max(cutoff_max_cauchy, cauchy_bound)
                                        cutoff_max_ratio = max(cutoff_max_ratio, endpoint_to_bound)
                                        scale = 1.0 + max(endpoint_energy, cauchy_bound, m0_left, m2_left)
                                        check("finite endpoint-energy values", all(np.isfinite(value) for value in [endpoint_zero, endpoint_one, endpoint_energy, m0_left, m2_left, cauchy_bound]), "finite", "finite", "endpoint energy")
                                        check("Gibbs log-energy identity", log_energy_error <= tolerance * 800, log_energy_error, f"<={tolerance * 800}", "Gibbs log-energy")
                                        check("endpoint orientation", endpoint_orientation_error <= tolerance * 800 * scale, endpoint_orientation_error, "<= tolerance", "endpoint symmetry")
                                        check("moment orientation", moment_orientation_error <= tolerance * 800 * scale, moment_orientation_error, "<= tolerance", "moment symmetry")
                                        check("endpoint reconstruction", endpoint_reconstruction_error <= tolerance * 800 * scale, endpoint_reconstruction_error, "<= tolerance", "endpoint energy")
                                        check("quadratic Cauchy envelope", cauchy_violation <= tolerance * 800 * scale, cauchy_violation, "<=0", "state-weighted Cauchy")
                                        check("nonnegative moments", min(m0_left, m0_right, m2_left, m2_right) >= -tolerance * 800, min(m0_left, m0_right, m2_left, m2_right), ">=0", "positivity")
                                        context_count += 1
            cutoff_contexts = context_count - cutoff_context_start
            expected_cutoff_contexts = len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
            check("cutoff coverage", cutoff_contexts == expected_cutoff_contexts, cutoff_contexts, expected_cutoff_contexts, "per-cutoff profile")
            for filter_label, filter_power in filters:
                profile = cutoff_filter_profiles[filter_label]
                check("filtered cutoff coverage", profile["contexts"] == cutoff_contexts, profile["contexts"], cutoff_contexts, "filtered per-cutoff profile")
                filtered_profiles.append({"shape": regime["shape"], "volume": volume, "cutoff": size, "filter": filter_label, "power": filter_power, **profile, "expected_contexts": expected_cutoff_contexts})
            for window_label, energy_window in energy_windows:
                profile = cutoff_corridor_profiles[window_label]
                check("corridor cutoff coverage", profile["contexts"] == cutoff_contexts, profile["contexts"], cutoff_contexts, "corridor per-cutoff profile")
                corridor_profiles.append({"shape": regime["shape"], "volume": volume, "cutoff": size, "window": window_label, **profile, "expected_contexts": expected_cutoff_contexts})
            cutoff_profiles.append({"shape": regime["shape"], "volume": volume, "cutoff": size, "contexts": cutoff_contexts, "expected_contexts": expected_cutoff_contexts, "maximum_endpoint": cutoff_max_endpoint, "maximum_m0": cutoff_max_m0, "maximum_m2": cutoff_max_m2, "maximum_cauchy_bound": cutoff_max_cauchy, "maximum_endpoint_to_cauchy_ratio": cutoff_max_ratio})
        regime_profiles = cutoff_profiles[regime_profile_start:]
        regime_filter_profiles = filtered_profiles[regime_filter_start:]
        regime_corridor_profiles = corridor_profiles[regime_corridor_start:]
        successive_ratios = []
        for previous, current in zip(regime_profiles, regime_profiles[1:]):
            m0_ratio = current["maximum_m0"] / previous["maximum_m0"] if previous["maximum_m0"] > tolerance else None
            m2_ratio = current["maximum_m2"] / previous["maximum_m2"] if previous["maximum_m2"] > tolerance else None
            successive_ratios.append({"from_cutoff": previous["cutoff"], "to_cutoff": current["cutoff"], "m0_ratio": m0_ratio, "m2_ratio": m2_ratio})
        expected_regime = sum(item["expected_contexts"] for item in regime_profiles)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_endpoint": regime_max_endpoint, "maximum_endpoint_energy": regime_max_first, "maximum_m0": regime_max_m0, "maximum_m2": regime_max_m2, "cutoff_profiles": regime_profiles, "filtered_profiles": regime_filter_profiles, "corridor_profiles": regime_corridor_profiles, "successive_ratios": successive_ratios})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    all_ratios = [ratio for regime in per_regime for ratio in regime["successive_ratios"]]
    valid_m0_ratios = [float(ratio["m0_ratio"]) for ratio in all_ratios if ratio["m0_ratio"] is not None]
    valid_m2_ratios = [float(ratio["m2_ratio"]) for ratio in all_ratios if ratio["m2_ratio"] is not None]
    maximum_successive_m0_ratio = max(valid_m0_ratios, default=0.0)
    maximum_successive_m2_ratio = max(valid_m2_ratios, default=0.0)
    growth_warning_ratio = float(fixture["growth_warning_ratio"])
    cutoff_growth_warning = any(ratio > growth_warning_ratio for ratio in valid_m0_ratios + valid_m2_ratios)
    maximum_filtered_m0 = max((profile["maximum_m0"] for profile in filtered_profiles), default=0.0)
    maximum_filtered_m2 = max((profile["maximum_m2"] for profile in filtered_profiles), default=0.0)
    maximum_filtered_endpoint = max((profile["maximum_endpoint"] for profile in filtered_profiles), default=0.0)
    reference_profiles = [profile for profile in filtered_profiles if abs(float(profile["power"]) - reference_power) <= gap_tolerance]
    maximum_reference_filtered_m0 = max((profile["maximum_m0"] for profile in reference_profiles), default=0.0)
    maximum_reference_filtered_m2 = max((profile["maximum_m2"] for profile in reference_profiles), default=0.0)
    maximum_reference_filtered_endpoint = max((profile["maximum_endpoint"] for profile in reference_profiles), default=0.0)
    maximum_corridor_removal_m0 = max((profile["maximum_removal_m0"] for profile in corridor_profiles), default=0.0)
    maximum_corridor_removal_m0_envelope = max((profile["maximum_removal_m0_envelope"] for profile in corridor_profiles), default=0.0)
    maximum_corridor_endpoint_removal = max((profile["maximum_endpoint_removal"] for profile in corridor_profiles), default=0.0)
    maximum_corridor_endpoint_removal_envelope = max((profile["maximum_endpoint_removal_envelope"] for profile in corridor_profiles), default=0.0)
    check("filtered profile coverage", len(filtered_profiles) == len(filters) * len(cutoff_profiles), len(filtered_profiles), len(filters) * len(cutoff_profiles), "coverage")
    check("corridor profile coverage", len(corridor_profiles) == len(energy_windows) * len(cutoff_profiles), len(corridor_profiles), len(energy_windows) * len(cutoff_profiles), "coverage")
    check("manifest coverage", expected_contexts == int(fixture["expected_contexts"]), expected_contexts, int(fixture["expected_contexts"]), "coverage")
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("Gibbs log-energy aggregate", max_log_energy_error <= tolerance * 800, max_log_energy_error, "<= tolerance", "Gibbs log-energy")
    check("endpoint symmetry aggregate", max_endpoint_orientation_error <= tolerance * 800 * (1.0 + max_endpoint), max_endpoint_orientation_error, "<= tolerance", "endpoint symmetry")
    check("moment symmetry aggregate", max_moment_orientation_error <= tolerance * 800 * (1.0 + max_m2), max_moment_orientation_error, "<= tolerance", "moment symmetry")
    check("endpoint reconstruction aggregate", max_endpoint_reconstruction_error <= tolerance * 800 * (1.0 + max_endpoint), max_endpoint_reconstruction_error, "<= tolerance", "endpoint energy")
    check("Cauchy aggregate", max_cauchy_violation <= tolerance * 800 * (1.0 + max_cauchy_bound), max_cauchy_violation, "<=0", "state-weighted Cauchy")
    check("Kubo floor", min_kubo >= -gap_tolerance, min_kubo, f">={-gap_tolerance}", "Kubo--Mori state")
    check("moment positivity aggregate", min(min_m0, min_m2) >= -tolerance * 800, min(min_m0, min_m2), ">=0", "positivity")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-TWO-SCALE-FILTER-REMOVAL-CORRIDOR",
        "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {
            "context_count": context_count, "expected_contexts": expected_contexts, "theta": float(Fraction(fixture["theta"])), "regimes": per_regime, "cutoff_profiles": cutoff_profiles, "maximum_successive_m0_ratio": maximum_successive_m0_ratio, "maximum_successive_m2_ratio": maximum_successive_m2_ratio, "growth_warning_ratio": growth_warning_ratio, "cutoff_growth_warning": cutoff_growth_warning, "filter_powers": [{"label": label, "power": power} for label, power in filters], "reference_power": reference_power, "energy_windows": [{"label": label, "window": window} for label, window in energy_windows], "corridor_profiles": corridor_profiles, "maximum_corridor_removal_m0": maximum_corridor_removal_m0, "maximum_corridor_removal_m0_envelope": maximum_corridor_removal_m0_envelope, "maximum_corridor_endpoint_removal": maximum_corridor_endpoint_removal, "maximum_corridor_endpoint_removal_envelope": maximum_corridor_endpoint_removal_envelope, "filtered_profiles": filtered_profiles, "maximum_filtered_m0": maximum_filtered_m0, "maximum_filtered_m2": maximum_filtered_m2, "maximum_filtered_endpoint": maximum_filtered_endpoint, "maximum_reference_filtered_m0": maximum_reference_filtered_m0, "maximum_reference_filtered_m2": maximum_reference_filtered_m2, "maximum_reference_filtered_endpoint": maximum_reference_filtered_endpoint,
            "maximum_gibbs_log_energy_identity_error": max_log_energy_error, "maximum_endpoint_orientation_error": max_endpoint_orientation_error, "maximum_moment_orientation_error": max_moment_orientation_error,
            "maximum_cauchy_envelope_violation": max_cauchy_violation, "maximum_endpoint_reconstruction_error": max_endpoint_reconstruction_error, "maximum_endpoint_modular_moment": max_endpoint,
            "maximum_endpoint_energy_first_moment": max_energy_first, "maximum_state_weighted_m0": max_m0, "maximum_state_weighted_m2": max_m2, "maximum_cauchy_bound": max_cauchy_bound,
            "minimum_state_weighted_m0": min_m0, "minimum_state_weighted_m2": min_m2, "maximum_endpoint_to_cauchy_ratio": max_endpoint_to_bound_ratio,
            "maximum_bond_unitary_factorization_error": max_unitary_error, "maximum_kubo_weight_asymmetry": max_kubo_asymmetry, "minimum_kubo_weight": min_kubo,
            "gibbs_log_energy_identity_finite_checked": True, "endpoint_energy_moment_finite_checked": True, "quadratic_cauchy_envelope_finite_checked": True, "left_right_energy_moment_symmetry_finite_checked": True, "per_cutoff_moment_profile_finite_checked": True, "successive_cutoff_ratio_diagnostic_finite_checked": True, "filtered_endpoint_envelope_finite_checked": True, "filtered_m2_envelope_finite_checked": True, "filtered_profile_finite_checked": True, "low_high_split_finite_checked": True, "filter_removal_envelope_finite_checked": True, "endpoint_removal_envelope_finite_checked": True, "filter_removal_proved": False,
            "low_frequency_uniformity_proved": False, "high_frequency_tail_uniformity_proved": False, "source_uniformity_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False,
            "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False,
        }, "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); args = parser.parse_args()
    payload = run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY TWO-SCALE-FILTER-REMOVAL-CORRIDOR PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} ratio={payload['derived']['maximum_endpoint_to_cauchy_ratio']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
