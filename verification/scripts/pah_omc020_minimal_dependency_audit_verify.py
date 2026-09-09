#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean replay for R-556."""

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
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-minimal-dependency-audit"
OUTPUT = RUN_DIR / "integrated.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-minimal-dependency-audit-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_minimal_dependency_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_minimal_dependency_audit_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_minimal_dependency_audit_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020MinimalDependency.lean"
LEAN_REGISTRY = ROOT / "verification/lean/registry.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def no_imports(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc020_minimal_dependency_audit", "verification.scripts", "codes.foundations")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        if any(any(token in name for token in forbidden) for name in names):
            return False
    return True


def find_lake() -> Path | None:
    candidates = sorted((Path.home() / ".elan/toolchains").glob("*/bin/lake.exe"))
    preferred = [path for path in candidates if "leanprover--lean4---v4.32.1" in str(path)]
    return (preferred or candidates)[0] if (preferred or candidates) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    commands = {
        "primary": [sys.executable, "-X", "utf8", str(PRIMARY), "--check"],
        "independent": [sys.executable, "-X", "utf8", str(INDEPENDENT), "--check"],
        "hostile": [sys.executable, "-X", "utf8", str(HOSTILE), "--check"],
    }
    replay: dict[str, dict[str, Any]] = {}
    for name, command in commands.items():
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        replay[name] = {"returncode": process.returncode, "command": " ".join(command), "stdout": process.stdout.strip(), "stderr": process.stderr.strip()}
        check(rows, f"{name} replay", process.returncode, 0, process.returncode == 0)

    contract = load(CONTRACT)
    runs = {name: load(RUN_DIR / f"{name}.json") for name in commands}
    check(rows, "result identity", contract.get("result_id"), "R-556", contract.get("result_id") == "R-556")
    check(rows, "primary hold verdict", runs["primary"].get("verdict"), "HOLD_FOR_EVIDENCE", runs["primary"].get("verdict") == "HOLD_FOR_EVIDENCE")
    check(rows, "independent hold verdict", runs["independent"].get("verdict"), "HOLD_FOR_EVIDENCE", runs["independent"].get("verdict") == "HOLD_FOR_EVIDENCE")
    check(rows, "hostile hold verdict", runs["hostile"].get("verdict"), "HOLD_FOR_EVIDENCE", runs["hostile"].get("verdict") == "HOLD_FOR_EVIDENCE")
    for name, run in runs.items():
        check(rows, f"{name} claim firewall", run.get("claim_bearing"), False, run.get("claim_bearing") is False)
        check(rows, f"{name} physical firewall", run.get("physical_promotion"), False, run.get("physical_promotion") is False)
        check(rows, f"{name} checks pass", all(item.get("status") == "PASS" for item in run.get("checks", [])), True, all(item.get("status") == "PASS" for item in run.get("checks", [])))
    check(rows, "independent non-importing", no_imports(INDEPENDENT), True, no_imports(INDEPENDENT))
    check(rows, "hostile non-importing", no_imports(HOSTILE), True, no_imports(HOSTILE))

    registry = load(LEAN_REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020MinimalDependency.lean"), None)
    check(rows, "Lean registry entry", isinstance(entry, dict), True, isinstance(entry, dict))
    check(rows, "Lean source hash", entry.get("sha256") if isinstance(entry, dict) else None, sha(LEAN_SOURCE), isinstance(entry, dict) and entry.get("sha256") == sha(LEAN_SOURCE))
    declarations = set(entry.get("declarations", [])) if isinstance(entry, dict) else set()
    required = {"full_ready_of_all_fields", "open_root_blocks_full", "radial_support_is_not_full_without_owner", "conditional_bridge_needs_both"}
    check(rows, "Lean declarations", sorted(declarations), sorted(required), required.issubset(declarations))

    lake = find_lake()
    if lake is None:
        check(rows, "Lean compile", "UNAVAILABLE", "PASS", False)
        lean_run = {"status": "UNAVAILABLE", "command": "lake env lean Tect/PahOmc020MinimalDependency.lean"}
    else:
        lean_cwd = ROOT / "verification/lean"
        if Path(r"E:\Dev\TECT\verification\lean").is_dir():
            lean_cwd = Path(r"E:\Dev\TECT\verification\lean")
        environment = os.environ.copy()
        environment.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "safe.directory", "GIT_CONFIG_VALUE_0": "*"})
        command = [str(lake), "env", "lean", str(LEAN_SOURCE)]
        process = subprocess.run(command, cwd=lean_cwd, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace")
        lean_run = {"status": "PASS" if process.returncode == 0 else "FAIL", "returncode": process.returncode, "command": " ".join(command), "cwd": str(lean_cwd), "stdout": process.stdout.strip(), "stderr": process.stderr.strip()}
        check(rows, "Lean compile", process.returncode, 0, process.returncode == 0)

    payload = {
        "schema": "tect/pah-omc020-minimal-dependency-audit-integrated/1.0",
        "audit_id": "PAH-OMC-020-MINIMAL-DEPENDENCY-AUDIT-INTEGRATED-001",
        "result_id": "R-556",
        "task_id": "T-086",
        "status": "HOLD_FOR_EVIDENCE_MINIMAL_DEPENDENCY_LEDGER",
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
        "replay": replay,
        "lean": lean_run,
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (CONTRACT, PRIMARY, INDEPENDENT, HOSTILE, LEAN_SOURCE, Path(__file__))},
        "run_files": {f"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-minimal-dependency-audit/{name}.json": sha(RUN_DIR / f"{name}.json") for name in commands},
        "finding": "All four verification lanes agree on a bounded dependency ledger: R-555 is the exact ordered implication, R-514/R-548 are restricted inputs, and the full-domain route remains held by three source-owned obligations.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_minimal_dependency_audit_verify.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 minimal dependency integrated replay mismatch")
    print(f"PAH-OMC-020 MINIMAL DEPENDENCY INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
