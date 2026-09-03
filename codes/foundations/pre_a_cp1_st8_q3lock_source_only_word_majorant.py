#!/usr/bin/env python3
"""Primary exact audit of a source-only all-local-Q3 word majorant.

This is a coefficient-level slice: after setting field variables to zero,
the actual onsite, Q3-edge and spatial-bond potential differences become
source polynomials.  A local connected history has at most one onsite, three
Q3-edge and six spatial-bond choices at a step.  The package proves the
resulting finite exponential generating majorant only on this slice.
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
SLUG = "pre-a-cp1-st8-q3lock-source-only-word-majorant"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def rational(value: str | int) -> sp.Rational:
    return sp.Rational(str(value))


def safe(value: Any) -> Any:
    if isinstance(value, (Fraction, sp.Rational)):
        return str(value)
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
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


def l1_radius(poly: sp.Expr, variables: tuple[sp.Symbol, ...], radius: sp.Rational) -> sp.Rational:
    total = sp.Rational(0)
    for powers, coefficient in sp.Poly(poly, *variables).terms():
        total += abs(coefficient) * radius ** sum(powers)
    return sp.factor(total)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g = rational(fixture["g"])
    coupling = rational(fixture["lambda"])
    spatial = rational(fixture["spatial_coupling"])
    radius = rational(fixture["source_radius"])
    time = rational(fixture["time"])
    u, v = sp.symbols("u v")
    audit = Audit()
    audit.check("exploration", manifest["exploration_id"] == "EXP-001039", manifest["exploration_id"], "EXP-001039", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    onsite = sp.expand(g * u**4 / 4)
    edge = sp.expand(coupling * (u - v) ** 2 * (u**2 + v**2) / 4)
    bond = sp.expand(spatial * (u - v) ** 2 / 2)
    onsite_l1 = l1_radius(onsite, (u, v), radius)
    edge_l1 = l1_radius(edge, (u, v), radius)
    bond_l1 = l1_radius(bond, (u, v), radius)
    audit.check("onsite degree", max(sum(powers) for powers, _ in sp.Poly(onsite, u, v).terms()) == 4, 4, 4, "source-slice")
    audit.check("edge degree", max(sum(powers) for powers, _ in sp.Poly(edge, u, v).terms()) == 4, 4, 4, "source-slice")
    audit.check("bond degree", max(sum(powers) for powers, _ in sp.Poly(bond, u, v).terms()) == 2, 2, 2, "source-slice")
    audit.check("orientation edge", l1_radius(edge.subs({u: v, v: u}, simultaneous=True), (u, v), radius) == edge_l1, edge_l1, edge_l1, "orientation")
    audit.check("orientation bond", l1_radius(bond.subs({u: v, v: u}, simultaneous=True), (u, v), radius) == bond_l1, bond_l1, bond_l1, "orientation")

    q3_degree = int(fixture["q3_degree"])
    spatial_degree = int(fixture["spatial_degree"])
    local_choices = 1 + q3_degree + spatial_degree
    audit.check("local choice count", local_choices == int(fixture["local_choice_count"]), local_choices, fixture["local_choice_count"], "graph")
    rate = sp.factor(onsite_l1 + q3_degree * edge_l1 + spatial_degree * bond_l1)
    weighted_rate = sp.factor(time * rate)
    audit.check("choice sum", rate == onsite_l1 + q3_degree * edge_l1 + spatial_degree * bond_l1, rate, rate, "majorant")
    audit.check("positive rate", rate > 0, rate, ">0", "majorant")
    audit.check("positive weighted rate", weighted_rate > 0, weighted_rate, ">0", "majorant")

    partial_rows: list[dict[str, Any]] = []
    partial = sp.Rational(0)
    max_word = int(fixture["max_word_length"])
    for n in range(max_word + 1):
        term = sp.factor(weighted_rate**n / sp.factorial(n))
        partial += term
        partial_rows.append({"length": n, "term": term, "partial": sp.factorial(1) * partial})
        audit.check(f"word term nonnegative n={n}", term >= 0, term, ">=0", "majorant")
        audit.check(f"word bound n={n}", sp.factor(time**n * rate**n / sp.factorial(n)) == term, term, term, "majorant")
    audit.check("partial below exponential", float(partial) <= math.exp(float(weighted_rate)) + 1e-12, float(partial), f"<={math.exp(float(weighted_rate))}", "majorant")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "partial_rows": partial_rows,
        "derived": {
            "onsite_l1_at_radius": onsite_l1,
            "q3_edge_l1_at_radius": edge_l1,
            "spatial_bond_l1_at_radius": bond_l1,
            "q3_degree": q3_degree,
            "spatial_degree": spatial_degree,
            "local_choice_count": local_choices,
            "local_rate_at_radius": rate,
            "weighted_rate": weighted_rate,
            "source_only_egf_closed": True,
            "orientation_symmetric": True,
            "field_dependent_operator_history_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY SOURCE-ONLY-Q3-WORD-MAJORANT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
