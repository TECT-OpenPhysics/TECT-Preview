#!/usr/bin/env python3
"""Independent Fraction polynomial audit for EXP-001050."""

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
SLUG = "pre-a-cp1-st8-q3lock-actual-source-coefficient-product"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
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
    out: Poly = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            out[monomial] = out.get(monomial, F(0)) + coefficient
    return clean_poly(out)


def scale(poly: Poly, coefficient: F) -> Poly:
    return clean_poly({monomial: coefficient * value for monomial, value in poly.items()})


def mul(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for lm, lc in left.items():
        for rm, rc in right.items():
            monomial = tuple(a + b for a, b in zip(lm, rm))
            out[monomial] = out.get(monomial, F(0)) + lc * rc
    return clean_poly(out)


def power(poly: Poly, exponent: int) -> Poly:
    result = {(0,) * len(next(iter(poly))): F(1)}
    for _ in range(exponent):
        result = mul(result, poly)
    return result


def variable(index: int, dimension: int) -> Poly:
    exponent = [0] * dimension
    exponent[index] = 1
    return {tuple(exponent): F(1)}


def weighted_norm(poly: Poly, radii: tuple[F, ...]) -> F:
    return sum(abs(coefficient) * math.prod(radius**degree for radius, degree in zip(radii, monomial)) for monomial, coefficient in poly.items())


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = upstream["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001050" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001050/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001045", upstream["exploration_id"], "EXP-001045", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    lam, coupling, source_radius = F(fixture["lambda"]), F(fixture["spatial_coupling"]), F(fixture["source_radius"])
    root, neighbour = F(fixture["root_scale"]), F(fixture["neighbor_factor_root"])
    q, v, a = variable(0, 3), variable(1, 3), variable(2, 3)
    q_minus_v = add(q, scale(v, F(-1)))
    q_minus_a_minus_v = add(q, scale(a, F(-1)), scale(v, F(-1)))
    edge_u = scale(add(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), scale(mul(power(q_minus_a_minus_v, 2), add(power(add(q, scale(a, F(-1))), 2), power(v, 2))), F(-1))), lam / 4)
    edge_v = scale(add(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), scale(mul(power(add(q, scale(v, F(-1)), a), 2), add(power(q, 2), power(add(v, scale(a, F(-1))), 2))), F(-1))), lam / 4)
    bond_u = scale(add(power(q_minus_v, 2), scale(power(q_minus_a_minus_v, 2), F(-1))), coupling / 2)
    bond_v = scale(add(power(q_minus_v, 2), scale(power(add(q, scale(v, F(-1)), a), 2), F(-1))), coupling / 2)
    onsite_q, onsite_a = variable(0, 2), variable(1, 2)
    onsite_q3 = scale(add(power(q, 4), scale(power(add(q, scale(a, F(-1))), 4), F(-1))), F(3, 20))
    onsite_v3 = scale(add(power(v, 4), scale(power(add(v, scale(a, F(-1))), 4), F(-1))), F(3, 20))
    P = add(onsite_q3, scale(edge_u, F(3)), scale(bond_u, F(6)))
    P_reverse = add(onsite_v3, scale(edge_v, F(3)), scale(bond_v, F(6)))
    B = weighted_norm(P, (root, root * neighbour, source_radius))
    B_reverse = weighted_norm(P_reverse, (root * neighbour, root, source_radius))
    expected_B = F(fixture["expected_local_rate"])
    check("center coefficient rate", B == expected_B, B, expected_B, "coefficient")
    check("reverse coefficient rate", B_reverse == B, B_reverse, B, "orientation")
    check("source radius positive", source_radius > 0, source_radius, ">0", "model")
    product_rows: list[dict[str, Any]] = []
    for n in range(1, 5):
        center_norm = weighted_norm(power(P, n), (root, root * neighbour, source_radius))
        reverse_norm = weighted_norm(power(P_reverse, n), (root * neighbour, root, source_radius))
        check(f"center product n={n}", center_norm <= B**n, center_norm, f"<={B**n}", "product")
        check(f"reverse product n={n}", reverse_norm <= B**n, reverse_norm, f"<={B**n}", "product")
        product_rows.append({"n": n, "center_norm": center_norm, "reverse_norm": reverse_norm, "bound": B**n})

    passage = manifest["first_passage_bridge"]
    eta = F(passage["orientations"]) * F(passage["degree_bound"]) * F(passage["spatial_base"]) * B * F(passage["time"])
    order = 32
    partial = sum(eta**n / math.factorial(n) for n in range(order + 1))
    check("EGF exponent positive", eta > 0, eta, ">0", "first-passage")
    check("finite EGF below exponential", float(partial) <= math.exp(float(eta)), partial, "<=exp(eta)", "first-passage")
    check("formal scope", manifest["scope"]["cauchy_product_envelope_closed_formally"] is True and manifest["scope"]["operator_to_coefficient_map_proved"] is False and manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], "formal/open", "scope")
    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": checks, "product_rows": product_rows,
        "derived": {
            "source_rate_B": B, "reverse_rate_B": B_reverse, "field_radius_center": root, "field_radius_neighbor": root * neighbour,
            "source_radius": source_radius, "product_lengths_checked": 4, "center_coefficient_embedding_closed_formally": True,
            "reverse_coefficient_embedding_closed_formally": True, "cauchy_product_envelope_closed_formally": True,
            "operator_to_coefficient_map_proved": False, "factorial_incidence_hypothesis_supplied": False,
            "eta": eta, "distance": int(passage["distance"]), "actual_q3_history_closed": False, "common_alpha_closed": False
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
    print(f"INDEPENDENT Q3-ACTUAL-SOURCE-COEFFICIENT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
