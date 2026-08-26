#!/usr/bin/env python3
"""Integrated verifier for EXP-001196 finite Q3 source-amplitude stress."""
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
SLUG = "pre_a_cp1_st8_q3lock_split_step_amplitude_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-split-step-amplitude-stress-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R355.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
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
    command = "lake env lean Tect/R355.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R355.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def row_key(row: dict[str, Any]) -> tuple[int, str, str, tuple[int, ...], str, str]:
    return (int(row["volume"]), str(row["beta"]), str(row["amplitude"]), tuple(int(site) for site in row["support"]), str(row["order"]), str(row["context"]))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001196" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001196/T-054/false")
    check("source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [PRIMARY, INDEPENDENT, LEAN], "present")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["amplitude_grid_fixture", "time_horizon_fixture", "weighted_step_fixture", "order_context_fixture", "scope_fixture"]
    check("Lean markers", all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="q3-amplitude-stress-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        check("parameter context count", p.get("parameter_context_count") == i.get("parameter_context_count") == 120, [p.get("parameter_context_count"), i.get("parameter_context_count")], 120)
        check("row counts", p.get("length_row_count") == i.get("length_row_count") and p.get("recurrence_row_count") == i.get("recurrence_row_count"), [p.get("length_row_count"), i.get("length_row_count"), p.get("recurrence_row_count"), i.get("recurrence_row_count")], "equal")
        p_rows = {row_key(row): row for row in p.get("context_summaries", [])}
        i_rows = {row_key(row): row for row in i.get("context_summaries", [])}
        check("context keys", set(p_rows) == set(i_rows) and len(p_rows) == 120, [len(p_rows), len(i_rows)], 120)
        agreement = float(fixture["agreement_tolerance"])
        for key in sorted(p_rows):
            p_row, i_row = p_rows[key], i_rows[key]
            check(f"lane max residual {key}", abs(float(p_row["max_residual"]) - float(i_row["max_residual"])) <= agreement, [p_row["max_residual"], i_row["max_residual"]], f"within {agreement}")
            check(f"lane min residual {key}", abs(float(p_row["min_residual"]) - float(i_row["min_residual"])) <= agreement, [p_row["min_residual"], i_row["min_residual"]], f"within {agreement}")
            check(f"lane violation count {key}", int(p_row["violation_count"]) == int(i_row["violation_count"]), [p_row["violation_count"], i_row["violation_count"]], "equal")
        check("finite scope", p.get("actual_split_recurrence_theorem_closed") is False and i.get("actual_split_recurrence_theorem_closed") is False and p.get("common_alpha_closed") is False and i.get("common_alpha_closed") is False, [p, i], "theorem/QFT gates remain open")
        check("route outcome", p.get("recurrence_status") == i.get("recurrence_status") and p.get("recurrence_status") in ("PASS_ALL_AMPLITUDE_ROWS", "FAIL_AMPLITUDE_ROUTE_LOCAL"), [p.get("recurrence_status"), i.get("recurrence_status")], "explicit finite outcome")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-SPLIT-STEP-AMPLITUDE-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}
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
    print(f"INTEGRATED ACTUAL-SPLIT-STEP AMPLITUDE STRESS PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())