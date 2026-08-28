#!/usr/bin/env python3
"""Increasing-cutoff stress for the R-402 Hamiltonian form comparison."""

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
SLUG = "pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_cutoff_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-carre-du-champ-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
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


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_tolerance"])
    ratio_floor = float(fixture["ratio_floor"])
    chi = float(Fraction(str(fixture["chi"])))
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    source_signs = [int(value) for value in fixture["source_sign_values"]]
    history_signs = [int(value) for value in fixture["history_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    orientations = list(fixture["orientations"])
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    support = tuple(int(site) for site in fixture["source_support_values"][0])
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 200:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001248" and manifest["result_id"] == "R-403" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001248/R-403/false", "provenance")
    finite_flags = ("finite_cutoff_form_stress_closed", "finite_ratio_profile_closed", "finite_lower_upper_direction_split_closed", "finite_orientation_history_stress_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite cutoff stress only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("single support", support == (0,), support, "(0,)", "fixture")

    profiles: list[dict[str, Any]] = []
    all_ratios: list[float] = []
    all_coordinate: list[float] = []
    all_kinetic: list[float] = []
    system_by_dimension: dict[str, dict[str, Any]] = {}
    total_contexts = 0
    total_rows = 0
    zero_rows = 0
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels, _, p_coordinate = r402.coordinate_data(dimension)
        spacings = np.diff(levels)
        check(f"d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        check(f"d={dimension} spacing", float(np.min(spacings)) > 0.0, float(np.min(spacings)), ">0", "coordinates")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        prefixes_by_key = {(order_name, history_sign): r399.all_prefixes(terms, order, history_sign, delta, hbar) for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms)))))) for history_sign in history_signs}
        dimension_ratios: list[float] = []
        dimension_coordinate: list[float] = []
        dimension_kinetic: list[float] = []
        context_count = 0
        row_count = 0
        for beta in betas:
            reference, raw_reference = r399.coordinate_distribution(states[beta], basis, dimension, volume)
            check(f"d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            for source_sign in source_signs:
                generator = q_ops[0]
                source = q3.character(generator, source_sign * amplitude, hbar)
                seeded = r399.hermitian(source @ states[beta] @ source.conj().T)
                for (order_name, history_sign), prefixes in prefixes_by_key.items():
                    for prefix_length, prefix in prefixes:
                        for history_adjoint in adjoints:
                            state = r399.hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else r399.hermitian(prefix.conj().T @ seeded @ prefix)
                            sample, raw_sample = r399.coordinate_distribution(state, basis, dimension, volume)
                            check(f"d={dimension} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                            for orientation in orientations:
                                collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                context_coordinate: list[float] = []
                                context_kinetic: list[float] = []
                                context_ratios: list[float] = []
                                for _, conditional, likelihood in r402.conditional_rows(reference, sample, collar_order, dimension, floor):
                                    coordinate_energy = r402.coordinate_form(conditional, likelihood, spacings)
                                    kinetic_energy = r402.kinetic_form(conditional, likelihood, p_coordinate, chi)
                                    dimension_coordinate.append(coordinate_energy)
                                    dimension_kinetic.append(kinetic_energy)
                                    all_coordinate.append(coordinate_energy)
                                    all_kinetic.append(kinetic_energy)
                                    row_count += 1
                                    total_rows += 1
                                    context_coordinate.append(coordinate_energy)
                                    context_kinetic.append(kinetic_energy)
                                    if coordinate_energy > ratio_floor:
                                        ratio = kinetic_energy / coordinate_energy
                                        if not math.isfinite(ratio) or ratio < 0.0:
                                            raise AssertionError("invalid ratio")
                                        dimension_ratios.append(ratio)
                                        all_ratios.append(ratio)
                                        context_ratios.append(ratio)
                                    else:
                                        zero_rows += 1
                                context_count += 1
                                total_contexts += 1
                                profiles.append({"dimension": dimension, "beta": beta, "source_sign": source_sign, "order": order_name, "history_sign": history_sign, "prefix_length": prefix_length, "history_adjoint": history_adjoint, "orientation": orientation, "row_count": len(context_coordinate), "minimum_coordinate_form": min(context_coordinate), "maximum_coordinate_form": max(context_coordinate), "minimum_kinetic_form": min(context_kinetic), "maximum_kinetic_form": max(context_kinetic), "minimum_ratio": min(context_ratios, default=None), "maximum_ratio": max(context_ratios, default=None)})
        if not dimension_ratios:
            raise AssertionError(f"no nonzero ratio rows at d={dimension}")
        system_by_dimension[f"d={dimension}"] = {"dimension": dimension, "context_count": context_count, "row_count": row_count, "nonzero_ratio_count": len(dimension_ratios), "minimum_ratio": min(dimension_ratios), "maximum_ratio": max(dimension_ratios), "minimum_coordinate_form": min(dimension_coordinate), "maximum_coordinate_form": max(dimension_coordinate), "minimum_kinetic_form": min(dimension_kinetic), "maximum_kinetic_form": max(dimension_kinetic)}
        check(f"d={dimension} ratio positivity", min(dimension_ratios) > 0.0 and all(math.isfinite(value) for value in dimension_ratios), [min(dimension_ratios), max(dimension_ratios)], ">0 finite", "ratio profile")

    dimensions = [dimension for _, dimension in pairs]
    first_max = system_by_dimension[f"d={dimensions[0]}"]["maximum_ratio"]
    last_max = system_by_dimension[f"d={dimensions[-1]}"]["maximum_ratio"]
    late_growth_ratio = last_max / first_max
    check("system coverage", len(system_by_dimension) == len(pairs), len(system_by_dimension), len(pairs), "coverage")
    check("context coverage", total_contexts == sum(4 * len(betas) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs), total_contexts, "expected cached contexts", "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("finite forms", all(math.isfinite(value) and value >= -tolerance for value in all_coordinate + all_kinetic), [min(all_coordinate), min(all_kinetic)], ">=-tolerance and finite", "forms")
    check("finite ratios", all(math.isfinite(value) and value >= 0.0 for value in all_ratios), [min(all_ratios), max(all_ratios)], "finite nonnegative", "ratio profile")
    check("late upper-profile growth", late_growth_ratio > float(fixture["late_growth_threshold"]), late_growth_ratio, f">{fixture['late_growth_threshold']}", "cutoff stress")
    check("lower direction retained", min(all_ratios) > 0.0, min(all_ratios), ">0 (not a uniform theorem)", "direction split")
    derived = {"system_count": len(pairs), "context_count": total_contexts, "comparison_row_count": total_rows, "nonzero_coordinate_row_count": len(all_ratios), "zero_coordinate_row_count": zero_rows, "minimum_coordinate_form": min(all_coordinate), "maximum_coordinate_form": max(all_coordinate), "minimum_kinetic_form": min(all_kinetic), "maximum_kinetic_form": max(all_kinetic), "minimum_kinetic_to_coordinate_ratio": min(all_ratios), "maximum_kinetic_to_coordinate_ratio": max(all_ratios), "baseline_dimension": dimensions[0], "late_dimension": dimensions[-1], "baseline_maximum_ratio": first_max, "late_maximum_ratio": last_max, "late_upper_profile_growth_ratio": late_growth_ratio, "system_by_dimension": system_by_dimension, "profiles": profiles}
    payload = {"schema": "tect/pre-a-r403-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-403", "exploration_id": "EXP-001248", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-403 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} ratio=[{derived['minimum_kinetic_to_coordinate_ratio']:.6g},{derived['maximum_kinetic_to_coordinate_ratio']:.6g}] late_growth={late_growth_ratio:.6g}")
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
