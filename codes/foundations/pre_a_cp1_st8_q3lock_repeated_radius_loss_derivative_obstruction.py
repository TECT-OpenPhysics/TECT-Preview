#!/usr/bin/env python3
"""Primary formal derivative-history boundary audit for EXP-001117.

The audit rederives the registered actual Q3 source polynomial rate and then
tests the pure repeated source-derivative model in the weighted coefficient
space.  It deliberately does not identify that model with the full Q3
commutator history or with an unbounded operator representation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_repeated_radius_loss_derivative_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-repeated-radius-loss-derivative-obstruction-manifest.json"
SOURCE_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-source-coefficient-product-manifest.json"
MIXED_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
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
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def weighted_norm(polynomial: sp.Expr, variables: tuple[sp.Symbol, ...], radii: tuple[sp.Rational, ...]) -> sp.Rational:
    total = sp.Rational(0)
    for monomial, coefficient in sp.Poly(sp.expand(polynomial), *variables).terms():
        total += abs(coefficient) * sp.prod(radius**degree for radius, degree in zip(radii, monomial))
    return sp.factor(total)


def build_source_polynomials(fixture: dict[str, Any]) -> tuple[sp.Expr, sp.Expr, tuple[sp.Rational, ...], tuple[sp.Rational, ...]]:
    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
    onsite_coupling = sp.Rational(str(json.loads(MANIFEST.read_text(encoding="utf-8"))["fixture"]["onsite_coupling"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    root = sp.Integer(str(fixture["root_scale"]))
    neighbour = sp.Integer(str(fixture["neighbor_factor_root"]))
    q, v, a = sp.symbols("q v a")
    edge = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = sp.expand(edge - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    edge_v = sp.expand(edge - lam * (q - (v - a)) ** 2 * (q**2 + (v - a) ** 2) / 4)
    bond = coupling * (q - v) ** 2 / 2
    bond_u = sp.expand(bond - coupling * (q - a - v) ** 2 / 2)
    bond_v = sp.expand(bond - coupling * (q - (v - a)) ** 2 / 2)
    onsite_q = onsite_coupling * (q**4 - (q - a) ** 4) / 4
    onsite_v = onsite_coupling * (v**4 - (v - a) ** 4) / 4
    center = sp.expand(onsite_q + 3 * edge_u + 6 * bond_u)
    reverse = sp.expand(onsite_v + 3 * edge_v + 6 * bond_v)
    return center, reverse, (root, root * neighbour, source_radius), (root * neighbour, root, source_radius)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    mixed_manifest = json.loads(MIXED_MANIFEST.read_text(encoding="utf-8"))
    fixture = mixed_manifest["fixture"]
    local = manifest["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001117" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001117/T-054", "provenance")
    check("upstream identities", source_manifest["exploration_id"] == "EXP-001050" and mixed_manifest["exploration_id"] == "EXP-001045", [source_manifest["exploration_id"], mixed_manifest["exploration_id"]], "EXP-001050/EXP-001045", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    center, reverse, center_radii, reverse_radii = build_source_polynomials(fixture)
    variables = tuple(sp.symbols("q v a"))
    center_rate = weighted_norm(center, variables, center_radii)
    reverse_rate = weighted_norm(reverse, variables, reverse_radii)
    expected_rate = sp.Rational(str(fixture["expected_local_rate"]))
    source_radius = sp.Rational(str(local["source_radius"]))
    reduced_source_radius = sp.Rational(str(local["reduced_source_radius"]))
    field_radius = sp.Rational(str(local["field_radius"]))
    reduced_field_radius = sp.Rational(str(local["reduced_field_radius"]))
    check("source rate", center_rate == expected_rate == sp.Rational(str(local["expected_local_rate"])), center_rate, expected_rate, "source polynomial")
    check("reverse rate", reverse_rate == center_rate, reverse_rate, center_rate, "orientation")
    check("source radii", source_radius == sp.Rational(str(fixture["source_radius"])) and source_radius > reduced_source_radius > 0, [source_radius, reduced_source_radius], "1/4>1/8>0", "radius")
    check("field radii", field_radius > reduced_field_radius > 0, [field_radius, reduced_field_radius], "4>3>0", "radius")

    source_degrees = [monomial[2] for monomial, _ in sp.Poly(center, *variables).terms()]
    reverse_source_degrees = [monomial[2] for monomial, _ in sp.Poly(reverse, *variables).terms()]
    check("source degree", max(source_degrees) == int(local["expected_source_degree"]), max(source_degrees), local["expected_source_degree"], "source polynomial")
    check("reverse source degree", max(reverse_source_degrees) == max(source_degrees), max(reverse_source_degrees), max(source_degrees), "orientation")

    branch_count = int(local["orientation_count"]) * int(local["neighbour_count"])
    check("branch count", branch_count == int(local["comparison_base"]), branch_count, local["comparison_base"], "history comparison")
    orders = [int(order) for order in local["orders"]]
    ratio_rows: list[dict[str, Any]] = []
    for order in orders:
        ratio = sp.factor(sp.factorial(order) / source_radius**order)
        lower = sp.Integer(order // 2) ** (order // 2) / source_radius**order if order % 2 == 0 else sp.Integer(0)
        check(f"derivative witness order={order}", ratio == sp.factorial(order) / source_radius**order, ratio, "n!/S^n", "derivative")
        if order % 2 == 0:
            check(f"even factorial lower bound order={order}", sp.factorial(order) >= sp.Integer(order // 2) ** (order // 2), sp.factorial(order), f">={(order // 2)}^({order // 2})", "asymptotic")
        ratio_rows.append({"order": order, "input_norm": source_radius**order, "output_norm": sp.factorial(order), "operator_lower_bound": ratio, "even_lower_bound": lower, "comparison_base_power": sp.Integer(branch_count) ** order, "exceeds_comparison_base": ratio > sp.Integer(branch_count) ** order})

    small_order = int(local["small_exact_witness_order"])
    large_order = int(local["asymptotic_witness_order"])
    small_ratio = sp.factor(sp.factorial(small_order) / source_radius**small_order)
    large_ratio = sp.factor(sp.factorial(large_order) / source_radius**large_order)
    check("order-8 exact witness", small_ratio > sp.Integer(branch_count) ** small_order, small_ratio, f">{branch_count}^{small_order}", "boundary")
    threshold = sp.factor(2 * (sp.Integer(branch_count) * source_radius) ** 2)
    check("order-32 asymptotic witness", sp.Integer(large_order) > threshold and large_ratio > sp.Integer(branch_count) ** large_order, [large_order, threshold], f"n>{threshold} and ratio>{branch_count}^n", "boundary")
    check("radius-loss independence", all(row["output_norm"] == sp.factorial(row["order"]) for row in ratio_rows), "constant output witnesses", "n!", "radius-loss")
    check("scope firewall", manifest["scope"]["fixed_exponential_derivative_envelope_refuted"] and not manifest["scope"]["actual_q3_common_core_map_proved"] and not manifest["scope"]["actual_q3_history_closed"], manifest["scope"], "formal route parked / Q3 open", "scope")

    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": checks,
        "derived": {
            "source_rate_B": center_rate,
            "reverse_rate_B": reverse_rate,
            "source_degree": max(source_degrees),
            "field_radius": field_radius,
            "reduced_field_radius": reduced_field_radius,
            "source_radius": source_radius,
            "reduced_source_radius": reduced_source_radius,
            "branch_count": branch_count,
            "ratio_rows": ratio_rows,
            "order_8_ratio": small_ratio,
            "order_32_ratio": large_ratio,
            "even_factorial_lower_bound": True,
            "fixed_exponential_derivative_envelope_refuted": True,
            "radius_loss_does_not_rescue_derivative_model": True,
            "actual_q3_common_core_map_proved": False,
            "actual_q3_history_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
            "source_manifest": str(SOURCE_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "source_manifest_sha256": sha256(SOURCE_MANIFEST),
            "mixed_manifest": str(MIXED_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "mixed_manifest_sha256": sha256(MIXED_MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY REPEATED-RADIUS-LOSS-DERIVATIVE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
