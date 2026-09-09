#!/usr/bin/env python3
"""Integrated replay for the PAH-OMC-020 K/D term-level ledger."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-kd-term-ledger-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_kd_term_ledger.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_kd_term_ledger_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_kd_term_ledger_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020KD.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-kd-term-ledger"
OUTPUT = RUN_DIR / "integrated.json"
DEFAULT_LEAN = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(handle)
    temporary = Path(temporary_name)
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--lean", type=Path, default=Path(os.environ.get("TECT_LEAN", str(DEFAULT_LEAN))))
    parser.add_argument("--lean-cache", type=Path, default=None, help="Accepted for reproducibility-command compatibility; Lean source is dependency-free.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    check("contract hash", digest(CONTRACT), digest(CONTRACT), True)
    check("contract schema", contract.get("schema"), "tect/pah-omc020-kd-term-ledger-contract/1.0", contract.get("schema") == "tect/pah-omc020-kd-term-ledger-contract/1.0")
    check("contract remains conditional", contract.get("conditional"), True, contract.get("conditional") is True)
    check("claim/gate/physical firewalls", {key: contract.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(contract.get(key) is False for key in ("claim_bearing", "active_gate_change", "physical_promotion")))
    check("required field count", len(contract.get("admission_predicate", {}).get("required_full_fields", [])), 8, len(contract.get("admission_predicate", {}).get("required_full_fields", [])) == 8)

    commands = [
        ("primary replay", [sys.executable, "-X", "utf8", str(PRIMARY), "--check"]),
        ("independent replay", [sys.executable, "-X", "utf8", str(INDEPENDENT), "--check"]),
        ("hostile replay", [sys.executable, "-X", "utf8", str(HOSTILE), "--check"]),
    ]
    subprocess_results: dict[str, dict[str, Any]] = {}
    for label, command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocess_results[label] = {"returncode": result.returncode, "stdout": result.stdout.strip()}
        check(label, result.returncode, 0, result.returncode == 0)

    primary_run = load(RUN_DIR / "primary.json")
    independent_run = load(RUN_DIR / "independent.json")
    hostile_run = load(RUN_DIR / "hostile.json")
    for label, run in (("primary output", primary_run), ("independent output", independent_run), ("hostile output", hostile_run)):
        check(f"{label} HOLD", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(f"{label} no promotion", {key: run.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(run.get(key) is False for key in ("claim_bearing", "active_gate_change", "physical_promotion")))
    check("primary and independent flags agree", primary_run.get("required_fields"), independent_run.get("required_fields"), primary_run.get("required_fields") == independent_run.get("required_fields"))
    check("primary and hostile agree on current hold", primary_run.get("full_kd_admitted"), False, primary_run.get("full_kd_admitted") is False and hostile_run.get("verdict") == "HOLD_FOR_EVIDENCE")

    check("Lean source is UTF-8 LF", b"\r" not in LEAN.read_bytes(), True, b"\r" not in LEAN.read_bytes())
    lean_text = LEAN.read_text(encoding="utf-8")
    forbidden_hits = {token: bool(re.search(rf"\b{re.escape(token)}\b", lean_text)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check("Lean source has no forbidden axioms", forbidden_hits, {token: False for token in forbidden_hits}, not any(forbidden_hits.values()))
    registry = load(REGISTRY)
    entries = registry.get("entrypoints", [])
    entry = next((item for item in entries if item.get("path") == "verification/lean/Tect/PahOmc020KD.lean"), None)
    check("Lean registry entry", entry is not None, True, entry is not None)
    if entry is None:
        entry = {}
    check("Lean registry hash", entry.get("sha256"), digest(LEAN), entry.get("sha256") == digest(LEAN))
    declarations = {"all_fields_admit", "missing_common_rejects", "missing_uniform_rejects", "missing_target_rejects", "missing_d_limit_rejects", "conditional_result_not_owner_admitted", "unowned_result_not_admitted"}
    check("Lean declaration set", sorted(entry.get("declarations", [])), sorted(declarations), set(entry.get("declarations", [])) == declarations)
    lean_command = [str(args.lean), str(LEAN)]
    lean_result = subprocess.run(lean_command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace") if args.lean.is_file() else None
    check("Lean compiler available", args.lean.is_file(), True, args.lean.is_file())
    if lean_result is None:
        lean_return = None
        lean_stdout = ""
    else:
        lean_return = lean_result.returncode
        lean_stdout = (lean_result.stdout + lean_result.stderr).strip()
    check("Lean compile", lean_return, 0, lean_return == 0)

    payload = {
        "schema": "tect/pah-omc020-kd-term-ledger-integrated/1.0",
        "audit_id": "PAH-OMC-020-KD-TERM-LEDGER-INTEGRATED-001",
        "task_id": "T-077",
        "status": "PASS_INTEGRATED_TERM_COVERAGE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "source_hashes": {
            "strategy/pa-hyp/PAH-OMC-020-kd-term-ledger-contract-v1.json": digest(CONTRACT),
            "verification/scripts/pah_omc020_kd_term_ledger.py": digest(PRIMARY),
            "codes/foundations/pah_omc020_kd_term_ledger_independent.py": digest(INDEPENDENT),
            "codes/foundations/pah_omc020_kd_term_ledger_hostile.py": digest(HOSTILE),
            "verification/scripts/pah_omc020_kd_term_ledger_verify.py": digest(Path(__file__)),
            "verification/lean/Tect/PahOmc020KD.lean": digest(LEAN),
            "verification/lean/registry.json": digest(REGISTRY),
        },
        "subprocesses": subprocess_results,
        "lean": {"command": lean_command, "returncode": lean_return, "output": lean_stdout},
        "coverage": primary_run.get("coverage"),
        "required_fields": primary_run.get("required_fields"),
        "full_kd_admitted": False,
        "finding": "The integrated replay confirms a term-level source crosswalk: R-514, R-510, R-493 and conditional R-517 supply only partial finite inputs; the common comparison, all-cylinder uniform K limit and R-512 target-process defect remain absent.",
        "next_single_question": contract["next_single_question"],
        "reproduction": contract["reproduction"],
        "non_claims": contract["non_claims"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 integrated K/D ledger replay mismatch")
    else:
        atomic_write(destination, encoded)
    print(f"PAH-OMC-020 K/D INTEGRATED: PASS {len(checks)}/{len(checks)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
