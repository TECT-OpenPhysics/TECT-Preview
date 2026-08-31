#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean check for R-471."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/p1-owner-map-admission-contract-v0.1.json"
PRIMARY = REPO / "codes/foundations/p1_owner_map_admission_contract.py"
INDEPENDENT = REPO / "codes/foundations/p1_owner_map_admission_contract_independent.py"
HOSTILE = REPO / "codes/foundations/p1_owner_map_admission_contract_hostile.py"
LEAN = REPO / "verification/lean/Tect/R471.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-integrated-p1-owner-map-admission/integrated.json"
)
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path) -> str:
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


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R471.lean", "output": "pinned lake executable not found"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R471.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    return {
        "status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "command": "lake env lean Tect/R471.lean",
        "returncode": process.returncode,
        "output": output[-2000:],
    }


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run(
        [str(PYTHON), "-X", "utf8", str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def run(output: Path = DEFAULT_OUTPUT, skip_lean: bool = False) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    with tempfile.TemporaryDirectory(prefix="p1-owner-map-admission-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        hostile_process, hostile = child(HOSTILE, Path(temporary) / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "PASS", hostile_process.stdout + hostile_process.stderr, "PASS")
        check("current state agreement", primary.get("current_state") == independent.get("current_state") == "EMPTY_OWNER_ARTIFACT", [primary.get("current_state"), independent.get("current_state")], "EMPTY_OWNER_ARTIFACT")
        check("synthetic firewall agreement", primary.get("synthetic_fixture_state") == independent.get("synthetic_fixture_state") == "CONTRACT_TEST_ONLY_COMPLETE", [primary.get("synthetic_fixture_state"), independent.get("synthetic_fixture_state")], "CONTRACT_TEST_ONLY_COMPLETE")
        check("production admission empty", primary.get("production_admission") == independent.get("production_admission") == hostile.get("production_admission") == "NONE", [primary.get("production_admission"), independent.get("production_admission"), hostile.get("production_admission")], "NONE")
        check("methods unchanged", primary.get("methods_unchanged") is True and independent.get("methods_unchanged") is True and hostile.get("methods_unchanged") is True, True, True)
        check("hostile mutations exercised", hostile.get("all_mutations_rejected") is True and hostile.get("mutation_count", 0) > 0, hostile.get("mutation_count"), "positive mutation count")
        check("child assertion counts positive", all(item.get("assertion_count", 0) > 0 for item in (primary, independent, hostile)), [item.get("assertion_count") for item in (primary, independent, hostile)], "positive")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R471.lean"} if skip_lean else lean_run()
    check("Lean compile", skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "P1-OWNER-MAP-ADMISSION-INTEGRATED",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": manifest["task_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "methods_unchanged": True,
        "production_admission": "NONE",
        "current_state": "EMPTY_OWNER_ARTIFACT",
        "synthetic_fixture_state": "CONTRACT_TEST_ONLY_COMPLETE",
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "assertion_count": len(checks),
        "passed": len(checks),
        "assertions": checks,
        "lean": lean,
        "evidence_level": manifest["evidence_level"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "manifest_sha256": digest(MANIFEST),
            "primary_sha256": digest(PRIMARY),
            "independent_sha256": digest(INDEPENDENT),
            "hostile_sha256": digest(HOSTILE),
            "lean_sha256": digest(LEAN),
        },
    }
    if output:
        atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"P1 OWNER/MAP ADMISSION INTEGRATED PASS {len(checks)}/{len(checks)}; Lean={lean['status']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-lean", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    run(None if args.no_store else args.output, skip_lean=args.skip_lean)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
