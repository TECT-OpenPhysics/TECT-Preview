#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001076."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-scalar-energy-moment-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-weighted-seminorm-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "independent.json"


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


def frac(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def root_ceiling(m5: Fraction, numerator: int, denominator: int, grid_denominator: int) -> Fraction:
    k = 0
    while Fraction(k, grid_denominator) ** denominator < m5 ** numerator:
        k += 1
    return Fraction(k, grid_denominator)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001076" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001076/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("previous authority", previous["exploration_id"] == "EXP-001075" and previous["scope"]["conditional_two_orientation_seminorm_bridge_closed"] is True, previous["exploration_id"], "EXP-001075 conditional bridge", "authority")
    check("scalar surrogate declared", manifest["scalar_surrogate"]["energy_weight"] == "K=A+p^2", manifest["scalar_surrogate"], "K=A+p^2", "model")
    check("actual transfer firewall", "actual Q3 representation must prove" in manifest["candidate_bridge"]["actual_transfer_condition"], manifest["candidate_bridge"]["actual_transfer_condition"], "explicit successor condition", "scope")

    m5 = frac(fixture["m5"])
    a_max = frac(fixture["a_max"])
    grid_denominator = int(fixture["root_grid_denominator"])
    check("positive inputs", m5 > 0 and a_max >= 0 and grid_denominator > 0, [m5, a_max, grid_denominator], "positive", "inputs")

    r14 = root_ceiling(m5, 1, 4, grid_denominator)
    r320 = root_ceiling(m5, 3, 20, grid_denominator)
    r110 = root_ceiling(m5, 1, 10, grid_denominator)
    check("root m5^1/4", r14**4 >= m5 and (r14 - Fraction(1, grid_denominator))**4 < m5, r14, "minimal grid ceiling", "roots")
    check("root m5^3/20", r320**20 >= m5**3 and (r320 - Fraction(1, grid_denominator))**20 < m5**3, r320, "minimal grid ceiling", "roots")
    check("root m5^1/10", r110**10 >= m5 and (r110 - Fraction(1, grid_denominator))**10 < m5, r110, "minimal grid ceiling", "roots")
    check("root fixture m5^1/4", r14 == frac(fixture["derived_root_ceiling_m5_quarter"]), r14, fixture["derived_root_ceiling_m5_quarter"], "fixture")
    check("root fixture m5^3/20", r320 == frac(fixture["derived_root_ceiling_m5_three_twentieths"]), r320, fixture["derived_root_ceiling_m5_three_twentieths"], "fixture")
    check("root fixture m5^1/10", r110 == frac(fixture["derived_root_ceiling_m5_one_tenth"]), r110, fixture["derived_root_ceiling_m5_one_tenth"], "fixture")

    x_ceiling = r14 + a_max * r320
    p_ceiling = 2 * x_ceiling + Fraction(9, 2) * r110
    q_ceiling = Fraction(3, 2) * r320
    p_two = 2 * p_ceiling
    q_two = 2 * q_ceiling
    derived = {
        "m5": m5,
        "a_max": a_max,
        "root_m5_quarter": r14,
        "root_m5_three_twentieths": r320,
        "root_m5_one_tenth": r110,
        "X_ceiling": x_ceiling,
        "P_sigma_ceiling": p_ceiling,
        "Q_sigma_ceiling": q_ceiling,
        "two_orientation_P_ceiling": p_two,
        "two_orientation_Q_ceiling": q_two,
    }
    for key, value in (("X_ceiling", x_ceiling), ("P_sigma_ceiling", p_ceiling), ("Q_sigma_ceiling", q_ceiling), ("two_orientation_P_ceiling", p_two), ("two_orientation_Q_ceiling", q_two)):
        check(f"derived {key}", value == frac(fixture[f"derived_{key}"]), value, fixture[f"derived_{key}"], "bridge")

    sample_rows = 0
    for q in range(-2, 3):
        for v in range(-2, 3):
            for p in range(-2, 3):
                A = 1 + q**4 + v**4
                K = A + p**2
                check(f"order sample {q},{v},{p}", A <= K and p**2 <= K and A**3 * p**4 <= K**5 and A**3 <= K**3 and q**12 <= A**3, True, True, "scalar-order")
                sample_rows += 1
    check("sample count", sample_rows == 125, sample_rows, 125, "scalar-order")
    check("root ceiling sqrt2", Fraction(3, 2) ** 2 >= 2, Fraction(3, 2), "sqrt(2)<=3/2", "ceilings")

    scope = manifest["scope"]
    closed_keys = ("scalar_commuting_energy_bridge_closed", "scalar_derivative_commutator_bound_closed", "candidate_P_Q_formula_closed")
    check("candidate closure", all(scope[key] is True for key in closed_keys), {key: scope[key] for key in closed_keys}, "candidate closed", "scope")
    open_keys = ("actual_q3_mixed_moment_bound_closed", "actual_q3_multiplication_domination_closed", "noncommutative_quadratic_form_transfer_closed", "modular_companion_bound_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_projected_d_duhamel_cauchy_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")

    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-PROJECTED-DELTA-D-THIRD-COEFFICIENT-SCALAR-ENERGY-MOMENT-BRIDGE",
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "verdict": "PASS",
        "passed": passed,
        "assertion_count": passed,
        "assertions": rows,
        "derived": derived,
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.output:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT PROJECTED-DELTA-D-THIRD-SCALAR-ENERGY-MOMENT-BRIDGE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
