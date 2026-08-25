#!/usr/bin/env python3
"""Integrated verifier for EXP-001152."""

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
SLUG = "pre_a_cp1_st8_q3lock_full_character_double_commutator_bound"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-full-character-double-commutator-bound-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
KINETIC = REPO / "strategy/pre-a-cp1-st8-q3lock-uniform-kinetic-character-moment-corollary-manifest.json"
FORCE = REPO / "strategy/pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge-manifest.json"
M5_AUTHORITY = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-doublet-route-split-manifest.json"
LEAN = REPO / "verification/lean/Tect/R322.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
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
    command = "lake env lean Tect/R322.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R322.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    kinetic = json.loads(KINETIC.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    m5_authority = json.loads(M5_AUTHORITY.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    oracle = manifest["derived_oracles"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001152" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001152/T-054/false")
    check("upstream kinetic", kinetic["exploration_id"] == "EXP-001068" and kinetic["scope"]["kinetic_character_two_sided_gibbs_bound_closed"] is True, kinetic["exploration_id"], "EXP-001068 closed")
    check("upstream force", force["exploration_id"] == "EXP-001061" and force["scope"]["compact_source_endpoint_third_moment_bridge_closed"] is True, force["exploration_id"], "EXP-001061 closed")
    check("upstream m5", "m5<infinity" in m5_authority["actual_q3_static_fifth_moment_and_elliptic_embedding"]["conclusion"], m5_authority["exploration_id"], "uniform m5")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["onsite_force_coefficient_fixture", "edge_force_polynomial_fixture", "pair_moment_fixture", "force_fourth_fixture", "kinetic_fixture", "full_safe_bound_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="full-character-double-commutator-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("passed", 0) > 0 and independent.get("passed", 0) > 0, [primary.get("passed"), independent.get("passed")], ">0")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        keys = ("onsite_force_fourth_coefficient", "edge_constant", "max_pair_factor", "pair_moment", "edge_single_fourth_bound", "edge_sum_fourth_bound", "force_fourth_bound", "kinetic_second_norm_bound", "force_safe_second_norm_bound", "full_safe_second_norm_bound")
        for key in keys:
            check(f"lane agreement {key}", p.get(key) == i.get(key), [p.get(key), i.get(key)], "equal exact values")
            check(f"oracle {key}", p.get(key) == oracle.get(key), p.get(key), oracle.get(key))
        check("grid coverage", p.get("onsite_force_grid_rows") == i.get("onsite_force_grid_rows") == 9 and p.get("edge_force_grid_rows") == i.get("edge_force_grid_rows") == 81 and p.get("pair_energy_grid_rows") == i.get("pair_energy_grid_rows") == 81, [p, i], "9/81/81")
        closed_keys = ("global_scalar_edge_force_bound_closed", "onsite_force_fourth_moment_envelope_closed", "full_onsite_edge_force_fourth_moment_bound_closed", "full_character_second_commutator_safe_bound_closed", "registered_periodic_compact_source_static_q3_scope_closed")
        check("static closure", all(p.get(key) is True and i.get(key) is True for key in closed_keys), [p, i], True)
        open_keys = ("arbitrary_boundary_extension_closed", "all_shape_exhaustion_uniformity_closed", "exact_ccr_common_core_closed", "modular_domain_transfer_closed", "actual_q3_four_context_history_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
        check("QFT firewall", all(p.get(key) is False and i.get(key) is False for key in open_keys), [p, i], "history and downstream open")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FULL-CHARACTER-DOUBLE-COMMUTATOR-BOUND",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "kinetic_manifest_sha256": sha256(KINETIC), "force_manifest_sha256": sha256(FORCE), "m5_manifest_sha256": sha256(M5_AUTHORITY)}
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
    print(f"INTEGRATED FULL-CHARACTER-DOUBLE-COMMUTATOR-BOUND PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
