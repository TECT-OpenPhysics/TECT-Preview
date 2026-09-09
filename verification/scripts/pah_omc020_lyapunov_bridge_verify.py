#!/usr/bin/env python3
"""Integrate primary, independent, hostile and Lean Lyapunov checks."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-lyapunov-bridge/integrated.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_lyapunov_bridge.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_lyapunov_bridge_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_lyapunov_bridge_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020Lyapunov.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-lyapunov-bridge-contract-v1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script: Path, output: Path) -> tuple[str, dict]:
    proc = subprocess.run([sys.executable, str(script), "--output", str(output)], cwd=ROOT, text=True, capture_output=True, check=True)
    return proc.stdout.strip(), json.loads(output.read_text(encoding="utf-8"))


def lean_path(cache: Path) -> str:
    parts = [str(p / ".lake" / "build" / "lib" / "lean") for p in cache.iterdir() if p.is_dir()]
    return os.pathsep.join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--lean-cache", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="pah-omc020-lyapunov-") as temp:
        td = Path(temp)
        stdout_primary, primary = run(PRIMARY, td / "primary.json")
        stdout_independent, independent = run(INDEPENDENT, td / "independent.json")
        stdout_hostile, hostile = run(HOSTILE, td / "hostile.json")
        env = os.environ.copy()
        env["LEAN_PATH"] = lean_path(args.lean_cache)
        lean_proc = subprocess.run([str(Path("C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lean.exe")), str(LEAN)], cwd=ROOT, text=True, capture_output=True, env=env, check=True)
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        entries = [e for e in registry["entrypoints"] if e.get("path") == "verification/lean/Tect/PahOmc020Lyapunov.lean"]
        checks = [
            {"name": "primary status", "ok": primary["status"] == "PASS_CONDITIONAL_LYAPUNOV_N2C_BRIDGE"},
            {"name": "independent status", "ok": independent["status"] == "PASS_INDEPENDENT_CONDITIONAL"},
            {"name": "hostile status", "ok": hostile["status"] == "PASS_HOSTILE_CONTROLS"},
            {"name": "primary checks", "ok": primary["checks_passed"] >= 20},
            {"name": "independent checks", "ok": independent["checks_passed"] >= 20},
            {"name": "hostile checks", "ok": hostile["checks_passed"] >= 14},
            {"name": "registry singleton", "ok": len(entries) == 1},
            {"name": "registry hash", "ok": entries and entries[0]["sha256"] == digest(LEAN)},
            {"name": "registry declarations", "ok": entries and all(name in entries[0]["declarations"] for name in ("probability_bound", "n4_bound", "envelope_step_decreases", "zero_boundary_when_zero_mass"))},
            {"name": "no primary import", "ok": not any(isinstance(node, (ast.Import, ast.ImportFrom)) and any("pah_omc020_lyapunov_bridge" in alias.name for alias in getattr(node, "names", [])) for node in ast.walk(ast.parse(INDEPENDENT.read_text(encoding="utf-8"))) if isinstance(node, (ast.Import, ast.ImportFrom)))},
            {"name": "no physical promotion", "ok": primary["physical_promotion"] is False and independent["verdict"] == "AUXILIARY_SUPPORT" and hostile["verdict"] == "AUXILIARY_SUPPORT"},
            {"name": "contract hash available", "ok": len(digest(CONTRACT)) == 64},
        ]
        if not all(item["ok"] for item in checks):
            raise SystemExit("integrated Lyapunov bridge check failed: " + repr(checks))
        payload = {
            "schema": "tect/pah-omc020-lyapunov-bridge-integrated/1.0",
            "status": "PASS_INTEGRATED_CONDITIONAL_LYAPUNOV_BRIDGE",
            "verdict": "AUXILIARY_SUPPORT",
            "conditional": True,
            "claim_bearing": False,
            "active_gate_change": False,
            "physical_promotion": False,
            "checks": checks,
            "checks_passed": len(checks),
            "lane_counts": {"primary": primary["checks_passed"], "independent": independent["checks_passed"], "hostile": hostile["checks_passed"]},
            "lean": {"path": str(LEAN.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(LEAN), "stdout": lean_proc.stdout, "stderr": lean_proc.stderr},
            "stdout": {"primary": stdout_primary, "independent": stdout_independent, "hostile": stdout_hostile},
            "source_hashes": {"contract": digest(CONTRACT), "primary": digest(PRIMARY), "independent": digest(INDEPENDENT), "hostile": digest(HOSTILE), "lean": digest(LEAN), "registry": digest(REGISTRY)},
            "non_claims": ["No owner packet, path law, non-explosion theorem, N2b/N2c/N4/N2d closure or semigroup convergence.", "No physical Pre-A, spacetime, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE conclusion."],
        }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists() and args.output.read_bytes() != encoded:
        raise SystemExit("integrated Lyapunov bridge replay mismatch")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(f"PAH-OMC-020 LYAPUNOV INTEGRATED: {len(checks)} checks; PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
