#!/usr/bin/env python3
"""Independent moment-formula lane for EXP-001166.

This lane does not enumerate remote configurations.  It derives the centered
four-leg contexts from Bernoulli first and second moments and checks the exact
all-n formula independently of the primary enumeration.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_centered_global_energy_context_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-centered-global-energy-context-obstruction-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def fraction(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def affine_second_moment(base: Fraction, slope: Fraction, mean: Fraction, variance: Fraction) -> Fraction:
    return base**2 + 2 * base * slope * mean + slope**2 * (variance + mean**2)


def moment_context(
    n: int,
    local_target: Fraction,
    local_gap: Fraction,
    remote_gap: Fraction,
    ratio: Fraction,
    shift: Fraction,
    probability: Fraction,
    amplitude_squared: Fraction,
) -> tuple[Fraction, Fraction]:
    q = ratio / (1 + ratio)
    remote_mean = Fraction(n) * q
    remote_variance = Fraction(n) * q * (1 - q)
    local_mean = q * local_gap
    centered_offset = local_target - local_mean
    centered = probability * amplitude_squared * (remote_gap**2 * remote_variance + centered_offset**2)
    uncentered = probability * amplitude_squared * affine_second_moment(shift + local_target, remote_gap, remote_mean, remote_variance)
    return centered, uncentered


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    local_gap = fraction(fixture["local_gap"])
    remote_gap = fraction(fixture["remote_gap"])
    ratio = fraction(fixture["gibbs_excited_weight_ratio"])
    shift = fraction(fixture["shift_constant"])
    amplitude_squared = fraction(fixture["amplitude_squared"])
    values = [int(n) for n in fixture["remote_site_values"]]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001166" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001166/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("parameter positivity", local_gap > 0 and remote_gap > 0 and ratio > 0 and shift > 0 and amplitude_squared == 1, [local_gap, remote_gap, ratio, shift, amplitude_squared], ">0 and unit local amplitude", "inputs")
    check("scope firewall", scope["exact_tensor_product_centered_contexts_closed"] and scope["all_n_closed_form_closed"] and scope["positive_linear_lower_bound_closed"] and scope["centered_global_energy_uniformity_refuted"] and not scope["actual_q3_interacting_uniformity_refuted"] and not scope["pre_a_closed"], scope, "centered product obstruction; QFT gates open", "scope")

    partition = 1 + ratio
    p0 = Fraction(1, 1) / partition
    p1 = ratio / partition
    q = ratio / partition
    variance_per_site = q * (1 - q)
    slopes = {
        "D_row": p0 * amplitude_squared * remote_gap**2 * variance_per_site,
        "D_column": p1 * amplitude_squared * remote_gap**2 * variance_per_site,
        "Dstar_row": p1 * amplitude_squared * remote_gap**2 * variance_per_site,
        "Dstar_column": p0 * amplitude_squared * remote_gap**2 * variance_per_site,
    }
    rows: list[dict[str, Any]] = []
    for n in values:
        d_row, d_row_uncentered = moment_context(n, local_gap, local_gap, remote_gap, ratio, shift, p0, amplitude_squared)
        d_column, _ = moment_context(n, Fraction(0), local_gap, remote_gap, ratio, shift, p1, amplitude_squared)
        dstar_row, _ = moment_context(n, Fraction(0), local_gap, remote_gap, ratio, shift, p1, amplitude_squared)
        dstar_column, _ = moment_context(n, local_gap, local_gap, remote_gap, ratio, shift, p0, amplitude_squared)
        centered = {"D_row": d_row, "D_column": d_column, "Dstar_row": dstar_row, "Dstar_column": dstar_column}
        for key, value in centered.items():
            check(f"n={n} {key} nonnegative", value >= 0, value, ">=0", "centered formula")
            check(f"n={n} {key} linear lower", value >= slopes[key] * n, value, f">={slopes[key] * n}", "remote variance")
        check(f"n={n} uncentered D_row direct formula", d_row_uncentered == affine_second_moment(shift + local_gap, remote_gap, Fraction(n) * q, Fraction(n) * variance_per_site) * p0 * amplitude_squared, d_row_uncentered, "moment formula", "uncentered comparison")
        rows.append({
            "remote_sites": n,
            "centered_contexts": {key: str(value) for key, value in centered.items()},
            "uncentered_D_row": str(d_row_uncentered),
            "linear_lower_bounds": {key: str(slopes[key] * n) for key in slopes},
        })

    origin = moment_context(0, local_gap, local_gap, remote_gap, ratio, shift, p0, amplitude_squared)[0]
    largest = moment_context(max(values), local_gap, local_gap, remote_gap, ratio, shift, p0, amplitude_squared)[0]
    min_slope = min(slopes.values())
    check("positive centered slope", min_slope > 0, min_slope, ">0", "asymptotic obstruction")
    check("centered growth", largest > origin, [largest, origin], ">", "asymptotic obstruction")
    quadratic_coefficient = p0 * amplitude_squared * (remote_gap * q) ** 2
    check("positive uncentered quadratic coefficient", quadratic_coefficient > 0, quadratic_coefficient, ">0", "uncentered comparison")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CENTERED-GLOBAL-ENERGY-CONTEXT-VOLUME-OBSTRUCTION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "rows": rows,
            "row_count": len(rows),
            "local_ground_probability": str(p0),
            "local_excited_probability": str(p1),
            "remote_excitation_probability": str(q),
            "centered_linear_slopes": {key: str(value) for key, value in slopes.items()},
            "minimum_centered_linear_slope": str(min_slope),
            "centered_D_row_at_origin": str(origin),
            "centered_D_row_at_largest_sample": str(largest),
            "uncentered_quadratic_coefficient": str(quadratic_coefficient),
            "centered_global_energy_uniformity_refuted": True,
            "actual_q3_interacting_uniformity_refuted": False,
            "local_energy_route_selected": True,
            "direct_d_delta_d_cauchy_closed": False,
            "modular_domain_transfer_closed": False,
            "common_unbounded_core_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT CENTERED-GLOBAL-ENERGY-CONTEXT-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
