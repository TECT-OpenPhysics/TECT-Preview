#!/usr/bin/env python3
"""Integrated verifier for EXP-001142 finite spectral pairing sums."""

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
SLUG = "pre_a_cp1_st8_q3lock_finite_spectral_pairing_sum"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-spectral-pairing-sum-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R312.lean"
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
    command = "lake env lean Tect/R312.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R312.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() and "warning:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def compare_summary(primary: list[dict[str, Any]], independent: list[dict[str, Any]], tolerance: float) -> tuple[bool, list[dict[str, Any]]]:
    if len(primary) != len(independent):
        return False, [{"reason": "length", "primary": len(primary), "independent": len(independent)}]
    keys = ("volume", "beta", "max_D_km_norm", "max_delta_D_km_norm", "max_spectral_second_moment", "max_pairing_identity_error", "max_spectral_sum_error")
    mismatches: list[dict[str, Any]] = []
    for left, right in zip(primary, independent):
        for key in keys:
            if isinstance(left.get(key), (int, float)) and isinstance(right.get(key), (int, float)):
                if abs(float(left[key]) - float(right[key])) > tolerance:
                    mismatches.append({"key": key, "primary": left[key], "independent": right[key], "row": [left.get("volume"), left.get("beta")]})
            elif left.get(key) != right.get(key):
                mismatches.append({"key": key, "primary": left.get(key), "independent": right.get(key), "row": [left.get("volume"), left.get("beta")]})
    return not mismatches, mismatches


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = max(float(fixture["commutator_tolerance"]), float(fixture["spectral_sum_tolerance"]))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001142" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001142/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("source lanes distinct", sha256(PRIMARY) != sha256(INDEPENDENT), [sha256(PRIMARY), sha256(INDEPENDENT)], "distinct SHA-256")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-spectral-pairing-sum-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        expected_rows = 1
        for key in ("volume_values", "beta_values", "radius_values", "time_values", "orientation_values"):
            expected_rows *= len(fixture[key])
        check("row count agreement", p.get("row_count") == i.get("row_count") == expected_rows, [p.get("row_count"), i.get("row_count")], expected_rows)
        agreement, mismatches = compare_summary(p.get("summary_rows", []), i.get("summary_rows", []), tolerance)
        check("summary agreement", agreement, mismatches, "within tolerance")
        check("finite spectral route agreement", p.get("finite_spectral_sum_identity_closed") is True and i.get("finite_spectral_sum_identity_closed") is True and p.get("nonnegative_spectral_second_moment_closed") is True and i.get("nonnegative_spectral_second_moment_closed") is True and p.get("uniform_beta_volume_direct_d_delta_d_closed") is False and i.get("uniform_beta_volume_direct_d_delta_d_closed") is False, [p, i], "finite spectral identity only")

    check("scope firewall", scope["finite_spectral_sum_identity_closed"] and scope["nonnegative_spectral_second_moment_closed"] and scope["edge_square_sixsite_rows_closed"] and scope["two_orientation_history_closed"] and not scope["uniform_beta_volume_direct_d_delta_d_closed"] and not scope["common_core_spectral_tail_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite spectral identity; QFT gates open")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SPECTRAL-PAIRING-SUM", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean, "boundary": scope, "derived": {"primary_summary_rows": p.get("summary_rows", []), "independent_summary_rows": i.get("summary_rows", []), "uniformity_promoted": False, "common_core_spectral_tail_promoted": False, "qft_promoted": False}, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}}


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
    print(f"INTEGRATED FINITE-SPECTRAL-PAIRING-SUM PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
