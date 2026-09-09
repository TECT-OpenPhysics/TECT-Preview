#!/usr/bin/env python3
"""Integrated replay for the PAH-OMC-020 D_n identification boundary."""

from __future__ import annotations

import argparse
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-target-identification-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_target_identification.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_target_identification_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_target_identification_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020Target.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-target-identification"
OUTPUT = RUN_DIR / "integrated.json"
DEFAULT_LEAN = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(fd)
    temp = Path(name)
    try:
        temp.write_bytes(data)
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--lean", type=Path, default=Path(os.environ.get("TECT_LEAN", str(DEFAULT_LEAN))))
    parser.add_argument("--lean-cache", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    dest = args.output if args.output.is_absolute() else ROOT / args.output
    contract = read(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    check("contract schema", contract.get("schema"), "tect/pah-omc020-target-identification-contract/1.0", contract.get("schema") == "tect/pah-omc020-target-identification-contract/1.0")
    check("contract task", contract.get("task_id"), "T-078", contract.get("task_id") == "T-078")
    check("firewalls", {k: contract.get(k) for k in ("claim_bearing", "active_gate_change", "physical_promotion")}, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(contract.get(k) is False for k in ("claim_bearing", "active_gate_change", "physical_promotion")))
    check("route field counts", {k: len(contract["routes"][k]["required_fields"]) for k in ("form", "path")}, {"form": 5, "path": 5}, all(len(contract["routes"][k]["required_fields"]) == 5 for k in ("form", "path")))

    commands = [
        ("primary replay", [sys.executable, "-X", "utf8", str(PRIMARY), "--check"]),
        ("independent replay", [sys.executable, "-X", "utf8", str(INDEPENDENT), "--check"]),
        ("hostile replay", [sys.executable, "-X", "utf8", str(HOSTILE), "--check"]),
    ]
    subprocesses: dict[str, dict[str, Any]] = {}
    for name, command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocesses[name] = {"returncode": result.returncode, "stdout": result.stdout.strip()}
        check(name, result.returncode, 0, result.returncode == 0)

    primary = read(RUN_DIR / "primary.json")
    independent = read(RUN_DIR / "independent.json")
    hostile = read(RUN_DIR / "hostile.json")
    for name, run in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(f"{name} hold", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(f"{name} no promotion", {k: run.get(k) for k in ("claim_bearing", "active_gate_change", "physical_promotion")}, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(run.get(k) is False for k in ("claim_bearing", "active_gate_change", "physical_promotion")))
    check("primary-independent fields", primary.get("required_fields"), independent.get("required_fields"), primary.get("required_fields") == independent.get("required_fields"))
    check("current D false", primary.get("required_fields", {}).get("D_limit"), False, primary.get("required_fields", {}).get("D_limit") is False)
    check("hostile route mutations present", hostile.get("passed", 0) >= 20, True, hostile.get("passed", 0) >= 20)

    check("Lean UTF-8 LF", b"\r" not in LEAN.read_bytes(), True, b"\r" not in LEAN.read_bytes())
    lean_text = LEAN.read_text(encoding="utf-8")
    forbidden = {token: bool(re.search(rf"\b{re.escape(token)}\b", lean_text)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check("Lean forbidden tokens absent", forbidden, {token: False for token in forbidden}, not any(forbidden.values()))
    registry = read(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020Target.lean"), None)
    check("Lean registry entry", entry is not None, True, entry is not None)
    if entry is None:
        entry = {}
    declarations = {"form_route_needs_common", "form_route_needs_liminf", "form_route_needs_recovery", "form_route_needs_transfer", "path_route_needs_space", "path_route_needs_unique", "named_target_is_not_route", "target_route_requires_one_complete"}
    check("Lean registry hash", entry.get("sha256"), sha(LEAN), entry.get("sha256") == sha(LEAN))
    check("Lean declarations", sorted(entry.get("declarations", [])), sorted(declarations), set(entry.get("declarations", [])) == declarations)
    lean_result = subprocess.run([str(args.lean), str(LEAN)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace") if args.lean.is_file() else None
    check("Lean compiler available", args.lean.is_file(), True, args.lean.is_file())
    lean_rc = lean_result.returncode if lean_result is not None else None
    lean_out = ((lean_result.stdout + lean_result.stderr).strip() if lean_result is not None else "")
    check("Lean compile", lean_rc, 0, lean_rc == 0)

    payload = {
        "schema": "tect/pah-omc020-target-identification-integrated/1.0",
        "audit_id": "PAH-OMC-020-TARGET-IDENTIFICATION-INTEGRATED-001",
        "task_id": "T-078",
        "status": "PASS_INTEGRATED_TARGET_BOUNDARY",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "source_hashes": {
            "strategy/pa-hyp/PAH-OMC-020-target-identification-contract-v1.json": sha(CONTRACT),
            "verification/scripts/pah_omc020_target_identification.py": sha(PRIMARY),
            "codes/foundations/pah_omc020_target_identification_independent.py": sha(INDEPENDENT),
            "codes/foundations/pah_omc020_target_identification_hostile.py": sha(HOSTILE),
            "verification/scripts/pah_omc020_target_identification_verify.py": sha(Path(__file__)),
            "verification/lean/Tect/PahOmc020Target.lean": sha(LEAN),
            "verification/lean/registry.json": sha(REGISTRY),
        },
        "subprocesses": subprocesses,
        "lean": {"command": [str(args.lean), str(LEAN)], "returncode": lean_rc, "output": lean_out},
        "required_fields": primary.get("required_fields"),
        "route_status": primary.get("route_status"),
        "finding": "Integrated primary, independent, hostile and Lean replay agrees: the exact target form is present, but both admissible D_n identification routes remain incomplete and no semigroup promotion is justified.",
        "next_single_question": "Can a source-authorized packet complete either the form or path route with the declared anchored-n compact-time quantifiers?",
        "reproduction": contract["reproduction"],
        "non_claims": contract["non_claims"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not dest.is_file() or dest.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 target-identification integrated replay mismatch")
    else:
        write(dest, encoded)
    print(f"PAH-OMC-020 TARGET IDENTIFICATION INTEGRATED: PASS {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
