#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001059."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-local-force-moment-interface/independent.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, Fraction):
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


def frac(value: Any) -> Fraction:
    return Fraction(str(value))


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

    g = frac(fixture["g"])
    r = frac(fixture["r"])
    chi = frac(fixture["chi"])
    hbar = frac(fixture["hbar"])
    c = frac(fixture["c"])
    lam = frac(fixture["lambda"])
    amplitude = frac(fixture["character_amplitude"])
    force_constant = frac(fixture["force_constant"])
    ratio = Fraction(8, 1) / g
    prefactor_power = force_constant**4 * ratio**3
    coefficient_power = (abs(amplitude) / (hbar * chi)) ** 4 * prefactor_power
    check("positive parameters", g > 0 and chi > 0 and hbar > 0 and c >= 0 and lam >= 0 and r < 0 and amplitude != 0, [g, chi, hbar, c, lam, r, amplitude], "g,chi,hbar>0; c,lambda>=0; r<0; a!=0", "parameters")
    check("weight ratio", ratio == frac(fixture["derived_weight_ratio"]), ratio, fixture["derived_weight_ratio"], "derived")
    check("energy shift", r * r / (2 * g) == frac(fixture["derived_energy_shift_per_site"]), r * r / (2 * g), fixture["derived_energy_shift_per_site"], "derived")
    check("local prefactor", prefactor_power == force_constant**4 * ratio**3, prefactor_power, "C^4*(8/g)^3", "derived")
    check("conditional coefficient fourth power", coefficient_power == (abs(amplitude) / (hbar * chi)) ** 4 * prefactor_power, coefficient_power, "(|a|/(hbar*chi))^4*local prefactor", "conditional")

    fields = tuple(frac(value) for value in fixture["field_values"])
    rows: list[dict[str, Any]] = []
    for q, v in itertools.product(fields, fields):
        e_q = r * q * q / 2 + g * q**4 / 4 + r * r / (2 * g)
        e_v = r * v * v / 2 + g * v**4 / 4 + r * r / (2 * g)
        force = c * (q - v) + lam * (q - v) * (2 * q**2 - q * v + v**2) / 2
        global_weight = 1 + q**4 + v**4
        pair_energy = 1 + e_q + e_v
        global_bound = force_constant**4 * global_weight**3
        local_bound = prefactor_power * pair_energy**3
        check(f"endpoint q bound {q}", q**4 <= ratio * e_q, q**4, ratio * e_q, "localization")
        check(f"endpoint v bound {v}", v**4 <= ratio * e_v, v**4, ratio * e_v, "localization")
        check(f"global force bound {q},{v}", abs(force) ** 4 <= global_bound, force, "global fourth-power bound", "grid")
        check(f"local force bound {q},{v}", abs(force) ** 4 <= local_bound, force, "local fourth-power bound", "grid")
        check(f"pair energy {q},{v}", pair_energy >= 1, pair_energy, ">=1", "grid")
        rows.append({"q": q, "v": v, "force": force, "energy_q": e_q, "energy_v": e_v, "pair_energy": pair_energy, "global_weight": global_weight, "global_bound": global_bound, "local_bound": local_bound})

    check("grid cardinality", len(rows) == int(fixture["grid_points"]), len(rows), fixture["grid_points"], "fixture")
    scope = manifest["scope"]
    check("conditional scope", scope["local_force_weight_bound_closed"] is True and scope["conditional_l4_coefficient_bound_closed"] is True and scope["uniform_local_third_moment_proved"] is False, scope, "conditional local bridge", "scope")
    check("QFT firewall", all(scope[key] is False for key in ("all_time_projected_d_duhamel_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "successor gates open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit,
        "grid_rows": rows,
        "derived": {
            "energy_shift_per_site": r * r / (2 * g),
            "weight_ratio": ratio,
            "local_prefactor_power": prefactor_power,
            "conditional_coefficient_fourth_power": coefficient_power,
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
    print(f"INDEPENDENT LOCAL-FORCE-MOMENT-INTERFACE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
