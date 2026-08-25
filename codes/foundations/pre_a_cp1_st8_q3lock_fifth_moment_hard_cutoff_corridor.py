#!/usr/bin/env python3
"""Primary scalar corridor audit for EXP-001111."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_fifth_moment_hard_cutoff_corridor"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


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


def exact_root_power(radius: int, denominator: int) -> int:
    root = round(radius ** (1.0 / denominator))
    if root**denominator != radius:
        raise AssertionError(f"radius {radius} is not an exact {denominator}-th power")
    return root


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001111" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001111/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", manifest["scope"]["hard_cutoff_polynomial_corridor_closed"] and not manifest["scope"]["q3_m20_uniformity_reproved"] and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "conditional corridor", "scope")

    a = Fraction(int(fixture["multiplicity_factor"]))
    b = Fraction(int(fixture["multiplicity_linear_factor"]))
    safe_m = Fraction(int(fixture["safe_m_constant"]))
    safe_square = Fraction(int(fixture["safe_square_constant"]))
    c = Fraction(str(fixture["c"]))
    m20 = Fraction(str(fixture["M20"]))
    cutoff_num = int(fixture["cutoff_exponent_numerator"])
    cutoff_den = int(fixture["cutoff_exponent_denominator"])
    tail_power = int(fixture["tail_power"])
    radius_power = int(fixture["radius_power"])
    multiplicity_rows: list[dict[str, Any]] = []
    for radius in [int(value) for value in fixture["R_values_exact_fifth_power"]]:
        root = exact_root_power(radius, cutoff_den)
        cutoff = root**cutoff_num
        multiplicity = a * radius * (b * radius + 1) ** 2
        check(f"R={radius} exact cutoff", cutoff**cutoff_den == radius**cutoff_num, cutoff, f"R^({cutoff_num}/{cutoff_den})", "cutoff")
        check(f"R={radius} multiplicity safety", multiplicity <= safe_m * radius**3, multiplicity, f"<={safe_m}R^3", "multiplicity")
        exact_tail = multiplicity**2 * c**2 * m20 / cutoff**tail_power
        safe_tail = safe_square * c**2 * m20 * Fraction(radius) ** radius_power / Fraction(cutoff) ** tail_power
        check(f"R={radius} tail safety", exact_tail <= safe_tail, exact_tail, f"<={safe_tail}", "tail")
        multiplicity_rows.append({"R": radius, "root": root, "L": cutoff, "m_R": str(multiplicity), "exact_tail": str(exact_tail), "safe_tail": str(safe_tail)})

    factorial_rows: list[dict[str, Any]] = []
    factorial_c = Fraction(str(fixture["factorial_C"]))
    for radius in [int(value) for value in fixture["R_values_exact_fifth_power"]]:
        root = exact_root_power(radius, cutoff_den)
        r_four_fifths = root ** int(fixture["factorial_radius_numerator"])
        exact_log = radius * math.log(float(factorial_c * r_four_fifths)) - math.lgamma(radius + 1.0)
        base = math.e * float(factorial_c) * radius ** (-1.0 / cutoff_den)
        majorant_log = radius * math.log(base)
        check(f"R={radius} factorial nonnegative", math.isfinite(exact_log), exact_log, "finite log", "factorial")
        check(f"R={radius} factorial Stirling comparison", exact_log <= majorant_log + 1.0e-10, exact_log, f"<={majorant_log}", "factorial")
        factorial_rows.append({"R": radius, "R_four_fifths": r_four_fifths, "exact_log": exact_log, "majorant_log": majorant_log, "base": base})

    check("safe constant derivation", safe_m**2 == safe_square, safe_m**2, safe_square, "constants")
    check("tail exponent reduction", Fraction(radius_power * cutoff_den - cutoff_num * tail_power, cutoff_den) == Fraction(-cutoff_num, cutoff_den), Fraction(radius_power * cutoff_den - cutoff_num * tail_power, cutoff_den), Fraction(-cutoff_num, cutoff_den), "exponents")
    check("large-radius factorial base", factorial_rows[-1]["base"] < 1.0, factorial_rows[-1]["base"], "<1", "factorial")
    check("corridor decreases", Fraction(multiplicity_rows[-1]["safe_tail"]) < Fraction(multiplicity_rows[0]["safe_tail"]), multiplicity_rows[-1]["safe_tail"], "below initial", "tail")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FIFTH-MOMENT-HARD-CUTOFF-CORRIDOR",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "multiplicity_rows": multiplicity_rows,
            "factorial_rows": factorial_rows,
            "multiplicity_bound_closed": True,
            "hard_cutoff_polynomial_corridor_closed": True,
            "factorial_shell_scalar_majorant_closed": True,
            "registered_m20_input_reused": True,
            "q3_m20_uniformity_reproved": False,
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
    print(f"PRIMARY FIFTH-MOMENT-HARD-CUTOFF-CORRIDOR PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
