#!/usr/bin/env python3
"""Independent finite reconstruction for the R-408 resistance certificate.

This lane rebuilds the finite oscillator, Gibbs, history, coordinate and
conditional-row data through the separately maintained R-407 reconstruction,
then computes the Laplacian pseudoinverse and resistance average locally.  It
does not import the R-408 primary module.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_effective_resistance"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-effective-resistance-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_canonical_path_resistance_independent as r407i  # noqa: E402
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


def effective_resistance_data(probabilities: np.ndarray, laplacian: np.ndarray, eigen_floor: float) -> dict[str, Any]:
    pi = np.asarray(probabilities, dtype=float)
    matrix = (np.asarray(laplacian, dtype=float) + np.asarray(laplacian, dtype=float).T) / 2.0
    if pi.ndim != 1 or matrix.shape != (pi.size, pi.size) or np.any(pi <= 0.0) or not np.all(np.isfinite(matrix)):
        raise AssertionError("invalid resistance input")
    pi = pi / float(np.sum(pi))
    eigenvalues, vectors = np.linalg.eigh(matrix)
    if eigenvalues.size < 2 or not np.all(np.isfinite(eigenvalues)) or float(eigenvalues[0]) < -eigen_floor:
        raise AssertionError("Laplacian is not positive semidefinite")
    positive = eigenvalues > eigen_floor
    if int(np.count_nonzero(positive)) != pi.size - 1:
        raise AssertionError("Laplacian is disconnected at resistance floor")
    inverse_values = np.zeros_like(eigenvalues)
    inverse_values[positive] = 1.0 / eigenvalues[positive]
    pseudoinverse = (vectors * inverse_values) @ vectors.T
    resistances = np.zeros_like(matrix)
    for left in range(pi.size):
        for right in range(left + 1, pi.size):
            value = float(pseudoinverse[left, left] + pseudoinverse[right, right] - 2.0 * pseudoinverse[left, right])
            if not math.isfinite(value) or value <= 0.0:
                raise AssertionError("nonpositive effective resistance")
            resistances[left, right] = resistances[right, left] = value
    average = sum(float(pi[left] * pi[right] * resistances[left, right]) for left in range(pi.size) for right in range(left + 1, pi.size))
    if not math.isfinite(average) or average <= 0.0:
        raise AssertionError("invalid resistance average")
    upper = np.triu_indices(pi.size, 1)
    return {
        "positive_eigenvalue_count": int(np.count_nonzero(positive)),
        "minimum_positive_laplacian_eigenvalue": float(np.min(eigenvalues[positive])),
        "maximum_laplacian_eigenvalue": float(np.max(eigenvalues)),
        "minimum_effective_resistance": float(np.min(resistances[upper])),
        "maximum_effective_resistance": float(np.max(resistances[upper])),
        "resistance_average": average,
        "resistance_bound": 1.0 / average,
        "pair_count": pi.size * (pi.size - 1) // 2,
    }


def variance(probabilities: np.ndarray, values: np.ndarray) -> float:
    pi = np.asarray(probabilities, dtype=float)
    pi = pi / float(np.sum(pi))
    values = np.asarray(values, dtype=float)
    centered = values - float(np.sum(pi * values))
    return max(0.0, float(np.sum(pi * centered * centered)))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_floor"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    chi = float(Fraction(str(fixture["chi"])))
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    source_signs = [int(value) for value in fixture["source_sign_values"]]
    history_signs = [int(value) for value in fixture["history_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    orientations = list(fixture["orientations"])
    supports = [tuple(int(site) for site in support) for support in fixture["source_support_values"]]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 220:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-408" and manifest["exploration_id"] == "EXP-001253" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-408/EXP-001253/false", "provenance")
    finite_flags = ("finite_effective_resistance_closed", "finite_resistance_poincare_closed", "finite_likelihood_row_bound_closed", "finite_cutoff_profile_closed", "finite_tree_independence_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite effective resistance only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("positive chi", chi > 0.0, chi, ">0", "fixture")

    profiles: dict[str, dict[str, Any]] = {}
    bounds: list[float] = []
    gaps: list[float] = []
    residuals: list[float] = []
    averages: list[float] = []
    minimum_laplacian_values: list[float] = []
    maximum_resistances: list[float] = []
    tree_bounds: list[float] = []
    total_contexts = 0
    total_rows = 0
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r407i.model(volume, dimension, fixture)
        basis = r407i.coordinate_basis(dimension, volume)
        _levels, momentum = r407i.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        states = {beta: r407i.gibbs(hamiltonian, beta) for beta in betas}
        generator = q_ops[0]
        prefix_cache = {(name, sign): r407i.prefixes(terms, order, sign, delta, hbar) for name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms))))) ) for sign in history_signs}
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_bound": float("inf"), "maximum_bound": 0.0, "minimum_gap": float("inf"), "maximum_gap": 0.0, "minimum_resistance_average": float("inf"), "maximum_resistance_average": 0.0, "minimum_laplacian_eigenvalue": float("inf"), "maximum_resistance": 0.0, "minimum_residual": float("inf"), "maximum_residual": 0.0, "minimum_tree_bound": float("inf")}
        for beta in betas:
            reference, raw_reference = r407i.probabilities(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            for support in supports:
                for source_sign in source_signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = r407i.hermitian(source @ states[beta] @ source.conj().T)
                    for (_order_name, history_sign), cached_prefixes in prefix_cache.items():
                        for prefix_length, prefix in cached_prefixes:
                            for history_adjoint in adjoints:
                                state = r407i.hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else r407i.hermitian(prefix.conj().T @ seeded @ prefix)
                                sample, raw_sample = r407i.probabilities(state, basis, dimension, volume)
                                check(f"d={dimension} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                                for orientation in orientations:
                                    order_sites = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                    for conditional, likelihood in r407i.conditional_rows(reference, sample, order_sites, dimension, floor):
                                        gap, laplacian, conductance = r407i.intrinsic_graph(conditional, momentum, chi)
                                        data = effective_resistance_data(conditional, laplacian, eigen_floor)
                                        tree = r407i.canonical_data(conditional, conductance, 1e-300)
                                        energy = max(0.0, float(np.real(likelihood @ laplacian @ likelihood)))
                                        var = variance(conditional, likelihood)
                                        residual = energy - data["resistance_bound"] * var
                                        check("resistance bound residual", math.isfinite(residual) and residual >= -tolerance, residual, f">=-{tolerance}", "effective resistance")
                                        check("resistance bound below graph gap", data["resistance_bound"] <= gap + tolerance, [data["resistance_bound"], gap], f"bound <= gap + {tolerance}", "effective resistance")
                                        bounds.append(data["resistance_bound"])
                                        gaps.append(gap)
                                        residuals.append(residual)
                                        averages.append(data["resistance_average"])
                                        minimum_laplacian_values.append(data["minimum_positive_laplacian_eigenvalue"])
                                        maximum_resistances.append(data["maximum_effective_resistance"])
                                        tree_bounds.append(tree["canonical_bound"])
                                        total_rows += 1
                                        profile["row_count"] += 1
                                        profile["minimum_bound"] = min(profile["minimum_bound"], data["resistance_bound"])
                                        profile["maximum_bound"] = max(profile["maximum_bound"], data["resistance_bound"])
                                        profile["minimum_gap"] = min(profile["minimum_gap"], gap)
                                        profile["maximum_gap"] = max(profile["maximum_gap"], gap)
                                        profile["minimum_resistance_average"] = min(profile["minimum_resistance_average"], data["resistance_average"])
                                        profile["maximum_resistance_average"] = max(profile["maximum_resistance_average"], data["resistance_average"])
                                        profile["minimum_laplacian_eigenvalue"] = min(profile["minimum_laplacian_eigenvalue"], data["minimum_positive_laplacian_eigenvalue"])
                                        profile["maximum_resistance"] = max(profile["maximum_resistance"], data["maximum_effective_resistance"])
                                        profile["minimum_residual"] = min(profile["minimum_residual"], residual)
                                        profile["maximum_residual"] = max(profile["maximum_residual"], residual)
                                        profile["minimum_tree_bound"] = min(profile["minimum_tree_bound"], tree["canonical_bound"])
                                    profile["context_count"] += 1
                                    total_contexts += 1
        check(f"V={volume} d={dimension} profile", profile["row_count"] > profile["context_count"] and profile["minimum_bound"] > 0.0, [profile["row_count"], profile["context_count"], profile["minimum_bound"]], "positive bound and rows", "coverage")
        profiles[f"V={volume}/d={dimension}"] = profile

    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("resistance bounds positive", all(math.isfinite(value) and value > 0.0 for value in bounds), [min(bounds), max(bounds)], ">0 finite", "effective resistance")
    check("resistance residuals nonnegative", all(math.isfinite(value) and value >= -tolerance for value in residuals), [min(residuals), max(residuals)], f">=-{tolerance}", "effective resistance")
    check("Laplacian connected", all(value > eigen_floor for value in minimum_laplacian_values), [min(minimum_laplacian_values), eigen_floor], ">eigen floor", "connectivity")
    check("tree-independent finite comparison", all(math.isfinite(value) and value > 0.0 for value in tree_bounds) and max(bounds) <= max(gaps) + tolerance, [min(tree_bounds), max(bounds), max(gaps)], "positive alternative and finite gap comparison", "tree independence")
    derived = {
        "system_count": len(pairs),
        "context_count": total_contexts,
        "comparison_row_count": total_rows,
        "minimum_resistance_bound": min(bounds),
        "maximum_resistance_bound": max(bounds),
        "minimum_intrinsic_gap": min(gaps),
        "maximum_intrinsic_gap": max(gaps),
        "minimum_resistance_average": min(averages),
        "maximum_resistance_average": max(averages),
        "minimum_positive_laplacian_eigenvalue": min(minimum_laplacian_values),
        "maximum_effective_resistance": max(maximum_resistances),
        "minimum_residual": min(residuals),
        "maximum_residual": max(residuals),
        "minimum_tree_bound": min(tree_bounds),
        "maximum_tree_bound": max(tree_bounds),
        "cutoff_dimensions": [dimension for _volume, dimension in pairs],
        "system_profiles": profiles,
        "finite_effective_resistance_closed": True,
        "finite_resistance_poincare_closed": True,
        "finite_likelihood_row_bound_closed": True,
        "finite_cutoff_profile_closed": True,
        "finite_tree_independence_closed": True,
        "cutoff_independent_green_bound_closed": False,
        "volume_independent_green_bound_closed": False,
        "phase_uniform_bound_closed": False,
        "exhaustion_uniform_bound_closed": False,
        "common_core_closed": False,
        "common_alpha_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r408-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-408", "exploration_id": "EXP-001253", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    r407i.atomic_json(output, payload)
    print(f"R-408 INDEPENDENT PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} bound=[{min(bounds):.6g},{max(bounds):.6g}] Rbar=[{min(averages):.6g},{max(averages):.6g}]")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
