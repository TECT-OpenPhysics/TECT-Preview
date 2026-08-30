#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-442."""

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
SLUG = "pre-a-cp1-st8-q3lock-rectangular-matching-general-lemma"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_general_lemma.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_general_lemma_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_general_lemma_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R442.lean"
LEAN_ROOT = ROOT / "verification/lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-rectangular_matching_general_lemma/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-rectangular_matching_general_lemma/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-rectangular_matching_general_lemma/hostile.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-rectangular_matching_general_lemma/integrated.json"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([sys.executable, "-X", "utf8", str(script), "--output", str(output)], cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    return process, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def lean_run() -> dict[str, Any]:
    if not LAKE.is_file():
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R442.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(LAKE), "env", "lean", "Tect/R442.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R442.lean", "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("manifest identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]] == ["R-442", "EXP-001287", "T-054", False], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], ["R-442", "EXP-001287", "T-054", False], "provenance")
    check("finite contract", manifest["finite_contract"]["dimension"] == 3 and manifest["finite_contract"]["parity_modulus"] == 2 and manifest["finite_contract"]["side_min"] == 2 and manifest["finite_contract"]["side_max"] == 6, manifest["finite_contract"], "3D parity-2 sides 2..6", "contract")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("formal event reserved", manifest["formal_integration"]["event_ordinal"] == 784 and manifest["formal_integration"]["tier_change"] is False, manifest["formal_integration"], "event 784 without tier change", "provenance")
    boundary = manifest["boundary"].lower()
    check("finite boundary", "finite" in boundary and "does not close" in boundary, boundary, "finite-only boundary", "scope")
    check("QFT firewall", "yang-mills" in boundary and "mass-gap" in boundary, boundary, "Yang-Mills/mass-gap explicitly open", "scope")
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in lean_source for marker in ("same_colour_incident_unique", "six_colour_layers")), lean_source, "markers present", "Lean")
    check("Lean firewall", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean source", "Lean")

    with tempfile.TemporaryDirectory(prefix="r442-integrated-") as temporary:
        root = Path(temporary)
        primary_process, primary = child(PRIMARY, root / "primary.json")
        independent_process, independent = child(INDEPENDENT, root / "independent.json")
        hostile_process, hostile = child(HOSTILE, root / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "GENERAL_RECTANGULAR_MATCHING_LEMMA_AUDITED", (primary_process.stdout + primary_process.stderr).strip(), "audited", "executables")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "INDEPENDENT_GENERAL_RECTANGULAR_MATCHING_CONTROL", (independent_process.stdout + independent_process.stderr).strip(), "independent control", "executables")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", (hostile_process.stdout + hostile_process.stderr).strip(), "8 rejected", "hostile")
        check("positive assertion totals", all(payload.get("assertion_count", 0) > 0 for payload in (primary, independent, hostile)), [payload.get("assertion_count") for payload in (primary, independent, hostile)], ">0", "executables")
        for key in ("dimension", "parity_modulus", "box_count", "total_vertices", "total_edges", "total_empty_layers", "maximum_degree", "edge_count_formula_checked", "matching_property_checked", "general_local_incidence_lemma_lean_checked"):
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal", "crosscheck")
        check("box summaries agree", primary.get("derived", {}).get("boxes") == independent.get("derived", {}).get("boxes"), "primary and independent box summaries", "equal", "crosscheck")
        check("hostile mutation count", hostile.get("mutations_rejected") == hostile.get("assertion_count") == 8, hostile.get("mutations_rejected"), 8, "hostile")
        primary_payload, independent_payload, hostile_payload = primary, independent, hostile

    lean_result = {"status": "SKIPPED", "command": "lake env lean Tect/R442.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean_result["status"] == "PASS", lean_result, "PASS", "Lean")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in (PRIMARY, INDEPENDENT, HOSTILE, LEAN, MANIFEST)}
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r442-integrated/1.0",
        "run_kind": "integrated",
        "result_id": "R-442",
        "exploration_id": "EXP-001287",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "verdict": "INTEGRATED_GENERAL_RECTANGULAR_MATCHING_AUDITED",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean_result,
        "derived": {"box_count": primary_payload["derived"]["box_count"], "total_vertices": primary_payload["derived"]["total_vertices"], "total_edges": primary_payload["derived"]["total_edges"], "matching_property_checked": True, "edge_count_formula_checked": True, "general_local_incidence_lemma_lean_checked": lean_result["status"] == "PASS", "operator_common_core_closed": False, "history_tail_closed": False, "exhaustion_cauchy_closed": False, "pre_a_closed": False, "sector_a_closed": False},
        "scope": {"finite_rectangular_family_audited": True, "independent_reconstruction_agrees": True, "hostile_mutations_rejected": True, "claim_bearing": False, "operator_or_physical_promotion": False},
        "source_hashes": hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-442 INTEGRATED {payload['verdict']} {len(checks)}/{len(checks)} Lean={lean_result['status']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
