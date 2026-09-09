#!/usr/bin/env python3
"""Integrated replay for PAH-OMC-020 ordered-epsilon bridge evidence."""

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
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-ordered-epsilon-bridge"
OUTPUT = RUN_DIR / "integrated.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-ordered-epsilon-bridge-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_ordered_epsilon_bridge.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_ordered_epsilon_bridge_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_ordered_epsilon_bridge_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020OrderedEpsilon.lean"
LEAN_REGISTRY = ROOT / "verification/lean/registry.json"


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
    forbidden = ("pah_omc020_ordered_epsilon_bridge", "verification.scripts", "codes.foundations")
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
        replay[name] = {"returncode": process.returncode, "command": " ".join(command), "stdout": process.stdout.strip()}
        check(rows, f"{name} replay", process.returncode, 0, process.returncode == 0)

    contract = load(CONTRACT)
    runs = {name: load(RUN_DIR / f"{name}.json") for name in commands}
    check(rows, "contract result", contract.get("result_id"), "R-555", contract.get("result_id") == "R-555")
    check(rows, "primary checks", all(item.get("status") == "PASS" for item in runs["primary"].get("checks", [])), True, all(item.get("status") == "PASS" for item in runs["primary"].get("checks", [])))
    check(rows, "independent checks", all(item.get("status") == "PASS" for item in runs["independent"].get("checks", [])), True, all(item.get("status") == "PASS" for item in runs["independent"].get("checks", [])))
    check(rows, "hostile checks", all(item.get("status") == "PASS" for item in runs["hostile"].get("checks", [])), True, all(item.get("status") == "PASS" for item in runs["hostile"].get("checks", [])))
    for name, run in runs.items():
        check(rows, f"{name} conditional verdict", run.get("verdict"), "PASS_CONDITIONAL", run.get("verdict") == "PASS_CONDITIONAL")
        check(rows, f"{name} claim firewall", run.get("claim_bearing"), False, run.get("claim_bearing") is False)
        check(rows, f"{name} physical firewall", run.get("physical_promotion"), False, run.get("physical_promotion") is False)
    check(rows, "independent non-importing", no_project_import(INDEPENDENT), True, no_project_import(INDEPENDENT))
    check(rows, "hostile non-importing", no_project_import(HOSTILE), True, no_project_import(HOSTILE))

    registry = load(LEAN_REGISTRY)
    entries = registry.get("entrypoints", [])
    lean_entry = next((item for item in entries if item.get("path") == "verification/lean/Tect/PahOmc020OrderedEpsilon.lean"), None)
    check(rows, "Lean registry entry", isinstance(lean_entry, dict), "entry", isinstance(lean_entry, dict))
    check(rows, "Lean source hash", lean_entry.get("sha256") if isinstance(lean_entry, dict) else None, sha(LEAN_SOURCE), isinstance(lean_entry, dict) and lean_entry.get("sha256") == sha(LEAN_SOURCE))
    declarations = set(lean_entry.get("declarations", [])) if isinstance(lean_entry, dict) else set()
    check(rows, "Lean theorem declarations", sorted(declarations), sorted({"ordered_epsilon_bridge", "ordered_epsilon_bridge_requires_both_terms", "split_fixture"}), declarations.issuperset({"ordered_epsilon_bridge", "ordered_epsilon_bridge_requires_both_terms", "split_fixture"}))
    lake = find_lake()
    lean_run: dict[str, Any]
    if lake is None:
        lean_run = {"status": "UNAVAILABLE", "command": "lake env lean Tect/PahOmc020OrderedEpsilon.lean"}
        check(rows, "Lean compile", "UNAVAILABLE", "PASS", False)
    else:
        lean_cwd = Path(r"E:\Dev\TECT\verification\lean")
        if not lean_cwd.is_dir():
            lean_cwd = ROOT / "verification/lean"
        command = [str(lake), "env", "lean", str(LEAN_SOURCE)]
        lean_env = os.environ.copy()
        # The bundled canonical mathlib checkout may be owned by the operator
        # account while this verifier runs as the sandbox account.  Scope the
        # safe-directory exception to this read-only Lean subprocess only.
        lean_env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "safe.directory", "GIT_CONFIG_VALUE_0": "*"})
        process = subprocess.run(command, cwd=lean_cwd, env=lean_env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        lean_run = {"status": "PASS" if process.returncode == 0 else "FAIL", "returncode": process.returncode, "command": " ".join(command), "cwd": str(lean_cwd), "stdout": process.stdout.strip(), "stderr": process.stderr.strip()}
        check(rows, "Lean compile", process.returncode, 0, process.returncode == 0)

    payload = {
        "schema": "tect/pah-omc020-ordered-epsilon-bridge-integrated/1.0",
        "audit_id": "PAH-OMC-020-ORDERED-EPSILON-BRIDGE-INTEGRATED-001",
        "result_id": "R-555",
        "task_id": "T-064",
        "status": "PASS_CONDITIONAL_ORDERED_EPSILON_BRIDGE",
        "verdict": "PASS_CONDITIONAL",
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
        "run_files": {f"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-ordered-epsilon-bridge/{name}.json": sha(RUN_DIR / f"{name}.json") for name in commands},
        "finding": "Primary, non-importing independent, hostile and Lean replay agree on the exact abstract j-before-n epsilon bridge. This does not instantiate the PAH-specific J and D estimates or advance the semigroup convergence gate.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_ordered_epsilon_bridge_verify.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 ordered-epsilon integrated replay mismatch")
    print(f"PAH-OMC-020 ORDERED-EPSILON INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=PASS_CONDITIONAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
