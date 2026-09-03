#!/usr/bin/env python3
"""Integrated verifier for EXP-001069."""

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
SLUG = "pre-a-cp1-st8-q3lock-static-character-full-double-commutator-bound"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_static_character_full_double_commutator_bound.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_static_character_full_double_commutator_bound_independent.py"
LEAN = REPO / "verification/lean/Tect/R251.lean"
LEAN_ROOT = REPO / "verification/lean"
BRIDGE = REPO / "strategy/pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge-manifest.json"
FORCE = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
KINETIC = REPO / "strategy/pre-a-cp1-st8-q3lock-uniform-kinetic-character-moment-corollary-manifest.json"
SPLIT = REPO / "strategy/pre-a-cp1-st8-q3lock-kinetic-force-double-commutator-split-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-doublet-route-split-manifest.json"
COMMON = REPO / "strategy/pre-a-cp1-st8-q3lock-common-alpha-topology-critical-graph-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "integrated.json"
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
    command = "lake env lean Tect/R251.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R251.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    bridge = json.loads(BRIDGE.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    kinetic = json.loads(KINETIC.read_text(encoding="utf-8"))
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    common = json.loads(COMMON.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001069" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001069/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("prior kinetic", kinetic["exploration_id"] == "EXP-001068", kinetic["exploration_id"], "EXP-001068")
    check("prior split", split["exploration_id"] == "EXP-001067", split["exploration_id"], "EXP-001067")
    check("bridge authority", bridge["exploration_id"] == "EXP-001061" and bridge["scope"]["compact_source_endpoint_third_moment_bridge_closed"] is True, bridge["exploration_id"], "EXP-001061 and closed")
    check("force authority", force["exploration_id"] == "EXP-001059" and "C=122099/35840" in force["model"]["force_input"], force["exploration_id"], "EXP-001059 and registered force")
    check("m5 authority", upstream["exploration_id"] == "EXP-000826" and "m5=sup" in upstream["conditional_fifth_graph_transport"]["definitions"], upstream["exploration_id"], "EXP-000826")
    check("coercivity authority", "p_z^2/(2chi)" in common["model"]["onsite_split"], common["model"]["onsite_split"], "onsite coercivity")
    check("exact split", split["model"]["exact_split"].startswith(manifest["model"]["split"]), manifest["model"]["split"], "registered split")

    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["bridge_fixture", "force_fourth_fixture", "force_ceiling_fixture", "force_norm_upper_fixture", "kinetic_upper_fixture", "full_triangle_upper_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="static-full-double-commutator-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("passed", 0) > 0 and independent.get("passed", 0) > 0, [primary.get("passed"), independent.get("passed")], ">0")
        pderived = primary.get("derived", {})
        iderived = independent.get("derived", {})
        keys = ("g", "r", "gamma", "m5", "chi", "hbar", "character_amplitude", "force_constant", "force_weight_ratio", "a_gamma", "A_r", "C0", "M_bridge_compact", "force_fourth_moment", "force_fourth_ceiling_square", "force_norm_squared_upper", "kinetic_squared_norm_bound", "full_squared_norm_upper", "static_force_summand_two_sided_bound_closed", "static_full_character_double_commutator_bound_closed", "force_history_uniform_closed", "full_actual_q3_double_commutator_uniform_closed")
        for key in keys:
            check(f"lane agreement {key}", str(pderived.get(key)) == str(iderived.get(key)), [pderived.get(key), iderived.get(key)], "equal")
        expected = manifest["finite_fixture"]
        for key in ("derived_M_bridge_compact", "derived_force_fourth_moment", "derived_force_norm_squared_upper", "derived_kinetic_squared_norm", "derived_full_squared_norm_upper"):
            derived_key = {"derived_M_bridge_compact": "M_bridge_compact", "derived_force_fourth_moment": "force_fourth_moment", "derived_force_norm_squared_upper": "force_norm_squared_upper", "derived_kinetic_squared_norm": "kinetic_squared_norm_bound", "derived_full_squared_norm_upper": "full_squared_norm_upper"}[key]
            check(f"fixture {key}", str(pderived.get(derived_key)) == expected[key], pderived.get(derived_key), expected[key])

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R251.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-STATIC-CHARACTER-FULL-DOUBLE-COMMUTATOR-BOUND",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "bridge_manifest_sha256": sha256(BRIDGE), "force_manifest_sha256": sha256(FORCE), "kinetic_manifest_sha256": sha256(KINETIC), "split_manifest_sha256": sha256(SPLIT), "upstream_manifest_sha256": sha256(UPSTREAM), "common_manifest_sha256": sha256(COMMON)},
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED STATIC-FULL-DOUBLE-COMMUTATOR PASS {len(rows)}/{len(rows)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
