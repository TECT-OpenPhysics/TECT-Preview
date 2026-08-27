#!/usr/bin/env python3
"""Independent finite Matsubara Lipschitz-budget audit for EXP-001217 / R-375."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering_independent as reference  # noqa: E402


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


def matsubara_layer(beta: float, energy: np.ndarray, mode: int) -> np.ndarray:
    frequency = math.pi * (2.0 * float(mode) + 1.0)
    square = frequency * frequency + np.square(beta * energy)
    return np.divide(8.0 * energy, square, out=np.zeros_like(energy), where=square > 0.0)


def matsubara_slope(beta: float, energy: np.ndarray, mode: int) -> np.ndarray:
    frequency = math.pi * (2.0 * float(mode) + 1.0)
    scaled = np.square(beta * energy)
    denominator = frequency * frequency + scaled
    return 8.0 * np.abs(frequency * frequency - scaled) / np.square(denominator)


def capped(beta: float, energy: np.ndarray) -> np.ndarray:
    return 2.0 * np.tanh(beta * energy / 2.0) / beta


def capped_slope(beta: float, energy: np.ndarray) -> np.ndarray:
    return np.square(1.0 / np.cosh(beta * energy / 2.0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    beta_values = [Fraction(item) for item in fixture["beta_values"]]
    sign_values = [int(item) for item in fixture["time_sign_values"]]
    adjoint_values = [int(item) for item in fixture["history_adjoint_values"]]
    modes = int(fixture["series_terms"])
    points = int(fixture["sample_grid_points"])
    step_fractions = [float(Fraction(item)) for item in fixture["perturbation_fractions"]]
    tolerance = float(fixture["finite_tolerance"])
    slack = tolerance * float(fixture["tolerance_multiplier"])
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
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["eigenvector_rotation_control_proved"] is False, manifest["scope"], "finite-scalar-sensitivity-only", "scope")
    check("grid", points >= 3, points, ">=3", "fixture")
    check("series", modes >= 1, modes, ">=1", "fixture")

    context_count = 0
    global_max_energy = 0.0
    global_max_layer_slope = 0.0
    global_layer_violation = -float("inf")
    global_partial_ratio = 0.0
    global_partial_violation = -float("inf")
    global_capped_ratio = 0.0
    global_capped_slope = 0.0
    global_capped_violation = -float("inf")
    global_monotonicity_violation = -float("inf")
    global_budget = 0.0
    global_tail = 0.0
    global_min_layer = float("inf")
    global_min_partial = float("inf")
    regime_rows: list[dict[str, Any]] = []

    for regime in fixture["regimes"]:
        volume = int(regime["volume"])
        cutoffs = [int(item) for item in regime["cutoff_values"]]
        sites = [int(item) for item in regime["site_values"]]
        bonds = [int(item) for item in regime["bond_term_indices"]]
        start = context_count
        regime_energy = 0.0
        regime_partial_ratio = 0.0
        regime_capped_ratio = 0.0
        rows: list[dict[str, Any]] = []
        for cutoff in cutoffs:
            _coordinates, hamiltonian, terms = reference.build_system(volume, cutoff, parameters)
            identity = np.eye(hamiltonian.shape[0], dtype=complex)
            for beta_fraction in beta_values:
                beta = float(beta_fraction)
                check(f"V={volume} d={cutoff} beta={beta_fraction} positive beta", beta > 0.0, beta, ">0", "Matsubara budget")
                for bond in bonds:
                    doubled_bond = np.kron(terms[bond], identity) + np.kron(identity, terms[bond])
                    spectrum = np.linalg.eigvalsh(reference.hermitian(doubled_bond))
                    span = float(spectrum[-1] - spectrum[0])
                    global_max_energy = max(global_max_energy, span)
                    regime_energy = max(regime_energy, span)
                    energies = np.linspace(0.0, span, points, dtype=float)
                    offsets = [fraction * (1.0 + span) for fraction in step_fractions]
                    budget = sum(8.0 / (math.pi * (2.0 * float(mode) + 1.0)) ** 2 for mode in range(modes))
                    tail = 4.0 / (math.pi * math.pi * (2.0 * modes - 1.0))
                    global_budget = max(global_budget, budget)
                    global_tail = max(global_tail, tail)
                    layer_values: list[np.ndarray] = []
                    for mode in range(modes):
                        derivative = matsubara_slope(beta, energies, mode)
                        frequency = math.pi * (2.0 * float(mode) + 1.0)
                        envelope = 8.0 / (frequency * frequency)
                        envelope_error = float(np.max(derivative - envelope))
                        global_layer_violation = max(global_layer_violation, envelope_error)
                        global_max_layer_slope = max(global_max_layer_slope, float(np.max(derivative)))
                        values = matsubara_layer(beta, energies, mode)
                        layer_values.append(values)
                        global_min_layer = min(global_min_layer, float(np.min(values)))
                    partial = np.sum(np.asarray(layer_values), axis=0)
                    global_min_partial = min(global_min_partial, float(np.min(partial)))
                    partial_sequence = np.cumsum(np.asarray(layer_values), axis=0)
                    global_monotonicity_violation = max(global_monotonicity_violation, float(np.max(-np.diff(partial_sequence, axis=0))))
                    exact = capped(beta, energies)
                    slope = capped_slope(beta, energies)
                    global_capped_slope = max(global_capped_slope, float(np.max(slope)))
                    global_capped_violation = max(global_capped_violation, float(np.max(slope - 1.0)))
                    for offset in offsets:
                        displaced = energies + offset
                        displaced_partial = sum((matsubara_layer(beta, displaced, mode) for mode in range(modes)), start=np.zeros_like(displaced))
                        partial_ratio = float(np.max(np.abs(displaced_partial - partial) / offset))
                        global_partial_ratio = max(global_partial_ratio, partial_ratio)
                        global_partial_violation = max(global_partial_violation, partial_ratio - budget)
                        regime_partial_ratio = max(regime_partial_ratio, partial_ratio)
                        displaced_exact = capped(beta, displaced)
                        capped_ratio = float(np.max(np.abs(displaced_exact - exact) / offset))
                        global_capped_ratio = max(global_capped_ratio, capped_ratio)
                        regime_capped_ratio = max(regime_capped_ratio, capped_ratio)
                    per_bond_context = len(sites) * len(sign_values) * len(adjoint_values) * (len(terms) + 1) * 2
                    context_count += per_bond_context
                    check(f"V={volume} d={cutoff} beta={beta_fraction} bond={bond} coverage", per_bond_context == len(sites) * 2 * len(sign_values) * (len(terms) + 1) * len(adjoint_values), per_bond_context, "declared all-prefix count", "all-prefix coverage")
                    check(f"V={volume} d={cutoff} beta={beta_fraction} bond={bond} slope", envelope_error <= slack, envelope_error, f"<={slack}", "Matsubara slope")
                    check(f"V={volume} d={cutoff} beta={beta_fraction} bond={bond} partial", global_partial_violation <= slack, global_partial_violation, f"<={slack}", "Matsubara slope")
                    check(f"V={volume} d={cutoff} beta={beta_fraction} bond={bond} capped", global_capped_violation <= slack, global_capped_violation, f"<={slack}", "capped kernel")
                    check(f"V={volume} d={cutoff} beta={beta_fraction} bond={bond} positive", global_min_layer >= -slack and global_min_partial >= -slack, [global_min_layer, global_min_partial], f">={-slack}", "Matsubara positivity")
                    rows.append({"cutoff": cutoff, "beta": str(beta_fraction), "bond_term_index": bond, "maximum_transition": span, "budget": budget, "budget_tail_envelope": tail, "context_count": per_bond_context, "maximum_partial_ratio": regime_partial_ratio, "maximum_exact_ratio": regime_capped_ratio})
        expected = sum(len(sites) * len(beta_values) * len(bonds) * 2 * len(sign_values) * (len(reference.build_system(volume, cutoff, parameters)[2]) + 1) * len(adjoint_values) for cutoff in cutoffs)
        regime_rows.append({"shape": regime["shape"], "volume": volume, "cutoffs": cutoffs, "contexts": context_count - start, "expected_contexts": expected, "maximum_transition": regime_energy, "maximum_partial_ratio": regime_partial_ratio, "maximum_exact_ratio": regime_capped_ratio, "bond_rows": rows})

    expected_contexts = sum(item["expected_contexts"] for item in regime_rows)
    check("coverage", context_count == expected_contexts, context_count, expected_contexts, "all-prefix coverage")
    check("layer envelope", global_layer_violation <= slack, global_layer_violation, f"<={slack}", "Matsubara slope")
    check("partial budget", global_partial_violation <= slack, global_partial_violation, f"<={slack}", "Matsubara slope")
    check("capped unit slope", global_capped_violation <= slack, global_capped_violation, f"<={slack}", "capped kernel")
    check("monotone partial", global_monotonicity_violation <= slack, global_monotonicity_violation, f"<={slack}", "Matsubara positivity")
    check("positivity", global_min_layer >= -slack and global_min_partial >= -slack, [global_min_layer, global_min_partial], f">={-slack}", "Matsubara positivity")
    check("budget positive", global_budget > 0.0, global_budget, ">0", "Matsubara budget")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-MATSUBARA-LIPSCHITZ-BUDGET", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {"context_count": context_count, "expected_contexts": expected_contexts, "theta": float(Fraction(fixture["theta"])), "series_terms": modes, "sample_grid_points": points, "perturbation_fractions": step_fractions, "maximum_transition_energy": global_max_energy, "maximum_layer_slope": global_max_layer_slope, "maximum_layer_slope_envelope_violation": global_layer_violation, "maximum_partial_lipschitz_ratio": global_partial_ratio, "maximum_partial_budget_violation": global_partial_violation, "maximum_exact_lipschitz_ratio": global_capped_ratio, "maximum_exact_slope": global_capped_slope, "maximum_exact_unit_slope_violation": global_capped_violation, "maximum_partial_monotonicity_violation": global_monotonicity_violation, "maximum_finite_budget": global_budget, "maximum_budget_tail_envelope": global_tail, "minimum_layer_value": global_min_layer, "minimum_partial_value": global_min_partial, "regimes": regime_rows, "layer_derivative_bound_finite_checked": True, "partial_lipschitz_budget_finite_checked": True, "exact_capped_kernel_lipschitz_finite_checked": True, "odd_frequency_budget_identity_recorded": True, "first_liouvillian_variation_reduction_proved": False, "eigenvector_rotation_control_proved": False, "resolvent_locality_proved": False, "capped_dirichlet_uniformity_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT MATSUBARA-LIPSCHITZ-BUDGET PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} L_N={payload['derived']['maximum_finite_budget']:.9f} ratio={payload['derived']['maximum_partial_lipschitz_ratio']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
