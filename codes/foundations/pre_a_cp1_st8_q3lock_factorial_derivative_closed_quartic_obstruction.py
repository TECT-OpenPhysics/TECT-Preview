#!/usr/bin/env python3
"""Primary exact audit for EXP-001118.

The package tests a factorial-weighted coefficient seminorm.  It proves an
algebraic derivative identity and then tests the positive absolute-value
top-monomial branch of the registered quartic source.  The branch is a route
envelope, not the signed full Q3 commutator history.
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

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_factorial_derivative_closed_quartic_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-factorial-derivative-closed-quartic-obstruction-manifest.json"
SOURCE_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-source-coefficient-product-manifest.json"
MIXED_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, (sp.Basic, Fraction)):
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


def source_polynomials() -> tuple[sp.Expr, sp.Expr]:
    fixture = json.loads(MANIFEST.read_text(encoding="utf-8"))["fixture"]
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    rate_fixture = json.loads(MIXED_MANIFEST.read_text(encoding="utf-8"))["fixture"]
    lam = sp.Rational(str(rate_fixture["lambda"]))
    onsite_coupling = sp.Rational(str(fixture["onsite_coupling"]))
    coupling = sp.Rational(str(rate_fixture["spatial_coupling"]))
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
    return center, reverse


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001118" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001118/T-054", "provenance")
    check("upstream identity", source_manifest["exploration_id"] == "EXP-001050", source_manifest["exploration_id"], "EXP-001050", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    center, reverse = source_polynomials()
    q, v, a = sp.symbols("q v a")
    center_top = sp.Poly(center, q, v, a).coeff_monomial(a**4)
    reverse_top = sp.Poly(reverse, q, v, a).coeff_monomial(a**4)
    expected_abs = sp.Rational(str(fixture["top_coefficient_abs"]))
    check("center top coefficient", abs(center_top) == expected_abs, center_top, f"abs={expected_abs}", "source polynomial")
    check("reverse top coefficient", abs(reverse_top) == expected_abs, reverse_top, f"abs={expected_abs}", "orientation")
    check("source degree", max(m[2] for m, _ in sp.Poly(center, q, v, a).terms()) == int(manifest["scope"].get("expected_source_degree", 4)), max(m[2] for m, _ in sp.Poly(center, q, v, a).terms()), 4, "source polynomial")

    S = sp.Rational(str(fixture["source_radius"]))
    S_prime = sp.Rational(str(fixture["reduced_source_radius"]))
    c = expected_abs
    branch = int(fixture["comparison_base"])
    n0 = int(fixture["witness_initial_degree"])
    check("radius order", 0 < S_prime < S, [S_prime, S], "0<S'<S", "radius")
    check("factorial derivative closure", (sp.Integer(n0) * sp.factorial(n0 - 1) * S ** (n0 - 1)) / (sp.factorial(n0) * S**n0) == 1 / S, 1 / S, "1/S", "derivative")

    rows: list[dict[str, Any]] = []
    for m in [int(value) for value in fixture["orders"]]:
        coefficient = c**m * sp.prod(n0 + 3 * j for j in range(m))
        degree = n0 + 3 * m
        ratio = sp.factor(coefficient * sp.factorial(degree) * S_prime**degree / (sp.factorial(n0) * S**n0))
        lower = sp.factor(c**m * (sp.Integer(m) ** (2 * m)) * S_prime**degree / S)
        check(f"recurrence m={m}", degree == n0 + 3 * m and coefficient == c**m * sp.prod(n0 + 3 * j for j in range(m)), [degree, coefficient], "exact recurrence", "recurrence")
        check(f"factorial lower bound m={m}", sp.factorial(degree) >= sp.Integer(m) ** (2 * m), [sp.factorial(degree), sp.Integer(m) ** (2 * m)], ">=", "asymptotic")
        rows.append({"m": m, "degree": degree, "coefficient": coefficient, "input_norm": sp.factorial(n0) * S**n0, "output_norm": coefficient * sp.factorial(degree) * S_prime**degree, "norm_ratio": ratio, "factorial_lower_bound": lower, "comparison_base_power": sp.Integer(branch) ** m, "exceeds_comparison_base": ratio > sp.Integer(branch) ** m})

    witness = next(row for row in rows if row["m"] == int(fixture["small_exact_witness_order"]))
    check("order-sixteen witness", witness["norm_ratio"] > sp.Integer(branch) ** witness["m"], witness["norm_ratio"], f">{branch}^{witness['m']}", "boundary")
    check("orientation symmetry", center_top == reverse_top, [center_top, reverse_top], "equal", "orientation")
    check("scope firewall", manifest["scope"]["factorial_derivative_closure_closed"] and manifest["scope"]["repeated_top_monomial_exponential_envelope_refuted"] and not manifest["scope"]["actual_q3_common_core_map_proved"] and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "route boundary / Q3 open", "scope")

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
            "center_top_coefficient": center_top,
            "reverse_top_coefficient": reverse_top,
            "top_coefficient_absolute": expected_abs,
            "source_radius": S,
            "reduced_source_radius": S_prime,
            "derivative_closure_constant": 1 / S,
            "comparison_base": branch,
            "ratio_rows": rows,
            "order_sixteen_ratio": witness["norm_ratio"],
            "factorial_derivative_closed": True,
            "repeated_top_monomial_exponential_envelope_refuted": True,
            "actual_q3_common_core_map_proved": False,
            "actual_q3_history_closed": False,
            "common_alpha_closed": False
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
            "source_manifest": str(SOURCE_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "source_manifest_sha256": sha256(SOURCE_MANIFEST)
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FACTORIAL-QUARTIC-OBSTRUCTION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
