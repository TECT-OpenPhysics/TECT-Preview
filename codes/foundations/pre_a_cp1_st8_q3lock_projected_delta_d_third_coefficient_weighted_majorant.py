#!/usr/bin/env python3
"""Primary symbolic audit for EXP-001074.

This file proves only a pointwise polynomial majorant for the exact finite CCR
third boundary coefficient recorded by EXP-001073.  It deliberately does not
construct a positive-time orbit estimate or a thermodynamic limit.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-weighted-majorant"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-boundary-coefficient-manifest.json"
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


def coefficient_majorant(expression: sp.Expr, q: sp.Symbol, v: sp.Symbol, a: sp.Symbol, source_bound: sp.Rational) -> tuple[sp.Rational, list[dict[str, Any]]]:
    polynomial = sp.Poly(sp.expand(expression), q, v, a)
    terms: list[dict[str, Any]] = []
    total = sp.Rational(0)
    for (q_degree, v_degree, source_degree), coefficient in polynomial.terms():
        if q_degree + v_degree > 3:
            raise AssertionError(f"field degree exceeds cubic rule: {(q_degree, v_degree, source_degree)}")
        if source_degree > 3:
            raise AssertionError(f"source degree exceeds cubic rule: {(q_degree, v_degree, source_degree)}")
        contribution = abs(sp.Rational(coefficient)) * source_bound**source_degree
        total += contribution
        terms.append(
            {
                "q_degree": q_degree,
                "v_degree": v_degree,
                "source_degree": source_degree,
                "coefficient": str(coefficient),
                "absolute_source_weight": str(contribution),
            }
        )
    return sp.factor(total), terms


def fourth_power_le(lhs: sp.Rational, rhs_constant: sp.Rational, weight: sp.Rational) -> bool:
    """Check lhs <= rhs_constant*weight^(3/4) without floating point arithmetic."""

    return lhs >= 0 and rhs_constant >= 0 and lhs**4 <= rhs_constant**4 * weight**3


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001074" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001074/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("previous authority", previous["exploration_id"] == "EXP-001073" and previous["scope"]["third_generator_difference_exact"] is True, previous["exploration_id"], "EXP-001073 third coefficient", "authority")
    check("model declarations", "D'''(0)" in manifest["model"]["boundary_coefficient"] and "F'" in manifest["model"]["A1"] and "F''" in manifest["model"]["A0"], manifest["model"], "A1/A0 coefficient model", "model")

    q, v, a = sp.symbols("q v a", real=True)
    imaginary = sp.I
    c = rational(fixture["c"])
    lam = rational(fixture["lambda"])
    chi = rational(fixture["chi"])
    hbar = rational(fixture["hbar"])
    source_bound = rational("1/4")
    bond = c * (q - v) ** 2 / 2 + lam * (q - v) ** 2 * (q**2 + v**2) / 4
    force = sp.diff(bond, q)
    force_first = sp.diff(force, q)
    force_second = sp.diff(force_first, q)
    a1 = sp.expand(-a * force_first / chi**2 - 3 * imaginary * a**2 * force / (chi**2 * hbar))
    a0 = sp.expand(-a * force_second / (2 * chi**2) - 2 * imaginary * a**2 * force_first / (chi**2 * hbar) + 3 * a**3 * force / (2 * chi**2 * hbar**2))
    components = {
        "A1_real": sp.expand(sp.re(a1)),
        "A1_imaginary": sp.expand(sp.im(a1)),
        "A0_real": sp.expand(sp.re(a0)),
        "A0_imaginary": sp.expand(sp.im(a0)),
    }

    majorants: dict[str, sp.Rational] = {}
    term_records: dict[str, list[dict[str, Any]]] = {}
    for label, expression in components.items():
        value, terms = coefficient_majorant(expression, q, v, a, source_bound)
        majorants[label] = value
        term_records[label] = terms
        check(f"majorant degree {label}", all(item["q_degree"] + item["v_degree"] <= 3 for item in terms), terms, "field degree <=3", "majorant")
        check(f"majorant {label}", value == rational(manifest["derived_majorants"][label]), value, manifest["derived_majorants"][label], "majorant")

    a1_sum = sp.factor(majorants["A1_real"] + majorants["A1_imaginary"])
    a0_sum = sp.factor(majorants["A0_real"] + majorants["A0_imaginary"])
    check("A1 sum", a1_sum == rational(manifest["derived_majorants"]["A1_sum"]), a1_sum, manifest["derived_majorants"]["A1_sum"], "majorant")
    check("A0 sum", a0_sum == rational(manifest["derived_majorants"]["A0_sum"]), a0_sum, manifest["derived_majorants"]["A0_sum"], "majorant")
    field_degrees = [max(sum(exponents[:2]) for exponents, _ in sp.Poly(expression, q, v, a).terms()) for expression in (force, a1, a0)]
    check("field degrees", field_degrees == [3, 3, 3], field_degrees, [3, 3, 3], "majorant")

    q_selected = rational(fixture["selected_q"])
    v_selected = rational(fixture["selected_v"])
    a_selected = rational(fixture["character_amplitude"])
    selected_substitution = {q: q_selected, v: v_selected, a: a_selected}
    selected_values = {label: sp.factor(expression.subs(selected_substitution)) for label, expression in components.items()}
    for label in components:
        manifest_key = f"derived_selected_{label}"
        check(f"selected {label}", selected_values[label] == rational(fixture[manifest_key]), selected_values[label], fixture[manifest_key], "fixture")
    selected_weight = 1 + q_selected**4 + v_selected**4
    check("selected weight", selected_weight == rational(fixture["derived_weight_at_selected"]), selected_weight, fixture["derived_weight_at_selected"], "fixture")

    field_grid = tuple(rational(value) for value in fixture["field_values"])
    source_grid = tuple(rational(value) for value in fixture["source_values"])
    grid_rows: list[dict[str, Any]] = []
    for q_value in field_grid:
        for v_value in field_grid:
            for a_value in source_grid:
                values = {q: q_value, v: v_value, a: a_value}
                row = {"q": q_value, "v": v_value, "a": a_value}
                for label, expression in components.items():
                    row[label] = sp.factor(expression.subs(values))
                row["weight"] = 1 + q_value**4 + v_value**4
                grid_rows.append(row)
    check("grid cardinality", len(grid_rows) == int(fixture["grid_points"]), len(grid_rows), fixture["grid_points"], "grid")
    ceilings = {label: max(abs(row[label]) for row in grid_rows) for label in components}
    for label in components:
        manifest_key = f"derived_abs_{label}_ceiling"
        check(f"grid ceiling {label}", ceilings[label] == rational(fixture[manifest_key]), ceilings[label], fixture[manifest_key], "grid")
        component_majorant = majorants[label]
        check(f"grid weighted bound {label}", all(fourth_power_le(abs(row[label]), component_majorant, row["weight"]) for row in grid_rows), component_majorant, "all grid rows", "grid")

    # One explicit derivative-weighted test uses the l1 complex norm, exactly
    # matching the triangle inequality used in the manifest.
    test_f = rational("2")
    test_fp = rational("-3")
    selected_a1_l1 = abs(selected_values["A1_real"] * test_fp + selected_values["A0_real"] * test_f) + abs(selected_values["A1_imaginary"] * test_fp + selected_values["A0_imaginary"] * test_f)
    weighted_rhs_constant = a1_sum * abs(test_fp) + a0_sum * abs(test_f)
    check("derivative weighted selected fixture", fourth_power_le(selected_a1_l1, weighted_rhs_constant, selected_weight), selected_a1_l1, "weighted pointwise upper bound", "derivative-weight")

    scope = manifest["scope"]
    closed_keys = ("coefficient_formula_reused", "all_real_polynomial_majorant_closed", "complex_component_bounds_closed", "derivative_weighted_pointwise_bound_closed", "finite_grid_crosscheck_closed")
    check("finite weighted closure", all(scope[key] is True for key in closed_keys), {key: scope[key] for key in closed_keys}, "finite weighted coefficient closed", "scope")
    open_keys = ("evolved_force_uniform_closed", "modular_domain_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_projected_d_duhamel_cauchy_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")

    derived = {
        "A1_real_majorant": majorants["A1_real"],
        "A1_imaginary_majorant": majorants["A1_imaginary"],
        "A0_real_majorant": majorants["A0_real"],
        "A0_imaginary_majorant": majorants["A0_imaginary"],
        "A1_sum": a1_sum,
        "A0_sum": a0_sum,
        "selected_A1_real": selected_values["A1_real"],
        "selected_A1_imaginary": selected_values["A1_imaginary"],
        "selected_A0_real": selected_values["A0_real"],
        "selected_A0_imaginary": selected_values["A0_imaginary"],
        "selected_weight": selected_weight,
        "grid_points": len(grid_rows),
        "grid_ceilings": ceilings,
        "field_degree_rule": 3,
        "source_radius": source_bound,
        "derivative_weighted_pointwise_bound_closed": True,
        "evolved_force_uniform_closed": False,
        "modular_domain_closed": False,
    }
    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-PROJECTED-DELTA-D-THIRD-COEFFICIENT-WEIGHTED-MAJORANT",
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "verdict": "PASS",
        "passed": passed,
        "assertion_count": passed,
        "assertions": rows,
        "derived": derived,
        "majorant_terms": term_records,
        "grid_rows": grid_rows,
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
    print(f"PRIMARY PROJECTED-DELTA-D-THIRD-WEIGHTED-MAJORANT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
