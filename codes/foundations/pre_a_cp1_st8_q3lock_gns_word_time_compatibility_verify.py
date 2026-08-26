#!/usr/bin/env python3
"""Integrated primary/independent/pinned-Lean verifier for EXP-001182."""

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
SLUG = "pre-a-cp1-st8-q3lock-gns-word-time-compatibility"
AUDIT = "PA-CP1-ST8-Q3LOCK-FINITE-GNS-WORD-TIME-COMPATIBILITY"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
PRIMARY = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R342.lean"
LEAN_ROOT = REPO / "verification" / "lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-integrated-{SLUG}" / "integrated.json"
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
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def run_lean() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R342.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R342.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def compare_rows(primary: list[dict[str, Any]], independent: list[dict[str, Any]], tolerance: float, key_fields: tuple[str, ...], numeric_fields: tuple[str, ...]) -> tuple[bool, str]:
    if len(primary) != len(independent):
        return False, f"row count {len(primary)} != {len(independent)}"
    left = {tuple(row[field] for field in key_fields): row for row in primary}
    right = {tuple(row[field] for field in key_fields): row for row in independent}
    if len(left) != len(primary) or len(right) != len(independent):
        return False, "duplicate row key"
    if set(left) != set(right):
        return False, "row key sets differ"
    for key in sorted(left):
        for field in numeric_fields:
            a, b = float(left[key][field]), float(right[key][field])
            if abs(a - b) > tolerance + tolerance * max(1.0, abs(a), abs(b)):
                return False, f"{key} {field}: {a} != {b}"
    return True, "all rows agree within tolerance"


