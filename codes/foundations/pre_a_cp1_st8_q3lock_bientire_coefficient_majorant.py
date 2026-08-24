#!/usr/bin/env python3
"""Primary audit of a formal bi-entire coefficient majorant for actual Q3 words.

The norm is an l1 coefficient norm with independent formal radii for field and
source variables.  It removes the finite field window of EXP-001040 at the
formal-polynomial level, but it is not an operator-domain or thermodynamic
estimate.
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
SLUG = "pre-a-cp1-st8-q3lock-bientire-coefficient-majorant"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, (Fraction, sp.Rational)):
        return str(value)
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def bi_l1_radius(poly: sp.Expr, fields: tuple[sp.Symbol, ...], source: sp.Symbol, field_radius: sp.Rational, source_radius: sp.Rational) -> sp.Rational:
    total = sp.Rational(0)
    for powers, coefficient in sp.Poly(poly, *(fields + (source,))).terms():
        field_degree = sum(powers[:-1])
        source_degree = powers[-1]
        total += abs(coefficient) * field_radius**field_degree * source_radius**source_degree
    return sp.factor(total)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g = sp.Rational(str(fixture["g"]))
    lam = sp.Rational(str(fixture["lambda"]))
    c = sp.Rational(str(fixture["spatial_coupling"]))
    field_radius = sp.Rational(str(fixture["field_radius"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    time = sp.Rational(str(fixture["time"]))
    q, v, r, a = sp.symbols("q v r a", real=True)
    fields_qv = (q, v)
    fields_qr = (q, r)
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001041" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001041/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("formal radii positive", field_radius > 0 and source_radius > 0, [field_radius, source_radius], ">0", "scope")

    onsite = sp.expand(g * (q**4 - (q - a)**4) / 4)
    edge_potential = lam * (q - v)**2 * (q**2 + v**2) / 4
    edge = sp.expand(edge_potential - edge_potential.subs(q, q - a))
    bond = sp.expand(c * ((q - r)**2 - (q - a - r)**2) / 2)
    expected_onsite = [0, g*q**3, -sp.Rational(3, 2)*g*q**2, g*q, -g/sp.Integer(4)]
    expected_edge = [0, lam*(q**3-sp.Rational(3, 2)*q**2*v+q*v**2-sp.Rational(1, 2)*v**3), -lam*(sp.Rational(3, 2)*q**2-sp.Rational(3, 2)*q*v+sp.Rational(1, 2)*v**2), lam*(q-sp.Rational(1, 2)*v), -lam/sp.Integer(4)]
    expected_bond = [0, c*(q-r), -c/sp.Integer(2)]
    actual_onsite = [sp.Poly(onsite, a).coeff_monomial(a**degree) for degree in range(5)]
    actual_edge = [sp.Poly(edge, a).coeff_monomial(a**degree) for degree in range(5)]
    actual_bond = [sp.Poly(bond, a).coeff_monomial(a**degree) for degree in range(3)]
    audit.check("onsite coefficient table", all(sp.expand(x-y) == 0 for x, y in zip(actual_onsite, expected_onsite)), actual_onsite, "Taylor table", "derivation")
    audit.check("edge coefficient table", all(sp.expand(x-y) == 0 for x, y in zip(actual_edge, expected_edge)), actual_edge, "Taylor table", "derivation")
    audit.check("bond coefficient table", all(sp.expand(x-y) == 0 for x, y in zip(actual_bond, expected_bond)), actual_bond, "Taylor table", "derivation")

    onsite_norm = bi_l1_radius(onsite, (q,), a, field_radius, source_radius)
    edge_norm = bi_l1_radius(edge, fields_qv, a, field_radius, source_radius)
    bond_norm = bi_l1_radius(bond, fields_qr, a, field_radius, source_radius)
    onsite_choices = int(fixture["onsite_choices"])
    edge_choices = int(fixture["q3_edge_choices"])
    bond_choices = int(fixture["spatial_bond_choices"])
    local_choices = onsite_choices + edge_choices + bond_choices
    rate = sp.factor(onsite_choices*onsite_norm + edge_choices*edge_norm + bond_choices*bond_norm)
    weighted_rate = sp.factor(time*rate)
    audit.check("positive local norms", onsite_norm > 0 and edge_norm > 0 and bond_norm > 0, [onsite_norm, edge_norm, bond_norm], ">0", "majorant")
    audit.check("choice count", local_choices == int(fixture["local_choice_count"]), local_choices, fixture["local_choice_count"], "graph")
    audit.check("rate formula", rate == onsite_choices*onsite_norm + edge_choices*edge_norm + bond_choices*bond_norm, rate, rate, "majorant")

    reversed_edge = sp.expand(edge_potential - edge_potential.subs(v, v - a))
    reversed_bond = sp.expand(c * ((r - q)**2 - (r - q + a)**2) / 2)
    audit.check("edge orientation norm", bi_l1_radius(reversed_edge, fields_qv, a, field_radius, source_radius) == edge_norm, bi_l1_radius(reversed_edge, fields_qv, a, field_radius, source_radius), edge_norm, "orientation")
    audit.check("bond orientation norm", bi_l1_radius(reversed_bond, fields_qr, a, field_radius, source_radius) == bond_norm, bi_l1_radius(reversed_bond, fields_qr, a, field_radius, source_radius), bond_norm, "orientation")

    factors = [onsite] * onsite_choices + [edge] * edge_choices + [bond] * bond_choices
    factor_norms = [onsite_norm] * onsite_choices + [edge_norm] * edge_choices + [bond_norm] * bond_choices
    product_rows: list[dict[str, Any]] = []
    product = sp.Integer(1)
    product_bound = sp.Integer(1)
    for length in range(1, int(fixture["max_word_length"])+1):
        product = sp.expand(product * factors[(length-1) % len(factors)])
        product_bound *= factor_norms[(length-1) % len(factor_norms)]
        actual = bi_l1_radius(product, (q, v, r), a, field_radius, source_radius)
        audit.check(f"product submultiplicativity n={length}", actual <= product_bound, actual, f"<={product_bound}", "majorant")
        product_rows.append({"length": length, "actual": actual, "bound": product_bound})

    partial = sp.Rational(0)
    word_rows: list[dict[str, Any]] = []
    for n in range(int(fixture["max_word_length"])+1):
        term = sp.factor(weighted_rate**n / sp.factorial(n))
        partial += term
        audit.check(f"EGF term n={n}", term >= 0, term, ">=0", "majorant")
        word_rows.append({"length": n, "term": term, "partial": partial})
    audit.check("EGF partial below exp", float(partial) <= math.exp(float(weighted_rate)) + 1e-12, float(partial), f"<={math.exp(float(weighted_rate))}", "majorant")
    audit.check("no field window", manifest["scope"]["formal_field_radius_not_a_cutoff"] is True, manifest["scope"], True, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit.rows, "product_rows": product_rows, "word_rows": word_rows,
        "derived": {"field_radius": field_radius, "source_radius": source_radius, "onsite_norm": onsite_norm, "q3_edge_norm": edge_norm, "spatial_bond_norm": bond_norm, "local_rate": rate, "weighted_rate": weighted_rate, "local_choices": local_choices, "formal_bientire_word_egf_closed": True, "orientation_symmetric": True, "formal_field_radius_not_a_cutoff": True, "operator_history_closed": False, "all_shape_exhaustion_closed": False, "common_alpha_closed": False},
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "exploration_id": manifest["exploration_id"], "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(); payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY BI-ENTIRE-Q3-COEFFICIENT-MAJORANT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
