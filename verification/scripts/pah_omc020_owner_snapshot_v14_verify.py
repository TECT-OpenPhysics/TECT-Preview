#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-020 owner-search snapshot v1.4."""

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
SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-snapshot-v1.4"
OUTPUT = RUN_DIR / "integrated.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_owner_packet_snapshot.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_owner_snapshot_v11_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


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


def no_project_import(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc020_owner_snapshot_v14", "verification.scripts", "codes.foundations")
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    commands = {
        "primary": [sys.executable, "-X", "utf8", str(PRIMARY), "--snapshot", str(SNAPSHOT), "--output", str(RUN_DIR / "primary.json"), "--check"],
        "independent": [sys.executable, "-X", "utf8", str(INDEPENDENT), "--snapshot", str(SNAPSHOT), "--output", str(RUN_DIR / "independent.json"), "--check"],
        "hostile": [sys.executable, "-X", "utf8", str(HOSTILE), "--snapshot", str(SNAPSHOT), "--output", str(RUN_DIR / "hostile.json"), "--check"],
    }
    replay: dict[str, dict[str, Any]] = {}
    for name, command in commands.items():
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        replay[name] = {"returncode": process.returncode, "command": " ".join(command)}
        check(rows, f"{name} replay", process.returncode, 0, process.returncode == 0)

    snapshot = load(SNAPSHOT)
    runs = {name: load(RUN_DIR / f"{name}.json") for name in commands}
    records = snapshot.get("candidate_records")
    check(rows, "snapshot id", snapshot.get("snapshot_id"), "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-004", snapshot.get("snapshot_id") == "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-004")
    check(rows, "snapshot schema", snapshot.get("schema"), "tect/pah-omc020-owner-search-snapshot/1.0", snapshot.get("schema") == "tect/pah-omc020-owner-search-snapshot/1.0")
    check(rows, "candidate list", isinstance(records, list), "list", isinstance(records, list))
    paths = [record.get("path") for record in records] if isinstance(records, list) else []
    check(rows, "candidate paths sorted and unique", paths, sorted(set(paths)), paths == sorted(set(paths)))
    check(rows, "candidate count self-consistent", snapshot.get("candidate_path_count"), len(paths), snapshot.get("candidate_path_count") == len(paths))
    check(rows, "manifest digest", snapshot.get("manifest_sha256"), hashlib.sha256(canonical(records)).hexdigest(), snapshot.get("manifest_sha256") == hashlib.sha256(canonical(records)).hexdigest())
    check(rows, "authorization remains empty", snapshot.get("authorized_paths"), [], snapshot.get("authorized_paths") == [] and snapshot.get("source_authorized_packet_present") is False)
    check(rows, "completion remains empty", snapshot.get("complete_paths"), [], snapshot.get("complete_paths") == [])
    check(rows, "primary all checks pass", all(item.get("status") == "PASS" for item in runs["primary"].get("checks", [])), True, all(item.get("status") == "PASS" for item in runs["primary"].get("checks", [])))
    check(rows, "independent all checks pass", all(item.get("status") == "PASS" for item in runs["independent"].get("checks", [])), True, all(item.get("status") == "PASS" for item in runs["independent"].get("checks", [])))
    check(rows, "hostile all checks pass", all(item.get("status") == "PASS" for item in runs["hostile"].get("checks", [])), True, all(item.get("status") == "PASS" for item in runs["hostile"].get("checks", [])))
    for name, run in runs.items():
        check(rows, f"{name} verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(rows, f"{name} claim firewall", run.get("claim_bearing"), False, run.get("claim_bearing") is False)
        check(rows, f"{name} gate firewall", run.get("active_gate_change"), False, run.get("active_gate_change") is False)
        check(rows, f"{name} physical firewall", run.get("physical_promotion"), False, run.get("physical_promotion") is False)
    check(rows, "independent non-importing", no_project_import(INDEPENDENT), True, no_project_import(INDEPENDENT))
    check(rows, "hostile non-importing", no_project_import(HOSTILE), True, no_project_import(HOSTILE))
    check(rows, "no physical promotion text", "no physical" in json.dumps(snapshot.get("non_claims", [])).lower(), True, "no physical" in json.dumps(snapshot.get("non_claims", [])).lower())

    payload = {
        "schema": "tect/pah-omc020-owner-snapshot-v14-integrated/1.0",
        "audit_id": "PAH-OMC-020-OWNER-SNAPSHOT-V14-INTEGRATED-001",
        "result_id": "R-554",
        "task_id": "T-064",
        "status": "PASS_FRESH_OWNER_SNAPSHOT_V14",
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
        "source_hashes": {
            "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json": sha(SNAPSHOT),
            "verification/scripts/pah_omc020_owner_packet_snapshot.py": sha(PRIMARY),
            "codes/foundations/pah_omc020_owner_snapshot_v11_independent.py": sha(INDEPENDENT),
            "codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py": sha(HOSTILE),
            "verification/scripts/pah_omc020_owner_snapshot_v14_verify.py": sha(Path(__file__)),
        },
        "finding": "The fresh v1.4 current-byte manifest replays with independent and hostile controls, but its source-authorized and complete owner sets are both empty. This is repository provenance only and does not construct a common space, path law or semigroup limit.",
        "snapshot": {
            "snapshot_id": snapshot.get("snapshot_id"),
            "candidate_path_count": snapshot.get("candidate_path_count"),
            "manifest_sha256": snapshot.get("manifest_sha256"),
            "authorized_paths": snapshot.get("authorized_paths"),
            "complete_paths": snapshot.get("complete_paths"),
        },
        "run_files": {f"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-snapshot-v1.4/{name}.json": sha(RUN_DIR / f"{name}.json") for name in commands},
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_owner_snapshot_v14_verify.py --check",
        "next_single_question": "Can a source owner supply one versioned, hash-pinned packet containing the common H/U_n comparison, anchored N2b liminf/recovery, N2c/N4 boundary escape and exact R-512 minimal-form identification?",
        "non_claims": [
            "No source-authorized U_n/common-Hilbert map, path-space law, non-explosion/uniqueness theorem, N2b liminf/recovery, N2c/N4 boundary escape, N2d minimal-form identification or PAH-OMC-020 semigroup convergence.",
            "The empty current snapshot is not a universal impossibility theorem or exact counterexample.",
            "No PAH-001 functional, rate, state, carrier, regulator, normalization, external Markov time or limit-order change.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("owner snapshot v1.4 integrated replay mismatch")
    print(f"PAH-OMC-020 OWNER SNAPSHOT V1.4 INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
