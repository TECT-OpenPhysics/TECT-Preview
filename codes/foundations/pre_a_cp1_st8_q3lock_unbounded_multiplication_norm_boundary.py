#!/usr/bin/env python3
"""Primary exact audit for EXP-001052.

The actual Q3 source is restricted to v=0 and a=1/4.  Its cubic growth shows
why an ordinary global multiplication norm is not the right QFT interface on
an unbounded field line.  The energy-weighted replacement remains a target,
not a theorem.
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
SLUG = "pre-a-cp1-st8-q3lock-unbounded-multiplication-norm-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-operator-evaluation-map-contract-manifest.json"
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
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001052" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001052/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001051", upstream["exploration_id"], "EXP-001051", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("target declared", manifest["energy_weighted_target"]["candidate_energy"] == "A(q)=1+q^4" and manifest["energy_weighted_target"]["status"].startswith("target"), manifest["energy_weighted_target"], "declared target", "scope")

    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
    q, v, a = sp.symbols("q v a")
    edge = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = sp.expand(edge - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    bond = coupling * (q - v) ** 2 / 2
    bond_u = sp.expand(bond - coupling * (q - a - v) ** 2 / 2)
    onsite_q = sp.Rational(3, 5) * (q**4 - (q - a) ** 4) / 4
    P = sp.expand(onsite_q + 3 * edge_u + 6 * bond_u)
    slice_poly = sp.factor(P.subs({v: 0, a: sp.Rational(1, 4)}))
    polynomial = sp.Poly(slice_poly, q)
    expected_lead = sp.Rational(str(manifest["slice_polynomial"]["leading_coefficient"]))
    factor_text = manifest["slice_polynomial"]["factorization"].replace(")(", ")*(").replace("8q", "8*q").replace("1632q", "1632*q").replace("408q", "408*q")
    expected_factor = sp.sympify(factor_text, locals={"q": q})
    check("slice degree", polynomial.degree() == 3, polynomial.degree(), 3, "slice")
    check("slice leading coefficient", polynomial.LC() == expected_lead, polynomial.LC(), expected_lead, "slice")
    check("slice factorization", sp.expand(slice_poly - expected_factor) == 0, slice_poly, expected_factor, "slice")
    ratio_limit = sp.limit(slice_poly / q**3, q, sp.oo)
    check("positive cubic limit", ratio_limit == expected_lead and ratio_limit > 0, ratio_limit, expected_lead, "growth")

    q_values = [sp.Integer(value) for value in manifest["finite_fixture"]["q_values"]]
    expected_values = [sp.Rational(value) for value in manifest["finite_fixture"]["values"]]
    values = [sp.factor(slice_poly.subs(q, value)) for value in q_values]
    for index, (value, expected) in enumerate(zip(values, expected_values)):
        check(f"slice value q={q_values[index]}", value == expected, value, expected, "growth")
    for left, right in zip(values, values[1:]):
        check("finite growth step", right > left, [left, right], "strictly increasing", "growth")
    B = sp.Rational(manifest["finite_fixture"]["coefficient_rate_B"])
    check("finite value exceeds coefficient rate", values[-2] > B, values[-2], f">{B}", "boundary")
    check("ordinary norm architecture boundary", manifest["scope"]["ordinary_global_operator_bound_closed"] is False and manifest["scope"]["energy_weighted_bound_proved"] is False, manifest["scope"], "ordinary open; weighted target", "boundary")
    check("QFT scope", manifest["scope"]["actual_q3_common_core_map_proved"] is False and manifest["scope"]["kms_os_closed"] is False and manifest["scope"]["continuum_closed"] is False, manifest["scope"], "conditional/open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit,
        "derived": {
            "slice_expression": slice_poly, "slice_degree": polynomial.degree(), "leading_coefficient": polynomial.LC(), "ratio_limit": ratio_limit,
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
    print(f"PRIMARY Q3-UNBOUNDED-MULTIPLICATION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
