#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001173."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-euclidean-os-gram-kms-bridge"
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


def compare_rows(left: list[dict[str, Any]], right: list[dict[str, Any]], keys: tuple[str, ...], numeric: tuple[str, ...], tolerance: float) -> tuple[bool, str]:
    order = lambda row: tuple(row.get(key) for key in keys)
    first, second = sorted(left, key=order), sorted(right, key=order)
    if len(first) != len(second):
        return False, f"row count {len(first)} != {len(second)}"
    for index, (one, two) in enumerate(zip(first, second)):
        if order(one) != order(two):
            return False, f"row {index} context mismatch"
        for field in numeric:
            if abs(float(one[field]) - float(two[field])) > tolerance * (1.0 + abs(float(one[field]))):
                return False, f"row {index} {field} mismatch"
    return True, "all contexts agree within tolerance"


def compare_shapes(left: list[dict[str, Any]], right: list[dict[str, Any]], tolerance: float) -> bool:
    keys = ("graph", "volume", "edge_count", "degree_min", "degree_max")
    numeric = ("degree_mean", "min_gram_eigenvalue", "max_gram_reflection_error", "min_gram_diagonal", "max_cyclicity_residual", "min_cyclicity_witness")
    ok, _ = compare_rows(left, right, keys, numeric, tolerance)
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001173" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001173/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("periodic graph fixture", list(manifest["finite_fixture"]["graphs"]) == ["bond2", "square4", "grid2x3"], list(manifest["finite_fixture"]["graphs"]), "bond2/square4/grid2x3")
    check("scope firewall", scope["finite_q3_euclidean_transfer_closed"] and scope["finite_os_reflection_gram_closed"] and scope["finite_thermal_cyclicity_closed"] and scope["all_source_sites_closed"] and not scope["finite_to_os_intertwiner_closed"] and not scope["common_alpha_closed"], scope, "finite OS-facing diagnostic only")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-euclidean-os-gram-kms-bridge-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        tolerance = float(manifest["finite_fixture"]["agreement_tolerance"])
        gram_ok, gram_message = compare_rows(primary.get("gram_rows", []), independent.get("gram_rows", []), ("graph", "source_site", "beta"), ("min_eigenvalue", "max_eigenvalue", "diagonal_min", "reflection_error"), tolerance)
        check("OS Gram crosscheck", gram_ok, gram_message, "same contexts and values")
        thermal_ok, thermal_message = compare_rows(primary.get("thermal_rows", []), independent.get("thermal_rows", []), ("graph", "source_site", "beta", "fraction"), ("forward_real", "forward_imag", "reverse_real", "reverse_imag", "cyclicity_residual", "witness"), tolerance)
        check("thermal word crosscheck", thermal_ok, thermal_message, "same contexts and values")
        check("shape summary crosscheck", compare_shapes(primary.get("shape_summaries", []), independent.get("shape_summaries", []), tolerance), "primary/independent shape summaries", "within tolerance")
        check("Gram row count", len(primary.get("gram_rows", [])) == len(independent.get("gram_rows", [])) == primary.get("derived", {}).get("gram_row_count"), [len(primary.get("gram_rows", [])), len(independent.get("gram_rows", [])), primary.get("derived", {}).get("gram_row_count")], "equal")
        check("thermal row count", len(primary.get("thermal_rows", [])) == len(independent.get("thermal_rows", [])) == primary.get("derived", {}).get("thermal_row_count"), [len(primary.get("thermal_rows", [])), len(independent.get("thermal_rows", [])), primary.get("derived", {}).get("thermal_row_count")], "equal")
        check("shape row count", len(primary.get("shape_summaries", [])) == len(independent.get("shape_summaries", [])) == primary.get("derived", {}).get("shape_count"), [len(primary.get("shape_summaries", [])), len(independent.get("shape_summaries", [])), primary.get("derived", {}).get("shape_count")], "equal")
        for flag in ("finite_q3_euclidean_transfer_closed", "finite_os_reflection_gram_closed", "finite_thermal_cyclicity_closed", "all_source_sites_closed", "shape_degree_diagnostic_closed", "finite_to_os_intertwiner_closed", "source_uniform_direct_d_cauchy_closed", "volume_uniform_direct_d_cauchy_closed", "beta_uniform_direct_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed", "no_new_negative_result", "no_tier_change", "no_pdf"):
            check(f"lane agreement {flag}", primary.get("derived", {}).get(flag) == independent.get("derived", {}).get(flag), [primary.get("derived", {}).get(flag), independent.get("derived", {}).get(flag)], "equal")
        check("minimum Gram eigenvalue agreement", abs(float(primary["derived"]["min_gram_eigenvalue"]) - float(independent["derived"]["min_gram_eigenvalue"])) <= tolerance, [primary["derived"]["min_gram_eigenvalue"], independent["derived"]["min_gram_eigenvalue"]], "within tolerance")
        check("maximum cyclicity agreement", abs(float(primary["derived"]["max_cyclicity_residual"]) - float(independent["derived"]["max_cyclicity_residual"])) <= tolerance, [primary["derived"]["max_cyclicity_residual"], independent["derived"]["max_cyclicity_residual"]], "within tolerance")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R247.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-EUCLIDEAN-OS-GRAM-KMS-BRIDGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(assertions),
        "assertions": assertions,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-EUCLIDEAN-OS-GRAM-KMS-BRIDGE PASS {len(assertions)}/{len(assertions)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
