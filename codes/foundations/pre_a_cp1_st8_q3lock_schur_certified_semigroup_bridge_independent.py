#!/usr/bin/env python3
"""Independent plain-loop reconstruction of R-415."""

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
SLUG = "pre_a_cp1_st8_q3lock_schur_certified_semigroup_bridge"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-schur-certified-semigroup-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_harmonic_schur_capacity_independent as r406i  # noqa: E402
import pre_a_cp1_st8_q3lock_spectral_counting_mixed_independent as r412i  # noqa: E402


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


def semigroup_data(values: np.ndarray, profile: dict[str, Any], times: list[float], split_time: float, certified_gap: float) -> dict[str, Any]:
    spectrum = [float(item) for item in np.asarray(values, dtype=float).tolist()]
    if len(spectrum) < 2 or any((not math.isfinite(item) or item <= 0.0) for item in spectrum) or any(right < left for left, right in zip(spectrum, spectrum[1:])):
        raise AssertionError("invalid ordered positive spectrum")
    split = int(profile["split"])
    alpha = float(profile["alpha_uv"])
    uv_constant = float(profile["uv_counting_constant"])
    if not 1 <= split < len(spectrum) or not 0.0 < alpha < 1.0 or uv_constant <= 0.0 or split_time <= 0.0 or certified_gap <= 0.0:
        raise AssertionError("invalid Schur semigroup profile")
    heat = [sum(math.exp(-time * value) for value in spectrum) for time in times]
    heat_tau = sum(math.exp(-split_time * value) for value in spectrum)
    short_actual = sum(-math.expm1(-split_time * value) / value for value in spectrum)
    late_actual = sum(math.exp(-split_time * value) / value for value in spectrum)
    trace_inverse = sum(1.0 / value for value in spectrum)
    uv_factor = uv_constant * alpha * math.gamma(alpha)
    power_constant = split * split_time**alpha + uv_factor
    short_budget = power_constant * split_time ** (1.0 - alpha) / (1.0 - alpha)
    late_budget = heat_tau / certified_gap
    green_bound = short_budget + late_budget
    return {"actual_heat": heat, "heat_at_split": heat_tau, "short_actual": short_actual, "late_actual": late_actual, "trace_inverse": trace_inverse, "first_positive_gap": min(spectrum), "certified_gap": certified_gap, "short_power_constant": power_constant, "uv_integral_factor": uv_factor, "short_power_bound_values": [power_constant * time ** (-alpha) for time in times], "late_exponential_bound_values": [heat_tau * math.exp(-certified_gap * (time - split_time)) for time in times], "short_power_budget": short_budget, "late_semigroup_bound": late_budget, "green_bound": green_bound}


