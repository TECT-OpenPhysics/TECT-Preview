#!/usr/bin/env python3
"""Independent Decimal lane for EXP-001112."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_registered_m20_uniform_hard_cutoff_corollary"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"
getcontext().prec = 80


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def fifth_root(radius: int) -> int:
    root = 1
    while root**5 < radius:
        root += 1
    if root**5 != radius:
        raise AssertionError(radius)
    return root


def decimal_fraction(value: Any) -> Decimal:
    text = str(value)
    if '/' in text:
        numerator, denominator = text.split('/', 1)
        return Decimal(numerator) / Decimal(denominator)
    return Decimal(text)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001112" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001112/T-054", "provenance")
    scope = manifest["scope"]
    check("scope firewall", scope["registered_finite_periodic_m20_uniform_corollary_closed"] and not scope["all_shape_exhaustion_closed"] and not scope["common_alpha_closed"], scope, "registered finite scope", "scope")

    d5 = decimal_fraction(fixture["d5"])
    transport = decimal_fraction(fixture["transport_factor_exp_G5T"])
    s_mu = decimal_fraction(fixture["S_mu"])
    m5 = decimal_fraction(fixture["m5"])
    c = decimal_fraction(fixture["c"])
    m20_star = Decimal(2) * d5**2 * transport * s_mu**5 * m5
    tail_constant = decimal_fraction(fixture["safe_tail_constant"])
    derived_tail_constant = Decimal(2916) * c**2 * m20_star
    check("M20 composition", m20_star == Decimal(120), m20_star, Decimal(120), "M20")
    check("tail constant composition", derived_tail_constant == tail_constant, derived_tail_constant, tail_constant, "tail")
    tail_rows: list[dict[str, Any]] = []
    for radius in [int(value) for value in fixture["R_values_exact_fifth_power"]]:
        root = fifth_root(radius)
        length = root**2
        tail = tail_constant * Decimal(radius) ** 2 / Decimal(length) ** 16
        check(f"R={radius} cutoff", length**5 == radius**2, length, "R^(2/5)", "cutoff")
        check(f"R={radius} tail nonnegative", tail >= 0, tail, ">=0", "tail")
        tail_rows.append({"R": radius, "L": length, "tail": str(tail)})
    check("tail decreases", Decimal(tail_rows[-1]["tail"]) < Decimal(tail_rows[0]["tail"]), tail_rows[-1]["tail"], "below initial", "tail")
    check("transport factor positive", transport > 0, transport, ">0", "inputs")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-REGISTERED-M20-UNIFORM-HARD-CUTOFF-COROLLARY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "M20_star": str(m20_star),
            "tail_constant": str(tail_constant),
            "tail_rows": tail_rows,
            "registered_finite_periodic_m20_uniform_corollary_closed": True,
            "registered_finite_periodic_hard_cutoff_uniform_corollary_closed": True,
            "registered_inputs_reused": True,
            "all_shape_exhaustion_closed": False,
            "beta_uniformity_closed": False,
            "actual_unbounded_q3_common_core_closed": False,
            "direct_d_delta_d_cauchy_closed": False,
            "common_alpha_closed": False
        },
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT REGISTERED-M20-HARD-CUTOFF-COROLLARY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
