#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001168."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-shape-split-operator-equality"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification/lean/Tect/R337.lean"
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
    if lake is None:
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R337.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R337.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R337.lean", "returncode": process.returncode, "output": output[-2000:]}


def compare_rows(primary: list[dict[str, Any]], independent: list[dict[str, Any]], tolerance: float) -> tuple[bool, str]:
    if len(primary) != len(independent):
        return False, f"row count {len(primary)} != {len(independent)}"
    fields = ("order", "time_sign", "adjoint", "step")
    for index, (left, right) in enumerate(zip(primary, independent)):
        if any(left.get(field) != right.get(field) for field in fields):
            return False, f"row {index} context mismatch"
        for field in ("operator_norm", "frobenius_norm"):
            if abs(float(left[field]) - float(right[field])) > tolerance:
                return False, f"row {index} {field} mismatch"
    return True, "all contexts and norms agree within tolerance"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001168" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001168/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    scope = manifest["scope"]
    check("scope firewall", scope["finite_operator_shape_equality_closed"] and scope["finite_first_external_step_witness_closed"] and not scope["analytic_trotter_rate_closed"] and not scope["common_core_domain_closed"] and not scope["N_to_infinity_common_alpha_closed"], scope, "finite shape only")
    source = LEAN.read_text(encoding="utf-8")
    markers = ["square_ball_fixture", "cube_ball_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-shape-split-operator-equality-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("total", 0) > 0 and independent.get("total", 0) > 0, [primary.get("total"), independent.get("total")], ">0")
        check("shape metadata", primary.get("shape_equivalence") == independent.get("shape_equivalence"), [primary.get("shape_equivalence"), independent.get("shape_equivalence")], "same rooted fixture")
        row_ok, row_message = compare_rows(primary.get("shape_rows", []), independent.get("shape_rows", []), float(manifest["finite_fixture"]["comparison_tolerance"]))
        check("shape rows crosscheck", row_ok, row_message, "same contexts and numerical norms")
        for key in ("finite_operator_shape_equality_closed", "finite_first_external_step_witness_closed", "rooted_ball_hypothesis_explicit", "analytic_trotter_rate_closed", "uniform_graph_lipschitz_closed", "common_core_domain_closed", "direct_d_delta_d_cauchy_closed", "N_to_infinity_common_alpha_closed", "exhaustion_independence_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed", "no_new_negative_result", "no_tier_change", "no_pdf"):
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal")
        check("inside bound agreement", abs(float(primary["derived"]["max_inside_operator_norm"]) - float(independent["derived"]["max_inside_operator_norm"])) <= float(manifest["finite_fixture"]["comparison_tolerance"]), [primary["derived"]["max_inside_operator_norm"], independent["derived"]["max_inside_operator_norm"]], "within tolerance")
        check("external witness agreement", abs(float(primary["derived"]["min_first_external_operator_norm"]) - float(independent["derived"]["min_first_external_operator_norm"])) <= float(manifest["finite_fixture"]["comparison_tolerance"]), [primary["derived"]["min_first_external_operator_norm"], independent["derived"]["min_first_external_operator_norm"]], "within tolerance")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R337.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SHAPE-SPLIT-OPERATOR-EQUALITY",
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
    print(f"INTEGRATED FINITE-SHAPE-SPLIT-OPERATOR-EQUALITY PASS {len(assertions)}/{len(assertions)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
