#!/usr/bin/env python3
"""Integrated primary/independent/pinned-Lean verifier for EXP-001178."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-gram-perturbation"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
PRIMARY = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R339.lean"
LEAN_ROOT = REPO / "verification" / "lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


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


def lake_path() -> Path | None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R339.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R339.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def compare(one: Any, two: Any, path: str) -> tuple[bool, str]:
    if isinstance(one, dict) and isinstance(two, dict):
        if set(one) != set(two):
            return False, f"{path}: keys differ"
        for key in sorted(one):
            ok, message = compare(one[key], two[key], f"{path}.{key}")
            if not ok:
                return False, message
        return True, "equal"
    if isinstance(one, list) and isinstance(two, list):
        if len(one) != len(two):
            return False, f"{path}: lengths differ"
        for index, (left, right) in enumerate(zip(one, two)):
            ok, message = compare(left, right, f"{path}[{index}]")
            if not ok:
                return False, message
        return True, "equal"
    return (one == two, f"{path}: values differ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001178" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001178/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("scope firewall", manifest["scope"]["finite_gram_perturbation_closed"] and manifest["scope"]["lean_entrypoint_registered"] and not manifest["scope"]["actual_q3_os_vector_factorization_closed"] and not manifest["scope"]["common_os_hilbert_carrier_closed"] and not manifest["scope"]["direct_d_delta_d_cauchy_closed"] and not manifest["scope"]["pre_a_closed"], manifest["scope"], "finite bridge only")
    with tempfile.TemporaryDirectory(prefix="finite-gram-perturbation-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        for field in ("rows", "formal_checks", "scope"):
            ok, message = compare(primary.get(field), independent.get(field), field)
            check(f"{field} agreement", ok, message, "equal")
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R339.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item["path"] == "verification/lean/Tect/R339.lean"), None)
    check("registry integrity", entry is not None and entry["sha256"] == sha256(LEAN), entry["sha256"] if entry else None, sha256(LEAN))
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GRAM-PERTURBATION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(assertions),
        "assertions": assertions,
        "lean": lean,
        "formal_checks": ["finite_gram_entry_perturbation"],
        "rows": primary.get("rows"),
        "scope": manifest["scope"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "registry_sha256": sha256(REGISTRY)},
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-GRAM-PERTURBATION PASS {len(assertions)}/{len(assertions)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
