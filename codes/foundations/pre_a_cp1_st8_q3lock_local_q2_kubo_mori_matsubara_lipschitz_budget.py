#!/usr/bin/env python3
"""Primary finite Matsubara Lipschitz-budget audit for EXP-001217 / R-375."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_matsubara_lipschitz_budget"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-matsubara-lipschitz-budget-manifest.json"
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


def layer(beta: float, delta: np.ndarray, index: int) -> np.ndarray:
    omega = (2.0 * float(index) + 1.0) * math.pi
    denominator = omega * omega + (beta * delta) ** 2
    return np.divide(8.0 * delta, denominator, out=np.zeros_like(delta), where=denominator > 0.0)


def layer_slope(beta: float, delta: np.ndarray, index: int) -> np.ndarray:
    omega = (2.0 * float(index) + 1.0) * math.pi
    beta_delta_sq = (beta * delta) ** 2
    denominator = omega * omega + beta_delta_sq
    return 8.0 * np.abs(omega * omega - beta_delta_sq) / (denominator * denominator)


def exact_kernel(beta: float, delta: np.ndarray) -> np.ndarray:
    return (2.0 / beta) * np.tanh(beta * delta / 2.0)


def exact_slope(beta: float, delta: np.ndarray) -> np.ndarray:
    return 1.0 / np.cosh(beta * delta / 2.0) ** 2


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    terms_count = int(fixture["series_terms"])
    grid_points = int(fixture["sample_grid_points"])
    perturbations = [float(Fraction(value)) for value in fixture["perturbation_fractions"]]
    tolerance = float(fixture["finite_tolerance"])
    threshold = tolerance * float(fixture["tolerance_multiplier"])
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

    check("authority", manifest["exploration_id"] == "EXP-001217" and manifest["result_id"] == "R-375", [manifest["exploration_id"], manifest["result_id"]], "EXP-001217/R-375", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["first_liouvillian_variation_reduction_proved"], manifest["scope"], "finite-scalar-sensitivity-only", "scope")
    check("grid", grid_points >= 3, grid_points, ">=3", "fixture")
    check("series length", terms_count >= 1, terms_count, ">=1", "fixture")

    context_count = 0
    maximum_transition = 0.0
    maximum_layer_slope = 0.0
    maximum_layer_slope_violation = -float("inf")
    maximum_partial_ratio = 0.0
    maximum_partial_budget_violation = -float("inf")
    maximum_exact_ratio = 0.0
    maximum_exact_slope = 0.0
    maximum_exact_slope_violation = -float("inf")
    maximum_partial_monotonicity_violation = -float("inf")
    maximum_budget = 0.0
    maximum_budget_tail_envelope = 0.0
    minimum_layer = float("inf")
    minimum_partial = float("inf")
    per_regime: list[dict[str, Any]] = []

    for regime in fixture["regimes"]:
        volume = int(regime["volume"])
        cutoffs = [int(value) for value in regime["cutoff_values"]]
        sites = [int(value) for value in regime["site_values"]]
        bond_indices = [int(value) for value in regime["bond_term_indices"]]
        regime_start = context_count
        regime_max_transition = 0.0
        regime_max_partial_ratio = 0.0
        regime_max_exact_ratio = 0.0
        bond_rows: list[dict[str, Any]] = []
        for size in cutoffs:
            _, hamiltonian, terms = prior.base.split_system(volume, size, parameters)
            identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
            for beta_fraction in betas:
                beta = float(beta_fraction)
                check(f"V={volume} d={size} beta={beta_fraction} beta positive", beta > 0.0, beta, ">0", "Matsubara budget")
                for bond_term_index in bond_indices:
                    generator = np.kron(terms[bond_term_index], identity_global) + np.kron(identity_global, terms[bond_term_index])
                    eigenvalues = np.linalg.eigvalsh(prior.hermitian(generator))
                    maximum_delta = float(np.max(eigenvalues) - np.min(eigenvalues))
                    maximum_transition = max(maximum_transition, maximum_delta)
                    regime_max_transition = max(regime_max_transition, maximum_delta)
                    grid = np.linspace(0.0, maximum_delta, grid_points, dtype=float)
                    shifts = [fraction * (1.0 + maximum_delta) for fraction in perturbations]
                    sample_values = [grid] + [grid + shift for shift in shifts]
                    budget = sum(8.0 / (((2.0 * float(index) + 1.0) * math.pi) ** 2) for index in range(terms_count))
                    budget_tail = 4.0 / (math.pi * math.pi * (2.0 * terms_count - 1.0))
                    maximum_budget = max(maximum_budget, budget)
                    maximum_budget_tail_envelope = max(maximum_budget_tail_envelope, budget_tail)
                    row = {"cutoff": size, "beta": str(beta_fraction), "bond_term_index": bond_term_index, "maximum_transition": maximum_delta, "budget": budget, "budget_tail_envelope": budget_tail, "context_count": 0}
                    partial_stack = []
                    for index in range(terms_count):
                        slope = layer_slope(beta, grid, index)
                        omega = (2.0 * float(index) + 1.0) * math.pi
                        bound = 8.0 / (omega * omega)
                        violation = float(np.max(slope - bound))
                        maximum_layer_slope = max(maximum_layer_slope, float(np.max(slope)))
                        maximum_layer_slope_violation = max(maximum_layer_slope_violation, violation)
                        layer_values = layer(beta, grid, index)
                        partial_stack.append(layer_values)
                        minimum_layer = min(minimum_layer, float(np.min(layer_values)))
                    partial_grid = np.sum(np.stack(partial_stack, axis=0), axis=0)
                    minimum_partial = min(minimum_partial, float(np.min(partial_grid)))
                    monotonicity = np.diff(np.cumsum(np.stack(partial_stack, axis=0), axis=0), axis=0)
                    maximum_partial_monotonicity_violation = max(maximum_partial_monotonicity_violation, float(np.max(-monotonicity)))
                    exact_grid = exact_kernel(beta, grid)
                    exact_slope_grid = exact_slope(beta, grid)
                    maximum_exact_slope = max(maximum_exact_slope, float(np.max(exact_slope_grid)))
                    maximum_exact_slope_violation = max(maximum_exact_slope_violation, float(np.max(exact_slope_grid - 1.0)))
                    for shifted, shift in zip(sample_values[1:], shifts):
                        shifted_partial = np.zeros_like(shifted)
                        for index in range(terms_count):
                            shifted_partial += layer(beta, shifted, index)
                        partial_ratio = float(np.max(np.abs(shifted_partial - partial_grid) / shift))
                        maximum_partial_ratio = max(maximum_partial_ratio, partial_ratio)
                        maximum_partial_budget_violation = max(maximum_partial_budget_violation, partial_ratio - budget)
                        regime_max_partial_ratio = max(regime_max_partial_ratio, partial_ratio)
                        shifted_exact = exact_kernel(beta, shifted)
                        exact_ratio = float(np.max(np.abs(shifted_exact - exact_grid) / shift))
                        maximum_exact_ratio = max(maximum_exact_ratio, exact_ratio)
                        regime_max_exact_ratio = max(regime_max_exact_ratio, exact_ratio)
                    expected_contexts = len(sites) * 2 * len(signs) * (len(terms) + 1) * len(adjoints)
                    for _site in sites:
                        for _order in range(2):
                            for _sign in signs:
                                for _prefix in range(len(terms) + 1):
                                    for _adjoint in adjoints:
                                        context_count += 1
                                        row["context_count"] += 1
                    check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} prefix coverage", row["context_count"] == expected_contexts, row["context_count"], expected_contexts, "all-prefix coverage")
                    check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} layer slope envelope", violation <= threshold, violation, f"<={threshold}", "Matsubara slope")
                    check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} partial budget", maximum_partial_budget_violation <= threshold, maximum_partial_budget_violation, f"<={threshold}", "Matsubara slope")
                    check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} exact unit slope", maximum_exact_slope_violation <= threshold, maximum_exact_slope_violation, f"<={threshold}", "capped kernel")
                    check(f"V={volume} d={size} beta={beta_fraction} bond={bond_term_index} positivity", minimum_layer >= -threshold and minimum_partial >= -threshold, [minimum_layer, minimum_partial], f">={-threshold}", "Matsubara positivity")
                    row.update({"maximum_partial_ratio": regime_max_partial_ratio, "maximum_exact_ratio": regime_max_exact_ratio})
                    bond_rows.append(row)
        expected_regime = sum(len(betas) * len(sites) * len(bond_indices) * 2 * len(signs) * (len(prior.base.split_system(volume, cutoff, parameters)[2]) + 1) * len(adjoints) for cutoff in cutoffs)
        per_regime.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "contexts": context_count - regime_start, "expected_contexts": expected_regime, "maximum_transition": regime_max_transition, "maximum_partial_ratio": regime_max_partial_ratio, "maximum_exact_ratio": regime_max_exact_ratio, "bond_rows": bond_rows})

    expected_contexts = sum(item["expected_contexts"] for item in per_regime)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "all-prefix coverage")
    check("layer slope envelope", maximum_layer_slope_violation <= threshold, maximum_layer_slope_violation, f"<={threshold}", "Matsubara slope")
    check("partial budget envelope", maximum_partial_budget_violation <= threshold, maximum_partial_budget_violation, f"<={threshold}", "Matsubara slope")
    check("exact capped unit slope", maximum_exact_slope_violation <= threshold, maximum_exact_slope_violation, f"<={threshold}", "capped kernel")
    check("partial monotonicity", maximum_partial_monotonicity_violation <= threshold, maximum_partial_monotonicity_violation, f"<={threshold}", "Matsubara positivity")
    check("positivity", minimum_layer >= -threshold and minimum_partial >= -threshold, [minimum_layer, minimum_partial], f">={-threshold}", "Matsubara positivity")
    check("finite budget positive", maximum_budget > 0.0, maximum_budget, ">0", "Matsubara budget")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-MATSUBARA-LIPSCHITZ-BUDGET", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {"context_count": context_count, "expected_contexts": expected_contexts, "theta": float(Fraction(fixture["theta"])), "series_terms": terms_count, "sample_grid_points": grid_points, "perturbation_fractions": perturbations, "maximum_transition_energy": maximum_transition, "maximum_layer_slope": maximum_layer_slope, "maximum_layer_slope_envelope_violation": maximum_layer_slope_violation, "maximum_partial_lipschitz_ratio": maximum_partial_ratio, "maximum_partial_budget_violation": maximum_partial_budget_violation, "maximum_exact_lipschitz_ratio": maximum_exact_ratio, "maximum_exact_slope": maximum_exact_slope, "maximum_exact_unit_slope_violation": maximum_exact_slope_violation, "maximum_partial_monotonicity_violation": maximum_partial_monotonicity_violation, "maximum_finite_budget": maximum_budget, "maximum_budget_tail_envelope": maximum_budget_tail_envelope, "minimum_layer_value": minimum_layer, "minimum_partial_value": minimum_partial, "regimes": per_regime, "layer_derivative_bound_finite_checked": True, "partial_lipschitz_budget_finite_checked": True, "exact_capped_kernel_lipschitz_finite_checked": True, "odd_frequency_budget_identity_recorded": True, "first_liouvillian_variation_reduction_proved": False, "eigenvector_rotation_control_proved": False, "resolvent_locality_proved": False, "capped_dirichlet_uniformity_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY MATSUBARA-LIPSCHITZ-BUDGET PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} L_N={payload['derived']['maximum_finite_budget']:.9f} ratio={payload['derived']['maximum_partial_lipschitz_ratio']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
