#!/usr/bin/env python3
"""Independent exact Fraction audit for EXP-001153.

The calculation is intentionally written as a separate lane rather than
importing the primary script.  It reverses the support-amplitude iteration and
rebuilds the static and Duhamel coefficients from the manifest inputs.
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

    chi = Fraction(str(fixture["chi"]))
    hbar = Fraction(str(fixture["hbar"]))
    m5 = Fraction(str(fixture["m5"]))
    support_size = int(fixture["support_size"])
    amplitudes = [Fraction(str(value)) for value in reversed(fixture["amplitudes"])]
    time_horizon = Fraction(str(fixture["time_horizon"]))
    check("positive parameters", chi > 0 and hbar > 0 and m5 > 0 and support_size > 0 and time_horizon > 0 and int(fixture["orientations"]) == 2, fixture, "positive fixed finite inputs", "hypotheses")
    check("support cardinality", len(amplitudes) == support_size, [len(amplitudes), support_size], support_size, "support")

    force_fourth = Fraction(str(static["derived_oracles"]["force_fourth_bound"]))
    check("force input agreement", force_fourth == Fraction(2282697884376432, 5), force_fourth, "2282697884376432/5", "upstream")
    check("force safe premise", force_fourth >= 1, force_fourth, ">=1", "force")

    shifted = [32 * chi * chi * m5 + value**4 / 2 for value in amplitudes]
    kinetic = 2 * support_size**3 * sum((value / (chi * hbar))**4 * bound for value, bound in zip(amplitudes, shifted))
    l1 = sum((value if value >= 0 else -value) for value in amplitudes)
    force_safe = 2 * (l1 / (chi * hbar))**2 * force_fourth
    full = 2 * (kinetic + force_safe)
    one = time_horizon**4 * full / 4
    two = time_horizon**4 * full
    kernel = (time_horizon**2 / 2) ** 2
    check("kinetic oracle", kinetic == Fraction(str(oracle["kinetic_squared_bound"])), kinetic, oracle["kinetic_squared_bound"], "static word")
    check("l1 oracle", l1 == Fraction(str(oracle["l1_amplitude"])), l1, oracle["l1_amplitude"], "static word")
    check("force oracle", force_safe == Fraction(str(oracle["force_safe_squared_bound"])), force_safe, oracle["force_safe_squared_bound"], "static word")
    check("full oracle", full == Fraction(str(oracle["full_word_squared_bound"])), full, oracle["full_word_squared_bound"], "static word")
    check("one orientation oracle", one == Fraction(str(oracle["one_orientation_remainder_squared_bound"])), one, oracle["one_orientation_remainder_squared_bound"], "Duhamel")
    check("two orientation oracle", two == Fraction(str(oracle["two_orientation_difference_squared_bound"])), two, oracle["two_orientation_difference_squared_bound"], "Duhamel")
    check("kernel oracle", kernel == Fraction(str(oracle["duhamel_kernel_squared_integral"])), kernel, oracle["duhamel_kernel_squared_integral"], "Duhamel")

    f1 = cylinder["finite_fixture"]["factor_one"]
    f2 = cylinder["finite_fixture"]["factor_two"]
    sup = Fraction(str(f1["sup_bound"])) * Fraction(str(f2["sup_bound"]))
    grad = Fraction(str(f1["sup_bound"])) * Fraction(str(f2["gradient_bound"])) + Fraction(str(f2["sup_bound"])) * Fraction(str(f1["gradient_bound"]))
    same = 2 * sup**2 + grad**2 / chi
    cross = 21 * same
    check("product sup", sup == 2, sup, 2, "product interface")
    check("product gradient", grad == Fraction(7, 2), grad, "7/2", "product interface")
    check("product same", same == Fraction(str(oracle["product_same_form_cost"])), same, oracle["product_same_form_cost"], "product interface")
    check("product cross", cross == Fraction(str(oracle["product_cross_form_cost"])), cross, oracle["product_cross_form_cost"], "product interface")

    closed = ("finite_support_static_multi_character_recomputed", "finite_member_positive_time_remainder_closed", "finite_member_negative_time_remainder_closed", "finite_member_two_orientation_difference_closed", "product_cost_recorded")
    check("finite history closure", all(scope[key] is True for key in closed), {key: scope[key] for key in closed}, True, "scope")
    open_keys = ("modular_derivative_closed", "actual_q3_four_context_history_closed", "actual_q3_factorial_history_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "unbounded_product_core_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed", "arbitrary_boundary_extension_closed", "all_shape_uniformity_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "downstream gates open", "boundary")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
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
            "amplitudes": [str(value) for value in reversed(amplitudes)],
            "kinetic_squared_bound": str(kinetic),
            "l1_amplitude": str(l1),
            "force_safe_squared_bound": str(force_safe),
            "full_word_squared_bound": str(full),
            "one_orientation_remainder_squared_bound": str(one),
            "negative_orientation_remainder_squared_bound": str(one),
            "two_orientation_difference_squared_bound": str(two),
            "duhamel_kernel_squared_integral": str(kernel),
            "product_same_form_cost": str(same),
            "product_cross_form_cost": str(cross),
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
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT TWO-SIDED-DUHAMEL-HISTORY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
