#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001072."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-multicharacter-uniform-duhamel-remainder"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
STATIC = REPO / "strategy/pre-a-cp1-st8-q3lock-multicharacter-static-double-commutator-bound-manifest.json"
FINITE = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-gibbs-isometric-duhamel-remainder-manifest.json"
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
    finite = json.loads(FINITE.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001072" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001072/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("finite authority", finite["exploration_id"] == "EXP-001066" and "t^2 N_beta(delta_H^2(X))/2" in finite["finite_time_theorem"]["bound"], finite["exploration_id"], "EXP-001066 finite bound", "authority")
    check("static authority", static["exploration_id"] == "EXP-001071" and static["scope"]["finite_support_static_multi_character_closed"] is True, static["exploration_id"], "EXP-001071 static multi-character bound", "authority")
    support_size = int(fixture["support_size"])
    amplitudes = tuple(frac(value) for value in fixture["amplitudes"])
    check("support cardinality", support_size == len(amplitudes) and support_size > 0, [support_size, len(amplitudes)], ">0 and equal", "parameters")
    check("support authority", support_size == int(static["finite_fixture"]["support_size"]) and list(fixture["amplitudes"]) == list(static["finite_fixture"]["amplitudes"]), [support_size, fixture["amplitudes"]], "EXP-001071 fixture", "authority")

    time = frac(fixture["time"])
    static_bound = frac(fixture["static_full_squared_norm_upper"])
    factor = time**4 / 4
    remainder_upper = factor * static_bound
    check("positive time", time > 0, time, ">0", "parameters")
    check("static bound input", static_bound == frac(static["finite_fixture"]["derived_full_squared_norm_upper"]), static_bound, static["finite_fixture"]["derived_full_squared_norm_upper"], "static")
    check("remainder factor", factor == frac(fixture["derived_remainder_factor"]), factor, fixture["derived_remainder_factor"], "scaling")
    check("remainder upper reduced", remainder_upper == frac(fixture["derived_remainder_squared_upper"]), remainder_upper, fixture["derived_remainder_squared_upper"], "scaling")
    check("remainder upper unreduced", remainder_upper == frac(fixture["derived_remainder_squared_upper_unreduced"]), remainder_upper, fixture["derived_remainder_squared_upper_unreduced"], "scaling")
    check("remainder below one", remainder_upper < 1, remainder_upper, "<1", "scaling")

    scope = manifest["scope"]
    check("finite-support closure", scope["finite_member_duhamel_remainder_reused"] is True and scope["static_multi_character_bound_reused"] is True and scope["finite_support_remainder_uniform_closed"] is True, scope, "finite-support remainder closed", "scope")
    open_keys = ("force_history_uniform_closed", "full_actual_q3_double_commutator_uniform_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")
    derived = {"support_size": support_size, "amplitudes": amplitudes, "time": time, "static_full_squared_norm_upper": static_bound, "remainder_factor": factor, "remainder_squared_upper": remainder_upper, "finite_support_remainder_uniform_closed": True, "product_core_density_closed": False, "actual_q3_factorial_history_proved": False}
    passed = len(rows)
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-MULTICHARACTER-UNIFORM-DUHAMEL-REMAINDER", "exploration_id": manifest["exploration_id"], "task_id": manifest["task_id"], "verdict": "PASS", "passed": passed, "assertion_count": passed, "assertions": rows, "derived": derived, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.output:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT MULTICHARACTER-DUHAMEL PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
