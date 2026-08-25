#!/usr/bin/env python3
"""Independent exact-arithmetic lane for EXP-001130."""

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
SLUG = "pre_a_cp1_st8_q3lock_common_core_form_comparison"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-common-core-form-comparison-manifest.json"
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
    return rows[:8] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]
def run() -> dict[str, Any]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = data["finite_fixture"], data["scope"]
    c = Fraction(fixture["c"])
    lam = Fraction(fixture["lambda"])
    chi = Fraction(fixture["chi"])
    mass = Fraction(fixture["r"])
    quartic = Fraction(fixture["g"])
    bond_c = Fraction(fixture["bond_form_constant"])
    values = tuple(Fraction(v) for v in fixture["grid_values"])
    lower_site = -(mass * mass) / (4 * quartic)
    lower_pair = 2 * lower_site
    shift = 1 - lower_pair
    bond_alpha = 1 + 4 * lam / quartic
    h_factor = 1 + 2 * bond_alpha
    remainder = bond_c + shift - h_factor * shift
    absorbed = h_factor + remainder
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", data["exploration_id"] == "EXP-001130" and data["task_id"] == "T-054", [data["exploration_id"], data["task_id"]], "EXP-001130/T-054", "provenance")
    check("claim nonbearing", data["claim_bearing"] is False, data["claim_bearing"], False, "scope")
    check("scope firewall", scope["common_core_form_comparison_closed"] and scope["positive_canonical_shift_closed"] and not scope["friedrichs_operator_realisation_closed"], scope, "form contract only", "scope")
    check("constants", [lower_pair, shift, h_factor, remainder, absorbed] == [Fraction(fixture["pair_lower_bound"]), Fraction(fixture["canonical_shift"]), Fraction(fixture["onsite_form_coefficient"]), Fraction(fixture["edge_remainder"]), Fraction(fixture["two_orientation_constant"])], [lower_pair, shift, h_factor, remainder, absorbed], "fixture constants", "constants")

    def potential(x: Fraction, p: Fraction) -> Fraction:
        return p * p / (2 * chi) + mass * x * x / 2 + quartic * x**4 / 4

    def interaction(x: Fraction, y: Fraction) -> Fraction:
        d = x - y
        return c * d * d / 2 + lam * d * d * (x * x + y * y) / 4

    minima = {"lower": None, "bond": None, "reverse": None, "upper": None, "absorbed": None}
    count = 0
    for x, y, p, q in product(values, repeat=4):
        h = potential(x, p) + potential(y, q)
        b = interaction(x, y)
        k0 = h + shift
        k1 = h + b + shift
        gaps = {"lower": h - lower_pair, "bond": b, "reverse": k1 - k0, "upper": h_factor * k0 + remainder - k1, "absorbed": absorbed * k0 - k1}
        for label, gap in gaps.items():
            check(f"grid row {count} {label}", gap >= 0, gap, ">=0", "form comparison")
            if minima[label] is None or gap < minima[label]:
                minima[label] = gap
        count += 1
    check("grid coverage", count == len(values) ** 4, count, len(values) ** 4, "grid")
    check("K_on >= I fixture", lower_pair + shift == 1, lower_pair + shift, 1, "positivity")
    check("open domain boundary", scope["friedrichs_operator_realisation_closed"] is False and scope["weighted_product_domain_closed"] is False, scope, "open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-COMMON-CORE-FORM-COMPARISON", "claim_id": data["claim_ids"][0], "task_id": data["task_id"], "exploration_id": data["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": compact_assertions(rows), "derived": {"grid_rows": count, "pair_lower_bound": str(lower_pair), "canonical_shift": str(shift), "edge_coefficient": str(h_factor), "edge_remainder": str(remainder), "two_orientation_constant_squared": str(absorbed), "minimum_slack": {label: str(value) for label, value in minima.items()}, "common_core_scalar_lower_bound_closed": True, "common_core_form_comparison_closed": True, "positive_canonical_shift_closed": True, "two_orientation_square_root_inclusion_contract_closed": True, "friedrichs_operator_realisation_closed": False, "weighted_product_domain_closed": False, "common_alpha_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT COMMON-CORE-FORM-COMPARISON PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
