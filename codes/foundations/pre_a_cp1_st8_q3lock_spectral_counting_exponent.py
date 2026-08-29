#!/usr/bin/env python3
"""Primary finite audit of the sublinear mode-counting family for R-411.

For D=diag(pi), W=D^(-1/2)L D^(-1/2), order the d-1 positive eigenvalues
as lambda_k.  For 0<alpha<1, C_alpha=max_k k/lambda_k^alpha gives the
finite envelope tr(W^+) <= C_alpha^(1/alpha) sum_k k^(-1/alpha), with an
integral tail comparison for the corresponding infinite zeta series.
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
SLUG = "pre_a_cp1_st8_q3lock_spectral_counting_exponent"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spectral-counting-exponent-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
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
    positive_eigenvalues = eigenvalues[positive]
    mode_indices = np.arange(1, pi.size, dtype=float)
    mode_constants = positive_eigenvalues / np.square(mode_indices)
    mode_constant = float(np.min(mode_constants))
    harmonic_square = float(np.sum(1.0 / np.square(mode_indices)))
    zeta_bound = harmonic_square / mode_constant
    zeta_infinite_bound = (math.pi**2 / 6.0) / mode_constant
    mode_envelope_residual = float(np.min(positive_eigenvalues - mode_constant * np.square(mode_indices)))
    if not all(math.isfinite(value) and value > 0.0 for value in (mode_constant, harmonic_square, zeta_bound, zeta_infinite_bound)):
        raise AssertionError("invalid quadratic mode-counting envelope")
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
        "ordered_positive_normalized_eigenvalues": [float(value) for value in positive_eigenvalues],
        "mode_constants": [float(value) for value in mode_constants],
        "mode_constant": mode_constant,
        "harmonic_square": harmonic_square,
        "zeta_bound": zeta_bound,
        "zeta_infinite_bound": zeta_infinite_bound,
        "mode_envelope_residual": mode_envelope_residual,
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


def sublinear_envelope_data(positive_eigenvalues: np.ndarray, exponents: list[float]) -> dict[str, dict[str, Any]]:
    values = np.asarray(positive_eigenvalues, dtype=float)
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)) or np.any(values <= 0.0):
        raise AssertionError("invalid positive spectrum for sublinear envelope")
    indices = np.arange(1, values.size + 1, dtype=float)
    profiles: dict[str, dict[str, Any]] = {}
    for alpha in exponents:
        if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
            raise AssertionError(f"sublinear exponent must lie in (0,1): {alpha}")
        reciprocal_exponent = 1.0 / alpha
        constants = indices / np.power(values, alpha)
        constant = float(np.max(constants))
        finite_zeta = float(np.sum(np.power(indices, -reciprocal_exponent)))
        tail = float(values.size ** (1.0 - reciprocal_exponent) / (reciprocal_exponent - 1.0))
        finite_bound = float(constant ** reciprocal_exponent * finite_zeta)
        infinite_bound = float(constant ** reciprocal_exponent * (finite_zeta + tail))
        implied_lower = np.power(indices / constant, reciprocal_exponent)
        envelope_residual = float(np.min(values - implied_lower))
        if not all(math.isfinite(item) and item > 0.0 for item in (constant, finite_zeta, tail, finite_bound, infinite_bound)):
            raise AssertionError("invalid sublinear counting envelope")
        label = str(alpha).rstrip("0").rstrip(".")
        profiles[label] = {
            "alpha": float(alpha),
            "reciprocal_exponent": reciprocal_exponent,
            "counting_constant": constant,
            "finite_zeta_sum": finite_zeta,
            "integral_tail_bound": tail,
            "finite_trace_bound": finite_bound,
            "infinite_zeta_bound": infinite_bound,
            "envelope_residual": envelope_residual,
        }
    return profiles


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_floor"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    exponents = [float(Fraction(value)) for value in fixture["counting_exponents"]]
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

    check("identity", manifest["result_id"] == "R-411" and manifest["exploration_id"] == "EXP-001256" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-411/EXP-001256/false", "provenance")
    finite_flags = ("finite_mode_ordering_closed", "finite_sublinear_counting_closed", "finite_zeta_tail_bound_closed", "finite_likelihood_row_coverage_closed")
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
    mode_constants: list[float] = []
    zeta_bounds: list[float] = []
    zeta_infinite_bounds: list[float] = []
    mode_envelope_residuals: list[float] = []
    alpha_rows: dict[str, list[dict[str, float]]] = {str(alpha).rstrip("0").rstrip("."): [] for alpha in exponents}
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
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_resistance_average": float("inf"), "maximum_resistance_average": 0.0, "minimum_trace_inverse": float("inf"), "maximum_trace_inverse": 0.0, "minimum_projector_trace": float("inf"), "maximum_projector_trace": 0.0, "maximum_identity_abs_residual": 0.0, "maximum_transformed_identity_abs_residual": 0.0, "maximum_projector_identity_abs_residual": 0.0, "minimum_positive_normalized_eigenvalue": float("inf"), "maximum_effective_resistance": 0.0, "minimum_mode_constant": float("inf"), "maximum_mode_constant": 0.0, "minimum_zeta_bound": float("inf"), "maximum_zeta_bound": 0.0, "maximum_mode_envelope_residual": 0.0, "alpha_profiles": {str(alpha).rstrip("0").rstrip("."): {"minimum_counting_constant": float("inf"), "maximum_counting_constant": 0.0, "minimum_finite_trace_bound": float("inf"), "maximum_finite_trace_bound": 0.0, "minimum_infinite_zeta_bound": float("inf"), "maximum_infinite_zeta_bound": 0.0, "maximum_envelope_abs_residual": 0.0} for alpha in exponents}, "pair_count": 0}
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
                                        alpha_data = sublinear_envelope_data(np.asarray(data["ordered_positive_normalized_eigenvalues"], dtype=float), exponents)
                                        for alpha_label, envelope in alpha_data.items():
                                            check(f"alpha={alpha_label} positive", envelope["counting_constant"] > 0.0 and envelope["reciprocal_exponent"] > 1.0, [envelope["counting_constant"], envelope["reciprocal_exponent"]], "C_alpha>0 and 1/alpha>1", "sublinear counting")
                                            check(f"alpha={alpha_label} finite trace bound", data["trace_inverse"] <= envelope["finite_trace_bound"] + tolerance, [data["trace_inverse"], envelope["finite_trace_bound"]], f"trace <= finite bound + {tolerance}", "sublinear zeta")
                                            check(f"alpha={alpha_label} tail comparison", envelope["finite_trace_bound"] <= envelope["infinite_zeta_bound"] + tolerance, [envelope["finite_trace_bound"], envelope["infinite_zeta_bound"]], f"finite <= infinite bound + {tolerance}", "sublinear zeta")
                                            alpha_rows[alpha_label].append(envelope)
                                            alpha_profile = profile["alpha_profiles"][alpha_label]
                                            alpha_profile["minimum_counting_constant"] = min(alpha_profile["minimum_counting_constant"], envelope["counting_constant"])
                                            alpha_profile["maximum_counting_constant"] = max(alpha_profile["maximum_counting_constant"], envelope["counting_constant"])
                                            alpha_profile["minimum_finite_trace_bound"] = min(alpha_profile["minimum_finite_trace_bound"], envelope["finite_trace_bound"])
                                            alpha_profile["maximum_finite_trace_bound"] = max(alpha_profile["maximum_finite_trace_bound"], envelope["finite_trace_bound"])
                                            alpha_profile["minimum_infinite_zeta_bound"] = min(alpha_profile["minimum_infinite_zeta_bound"], envelope["infinite_zeta_bound"])
                                            alpha_profile["maximum_infinite_zeta_bound"] = max(alpha_profile["maximum_infinite_zeta_bound"], envelope["infinite_zeta_bound"])
                                            alpha_profile["maximum_envelope_abs_residual"] = max(alpha_profile["maximum_envelope_abs_residual"], abs(envelope["envelope_residual"]))
                                        check("ordered positive spectrum", data["ordered_positive_normalized_eigenvalues"] == sorted(data["ordered_positive_normalized_eigenvalues"]) and len(data["ordered_positive_normalized_eigenvalues"]) == dimension - 1, data["ordered_positive_normalized_eigenvalues"], f"sorted length {dimension - 1}", "mode counting")
                                        check("quadratic mode envelope", data["mode_envelope_residual"] >= -tolerance and data["mode_constant"] > 0.0, [data["mode_envelope_residual"], data["mode_constant"]], f"residual >= -{tolerance}, c2 > 0", "mode counting")
                                        check("finite zeta trace upper bound", data["trace_inverse"] <= data["zeta_bound"] + tolerance, [data["trace_inverse"], data["zeta_bound"]], f"trace <= bound + {tolerance}", "zeta envelope")
                                        check("infinite zeta comparison", data["zeta_bound"] <= data["zeta_infinite_bound"] + tolerance, [data["zeta_bound"], data["zeta_infinite_bound"]], f"finite <= pi^2/6 bound + {tolerance}", "zeta envelope")
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
                                        mode_constants.append(data["mode_constant"])
                                        zeta_bounds.append(data["zeta_bound"])
                                        zeta_infinite_bounds.append(data["zeta_infinite_bound"])
                                        mode_envelope_residuals.append(data["mode_envelope_residual"])
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
                                        profile["minimum_mode_constant"] = min(profile["minimum_mode_constant"], data["mode_constant"])
                                        profile["maximum_mode_constant"] = max(profile["maximum_mode_constant"], data["mode_constant"])
                                        profile["minimum_zeta_bound"] = min(profile["minimum_zeta_bound"], data["zeta_bound"])
                                        profile["maximum_zeta_bound"] = max(profile["maximum_zeta_bound"], data["zeta_bound"])
                                        profile["maximum_mode_envelope_residual"] = max(profile["maximum_mode_envelope_residual"], abs(data["mode_envelope_residual"]))
                                        profile["pair_count"] = data["pair_count"]
                                    profile["context_count"] += 1
                                    total_contexts += 1
        check(f"V={volume} d={dimension} profile", profile["row_count"] > profile["context_count"] and profile["minimum_resistance_average"] > 0.0 and profile["minimum_mode_constant"] > 0.0, [profile["row_count"], profile["context_count"], profile["minimum_resistance_average"], profile["minimum_mode_constant"]], "positive trace and mode envelope", "coverage")
        profiles[f"V={volume}/d={dimension}"] = profile

    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("trace identities nonnegative", all(math.isfinite(value) and value > 0.0 for value in traces + averages + projector_traces), [min(averages), max(averages), min(traces), max(traces)], ">0 finite", "trace identity")
    check("mode constants positive", all(math.isfinite(value) and value > 0.0 for value in mode_constants), [min(mode_constants), max(mode_constants)], ">0 finite", "mode counting")
    check("zeta bounds finite", all(math.isfinite(value) and value > 0.0 for value in zeta_bounds + zeta_infinite_bounds), [min(zeta_bounds), max(zeta_bounds), min(zeta_infinite_bounds), max(zeta_infinite_bounds)], ">0 finite", "zeta envelope")
    check("zeta slack nonnegative", max(data - trace for data, trace in zip(zeta_bounds, traces)) >= -tolerance and min(data - trace for data, trace in zip(zeta_bounds, traces)) >= -tolerance, [min(data - trace for data, trace in zip(zeta_bounds, traces)), max(data - trace for data, trace in zip(zeta_bounds, traces))], f">= -{tolerance}", "zeta envelope")
    check("sublinear exponent grid", set(alpha_rows) == {str(alpha).rstrip("0").rstrip(".") for alpha in exponents} and all(len(rows) == total_rows for rows in alpha_rows.values()), [sorted(alpha_rows), [len(rows) for rows in alpha_rows.values()]], f"all exponents across {total_rows} rows", "sublinear counting")
    alpha_aggregates: dict[str, dict[str, float]] = {}
    for alpha_label, rows in alpha_rows.items():
        slacks = [row["infinite_zeta_bound"] - row["finite_trace_bound"] for row in rows]
        check(f"alpha={alpha_label} aggregate", min(row["counting_constant"] for row in rows) > 0.0 and min(row["finite_trace_bound"] - trace for row, trace in zip(rows, traces)) >= -tolerance and min(slacks) >= -tolerance, [min(row["counting_constant"] for row in rows), min(row["finite_trace_bound"] - trace for row, trace in zip(rows, traces)), min(slacks)], f"positive constants and nonnegative bounds +/- {tolerance}", "sublinear zeta")
        alpha_aggregates[alpha_label] = {
            "alpha": rows[0]["alpha"],
            "minimum_counting_constant": min(row["counting_constant"] for row in rows),
            "maximum_counting_constant": max(row["counting_constant"] for row in rows),
            "minimum_finite_trace_bound": min(row["finite_trace_bound"] for row in rows),
            "maximum_finite_trace_bound": max(row["finite_trace_bound"] for row in rows),
            "minimum_infinite_zeta_bound": min(row["infinite_zeta_bound"] for row in rows),
            "maximum_infinite_zeta_bound": max(row["infinite_zeta_bound"] for row in rows),
            "maximum_envelope_abs_residual": max(abs(row["envelope_residual"]) for row in rows),
        }
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
        "minimum_mode_constant": min(mode_constants),
        "maximum_mode_constant": max(mode_constants),
        "minimum_zeta_bound": min(zeta_bounds),
        "maximum_zeta_bound": max(zeta_bounds),
        "minimum_zeta_infinite_bound": min(zeta_infinite_bounds),
        "maximum_zeta_infinite_bound": max(zeta_infinite_bounds),
        "maximum_mode_envelope_abs_residual": max(abs(value) for value in mode_envelope_residuals),
        "alpha_profiles": alpha_aggregates,
        "pair_count": sorted(set(pair_counts)),
        "cutoff_dimensions": [dimension for _volume, dimension in pairs],
        "system_profiles": profiles,
        "finite_mode_ordering_closed": True,
        "finite_sublinear_counting_closed": True,
        "finite_zeta_tail_bound_closed": True,
        "finite_likelihood_row_coverage_closed": True,
        "cutoff_independent_exponent_constant_closed": False,
        "volume_independent_exponent_constant_closed": False,
        "phase_uniform_exponent_constant_closed": False,
        "exhaustion_uniform_exponent_constant_closed": False,
        "common_core_closed": False,
        "common_alpha_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False
    }
    payload = {"schema": "tect/pre-a-r411-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-411", "exploration_id": "EXP-001256", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    r408.r407.atomic_json(output, payload)
    print(f"R-411 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} alpha={len(exponents)} c2=[{min(mode_constants):.6g},{max(mode_constants):.6g}] trace=[{min(traces):.6g},{max(traces):.6g}]")
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
