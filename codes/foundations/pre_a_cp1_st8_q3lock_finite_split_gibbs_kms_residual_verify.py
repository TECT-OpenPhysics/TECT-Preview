#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001170."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-split-gibbs-kms-residual"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification/lean/Tect/R247.lean"
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


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R247.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R247.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (row.get("graph"), row.get("beta"), row.get("delta"), row.get("order"), row.get("sign"))


def compare_rows(primary: list[dict[str, Any]], independent: list[dict[str, Any]], tolerance: float) -> tuple[bool, str]:
    left = sorted(primary, key=row_key)
    right = sorted(independent, key=row_key)
    if len(left) != len(right):
        return False, f"row count {len(left)} != {len(right)}"
    fields = ("stationarity_defect", "kms_residual", "complex_inverse_error")
    for index, (one, two) in enumerate(zip(left, right)):
        if row_key(one) != row_key(two):
            return False, f"row {index} context mismatch"
        for field in fields:
            scale = 1.0 + abs(float(one[field]))
            if abs(float(one[field]) - float(two[field])) > tolerance * scale:
                return False, f"row {index} {field} mismatch"
    return True, "all contexts and residuals agree within tolerance"


def compare_mesh(primary: list[dict[str, Any]], independent: list[dict[str, Any]], tolerance: float) -> bool:
    left = sorted(primary, key=lambda row: (row.get("graph"), row.get("beta"), row.get("order"), row.get("sign")))
    right = sorted(independent, key=lambda row: (row.get("graph"), row.get("beta"), row.get("order"), row.get("sign")))
    if len(left) != len(right):
        return False
    for one, two in zip(left, right):
        if any(one.get(key) != two.get(key) for key in ("graph", "beta", "order", "sign", "coarse_delta", "fine_delta")):
            return False
        for key in ("kms_ratio", "stationarity_ratio"):
            if abs(float(one[key]) - float(two[key])) > tolerance * (1.0 + abs(float(one[key]))):
                return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001170" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001170/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("scope firewall", scope["finite_exact_gibbs_control_closed"] and scope["finite_split_stationarity_rows_closed"] and scope["finite_split_kms_residual_rows_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite split KMS diagnostic only")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean source", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-split-gibbs-kms-residual-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        tolerance = float(manifest["finite_fixture"]["agreement_tolerance"])
        row_ok, row_message = compare_rows(primary.get("rows", []), independent.get("rows", []), tolerance)
        check("row crosscheck", row_ok, row_message, "same contexts and residuals")
        check("mesh crosscheck", compare_mesh(primary.get("mesh_rows", []), independent.get("mesh_rows", []), tolerance), "primary/independent mesh ratios", "within tolerance")
        check("exact control crosscheck", len(primary.get("exact_rows", [])) == len(independent.get("exact_rows", [])) > 0, [len(primary.get("exact_rows", [])), len(independent.get("exact_rows", []))], ">0 and equal")
        check("shape coverage", len(primary.get("shape_rows", [])) == len(independent.get("shape_rows", [])) == len(primary.get("rows", [])), [len(primary.get("shape_rows", [])), len(independent.get("shape_rows", [])), len(primary.get("rows", []))], "equal")
        for key in ("exact_gibbs_kms_control_closed", "finite_split_stationarity_rows_closed", "finite_split_kms_residual_rows_closed", "mesh_decrease_diagnostic_closed", "path_exhaustion_diagnostic_closed", "volume_uniform_direct_d_cauchy_closed", "beta_uniform_direct_d_cauchy_closed", "modular_domain_transfer_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed", "no_new_negative_result", "no_tier_change", "no_pdf"):
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal")
        check("witness agreement", abs(float(primary["derived"]["min_kms_residual"]) - float(independent["derived"]["min_kms_residual"])) <= tolerance, [primary["derived"]["min_kms_residual"], independent["derived"]["min_kms_residual"]], "within tolerance")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R247.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SPLIT-GIBBS-KMS-RESIDUAL",
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
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-SPLIT-GIBBS-KMS-RESIDUAL PASS {len(checks)}/{len(checks)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
