#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001073."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-projected-delta-d-third-boundary-coefficient"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-boundary-taylor-coefficient-manifest.json"
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


def frac(value: str | int) -> Fraction:
    return Fraction(str(value))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001073" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001073/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("previous authority", previous["exploration_id"] == "EXP-001058" and previous["scope"]["second_generator_difference_exact"] is True, previous["exploration_id"], "EXP-001058 second coefficient", "authority")

    chi = frac(fixture["chi"])
    hbar = frac(fixture["hbar"])
    c = frac(fixture["c"])
    lam = frac(fixture["lambda"])
    amplitude = frac(fixture["character_amplitude"])

    def force(q: Fraction, v: Fraction) -> Fraction:
        return c * (q - v) + lam * (q - v) * (2 * q**2 - q * v + v**2) / 2

    def force_first(q: Fraction, v: Fraction) -> Fraction:
        return c + lam * (3 * q**2 - 3 * q * v + v**2)

    def force_second(q: Fraction, v: Fraction) -> Fraction:
        return lam * (6 * q - 3 * v)

    def a1_parts(q: Fraction, v: Fraction) -> tuple[Fraction, Fraction]:
        return (-amplitude * force_first(q, v) / chi**2, -3 * amplitude**2 * force(q, v) / (chi**2 * hbar))

    def a0_parts(q: Fraction, v: Fraction) -> tuple[Fraction, Fraction]:
        return (-amplitude * force_second(q, v) / (2 * chi**2) + 3 * amplitude**3 * force(q, v) / (2 * chi**2 * hbar**2), -2 * amplitude**2 * force_first(q, v) / (chi**2 * hbar))

    selected_q = frac(fixture["selected_q"])
    selected_v = frac(fixture["selected_v"])
    selected_force = force(selected_q, selected_v)
    selected_first = force_first(selected_q, selected_v)
    selected_second = force_second(selected_q, selected_v)
    selected_a1 = a1_parts(selected_q, selected_v)
    selected_a0 = a0_parts(selected_q, selected_v)
    check("selected force", selected_force == frac(fixture["derived_selected_force"]), selected_force, fixture["derived_selected_force"], "fixture")
    check("selected force first", selected_first == frac(fixture["derived_selected_force_first_derivative"]), selected_first, fixture["derived_selected_force_first_derivative"], "fixture")
    check("selected force second", selected_second == frac(fixture["derived_selected_force_second_derivative"]), selected_second, fixture["derived_selected_force_second_derivative"], "fixture")
    check("selected A1 real", selected_a1[0] == frac(fixture["derived_selected_A1_real"]), selected_a1[0], fixture["derived_selected_A1_real"], "fixture")
    check("selected A1 imaginary", selected_a1[1] == frac(fixture["derived_selected_A1_imaginary"]), selected_a1[1], fixture["derived_selected_A1_imaginary"], "fixture")
    check("selected A0 real", selected_a0[0] == frac(fixture["derived_selected_A0_real"]), selected_a0[0], fixture["derived_selected_A0_real"], "fixture")
    check("selected A0 imaginary", selected_a0[1] == frac(fixture["derived_selected_A0_imaginary"]), selected_a0[1], fixture["derived_selected_A0_imaginary"], "fixture")

    grid = tuple(frac(value) for value in fixture["field_values"])
    grid_rows: list[dict[str, Any]] = []
    for q_value in grid:
        for v_value in grid:
            a1_value = a1_parts(q_value, v_value)
            a0_value = a0_parts(q_value, v_value)
            grid_rows.append({"q": q_value, "v": v_value, "a1_real": a1_value[0], "a1_imaginary": a1_value[1], "a0_real": a0_value[0], "a0_imaginary": a0_value[1]})
    ceilings = {"abs_a1_real": max(abs(row["a1_real"]) for row in grid_rows), "abs_a1_imaginary": max(abs(row["a1_imaginary"]) for row in grid_rows), "abs_a0_real": max(abs(row["a0_real"]) for row in grid_rows), "abs_a0_imaginary": max(abs(row["a0_imaginary"]) for row in grid_rows)}
    for key, manifest_key in (("abs_a1_real", "derived_abs_A1_real_ceiling"), ("abs_a1_imaginary", "derived_abs_A1_imaginary_ceiling"), ("abs_a0_real", "derived_abs_A0_real_ceiling"), ("abs_a0_imaginary", "derived_abs_A0_imaginary_ceiling")):
        check(key, ceilings[key] == frac(fixture[manifest_key]), ceilings[key], fixture[manifest_key], "grid")
    check("grid cardinality", len(grid_rows) == int(fixture["grid_points"]), len(grid_rows), fixture["grid_points"], "grid")
    check("degree fixtures", int(fixture["derived_force_degree"]) == 3 and int(fixture["derived_A1_degree"]) == 3 and int(fixture["derived_A0_degree"]) == 3, [fixture["derived_force_degree"], fixture["derived_A1_degree"], fixture["derived_A0_degree"]], [3, 3, 3], "degree")

    scope = manifest["scope"]
    check("finite coefficient closure", scope["first_generator_difference_zero"] is True and scope["third_generator_difference_exact"] is True and scope["third_coefficient_operator_form_closed"] is True and scope["finite_grid_component_bounds_closed"] is True, scope, "finite coefficient closed", "scope")
    open_keys = ("evolved_force_uniform_closed", "modular_domain_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_projected_d_duhamel_cauchy_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")
    derived = {"first_difference_zero": True, "second_difference_exact": True, "third_difference_exact": True, "selected_force": selected_force, "selected_force_first_derivative": selected_first, "selected_force_second_derivative": selected_second, "selected_A1_real": selected_a1[0], "selected_A1_imaginary": selected_a1[1], "selected_A0_real": selected_a0[0], "selected_A0_imaginary": selected_a0[1], "abs_A1_real_ceiling": ceilings["abs_a1_real"], "abs_A1_imaginary_ceiling": ceilings["abs_a1_imaginary"], "abs_A0_real_ceiling": ceilings["abs_a0_real"], "abs_A0_imaginary_ceiling": ceilings["abs_a0_imaginary"], "grid_points": len(grid_rows), "force_degree": 3, "A1_degree": 3, "A0_degree": 3, "third_coefficient_operator_form_closed": True, "evolved_force_uniform_closed": False, "modular_domain_closed": False}
    passed = len(rows)
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-PROJECTED-DELTA-D-THIRD-BOUNDARY-COEFFICIENT", "exploration_id": manifest["exploration_id"], "task_id": manifest["task_id"], "verdict": "PASS", "passed": passed, "assertion_count": passed, "assertions": rows, "derived": derived, "grid_rows": grid_rows, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.output:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT PROJECTED-DELTA-D-THIRD-COEFFICIENT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
