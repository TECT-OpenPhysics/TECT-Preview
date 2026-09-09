#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-020 mesh-to-uniform transfer."""

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
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-mesh-uniform-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_mesh_uniform.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_mesh_uniform_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_mesh_uniform_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020MeshUniform.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-mesh-uniform"
OUTPUT = RUN_DIR / "integrated.json"
DEFAULT_LEAN = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe")
DEFAULT_CACHE = Path(r"E:\Dev\TECT\verification\lean\.lake\packages")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def no_project_import(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc020_mesh_uniform", "verification.scripts", "codes.foundations")
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


def lean_path(cache: Path | None) -> str:
    roots = [cache, ROOT / "verification/lean/.lake/packages"]
    values: list[str] = []
    for root in roots:
        if root is None or not root.is_dir():
            continue
        for package in sorted(root.iterdir()):
            candidate = package / ".lake" / "build" / "lib" / "lean"
            if candidate.is_dir() and str(candidate) not in values:
                values.append(str(candidate))
    return os.pathsep.join(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--lean", type=Path, default=DEFAULT_LEAN)
    parser.add_argument("--lean-cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    subprocesses: dict[str, dict[str, Any]] = {}
    for name, script in (("primary", PRIMARY), ("independent", INDEPENDENT), ("hostile", HOSTILE)):
        command = [sys.executable, "-X", "utf8", str(script), "--check"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocesses[name] = {"returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        check(rows, f"{name} replay", result.returncode, 0, result.returncode == 0)

    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    for name, run in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(rows, f"{name} verdict", run.get("verdict"), "PASS", run.get("verdict") == "PASS")
        flags = {key: run.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}
        check(rows, f"{name} firewalls", flags, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(value is False for value in flags.values()))
        check(rows, f"{name} checks nonzero", run.get("checks_passed", 0) > 0, True, run.get("checks_passed", 0) > 0)
    check(rows, "primary count", primary.get("checks_passed"), 27, primary.get("checks_passed") == 27)
    check(rows, "independent count", independent.get("checks_passed"), 16, independent.get("checks_passed") == 16)
    check(rows, "hostile count", hostile.get("checks_passed"), 15, hostile.get("checks_passed") == 15)
    check(rows, "independent has no project import", no_project_import(INDEPENDENT), True, no_project_import(INDEPENDENT))
    check(rows, "hostile has no project import", no_project_import(HOSTILE), True, no_project_import(HOSTILE))
    check(rows, "parent hashes agree", primary.get("source_hashes"), independent.get("source_hashes"), primary.get("source_hashes") == independent.get("source_hashes") == hostile.get("source_hashes"))

    contract = load(CONTRACT)
    check(rows, "contract is present", CONTRACT.is_file(), True, CONTRACT.is_file())
    check(rows, "conditional classification", type(contract.get("acceptance", {}).get("PASS")).__name__, "str", isinstance(contract.get("acceptance", {}).get("PASS"), str))
    check(rows, "mesh input remains open", "not proved" in contract["hypotheses"]["mesh_pointwise"].lower(), True, "not proved" in contract["hypotheses"]["mesh_pointwise"].lower())
    check(rows, "target source remains R-530", "R-530" in contract["scope"]["target"], True, "R-530" in contract["scope"]["target"])
    check(rows, "no physical claim", "qft" in json.dumps(contract["non_claims"]).lower() and "gravity" in json.dumps(contract["non_claims"]).lower(), True, "qft" in json.dumps(contract["non_claims"]).lower() and "gravity" in json.dumps(contract["non_claims"]).lower())

    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020MeshUniform.lean"), None)
    check(rows, "Lean registry entry", entry is not None, True, entry is not None)
    entry = entry or {}
    declarations = ["mesh_triangle_envelope", "mesh_refinement_strict", "primary_fixture", "independent_fixture"]
    check(rows, "Lean registry hash", entry.get("sha256"), sha(LEAN), entry.get("sha256") == sha(LEAN))
    check(rows, "Lean declarations", sorted(entry.get("declarations", [])), sorted(declarations), set(entry.get("declarations", [])) == set(declarations))
    check(rows, "Lean LF", b"\r" not in LEAN.read_bytes(), True, b"\r" not in LEAN.read_bytes())
    lean_text = LEAN.read_text(encoding="utf-8")
    check(rows, "Lean forbidden tokens", any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), False, not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")))

    env = os.environ.copy()
    paths = lean_path(args.lean_cache)
    if paths:
        env["LEAN_PATH"] = paths
    lean_result = subprocess.run([str(args.lean), str(LEAN)], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace") if args.lean.is_file() else None
    check(rows, "Lean compiler available", args.lean.is_file(), True, args.lean.is_file())
    lean_rc = lean_result.returncode if lean_result is not None else None
    lean_output = ((lean_result.stdout + lean_result.stderr).strip() if lean_result is not None else "")
    check(rows, "Lean compile", lean_rc, 0, lean_rc == 0)

    payload = {
        "schema": "tect/pah-omc020-mesh-uniform-integrated/1.0",
        "audit_id": "PAH-OMC-020-MESH-UNIFORM-INTEGRATED-001",
        "result_id": "R-545",
        "task_id": "T-065",
        "status": "PASS_INTEGRATED_CONDITIONAL_MESH_TRANSFER",
        "verdict": "PASS",
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
            "strategy/pa-hyp/PAH-OMC-020-mesh-uniform-contract-v1.json": sha(CONTRACT),
            "verification/scripts/pah_omc020_mesh_uniform.py": sha(PRIMARY),
            "codes/foundations/pah_omc020_mesh_uniform_independent.py": sha(INDEPENDENT),
            "codes/foundations/pah_omc020_mesh_uniform_hostile.py": sha(HOSTILE),
            "verification/scripts/pah_omc020_mesh_uniform_verify.py": sha(Path(__file__)),
            "verification/lean/Tect/PahOmc020MeshUniform.lean": sha(LEAN),
            "verification/lean/registry.json": sha(REGISTRY),
        },
        "finding": "All lanes verify the scalar mesh envelope and its conditional ordered implication. Actual PAH mesh-pointwise convergence and source-authorized common-space/path-space identification remain open.",
        "next_single_question": contract["single_next_question"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_mesh_uniform_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        "non_claims": contract["non_claims"],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 mesh-uniform integrated replay mismatch")
    print(f"PAH-OMC-020 MESH UNIFORM INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
