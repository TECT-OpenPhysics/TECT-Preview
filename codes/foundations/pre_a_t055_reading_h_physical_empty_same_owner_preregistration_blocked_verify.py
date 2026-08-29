#!/usr/bin/env python3
"""Integrate primary, independent, and hostile R-418 blocker lanes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre-a-t055-reading-h-physical-empty-same-owner-preregistration-blocked"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
CODE = "pre_a_t055_reading_h_physical_empty_same_owner_preregistration_blocked"
PRIMARY = ROOT / f"codes/foundations/{CODE}.py"
INDEPENDENT = ROOT / f"codes/foundations/{CODE}_independent.py"
HOSTILE = ROOT / f"codes/foundations/{CODE}_hostile.py"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-hostile-{SLUG}/hostile.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-integrated-{SLUG}/integrated.json"


def sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_child(script: Path, output: Path) -> dict[str, Any]:
    command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
    completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {script.name}\n{completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("manifest identity", manifest.get("result_id") == "R-418" and manifest.get("exploration_id") == "EXP-001263" and manifest.get("claim_bearing") is False, [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("claim_bearing")], ["R-418", "EXP-001263", False], "provenance")
    check("blocked owner contract", manifest["owner_contract"]["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and manifest["owner_contract"]["finite_evaluation_allowed"] is False, [manifest["owner_contract"]["field_status"], manifest["owner_contract"]["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", False], "contract")
    check("E is a blocked preregistration slot", manifest["physical_empty_branch_E"]["admission_status"] == "BLOCKED_NOT_INSTANTIATED", manifest["physical_empty_branch_E"]["admission_status"], "BLOCKED_NOT_INSTANTIATED", "contract")
    check("three verdicts are blocked", all(item["status"] == "BLOCKED_NOT_EVALUATED" for item in manifest["verdicts"].values()) and len(manifest["verdicts"]) == 3, {key: value["status"] for key, value in manifest["verdicts"].items()}, "three BLOCKED_NOT_EVALUATED statuses", "verdict")
    artifacts = [MANIFEST, PRIMARY, INDEPENDENT, HOSTILE]
    check("artifact presence", all(path.is_file() for path in artifacts), [str(path) for path in artifacts if not path.is_file()], "all R-418 artifacts", "provenance")
    source_hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("source hashes are distinct", len(set(source_hashes.values())) == len(source_hashes), source_hashes, "distinct hashes", "provenance")
    if args.reuse_existing:
        primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
        independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
        hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
        rows.append({"name": "reuse existing child runs", "group": "executables", "status": "PASS", "actual": True, "expected": True})
    else:
        primary = run_child(PRIMARY, PRIMARY_OUTPUT)
        independent = run_child(INDEPENDENT, INDEPENDENT_OUTPUT)
        hostile = run_child(HOSTILE, HOSTILE_OUTPUT)
        rows.append({"name": "run primary/independent/hostile children", "group": "executables", "status": "PASS", "actual": True, "expected": True})
    check("primary blocker verdict", primary.get("verdict") == "BLOCKED", primary.get("verdict"), "BLOCKED", "executables")
    check("independent blocker verdict", independent.get("verdict") == "BLOCKED", independent.get("verdict"), "BLOCKED", "executables")
    check("hostile lane passes", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    check("primary-independent identity", [primary.get("result_id"), primary.get("exploration_id"), primary.get("claim_id") ] == [independent.get("result_id"), independent.get("exploration_id"), independent.get("claim_id")], [primary.get("result_id"), primary.get("exploration_id"), primary.get("claim_id")], "exact identity agreement", "independence")
    check("primary-independent blocker status", primary["derived"]["owner_contract_status"] == independent["derived"]["owner_contract_status"] and primary["derived"]["physical_empty_slot"] == independent["derived"]["physical_empty_slot"], [primary["derived"]["owner_contract_status"], independent["derived"]["owner_contract_status"]], "same owner/E blocker", "independence")
    check("primary-independent no numeric evaluation", primary["derived"]["numeric_evaluation"] is False and independent["derived"]["numeric_evaluation"] is False, [primary["derived"]["numeric_evaluation"], independent["derived"]["numeric_evaluation"]], [False, False], "scope")
    check("primary-independent source hashes", primary["source_hashes"] == independent["source_hashes"], True, True, "independence")
    check("three exact blocked verdict fields", primary["derived"]["sign_status"] == "BLOCKED_NOT_EVALUATED" and primary["derived"]["stationarity_status"] == "BLOCKED_NOT_EVALUATED" and primary["derived"]["transverse_stability_status"] == "BLOCKED_NOT_EVALUATED", primary["derived"], "all three BLOCKED_NOT_EVALUATED", "verdict")
    check("hostile mutations all pass", all(row.get("status") == "PASS" for row in hostile.get("assertions", [])) and len(hostile.get("assertions", [])) >= 6, len(hostile.get("assertions", [])), "at least six PASS mutation checks", "hostile")
    payload = {
        "schema": "tect/pre-a-t055-physical-empty-blocked-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "T055-PHYSICAL-EMPTY-SAME-OWNER-PREREGISTRATION-BLOCKED",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-418",
        "exploration_id": "EXP-001263",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "verdict": "BLOCKED",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "primary": primary["derived"],
            "independent": independent["derived"],
            "hostile": hostile["derived"],
            "numeric_evaluation": False,
            "lean": "not applicable"
        },
        "evidence_level": manifest["evidence_level"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "blockers": manifest["blockers"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"]
    }
    if args.self_test:
        assert payload["verdict"] == "BLOCKED"
        assert payload["derived"]["numeric_evaluation"] is False
        print("R-418 INTEGRATED SELFTEST: PASS (three-lane blocked contract and hostile firewall)")
        return 0
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-418 INTEGRATED BLOCKED {len(rows)}/{len(rows)} assertions; all three requested tests remain NOT_EVALUATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
