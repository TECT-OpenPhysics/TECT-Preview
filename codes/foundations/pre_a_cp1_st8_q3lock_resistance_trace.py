#!/usr/bin/env python3
"""Primary finite audit of the resistance-average trace identity for R-409.

For D=diag(pi), W=D^(-1/2)L D^(-1/2), and u=sqrt(pi), the weighted sum of
transformed pair vectors is I-u*u.T.  Therefore the unordered resistance
average equals tr(W^+) and the finite heat-trace integral
sum_{k>0} 1/lambda_k(W).
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_resistance_trace"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-resistance-trace-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_effective_resistance as r408  # noqa: E402
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


def trace_identity_data(probabilities: np.ndarray, laplacian: np.ndarray, eigen_floor: float, numerical_tolerance: float) -> dict[str, Any]:
    pi = np.asarray(probabilities, dtype=float)
    matrix = (np.asarray(laplacian, dtype=float) + np.asarray(laplacian, dtype=float).T) / 2.0
    if pi.ndim != 1 or matrix.shape != (pi.size, pi.size) or np.any(pi <= 0.0) or not np.all(np.isfinite(matrix)):
        raise AssertionError("invalid trace-identity input")
    pi = pi / float(np.sum(pi))
    diagonal_inverse_sqrt = 1.0 / np.sqrt(pi)
    normalized = diagonal_inverse_sqrt[:, None] * matrix * diagonal_inverse_sqrt[None, :]
    normalized = (normalized + normalized.T) / 2.0
    eigenvalues, vectors = np.linalg.eigh(normalized)
    # The source graph constructor accepts the same finite 1e-8 roundoff band
    # for its constant zero mode; keep the spectral floor strict for positive
    # modes while allowing only that declared numerical tolerance below zero.
    if eigenvalues.size < 2 or not np.all(np.isfinite(eigenvalues)) or float(eigenvalues[0]) < -numerical_tolerance:
        raise AssertionError("normalized Laplacian is not positive semidefinite")
    spectral_zero_threshold = max(eigen_floor, numerical_tolerance)
    positive = eigenvalues > spectral_zero_threshold
    if int(np.count_nonzero(positive)) != pi.size - 1:
        raise AssertionError(f"normalized Laplacian is disconnected at trace floor: {eigenvalues}")
    inverse_values = np.zeros_like(eigenvalues)
    inverse_values[positive] = 1.0 / eigenvalues[positive]
    normalized_inverse = (vectors * inverse_values) @ vectors.T
    unit_null = np.sqrt(pi)
    projector = np.eye(pi.size) - np.outer(unit_null, unit_null)
    trace_inverse = float(np.trace(normalized_inverse))
    projector_trace = float(np.trace(normalized_inverse @ projector))
    transformed_average = 0.0
    upper = np.triu_indices(pi.size, 1)
    transformed_pair_resistances = np.zeros_like(matrix)
    for left in range(pi.size):
        for right in range(left + 1, pi.size):
            vector = np.zeros(pi.size, dtype=float)
            vector[left] = 1.0 / math.sqrt(float(pi[left]))
            vector[right] = -1.0 / math.sqrt(float(pi[right]))
            value = float(vector @ normalized_inverse @ vector)
            if not math.isfinite(value) or value <= 0.0:
                raise AssertionError("nonpositive transformed resistance")
            transformed_pair_resistances[left, right] = transformed_pair_resistances[right, left] = value
            transformed_average += float(pi[left] * pi[right] * value)

    raw_eigenvalues, raw_vectors = np.linalg.eigh(matrix)
    if float(raw_eigenvalues[0]) < -numerical_tolerance:
        raise AssertionError("raw Laplacian is not positive semidefinite")
    raw_positive = raw_eigenvalues > spectral_zero_threshold
    if int(np.count_nonzero(raw_positive)) != pi.size - 1:
        raise AssertionError(f"raw Laplacian is disconnected at trace floor: {raw_eigenvalues}")
    raw_inverse_values = np.zeros_like(raw_eigenvalues)
    raw_inverse_values[raw_positive] = 1.0 / raw_eigenvalues[raw_positive]
    raw_inverse = (raw_vectors * raw_inverse_values) @ raw_vectors.T
    direct_average = 0.0
    for left in range(pi.size):
        for right in range(left + 1, pi.size):
            difference = np.zeros(pi.size, dtype=float)
            difference[left] = 1.0
            difference[right] = -1.0
            resistance = float(difference @ raw_inverse @ difference)
            if not math.isfinite(resistance) or resistance <= 0.0:
                raise AssertionError("nonpositive raw resistance")
            direct_average += float(pi[left] * pi[right] * resistance)
    if not math.isfinite(direct_average) or direct_average <= 0.0:
        raise AssertionError("invalid direct resistance average")
    heat_integral = float(np.sum(inverse_values[positive]))
    return {
        "positive_normalized_eigenvalue_count": int(np.count_nonzero(positive)),
        "minimum_positive_normalized_eigenvalue": float(np.min(eigenvalues[positive])),
        "maximum_normalized_eigenvalue": float(np.max(eigenvalues)),
        "positive_raw_eigenvalue_count": int(np.count_nonzero(raw_positive)),
        "minimum_positive_raw_eigenvalue": float(np.min(raw_eigenvalues[raw_positive])),
        "resistance_average": direct_average,
        "transformed_pair_average": transformed_average,
        "trace_inverse": trace_inverse,
        "projector_trace": projector_trace,
        "heat_trace_integral": heat_integral,
        "identity_residual": direct_average - trace_inverse,
        "transformed_identity_residual": transformed_average - trace_inverse,
        "projector_identity_residual": projector_trace - trace_inverse,
        "maximum_effective_resistance": float(np.max(transformed_pair_resistances[upper])),
        "pair_count": pi.size * (pi.size - 1) // 2,
    }


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

    check("identity", manifest["result_id"] == "R-409" and manifest["exploration_id"] == "EXP-001254" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-409/EXP-001254/false", "provenance")
    finite_flags = ("finite_resistance_trace_identity_closed", "finite_normalized_green_trace_closed", "finite_heat_trace_representation_closed", "finite_pair_normalization_closed", "finite_likelihood_row_coverage_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite trace identity only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("positive chi", chi > 0.0, chi, ">0", "fixture")

    profiles: dict[str, dict[str, Any]] = {}
    averages: list[float] = []
    traces: list[float] = []
    projector_traces: list[float] = []
    identity_residuals: list[float] = []
    transformed_residuals: list[float] = []
    projector_residuals: list[float] = []
    minimum_eigenvalues: list[float] = []
    maximum_resistances: list[float] = []
    pair_counts: list[int] = []
    total_contexts = 0
    total_rows = 0
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        generator_cache = {support: sum((q_ops[site] for site in support), np.zeros_like(q_ops[0])) for support in supports}
        prefixes_by_key = {(order_name, history_sign): r399.all_prefixes(terms, order, history_sign, delta, hbar) for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms))))) ) for history_sign in history_signs}
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_resistance_average": float("inf"), "maximum_resistance_average": 0.0, "minimum_trace_inverse": float("inf"), "maximum_trace_inverse": 0.0, "minimum_projector_trace": float("inf"), "maximum_projector_trace": 0.0, "maximum_identity_abs_residual": 0.0, "maximum_transformed_identity_abs_residual": 0.0, "maximum_projector_identity_abs_residual": 0.0, "minimum_positive_normalized_eigenvalue": float("inf"), "maximum_effective_resistance": 0.0, "pair_count": 0}
        for beta in betas:
            reference, raw_reference = r399.coordinate_distribution(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            for support in supports:
                for source_sign in source_signs:
                    source = q3.character(generator_cache[support], source_sign * amplitude, hbar)
                    seeded = r399.hermitian(source @ states[beta] @ source.conj().T)
                    for (_order_name, history_sign), prefixes in prefixes_by_key.items():
                        for prefix_length, prefix in prefixes:
                            for history_adjoint in adjoints:
                                state = r399.hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else r399.hermitian(prefix.conj().T @ seeded @ prefix)
                                sample, raw_sample = r399.coordinate_distribution(state, basis, dimension, volume)
                                check(f"d={dimension} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                                for orientation in orientations:
                                    collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                    for conditional, _likelihood in r408.r407.conditional_rows(reference, sample, collar_order, dimension, floor):
                                        _gap, laplacian, _conductance = r408.r407.intrinsic_graph(conditional, momentum, chi)
                                        data = trace_identity_data(conditional, laplacian, eigen_floor, tolerance)
                                        check("raw/normalized trace identity", abs(data["identity_residual"]) <= tolerance, data["identity_residual"], f"abs <= {tolerance}", "trace identity")
                                        check("transformed pair identity", abs(data["transformed_identity_residual"]) <= tolerance, data["transformed_identity_residual"], f"abs <= {tolerance}", "trace identity")
                                        check("projector trace identity", abs(data["projector_identity_residual"]) <= tolerance, data["projector_identity_residual"], f"abs <= {tolerance}", "trace identity")
                                        check("heat trace representation", abs(data["heat_trace_integral"] - data["trace_inverse"]) <= tolerance, [data["heat_trace_integral"], data["trace_inverse"]], f"abs <= {tolerance}", "heat trace")
                                        check("pair normalization", data["pair_count"] == dimension * (dimension - 1) // 2 and data["resistance_average"] > 0.0, [data["pair_count"], data["resistance_average"]], "unordered pair count and positive average", "normalization")
                                        averages.append(data["resistance_average"])
                                        traces.append(data["trace_inverse"])
                                        projector_traces.append(data["projector_trace"])
                                        identity_residuals.append(data["identity_residual"])
                                        transformed_residuals.append(data["transformed_identity_residual"])
                                        projector_residuals.append(data["projector_identity_residual"])
                                        minimum_eigenvalues.append(data["minimum_positive_normalized_eigenvalue"])
                                        maximum_resistances.append(data["maximum_effective_resistance"])
                                        pair_counts.append(data["pair_count"])
                                        total_rows += 1
                                        profile["row_count"] += 1
                                        profile["minimum_resistance_average"] = min(profile["minimum_resistance_average"], data["resistance_average"])
                                        profile["maximum_resistance_average"] = max(profile["maximum_resistance_average"], data["resistance_average"])
                                        profile["minimum_trace_inverse"] = min(profile["minimum_trace_inverse"], data["trace_inverse"])
                                        profile["maximum_trace_inverse"] = max(profile["maximum_trace_inverse"], data["trace_inverse"])
                                        profile["minimum_projector_trace"] = min(profile["minimum_projector_trace"], data["projector_trace"])
                                        profile["maximum_projector_trace"] = max(profile["maximum_projector_trace"], data["projector_trace"])
                                        profile["maximum_identity_abs_residual"] = max(profile["maximum_identity_abs_residual"], abs(data["identity_residual"]))
                                        profile["maximum_transformed_identity_abs_residual"] = max(profile["maximum_transformed_identity_abs_residual"], abs(data["transformed_identity_residual"]))
                                        profile["maximum_projector_identity_abs_residual"] = max(profile["maximum_projector_identity_abs_residual"], abs(data["projector_identity_residual"]))
                                        profile["minimum_positive_normalized_eigenvalue"] = min(profile["minimum_positive_normalized_eigenvalue"], data["minimum_positive_normalized_eigenvalue"])
                                        profile["maximum_effective_resistance"] = max(profile["maximum_effective_resistance"], data["maximum_effective_resistance"])
                                        profile["pair_count"] = data["pair_count"]
                                    profile["context_count"] += 1
                                    total_contexts += 1
        check(f"V={volume} d={dimension} profile", profile["row_count"] > profile["context_count"] and profile["minimum_resistance_average"] > 0.0, [profile["row_count"], profile["context_count"], profile["minimum_resistance_average"]], "positive trace and rows", "coverage")
        profiles[f"V={volume}/d={dimension}"] = profile

    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("trace identities nonnegative", all(math.isfinite(value) and value > 0.0 for value in traces + averages + projector_traces), [min(averages), max(averages), min(traces), max(traces)], ">0 finite", "trace identity")
    check("identity residuals bounded", max(abs(value) for value in identity_residuals + transformed_residuals + projector_residuals) <= tolerance, [max(abs(value) for value in identity_residuals), max(abs(value) for value in transformed_residuals), max(abs(value) for value in projector_residuals)], f"abs <= {tolerance}", "trace identity")
    check("positive normalized spectrum", all(value > eigen_floor for value in minimum_eigenvalues), [min(minimum_eigenvalues), eigen_floor], "> eigen floor", "connectivity")
    expected_pair_counts = sorted({dimension * (dimension - 1) // 2 for _volume, dimension in pairs})
    check("pair-count coverage", all(value in expected_pair_counts for value in pair_counts), sorted(set(pair_counts)), expected_pair_counts, "normalization")
    derived = {
        "system_count": len(pairs),
        "context_count": total_contexts,
        "comparison_row_count": total_rows,
        "minimum_resistance_average": min(averages),
        "maximum_resistance_average": max(averages),
        "minimum_trace_inverse": min(traces),
        "maximum_trace_inverse": max(traces),
        "minimum_projector_trace": min(projector_traces),
        "maximum_projector_trace": max(projector_traces),
        "maximum_identity_abs_residual": max(abs(value) for value in identity_residuals),
        "maximum_transformed_identity_abs_residual": max(abs(value) for value in transformed_residuals),
        "maximum_projector_identity_abs_residual": max(abs(value) for value in projector_residuals),
        "minimum_positive_normalized_eigenvalue": min(minimum_eigenvalues),
        "maximum_effective_resistance": max(maximum_resistances),
        "pair_count": sorted(set(pair_counts)),
        "cutoff_dimensions": [dimension for _volume, dimension in pairs],
        "system_profiles": profiles,
        "finite_resistance_trace_identity_closed": True,
        "finite_normalized_green_trace_closed": True,
        "finite_heat_trace_representation_closed": True,
        "finite_pair_normalization_closed": True,
        "finite_likelihood_row_coverage_closed": True,
        "cutoff_independent_green_trace_closed": False,
        "volume_independent_green_trace_closed": False,
        "phase_uniform_green_trace_closed": False,
        "exhaustion_uniform_green_trace_closed": False,
        "common_core_closed": False,
        "common_alpha_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False
    }
    payload = {"schema": "tect/pre-a-r409-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-409", "exploration_id": "EXP-001254", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    r408.r407.atomic_json(output, payload)
    print(f"R-409 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} Rbar=[{min(averages):.6g},{max(averages):.6g}] trace=[{min(traces):.6g},{max(traces):.6g}] max_residual={max(abs(value) for value in identity_residuals + transformed_residuals + projector_residuals):.3g}")
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
