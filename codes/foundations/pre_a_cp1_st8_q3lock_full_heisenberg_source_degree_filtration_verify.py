#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001114."""

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
SLUG = "pre_a_cp1_st8_q3lock_full_heisenberg_source_degree_filtration"
MANIFEST = REPO / "strategy/pre_a_cp1_st8_q3lock_full_heisenberg_source_degree_filtration_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R286.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R286.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R286.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R286.lean", "returncode": process.returncode, "output": output[-2000:]}


def target_signature(rows: list[dict[str, Any]], coefficient_key: str) -> list[tuple[Any, Any, Any]]:
    return [(row["m"], row[coefficient_key], row["degree"]) for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001114" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001114/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("scope flags", manifest["scope"]["full_taylor_source_degree_closed"] is True and manifest["scope"]["actual_q3_operator_domain_closed"] is False and manifest["scope"]["common_alpha_closed"] is False, manifest["scope"], "closed coefficient / open operator")
    source = LEAN.read_text(encoding="utf-8")
    check("Lean source", LEAN.is_file() and all(marker in source for marker in ("coefficient_m1", "coefficient_m6", "kinetic_degree_gap")), "markers present", "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="full-heisenberg-source-filtration-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("total", 0) > 0 and independent.get("total", 0) > 0, [primary.get("total"), independent.get("total")], ">0")
        primary_derived = primary.get("derived", {})
        independent_derived = independent.get("derived", {})
        check("lane G agreement", primary_derived.get("G") == independent_derived.get("G"), [primary_derived.get("G"), independent_derived.get("G")], "equal")
        check("lane target agreement", target_signature(primary_derived.get("target_rows", []), "coefficient") == target_signature(independent_derived.get("target_rows", []), "target"), "matching m/coefficient/degree rows", "equal")
        check("lane orientation agreement", target_signature(primary_derived.get("reversed_rows", []), "coefficient") == target_signature(independent_derived.get("reversed_rows", []), "target"), "matching orientation rows", "equal")
        check("lane kinetic agreement", primary_derived.get("kinetic_rows") == independent_derived.get("kinetic_rows"), "matching filtration rows", "equal")
        check("degree formula", primary_derived.get("top_degree_formula") == "4*m-3" and independent_derived.get("top_degree_formula") == "4*m-3", [primary_derived.get("top_degree_formula"), independent_derived.get("top_degree_formula")], "4*m-3")
        check("coefficient formula", primary_derived.get("top_coefficient_formula") == "-m*c*(-G/4)^(m-1)" and independent_derived.get("top_coefficient_formula") == "-m*c*(-G/4)^(m-1)", [primary_derived.get("top_coefficient_formula"), independent_derived.get("top_coefficient_formula")], "declared formula")
        check("operator boundary", primary_derived.get("actual_q3_operator_domain_closed") is False and independent_derived.get("actual_q3_operator_domain_closed") is False, [primary_derived.get("actual_q3_operator_domain_closed"), independent_derived.get("actual_q3_operator_domain_closed")], False)

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R286.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FULL-HEISENBERG-SOURCE-DEGREE-FILTRATION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": manifest["scope"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)},
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FULL-HEISENBERG-SOURCE-FILTRATION PASS {len(rows)}/{len(rows)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
