#!/usr/bin/env python3
"""Integrate primary, independent, and hostile Sector-A frontier audits.

The verifier executes the three additive metadata checks in isolated output
files and compares their source-derived contracts.  Lean is deliberately not
invoked: this checkpoint introduces no mathematical proposition, only a
reader/dependency index and fail-closed mutation tests.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PRIMARY = REPO / "verification" / "scripts" / "sector_a_frontier_audit.py"
INDEPENDENT = REPO / "codes" / "foundations" / "sector_a_frontier_audit_independent.py"
HOSTILE = REPO / "codes" / "foundations" / "sector_a_frontier_audit_hostile.py"
PROGRAMME = REPO / "strategy" / "main-proof-program-v1.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A5-SECTOR-A-SYNTHESIS"
    / "runs"
    / "2026-08-31-sector-a-frontier-audit"
    / "integrated.json"
)
AUDIT_ID = "SECTOR-A-FRONTIER-AUDIT-INTEGRATED-v1"
EXPLORATION_ID = "EXP-001351"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run_checker(script: Path, output: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output), "--self-test"],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    report = load_json(output) if output.exists() else {}
    return {
        "script": str(script.relative_to(REPO)).replace("\\", "/"),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "report": report,
    }


def primary_projection(report: dict[str, Any]) -> dict[str, Any]:
    snapshot = report.get("authority_snapshot", {})
    rows = snapshot.get("status_cards", [])
    return {
        "ids": sorted(row.get("id") for row in rows),
        "dependencies": {
            row.get("id"): sorted(
                set(row.get("dependencies", [])) | set(row.get("soft_dependencies", []))
            )
            for row in rows
        },
        "open_gate_union": sorted(report.get("frontier", {}).get("open_gate_union", [])),
        "a5_dependencies": sorted(report.get("frontier", {}).get("a5_dependencies", [])),
    }


def build_report() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="sector-a-frontier-") as temporary_dir:
        temporary = Path(temporary_dir)
        primary_run = run_checker(PRIMARY, temporary / "primary.json")
        independent_run = run_checker(INDEPENDENT, temporary / "independent.json")
        hostile_run = run_checker(HOSTILE, temporary / "hostile.json")

    primary_report = primary_run["report"]
    independent_report = independent_run["report"]
    hostile_report = hostile_run["report"]
    p_projection = primary_projection(primary_report)
    i_core = independent_report.get("core", {})
    programme = load_json(PROGRAMME)
    lanes = programme.get("lanes", {})
    lane_contract_ok = {
        "forward": {
            "task_id": lanes.get("forward", {}).get("task_id"),
            "science_gate": lanes.get("forward", {}).get("science_gate"),
        },
        "inverse": {
            "task_id": lanes.get("inverse", {}).get("task_id"),
            "science_gate": lanes.get("inverse", {}).get("science_gate"),
        },
    }
    assertions = [
        {
            "name": "primary checker exits successfully",
            "status": "PASS" if primary_run["returncode"] == 0 else "FAIL",
            "actual": primary_run["returncode"],
            "expected": 0,
        },
        {
            "name": "independent checker exits successfully",
            "status": "PASS" if independent_run["returncode"] == 0 else "FAIL",
            "actual": independent_run["returncode"],
            "expected": 0,
        },
        {
            "name": "hostile checker exits successfully",
            "status": "PASS" if hostile_run["returncode"] == 0 else "FAIL",
            "actual": hostile_run["returncode"],
            "expected": 0,
        },
        {
            "name": "primary verdict is open-gate pass",
            "status": "PASS"
            if primary_report.get("verdict") == "SECTOR_A_FRONTIER_AUDIT_PASS_OPEN_GATES"
            else "FAIL",
            "actual": primary_report.get("verdict"),
            "expected": "SECTOR_A_FRONTIER_AUDIT_PASS_OPEN_GATES",
        },
        {
            "name": "independent verdict passes",
            "status": "PASS"
            if independent_report.get("verdict") == "SECTOR_A_FRONTIER_INDEPENDENT_PASS"
            else "FAIL",
            "actual": independent_report.get("verdict"),
            "expected": "SECTOR_A_FRONTIER_INDEPENDENT_PASS",
        },
        {
            "name": "hostile verdict rejects every mutation",
            "status": "PASS"
            if hostile_report.get("verdict") == "HOSTILE_MUTATIONS_REJECTED"
            else "FAIL",
            "actual": hostile_report.get("verdict"),
            "expected": "HOSTILE_MUTATIONS_REJECTED",
        },
        {
            "name": "primary and independent ids agree",
            "status": "PASS" if p_projection["ids"] == i_core.get("sector_a_ids") else "FAIL",
            "actual": p_projection["ids"],
            "expected": i_core.get("sector_a_ids"),
        },
        {
            "name": "primary and independent dependencies agree",
            "status": "PASS"
            if p_projection["dependencies"] == i_core.get("dependencies")
            else "FAIL",
            "actual": p_projection["dependencies"],
            "expected": i_core.get("dependencies"),
        },
        {
            "name": "primary and independent open gates agree",
            "status": "PASS"
            if p_projection["open_gate_union"] == i_core.get("open_gate_union")
            else "FAIL",
            "actual": p_projection["open_gate_union"],
            "expected": i_core.get("open_gate_union"),
        },
        {
            "name": "primary and independent A5 dependencies agree",
            "status": "PASS"
            if p_projection["a5_dependencies"] == i_core.get("a5_dependencies")
            else "FAIL",
            "actual": p_projection["a5_dependencies"],
            "expected": i_core.get("a5_dependencies"),
        },
        {
            "name": "independent lane contract matches programme",
            "status": "PASS"
            if lane_contract_ok == i_core.get("lane_contract")
            else "FAIL",
            "actual": lane_contract_ok,
            "expected": i_core.get("lane_contract"),
        },
        {
            "name": "all primary assertions pass",
            "status": "PASS"
            if primary_report.get("assertion_summary", {}).get("passed")
            == primary_report.get("assertion_summary", {}).get("total")
            else "FAIL",
            "actual": primary_report.get("assertion_summary"),
            "expected": "passed equals total",
        },
        {
            "name": "all independent assertions pass",
            "status": "PASS"
            if independent_report.get("assertion_summary", {}).get("passed")
            == independent_report.get("assertion_summary", {}).get("total")
            else "FAIL",
            "actual": independent_report.get("assertion_summary"),
            "expected": "passed equals total",
        },
        {
            "name": "hostile mutation summary is fully rejected",
            "status": "PASS"
            if hostile_report.get("mutation_summary", {}).get("rejected")
            == hostile_report.get("mutation_summary", {}).get("total")
            else "FAIL",
            "actual": hostile_report.get("mutation_summary"),
            "expected": "rejected equals total",
        },
        {
            "name": "independent and hostile source fingerprints agree",
            "status": "PASS"
            if i_core.get("core_fingerprint")
            == hostile_report.get("base_core_fingerprint")
            else "FAIL",
            "actual": hostile_report.get("base_core_fingerprint"),
            "expected": i_core.get("core_fingerprint"),
        },
    ]
    passed = sum(item["status"] == "PASS" for item in assertions)
    return {
        "schema": "tect/sector-a-frontier-audit-integrated/1.0",
        "schema_version": "1.0",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": "T-054",
        "claim_context": ["A5-SECTOR-A-SYNTHESIS"],
        "tier": "T0",
        "claim_bearing": False,
        "verdict": "SECTOR_A_FRONTIER_INTEGRATED_PASS"
        if passed == len(assertions)
        else "SECTOR_A_FRONTIER_INTEGRATED_FAIL",
        "evidence_level": "T0 integrated primary/independent/hostile metadata audit",
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "checkers": {
            "primary": {key: value for key, value in primary_run.items() if key != "report"},
            "independent": {key: value for key, value in independent_run.items() if key != "report"},
            "hostile": {key: value for key, value in hostile_run.items() if key != "report"},
        },
        "core_fingerprint": i_core.get("core_fingerprint"),
        "lean": {
            "applicable": False,
            "reason": "No mathematical proposition was introduced; this checkpoint audits metadata, dependencies, and fail-closed mutations only.",
        },
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "missing_assumptions": [
            "Source authorities and programme lane declarations remain the canonical inputs.",
            "Analytic owner, common-core, uniform-limit, and physical-sector obligations remain open where declared.",
        ],
        "non_claims": [
            "No existing research method, owner order, claim tier, or gate is changed.",
            "No A6-A13 gate is closed; no theorem, continuum, physical, QFT, Yang--Mills, or mass-gap result is claimed.",
            "Lean is not a substitute for future mathematical formalisation when a proposition is introduced.",
        ],
        "boundary": "Integration of three finite metadata checks for planning continuity; it is not proof completion.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true", help="assert integrated agreement")
    args = parser.parse_args()
    report = build_report()
    atomic_write(args.output, report)
    if report["verdict"] != "SECTOR_A_FRONTIER_INTEGRATED_PASS":
        print("SECTOR-A-FRONTIER-INTEGRATED: FAIL")
        return 1
    print(
        "SECTOR-A-FRONTIER-INTEGRATED: PASS "
        f"(assertions={report['assertion_summary']['passed']}/"
        f"{report['assertion_summary']['total']}; "
        f"fingerprint={report['core_fingerprint']}; lean_applicable=false)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
