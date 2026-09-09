#!/usr/bin/env python3
"""Integrated replay for PAH-OMC-021 composite owner-packet transfer."""

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
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc021-composite-owner-packet-transfer"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-021-composite-owner-packet-transfer-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc021_composite_owner_packet_transfer.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc021_composite_owner_packet_transfer_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc021_composite_owner_packet_transfer_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc021CompositeOwnerPacketTransfer.lean"
REGISTRY = ROOT / "verification/lean/registry.json"


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
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def no_import(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc021_composite_owner_packet_transfer", "verification.scripts", "codes.foundations")
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        if any(any(token in name for token in forbidden) for name in names):
            return False
    return True


def find_lake() -> Path | None:
    candidates = sorted((Path.home() / ".elan/toolchains").glob("*/bin/lake.exe"))
    preferred = [path for path in candidates if "leanprover--lean4---v4.32.1" in str(path)]
    return (preferred or candidates)[0] if (preferred or candidates) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "integrated.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    replay: dict[str, dict[str, Any]] = {}
    for name, script in (("primary", PRIMARY), ("independent", INDEPENDENT), ("hostile", HOSTILE)):
        command = [sys.executable, "-X", "utf8", str(script), "--check"]
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        replay[name] = {"returncode": process.returncode, "command": " ".join(command), "stdout": process.stdout.strip(), "stderr": process.stderr.strip()}
        check(rows, f"{name} replay", process.returncode, 0, process.returncode == 0)

    contract = load(CONTRACT)
    runs = {name: load(RUN_DIR / f"{name}.json") for name in ("primary", "independent", "hostile")}
    check(rows, "contract identity", contract.get("result_id"), "R-558", contract.get("result_id") == "R-558")
    for name, run in runs.items():
        check(rows, f"{name} hold verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(rows, f"{name} claim firewall", run.get("claim_bearing"), False, run.get("claim_bearing") is False)
        check(rows, f"{name} physical firewall", run.get("physical_promotion"), False, run.get("physical_promotion") is False)
        check(rows, f"{name} all checks pass", all(item.get("status") == "PASS" for item in run.get("checks", [])), True, all(item.get("status") == "PASS" for item in run.get("checks", [])))
    check(rows, "independent non-importing", no_import(INDEPENDENT), True, no_import(INDEPENDENT))
    check(rows, "hostile non-importing", no_import(HOSTILE), True, no_import(HOSTILE))

    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc021CompositeOwnerPacketTransfer.lean"), None)
    declarations = {"finite_common_fields_are_not_ordered_fields", "finite_fields_do_not_admit", "status_only_asymptotic_fill_does_not_admit"}
    check(rows, "Lean registry entry", isinstance(entry, dict), True, isinstance(entry, dict))
    check(rows, "Lean source hash", entry.get("sha256") if isinstance(entry, dict) else None, digest(LEAN), isinstance(entry, dict) and entry.get("sha256") == digest(LEAN))
    check(rows, "Lean declarations", sorted(entry.get("declarations", [])) if isinstance(entry, dict) else [], sorted(declarations), isinstance(entry, dict) and declarations.issubset(set(entry.get("declarations", []))))

    lake = find_lake()
    if lake is None:
        check(rows, "Lean compile", "UNAVAILABLE", "PASS", False)
        lean_run = {"status": "UNAVAILABLE", "command": "lake env lean Tect/PahOmc021CompositeOwnerPacketTransfer.lean"}
    else:
        lean_cwd = ROOT / "verification/lean"
        if Path(r"E:\Dev\TECT\verification\lean").is_dir():
            lean_cwd = Path(r"E:\Dev\TECT\verification\lean")
        environment = os.environ.copy()
        environment.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "safe.directory", "GIT_CONFIG_VALUE_0": "*"})
        command = [str(lake), "env", "lean", str(LEAN)]
        process = subprocess.run(command, cwd=lean_cwd, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace")
        lean_run = {"status": "PASS" if process.returncode == 0 else "FAIL", "returncode": process.returncode, "command": " ".join(command), "cwd": str(lean_cwd), "stdout": process.stdout.strip(), "stderr": process.stderr.strip()}
        check(rows, "Lean compile", process.returncode, 0, process.returncode == 0)

    payload = {
        "schema": "tect/pah-omc021-composite-owner-packet-transfer-integrated/1.0",
        "audit_id": "PAH-OMC-021-COMPOSITE-OWNER-PACKET-TRANSFER-INTEGRATED-001",
        "result_id": "R-558",
        "task_id": "T-088",
        "status": "PASS_COMPOSITE_FINITE_FIELDS_ONLY_HOLD_FOR_EVIDENCE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "replay": replay,
        "lean": lean_run,
        "source_hashes": {str(path.relative_to(ROOT)): digest(path) for path in (CONTRACT, PRIMARY, INDEPENDENT, HOSTILE, LEAN, Path(__file__))},
        "child_run_hashes": {name: digest(RUN_DIR / f"{name}.json") for name in ("primary", "independent", "hostile")},
        "finding": "All lanes agree that the finite composite owner packet is real but cannot be transferred into the R-557 source-authorized ordered proof: PAH-OMC-001 is a researcher successor and the six asymptotic fields remain missing.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc021_composite_owner_packet_transfer_verify.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-021 integrated replay mismatch")
    print(f"PAH-OMC-021 COMPOSITE OWNER PACKET INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
