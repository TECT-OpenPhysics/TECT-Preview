#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean audit for HOLD-LC-001 rsp2 indexing."""

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
CONTRACT = REPO / "strategy/hold-lc-001-rsp2-segment-index-contract-v0.1.json"
PRIMARY = REPO / "codes/foundations/hold_lc_001_rsp2_segment_index.py"
INDEPENDENT = REPO / "codes/foundations/hold_lc_001_rsp2_segment_index_independent.py"
HOSTILE = REPO / "codes/foundations/hold_lc_001_rsp2_segment_index_hostile.py"
LEAN = REPO / "verification/lean/Tect/R468.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-hold-lc-rsp2-segment-index/integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def child(script: Path, output: Path | None = None) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    command = [str(PYTHON), "-X", "utf8", str(script)]
    if output is not None: command += ["--output", str(output)]
    process = subprocess.run(command, cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output is not None and output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file(): return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    lake = lake_path()
    if lake is None: return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R468.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R468.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R468.lean", "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--skip-lean", action="store_true"); parser.add_argument("--no-store", action="store_true"); args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    with tempfile.TemporaryDirectory(prefix="hold-lc-001-rsp2-index-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        hostile_process, hostile = child(HOSTILE, Path(temporary) / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "PASS", hostile_process.stdout + hostile_process.stderr, "PASS")
        check("lane core agreement", primary.get("core_digest") == independent.get("core_digest"), [primary.get("core_digest"), independent.get("core_digest")], "equal")
        check("two products", len(primary.get("products", [])) == 2, len(primary.get("products", [])), 2)
        check("sixteen segments", sum(item["source"]["response_segment_count"] for item in primary["products"]) == 16, sum(item["source"]["response_segment_count"] for item in primary["products"]), 16)
        check("query alternatives retained", all(len(item["query_selection_alternatives"]) == 5 for item in primary["products"]), [len(item["query_selection_alternatives"]) for item in primary["products"]], 5)
        check("matrix values locked", primary.get("matrix_coefficients_read") is False and primary.get("admission", {}).get("matrix_values_read") is False, primary.get("admission"), False)
        check("selection stopped", primary.get("selection_mode") == "NONE_SELECTED" and primary.get("candidate_scoring") is False, [primary.get("selection_mode"), primary.get("candidate_scoring")], ["NONE_SELECTED", False])
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R468.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "HOLD-LC-001-RSP2-SEGMENT-INDEX-INTEGRATED", "claim_id": contract["holdout_id"].replace("HOLD-LC-001", "C6-SPACETIME-SIGNATURE"), "task_id": contract["task_id"], "holdout_id": contract["holdout_id"], "verdict": "PASS", "assertion_count": len(checks), "passed": len(checks), "assertions": checks, "lean": lean, "boundary": contract["non_claims"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"contract_sha256": digest(CONTRACT), "primary_sha256": digest(PRIMARY), "independent_sha256": digest(INDEPENDENT), "hostile_sha256": digest(HOSTILE), "lean_sha256": digest(LEAN)}}
    if not args.no_store: store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED HOLD-LC-001 RSP2 INDEX PASS {len(checks)}/{len(checks)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
