#!/usr/bin/env python3
"""Integrated replay for R-557 owner-packet sufficiency evidence."""

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
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-packet-sufficiency"
OUTPUT = RUN_DIR / "integrated.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_owner_packet_sufficiency.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_owner_packet_sufficiency_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_owner_packet_sufficiency_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020OwnerPacketSufficiency.lean"
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
        raise AssertionError(name)


def no_import(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc020_owner_packet_sufficiency", "verification.scripts", "codes.foundations")
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
    check(rows, "contract result", contract.get("result_id"), "R-557", contract.get("result_id") == "R-557")
    for name, run in runs.items():
        check(rows, f"{name} hold verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(rows, f"{name} claim firewall", run.get("claim_bearing"), False, run.get("claim_bearing") is False)
        check(rows, f"{name} physical firewall", run.get("physical_promotion"), False, run.get("physical_promotion") is False)
        check(rows, f"{name} checks pass", all(item.get("status") == "PASS" for item in run.get("checks", [])), True, all(item.get("status") == "PASS" for item in run.get("checks", [])))
    check(rows, "independent non-importing", no_import(INDEPENDENT), True, no_import(INDEPENDENT))
    check(rows, "hostile non-importing", no_import(HOSTILE), True, no_import(HOSTILE))

    registry = load(LEAN_REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020OwnerPacketSufficiency.lean"), None)
    check(rows, "Lean registry entry", isinstance(entry, dict), True, isinstance(entry, dict))
    check(rows, "Lean source hash", entry.get("sha256") if isinstance(entry, dict) else None, sha(LEAN_SOURCE), isinstance(entry, dict) and entry.get("sha256") == sha(LEAN_SOURCE))
    required = {"ordered_error_from_complete_packet", "missing_root_field_rejects", "radial_partial_packet_rejects", "complete_packet_has_full_domain_terms"}
    declarations = set(entry.get("declarations", [])) if isinstance(entry, dict) else set()
    check(rows, "Lean declaration set", sorted(declarations), sorted(required), required.issubset(declarations))

    lake = find_lake()
    if lake is None:
        check(rows, "Lean compile", "UNAVAILABLE", "PASS", False)
        lean_run = {"status": "UNAVAILABLE", "command": "lake env lean Tect/PahOmc020OwnerPacketSufficiency.lean"}
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
        "schema": "tect/pah-omc020-owner-packet-sufficiency-integrated/1.0",
        "audit_id": "PAH-OMC-020-OWNER-PACKET-SUFFICIENCY-INTEGRATED-001",
        "result_id": "R-557",
        "task_id": "T-087",
        "status": "PASS_CONDITIONAL_PACKET_SUFFICIENCY_HOLD_FOR_EVIDENCE",
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
        "run_files": {f"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-packet-sufficiency/{name}.json": sha(RUN_DIR / f"{name}.json") for name in commands},
        "finding": "All four verification lanes agree that a complete ten-field owner packet is logically sufficient for the registered ordered-correlation conclusion, but the current corpus has no source-authorized packet and therefore remains HOLD_FOR_EVIDENCE.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_owner_packet_sufficiency_verify.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 owner-packet sufficiency integrated replay mismatch")
    print(f"PAH-OMC-020 OWNER PACKET SUFFICIENCY INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
