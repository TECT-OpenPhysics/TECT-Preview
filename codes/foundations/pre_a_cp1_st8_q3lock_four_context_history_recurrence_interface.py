#!/usr/bin/env python3
"""Primary exact audit for EXP-001154.

The package counts the four finite-member contexts (W/W* and both real-time
signs) from EXP-001153 and then evaluates, conditionally, the weighted
recurrence coefficient from EXP-001151.  The recurrence and response bounds
remain hypotheses; this file closes only their exact arithmetic consequence.
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
SLUG = "pre_a_cp1_st8_q3lock_four_context_history_recurrence_interface"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-four-context-history-recurrence-interface-manifest.json"
SEED = REPO / "strategy/pre-a-cp1-st8-q3lock-full-character-two-sided-duhamel-history-bound-manifest.json"
RECURRENCE = REPO / "strategy/pre-a-cp1-st8-q3lock-inductive-cylinder-recurrence-cauchy-interface-manifest.json"
CYLINDER = REPO / "strategy/pre-a-cp1-st8-q3lock-inductive-cylinder-form-contract-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"


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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    recurrence = json.loads(RECURRENCE.read_text(encoding="utf-8"))
    cylinder = json.loads(CYLINDER.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    oracle = manifest["derived_oracles"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001154" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001154/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("history seed", seed["exploration_id"] == "EXP-001153" and seed["scope"]["finite_member_two_orientation_difference_closed"] is True, seed["exploration_id"], "EXP-001153 finite seed", "upstream")
    check("recurrence parent", recurrence["exploration_id"] == "EXP-001151" and recurrence["scope"]["conditional_weighted_recurrence_arithmetic_closed"] is True, recurrence["exploration_id"], "EXP-001151 conditional recurrence", "upstream")
    check("cylinder parent", cylinder["exploration_id"] == "EXP-001150" and cylinder["scope"]["inductive_limit_test_algebra_contract_closed"] is True, cylinder["exploration_id"], "EXP-001150 bounded cylinder", "upstream")

    one_context = Fraction(fixture["one_context_squared_bound"])
    context_count = int(fixture["context_count"])
    pair_count = int(fixture["orientation_pair_count"])
    time_horizon = Fraction(fixture["time_horizon"])
    check("finite context parameters", context_count == 4 and pair_count == 2 and time_horizon > 0, fixture, "four finite contexts", "hypotheses")
    check("seed oracle", one_context == Fraction(seed["derived_oracles"]["one_orientation_remainder_squared_bound"]), one_context, seed["derived_oracles"]["one_orientation_remainder_squared_bound"], "upstream")

    amplitudes = [Fraction(value) for value in seed["finite_fixture"]["amplitudes"]]
    even_original = sum(value**4 for value in amplitudes)
    even_adjoint = sum((-value)**4 for value in amplitudes)
    l1_original = sum(abs(value) for value in amplitudes)
    l1_adjoint = sum(abs(-value) for value in amplitudes)
    check("adjoint even-power invariance", even_original == even_adjoint, [even_original, even_adjoint], "equal", "adjoint")
    check("adjoint l1 invariance", l1_original == l1_adjoint, [l1_original, l1_adjoint], "equal", "adjoint")
    adjoint_one = one_context
    pair_squared = 4 * one_context
    four_sum = context_count * one_context
    check("adjoint context bound", adjoint_one == Fraction(oracle["adjoint_one_context_squared_bound"]), adjoint_one, oracle["adjoint_one_context_squared_bound"], "four contexts")
    check("orientation pair bound", pair_squared == Fraction(oracle["orientation_pair_squared_bound"]), pair_squared, oracle["orientation_pair_squared_bound"], "four contexts")
    check("four context sum", four_sum == Fraction(oracle["four_context_squared_sum"]), four_sum, oracle["four_context_squared_sum"], "four contexts")

    recurrence_fixture = recurrence["finite_fixture"]
    recurrence_c = Fraction(recurrence_fixture["recurrence_C"])
    recurrence_j = Fraction(recurrence_fixture["recurrence_J"])
    degree = int(recurrence_fixture["degree"])
    base = Fraction(recurrence_fixture["base_weight"])
    delta = Fraction(recurrence_fixture["time_step"])
    steps = int(recurrence_fixture["steps"])
    distance = int(recurrence_fixture["boundary_distance"])
    source_mass = Fraction(recurrence_fixture["source_mass"])
    weighted_step = 1 + (recurrence_c + recurrence_j * degree * base) * delta
    response = weighted_step**steps * base**(-distance) * source_mass
    conditional_cauchy = Fraction(context_count) * time_horizon * response
    check("weighted step", weighted_step == Fraction(oracle["weighted_step_factor"]), weighted_step, oracle["weighted_step_factor"], "conditional recurrence")
    check("conditional response", response == Fraction(oracle["conditional_response_envelope"]), response, oracle["conditional_response_envelope"], "conditional recurrence")
    check("conditional four-context coefficient", conditional_cauchy == Fraction(oracle["conditional_four_context_cauchy_coefficient"]), conditional_cauchy, oracle["conditional_four_context_cauchy_coefficient"], "conditional recurrence")

    factor_one = cylinder["finite_fixture"]["factor_one"]
    factor_two = cylinder["finite_fixture"]["factor_two"]
    chi = Fraction(cylinder["finite_fixture"]["chi"])
    sup = Fraction(factor_one["sup_bound"]) * Fraction(factor_two["sup_bound"])
    gradient = Fraction(factor_one["sup_bound"]) * Fraction(factor_two["gradient_bound"]) + Fraction(factor_two["sup_bound"]) * Fraction(factor_one["gradient_bound"])
    same_form = 2 * sup**2 + gradient**2 / chi
    form_multiplier = Fraction(cylinder["finite_fixture"]["form_order_multiplier"])
    cross_form = form_multiplier * same_form
    check("product same form", same_form == Fraction(oracle["product_same_form_cost"]), same_form, oracle["product_same_form_cost"], "product interface")
    check("product cross form", cross_form == Fraction(oracle["product_cross_form_cost"]), cross_form, oracle["product_cross_form_cost"], "product interface")

    closed = ("finite_member_four_context_remainder_accounting_closed", "adjoint_context_static_invariance_closed", "orientation_pair_triangle_accounting_closed", "conditional_weighted_recurrence_arithmetic_closed", "conditional_four_context_cauchy_coefficient_closed", "product_cost_recorded")
    check("scope closed", all(scope[key] is True for key in closed), {key: scope[key] for key in closed}, True, "scope")
    open_keys = ("actual_q3_recurrence_closed", "actual_first_commutator_decay_closed", "actual_second_commutator_decay_closed", "modular_derivative_closed", "actual_q3_factorial_history_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "unbounded_product_core_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed", "all_shape_uniformity_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "actual recurrence and downstream gates remain open", "boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FOUR-CONTEXT-HISTORY-RECURRENCE-INTERFACE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "one_context_squared_bound": str(one_context),
            "adjoint_one_context_squared_bound": str(adjoint_one),
            "orientation_pair_squared_bound": str(pair_squared),
            "four_context_squared_sum": str(four_sum),
            "weighted_step_factor": str(weighted_step),
            "conditional_response_envelope": str(response),
            "conditional_four_context_cauchy_coefficient": str(conditional_cauchy),
            "product_same_form_cost": str(same_form),
            "product_cross_form_cost": str(cross_form),
            "finite_member_four_context_remainder_accounting_closed": True,
            "adjoint_context_static_invariance_closed": True,
            "orientation_pair_triangle_accounting_closed": True,
            "conditional_weighted_recurrence_arithmetic_closed": True,
            "conditional_four_context_cauchy_coefficient_closed": True,
            "product_cost_recorded": True,
            "actual_q3_recurrence_closed": False,
            "actual_first_commutator_decay_closed": False,
            "actual_second_commutator_decay_closed": False,
            "modular_derivative_closed": False,
            "actual_q3_factorial_history_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "unbounded_product_core_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
            "all_shape_uniformity_closed": False
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
    print(f"PRIMARY FOUR-CONTEXT-HISTORY-RECURRENCE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
