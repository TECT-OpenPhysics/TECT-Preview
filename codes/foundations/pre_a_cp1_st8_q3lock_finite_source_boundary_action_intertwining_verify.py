#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001183."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-source-boundary-action-intertwining"
AUDIT = "PA-CP1-ST8-Q3LOCK-FINITE-SOURCE-BOUNDARY-ACTION-INTERTWINING"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
PRIMARY = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R343.lean"
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
    command = "lake env lean Tect/R343.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R343.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def compare_rows(left_rows: list[dict[str, Any]], right_rows: list[dict[str, Any]], key_fields: tuple[str, ...], numeric_fields: tuple[str, ...], tolerance: float) -> tuple[bool, str]:
    left = {tuple(row[field] for field in key_fields): row for row in left_rows}
    right = {tuple(row[field] for field in key_fields): row for row in right_rows}
    if len(left) != len(left_rows) or len(right) != len(right_rows):
        return False, "duplicate row key"
    if set(left) != set(right):
        return False, f"row keys differ: {sorted(set(left) ^ set(right))}"
    for key in sorted(left):
        for field in numeric_fields:
            first, second = float(left[key][field]), float(right[key][field])
            if abs(first - second) > tolerance + tolerance * max(1.0, abs(first), abs(second)):
                return False, f"{key} {field}: {first} != {second}"
    return True, "all rows agree within tolerance"


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})

    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001183", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001183/T-054/false")
    check("scope firewall", scope["finite_duhamel_action_intertwining_identity_closed"] and scope["finite_euclidean_source_boundary_diagnostic_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite source-boundary diagnostic only")
    check("fixture", fixture["nested_pairs"] == [["path2", "path3"], ["path3", "path4"]] and fixture["observable_kinds"] == ["q", "p"], fixture, "declared nested source fixture")
    with tempfile.TemporaryDirectory(prefix="finite-source-boundary-intertwining-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("audit identity", primary.get("audit_id") == independent.get("audit_id") == AUDIT, [primary.get("audit_id"), independent.get("audit_id")], AUDIT)
        check("scope agreement", primary.get("scope") == independent.get("scope"), primary.get("scope"), "identical scope")
        tolerance = float(fixture["finite_tolerance"])
        order_ok, order_message = compare_rows(primary.get("order_rows", []), independent.get("order_rows", []), ("small_graph", "large_graph", "kind", "order"), ("difference_frobenius",), tolerance)
        check("order-row agreement", order_ok, order_message, "all order rows")
        boundary_ok, boundary_message = compare_rows(primary.get("source_boundary_rows", []), independent.get("source_boundary_rows", []), ("small_graph", "large_graph"), ("boundary_frobenius", "q_source_commutator", "p_source_commutator"), tolerance)
        check("boundary-row agreement", boundary_ok, boundary_message, "all boundary rows")
        action_ok, action_message = compare_rows(primary.get("action_rows", []), independent.get("action_rows", []), ("small_graph", "large_graph", "kind", "seconds"), ("direct_defect_frobenius", "direct_defect_relative", "duhamel_reconstruction_frobenius", "duhamel_residual_frobenius", "duhamel_residual_relative"), tolerance)
        check("action-row agreement", action_ok, action_message, "all real-time rows")
        os_ok, os_message = compare_rows(primary.get("os_rows", []), independent.get("os_rows", []), ("small_graph", "large_graph", "kind", "beta", "tau_fraction"), ("partition_small", "partition_large", "defect_frobenius", "defect_relative"), tolerance)
        check("OS-row agreement", os_ok, os_message, "all Euclidean rows")
        for field in ("pair_count", "order_row_count", "action_row_count", "os_row_count", "max_source_commutator", "max_action_defect_relative", "max_duhamel_residual_relative", "max_os_defect_relative"):
            first, second = float(primary.get("derived", {}).get(field)), float(independent.get("derived", {}).get(field))
            check(f"derived {field}", abs(first - second) <= tolerance + tolerance * max(1.0, abs(first), abs(second)), [first, second], "agree within tolerance")
        check("first-order agreement", primary.get("derived", {}).get("first_nonzero_orders") == independent.get("derived", {}).get("first_nonzero_orders"), primary.get("derived", {}).get("first_nonzero_orders"), "identical finite order diagnostics")
        check("row coverage", len(primary.get("action_rows", [])) == len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * len(fixture["real_time_values"]) and len(primary.get("os_rows", [])) == len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * len(fixture["beta_values"]) * len(fixture["euclidean_time_fractions"]), [len(primary.get("action_rows", [])), len(primary.get("os_rows", []))], "20 real-time and 24 Euclidean rows")
        check("finite action witness", primary.get("derived", {}).get("max_action_defect_relative", 0.0) > float(fixture["order_witness_floor"]), primary.get("derived", {}).get("max_action_defect_relative"), f">{fixture['order_witness_floor']}")
        check("finite OS witness", primary.get("derived", {}).get("max_os_defect_relative", 0.0) > float(fixture["order_witness_floor"]), primary.get("derived", {}).get("max_os_defect_relative"), f">{fixture['order_witness_floor']}")
    lean = run_lean()
    check("Lean R343", lean["status"] == "PASS", lean, "PASS")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R343.lean"), None)
    check("registry R343", entry is not None and entry.get("sha256") == sha256(LEAN) and entry.get("declarations") == ["commutator_difference", "commutator_difference_zero"], entry, "registered LF hash and declarations")
    downstream = ("source_volume_cutoff_beta_uniform_closed", "word_product_star_action_intertwining_closed", "common_os_hilbert_carrier_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("downstream QFT firewall", all(not scope[field] for field in downstream), {field: scope[field] for field in downstream}, "all downstream QFT gates open")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": AUDIT, "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "source_boundary_rows": primary.get("source_boundary_rows"), "order_rows": primary.get("order_rows"), "action_rows": primary.get("action_rows"), "os_rows": primary.get("os_rows"), "derived": primary.get("derived"), "scope": scope, "boundary": manifest["boundary"], "lean": lean, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "registry_sha256": sha256(REGISTRY)}}
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-lean", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    if args.skip_lean:
        raise SystemExit("--skip-lean is not permitted for this integrated verifier")
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-SOURCE-BOUNDARY-ACTION-INTERTWINING PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
