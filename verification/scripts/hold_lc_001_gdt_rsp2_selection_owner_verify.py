#!/usr/bin/env python3
"""Integrated R-469 primary/independent/hostile/Lean verification."""

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
CONTRACT = REPO / "strategy/hold-lc-001-gdt-rsp2-selection-owner-v0.1.json"
PRIMARY = REPO / "codes/foundations/hold_lc_001_gdt_rsp2_selection_owner.py"
INDEPENDENT = REPO / "codes/foundations/hold_lc_001_gdt_rsp2_selection_owner_independent.py"
HOSTILE = REPO / "codes/foundations/hold_lc_001_gdt_rsp2_selection_owner_hostile.py"
LEAN = REPO / "verification/lean/Tect/R469.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-hold-lc-gdt-selection-owner/integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def store(path: Path, payload: dict[str, Any]) -> None:
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


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


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
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R469.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R469.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R469.lean", "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--skip-lean", action="store_true"); parser.add_argument("--no-store", action="store_true"); args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    with tempfile.TemporaryDirectory(prefix="hold-lc-001-gdt-selection-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        hostile_process, hostile = child(HOSTILE, Path(temporary) / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "PASS", hostile_process.stdout + hostile_process.stderr, "PASS")
        check("lane core agreement", primary.get("core_digest") == independent.get("core_digest"), [primary.get("core_digest"), independent.get("core_digest")], "equal")
        check("source pin", primary.get("source_pin", {}).get("commit") == contract["source_owner"]["commit"] and primary.get("source_pin", {}).get("source_sha256") == contract["source_owner"]["source_sha256"], primary.get("source_pin"), contract["source_owner"]["commit"])
        check("parent index", primary.get("parent_index", {}).get("sha256") == contract["parent_index"]["sha256"], primary.get("parent_index"), contract["parent_index"]["sha256"])
        check("two products", len(primary.get("products", [])) == 2, len(primary.get("products", [])), 2)
        check("sixteen segments", sum(item["segment_count"] for item in primary["products"]) == 16, sum(item["segment_count"] for item in primary["products"]), 16)
        check("endpoint probes", sum(len(item["edge_probes"]) for item in primary["products"]) == 22, sum(len(item["edge_probes"]) for item in primary["products"]), 22)
        check("doc mismatch recorded", primary.get("synthetic_probe", {}).get("doc_implementation_mismatch") is True, primary.get("synthetic_probe"), True)
        check("matrix paths locked", primary.get("matrix_coefficients_read") is False and primary.get("admission", {}).get("calibration_interpolation_admitted") is False, primary.get("admission"), False)
        check("selection stopped", primary.get("selection_mode") == "NONE_SELECTED" and primary.get("candidate_scoring") is False, [primary.get("selection_mode"), primary.get("candidate_scoring")], ["NONE_SELECTED", False])
        check("methods unchanged", primary.get("methods_unchanged") is True, primary.get("methods_unchanged"), True)
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R469.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "HOLD-LC-001-GDT-RSP2-SELECTION-OWNER-INTEGRATED", "claim_id": "C6-SPACETIME-SIGNATURE", "task_id": contract["task_id"], "holdout_id": contract["holdout_id"], "verdict": "PASS", "claim_bearing": False, "methods_unchanged": True, "selection_mode": "NONE_SELECTED", "candidate_scoring": False, "prospective_lock": "EMPTY", "matrix_coefficients_read": False, "source_owner_semantics_admitted": False, "assertion_count": len(checks), "passed": len(checks), "assertions": checks, "lean": lean, "boundary": contract["non_claims"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"contract_sha256": digest(CONTRACT), "primary_sha256": digest(PRIMARY), "independent_sha256": digest(INDEPENDENT), "hostile_sha256": digest(HOSTILE), "lean_sha256": digest(LEAN)}}
    if not args.no_store:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED HOLD-LC-001 GDT RSP2 SELECTION OWNER PASS {len(checks)}/{len(checks)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
