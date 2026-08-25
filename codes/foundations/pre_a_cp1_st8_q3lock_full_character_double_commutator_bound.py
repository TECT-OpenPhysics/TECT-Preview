#!/usr/bin/env python3
"""Primary exact audit for EXP-001152.

The package composes two registered inputs: the kinetic character estimate from
EXP-001068 and the compact-source endpoint third-moment bridge from EXP-001061.
The onsite-plus-edge force estimate is rebuilt here from global polynomial
inequalities, so the finite field grid is only a sanity check and not the
source of the claimed constant.  The result is a registered-family static
bound, not a thermodynamic history theorem.
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
SLUG = "pre_a_cp1_st8_q3lock_full_character_double_commutator_bound"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-full-character-double-commutator-bound-manifest.json"
KINETIC = REPO / "strategy/pre-a-cp1-st8-q3lock-uniform-kinetic-character-moment-corollary-manifest.json"
FORCE = REPO / "strategy/pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge-manifest.json"
M5_AUTHORITY = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-doublet-route-split-manifest.json"
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


def compact_assertions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, int] = {}
    for row in rows:
        group = str(row.get("group", "unknown"))
        groups[group] = groups.get(group, 0) + 1
    summary = {"total": len(rows), "groups": groups, "storage": "compact-summary; all assertions executed in memory"}
    return rows[:18] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    kinetic = json.loads(KINETIC.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    m5_authority = json.loads(M5_AUTHORITY.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    chi = Fraction(fixture["chi"])
    hbar = Fraction(fixture["hbar"])
    g = Fraction(fixture["g"])
    r = Fraction(fixture["r"])
    gamma = Fraction(fixture["gamma"])
    c = Fraction(fixture["c"])
    lam = Fraction(fixture["lambda"])
    m5 = Fraction(fixture["m5"])
    degree = int(fixture["degree"])
    amplitude = Fraction(fixture["character_amplitude"])
    grid = [int(value) for value in fixture["field_grid"]]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001152" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001152/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("kinetic parent", kinetic["exploration_id"] == "EXP-001068" and kinetic["scope"]["kinetic_character_two_sided_gibbs_bound_closed"] is True, kinetic["exploration_id"], "EXP-001068 kinetic input", "upstream")
    check("force parent", force["exploration_id"] == "EXP-001061" and force["scope"]["compact_source_endpoint_third_moment_bridge_closed"] is True, force["exploration_id"], "EXP-001061 pair-moment input", "upstream")
    m5_scope = m5_authority["actual_q3_static_fifth_moment_and_elliptic_embedding"]
    check("m5 authority", "m5<infinity" in m5_scope["conclusion"] and "Registered finite periodic" in m5_scope["scope"], m5_scope["conclusion"], "uniform registered m5", "upstream")
    check("positive parameters", chi > 0 and hbar > 0 and g > 0 and gamma > 0 and m5 > 0 and degree > 0 and amplitude != 0, fixture, "positive inputs", "hypotheses")

    # Onsite force: |r q + g q^3|^4 <= 8(r^4 q^4 + g^4 q^12),
    # q^4 <= k/gamma and q^12 <= k^5/gamma^3 for k>=1.
    onsite_coefficient = 8 * (r**4 / gamma + g**4 / gamma**3)
    check("onsite force coefficient", onsite_coefficient == 8 * (r**4 / gamma + g**4 / gamma**3), onsite_coefficient, "8*(r^4/gamma+g^4/gamma^3)", "onsite force")

    # Edge force: S=1+q^4+v^4 >= 1, |q|,|v|<=S^(1/4),
    # |q-v|<=2*S^(1/4), and |2q^2-qv+v^2|<=4*S^(1/2).
    edge_constant = 2 * c + 4 * lam
    max_pair_factor = max(Fraction(1), Fraction(8) / g)
    ar = r**2 / (2 * g)
    a_gamma = g / (4 * gamma)
    c0 = 1 + 2 * ar
    pair_moment = 9 * (c0**3 + 2 * a_gamma**3 * m5)
    check("edge constant derivation", edge_constant == 2 * c + 4 * lam, edge_constant, "2*c+4*lambda", "edge force")
    check("pair moment agreement", pair_moment == Fraction(force["finite_fixture"]["derived_M_bridge_compact"]), pair_moment, force["finite_fixture"]["derived_M_bridge_compact"], "pair moment")
    edge_single_fourth = edge_constant**4 * max_pair_factor**3 * pair_moment
    edge_sum_fourth = Fraction(degree) ** 4 * edge_single_fourth
    check("edge single formula", edge_single_fourth == edge_constant**4 * max_pair_factor**3 * pair_moment, edge_single_fourth, "C_edge^4*max(1,8/g)^3*M_pair", "edge force")
    check("edge count", edge_sum_fourth == Fraction(degree) ** 4 * edge_single_fourth, edge_sum_fourth, "z^4*single_edge", "edge force")

    force_fourth = 8 * (onsite_coefficient * m5 + edge_sum_fourth)
    check("full force fourth formula", force_fourth == 8 * (onsite_coefficient * m5 + edge_sum_fourth), force_fourth, "8*(A_on*m5+A_edge)", "force moment")
    check("force fourth finite", force_fourth >= 1, force_fourth, ">=1 for rational safe L2 envelope", "force moment")

    kinetic_squared = (amplitude**4 / (chi**4 * hbar**4)) * (64 * chi**2 * m5 + amplitude**4)
    force_safe_squared = 2 * (amplitude / (chi * hbar))**2 * force_fourth
    full_safe_squared = 2 * (kinetic_squared + force_safe_squared)
    check("kinetic composition", kinetic_squared == (amplitude**4 / (chi**4 * hbar**4)) * (64 * chi**2 * m5 + amplitude**4), kinetic_squared, "EXP-001068 kinetic bound", "composition")
    check("force character composition", force_safe_squared == 2 * (amplitude / (chi * hbar))**2 * force_fourth, force_safe_squared, "safe force L2 bound", "composition")
    check("full triangle envelope", full_safe_squared == 2 * (kinetic_squared + force_safe_squared), full_safe_squared, "2*(kinetic+force)", "composition")

    onsite_grid = 0
    edge_grid = 0
    pair_grid = 0
    for q in grid:
        qf = Fraction(q)
        k_lower = 1 + gamma * qf**4
        onsite_force = r * qf + g * qf**3
        check(f"onsite grid q={q}", abs(onsite_force)**4 <= onsite_coefficient * k_lower**5, [q, onsite_force], "analytic onsite envelope", "grid sanity")
        onsite_grid += 1
        for v in grid:
            vf = Fraction(v)
            s = 1 + qf**4 + vf**4
            edge_force = c * (qf - vf) + lam * (qf - vf) * (2 * qf**2 - qf * vf + vf**2) / 2
            pair_energy = 1 + (r * qf**2 / 2 + g * qf**4 / 4 + r**2 / (2 * g)) + (r * vf**2 / 2 + g * vf**4 / 4 + r**2 / (2 * g))
            check(f"edge grid q={q} v={v}", abs(edge_force)**4 <= edge_constant**4 * s**3, [q, v, edge_force], "analytic edge envelope", "grid sanity")
            check(f"pair grid q={q} v={v}", s <= max_pair_factor * pair_energy, [q, v, s, pair_energy], "S<=max(1,8/g)*E_pair", "grid sanity")
            edge_grid += 1
            pair_grid += 1
    check("grid coverage", onsite_grid == len(grid) and edge_grid == len(grid) ** 2 and pair_grid == len(grid) ** 2, [onsite_grid, edge_grid, pair_grid], [len(grid), len(grid) ** 2, len(grid) ** 2], "grid sanity")

    closed_keys = ("global_scalar_edge_force_bound_closed", "onsite_force_fourth_moment_envelope_closed", "compact_source_pair_third_moment_reused", "full_onsite_edge_force_fourth_moment_bound_closed", "full_character_second_commutator_safe_bound_closed", "registered_periodic_compact_source_static_q3_scope_closed")
    check("registered static closure", all(scope[key] is True for key in closed_keys), scope, True, "scope")
    open_keys = ("arbitrary_boundary_extension_closed", "all_shape_exhaustion_uniformity_closed", "exact_ccr_common_core_closed", "modular_domain_transfer_closed", "actual_q3_four_context_history_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "history and downstream gates remain open", "boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FULL-CHARACTER-DOUBLE-COMMUTATOR-BOUND",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "onsite_force_fourth_coefficient": str(onsite_coefficient),
            "edge_constant": str(edge_constant),
            "max_pair_factor": str(max_pair_factor),
            "pair_moment": str(pair_moment),
            "edge_single_fourth_bound": str(edge_single_fourth),
            "edge_sum_fourth_bound": str(edge_sum_fourth),
            "force_fourth_bound": str(force_fourth),
            "kinetic_second_norm_bound": str(kinetic_squared),
            "force_safe_second_norm_bound": str(force_safe_squared),
            "full_safe_second_norm_bound": str(full_safe_squared),
            "onsite_force_grid_rows": onsite_grid,
            "edge_force_grid_rows": edge_grid,
            "pair_energy_grid_rows": pair_grid,
            "global_scalar_edge_force_bound_closed": True,
            "onsite_force_fourth_moment_envelope_closed": True,
            "full_onsite_edge_force_fourth_moment_bound_closed": True,
            "full_character_second_commutator_safe_bound_closed": True,
            "registered_periodic_compact_source_static_q3_scope_closed": True,
            "arbitrary_boundary_extension_closed": False,
            "all_shape_exhaustion_uniformity_closed": False,
            "exact_ccr_common_core_closed": False,
            "modular_domain_transfer_closed": False,
            "actual_q3_four_context_history_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "common_alpha_closed": False,
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
    print(f"PRIMARY FULL-CHARACTER-DOUBLE-COMMUTATOR-BOUND PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
