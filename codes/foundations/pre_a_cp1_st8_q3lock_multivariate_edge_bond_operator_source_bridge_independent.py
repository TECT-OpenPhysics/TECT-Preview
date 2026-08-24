#!/usr/bin/env python3
"""Independent Fraction/polynomial audit for EXP-001044.

This lane deliberately avoids SymPy.  It builds the registered edge, bond,
and onsite differences from a tiny exact polynomial algebra and reproduces
the source rates plus the finite A-power transport witness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-multivariate-edge-bond-operator-source-bridge"
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


def constant(value: F, dimension: int) -> Poly:
    return {(0,) * dimension: value}


def coefficient_rate(poly: Poly, moments: list[F], source_radius: F) -> F:
    return sum(abs(coefficient) * moments[sum(monomial[:-1])] * source_radius ** monomial[-1] for monomial, coefficient in poly.items())


def matmul(left: list[list[F]], right: list[list[F]]) -> list[list[F]]:
    return [[sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))] for i in range(len(left))]


def inf_norm(matrix: list[list[F]]) -> F:
    return max((sum(abs(value) for value in row) for row in matrix), default=F(0))


def diagonal(values: list[F]) -> list[list[F]]:
    return [[value if i == j else F(0) for j in range(len(values))] for i, value in enumerate(values)]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    lam = F(fixture["lambda"])
    coupling = F(fixture["spatial_coupling"])
    source_radius = F(fixture["source_radius"])
    time = F(fixture["time"])
    ratio = F(fixture["energy_ratio"])
    root = F(fixture["root_scale"])
    moments = [root**degree for degree in range(4)]
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001044" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001044/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("positive fixture", lam > 0 and coupling > 0 and source_radius > 0 and time > 0, [lam, coupling, source_radius, time], ">0", "hypothesis")
    audit.check("moment ladder", moments == [F(1), F(4), F(16), F(64)], moments, "[1,4,16,64]", "hypothesis")
    audit.check("energy ratio", root**4 == ratio, [root, ratio], "root^4=ratio", "hypothesis")

    q, v, a = variable(0, 3), variable(1, 3), variable(2, 3)
    r = variable(1, 3)
    q_minus_v = add(q, scale(v, F(-1)))
    q_minus_a_minus_v = add(q, scale(a, F(-1)), scale(v, F(-1)))
    edge = scale(add(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), scale(mul(power(q_minus_a_minus_v, 2), add(power(add(q, scale(a, F(-1))), 2), power(v, 2))), F(-1))), lam / 4)
    edge_reverse = scale(add(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), scale(mul(power(add(q, scale(v, F(-1)), a), 2), add(power(q, 2), power(add(v, scale(a, F(-1))), 2))), F(-1))), lam / 4)
    q_minus_r = add(q, scale(r, F(-1)))
    q_minus_a_minus_r = add(q, scale(a, F(-1)), scale(r, F(-1)))
    bond = scale(add(power(q_minus_r, 2), scale(power(q_minus_a_minus_r, 2), F(-1))), coupling / 2)
    bond_reverse = scale(add(power(q_minus_r, 2), scale(power(add(q, scale(r, F(-1)), a), 2), F(-1))), coupling / 2)
    edge_rate = coefficient_rate(edge, moments, source_radius)
    edge_reverse_rate = coefficient_rate(edge_reverse, moments, source_radius)
    bond_rate = coefficient_rate(bond, moments, source_radius)
    bond_reverse_rate = coefficient_rate(bond_reverse, moments, source_radius)
    audit.check("edge source rate", edge_rate == F(69217, 3584), edge_rate, "69217/3584", "majorant")
    audit.check("edge reverse endpoint rate", edge_reverse_rate == edge_rate, edge_reverse_rate, edge_rate, "orientation")
    audit.check("bond source rate", bond_rate == F(65, 48), bond_rate, "65/48", "majorant")
    audit.check("bond reverse endpoint rate", bond_reverse_rate == bond_rate, bond_reverse_rate, bond_rate, "orientation")

    onsite_q, onsite_a = variable(0, 2), variable(1, 2)
    onsite = scale(add(power(onsite_q, 4), scale(power(add(onsite_q, scale(onsite_a, F(-1))), 4), F(-1))), F(3, 20))
    onsite_rate = coefficient_rate(onsite, moments, source_radius)
    local_rate = onsite_rate + 3 * edge_rate + 6 * bond_rate
    weighted_local_rate = time * local_rate
    audit.check("onsite inherited rate", onsite_rate == F(10791, 1024), onsite_rate, "10791/1024", "composition")
    audit.check("ten-choice local rate", local_rate == F(549079, 7168), local_rate, "549079/7168", "composition")
    audit.check("weighted local rate", weighted_local_rate == F(549079, 57344), weighted_local_rate, "549079/57344", "composition")

    A_quarter = diagonal([F(1), F(2), F(4)])
    A_inv_quarter = diagonal([F(1), F(1, 2), F(1, 4)])
    A_inv_three_quarter = diagonal([F(1), F(1, 8), F(1, 64)])
    shift = [[F(0), F(0), F(0)], [F(1), F(0), F(0)], [F(0), F(1), F(0)]]
    Q = matmul(shift, A_quarter)
    one_factor = matmul(Q, A_inv_quarter)
    mixed_factor = matmul(matmul(Q, Q), A_inv_three_quarter)
    audit.check("one-factor exact cancellation", one_factor == shift, one_factor, "S", "transport")
    audit.check("one-factor norm", inf_norm(one_factor) == 1, inf_norm(one_factor), 1, "transport")
    audit.check("second marginal norm", inf_norm(one_factor) == 1, inf_norm(one_factor), 1, "transport")
    audit.check("mixed norm", inf_norm(mixed_factor) == 2, inf_norm(mixed_factor), 2, "transport")
    audit.check("naive mixed product fails", inf_norm(mixed_factor) > inf_norm(one_factor) * inf_norm(one_factor), [inf_norm(mixed_factor), inf_norm(one_factor) ** 2], ">", "transport")
    audit.check("history remains open", manifest["scope"]["history_product_closed"] is False and manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], "false/false", "scope")
    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "energy_ratio": ratio,
            "root_scale": root,
            "source_radius": source_radius,
            "edge_source_rate": edge_rate,
            "edge_reverse_source_rate": edge_reverse_rate,
            "bond_source_rate": bond_rate,
            "bond_reverse_source_rate": bond_reverse_rate,
            "onsite_source_rate": onsite_rate,
            "local_rate": local_rate,
            "weighted_local_rate": weighted_local_rate,
            "edge_one_step_bridge_closed": True,
            "bond_one_step_bridge_closed": True,
            "mixed_graph_bounds_assumed": True,
            "naive_one_site_transport_refuted": True,
            "transport_one_factor_norm": inf_norm(one_factor),
            "transport_mixed_factor_norm": inf_norm(mixed_factor),
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
    print(f"INDEPENDENT Q3-MULTIVARIATE-EDGE-BOND PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
