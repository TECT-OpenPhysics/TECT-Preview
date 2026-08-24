#!/usr/bin/env python3
"""Primary exact audit for the conditional Q3 edge/bond source bridge.

The mixed two-site graph moments are declared inputs.  This audit expands the
actual Q3 edge and spatial bond source differences, computes the two-sided
coefficient majorants, and checks a finite matrix witness showing that
one-site graph bounds do not compose into a mixed bound without A-power
transport.  It is claim-nonbearing and does not assert a history theorem.
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
SLUG = "pre-a-cp1-st8-q3lock-multivariate-edge-bond-operator-source-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[safe(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
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


def coefficient_rate(polynomial: sp.Expr, variables: tuple[sp.Symbol, ...], moments: list[sp.Rational], source_radius: sp.Rational) -> sp.Rational:
    total = sp.Rational(0)
    for monomial, coefficient in sp.Poly(sp.expand(polynomial), *variables).terms():
        field_degree = sum(monomial[:-1])
        source_degree = monomial[-1]
        total += abs(coefficient) * moments[field_degree] * source_radius**source_degree
    return sp.factor(total)


def inf_norm(matrix: sp.Matrix) -> sp.Rational:
    return max((sum(abs(matrix[i, j]) for j in range(matrix.cols)) for i in range(matrix.rows)), default=sp.Rational(0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    time = sp.Rational(str(fixture["time"]))
    ratio = sp.Rational(str(fixture["energy_ratio"]))
    root = sp.Integer(str(fixture["root_scale"]))
    moments = [root**degree for degree in range(4)]

    q, v, r, a = sp.symbols("q v r a")
    edge_potential = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_shift = sp.expand(edge_potential - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    edge_reverse = sp.expand(edge_potential - lam * (q - (v - a)) ** 2 * (q**2 + (v - a) ** 2) / 4)
    bond_potential = coupling * (q - r) ** 2 / 2
    bond_shift = sp.expand(bond_potential - coupling * (q - a - r) ** 2 / 2)
    bond_reverse = sp.expand(bond_potential - coupling * (q - (r - a)) ** 2 / 2)

    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001044" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001044/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("positive fixture", lam > 0 and coupling > 0 and source_radius > 0 and time > 0, [lam, coupling, source_radius, time], ">0", "hypothesis")
    audit.check("moment ladder", moments == [sp.Integer(1), sp.Integer(4), sp.Integer(16), sp.Integer(64)], moments, "[1,4,16,64]", "hypothesis")
    audit.check("energy ratio", root**4 == ratio, [root, ratio], "root^4=ratio", "hypothesis")
    audit.check("edge potential convention", edge_potential == lam * (q - v) ** 2 * (q**2 + v**2) / 4, edge_potential, "registered V_e", "derivation")
    audit.check("bond potential convention", bond_potential == coupling * (q - r) ** 2 / 2, bond_potential, "registered V_b", "derivation")

    edge_rate = coefficient_rate(edge_shift, (q, v, a), moments, source_radius)
    edge_reverse_rate = coefficient_rate(edge_reverse, (q, v, a), moments, source_radius)
    bond_rate = coefficient_rate(bond_shift, (q, r, a), moments, source_radius)
    bond_reverse_rate = coefficient_rate(bond_reverse, (q, r, a), moments, source_radius)
    audit.check("edge source rate", edge_rate == sp.Rational(69217, 3584), edge_rate, "69217/3584", "majorant")
    audit.check("edge reverse endpoint rate", edge_reverse_rate == edge_rate, edge_reverse_rate, edge_rate, "orientation")
    audit.check("bond source rate", bond_rate == sp.Rational(65, 48), bond_rate, "65/48", "majorant")
    audit.check("bond reverse endpoint rate", bond_reverse_rate == bond_rate, bond_reverse_rate, bond_rate, "orientation")
    onsite_g = sp.Rational(3, 5)  # fixture input inherited from EXP-001043
    onsite_q = sp.symbols("onsite_q")
    onsite = onsite_g * (onsite_q**4 - (onsite_q - a) ** 4) / 4
    onsite_rate = coefficient_rate(onsite, (onsite_q, a), moments, source_radius)
    local_rate = sp.factor(onsite_rate + 3 * edge_rate + 6 * bond_rate)
    weighted_local_rate = sp.factor(time * local_rate)
    audit.check("onsite inherited rate", onsite_rate == sp.Rational(10791, 1024), onsite_rate, "10791/1024", "composition")
    audit.check("ten-choice local rate", local_rate == sp.Rational(549079, 7168), local_rate, "549079/7168", "composition")
    audit.check("weighted local rate", weighted_local_rate == sp.Rational(549079, 57344), weighted_local_rate, "549079/57344", "composition")

    # Exact finite transport obstruction.  A=diag(1,16,256), S raises one
    # level, and Q=S*A^(1/4).  Each Q*A^(-1/4) is S, but the mixed product
    # Q^2*A^(-3/4) has induced infinity norm two.
    A = sp.diag(1, 16, 256)
    A_quarter = sp.diag(1, 2, 4)
    A_inv_quarter = sp.diag(1, sp.Rational(1, 2), sp.Rational(1, 4))
    A_inv_three_quarter = sp.diag(1, sp.Rational(1, 8), sp.Rational(1, 64))
    shift = sp.Matrix([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    Q = shift * A_quarter
    one_factor = Q * A_inv_quarter
    mixed_factor = Q * Q * A_inv_three_quarter
    audit.check("transport A positive", all(A[i, i] > 0 for i in range(3)), list(A.diagonal()), ">0", "transport")
    audit.check("one-factor exact cancellation", one_factor == shift, one_factor, "S", "transport")
    audit.check("one-factor norm", inf_norm(one_factor) == 1, inf_norm(one_factor), 1, "transport")
    audit.check("second marginal norm", inf_norm(Q * A_inv_quarter) == 1, inf_norm(Q * A_inv_quarter), 1, "transport")
    audit.check("mixed norm", inf_norm(mixed_factor) == 2, inf_norm(mixed_factor), 2, "transport")
    audit.check("naive mixed product fails", inf_norm(mixed_factor) > inf_norm(one_factor) * inf_norm(one_factor), [inf_norm(mixed_factor), inf_norm(one_factor) ** 2], ">", "transport")
    audit.check("history remains open", manifest["scope"]["history_product_closed"] is False and manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], "false/false", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
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
        "polynomials": {"edge": edge_shift, "edge_reverse": edge_reverse, "bond": bond_shift, "bond_reverse": bond_reverse},
        "transport_fixture": {"A": A, "shift": shift, "Q": Q, "one_factor": one_factor, "mixed_factor": mixed_factor},
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
    print(f"PRIMARY Q3-MULTIVARIATE-EDGE-BOND PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
