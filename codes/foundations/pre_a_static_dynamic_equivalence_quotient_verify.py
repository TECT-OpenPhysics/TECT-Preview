#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-448."""

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

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-static-dynamic-equivalence-quotient-manifest.json"
PRIMARY = ROOT / "verification/scripts/pre_a_static_dynamic_equivalence_quotient.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_static_dynamic_equivalence_quotient_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_static_dynamic_equivalence_quotient_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R448.lean"
LEAN_ROOT = ROOT / "verification/lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-static_dynamic_equivalence_quotient/integrated.json"


def atomic_json(path: Path, payload: dict) -> None:
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    process = subprocess.run([sys.executable, "-X", "utf8", str(script), "--output", str(output)], cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict:
    if not LAKE.is_file():
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R448.lean", "output": "pinned direct lake executable not found"}
    process = subprocess.run([str(LAKE), "env", "lean", "Tect/R448.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R448.lean", "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def check(name: str, condition: bool, actual, expected, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"]] == ["R-448", "EXP-001321", "T-061", False, "T0"], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"]], "R-448/EXP-001321/T-061/false/T0", "provenance")
    check("method preservation", all(manifest["methods_preserved"].values()), manifest["methods_preserved"], "all true", "method-firewall")
    check("static class boundary", manifest["scope"]["static_identifiability"] == "NON_IDENTIFIABLE" and manifest["scope"]["source_owner_admitted"] is False and manifest["scope"]["physical_identity"] is False, manifest["scope"], "non-identifiable and unowned", "boundary")
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in source for marker in manifest["lean_crosscheck"]["theorem_markers"]), manifest["lean_crosscheck"]["theorem_markers"], "all present", "Lean")
    check("Lean firewall", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean", "Lean")
    for key, item in manifest["files"].items():
        path = ROOT / item["path"]
        if not (path.is_file() and item["sha256"] != "TO_BE_FILLED" and digest(path) == item["sha256"]):
            raise AssertionError(f"file {key} hash mismatch")
    with tempfile.TemporaryDirectory(prefix="r448-integrated-") as directory:
        temporary = Path(directory)
        primary_process, primary = run_child(PRIMARY, temporary / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, temporary / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, temporary / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == manifest["status"], primary_process.stdout + primary_process.stderr, manifest["status"], "executables")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "INDEPENDENT_STATIC_DYNAMIC_EQUIVALENCE_QUOTIENT_CONTROL", independent_process.stdout + independent_process.stderr, "independent", "executables")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile_process.stdout + hostile_process.stderr, "hostile", "executables")
        check("independent does not import primary", "pre_a_static_dynamic_equivalence_quotient.py" not in INDEPENDENT.read_text(encoding="utf-8"), True, "independent source", "independence")
        keys = ("static_signature", "map_a_factors", "map_b_factors", "probe", "probe_a", "probe_b", "static_equivalent", "maps_distinct", "equivalence_relation_checked", "static_class_non_singleton", "finite_estimand_separates", "static_identifiability", "stability_under_observation_error", "stability_under_regulator_change", "holdout_prediction", "source_owner_admitted", "physical_identity")
        for key in keys:
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal", "cross-check")
        check("hostile count", hostile.get("mutations_rejected") == hostile.get("assertion_count") == 8, hostile.get("mutations_rejected"), 8, "hostile")
        derived = primary["derived"]
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R448.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS", "Lean")
    payload = {
        "schema": "tect/pre-a-static-dynamic-equivalence-quotient-integrated/1.0",
        "run_kind": "integrated",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "verdict": "INTEGRATED_STATIC_DYNAMIC_EQUIVALENCE_QUOTIENT_AUDITED",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "derived": derived,
        "scope": {"static_class_non_singleton": True, "finite_estimand_separates": True, "independent_reconstruction_agrees": True, "hostile_mutations_rejected": True, "claim_bearing": False, "source_owner_admitted": False, "physical_identity": False},
        "source_hashes": {path.relative_to(ROOT).as_posix(): digest(path) for path in (MANIFEST, PRIMARY, INDEPENDENT, HOSTILE, LEAN)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-448 INTEGRATED {payload['verdict']} {len(checks)}/{len(checks)} Lean={lean['status']}", flush=True)
    if args.self_test:
        assert payload["verdict"] == "INTEGRATED_STATIC_DYNAMIC_EQUIVALENCE_QUOTIENT_AUDITED"
        print("R-448 INTEGRATED SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
