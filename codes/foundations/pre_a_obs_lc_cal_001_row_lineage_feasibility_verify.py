#!/usr/bin/env python3
"""Integrate primary, independent, hostile, and inverse-contract checks for R-446."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_obs_lc_cal_001_row_lineage_feasibility.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_obs_lc_cal_001_row_lineage_feasibility_independent.py"
HOSTILE = REPO / "codes/foundations/pre_a_obs_lc_cal_001_row_lineage_feasibility_hostile.py"
INVERSE_CHECK = REPO / "verification/scripts/check_obs_inverse.py"
MANIFEST = REPO / "strategy/obs-lc-cal-001-row-lineage-feasibility-manifest-v0.1.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-obs_lc_cal_001_row_lineage_feasibility/integrated.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=REPO, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check("manifest identity", [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing")] == ["R-446", "EXP-001298", "T-061", False], [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing")], "R-446/EXP-001298/T-061/false", "provenance")
    check("manifest method firewall", manifest.get("checks", {}).get("methods_unchanged") is True, manifest.get("checks", {}).get("methods_unchanged"), True, "scope")
    with tempfile.TemporaryDirectory(prefix="r446-integrated-") as temporary:
        root = Path(temporary)
        primary_output = root / "primary.json"
        independent_output = root / "independent.json"
        hostile_output = root / "hostile.json"
        primary_process = command([sys.executable, "-X", "utf8", str(PRIMARY), "--output", str(primary_output)])
        independent_process = command([sys.executable, "-X", "utf8", str(INDEPENDENT), "--output", str(independent_output)])
        hostile_process = command([sys.executable, "-X", "utf8", str(HOSTILE), "--output", str(hostile_output)])
        primary = json.loads(primary_output.read_text(encoding="utf-8"))
        independent = json.loads(independent_output.read_text(encoding="utf-8"))
        hostile = json.loads(hostile_output.read_text(encoding="utf-8"))
        check("primary executable", primary_process.returncode == 0 and primary.get("verdict") == "FROZEN_LINEAGE_FEASIBILITY_INTERFACE_AUDITED", primary_process.stdout + primary_process.stderr, "audited", "executables")
        check("independent executable", independent_process.returncode == 0 and independent.get("verdict") == "INDEPENDENT_FROZEN_LINEAGE_FEASIBILITY_INTERFACE_CONTROL", independent_process.stdout + independent_process.stderr, "control", "executables")
        check("hostile executable", hostile_process.returncode == 0 and hostile.get("verdict") == "HOSTILE_LINEAGE_FEASIBILITY_MUTATIONS_REJECTED", hostile_process.stdout + hostile_process.stderr, "mutations rejected", "executables")
        for key in ("row_count", "source_hash_pinned", "likelihood_admitted", "covariance_admitted", "candidate_map_admitted", "candidate_scoring_performed"):
            check(f"primary/independent agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal", "crosscheck")
        check("dimension agreement", [primary["derived"]["operator_dimension_min"], primary["derived"]["operator_dimension_max"]] == [min(independent["derived"]["operator_dimensions"]), max(independent["derived"]["operator_dimensions"])], [primary["derived"]["operator_dimension_min"], primary["derived"]["operator_dimension_max"]], "3-9", "crosscheck")
        check("hostile count", hostile.get("mutations_rejected") == hostile.get("assertion_count") == 8, hostile.get("mutations_rejected"), 8, "hostile")
        inverse_process = command([sys.executable, "-X", "utf8", str(INVERSE_CHECK), "--self-test"])
        check("inverse contract self-test", inverse_process.returncode == 0 and "PASS" in inverse_process.stdout, inverse_process.stdout + inverse_process.stderr, "OBS-INVERSE self-test PASS", "inverse")
        check("primary authority hashes", all(len(value) == 64 for value in primary.get("source_hashes", {}).values()), primary.get("source_hashes"), "sha256 map", "provenance")

    payload: dict[str, Any] = {
        "schema": "tect/obs-lc-cal-001-row-lineage-feasibility-integrated/1.0",
        "run_kind": "integrated",
        "result_id": "R-446",
        "exploration_id": "EXP-001298",
        "task_id": "T-061",
        "verdict": "INTEGRATED_FROZEN_LINEAGE_FEASIBILITY_INTERFACE_AUDITED",
        "assertion_count": len(checks),
        "assertions": checks,
        "scope": {
            "primary": True,
            "independent": True,
            "hostile": True,
            "inverse_contract": True,
            "candidate_scoring": False,
            "method_overhaul": False,
        },
        "source_hashes": {path.relative_to(REPO).as_posix(): sha256(path) for path in (SCRIPT, PRIMARY, INDEPENDENT, HOSTILE, INVERSE_CHECK, MANIFEST)},
        "evidence_level": "T0 source-lineage plus pre-registered finite feasibility-interface integrated audit",
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    destination = args.output if args.output.is_absolute() else REPO / args.output
    atomic_json(destination, payload)
    print(f"R-446 INTEGRATED {payload['verdict']} {len(checks)}/{len(checks)}")
    if args.self_test:
        assert payload["scope"]["primary"] and payload["scope"]["independent"] and payload["scope"]["hostile"]
        print("R-446 INTEGRATED SELFTEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
