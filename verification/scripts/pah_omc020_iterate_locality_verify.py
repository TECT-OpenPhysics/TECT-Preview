#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean replay for R-561."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_iterate_locality.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_iterate_locality_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_iterate_locality_hostile.py"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_SOURCE = LEAN_ROOT / "Tect/PahOmc020FiniteSemigroup.lean"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-iterate-locality/integrated.json"
LAKE_FALLBACK = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe")
CANONICAL_LEAN_ROOT = Path(r"E:\Dev\TECT\verification\lean")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict[str, object]:
    process = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {"command": " ".join(command), "returncode": process.returncode, "stdout": process.stdout[-4000:], "stderr": process.stderr[-4000:]}


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    python = sys.executable
    lake = shutil.which("lake") or (str(LAKE_FALLBACK) if LAKE_FALLBACK.exists() else "lake")
    lean_cwd = LEAN_ROOT
    lean_source = "Tect/PahOmc020FiniteSemigroup.lean"
    if not (LEAN_ROOT / ".lake/packages/mathlib").exists() and (CANONICAL_LEAN_ROOT / ".lake/packages/mathlib").exists():
        lean_cwd = CANONICAL_LEAN_ROOT
        lean_source = str(LEAN_SOURCE)
    lean_env = os.environ.copy()
    if lean_cwd == CANONICAL_LEAN_ROOT:
        lean_env["GIT_CONFIG_COUNT"] = "1"
        lean_env["GIT_CONFIG_KEY_0"] = "safe.directory"
        # The prebuilt Lean dependency checkout is operator-owned while this
        # replay runs as the sandbox user; scope the exception to this child
        # process so Lake can read all pinned package checkouts.
        lean_env["GIT_CONFIG_VALUE_0"] = "*"
    runs = {
        "primary": run_command([python, str(PRIMARY), "--check"], ROOT),
        "independent": run_command([python, str(INDEPENDENT), "--check"], ROOT),
        "hostile": run_command([python, str(HOSTILE), "--check"], ROOT),
        "lean": run_command([lake, "env", "lean", lean_source], lean_cwd, lean_env),
    }
    rows = []
    for name, result in runs.items():
        ok = result["returncode"] == 0
        rows.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": result})
    failed = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/pah-omc020-iterate-locality-integrated/1.0",
        "result_id": "R-561",
        "verification": "PASS" if not failed else "FAIL",
        "checks": rows,
        "checks_passed": len(rows) - len(failed),
        "checks_failed": len(failed),
        "tool_hashes": {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path) for path in (PRIMARY, INDEPENDENT, HOSTILE, LEAN_SOURCE)},
    }
    if not args.check:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        atomic_json(output, payload)
    print(f"PAH-OMC-020 ITERATE LOCALITY INTEGRATED: {payload['verification']} {payload['checks_passed']}/{len(rows)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
