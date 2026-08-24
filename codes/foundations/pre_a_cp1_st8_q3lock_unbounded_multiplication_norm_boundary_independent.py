#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001052."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-unbounded-multiplication-norm-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-operator-evaluation-map-contract-manifest.json"
FIXTURE = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "independent.json"
Poly = dict[tuple[int, ...], F]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def clean_poly(poly: Poly) -> Poly:
    return {monomial: coefficient for monomial, coefficient in poly.items() if coefficient}


def add(*polys: Poly) -> Poly:
    result: Poly = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] = result.get(monomial, F(0)) + coefficient
    return clean_poly(result)


def scale(poly: Poly, coefficient: F) -> Poly:
    return clean_poly({monomial: coefficient * value for monomial, value in poly.items()})


def mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(a + b for a, b in zip(left_monomial, right_monomial))
            result[monomial] = result.get(monomial, F(0)) + left_coefficient * right_coefficient
    return clean_poly(result)


def power(poly: Poly, exponent: int) -> Poly:
    result = {(0,) * len(next(iter(poly))): F(1)}
    for _ in range(exponent):
        result = mul(result, poly)
    return result


def variable(index: int, dimension: int = 3) -> Poly:
    monomial = [0] * dimension
    monomial[index] = 1
    return {tuple(monomial): F(1)}


def evaluate(poly: Poly, point: tuple[F, ...]) -> F:
    return sum(coefficient * math.prod(value**degree for value, degree in zip(point, monomial)) for monomial, coefficient in poly.items())


def slice_coefficients(poly: Poly, source_value: F) -> dict[int, F]:
    result: dict[int, F] = {}
    for (q_degree, v_degree, a_degree), coefficient in poly.items():
        if v_degree == 0:
            result[q_degree] = result.get(q_degree, F(0)) + coefficient * source_value**a_degree
    return {degree: coefficient for degree, coefficient in result.items() if coefficient}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001052" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001052/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001051", upstream["exploration_id"], "EXP-001051", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    lam = F(fixture["lambda"])
    coupling = F(fixture["spatial_coupling"])
    q, v, a = variable(0), variable(1), variable(2)
    q_minus_v = add(q, scale(v, F(-1)))
    q_minus_a = add(q, scale(a, F(-1)))
    q_minus_a_minus_v = add(q, scale(a, F(-1)), scale(v, F(-1)))
    edge = scale(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), lam / 4)
    edge_u = add(edge, scale(scale(mul(power(q_minus_a_minus_v, 2), add(power(q_minus_a, 2), power(v, 2))), lam / 4), F(-1)))
    bond = scale(power(q_minus_v, 2), coupling / 2)
    bond_u = add(bond, scale(scale(power(q_minus_a_minus_v, 2), coupling / 2), F(-1)))
    onsite = scale(add(power(q, 4), scale(power(q_minus_a, 4), F(-1))), F(3, 20))
    P = add(onsite, scale(edge_u, F(3)), scale(bond_u, F(6)))
    slice_coeffs = slice_coefficients(P, F(1, 4))
    expected_lead = F(manifest["slice_polynomial"]["leading_coefficient"])
    check("slice degree", max(slice_coeffs) == 3, max(slice_coeffs), 3, "slice")
    check("slice leading coefficient", slice_coeffs[3] == expected_lead, slice_coeffs[3], expected_lead, "slice")
    check("positive cubic limit", slice_coeffs[3] > 0, slice_coeffs[3], ">0", "growth")
    q_values = [F(value) for value in manifest["finite_fixture"]["q_values"]]
    expected_values = [F(value) for value in manifest["finite_fixture"]["values"]]
    values = [evaluate(P, (value, F(0), F(1, 4))) for value in q_values]
    for index, (value, expected) in enumerate(zip(values, expected_values)):
        check(f"slice value q={q_values[index]}", value == expected, value, expected, "growth")
    for left, right in zip(values, values[1:]):
        check("finite growth step", right > left, [left, right], "strictly increasing", "growth")
    B = F(manifest["finite_fixture"]["coefficient_rate_B"])
    check("finite value exceeds coefficient rate", values[-2] > B, values[-2], f">{B}", "boundary")
    check("ordinary norm architecture boundary", manifest["scope"]["ordinary_global_operator_bound_closed"] is False and manifest["scope"]["energy_weighted_bound_proved"] is False, manifest["scope"], "ordinary open; weighted target", "boundary")
    check("QFT scope", manifest["scope"]["actual_q3_common_core_map_proved"] is False and manifest["scope"]["kms_os_closed"] is False and manifest["scope"]["continuum_closed"] is False, manifest["scope"], "conditional/open", "scope")
    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": checks,
        "derived": {
            "slice_coefficients": slice_coeffs, "slice_degree": max(slice_coeffs), "leading_coefficient": slice_coeffs[3],
            "q_values_checked": len(q_values), "ordinary_multiplication_growth_checked": True, "ordinary_global_operator_bound_closed": False,
            "energy_weighted_bound_proved": False, "actual_q3_common_core_map_proved": False, "factorial_incidence_supplied": False,
            "actual_q3_history_closed": False, "common_alpha_closed": False
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST), "upstream_manifest_sha256": sha256(UPSTREAM), "fixture_manifest_sha256": sha256(FIXTURE)},
        "exploration_id": manifest["exploration_id"], "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT Q3-UNBOUNDED-MULTIPLICATION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
