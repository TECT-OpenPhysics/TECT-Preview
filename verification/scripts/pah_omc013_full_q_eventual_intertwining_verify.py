#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-013 finite common-core packet.

The verifier reruns the primary, independent, and hostile lanes, checks all
hash pins and registered Lean declarations, and compiles R493 with the local
pinned Lean executable.  It is intentionally offline: no lake self-update or
network fetch is attempted.
"""
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
CONTRACT = REPO / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
MANIFEST = REPO / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-manifest.json"
LEAN = REPO / "verification/lean/Tect/R493.lean"
REGISTRY = REPO / "verification/lean/registry.json"
RUN_DIR = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc013-full-q-eventual-intertwining"
PRIMARY = REPO / "codes/foundations/pah_omc013_full_q_eventual_intertwining.py"
INDEPENDENT = REPO / "codes/foundations/pah_omc013_full_q_eventual_intertwining_independent.py"
HOSTILE = REPO / "codes/foundations/pah_omc013_full_q_eventual_intertwining_hostile.py"
SOURCE_FILES = {
    "PAH-001": REPO / "strategy/pa-hyp/PAH-001-v1.json",
    "PAH-OMC-004": REPO / "strategy/pa-hyp/PAH-OMC-004-v1.json",
    "PAH-OMC-008": REPO / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json",
    "PAH-OMC-010": REPO / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json",
    "PAH-OMC-010-MANIFEST": REPO / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json",
    "PAH-OMC-011": REPO / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json",
    "PAH-OMC-012": REPO / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json",
    "PAH-OMC-012-MANIFEST": REPO / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-manifest.json",
    "R-484": REPO / "strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json",
    "R-484-RUN": REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json",
    "R-490-CERTIFICATE": REPO / "strategy/pa-hyp/R490-certificate.md",
    "R-490-PRIMARY-RUN": REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json",
}
RESULT_ID = "R-493"
EXPLORATION_ID = "EXP-001474"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-013-FULL-Q-EVENTUAL-INTERTWINING-INTEGRATED-001"


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


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(fd, "w", encoding="utf-8", newline="", closefd=True) as stream:
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
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", str(path), "--output", str(output)],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    payload = load(output) if output.is_file() else {}
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
        "verification": payload.get("verification"),
        "verdict": payload.get("verdict"),
        "assertion_count": payload.get("assertion_count"),
        "passed": payload.get("passed"),
        "failed": payload.get("failed"),
        "payload": payload,
    }


def lean_executable() -> Path | None:
    candidates = [
        Path.home() / ".elan" / "toolchains" / "leanprover--lean4---v4.32.1" / "bin" / "lean.exe",
        Path.home() / ".elan" / "toolchains" / "leanprover--lean4---v4.32.1" / "bin" / "lean",
    ]
    return next((path for path in candidates if path.is_file()), None)


def direct_lean_compile() -> dict[str, Any]:
    executable = lean_executable()
    if executable is None:
        return {"status": "BLOCKED", "reason": "pinned Lean executable missing", "command": "lean Tect/R493.lean"}
    lean_root = REPO / "verification/lean"
    search_paths: list[str] = []
    packages = lean_root / ".lake" / "packages"
    if packages.is_dir():
        for package in sorted(packages.iterdir()):
            candidate = package / ".lake" / "build" / "lib" / "lean"
            if candidate.is_dir():
                search_paths.append(str(candidate.resolve()))
    local_lib = lean_root / ".lake" / "build" / "lib" / "lean"
    if local_lib.is_dir():
        search_paths.append(str(local_lib.resolve()))
    environment = os.environ.copy()
    environment["LEAN_PATH"] = os.pathsep.join(search_paths)
    completed = subprocess.run(
        [str(executable), "Tect/R493.lean"], cwd=lean_root, env=environment,
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=180,
    )
    output = f"{completed.stdout}\n{completed.stderr}"
    return {
        "status": "PASS" if completed.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": completed.returncode, "command": "lean Tect/R493.lean (offline pinned toolchain)",
        "output": output[-4000:], "executable": str(executable), "lean_path_entries": len(search_paths),
    }


def run(output: Path = RUN_DIR / "integrated.json") -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    rows: list[dict[str, Any]] = []

    def add(name: str, passed: bool, actual: Any = None, expected: Any = True) -> None:
        rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    current = {key: sha(path) for key, path in SOURCE_FILES.items()}
    current["PAH-OMC-013"] = sha(CONTRACT)
    current["PAH-OMC-013-MANIFEST"] = sha(MANIFEST)
    current["R493-Lean"] = sha(LEAN, normalize=True)
    add("contract hash pinned", manifest["contract"]["sha256"] == current["PAH-OMC-013"], manifest["contract"]["sha256"], current["PAH-OMC-013"])
    parent_hash_ok = all(manifest["parents"][key]["sha256"] == current[key] for key in SOURCE_FILES if key not in {"R-484-RUN", "R-490-CERTIFICATE", "R-490-PRIMARY-RUN"})
    parent_hash_ok = parent_hash_ok and manifest["parents"]["R-484"]["run_sha256"] == current["R-484-RUN"]
    parent_hash_ok = parent_hash_ok and manifest["parents"]["R-490"]["certificate_sha256"] == current["R-490-CERTIFICATE"]
    parent_hash_ok = parent_hash_ok and manifest["parents"]["R-490"]["run_sha256"] == current["R-490-PRIMARY-RUN"]
    add("all parent hashes pinned", parent_hash_ok, {"manifest": manifest["parents"], "current": current}, "all parent and run hashes")
    add("manifest status", manifest["status"] == "MAINLINE_ADVANCE" and manifest["claim_bearing"] is False and manifest["active_gate_change"] is False and manifest["physical_promotion"] is False, {k: manifest.get(k) for k in ("status", "claim_bearing", "active_gate_change", "physical_promotion")}, "MAINLINE_ADVANCE/non-bearing/no gate change")
    add("preservation firewall", all(value is True for value in contract["preservation_firewall"].values()) and manifest["no_parent_mutation"] is True, contract["preservation_firewall"], "all true")
    add("contract identity", contract["contract_id"] == "PAH-OMC-013" and manifest["manifest_id"].startswith("PAH-OMC-013"), contract["contract_id"], "PAH-OMC-013")

    primary = run_script(PRIMARY, RUN_DIR / "primary.json")
    independent = run_script(INDEPENDENT, RUN_DIR / "independent.json")
    hostile = run_script(HOSTILE, RUN_DIR / "hostile.json")
    for label, item in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        add(f"{label} subprocess", item["returncode"] == 0 and item["verification"] == "PASS", {k: item[k] for k in ("returncode", "verification", "verdict", "passed", "failed")}, "PASS")
        add(f"{label} result identity", item["payload"].get("result_id") == RESULT_ID and item["payload"].get("exploration_id") == EXPLORATION_ID and item["payload"].get("task_id") == TASK_ID, {k: item["payload"].get(k) for k in ("result_id", "exploration_id", "task_id")}, {"result_id": RESULT_ID, "exploration_id": EXPLORATION_ID, "task_id": TASK_ID})
    add("cross-lane verdict", all(item["verdict"] == "MAINLINE_ADVANCE" for item in (primary, independent, hostile)), [item["verdict"] for item in (primary, independent, hostile)], "all MAINLINE_ADVANCE")
    add("primary structural and regression rows", primary["payload"].get("derived", {}).get("structural_rows", 0) > 0 and primary["payload"].get("derived", {}).get("regression_rows", 0) > 0, primary["payload"].get("derived"), "positive rows")
    add("independent replay rows", independent["payload"].get("derived", {}).get("regression_rows", 0) > 0 and independent["payload"].get("derived", {}).get("grade_rows", 0) > 0, independent["payload"].get("derived"), "positive rows")
    add("hostile mutation firewall", all(row.get("rejected") is True for row in hostile["payload"].get("assertions", [])), hostile["payload"].get("assertions"), "all mutations rejected")
    add("R-484 defect and C_sw role", primary["payload"].get("boundary_defect", {}).get("hidden_diagonal_defect") == "16/9" and primary["payload"].get("state_weighted_input") == {"C_sw": 540, "role": "domination_only", "intertwining_proved_by_C_sw": False}, {"boundary": primary["payload"].get("boundary_defect"), "state_weighted": primary["payload"].get("state_weighted_input")}, "defect retained/C_sw domination-only")

    registry_entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R493.lean"), None)
    lean_source = LEAN.read_text(encoding="utf-8")
    add("Lean registry entry", registry_entry is not None and registry_entry.get("sha256") == current["R493-Lean"], registry_entry, current["R493-Lean"])
    add("Lean source firewall", not any(re.search(rf"\b{re.escape(token)}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", True)
    declarations = manifest["lean"]["declarations"]
    add("Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in declarations), declarations, "all registered")
    lean = direct_lean_compile()
    add("Lean compile", lean.get("status") == "PASS", lean, "PASS")
    add("no physical promotion", contract["status"]["claim_bearing"] is False and contract["status"]["active_gate_change"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]), contract["non_claims"], True)

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc013-full-q-eventual-intertwining-integrated/1.0",
        "run_kind": "integrated", "audit_id": AUDIT_ID, "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID, "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "MAINLINE_ADVANCE" if not failed else "HOLD_FOR_EVIDENCE",
        "assertion_count": len(rows), "passed": len(rows) - len(failed), "failed": len(failed),
        "assertions": rows, "source_hashes": current,
        "runs": {"primary": primary, "independent": independent, "hostile": hostile, "lean": lean},
        "contract_scope": contract["exact_scope"],
        "claim_bearing": False, "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP",
        "weak_gibbs_l2": "NOT_PROVED", "infinite_volume": "NOT_PROVED",
        "non_claims": contract["non_claims"], "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    write_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; Lean={lean.get('status')}; verdict={payload['verdict']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "integrated.json")
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
