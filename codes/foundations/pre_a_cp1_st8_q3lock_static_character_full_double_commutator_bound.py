#!/usr/bin/env python3
"""Primary exact audit for EXP-001069.

This combines the registered static endpoint-force moment with the independent
kinetic character estimate.  It is deliberately a finite-periodic static
checkpoint; it does not audit split histories or a thermodynamic limit.
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
SLUG = "pre-a-cp1-st8-q3lock-static-character-full-double-commutator-bound"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
BRIDGE = REPO / "strategy/pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge-manifest.json"
FORCE = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
KINETIC = REPO / "strategy/pre-a-cp1-st8-q3lock-uniform-kinetic-character-moment-corollary-manifest.json"
SPLIT = REPO / "strategy/pre-a-cp1-st8-q3lock-kinetic-force-double-commutator-split-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-doublet-route-split-manifest.json"
COMMON = REPO / "strategy/pre-a-cp1-st8-q3lock-common-alpha-topology-critical-graph-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


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
    bridge = json.loads(BRIDGE.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    kinetic = json.loads(KINETIC.read_text(encoding="utf-8"))
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    common = json.loads(COMMON.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001069" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001069/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("prior kinetic identity", kinetic["exploration_id"] == "EXP-001068", kinetic["exploration_id"], "EXP-001068", "authority")
    check("prior split identity", split["exploration_id"] == "EXP-001067", split["exploration_id"], "EXP-001067", "authority")
    check("bridge identity", bridge["exploration_id"] == "EXP-001061", bridge["exploration_id"], "EXP-001061", "authority")
    check("force identity", force["exploration_id"] == "EXP-001059", force["exploration_id"], "EXP-001059", "authority")
    check("m5 identity", upstream["exploration_id"] == "EXP-000826" and "m5=sup" in upstream["conditional_fifth_graph_transport"]["definitions"], upstream["exploration_id"], "EXP-000826", "authority")
    check("coercivity authority", "p_z^2/(2chi)" in common["model"]["onsite_split"], common["model"]["onsite_split"], "onsite coercivity", "authority")
    check("exact split", split["model"]["exact_split"].startswith(manifest["model"]["split"]), manifest["model"]["split"], split["model"]["exact_split"], "CCR")
    check("force input", "C=122099/35840" in force["model"]["force_input"], force["model"]["force_input"], "registered force grid", "force")
    check("bridge input", bridge["scope"]["compact_source_endpoint_third_moment_bridge_closed"] is True and bridge["model"]["bridge_bound"].startswith("sup phi"), bridge["scope"], "closed endpoint bridge", "force")

    g = rational(fixture["g"])
    r = rational(fixture["r"])
    gamma = rational(fixture["gamma"])
    m5 = rational(fixture["m5"])
    chi = rational(fixture["chi"])
    hbar = rational(fixture["hbar"])
    amplitude = rational(fixture["character_amplitude"])
    force_constant = rational(fixture["force_constant"])
    ratio = max(sp.Integer(1), sp.Rational(8) / g)
    a_gamma = sp.factor(g / (4 * gamma))
    A_r = sp.factor(r**2 / (2 * g))
    C0 = sp.factor(1 + 2 * A_r)
    M_bridge = sp.factor(9 * (C0**3 + 2 * a_gamma**3 * m5))
    force_fourth = sp.factor(force_constant**4 * ratio**3 * M_bridge)
    force_sqrt_ceiling = rational(fixture["force_sqrt_ceiling"])
    force_ceiling_square = sp.factor(force_sqrt_ceiling**2)
    force_norm_squared_upper = sp.factor(2 * (amplitude / (chi * hbar))**2 * force_sqrt_ceiling)

    kinetic_fixture = kinetic["finite_fixture"]
    kinetic_bound = sp.factor((amplitude**4 / (chi**4 * hbar**4)) * (64 * chi**2 * m5 + amplitude**4))
    kinetic_sqrt_ceiling = rational(fixture["kinetic_norm_sqrt_ceiling"])
    force_norm_sqrt_ceiling = rational(fixture["force_norm_sqrt_ceiling"])
    full_upper = sp.factor((kinetic_sqrt_ceiling + force_norm_sqrt_ceiling)**2)

    check("positive parameters", g > 0 and gamma > 0 and m5 >= 0 and chi > 0 and hbar > 0 and amplitude != 0, [g, gamma, m5, chi, hbar, amplitude], "positive inputs", "parameters")
    check("bridge a_gamma", a_gamma == rational(bridge["finite_fixture"]["derived_a_gamma"]), a_gamma, bridge["finite_fixture"]["derived_a_gamma"], "bridge")
    check("bridge A_r", A_r == rational(bridge["finite_fixture"]["derived_A_r"]), A_r, bridge["finite_fixture"]["derived_A_r"], "bridge")
    check("bridge C0", C0 == rational(bridge["finite_fixture"]["derived_C0"]), C0, bridge["finite_fixture"]["derived_C0"], "bridge")
    check("bridge M", M_bridge == rational(bridge["finite_fixture"]["derived_M_bridge_compact"]), M_bridge, bridge["finite_fixture"]["derived_M_bridge_compact"], "bridge")
    check("force ratio", ratio == rational(fixture["force_weight_ratio"]), ratio, fixture["force_weight_ratio"], "force")
    check("force fourth moment", force_fourth == rational(fixture["derived_force_fourth_moment"]), force_fourth, fixture["derived_force_fourth_moment"], "force")
    check("force ceiling", force_fourth < force_ceiling_square, force_fourth, f"<{force_ceiling_square}", "force")
    check("force norm envelope", force_norm_squared_upper == rational(fixture["derived_force_norm_squared_upper"]), force_norm_squared_upper, fixture["derived_force_norm_squared_upper"], "force")
    check("kinetic bound", kinetic_bound == rational(kinetic_fixture["derived_double_commutator_kinetic_squared_norm_bound"]), kinetic_bound, kinetic_fixture["derived_double_commutator_kinetic_squared_norm_bound"], "kinetic")
    check("kinetic ceiling", kinetic_bound < kinetic_sqrt_ceiling**2, kinetic_bound, f"<{kinetic_sqrt_ceiling**2}", "kinetic")
    check("force square ceiling", force_norm_squared_upper < force_norm_sqrt_ceiling**2, force_norm_squared_upper, f"<{force_norm_sqrt_ceiling**2}", "force")
    check("full triangle envelope", full_upper == rational(fixture["derived_full_squared_norm_upper"]), full_upper, fixture["derived_full_squared_norm_upper"], "triangle")
    check("bridge grid", int(bridge["finite_fixture"]["grid_points"]) == int(fixture["bridge_grid_points"]), bridge["finite_fixture"]["grid_points"], fixture["bridge_grid_points"], "fixture")
    check("force grid", int(force["finite_fixture"]["grid_points"]) == int(fixture["force_grid_points"]), force["finite_fixture"]["grid_points"], fixture["force_grid_points"], "fixture")

    scope = manifest["scope"]
    check("static closure", scope["endpoint_third_moment_reused"] is True and scope["static_force_summand_two_sided_bound_closed"] is True and scope["static_full_character_double_commutator_bound_closed"] is True, scope, "static character bound closed", "scope")
    open_keys = ("force_history_uniform_closed", "full_actual_q3_double_commutator_uniform_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")

    derived = {
        "g": g,
        "r": r,
        "gamma": gamma,
        "m5": m5,
        "chi": chi,
        "hbar": hbar,
        "character_amplitude": amplitude,
        "force_constant": force_constant,
        "force_weight_ratio": ratio,
        "a_gamma": a_gamma,
        "A_r": A_r,
        "C0": C0,
        "M_bridge_compact": M_bridge,
        "force_fourth_moment": force_fourth,
        "force_fourth_ceiling_square": force_ceiling_square,
        "force_norm_squared_upper": force_norm_squared_upper,
        "kinetic_squared_norm_bound": kinetic_bound,
        "full_squared_norm_upper": full_upper,
        "static_force_summand_two_sided_bound_closed": True,
        "static_full_character_double_commutator_bound_closed": True,
        "force_history_uniform_closed": False,
        "full_actual_q3_double_commutator_uniform_closed": False,
    }
    passed = len(rows)
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-STATIC-CHARACTER-FULL-DOUBLE-COMMUTATOR-BOUND", "exploration_id": manifest["exploration_id"], "task_id": manifest["task_id"], "verdict": "PASS", "passed": passed, "assertion_count": passed, "assertions": rows, "derived": derived, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.output:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY STATIC-FULL-DOUBLE-COMMUTATOR PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
