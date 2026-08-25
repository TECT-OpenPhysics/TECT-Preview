#!/usr/bin/env python3
"""Primary exact audit for EXP-001153.

This package takes the registered full Q3 static second-commutator envelope
from EXP-001152 and inserts it into the finite-member Duhamel remainder for a
fixed two-site configuration character.  The positive and negative time
orientations are kept separate.  Product, modular and exhaustion costs are
recorded as boundaries, not silently promoted to a thermodynamic theorem.
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
SLUG = "pre_a_cp1_st8_q3lock_full_character_two_sided_duhamel_history_bound"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-full-character-two-sided-duhamel-history-bound-manifest.json"
STATIC = REPO / "strategy/pre-a-cp1-st8-q3lock-full-character-double-commutator-bound-manifest.json"
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
    static = json.loads(STATIC.read_text(encoding="utf-8"))
    cylinder = json.loads(CYLINDER.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    oracle = manifest["derived_oracles"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001153" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001153/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("static authority", static["exploration_id"] == "EXP-001152" and static["scope"]["full_character_second_commutator_safe_bound_closed"] is True, static["exploration_id"], "EXP-001152 registered full static bound", "upstream")
    check("bounded cylinder authority", cylinder["exploration_id"] == "EXP-001150" and cylinder["scope"]["inductive_limit_test_algebra_contract_closed"] is True, cylinder["exploration_id"], "EXP-001150 bounded cylinder contract", "upstream")

    chi = Fraction(fixture["chi"])
    hbar = Fraction(fixture["hbar"])
    m5 = Fraction(fixture["m5"])
    support_size = int(fixture["support_size"])
    amplitudes = tuple(Fraction(value) for value in fixture["amplitudes"])
    time_horizon = Fraction(fixture["time_horizon"])
    orientations = int(fixture["orientations"])
    check("positive parameters", chi > 0 and hbar > 0 and m5 > 0 and support_size > 0 and time_horizon > 0 and orientations == 2, fixture, "positive fixed finite inputs", "hypotheses")
    check("support cardinality", len(amplitudes) == support_size, [len(amplitudes), support_size], support_size, "support")

    g_force4 = Fraction(static["derived_oracles"]["force_fourth_bound"])
    check("force input agreement", g_force4 == Fraction("2282697884376432/5"), g_force4, "registered EXP-001152 force fourth bound", "upstream")
    check("force safe premise", g_force4 >= 1, g_force4, ">=1 for sqrt(X)<=X", "force")

    shifted_bounds = tuple(32 * chi**2 * m5 + amplitude**4 / 2 for amplitude in amplitudes)
    kinetic_squared = 2 * support_size**3 * sum((amplitude / (chi * hbar))**4 * shifted for amplitude, shifted in zip(amplitudes, shifted_bounds))
    l1_amplitude = sum(abs(amplitude) for amplitude in amplitudes)
    force_safe_squared = 2 * (l1_amplitude / (chi * hbar))**2 * g_force4
    full_word_squared = 2 * (kinetic_squared + force_safe_squared)
    one_orientation_squared = time_horizon**4 * full_word_squared / 4
    two_orientation_squared = time_horizon**4 * full_word_squared
    kernel_squared_integral = (time_horizon**2 / 2) ** 2

    check("kinetic bound", kinetic_squared == Fraction(oracle["kinetic_squared_bound"]), kinetic_squared, oracle["kinetic_squared_bound"], "static word")
    check("l1 amplitude", l1_amplitude == Fraction(oracle["l1_amplitude"]), l1_amplitude, oracle["l1_amplitude"], "static word")
    check("force safe bound", force_safe_squared == Fraction(oracle["force_safe_squared_bound"]), force_safe_squared, oracle["force_safe_squared_bound"], "static word")
    check("full word bound", full_word_squared == Fraction(oracle["full_word_squared_bound"]), full_word_squared, oracle["full_word_squared_bound"], "static word")
    check("one orientation Duhamel scaling", one_orientation_squared == Fraction(oracle["one_orientation_remainder_squared_bound"]), one_orientation_squared, oracle["one_orientation_remainder_squared_bound"], "Duhamel")
    check("two orientation triangle scaling", two_orientation_squared == Fraction(oracle["two_orientation_difference_squared_bound"]), two_orientation_squared, oracle["two_orientation_difference_squared_bound"], "Duhamel")
    check("kernel square integral", kernel_squared_integral == Fraction(oracle["duhamel_kernel_squared_integral"]), kernel_squared_integral, oracle["duhamel_kernel_squared_integral"], "Duhamel")

    product_one = Fraction(cylinder["finite_fixture"]["factor_one"]["sup_bound"])
    product_two = Fraction(cylinder["finite_fixture"]["factor_two"]["sup_bound"])
    gradient_one = Fraction(cylinder["finite_fixture"]["factor_one"]["gradient_bound"])
    gradient_two = Fraction(cylinder["finite_fixture"]["factor_two"]["gradient_bound"])
    product_sup = product_one * product_two
    product_gradient = product_one * gradient_two + product_two * gradient_one
    same_form_cost = 2 * product_sup**2 + product_gradient**2 / chi
    cross_form_cost = 21 * same_form_cost
    check("product sup rule", product_sup == 2, product_sup, 2, "product interface")
    check("product gradient rule", product_gradient == Fraction(7, 2), product_gradient, "7/2", "product interface")
    check("product same form cost", same_form_cost == Fraction(oracle["product_same_form_cost"]), same_form_cost, oracle["product_same_form_cost"], "product interface")
    check("product cross form cost", cross_form_cost == Fraction(oracle["product_cross_form_cost"]), cross_form_cost, oracle["product_cross_form_cost"], "product interface")

    closed_keys = ("finite_support_static_multi_character_recomputed", "finite_member_positive_time_remainder_closed", "finite_member_negative_time_remainder_closed", "finite_member_two_orientation_difference_closed", "product_cost_recorded")
    check("finite history closure", all(scope[key] is True for key in closed_keys), {key: scope[key] for key in closed_keys}, True, "scope")
    open_keys = ("modular_derivative_closed", "actual_q3_four_context_history_closed", "actual_q3_factorial_history_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "unbounded_product_core_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed", "arbitrary_boundary_extension_closed", "all_shape_uniformity_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "downstream history and QFT gates remain open", "boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FULL-CHARACTER-TWO-SIDED-DUHAMEL-HISTORY-BOUND",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "support_size": support_size,
            "amplitudes": [str(value) for value in amplitudes],
            "kinetic_squared_bound": str(kinetic_squared),
            "l1_amplitude": str(l1_amplitude),
            "force_safe_squared_bound": str(force_safe_squared),
            "full_word_squared_bound": str(full_word_squared),
            "one_orientation_remainder_squared_bound": str(one_orientation_squared),
            "negative_orientation_remainder_squared_bound": str(one_orientation_squared),
            "two_orientation_difference_squared_bound": str(two_orientation_squared),
            "duhamel_kernel_squared_integral": str(kernel_squared_integral),
            "product_same_form_cost": str(same_form_cost),
            "product_cross_form_cost": str(cross_form_cost),
            "finite_support_static_multi_character_recomputed": True,
            "finite_member_positive_time_remainder_closed": True,
            "finite_member_negative_time_remainder_closed": True,
            "finite_member_two_orientation_difference_closed": True,
            "product_cost_recorded": True,
            "modular_derivative_closed": False,
            "actual_q3_four_context_history_closed": False,
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
    print(f"PRIMARY TWO-SIDED-DUHAMEL-HISTORY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
