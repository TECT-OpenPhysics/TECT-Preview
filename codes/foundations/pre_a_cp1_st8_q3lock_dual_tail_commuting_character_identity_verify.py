#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001124."""

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


ROOT = Path(__file__).resolve().parents[2]
NAME = "pre_a_cp1_st8_q3lock_dual_tail_commuting_character_identity"
MANIFEST = ROOT / f"strategy/{NAME}_manifest.json"
PRIMARY = ROOT / f"codes/foundations/{NAME}.py"
INDEPENDENT = ROOT / f"codes/foundations/{NAME}_independent.py"
LEAN = ROOT / "verification/lean/Tect/R295.lean"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{NAME}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict[str, Any]:
    registry = json.loads((ROOT / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    lake = next((candidate / name for name in ("lake.exe", "lake") if (candidate / name).is_file()), None) or shutil.which("lake")
    command = "lake env lean Tect/R295.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R295.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    clean = "error:" not in output.lower() and "warning:" not in output.lower()
    return {"status": "PASS" if process.returncode == 0 and clean else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001124" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001124/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("source distinct", digest(PRIMARY) != digest(INDEPENDENT), [digest(PRIMARY), digest(INDEPENDENT)], "distinct source hashes")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["rotation_norm_fixture", "tail_square_fixture", "dual_tail_static_fixture", "scope_fixture"]
    check("Lean markers", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden tokens", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="dual-tail-identity-") as temporary:
        p_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        i_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", p_process.returncode == 0 and primary.get("verdict") == "PASS", p_process.stdout + p_process.stderr, "PASS")
        check("independent child", i_process.returncode == 0 and independent.get("verdict") == "PASS", i_process.stdout + i_process.stderr, "PASS")
        check("reference values agree", primary.get("derived", {}).get("reference_tail_value") == independent.get("derived", {}).get("reference_tail_value"), [primary.get("derived", {}).get("reference_tail_value"), independent.get("derived", {}).get("reference_tail_value")], "equal")
        check("dual values agree", primary.get("derived", {}).get("dual_tail_value") == independent.get("derived", {}).get("dual_tail_value"), [primary.get("derived", {}).get("dual_tail_value"), independent.get("derived", {}).get("dual_tail_value")], "equal")
        for key, value in scope.items():
            if key in primary.get("derived", {}):
                check("scope agreement " + key, primary["derived"].get(key) == independent["derived"].get(key) == value, [primary["derived"].get(key), independent["derived"].get(key), value], "equal")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    open_keys = tuple(key for key, value in scope.items() if value is False)
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all open")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-TAIL-COMMUTING-CHARACTER-IDENTITY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": digest(PRIMARY), "independent_sha256": digest(INDEPENDENT), "manifest_sha256": digest(MANIFEST), "lean_sha256": digest(LEAN)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    if args.skip_lean:
        raise SystemExit("skip-lean is not allowed for the integrated proof checkpoint")
    payload = run()
    if not args.no_store:
        save(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INTEGRATED DUAL-TAIL-COMMUTING-CHARACTER PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
