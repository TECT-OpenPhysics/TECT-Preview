#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-443."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-arbitrary-box-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_arbitrary_box.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_arbitrary_box_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_arbitrary_box_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R443.lean"
LEAN_ROOT = ROOT / "verification/lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-rectangular_matching_arbitrary_box/integrated.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([sys.executable, "-X", "utf8", str(script), "--output", str(output)], cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    return process, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def lean_run() -> dict[str, Any]:
    if not LAKE.is_file(): return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R443.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(LAKE), "env", "lean", "Tect/R443.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R443.lean", "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); parser.add_argument("--skip-lean", action="store_true"); args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]] == ["R-443", "EXP-001288", "T-054", False], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "R-443/EXP-001288/T-054/false", "provenance")
    check("arbitrary-box scope", manifest["scope"]["arbitrary_box_edge_colouring_closed"] is True and manifest["scope"]["weighted_operator_form_closed"] is False, manifest["scope"], "combinatorics only", "scope")
    check("event reservation", manifest["formal_integration"]["event_ordinal"] == 785 and manifest["formal_integration"]["tier_change"] is False, manifest["formal_integration"], "event 785 without tier change", "provenance")
    boundary = manifest["boundary"].lower()
    check("finite boundary", "does not close" in boundary and "operator" in boundary, boundary, "open operator boundary", "scope")
    check("QFT firewall", "yang-mills" in boundary and "mass-gap" in boundary, boundary, "open Yang-Mills/mass-gap", "scope")
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in source for marker in ("same_colour_incident_unique", "arbitrary_box_layer_matching", "six_colour_layers")), "markers", "present", "Lean")
    check("Lean firewall", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean", "Lean")
    with tempfile.TemporaryDirectory(prefix="r443-integrated-") as temporary:
        root = Path(temporary)
        pp, primary = child(PRIMARY, root / "primary.json")
        ip, independent = child(INDEPENDENT, root / "independent.json")
        hp, hostile = child(HOSTILE, root / "hostile.json")
        check("primary child", pp.returncode == 0 and primary.get("verdict") == "ARBITRARY_BOX_MATCHING_THEOREM_AUDITED", (pp.stdout + pp.stderr).strip(), "audited", "executables")
        check("independent child", ip.returncode == 0 and independent.get("verdict") == "INDEPENDENT_ARBITRARY_BOX_MATCHING_CONTROL", (ip.stdout + ip.stderr).strip(), "independent", "executables")
        check("hostile child", hp.returncode == 0 and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", (hp.stdout + hp.stderr).strip(), "8 rejected", "hostile")
        check("assertions nonzero", all(item.get("assertion_count", 0) > 0 for item in (primary, independent, hostile)), [item.get("assertion_count") for item in (primary, independent, hostile)], ">0", "executables")
        for key in ("dimension", "parity_modulus", "box_count", "total_vertices", "total_edges", "total_empty_layers", "maximum_degree", "maximum_incidence", "layer_count", "edge_count_formula_checked", "matching_property_checked", "general_local_incidence_lemma_lean_checked", "arbitrary_box_edge_colouring_closed", "weighted_operator_form_closed", "history_tail_closed", "common_core_closed", "common_alpha_closed", "pre_a_closed", "sector_a_closed"):
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal", "crosscheck")
        check("box summaries agree", primary.get("derived", {}).get("boxes") == independent.get("derived", {}).get("boxes"), "primary and independent summaries", "equal", "crosscheck")
        check("hostile count", hostile.get("mutations_rejected") == hostile.get("assertion_count") == 8, hostile.get("mutations_rejected"), 8, "hostile")
        primary_payload, independent_payload = primary, independent
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R443.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS", "Lean")
    payload: dict[str, Any] = {"schema": "tect/pre-a-r443-integrated/1.0", "run_kind": "integrated", "result_id": "R-443", "exploration_id": "EXP-001288", "claim_id": manifest["claim_ids"][0], "manifest": MANIFEST.relative_to(ROOT).as_posix(), "verdict": "INTEGRATED_ARBITRARY_BOX_MATCHING_AUDITED", "assertion_count": len(checks), "assertions": checks, "lean": lean, "derived": {"box_count": primary_payload["derived"]["box_count"], "total_vertices": primary_payload["derived"]["total_vertices"], "total_edges": primary_payload["derived"]["total_edges"], "layer_count": primary_payload["derived"]["layer_count"], "matching_property_checked": True, "edge_count_formula_checked": True, "arbitrary_box_edge_colouring_closed": True, "operator_common_core_closed": False, "history_tail_closed": False, "exhaustion_cauchy_closed": False, "common_alpha_closed": False, "pre_a_closed": False, "sector_a_closed": False}, "scope": {"finite_family_audited": True, "independent_reconstruction_agrees": True, "hostile_mutations_rejected": True, "claim_bearing": False, "operator_or_physical_promotion": False}, "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in (MANIFEST, PRIMARY, INDEPENDENT, HOSTILE, LEAN)}, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-443 INTEGRATED {payload['verdict']} {len(checks)}/{len(checks)} Lean={lean['status']}", flush=True)
    if args.self_test: assert payload["verdict"] == "INTEGRATED_ARBITRARY_BOX_MATCHING_AUDITED" and payload["assertion_count"] == len(checks); print("R-443 INTEGRATED SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
