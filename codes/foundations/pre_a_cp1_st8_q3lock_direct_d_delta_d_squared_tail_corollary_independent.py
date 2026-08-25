#!/usr/bin/env python3
"""Independent Fraction lane for EXP-001113."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_direct_d_delta_d_squared_tail_corollary"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
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


def parse_fraction(value: Any) -> Fraction:
    text = str(value)
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(text)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001113" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001113/T-054", "provenance")
    check("scope firewall", scope["combined_squared_tail_limit_closed"] and not scope["dual_tail_input_proved"] and not scope["actual_q3_integrand_bound_proved"] and not scope["direct_d_delta_d_cauchy_closed"], scope, "conditional scalar bridge", "scope")

    k0 = Fraction(int(fixture["reference_tail_constant"]))
    k1 = Fraction(int(fixture["dual_tail_constant"]))
    a0 = parse_fraction(fixture["d_integrand_multiplier"])
    a1 = parse_fraction(fixture["delta_d_integrand_multiplier"])
    time = parse_fraction(fixture["time"])
    coefficient = time * time * (a0 * a0 * k0 + a1 * a1 * k1)
    check("coefficient", coefficient == Fraction(6318, 5), coefficient, Fraction(6318, 5), "Duhamel")

    rows: list[dict[str, Any]] = []
    for shell_root in [int(value) for value in fixture["shell_roots"]]:
        radius = shell_root**5
        cutoff_length = shell_root**2
        reference_tail = k0 / cutoff_length
        dual_tail = k1 / cutoff_length
        direct_squared = time * time * a0 * a0 * reference_tail
        delta_squared = time * time * a1 * a1 * dual_tail
        combined = direct_squared + delta_squared
        check(f"s={shell_root} shell", cutoff_length**5 == radius**2, [radius, cutoff_length], "L^5=R^2", "shell")
        check(f"s={shell_root} composition", combined == coefficient / cutoff_length, combined, coefficient / cutoff_length, "Duhamel")
        rows.append({"shell_root": shell_root, "R": radius, "L": cutoff_length, "reference_tail": str(reference_tail), "dual_tail": str(dual_tail), "direct_squared": str(direct_squared), "delta_squared": str(delta_squared), "combined_squared": str(combined)})
    check("decrease", Fraction(rows[-1]["combined_squared"]) < Fraction(rows[0]["combined_squared"]), rows[-1]["combined_squared"], "below initial", "limit")
    check("positive inputs", k0 > 0 and k1 > 0 and a0 > 0 and a1 > 0 and time > 0, [k0, k1, a0, a1, time], "positive", "inputs")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DIRECT-D-DELTA-D-SQUARED-TAIL-COROLLARY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions,
        "derived": {
            "coefficient": str(coefficient),
            "rows": rows,
            "shell_tail_to_squared_direct_d_corollary_closed": True,
            "shell_tail_to_squared_delta_d_corollary_closed": True,
            "combined_squared_tail_limit_closed": True,
            "reference_tail_input_reused": True,
            "dual_tail_input_proved": False,
            "actual_q3_integrand_bound_proved": False,
            "actual_unbounded_q3_common_core_closed": False,
            "direct_d_delta_d_cauchy_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False
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
    print(f"INDEPENDENT DIRECT-D-DELTA-D-SQUARED-TAIL PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
