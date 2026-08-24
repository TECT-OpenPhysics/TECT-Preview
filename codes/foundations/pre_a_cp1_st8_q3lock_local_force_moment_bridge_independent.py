#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001060.

No SymPy or primary-script imports are used in this lane.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-local-force-moment-bridge/independent.json"
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    fixture = manifest["finite_fixture"]
    A0 = Fraction(fixture["A0_input"])
    m5 = Fraction(fixture["m5_input"])
    base_energy = 1
    endpoint_count = 2
    cube_terms = 3
    cube_power = 3
    cube_constant = cube_terms ** (cube_power - 1)
    C0 = base_energy + endpoint_count * A0
    M_bridge = cube_constant * (C0**cube_power + endpoint_count * m5)

    check("identity", manifest["exploration_id"] == "EXP-001060" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001060/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("nonnegative inputs", A0 >= 0 and m5 >= 0, [A0, m5], "A0,m5>=0")
    check("cube constant derived", cube_constant == 9, cube_constant, "3^(3-1)")

    test_values = (0, 1, 2, 5, 10)
    cube_checks = 0
    for c_value in test_values:
        for x_value in test_values:
            for y_value in test_values:
                lhs = (c_value + x_value + y_value) ** cube_power
                rhs = cube_constant * (c_value**cube_power + x_value**cube_power + y_value**cube_power)
                check(f"cube majorant {cube_checks}", lhs <= rhs, lhs, rhs)
                cube_checks += 1

    for index, value in enumerate((1, 2, 5, 10)):
        check(f"fifth dominates third {index}", value**3 <= value**5, value**3, value**5)

    for index, (kx, ky) in enumerate(((1, 1), (2, 5), (10, 2))):
        E_upper = C0 + kx + ky
        rhs = cube_constant * (C0**cube_power + kx**3 + ky**3)
        check(f"endpoint upper cube {index}", E_upper**3 <= rhs, E_upper**3, rhs)

    check("fixture C0", str(C0) == fixture["derived_C0"], C0, fixture["derived_C0"])
    check("fixture bridge", str(M_bridge) == fixture["derived_M_bridge"], M_bridge, fixture["derived_M_bridge"])
    scope = manifest["scope"]
    check("bridge scope", scope["endpoint_third_moment_bridge_closed"] is True and scope["registered_periodic_zero_source_scope_only"] is True, scope, "registered bridge closed")
    check("QFT firewall", all(scope[key] is False for key in ("all_time_projected_d_duhamel_cauchy_closed", "delta_d_cauchy_closed", "exhaustion_independence_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "successor gates open")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-FORCE-MOMENT-BRIDGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "A0": str(A0),
            "m5": str(m5),
            "cube_constant": str(cube_constant),
            "C0": str(C0),
            "M_bridge": str(M_bridge),
            "endpoint_count": str(endpoint_count),
            "cube_grid_points": cube_checks,
            "endpoint_third_moment_bridge_closed": True,
            "compact_source_uniform_shift_closed": False,
            "all_time_projected_d_duhamel_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "boundary": scope,
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT LOCAL-FORCE-MOMENT-BRIDGE PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
