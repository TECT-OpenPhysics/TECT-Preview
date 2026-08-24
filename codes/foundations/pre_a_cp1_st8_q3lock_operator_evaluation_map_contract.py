#!/usr/bin/env python3
"""Primary exact audit for EXP-001051.

This package isolates the missing Q3 coefficient-to-operator interface.  An
explicit common-core evaluation contract implies the weighted coefficient
bound and its product consequence.  A finite radius-violating evaluation is
also checked to show that coefficient data alone cannot provide that contract.
No physical Q3 representation is claimed.
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
SLUG = "pre-a-cp1-st8-q3lock-operator-evaluation-map-contract"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-source-coefficient-product-manifest.json"
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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    source_manifest = json.loads((REPO / manifest["upstream_input"]["coefficient_manifest"]).read_text(encoding="utf-8"))
    fixture = json.loads((REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json").read_text(encoding="utf-8"))["fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001051" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001051/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001050" and source_manifest["exploration_id"] == "EXP-001050", [upstream["exploration_id"], source_manifest["exploration_id"]], "EXP-001050", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("contract fields", all(key in manifest["map_contract"] for key in ("common_core", "seminorm", "generator_bounds", "linearity", "multiplicativity", "conclusion")), list(manifest["map_contract"]), "all contract fields", "model")

    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
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
    onsite_q = sp.Rational(3, 5) * (q**4 - (q - a) ** 4) / 4
    onsite_v = sp.Rational(3, 5) * (v**4 - (v - a) ** 4) / 4
    P = sp.expand(onsite_q + 3 * edge_u + 6 * bond_u)
    P_reverse = sp.expand(onsite_v + 3 * edge_v + 6 * bond_v)
    center_radii = (root, root * neighbour, source_radius)
    reverse_radii = (root * neighbour, root, source_radius)
    B = weighted_norm(P, (q, v, a), center_radii)
    B_reverse = weighted_norm(P_reverse, (q, v, a), reverse_radii)
    expected_B = sp.Rational(str(fixture["expected_local_rate"]))
    check("center rate preserved", B == expected_B and B == sp.Rational(manifest["upstream_input"]["expected_rate_B"]), B, expected_B, "coefficient")
    check("reverse rate preserved", B_reverse == B, B_reverse, B, "orientation")

    signs = tuple(sp.Integer(sign) for sign in (1, -1))
    evaluations: list[dict[str, Any]] = []
    for q_sign, v_sign, a_sign in itertools.product(signs, repeat=3):
        point = (q_sign * center_radii[0], v_sign * center_radii[1], a_sign * center_radii[2])
        reverse_point = (q_sign * reverse_radii[0], v_sign * reverse_radii[1], a_sign * reverse_radii[2])
        value = sp.factor(P.subs({q: point[0], v: point[1], a: point[2]}))
        reverse_value = sp.factor(P_reverse.subs({q: reverse_point[0], v: reverse_point[1], a: reverse_point[2]}))
        check(f"bounded center evaluation {q_sign},{v_sign},{a_sign}", abs(value) <= B, value, f"|value|<={B}", "map")
        check(f"bounded reverse evaluation {q_sign},{v_sign},{a_sign}", abs(reverse_value) <= B, reverse_value, f"|value|<={B}", "map")
        evaluations.append({"point": point, "reverse_point": reverse_point, "center": value, "reverse": reverse_value})

    product_rows: list[dict[str, Any]] = []
    for n in range(1, 5):
        center_max = max(abs(row["center"]) ** n for row in evaluations)
        reverse_max = max(abs(row["reverse"]) ** n for row in evaluations)
        check(f"map product center n={n}", center_max <= B**n, center_max, f"<={B**n}", "product")
        check(f"map product reverse n={n}", reverse_max <= B**n, reverse_max, f"<={B**n}", "product")
        product_rows.append({"n": n, "center_max": center_max, "reverse_max": reverse_max, "bound": B**n})

    obstruction = manifest["finite_fixture"]
    obstruction_point = {
        q: sp.Rational(str(obstruction["obstruction_q"])),
        v: sp.Rational(str(obstruction["obstruction_v"])),
        a: sp.Rational(str(obstruction["obstruction_a"])),
    }
    obstruction_value = sp.factor(P.subs(obstruction_point))
    check("coefficient-only obstruction", abs(obstruction_value) > B, obstruction_value, f">{B}", "boundary")
    check("obstruction leaves radius", obstruction_point[q] > center_radii[0], obstruction_point[q], f">{center_radii[0]}", "boundary")
    check("incidence remains absent", manifest["spatial_bridge"]["status"] == "not supplied" and manifest["scope"]["factorial_incidence_supplied"] is False, manifest["spatial_bridge"], "not supplied", "scope")
    check("QFT scope", manifest["scope"]["actual_q3_common_core_map_proved"] is False and manifest["scope"]["kms_os_closed"] is False and manifest["scope"]["continuum_closed"] is False, manifest["scope"], "conditional/open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit, "product_rows": product_rows,
        "derived": {
            "source_rate_B": B, "reverse_rate_B": B_reverse, "sign_evaluations": len(evaluations), "product_lengths_checked": 4,
            "conditional_evaluation_contract_checked": True, "finite_bounded_evaluations_checked": True,
            "coefficient_only_map_inference_rejected": True, "obstruction_value": obstruction_value, "obstruction_exceeds_B": True,
            "actual_q3_common_core_map_proved": False, "unbounded_domain_closure_proved": False,
            "factorial_incidence_supplied": False, "actual_q3_history_closed": False, "common_alpha_closed": False
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST), "upstream_manifest": str(UPSTREAM.relative_to(REPO)).replace("\\", "/"), "upstream_manifest_sha256": sha256(UPSTREAM)},
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
    print(f"PRIMARY Q3-OPERATOR-MAP-CONTRACT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
