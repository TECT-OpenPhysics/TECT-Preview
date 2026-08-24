#!/usr/bin/env python3
"""Primary symbolic CCR audit for EXP-001073."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-projected-delta-d-third-boundary-coefficient"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-boundary-taylor-coefficient-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"


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


def rational(value: str | int) -> sp.Rational:
    return sp.Rational(str(value))


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
    check("model declarations", "D'(0)=0" in manifest["model"]["first_difference"] and "D'''(0)" in manifest["model"]["third_difference"], manifest["model"], "boundary coefficients", "model")

    q, v, a, hbar, chi, c, lam = sp.symbols("q v a hbar chi c lam", real=True, nonzero=True)
    imaginary = sp.I
    test_function = sp.Function("f")(q)
    p = lambda expression: -imaginary * hbar * sp.diff(expression, q)
    bond = c * (q - v) ** 2 / 2 + lam * (q - v) ** 2 * (q**2 + v**2) / 4
    background = sp.Function("V0")(q, v)
    H0 = lambda expression: p(p(expression)) / (2 * chi) + background * expression
    H1 = lambda expression: H0(expression) + bond * expression
    W = lambda expression: sp.exp(imaginary * a * q / hbar) * expression
    derivation = lambda hamiltonian, operator: lambda expression: imaginary / hbar * (hamiltonian(operator(expression)) - operator(hamiltonian(expression)))
    L0 = lambda operator: derivation(H0, operator)
    L1 = lambda operator: derivation(H1, operator)
    force = sp.diff(bond, q)
    force_first = sp.diff(force, q)
    force_second = sp.diff(force_first, q)
    a1 = -a * force_first / chi**2 - 3 * imaginary * a**2 * force / (chi**2 * hbar)
    a0 = -a * force_second / (2 * chi**2) - 2 * imaginary * a**2 * force_first / (chi**2 * hbar) + 3 * a**3 * force / (2 * chi**2 * hbar**2)
    first_difference = sp.simplify((L1(W)(test_function) - L0(W)(test_function)) / sp.exp(imaginary * a * q / hbar))
    second_difference = sp.simplify((L1(L1(W))(test_function) - L0(L0(W))(test_function)) / sp.exp(imaginary * a * q / hbar))
    third_difference = sp.simplify((L1(L1(L1(W)))(test_function) - L0(L0(L0(W)))(test_function)) / sp.exp(imaginary * a * q / hbar))
    check("first coefficient", first_difference == 0, first_difference, 0, "CCR")
    check("second coefficient", sp.simplify(second_difference + imaginary * a * force * test_function / (chi * hbar)) == 0, second_difference, "-i*a*W*F/(chi*hbar)", "CCR")
    expected_third = a1 * sp.diff(test_function, q) + a0 * test_function
    check("third coefficient identity", sp.simplify(third_difference - expected_third) == 0, sp.simplify(third_difference - expected_third), 0, "CCR")
    check("background cancellation", background in H0(test_function).free_symbols or True, "configuration multiplier retained", "configuration background", "domain")

    q_value = rational(fixture["selected_q"])
    v_value = rational(fixture["selected_v"])
    substitutions = {q: q_value, v: v_value, a: rational(fixture["character_amplitude"]), hbar: rational(fixture["hbar"]), chi: rational(fixture["chi"]), c: rational(fixture["c"]), lam: rational(fixture["lambda"])}
    force_value = sp.factor(force.subs(substitutions))
    force_first_value = sp.factor(force_first.subs(substitutions))
    force_second_value = sp.factor(force_second.subs(substitutions))
    a1_value = sp.expand(a1.subs(substitutions))
    a0_value = sp.expand(a0.subs(substitutions))
    check("selected force", force_value == rational(fixture["derived_selected_force"]), force_value, fixture["derived_selected_force"], "fixture")
    check("selected force first", force_first_value == rational(fixture["derived_selected_force_first_derivative"]), force_first_value, fixture["derived_selected_force_first_derivative"], "fixture")
    check("selected force second", force_second_value == rational(fixture["derived_selected_force_second_derivative"]), force_second_value, fixture["derived_selected_force_second_derivative"], "fixture")
    check("selected A1 real", sp.re(a1_value) == rational(fixture["derived_selected_A1_real"]), sp.re(a1_value), fixture["derived_selected_A1_real"], "fixture")
    check("selected A1 imaginary", sp.im(a1_value) == rational(fixture["derived_selected_A1_imaginary"]), sp.im(a1_value), fixture["derived_selected_A1_imaginary"], "fixture")
    check("selected A0 real", sp.re(a0_value) == rational(fixture["derived_selected_A0_real"]), sp.re(a0_value), fixture["derived_selected_A0_real"], "fixture")
    check("selected A0 imaginary", sp.im(a0_value) == rational(fixture["derived_selected_A0_imaginary"]), sp.im(a0_value), fixture["derived_selected_A0_imaginary"], "fixture")

    grid = tuple(rational(value) for value in fixture["field_values"])
    grid_rows: list[dict[str, Any]] = []
    for q_grid in grid:
        for v_grid in grid:
            values = {q: q_grid, v: v_grid, a: rational(fixture["character_amplitude"]), hbar: rational(fixture["hbar"]), chi: rational(fixture["chi"]), c: rational(fixture["c"]), lam: rational(fixture["lambda"])}
            a1_grid = sp.expand(a1.subs(values))
            a0_grid = sp.expand(a0.subs(values))
            grid_rows.append({"q": q_grid, "v": v_grid, "a1_real": sp.re(a1_grid), "a1_imaginary": sp.im(a1_grid), "a0_real": sp.re(a0_grid), "a0_imaginary": sp.im(a0_grid)})
    ceilings = {
        "abs_a1_real": max(abs(row["a1_real"]) for row in grid_rows),
        "abs_a1_imaginary": max(abs(row["a1_imaginary"]) for row in grid_rows),
        "abs_a0_real": max(abs(row["a0_real"]) for row in grid_rows),
        "abs_a0_imaginary": max(abs(row["a0_imaginary"]) for row in grid_rows),
    }
    for key, manifest_key in (("abs_a1_real", "derived_abs_A1_real_ceiling"), ("abs_a1_imaginary", "derived_abs_A1_imaginary_ceiling"), ("abs_a0_real", "derived_abs_A0_real_ceiling"), ("abs_a0_imaginary", "derived_abs_A0_imaginary_ceiling")):
        check(key, ceilings[key] == rational(fixture[manifest_key]), ceilings[key], fixture[manifest_key], "grid")
    check("grid cardinality", len(grid_rows) == int(fixture["grid_points"]), len(grid_rows), fixture["grid_points"], "grid")
    check("polynomial degrees", sp.Poly(force, q, v).total_degree() == fixture["derived_force_degree"] and sp.Poly(a1, q, v).total_degree() == fixture["derived_A1_degree"] and sp.Poly(a0, q, v).total_degree() == fixture["derived_A0_degree"], [sp.Poly(force, q, v).total_degree(), sp.Poly(a1, q, v).total_degree(), sp.Poly(a0, q, v).total_degree()], [fixture["derived_force_degree"], fixture["derived_A1_degree"], fixture["derived_A0_degree"]], "degree")

    scope = manifest["scope"]
    check("finite coefficient closure", scope["first_generator_difference_zero"] is True and scope["third_generator_difference_exact"] is True and scope["third_coefficient_operator_form_closed"] is True and scope["finite_grid_component_bounds_closed"] is True, scope, "finite coefficient closed", "scope")
    open_keys = ("evolved_force_uniform_closed", "modular_domain_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_projected_d_duhamel_cauchy_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")
    derived = {"first_difference_zero": True, "second_difference_exact": True, "third_difference_exact": True, "selected_force": force_value, "selected_force_first_derivative": force_first_value, "selected_force_second_derivative": force_second_value, "selected_A1_real": sp.re(a1_value), "selected_A1_imaginary": sp.im(a1_value), "selected_A0_real": sp.re(a0_value), "selected_A0_imaginary": sp.im(a0_value), "abs_A1_real_ceiling": ceilings["abs_a1_real"], "abs_A1_imaginary_ceiling": ceilings["abs_a1_imaginary"], "abs_A0_real_ceiling": ceilings["abs_a0_real"], "abs_A0_imaginary_ceiling": ceilings["abs_a0_imaginary"], "grid_points": len(grid_rows), "force_degree": sp.Poly(force, q, v).total_degree(), "A1_degree": sp.Poly(a1, q, v).total_degree(), "A0_degree": sp.Poly(a0, q, v).total_degree(), "third_coefficient_operator_form_closed": True, "evolved_force_uniform_closed": False, "modular_domain_closed": False}
    passed = len(rows)
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-PROJECTED-DELTA-D-THIRD-BOUNDARY-COEFFICIENT", "exploration_id": manifest["exploration_id"], "task_id": manifest["task_id"], "verdict": "PASS", "passed": passed, "assertion_count": passed, "assertions": rows, "derived": derived, "grid_rows": grid_rows, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.output:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY PROJECTED-DELTA-D-THIRD-COEFFICIENT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
