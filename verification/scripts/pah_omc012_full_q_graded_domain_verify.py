#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-012 full-Q graded-domain packet."""
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
CONTRACT = REPO / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
MANIFEST = REPO / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-manifest.json"
LEAN = REPO / "verification/lean/Tect/R492.lean"
REGISTRY = REPO / "verification/lean/registry.json"
RUN_DIR = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain"
PRIMARY = REPO / "codes/foundations/pah_omc012_full_q_graded_domain.py"
INDEPENDENT = REPO / "codes/foundations/pah_omc012_full_q_graded_domain_independent.py"
HOSTILE = REPO / "codes/foundations/pah_omc012_full_q_graded_domain_hostile.py"
SOURCE_FILES = {
    "PAH-001": REPO / "strategy/pa-hyp/PAH-001-v1.json",
    "PAH-OMC-004": REPO / "strategy/pa-hyp/PAH-OMC-004-v1.json",
    "PAH-OMC-008": REPO / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json",
    "PAH-OMC-010": REPO / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json",
    "PAH-OMC-010-MANIFEST": REPO / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json",
    "PAH-OMC-011": REPO / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json",
    "R-490-PRIMARY-RUN": REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json",
}
RESULT_ID = "R-492"
EXPLORATION_ID = "EXP-001461"
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
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except BaseException:
        try:
            os.unlink(temp)
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
        return {"status": "BLOCKED", "reason": "pinned lake executable missing", "command": "lake env lean Tect/R492.lean"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R492.lean"],
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
        "command": "lake env lean Tect/R492.lean",
        "output": output[-4000:],
        "lake": str(lake),
    }

def run(output: Path = RUN_DIR / "integrated.json") -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    rows: list[dict[str, Any]] = []

    def add(name: str, passed: bool, actual: Any = None, expected: Any = True) -> None:
        rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    current = {key: sha(path) for key, path in SOURCE_FILES.items()}
    current["PAH-OMC-012"] = sha(CONTRACT)
    current["PAH-OMC-012-MANIFEST"] = sha(MANIFEST)
    current["R492-Lean"] = sha(LEAN, normalize=True)
    add("contract hash pinned", manifest["contract"]["sha256"] == current["PAH-OMC-012"], manifest["contract"]["sha256"], current["PAH-OMC-012"])
    add("all parent hashes pinned", all(manifest["parents"][key]["sha256"] == current[key] for key in SOURCE_FILES), {key: manifest["parents"][key]["sha256"] for key in SOURCE_FILES}, {key: current[key] for key in SOURCE_FILES})
    add("manifest status", manifest["status"] == "MAINLINE_ADVANCE" and manifest["claim_bearing"] is False and manifest["active_gate_change"] is False and manifest["physical_promotion"] is False, manifest, "MAINLINE_ADVANCE/non-bearing/no gate change")
    add("firewall", all(value is True for value in contract["preservation_firewall"].values()) and manifest["no_parent_mutation"] is True, contract["preservation_firewall"], "all true")
    add("source identity", contract["contract_id"] == "PAH-OMC-012" and manifest["manifest_id"].startswith("PAH-OMC-012"), contract["contract_id"], "PAH-OMC-012")

    primary = run_script(PRIMARY, RUN_DIR / "primary.json")
    independent = run_script(INDEPENDENT, RUN_DIR / "independent.json")
    hostile = run_script(HOSTILE, RUN_DIR / "hostile.json")
    for label, item in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        add(f"{label} subprocess", item["returncode"] == 0 and item["verification"] == "PASS", item, "PASS")
    add("cross-lane verdict", all(item["verdict"] == "MAINLINE_ADVANCE" for item in (primary, independent, hostile)), [item["verdict"] for item in (primary, independent, hostile)], "all MAINLINE_ADVANCE")
    add("cross-lane eligibility", all(item["payload"].get("eligible_for_omc011_retest") is True for item in (primary, independent, hostile)), [item["payload"].get("eligible_for_omc011_retest") for item in (primary, independent, hostile)], True)
    add("graded totality and nonzero lift", primary["payload"].get("derived", {}).get("r488_witness_rows") and primary["payload"].get("eligible_for_omc011_retest") is True, primary["payload"].get("derived"), "total/unique/nonzero")
    add("C_sw role", primary["payload"].get("state_weighted_input") == {"C_sw": 540, "role": "domination_only", "intertwining_proved": False}, primary["payload"].get("state_weighted_input"), "domination only")

    registry_entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R492.lean"), None)
    lean_source = LEAN.read_text(encoding="utf-8")
    add("Lean registry entry", registry_entry is not None and registry_entry.get("sha256") == current["R492-Lean"], registry_entry, current["R492-Lean"])
    add("Lean source firewall", not any(re.search(rf"\b{re.escape(token)}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", True)
    declarations = manifest["lean"]["declarations"]
    add("Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in declarations), declarations, "all registered")
    lean = run_lean(registry)
    add("Lean compile", lean.get("status") == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc012-full-q-graded-domain-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-012-FULL-Q-GRADED-DOMAIN-INTEGRATED-001",
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "MAINLINE_ADVANCE" if not failed else "HOLD_FOR_EVIDENCE",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": current,
        "runs": {"primary": primary, "independent": independent, "hostile": hostile, "lean": lean},
        "contract": contract["exact_scope"],
        "component_recovery": contract["proof_obligations"]["component_recovery"],
        "state_weighted_input": {"C_sw": 540, "role": "domination_only", "intertwining_proved": False},
        "global_normalized_gibbs_measure": "NOT_DEFINED_BY_PARENT; not needed for this finite domain-map gate",
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "eligible_for_omc011_retest": bool(not failed),
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"R-492 INTEGRATED: {payload['verification']} ({payload['passed']}/{payload['assertion_count']}; Lean={lean.get('status')}; verdict={payload['verdict']})")
    return payload

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "integrated.json")
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
