#!/usr/bin/env python3
"""Integrated verifier for EXP-001092 primary/independent/Lean evidence."""

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
SLUG = "pre_a_cp1_st8_q3lock_finite_volume_operator_norm_cutoff_duhamel_bound"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R274.lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-integrated-{SLUG}" / "integrated.json"
LAKE = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe")


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
    completed = subprocess.run(command, cwd=REPO, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"child failed: {' '.join(command)}\nstdout={completed.stdout}\nstderr={completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


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


def compare_values(left: Any, right: Any, tolerance: float = 1.0e-7, path: str = "root") -> list[str]:
    if isinstance(left, bool) or isinstance(right, bool):
        return [] if left == right else [f"{path}: {left!r} != {right!r}"]
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return [] if abs(float(left) - float(right)) <= tolerance else [f"{path}: {left!r} != {right!r}"]
    if isinstance(left, list) and isinstance(right, list):
        errors: list[str] = []
        if len(left) != len(right):
            errors.append(f"{path}: length {len(left)} != {len(right)}")
        for index, (a, b) in enumerate(zip(left, right)):
            errors.extend(compare_values(a, b, tolerance, f"{path}[{index}]"))
        return errors
    if isinstance(left, dict) and isinstance(right, dict):
        errors = []
        if set(left) != set(right):
            errors.append(f"{path}: keys differ")
        for key in sorted(set(left) & set(right)):
            errors.extend(compare_values(left[key], right[key], tolerance, f"{path}.{key}"))
        return errors
    return [] if left == right else [f"{path}: {left!r} != {right!r}"]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["exploration_id"] == "EXP-001092" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001092/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("scope firewall", manifest["scope"]["finite_modular_companion_bound_closed"] and not manifest["scope"]["common_alpha_closed"] and not manifest["scope"]["c6_closed"], manifest["scope"], "finite only")
    check("primary exists", PRIMARY.is_file(), PRIMARY, "file")
    check("independent exists", INDEPENDENT.is_file(), INDEPENDENT, "file")
    check("Lean exists", LEAN.is_file(), LEAN, "file")

    with tempfile.TemporaryDirectory(prefix="exp001092-integrated-") as directory:
        temp = Path(directory)
        primary, primary_stdout = run_child(PRIMARY, temp / "primary.json")
        independent, independent_stdout = run_child(INDEPENDENT, temp / "independent.json")

    check("primary verdict", primary["verdict"] == "PASS" and primary["failed"] == 0, primary["verdict"], "PASS")
    check("independent verdict", independent["verdict"] == "PASS" and independent["failed"] == 0, independent["verdict"], "PASS")
    check("primary/independent identity", primary["exploration_id"] == independent["exploration_id"] == "EXP-001092", [primary["exploration_id"], independent["exploration_id"]], "EXP-001092")
    differences = compare_values(primary["derived"], independent["derived"])
    check("primary/independent derived agreement", not differences, differences[:3], "no differences")
    check("primary assertions", primary["passed"] == primary["total"] and primary["total"] == 165, [primary["passed"], primary["total"]], "165/165")
    check("independent assertions", independent["passed"] == independent["total"] and independent["total"] == 165, [independent["passed"], independent["total"]], "165/165")

    source = LEAN.read_text(encoding="utf-8")
    check("Lean source policy", source.endswith("\n") and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), "LF/no forbidden tokens", "required")
    completed = subprocess.run([str(LAKE), "env", "lean", "Tect/R274.lean"], cwd=REPO / "verification/lean", text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Lean R274 failed:\nstdout={completed.stdout}\nstderr={completed.stderr}")
    check("Lean R274 compile", completed.returncode == 0, "PASS", "PASS")
    check("Lean source hash", hashlib.sha256(LEAN.read_bytes()).hexdigest() == "95aab8614047d854d2a361d3b92068b4058130aa000aec62f86e6d33cfeb1422", hashlib.sha256(LEAN.read_bytes()).hexdigest(), "registry hash")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-VOLUME-OPERATOR-NORM-CUTOFF-DUHAMEL-BOUND",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "total": len(checks),
        "failed": 0,
        "assertions": checks,
        "children": {"primary_stdout": primary_stdout, "independent_stdout": independent_stdout, "primary": {"passed": primary["passed"], "total": primary["total"]}, "independent": {"passed": independent["passed"], "total": independent["total"]}},
        "lean": {"path": str(LEAN.relative_to(REPO)).replace("\\", "/"), "command": "lake env lean Tect/R274.lean", "status": "PASS"},
        "derived": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-VOLUME-DUHAMEL-BOUND PASS {payload['passed']}/{payload['total']}; Lean=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
