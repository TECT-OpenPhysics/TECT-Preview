#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001174."""

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

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-common-word-cauchy"
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
            if field in ("matrix_real", "matrix_imag"):
                one_array, two_array = np.asarray(one[field], dtype=float), np.asarray(two[field], dtype=float)
                if one_array.shape != two_array.shape or not np.allclose(one_array, two_array, rtol=tolerance, atol=tolerance):
                    return False, f"row {index} {field} mismatch"
            elif abs(float(one[field]) - float(two[field])) > tolerance * (1.0 + abs(float(one[field]))):
                return False, f"row {index} {field} mismatch"
    return True, "all contexts agree within tolerance"


def compare_derived(left: dict[str, Any], right: dict[str, Any], fields: tuple[str, ...], tolerance: float) -> tuple[bool, str]:
    for field in fields:
        one, two = left.get(field), right.get(field)
        if isinstance(one, list) and isinstance(two, list):
            if len(one) != len(two) or not np.allclose(np.asarray(one, dtype=float), np.asarray(two, dtype=float), rtol=tolerance, atol=tolerance):
                return False, f"derived {field} mismatch"
        elif isinstance(one, bool) or isinstance(two, bool):
            if one != two:
                return False, f"derived {field} mismatch"
        elif abs(float(one) - float(two)) > tolerance * (1.0 + abs(float(one))):
            return False, f"derived {field} mismatch"
    return True, "derived values agree"


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

    check("identity", manifest["exploration_id"] == "EXP-001174" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001174/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("graph fixture", list(manifest["finite_fixture"]["graphs"]) == ["path2", "path3", "path4", "path5", "bond2", "square4", "grid2x3"], list(manifest["finite_fixture"]["graphs"]), "registered contexts")
    check("scope firewall", scope["finite_q3_transfer_closed"] and scope["finite_os_gram_closed"] and scope["finite_thermal_cyclicity_closed"] and scope["identical_local_word_descriptor_closed"] and scope["finite_context_comparison_closed"] and not scope["source_uniform_common_word_closed"] and not scope["volume_uniform_os_cauchy_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite comparison only")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-common-word-cauchy-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        tolerance = float(manifest["finite_fixture"]["agreement_tolerance"])
        gram_ok, gram_message = compare_rows(primary.get("gram_rows", []), independent.get("gram_rows", []), ("graph", "source_site", "beta"), ("min_eigenvalue", "max_eigenvalue", "diagonal_min", "reflection_error", "partition_function", "matrix_real", "matrix_imag"), tolerance)
        check("OS Gram crosscheck", gram_ok, gram_message, "same contexts and values")
        thermal_ok, thermal_message = compare_rows(primary.get("thermal_rows", []), independent.get("thermal_rows", []), ("graph", "source_site", "beta", "fraction"), ("forward_real", "forward_imag", "reverse_real", "reverse_imag", "cyclicity_residual", "witness", "seconds"), tolerance)
        check("thermal word crosscheck", thermal_ok, thermal_message, "same contexts and values")
        comparison_ok, comparison_message = compare_rows(primary.get("comparisons", []), independent.get("comparisons", []), ("from_graph", "to_graph", "beta"), ("from_volume", "to_volume", "gram_max_delta", "gram_frobenius_delta", "gram_relative_max_delta", "thermal_max_delta", "thermal_relative_max_delta", "max_context_delta"), tolerance)
        check("context delta crosscheck", comparison_ok, comparison_message, "same adjacent context deltas")
        check("Gram row count", len(primary.get("gram_rows", [])) == len(independent.get("gram_rows", [])) == primary.get("derived", {}).get("gram_row_count"), [len(primary.get("gram_rows", [])), len(independent.get("gram_rows", [])), primary.get("derived", {}).get("gram_row_count")], "equal")
        check("thermal row count", len(primary.get("thermal_rows", [])) == len(independent.get("thermal_rows", [])) == primary.get("derived", {}).get("thermal_row_count"), [len(primary.get("thermal_rows", [])), len(independent.get("thermal_rows", [])), primary.get("derived", {}).get("thermal_row_count")], "equal")
        check("comparison row count", len(primary.get("comparisons", [])) == len(independent.get("comparisons", [])) == primary.get("derived", {}).get("comparison_count"), [len(primary.get("comparisons", [])), len(independent.get("comparisons", [])), primary.get("derived", {}).get("comparison_count")], "equal")
        derived_fields = ("context_count", "nested_pair_count", "gram_row_count", "thermal_row_count", "comparison_count", "min_context_delta", "max_context_delta", "path_beta0_delta_sequence", "path_beta0_delta_nonincreasing", "finite_q3_transfer_closed", "finite_os_gram_closed", "finite_thermal_cyclicity_closed", "identical_local_word_descriptor_closed", "finite_context_comparison_closed", "source_uniform_common_word_closed", "volume_uniform_direct_d_cauchy_closed", "volume_uniform_os_cauchy_closed", "exhaustion_independence_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed", "no_new_negative_result", "no_tier_change", "no_pdf")
        derived_ok, derived_message = compare_derived(primary.get("derived", {}), independent.get("derived", {}), derived_fields, tolerance)
        check("derived crosscheck", derived_ok, derived_message, "equal within tolerance")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R247.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-COMMON-WORD-CAUCHY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(assertions),
        "assertions": assertions,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)},
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-COMMON-WORD-CAUCHY PASS {len(assertions)}/{len(assertions)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
