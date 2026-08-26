#!/usr/bin/env python3
"""Primary exact audit for the centered global-energy context obstruction.

The witness is an exactly solvable tensor-product Gibbs family.  A local
transition is tensored with the identity on n remote two-level sites.  After
subtracting the full Gibbs mean from the shifted total energy, the remote
Binomial variance remains and grows linearly in n.  This is a route-local
topology obstruction only; it is not an interacting Q3 statement.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_centered_global_energy_context_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-centered-global-energy-context-obstruction-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"


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


def binomial_probability(n: int, m: int, ratio: Fraction) -> Fraction:
    return Fraction(comb(n, m)) * ratio**m / (1 + ratio) ** n


def moments(n: int, ratio: Fraction) -> tuple[Fraction, Fraction]:
    q = ratio / (1 + ratio)
    return Fraction(n) * q, Fraction(n) * q * (1 - q)


def context_rows(
    n: int,
    local_gap: Fraction,
    remote_gap: Fraction,
    ratio: Fraction,
    shift: Fraction,
    amplitude_squared: Fraction,
    centered: bool,
) -> dict[str, Fraction]:
    local_partition = 1 + ratio
    p0 = Fraction(1, 1) / local_partition
    p1 = ratio / local_partition
    local_mean = p1 * local_gap
    remote_mean, _ = moments(n, ratio)
    mean_k = shift + local_mean + remote_gap * remote_mean
    contexts = {key: Fraction(0) for key in ("D_row", "D_column", "Dstar_row", "Dstar_column")}
    for m in range(n + 1):
        probability = binomial_probability(n, m, ratio)
        remote_energy = remote_gap * m
        row_energy = shift + remote_energy
        column_energy = shift + local_gap + remote_energy
        if centered:
            row_energy -= mean_k
            column_energy -= mean_k
        contexts["D_row"] += p0 * probability * column_energy**2 * amplitude_squared
        contexts["D_column"] += p1 * probability * row_energy**2 * amplitude_squared
        contexts["Dstar_row"] += p1 * probability * row_energy**2 * amplitude_squared
        contexts["Dstar_column"] += p0 * probability * column_energy**2 * amplitude_squared
    return contexts


def centered_closed(
    n: int,
    local_target: Fraction,
    local_gap: Fraction,
    remote_gap: Fraction,
    ratio: Fraction,
    local_probability: Fraction,
    amplitude_squared: Fraction,
) -> Fraction:
    local_mean = ratio / (1 + ratio) * local_gap
    _, remote_variance = moments(n, ratio)
    q = ratio / (1 + ratio)
    return local_probability * amplitude_squared * (remote_gap**2 * remote_variance + (local_target - local_mean) ** 2)


def uncentered_closed(
    n: int,
    local_target: Fraction,
    local_gap: Fraction,
    remote_gap: Fraction,
    ratio: Fraction,
    shift: Fraction,
    local_probability: Fraction,
    amplitude_squared: Fraction,
) -> Fraction:
    mean, variance = moments(n, ratio)
    second = (shift + local_target) ** 2 + 2 * (shift + local_target) * remote_gap * mean + remote_gap**2 * (variance + mean**2)
    return local_probability * amplitude_squared * second


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

    local_partition = 1 + ratio
    p0 = Fraction(1, 1) / local_partition
    p1 = ratio / local_partition
    q = ratio / local_partition
    _, remote_variance_per_site = moments(1, ratio)
    slopes = {
        "D_row": p0 * amplitude_squared * remote_gap**2 * remote_variance_per_site,
        "D_column": p1 * amplitude_squared * remote_gap**2 * remote_variance_per_site,
        "Dstar_row": p1 * amplitude_squared * remote_gap**2 * remote_variance_per_site,
        "Dstar_column": p0 * amplitude_squared * remote_gap**2 * remote_variance_per_site,
    }
    rows: list[dict[str, Any]] = []
    for n in values:
        probability_mass = sum((binomial_probability(n, m, ratio) for m in range(n + 1)), Fraction(0))
        check(f"n={n} probability mass", probability_mass == 1, probability_mass, 1, "Gibbs tensor product")
        centered = context_rows(n, local_gap, remote_gap, ratio, shift, amplitude_squared, True)
        uncentered = context_rows(n, local_gap, remote_gap, ratio, shift, amplitude_squared, False)
        expected_centered = {
            "D_row": centered_closed(n, local_gap, local_gap, remote_gap, ratio, p0, amplitude_squared),
            "D_column": centered_closed(n, Fraction(0), local_gap, remote_gap, ratio, p1, amplitude_squared),
            "Dstar_row": centered_closed(n, Fraction(0), local_gap, remote_gap, ratio, p1, amplitude_squared),
            "Dstar_column": centered_closed(n, local_gap, local_gap, remote_gap, ratio, p0, amplitude_squared),
        }
        for key in centered:
            check(f"n={n} {key} closed formula", centered[key] == expected_centered[key], centered[key], expected_centered[key], "centered formula")
            check(f"n={n} {key} linear lower", centered[key] >= slopes[key] * n, centered[key], f">={slopes[key] * n}", "remote variance")
        expected_uncentered = uncentered_closed(n, local_gap, local_gap, remote_gap, ratio, shift, p0, amplitude_squared)
        check(f"n={n} uncentered D_row formula", uncentered["D_row"] == expected_uncentered, uncentered["D_row"], expected_uncentered, "uncentered comparison")
        for alternate_shift in (Fraction(0), shift, Fraction(7)):
            shifted_centered = context_rows(n, local_gap, remote_gap, ratio, alternate_shift, amplitude_squared, True)
            check(f"n={n} centered shift invariance {alternate_shift}", shifted_centered == centered, shifted_centered, centered, "centering")
        rows.append({
            "remote_sites": n,
            "centered_contexts": {key: str(value) for key, value in centered.items()},
            "uncentered_D_row": str(uncentered["D_row"]),
            "linear_lower_bounds": {key: str(slopes[key] * n) for key in slopes},
        })

    origin = context_rows(0, local_gap, remote_gap, ratio, shift, amplitude_squared, True)
    largest = context_rows(max(values), local_gap, remote_gap, ratio, shift, amplitude_squared, True)
    min_slope = min(slopes.values())
    check("positive centered slope", min_slope > 0, min_slope, ">0", "asymptotic obstruction")
    check("centered growth", largest["D_column"] > origin["D_column"], [largest["D_column"], origin["D_column"]], ">", "asymptotic obstruction")
    uncentered_n = uncentered_closed(max(values), local_gap, local_gap, remote_gap, ratio, shift, p0, amplitude_squared)
    uncentered_origin = uncentered_closed(0, local_gap, local_gap, remote_gap, ratio, shift, p0, amplitude_squared)
    quadratic_coefficient = p0 * amplitude_squared * (remote_gap * q) ** 2
    check("positive uncentered quadratic coefficient", quadratic_coefficient > 0, quadratic_coefficient, ">0", "uncentered comparison")
    check("uncentered comparison growth", uncentered_n > uncentered_origin, [uncentered_n, uncentered_origin], ">", "uncentered comparison")

    derived = {
        "rows": rows,
        "row_count": len(rows),
        "local_ground_probability": str(p0),
        "local_excited_probability": str(p1),
        "remote_excitation_probability": str(q),
        "centered_linear_slopes": {key: str(value) for key, value in slopes.items()},
        "minimum_centered_linear_slope": str(min_slope),
        "centered_D_row_at_origin": str(origin["D_row"]),
        "centered_D_row_at_largest_sample": str(largest["D_row"]),
        "uncentered_quadratic_coefficient": str(quadratic_coefficient),
        "centered_global_energy_uniformity_refuted": True,
        "actual_q3_interacting_uniformity_refuted": False,
        "local_energy_route_selected": True,
        "direct_d_delta_d_cauchy_closed": False,
        "modular_domain_transfer_closed": False,
        "common_unbounded_core_closed": False,
        "common_alpha_closed": False,
        "pre_a_closed": False,
    }
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CENTERED-GLOBAL-ENERGY-CONTEXT-VOLUME-OBSTRUCTION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
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
    print(f"PRIMARY CENTERED-GLOBAL-ENERGY-CONTEXT-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
