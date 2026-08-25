#!/usr/bin/env python3
"""Integrated verifier for EXP-001140."""

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
SLUG = "pre_a_cp1_st8_q3lock_generator_pairing_cancellation"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-generator-pairing-cancellation-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R310.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
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
    command = "lake env lean Tect/R310.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R310.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def compare_summary(primary: list[dict[str, Any]], independent: list[dict[str, Any]], tolerance: float) -> tuple[bool, list[dict[str, Any]]]:
    if len(primary) != len(independent):
        return False, [{"reason": "length", "primary": len(primary), "independent": len(independent)}]
    mismatches: list[dict[str, Any]] = []
    keys = ("beta", "volume", "max_D", "max_delta_D", "max_delta2_D", "max_D_km", "max_delta_D_km", "max_delta2_D_km", "max_cancellation_error")
    for left, right in zip(primary, independent):
        for key in keys:
            if isinstance(left.get(key), (int, float)) and isinstance(right.get(key), (int, float)):
                if abs(float(left[key]) - float(right[key])) > tolerance:
                    mismatches.append({"key": key, "primary": left[key], "independent": right[key], "row": [left.get("beta"), left.get("volume")]})
            elif left.get(key) != right.get(key):
                mismatches.append({"key": key, "primary": left.get(key), "independent": right.get(key), "row": [left.get("beta"), left.get("volume")]})
    return not mismatches, mismatches


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["commutator_tolerance"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001140" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001140/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["generator_pairing_scalar_fixture", "skew_adjoint_scalar_fixture", "modular_coefficient_fixture", "orientation_sum_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="generator-pairing-cancellation-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        check("row count agreement", p.get("row_count") == i.get("row_count") == 72, [p.get("row_count"), i.get("row_count")], 72)
        agreement, mismatches = compare_summary(p.get("summary_rows", []), i.get("summary_rows", []), tolerance)
        check("summary agreement", agreement, mismatches, "within tolerance")
        check("growth agreement", compare_summary(p.get("growth_rows", []), i.get("growth_rows", []), tolerance)[0], [p.get("growth_rows"), i.get("growth_rows")], "within tolerance")
        check("finite route agreement", p.get("full_generator_pairing_identity_closed") is True and i.get("full_generator_pairing_identity_closed") is True and p.get("uniform_beta_volume_direct_d_delta_d_closed") is False and i.get("uniform_beta_volume_direct_d_delta_d_closed") is False, [p, i], "finite cancellation only")

    check("scope firewall", scope["finite_actual_d_delta_rows_closed"] and scope["full_generator_pairing_identity_closed"] and scope["two_orientation_history_closed"] and not scope["uniform_beta_volume_direct_d_delta_d_closed"] and not scope["common_alpha_closed"], scope, "finite full-generator pairing; QFT gates open")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-GENERATOR-PAIRING-CANCELLATION", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean, "boundary": scope, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}}


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
    print(f"INTEGRATED GENERATOR-PAIRING-CANCELLATION PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
