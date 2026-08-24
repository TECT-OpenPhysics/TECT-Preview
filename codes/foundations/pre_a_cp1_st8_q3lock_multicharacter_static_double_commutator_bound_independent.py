#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001071."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-multicharacter-static-double-commutator-bound"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
STATIC = REPO / "strategy/pre-a-cp1-st8-q3lock-static-character-full-double-commutator-bound-manifest.json"
KINETIC = REPO / "strategy/pre-a-cp1-st8-q3lock-uniform-kinetic-character-moment-corollary-manifest.json"
SPLIT = REPO / "strategy/pre-a-cp1-st8-q3lock-kinetic-force-double-commutator-split-manifest.json"
BRIDGE = REPO / "strategy/pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge-manifest.json"
FORCE = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "independent.json"


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


def frac(value: str | int) -> Fraction:
    return Fraction(str(value))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    static = json.loads(STATIC.read_text(encoding="utf-8"))
    kinetic = json.loads(KINETIC.read_text(encoding="utf-8"))
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    bridge = json.loads(BRIDGE.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001071" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001071/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("static authority", static["exploration_id"] == "EXP-001069" and static["scope"]["static_full_character_double_commutator_bound_closed"] is True, static["exploration_id"], "EXP-001069 static bound", "authority")
    check("kinetic authority", kinetic["exploration_id"] == "EXP-001068" and kinetic["scope"]["kinetic_character_two_sided_gibbs_bound_closed"] is True, kinetic["exploration_id"], "EXP-001068 kinetic bound", "authority")
    check("CCR authority", split["exploration_id"] == "EXP-001067" and "(p_x+a/2)^2" in split["model"]["exact_split"], split["exploration_id"], "EXP-001067 split", "authority")
    check("force authority", bridge["exploration_id"] == "EXP-001061" and force["exploration_id"] == "EXP-001059", [bridge["exploration_id"], force["exploration_id"]], "EXP-001061/EXP-001059", "authority")

    chi = frac(fixture["chi"])
    hbar = frac(fixture["hbar"])
    m5 = frac(fixture["m5"])
    amplitudes = tuple(frac(value) for value in fixture["amplitudes"])
    support_size = int(fixture["support_size"])
    shifted_bounds = tuple(32 * chi**2 * m5 + amplitude**4 / 2 for amplitude in amplitudes)
    kinetic_bound = 2 * support_size**3 * sum((amplitude / (chi * hbar))**4 * shifted for amplitude, shifted in zip(amplitudes, shifted_bounds))
    l1_amplitude = sum(abs(amplitude) for amplitude in amplitudes)
    force_sqrt_ceiling = frac(fixture["force_sqrt_ceiling"])
    force_fourth = frac(static["finite_fixture"]["derived_force_fourth_moment"])
    force_upper = 2 * (l1_amplitude / (chi * hbar))**2 * force_sqrt_ceiling
    kinetic_sqrt_ceiling = frac(fixture["kinetic_norm_sqrt_ceiling"])
    force_norm_sqrt_ceiling = frac(fixture["force_norm_sqrt_ceiling"])
    full_upper = (kinetic_sqrt_ceiling + force_norm_sqrt_ceiling)**2
    check("support cardinality", support_size == len(amplitudes) and support_size > 0, [support_size, len(amplitudes)], ">0 and equal", "parameters")
    check("shifted fourth bounds", shifted_bounds == tuple(frac(value) for value in fixture["derived_shifted_fourth_bounds"]), shifted_bounds, fixture["derived_shifted_fourth_bounds"], "kinetic")
    check("l1 amplitude", l1_amplitude == frac(fixture["derived_l1_amplitude"]), l1_amplitude, fixture["derived_l1_amplitude"], "force")
    check("force fourth ceiling input", force_fourth < force_sqrt_ceiling**2, force_fourth, f"<{force_sqrt_ceiling**2}", "force")
    check("kinetic bound", kinetic_bound == frac(fixture["derived_kinetic_squared_norm"]), kinetic_bound, fixture["derived_kinetic_squared_norm"], "kinetic")
    check("kinetic ceiling", kinetic_bound < kinetic_sqrt_ceiling**2, kinetic_bound, f"<{kinetic_sqrt_ceiling**2}", "kinetic")
    check("force upper", force_upper == frac(fixture["derived_force_squared_upper"]), force_upper, fixture["derived_force_squared_upper"], "force")
    check("force ceiling", force_upper < force_norm_sqrt_ceiling**2, force_upper, f"<{force_norm_sqrt_ceiling**2}", "force")
    check("full triangle upper", full_upper == frac(fixture["derived_full_squared_norm_upper"]), full_upper, fixture["derived_full_squared_norm_upper"], "triangle")
    scope = manifest["scope"]
    check("static multi closure", scope["finite_support_static_multi_character_closed"] is True and scope["static_product_character_bound_closed"] is True, scope, "finite-support static closure", "scope")
    open_keys = ("force_history_uniform_closed", "full_actual_q3_double_commutator_uniform_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")
    derived = {"support_size": support_size, "amplitudes": amplitudes, "shifted_fourth_bounds": shifted_bounds, "l1_amplitude": l1_amplitude, "force_fourth_moment": force_fourth, "kinetic_squared_norm_bound": kinetic_bound, "force_squared_upper": force_upper, "full_squared_norm_upper": full_upper, "finite_support_static_multi_character_closed": True, "static_product_character_bound_closed": True, "product_core_density_closed": False, "actual_q3_factorial_history_proved": False}
    passed = len(rows)
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-MULTICHARACTER-STATIC-DOUBLE-COMMUTATOR-BOUND", "exploration_id": manifest["exploration_id"], "task_id": manifest["task_id"], "verdict": "PASS", "passed": passed, "assertion_count": passed, "assertions": rows, "derived": derived, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.output:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT MULTICHARACTER-STATIC-DOUBLE-COMMUTATOR PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
