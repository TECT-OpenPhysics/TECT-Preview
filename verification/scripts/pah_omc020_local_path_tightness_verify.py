#!/usr/bin/env python3
"""Integrated replay for the PAH-OMC-020 local path-tightness checkpoint."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_local_path_tightness.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_local_path_tightness_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_local_path_tightness_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020PathTightness.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-local-path-tightness"
)
OUTPUT = RUN_DIR / "integrated.json"
DEFAULT_LEAN = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def build_lean_path(cache: Path | None) -> str:
    candidates: list[str] = []
    for root in (cache, ROOT / "verification/lean/.lake/packages"):
        if root is None or not root.is_dir():
            continue
        for package in sorted(root.iterdir()):
            candidate = package / ".lake" / "build" / "lib" / "lean"
            if candidate.is_dir() and str(candidate) not in candidates:
                candidates.append(str(candidate))
    return os.pathsep.join(candidates)


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def imports_are_independent(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc020_local_path_tightness", "verification.scripts", "codes.foundations")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        if any(any(token in name for token in forbidden) for name in names):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--lean", type=Path, default=DEFAULT_LEAN)
    parser.add_argument("--lean-cache", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    rows: list[dict[str, Any]] = []

    commands = [
        ("primary", [sys.executable, "-X", "utf8", str(PRIMARY), "--check"]),
        ("independent", [sys.executable, "-X", "utf8", str(INDEPENDENT), "--check"]),
        ("hostile", [sys.executable, "-X", "utf8", str(HOSTILE), "--check"]),
    ]
    subprocesses: dict[str, dict[str, Any]] = {}
    for name, command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocesses[name] = {"returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        check(rows, f"{name} replay", result.returncode, 0, result.returncode == 0)

    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    for name, run in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(rows, f"{name} verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        flags = {key: run.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}
        check(rows, f"{name} firewalls", flags, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(value is False for value in flags.values()))
        check(rows, f"{name} status", run.get("status", ""), run.get("status", ""), run.get("status", "").startswith("PASS_"))
    check(rows, "primary check count", primary.get("checks_passed"), 25, primary.get("checks_passed") == 25)
    check(rows, "independent check count", independent.get("checks_passed"), 20, independent.get("checks_passed") == 20)
    check(rows, "hostile mutation count", hostile.get("checks_passed"), 9, hostile.get("checks_passed") == 9)
    check(rows, "source constants agree", primary.get("source_constants"), {"C2_per_site": 60, "C_sw": 540, "root_bound_per_site": 60}, primary.get("source_constants") == {"C2_per_site": 60, "C_sw": 540, "root_bound_per_site": 60})
    check(rows, "independent source constants agree", independent.get("source_constants"), {"C2_per_site": 60, "C_sw": 540}, independent.get("source_constants") == {"C2_per_site": 60, "C_sw": 540})

    check(rows, "independent verifier has no project import", imports_are_independent(INDEPENDENT), True, imports_are_independent(INDEPENDENT))
    check(rows, "hostile verifier has no project import", imports_are_independent(HOSTILE), True, imports_are_independent(HOSTILE))
    check(rows, "Lean line endings", b"\r" not in LEAN.read_bytes(), True, b"\r" not in LEAN.read_bytes())
    lean_text = LEAN.read_text(encoding="utf-8")
    forbidden = {token: bool(re.search(rf"\b{re.escape(token)}\b", lean_text)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check(rows, "Lean forbidden tokens", forbidden, {token: False for token in forbidden}, not any(forbidden.values()))
    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020PathTightness.lean"), None)
    check(rows, "Lean registry entry", entry is not None, True, entry is not None)
    if entry is None:
        entry = {}
    declarations = {"two_square_sum", "envelope_nonnegative", "markov_bound_nonnegative", "envelope_decreases", "source_constants_fixture", "compact_time_fixture"}
    check(rows, "Lean registry hash", entry.get("sha256"), digest(LEAN), entry.get("sha256") == digest(LEAN))
    check(rows, "Lean declarations", sorted(entry.get("declarations", [])), sorted(declarations), set(entry.get("declarations", [])) == declarations)
    env = os.environ.copy()
    paths = build_lean_path(args.lean_cache)
    if paths:
        env["LEAN_PATH"] = paths
    lean_result = subprocess.run([str(args.lean), str(LEAN)], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace") if args.lean.is_file() else None
    check(rows, "Lean compiler available", args.lean.is_file(), True, args.lean.is_file())
    lean_rc = lean_result.returncode if lean_result is not None else None
    lean_output = ((lean_result.stdout + lean_result.stderr).strip() if lean_result is not None else "")
    check(rows, "Lean compile", lean_rc, 0, lean_rc == 0)

    parent_hashes = primary.get("source_hashes", {})
    check(rows, "parent source hashes are shared", independent.get("source_hashes"), parent_hashes, independent.get("source_hashes") == parent_hashes and hostile.get("source_hashes") == parent_hashes)
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-local-path-tightness-integrated/1.0",
        "audit_id": "PAH-OMC-020-LOCAL-PATH-TIGHTNESS-INTEGRATED-001",
        "result_id": "R-541",
        "task_id": "T-064",
        "status": "PASS_INTEGRATED_LOCAL_PATH_TIGHTNESS_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(rows),
        "passed": len(rows),
        "failed": 0,
        "checks": rows,
        "subprocesses": subprocesses,
        "lean": {"command": [str(args.lean), str(LEAN)], "returncode": lean_rc, "output": lean_output},
        "source_hashes": {
            **parent_hashes,
            "verification/scripts/pah_omc020_local_path_tightness.py": digest(PRIMARY),
            "codes/foundations/pah_omc020_local_path_tightness_independent.py": digest(INDEPENDENT),
            "codes/foundations/pah_omc020_local_path_tightness_hostile.py": digest(HOSTILE),
            "verification/scripts/pah_omc020_local_path_tightness_verify.py": digest(Path(__file__)),
            "verification/lean/Tect/PahOmc020PathTightness.lean": digest(LEAN),
            "verification/lean/registry.json": digest(REGISTRY),
        },
        "finding": "Primary, independent and hostile replays plus Lean compile agree that the pinned Gibbs conductance and C2 inputs yield a finite local stopped-time second-moment envelope; no limiting process is identified.",
        "next_single_question": "Can a source-authorized martingale-problem/path-space construction with non-explosion and uniqueness identify every subsequential local path limit with the R-512 minimal-form semigroup in the frozen j-before-anchored-n order?",
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_local_path_tightness_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        "non_claims": [
            "No new PAH functional, rate, state, carrier, regulator, normalization or time interpretation.",
            "No infinite-volume process, semigroup convergence, N2b/N2c/N4 closure or R-512 identification.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
        ],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 local path tightness integrated replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 LOCAL PATH TIGHTNESS INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
