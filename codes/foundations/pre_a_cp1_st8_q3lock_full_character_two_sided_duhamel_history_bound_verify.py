#!/usr/bin/env python3
"""Integrated verifier for EXP-001153."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_full_character_two_sided_duhamel_history_bound"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-full-character-two-sided-duhamel-history-bound-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
STATIC = REPO / "strategy/pre-a-cp1-st8-q3lock-full-character-double-commutator-bound-manifest.json"
CYLINDER = REPO / "strategy/pre-a-cp1-st8-q3lock-inductive-cylinder-form-contract-manifest.json"
LEAN = REPO / "verification/lean/Tect/R323.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R323.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R323.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    static = json.loads(STATIC.read_text(encoding="utf-8"))
    cylinder = json.loads(CYLINDER.read_text(encoding="utf-8"))
    oracle = manifest["derived_oracles"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001153" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001153/T-054/false")
    check("static parent", static["exploration_id"] == "EXP-001152" and static["scope"]["full_character_second_commutator_safe_bound_closed"] is True, static["exploration_id"], "EXP-001152 closed")
    check("cylinder parent", cylinder["exploration_id"] == "EXP-001150" and cylinder["scope"]["inductive_limit_test_algebra_contract_closed"] is True, cylinder["exploration_id"], "EXP-001150 closed")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["multi_support_kinetic_fixture", "force_safe_fixture", "full_word_fixture", "duhamel_one_orientation_fixture", "duhamel_two_orientation_fixture", "product_cost_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="two-sided-duhamel-history-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("passed", 0) > 0 and independent.get("passed", 0) > 0, [primary.get("passed"), independent.get("passed")], ">0")
        p = primary.get("derived", {})
        i = independent.get("derived", {})
        keys = ("kinetic_squared_bound", "l1_amplitude", "force_safe_squared_bound", "full_word_squared_bound", "one_orientation_remainder_squared_bound", "negative_orientation_remainder_squared_bound", "two_orientation_difference_squared_bound", "duhamel_kernel_squared_integral", "product_same_form_cost", "product_cross_form_cost")
        for key in keys:
            check(f"lane agreement {key}", p.get(key) == i.get(key), [p.get(key), i.get(key)], "equal exact values")
            check(f"oracle {key}", p.get(key) == oracle.get(key), p.get(key), oracle.get(key))
        check("orientation equality", p.get("one_orientation_remainder_squared_bound") == p.get("negative_orientation_remainder_squared_bound"), p, "same finite bound")
        closed = ("finite_support_static_multi_character_recomputed", "finite_member_positive_time_remainder_closed", "finite_member_negative_time_remainder_closed", "finite_member_two_orientation_difference_closed", "product_cost_recorded")
        check("finite history closure", all(p.get(key) is True and i.get(key) is True for key in closed), [p, i], True)
        open_keys = ("modular_derivative_closed", "actual_q3_four_context_history_closed", "actual_q3_factorial_history_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "unbounded_product_core_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
        check("QFT firewall", all(p.get(key) is False and i.get(key) is False for key in open_keys), [p, i], "downstream gates open")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FULL-CHARACTER-TWO-SIDED-DUHAMEL-HISTORY-BOUND",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "static_manifest_sha256": sha256(STATIC), "cylinder_manifest_sha256": sha256(CYLINDER)}
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    if args.skip_lean:
        raise SystemExit("skip-lean is not allowed for the integrated proof checkpoint")
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED TWO-SIDED-DUHAMEL-HISTORY PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
