#!/usr/bin/env python3
"""Independent Decimal/integer lane for EXP-001111."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_fifth_moment_hard_cutoff_corridor"
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


def exact_fifth_root(radius: int) -> int:
    candidate = 1
    while candidate**5 < radius:
        candidate += 1
    if candidate**5 != radius:
        raise AssertionError(radius)
    return candidate


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001111" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001111/T-054", "provenance")
    check("scope firewall", manifest["scope"]["hard_cutoff_polynomial_corridor_closed"] and not manifest["scope"]["q3_m20_uniformity_reproved"], manifest["scope"], "conditional corridor", "scope")

    multiplier = int(fixture["multiplicity_factor"])
    linear = int(fixture["multiplicity_linear_factor"])
    safe_m = int(fixture["safe_m_constant"])
    safe_square = int(fixture["safe_square_constant"])
    radius_rows: list[dict[str, Any]] = []
    for radius in [int(value) for value in fixture["R_values_exact_fifth_power"]]:
        root = exact_fifth_root(radius)
        length = root**int(fixture["cutoff_exponent_numerator"])
        multiplicity = multiplier * radius * (linear * radius + 1) ** 2
        safe_tail = Decimal(safe_square) * Decimal(str(fixture["c"])) ** 2 * Decimal(str(fixture["M20"])) * Decimal(radius) ** int(fixture["radius_power"]) / (Decimal(length) ** int(fixture["tail_power"]))
        exact_tail = Decimal(multiplicity) ** 2 * Decimal(str(fixture["c"])) ** 2 * Decimal(str(fixture["M20"])) / (Decimal(length) ** int(fixture["tail_power"]))
        check(f"R={radius} root", root**5 == radius, root, "fifth power", "cutoff")
        check(f"R={radius} multiplicity", multiplicity <= safe_m * radius**3, multiplicity, f"<={safe_m}R^3", "multiplicity")
        check(f"R={radius} tail", exact_tail <= safe_tail, exact_tail, f"<={safe_tail}", "tail")
        radius_rows.append({"R": radius, "L": length, "m_R": multiplicity, "exact_tail": str(exact_tail), "safe_tail": str(safe_tail)})

    factorial_rows: list[dict[str, Any]] = []
    for radius in [int(value) for value in fixture["R_values_exact_fifth_power"]]:
        root = exact_fifth_root(radius)
        r_four_fifths = root**int(fixture["factorial_radius_numerator"])
        exact_log = radius * math.log(float(r_four_fifths)) - math.lgamma(radius + 1)
        base = math.e * float(fixture["factorial_C"]) * radius ** (-1.0 / int(fixture["cutoff_exponent_denominator"]))
        majorant_log = radius * math.log(base)
        check(f"R={radius} factorial bound", exact_log <= majorant_log + 1.0e-10, exact_log, f"<={majorant_log}", "factorial")
        factorial_rows.append({"R": radius, "R_four_fifths": r_four_fifths, "exact_log": exact_log, "majorant_log": majorant_log, "base": base})

    check("safe square", safe_m * safe_m == safe_square, safe_m * safe_m, safe_square, "constants")
    check("large base", factorial_rows[-1]["base"] < 1.0, factorial_rows[-1]["base"], "<1", "factorial")
    check("tail decreases", Decimal(radius_rows[-1]["safe_tail"]) < Decimal(radius_rows[0]["safe_tail"]), radius_rows[-1]["safe_tail"], "below initial", "tail")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FIFTH-MOMENT-HARD-CUTOFF-CORRIDOR",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "multiplicity_rows": radius_rows,
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
    print(f"INDEPENDENT FIFTH-MOMENT-HARD-CUTOFF-CORRIDOR PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
