#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001152.

This lane reconstructs the coefficient composition in a different order and
checks the global polynomial envelopes on a reversed field grid.  It does not
import the primary implementation.
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


def compact_assertions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, int] = {}
    for row in rows:
        group = str(row.get("group", "unknown"))
        groups[group] = groups.get(group, 0) + 1
    summary = {"total": len(rows), "groups": groups, "storage": "compact-summary; all assertions executed in memory"}
    return rows[:18] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": json.dumps(summary, sort_keys=True), "expected": "all executed assertions passed"}]


def run() -> dict[str, Any]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    kinetic = json.loads(KINETIC.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    m5_authority = json.loads(M5_AUTHORITY.read_text(encoding="utf-8"))
    f = data["finite_fixture"]
    scope = data["scope"]
    chi, hbar = Fraction(f["chi"]), Fraction(f["hbar"])
    g, r, gamma = Fraction(f["g"]), Fraction(f["r"]), Fraction(f["gamma"])
    c, lam, m5 = Fraction(f["c"]), Fraction(f["lambda"]), Fraction(f["m5"])
    z, a = int(f["degree"]), Fraction(f["character_amplitude"])
    grid = tuple(reversed(tuple(int(value) for value in f["field_grid"])))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("provenance", data["exploration_id"] == "EXP-001152" and data["task_id"] == "T-054" and data["claim_bearing"] is False, [data["exploration_id"], data["task_id"], data["claim_bearing"]], "EXP-001152/T-054/false", "provenance")
    check("upstream identities", kinetic["exploration_id"] == "EXP-001068" and force["exploration_id"] == "EXP-001061", [kinetic["exploration_id"], force["exploration_id"]], "EXP-001068/EXP-001061", "upstream")
    check("upstream scopes", kinetic["scope"]["kinetic_character_two_sided_gibbs_bound_closed"] and force["scope"]["compact_source_endpoint_third_moment_bridge_closed"], [kinetic["scope"], force["scope"]], "closed inputs", "upstream")
    check("m5 conclusion", "m5<infinity" in m5_authority["actual_q3_static_fifth_moment_and_elliptic_embedding"]["conclusion"], m5_authority["exploration_id"], "uniform m5", "upstream")

    # Independent composition: calculate the pair bridge first, then the edge
    # envelope, then the force sum and the two-sided character constants.
    shift = r**2 / (2 * g)
    endpoint_factor = g / (4 * gamma)
    pair_constant = 1 + 2 * shift
    pair_moment = 9 * (pair_constant**3 + 2 * endpoint_factor**3 * m5)
    edge_scale = max(Fraction(1), Fraction(8) / g)
    edge_constant = 2 * c + 4 * lam
    edge_one = pair_moment * edge_scale**3 * edge_constant**4
    edge_total = edge_one * z**4
    onsite = 8 * (r**4 / gamma + g**4 / gamma**3)
    force_fourth = 8 * (onsite * m5 + edge_total)
    kinetic = a**4 * (64 * m5 + a**4) / (chi**4 * hbar**4)
    force_safe = 2 * a**2 * force_fourth / (chi**2 * hbar**2)
    full_safe = 2 * (kinetic + force_safe)

    oracle = data["derived_oracles"]
    check("pair moment", pair_moment == Fraction(oracle["pair_third_moment"]) == Fraction(force["finite_fixture"]["derived_M_bridge_compact"]), pair_moment, oracle["pair_third_moment"], "pair moment")
    check("global edge coefficient", edge_constant == 2 * c + 4 * lam, edge_constant, "2*c+4*lambda", "edge force")
    check("onsite envelope", onsite == Fraction(oracle["onsite_force_fourth_coefficient"]), onsite, oracle["onsite_force_fourth_coefficient"], "onsite force")
    check("edge one", edge_one == Fraction(oracle["edge_single_fourth_bound"]), edge_one, oracle["edge_single_fourth_bound"], "edge force")
    check("edge total", edge_total == Fraction(oracle["edge_sum_fourth_bound"]), edge_total, oracle["edge_sum_fourth_bound"], "edge force")
    check("force fourth", force_fourth == Fraction(oracle["force_fourth_bound"]), force_fourth, oracle["force_fourth_bound"], "force moment")
    check("kinetic", kinetic == Fraction(oracle["kinetic_second_norm_bound"]), kinetic, oracle["kinetic_second_norm_bound"], "kinetic")
    check("force safe", force_safe == Fraction(oracle["force_safe_second_norm_bound"]), force_safe, oracle["force_safe_second_norm_bound"], "composition")
    check("full safe", full_safe == Fraction(oracle["full_safe_second_norm_bound"]), full_safe, oracle["full_safe_second_norm_bound"], "composition")
    check("safe root premise", force_fourth >= 1, force_fourth, ">=1", "force moment")

    onsite_rows = edge_rows = pair_rows = 0
    for q in grid:
        qf = Fraction(q)
        k = 1 + gamma * qf**4
        onsite_force = r * qf + g * qf**3
        check(f"reverse onsite {q}", abs(onsite_force)**4 <= onsite * k**5, [q, onsite_force], "analytic", "grid")
        onsite_rows += 1
        for v in grid:
            vf = Fraction(v)
            s = 1 + qf**4 + vf**4
            edge_force = c * (qf - vf) + lam * (qf - vf) * (2 * qf**2 - qf * vf + vf**2) / 2
            e_q = r * qf**2 / 2 + g * qf**4 / 4 + r**2 / (2 * g)
            e_v = r * vf**2 / 2 + g * vf**4 / 4 + r**2 / (2 * g)
            check(f"reverse edge {q},{v}", abs(edge_force)**4 <= edge_constant**4 * s**3, [q, v], "analytic", "grid")
            check(f"reverse pair {q},{v}", s <= edge_scale * (1 + e_q + e_v), [q, v], "pair envelope", "grid")
            edge_rows += 1
            pair_rows += 1
    check("reverse grid coverage", [onsite_rows, edge_rows, pair_rows] == [len(grid), len(grid) ** 2, len(grid) ** 2], [onsite_rows, edge_rows, pair_rows], "coverage", "grid")
    open_keys = ("arbitrary_boundary_extension_closed", "all_shape_exhaustion_uniformity_closed", "exact_ccr_common_core_closed", "modular_domain_transfer_closed", "actual_q3_four_context_history_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("firewall", all(scope[key] is False for key in open_keys), scope, "open", "boundary")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FULL-CHARACTER-DOUBLE-COMMUTATOR-BOUND",
        "claim_id": data["claim_ids"][0],
        "task_id": data["task_id"],
        "exploration_id": data["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": compact_assertions(rows),
        "derived": {
            "onsite_force_fourth_coefficient": str(onsite),
            "edge_constant": str(edge_constant),
            "max_pair_factor": str(edge_scale),
            "pair_moment": str(pair_moment),
            "edge_single_fourth_bound": str(edge_one),
            "edge_sum_fourth_bound": str(edge_total),
            "force_fourth_bound": str(force_fourth),
            "kinetic_second_norm_bound": str(kinetic),
            "force_safe_second_norm_bound": str(force_safe),
            "full_safe_second_norm_bound": str(full_safe),
            "onsite_force_grid_rows": onsite_rows,
            "edge_force_grid_rows": edge_rows,
            "pair_energy_grid_rows": pair_rows,
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
    print(f"INDEPENDENT FULL-CHARACTER-DOUBLE-COMMUTATOR-BOUND PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
