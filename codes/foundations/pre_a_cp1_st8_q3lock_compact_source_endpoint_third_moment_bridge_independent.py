#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001061.

This lane does not import SymPy or the primary script.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge/independent.json"
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
    g = Fraction(fixture["g"])
    r = Fraction(fixture["r"])
    gamma = Fraction(fixture["gamma"])
    m5 = Fraction(fixture["m5"])
    a_gamma = g / (4 * gamma)
    A_r = r * r / (2 * g)
    C0 = 1 + 2 * A_r
    M_bridge = 9 * (C0**3 + 2 * a_gamma**3 * m5)

    check("identity", manifest["exploration_id"] == "EXP-001061" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001061/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("parameter signs", g > 0 and r < 0 and gamma > 0 and gamma < g / 32 and m5 >= 0, [g, r, gamma, m5], "g>0,r<0,0<gamma<g/32,m5>=0")
    check("coefficient derivation", 4 * gamma * a_gamma == g, 4 * gamma * a_gamma, g)
    check("shift derivation", 2 * g * A_r == r * r, 2 * g * A_r, r * r)

    q_values = tuple(Fraction(value) for value in fixture["field_values"])
    form_checks = 0
    for q in q_values:
        endpoint = r * q * q / 2 + g * q**4 / 4 + A_r
        k_lower = 1 + gamma * q**4
        rhs = a_gamma * k_lower + A_r
        check(f"endpoint form {form_checks}", endpoint <= rhs, endpoint, rhs)
        check(f"endpoint nonnegative {form_checks}", endpoint >= 0, endpoint, ">=0")
        form_checks += 1

    test_values = (0, 1, 2, 5, 10)
    cube_checks = 0
    for c_value in test_values:
        for x_value in test_values:
            for y_value in test_values:
                lhs = (c_value + x_value + y_value) ** 3
                rhs = 9 * (c_value**3 + x_value**3 + y_value**3)
                check(f"cube majorant {cube_checks}", lhs <= rhs, lhs, rhs)
                cube_checks += 1

    for index, value in enumerate((1, 2, 5, 10)):
        check(f"fifth dominates third {index}", value**3 <= value**5, value**3, value**5)

    for index, (kx, ky) in enumerate(((1, 1), (2, 5), (10, 2))):
        upper = C0 + a_gamma * (kx + ky)
        rhs = 9 * (C0**3 + a_gamma**3 * kx**3 + a_gamma**3 * ky**3)
        check(f"endpoint upper cube {index}", upper**3 <= rhs, upper**3, rhs)

    check("fixture a_gamma", str(a_gamma) == fixture["derived_a_gamma"], a_gamma, fixture["derived_a_gamma"])
    check("fixture A_r", str(A_r) == fixture["derived_A_r"], A_r, fixture["derived_A_r"])
    check("fixture C0", str(C0) == fixture["derived_C0"], C0, fixture["derived_C0"])
    check("fixture bridge", str(M_bridge) == fixture["derived_M_bridge_compact"], M_bridge, fixture["derived_M_bridge_compact"])

    scope = manifest["scope"]
    check("compact-source bridge scope", scope["compact_source_endpoint_third_moment_bridge_closed"] is True and scope["registered_periodic_compact_source_scope_only"] is True, scope, "registered compact-source bridge")
    check("QFT firewall", all(scope[key] is False for key in ("all_time_projected_d_duhamel_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "successor gates open")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-COMPACT-SOURCE-ENDPOINT-THIRD-MOMENT-BRIDGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "g": str(g),
            "r": str(r),
            "gamma": str(gamma),
            "m5": str(m5),
            "a_gamma": str(a_gamma),
            "A_r": str(A_r),
            "C0": str(C0),
            "M_bridge_compact": str(M_bridge),
            "form_grid_points": form_checks,
            "cube_grid_points": cube_checks,
            "compact_source_endpoint_third_moment_bridge_closed": True,
            "arbitrary_boundary_extension_closed": False,
            "all_time_projected_d_duhamel_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "boundary": scope,
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT COMPACT-SOURCE-ENDPOINT-BRIDGE PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
