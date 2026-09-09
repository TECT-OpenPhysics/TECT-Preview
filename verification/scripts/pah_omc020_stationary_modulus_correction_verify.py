#!/usr/bin/env python3
"""Integrated replay for the PAH-OMC-020 stationary-modulus correction."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_stationary_modulus_correction.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_stationary_modulus_correction_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_stationary_modulus_correction_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020StationaryModulus.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-stationary-modulus-correction"
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


def lean_path(cache: Path | None) -> str:
    candidates: list[str] = []
    for root in (cache, ROOT / "verification/lean/.lake/packages"):
        if root is None or not root.is_dir():
            continue
        for package in sorted(root.iterdir()):
            candidate = package / ".lake" / "build" / "lib" / "lean"
            if candidate.is_dir() and str(candidate) not in candidates:
                candidates.append(str(candidate))
    return os.pathsep.join(candidates)


def no_project_import(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc020_stationary_modulus_correction", "verification.scripts", "codes.foundations")
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


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


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
    check(rows, "primary count", primary.get("checks_passed"), 21, primary.get("checks_passed") == 21)
    check(rows, "independent count", independent.get("checks_passed"), 18, independent.get("checks_passed") == 18)
    check(rows, "hostile count", hostile.get("checks_passed"), 11, hostile.get("checks_passed") == 11)
    check(rows, "deterministic-only boundary", "deterministic-time" in primary.get("proof_boundary", "") or "deterministic" in primary.get("finding", ""), True, "deterministic" in primary.get("proof_boundary", "") or "deterministic" in primary.get("finding", ""))
    check(rows, "abstract diagnostic is quarantined", "abstract implication diagnostic only; not an exact PAH counterexample" in primary.get("rare_state_diagnostic", {}).get("interpretation", ""), True, "abstract implication diagnostic only; not an exact PAH counterexample" in primary.get("rare_state_diagnostic", {}).get("interpretation", ""))
    check(rows, "independent lane has no project import", no_project_import(INDEPENDENT), True, no_project_import(INDEPENDENT))
    check(rows, "hostile lane has no project import", no_project_import(HOSTILE), True, no_project_import(HOSTILE))

    lean_text = LEAN.read_text(encoding="utf-8")
    check(rows, "Lean line endings", b"\r" not in LEAN.read_bytes(), True, b"\r" not in LEAN.read_bytes())
    forbidden = {token: bool(re.search(rf"\b{re.escape(token)}\b", lean_text)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check(rows, "Lean forbidden tokens", forbidden, {token: False for token in forbidden}, not any(forbidden.values()))
    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020StationaryModulus.lean"), None)
    check(rows, "Lean registry entry", entry is not None, True, entry is not None)
    if entry is None:
        entry = {}
    declarations = {"weighted_gamma_rare", "rare_fixture_m8", "rare_fixture_scale_m8", "deterministic_envelope_fixture", "two_square_sum"}
    check(rows, "Lean registry hash", entry.get("sha256"), digest(LEAN), entry.get("sha256") == digest(LEAN))
    check(rows, "Lean declarations", sorted(entry.get("declarations", [])), sorted(declarations), set(entry.get("declarations", [])) == declarations)
    env = os.environ.copy()
    paths = lean_path(args.lean_cache)
    if paths:
        env["LEAN_PATH"] = paths
    lean_result = subprocess.run([str(args.lean), str(LEAN)], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace") if args.lean.is_file() else None
    check(rows, "Lean compiler available", args.lean.is_file(), True, args.lean.is_file())
    lean_rc = lean_result.returncode if lean_result is not None else None
    lean_output = ((lean_result.stdout + lean_result.stderr).strip() if lean_result is not None else "")
    check(rows, "Lean compile", lean_rc, 0, lean_rc == 0)
    check(rows, "all lanes keep source hashes", primary.get("source_hashes"), independent.get("source_hashes"), primary.get("source_hashes") == independent.get("source_hashes") and primary.get("source_hashes") == hostile.get("source_hashes"))

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-stationary-modulus-correction-integrated/1.0",
        "audit_id": "PAH-OMC-020-STATIONARY-MODULUS-CORRECTION-INTEGRATED-001",
        "result_id": "R-542",
        "task_id": "T-064",
        "status": "PASS_INTEGRATED_STATIONARY_MODULUS_CORRECTION_HOLD",
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
            **primary.get("source_hashes", {}),
            "verification/scripts/pah_omc020_stationary_modulus_correction.py": digest(PRIMARY),
            "codes/foundations/pah_omc020_stationary_modulus_correction_independent.py": digest(INDEPENDENT),
            "codes/foundations/pah_omc020_stationary_modulus_correction_hostile.py": digest(HOSTILE),
            "verification/scripts/pah_omc020_stationary_modulus_correction_verify.py": digest(Path(__file__)),
            "verification/lean/Tect/PahOmc020StationaryModulus.lean": digest(LEAN),
            "verification/lean/registry.json": digest(REGISTRY),
        },
        "finding": "The deterministic-time stationary modulus is valid from the pinned pi-weighted inputs. The hostile and abstract rare-state controls reject upgrading that average bound to a bounded-stopping-time Aldous estimate without a separate conditional owner packet.",
        "next_single_question": "Can a source-authorized pointwise local-rate or predictable-compensator estimate upgrade the deterministic stationary modulus to the bounded-stopping-time Aldous condition without changing PAH-001?",
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_stationary_modulus_correction_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        "non_claims": [
            "No exact PAH counterexample is claimed; the rare-state chain is only an implication diagnostic.",
            "No Aldous path tightness, path-space construction, non-explosion, semigroup convergence or R-512 identification.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
        ],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 stationary-modulus correction integrated replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 STATIONARY MODULUS CORRECTION INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
