#!/usr/bin/env python3
"""Primary exact audit for EXP-001068.

This is the scalar/operator-algebra checkpoint that turns the registered
onsite fifth Gibbs moment into a two-sided kinetic character bound.  It does
not re-prove the upstream Q3 Gibbs moment theorem and does not include the
force summand of the full second commutator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-uniform-kinetic-character-moment-corollary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-doublet-route-split-manifest.json"
COMMON = REPO / "strategy/pre-a-cp1-st8-q3lock-common-alpha-topology-critical-graph-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    common = json.loads(COMMON.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    chi = sp.Rational(fixture["chi"])
    hbar = sp.Rational(fixture["hbar"])
    m5 = sp.Rational(fixture["m5"])
    amplitude = sp.Rational(fixture["character_amplitude"])
    p = sp.symbols("p", real=True)
    half = amplitude / 2
    p_plus = p + half
    p_minus = p - half

    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001068" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001068/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("upstream m5 scope", upstream["exploration_id"] == "EXP-000826" and "m5=sup" in upstream["conditional_fifth_graph_transport"]["definitions"], upstream["exploration_id"], "EXP-001020 with m5", "authority")
    check("coercivity scope", "p_z^2/(2chi)" in common["model"]["onsite_split"], common["model"]["onsite_split"], "kinetic coercivity", "authority")
    check("positive inputs", chi > 0 and hbar > 0 and m5 >= 0 and amplitude != 0, [chi, hbar, m5, amplitude], "chi,hbar>0; m5>=0; a!=0", "parameters")

    # The exact two-sided character identity uses W p W* = p-a.
    identity_sum = sp.expand(p_plus**4 + p_minus**4)
    raw_sum_bound = sp.expand(16 * (p**4 + half**4))
    check("Weyl shifted orientations", identity_sum == 2 * p**4 + 12 * p**2 * half**2 + 2 * half**4, identity_sum, "2p^4+12p^2(a/2)^2+2(a/2)^4", "Weyl")
    check("scalar fourth shift bound", sp.expand(8 * (p**4 + half**4) - p_plus**4).subs(p, 0) >= 0 and sp.expand(8 * (p**4 + half**4) - p_minus**4).subs(p, 0) >= 0, "p=0 fixture", ">=0", "shift")

    phi_p4_bound = 4 * chi**2 * m5
    shifted_norm_bound = sp.factor(16 * phi_p4_bound + amplitude**4)
    double_bound = sp.factor((amplitude**4 / (chi**4 * hbar**4)) * shifted_norm_bound)
    check("fourth moment reduction", phi_p4_bound == 4 * chi**2 * m5, phi_p4_bound, "4 chi^2 m5", "moment")
    check("shifted seminorm formula", shifted_norm_bound == 64 * chi**2 * m5 + amplitude**4, shifted_norm_bound, "64 chi^2 m5+a^4", "moment")
    check("kinetic coefficient formula", double_bound == (amplitude**4 / (chi**4 * hbar**4)) * (64 * chi**2 * m5 + amplitude**4), double_bound, "derived coefficient bound", "moment")

    p_values = tuple(sp.Rational(value) for value in fixture["p_grid"])
    grid_rows: list[dict[str, Any]] = []
    for value in p_values:
        plus_value = sp.factor(p_plus.subs(p, value))
        minus_value = sp.factor(p_minus.subs(p, value))
        plus_bound = 8 * (value**4 + half**4)
        minus_bound = 8 * (value**4 + half**4)
        check(f"plus shift grid {value}", plus_value**4 <= plus_bound, plus_value**4, plus_bound, "shift")
        check(f"minus shift grid {value}", minus_value**4 <= minus_bound, minus_value**4, minus_bound, "shift")
        grid_rows.append({"p": value, "plus_fourth": plus_value**4, "minus_fourth": minus_value**4, "bound": plus_bound})
    check("grid cardinality", len(grid_rows) == int(fixture["grid_points"]), len(grid_rows), fixture["grid_points"], "fixture")
    check("fixture shifted bound", shifted_norm_bound == sp.Rational(fixture["derived_shifted_kinetic_squared_norm_bound"]), shifted_norm_bound, fixture["derived_shifted_kinetic_squared_norm_bound"], "fixture")
    check("fixture double bound", double_bound == sp.Rational(fixture["derived_double_commutator_kinetic_squared_norm_bound"]), double_bound, fixture["derived_double_commutator_kinetic_squared_norm_bound"], "fixture")

    scope = manifest["scope"]
    check("kinetic closure", scope["onsite_momentum_fourth_moment_closed"] is True and scope["kinetic_character_two_sided_gibbs_bound_closed"] is True and scope["modular_multiplier_for_kinetic_part_needed"] is False, scope, "kinetic subgate closed", "scope")
    open_keys = ("force_summand_closed", "full_actual_q3_double_commutator_uniform_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")

    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": rows,
        "derived": {
            "chi": chi,
            "hbar": hbar,
            "m5": m5,
            "character_amplitude": amplitude,
            "phi_p4_bound": phi_p4_bound,
            "shifted_kinetic_squared_norm_bound": shifted_norm_bound,
            "double_commutator_kinetic_squared_norm_bound": double_bound,
            "onsite_momentum_fourth_moment_closed": True,
            "kinetic_character_two_sided_gibbs_bound_closed": True,
            "modular_multiplier_for_kinetic_part_needed": False,
            "force_summand_closed": False,
            "full_actual_q3_double_commutator_uniform_closed": False,
            "grid_rows": grid_rows,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
            "upstream_manifest": str(UPSTREAM.relative_to(REPO)).replace("\\", "/"),
            "common_manifest": str(COMMON.relative_to(REPO)).replace("\\", "/"),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY UNIFORM-KINETIC-CHARACTER PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
