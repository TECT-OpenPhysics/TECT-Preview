#!/usr/bin/env python3
"""Primary exact audit for the conditional R-167 mixed graph lift.

The weighted-energy/Heinz--Kato graph estimate is an explicit prior input.
This audit proves the finite scalar domination table, inserts its weighted
moments into the actual Q3 edge/bond source polynomials in both endpoint
orientations, and records the spatial weight cost.  It does not prove the
inherited operator theorem or any repeated-history result.
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
SLUG = "pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift"
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


def weighted_rate(polynomial: sp.Expr, variables: tuple[sp.Symbol, ...], source_radius: sp.Rational, root_scale: sp.Integer, neighbour_root: sp.Integer, neighbour_index: int) -> sp.Rational:
    total = sp.Rational(0)
    for monomial, coefficient in sp.Poly(sp.expand(polynomial), *variables).terms():
        field_degree = sum(monomial[:-1])
        source_degree = monomial[-1]
        total += abs(coefficient) * root_scale**field_degree * neighbour_root**monomial[neighbour_index] * source_radius**source_degree
    return sp.factor(total)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    gamma = sp.Rational(str(fixture["gamma"]))
    kappa = sp.Rational(str(fixture["kappa"]))
    ratio = sp.Rational(str(fixture["energy_ratio"]))
    root_scale = sp.Integer(str(fixture["root_scale"]))
    weight_center = sp.Rational(str(fixture["weight_center"]))
    weight_neighbor = sp.Rational(str(fixture["weight_neighbor"]))
    neighbour_root = sp.Integer(str(fixture["neighbor_factor_root"]))
    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    time = sp.Rational(str(fixture["time"]))
    q, v, r, a = sp.symbols("q v r a")
    edge_potential = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = sp.expand(edge_potential - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    edge_v = sp.expand(edge_potential - lam * (q - (v - a)) ** 2 * (q**2 + (v - a) ** 2) / 4)
    bond_potential = coupling * (q - r) ** 2 / 2
    bond_u = sp.expand(bond_potential - coupling * (q - a - r) ** 2 / 2)
    bond_v = sp.expand(bond_potential - coupling * (q - (r - a)) ** 2 / 2)
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001045" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001045/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("positive inputs", gamma > 0 and kappa > 0 and source_radius > 0 and time > 0, [gamma, kappa, source_radius, time], ">0", "hypothesis")
    audit.check("energy ratio root", root_scale**4 == ratio and ratio == kappa / gamma, [root_scale, ratio, kappa / gamma], "root^4=kappa/gamma", "hypothesis")
    audit.check("weight fixture", weight_center == 1 and weight_neighbor == sp.Rational(1, 16) and neighbour_root**4 == weight_center / weight_neighbor, [weight_center, weight_neighbor, neighbour_root], "1,1/16,2^4=16", "hypothesis")

    X, Y = sp.symbols("X Y", nonnegative=True)
    scalar_rows: list[dict[str, Any]] = []
    for total_degree in (1, 2, 3):
        for i in range(total_degree + 1):
            j = total_degree - i
            difference = sp.Poly(sp.expand((X + Y) ** total_degree - X**i * Y**j), X, Y)
            nonnegative_coefficients = all(coefficient >= 0 for coefficient in difference.coeffs())
            audit.check(f"scalar lift i={i} j={j}", nonnegative_coefficients, difference.as_expr(), ">=0 coefficients", "scalar")
            scalar_rows.append({"i": i, "j": j, "difference": difference.as_expr()})
    audit.check("powered scalar fixture", (sp.Integer(1) ** 2 * sp.Integer(16)) <= (sp.Integer(1) + sp.Integer(16)) ** 3, 16, "<=4913", "scalar")

    edge_u_rate = weighted_rate(edge_u, (q, v, a), source_radius, root_scale, neighbour_root, 1)
    edge_v_rate = weighted_rate(edge_v, (q, v, a), source_radius, root_scale, neighbour_root, 0)
    bond_u_rate = weighted_rate(bond_u, (q, r, a), source_radius, root_scale, neighbour_root, 1)
    bond_v_rate = weighted_rate(bond_v, (q, r, a), source_radius, root_scale, neighbour_root, 0)
    onsite_q = sp.symbols("onsite_q")
    onsite = sp.Rational(3, 5) * (onsite_q**4 - (onsite_q - a) ** 4) / 4
    onsite_rate = weighted_rate(onsite, (onsite_q, a), source_radius, root_scale, sp.Integer(1), 0)
    local_rate = sp.factor(onsite_rate + 3 * edge_u_rate + 6 * bond_u_rate)
    weighted_local_rate = sp.factor(time * local_rate)
    audit.check("edge centered rate", edge_u_rate == sp.Rational(203393, 3584), edge_u_rate, "203393/3584", "majorant")
    audit.check("edge relabelled rate", edge_v_rate == edge_u_rate, edge_v_rate, edge_u_rate, "orientation")
    audit.check("bond centered rate", bond_u_rate == sp.Rational(97, 48), bond_u_rate, "97/48", "majorant")
    audit.check("bond relabelled rate", bond_v_rate == bond_u_rate, bond_v_rate, bond_u_rate, "orientation")
    audit.check("onsite rate", onsite_rate == sp.Rational(10791, 1024), onsite_rate, "10791/1024", "composition")
    audit.check("local rate", local_rate == sp.Rational(1382807, 7168), local_rate, "1382807/7168", "composition")
    audit.check("weighted local rate", weighted_local_rate == sp.Rational(1382807, 57344), weighted_local_rate, "1382807/57344", "composition")
    audit.check("spatial cost retained", weight_center / weight_neighbor == 16 and neighbour_root**4 == 16, [weight_center / weight_neighbor, neighbour_root**4], 16, "spatial")
    audit.check("conditional history scope", manifest["scope"]["weighted_mixed_graph_lift_closed_conditionally"] is True and manifest["scope"]["history_product_closed"] is False, manifest["scope"], "conditional/false", "scope")
    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "scalar_rows": scalar_rows,
        "derived": {
            "gamma": gamma,
            "kappa": kappa,
            "energy_ratio": ratio,
            "root_scale": root_scale,
            "weight_center": weight_center,
            "weight_neighbor": weight_neighbor,
            "neighbor_factor_root": neighbour_root,
            "edge_weighted_rate": edge_u_rate,
            "edge_relabelled_rate": edge_v_rate,
            "bond_weighted_rate": bond_u_rate,
            "bond_relabelled_rate": bond_v_rate,
            "onsite_rate": onsite_rate,
            "local_rate": local_rate,
            "weighted_local_rate": weighted_local_rate,
            "scalar_mixed_lift_closed": True,
            "weighted_mixed_graph_lift_closed_conditionally": True,
            "edge_one_step_bridge_closed_conditionally": True,
            "bond_one_step_bridge_closed_conditionally": True,
            "spatial_weight_cost_explicit": True,
            "mixed_graph_hypothesis_independent": False,
            "history_product_closed": False,
            "actual_q3_history_closed": False,
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
    print(f"PRIMARY Q3-WEIGHTED-MIXED-GRAPH PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
