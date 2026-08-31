#!/usr/bin/env python3
"""Integrate primary, independent, hostile, and Lean checks for R-474."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-q3lock-ordered-limit-rectangle-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "pre_a_q3lock_ordered_limit_rectangle.py"
INDEPENDENT = REPO / "codes" / "foundations" / "pre_a_q3lock_ordered_limit_rectangle_independent.py"
HOSTILE = REPO / "codes" / "foundations" / "pre_a_q3lock_ordered_limit_rectangle_hostile.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R474.lean"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / "2026-08-31-integrated-r474-ordered-limit-rectangle" / "integrated.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def run(script: Path, output: Path) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, "-X", "utf8", str(script), "--output", str(output), "--self-test"], cwd=REPO, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    report = load(output) if output.exists() else {}
    return {"script": str(script.relative_to(REPO)).replace("\\", "/"), "returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip(), "report": report}


def lean_check() -> dict[str, Any]:
    encoded = "leanprover--lean4---v4.32.1"
    candidates = [Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe", Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake"]
    lake = next((item for item in candidates if item.is_file()), None)
    if lake is None:
        return {"pass": False, "returncode": None, "stdout": "", "stderr": "pinned lake executable missing"}
    proc = subprocess.run([str(lake), "env", "lean", "Tect/R474.lean"], cwd=REPO / "verification" / "lean", text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    combined = f"{proc.stdout}\n{proc.stderr}"
    return {"pass": proc.returncode == 0 and "error:" not in combined.lower(), "returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = load(MANIFEST)
    with tempfile.TemporaryDirectory(prefix="r474-ordered-limit-") as directory:
        root = Path(directory)
        primary = run(PRIMARY, root / "primary.json")
        independent = run(INDEPENDENT, root / "independent.json")
        hostile = run(HOSTILE, root / "hostile.json")
    p = primary["report"]
    i = independent["report"]
    h = hostile["report"]
    lean = lean_check()
    assertions = [
        {"name": "manifest identity", "pass": [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("claim_bearing"), manifest.get("tier")] == ["R-474", "EXP-001353", False, "T0"], "actual": [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("claim_bearing"), manifest.get("tier")], "expected": ["R-474", "EXP-001353", False, "T0"]},
        {"name": "primary exits", "pass": primary["returncode"] == 0, "actual": primary["returncode"], "expected": 0},
        {"name": "independent exits", "pass": independent["returncode"] == 0, "actual": independent["returncode"], "expected": 0},
        {"name": "hostile exits", "pass": hostile["returncode"] == 0, "actual": hostile["returncode"], "expected": 0},
        {"name": "primary assertions pass", "pass": p.get("assertion_summary", {}).get("passed") == p.get("assertion_summary", {}).get("total"), "actual": p.get("assertion_summary"), "expected": "passed=total"},
        {"name": "independent assertions pass", "pass": i.get("assertion_summary", {}).get("passed") == i.get("assertion_summary", {}).get("total"), "actual": i.get("assertion_summary"), "expected": "passed=total"},
        {"name": "hostile mutations rejected", "pass": h.get("mutation_summary", {}).get("rejected") == h.get("mutation_summary", {}).get("total"), "actual": h.get("mutation_summary"), "expected": "rejected=total"},
        {"name": "independent and hostile fixture fingerprints agree", "pass": i.get("core", {}).get("core_fingerprint") == h.get("base_core_fingerprint"), "actual": [i.get("core", {}).get("core_fingerprint"), h.get("base_core_fingerprint")], "expected": "equal"},
        {"name": "Lean R474 compiles", "pass": lean["pass"], "actual": lean, "expected": "exit 0 without errors"},
        {"name": "forward rectangle closed", "pass": p.get("derived", {}).get("forward_rectangle_closed") is True, "actual": p.get("derived", {}).get("forward_rectangle_closed"), "expected": True},
        {"name": "reverse rectangle closed", "pass": p.get("derived", {}).get("reverse_rectangle_closed") is True, "actual": p.get("derived", {}).get("reverse_rectangle_closed"), "expected": True},
        {"name": "ordered limit remains open", "pass": p.get("derived", {}).get("ordered_limit_closed") is False, "actual": p.get("derived", {}).get("ordered_limit_closed"), "expected": False},
        {"name": "methods remain unchanged", "pass": all(manifest.get("method_preservation", {}).values()), "actual": manifest.get("method_preservation"), "expected": "all true"},
    ]
    passed = sum(bool(item["pass"]) for item in assertions)
    payload = {
        "schema": "tect/r474-ordered-limit-rectangle-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "R474-ORDERED-LIMIT-RECTANGLE-INTEGRATED-v1",
        "result_id": "R-474",
        "exploration_id": "EXP-001353",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": "T-054",
        "tier": "T0",
        "claim_bearing": False,
        "verdict": "R474_ORDERED_LIMIT_RECTANGLE_INTEGRATED_PASS" if passed == len(assertions) else "R474_ORDERED_LIMIT_RECTANGLE_INTEGRATED_FAIL",
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "checkers": {"primary": {key: value for key, value in primary.items() if key != "report"}, "independent": {key: value for key, value in independent.items() if key != "report"}, "hostile": {key: value for key, value in hostile.items() if key != "report"}},
        "lean": lean,
        "source_hashes": {"manifest": digest(MANIFEST), "primary": digest(PRIMARY), "independent": digest(INDEPENDENT), "hostile": digest(HOSTILE), "lean": digest(LEAN), "integrated": digest(Path(__file__))},
        "derived": {"forward_rectangle_closed": True, "reverse_rectangle_closed": True, "ordered_limit_closed": False, "source_owner_present": False, "common_norm_present": False},
        "evidence_level": manifest["evidence_level"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, args.output)
    print(f"R-474 INTEGRATED: {payload['verdict']} ({passed}/{len(assertions)} assertions; Lean={'PASS' if lean['pass'] else 'FAIL'})")
    return 0 if payload["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
