#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-010 state-weighted envelope packet."""

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
CONTRACT = REPO / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
MANIFEST = REPO / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json"
SOURCE = REPO / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = REPO / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = REPO / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
PRECEDING = REPO / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json"
PRIMARY_SCRIPT = REPO / "codes/foundations/pah_omc010_state_weighted_envelope.py"
INDEPENDENT_SCRIPT = REPO / "codes/foundations/pah_omc010_state_weighted_envelope_independent.py"
HOSTILE_SCRIPT = REPO / "codes/foundations/pah_omc010_state_weighted_envelope_hostile.py"
LEAN = REPO / "verification/lean/Tect/R490.lean"
REGISTRY = REPO / "verification/lean/registry.json"
RUN_DIR = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"

RESULT_ID = "R-490"
EXPLORATION_ID = "EXP-001438"
TASK_ID = "T-054"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path, normalize: bool = False) -> str:
    raw = path.read_bytes()
    if normalize:
        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


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


def find_lake(toolchain: str) -> Path | None:
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidates = [
        Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe",
        Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake",
        Path.home() / ".elan" / "bin" / "lake.exe",
        Path.home() / ".elan" / "bin" / "lake",
    ]
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def run_script(script: Path, output: Path) -> dict[str, Any]:
    command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
    process = subprocess.run(command, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    payload = load(output) if output.is_file() else {}
    return {
        "returncode": process.returncode,
        "stdout": process.stdout[-2000:],
        "stderr": process.stderr[-2000:],
        "verification": payload.get("verification"),
        "verdict": payload.get("verdict"),
        "assertion_count": payload.get("assertion_count"),
        "payload": payload,
    }


def run_lean() -> dict[str, Any]:
    toolchain = load(REGISTRY)["toolchain"]["toolchain"]
    lake = find_lake(toolchain)
    if lake is None:
        return {"status": "BLOCKED", "reason": "pinned lake executable missing", "command": "lake env lean Tect/R490.lean"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R490.lean"],
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
        "command": "lake env lean Tect/R490.lean",
        "output": output[-4000:],
        "lake": str(lake),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    source_hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-009": sha(PRECEDING),
        "PAH-OMC-010": sha(CONTRACT),
        "PAH-OMC-010-MANIFEST": sha(MANIFEST),
        "R490-Lean": sha(LEAN, normalize=True),
    }
    rows: list[dict[str, Any]] = []

    def add(name: str, passed: bool, actual: Any = None, expected: Any = True) -> None:
        rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    add("contract hash pinned", manifest["contract"]["sha256"] == source_hashes["PAH-OMC-010"], manifest["contract"]["sha256"], source_hashes["PAH-OMC-010"])
    add("parent hashes pinned", all(manifest[key]["sha256"] == source_hashes[value] for key, value in (("functional_source", "PAH-001"), ("geometric_source", "PAH-OMC-004"), ("starting_result", "PAH-OMC-008"), ("preceding_negative", "PAH-OMC-009"))), {key: manifest[key]["sha256"] for key in ("functional_source", "geometric_source", "starting_result", "preceding_negative")}, "current parent hashes")
    add("source IDs", contract["contract_id"] == "PAH-OMC-010" and manifest["manifest_id"].startswith("PAH-OMC-010"), contract["contract_id"], "PAH-OMC-010")
    add("firewall", all(contract["preservation_firewall"].values()) and manifest["no_parent_mutation"] and manifest["no_new_finite_fixture"], contract["preservation_firewall"], "all preservation flags true")
    add("physical firewall", manifest["physical_promotion"] is False and contract["provenance"]["physical_authority"] is False, {"manifest": manifest["physical_promotion"], "authority": contract["provenance"]["physical_authority"]}, "false")

    primary_output = RUN_DIR / "primary.json"
    independent_output = RUN_DIR / "independent.json"
    hostile_output = RUN_DIR / "hostile.json"
    primary = run_script(PRIMARY_SCRIPT, primary_output)
    independent = run_script(INDEPENDENT_SCRIPT, independent_output)
    hostile = run_script(HOSTILE_SCRIPT, hostile_output)
    add("primary subprocess", primary["returncode"] == 0 and primary["verification"] == "PASS", primary, "PASS")
    add("independent subprocess", independent["returncode"] == 0 and independent["verification"] == "PASS", independent, "PASS")
    add("hostile subprocess", hostile["returncode"] == 0 and hostile["verification"] == "PASS", hostile, "PASS")
    add("cross-lane verdict", all(item["verdict"] == "MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE" for item in (primary, independent, hostile)), [item["verdict"] for item in (primary, independent, hostile)], "all MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE")
    add("cross-lane constants", primary.get("payload", {}).get("family", {}).get("S_geom") == independent.get("payload", {}).get("derived", {}).get("S_geom") == 8 and primary.get("payload", {}).get("family", {}).get("N_geom") == independent.get("payload", {}).get("derived", {}).get("N_geom") == 60 and primary.get("payload", {}).get("family", {}).get("C_sw") == independent.get("payload", {}).get("derived", {}).get("C_sw") == 540, {"primary": primary.get("payload", {}).get("family"), "independent": independent.get("payload", {}).get("derived")}, {"S_geom": 8, "N_geom": 60, "C_sw": 540})
    add("R-488 nonzero observables", primary.get("payload", {}).get("r488_observables", {}).get("positive_norm_for_all_finite_n_R") is True and all(value != 0 for value in primary.get("payload", {}).get("r488_observables", {}).get("values", {}).values()), primary.get("payload", {}).get("r488_observables"), "four nonzero witness values")
    add("conditional common-core boundary", "not_proved" in primary.get("payload", {}).get("common_core_input", {}) and "CONDITIONAL" in primary.get("payload", {}).get("common_core_input", {}).get("status", ""), primary.get("payload", {}).get("common_core_input"), "separate intertwining remains")

    registry_entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R490.lean"), None)
    lean_source = LEAN.read_text(encoding="utf-8")
    add("Lean registry entry", registry_entry is not None and registry_entry.get("sha256") == source_hashes["R490-Lean"], registry_entry, source_hashes["R490-Lean"])
    add("Lean source firewall", not any(re.search(rf"\b{re.escape(token)}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "escape tokens absent", True)
    required_declarations = registry_entry.get("declarations", []) if registry_entry else []
    add("Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in required_declarations), required_declarations, "registered declarations")
    lean = run_lean()
    add("Lean compile", lean.get("status") == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc010-state-weighted-envelope-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-010-STATE-WEIGHTED-ENVELOPE-INTEGRATED-001",
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE" if not failed else "HOLD_FOR_EVIDENCE",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": source_hashes,
        "contract": contract["exact_scope"],
        "runs": {"primary": primary, "independent": independent, "hostile": hostile, "lean": lean},
        "derived": {"S_geom": 8, "N_geom": 60, "C_sw": 540, "per_root_conductance_bound": 1},
        "claim_bearing": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": manifest["reproduction"],
    }
    atomic_json(output, payload)
    print(f"R-490 INTEGRATED: {payload['verification']} ({payload['passed']}/{payload['assertion_count']}; Lean={lean.get('status')})")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
