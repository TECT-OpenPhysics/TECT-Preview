#!/usr/bin/env python3
"""Primary symbolic audit for EXP-001075.

The package is a conditional seminorm bridge.  It computes the exact algebra
that would follow from four declared weighted moment-root inputs; it does not
claim those inputs for the thermodynamic Q3 system.
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
SLUG = "pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-weighted-seminorm-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-weighted-majorant-manifest.json"
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

    check("identity", manifest["exploration_id"] == "EXP-001075" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001075/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("previous authority", previous["exploration_id"] == "EXP-001074" and previous["scope"]["derivative_weighted_pointwise_bound_closed"] is True, previous["exploration_id"], "EXP-001074 weighted majorant", "authority")
    check("domination is explicit", "declared two-sided multiplication-domination hypothesis" in manifest["model"]["mixed_moment_inputs"], manifest["model"]["mixed_moment_inputs"], "explicit hypothesis", "model")
    check("modular inputs are separate", "separate roots" in manifest["model"]["modular_inputs"] and "no Hamiltonian/modular commutation" in manifest["model"]["modular_inputs"], manifest["model"]["modular_inputs"], "separate modular input", "model")

    hbar = rational(fixture["hbar"])
    c1 = rational(fixture["A1_sum"])
    c0 = rational(fixture["A0_sum"])
    check("A1 majorant authority", c1 == rational(previous["derived_majorants"]["A1_sum"]), c1, previous["derived_majorants"]["A1_sum"], "authority")
    check("A0 majorant authority", c0 == rational(previous["derived_majorants"]["A0_sum"]), c0, previous["derived_majorants"]["A0_sum"], "authority")
    check("positive coefficients", c1 > 0 and c0 > 0 and hbar > 0, [c1, c0, hbar], "positive", "algebra")

    p_plus = rational(fixture["P_plus"])
    q_plus = rational(fixture["Q_plus"])
    p_minus = rational(fixture["P_minus"])
    q_minus = rational(fixture["Q_minus"])
    p_delta_plus = rational(fixture["P_delta_plus"])
    q_delta_plus = rational(fixture["Q_delta_plus"])
    p_delta_minus = rational(fixture["P_delta_minus"])
    q_delta_minus = rational(fixture["Q_delta_minus"])
    inputs = (p_plus, q_plus, p_minus, q_minus, p_delta_plus, q_delta_plus, p_delta_minus, q_delta_minus)
    check("moment roots nonnegative", all(value >= 0 for value in inputs), inputs, "nonnegative", "moments")

    m_plus = sp.factor(c1 * p_plus / hbar + c0 * q_plus)
    m_minus = sp.factor(c1 * p_minus / hbar + c0 * q_minus)
    m_two = sp.factor(m_plus + m_minus)
    m_delta_plus = sp.factor(c1 * p_delta_plus / hbar + c0 * q_delta_plus)
    m_delta_minus = sp.factor(c1 * p_delta_minus / hbar + c0 * q_delta_minus)
    m_delta_two = sp.factor(m_delta_plus + m_delta_minus)
    for label, value in (("M_plus", m_plus), ("M_minus", m_minus), ("M_two_orientation", m_two), ("M_delta_plus", m_delta_plus), ("M_delta_minus", m_delta_minus), ("M_delta_two_orientation", m_delta_two)):
        check(label, value == rational(fixture[f"derived_{label}"]), value, fixture[f"derived_{label}"], "bridge")

    time = rational(fixture["time"])
    t3_over_6 = sp.factor(time**3 / 6)
    check("third Taylor scale", t3_over_6 == rational(fixture["derived_t3_over_6"]), t3_over_6, fixture["derived_t3_over_6"], "time")
    third_bound = sp.factor(t3_over_6 * m_two)
    third_modular_bound = sp.factor(t3_over_6 * m_delta_two)
    check("third two-orientation bound", third_bound == rational(fixture["derived_third_two_orientation_bound"]), third_bound, fixture["derived_third_two_orientation_bound"], "time")
    check("third modular bound", third_modular_bound == rational(fixture["derived_third_modular_bound"]), third_modular_bound, fixture["derived_third_modular_bound"], "time")
    check("triangle decomposition", m_two == (c1 * p_plus / hbar + c0 * q_plus) + (c1 * p_minus / hbar + c0 * q_minus), m_two, "M_plus+M_minus", "bridge")
    check("modular separation", m_delta_two == m_delta_plus + m_delta_minus and m_delta_two != m_two, [m_delta_two, m_two], "separate modular roots", "modular")

    scope = manifest["scope"]
    closed_keys = ("pointwise_majorant_reused", "conditional_two_orientation_seminorm_bridge_closed", "conditional_modular_companion_formula_closed", "third_boundary_t3_scale_closed")
    check("conditional bridge closure", all(scope[key] is True for key in closed_keys), {key: scope[key] for key in closed_keys}, "conditional bridge closed", "scope")
    open_keys = ("actual_weighted_moment_bound_closed", "multiplication_domination_on_actual_q3_core_closed", "modular_domain_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_projected_d_duhamel_cauchy_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")

    derived = {
        "A1_sum": c1,
        "A0_sum": c0,
        "M_plus": m_plus,
        "M_minus": m_minus,
        "M_two_orientation": m_two,
        "M_delta_plus": m_delta_plus,
        "M_delta_minus": m_delta_minus,
        "M_delta_two_orientation": m_delta_two,
        "t3_over_6": t3_over_6,
        "third_two_orientation_bound": third_bound,
        "third_modular_bound": third_modular_bound,
        "actual_weighted_moment_bound_closed": False,
        "multiplication_domination_on_actual_q3_core_closed": False,
        "modular_domain_closed": False,
    }
    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-PROJECTED-DELTA-D-THIRD-COEFFICIENT-WEIGHTED-SEMINORM-BRIDGE",
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
    print(f"PRIMARY PROJECTED-DELTA-D-THIRD-WEIGHTED-SEMINORM-BRIDGE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
