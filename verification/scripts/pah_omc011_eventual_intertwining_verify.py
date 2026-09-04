#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-011 HOLD_FOR_EVIDENCE packet."""

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


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json"
MANIFEST = REPO / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-manifest.json"
SOURCE = REPO / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = REPO / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = REPO / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
WEIGHT = REPO / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
LEAN = REPO / "verification/lean/Tect/R491.lean"
REGISTRY = REPO / "verification/lean/registry.json"
RUN_DIR = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc011-eventual-intertwining"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"

RESULT_ID = "R-491"
EXPLORATION_ID = "EXP-001457"
TASK_ID = "T-054"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path, normalize: bool = False) -> str:
    data = path.read_bytes()
    if normalize:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def run_script(path: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(path), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    payload = load(output) if output.is_file() else {}
    return {
        "returncode": process.returncode,
        "stdout": process.stdout[-2000:],
        "stderr": process.stderr[-2000:],
        "verification": payload.get("verification"),
        "verdict": payload.get("verdict"),
        "assertion_count": payload.get("assertion_count"),
        "passed": payload.get("passed"),
        "payload": payload,
    }


def find_lake(toolchain: str) -> Path | None:
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidates = [
        Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe",
        Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake",
        Path.home() / ".elan" / "bin" / "lake.exe",
        Path.home() / ".elan" / "bin" / "lake",
    ]
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def run_lean(registry: dict[str, Any]) -> dict[str, Any]:
    toolchain = registry["toolchain"]["toolchain"]
    lake = find_lake(toolchain)
    if lake is None:
        return {"status": "BLOCKED", "reason": "pinned lake executable missing", "command": "lake env lean Tect/R491.lean"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R491.lean"],
        cwd=REPO / "verification/lean",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=180,
    )
    output = f"{process.stdout}\n{process.stderr}"
    return {
        "status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": process.returncode,
        "command": "lake env lean Tect/R491.lean",
        "output": output[-4000:],
        "lake": str(lake),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    rows: list[dict[str, Any]] = []

    def add(name: str, passed: bool, actual: Any = None, expected: Any = True) -> None:
        rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    current = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-010": sha(WEIGHT),
        "PAH-OMC-011": sha(CONTRACT),
        "PAH-OMC-011-MANIFEST": sha(MANIFEST),
        "R491-Lean": sha(LEAN, normalize=True),
    }
    add("contract hash pinned", manifest["contract"]["sha256"] == current["PAH-OMC-011"], manifest["contract"]["sha256"], current["PAH-OMC-011"])
    add("parent hashes pinned", all(manifest["parents"][key]["sha256"] == current[pid] for key, pid in (("PAH-001", "PAH-001"), ("PAH-OMC-004", "PAH-OMC-004"), ("PAH-OMC-008", "PAH-OMC-008"), ("PAH-OMC-010", "PAH-OMC-010"))), {key: manifest["parents"][key]["sha256"] for key in ("PAH-001", "PAH-OMC-004", "PAH-OMC-008", "PAH-OMC-010")}, current)
    add("manifest status", manifest["status"] == "HOLD_FOR_EVIDENCE" and manifest["claim_bearing"] is False and manifest["active_gate_change"] is False, manifest, "HOLD_FOR_EVIDENCE/non-bearing/no gate change")
    add("firewall", all(value is True for value in contract["preservation_firewall"].values()) and manifest["no_parent_mutation"] is True, contract["preservation_firewall"], "all true")
    add("source identity", contract["contract_id"] == "PAH-OMC-011" and manifest["manifest_id"].startswith("PAH-OMC-011"), contract["contract_id"], "PAH-OMC-011")

    primary = run_script(REPO / "codes/foundations/pah_omc011_eventual_intertwining.py", RUN_DIR / "primary.json")
    independent = run_script(REPO / "codes/foundations/pah_omc011_eventual_intertwining_independent.py", RUN_DIR / "independent.json")
    hostile = run_script(REPO / "codes/foundations/pah_omc011_eventual_intertwining_hostile.py", RUN_DIR / "hostile.json")
    for label, item in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        add(f"{label} subprocess", item["returncode"] == 0 and item["verification"] == "PASS", item, "PASS")
    add("cross-lane HOLD verdict", all(item["verdict"] == "HOLD_FOR_EVIDENCE" for item in (primary, independent, hostile)), [item["verdict"] for item in (primary, independent, hostile)], "all HOLD_FOR_EVIDENCE")
    add("cross-lane projection obstruction", all(item.get("payload", {}).get("domain_obstruction", {}).get("projection_total") is False for item in (primary, independent)) and hostile["payload"].get("classification") == "HOSTILE_FIREWALL_REJECTS_ALL_STATE_OVERCLAIMS", {"primary": primary.get("payload", {}).get("domain_obstruction"), "independent": independent.get("payload", {}).get("domain_obstruction")}, "projection_total=false")
    add("N(f) and boundary evidence", primary.get("payload", {}).get("stabilization", {}).get("rows") and primary.get("payload", {}).get("boundary_defect", {}).get("hidden_diagonal_defect") == "16/9", {"stabilization": primary.get("payload", {}).get("stabilization"), "boundary": primary.get("payload", {}).get("boundary_defect")}, "N(f) rows and 16/9")
    add("C_sw role", primary.get("payload", {}).get("state_weighted_input", {}).get("C_sw") == 540 and primary.get("payload", {}).get("state_weighted_input", {}).get("intertwining_proved") is False, primary.get("payload", {}).get("state_weighted_input"), "domination only")
    add("weak L2 scope", primary.get("payload", {}).get("weak_gibbs_l2", {}).get("status") == "BLOCKED_UNDEFINED_LIFT_ON_FULL_DOMAIN" and primary.get("payload", {}).get("weak_gibbs_l2", {}).get("universal_failure_claimed") is False, primary.get("payload", {}).get("weak_gibbs_l2"), "blocked/undefined, no universal failure")

    registry_entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R491.lean"), None)
    lean_source = LEAN.read_text(encoding="utf-8")
    add("Lean registry entry", registry_entry is not None and registry_entry.get("sha256") == current["R491-Lean"], registry_entry, current["R491-Lean"])
    add("Lean source firewall", not any(re.search(rf"\b{re.escape(token)}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", True)
    declarations = manifest["lean"]["declarations"]
    add("Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in declarations), declarations, "all registered")
    lean = run_lean(registry)
    add("Lean compile", lean.get("status") == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc011-eventual-intertwining-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-011-EVENTUAL-INTERTWINING-INTEGRATED-001",
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": current,
        "runs": {"primary": primary, "independent": independent, "hostile": hostile, "lean": lean},
        "contract": contract["exact_scope"],
        "stabilization": contract["pre_registered_stabilization"],
        "domain_obstruction": contract["domain_obstruction"],
        "state_weighted_input": {"C_sw": 540, "role": "domination_only", "intertwining_proved": False},
        "weak_gibbs_l2": {"status": "BLOCKED_UNDEFINED_LIFT_ON_FULL_DOMAIN", "universal_failure_claimed": False},
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"R-491 INTEGRATED: {payload['verification']} ({payload['passed']}/{payload['assertion_count']}; Lean={lean.get('status')}; verdict=HOLD_FOR_EVIDENCE)")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
