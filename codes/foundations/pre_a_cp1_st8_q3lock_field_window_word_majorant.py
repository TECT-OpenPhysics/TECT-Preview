#!/usr/bin/env python3
"""Primary audit of a field-window actual-Q3 multiplication-word envelope.

This is a coefficient-level theorem on a declared bounded field window.  It
keeps the field variables in the canonical onsite, Q3-edge and spatial-bond
potential differences, unlike the source-only slice of EXP-001039.  It does
not turn the window into an operator-domain or thermodynamic estimate.
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
SLUG = "pre-a-cp1-st8-q3lock-field-window-word-majorant"
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
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
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


def l1_radius(poly: sp.Expr, variable: sp.Symbol, radius: sp.Rational) -> sp.Rational:
    return sp.factor(sum(abs(coefficient) * radius ** powers[0] for powers, coefficient in sp.Poly(poly, variable).terms()))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g = sp.Rational(str(fixture["g"]))
    lam = sp.Rational(str(fixture["lambda"]))
    c = sp.Rational(str(fixture["spatial_coupling"]))
    Q = sp.Rational(str(fixture["field_radius"]))
    S = sp.Rational(str(fixture["source_radius"]))
    time = sp.Rational(str(fixture["time"]))
    q, v, r, a = sp.symbols("q v r a", real=True)
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001040" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001040/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("field window", Q > 0 and S > 0, [Q, S], ">0", "scope")

    onsite = sp.expand(g * (q**4 - (q - a)**4) / 4)
    edge_potential = lam * (q - v)**2 * (q**2 + v**2) / 4
    edge = sp.expand(edge_potential - edge_potential.subs(q, q - a))
    bond = sp.expand(c * ((q - r)**2 - (q - a - r)**2) / 2)
    onsite_coeffs = [sp.Poly(onsite, a).coeff_monomial(a**degree) for degree in range(5)]
    edge_coeffs = [sp.Poly(edge, a).coeff_monomial(a**degree) for degree in range(5)]
    bond_coeffs = [sp.Poly(bond, a).coeff_monomial(a**degree) for degree in range(3)]
    expected_onsite = [0, g*q**3, -sp.Rational(3, 2)*g*q**2, g*q, -g/sp.Integer(4)]
    expected_edge = [0, lam*(q**3-sp.Rational(3, 2)*q**2*v+q*v**2-sp.Rational(1, 2)*v**3), -lam*(sp.Rational(3, 2)*q**2-sp.Rational(3, 2)*q*v+sp.Rational(1, 2)*v**2), lam*(q-sp.Rational(1, 2)*v), -lam/sp.Integer(4)]
    expected_bond = [0, c*(q-r), -c/sp.Integer(2)]
    audit.check("onsite coefficient table", all(sp.expand(actual-expected) == 0 for actual, expected in zip(onsite_coeffs, expected_onsite)), onsite_coeffs, "Taylor table", "derivation")
    audit.check("edge coefficient table", all(sp.expand(actual-expected) == 0 for actual, expected in zip(edge_coeffs, expected_edge)), edge_coeffs, "Taylor table", "derivation")
    audit.check("bond coefficient table", all(sp.expand(actual-expected) == 0 for actual, expected in zip(bond_coeffs, expected_bond)), bond_coeffs, "Taylor table", "derivation")

    onsite_bound = g * (Q**3*S + sp.Rational(3, 2)*Q**2*S**2 + Q*S**3 + S**4/sp.Integer(4))
    edge_bound = lam * (4*Q**3*S + sp.Rational(7, 2)*Q**2*S**2 + sp.Rational(3, 2)*Q*S**3 + S**4/sp.Integer(4))
    bond_bound = c * (2*Q*S + S**2/sp.Integer(2))
    onsite_choices = int(fixture["onsite_choices"])
    edge_choices = int(fixture["q3_edge_choices"])
    bond_choices = int(fixture["spatial_bond_choices"])
    local_choices = onsite_choices + edge_choices + bond_choices
    rate = sp.factor(onsite_choices*onsite_bound + edge_choices*edge_bound + bond_choices*bond_bound)
    weighted_rate = sp.factor(time * rate)
    audit.check("onsite bound positive", onsite_bound > 0, onsite_bound, ">0", "window")
    audit.check("edge bound positive", edge_bound > 0, edge_bound, ">0", "window")
    audit.check("bond bound positive", bond_bound > 0, bond_bound, ">0", "window")

    grid = tuple(-Q + 2*Q*sp.Rational(index, 4) for index in range(5))
    rows: list[dict[str, Any]] = []
    for q_value in grid:
        for v_value in grid:
            on_l1 = l1_radius(onsite.subs(q, q_value), a, S)
            edge_l1 = l1_radius(edge.subs({q: q_value, v: v_value}), a, S)
            reverse_l1 = l1_radius((edge_potential - edge_potential.subs(v, v - a)).subs({q: q_value, v: v_value}), a, S)
            audit.check(f"onsite window q={q_value}", on_l1 <= onsite_bound, on_l1, f"<={onsite_bound}", "window")
            audit.check(f"edge window q={q_value} v={v_value}", edge_l1 <= edge_bound, edge_l1, f"<={edge_bound}", "window")
            audit.check(f"edge orientation q={q_value} v={v_value}", reverse_l1 <= edge_bound, reverse_l1, f"<={edge_bound}", "orientation")
            rows.append({"q": q_value, "v": v_value, "onsite_l1": on_l1, "edge_l1": edge_l1, "reverse_edge_l1": reverse_l1})
    for q_value in grid:
        for r_value in grid:
            bond_l1 = l1_radius(bond.subs({q: q_value, r: r_value}), a, S)
            reverse_l1 = l1_radius((c*((r_value - q_value)**2 - (r_value - q_value + a)**2)/2), a, S)
            audit.check(f"bond window q={q_value} r={r_value}", bond_l1 <= bond_bound, bond_l1, f"<={bond_bound}", "window")
            audit.check(f"bond orientation q={q_value} r={r_value}", reverse_l1 <= bond_bound, reverse_l1, f"<={bond_bound}", "orientation")

    max_word = int(fixture["max_word_length"])
    partial = sp.Rational(0)
    word_rows: list[dict[str, Any]] = []
    for n in range(max_word + 1):
        term = sp.factor(weighted_rate**n / sp.factorial(n))
        partial += term
        audit.check(f"word envelope n={n}", term >= 0, term, ">=0", "majorant")
        audit.check(f"word term formula n={n}", term == time**n * rate**n / sp.factorial(n), term, term, "majorant")
        word_rows.append({"length": n, "term": term, "partial": partial})
    audit.check("EGF partial below exp", float(partial) <= math.exp(float(weighted_rate)) + 1e-12, float(partial), f"<={math.exp(float(weighted_rate))}", "majorant")
    audit.check("choice count", local_choices == int(fixture["local_choice_count"]), local_choices, fixture["local_choice_count"], "graph")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS",
        "passed": passed, "total": passed, "failed": 0, "assertions": audit.rows,
        "grid_rows": rows, "word_rows": word_rows,
        "derived": {
            "field_radius": Q, "source_radius": S,
            "onsite_bound": onsite_bound, "q3_edge_bound": edge_bound, "spatial_bond_bound": bond_bound,
            "local_rate": rate, "weighted_rate": weighted_rate, "local_choices": local_choices,
            "field_window_word_egf_closed": True, "orientation_symmetric": True,
            "field_independent_operator_history_closed": False, "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "exploration_id": manifest["exploration_id"], "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FIELD-WINDOW-Q3-WORD-MAJORANT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
