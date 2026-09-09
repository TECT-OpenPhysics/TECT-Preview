#!/usr/bin/env python3
"""Integrated current-byte replay for the PAH-OMC-020 N2b successor audit."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_n2b_common_space_audit_v11.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_n2b_common_space_audit_v11_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_n2b_common_space_audit_v11_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-n2b-common-space-audit-v1.1"
)
OUTPUT = RUN_DIR / "integrated.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json"
DEFAULT_LEAN = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe")


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

    check("intake contract schema", contract.get("schema"), "tect/pah-omc020-n2a-owner-packet-intake/1.1",
          contract.get("schema") == "tect/pah-omc020-n2a-owner-packet-intake/1.1")
    check("intake still false", contract["provenance"].get("source_authorized_packet_present"), False,
          contract["provenance"].get("source_authorized_packet_present") is False)
    check("no gate or physical promotion", {key: contract["provenance"].get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")},
          {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False},
          all(contract["provenance"].get(key) is False for key in ("claim_bearing", "active_gate_change", "physical_promotion")))

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

    primary = load(RUN_DIR / "result.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    for name, run in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(f"{name} verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        flags = {key: run.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}
        check(f"{name} firewalls", flags, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False},
              all(value is False for value in flags.values()))
    check("primary successor marker", primary.get("successor", {}).get("reason", ""), "stale pins repaired", "stale" in primary.get("successor", {}).get("reason", ""))
    check("independent empty candidates", independent.get("strict_owner_candidates"), [], independent.get("strict_owner_candidates") == [])
    check("hostile mutation coverage", hostile.get("checks_passed", 0), 12, hostile.get("checks_passed", 0) == 12)

    check("Lean LF", b"\r" not in LEAN.read_bytes(), True, b"\r" not in LEAN.read_bytes())
    lean_text = LEAN.read_text(encoding="utf-8")
    forbidden = {token: bool(re.search(rf"\b{re.escape(token)}\b", lean_text)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check("Lean forbidden tokens", forbidden, {token: False for token in forbidden}, not any(forbidden.values()))
    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020.lean"), None)
    check("Lean registry entry", entry is not None, True, entry is not None)
    if entry is None:
        entry = {}
    declarations = {"inverse_pair_form", "finite_sum_square_bound", "finite_sum_abs_bound", "radial_form_coefficient", "split_boundary_gap", "split_fibre_ratio_strict_decay"}
    check("Lean registry hash", entry.get("sha256"), sha(LEAN), entry.get("sha256") == sha(LEAN))
    check("Lean declarations", sorted(entry.get("declarations", [])), sorted(declarations), set(entry.get("declarations", [])) == declarations)
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
        "schema": "tect/pah-omc020-n2b-common-space-audit-integrated/1.1",
        "audit_id": "PAH-OMC-020-N2B-COMMON-SPACE-AUDIT-001-V1.1-INTEGRATED",
        "task_id": "T-064",
        "status": "PASS_INTEGRATED_N2B_CURRENT_BYTE_HOLD",
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
            "verification/scripts/pah_omc020_n2b_common_space_audit_v11.py": sha(PRIMARY),
            "codes/foundations/pah_omc020_n2b_common_space_audit_v11_independent.py": sha(INDEPENDENT),
            "codes/foundations/pah_omc020_n2b_common_space_audit_v11_hostile.py": sha(HOSTILE),
            "verification/scripts/pah_omc020_n2b_common_space_audit_v11_verify.py": sha(Path(__file__)),
            "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json": sha(CONTRACT),
            "verification/lean/Tect/PahOmc020.lean": sha(LEAN),
            "verification/lean/registry.json": sha(REGISTRY),
        },
        "finding": "Integrated current-byte replay confirms the original T-064 stale pins are repaired while the source-authorized N2b common-space owner packet remains absent.",
        "next_single_question": "Can one source-authorized owner provide the complete nine-field common-space packet, including arbitrary-sequence liminf, recovery, N2c/N4 boundary escape and R-512 minimal identification, without changing PAH-001?",
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit_v11_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        "non_claims": [
            "No PAH-OMC-020 semigroup convergence, Mosco theorem or universal impossibility theorem.",
            "No PAH functional, rate, state, carrier, regulator, normalization, time or limit-order change.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 N2b integrated v1.1 replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 N2B INTEGRATED V1.1: PASS {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
