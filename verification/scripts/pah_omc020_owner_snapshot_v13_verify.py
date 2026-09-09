#!/usr/bin/env python3
"""Integrated current-byte owner snapshot v1.3 verifier."""

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
SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.3.json"
PRIMARY_SCRIPT = ROOT / "verification/scripts/pah_omc020_owner_packet_snapshot.py"
INDEPENDENT_SCRIPT = ROOT / "codes/foundations/pah_omc020_owner_snapshot_v11_independent.py"
HOSTILE_SCRIPT = ROOT / "codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-snapshot-v1.3"
OUTPUT = RUN_DIR / "integrated.json"


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
            handle.write(encoded); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok: raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def no_project_import(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc020_owner_snapshot_v13", "verification.scripts", "codes.foundations")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom): names = [node.module or ""]
        else: continue
        if any(any(token in name for token in forbidden) for name in names): return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    subprocesses: dict[str, dict[str, Any]] = {}
    commands = {
        "primary": [sys.executable, "-X", "utf8", str(PRIMARY_SCRIPT), "--snapshot", str(SNAPSHOT), "--output", str(RUN_DIR / "primary.json"), "--check"],
        "independent": [sys.executable, "-X", "utf8", str(INDEPENDENT_SCRIPT), "--snapshot", str(SNAPSHOT), "--output", str(RUN_DIR / "independent.json"), "--check"],
        "hostile": [sys.executable, "-X", "utf8", str(HOSTILE_SCRIPT), "--snapshot", str(SNAPSHOT), "--output", str(RUN_DIR / "hostile.json"), "--check"],
    }
    for name, command in commands.items():
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocesses[name] = {"returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        check(rows, f"{name} replay", result.returncode, 0, result.returncode == 0)
    snapshot = load(SNAPSHOT)
    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    check(rows, "snapshot id", snapshot.get("snapshot_id"), "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-003", snapshot.get("snapshot_id") == "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-003")
    check(rows, "fresh candidate count", snapshot.get("candidate_path_count"), 164, snapshot.get("candidate_path_count") == 164)
    check(rows, "fresh manifest", snapshot.get("manifest_sha256"), "ee56276cb87bd1c95f3230ab581b38151c94b92e85f5897b328612a5a6c3ed30", snapshot.get("manifest_sha256") == "ee56276cb87bd1c95f3230ab581b38151c94b92e85f5897b328612a5a6c3ed30")
    check(rows, "authorization remains empty", snapshot.get("authorized_paths"), [], snapshot.get("authorized_paths") == [] and snapshot.get("source_authorized_packet_present") is False)
    check(rows, "completion remains empty", snapshot.get("complete_paths"), [], snapshot.get("complete_paths") == [])
    for name, run in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(rows, f"{name} verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        flags = {key: run.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}
        check(rows, f"{name} firewalls", flags, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(value is False for value in flags.values()))
    check(rows, "primary count", primary.get("checks_passed", len(primary.get("checks", []))), 847, primary.get("checks_passed", len(primary.get("checks", []))) == 847)
    check(rows, "independent count", independent.get("checks_passed", len(independent.get("checks", []))), 667, independent.get("checks_passed", len(independent.get("checks", []))) == 667)
    check(rows, "hostile count", hostile.get("checks_passed", len(hostile.get("checks", []))), 10, hostile.get("checks_passed", len(hostile.get("checks", []))) == 10)
    check(rows, "independent non-importing", no_project_import(INDEPENDENT_SCRIPT), True, no_project_import(INDEPENDENT_SCRIPT))
    check(rows, "hostile non-importing", no_project_import(HOSTILE_SCRIPT), True, no_project_import(HOSTILE_SCRIPT))
    expected_snapshot_sha = "f2be a35647f54f305ac1fa3a3bc5bdf7e7078acb682cccb79da4e0eecd7d1638".replace(" ", "")
    check(rows, "source snapshot hash", sha(SNAPSHOT), expected_snapshot_sha, sha(SNAPSHOT) == expected_snapshot_sha)
    no_physical_claims = all(
        "no physical" in json.dumps(run.get("non_claims", [])).lower()
        for run in (primary, independent, hostile)
    )
    check(rows, "no physical promotion", no_physical_claims, True, no_physical_claims)
    payload = {
        "schema": "tect/pah-omc020-owner-snapshot-v13-integrated/1.0",
        "audit_id": "PAH-OMC-020-OWNER-SNAPSHOT-V13-INTEGRATED-001",
        "result_id": "R-547",
        "task_id": "T-064",
        "status": "PASS_FRESH_OWNER_SNAPSHOT_V13",
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
        "source_hashes": {
            "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.3.json": sha(SNAPSHOT),
            "verification/scripts/pah_omc020_owner_packet_snapshot.py": sha(PRIMARY_SCRIPT),
            "codes/foundations/pah_omc020_owner_snapshot_v11_independent.py": sha(INDEPENDENT_SCRIPT),
            "codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py": sha(HOSTILE_SCRIPT),
            "verification/scripts/pah_omc020_owner_snapshot_v13_verify.py": sha(Path(__file__)),
        },
        "finding": "A fresh current-byte v1.3 marker manifest includes 164 candidates after R-545/R-546, but authorized_paths and complete_paths remain empty. This is provenance only and not a universal no-go or semigroup theorem.",
        "next_single_question": "Can a source owner provide one versioned, hash-pinned packet containing the common H/U_n comparison, anchored N2b liminf/recovery, N2c/N4 boundary escape and exact R-512 minimal-form identification?",
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_owner_snapshot_v13_verify.py --check",
        "non_claims": ["No source-authorized U_n/common-Hilbert map, path law, N2b/N2c/N4/N2d closure or PAH-OMC-020 semigroup convergence.", "No universal impossibility theorem follows from the empty snapshot.", "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion."]
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded): raise SystemExit("owner snapshot v1.3 integrated replay mismatch")
    print(f"PAH-OMC-020 OWNER SNAPSHOT V1.3 INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
