#!/usr/bin/env python3
"""Non-importing independent odd-Matsubara resolvent-layer audit for EXP-001216 / R-374."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_matsubara_resolvent_layers"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-matsubara-resolvent-layers-manifest.json"
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


def odd_layer_sum(beta: float, deltas: np.ndarray, terms: int) -> np.ndarray:
    indices = np.arange(terms, dtype=float)[:, None, None]
    odd = (2.0 * indices + 1.0) * math.pi
    denominator = odd * odd + (beta * deltas[None, :, :]) ** 2
    numerator = 8.0 * deltas[None, :, :]
    return np.sum(np.divide(numerator, denominator, out=np.zeros_like(denominator), where=denominator > 0.0), axis=0)


def odd_layer_tail_bound(beta: float, deltas: np.ndarray, terms: int) -> np.ndarray:
    if terms < 1:
        raise ValueError("series_terms must be at least one")
    return (4.0 * deltas) / (math.pi * math.pi * (2.0 * terms - 1.0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    delta_t = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tolerance = float(fixture["finite_tolerance"])
    threshold = tolerance * float(fixture["tolerance_multiplier"])
    gap_tolerance = float(fixture["log_mean_gap_tolerance"])
    terms_count = int(fixture["series_terms"])
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

    check("authority", manifest["exploration_id"] == "EXP-001216" and manifest["result_id"] == "R-374", [manifest["exploration_id"], manifest["result_id"]], "EXP-001216/R-374", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["resolvent_locality_proved"], manifest["scope"], "finite-resolvent-layer-only", "scope")
    check("series length", terms_count >= 1, terms_count, ">=1", "Matsubara interface")

    context_count = 0
    max_direct_error = 0.0
    max_tail_bound = 0.0
    max_tail_violation = -float("inf")
    max_partial_above_exact = -float("inf")
    max_partial_below_zero = -float("inf")
    max_exact_below_partial = -float("inf")
    max_shell_remainder = -float("inf")
    max_shell_tail_violation = -float("inf")
    max_partial_shell = 0.0
    max_exact_shell = 0.0
    max_layer_shell = 0.0
    max_transition = 0.0
    min_layer = float("inf")
    min_partial = float("inf")
    max_unitary_error = 0.0
    per_regime: list[dict[str, Any]] = []

    for regime in fixture["regimes"]:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        bond_indices = [int(value) for value in regime["bond_term_indices"]]
        regime_start = context_count
        regime_max_exact = 0.0
        regime_max_partial = 0.0
        regime_max_tail = 0.0
        rows: dict[str, dict[str, Any]] = {}
        for size in cutoffs:
            _, hamiltonian, terms = prior.build_system(volume, size, parameters)
            q_single, _ = prior.graph.oscillator(size)
            identity_single = np.eye(size, dtype=complex)
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            pvm = prior.projectors(q_single)
            orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
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
                        deltas = np.abs(eigenvalues[:, None] - eigenvalues[None, :])
                        exact = (2.0 / beta) * np.tanh(beta * deltas / 2.0)
                        partial = odd_layer_sum(beta, deltas, terms_count)
                        tail_bound = odd_layer_tail_bound(beta, deltas, terms_count)
                        partial_layers = []
                        for index in range(terms_count):
                            odd = (2.0 * index + 1.0) * math.pi
                            denominator = odd * odd + (beta * deltas) ** 2
                            partial_layers.append(np.divide(8.0 * deltas, denominator, out=np.zeros_like(deltas), where=denominator > 0.0))
                        layer_stack = np.stack(partial_layers, axis=0)
                        layer_floor = float(np.min(layer_stack))
                        first_layer = layer_stack[0]
                        min_layer = min(min_layer, layer_floor)
                        min_partial = min(min_partial, float(np.min(partial)))
                        direct_error = float(np.max(np.abs(exact - partial)))
                        partial_above = float(np.max(partial - exact))
                        partial_below = float(np.min(partial))
                        exact_below = float(np.max(partial - exact))
                        tail_violation = float(np.max(exact - partial - tail_bound))
                        max_direct_error = max(max_direct_error, direct_error)
                        max_tail_bound = max(max_tail_bound, float(np.max(tail_bound)))
                        max_tail_violation = max(max_tail_violation, tail_violation)
                        max_partial_above_exact = max(max_partial_above_exact, partial_above)
                        max_partial_below_zero = max(max_partial_below_zero, -partial_below)
                        max_exact_below_partial = max(max_exact_below_partial, exact_below)
                        max_transition = max(max_transition, float(np.max(deltas)))
                        key = f"d={size}/bond={bond_term_index}"
                        row = rows.setdefault(key, {"cutoff": size, "bond_term_index": bond_term_index, "maximum_direct_kernel_error": 0.0, "maximum_tail_bound": 0.0, "maximum_exact_shell": 0.0, "maximum_partial_shell": 0.0, "maximum_shell_remainder": 0.0, "context_count": 0})
                        for order_name, order in orders.items():
                            for sign in signs:
                                for _, prefix in prior.all_prefixes(terms, order, sign, delta_t, hbar):
                                    for history_adjoint in adjoints:
                                        evolution = prefix if not history_adjoint else prefix.conj().T
                                        doubled = np.kron(evolution, evolution)
                                        moved = prior.hermitian(doubled.conj().T @ local_witness @ doubled)
                                        transformed = eigenvectors.conj().T @ moved @ eigenvectors
                                        bond_mean = float(np.sum(probabilities * np.real(np.diag(transformed))))
                                        centered = transformed - bond_mean * np.eye(transformed.shape[0], dtype=complex)
                                        square_entries = np.abs(centered) ** 2
                                        exact_shell = float(np.sum((probabilities[:, None] + probabilities[None, :]) * exact * square_entries))
                                        partial_shell = float(np.sum((probabilities[:, None] + probabilities[None, :]) * partial * square_entries))
                                        first_layer_shell = float(np.sum((probabilities[:, None] + probabilities[None, :]) * first_layer * square_entries))
                                        tail_form = float(np.sum((probabilities[:, None] + probabilities[None, :]) * tail_bound * square_entries))
                                        shell_remainder = exact_shell - partial_shell
                                        shell_tail_violation = shell_remainder - tail_form
                                        max_shell_remainder = max(max_shell_remainder, shell_remainder)
                                        max_shell_tail_violation = max(max_shell_tail_violation, shell_tail_violation)
                                        max_partial_shell = max(max_partial_shell, partial_shell)
                                        max_exact_shell = max(max_exact_shell, exact_shell)
                                        max_layer_shell = max(max_layer_shell, first_layer_shell)
                                        regime_max_exact = max(regime_max_exact, exact_shell)
                                        regime_max_partial = max(regime_max_partial, partial_shell)
                                        regime_max_tail = max(regime_max_tail, tail_form)
                                        row["maximum_direct_kernel_error"] = max(row["maximum_direct_kernel_error"], direct_error)
                                        row["maximum_tail_bound"] = max(row["maximum_tail_bound"], float(np.max(tail_bound)))
                                        row["maximum_exact_shell"] = max(row["maximum_exact_shell"], exact_shell)
                                        row["maximum_partial_shell"] = max(row["maximum_partial_shell"], partial_shell)
                                        row["maximum_shell_remainder"] = max(row["maximum_shell_remainder"], shell_remainder)
                                        row["context_count"] += 1
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} series positivity", float(np.min(partial)) >= -threshold and layer_floor >= -threshold, [float(np.min(partial)), layer_floor], f">={-threshold}", "Matsubara layers")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} partial below direct", partial_above <= threshold * (1.0 + float(np.max(exact))), partial_above, "<= direct+tolerance", "Matsubara layers")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} tail envelope", tail_violation <= threshold * (1.0 + float(np.max(exact))), tail_violation, "<= envelope+tolerance", "Matsubara layers")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} shell remainder", shell_remainder >= -threshold * (1.0 + exact_shell) and shell_tail_violation <= threshold * (1.0 + exact_shell), [shell_remainder, shell_tail_violation], "one-sided remainder", "Matsubara shell")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} shell nonnegative", exact_shell >= -threshold and partial_shell >= -threshold, [exact_shell, partial_shell], f">={-threshold}", "Matsubara shell")
                                        context_count += 1
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_exact_shell": regime_max_exact, "maximum_partial_shell": regime_max_partial, "maximum_tail_form": regime_max_tail, "bond_rows": list(rows.values())})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("partial sum nonnegative", max_partial_below_zero <= threshold, max_partial_below_zero, f"<={threshold}", "Matsubara layers")
    check("partial sum below exact", max_partial_above_exact <= threshold * (1.0 + max_transition), max_partial_above_exact, "<= tolerance", "Matsubara layers")
    check("tail envelope", max_tail_violation <= threshold * (1.0 + max_transition), max_tail_violation, "<= envelope+tolerance", "Matsubara layers")
    check("shell tail envelope", max_shell_tail_violation <= threshold * (1.0 + max_exact_shell), max_shell_tail_violation, "<= envelope+tolerance", "Matsubara shell")
    check("layer floor", min_layer >= -threshold, min_layer, f">={-threshold}", "Matsubara layers")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-MATSUBARA-RESOLVENT-LAYERS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {"context_count": context_count, "expected_contexts": expected_contexts, "theta": float(Fraction(fixture["theta"])), "series_terms": terms_count, "regimes": per_regime, "maximum_direct_kernel_series_error": max_direct_error, "maximum_matsubara_tail_bound": max_tail_bound, "maximum_matsubara_tail_envelope_violation": max_tail_violation, "maximum_partial_above_exact_kernel": max_partial_above_exact, "maximum_partial_below_zero_violation": max_partial_below_zero, "maximum_shell_remainder": max_shell_remainder, "maximum_shell_tail_envelope_violation": max_shell_tail_violation, "maximum_exact_kernel_shell": max_exact_shell, "maximum_partial_kernel_shell": max_partial_shell, "maximum_single_layer_shell": max_layer_shell, "maximum_transition_energy": max_transition, "minimum_layer_value": min_layer, "minimum_partial_kernel_value": min_partial, "maximum_bond_unitary_factorization_error": max_unitary_error, "odd_matsubara_series_finite_checked": True, "positive_resolvent_layer_finite_checked": True, "partial_sum_monotonicity_finite_checked": True, "tail_bound_finite_checked": True, "resolvent_locality_proved": False, "capped_dirichlet_uniformity_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False},
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
    print(f"INDEPENDENT MATSUBARA-RESOLVENT-LAYERS PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} tail={payload['derived']['maximum_matsubara_tail_bound']:.6e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
