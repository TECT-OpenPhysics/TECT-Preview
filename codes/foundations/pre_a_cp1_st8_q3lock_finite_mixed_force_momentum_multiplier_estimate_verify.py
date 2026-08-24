#!/usr/bin/env python3
"""Integrated verifier for EXP-001081."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-mixed-force-momentum-multiplier-estimate"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_finite_mixed_force_momentum_multiplier_estimate.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_finite_mixed_force_momentum_multiplier_estimate_independent.py"
LEAN = REPO / "verification/lean/Tect/R263.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "integrated.json"
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
    lake = lake_path()
    command = "lake env lean Tect/R263.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R263.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001081" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001081/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["mixed_bound_fixture", "force_fixture", "force_prime_fixture", "product_rule_fixture", "finite_scaling_diagnostic_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-mixed-force-momentum-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive assertion totals", primary.get("passed", 0) > 0 and independent.get("passed", 0) > 0, [primary.get("passed"), independent.get("passed")], ">0")
        p_rows = primary.get("derived", {}).get("dimension_rows", [])
        i_rows = independent.get("derived", {}).get("dimension_rows", [])
        check("lane dimensions", [item.get("n") for item in p_rows] == [item.get("n") for item in i_rows], [[item.get("n") for item in p_rows], [item.get("n") for item in i_rows]], "equal")
        p_u = primary.get("derived", {}).get("fixed_radius_multiplier_norms", [])
        i_u = independent.get("derived", {}).get("fixed_radius_multiplier_norms", [])
        check("lane scaling length", len(p_u) == len(i_u) == len(manifest["finite_fixture"]["n_values"]), [len(p_u), len(i_u)], len(manifest["finite_fixture"]["n_values"]),)
        check("lane scaling agreement", all(abs(float(a) - float(b)) < 1.0e-8 * (1.0 + abs(float(a))) for a, b in zip(p_u, i_u)), [p_u, i_u], "within 1e-8 relative")
        for p_item, i_item in zip(p_rows, i_rows):
            check(f"lane n={p_item['n']} radius count", len(p_item.get("radii", [])) == len(i_item.get("radii", [])), [len(p_item.get("radii", [])), len(i_item.get("radii", []))], "equal")
            for p_radius, i_radius in zip(p_item.get("radii", []), i_item.get("radii", [])):
                check(f"lane n={p_item['n']} L={p_radius['radius']}", all(abs(float(p_radius[key]) - float(i_radius[key])) < 1.0e-8 * (1.0 + abs(float(p_radius[key]))) for key in ("actual_root", "bound_root", "multiplier_norm", "derivative_norm", "kinetic_root")), [p_radius, i_radius], "within 1e-8 relative")

    open_keys = ("unweighted_cutoff_uniformity_proved", "energy_weighted_mixed_bound_closed", "actual_ccr_domain_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-MIXED-FORCE-MOMENTUM-MULTIPLIER-ESTIMATE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)},
    }
    return payload


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
    print(f"INTEGRATED FINITE-MIXED-FORCE-MOMENTUM PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
