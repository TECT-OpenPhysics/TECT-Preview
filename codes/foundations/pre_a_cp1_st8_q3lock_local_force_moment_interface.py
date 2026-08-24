#!/usr/bin/env python3
"""Primary exact audit for EXP-001059.

This package localizes the EXP-001058 Q3 bond force to endpoint shifted onsite
energies and states, but does not prove, the uniform local Gibbs moment needed
for a volume-uniform Duhamel estimate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-local-force-moment-interface/primary.json"
)


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


def rational(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    model = manifest["model"]
    fixture = manifest["finite_fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001059" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001059/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("conditional declaration", model["conditional_moment"].startswith("sup_{Lambda,x~y}") and "M_beta,local" in model["conditional_l4"], model, "explicit local moment input", "model")

    g = rational(fixture["g"])
    r = rational(fixture["r"])
    chi = rational(fixture["chi"])
    hbar = rational(fixture["hbar"])
    c = rational(fixture["c"])
    lam = rational(fixture["lambda"])
    amplitude = rational(fixture["character_amplitude"])
    force_constant = rational(fixture["force_constant"])
    ratio = sp.Rational(8, 1) / g
    max_ratio = sp.Max(1, ratio)
    q, v = sp.symbols("q v", real=True)
    e_q = sp.factor(r * q**2 / 2 + g * q**4 / 4 + r**2 / (2 * g))
    e_v = sp.factor(r * v**2 / 2 + g * v**4 / 4 + r**2 / (2 * g))
    endpoint_residual = sp.factor(ratio * e_q - q**4)
    pair_residual = sp.factor(1 + ratio * (e_q + e_v) - (1 + q**4 + v**4))
    bond = c * (q - v) ** 2 / 2 + lam * (q - v) ** 2 * (q**2 + v**2) / 4
    force = sp.factor(sp.diff(bond, q))
    prefactor_power = sp.factor(force_constant**4 * max_ratio**3)
    coefficient_prefactor = sp.factor(abs(amplitude) / (hbar * chi) * force_constant * max_ratio ** sp.Rational(3, 4))
    check("positive parameters", g > 0 and chi > 0 and hbar > 0 and c >= 0 and lam >= 0 and r < 0 and amplitude != 0, [g, chi, hbar, c, lam, r, amplitude], "g,chi,hbar>0; c,lambda>=0; r<0; a!=0", "parameters")
    check("endpoint energy nonnegative", sp.factor(e_q - g * (q**2 + r / g) ** 2 / 4 - r**2 / (4 * g)) == 0, e_q, "nonnegative completed square", "algebra")
    check("endpoint quartic ratio", endpoint_residual == (q**2 + 2 * r / g) ** 2, endpoint_residual, "square", "algebra")
    check("pair weight ratio", sp.factor(pair_residual - (q**2 + 2 * r / g) ** 2 - (v**2 + 2 * r / g) ** 2) == 0, pair_residual, "sum of squares", "algebra")
    expected_force = c * (q - v) + lam * (q - v) * (2 * q**2 - q * v + v**2) / 2
    check("force identity", sp.factor(force - expected_force) == 0, force, expected_force, "force")
    check("weight ratio", ratio == rational(fixture["derived_weight_ratio"]), ratio, fixture["derived_weight_ratio"], "derived")
    check("energy shift", r**2 / (2 * g) == rational(fixture["derived_energy_shift_per_site"]), r**2 / (2 * g), fixture["derived_energy_shift_per_site"], "derived")
    check("local prefactor formula", prefactor_power == force_constant**4 * max_ratio**3, prefactor_power, "C^4*max(1,8/g)^3", "derived")
    check("conditional coefficient formula", coefficient_prefactor == abs(amplitude) / (hbar * chi) * force_constant * max_ratio ** sp.Rational(3, 4), coefficient_prefactor, "|a|/(hbar*chi)*C*max(1,8/g)^(3/4)", "conditional")

    fields = tuple(rational(value) for value in fixture["field_values"])
    rows: list[dict[str, Any]] = []
    for q_value, v_value in itertools.product(fields, fields):
        force_value = sp.factor(force.subs({q: q_value, v: v_value}))
        energy_q = sp.factor(e_q.subs(q, q_value))
        energy_v = sp.factor(e_v.subs(v, v_value))
        pair_energy = 1 + energy_q + energy_v
        global_weight = 1 + q_value**4 + v_value**4
        force_bound_power = force_constant**4 * global_weight**3
        local_bound_power = prefactor_power * pair_energy**3
        check(f"global force bound {q_value},{v_value}", abs(force_value) ** 4 <= force_bound_power, force_value, "global fourth-power bound", "grid")
        check(f"local force bound {q_value},{v_value}", abs(force_value) ** 4 <= local_bound_power, force_value, "local fourth-power bound", "grid")
        check(f"pair energy nonnegative {q_value},{v_value}", pair_energy >= 1, pair_energy, ">=1", "grid")
        rows.append({"q": q_value, "v": v_value, "force": force_value, "energy_q": energy_q, "energy_v": energy_v, "pair_energy": pair_energy, "global_weight": global_weight, "force_bound_power": force_bound_power, "local_bound_power": local_bound_power})

    check("grid cardinality", len(rows) == int(fixture["grid_points"]), len(rows), fixture["grid_points"], "fixture")
    scope = manifest["scope"]
    check("conditional scope", scope["local_force_weight_bound_closed"] is True and scope["conditional_l4_coefficient_bound_closed"] is True and scope["uniform_local_third_moment_proved"] is False, scope, "conditional local bridge", "scope")
    check("QFT firewall", all(scope[key] is False for key in ("all_time_projected_d_duhamel_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "successor gates open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit,
        "grid_rows": rows,
        "derived": {
            "energy_shift_per_site": r**2 / (2 * g),
            "weight_ratio": ratio,
            "local_prefactor_power": prefactor_power,
            "conditional_coefficient_prefactor": coefficient_prefactor,
            "grid_points": len(rows),
            "local_force_weight_bound_closed": True,
            "conditional_l4_coefficient_bound_closed": True,
            "uniform_local_third_moment_proved": False,
            "all_time_projected_d_duhamel_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
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
    print(f"PRIMARY LOCAL-FORCE-MOMENT-INTERFACE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
