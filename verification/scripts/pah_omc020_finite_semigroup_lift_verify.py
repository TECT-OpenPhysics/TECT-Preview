#!/usr/bin/env python3
"""Integrated verifier for PAH-OMC-020 R-550."""
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-finite-semigroup-lift-contract-v1.json"
R493 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc020FiniteSemigroup.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-finite-semigroup-lift"
PRIMARY = ROOT / "verification/scripts/pah_omc020_finite_semigroup_lift.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_finite_semigroup_lift_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_finite_semigroup_lift_hostile.py"
RESULT_ID = "R-550"
TASK_ID = "T-082"
AUDIT_ID = "PAH-OMC-020-FINITE-SEMIGROUP-LIFT-INTEGRATED-001"
DECLARATIONS = [
    "iterate_intertwines",
    "exp_partial_intertwines",
    "restricted_iterate_intertwines",
    "coefficient_identity_requires_iterate_scope",
    "finite_bridge_nonpromotion",
]


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path, normalize: bool = False) -> str:
    data = path.read_bytes()
    if normalize:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_lane(path: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", str(path), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    payload = read(output) if output.is_file() else {}
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
        "verification": payload.get("verification"),
        "verdict": payload.get("verdict"),
        "checks_passed": payload.get("checks_passed"),
        "checks_failed": payload.get("checks_failed"),
        "payload": payload,
    }


def lean_executable() -> Path | None:
    candidates = [
        Path.home() / ".elan" / "toolchains" / "leanprover--lean4---v4.32.1" / "bin" / "lean.exe",
        Path.home() / ".elan" / "toolchains" / "leanprover--lean4---v4.32.1" / "bin" / "lean",
    ]
    return next((path for path in candidates if path.is_file()), None)


def compile_lean() -> dict[str, Any]:
    executable = lean_executable()
    if executable is None:
        return {"status": "BLOCKED", "reason": "pinned Lean executable missing"}
    lean_root = ROOT / "verification/lean"
    cache_root = Path("E:/Dev/TECT/verification/lean/.lake/packages")
    search_paths: list[str] = []
    if cache_root.is_dir():
        for package in sorted(cache_root.iterdir()):
            candidate = package / ".lake" / "build" / "lib" / "lean"
            if candidate.is_dir():
                search_paths.append(str(candidate.resolve()))
    local_lib = lean_root / ".lake" / "build" / "lib" / "lean"
    if local_lib.is_dir():
        search_paths.append(str(local_lib.resolve()))
    environment = os.environ.copy()
    environment["LEAN_PATH"] = os.pathsep.join(search_paths)
    completed = subprocess.run(
        [str(executable), str(LEAN)],
        cwd=lean_root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=180,
    )
    output = f"{completed.stdout}\n{completed.stderr}"
    return {"status": "PASS" if completed.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": completed.returncode, "output": output[-3000:], "executable": str(executable)}


def run(output: Path) -> dict[str, Any]:
    contract = read(CONTRACT)
    r493 = read(R493)
    registry = read(REGISTRY)
    rows: list[dict[str, Any]] = []

    def add(name: str, passed: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    add("contract hash self-consistent", contract["parents"]["PAH-OMC-013"]["sha256"] == sha(R493), {"declared": contract["parents"]["PAH-OMC-013"]["sha256"], "actual": sha(R493)}, "equal")
    add("contract identity", contract["result_id"] == RESULT_ID and contract["task_id"] == TASK_ID, {"result_id": contract["result_id"], "task_id": contract["task_id"]}, {"result_id": RESULT_ID, "task_id": TASK_ID})
    add("conditional scope", contract["status"]["finite_conditional_bridge"] == "PROVED_CONDITIONALLY" and contract["status"]["paH_omc013_semigroup"] == "NOT_PROVED", contract["status"], "conditional/not proved")
    add("firewall", all(value is True for value in contract["preservation_firewall"].values()), contract["preservation_firewall"], "all true")

    primary = run_lane(PRIMARY, RUN_DIR / "primary.json")
    independent = run_lane(INDEPENDENT, RUN_DIR / "independent.json")
    hostile = run_lane(HOSTILE, RUN_DIR / "hostile.json")
    for name, lane in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        add(f"{name} lane", lane["returncode"] == 0 and lane["verification"] == "PASS" and lane["verdict"] == "HOLD_FOR_EVIDENCE", {key: lane[key] for key in ("returncode", "verification", "verdict", "checks_passed", "checks_failed")}, "PASS/HOLD_FOR_EVIDENCE")
        add(f"{name} identity", lane["payload"].get("result_id") == RESULT_ID and lane["payload"].get("task_id") == TASK_ID, {"result_id": lane["payload"].get("result_id"), "task_id": lane["payload"].get("task_id")}, {"result_id": RESULT_ID, "task_id": TASK_ID})
    add("cross-lane replay", all(lane["verification"] == "PASS" for lane in (primary, independent, hostile)), [lane["verification"] for lane in (primary, independent, hostile)], "all PASS")
    add("hostile mutation firewall", all(row.get("rejected") is True for row in hostile["payload"].get("checks", [])), hostile["payload"].get("checks", []), "all rejected")

    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020FiniteSemigroup.lean"), None)
    source = LEAN.read_text(encoding="utf-8")
    add("Lean registry pin", entry is not None and entry.get("sha256") == sha(LEAN, normalize=True), entry, sha(LEAN, normalize=True))
    add("Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(name)}\b", source) for name in DECLARATIONS), DECLARATIONS, "all registered")
    add("Lean forbidden tokens", not any(re.search(rf"\b{re.escape(token)}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", True)
    lean = compile_lean()
    add("Lean compile", lean.get("status") == "PASS", lean, "PASS")

    add("R-493 remains local", "support-dependent" in contract["closure_audit"]["support_rule"].lower() and "every iterate" in contract["closure_audit"]["iterate_requirement"].lower(), contract["closure_audit"], "missing invariant/iterate premise")
    add("no physical promotion", contract["status"]["claim_bearing"] is False and contract["status"]["active_gate_change"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]), contract["status"], "non-bearing/no gate change")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-finite-semigroup-lift-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "runs": {"primary": primary, "independent": independent, "hostile": hostile, "lean": lean},
        "source_hashes": {"contract": sha(CONTRACT), "R493": sha(R493), "Lean": sha(LEAN, normalize=True)},
        "claim_bearing": False,
        "active_gate_change": False,
        "conditional_finite_bridge": "PROVED_CONDITIONALLY",
        "paH_omc013_semigroup": "NOT_PROVED",
        "missing_assumptions": contract["missing_assumptions"],
        "single_next_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; Lean={lean.get('status')}; verdict=HOLD_FOR_EVIDENCE")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "integrated.json")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    return 0 if run(output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
