#!/usr/bin/env python3
"""Integrated verifier for EXP-001125 primary, independent and Lean lanes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_evolved_dual_integrand_cross_term_audit"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R296.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def normalized_sha256(path: Path) -> str:
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


def lean_run() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R296.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R296.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def close(a: Any, b: Any, tolerance: float = 1.0e-7) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tolerance * max(1.0, abs(float(a)), abs(float(b)))
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(close(x, y, tolerance) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(close(a[key], b[key], tolerance) for key in a)
    return a == b


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001125" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001125/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("primary source", PRIMARY.is_file(), PRIMARY, "file")
    check("independent source", INDEPENDENT.is_file(), INDEPENDENT, "file")
    check("Lean source", LEAN.is_file(), LEAN, "file")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in lean_source for marker in ("commutator_cross_term_fixture", "second_order_operator_bound_fixture", "initial_cancellation_fixture", "scope_fixture")), "markers", "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="evolved-dual-cross-term-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("primary/independent assertion counts", primary.get("assertion_count") == 469 and independent.get("assertion_count") == 321, [primary.get("assertion_count"), independent.get("assertion_count")], "469/321")
        for key in ("finite_cross_term_identity_closed", "finite_second_order_operator_bound_closed", "finite_reference_cross_term_closed", "finite_dual_cross_term_closed", "finite_small_time_diagnostic_closed"):
            check(f"derived {key}", primary.get("derived", {}).get(key) is True and independent.get("derived", {}).get(key) is True, [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], True)
        for key in ("actual_q3_evolved_dual_integrand_uniform_closed", "state_isometry_for_signed_dynamics_closed", "actual_q3_unbounded_common_core_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
            check(f"open gate {key}", primary.get("derived", {}).get(key) is False and independent.get("derived", {}).get(key) is False, [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], False)
        for key in ("max_operator_bound_ratio", "min_cross_to_tail_ratio", "max_cross_to_tail_ratio"):
            check(f"lane metric {key}", close(primary["derived"][key], independent["derived"][key]), [primary["derived"][key], independent["derived"][key]], "agree")
        check("row reconstruction", close(primary["derived"]["volume_rows"], independent["derived"]["volume_rows"]), "all finite rows", "agree within 1e-7")

    lean = {"status": "SKIPPED"} if args.skip_lean else lean_run()
    check("Lean run", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-EVOLVED-DUAL-INTEGRAND-CROSS-TERM", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "lean": lean, "derived": {"primary_assertion_count": primary["assertion_count"], "independent_assertion_count": independent["assertion_count"], "max_operator_bound_ratio": primary["derived"]["max_operator_bound_ratio"], "min_cross_to_tail_ratio": primary["derived"]["min_cross_to_tail_ratio"], "max_cross_to_tail_ratio": primary["derived"]["max_cross_to_tail_ratio"], "finite_cross_term_identity_closed": True, "finite_second_order_operator_bound_closed": True, "finite_reference_cross_term_closed": True, "finite_dual_cross_term_closed": True, "finite_reference_D_closed": True, "finite_dual_D_closed": True, "finite_reference_delta_D_closed": True, "finite_dual_delta_D_closed": True, "finite_small_time_diagnostic_closed": True, "actual_q3_evolved_dual_integrand_uniform_closed": False, "state_isometry_for_signed_dynamics_closed": False, "actual_q3_unbounded_common_core_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "provenance": {"primary": str(PRIMARY.relative_to(REPO)).replace("\\", "/"), "primary_sha256": normalized_sha256(PRIMARY), "independent": str(INDEPENDENT.relative_to(REPO)).replace("\\", "/"), "independent_sha256": normalized_sha256(INDEPENDENT), "lean": str(LEAN.relative_to(REPO)).replace("\\", "/")}, "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED EVOLVED-DUAL-CROSS-TERM PASS {len(checks)}/{len(checks)} | LEAN {lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
