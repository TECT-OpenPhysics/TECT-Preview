#!/usr/bin/env python3
"""Independent reconstruction of the R-413 finite Mellin heat budget.

This lane rebuilds the oscillator/Gibbs/conditional graph through the
non-importing R-412 implementation and evaluates the heat formulas with
plain Python sums, rather than importing the R-413 primary module.
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
SLUG = "pre_a_cp1_st8_q3lock_heat_trace_mellin_bridge"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-heat-trace-mellin-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_spectral_counting_mixed_independent as r412i  # noqa: E402
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


def heat_data(values: np.ndarray, profile: dict[str, Any], times: list[float], split_time: float) -> dict[str, Any]:
    """Plain-loop version of the R-413 heat and Mellin formulas."""
    spectrum = [float(item) for item in np.asarray(values, dtype=float).tolist()]
    if len(spectrum) < 2 or any((not math.isfinite(item) or item <= 0.0) for item in spectrum):
        raise AssertionError("invalid spectrum")
    if any((not math.isfinite(item) or item <= 0.0) for item in times) or any(right < left for left, right in zip(times, times[1:])):
        raise AssertionError("invalid heat times")
    split = int(profile["split"])
    if split < 1 or split >= len(spectrum):
        raise AssertionError("non-interior split")
    alpha_ir = float(profile["alpha_ir"])
    alpha_uv = float(profile["alpha_uv"])
    if not 0.0 < alpha_ir < 1.0 or not 0.0 < alpha_uv < 1.0:
        raise AssertionError("sublinear exponents required")
    ir_constant = float(profile["ir_counting_constant"])
    uv_constant = float(profile["uv_counting_constant"])
    ir_lower = [((index + 1.0) / ir_constant) ** (1.0 / alpha_ir) for index in range(split)]
    uv_lower = [((index + split + 1.0) / uv_constant) ** (1.0 / alpha_uv) for index in range(len(spectrum) - split)]
    actual_heat = [sum(math.exp(-time * value) for value in spectrum) for time in times]
    finite_head_heat = [sum(math.exp(-time * value) for value in ir_lower) for time in times]
    finite_tail_heat = [sum(math.exp(-time * value) for value in uv_lower) for time in times]
    continuous_constant = uv_constant * alpha_uv * math.gamma(alpha_uv)
    continuous_heat_bound = [head + continuous_constant * time ** (-alpha_uv) for head, time in zip(finite_head_heat, times)]
    finite_heat_bound = [head + tail for head, tail in zip(finite_head_heat, finite_tail_heat)]
    short_actual = sum(-math.expm1(-split_time * value) / value for value in spectrum)
    late_actual = sum(math.exp(-split_time * value) / value for value in spectrum)
    short_head = sum(-math.expm1(-split_time * value) / value for value in ir_lower)
    short_uv = continuous_constant * split_time ** (1.0 - alpha_uv) / (1.0 - alpha_uv)
    late_bound = sum(math.exp(-split_time * value) / value for value in ir_lower + uv_lower)
    if not all(math.isfinite(item) for item in actual_heat + finite_heat_bound + continuous_heat_bound + [short_actual, late_actual, short_head, short_uv, late_bound]):
        raise AssertionError("nonfinite heat result")
    return {
        "actual_heat": actual_heat,
        "finite_heat_bound": finite_heat_bound,
        "continuous_heat_bound": continuous_heat_bound,
        "short_actual": short_actual,
        "late_actual": late_actual,
        "short_bound": short_head + short_uv,
        "late_bound": late_bound,
        "uv_integral_constant": continuous_constant,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_floor"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    exponents = [float(Fraction(value)) for value in fixture["counting_exponents"]]
    heat_times = [float(Fraction(value)) for value in fixture["heat_time_values"]]
    split_time = float(Fraction(fixture["mellin_split_time"]))
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
        if len(checks) < 260:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-413" and manifest["exploration_id"] == "EXP-001258" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-413/EXP-001258/false", "provenance")
    finite_flags = ("finite_mellin_identity_closed", "finite_mixed_heat_envelope_closed", "finite_short_time_uv_budget_closed", "finite_likelihood_row_coverage_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("heat grid", len(heat_times) >= 4 and heat_times[0] > 0.0 and all(right >= left for left, right in zip(heat_times, heat_times[1:])) and split_time > 0.0, heat_times + [split_time], "ordered positive times", "fixture")

    profiles: dict[str, dict[str, Any]] = {}
    traces: list[float] = []
    short_actuals: list[float] = []
    late_actuals: list[float] = []
    mellin_residuals: list[float] = []
    heat_values: list[float] = []
    heat_increases: list[float] = []
    candidate_heat_slacks: list[float] = []
    candidate_continuous_slacks: list[float] = []
    candidate_short_slacks: list[float] = []
    candidate_late_slacks: list[float] = []
    selected_short_bounds: list[float] = []
    selected_late_bounds: list[float] = []
    selected_keys: list[str] = []
    candidate_counts: list[int] = []
    total_contexts = 0
    total_rows = 0

    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r412i.r407i.model(volume, dimension, fixture)
        basis = r412i.r407i.coordinate_basis(dimension, volume)
        _levels, momentum = r412i.r407i.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension ** volume, dimension ** volume), basis.shape, (dimension ** volume, dimension ** volume), "coordinates")
        states = {beta: r412i.r407i.gibbs(hamiltonian, beta) for beta in betas}
        generator = q_ops[0]
        prefix_cache = {(name, sign): r412i.r407i.prefixes(terms, order, sign, delta, hbar) for name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms))))) ) for sign in history_signs}
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_trace": float("inf"), "maximum_trace": 0.0, "minimum_candidate_heat_slack": float("inf"), "minimum_continuous_heat_slack": float("inf"), "minimum_short_slack": float("inf"), "minimum_late_slack": float("inf"), "minimum_mellin_remainder": float("inf"), "maximum_mellin_residual": 0.0, "maximum_heat_value": 0.0}
        for beta in betas:
            reference, raw_reference = r412i.r407i.probabilities(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            for support in supports:
                for source_sign in source_signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = r412i.r407i.hermitian(source @ states[beta] @ source.conj().T)
                    for (_name, history_sign), cached_prefixes in prefix_cache.items():
                        for prefix_length, prefix in cached_prefixes:
                            for history_adjoint in adjoints:
                                state = r412i.r407i.hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else r412i.r407i.hermitian(prefix.conj().T @ seeded @ prefix)
                                sample, raw_sample = r412i.r407i.probabilities(state, basis, dimension, volume)
                                check(f"d={dimension} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                                for orientation in orientations:
                                    order_sites = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                    for conditional, _likelihood in r412i.r407i.conditional_rows(reference, sample, order_sites, dimension, floor):
                                        _gap, laplacian, _conductance = r412i.r407i.intrinsic_graph(conditional, momentum, chi)
                                        trace_data = r412i.trace_identity_data(conditional, laplacian, eigen_floor, tolerance)
                                        values = np.asarray(trace_data["ordered_positive_normalized_eigenvalues"], dtype=float)
                                        mixed = r412i.mixed_envelope_data(values, exponents)
                                        actual = heat_data(values, next(iter(mixed.values())), heat_times, split_time)
                                        residual = trace_data["trace_inverse"] - actual["short_actual"] - actual["late_actual"]
                                        check("Mellin identity", abs(residual) <= tolerance, residual, f"abs <= {tolerance}", "Mellin")
                                        check("Mellin remainder", actual["late_actual"] >= -tolerance, actual["late_actual"], f">=-{tolerance}", "Mellin")
                                        differences = [right - left for left, right in zip(actual["actual_heat"], actual["actual_heat"][1:])]
                                        check("heat monotone", max(differences, default=-math.inf) <= tolerance, differences, f"max <= {tolerance}", "heat trace")
                                        row_heat: list[float] = []
                                        row_continuous: list[float] = []
                                        row_short: list[float] = []
                                        row_late: list[float] = []
                                        for candidate in mixed.values():
                                            envelope = heat_data(values, candidate, heat_times, split_time)
                                            row_heat.extend(bound - actual_value for bound, actual_value in zip(envelope["finite_heat_bound"], actual["actual_heat"]))
                                            row_continuous.extend(bound - actual_value for bound, actual_value in zip(envelope["continuous_heat_bound"], actual["actual_heat"]))
                                            row_short.append(envelope["short_bound"] - envelope["short_actual"])
                                            row_late.append(envelope["late_bound"] - envelope["late_actual"])
                                        check("finite candidate heat", min(row_heat) >= -tolerance, [min(row_heat), max(row_heat)], f">=-{tolerance}", "heat envelope")
                                        check("continuous UV heat", min(row_continuous) >= -tolerance, [min(row_continuous), max(row_continuous)], f">=-{tolerance}", "UV Mellin")
                                        check("short UV budget", min(row_short) >= -tolerance, [min(row_short), max(row_short)], f">=-{tolerance}", "UV Mellin")
                                        check("late IR budget", min(row_late) >= -tolerance, [min(row_late), max(row_late)], f">=-{tolerance}", "IR remainder")
                                        best_key, best = min(mixed.items(), key=lambda item: (item[1]["infinite_zeta_bound"], item[1]["finite_trace_bound"], item[0]))
                                        selected = heat_data(values, best, heat_times, split_time)
                                        traces.append(float(trace_data["trace_inverse"]))
                                        short_actuals.append(float(selected["short_actual"]))
                                        late_actuals.append(float(selected["late_actual"]))
                                        mellin_residuals.append(float(residual))
                                        heat_values.extend(float(value) for value in actual["actual_heat"])
                                        heat_increases.extend(differences)
                                        candidate_heat_slacks.extend(row_heat)
                                        candidate_continuous_slacks.extend(row_continuous)
                                        candidate_short_slacks.extend(row_short)
                                        candidate_late_slacks.extend(row_late)
                                        selected_short_bounds.append(float(selected["short_bound"]))
                                        selected_late_bounds.append(float(selected["late_bound"]))
                                        selected_keys.append(best_key)
                                        candidate_counts.append(len(mixed))
                                        total_rows += 1
                                        profile["row_count"] += 1
                                        profile["minimum_trace"] = min(profile["minimum_trace"], trace_data["trace_inverse"])
                                        profile["maximum_trace"] = max(profile["maximum_trace"], trace_data["trace_inverse"])
                                        profile["minimum_candidate_heat_slack"] = min(profile["minimum_candidate_heat_slack"], min(row_heat))
                                        profile["minimum_continuous_heat_slack"] = min(profile["minimum_continuous_heat_slack"], min(row_continuous))
                                        profile["minimum_short_slack"] = min(profile["minimum_short_slack"], min(row_short))
                                        profile["minimum_late_slack"] = min(profile["minimum_late_slack"], min(row_late))
                                        profile["minimum_mellin_remainder"] = min(profile["minimum_mellin_remainder"], selected["late_actual"])
                                        profile["maximum_mellin_residual"] = max(profile["maximum_mellin_residual"], abs(residual))
                                        profile["maximum_heat_value"] = max(profile["maximum_heat_value"], max(actual["actual_heat"]))
                                    profile["context_count"] += 1
                                    total_contexts += 1
        check(f"V={volume} d={dimension} profile", profile["row_count"] > profile["context_count"] and profile["minimum_trace"] > 0.0 and profile["minimum_candidate_heat_slack"] >= -tolerance and profile["minimum_short_slack"] >= -tolerance, [profile["row_count"], profile["context_count"], profile["minimum_trace"], profile["minimum_candidate_heat_slack"], profile["minimum_short_slack"]], "finite heat budget", "coverage")
        profiles[f"V={volume}/d={dimension}"] = profile

    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("candidate coverage", set(candidate_counts) == {len(exponents) * len(exponents) * (dimension - 2) for _volume, dimension in pairs}, sorted(set(candidate_counts)), "all candidate counts", "coverage")
    check("trace positive", min(traces) > 0.0 and all(math.isfinite(value) for value in traces), [min(traces), max(traces)], ">0 finite", "Mellin")
    check("Mellin aggregate", min(late_actuals) >= -tolerance and max(abs(value) for value in mellin_residuals) <= tolerance, [min(late_actuals), max(abs(value) for value in mellin_residuals)], "positive remainder and exact split", "Mellin")
    check("heat aggregate", max(heat_increases) <= tolerance and min(candidate_heat_slacks) >= -tolerance and min(candidate_continuous_slacks) >= -tolerance, [max(heat_increases), min(candidate_heat_slacks), min(candidate_continuous_slacks)], "monotone and bounded", "heat envelope")
    check("budget aggregate", min(candidate_short_slacks) >= -tolerance and min(candidate_late_slacks) >= -tolerance, [min(candidate_short_slacks), min(candidate_late_slacks)], f">=-{tolerance}", "split budget")
    derived = {
        "system_count": len(pairs),
        "context_count": total_contexts,
        "comparison_row_count": total_rows,
        "heat_time_values": heat_times,
        "mellin_split_time": split_time,
        "minimum_trace_inverse": min(traces),
        "maximum_trace_inverse": max(traces),
        "minimum_short_actual": min(short_actuals),
        "maximum_short_actual": max(short_actuals),
        "minimum_late_actual": min(late_actuals),
        "maximum_late_actual": max(late_actuals),
        "minimum_mellin_remainder": min(late_actuals),
        "maximum_mellin_identity_abs_residual": max(abs(value) for value in mellin_residuals),
        "minimum_heat_value": min(heat_values),
        "maximum_heat_value": max(heat_values),
        "maximum_heat_increase": max(heat_increases),
        "minimum_candidate_heat_slack": min(candidate_heat_slacks),
        "minimum_continuous_heat_slack": min(candidate_continuous_slacks),
        "minimum_short_budget_slack": min(candidate_short_slacks),
        "minimum_late_budget_slack": min(candidate_late_slacks),
        "minimum_selected_short_bound": min(selected_short_bounds),
        "maximum_selected_short_bound": max(selected_short_bounds),
        "minimum_selected_late_bound": min(selected_late_bounds),
        "maximum_selected_late_bound": max(selected_late_bounds),
        "candidate_count_per_row": sorted(set(candidate_counts)),
        "selected_key_histogram": {key: selected_keys.count(key) for key in sorted(set(selected_keys))},
        "system_profiles": profiles,
        "finite_mellin_identity_closed": True,
        "finite_mixed_heat_envelope_closed": True,
        "finite_short_time_uv_budget_closed": True,
        "finite_likelihood_row_coverage_closed": True,
        "cutoff_independent_heat_budget_closed": False,
        "volume_independent_heat_budget_closed": False,
        "phase_uniform_heat_budget_closed": False,
        "exhaustion_uniform_heat_budget_closed": False,
        "common_core_closed": False,
        "common_split_rule_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r413-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-413", "exploration_id": "EXP-001258", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-413 INDEPENDENT PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} heat_times={len(heat_times)} candidates={sorted(set(candidate_counts))} trace=[{min(traces):.6g},{max(traces):.6g}] slack=[{min(candidate_continuous_slacks):.6g},{min(candidate_short_slacks):.6g}]")
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
