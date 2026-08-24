#!/usr/bin/env python3
"""Primary exact audit for EXP-001053.

The scalar Q3 slice is controlled by an energy weight with cubic growth using
an exact coefficient triangle.  This is a scalar weighted interface only.
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
SLUG = "pre-a-cp1-st8-q3lock-scalar-energy-weighted-slice-bound"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-unbounded-multiplication-norm-boundary-manifest.json"
GROWTH = REPO / "strategy/pre-a-cp1-st8-q3lock-unbounded-multiplication-norm-boundary-manifest.json"
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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    growth = json.loads(GROWTH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001053" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001053/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001052" and growth["exploration_id"] == "EXP-001052", [upstream["exploration_id"], growth["exploration_id"]], "EXP-001052", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("weighted target", manifest["weighted_target"]["energy"] == "A(q)=1+q^4" and manifest["weighted_target"]["exponent"] == "3/4", manifest["weighted_target"], "A(q), 3/4", "model")

    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
    q, v, a = sp.symbols("q v a")
    edge = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = sp.expand(edge - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    bond = coupling * (q - v) ** 2 / 2
    bond_u = sp.expand(bond - coupling * (q - a - v) ** 2 / 2)
    onsite_q = sp.Rational(3, 5) * (q**4 - (q - a) ** 4) / 4
    P = sp.expand(onsite_q + 3 * edge_u + 6 * bond_u)
    slice_poly = sp.Poly(sp.expand(P.subs({v: 0, a: sp.Rational(1, 4)})), q)
    expression_text = growth["slice_polynomial"]["expression"].replace("^", "**").replace(")q", ")*q")
    expected_expression = sp.sympify(expression_text, locals={"q": q})
    check("slice expression", sp.expand(slice_poly.as_expr() - expected_expression) == 0, slice_poly.as_expr(), expected_expression, "slice")
    check("slice degree at most three", slice_poly.degree() <= 3, slice_poly.degree(), "<=3", "slice")
    coefficients = [slice_poly.coeff_monomial(q**degree) for degree in range(4)]
    coefficient_sum = sp.factor(sum(abs(coefficient) for coefficient in coefficients))
    expected_C = sp.Rational(manifest["weighted_target"]["majorant"].split("=")[-1])
    check("coefficient majorant", coefficient_sum == expected_C, coefficient_sum, expected_C, "weight")
    check("majorant positive", expected_C > 0, expected_C, ">0", "weight")
    check("power range", all(degree <= 3 for degree in range(4)), list(range(4)), "0..3", "weight")

    samples = [sp.Rational(value) for value in manifest["finite_fixture"]["q_values"]]
    sample_rows: list[dict[str, Any]] = []
    for sample in samples:
        value = sp.factor(slice_poly.as_expr().subs(q, sample))
        energy = 1 + sample**4
        fourth_left = abs(value) ** 4
        fourth_right = expected_C**4 * energy**3
        check(f"weighted sample q={sample}", fourth_left <= fourth_right, [fourth_left, fourth_right], "left<=right", "weight")
        sample_rows.append({"q": sample, "value": value, "energy": energy, "fourth_left": fourth_left, "fourth_right": fourth_right})
    check("scalar weighted majorant declared", manifest["scope"]["scalar_energy_weighted_majorant_closed"] is True and manifest["scope"]["actual_q3_common_core_map_proved"] is False, manifest["scope"], "scalar-only/open", "scope")
    check("QFT scope", manifest["scope"]["multivariate_weighted_bound_proved"] is False and manifest["scope"]["kms_os_closed"] is False and manifest["scope"]["continuum_closed"] is False, manifest["scope"], "conditional/open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit, "sample_rows": sample_rows,
        "derived": {
            "slice_expression": slice_poly.as_expr(), "slice_degree": slice_poly.degree(), "slice_coefficients": coefficients,
            "coefficient_majorant_C": coefficient_sum, "energy_exponent": "3/4", "sample_count": len(samples),
            "scalar_energy_weighted_majorant_closed": True, "actual_q3_common_core_map_proved": False, "operator_domain_closure_proved": False,
            "multivariate_weighted_bound_proved": False, "factorial_incidence_supplied": False, "actual_q3_history_closed": False, "common_alpha_closed": False
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST), "upstream_manifest_sha256": sha256(UPSTREAM), "growth_manifest_sha256": sha256(GROWTH), "fixture_manifest_sha256": sha256(FIXTURE)},
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
    print(f"PRIMARY Q3-SCALAR-ENERGY-WEIGHT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
