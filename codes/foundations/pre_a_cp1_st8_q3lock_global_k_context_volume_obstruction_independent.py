#!/usr/bin/env python3
"""Independent moment-formula lane for EXP-001146.

This lane does not enumerate remote configurations.  It derives all four
contexts from the first two moments of the Bernoulli excitation count.
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
SLUG = "pre_a_cp1_st8_q3lock_global_k_context_volume_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-global-k-context-volume-obstruction-manifest.json"
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


def f(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def affine_second_moment(base: Fraction, slope: Fraction, count_mean: Fraction, count_variance: Fraction) -> Fraction:
    return base**2 + 2 * base * slope * count_mean + slope**2 * (count_variance + count_mean**2)


def contexts_from_moments(n: int, local_gap: Fraction, remote_gap: Fraction, ratio: Fraction, shift: Fraction, amplitude_squared: Fraction) -> dict[str, Fraction]:
    local_partition = 1 + ratio
    p_row = Fraction(1, 1) / local_partition
    p_column = ratio / local_partition
    q = ratio / local_partition
    mean = Fraction(n) * q
    variance = Fraction(n) * q * (1 - q)
    row_second = affine_second_moment(shift, remote_gap, mean, variance)
    column_second = affine_second_moment(shift + local_gap, remote_gap, mean, variance)
    return {
        "A": p_row * amplitude_squared * row_second,
        "B": p_row * amplitude_squared * column_second,
        "C": p_column * amplitude_squared * row_second,
        "D": p_column * amplitude_squared * column_second,
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    local_gap, remote_gap = f(fixture["local_gap"]), f(fixture["remote_gap"])
    ratio, shift = f(fixture["gibbs_excited_weight_ratio"]), f(fixture["shift_constant"])
    amplitude_squared = f(fixture["amplitude_squared"])
    values = [int(n) for n in fixture["remote_site_values"]]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001146" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001146/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("moment inputs", local_gap > 0 and remote_gap > 0 and ratio > 0 and shift > 0 and amplitude_squared >= 0, [local_gap, remote_gap, ratio, shift, amplitude_squared], ">0 except amplitude square", "inputs")
    check("scope firewall", scope["exact_tensor_product_contexts_closed"] and scope["quadratic_lower_bound_closed"] and scope["global_k_volume_uniformity_refuted"] and not scope["actual_q3_interacting_uniformity_refuted"] and not scope["pre_a_closed"], scope, "product route-local obstruction", "scope")

    local_partition = 1 + ratio
    p_row = Fraction(1, 1) / local_partition
    q = ratio / local_partition
    coefficient = p_row * amplitude_squared * (remote_gap * q) ** 2
    rows: list[dict[str, Any]] = []
    for n in values:
        contexts = contexts_from_moments(n, local_gap, remote_gap, ratio, shift, amplitude_squared)
        formula_b = contexts["B"]
        lower_bound = coefficient * n**2
        check(f"n={n} context nonnegative", all(value >= 0 for value in contexts.values()), contexts, ">=0", "contexts")
        check(f"n={n} B quadratic lower", contexts["B"] >= lower_bound, contexts["B"], f">={lower_bound}", "quadratic obstruction")
        rows.append({"remote_sites": n, "contexts": {key: str(value) for key, value in contexts.items()}, "B_closed_formula": str(formula_b), "B_quadratic_lower_bound": str(lower_bound), "B_float": float(contexts["B"])})

    origin = contexts_from_moments(0, local_gap, remote_gap, ratio, shift, amplitude_squared)["B"]
    largest = contexts_from_moments(max(values), local_gap, remote_gap, ratio, shift, amplitude_squared)["B"]
    check("positive quadratic coefficient", coefficient > 0, coefficient, ">0", "asymptotic obstruction")
    check("sample growth", largest > origin, [largest, origin], ">", "asymptotic obstruction")
    check("local observable norm input", amplitude_squared == 1, amplitude_squared, 1, "locality")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-GLOBAL-K-CONTEXT-VOLUME-OBSTRUCTION",
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
            "local_row_probability": str(p_row),
            "remote_excitation_probability": str(q),
            "quadratic_coefficient": str(coefficient),
            "B_at_origin": str(origin),
            "B_at_largest_sample": str(largest),
            "exact_tensor_product_contexts_closed": True,
            "quadratic_lower_bound_closed": True,
            "global_k_volume_uniformity_refuted": True,
            "actual_q3_interacting_uniformity_refuted": False,
            "local_energy_weight_route_selected": True,
            "direct_d_delta_d_cauchy_closed": False,
            "modular_domain_transfer_closed": False,
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
    print(f"INDEPENDENT GLOBAL-K-CONTEXT-VOLUME-OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
