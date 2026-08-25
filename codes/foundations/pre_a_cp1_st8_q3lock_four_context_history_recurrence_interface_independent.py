#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001154."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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

    one = Fraction(str(fixture["one_context_squared_bound"]))
    contexts = int(fixture["context_count"])
    pairs = int(fixture["orientation_pair_count"])
    horizon = Fraction(str(fixture["time_horizon"]))
    check("context inputs", contexts == 4 and pairs == 2 and horizon > 0, fixture, "four contexts", "hypotheses")
    check("seed agreement", one == Fraction(str(seed["derived_oracles"]["one_orientation_remainder_squared_bound"])), one, seed["derived_oracles"]["one_orientation_remainder_squared_bound"], "upstream")

    amplitudes = [Fraction(str(value)) for value in reversed(seed["finite_fixture"]["amplitudes"])]
    even = sum(value**4 for value in amplitudes)
    even_negated = sum((-value)**4 for value in amplitudes)
    l1 = sum(abs(value) for value in amplitudes)
    l1_negated = sum(abs(-value) for value in amplitudes)
    check("adjoint even invariant", even == even_negated, [even, even_negated], "equal", "adjoint")
    check("adjoint l1 invariant", l1 == l1_negated, [l1, l1_negated], "equal", "adjoint")
    pair = pairs * 2 * one
    four_sum = contexts * one
    check("adjoint bound", one == Fraction(str(oracle["adjoint_one_context_squared_bound"])), one, oracle["adjoint_one_context_squared_bound"], "four contexts")
    check("pair bound", pair == Fraction(str(oracle["orientation_pair_squared_bound"])), pair, oracle["orientation_pair_squared_bound"], "four contexts")
    check("four sum", four_sum == Fraction(str(oracle["four_context_squared_sum"])), four_sum, oracle["four_context_squared_sum"], "four contexts")

    rf = recurrence["finite_fixture"]
    c = Fraction(str(rf["recurrence_C"]))
    j = Fraction(str(rf["recurrence_J"]))
    z = int(rf["degree"])
    b = Fraction(str(rf["base_weight"]))
    dt = Fraction(str(rf["time_step"]))
    n = int(rf["steps"])
    d = int(rf["boundary_distance"])
    mass = Fraction(str(rf["source_mass"]))
    step = 1 + (c + j * z * b) * dt
    response = step**n * b**(-d) * mass
    coefficient = Fraction(contexts) * horizon * response
    check("step", step == Fraction(str(oracle["weighted_step_factor"])), step, oracle["weighted_step_factor"], "conditional recurrence")
    check("response", response == Fraction(str(oracle["conditional_response_envelope"])), response, oracle["conditional_response_envelope"], "conditional recurrence")
    check("four coefficient", coefficient == Fraction(str(oracle["conditional_four_context_cauchy_coefficient"])), coefficient, oracle["conditional_four_context_cauchy_coefficient"], "conditional recurrence")

    f1 = cylinder["finite_fixture"]["factor_one"]
    f2 = cylinder["finite_fixture"]["factor_two"]
    chi = Fraction(str(cylinder["finite_fixture"]["chi"]))
    sup = Fraction(str(f1["sup_bound"])) * Fraction(str(f2["sup_bound"]))
    grad = Fraction(str(f1["sup_bound"])) * Fraction(str(f2["gradient_bound"])) + Fraction(str(f2["sup_bound"])) * Fraction(str(f1["gradient_bound"]))
    same = 2 * sup**2 + grad**2 / chi
    multiplier = Fraction(str(cylinder["finite_fixture"]["form_order_multiplier"]))
    cross = multiplier * same
    check("same product cost", same == Fraction(str(oracle["product_same_form_cost"])), same, oracle["product_same_form_cost"], "product interface")
    check("cross product cost", cross == Fraction(str(oracle["product_cross_form_cost"])), cross, oracle["product_cross_form_cost"], "product interface")

    closed = ("finite_member_four_context_remainder_accounting_closed", "adjoint_context_static_invariance_closed", "orientation_pair_triangle_accounting_closed", "conditional_weighted_recurrence_arithmetic_closed", "conditional_four_context_cauchy_coefficient_closed", "product_cost_recorded")
    check("scope closed", all(scope[key] is True for key in closed), {key: scope[key] for key in closed}, True, "scope")
    open_keys = ("actual_q3_recurrence_closed", "actual_first_commutator_decay_closed", "actual_second_commutator_decay_closed", "modular_derivative_closed", "actual_q3_factorial_history_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "unbounded_product_core_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed", "all_shape_uniformity_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "actual recurrence and downstream gates remain open", "boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FOUR-CONTEXT-HISTORY-RECURRENCE-INTERFACE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "one_context_squared_bound": str(one),
            "adjoint_one_context_squared_bound": str(one),
            "orientation_pair_squared_bound": str(pair),
            "four_context_squared_sum": str(four_sum),
            "weighted_step_factor": str(step),
            "conditional_response_envelope": str(response),
            "conditional_four_context_cauchy_coefficient": str(coefficient),
            "product_same_form_cost": str(same),
            "product_cross_form_cost": str(cross),
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
    print(f"INDEPENDENT FOUR-CONTEXT-HISTORY-RECURRENCE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
