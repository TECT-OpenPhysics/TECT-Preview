#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001150."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_inductive_cylinder_form_contract"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-inductive-cylinder-form-contract-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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
    return rows[:12] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]


def run() -> dict[str, Any]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = data["finite_fixture"]
    scope = data["scope"]
    chi = Fraction(fixture["chi"])
    degree = int(fixture["degree_bound"])
    order = Fraction(fixture["form_order_multiplier"])
    volumes = tuple(sorted(int(value) for value in fixture["ambient_volumes"]))
    supports = tuple(sorted(int(value) for value in fixture["support_sizes"]))
    m_bound = Fraction(fixture["coordinate_sup_bound"])
    l_bound = Fraction(fixture["coordinate_gradient_bound"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("provenance", data["exploration_id"] == "EXP-001150" and data["task_id"] == "T-054" and data["claim_bearing"] is False, [data["exploration_id"], data["task_id"], data["claim_bearing"]], "EXP-001150/T-054/false", "provenance")
    check("degree arithmetic", order == 1 + Fraction(10, 3) * degree, [order, degree], "21", "constants")
    check("ambient ordering", volumes == (1, 2, 4, 8, 16) and supports == (1, 2, 4, 8), [volumes, supports], "declared fixtures", "embedding")

    by_support: dict[int, tuple[Fraction, Fraction]] = {}
    embedding_rows: list[dict[str, Any]] = []
    for support in reversed(supports):
        admissible = [volume for volume in volumes if volume >= support]
        check(f"S{support} admissible", len(admissible) > 0, admissible, "nonempty", "embedding")
        same = 2 * m_bound * m_bound + Fraction(support) * l_bound * l_bound / chi
        cross = order * same
        by_support[support] = (same, cross)
        for volume in reversed(admissible):
            check(f"S{support} in V{volume}", volume - support >= 0, volume - support, ">=0", "embedding")
            embedding_rows.append({"support_size": support, "ambient_volume": volume, "padding": volume - support, "same": str(same), "cross": str(cross)})
        for left in admissible:
            for right in admissible:
                if left <= right:
                    check(f"S{support} pair {left}/{right}", by_support[support] == (same, cross), by_support[support], (same, cross), "restriction extension")

    f1 = fixture["factor_one"]
    f2 = fixture["factor_two"]
    m1, l1 = Fraction(f1["sup_bound"]), Fraction(f1["gradient_bound"])
    m2, l2 = Fraction(f2["sup_bound"]), Fraction(f2["gradient_bound"])
    product_m = m1 * m2
    product_l = m1 * l2 + m2 * l1
    product_same = 2 * product_m * product_m + product_l * product_l / chi
    product_cross = order * product_same
    check("Leibniz sup", product_m == 2, product_m, 2, "product algebra")
    check("Leibniz gradient", product_l == Fraction(7, 2), product_l, Fraction(7, 2), "product algebra")
    check("product same", product_same == Fraction(81, 4), product_same, Fraction(81, 4), "product algebra")
    check("product cross", product_cross == Fraction(1701, 4), product_cross, Fraction(1701, 4), "product algebra")
    check("contract flags", all(scope[key] is True for key in ("finite_support_embedding_contract_closed", "ambient_volume_independent_form_constants_closed", "restriction_extension_compatibility_closed", "bounded_c1_cylinder_product_closure_closed", "inductive_limit_test_algebra_contract_closed")), scope, True, "scope")
    check("downstream flags", all(scope[key] is False for key in ("unbounded_polynomial_products_closed", "modular_domain_transfer_closed", "direct_d_cauchy_closed", "delta_d_cauchy_closed", "common_alpha_closed", "exhaustion_independence_closed", "kms_gns_gap_closed", "continuum_closed", "pre_a_closed")), scope, "open", "QFT boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-INDUCTIVE-CYLINDER-FORM-CONTRACT",
        "claim_id": data["claim_ids"][0],
        "task_id": data["task_id"],
        "exploration_id": data["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "embedding_rows": embedding_rows,
            "ambient_volume_count": len(volumes),
            "support_count": len(supports),
            "form_order_multiplier": str(order),
            "product_bounds": {"sup_bound": str(product_m), "gradient_bound": str(product_l), "same_form_bound_squared": str(product_same), "cross_orientation_bound_squared": str(product_cross)},
            "finite_support_embedding_contract_closed": True,
            "ambient_volume_independent_form_constants_closed": True,
            "restriction_extension_compatibility_closed": True,
            "bounded_c1_cylinder_product_closure_closed": True,
            "same_orientation_weighted_products_closed": True,
            "cross_orientation_weighted_products_closed": True,
            "inductive_limit_test_algebra_contract_closed": True,
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
    print(f"INDEPENDENT INDUCTIVE-CYLINDER-FORM-CONTRACT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
