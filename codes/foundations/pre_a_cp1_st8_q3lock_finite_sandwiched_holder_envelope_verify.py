#!/usr/bin/env python3
"""Integrated verifier for EXP-001187 finite inverse-free Holder envelope."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-sandwiched-holder-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification/lean/Tect/R346.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-integrated-{SLUG}" / "integrated.json"
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
    command = "lake env lean Tect/R346.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R346.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def compare_rows(primary: list[dict[str, Any]], independent: list[dict[str, Any]], tolerance: float) -> list[dict[str, Any]]:
    if len(primary) != len(independent):
        return [{"reason": "length", "primary": len(primary), "independent": len(independent)}]
    keys = ("volume", "oscillator_dimension", "beta", "max_lhs", "max_bound", "max_ratio", "max_adjoint_lhs", "max_adjoint_bound", "max_adjoint_ratio", "max_tail_l4_left", "max_tail_l4_right")
    mismatches: list[dict[str, Any]] = []
    for left, right in zip(primary, independent):
        for key in keys:
            if isinstance(left.get(key), (int, float)) and isinstance(right.get(key), (int, float)):
                if abs(float(left[key]) - float(right[key])) > tolerance * (1.0 + abs(float(left[key]))):
                    mismatches.append({"key": key, "primary": left[key], "independent": right[key], "row": [left.get("volume"), left.get("beta")]})
            elif left.get(key) != right.get(key):
                mismatches.append({"key": key, "primary": left.get(key), "independent": right.get(key), "row": [left.get("volume"), left.get("beta")]})
    return mismatches


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001187" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001187/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    primary_hash, independent_hash = sha256(PRIMARY), sha256(INDEPENDENT)
    check("source lanes distinct", primary_hash != independent_hash, [primary_hash, independent_hash], "distinct SHA-256")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-sandwiched-holder-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        expected_history = len(fixture["scenarios"]) * len(fixture["beta_values"]) * len(fixture["radius_values"]) * len(fixture["orientation_values"]) * len(fixture["interpolation_values"]) * len(fixture["time_values"])
        check("history coverage", len(p.get("history_rows", [])) == len(i.get("history_rows", [])) == expected_history, [len(p.get("history_rows", [])), len(i.get("history_rows", []))], expected_history)
        mismatches = compare_rows(p.get("summary_rows", []), i.get("summary_rows", []), float(fixture["lane_tolerance"]))
        check("summary agreement", not mismatches, mismatches, "within lane tolerance")
        check("finite Holder promoted", p.get("finite_inverse_free_sandwiched_holder_closed") is True and i.get("finite_inverse_free_sandwiched_holder_closed") is True, [p.get("finite_inverse_free_sandwiched_holder_closed"), i.get("finite_inverse_free_sandwiched_holder_closed")], True)
        check("uniformity remains open", p.get("local_fourth_moment_uniform_closed") is False and i.get("local_fourth_moment_uniform_closed") is False and p.get("source_volume_cutoff_beta_uniform_closed") is False and i.get("source_volume_cutoff_beta_uniform_closed") is False, [p, i], False)

    check("scope firewall", scope["finite_inverse_free_sandwiched_holder_closed"] and scope["finite_actual_q3_history_rows_closed"] and scope["finite_two_orientation_rows_closed"] and not scope["local_fourth_moment_uniform_closed"] and not scope["modular_domain_transfer_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite Holder; QFT gates open")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SANDWICHED-HOLDER-ENVELOPE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean, "boundary": scope, "derived": {"primary_summary_rows": p.get("summary_rows", []), "independent_summary_rows": i.get("summary_rows", []), "finite_inverse_free_sandwiched_holder_closed": True, "uniformity_promoted": False, "common_core_promoted": False, "qft_promoted": False}, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": primary_hash, "independent_sha256": independent_hash, "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}}


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
    print(f"INTEGRATED FINITE-SANDWICHED-HOLDER-ENVELOPE PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
