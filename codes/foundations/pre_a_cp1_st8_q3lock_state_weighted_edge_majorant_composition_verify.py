#!/usr/bin/env python3
"""Integrated verifier for the EXP-001320 state-weighted edge interface."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_state_weighted_edge_majorant_composition.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_state_weighted_edge_majorant_composition_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_state_weighted_edge_majorant_composition_hostile.py"
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-state-weighted-edge-majorant-composition-manifest.json"
DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-30-integrated-pre_a_cp1_st8_q3lock_state_weighted_edge_majorant_composition/integrated.json"
)


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def run_child(path: Path, output: Path) -> tuple[int, str, dict[str, Any] | None]:
    completed = subprocess.run(
        [sys.executable, str(path), "--output", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    payload = None
    if completed.returncode == 0 and output.is_file():
        payload = json.loads(output.read_text(encoding="utf-8"))
    return completed.returncode, (completed.stdout + "\n" + completed.stderr).strip(), payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    args = parser.parse_args()
    packet = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    with tempfile.TemporaryDirectory(prefix="tect-exp001320-") as temporary:
        temp = Path(temporary)
        primary_code, primary_text, primary = run_child(PRIMARY, temp / "primary.json")
        independent_code, independent_text, independent = run_child(INDEPENDENT, temp / "independent.json")
        hostile_code, hostile_text, hostile = run_child(HOSTILE, temp / "hostile.json")
        check("primary child", primary_code == 0 and primary is not None, primary_text[-300:], "exit 0 and JSON")
        check("independent child", independent_code == 0 and independent is not None, independent_text[-300:], "exit 0 and JSON")
        check("hostile child", hostile_code == 0 and hostile is not None, hostile_text[-300:], "exit 0 and JSON")

        assert primary is not None and independent is not None and hostile is not None
        check("verdict agreement", primary["verdict"] == independent["verdict"] == hostile["verdict"] == "PASS", [primary["verdict"], independent["verdict"], hostile["verdict"]], "PASS")
        for key in ("force_constant", "g", "D", "A0", "m5", "C0", "M_bridge", "C4_edge"):
            check(f"derived agreement {key}", primary["derived"][key] == independent["derived"][key], [primary["derived"][key], independent["derived"][key]], "equal")
        check("hostile mutation coverage", hostile["mutation_count"] == 8 and len(hostile["mutations_rejected"]) == 8, hostile["mutation_count"], 8)

    # The composition reuses two already compiled Lean authorities.  This
    # package adds no new Lean entrypoint, so the integrated lane checks that
    # the cited source files and manifest bridges are present and leaves
    # compilation to their existing R242/R445 verification records.
    for relative in ("verification/lean/Tect/R242.lean", "verification/lean/Tect/R445.lean"):
        check(f"Lean parent source {relative}", (ROOT / relative).is_file(), relative, "file exists")
    lean_refs = packet["verification"]["lean_parent_crosschecks"]
    check("Lean parent references", set(lean_refs) == {"verification/lean/Tect/R242.lean", "verification/lean/Tect/R445.lean"}, lean_refs, "R242 and R445")
    check("scope firewall", packet["scope"]["actual_q3_operator_norm_majorant_closed"] is False and packet["scope"]["common_alpha_closed"] is False, packet["scope"], "operator/common-alpha false")
    check("method preserved", packet["formal_integration"]["no_tier_change"] is True and "established research method" in " ".join(packet["non_claims"]), packet["formal_integration"]["no_tier_change"], True)

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-EDGE-MAJORANT-COMPOSITION",
        "claim_id": packet["claim_ids"][0],
        "task_id": packet["task_id"],
        "exploration_id": packet["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "primary_independent_agree": True,
            "hostile_mutations_rejected": 8,
            "lean_parent_sources_present": True,
            "lean_parent_compilation_authorities": ["R242", "R445"],
            "conditional_state_weighted_edge_majorant_closed": True,
            "actual_q3_operator_norm_majorant_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "boundary": packet["boundary"],
        "assumptions": packet["assumptions"],
        "missing_assumptions": packet["missing_assumptions"],
        "evidence_level": packet["evidence_level"],
        "non_claims": packet["non_claims"],
    }
    store(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INTEGRATED STATE-WEIGHTED-EDGE-MAJORANT PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
