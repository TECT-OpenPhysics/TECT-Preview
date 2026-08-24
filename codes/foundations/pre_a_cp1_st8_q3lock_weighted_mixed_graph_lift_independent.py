#!/usr/bin/env python3
"""Independent exact polynomial/Fraction audit for EXP-001045."""

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
SLUG = "pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"
Poly = dict[tuple[int, ...], F]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, F):
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


def clean(poly: Poly) -> Poly:
    return {monomial: coefficient for monomial, coefficient in poly.items() if coefficient}


def add(*polys: Poly) -> Poly:
    result: Poly = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] = result.get(monomial, F(0)) + coefficient
    return clean(result)


def scale(poly: Poly, coefficient: F) -> Poly:
    return clean({monomial: coefficient * value for monomial, value in poly.items()})


def mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(a + b for a, b in zip(left_monomial, right_monomial))
            result[monomial] = result.get(monomial, F(0)) + left_coefficient * right_coefficient
    return clean(result)


def power(poly: Poly, exponent: int) -> Poly:
    result = {(0,) * len(next(iter(poly))): F(1)}
    for _ in range(exponent):
        result = mul(result, poly)
    return result


def variable(index: int, dimension: int) -> Poly:
    exponent = [0] * dimension
    exponent[index] = 1
    return {tuple(exponent): F(1)}


def weighted_rate(poly: Poly, source_radius: F, root_scale: F, neighbour_root: F, neighbour_index: int) -> F:
    return sum(abs(coefficient) * root_scale ** sum(monomial[:-1]) * neighbour_root ** monomial[neighbour_index] * source_radius ** monomial[-1] for monomial, coefficient in poly.items())


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    gamma = F(fixture["gamma"])
    kappa = F(fixture["kappa"])
    ratio = F(fixture["energy_ratio"])
    root_scale = F(fixture["root_scale"])
    weight_center = F(fixture["weight_center"])
    weight_neighbor = F(fixture["weight_neighbor"])
    neighbour_root = F(fixture["neighbor_factor_root"])
    lam = F(fixture["lambda"])
    coupling = F(fixture["spatial_coupling"])
    source_radius = F(fixture["source_radius"])
    time = F(fixture["time"])
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001045" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001045/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("positive inputs", gamma > 0 and kappa > 0 and source_radius > 0 and time > 0, [gamma, kappa, source_radius, time], ">0", "hypothesis")
    audit.check("energy ratio root", root_scale**4 == ratio and ratio == kappa / gamma, [root_scale, ratio, kappa / gamma], "root^4=kappa/gamma", "hypothesis")
    audit.check("weight fixture", weight_center == 1 and weight_neighbor == F(1, 16) and neighbour_root**4 == weight_center / weight_neighbor, [weight_center, weight_neighbor, neighbour_root], "1,1/16,2^4=16", "hypothesis")

    scalar_rows: list[dict[str, Any]] = []
    for total_degree in (1, 2, 3):
        for i in range(total_degree + 1):
            j = total_degree - i
            coefficients = [math.comb(total_degree, exponent) for exponent in range(total_degree + 1)]
            # Every coefficient in (X+Y)^m is nonnegative and the selected
            # monomial has coefficient at least one, hence the powered lift.
            audit.check(f"scalar lift i={i} j={j}", all(value >= 0 for value in coefficients) and coefficients[i] >= 1, coefficients, ">=0 and selected coefficient >=1", "scalar")
            scalar_rows.append({"i": i, "j": j, "selected_binomial": coefficients[i]})
    audit.check("powered scalar fixture", F(1) ** 2 * F(16) <= (F(1) + F(16)) ** 3, 16, "<=4913", "scalar")

    q, v, a = variable(0, 3), variable(1, 3), variable(2, 3)
    r = variable(1, 3)
    q_minus_v = add(q, scale(v, F(-1)))
    q_minus_a_minus_v = add(q, scale(a, F(-1)), scale(v, F(-1)))
    edge_u = scale(add(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), scale(mul(power(q_minus_a_minus_v, 2), add(power(add(q, scale(a, F(-1))), 2), power(v, 2))), F(-1))), lam / 4)
    edge_v = scale(add(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), scale(mul(power(add(q, scale(v, F(-1)), a), 2), add(power(q, 2), power(add(v, scale(a, F(-1))), 2))), F(-1))), lam / 4)
    q_minus_r = add(q, scale(r, F(-1)))
    q_minus_a_minus_r = add(q, scale(a, F(-1)), scale(r, F(-1)))
    bond_u = scale(add(power(q_minus_r, 2), scale(power(q_minus_a_minus_r, 2), F(-1))), coupling / 2)
    bond_v = scale(add(power(q_minus_r, 2), scale(power(add(q, scale(r, F(-1)), a), 2), F(-1))), coupling / 2)
    edge_u_rate = weighted_rate(edge_u, source_radius, root_scale, neighbour_root, 1)
    edge_v_rate = weighted_rate(edge_v, source_radius, root_scale, neighbour_root, 0)
    bond_u_rate = weighted_rate(bond_u, source_radius, root_scale, neighbour_root, 1)
    bond_v_rate = weighted_rate(bond_v, source_radius, root_scale, neighbour_root, 0)
    onsite_q, onsite_a = variable(0, 2), variable(1, 2)
    onsite = scale(add(power(onsite_q, 4), scale(power(add(onsite_q, scale(onsite_a, F(-1))), 4), F(-1))), F(3, 20))
    onsite_rate = weighted_rate(onsite, source_radius, root_scale, F(1), 0)
    local_rate = onsite_rate + 3 * edge_u_rate + 6 * bond_u_rate
    weighted_local_rate = time * local_rate
    audit.check("edge centered rate", edge_u_rate == F(203393, 3584), edge_u_rate, "203393/3584", "majorant")
    audit.check("edge relabelled rate", edge_v_rate == edge_u_rate, edge_v_rate, edge_u_rate, "orientation")
    audit.check("bond centered rate", bond_u_rate == F(97, 48), bond_u_rate, "97/48", "majorant")
    audit.check("bond relabelled rate", bond_v_rate == bond_u_rate, bond_v_rate, bond_u_rate, "orientation")
    audit.check("onsite rate", onsite_rate == F(10791, 1024), onsite_rate, "10791/1024", "composition")
    audit.check("local rate", local_rate == F(1382807, 7168), local_rate, "1382807/7168", "composition")
    audit.check("weighted local rate", weighted_local_rate == F(1382807, 57344), weighted_local_rate, "1382807/57344", "composition")
    audit.check("spatial cost retained", weight_center / weight_neighbor == 16 and neighbour_root**4 == 16, [weight_center / weight_neighbor, neighbour_root**4], 16, "spatial")
    audit.check("conditional history scope", manifest["scope"]["weighted_mixed_graph_lift_closed_conditionally"] is True and manifest["scope"]["history_product_closed"] is False, manifest["scope"], "conditional/false", "scope")
    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
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
    print(f"INDEPENDENT Q3-WEIGHTED-MIXED-GRAPH PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