def conditional_rows(reference: np.ndarray, order: list[int], dimension: int, floor: float):
    """Rebuild the ordered one-site conditional rows without the primary helper."""
    for radius in range(len(order)):
        prefix = r406i.marginal(reference, order[: radius + 1], dimension)
        parent = np.ones((1,), dtype=float) if radius == 0 else r406i.marginal(reference, order[:radius], dimension).reshape(-1)
        if float(np.min(prefix)) <= floor or float(np.min(parent)) <= floor:
            raise AssertionError("marginal floor")
        for mass, row in zip(parent, prefix.reshape(-1, dimension)):
            conditional = row / float(mass)
            conditional /= float(np.sum(conditional))
            yield conditional


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    decomposition_tolerance = float(fixture["decomposition_tolerance"])
    floor = float(fixture["probability_floor"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    gap_floor = float(fixture["gap_floor"])
    exponents = [float(Fraction(value)) for value in fixture["counting_exponents"]]
    heat_times = [float(Fraction(value)) for value in fixture["heat_time_values"]]
    split_time = float(Fraction(fixture["semigroup_split_time"]))
    chi = float(Fraction(str(fixture["chi"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 300:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-415" and manifest["exploration_id"] == "EXP-001260" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-415/EXP-001260/false", "provenance")
    finite_flags = ("finite_schur_certified_semigroup_closed", "finite_short_time_power_budget_closed", "finite_late_time_semigroup_budget_closed", "finite_green_trace_criterion_closed", "finite_harmonic_split_revalidated", "finite_likelihood_row_coverage_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("heat grid", len(heat_times) >= 4 and min(heat_times) < split_time < max(heat_times) and all(right >= left for left, right in zip(heat_times, heat_times[1:])), heat_times + [split_time], "ordered positive times straddling split", "fixture")

    traces: list[float] = []
    full_gaps: list[float] = []
    certified_gaps: list[float] = []
    coarse_gaps: list[float] = []
    residual_gaps: list[float] = []
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
    total_profiles = 0
    total_rows = 0
    short_indices = [index for index, time in enumerate(heat_times) if time <= split_time + tolerance]
    late_indices = [index for index, time in enumerate(heat_times) if time >= split_time - tolerance]

    for volume, dimension in pairs:
        hamiltonian = r406i.model(volume, dimension, fixture)
        basis = r406i.coordinate_basis(dimension, volume)
        _levels, momentum = r412i.r407i.coordinate_data(dimension)
        lower, upper, neutral = r406i.phase_indices(_levels)
        blocks = [lower, neutral, upper] if len(neutral) else [lower, upper]
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension ** volume, dimension ** volume), basis.shape, (dimension ** volume, dimension ** volume), "coordinates")
        states = {beta: r406i.gibbs(hamiltonian, beta) for beta in betas}
        for beta in betas:
            reference = r406i.distribution(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor, float(np.min(reference)), f">{floor}", "Gibbs")
            for orientation in orientations:
                collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"row_count": 0, "minimum_full_gap": float("inf"), "minimum_certified_gap": float("inf"), "minimum_coarse_gap": float("inf"), "minimum_residual_gap": float("inf"), "minimum_green_slack": float("inf")}
                for conditional in conditional_rows(reference, collar_order, dimension, floor):
                    full_gap, edges = r406i.graph(conditional, momentum, chi)
                    schur = r406i.harmonic(conditional, edges, blocks)
                    laplacian = np.diag(np.sum(edges, axis=1)) - edges
                    trace_data = r412i.trace_identity_data(conditional, laplacian, eigen_floor, tolerance)
                    values = np.asarray(trace_data["ordered_positive_normalized_eigenvalues"], dtype=float)
                    mixed = r412i.mixed_envelope_data(values, exponents)
                    certified_gap = float(schur["decomposition_gap"])
                    check("Schur lower relation", certified_gap <= full_gap + decomposition_tolerance and certified_gap > gap_floor, [certified_gap, full_gap], f"{gap_floor}<certified<=full+{decomposition_tolerance}", "Schur")
                    check("Schur components positive", schur["coarse_gap"] > gap_floor and schur["residual_gap"] > gap_floor, [schur["coarse_gap"], schur["residual_gap"]], f">{gap_floor}", "Schur")
                    actual = semigroup_data(values, next(iter(mixed.values())), heat_times, split_time, certified_gap)
                    heat = actual["actual_heat"]
                    mellin_residual = actual["trace_inverse"] - actual["short_actual"] - actual["late_actual"]
                    check("Mellin decomposition", abs(mellin_residual) <= tolerance, mellin_residual, f"abs <= {tolerance}", "Mellin")
                    differences = [right - left for left, right in zip(heat, heat[1:])]
                    check("heat monotone", max(differences, default=-math.inf) <= tolerance, differences, f"max <= {tolerance}", "heat trace")
                    min_short_pointwise = float("inf")
                    min_late_pointwise = float("inf")
                    min_short_budget = float("inf")
                    min_late_budget = float("inf")
                    min_green = float("inf")
                    for candidate in mixed.values():
                        data = semigroup_data(values, candidate, heat_times, split_time, certified_gap)
                        min_short_pointwise = min(min_short_pointwise, min(data["short_power_bound_values"][index] - heat[index] for index in short_indices))
                        min_late_pointwise = min(min_late_pointwise, min(data["late_exponential_bound_values"][index] - heat[index] for index in late_indices))
                        min_short_budget = min(min_short_budget, data["short_power_budget"] - data["short_actual"])
                        min_late_budget = min(min_late_budget, data["late_semigroup_bound"] - data["late_actual"])
                        min_green = min(min_green, data["green_bound"] - data["trace_inverse"])
                    check("short power envelope", min_short_pointwise >= -tolerance, min_short_pointwise, f">=-{tolerance}", "short UV budget")
                    check("late Schur semigroup envelope", min_late_pointwise >= -tolerance, min_late_pointwise, f">=-{tolerance}", "late IR budget")
                    check("short power budget", min_short_budget >= -tolerance, min_short_budget, f">=-{tolerance}", "short UV budget")
                    check("late Schur budget", min_late_budget >= -tolerance, min_late_budget, f">=-{tolerance}", "late IR budget")
                    check("Schur Green criterion", min_green >= -tolerance, min_green, f">=-{tolerance}", "two-scale criterion")
                    selected_key, selected_profile = min(mixed.items(), key=lambda item: (semigroup_data(values, item[1], heat_times, split_time, certified_gap)["green_bound"], item[0]))
                    selected = semigroup_data(values, selected_profile, heat_times, split_time, certified_gap)
                    check("selected criterion", selected["green_bound"] >= selected["trace_inverse"] - tolerance and selected["late_semigroup_bound"] >= selected["late_actual"] - tolerance, [selected["green_bound"], selected["trace_inverse"], selected["late_semigroup_bound"], selected["late_actual"]], f"finite bounds within {tolerance}", "two-scale criterion")
                    traces.append(selected["trace_inverse"])
                    full_gaps.append(full_gap)
                    certified_gaps.append(certified_gap)
                    coarse_gaps.append(float(schur["coarse_gap"]))
                    residual_gaps.append(float(schur["residual_gap"]))
                    heat_at_split_values.append(selected["heat_at_split"])
                    short_power_slacks.append(min_short_pointwise)
                    late_exponential_slacks.append(min_late_pointwise)
                    short_budget_slacks.append(min_short_budget)
                    late_budget_slacks.append(min_late_budget)
                    green_slacks.append(min_green)
                    mellin_residuals.append(mellin_residual)
                    heat_values.extend(heat)
                    heat_increases.extend(differences)
                    selected_bounds.append(selected["green_bound"])
                    selected_keys.append(selected_key)
                    candidate_counts.append(len(mixed))
                    total_rows += 1
                    profile["row_count"] += 1
                    profile["minimum_full_gap"] = min(profile["minimum_full_gap"], full_gap)
                    profile["minimum_certified_gap"] = min(profile["minimum_certified_gap"], certified_gap)
                    profile["minimum_coarse_gap"] = min(profile["minimum_coarse_gap"], schur["coarse_gap"])
                    profile["minimum_residual_gap"] = min(profile["minimum_residual_gap"], schur["residual_gap"])
                    profile["minimum_green_slack"] = min(profile["minimum_green_slack"], min_green)
                check(f"V={volume} d={dimension} beta={beta} {orientation} profile", profile["row_count"] > 0 and profile["minimum_certified_gap"] > gap_floor and profile["minimum_green_slack"] >= -tolerance, [profile["row_count"], profile["minimum_certified_gap"], profile["minimum_green_slack"]], "positive finite Schur semigroup profile", "coverage")
                total_profiles += 1

    check("profile coverage", total_profiles == len(pairs) * len(betas) * len(orientations), total_profiles, len(pairs) * len(betas) * len(orientations), "coverage")
    check("row coverage", total_rows > total_profiles and total_rows > 0, total_rows, f">{total_profiles}", "coverage")
    check("candidate count coverage", set(candidate_counts) == {len(exponents) * len(exponents) * (dimension - 2) for _volume, dimension in pairs}, sorted(set(candidate_counts)), "all mixed profiles", "coverage")
    check("gap ordering aggregate", min(certified_gaps) > gap_floor and min(full_gaps) > gap_floor and min(certified_gaps) <= min(full_gaps) + decomposition_tolerance, [min(certified_gaps), min(full_gaps)], f"certified gap <= full gap + {decomposition_tolerance}", "Schur")
    check("trace positivity", all(value > 0.0 and math.isfinite(value) for value in traces), [min(traces), max(traces)], ">0 finite", "Mellin")
    check("two-scale aggregate", min(short_power_slacks) >= -tolerance and min(late_exponential_slacks) >= -tolerance and min(short_budget_slacks) >= -tolerance and min(late_budget_slacks) >= -tolerance and min(green_slacks) >= -tolerance, [min(short_power_slacks), min(late_exponential_slacks), min(short_budget_slacks), min(late_budget_slacks), min(green_slacks)], f">=-{tolerance}", "two-scale criterion")
    check("Mellin aggregate", max(abs(value) for value in mellin_residuals) <= tolerance, max(abs(value) for value in mellin_residuals), f"<= {tolerance}", "Mellin")
    check("heat monotonicity aggregate", max(heat_increases) <= tolerance, max(heat_increases), f"<= {tolerance}", "heat trace")
    derived = {
        "system_count": len(pairs), "profile_count": total_profiles, "comparison_row_count": total_rows, "heat_time_values": heat_times, "semigroup_split_time": split_time,
        "minimum_trace_inverse": min(traces), "maximum_trace_inverse": max(traces), "minimum_first_positive_gap": min(full_gaps), "maximum_first_positive_gap": max(full_gaps), "minimum_certified_schur_gap": min(certified_gaps), "maximum_certified_schur_gap": max(certified_gaps), "minimum_coarse_schur_gap": min(coarse_gaps), "maximum_coarse_schur_gap": max(coarse_gaps), "minimum_residual_gap": min(residual_gaps), "maximum_residual_gap": max(residual_gaps), "minimum_heat_at_split": min(heat_at_split_values), "maximum_heat_at_split": max(heat_at_split_values), "minimum_short_power_slack": min(short_power_slacks), "minimum_late_exponential_slack": min(late_exponential_slacks), "minimum_short_budget_slack": min(short_budget_slacks), "minimum_late_budget_slack": min(late_budget_slacks), "minimum_green_trace_slack": min(green_slacks), "maximum_mellin_identity_abs_residual": max(abs(value) for value in mellin_residuals), "minimum_heat_value": min(heat_values), "maximum_heat_value": max(heat_values), "maximum_heat_increase": max(heat_increases), "minimum_selected_green_bound": min(selected_bounds), "maximum_selected_green_bound": max(selected_bounds), "candidate_count_per_row": sorted(set(candidate_counts)), "selected_key_histogram": {key: selected_keys.count(key) for key in sorted(set(selected_keys))},
        "finite_schur_certified_semigroup_closed": True, "finite_short_time_power_budget_closed": True, "finite_late_time_semigroup_budget_closed": True, "finite_green_trace_criterion_closed": True, "finite_harmonic_split_revalidated": True, "finite_likelihood_row_coverage_closed": True,
        "cutoff_independent_schur_gap_closed": False, "volume_independent_schur_gap_closed": False, "phase_uniform_semigroup_closed": False, "exhaustion_uniform_semigroup_closed": False, "common_core_closed": False, "common_split_rule_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r415-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-415", "exploration_id": "EXP-001260", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-415 INDEPENDENT PASS {check_count}/{check_count} systems={len(pairs)} profiles={total_profiles} rows={total_rows} certified_gap=[{min(certified_gaps):.6g},{max(certified_gaps):.6g}] green_slack={min(green_slacks):.6g}")
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
