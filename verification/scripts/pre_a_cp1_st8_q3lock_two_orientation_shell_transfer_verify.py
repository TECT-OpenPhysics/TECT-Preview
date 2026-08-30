#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-450."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-orientation-shell-transfer-manifest.json"
PRIMARY = ROOT / "verification/scripts/pre_a_cp1_st8_q3lock_two_orientation_shell_transfer.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_two_orientation_shell_transfer_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_two_orientation_shell_transfer_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R450.lean"
LEAN_ROOT = ROOT / "verification/lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/integrated.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([sys.executable, "-X", "utf8", str(script), "--output", str(output)], cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict[str, Any]:
    if not LAKE.is_file():
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R450.lean", "output": "pinned direct lake executable not found"}
    process = subprocess.run([str(LAKE), "env", "lean", "Tect/R450.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R450.lean", "returncode": process.returncode, "output": output[-2000:]}


def run(output: Path = DEFAULT_OUTPUT, skip_lean: bool = False) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]] == ["R-450", "EXP-001323", "T-054", False, "TWO_ORIENTATION_SHELL_TRANSFER_AUDITED"], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]], ["R-450", "EXP-001323", "T-054", False, "TWO_ORIENTATION_SHELL_TRANSFER_AUDITED"], "provenance")
    check("method firewall", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true", "method")
    check("scope firewall", all(value is False for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in {"parent_state_weighted_edge_majorant_reused", "parent_scalar_shell_tail_reused", "coefficient_weight_domination_checked", "finite_box_two_orientation_envelope_closed", "root_free_fourth_power_certificate_closed"}), manifest["scope"], "all downstream false", "scope")
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in lean_source for marker in manifest["lean_crosscheck"]["declarations"]), manifest["lean_crosscheck"]["declarations"], "all present", "Lean")
    check("Lean forbidden tokens", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), "clean", "forbidden absent", "Lean")
    for name, relative in {"manifest": MANIFEST, "primary": PRIMARY, "independent": INDEPENDENT, "hostile": HOSTILE, "integrated": Path(__file__) }.items():
        check(f"artifact {name}", relative.is_file(), str(relative), True, "artifacts")

    with tempfile.TemporaryDirectory(prefix="r450-integrated-") as directory:
        temp = Path(directory)
        p_process, primary = child(PRIMARY, temp / "primary.json")
        i_process, independent = child(INDEPENDENT, temp / "independent.json")
        h_process, hostile = child(HOSTILE, temp / "hostile.json")
        check("primary child", p_process.returncode == 0 and primary.get("verdict") == manifest["status"], p_process.stdout + p_process.stderr, manifest["status"], "children")
        check("independent child", i_process.returncode == 0 and independent.get("verdict") == manifest["status"], i_process.stdout + i_process.stderr, manifest["status"], "children")
        check("hostile child", h_process.returncode == 0 and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", h_process.stdout + h_process.stderr, "HOSTILE_MUTATIONS_REJECTED", "children")
        check("independent does not import primary", "pre_a_cp1_st8_q3lock_two_orientation_shell_transfer.py" not in INDEPENDENT.read_text(encoding="utf-8"), True, "no import", "independence")
        check("hostile mutation count", hostile.get("mutation_count") == 9 and len(hostile.get("mutations_rejected", [])) == 9, hostile.get("mutation_count"), 9, "hostile")
        check("primary envelope", primary.get("derived", {}).get("finite_box_two_orientation_envelope_closed") is True and primary.get("derived", {}).get("tail_rows") == 4116, primary.get("derived", {}), "closed/4116 rows", "children")
        check("independent envelope", independent.get("derived", {}).get("finite_box_two_orientation_envelope_closed") is True and independent.get("derived", {}).get("tail_rows") == 4116, independent.get("derived", {}), "closed/4116 rows", "children")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R450.lean"} if skip_lean else lean_run()
    if not skip_lean:
        check("Lean run", lean["status"] == "PASS", lean, "PASS", "Lean")
    else:
        check("Lean source-only mode", True, lean["status"], "SKIPPED", "Lean")

    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": manifest["candidate_id"], "result_id": manifest["result_id"], "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "source_hashes": {"manifest": digest(MANIFEST), "primary": digest(PRIMARY), "independent": digest(INDEPENDENT), "hostile": digest(HOSTILE), "integrated": digest(Path(__file__)), "lean": digest(LEAN)}, "derived": {"two_orientation_transfer_closed": True, "actual_q3_per_edge_majorant_closed": False, "actual_q3_history_identification_closed": False, "common_weighted_operator_domain_closed": False, "common_alpha_closed": False, "pre_a_closed": False, "sector_a_closed": False}, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"]}
    save(output if output.is_absolute() else ROOT / output, payload)
    print(f"R-450 INTEGRATED PASS {len(checks)}/{len(checks)} Lean={lean['status']}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    run(args.output, skip_lean=args.skip_lean)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
