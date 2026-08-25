#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001118."""

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
SLUG = "pre_a_cp1_st8_q3lock_factorial_derivative_closed_quartic_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-factorial-derivative-closed-quartic-obstruction-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R290.lean"
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
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
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
    if lake is None:
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R290.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R290.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R290.lean", "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); parser.add_argument("--skip-lean", action="store_true"); args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001118" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001118/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("scope flags", manifest["scope"]["factorial_derivative_closure_closed"] and manifest["scope"]["repeated_top_monomial_exponential_envelope_refuted"] and not manifest["scope"]["actual_q3_common_core_map_proved"] and not manifest["scope"]["common_alpha_closed"], manifest["scope"], "route boundary / Q3 open")
    source = LEAN.read_text(encoding="utf-8")
    markers = ("factorial_derivative_fixture", "order_sixteen_top_branch_ratio", "factorial_lower_bound_m16", "radius_loss_scope")
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), "markers present", "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="factorial-quartic-obstruction-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("total", 0) > 0 and independent.get("total", 0) > 0, [primary.get("total"), independent.get("total")], ">0")
        pd = primary.get("derived", {}); ind = independent.get("derived", {})
        check("top coefficient agreement", pd.get("center_top_coefficient") == ind.get("center_top_coefficient") and pd.get("reverse_top_coefficient") == ind.get("reverse_top_coefficient"), [pd.get("center_top_coefficient"), ind.get("center_top_coefficient"), pd.get("reverse_top_coefficient"), ind.get("reverse_top_coefficient")], "equal")
        check("derivative constant agreement", str(pd.get("derivative_closure_constant")) == ind.get("derivative_closure_constant") == "4", [pd.get("derivative_closure_constant"), ind.get("derivative_closure_constant")], "4")
        primary_rows = [(row.get("m"), str(row.get("degree")), str(row.get("norm_ratio")), str(row.get("comparison_base_power"))) for row in pd.get("ratio_rows", [])]
        independent_rows = [(row.get("m"), str(row.get("degree")), str(row.get("norm_ratio")), str(row.get("comparison_base_power"))) for row in ind.get("ratio_rows", [])]
        check("recurrence rows agreement", primary_rows == independent_rows, [primary_rows, independent_rows], "equal")
        check("order-sixteen agreement", pd.get("order_sixteen_ratio") == ind.get("order_sixteen_ratio"), [pd.get("order_sixteen_ratio"), ind.get("order_sixteen_ratio")], "equal")
        check("scope agreement", pd.get("repeated_top_monomial_exponential_envelope_refuted") is True and ind.get("repeated_top_monomial_exponential_envelope_refuted") is True and pd.get("actual_q3_history_closed") is False and ind.get("actual_q3_history_closed") is False, "matching boundary flags", "true/false")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R290.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-FACTORIAL-DERIVATIVE-CLOSED-QUARTIC-OBSTRUCTION", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean, "boundary": manifest["scope"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FACTORIAL-QUARTIC-OBSTRUCTION PASS {payload['assertion_count']}/{payload['assertion_count']} | Lean {lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