def compare_derived(primary: dict[str, Any], independent: dict[str, Any], tolerance: float, condition_tolerance: float) -> tuple[bool, str]:
    left, right = primary.get("derived", {}), independent.get("derived", {})
    if left.get("lean_marker") != right.get("lean_marker"):
        return False, "Lean marker differs"
    general_fields = ("row_count", "max_restricted_transport_compatibility_residual", "max_translated_gram_delta_relative", "max_base_congruence_residual", "max_expanded_congruence_residual", "max_base_transport_distance", "max_expanded_transport_distance", "min_support")
    condition_fields = ("max_base_condition", "max_expanded_condition")
    for field in general_fields:
        a, b = float(left[field]), float(right[field])
        if abs(a - b) > tolerance + tolerance * max(1.0, abs(a), abs(b)):
            return False, f"derived {field}: {a} != {b}"
    for field in condition_fields:
        a, b = float(left[field]), float(right[field])
        if abs(a - b) > condition_tolerance + condition_tolerance * max(1.0, abs(a), abs(b)):
            return False, f"derived {field}: {a} != {b}"
    return True, "derived metrics agree within tolerance"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-lean", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})

    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001182", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"],], "EXP-001182/T-054/false")
    check("scope firewall", scope["finite_word_enlargement_time_translate_diagnostic_closed"] and scope["finite_base_polar_congruence_closed"] and scope["finite_expanded_polar_congruence_closed"] and not scope["word_product_star_action_intertwining_closed"] and not scope["common_os_hilbert_carrier_closed"], scope, "finite compatibility diagnostic only")
    check("fixture extension", fixture["added_word_kinds"] == ["qpq"] and fixture["translated_tau_fraction"] == 0.375, {"added_word_kinds": fixture["added_word_kinds"], "translated_tau_fraction": fixture["translated_tau_fraction"]}, "qpq at tau fraction 0.375")
    with tempfile.TemporaryDirectory(prefix="gns-word-time-compatibility-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("child audit identity", primary.get("audit_id") == independent.get("audit_id") == AUDIT, [primary.get("audit_id"), independent.get("audit_id")], "common audit id")
        check("scope agreement", primary.get("scope") == independent.get("scope"), primary.get("scope"), "identical scope")
        tolerance = float(fixture["agreement_tolerance"])
        condition_tolerance = float(fixture["condition_agreement_tolerance"])
        row_fields = ("base_congruence_relative_residual", "expanded_congruence_relative_residual", "principal_base_consistency_residual", "restricted_transport_compatibility_residual", "translated_gram_delta_relative", "base_transport_distance", "expanded_transport_distance", "min_support")
        condition_fields = ("base_condition_small", "base_condition_large", "expanded_condition_small", "expanded_condition_large")
        row_ok, row_message = compare_rows(primary.get("rows", []), independent.get("rows", []), tolerance, ("small_graph", "large_graph", "beta"), row_fields)
        check("block row agreement", row_ok, row_message, "all primary/independent block rows")
        condition_ok, condition_message = compare_rows(primary.get("rows", []), independent.get("rows", []), condition_tolerance, ("small_graph", "large_graph", "beta"), condition_fields)
        check("condition agreement", condition_ok, condition_message, "all primary/independent condition numbers")
        support_fields = tuple(key for key in primary.get("support_rows", [{}])[0] if key not in ("small_graph", "large_graph", "beta"))
        support_general_fields = tuple(key for key in support_fields if key not in condition_fields)
        support_ok, support_message = compare_rows(primary.get("support_rows", []), independent.get("support_rows", []), tolerance, ("small_graph", "large_graph", "beta"), support_general_fields)
        check("support row agreement", support_ok, support_message, "all primary/independent support rows")
        support_condition_ok, support_condition_message = compare_rows(primary.get("support_rows", []), independent.get("support_rows", []), condition_tolerance, ("small_graph", "large_graph", "beta"), condition_fields)
        check("support condition agreement", support_condition_ok, support_condition_message, "all primary/independent support condition numbers")
        derived_ok, derived_message = compare_derived(primary, independent, tolerance, condition_tolerance)
        check("derived agreement", derived_ok, derived_message, "all derived metrics")
        check("coverage agreement", len(primary.get("rows", [])) == len(independent.get("rows", [])) == len(fixture["nested_pairs"]) * len(fixture["beta_values"]), [len(primary.get("rows", [])), len(independent.get("rows", []))], "4 block rows")
        check("positive support", primary.get("derived", {}).get("min_support", 0.0) > float(fixture["support_floor"]) and independent.get("derived", {}).get("min_support", 0.0) > float(fixture["support_floor"]), [primary.get("derived", {}).get("min_support"), independent.get("derived", {}).get("min_support")], f">{fixture['support_floor']}")
        check("compatibility witness", primary.get("derived", {}).get("max_restricted_transport_compatibility_residual", 0.0) >= float(fixture["witness_floor"]) and independent.get("derived", {}).get("max_restricted_transport_compatibility_residual", 0.0) >= float(fixture["witness_floor"]), [primary.get("derived", {}).get("max_restricted_transport_compatibility_residual"), independent.get("derived", {}).get("max_restricted_transport_compatibility_residual")], f">={fixture['witness_floor']}")
        check("translated Gram witness", primary.get("derived", {}).get("max_translated_gram_delta_relative", 0.0) >= float(fixture["witness_floor"]) and independent.get("derived", {}).get("max_translated_gram_delta_relative", 0.0) >= float(fixture["witness_floor"]), [primary.get("derived", {}).get("max_translated_gram_delta_relative"), independent.get("derived", {}).get("max_translated_gram_delta_relative")], f">={fixture['witness_floor']}")
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R342.lean"} if args.skip_lean else run_lean()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/R342.lean"), None)
    check("registry integrity", entry is not None and entry["sha256"] == sha256(LEAN), entry["sha256"] if entry else None, sha256(LEAN))
    downstream = ("word_product_star_action_intertwining_closed", "common_os_hilbert_carrier_closed", "source_volume_cutoff_beta_uniform_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("downstream QFT firewall", all(not scope[field] for field in downstream), {field: scope[field] for field in downstream}, "all downstream QFT gates open")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": AUDIT, "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "rows": primary.get("rows"), "support_rows": primary.get("support_rows"), "derived": primary.get("derived"), "scope": scope, "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "registry_sha256": sha256(REGISTRY)}}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED GNS-WORD-TIME-COMPATIBILITY PASS {len(checks)}/{len(checks)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
