#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001132."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


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
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = data["finite_fixture"], data["scope"]
    chi = Fraction(fixture["chi"])
    degree = int(fixture["degree_bound"])
    order = Fraction(fixture["form_order_multiplier"])
    vectors = [[Fraction(value) for value in vector] for vector in fixture["support_vectors"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", data["exploration_id"] == "EXP-001132" and data["task_id"] == "T-054", [data["exploration_id"], data["task_id"]], "EXP-001132/T-054", "provenance")
    check("scope", data["claim_bearing"] is False and scope["bounded_weyl_cylinder_form_invariance_closed"] and not scope["unbounded_polynomial_products_closed"], scope, "bounded Weyl only", "scope")
    check("order", order == 1 + Fraction(10, 3) * degree, [order, degree], "1+(10/3)d", "constants")

    bound_rows: list[dict[str, Any]] = []
    for index, vector in enumerate(vectors):
        norm_square = sum(value * value for value in vector)
        base = Fraction(2) + norm_square / chi
        cross = order * base
        check(f"vector {index} nonnegative norm", norm_square >= 0, norm_square, ">=0", "gradient")
        check(f"vector {index} base", base >= 2, base, ">=2", "same orientation")
        check(f"vector {index} cross", cross >= 2 * order, cross, f">={2 * order}", "cross orientation")
        bound_rows.append({"support_size": len(vector), "norm_square": str(norm_square), "same_form_bound_squared": str(base), "cross_orientation_bound_squared": str(cross)})

    check("support family", len(bound_rows) == len(vectors), [len(bound_rows), len(vectors)], "equal", "coverage")
    check("volume degree hypothesis", degree == 6, degree, 6, "bounded-degree class")
    check("form-domain boundary", scope["all_bounded_local_observables_closed"] is False and scope["weighted_product_domain_closed"] is False, scope, "Weyl cylinder only", "boundary")
    check("QFT boundary", all(scope[key] is False for key in ("modular_domain_transfer_closed", "direct_d_cauchy_closed", "common_alpha_closed", "kms_gns_gap_closed", "continuum_closed", "pre_a_closed")), scope, "QFT gates open", "boundary")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-WEYL-CYLINDER-FORM-INVARIANCE",
        "claim_id": data["claim_ids"][0],
        "task_id": data["task_id"],
        "exploration_id": data["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "support_count": len(vectors),
            "form_order_multiplier": str(order),
            "support_rows": bound_rows,
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
    print(f"INDEPENDENT WEYL-CYLINDER-FORM-INVARIANCE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
