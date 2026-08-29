#!/usr/bin/env python3
"""Independent reconstruction of the R-412 mixed IR/UV mode envelope."""

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
SLUG = "pre_a_cp1_st8_q3lock_spectral_counting_mixed"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spectral-counting-mixed-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_canonical_path_resistance_independent as r407i  # noqa: E402
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
    if eigenvalues.size < 2 or not np.all(np.isfinite(eigenvalues)) or float(eigenvalues[0]) < -numerical_tolerance:
        raise AssertionError("normalized Laplacian is not positive semidefinite")
    spectral_zero_threshold = max(eigen_floor, numerical_tolerance)
    positive = eigenvalues > spectral_zero_threshold
    if int(np.count_nonzero(positive)) != pi.size - 1:
        raise AssertionError("normalized Laplacian is disconnected at trace floor")
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
        raise AssertionError("raw Laplacian is disconnected at trace floor")
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
        "heat_trace_integral": float(np.sum(inverse_values[positive])),
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


def mixed_envelope_data(positive_eigenvalues: np.ndarray, exponents: list[float]) -> dict[str, dict[str, Any]]:
    """Enumerate every two-regime exponent pair and every interior split."""
    values = np.asarray(positive_eigenvalues, dtype=float)
    if values.ndim != 1 or values.size < 2 or not np.all(np.isfinite(values)) or np.any(values <= 0.0):
        raise AssertionError("invalid positive spectrum for mixed envelope")
    indices = np.arange(1, values.size + 1, dtype=float)
    profiles: dict[str, dict[str, Any]] = {}
    for alpha_ir in exponents:
        if not math.isfinite(alpha_ir) or not 0.0 < alpha_ir < 1.0:
            raise AssertionError(f"IR exponent must lie in (0,1): {alpha_ir}")
        ir_power = 1.0 / alpha_ir
        ir_label = str(alpha_ir).rstrip("0").rstrip(".")
        for alpha_uv in exponents:
            if not math.isfinite(alpha_uv) or not 0.0 < alpha_uv < 1.0:
                raise AssertionError(f"UV exponent must lie in (0,1): {alpha_uv}")
            uv_power = 1.0 / alpha_uv
            uv_label = str(alpha_uv).rstrip("0").rstrip(".")
            for split in range(1, values.size):
                head_indices = indices[:split]
                head_values = values[:split]
                tail_indices = indices[split:]
                tail_values = values[split:]
                ir_constant = float(np.max(head_indices / np.power(head_values, alpha_ir)))
                uv_constant = float(np.max(tail_indices / np.power(tail_values, alpha_uv)))
                ir_sum = float(np.sum(np.power(head_indices, -ir_power)))
                uv_sum = float(np.sum(np.power(tail_indices, -uv_power)))
                uv_tail = float(values.size ** (1.0 - uv_power) / (uv_power - 1.0))
                ir_bound = float(ir_constant ** ir_power * ir_sum)
                uv_bound = float(uv_constant ** uv_power * uv_sum)
                uv_infinite_bound = float(uv_constant ** uv_power * (uv_sum + uv_tail))
                ir_lower = np.power(head_indices / ir_constant, ir_power)
                uv_lower = np.power(tail_indices / uv_constant, uv_power)
                envelope_residual = float(min(np.min(head_values - ir_lower), np.min(tail_values - uv_lower)))
                if not all(math.isfinite(item) and item > 0.0 for item in (ir_constant, uv_constant, ir_sum, uv_sum, uv_tail, ir_bound, uv_bound, uv_infinite_bound)):
                    raise AssertionError("invalid mixed spectral envelope")
                key = f"ir={ir_label};uv={uv_label};split={split}"
                profiles[key] = {
                    "alpha_ir": float(alpha_ir),
                    "alpha_uv": float(alpha_uv),
                    "split": int(split),
                    "ir_counting_constant": ir_constant,
                    "uv_counting_constant": uv_constant,
                    "ir_finite_zeta_sum": ir_sum,
                    "uv_finite_zeta_sum": uv_sum,
                    "uv_integral_tail_bound": uv_tail,
                    "ir_trace_bound": ir_bound,
                    "uv_trace_bound": uv_bound,
                    "finite_trace_bound": ir_bound + uv_bound,
                    "infinite_zeta_bound": ir_bound + uv_infinite_bound,
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

    check("identity", manifest["result_id"] == "R-412" and manifest["exploration_id"] == "EXP-001257" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-412/EXP-001257/false", "provenance")
    finite_flags = ("finite_mode_ordering_closed", "finite_mixed_counting_closed", "finite_mixed_zeta_tail_bound_closed", "finite_likelihood_row_coverage_closed")
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
    mixed_selected_rows: list[dict[str, Any]] = []
    mixed_finite_bounds: list[float] = []
    mixed_infinite_bounds: list[float] = []
    mixed_residuals: list[float] = []
    mixed_profile_rows: dict[str, list[dict[str, float]]] = {}
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
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_resistance_average": float("inf"), "maximum_resistance_average": 0.0, "minimum_trace_inverse": float("inf"), "maximum_trace_inverse": 0.0, "minimum_projector_trace": float("inf"), "maximum_projector_trace": 0.0, "maximum_identity_abs_residual": 0.0, "maximum_transformed_identity_abs_residual": 0.0, "maximum_projector_identity_abs_residual": 0.0, "minimum_positive_normalized_eigenvalue": float("inf"), "maximum_effective_resistance": 0.0, "minimum_mode_constant": float("inf"), "maximum_mode_constant": 0.0, "minimum_zeta_bound": float("inf"), "maximum_zeta_bound": 0.0, "maximum_mode_envelope_residual": 0.0, "alpha_profiles": {str(alpha).rstrip("0").rstrip("."): {"minimum_counting_constant": float("inf"), "maximum_counting_constant": 0.0, "minimum_finite_trace_bound": float("inf"), "maximum_finite_trace_bound": 0.0, "minimum_infinite_zeta_bound": float("inf"), "maximum_infinite_zeta_bound": 0.0, "maximum_envelope_abs_residual": 0.0} for alpha in exponents}, "mixed_selected_min_finite_bound": float("inf"), "mixed_selected_max_finite_bound": 0.0, "mixed_selected_min_infinite_bound": float("inf"), "mixed_selected_max_infinite_bound": 0.0, "mixed_selected_keys": {}, "pair_count": 0}
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
                                    for conditional, _likelihood in r407i.conditional_rows(reference, sample, order_sites, dimension, floor):
                                        _gap, laplacian, _conductance = r407i.intrinsic_graph(conditional, momentum, chi)
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
                                        mixed_data = mixed_envelope_data(np.asarray(data["ordered_positive_normalized_eigenvalues"], dtype=float), exponents)
                                        expected_mixed_candidates = len(exponents) * len(exponents) * (dimension - 2)
                                        check("mixed candidate coverage", len(mixed_data) == expected_mixed_candidates, len(mixed_data), expected_mixed_candidates, "mixed counting")
                                        mixed_finite_slacks = [envelope["finite_trace_bound"] - data["trace_inverse"] for envelope in mixed_data.values()]
                                        mixed_tail_slacks = [envelope["infinite_zeta_bound"] - envelope["finite_trace_bound"] for envelope in mixed_data.values()]
                                        mixed_candidate_residuals = [envelope["envelope_residual"] for envelope in mixed_data.values()]
                                        check("mixed finite envelopes", min(mixed_finite_slacks) >= -tolerance, [min(mixed_finite_slacks), max(mixed_finite_slacks)], f">= -{tolerance}", "mixed counting")
                                        check("mixed UV tail comparisons", min(mixed_tail_slacks) >= -tolerance, [min(mixed_tail_slacks), max(mixed_tail_slacks)], f">= -{tolerance}", "mixed zeta")
                                        check("mixed segment residuals", min(mixed_candidate_residuals) >= -tolerance, [min(mixed_candidate_residuals), max(mixed_candidate_residuals)], f">= -{tolerance}", "mixed counting")
                                        best_key, best = min(mixed_data.items(), key=lambda item: (item[1]["infinite_zeta_bound"], item[1]["finite_trace_bound"], item[0]))
                                        mixed_selected_rows.append({"dimension": dimension, "key": best_key, **best})
                                        mixed_finite_bounds.append(best["finite_trace_bound"])
                                        mixed_infinite_bounds.append(best["infinite_zeta_bound"])
                                        mixed_residuals.extend(mixed_candidate_residuals)
                                        aggregate = mixed_profile_rows.setdefault(best_key, [])
                                        aggregate.append({"finite_trace_bound": best["finite_trace_bound"], "infinite_zeta_bound": best["infinite_zeta_bound"], "ir_counting_constant": best["ir_counting_constant"], "uv_counting_constant": best["uv_counting_constant"], "envelope_residual": best["envelope_residual"]})
                                        profile["mixed_selected_min_finite_bound"] = min(profile["mixed_selected_min_finite_bound"], best["finite_trace_bound"])
                                        profile["mixed_selected_max_finite_bound"] = max(profile["mixed_selected_max_finite_bound"], best["finite_trace_bound"])
                                        profile["mixed_selected_min_infinite_bound"] = min(profile["mixed_selected_min_infinite_bound"], best["infinite_zeta_bound"])
                                        profile["mixed_selected_max_infinite_bound"] = max(profile["mixed_selected_max_infinite_bound"], best["infinite_zeta_bound"])
                                        profile["mixed_selected_keys"][best_key] = profile["mixed_selected_keys"].get(best_key, 0) + 1
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
        check(f"V={volume} d={dimension} profile", profile["row_count"] > profile["context_count"] and profile["minimum_resistance_average"] > 0.0 and profile["minimum_mode_constant"] > 0.0 and profile["mixed_selected_min_finite_bound"] > 0.0, [profile["row_count"], profile["context_count"], profile["minimum_resistance_average"], profile["minimum_mode_constant"], profile["mixed_selected_min_finite_bound"]], "positive trace and mixed envelope", "coverage")
        profiles[f"V={volume}/d={dimension}"] = profile

    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("trace identities nonnegative", all(math.isfinite(value) and value > 0.0 for value in traces + averages + projector_traces), [min(averages), max(averages), min(traces), max(traces)], ">0 finite", "trace identity")
    check("mode constants positive", all(math.isfinite(value) and value > 0.0 for value in mode_constants), [min(mode_constants), max(mode_constants)], ">0 finite", "mode counting")
    check("zeta bounds finite", all(math.isfinite(value) and value > 0.0 for value in zeta_bounds + zeta_infinite_bounds), [min(zeta_bounds), max(zeta_bounds), min(zeta_infinite_bounds), max(zeta_infinite_bounds)], ">0 finite", "zeta envelope")
    zeta_slacks = [bound - trace for bound, trace in zip(zeta_bounds, traces)]
    check("zeta slack nonnegative", min(zeta_slacks) >= -tolerance, [min(zeta_slacks), max(zeta_slacks)], f">= -{tolerance}", "zeta envelope")
    check("sublinear exponent grid", set(alpha_rows) == {str(alpha).rstrip("0").rstrip(".") for alpha in exponents} and all(len(rows) == total_rows for rows in alpha_rows.values()), [sorted(alpha_rows), [len(rows) for rows in alpha_rows.values()]], f"all exponents across {total_rows} rows", "sublinear counting")
    alpha_aggregates: dict[str, dict[str, float]] = {}
    for alpha_label, rows in alpha_rows.items():
        slacks = [row["infinite_zeta_bound"] - row["finite_trace_bound"] for row in rows]
        trace_slacks = [row["finite_trace_bound"] - trace for row, trace in zip(rows, traces)]
        check(f"alpha={alpha_label} aggregate", min(row["counting_constant"] for row in rows) > 0.0 and min(trace_slacks) >= -tolerance and min(slacks) >= -tolerance, [min(row["counting_constant"] for row in rows), min(trace_slacks), min(slacks)], f"positive constants and nonnegative bounds +/- {tolerance}", "sublinear zeta")
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
    check("mixed row coverage", len(mixed_selected_rows) == total_rows and len(mixed_finite_bounds) == total_rows and len(mixed_infinite_bounds) == total_rows, [len(mixed_selected_rows), len(mixed_finite_bounds), len(mixed_infinite_bounds)], f"one selected mixed envelope per {total_rows} rows", "mixed counting")
    check("mixed selected trace bounds", all(bound > 0.0 for bound in mixed_finite_bounds) and min(bound - trace for bound, trace in zip(mixed_finite_bounds, traces)) >= -tolerance and min(bound - finite for bound, finite in zip(mixed_infinite_bounds, mixed_finite_bounds)) >= -tolerance, [min(mixed_finite_bounds), max(mixed_finite_bounds), min(mixed_infinite_bounds), max(mixed_infinite_bounds)], f"positive and ordered bounds +/- {tolerance}", "mixed zeta")
    mixed_aggregates: dict[str, dict[str, Any]] = {}
    for key, rows in mixed_profile_rows.items():
        mixed_aggregates[key] = {
            "count": len(rows),
            "minimum_ir_counting_constant": min(row["ir_counting_constant"] for row in rows),
            "maximum_ir_counting_constant": max(row["ir_counting_constant"] for row in rows),
            "minimum_uv_counting_constant": min(row["uv_counting_constant"] for row in rows),
            "maximum_uv_counting_constant": max(row["uv_counting_constant"] for row in rows),
            "minimum_finite_trace_bound": min(row["finite_trace_bound"] for row in rows),
            "maximum_finite_trace_bound": max(row["finite_trace_bound"] for row in rows),
            "minimum_infinite_zeta_bound": min(row["infinite_zeta_bound"] for row in rows),
            "maximum_infinite_zeta_bound": max(row["infinite_zeta_bound"] for row in rows),
            "maximum_envelope_abs_residual": max(abs(row["envelope_residual"]) for row in rows),
        }
    check("mixed residuals bounded", min(mixed_residuals) >= -tolerance, [min(mixed_residuals), max(mixed_residuals)], f">= -{tolerance}", "mixed counting")
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
        "mixed_selected_min_finite_bound": min(mixed_finite_bounds),
        "mixed_selected_max_finite_bound": max(mixed_finite_bounds),
        "mixed_selected_min_infinite_bound": min(mixed_infinite_bounds),
        "mixed_selected_max_infinite_bound": max(mixed_infinite_bounds),
        "mixed_selected_min_trace_slack": min(bound - trace for bound, trace in zip(mixed_finite_bounds, traces)),
        "mixed_selected_min_tail_slack": min(bound - finite for bound, finite in zip(mixed_infinite_bounds, mixed_finite_bounds)),
        "mixed_candidate_count_per_row": len(exponents) * len(exponents) * (max(dimension for _volume, dimension in pairs) - 2),
        "mixed_selected_key_histogram": {key: sum(1 for item in mixed_selected_rows if item["key"] == key) for key in sorted({item["key"] for item in mixed_selected_rows})},
        "mixed_aggregates": mixed_aggregates,
        "pair_count": sorted(set(pair_counts)),
        "cutoff_dimensions": [dimension for _volume, dimension in pairs],
        "system_profiles": profiles,
        "finite_mode_ordering_closed": True,
        "finite_mixed_counting_closed": True,
        "finite_mixed_zeta_tail_bound_closed": True,
        "finite_likelihood_row_coverage_closed": True,
        "cutoff_independent_mixed_constant_closed": False,
        "volume_independent_mixed_constant_closed": False,
        "phase_uniform_mixed_constant_closed": False,
        "exhaustion_uniform_mixed_constant_closed": False,
        "common_core_closed": False,
        "common_split_rule_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False
    }
    payload = {"schema": "tect/pre-a-r412-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-412", "exploration_id": "EXP-001257", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    r407i.atomic_json(output, payload)
    print(f"R-412 INDEPENDENT PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} mixed_candidates={len(exponents) * len(exponents)} selected_bounds=[{min(mixed_finite_bounds):.6g},{max(mixed_finite_bounds):.6g}] trace=[{min(traces):.6g},{max(traces):.6g}]")
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
