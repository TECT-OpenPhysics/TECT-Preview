#!/usr/bin/env python3
"""Integrated verifier for EXP-001091."""

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
SLUG = "pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R273.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-integrated-{SLUG}" / "integrated.json"
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


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def close(left: Any, right: Any, tolerance: float = 1.0e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance * (1.0 + abs(float(left)))


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001091" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001091/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("scope firewall", scope["bounded_cutoff_dyson_envelope_closed"] and scope["scale_balance_closed"] and not scope["actual_q3_modular_history_envelope_closed"] and not scope["common_alpha_closed"], scope, "bounded bridge with actual Q3 hypotheses open")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["dyson_coefficient_fixture", "modular_coefficient_fixture", "sublinear_scale_fixture", "factorial_exponent_fixture", "static_margin_d_fixture", "static_margin_delta_fixture", "orientation_fixture", "scale_radius_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="bounded-cutoff-dyson-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("kappa agreement", primary["derived"]["kappa0"] == independent["derived"]["kappa0"] and primary["derived"]["kappa1"] == independent["derived"]["kappa1"], [primary["derived"]["kappa0"], independent["derived"]["kappa0"], primary["derived"]["kappa1"], independent["derived"]["kappa1"]], "equal")
        p_rows = primary["derived"]["rows"]
        i_rows = independent["derived"]["rows"]
        check("row count", len(p_rows) == len(i_rows) == len(manifest["fixture"]["radius_values"]), [len(p_rows), len(i_rows)], len(manifest["fixture"]["radius_values"]))
        fields = ("interaction_bound", "lambda_L", "lambda_modular_L", "D_dynamic_log_bound", "delta_D_dynamic_log_bound", "D_static_log_bound", "delta_D_static_log_bound")
        for p_row, i_row in zip(p_rows, i_rows):
            check(f"R={p_row['radius']} row agreement", p_row["radius"] == i_row["radius"] and p_row["cutoff"] == i_row["cutoff"] and all(close(p_row[field], i_row[field]) for field in fields), [p_row, i_row], "within 1e-12 relative")

    lake = lake_path()
    check("pinned Lake", lake is not None, str(lake) if lake else None, "available")
    if lake is None:
        lean = {"status": "FAIL", "command": "lake env lean Tect/R273.lean", "output": "pinned lake executable not found"}
    else:
        process = subprocess.run([str(lake), "env", "lean", "Tect/R273.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
        output = (process.stdout + "\n" + process.stderr).strip()
        lean = {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() and "warning:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R273.lean", "returncode": process.returncode, "output": output[-2000:]}
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-BOUNDED-CUTOFF-DYSON-SHELL-MODULAR-SCALE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean, "boundary": scope, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED BOUNDED-CUTOFF-DYSON-SHELL PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
