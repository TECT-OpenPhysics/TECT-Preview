#!/usr/bin/env python3
"""Integrated verifier for EXP-001095 and Lean R276."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_particle_core_domain"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN_ROOT = REPO / "verification/lean"
LEAN_SOURCE = LEAN_ROOT / "Tect/R276.lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-integrated-{SLUG}" / "integrated.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def lake_path() -> Path:
    return Path.home() / ".elan" / "toolchains" / "leanprover--lean4---v4.32.1" / "bin" / "lake.exe"


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": str(actual), "expected": str(expected)})
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001095" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001095/T-054")
    check("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("authority files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN_SOURCE.is_file(), [str(PRIMARY), str(INDEPENDENT), str(LEAN_SOURCE)], "present")

    primary_output = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"
    independent_output = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"
    children: dict[str, dict[str, Any]] = {}
    for label, script, output in (("primary", PRIMARY, primary_output), ("independent", INDEPENDENT, independent_output)):
        process = subprocess.run([sys.executable, "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
        check(f"{label} process", process.returncode == 0, process.stdout + process.stderr, "exit 0")
        check(f"{label} output", output.is_file(), str(output), "stored JSON")
        children[label] = json.loads(output.read_text(encoding="utf-8"))
        check(f"{label} PASS", children[label].get("verdict") == "PASS", children[label].get("verdict"), "PASS")

    primary_rows = children["primary"]["derived"]["rows"]
    independent_rows = children["independent"]["derived"]["rows"]
    check("core row reconciliation", primary_rows == independent_rows, [len(primary_rows), len(independent_rows)], "identical rows")
    check("history tail remains open", children["primary"]["derived"]["evolved_history_tail_closed"] is False and children["independent"]["derived"]["gibbs_tail_uniformity_closed"] is False, "both false", "both false")

    lake = lake_path()
    check("pinned lake", lake.is_file(), str(lake), "present")
    lean = subprocess.run([str(lake), "env", "lean", "Tect/R276.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False) if lake.is_file() else None
    lean_ok = bool(lean and lean.returncode == 0 and "error:" not in (lean.stdout + lean.stderr).lower())
    check("Lean R276", lean_ok, (lean.stdout + lean.stderr)[-1000:] if lean else "missing", "exit 0")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-PARTICLE-CORE-DOMAIN", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "children": {"primary": str(primary_output.relative_to(REPO)).replace("\\", "/"), "independent": str(independent_output.relative_to(REPO)).replace("\\", "/")}, "lean": {"path": "verification/lean/Tect/R276.lean", "status": "PASS", "sha256": digest(LEAN_SOURCE)}, "derived": {"fixed_finite_particle_core_strong_zero_closed": True, "embedded_basis_identity_closed": True, "evolved_history_tail_closed": False, "gibbs_tail_uniformity_closed": False, "actual_unbounded_q3_domain_transfer_closed": False, "source_volume_uniform_modular_history_closed": False, "common_alpha_closed": False}, "boundary": manifest["boundary"], "provenance": {"primary_sha256": digest(PRIMARY), "independent_sha256": digest(INDEPENDENT), "manifest_sha256": digest(MANIFEST), "lean_sha256": digest(LEAN_SOURCE)}}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); args = parser.parse_args()
    payload = run(); atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload); print(f"INTEGRATED FINITE-PARTICLE-CORE-DOMAIN PASS {payload['assertion_count']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
