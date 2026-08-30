#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-440."""

from __future__ import annotations

import argparse
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-layer-family-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_layer_family.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_layer_family_independent.py"
HOSTILE = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_layer_family_hostile.py"
LEAN = REPO / "verification/lean/Tect/R440.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-rectangular_matching_layer_family/integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    return process, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def pinned_lake() -> Path | None:
    try:
        registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
        toolchain = registry["toolchain"]["toolchain"]
        encoded = toolchain.replace("/", "--").replace(":", "---")
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
        for name in ("lake.exe", "lake"):
            if (candidate / name).is_file():
                return candidate / name
    except (KeyError, OSError, json.JSONDecodeError):
        pass
    located = shutil.which("lake")
    return Path(located) if located else None


def lean_run() -> dict[str, Any]:
    lake = pinned_lake()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R440.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R440.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R440.lean", "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", [manifest["exploration_id"], manifest["result_id"], manifest["task_id"]] == ["EXP-001285", "R-440", "T-054"], [manifest["exploration_id"], manifest["result_id"], manifest["task_id"]], "EXP-001285/R-440/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("formal event reserved", manifest["formal_integration"]["event_ordinal"] == 782 and manifest["formal_integration"]["tier_change"] is False, manifest["formal_integration"], "event 782 without tier change")
    check("Lean source exists", LEAN.is_file(), str(LEAN), True)
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in lean_source for marker in manifest["lean_crosscheck"]["theorem_markers"]), manifest["lean_crosscheck"]["theorem_markers"], "present")
    check("Lean forbidden tokens absent", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    boundary = manifest["boundary"].lower()
    check("finite boundary", "finite" in boundary and "conditional" in boundary, boundary, "finite conditional boundary")
    check("common-alpha boundary", "common alpha" in boundary and "not" in boundary, boundary, "open common alpha")
    check("QFT firewall", "yang-mills" in boundary and "mass-gap" in boundary, boundary, "open Yang-Mills/mass-gap")

    with tempfile.TemporaryDirectory(prefix="r440-integrated-") as temporary:
        root = Path(temporary)
        primary_process, primary = child(PRIMARY, root / "primary.json")
        independent_process, independent = child(INDEPENDENT, root / "independent.json")
        hostile_process, hostile = child(HOSTILE, root / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "PASS", hostile_process.stdout + hostile_process.stderr, "PASS")
        check("positive assertion totals", all(payload.get("assertion_count", 0) > 0 for payload in (primary, independent, hostile)), [primary.get("assertion_count"), independent.get("assertion_count"), hostile.get("assertion_count")], ">0")
        keys = ("dimension", "box_count", "layer_count", "matching_coefficient", "one_layer_form_factor", "endpoint_exponent", "global_max_layer_energy_ratio", "total_layer_rows", "total_product_rows", "rectangular_box_family_checked", "edge_colour_partition_checked", "six_matching_layers_checked", "per_layer_weighted_finite_form_checked", "volume_independent_coefficient_observed", "arbitrary_box_theorem_closed", "operator_common_core_closed", "boundary_commutator_decay_closed", "exhaustion_cauchy_closed", "common_alpha_closed", "kms_gns_gap_closed", "pre_a_closed")
        for key in keys:
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal")
        check("box summaries agree", primary.get("derived", {}).get("boxes") == independent.get("derived", {}).get("boxes"), [primary.get("derived", {}).get("boxes"), independent.get("derived", {}).get("boxes")], "equal")
        check("hostile mutation count", hostile.get("mutations_rejected") == hostile.get("assertion_count") == 10, hostile.get("mutations_rejected"), 10)

    lean_result = {"status": "SKIPPED", "command": "lake env lean Tect/R440.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean_result["status"] == "PASS", lean_result, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RECTANGULAR-MATCHING-LAYER-FAMILY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean_result,
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store and not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"R-440 INTEGRATED RECTANGULAR_MATCHING_LAYER_AUDITED {len(rows)}/{len(rows)} Lean={lean_result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
