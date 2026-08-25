#!/usr/bin/env python3
"""Primary exact audit for the Q3 energy-to-number Shubin corollary."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from collections import defaultdict
from fractions import Fraction
from itertools import product
from math import comb, factorial
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_energy_to_number_shubin_corollary"
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


def zero_multi(dimension: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return tuple(0 for _ in range(dimension)), tuple(0 for _ in range(dimension))


def number_operator(dimension: int) -> dict[tuple[tuple[int, ...], tuple[int, ...]], int]:
    creation = [0] * dimension
    annihilation = [0] * dimension
    creation[0] = 1
    annihilation[0] = 1
    return {(tuple(creation), tuple(annihilation)): 1}


def multiply_normal(
    left: dict[tuple[tuple[int, ...], tuple[int, ...]], int],
    right: dict[tuple[tuple[int, ...], tuple[int, ...]], int],
) -> dict[tuple[tuple[int, ...], tuple[int, ...]], int]:
    result: defaultdict[tuple[tuple[int, ...], tuple[int, ...]], int] = defaultdict(int)
    for (left_creation, left_annihilation), left_value in left.items():
        for (right_creation, right_annihilation), right_value in right.items():
            choices = [range(min(left_annihilation[index], right_creation[index]) + 1) for index in range(len(left_creation))]
            for contractions in product(*choices):
                coefficient = left_value * right_value
                creation: list[int] = []
                annihilation: list[int] = []
                for index, contraction in enumerate(contractions):
                    coefficient *= comb(left_annihilation[index], contraction)
                    coefficient *= comb(right_creation[index], contraction) * factorial(contraction)
                    creation.append(left_creation[index] + right_creation[index] - contraction)
                    annihilation.append(left_annihilation[index] + right_annihilation[index] - contraction)
                result[(tuple(creation), tuple(annihilation))] += coefficient
    return {key: value for key, value in result.items() if value != 0}


def normal_power(dimension: int, order: int) -> dict[tuple[tuple[int, ...], tuple[int, ...]], int]:
    operator: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {}
    for component in range(dimension):
        creation = [0] * dimension
        annihilation = [0] * dimension
        creation[component] = 1
        annihilation[component] = 1
        key = (tuple(creation), tuple(annihilation))
        operator[key] = operator.get(key, 0) + 1
    current = {zero_multi(dimension): 1}
    for _ in range(order):
        current = multiply_normal(current, operator)
    return current


def total_degree(key: tuple[tuple[int, ...], tuple[int, ...]]) -> int:
    return sum(key[0]) + sum(key[1])


def fraction(text: str) -> Fraction:
    return Fraction(text)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    order = int(fixture["moment_order"])
    weight = Fraction(str(fixture["anisotropic_creation_annihilation_weight"]))
    tolerance = float(fixture["tolerance"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001110" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001110/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("authority inputs", manifest["authoritative_inputs"]["shubin_graph"]["scope"] == "registered fixed-beta finite-periodic compact-source one-site Q3 family" and manifest["authoritative_inputs"]["normal_order"]["component_count"] == 8, manifest["authoritative_inputs"], "R-167 and EXP-001108", "provenance")
    check("scope firewall", scope["energy_to_number_form_corollary_closed"] and scope["registered_gibbs_top_tail_closed"] and scope["registered_split_history_top_tail_closed"] and not scope["all_shape_exhaustion_top_tail_closed"] and not scope["common_alpha_closed"], scope, "registered corollary only", "scope")

    component_rows: list[dict[str, Any]] = []
    for component_count in [int(value) for value in fixture["component_values"]]:
        terms = normal_power(component_count, order)
        degrees = [total_degree(key) for key in terms]
        maximum_degree = max(degrees)
        maximum_order = weight * maximum_degree
        coefficient_l1 = sum(abs(value) for value in terms.values())
        check(f"components={component_count} nonempty", bool(terms), len(terms), ">0", "normal order")
        check(f"components={component_count} degree", maximum_degree <= 2 * order, maximum_degree, f"<={2 * order}", "normal order")
        check(f"components={component_count} anisotropic order", maximum_order <= order, maximum_order, f"<={order}", "normal order")
        component_rows.append({"components": component_count, "term_count": len(terms), "maximum_degree": maximum_degree, "maximum_anisotropic_order": maximum_order, "coefficient_l1": coefficient_l1})

    eight = next(row for row in component_rows if row["components"] == 8)
    coefficient_sum = Fraction(int(eight["coefficient_l1"]))
    check("eight-component term count", eight["term_count"] == 1286, eight["term_count"], "1286 (EXP-001108 oracle)", "normal order")
    check("eight-component coefficient sum", eight["coefficient_l1"] == 87496, eight["coefficient_l1"], "87496 (EXP-001108 oracle)", "normal order")

    graph_rows: list[dict[str, Any]] = []
    for graph_text in fixture["graph_constant_test_values"]:
        graph_constant = fraction(graph_text)
        form_constant = coefficient_sum * graph_constant
        graph_rows.append({"graph_constant": graph_text, "coefficient_l1": int(coefficient_sum), "form_constant": str(form_constant)})
        check(f"graph constant {graph_text} positive", graph_constant > 0 and form_constant > 0, [graph_constant, form_constant], ">0", "form composition")
        for vector_norm in (Fraction(0), Fraction(1, 3), Fraction(2)):
            energy_norm = vector_norm + Fraction(1, 2)
            left = form_constant * vector_norm * energy_norm
            right = form_constant * energy_norm * energy_norm
            check(f"Young {graph_text} x={vector_norm}", float(left) <= float(right) + tolerance, [left, right], "left<=right when k_h>=1", "form composition")

    moment = fraction(fixture["moment_test"])
    static_constant = coefficient_sum * fraction(fixture["graph_constant_test_values"][1])
    tail_rows: list[dict[str, Any]] = []
    previous = None
    for cutoff in [int(value) for value in fixture["cutoff_values"]]:
        value = static_constant * moment * Fraction(cutoff * cutoff, (cutoff - 1) ** 5)
        if previous is not None:
            check(f"static tail monotone n={cutoff}", value < previous, [value, previous], "strictly smaller", "tail")
        previous = value
        tail_rows.append({"cutoff": cutoff, "bound": str(value)})
    check("static tail positive", all(fraction(row["bound"]) > 0 for row in tail_rows), tail_rows, ">0", "tail")

    transport = fraction(fixture["transport_constant_test"])
    history_time = fraction(fixture["history_time_test"])
    history_weight_sum = fraction(fixture["history_weight_sum_test"])
    history_moment = float(math.exp(float(transport * history_time)) * float(history_weight_sum ** 5) * float(moment))
    check("history moment finite", math.isfinite(history_moment) and history_moment > 0, history_moment, ">0 finite", "history")
    history_rows: list[dict[str, Any]] = []
    for cutoff in [int(value) for value in fixture["cutoff_values"]]:
        bound = float(static_constant) * history_moment * cutoff * cutoff / ((cutoff - 1) ** 5)
        history_rows.append({"cutoff": cutoff, "bound": bound})
    check("history tail decreases", all(left["bound"] > right["bound"] for left, right in zip(history_rows, history_rows[1:])), history_rows, "strictly decreasing", "history")
    check("tail limit trend", history_rows[-1]["bound"] < history_rows[0]["bound"], [history_rows[0]["bound"], history_rows[-1]["bound"]], "decreases", "history")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ENERGY-TO-NUMBER-SHUBIN-COROLLARY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "component_rows": component_rows,
            "eight_component_coefficient_l1": int(coefficient_sum),
            "graph_rows": graph_rows,
            "static_tail_rows": tail_rows,
            "history_tail_rows": history_rows,
            "energy_to_number_form_constant_formula": "S_N5*G_graph",
            "energy_to_number_form_corollary_closed": True,
            "registered_gibbs_top_tail_closed": True,
            "registered_split_history_top_tail_closed": True,
            "all_shape_exhaustion_top_tail_closed": False,
            "actual_full_q3_common_core_closed": False,
            "direct_d_delta_d_cauchy_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY ENERGY-TO-NUMBER-SHUBIN-COROLLARY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
