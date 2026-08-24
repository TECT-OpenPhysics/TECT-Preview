#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001054."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-multivariate-energy-weighted-source-bound"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-scalar-energy-weighted-slice-bound-manifest.json"
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


def weighted_majorant(poly: Poly, source_radius: F) -> tuple[F, int, int]:
    total = F(0)
    max_field_degree = 0
    max_source_degree = 0
    for monomial, coefficient in poly.items():
        field_degree = sum(monomial[:2])
        source_degree = monomial[2]
        max_field_degree = max(max_field_degree, field_degree)
        max_source_degree = max(max_source_degree, source_degree)
        total += abs(coefficient) * source_radius**source_degree
    return total, max_field_degree, max_source_degree


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001054" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001054/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001053", upstream["exploration_id"], "EXP-001053", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    lam = F(fixture["lambda"])
    coupling = F(fixture["spatial_coupling"])
    source_radius = F(fixture["source_radius"])
    q, v, a = variable(0), variable(1), variable(2)
    q_minus_v = add(q, scale(v, F(-1)))
    q_minus_a = add(q, scale(a, F(-1)))
    v_minus_a = add(v, scale(a, F(-1)))
    q_minus_a_minus_v = add(q, scale(a, F(-1)), scale(v, F(-1)))
    v_minus_a_minus_q = add(v, scale(a, F(-1)), scale(q, F(-1)))
    edge = scale(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), lam / 4)
    edge_u = add(edge, scale(scale(mul(power(q_minus_a_minus_v, 2), add(power(q_minus_a, 2), power(v, 2))), lam / 4), F(-1)))
    edge_v = add(edge, scale(scale(mul(power(add(q, scale(v, F(-1)), a), 2), add(power(q, 2), power(v_minus_a, 2))), lam / 4), F(-1)))
    bond = scale(power(q_minus_v, 2), coupling / 2)
    bond_u = add(bond, scale(scale(power(q_minus_a_minus_v, 2), coupling / 2), F(-1)))
    bond_v = add(bond, scale(scale(power(add(q, scale(v, F(-1)), a), 2), coupling / 2), F(-1)))
    onsite_q = scale(add(power(q, 4), scale(power(q_minus_a, 4), F(-1))), F(3, 20))
    onsite_v = scale(add(power(v, 4), scale(power(v_minus_a, 4), F(-1))), F(3, 20))
    P = add(onsite_q, scale(edge_u, F(3)), scale(bond_u, F(6)))
    P_reverse = add(onsite_v, scale(edge_v, F(3)), scale(bond_v, F(6)))
    center_C, center_field, center_source = weighted_majorant(P, source_radius)
    reverse_C, reverse_field, reverse_source = weighted_majorant(P_reverse, source_radius)
    expected_C = F(manifest["weighted_target"]["majorant_center"].split("=")[-1])
    check("center coefficient majorant", center_C == expected_C, center_C, expected_C, "weight")
    check("reverse coefficient majorant", reverse_C == expected_C, reverse_C, expected_C, "orientation")
    check("orientation equality", reverse_C == center_C, [center_C, reverse_C], "equal", "orientation")
    check("field degree bound", center_field <= 3 and reverse_field <= 3, [center_field, reverse_field], "<=3", "weight")
    check("source degree bound", center_source <= 4 and reverse_source <= 4, [center_source, reverse_source], "<=4", "weight")
    check("source radius", source_radius == F(1, 4), source_radius, "1/4", "model")
    fields = tuple(F(value) for value in manifest["finite_fixture"]["field_values"])
    sources = tuple(F(value) for value in manifest["finite_fixture"]["source_values"])
    grid_rows: list[dict[str, Any]] = []
    for q_value, v_value, a_value in itertools.product(fields, fields, sources):
        energy = 1 + q_value**4 + v_value**4
        center_value = evaluate(P, (q_value, v_value, a_value))
        reverse_value = evaluate(P_reverse, (q_value, v_value, a_value))
        bound_power = center_C**4 * energy**3
        check(f"center weighted grid {q_value},{v_value},{a_value}", abs(center_value) ** 4 <= bound_power, center_value, "fourth-power bound", "grid")
        check(f"reverse weighted grid {q_value},{v_value},{a_value}", abs(reverse_value) ** 4 <= bound_power, reverse_value, "fourth-power bound", "grid")
        grid_rows.append({"q": q_value, "v": v_value, "a": a_value, "center": center_value, "reverse": reverse_value, "energy": energy, "bound_power": bound_power})
    check("grid cardinality", len(grid_rows) == manifest["finite_fixture"]["grid_points"], len(grid_rows), manifest["finite_fixture"]["grid_points"], "grid")
    check("scalar/open scope", manifest["scope"]["multivariate_scalar_majorant_closed"] is True and manifest["scope"]["actual_q3_common_core_map_proved"] is False and manifest["scope"]["weighted_product_bound_proved"] is False, manifest["scope"], "pointwise/open", "scope")
    check("QFT scope", manifest["scope"]["factorial_incidence_supplied"] is False and manifest["scope"]["kms_os_closed"] is False and manifest["scope"]["continuum_closed"] is False, manifest["scope"], "conditional/open", "scope")
    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": checks, "grid_rows": grid_rows,
        "derived": {
            "center_C": center_C, "reverse_C": reverse_C, "max_field_degree": max(center_field, reverse_field), "max_source_degree": max(center_source, reverse_source),
            "grid_points": len(grid_rows), "multivariate_scalar_majorant_closed": True, "both_orientations_checked": True,
            "actual_q3_common_core_map_proved": False, "operator_domain_closure_proved": False, "weighted_product_bound_proved": False,
            "factorial_incidence_supplied": False, "actual_q3_history_closed": False, "common_alpha_closed": False
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
    print(f"INDEPENDENT Q3-MULTIVARIATE-ENERGY-WEIGHT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
