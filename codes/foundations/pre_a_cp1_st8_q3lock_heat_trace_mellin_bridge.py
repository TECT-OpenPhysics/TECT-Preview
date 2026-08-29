#!/usr/bin/env python3
"""Primary finite audit of the R-413 Mellin heat-trace bridge.

The R-412 mixed counting constants give lower envelopes for each ordered
positive mode.  This module checks the finite Mellin split identity, a
pointwise mixed heat envelope, a short-time UV integral budget, and a finite
late-remainder budget on the complete R-412 conditional-row grid.
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


def _lower_modes(values: np.ndarray, profile: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    spectrum = np.asarray(values, dtype=float)
    if spectrum.ndim != 1 or spectrum.size < 2 or not np.all(np.isfinite(spectrum)) or np.any(spectrum <= 0.0):
        raise AssertionError("invalid spectrum for heat bridge")
    split = int(profile["split"])
    if not 1 <= split < spectrum.size:
        raise AssertionError("mixed split is not interior")
    indices = np.arange(1, spectrum.size + 1, dtype=float)
    alpha_ir = float(profile["alpha_ir"])
    alpha_uv = float(profile["alpha_uv"])
    if not 0.0 < alpha_ir < 1.0 or not 0.0 < alpha_uv < 1.0:
        raise AssertionError("heat bridge requires sublinear exponents")
    ir_constant = float(profile["ir_counting_constant"])
    uv_constant = float(profile["uv_counting_constant"])
    if not math.isfinite(ir_constant) or not math.isfinite(uv_constant) or ir_constant <= 0.0 or uv_constant <= 0.0:
        raise AssertionError("invalid mixed counting constant")
    ir_lower = np.power(indices[:split] / ir_constant, 1.0 / alpha_ir)
    uv_lower = np.power(indices[split:] / uv_constant, 1.0 / alpha_uv)
    if not np.all(np.isfinite(ir_lower)) or not np.all(np.isfinite(uv_lower)) or np.any(ir_lower <= 0.0) or np.any(uv_lower <= 0.0):
        raise AssertionError("invalid lower spectral envelope")
    return ir_lower, uv_lower


def heat_data(values: np.ndarray, profile: dict[str, Any], heat_times: np.ndarray, split_time: float) -> dict[str, Any]:
    """Return actual and envelope quantities for one finite mixed profile."""
    spectrum = np.asarray(values, dtype=float)
    times = np.asarray(heat_times, dtype=float)
    if times.ndim != 1 or times.size == 0 or not np.all(np.isfinite(times)) or np.any(times <= 0.0) or np.any(np.diff(times) < 0.0):
        raise AssertionError("heat times must be positive and ordered")
    if not math.isfinite(split_time) or split_time <= 0.0:
        raise AssertionError("Mellin split time must be positive")
    ir_lower, uv_lower = _lower_modes(spectrum, profile)
    actual_heat = np.asarray([float(np.sum(np.exp(-float(time) * spectrum))) for time in times], dtype=float)
    finite_head_heat = np.asarray([float(np.sum(np.exp(-float(time) * ir_lower))) for time in times], dtype=float)
    finite_tail_heat = np.asarray([float(np.sum(np.exp(-float(time) * uv_lower))) for time in times], dtype=float)
    alpha_uv = float(profile["alpha_uv"])
    uv_constant = float(profile["uv_counting_constant"])
    uv_integral_constant = uv_constant * alpha_uv * math.gamma(alpha_uv)
    continuous_uv_heat = uv_integral_constant * np.power(times, -alpha_uv)
    finite_heat_bound = finite_head_heat + finite_tail_heat
    continuous_heat_bound = finite_head_heat + continuous_uv_heat
    short_actual = float(np.sum(-np.expm1(-split_time * spectrum) / spectrum))
    late_actual = float(np.sum(np.exp(-split_time * spectrum) / spectrum))
    short_head_bound = float(np.sum(-np.expm1(-split_time * ir_lower) / ir_lower))
    short_uv_bound = float(uv_integral_constant * split_time ** (1.0 - alpha_uv) / (1.0 - alpha_uv))
    late_bound = float(np.sum(np.exp(-split_time * ir_lower) / ir_lower) + np.sum(np.exp(-split_time * uv_lower) / uv_lower))
    if not all(math.isfinite(item) for item in actual_heat.tolist() + finite_heat_bound.tolist() + continuous_heat_bound.tolist() + [short_actual, late_actual, short_head_bound, short_uv_bound, late_bound]):
        raise AssertionError("nonfinite heat bridge quantity")
    return {
        "actual_heat": actual_heat,
        "finite_heat_bound": finite_heat_bound,
        "continuous_heat_bound": continuous_heat_bound,
        "continuous_uv_heat": continuous_uv_heat,
        "short_actual": short_actual,
        "late_actual": late_actual,
        "short_head_bound": short_head_bound,
        "short_uv_bound": short_uv_bound,
        "short_bound": short_head_bound + short_uv_bound,
        "late_bound": late_bound,
        "ir_mode_count": int(ir_lower.size),
        "uv_mode_count": int(uv_lower.size),
        "uv_integral_constant": uv_integral_constant,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_floor"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    exponents = [float(Fraction(value)) for value in fixture["counting_exponents"]]
    heat_times = np.asarray([float(Fraction(value)) for value in fixture["heat_time_values"]], dtype=float)
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
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite heat bridge only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("positive chi", chi > 0.0, chi, ">0", "fixture")
    check("heat grid", heat_times.size >= 4 and float(np.min(heat_times)) > 0.0 and np.all(np.diff(heat_times) >= 0.0) and split_time > 0.0, heat_times.tolist() + [split_time], "ordered positive times and split", "fixture")

    profiles: dict[str, dict[str, Any]] = {}
    traces: list[float] = []
    short_actuals: list[float] = []
    late_actuals: list[float] = []
    mellin_residuals: list[float] = []
    remainder_values: list[float] = []
    heat_values: list[float] = []
    heat_monotone_margins: list[float] = []
    candidate_heat_slacks: list[float] = []
    candidate_continuous_slacks: list[float] = []
    candidate_short_slacks: list[float] = []
    candidate_late_slacks: list[float] = []
    selected_short_bounds: list[float] = []
    selected_late_bounds: list[float] = []
    selected_keys: list[str] = []
    total_contexts = 0
    total_rows = 0
    candidate_counts: list[int] = []

    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension ** volume, dimension ** volume), basis.shape, (dimension ** volume, dimension ** volume), "coordinates")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        generator_cache = {support: sum((q_ops[site] for site in support), np.zeros_like(q_ops[0])) for support in supports}
        prefixes_by_key = {(order_name, history_sign): r399.all_prefixes(terms, order, history_sign, delta, hbar) for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms))))) ) for history_sign in history_signs}
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "minimum_trace": float("inf"), "maximum_trace": 0.0, "minimum_short_actual": float("inf"), "maximum_short_actual": 0.0, "minimum_late_actual": float("inf"), "maximum_late_actual": 0.0, "minimum_candidate_heat_slack": float("inf"), "minimum_continuous_heat_slack": float("inf"), "minimum_short_slack": float("inf"), "minimum_late_slack": float("inf"), "minimum_mellin_remainder": float("inf"), "maximum_mellin_residual": 0.0, "maximum_heat_value": 0.0, "candidate_count": 0}
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
                                        check("mixed candidate coverage", len(mixed) == len(exponents) * len(exponents) * (dimension - 2), len(mixed), len(exponents) * len(exponents) * (dimension - 2), "mixed counting")
                                        actual = heat_data(values, next(iter(mixed.values())), heat_times, split_time)
                                        actual_heat = actual["actual_heat"]
                                        mellin_residual = trace_data["trace_inverse"] - (actual["short_actual"] + actual["late_actual"])
                                        check("Mellin truncation identity", abs(mellin_residual) <= tolerance, mellin_residual, f"abs <= {tolerance}", "Mellin")
                                        check("Mellin remainder positive", actual["late_actual"] >= -tolerance, actual["late_actual"], f">=-{tolerance}", "Mellin")
                                        heat_differences = np.diff(actual_heat)
                                        check("heat monotonicity", float(np.max(heat_differences, initial=-math.inf)) <= tolerance, heat_differences.tolist(), f"max <= {tolerance}", "heat trace")
                                        row_candidate_heat_slacks: list[float] = []
                                        row_continuous_slacks: list[float] = []
                                        row_short_slacks: list[float] = []
                                        row_late_slacks: list[float] = []
                                        for candidate in mixed.values():
                                            envelope = heat_data(values, candidate, heat_times, split_time)
                                            finite_slack = envelope["finite_heat_bound"] - actual_heat
                                            continuous_slack = envelope["continuous_heat_bound"] - actual_heat
                                            short_slack = envelope["short_bound"] - envelope["short_actual"]
                                            late_slack = envelope["late_bound"] - envelope["late_actual"]
                                            row_candidate_heat_slacks.extend(float(value) for value in finite_slack)
                                            row_continuous_slacks.extend(float(value) for value in continuous_slack)
                                            row_short_slacks.append(float(short_slack))
                                            row_late_slacks.append(float(late_slack))
                                        check("finite mixed heat envelopes", min(row_candidate_heat_slacks) >= -tolerance, [min(row_candidate_heat_slacks), max(row_candidate_heat_slacks)], f">=-{tolerance}", "heat envelope")
                                        check("continuous UV heat envelopes", min(row_continuous_slacks) >= -tolerance, [min(row_continuous_slacks), max(row_continuous_slacks)], f">=-{tolerance}", "UV Mellin")
                                        check("short-time UV budgets", min(row_short_slacks) >= -tolerance, [min(row_short_slacks), max(row_short_slacks)], f">=-{tolerance}", "UV Mellin")
                                        check("late remainder budgets", min(row_late_slacks) >= -tolerance, [min(row_late_slacks), max(row_late_slacks)], f">=-{tolerance}", "IR remainder")
                                        best_key, best = min(mixed.items(), key=lambda item: (item[1]["infinite_zeta_bound"], item[1]["finite_trace_bound"], item[0]))
                                        selected = heat_data(values, best, heat_times, split_time)
                                        check("selected trace decomposition", selected["short_actual"] >= -tolerance and selected["late_actual"] >= -tolerance and abs(trace_data["trace_inverse"] - selected["short_actual"] - selected["late_actual"]) <= tolerance, [selected["short_actual"], selected["late_actual"], trace_data["trace_inverse"]], "nonnegative parts sum to trace", "Mellin")
                                        check("selected split bounds", selected["short_bound"] >= selected["short_actual"] - tolerance and selected["late_bound"] >= selected["late_actual"] - tolerance, [selected["short_bound"], selected["short_actual"], selected["late_bound"], selected["late_actual"]], f"bounds within {tolerance}", "split budget")
                                        traces.append(float(trace_data["trace_inverse"]))
                                        short_actuals.append(float(selected["short_actual"]))
                                        late_actuals.append(float(selected["late_actual"]))
                                        mellin_residuals.append(float(mellin_residual))
                                        remainder_values.append(float(selected["late_actual"]))
                                        heat_values.extend(float(value) for value in actual_heat)
                                        heat_monotone_margins.extend(float(value) for value in heat_differences)
                                        candidate_heat_slacks.extend(row_candidate_heat_slacks)
                                        candidate_continuous_slacks.extend(row_continuous_slacks)
                                        candidate_short_slacks.extend(row_short_slacks)
                                        candidate_late_slacks.extend(row_late_slacks)
                                        selected_short_bounds.append(float(selected["short_bound"]))
                                        selected_late_bounds.append(float(selected["late_bound"]))
                                        selected_keys.append(best_key)
                                        candidate_counts.append(len(mixed))
                                        total_rows += 1
                                        profile["row_count"] += 1
                                        profile["minimum_trace"] = min(profile["minimum_trace"], trace_data["trace_inverse"])
                                        profile["maximum_trace"] = max(profile["maximum_trace"], trace_data["trace_inverse"])
                                        profile["minimum_short_actual"] = min(profile["minimum_short_actual"], selected["short_actual"])
                                        profile["maximum_short_actual"] = max(profile["maximum_short_actual"], selected["short_actual"])
                                        profile["minimum_late_actual"] = min(profile["minimum_late_actual"], selected["late_actual"])
                                        profile["maximum_late_actual"] = max(profile["maximum_late_actual"], selected["late_actual"])
                                        profile["minimum_candidate_heat_slack"] = min(profile["minimum_candidate_heat_slack"], min(row_candidate_heat_slacks))
                                        profile["minimum_continuous_heat_slack"] = min(profile["minimum_continuous_heat_slack"], min(row_continuous_slacks))
                                        profile["minimum_short_slack"] = min(profile["minimum_short_slack"], min(row_short_slacks))
                                        profile["minimum_late_slack"] = min(profile["minimum_late_slack"], min(row_late_slacks))
                                        profile["minimum_mellin_remainder"] = min(profile["minimum_mellin_remainder"], selected["late_actual"])
                                        profile["maximum_mellin_residual"] = max(profile["maximum_mellin_residual"], abs(mellin_residual))
                                        profile["maximum_heat_value"] = max(profile["maximum_heat_value"], float(np.max(actual_heat)))
                                    profile["context_count"] += 1
                                    total_contexts += 1
        check(f"V={volume} d={dimension} profile", profile["row_count"] > profile["context_count"] and profile["minimum_trace"] > 0.0 and profile["minimum_short_slack"] >= -tolerance and profile["minimum_late_slack"] >= -tolerance, [profile["row_count"], profile["context_count"], profile["minimum_trace"], profile["minimum_short_slack"], profile["minimum_late_slack"]], "positive finite heat budget", "coverage")
        profiles[f"V={volume}/d={dimension}"] = profile

    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    expected_candidates = {len(exponents) * len(exponents) * (dimension - 2) for _volume, dimension in pairs}
    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("candidate count coverage", set(candidate_counts) == expected_candidates, sorted(set(candidate_counts)), sorted(expected_candidates), "coverage")
    check("trace positivity", all(math.isfinite(value) and value > 0.0 for value in traces), [min(traces), max(traces)], ">0 finite", "Mellin")
    check("Mellin remainders", min(remainder_values) >= -tolerance and max(abs(value) for value in mellin_residuals) <= tolerance, [min(remainder_values), max(abs(value) for value in mellin_residuals)], f"remainder >= -{tolerance}, identity <= {tolerance}", "Mellin")
    check("heat monotonicity aggregate", max(heat_monotone_margins) <= tolerance, max(heat_monotone_margins), f"<= {tolerance}", "heat trace")
    check("candidate heat slack aggregate", min(candidate_heat_slacks) >= -tolerance and min(candidate_continuous_slacks) >= -tolerance, [min(candidate_heat_slacks), min(candidate_continuous_slacks)], f">=-{tolerance}", "heat envelope")
    check("split budget aggregate", min(candidate_short_slacks) >= -tolerance and min(candidate_late_slacks) >= -tolerance, [min(candidate_short_slacks), min(candidate_late_slacks)], f">=-{tolerance}", "split budget")
    check("short UV integrability", split_time > 0.0 and all(float(Fraction(value)) < 1.0 for value in fixture["counting_exponents"]) and min(selected_short_bounds) > 0.0, [split_time, selected_short_bounds[0], selected_short_bounds[-1]], "positive tau and 0<alpha_UV<1", "UV Mellin")
    derived = {
        "system_count": len(pairs),
        "context_count": total_contexts,
        "comparison_row_count": total_rows,
        "heat_time_values": [float(value) for value in heat_times],
        "mellin_split_time": split_time,
        "minimum_trace_inverse": min(traces),
        "maximum_trace_inverse": max(traces),
        "minimum_short_actual": min(short_actuals),
        "maximum_short_actual": max(short_actuals),
        "minimum_late_actual": min(late_actuals),
        "maximum_late_actual": max(late_actuals),
        "minimum_mellin_remainder": min(remainder_values),
        "maximum_mellin_identity_abs_residual": max(abs(value) for value in mellin_residuals),
        "minimum_heat_value": min(heat_values),
        "maximum_heat_value": max(heat_values),
        "maximum_heat_increase": max(heat_monotone_margins),
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
    payload = {"schema": "tect/pre-a-r413-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-413", "exploration_id": "EXP-001258", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-413 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} heat_times={len(heat_times)} candidates={sorted(set(candidate_counts))} trace=[{min(traces):.6g},{max(traces):.6g}] slack=[{min(candidate_continuous_slacks):.6g},{min(candidate_short_slacks):.6g}]")
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
