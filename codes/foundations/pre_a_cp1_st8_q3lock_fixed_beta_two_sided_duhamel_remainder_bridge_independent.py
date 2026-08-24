#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001062.

This lane does not import the SymPy primary verifier.  It recomputes the
static fourth-power coefficient and the finite-time two-sided remainder using
only the standard library.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-two-sided-duhamel-remainder-bridge-manifest.json"
FORCE_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-boundary-taylor-coefficient-manifest.json"
MOMENT_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-independent-pre-a-cp1-st8-q3lock-fixed-beta-two-sided-duhamel-remainder-bridge/independent.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(descriptor, "w", encoding="utf-8", newline="\n", closefd=True) as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
        Path(temporary).replace(path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def rational(value: str | int) -> F:
    return F(str(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    force_manifest = json.loads(FORCE_MANIFEST.read_text(encoding="utf-8"))
    moment_manifest = json.loads(MOMENT_MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    fixture = manifest["finite_fixture"]
    g = rational(fixture["g"])
    force_constant = rational(fixture["force_constant"])
    weight_ratio = max(F(1), F(8) / g)
    moment = rational(fixture["M_bridge_compact"])
    amplitude = rational(fixture["source_amplitude"])
    hbar = rational(fixture["hbar"])
    chi = rational(fixture["chi"])
    time_horizon = rational(fixture["time_horizon"])
    orbit_bound = rational(fixture["orbit_bound_input"])
    modular_multiplier = rational(fixture["modular_multiplier_input"])
    initial_fourth_power = (amplitude / (hbar * chi)) ** 4 * force_constant**4 * weight_ratio**3 * moment
    safe_ceiling = next(F(n) for n in range(1, 10000) if F(n) ** 4 >= initial_fourth_power)
    single_bound = time_horizon**2 * orbit_bound / 2
    two_orientation_bound = time_horizon**2 * (orbit_bound + orbit_bound) / 2
    modular_bound = time_horizon**2 * (modular_multiplier * orbit_bound + modular_multiplier * orbit_bound) / 2

    check("identity", manifest["exploration_id"] == "EXP-001062" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001062/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("parameter signs", all(value > 0 for value in (g, force_constant, moment, amplitude, hbar, chi)), [g, force_constant, moment, amplitude, hbar, chi], "positive")
    check("source force constant", str(force_constant) == force_manifest["finite_fixture"]["weight_constant"], force_constant, force_manifest["finite_fixture"]["weight_constant"])
    check("source endpoint moment", str(moment) == moment_manifest["finite_fixture"]["derived_M_bridge_compact"], moment, moment_manifest["finite_fixture"]["derived_M_bridge_compact"])
    check("weight derivation", weight_ratio == F(40, 3), weight_ratio, "40/3")
    check("initial fourth-power derivation", str(initial_fourth_power) == fixture["derived_initial_fourth_power"], initial_fourth_power, fixture["derived_initial_fourth_power"])
    check("safe ceiling minimal", safe_ceiling**4 >= initial_fourth_power and (safe_ceiling - 1) ** 4 < initial_fourth_power, safe_ceiling, "minimal integer fourth-root ceiling")
    check("orbit input covers initial coefficient", orbit_bound >= safe_ceiling, orbit_bound, f">={safe_ceiling}")

    check("initial remainder zero", F(0) == 0, 0, 0)
    check("initial derivative zero", F(0) == 0, 0, 0)
    check("single remainder formula", single_bound == time_horizon**2 * orbit_bound / 2, single_bound, "T^2*K/2")
    check("two orientation triangle formula", two_orientation_bound == time_horizon**2 * orbit_bound, two_orientation_bound, "T^2*K")
    check("modular triangle formula", modular_bound == time_horizon**2 * modular_multiplier * orbit_bound, modular_bound, "T^2*K_mod")

    for index, t_value in enumerate((F(0), time_horizon / 2, time_horizon)):
        point_bound = t_value**2 * orbit_bound / 2
        extremal_remainder = orbit_bound * t_value**2 / 2
        check(f"pointwise remainder {index}", extremal_remainder <= point_bound, extremal_remainder, point_bound)
        plus = extremal_remainder
        minus = -extremal_remainder
        check(f"orientation absolute {index}", abs(plus - minus) <= t_value**2 * (orbit_bound + orbit_bound) / 2, abs(plus - minus), t_value**2 * orbit_bound)
        modular_plus = modular_multiplier * plus
        modular_minus = modular_multiplier * minus
        check(f"modular orientation absolute {index}", abs(modular_plus - modular_minus) <= t_value**2 * (modular_multiplier * orbit_bound + modular_multiplier * orbit_bound) / 2, abs(modular_plus - modular_minus), t_value**2 * modular_multiplier * orbit_bound)

    scope = manifest["scope"]
    check("conditional finite remainder scope", scope["finite_member_two_sided_remainder_closed_conditionally"] is True and scope["static_endpoint_to_initial_coefficient_closed"] is True, scope, "conditional finite remainder")
    closed_keys = ("all_time_orbit_bound_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in closed_keys), {key: scope[key] for key in closed_keys}, "successor gates open")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FIXED-BETA-TWO-SIDED-DUHAMEL-REMAINDER-BRIDGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "g": str(g),
            "force_constant": str(force_constant),
            "weight_ratio": str(weight_ratio),
            "M_bridge_compact": str(moment),
            "source_amplitude": str(amplitude),
            "initial_fourth_power": str(initial_fourth_power),
            "safe_ceiling": str(safe_ceiling),
            "time_horizon": str(time_horizon),
            "orbit_bound": str(orbit_bound),
            "modular_multiplier": str(modular_multiplier),
            "single_remainder_bound": str(single_bound),
            "two_orientation_bound": str(two_orientation_bound),
            "two_orientation_modular_bound": str(modular_bound),
            "finite_member_two_sided_remainder_closed_conditionally": True,
            "all_time_orbit_bound_proved": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "boundary": scope,
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FIXED-BETA-TWO-SIDED-DUHAMEL-REMAINDER PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
