#!/usr/bin/env python3
"""Primary exact audit for EXP-001054.

The actual Q3 source and its reverse orientation receive a pointwise
multivariate energy-weighted coefficient majorant.  This remains a commuting
scalar interface, not an unbounded-operator history theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-multivariate-energy-weighted-source-bound"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-scalar-energy-weighted-slice-bound-manifest.json"
FIXTURE = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
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


def weighted_majorant(polynomial: sp.Poly, source_radius: sp.Rational) -> tuple[sp.Rational, int, int]:
    total = sp.Rational(0)
    max_field_degree = 0
    max_source_degree = 0
    for monomial, coefficient in polynomial.terms():
        field_degree = sum(monomial[:2])
        source_degree = monomial[2]
        max_field_degree = max(max_field_degree, field_degree)
        max_source_degree = max(max_source_degree, source_degree)
        total += abs(coefficient) * source_radius**source_degree
    return sp.factor(total), max_field_degree, max_source_degree


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001054" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001054/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001053", upstream["exploration_id"], "EXP-001053", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("weighted target", manifest["weighted_target"]["energy"] == "A(q,v)=1+q^4+v^4" and manifest["weighted_target"]["exponent"] == "3/4", manifest["weighted_target"], "A(q,v), 3/4", "model")

    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    q, v, a = sp.symbols("q v a")
    edge = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = sp.expand(edge - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    edge_v = sp.expand(edge - lam * (q - (v - a)) ** 2 * (q**2 + (v - a) ** 2) / 4)
    bond = coupling * (q - v) ** 2 / 2
    bond_u = sp.expand(bond - coupling * (q - a - v) ** 2 / 2)
    bond_v = sp.expand(bond - coupling * (q - (v - a)) ** 2 / 2)
    onsite_q = sp.Rational(3, 5) * (q**4 - (q - a) ** 4) / 4
    onsite_v = sp.Rational(3, 5) * (v**4 - (v - a) ** 4) / 4
    P = sp.Poly(sp.expand(onsite_q + 3 * edge_u + 6 * bond_u), q, v, a)
    P_reverse = sp.Poly(sp.expand(onsite_v + 3 * edge_v + 6 * bond_v), q, v, a)
    C, field_degree, source_degree = weighted_majorant(P, source_radius)
    C_reverse, reverse_field_degree, reverse_source_degree = weighted_majorant(P_reverse, source_radius)
    expected_C = sp.Rational(manifest["weighted_target"]["majorant_center"].split("=")[-1])
    check("center coefficient majorant", C == expected_C, C, expected_C, "weight")
    check("reverse coefficient majorant", C_reverse == expected_C, C_reverse, expected_C, "orientation")
    check("orientation equality", C_reverse == C, [C, C_reverse], "equal", "orientation")
    check("field degree bound", field_degree <= 3 and reverse_field_degree <= 3, [field_degree, reverse_field_degree], "<=3", "weight")
    check("source degree bound", source_degree <= 4 and reverse_source_degree <= 4, [source_degree, reverse_source_degree], "<=4", "weight")
    check("source radius", source_radius == sp.Rational(1, 4), source_radius, "1/4", "model")

    fields = tuple(sp.Rational(value) for value in manifest["finite_fixture"]["field_values"])
    sources = tuple(sp.Rational(value) for value in manifest["finite_fixture"]["source_values"])
    grid_rows: list[dict[str, Any]] = []
    for q_value, v_value, a_value in itertools.product(fields, fields, sources):
        energy = 1 + q_value**4 + v_value**4
        center_value = sp.factor(P.as_expr().subs({q: q_value, v: v_value, a: a_value}))
        reverse_value = sp.factor(P_reverse.as_expr().subs({q: q_value, v: v_value, a: a_value}))
        bound_power = C**4 * energy**3
        check(f"center weighted grid {q_value},{v_value},{a_value}", abs(center_value) ** 4 <= bound_power, center_value, "fourth-power bound", "grid")
        check(f"reverse weighted grid {q_value},{v_value},{a_value}", abs(reverse_value) ** 4 <= bound_power, reverse_value, "fourth-power bound", "grid")
        grid_rows.append({"q": q_value, "v": v_value, "a": a_value, "center": center_value, "reverse": reverse_value, "energy": energy, "bound_power": bound_power})
    check("grid cardinality", len(grid_rows) == manifest["finite_fixture"]["grid_points"], len(grid_rows), manifest["finite_fixture"]["grid_points"], "grid")
    check("scalar/open scope", manifest["scope"]["multivariate_scalar_majorant_closed"] is True and manifest["scope"]["actual_q3_common_core_map_proved"] is False and manifest["scope"]["weighted_product_bound_proved"] is False, manifest["scope"], "pointwise/open", "scope")
    check("QFT scope", manifest["scope"]["factorial_incidence_supplied"] is False and manifest["scope"]["kms_os_closed"] is False and manifest["scope"]["continuum_closed"] is False, manifest["scope"], "conditional/open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit, "grid_rows": grid_rows,
        "derived": {
            "center_C": C, "reverse_C": C_reverse, "max_field_degree": max(field_degree, reverse_field_degree), "max_source_degree": max(source_degree, reverse_source_degree),
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
    print(f"PRIMARY Q3-MULTIVARIATE-ENERGY-WEIGHT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
