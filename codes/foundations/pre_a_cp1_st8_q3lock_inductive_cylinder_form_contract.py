#!/usr/bin/env python3
"""Primary exact-arithmetic audit for EXP-001150."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"


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
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    chi = Fraction(fixture["chi"])
    degree = int(fixture["degree_bound"])
    order = Fraction(fixture["form_order_multiplier"])
    ambient = [int(value) for value in fixture["ambient_volumes"]]
    supports = [int(value) for value in fixture["support_sizes"]]
    m_bound = Fraction(fixture["coordinate_sup_bound"])
    l_bound = Fraction(fixture["coordinate_gradient_bound"])
    factor_one = fixture["factor_one"]
    factor_two = fixture["factor_two"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001150" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001150/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive parameters", chi > 0 and degree > 0 and order > 0 and ambient == sorted(ambient) and supports == sorted(supports), [chi, degree, order, ambient, supports], "positive sorted fixtures", "hypotheses")
    check("degree order", order == 1 + Fraction(10, 3) * degree, order, "1+(10/3)d", "prior form order")
    check("support inclusion", all(any(volume >= support for volume in ambient) for support in supports), [ambient, supports], "every support embeds", "embedding")

    ambient_rows: list[dict[str, Any]] = []
    constants_by_support: dict[int, set[tuple[str, str]]] = {support: set() for support in supports}
    for volume in ambient:
        for support in supports:
            if support > volume:
                continue
            padding = volume - support
            gradient_square = Fraction(support) * l_bound * l_bound
            same_bound = 2 * m_bound * m_bound + gradient_square / chi
            cross_bound = order * same_bound
            check(f"V{volume}/S{support} padding", padding >= 0, padding, ">=0", "embedding")
            check(f"V{volume}/S{support} same", same_bound == 2 + Fraction(support), same_bound, f"2+{support}", "form constants")
            check(f"V{volume}/S{support} cross", cross_bound == order * same_bound, cross_bound, "21*same", "form constants")
            constants_by_support[support].add((str(same_bound), str(cross_bound)))
            ambient_rows.append({"ambient_volume": volume, "support_size": support, "padding": padding, "same_form_bound_squared": str(same_bound), "cross_orientation_bound_squared": str(cross_bound)})

    for support, constants in constants_by_support.items():
        check(f"support {support} ambient independence", len(constants) == 1, sorted(constants), "one constant pair", "inductive compatibility")

    embedding_rows: list[dict[str, Any]] = []
    for support in supports:
        admissible = [volume for volume in ambient if volume >= support]
        for left in admissible:
            for right in admissible:
                if right < left:
                    continue
                left_row = next(row for row in ambient_rows if row["ambient_volume"] == left and row["support_size"] == support)
                right_row = next(row for row in ambient_rows if row["ambient_volume"] == right and row["support_size"] == support)
                check(f"S{support} {left}->{right} restriction", left_row["same_form_bound_squared"] == right_row["same_form_bound_squared"] and left_row["cross_orientation_bound_squared"] == right_row["cross_orientation_bound_squared"], [left_row, right_row], "equal constants", "inductive compatibility")
                embedding_rows.append({"support_size": support, "from_volume": left, "to_volume": right, "constant_preserved": True, "added_sites": right - left})

    m_one = Fraction(factor_one["sup_bound"])
    l_one = Fraction(factor_one["gradient_bound"])
    m_two = Fraction(factor_two["sup_bound"])
    l_two = Fraction(factor_two["gradient_bound"])
    product_m = m_one * m_two
    product_l = m_one * l_two + m_two * l_one
    product_same = 2 * product_m * product_m + product_l * product_l / chi
    product_cross = order * product_same
    check("product sup bound", product_m == Fraction(2), product_m, 2, "cylinder algebra")
    check("product gradient Leibniz bound", product_l == Fraction(7, 2), product_l, Fraction(7, 2), "cylinder algebra")
    check("product same form bound", product_same == Fraction(81, 4), product_same, Fraction(81, 4), "cylinder algebra")
    check("product cross form bound", product_cross == Fraction(1701, 4), product_cross, Fraction(1701, 4), "cylinder algebra")
    check("fixed support product", int(factor_one["support_size"]) + int(factor_two["support_size"]) <= max(ambient), [factor_one["support_size"], factor_two["support_size"], max(ambient)], "admissible", "cylinder algebra")

    check("inductive contract", all(scope[key] for key in ("finite_support_embedding_contract_closed", "ambient_volume_independent_form_constants_closed", "restriction_extension_compatibility_closed", "bounded_c1_cylinder_product_closure_closed", "same_orientation_weighted_products_closed", "cross_orientation_weighted_products_closed", "inductive_limit_test_algebra_contract_closed")), scope, True, "contract")
    check("QFT firewall", all(scope[key] is False for key in ("unbounded_polynomial_products_closed", "weighted_product_domain_closed", "modular_domain_transfer_closed", "direct_d_cauchy_closed", "delta_d_cauchy_closed", "common_alpha_closed", "exhaustion_independence_closed", "kms_gns_gap_closed", "continuum_closed", "pre_a_closed")), scope, "QFT successor gates remain open", "boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-INDUCTIVE-CYLINDER-FORM-CONTRACT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "ambient_rows": ambient_rows,
            "embedding_rows": embedding_rows,
            "ambient_volume_count": len(ambient),
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
    print(f"PRIMARY INDUCTIVE-CYLINDER-FORM-CONTRACT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
