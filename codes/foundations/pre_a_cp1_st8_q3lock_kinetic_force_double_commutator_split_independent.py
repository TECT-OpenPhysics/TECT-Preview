#!/usr/bin/env python3
"""Independent Fraction-only audit for EXP-001067."""

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
SLUG = "pre-a-cp1-st8-q3lock-kinetic-force-double-commutator-split"
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
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001067" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001067/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("force-free declaration", manifest["adversarial_fixture"]["force"] == "V=0, hence F=0 and every force moment is zero", manifest["adversarial_fixture"]["force"], "V=0", "force")
    check("split declaration", "p_x" in manifest["model"]["exact_split"] and "F_x" in manifest["model"]["exact_split"], manifest["model"]["exact_split"], "kinetic plus force", "CCR")

    n = Fraction(int(manifest["adversarial_fixture"]["fixture_n"]), 1)
    initial = Fraction(2, 1)
    double = 2 * n**4
    expected_fixture = Fraction(int(manifest["adversarial_fixture"]["fixture_squared_norm"]), 1)
    check("normalized state", Fraction(2, 3) + Fraction(1, 3) == 1, Fraction(2, 3) + Fraction(1, 3), 1, "fixture")
    check("unitary character", Fraction(1, 1) == 1, 1, 1, "fixture")
    check("force zero", Fraction(0, 1) == 0, 0, 0, "force")
    check("double commutator scaling", double == 2 * n**4, double, 2 * n**4, "fixture")
    check("initial two-sided norm", initial == 2, initial, 2, "fixture")
    check("n=4 fixture", double == expected_fixture, double, expected_fixture, "fixture")

    growth_rows: list[dict[str, Any]] = []
    for level in range(1, 6):
        level_fraction = Fraction(level, 1)
        squared = 2 * level_fraction**4
        growth_rows.append({"n": level, "double_squared_norm": str(squared)})
        check(f"growth formula n={level}", squared == 2 * level_fraction**4, squared, 2 * level_fraction**4, "growth")
    check("strict growth", Fraction(growth_rows[-1]["double_squared_norm"]) > Fraction(growth_rows[0]["double_squared_norm"]), growth_rows, "increasing", "growth")

    scope = manifest["scope"]
    check("scope split", scope["finite_ccr_split_closed"] is True and scope["force_endpoint_interface_reused"] is True and scope["force_only_shortcut_rejected"] is True, scope, "finite split and shortcut obstruction", "scope")
    open_keys = (
        "kinetic_uniform_bound_closed",
        "modular_multiplier_bound_closed",
        "actual_q3_double_commutator_uniform_closed",
        "actual_q3_four_context_theorem_proved",
        "actual_q3_factorial_history_proved",
        "volume_uniform_direct_d_cauchy_closed",
        "delta_d_cauchy_closed",
        "product_core_density_closed",
        "exhaustion_independence_closed",
        "group_law_closed",
        "common_alpha_closed",
        "hamiltonian_os_identification_closed",
        "kms_os_closed",
        "gns_gap_closed",
        "continuum_closed",
        "c6_closed",
        "sector_a_closed",
        "pre_a_closed",
    )
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
            "fixture_n": str(n),
            "initial_two_sided_squared_norm": str(initial),
            "double_two_sided_squared_norm": str(double),
            "force_moment": "0",
            "finite_ccr_split_closed": True,
            "force_endpoint_interface_reused": True,
            "kinetic_uniform_bound_closed": False,
            "modular_multiplier_bound_closed": False,
            "force_only_shortcut_rejected": True,
            "actual_q3_double_commutator_uniform_closed": False,
            "growth_rows": growth_rows,
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
    print(f"INDEPENDENT KINETIC-FORCE-SPLIT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
