#!/usr/bin/env python3
"""Primary finite Renyi interpolation audit for EXP-001222 / R-380."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_renyi_interpolation_bridge"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-renyi-interpolation-bridge-manifest.json"
SOURCE_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-28-integrated-pre_a_cp1_st8_q3lock_local_q2_kubo_mori_three_channel_bridge/integrated.json"
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


def interpolation(probabilities: np.ndarray, modular_gap: np.ndarray, entries: np.ndarray, s: float) -> float:
    log_probabilities = np.log(probabilities)
    weights = np.exp(s * log_probabilities[:, None] + (1.0 - s) * log_probabilities[None, :])
    return float(np.sum(weights * modular_gap * entries))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    sample_points = [float(Fraction(value)) for value in fixture["sample_points"]]
    delta_t = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tolerance = float(fixture["finite_tolerance"])
    gap_tolerance = float(fixture["log_mean_gap_tolerance"])
    quadrature_tolerance = float(fixture["quadrature_tolerance"])
    quadrature_nodes = int(fixture["quadrature_nodes"])
    parameters = fixture["parameters"]
    quadrature_x, quadrature_w = np.polynomial.legendre.leggauss(quadrature_nodes)
    quadrature_s = (quadrature_x + 1.0) / 2.0
    quadrature_weights = quadrature_w / 2.0
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 180:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001222" and manifest["result_id"] == "R-380", [manifest["exploration_id"], manifest["result_id"]], "EXP-001222/R-380", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "finite-renyi-interpolation-only", "scope")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("R-379 source", source.get("verdict") == "PASS" and source.get("derived", {}).get("primary", {}).get("context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("primary", {}).get("context_count")], "R-379 PASS and expected contexts", "source linkage")

    context_count = 0
    max_endpoint_symmetry = 0.0
    max_sample_symmetry = 0.0
    max_chord_violation = -float("inf")
    max_midpoint_lower_violation = -float("inf")
    max_integral_upper_violation = -float("inf")
    max_integral_identity_error = 0.0
    max_quadrature_error = 0.0
    max_kubo_identity_error = 0.0
    max_shell = 0.0
    max_endpoint = 0.0
    max_midpoint = 0.0
    max_integral = 0.0
    min_endpoint = float("inf")
    min_midpoint = float("inf")
    min_integral = float("inf")
    max_midpoint_to_integral_ratio = 0.0
    max_integral_to_endpoint_ratio = 0.0
    max_centering_error = 0.0
    max_unitary_error = 0.0
    min_kubo = float("inf")
    max_kubo_asymmetry = 0.0
    per_regime: list[dict[str, Any]] = []

    for regime in fixture["regimes"]:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        bond_indices = [int(value) for value in regime["bond_term_indices"]]
        regime_start = context_count
        regime_max_endpoint = 0.0
        regime_max_midpoint = 0.0
        regime_max_integral = 0.0
        regime_max_shell = 0.0
        for size in cutoffs:
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
                        log_probabilities = np.log(probabilities)
                        modular_gap = np.abs(log_probabilities[:, None] - log_probabilities[None, :])
                        entries_by_context = []
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
                                        endpoint_zero = interpolation(probabilities, modular_gap, entries, 0.0)
                                        endpoint_one = interpolation(probabilities, modular_gap, entries, 1.0)
                                        midpoint = interpolation(probabilities, modular_gap, entries, 0.5)
                                        samples = [interpolation(probabilities, modular_gap, entries, point) for point in sample_points]
                                        integral_direct = float(np.sum(np.abs(probabilities[:, None] - probabilities[None, :]) * entries))
                                        quadrature = float(sum(weight * interpolation(probabilities, modular_gap, entries, point) for point, weight in zip(quadrature_s, quadrature_weights)))
                                        log_gap = log_probabilities[:, None] - log_probabilities[None, :]
                                        kubo = np.empty_like(log_gap)
                                        close_gap = np.abs(log_gap) <= gap_tolerance
                                        arithmetic = 0.5 * (probabilities[:, None] + probabilities[None, :])
                                        np.divide(probabilities[:, None] - probabilities[None, :], log_gap, out=kubo, where=~close_gap)
                                        kubo[close_gap] = arithmetic[close_gap]
                                        kubo = prior.hermitian(kubo)
                                        kubo_identity_error = float(np.max(np.abs(kubo * modular_gap - np.abs(probabilities[:, None] - probabilities[None, :]))))
                                        integral_identity_error = abs(integral_direct - float(np.sum(kubo * modular_gap * entries)))
                                        shell = (2.0 / beta) * integral_direct
                                        endpoint_symmetry = abs(endpoint_zero - endpoint_one)
                                        sample_symmetry = abs(samples[1] - samples[3])
                                        chord_violation = max(samples[index] - ((1.0 - point) * endpoint_zero + point * endpoint_one) for index, point in enumerate(sample_points))
                                        midpoint_lower_violation = midpoint - integral_direct
                                        integral_upper_violation = integral_direct - 0.5 * (endpoint_zero + endpoint_one)
                                        quadrature_error = abs(quadrature - integral_direct)
                                        max_endpoint_symmetry = max(max_endpoint_symmetry, endpoint_symmetry)
                                        max_sample_symmetry = max(max_sample_symmetry, sample_symmetry)
                                        max_chord_violation = max(max_chord_violation, chord_violation)
                                        max_midpoint_lower_violation = max(max_midpoint_lower_violation, midpoint_lower_violation)
                                        max_integral_upper_violation = max(max_integral_upper_violation, integral_upper_violation)
                                        max_integral_identity_error = max(max_integral_identity_error, integral_identity_error)
                                        max_quadrature_error = max(max_quadrature_error, quadrature_error)
                                        max_kubo_identity_error = max(max_kubo_identity_error, kubo_identity_error)
                                        max_shell = max(max_shell, shell)
                                        max_endpoint = max(max_endpoint, endpoint_zero, endpoint_one)
                                        max_midpoint = max(max_midpoint, midpoint)
                                        max_integral = max(max_integral, integral_direct)
                                        min_endpoint = min(min_endpoint, endpoint_zero, endpoint_one)
                                        min_midpoint = min(min_midpoint, midpoint)
                                        min_integral = min(min_integral, integral_direct)
                                        max_midpoint_to_integral_ratio = max(max_midpoint_to_integral_ratio, midpoint / integral_direct if integral_direct > tolerance else 0.0)
                                        max_integral_to_endpoint_ratio = max(max_integral_to_endpoint_ratio, integral_direct / endpoint_zero if endpoint_zero > tolerance else 0.0)
                                        centering_error = abs(float(np.sum(probabilities * np.real(np.diag(centered)))))
                                        max_centering_error = max(max_centering_error, centering_error)
                                        regime_max_endpoint = max(regime_max_endpoint, endpoint_zero, endpoint_one)
                                        regime_max_midpoint = max(regime_max_midpoint, midpoint)
                                        regime_max_integral = max(regime_max_integral, integral_direct)
                                        regime_max_shell = max(regime_max_shell, shell)
                                        min_kubo = min(min_kubo, float(np.min(kubo)))
                                        max_kubo_asymmetry = max(max_kubo_asymmetry, float(np.max(np.abs(kubo - kubo.T))))
                                        scale = 1.0 + max(endpoint_zero, endpoint_one, integral_direct)
                                        check("finite interpolation values", all(np.isfinite(value) for value in [*samples, endpoint_zero, endpoint_one, midpoint, integral_direct, quadrature]), "finite", "finite", "Renyi interpolation")
                                        check("endpoint symmetry", endpoint_symmetry <= tolerance * 800 * scale, endpoint_symmetry, f"<={tolerance * 800 * scale}", "Renyi symmetry")
                                        check("sample symmetry", sample_symmetry <= tolerance * 800 * scale, sample_symmetry, f"<={tolerance * 800 * scale}", "Renyi symmetry")
                                        check("pointwise convex chord", chord_violation <= tolerance * 800 * scale, chord_violation, "<=0", "convexity envelope")
                                        check("midpoint lower envelope", midpoint_lower_violation <= tolerance * 800 * scale, midpoint_lower_violation, "<=0", "convexity envelope")
                                        check("integral upper envelope", integral_upper_violation <= tolerance * 800 * scale, integral_upper_violation, "<=0", "convexity envelope")
                                        check("shell integral identity", integral_identity_error <= tolerance * 800 * scale, integral_identity_error, "<= tolerance", "Kubo--Mori shell")
                                        check("quadrature reconstruction", quadrature_error <= quadrature_tolerance * scale, quadrature_error, f"<={quadrature_tolerance * scale}", "quadrature")
                                        check("Kubo modular identity", kubo_identity_error <= tolerance * 800, kubo_identity_error, f"<={tolerance * 800}", "Kubo--Mori shell")
                                        check("nonnegative endpoint", min(endpoint_zero, endpoint_one) >= -tolerance * 800, min(endpoint_zero, endpoint_one), ">=0", "positivity")
                                        check("nonnegative midpoint", midpoint >= -tolerance * 800, midpoint, ">=0", "positivity")
                                        check("nonnegative integral", integral_direct >= -tolerance * 800, integral_direct, ">=0", "positivity")
                                        context_count += 1
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_endpoint": regime_max_endpoint, "maximum_midpoint": regime_max_midpoint, "maximum_integral": regime_max_integral, "maximum_shell": regime_max_shell})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("endpoint symmetry aggregate", max_endpoint_symmetry <= tolerance * 800 * (1.0 + max_endpoint), max_endpoint_symmetry, "<= tolerance", "Renyi symmetry")
    check("sample symmetry aggregate", max_sample_symmetry <= tolerance * 800 * (1.0 + max_endpoint), max_sample_symmetry, "<= tolerance", "Renyi symmetry")
    check("pointwise convex chord aggregate", max_chord_violation <= tolerance * 800 * (1.0 + max_endpoint), max_chord_violation, "<=0", "convexity envelope")
    check("midpoint lower aggregate", max_midpoint_lower_violation <= tolerance * 800 * (1.0 + max_integral), max_midpoint_lower_violation, "<=0", "convexity envelope")
    check("integral upper aggregate", max_integral_upper_violation <= tolerance * 800 * (1.0 + max_endpoint), max_integral_upper_violation, "<=0", "convexity envelope")
    check("integral identity aggregate", max_integral_identity_error <= tolerance * 800 * (1.0 + max_integral), max_integral_identity_error, "<= tolerance", "Kubo--Mori shell")
    check("Kubo identity aggregate", max_kubo_identity_error <= tolerance * 800, max_kubo_identity_error, "<= tolerance", "Kubo--Mori shell")
    check("Kubo floor", min_kubo >= -gap_tolerance, min_kubo, f">={-gap_tolerance}", "Kubo--Mori state")
    check("positivity aggregate", min(min_endpoint, min_midpoint, min_integral) >= -tolerance * 800, min(min_endpoint, min_midpoint, min_integral), ">=0", "positivity")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-RENYI-INTERPOLATION-BRIDGE",
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
            "sample_points": sample_points,
            "quadrature_nodes": quadrature_nodes,
            "regimes": per_regime,
            "maximum_endpoint_symmetry_error": max_endpoint_symmetry,
            "maximum_sample_symmetry_error": max_sample_symmetry,
            "maximum_convex_chord_violation": max_chord_violation,
            "maximum_midpoint_lower_envelope_violation": max_midpoint_lower_violation,
            "maximum_integral_upper_envelope_violation": max_integral_upper_violation,
            "maximum_shell_integral_identity_error": max_integral_identity_error,
            "maximum_quadrature_reconstruction_error": max_quadrature_error,
            "maximum_kubo_modular_identity_error": max_kubo_identity_error,
            "maximum_shell": max_shell,
            "maximum_endpoint_modular_moment": max_endpoint,
            "maximum_midpoint_modular_moment": max_midpoint,
            "maximum_integrated_modular_shell": max_integral,
            "minimum_endpoint_modular_moment": min_endpoint,
            "minimum_midpoint_modular_moment": min_midpoint,
            "minimum_integrated_modular_shell": min_integral,
            "maximum_midpoint_to_integral_ratio": max_midpoint_to_integral_ratio,
            "maximum_integral_to_endpoint_ratio": max_integral_to_endpoint_ratio,
            "maximum_bond_gibbs_centering_error": max_centering_error,
            "maximum_bond_unitary_factorization_error": max_unitary_error,
            "maximum_kubo_weight_asymmetry": max_kubo_asymmetry,
            "minimum_kubo_weight": min_kubo,
            "renyi_interpolation_finite_checked": True,
            "midpoint_shell_lower_bound_finite_checked": True,
            "endpoint_shell_upper_bound_finite_checked": True,
            "shell_integral_identity_finite_checked": True,
            "source_uniformity_proved": False,
            "weighted_cutoff_uniformity_proved": False,
            "weighted_volume_uniformity_proved": False,
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
    print(f"PRIMARY RENYI-INTERPOLATION-BRIDGE PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} midpoint_ratio={payload['derived']['maximum_midpoint_to_integral_ratio']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
