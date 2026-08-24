#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001074.

The polynomial dictionary and rational arithmetic are independent of SymPy.
The output remains a finite pointwise coefficient check, not an operator-limit
theorem.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-weighted-majorant"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-boundary-coefficient-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "independent.json"

Poly2 = dict[tuple[int, int], Fraction]
Poly3 = dict[tuple[int, int, int], Fraction]


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


def add2(left: Poly2, right: Poly2) -> Poly2:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, Fraction(0)) + value
    return {key: value for key, value in result.items() if value}


def scale2(poly: Poly2, factor: Fraction) -> Poly2:
    return {key: value * factor for key, value in poly.items() if value * factor}


def mul2(left: Poly2, right: Poly2) -> Poly2:
    result: Poly2 = {}
    for (iq, iv), left_value in left.items():
        for (jq, jv), right_value in right.items():
            key = (iq + jq, iv + jv)
            result[key] = result.get(key, Fraction(0)) + left_value * right_value
    return {key: value for key, value in result.items() if value}


def deriv_q(poly: Poly2) -> Poly2:
    return {(iq - 1, iv): coefficient * iq for (iq, iv), coefficient in poly.items() if iq}


def eval2(poly: Poly2, q: Fraction, v: Fraction) -> Fraction:
    return sum(coefficient * q**iq * v**iv for (iq, iv), coefficient in poly.items())


def add3(left: Poly3, right: Poly3) -> Poly3:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, Fraction(0)) + value
    return {key: value for key, value in result.items() if value}


def scale3(poly: Poly3, factor: Fraction) -> Poly3:
    return {key: value * factor for key, value in poly.items() if value * factor}


def lift(poly: Poly2, source_degree: int, factor: Fraction) -> Poly3:
    return {(iq, iv, source_degree): coefficient * factor for (iq, iv), coefficient in poly.items() if coefficient * factor}


def eval3(poly: Poly3, q: Fraction, v: Fraction, a: Fraction) -> Fraction:
    return sum(coefficient * q**iq * v**iv * a**ia for (iq, iv, ia), coefficient in poly.items())


def coefficient_majorant(poly: Poly3, source_bound: Fraction) -> tuple[Fraction, list[dict[str, Any]]]:
    total = Fraction(0)
    terms: list[dict[str, Any]] = []
    for (iq, iv, ia), coefficient in sorted(poly.items()):
        if iq + iv > 3 or ia > 3:
            raise AssertionError(f"degree rule failed: {(iq, iv, ia)}")
        contribution = abs(coefficient) * source_bound**ia
        total += contribution
        terms.append({"q_degree": iq, "v_degree": iv, "source_degree": ia, "coefficient": str(coefficient), "absolute_source_weight": str(contribution)})
    return total, terms


def fourth_power_le(lhs: Fraction, rhs_constant: Fraction, weight: Fraction) -> bool:
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

    c = frac(fixture["c"])
    lam = frac(fixture["lambda"])
    field_grid = tuple(frac(value) for value in fixture["field_values"])
    source_grid = tuple(frac(value) for value in fixture["source_values"])
    source_bound = max(abs(value) for value in source_grid)
    qm = {(1, 0): Fraction(1), (0, 1): Fraction(-1)}
    q2v2 = {(2, 0): Fraction(1), (0, 2): Fraction(1)}
    bond = add2(scale2(mul2(qm, qm), c / 2), scale2(mul2(mul2(qm, qm), q2v2), lam / 4))
    force = deriv_q(bond)
    force_first = deriv_q(force)
    force_second = deriv_q(force_first)

    components: dict[str, Poly3] = {
        "A1_real": lift(force_first, 1, Fraction(-1)),
        "A1_imaginary": lift(force, 2, Fraction(-3)),
        "A0_real": add3(lift(force_second, 1, Fraction(-1, 2)), lift(force, 3, Fraction(3, 2))),
        "A0_imaginary": lift(force_first, 2, Fraction(-2)),
    }
    majorants: dict[str, Fraction] = {}
    term_records: dict[str, list[dict[str, Any]]] = {}
    expected_majorant_keys = ("A1_real", "A1_imaginary", "A0_real", "A0_imaginary")
    for label in expected_majorant_keys:
        value, terms = coefficient_majorant(components[label], source_bound)
        majorants[label] = value
        term_records[label] = terms
        check(f"majorant {label}", value == frac(manifest["derived_majorants"][label]), value, manifest["derived_majorants"][label], "majorant")
        check(f"degree rule {label}", all(item["q_degree"] + item["v_degree"] <= 3 for item in terms), terms, "field degree <=3", "majorant")

    a1_sum = majorants["A1_real"] + majorants["A1_imaginary"]
    a0_sum = majorants["A0_real"] + majorants["A0_imaginary"]
    check("A1 sum", a1_sum == frac(manifest["derived_majorants"]["A1_sum"]), a1_sum, manifest["derived_majorants"]["A1_sum"], "majorant")
    check("A0 sum", a0_sum == frac(manifest["derived_majorants"]["A0_sum"]), a0_sum, manifest["derived_majorants"]["A0_sum"], "majorant")
    check("force degree", max(iq + iv for iq, iv in force) == 3, max(iq + iv for iq, iv in force), 3, "majorant")

    q_selected = frac(fixture["selected_q"])
    v_selected = frac(fixture["selected_v"])
    a_selected = frac(fixture["character_amplitude"])
    selected_values = {label: eval3(poly, q_selected, v_selected, a_selected) for label, poly in components.items()}
    for label in components:
        manifest_key = f"derived_selected_{label}"
        check(f"selected {label}", selected_values[label] == frac(fixture[manifest_key]), selected_values[label], fixture[manifest_key], "fixture")
    selected_weight = 1 + q_selected**4 + v_selected**4
    check("selected weight", selected_weight == frac(fixture["derived_weight_at_selected"]), selected_weight, fixture["derived_weight_at_selected"], "fixture")

    grid_rows: list[dict[str, Any]] = []
    for q_value in field_grid:
        for v_value in field_grid:
            for a_value in source_grid:
                row = {"q": q_value, "v": v_value, "a": a_value, "weight": 1 + q_value**4 + v_value**4}
                for label, poly in components.items():
                    row[label] = eval3(poly, q_value, v_value, a_value)
                grid_rows.append(row)
    check("grid cardinality", len(grid_rows) == int(fixture["grid_points"]), len(grid_rows), fixture["grid_points"], "grid")
    ceilings = {label: max(abs(row[label]) for row in grid_rows) for label in components}
    for label in components:
        manifest_key = f"derived_abs_{label}_ceiling"
        check(f"grid ceiling {label}", ceilings[label] == frac(fixture[manifest_key]), ceilings[label], fixture[manifest_key], "grid")
        check(f"grid weighted bound {label}", all(fourth_power_le(abs(row[label]), majorants[label], row["weight"]) for row in grid_rows), majorants[label], "all grid rows", "grid")

    test_f = frac(2)
    test_fp = frac(-3)
    selected_l1 = abs(selected_values["A1_real"] * test_fp + selected_values["A0_real"] * test_f) + abs(selected_values["A1_imaginary"] * test_fp + selected_values["A0_imaginary"] * test_f)
    weighted_rhs_constant = a1_sum * abs(test_fp) + a0_sum * abs(test_f)
    check("derivative weighted selected fixture", fourth_power_le(selected_l1, weighted_rhs_constant, selected_weight), selected_l1, "weighted pointwise upper bound", "derivative-weight")

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
        "run_kind": "independent",
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
    print(f"INDEPENDENT PROJECTED-DELTA-D-THIRD-WEIGHTED-MAJORANT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
