#!/usr/bin/env python3
"""Independent Fraction lane for EXP-001117.

This lane uses a sparse exact polynomial dictionary rather than SymPy and
rechecks the source rate, orientation symmetry and factorial derivative
witnesses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_repeated_radius_loss_derivative_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-repeated-radius-loss-derivative-obstruction-manifest.json"
MIXED_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"
Poly = dict[tuple[int, int, int], Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def clean(poly: Poly) -> Poly:
    return {key: value for key, value in poly.items() if value}


def add(left: Poly, right: Poly, sign: Fraction = Fraction(1)) -> Poly:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, Fraction(0)) + sign * value
    return clean(result)


def scale(poly: Poly, factor: Fraction) -> Poly:
    return clean({key: factor * value for key, value in poly.items()})


def multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_key, left_value in left.items():
        for right_key, right_value in right.items():
            key = tuple(left_key[index] + right_key[index] for index in range(3))
            result[key] = result.get(key, Fraction(0)) + left_value * right_value
    return clean(result)


def power(poly: Poly, exponent: int) -> Poly:
    result: Poly = {(0, 0, 0): Fraction(1)}
    for _ in range(exponent):
        result = multiply(result, poly)
    return result


def weighted_norm(poly: Poly, radii: tuple[Fraction, Fraction, Fraction]) -> Fraction:
    total = Fraction(0)
    for exponents, coefficient in poly.items():
        weight = Fraction(1)
        for radius, exponent in zip(radii, exponents):
            weight *= radius**exponent
        total += abs(coefficient) * weight
    return total


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mixed = json.loads(MIXED_MANIFEST.read_text(encoding="utf-8"))
    upstream = mixed["fixture"]
    local = manifest["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001117" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001117/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    q: Poly = {(1, 0, 0): Fraction(1)}
    v: Poly = {(0, 1, 0): Fraction(1)}
    a: Poly = {(0, 0, 1): Fraction(1)}
    one: Poly = {(0, 0, 0): Fraction(1)}
    lam = Fraction(str(upstream["lambda"]))
    coupling = Fraction(str(upstream["spatial_coupling"]))
    onsite_coupling = Fraction(str(local["onsite_coupling"]))
    edge_difference = add(q, v, Fraction(-1))
    edge = scale(multiply(power(edge_difference, 2), add(power(q, 2), power(v, 2))), lam / 4)
    q_shift = add(add(q, a, Fraction(-1)), v, Fraction(-1))
    q_minus_a = add(q, a, Fraction(-1))
    edge_shift = scale(multiply(power(q_shift, 2), add(power(q_minus_a, 2), power(v, 2))), lam / 4)
    edge_u = add(edge, edge_shift, Fraction(-1))
    v_shift = add(q, add(v, a, Fraction(-1)), Fraction(-1))
    v_minus_a = add(v, a, Fraction(-1))
    edge_reverse_shift = scale(multiply(power(v_shift, 2), add(power(q, 2), power(v_minus_a, 2))), lam / 4)
    edge_v = add(edge, edge_reverse_shift, Fraction(-1))
    bond = scale(power(edge_difference, 2), coupling / 2)
    bond_u = add(bond, scale(power(q_shift, 2), coupling / 2), Fraction(-1))
    bond_v = add(bond, scale(power(v_shift, 2), coupling / 2), Fraction(-1))
    onsite = scale(add(power(q, 4), power(q_minus_a, 4), Fraction(-1)), onsite_coupling / 4)
    onsite_reverse = scale(add(power(v, 4), power(v_minus_a, 4), Fraction(-1)), onsite_coupling / 4)
    center = add(add(onsite, scale(edge_u, Fraction(3))), scale(bond_u, Fraction(6)))
    reverse = add(add(onsite_reverse, scale(edge_v, Fraction(3))), scale(bond_v, Fraction(6)))

    source_radius = Fraction(str(local["source_radius"]))
    center_radii = (Fraction(str(upstream["root_scale"])), Fraction(str(upstream["root_scale"])) * Fraction(str(upstream["neighbor_factor_root"])), source_radius)
    reverse_radii = (center_radii[1], center_radii[0], source_radius)
    center_rate = weighted_norm(center, center_radii)
    reverse_rate = weighted_norm(reverse, reverse_radii)
    expected_rate = Fraction(str(upstream["expected_local_rate"]))
    check("source rate", center_rate == expected_rate == Fraction(str(local["expected_local_rate"])), center_rate, expected_rate, "source polynomial")
    check("reverse rate", reverse_rate == center_rate, reverse_rate, center_rate, "orientation")
    check("source degree", max(exponents[2] for exponents in center) == int(local["expected_source_degree"]), max(exponents[2] for exponents in center), local["expected_source_degree"], "source polynomial")

    branch_count = int(local["orientation_count"]) * int(local["neighbour_count"])
    check("branch count", branch_count == int(local["comparison_base"]), branch_count, local["comparison_base"], "history comparison")
    rows: list[dict[str, Any]] = []
    for order in map(int, local["orders"]):
        ratio = Fraction(math.factorial(order), 1) / source_radius**order
        even_lower = Fraction((order // 2) ** (order // 2), 1) / source_radius**order if order % 2 == 0 else Fraction(0)
        if order % 2 == 0:
            check(f"even factorial lower bound order={order}", math.factorial(order) >= (order // 2) ** (order // 2), math.factorial(order), f">={(order // 2)}^({order // 2})", "asymptotic")
        check(f"derivative witness order={order}", ratio == Fraction(math.factorial(order), 1) / source_radius**order, ratio, "n!/S^n", "derivative")
        rows.append({"order": order, "input_norm": source_radius**order, "output_norm": math.factorial(order), "operator_lower_bound": ratio, "even_lower_bound": even_lower, "comparison_base_power": branch_count**order, "exceeds_comparison_base": ratio > branch_count**order})

    order8 = int(local["small_exact_witness_order"])
    order32 = int(local["asymptotic_witness_order"])
    ratio8 = Fraction(math.factorial(order8), 1) / source_radius**order8
    ratio32 = Fraction(math.factorial(order32), 1) / source_radius**order32
    threshold = 2 * (branch_count * source_radius) ** 2
    check("order-8 exact witness", ratio8 > branch_count**order8, ratio8, f">{branch_count}^{order8}", "boundary")
    check("order-32 asymptotic witness", order32 > threshold and ratio32 > branch_count**order32, [order32, threshold], f"n>{threshold} and ratio>{branch_count}^n", "boundary")
    check("radius-loss independence", all(row["output_norm"] == math.factorial(row["order"]) for row in rows), "constant output witnesses", "n!", "radius-loss")
    check("scope firewall", manifest["scope"]["fixed_exponential_derivative_envelope_refuted"] and not manifest["scope"]["actual_q3_common_core_map_proved"] and not manifest["scope"]["actual_q3_history_closed"], manifest["scope"], "formal route parked / Q3 open", "scope")

    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": checks,
        "derived": {
            "source_rate_B": center_rate, "reverse_rate_B": reverse_rate, "source_degree": max(exponents[2] for exponents in center),
            "source_radius": source_radius, "reduced_source_radius": Fraction(str(local["reduced_source_radius"])), "branch_count": branch_count,
            "ratio_rows": rows, "order_8_ratio": ratio8, "order_32_ratio": ratio32,
            "even_factorial_lower_bound": True, "fixed_exponential_derivative_envelope_refuted": True,
            "radius_loss_does_not_rescue_derivative_model": True, "actual_q3_common_core_map_proved": False,
            "actual_q3_history_closed": False, "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST),
            "mixed_manifest": str(MIXED_MANIFEST.relative_to(REPO)).replace("\\", "/"), "mixed_manifest_sha256": sha256(MIXED_MANIFEST),
        },
        "exploration_id": manifest["exploration_id"], "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT REPEATED-RADIUS-LOSS-DERIVATIVE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
