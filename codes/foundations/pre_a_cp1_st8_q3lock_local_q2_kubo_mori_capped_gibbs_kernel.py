#!/usr/bin/env python3
"""Primary capped-Gibbs-kernel stress for EXP-001215 / R-373."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_capped_gibbs_kernel"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-capped-gibbs-kernel-manifest.json"
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
        if len(checks) < 128:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001215" and manifest["result_id"] == "R-373", [manifest["exploration_id"], manifest["result_id"]], "EXP-001215/R-373", "provenance")
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["capped_dirichlet_uniformity_proved"] is False, manifest["scope"], "finite-capped-kernel-only", "scope")
    context_count = 0
    max_identity_error = 0.0
    max_kernel_envelope_violation = -float("inf")
    max_kernel_row_error = 0.0
    max_capped_bound_violation = -float("inf")
    max_shell = 0.0
    max_capped_row = 0.0
    max_kappa = 0.0
    min_kappa = float("inf")
    max_capped_ratio = 0.0
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
        regime_max_capped = 0.0
        bond_rows: dict[str, dict[str, Any]] = {}
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
                        log_gap = np.log(probabilities)[:, None] - np.log(probabilities)[None, :]
                        arithmetic = 0.5 * (probabilities[:, None] + probabilities[None, :])
                        kubo = np.empty_like(log_gap)
                        close_gap = np.abs(log_gap) <= gap_tolerance
                        np.divide(probabilities[:, None] - probabilities[None, :], log_gap, out=kubo, where=~close_gap)
                        kubo[close_gap] = arithmetic[close_gap]
                        kubo = prior.hermitian(kubo)
                        max_weight_asymmetry = max(max_weight_asymmetry, float(np.max(np.abs(kubo - kubo.T))))
                        min_weight = min(min_weight, float(np.min(kubo)))
                        key = f"d={size}/bond={bond_term_index}"
                        row = bond_rows.setdefault(key, {"cutoff": size, "bond_term_index": bond_term_index, "maximum_shell": 0.0, "maximum_capped_row": 0.0, "maximum_capped_ratio": 0.0, "context_count": 0})
                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Gibbs normalization", np.isfinite(probabilities).all() and abs(float(np.sum(probabilities)) - 1.0) <= gap_tolerance, float(np.sum(probabilities)), 1.0, "Kubo--Mori state")
                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Kubo symmetry", float(np.max(np.abs(kubo - kubo.T))) <= gap_tolerance, float(np.max(np.abs(kubo - kubo.T))), f"<={gap_tolerance}", "Kubo--Mori state")
                        for order_name, order in orders.items():
                            for sign in signs:
                                for prefix_length, prefix in prior.all_prefixes(terms, order, sign, delta_t, hbar):
                                    for history_adjoint in adjoints:
                                        evolution = prefix if not history_adjoint else prefix.conj().T
                                        doubled = np.kron(evolution, evolution)
                                        moved = prior.hermitian(doubled.conj().T @ local_witness @ doubled)
                                        transformed = eigenvectors.conj().T @ moved @ eigenvectors
                                        deltas = np.abs(eigenvalues[:, None] - eigenvalues[None, :])
                                        probabilities_difference = np.abs(probabilities[:, None] - probabilities[None, :])
                                        kappa = (2.0 / beta) * np.tanh(beta * deltas / 2.0)
                                        cap = np.minimum(deltas, 2.0 / beta)
                                        bond_mean = float(np.sum(probabilities * np.real(np.diag(transformed))))
                                        centered = transformed - bond_mean * np.eye(transformed.shape[0], dtype=complex)
                                        shell = float((2.0 / beta) * np.sum(probabilities_difference * np.abs(centered) ** 2))
                                        kernel_shell = float(np.sum((probabilities[:, None] + probabilities[None, :]) * kappa * np.abs(centered) ** 2))
                                        row_shell = float(2.0 * np.sum(probabilities[:, None] * kappa * np.abs(centered) ** 2))
                                        capped_row = float(2.0 * np.sum(probabilities[:, None] * cap * np.abs(centered) ** 2))
                                        identity_error = float(np.max(np.abs((2.0 / beta) * probabilities_difference - (probabilities[:, None] + probabilities[None, :]) * kappa)))
                                        envelope_violation = float(np.max(kappa - cap))
                                        row_error = abs(kernel_shell - row_shell)
                                        capped_violation = shell - capped_row
                                        centering_error = abs(row_shell - shell)
                                        max_identity_error = max(max_identity_error, identity_error)
                                        max_kernel_envelope_violation = max(max_kernel_envelope_violation, envelope_violation)
                                        max_kernel_row_error = max(max_kernel_row_error, row_error)
                                        max_capped_bound_violation = max(max_capped_bound_violation, capped_violation)
                                        max_shell = max(max_shell, shell)
                                        max_capped_row = max(max_capped_row, capped_row)
                                        max_kappa = max(max_kappa, float(np.max(kappa)))
                                        min_kappa = min(min_kappa, float(np.min(kappa)))
                                        max_capped_ratio = max(max_capped_ratio, shell / capped_row if capped_row > tolerance ** 2 else 0.0)
                                        max_transition = max(max_transition, float(np.max(deltas)))
                                        max_centering_error = max(max_centering_error, centering_error)
                                        regime_max_shell = max(regime_max_shell, shell)
                                        regime_max_capped = max(regime_max_capped, capped_row)
                                        row["maximum_shell"] = max(row["maximum_shell"], shell)
                                        row["maximum_capped_row"] = max(row["maximum_capped_row"], capped_row)
                                        row["maximum_capped_ratio"] = max(row["maximum_capped_ratio"], shell / capped_row if capped_row > tolerance ** 2 else 0.0)
                                        row["context_count"] += 1
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} Gibbs kernel identity", identity_error <= tolerance * 800, identity_error, f"<={tolerance * 800}", "capped Gibbs kernel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} kernel envelope", envelope_violation <= tolerance * 800, envelope_violation, f"<={tolerance * 800}", "capped Gibbs kernel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} row symmetry", row_error <= tolerance * 800 * (1.0 + shell), row_error, f"<={tolerance * 800 * (1.0 + shell)}", "capped Gibbs kernel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} capped bound", capped_violation <= tolerance * 800 * (1.0 + capped_row), [shell, capped_row], "<= bound", "capped Gibbs kernel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} shell nonnegative", shell >= -tolerance * 800, shell, f">={-tolerance * 800}", "capped Gibbs kernel")
                                        check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} kappa nonnegative", float(np.min(kappa)) >= -tolerance * 800, float(np.min(kappa)), f">={-tolerance * 800}", "capped Gibbs kernel")
                                        context_count += 1
        expected_regime = len(cutoffs) * len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "sites": sites, "bond_term_indices": bond_indices, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_shell": regime_max_shell, "maximum_capped_row": regime_max_capped, "bond_rows": list(bond_rows.values())})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("Gibbs kernel identity", max_identity_error <= tolerance * 800, max_identity_error, f"<={tolerance * 800}", "capped Gibbs kernel")
    check("capped kernel envelope", max_kernel_envelope_violation <= tolerance * 800, max_kernel_envelope_violation, f"<={tolerance * 800}", "capped Gibbs kernel")
    check("capped row symmetry", max_kernel_row_error <= tolerance * 800 * (1.0 + max_shell), max_kernel_row_error, f"<={tolerance * 800 * (1.0 + max_shell)}", "capped Gibbs kernel")
    check("capped local bound", max_capped_bound_violation <= tolerance * 800 * (1.0 + max_capped_row), max_capped_bound_violation, f"<={tolerance * 800 * (1.0 + max_capped_row)}", "capped Gibbs kernel")
    check("Kubo weight floor", min_weight >= -gap_tolerance, min_weight, f">={-gap_tolerance}", "Kubo--Mori state")
    check("kernel floor", min_kappa >= -tolerance * 800, min_kappa, f">={-tolerance * 800}", "capped Gibbs kernel")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-CAPPED-GIBBS-KERNEL", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {"context_count": context_count, "expected_contexts": expected_contexts, "theta": float(Fraction(fixture["theta"])), "regimes": per_regime, "maximum_gibbs_hyperbolic_kernel_identity_error": max_identity_error, "maximum_capped_kernel_envelope_violation": max_kernel_envelope_violation, "maximum_capped_row_symmetry_error": max_kernel_row_error, "maximum_capped_local_dirichlet_bound_violation": max_capped_bound_violation, "maximum_capped_shell": max_shell, "maximum_capped_row_form": max_capped_row, "maximum_kappa": max_kappa, "minimum_kappa": min_kappa, "maximum_shell_to_capped_row_ratio": max_capped_ratio, "maximum_transition_energy": max_transition, "maximum_bond_gibbs_centering_shell_error": max_centering_error, "maximum_kubo_weight_asymmetry": max_weight_asymmetry, "minimum_kubo_weight": min_weight, "maximum_bond_unitary_factorization_error": max_unitary_error, "gibbs_hyperbolic_kernel_identity_finite_checked": True, "capped_kernel_envelope_finite_checked": True, "capped_local_dirichlet_bound_finite_checked": True, "local_variance_uniformity_proved": False, "capped_dirichlet_uniformity_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False, "local_modular_dirichlet_comparison_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY CAPPED-GIBBS-KERNEL PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} shell={payload['derived']['maximum_capped_shell']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
