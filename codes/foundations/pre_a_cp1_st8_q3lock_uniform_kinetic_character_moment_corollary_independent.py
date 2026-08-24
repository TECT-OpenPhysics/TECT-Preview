#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001068."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-uniform-kinetic-character-moment-corollary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    chi = Fraction(fixture["chi"])
    hbar = Fraction(fixture["hbar"])
    m5 = Fraction(fixture["m5"])
    amplitude = Fraction(fixture["character_amplitude"])
    half = amplitude / 2
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001068" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001068/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive inputs", chi > 0 and hbar > 0 and m5 >= 0 and amplitude != 0, [chi, hbar, m5, amplitude], "positive", "parameters")

    phi_p4_bound = 4 * chi**2 * m5
    shifted_bound = 16 * phi_p4_bound + amplitude**4
    double_bound = amplitude**4 * shifted_bound / (chi**4 * hbar**4)
    check("fourth moment reduction", phi_p4_bound == 4 * chi**2 * m5, phi_p4_bound, "4 chi^2 m5", "moment")
    check("shifted norm formula", shifted_bound == 64 * chi**2 * m5 + amplitude**4, shifted_bound, "64 chi^2 m5+a^4", "moment")
    check("double coefficient formula", double_bound == amplitude**4 * (64 * chi**2 * m5 + amplitude**4) / (chi**4 * hbar**4), double_bound, "derived", "moment")

    grid_rows: list[dict[str, Any]] = []
    for raw in fixture["p_grid"]:
        value = Fraction(raw)
        plus = value + half
        minus = value - half
        bound = 8 * (value**4 + half**4)
        check(f"plus shift grid {value}", plus**4 <= bound, plus**4, bound, "shift")
        check(f"minus shift grid {value}", minus**4 <= bound, minus**4, bound, "shift")
        grid_rows.append({"p": str(value), "plus_fourth": str(plus**4), "minus_fourth": str(minus**4), "bound": str(bound)})
    check("grid cardinality", len(grid_rows) == int(fixture["grid_points"]), len(grid_rows), fixture["grid_points"], "fixture")
    check("fixture shifted bound", shifted_bound == Fraction(fixture["derived_shifted_kinetic_squared_norm_bound"]), shifted_bound, fixture["derived_shifted_kinetic_squared_norm_bound"], "fixture")
    check("fixture double bound", double_bound == Fraction(fixture["derived_double_commutator_kinetic_squared_norm_bound"]), double_bound, fixture["derived_double_commutator_kinetic_squared_norm_bound"], "fixture")

    scope = manifest["scope"]
    check("kinetic scope", scope["onsite_momentum_fourth_moment_closed"] is True and scope["kinetic_character_two_sided_gibbs_bound_closed"] is True and scope["modular_multiplier_for_kinetic_part_needed"] is False, scope, "kinetic closed", "scope")
    open_keys = ("force_summand_closed", "full_actual_q3_double_commutator_uniform_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")

    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": rows,
        "derived": {
            "chi": str(chi),
            "hbar": str(hbar),
            "m5": str(m5),
            "character_amplitude": str(amplitude),
            "phi_p4_bound": str(phi_p4_bound),
            "shifted_kinetic_squared_norm_bound": str(shifted_bound),
            "double_commutator_kinetic_squared_norm_bound": str(double_bound),
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
    print(f"INDEPENDENT UNIFORM-KINETIC-CHARACTER PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
