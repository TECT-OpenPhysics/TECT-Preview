#!/usr/bin/env python3
"""Integrated replay for the PAH-OMC-020 Mosco-resolvent contract."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-mosco-resolvent-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_mosco_resolvent.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_mosco_resolvent_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_mosco_resolvent_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020MoscoResolvent.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-mosco-resolvent"
)
OUTPUT = RUN_DIR / "integrated.json"
DEFAULT_LEAN = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--lean", type=Path, default=DEFAULT_LEAN)
    parser.add_argument("--lean-cache", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    check("contract schema", contract.get("schema"), "tect/pah-omc020-mosco-resolvent-contract/1.0",
          contract.get("schema") == "tect/pah-omc020-mosco-resolvent-contract/1.0")
    check("task", contract.get("task_id"), "T-080", contract.get("task_id") == "T-080")
    check("conditional firewalls",
          {key: contract["provenance"].get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")},
          {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False},
          all(contract["provenance"].get(key) is False for key in ("claim_bearing", "active_gate_change", "physical_promotion")))
    expected_fields = {
        "common_space_equicoercivity", "arbitrary_sequence_liminf", "recovery_sequence",
        "data_recovery", "target_exact_unique", "norm_upgrade", "semigroup_bridge",
    }
    check("owner field set", sorted(contract["required_owner_packet"]), sorted(expected_fields),
          set(contract["required_owner_packet"]) == expected_fields)

    commands = [
        ("primary", [sys.executable, "-X", "utf8", str(PRIMARY), "--check"]),
        ("independent", [sys.executable, "-X", "utf8", str(INDEPENDENT), "--check"]),
        ("hostile", [sys.executable, "-X", "utf8", str(HOSTILE), "--check"]),
    ]
    subprocesses: dict[str, dict[str, Any]] = {}
    for name, command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocesses[name] = {"returncode": result.returncode, "stdout": result.stdout.strip()}
        check(f"{name} replay", result.returncode, 0, result.returncode == 0)

    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    for name, run in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(f"{name} verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        flags = {key: run.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}
        check(f"{name} no promotion", flags,
              {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False},
              all(value is False for value in flags.values()))
    check("primary-independent target", primary["fixture"]["target_minimizer"], independent["fixture"]["target"],
          primary["fixture"]["target_minimizer"] == independent["fixture"]["target"])
    check("primary-independent minimizers", primary["fixture"]["minimizers"], independent["fixture"]["minimizers"],
          primary["fixture"]["minimizers"] == independent["fixture"]["minimizers"])
    check("hostile retained-term checks", hostile.get("checks_passed", 0), 25, hostile.get("checks_passed", 0) == 25)

    check("Lean LF", b"\r" not in LEAN.read_bytes(), True, b"\r" not in LEAN.read_bytes())
    lean_text = LEAN.read_text(encoding="utf-8")
    forbidden = {token: bool(re.search(rf"\b{re.escape(token)}\b", lean_text)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check("Lean forbidden tokens", forbidden, {token: False for token in forbidden}, not any(forbidden.values()))
    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020MoscoResolvent.lean"), None)
    check("Lean registry entry", entry is not None, True, entry is not None)
    if entry is None:
        entry = {}
    declarations = {
        "minimizer_le", "minimizer_unique", "oracle_target_minimizer",
        "oracle_sequence_error_decreases", "missing_liminf_blocks", "owner_packet_requires_all_fields",
    }
    check("Lean registry hash", entry.get("sha256"), digest(LEAN), entry.get("sha256") == digest(LEAN))
    check("Lean declarations", sorted(entry.get("declarations", [])), sorted(declarations),
          set(entry.get("declarations", [])) == declarations)
    env = os.environ.copy()
    paths = lean_path(args.lean_cache)
    if paths:
        env["LEAN_PATH"] = paths
    lean_result = subprocess.run([str(args.lean), str(LEAN)], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace") if args.lean.is_file() else None
    check("Lean compiler available", args.lean.is_file(), True, args.lean.is_file())
    lean_rc = lean_result.returncode if lean_result is not None else None
    lean_output = ((lean_result.stdout + lean_result.stderr).strip() if lean_result is not None else "")
    check("Lean compile", lean_rc, 0, lean_rc == 0)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-mosco-resolvent-integrated/1.0",
        "audit_id": "PAH-OMC-020-MOSCO-RESOLVENT-INTEGRATED-001",
        "task_id": "T-080",
        "status": "PASS_INTEGRATED_MOSCO_RESOLVENT_BOUNDARY",
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
        "subprocesses": subprocesses,
        "lean": {"command": [str(args.lean), str(LEAN)], "returncode": lean_rc, "output": lean_output},
        "source_hashes": {
            "strategy/pa-hyp/PAH-OMC-020-mosco-resolvent-contract-v1.json": digest(CONTRACT),
            "verification/scripts/pah_omc020_mosco_resolvent.py": digest(PRIMARY),
            "codes/foundations/pah_omc020_mosco_resolvent_independent.py": digest(INDEPENDENT),
            "codes/foundations/pah_omc020_mosco_resolvent_hostile.py": digest(HOSTILE),
            "verification/scripts/pah_omc020_mosco_resolvent_verify.py": digest(Path(__file__)),
            "verification/lean/Tect/PahOmc020MoscoResolvent.lean": digest(LEAN),
            "verification/lean/registry.json": digest(REGISTRY),
        },
        "owner_fields": contract["current_status"],
        "finding": "Integrated replay agrees that the variational resolvent selection implication is exact for the scalar fixture, while common-space equicoercivity, arbitrary-sequence liminf, recovery, norm upgrade and the separate semigroup bridge remain absent.",
        "next_single_question": contract["single_next_question"],
        "reproduction": contract["reproduction"],
        "non_claims": contract["non_claims"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 Mosco-resolvent integrated replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 MOSCO RESOLVENT INTEGRATED: PASS {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
