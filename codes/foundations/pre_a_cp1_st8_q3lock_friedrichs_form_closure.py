#!/usr/bin/env python3
"""Primary exact-arithmetic audit for EXP-001131."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_friedrichs_form_closure"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-friedrichs-form-closure-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def compact_assertions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in rows:
        group = str(row.get("group", "unknown"))
        counts[group] = counts.get(group, 0) + 1
    summary = {"total": len(rows), "groups": counts, "storage": "compact-summary; all assertions executed in memory"}
    return rows[:10] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    c, lam, chi, r, g = (Fraction(fixture[key]) for key in ("c", "lambda", "chi", "r", "g"))
    bond_constant = Fraction(fixture["bond_form_constant"])
    degree_bound = int(fixture["degree_bound"])
    grid = [Fraction(value) for value in fixture["grid_values"]]
    volumes = [int(value) for value in fixture["volumes"]]
    site_lower = -(r * r) / (4 * g)
    alpha = 2 * (1 + 4 * lam / g)
    shift = Fraction(fixture["per_site_shift"])
    growth_remainder = bond_constant - 2 * alpha * shift
    multiplier = 1 + alpha * degree_bound
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001131" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001131/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("parameter hypotheses", chi > 0 and g > 0 and c >= 0 and lam >= 0, [chi, g, c, lam], "chi,g>0 and c,lambda>=0", "theorem hypotheses")
    check("site lower bound", site_lower == Fraction(fixture["site_lower_bound"]), site_lower, fixture["site_lower_bound"], "constants")
    check("bond coefficient", alpha == Fraction(fixture["bond_on_site_coefficient"]), alpha, fixture["bond_on_site_coefficient"], "constants")
    check("per-site coercive shift", site_lower + shift == 1, site_lower + shift, 1, "constants")
    check("growth remainder", growth_remainder == Fraction(fixture["growth_remainder"]) and growth_remainder <= 0, growth_remainder, fixture["growth_remainder"], "constants")
    check("degree multiplier", multiplier == Fraction(fixture["edge_multiplier"]), multiplier, fixture["edge_multiplier"], "constants")

    def potential(x: Fraction, p: Fraction) -> Fraction:
        return p * p / (2 * chi) + r * x * x / 2 + g * x**4 / 4

    def bond(x: Fraction, y: Fraction) -> Fraction:
        difference = x - y
        return c * difference * difference / 2 + lam * difference * difference * (x * x + y * y) / 4

    minimum_slack = {"lower": None, "bond": None, "envelope": None, "shifted_envelope": None, "kinetic_envelope": None}
    pair_count = 0
    for x, y, p, q in product(grid, repeat=4):
        vx, vy = potential(x, Fraction(0)), potential(y, Fraction(0))
        hx, hy = potential(x, p), potential(y, q)
        b = bond(x, y)
        slacks = {
            "lower": vx - site_lower,
            "bond": b,
            "envelope": alpha * (vx + vy) + bond_constant - b,
            "shifted_envelope": alpha * ((vx + shift) + (vy + shift)) - b,
            "kinetic_envelope": alpha * ((hx + shift) + (hy + shift)) - b,
        }
        for label, slack in slacks.items():
            check(f"pair row {pair_count} {label}", slack >= 0, slack, ">=0", "polynomial form bounds")
            if minimum_slack[label] is None or slack < minimum_slack[label]:
                minimum_slack[label] = slack
        pair_count += 1
    check("pair grid coverage", pair_count == len(grid) ** 4, pair_count, len(grid) ** 4, "grid")

    graph_rows: list[dict[str, Any]] = []
    for volume in volumes:
        edges = [(index, index + 1) for index in range(max(0, volume - 1))]
        degrees = [0] * volume
        for left, right in edges:
            degrees[left] += 1
            degrees[right] += 1
        check(f"graph volume {volume} degree", max(degrees, default=0) <= degree_bound, max(degrees, default=0), f"<={degree_bound}", "bounded-degree graph")
        check(f"graph volume {volume} incidence", sum(degrees) == 2 * len(edges), [sum(degrees), len(edges)], "2|E|", "bounded-degree graph")
        graph_rows.append({"volume": volume, "edges": len(edges), "max_degree": max(degrees, default=0)})

    hypotheses = all([
        scope["finite_graph_form_closure_closed"],
        scope["finite_graph_friedrichs_operator_realisation_closed"],
        scope["finite_graph_common_form_domain_closed"],
        scope["bounded_degree_shifted_form_order_closed"],
        scope["two_orientation_square_root_inclusion_closed"],
    ])
    check("standard finite-form theorem contract", hypotheses, scope, "fixed finite graph closure and order", "form theorem")
    check("product-domain firewall", scope["weighted_product_domain_closed"] is False and scope["direct_d_cauchy_closed"] is False and scope["delta_d_cauchy_closed"] is False, scope, "unbounded product and Cauchy gates remain open", "boundary")
    check("QFT firewall", all(scope[key] is False for key in ("common_alpha_closed", "modular_domain_transfer_closed", "kms_gns_gap_closed", "continuum_closed", "pre_a_closed")), scope, "QFT/limit gates remain open", "boundary")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FRIEDRICHS-FORM-CLOSURE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "pair_grid_rows": pair_count,
            "site_lower_bound": str(site_lower),
            "bond_on_site_coefficient": str(alpha),
            "per_site_shift": str(shift),
            "growth_remainder": str(growth_remainder),
            "degree_bound": degree_bound,
            "edge_multiplier": str(multiplier),
            "minimum_slack": {key: str(value) for key, value in minimum_slack.items()},
            "graph_rows": graph_rows,
            "finite_graph_form_closure_closed": True,
            "finite_graph_friedrichs_operator_realisation_closed": True,
            "finite_graph_common_form_domain_closed": True,
            "bounded_degree_shifted_form_order_closed": True,
            "two_orientation_square_root_inclusion_closed": True,
            "weighted_product_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FRIEDRICHS-FORM-CLOSURE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
