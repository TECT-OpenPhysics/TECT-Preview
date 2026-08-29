#!/usr/bin/env python3
"""Hostile mutation suite for the R-414 two-scale semigroup criterion."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-scale-semigroup-bridge-manifest.json"
SLUG = "pre_a_cp1_st8_q3lock_two_scale_semigroup_bridge"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-hostile-{SLUG}" / "hostile.json"


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


def profile_for(spectrum: list[float], split: int, alpha: float) -> dict[str, Any]:
    if not 1 <= split < len(spectrum) or not 0.0 < alpha < 1.0:
        raise ValueError("split and alpha must be in the finite admissible range")
    uv_constant = max((index + 1.0) / value**alpha for index, value in enumerate(spectrum[split:], start=split))
    return {"split": split, "alpha_uv": alpha, "uv_counting_constant": uv_constant}


def quantities(spectrum: list[float], profile: dict[str, Any], tau: float) -> dict[str, float | list[float]]:
    if not all(value > 0.0 and math.isfinite(value) for value in spectrum) or any(right < left for left, right in zip(spectrum, spectrum[1:])):
        raise ValueError("spectrum must be ordered and positive")
    split = int(profile["split"])
    alpha = float(profile["alpha_uv"])
    if not 1 <= split < len(spectrum) or not 0.0 < alpha < 1.0:
        raise ValueError("the UV power must be strictly sublinear")
    if tau <= 0.0:
        raise ValueError("tau must be positive")
    uv_factor = float(profile["uv_counting_constant"]) * alpha * math.gamma(alpha)
    heat_tau = sum(math.exp(-tau * value) for value in spectrum)
    short_actual = sum(-math.expm1(-tau * value) / value for value in spectrum)
    late_actual = sum(math.exp(-tau * value) / value for value in spectrum)
    trace = sum(1.0 / value for value in spectrum)
    head_power = split * tau**alpha
    short_power_constant = head_power + uv_factor
    short_budget = short_power_constant * tau ** (1.0 - alpha) / (1.0 - alpha)
    gap = min(spectrum)
    late_budget = heat_tau / gap
    return {"heat_tau": heat_tau, "short_actual": short_actual, "late_actual": late_actual, "trace": trace, "gap": gap, "uv_factor": uv_factor, "head_power": head_power, "short_power_constant": short_power_constant, "short_budget": short_budget, "late_budget": late_budget, "green_bound": short_budget + late_budget}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    threshold = float(manifest["finite_fixture"]["hostile_zero_threshold"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        status = "PASS" if condition else "FAIL"
        checks.append({"name": name, "status": status, "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    baseline_spectrum = [0.25, 4.0]
    baseline_profile = profile_for(baseline_spectrum, 1, 0.5)
    baseline = quantities(baseline_spectrum, baseline_profile, 1.0)
    check("baseline criterion", baseline["green_bound"] >= baseline["trace"], [baseline["green_bound"], baseline["trace"]], "green bound covers trace")

    head_heavy = [0.25, 0.5, 0.75, 1.0, 100.0]
    head_profile = profile_for(head_heavy, 4, 0.5)
    head_data = quantities(head_heavy, head_profile, 0.1)
    omitted_head_budget = head_data["uv_factor"] * 0.1 ** (1.0 - 0.5) / (1.0 - 0.5)
    omitted_head_deficit = head_data["short_actual"] - omitted_head_budget
    check("omitted IR head rejected", omitted_head_deficit > threshold, omitted_head_deficit, f">{threshold}")

    tail_heavy = [0.25, 4.0, 5.0, 6.0]
    tail_profile = profile_for(tail_heavy, 1, 0.5)
    tail_data = quantities(tail_heavy, tail_profile, 0.1)
    omitted_uv_budget = tail_data["head_power"] * 0.1 ** (1.0 - 0.5) / (1.0 - 0.5)
    omitted_uv_deficit = tail_data["short_actual"] - omitted_uv_budget
    check("omitted UV term rejected", omitted_uv_deficit > threshold, omitted_uv_deficit, f">{threshold}")

    wrong_gap_bound = baseline["heat_tau"] / max(baseline_spectrum)
    wrong_gap_deficit = baseline["late_actual"] - wrong_gap_bound
    check("max-eigenvalue IR shortcut rejected", wrong_gap_deficit > threshold, wrong_gap_deficit, f">{threshold}")

    omitted_late_deficit = baseline["trace"] - baseline["short_budget"]
    check("omitted late budget rejected", omitted_late_deficit > threshold, omitted_late_deficit, f">{threshold}")

    wrong_shift_bound = baseline["heat_tau"] * math.exp(-baseline["gap"] * (2.0 + 1.0))
    wrong_shift_deficit = baseline["late_actual"] - wrong_shift_bound
    check("wrong late-time shift rejected", wrong_shift_deficit > threshold, wrong_shift_deficit, f">{threshold}")

    try:
        profile_for(baseline_spectrum, 1, 1.0)
        alpha_one_rejected = False
    except ValueError:
        alpha_one_rejected = True
    check("alpha=1 rejected", alpha_one_rejected, alpha_one_rejected, True)

    reversed_times = [2.0, 1.0, 0.5, 0.25]
    reversed_heat = [sum(math.exp(-time * value) for value in baseline_spectrum) for time in reversed_times]
    reverse_increase = max(right - left for left, right in zip(reversed_heat, reversed_heat[1:]))
    check("reversed time ordering rejected", reverse_increase > threshold, reverse_increase, f">{threshold}")

    wrong_sign_residual = baseline["trace"] - (baseline["short_actual"] - baseline["late_actual"])
    check("wrong Mellin sign rejected", abs(wrong_sign_residual) > threshold, wrong_sign_residual, f"abs>{threshold}")

    derived = {
        "baseline": baseline,
        "omitted_head_short_deficit": omitted_head_deficit,
        "omitted_uv_short_deficit": omitted_uv_deficit,
        "wrong_gap_late_deficit": wrong_gap_deficit,
        "omitted_late_green_deficit": omitted_late_deficit,
        "wrong_shift_late_deficit": wrong_shift_deficit,
        "reverse_heat_max_increase": reverse_increase,
        "wrong_sign_residual": wrong_sign_residual,
        "alpha_one_rejected": alpha_one_rejected,
        "toy_threshold": threshold,
    }
    payload = {"schema": "tect/pre-a-r414-hostile/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-414", "exploration_id": "EXP-001259", "verdict": "PASS", "checks": checks, "assertion_count": len(checks), "derived": derived, "boundary": manifest["boundary"]}
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"R-414 HOSTILE PASS {len(checks)}/{len(checks)} omitted_uv={omitted_uv_deficit:.6g} omitted_head={omitted_head_deficit:.6g} wrong_gap={wrong_gap_deficit:.6g} reverse_increase={reverse_increase:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
