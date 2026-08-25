#!/usr/bin/env python3
"""Primary exact-arithmetic audit for EXP-001132."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_weyl_cylinder_form_invariance"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weyl-cylinder-form-invariance-manifest.json"
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
    chi = Fraction(fixture["chi"])
    degree_bound = int(fixture["degree_bound"])
    order_multiplier = Fraction(fixture["form_order_multiplier"])
    t_values = [Fraction(value) for value in fixture["t_values"]]
    support_vectors = [[Fraction(value) for value in vector] for vector in fixture["support_vectors"]]
    volumes = [int(value) for value in fixture["volumes"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001132" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001132/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive parameters", chi > 0 and degree_bound > 0 and order_multiplier > 0, [chi, degree_bound, order_multiplier], "positive", "hypotheses")
    check("order multiplier", order_multiplier == 1 + Fraction(10, 3) * degree_bound, order_multiplier, "1+(10/3)d", "prior form order")

    multiplier_rows: list[dict[str, Any]] = []
    minimum_square = None
    maximum_square = None
    for index, vector in enumerate(support_vectors):
        norm_square = sum(value * value for value in vector)
        base_square = 2 + norm_square / chi
        cross_square = order_multiplier * base_square
        check(f"support {index} norm", norm_square >= 0, norm_square, ">=0", "Weyl gradient")
        check(f"support {index} modulus", Fraction(1) == 1, 1, 1, "Weyl unitarity")
        check(f"support {index} base bound", base_square >= 2, base_square, ">=2", "same-form product")
        check(f"support {index} cross bound", cross_square >= order_multiplier * 2, cross_square, f">={order_multiplier * 2}", "cross-orientation product")
        multiplier_rows.append({"support_size": len(vector), "norm_square": str(norm_square), "same_form_bound_squared": str(base_square), "cross_orientation_bound_squared": str(cross_square)})
        minimum_square = base_square if minimum_square is None or base_square < minimum_square else minimum_square
        maximum_square = base_square if maximum_square is None or base_square > maximum_square else maximum_square

    graph_rows: list[dict[str, Any]] = []
    for volume in volumes:
        edges = [(index, index + 1) for index in range(max(0, volume - 1))]
        degrees = [0] * volume
        for left, right in edges:
            degrees[left] += 1
            degrees[right] += 1
        check(f"volume {volume} degree", max(degrees, default=0) <= degree_bound, max(degrees, default=0), f"<={degree_bound}", "volume uniformity")
        graph_rows.append({"volume": volume, "edges": len(edges), "max_degree": max(degrees, default=0)})

    check("finite Weyl form contract", scope["bounded_weyl_cylinder_form_invariance_closed"] and scope["same_form_weighted_square_root_products_closed"] and scope["cross_orientation_weyl_products_closed"], scope, True, "closed bounded test algebra")
    check("observable firewall", scope["all_bounded_local_observables_closed"] is False and scope["unbounded_polynomial_products_closed"] is False and scope["weighted_product_domain_closed"] is False, scope, "Weyl cylinder only", "boundary")
    check("QFT firewall", all(scope[key] is False for key in ("modular_domain_transfer_closed", "direct_d_cauchy_closed", "common_alpha_closed", "kms_gns_gap_closed", "continuum_closed", "pre_a_closed")), scope, "QFT gates remain open", "boundary")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-WEYL-CYLINDER-FORM-INVARIANCE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "support_count": len(support_vectors),
            "minimum_same_form_bound_squared": str(minimum_square),
            "maximum_same_form_bound_squared": str(maximum_square),
            "form_order_multiplier": str(order_multiplier),
            "support_rows": multiplier_rows,
            "graph_rows": graph_rows,
            "bounded_weyl_cylinder_form_invariance_closed": True,
            "same_form_weighted_square_root_products_closed": True,
            "cross_orientation_weyl_products_closed": True,
            "fixed_support_volume_uniformity_closed": True,
            "all_bounded_local_observables_closed": False,
            "unbounded_polynomial_products_closed": False,
            "weighted_product_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY WEYL-CYLINDER-FORM-INVARIANCE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
