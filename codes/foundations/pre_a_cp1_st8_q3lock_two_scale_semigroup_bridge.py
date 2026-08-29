#!/usr/bin/env python3
"""Primary finite audit of the R-414 two-scale semigroup bridge.

The R-413 mixed heat envelope is reorganized into a short-time power budget
and a late-time exponential budget.  The calculation is finite and
claim-nonbearing: the first positive eigenvalue and the split-time heat value
are measured row by row, not promoted to uniform constants.
"""

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
SLUG = "pre_a_cp1_st8_q3lock_two_scale_semigroup_bridge"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-scale-semigroup-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_spectral_counting_mixed as r412  # noqa: E402
import pre_a_cp1_st8_q3lock_effective_resistance as r408  # noqa: E402
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def semigroup_data(values: np.ndarray, profile: dict[str, Any], heat_times: np.ndarray, split_time: float) -> dict[str, Any]:
    """Compute the finite two-scale heat and Green-trace quantities."""
    spectrum = np.asarray(values, dtype=float)
    times = np.asarray(heat_times, dtype=float)
    if spectrum.ndim != 1 or spectrum.size < 2 or not np.all(np.isfinite(spectrum)) or np.any(spectrum <= 0.0):
        raise AssertionError("invalid positive spectrum")
    if np.any(np.diff(spectrum) < 0.0):
        raise AssertionError("spectrum must be ordered")
    if times.ndim != 1 or times.size == 0 or not np.all(np.isfinite(times)) or np.any(times <= 0.0) or np.any(np.diff(times) < 0.0):
        raise AssertionError("heat times must be positive and ordered")
    if not math.isfinite(split_time) or split_time <= 0.0:
        raise AssertionError("split time must be positive")
    split = int(profile["split"])
    alpha = float(profile["alpha_uv"])
    uv_constant = float(profile["uv_counting_constant"])
    if not 1 <= split < spectrum.size or not 0.0 < alpha < 1.0:
        raise AssertionError("invalid interior split or UV exponent")
    if not math.isfinite(uv_constant) or uv_constant <= 0.0:
        raise AssertionError("invalid UV counting constant")
    gap = float(spectrum[0])
    heat = np.asarray([float(np.sum(np.exp(-float(time) * spectrum))) for time in times], dtype=float)
    heat_tau = float(np.sum(np.exp(-split_time * spectrum)))
    late_actual = float(np.sum(np.exp(-split_time * spectrum) / spectrum))
    short_actual = float(np.sum(-np.expm1(-split_time * spectrum) / spectrum))
    trace_inverse = float(np.sum(1.0 / spectrum))
    uv_factor = uv_constant * alpha * math.gamma(alpha)
    power_constant = split * split_time**alpha + uv_factor
    short_power_budget = power_constant * split_time ** (1.0 - alpha) / (1.0 - alpha)
    late_semigroup_bound = heat_tau / gap
    green_bound = short_power_budget + late_semigroup_bound
    short_power_values = power_constant * np.power(times, -alpha)
    late_exponential_values = heat_tau * np.exp(-gap * (times - split_time))
    if not all(math.isfinite(item) for item in heat.tolist() + short_power_values.tolist() + late_exponential_values.tolist() + [gap, heat_tau, late_actual, short_actual, trace_inverse, uv_factor, power_constant, short_power_budget, late_semigroup_bound, green_bound]):
        raise AssertionError("nonfinite semigroup quantity")
    return {
        "actual_heat": heat,
        "heat_at_split": heat_tau,
        "first_positive_gap": gap,
        "short_power_constant": power_constant,
        "uv_integral_factor": uv_factor,
        "short_power_bound_values": short_power_values,
        "late_exponential_bound_values": late_exponential_values,
        "short_actual": short_actual,
        "late_actual": late_actual,
        "trace_inverse": trace_inverse,
        "short_power_budget": short_power_budget,
        "late_semigroup_bound": late_semigroup_bound,
        "green_bound": green_bound,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_floor"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    exponents = [float(Fraction(value)) for value in fixture["counting_exponents"]]
    heat_times = np.asarray([float(Fraction(value)) for value in fixture["heat_time_values"]], dtype=float)
    split_time = float(Fraction(fixture["semigroup_split_time"]))
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
        if len(checks) < 280:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-414" and manifest["exploration_id"] == "EXP-001259" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-414/EXP-001259/false", "provenance")
    finite_flags = ("finite_two_scale_envelope_closed", "finite_short_time_power_budget_closed", "finite_late_time_semigroup_budget_closed", "finite_green_trace_criterion_closed", "finite_likelihood_row_coverage_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite two-scale criterion only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("heat grid", heat_times.size >= 4 and float(np.min(heat_times)) > 0.0 and np.all(np.diff(heat_times) >= 0.0) and float(np.min(heat_times)) < split_time < float(np.max(heat_times)), heat_times.tolist() + [split_time], "positive ordered times straddling split", "fixture")

    traces: list[float] = []
    gaps: list[float] = []
    heat_at_split_values: list[float] = []
    short_power_slacks: list[float] = []
    late_exponential_slacks: list[float] = []
    short_budget_slacks: list[float] = []
    late_budget_slacks: list[float] = []
    green_slacks: list[float] = []
    mellin_residuals: list[float] = []
    heat_values: list[float] = []
    heat_increases: list[float] = []
    selected_bounds: list[float] = []
    selected_keys: list[str] = []
    candidate_counts: list[int] = []
    profiles: dict[str, dict[str, Any]] = {}
    total_contexts = 0
    total_rows = 0

    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension ** volume, dimension ** volume), basis.shape, (dimension ** volume, dimension ** volume), "coordinates")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        generator_cache = {support: sum((q_ops[site] for site in support), np.zeros_like(q_ops[0])) for support in supports}
        prefixes_by_key = {(order_name, history_sign): r399.all_prefixes(terms, order, history_sign, delta, hbar) for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms))))) ) for history_sign in history_signs}
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_trace": float("inf"), "maximum_trace": 0.0, "minimum_gap": float("inf"), "maximum_gap": 0.0, "minimum_heat_at_split": float("inf"), "maximum_heat_at_split": 0.0, "minimum_short_power_slack": float("inf"), "minimum_late_exponential_slack": float("inf"), "minimum_short_budget_slack": float("inf"), "minimum_late_budget_slack": float("inf"), "minimum_green_slack": float("inf"), "maximum_mellin_residual": 0.0, "maximum_heat_value": 0.0}
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
                                        trace_data = r412.trace_identity_data(conditional, laplacian, eigen_floor, tolerance)
                                        values = np.asarray(trace_data["ordered_positive_normalized_eigenvalues"], dtype=float)
                                        mixed = r412.mixed_envelope_data(values, exponents)
                                        actual = semigroup_data(values, next(iter(mixed.values())), heat_times, split_time)
                                        heat = actual["actual_heat"]
                                        mellin_residual = actual["trace_inverse"] - actual["short_actual"] - actual["late_actual"]
                                        check("Mellin decomposition", abs(mellin_residual) <= tolerance, mellin_residual, f"abs <= {tolerance}", "Mellin")
                                        check("late remainder nonnegative", actual["late_actual"] >= -tolerance, actual["late_actual"], f">=-{tolerance}", "Mellin")
                                        heat_differences = np.diff(heat)
                                        check("heat monotone", float(np.max(heat_differences, initial=-math.inf)) <= tolerance, heat_differences.tolist(), f"max <= {tolerance}", "heat trace")
                                        short_mask = heat_times <= split_time + tolerance
                                        late_mask = heat_times >= split_time - tolerance
                                        min_short_pointwise = float("inf")
                                        min_late_pointwise = float("inf")
                                        min_short_budget = float("inf")
                                        min_late_budget = float("inf")
                                        min_green = float("inf")
                                        for key, candidate in mixed.items():
                                            data = semigroup_data(values, candidate, heat_times, split_time)
                                            min_short_pointwise = min(min_short_pointwise, float(np.min(data["short_power_bound_values"][short_mask] - heat[short_mask])))
                                            min_late_pointwise = min(min_late_pointwise, float(np.min(data["late_exponential_bound_values"][late_mask] - heat[late_mask])))
                                            min_short_budget = min(min_short_budget, data["short_power_budget"] - data["short_actual"])
                                            min_late_budget = min(min_late_budget, data["late_semigroup_bound"] - data["late_actual"])
                                            min_green = min(min_green, data["green_bound"] - data["trace_inverse"])
                                        check("short-time power envelopes", min_short_pointwise >= -tolerance, min_short_pointwise, f">=-{tolerance}", "short UV budget")
                                        check("late-time exponential envelopes", min_late_pointwise >= -tolerance, min_late_pointwise, f">=-{tolerance}", "late IR budget")
                                        check("short-time power budget", min_short_budget >= -tolerance, min_short_budget, f">=-{tolerance}", "short UV budget")
                                        check("late-time semigroup budget", min_late_budget >= -tolerance, min_late_budget, f">=-{tolerance}", "late IR budget")
                                        check("Green trace criterion", min_green >= -tolerance, min_green, f">=-{tolerance}", "two-scale criterion")
                                        selected_key, selected_profile = min(mixed.items(), key=lambda item: (semigroup_data(values, item[1], heat_times, split_time)["green_bound"], item[0]))
                                        selected = semigroup_data(values, selected_profile, heat_times, split_time)
                                        check("selected criterion", selected["green_bound"] >= selected["trace_inverse"] - tolerance and selected["short_power_budget"] >= selected["short_actual"] - tolerance and selected["late_semigroup_bound"] >= selected["late_actual"] - tolerance, [selected["green_bound"], selected["trace_inverse"], selected["short_power_budget"], selected["short_actual"], selected["late_semigroup_bound"], selected["late_actual"]], f"finite bounds within {tolerance}", "two-scale criterion")
                                        traces.append(selected["trace_inverse"])
                                        gaps.append(selected["first_positive_gap"])
                                        heat_at_split_values.append(selected["heat_at_split"])
                                        short_power_slacks.append(min_short_pointwise)
                                        late_exponential_slacks.append(min_late_pointwise)
                                        short_budget_slacks.append(min_short_budget)
                                        late_budget_slacks.append(min_late_budget)
                                        green_slacks.append(min_green)
                                        mellin_residuals.append(mellin_residual)
                                        heat_values.extend(float(value) for value in heat)
                                        heat_increases.extend(float(value) for value in heat_differences)
                                        selected_bounds.append(selected["green_bound"])
                                        selected_keys.append(selected_key)
                                        candidate_counts.append(len(mixed))
                                        total_rows += 1
                                        profile["row_count"] += 1
                                        profile["minimum_trace"] = min(profile["minimum_trace"], selected["trace_inverse"])
                                        profile["maximum_trace"] = max(profile["maximum_trace"], selected["trace_inverse"])
                                        profile["minimum_gap"] = min(profile["minimum_gap"], selected["first_positive_gap"])
                                        profile["maximum_gap"] = max(profile["maximum_gap"], selected["first_positive_gap"])
                                        profile["minimum_heat_at_split"] = min(profile["minimum_heat_at_split"], selected["heat_at_split"])
                                        profile["maximum_heat_at_split"] = max(profile["maximum_heat_at_split"], selected["heat_at_split"])
                                        profile["minimum_short_power_slack"] = min(profile["minimum_short_power_slack"], min_short_pointwise)
                                        profile["minimum_late_exponential_slack"] = min(profile["minimum_late_exponential_slack"], min_late_pointwise)
                                        profile["minimum_short_budget_slack"] = min(profile["minimum_short_budget_slack"], min_short_budget)
                                        profile["minimum_late_budget_slack"] = min(profile["minimum_late_budget_slack"], min_late_budget)
                                        profile["minimum_green_slack"] = min(profile["minimum_green_slack"], min_green)
                                        profile["maximum_mellin_residual"] = max(profile["maximum_mellin_residual"], abs(mellin_residual))
                                        profile["maximum_heat_value"] = max(profile["maximum_heat_value"], float(np.max(heat)))
                                    profile["context_count"] += 1
                                    total_contexts += 1
        check(f"V={volume} d={dimension} profile", profile["row_count"] > profile["context_count"] and profile["minimum_gap"] > 0.0 and profile["minimum_green_slack"] >= -tolerance, [profile["row_count"], profile["context_count"], profile["minimum_gap"], profile["minimum_green_slack"]], "positive finite semigroup profile", "coverage")
        profiles[f"V={volume}/d={dimension}"] = profile

    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts > 0 and total_rows > total_contexts, [total_contexts, total_rows], "positive rows beyond contexts", "coverage")
    check("candidate count coverage", set(candidate_counts) == {len(exponents) * len(exponents) * (dimension - 2) for _volume, dimension in pairs}, sorted(set(candidate_counts)), "all mixed profiles", "coverage")
    check("trace positivity", all(math.isfinite(value) and value > 0.0 for value in traces), [min(traces), max(traces)], ">0 finite", "Mellin")
    check("IR gap positivity", all(math.isfinite(value) and value > 0.0 for value in gaps), [min(gaps), max(gaps)], ">0 finite", "late IR budget")
    check("Mellin aggregate", min(abs(value) for value in mellin_residuals) >= 0.0 and max(abs(value) for value in mellin_residuals) <= tolerance, max(abs(value) for value in mellin_residuals), f"<= {tolerance}", "Mellin")
    check("heat monotonicity aggregate", max(heat_increases) <= tolerance, max(heat_increases), f"<= {tolerance}", "heat trace")
    check("two-scale aggregate", min(short_power_slacks) >= -tolerance and min(late_exponential_slacks) >= -tolerance and min(short_budget_slacks) >= -tolerance and min(late_budget_slacks) >= -tolerance and min(green_slacks) >= -tolerance, [min(short_power_slacks), min(late_exponential_slacks), min(short_budget_slacks), min(late_budget_slacks), min(green_slacks)], f">=-{tolerance}", "two-scale criterion")
    derived = {
        "system_count": len(pairs),
        "context_count": total_contexts,
        "comparison_row_count": total_rows,
        "heat_time_values": [float(value) for value in heat_times],
        "semigroup_split_time": split_time,
        "minimum_trace_inverse": min(traces),
        "maximum_trace_inverse": max(traces),
        "minimum_first_positive_gap": min(gaps),
        "maximum_first_positive_gap": max(gaps),
        "minimum_heat_at_split": min(heat_at_split_values),
        "maximum_heat_at_split": max(heat_at_split_values),
        "minimum_short_power_slack": min(short_power_slacks),
        "minimum_late_exponential_slack": min(late_exponential_slacks),
        "minimum_short_budget_slack": min(short_budget_slacks),
        "minimum_late_budget_slack": min(late_budget_slacks),
        "minimum_green_trace_slack": min(green_slacks),
        "maximum_mellin_identity_abs_residual": max(abs(value) for value in mellin_residuals),
        "minimum_heat_value": min(heat_values),
        "maximum_heat_value": max(heat_values),
        "maximum_heat_increase": max(heat_increases),
        "minimum_selected_green_bound": min(selected_bounds),
        "maximum_selected_green_bound": max(selected_bounds),
        "candidate_count_per_row": sorted(set(candidate_counts)),
        "selected_key_histogram": {key: selected_keys.count(key) for key in sorted(set(selected_keys))},
        "system_profiles": profiles,
        "finite_two_scale_envelope_closed": True,
        "finite_short_time_power_budget_closed": True,
        "finite_late_time_semigroup_budget_closed": True,
        "finite_green_trace_criterion_closed": True,
        "finite_likelihood_row_coverage_closed": True,
        "cutoff_independent_uv_coefficient_closed": False,
        "volume_independent_ir_gap_closed": False,
        "phase_uniform_semigroup_closed": False,
        "exhaustion_uniform_semigroup_closed": False,
        "common_core_closed": False,
        "common_split_rule_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r414-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-414", "exploration_id": "EXP-001259", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-414 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} heat_times={len(heat_times)} candidates={sorted(set(candidate_counts))} gap=[{min(gaps):.6g},{max(gaps):.6g}] green_slack={min(green_slacks):.6g}")
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
