#!/usr/bin/env python3
"""Integrated verifier for EXP-001144."""

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
SLUG = "pre_a_cp1_st8_q3lock_energy_moment_norm_counterexample"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-energy-moment-norm-counterexample-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R314.lean"
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
    command = "lake env lean Tect/R314.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R314.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() and "warning:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def compare(primary: dict[str, Any], independent: dict[str, Any], tolerance: float) -> tuple[bool, list[dict[str, Any]]]:
    keys = ("logarithmic_mean", "M2", "spectral_moment", "operator_candidate_bound", "weighted_rhs", "coarse_trace_bound")
    mismatches: list[dict[str, Any]] = []
    for key in keys:
        left, right = primary.get(key), independent.get(key)
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)) or abs(float(left) - float(right)) > tolerance:
            mismatches.append({"key": key, "primary": left, "independent": right})
    return not mismatches, mismatches


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    tolerance = float(manifest["finite_fixture"]["tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001144" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001144/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    primary_hash, independent_hash = sha256(PRIMARY), sha256(INDEPENDENT)
    check("source lanes distinct", primary_hash != independent_hash, [primary_hash, independent_hash], "distinct SHA-256")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="energy-moment-norm-counterexample-") as temporary:
        primary_process, primary_payload = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent_payload = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary_payload.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent_payload.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary_payload.get("derived", {}), independent_payload.get("derived", {})
        agreement, mismatches = compare(p, i, tolerance)
        check("numeric agreement", agreement, mismatches, "within tolerance")
        check("counterexample agreement", p.get("operator_norm_general_transfer_refuted") is True and i.get("operator_norm_general_transfer_refuted") is True and p.get("hilbert_schmidt_general_transfer_refuted") is True and i.get("hilbert_schmidt_general_transfer_refuted") is True, [p, i], "both norm routes refuted")
        check("corrected interface agreement", p.get("D_weighted_two_sided_interface_identified") is True and i.get("D_weighted_two_sided_interface_identified") is True, [p, i], "D-weighted interface identified")

    check("scope firewall", scope["two_level_counterexample_closed"] and scope["operator_norm_general_transfer_refuted"] and scope["hilbert_schmidt_general_transfer_refuted"] and scope["D_weighted_two_sided_interface_identified"] and not scope["uniform_local_M2_common_core_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "route correction only")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ENERGY-MOMENT-NORM-COUNTEREXAMPLE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "boundary": scope,
        "derived": {
            "primary": p,
            "independent": i,
            "two_level_counterexample_promoted": True,
            "unweighted_M2_norm_transfer_promoted": False,
            "D_weighted_two_sided_interface_promoted": True,
            "uniformity_promoted": False,
            "qft_promoted": False
        },
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "primary_sha256": primary_hash,
            "independent_sha256": independent_hash,
            "manifest_sha256": sha256(MANIFEST),
            "lean_sha256": sha256(LEAN)
        }
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
    print(f"INTEGRATED ENERGY-MOMENT-NORM-COUNTEREXAMPLE PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
