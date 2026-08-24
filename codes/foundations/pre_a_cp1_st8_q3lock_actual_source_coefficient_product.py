#!/usr/bin/env python3
"""Primary exact audit for EXP-001050.

The actual Q3 source polynomials are embedded into a formal weighted
coefficient algebra.  Cauchy-product bounds are checked exactly; no operator
realization or history theorem is claimed.
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
SLUG = "pre-a-cp1-st8-q3lock-actual-source-coefficient-product"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
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
        weight = sp.prod(radius**degree for radius, degree in zip(radii, monomial))
        total += abs(coefficient) * weight
    return sp.factor(total)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = upstream["fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001050" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001050/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001045", upstream["exploration_id"], "EXP-001045", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("formal model", manifest["coefficient_model"]["norm"] == "weighted l1 coefficient norm", manifest["coefficient_model"]["norm"], "weighted l1 coefficient norm", "model")

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
    check("center coefficient rate", B == expected_B, B, expected_B, "coefficient")
    check("reverse coefficient rate", B_reverse == B, B_reverse, B, "orientation")
    check("source radius positive", source_radius > 0, source_radius, ">0", "model")
    check("source polynomial nonzero", P != 0 and P_reverse != 0, [P != 0, P_reverse != 0], "true", "polynomial")

    product_rows: list[dict[str, Any]] = []
    for n in range(1, 5):
        product_norm = weighted_norm(P**n, (q, v, a), center_radii)
        reverse_product_norm = weighted_norm(P_reverse**n, (q, v, a), reverse_radii)
        check(f"center Cauchy product n={n}", product_norm <= B**n, product_norm, f"<={B**n}", "product")
        check(f"reverse Cauchy product n={n}", reverse_product_norm <= B**n, reverse_product_norm, f"<={B**n}", "product")
        product_rows.append({"n": n, "center_norm": product_norm, "reverse_norm": reverse_product_norm, "bound": B**n})

    passage = manifest["first_passage_bridge"]
    orientations = sp.Integer(passage["orientations"])
    degree = sp.Integer(passage["degree_bound"])
    base = sp.Integer(passage["spatial_base"])
    time = sp.Rational(str(passage["time"]))
    distance = int(passage["distance"])
    eta = sp.factor(orientations * degree * base * B * time)
    partial = sum(eta**n / sp.factorial(n) for n in range(33))
    check("EGF exponent positive", eta > 0, eta, ">0", "first-passage")
    check("finite EGF below exponential", float(partial) <= float(sp.exp(eta)), partial, f"<=exp({eta})", "first-passage")
    check("distance factor", base ** (-distance) == sp.Rational(1, base**distance), base ** (-distance), "exact", "first-passage")
    check("formal scope", manifest["scope"]["cauchy_product_envelope_closed_formally"] is True and manifest["scope"]["operator_to_coefficient_map_proved"] is False and manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], "formal/open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit, "product_rows": product_rows,
        "derived": {
            "source_rate_B": B, "reverse_rate_B": B_reverse, "field_radius_center": root, "field_radius_neighbor": root * neighbour,
            "source_radius": source_radius, "product_lengths_checked": 4, "center_coefficient_embedding_closed_formally": True,
            "reverse_coefficient_embedding_closed_formally": True, "cauchy_product_envelope_closed_formally": True,
            "operator_to_coefficient_map_proved": False, "factorial_incidence_hypothesis_supplied": False,
            "eta": eta, "distance": distance, "actual_q3_history_closed": False, "common_alpha_closed": False
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
    print(f"PRIMARY Q3-ACTUAL-SOURCE-COEFFICIENT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
