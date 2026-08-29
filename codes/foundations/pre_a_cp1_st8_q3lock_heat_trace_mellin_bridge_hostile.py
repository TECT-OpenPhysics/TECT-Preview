#!/usr/bin/env python3
"""Adversarial checks for the R-413 Mellin heat-trace bridge."""

from __future__ import annotations

import argparse
import copy
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-heat-trace-mellin-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-31-hostile-pre_a_cp1_st8_q3lock_heat_trace_mellin_bridge" / "hostile.json"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_heat_trace_mellin_bridge as primary  # noqa: E402
import pre_a_cp1_st8_q3lock_spectral_counting_mixed as r412  # noqa: E402
import pre_a_cp1_st8_q3lock_effective_resistance_hostile as r408h  # noqa: E402


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    eigen_floor = float(fixture["resistance_eigen_floor"])
    times = np.asarray([float(Fraction(value)) for value in fixture["heat_time_values"]], dtype=float)
    split_time = float(Fraction(fixture["mellin_split_time"]))
    exponents = [float(Fraction(value)) for value in fixture["counting_exponents"]]
    selected: list[dict[str, Any]] = []
    for dimension in (3, 12):
        conditional, _likelihood, momentum, chi = r408h.selected_row(dimension, fixture)
        _gap, laplacian, _conductance = r408h.primary.r407.intrinsic_graph(conditional, momentum, chi)
        trace = r412.trace_identity_data(conditional, laplacian, eigen_floor, tolerance)
        values = np.asarray(trace["ordered_positive_normalized_eigenvalues"], dtype=float)
        mixed = r412.mixed_envelope_data(values, exponents)
        key, profile = min(mixed.items(), key=lambda item: (item[1]["infinite_zeta_bound"], item[1]["finite_trace_bound"], item[0]))
        good = primary.heat_data(values, profile, times, split_time)
        split = int(profile["split"])
        ir_lower, uv_lower = primary._lower_modes(values, profile)
        reversed_heat = np.asarray([float(np.sum(np.exp(-time * values))) for time in times[::-1]], dtype=float)
        wrong_sign_residual = float(trace["trace_inverse"] - good["short_actual"] + good["late_actual"])
        selected.append({
            "dimension": dimension,
            "mixed_key": key,
            "trace_inverse": float(trace["trace_inverse"]),
            "good_short_bound": float(good["short_bound"]),
            "good_late_bound": float(good["late_bound"]),
            "good_min_heat_slack": float(np.min(good["continuous_heat_bound"] - good["actual_heat"])),
            "reverse_heat_max_increase": float(np.max(np.diff(reversed_heat))),
            "wrong_sign_residual": wrong_sign_residual,
            "alpha_uv": float(profile["alpha_uv"]),
            "split": split,
        })

    # Use exact two-mode toy spectra for mutations whose failure can be hidden
    # by a deliberately loose finite head bound on a selected production row.
    toy_values = np.asarray([1.0, 2.0], dtype=float)
    toy_profile = r412.mixed_envelope_data(toy_values, [0.5])["ir=0.5;uv=0.5;split=1"]
    toy_good = primary.heat_data(toy_values, toy_profile, times, split_time)
    toy_ir, toy_uv = primary._lower_modes(toy_values, toy_profile)
    toy_head_short = float(np.sum(-np.expm1(-split_time * toy_ir) / toy_ir))
    toy_uv_late = float(np.sum(np.exp(-split_time * toy_uv) / toy_uv))
    toy_wrong_time = toy_good["continuous_heat_bound"] - toy_good["continuous_uv_heat"] + float(toy_profile["uv_counting_constant"]) * float(toy_profile["alpha_uv"]) * math.gamma(float(toy_profile["alpha_uv"])) * np.power(times, float(toy_profile["alpha_uv"]))
    small_values = np.asarray([0.01, 0.02], dtype=float)
    small_profile = r412.mixed_envelope_data(small_values, [0.5])["ir=0.5;uv=0.5;split=1"]
    small_good = primary.heat_data(small_values, small_profile, times, split_time)
    wrong_ir = np.power(np.arange(1, small_values.size + 1, dtype=float) / float(small_profile["ir_counting_constant"]), float(small_profile["alpha_ir"]))
    wrong_uv = np.power(np.asarray([2.0]) / float(small_profile["uv_counting_constant"]), float(small_profile["alpha_uv"]))
    wrong_power_bound = float(np.exp(-times[0] * wrong_ir[0]) + np.exp(-times[0] * wrong_uv[0]))

    alpha_one_rejected = False
    representative = r412.mixed_envelope_data(np.asarray([1.0, 2.0, 3.0], dtype=float), [0.5])["ir=0.5;uv=0.5;split=1"]
    alpha_one_profile = copy.deepcopy(representative)
    alpha_one_profile["alpha_uv"] = 1.0
    try:
        primary._lower_modes(np.asarray([1.0, 2.0, 3.0], dtype=float), alpha_one_profile)
    except AssertionError:
        alpha_one_rejected = True

    # A single omitted UV term is always too small because every tail mode is
    # strictly positive at finite time.  The numerical deficit is recorded as
    # an adversarial witness rather than as a new negative theorem.
    checks = [
        {"name": "baseline continuous heat bound", "status": "PASS" if all(item["good_min_heat_slack"] >= -tolerance for item in selected) else "FAIL", "actual": [item["good_min_heat_slack"] for item in selected], "expected": "nonnegative continuous-envelope slack"},
        {"name": "UV term omission rejected", "status": "PASS" if toy_good["short_actual"] - toy_head_short > tolerance else "FAIL", "actual": toy_good["short_actual"] - toy_head_short, "expected": "toy short actual exceeds head-only budget"},
        {"name": "IR head omission rejected", "status": "PASS" if toy_good["late_actual"] - toy_uv_late > tolerance else "FAIL", "actual": toy_good["late_actual"] - toy_uv_late, "expected": "toy late actual exceeds UV-tail-only budget"},
        {"name": "wrong time power rejected", "status": "PASS" if float(np.min(toy_wrong_time - toy_good["actual_heat"])) < -tolerance else "FAIL", "actual": float(np.min(toy_wrong_time - toy_good["actual_heat"])), "expected": "t^alpha is not t^-alpha"},
        {"name": "wrong counting power rejected", "status": "PASS" if wrong_power_bound - small_good["actual_heat"][0] < -tolerance else "FAIL", "actual": wrong_power_bound - small_good["actual_heat"][0], "expected": "lambda^alpha is not the reciprocal lower-envelope power"},
        {"name": "reverse time ordering rejected", "status": "PASS" if all(item["reverse_heat_max_increase"] > tolerance for item in selected) else "FAIL", "actual": [item["reverse_heat_max_increase"] for item in selected], "expected": "heat is decreasing only in increasing time"},
        {"name": "Mellin remainder sign rejected", "status": "PASS" if all(abs(item["wrong_sign_residual"]) > tolerance for item in selected) else "FAIL", "actual": [item["wrong_sign_residual"] for item in selected], "expected": "late remainder enters with a plus sign"},
        {"name": "alpha one divergent tail rejected", "status": "PASS" if alpha_one_rejected else "FAIL", "actual": alpha_one_rejected, "expected": "alpha_uv=1 outside the integrable domain"},
    ]
    if not all(row["status"] == "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r413-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-413", "exploration_id": "EXP-001258", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": {"selected": selected, "toy": {"uv_omission_short_deficit": toy_good["short_actual"] - toy_head_short, "ir_omission_late_deficit": toy_good["late_actual"] - toy_uv_late, "wrong_time_min_slack": float(np.min(toy_wrong_time - toy_good["actual_heat"])), "wrong_power_slack": wrong_power_bound - small_good["actual_heat"][0]}, "alpha_one_rejected": alpha_one_rejected, "mutation": "omitted UV/head terms, wrong time power, wrong counting power, reversed time order, Mellin sign and alpha=1"}, "boundary": manifest["boundary"]}
    primary.atomic_json(output, payload)
    print(f"R-413 HOSTILE PASS {len(checks)}/{len(checks)} dimensions={[item['dimension'] for item in selected]} toy_uv_omission={payload['derived']['toy']['uv_omission_short_deficit']:.6g}")
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
