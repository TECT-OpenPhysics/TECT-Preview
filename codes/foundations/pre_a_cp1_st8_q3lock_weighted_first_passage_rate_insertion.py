#!/usr/bin/env python3
"""Primary exact audit for EXP-001046.

This inserts the EXP-001045 weighted local rate into a conditional factorial
first-passage bridge.  The response expansion remains an explicit hypothesis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-weighted-first-passage-rate-insertion"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


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


def coefficient_rate(polynomial: sp.Expr, variables: tuple[sp.Symbol, ...], source_radius: sp.Rational, root_scale: sp.Integer, neighbour_root: sp.Integer, neighbour_index: int) -> sp.Rational:
    total = sp.Rational(0)
    for monomial, coefficient in sp.Poly(sp.expand(polynomial), *variables).terms():
        total += abs(coefficient) * root_scale**sum(monomial[:-1]) * neighbour_root**monomial[neighbour_index] * source_radius**monomial[-1]
    return sp.factor(total)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    lam = sp.Rational(2, 7)
    coupling = sp.Rational(2, 3)
    onsite_g = sp.Rational(3, 5)
    source_radius = sp.Rational(str(fixture["source_radius"])) if "source_radius" in fixture else sp.Rational(1, 1000)
    time = sp.Rational(str(fixture["time"]))
    root_scale = sp.Integer(4)
    neighbour_root = sp.Integer(2)
    orientation_count = sp.Integer(str(fixture["orientation_count"]))
    degree = sp.Integer(str(fixture["degree"]))
    base = sp.Integer(str(fixture["base"]))
    distance = int(fixture["distance"])
    truncation = int(fixture["truncation_order"])
    q, v, r, a = sp.symbols("q v r a")
    edge = lam * ((q - v) ** 2 * (q**2 + v**2) - (q - a - v) ** 2 * ((q - a) ** 2 + v**2)) / 4
    bond = coupling * ((q - r) ** 2 - (q - a - r) ** 2) / 2
    onsite_q = sp.symbols("onsite_q")
    onsite = onsite_g * (onsite_q**4 - (onsite_q - a) ** 4) / 4
    onsite_rate = coefficient_rate(onsite, (onsite_q, a), source_radius, root_scale, sp.Integer(1), 0)
    edge_rate = coefficient_rate(edge, (q, v, a), source_radius, root_scale, neighbour_root, 1)
    bond_rate = coefficient_rate(bond, (q, r, a), source_radius, root_scale, neighbour_root, 1)
    local_rate = sp.factor(onsite_rate + 3 * edge_rate + 6 * bond_rate)
    exponent = sp.factor(orientation_count * local_rate * degree * base * time)
    distance_factor = sp.factor(base ** (-distance))
    partial = sp.Rational(0)
    partial_rows: list[dict[str, Any]] = []
    for n in range(truncation + 1):
        term = sp.factor(exponent**n / sp.factorial(n))
        partial += term
        partial_rows.append({"n": n, "term": term, "partial": partial})
    boundary_partial = sp.factor(distance_factor * partial)
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001046" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001046/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("response hypothesis explicit", manifest["scope"]["factorial_first_passage_expansion_supplied"] is False, manifest["scope"]["factorial_first_passage_expansion_supplied"], False, "hypothesis")
    audit.check("rate provenance", local_rate == sp.Rational(1382807, 7168), local_rate, "1382807/7168", "rate")
    audit.check("edge rate provenance", edge_rate == sp.Rational(203393, 3584), edge_rate, "203393/3584", "rate")
    audit.check("bond rate provenance", bond_rate == sp.Rational(97, 48), bond_rate, "97/48", "rate")
    audit.check("orientation count", orientation_count == 2, orientation_count, 2, "graph")
    audit.check("degree", degree == 6, degree, 6, "graph")
    audit.check("spatial base", base == 2 and distance_factor == sp.Rational(1, 1024), [base, distance_factor], "2,1/1024", "space")
    audit.check("exact exponent", exponent == sp.Rational(4148421, 896000), exponent, "4148421/896000", "bridge")
    audit.check("finite truncation order", truncation == 32 and truncation >= distance, [truncation, distance], "32>=10", "bridge")
    audit.check("partial terms nonnegative", all(row["term"] >= 0 for row in partial_rows), True, True, "bridge")
    audit.check("partial below exponential", float(partial) <= math.exp(float(exponent)) + 1e-12, float(partial), "<=exp(E)", "bridge")
    audit.check("boundary partial below exponential envelope", float(boundary_partial) <= float(distance_factor) * math.exp(float(exponent)) + 1e-12, float(boundary_partial), "<=2^-d exp(E)", "space")
    audit.check("history remains open", manifest["scope"]["actual_q3_recurrence_closed"] is False and manifest["scope"]["boundary_commutator_decay_closed"] is False, manifest["scope"], "false/false", "scope")
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
            "onsite_rate": onsite_rate,
            "edge_rate": edge_rate,
            "bond_rate": bond_rate,
            "local_rate": local_rate,
            "orientation_count": orientation_count,
            "degree": degree,
            "base": base,
            "time": time,
            "distance": distance,
            "exponent": exponent,
            "distance_factor": distance_factor,
            "partial_order": truncation,
            "boundary_partial": boundary_partial,
            "rate_insertion_closed_conditionally": True,
            "finite_poisson_arithmetic_closed": True,
            "factorial_first_passage_expansion_supplied": False,
            "actual_q3_recurrence_closed": False,
            "boundary_commutator_decay_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY Q3-WEIGHTED-FIRST-PASSAGE-RATE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
