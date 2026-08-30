#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean audit for HOLD-LC-001."""

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
CONTRACT = REPO / "strategy/hold-lc-001-set-valued-delay-envelope-v0.1.json"
PRIMARY = REPO / "codes/foundations/hold_lc_001_set_valued_delay_envelope.py"
INDEPENDENT = REPO / "codes/foundations/hold_lc_001_set_valued_delay_envelope_independent.py"
HOSTILE = REPO / "codes/foundations/hold_lc_001_set_valued_delay_envelope_hostile.py"
LEAN = REPO / "verification/lean/Tect/R447.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-hold_lc_001_set_valued_delay_envelope/integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def child(script: Path, output: Path | None = None) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    command = [str(PYTHON), "-X", "utf8", str(script)]
    if output is not None: command += ["--output", str(output)]
    process = subprocess.run(command, cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload: dict[str, Any] = {}
    if output is not None and output.is_file(): payload = json.loads(output.read_text(encoding="utf-8"))
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
    if lake is None: return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R447.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R447.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R447.lean", "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--skip-lean", action="store_true"); parser.add_argument("--no-store", action="store_true"); args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    with tempfile.TemporaryDirectory(prefix="hold-lc-001-envelope-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        hostile_process, _ = child(HOSTILE)
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("hostile child", hostile_process.returncode == 0, hostile_process.stdout + hostile_process.stderr, "exit 0")
        check("primary assertions", primary.get("assertion_count", 0) > 0 and primary.get("passed") == primary.get("assertion_count"), primary, "all pass")
        check("independent assertions", independent.get("assertion_count", 0) > 0 and independent.get("passed") == independent.get("assertion_count"), independent, "all pass")
        check("lane agreement", primary.get("derived") == independent.get("derived"), [primary.get("derived"), independent.get("derived")], "equal")
        check("envelope only", primary.get("derived", {}).get("set_valued_feasibility_only") is True, primary.get("derived"), True)
        check("no score", primary.get("derived", {}).get("aggregate_scoring_allowed") is False, primary.get("derived"), False)

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R447.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "HOLD-LC-001-SET-VALUED-DELAY-ENVELOPE-INTEGRATED", "claim_id": "C6-SPACETIME-SIGNATURE", "task_id": contract["task_id"], "holdout_id": contract["holdout_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "boundary": contract["non_claims"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"contract_sha256": sha256(CONTRACT), "primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "hostile_sha256": sha256(HOSTILE), "lean_sha256": sha256(LEAN)}}
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED HOLD-LC-001 SET-VALUED ENVELOPE PASS {len(checks)}/{len(checks)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
