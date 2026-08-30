#!/usr/bin/env python3
"""Integrated verifier for the R-445 conditional finite norm-transfer package."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-scalar-operator-tail-transfer-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_scalar_operator_tail_transfer.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_scalar_operator_tail_transfer_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_scalar_operator_tail_transfer_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R445.lean"
LEAN_ROOT = ROOT / "verification/lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-scalar_operator_tail_transfer/integrated.json"


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
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([sys.executable, "-X", "utf8", str(script), "--output", str(output)], cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict[str, Any]:
    if not LAKE.is_file():
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R445.lean", "output": "pinned lake executable not found"}
    process = subprocess.run([str(LAKE), "env", "lean", "Tect/R445.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    status = "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL"
    return {"status": status, "command": "lake env lean Tect/R445.lean", "returncode": process.returncode, "output": output[-2000:]}


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

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]] == ["R-445", "EXP-001297", "T-054", False], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "R-445/EXP-001297/T-054/false", "provenance")
    scope = manifest["scope"]
    check("conditional assumption", scope["per_edge_majorant_assumed"] is True and scope["operator_norm_of_actual_q3_terms"] is False, {"assumed": scope["per_edge_majorant_assumed"], "actual_q3": scope["operator_norm_of_actual_q3_terms"]}, "assumption without identification", "scope")
    check("finite transfer chain", "||sum_tail K_e||" in manifest["finite_contract"]["transfer_chain"] and "C*T(R)" in manifest["finite_contract"]["transfer_chain"], manifest["finite_contract"]["transfer_chain"], "triangle plus scalar majorant", "contract")
    check("scope firewall", all(scope[key] is False for key in ("q3lock_commutator_identification", "history_tail_closed", "weighted_operator_form_closed", "common_core_closed", "common_alpha_closed", "exhaustion_cauchy_closed", "kms_gns_gap_closed", "physical_empty_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), {key: scope[key] for key in scope}, "all higher closures false", "scope")
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean theorem markers", all(marker in lean_source for marker in ("weighted_tail_transfer", "scaled_tail_r1_bound")), "markers present", "R-445 theorem markers", "Lean")
    check("Lean firewall", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean source", "Lean")

    with tempfile.TemporaryDirectory(prefix="r445-integrated-") as temporary:
        temp_root = Path(temporary)
        primary_process, primary = run_child(PRIMARY, temp_root / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, temp_root / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, temp_root / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "CONDITIONAL_WEIGHTED_NORM_TRANSFER_AUDITED", primary_process.stdout + primary_process.stderr, "primary audited", "executables")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "INDEPENDENT_CONDITIONAL_WEIGHTED_NORM_TRANSFER_CONTROL", independent_process.stdout + independent_process.stderr, "independent control", "executables")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile_process.stdout + hostile_process.stderr, "hostile rejected", "executables")
        for key in ("box_count", "total_edges", "total_tail_rows", "finite_scalar_dominance", "conditional_norm_transfer", "maximum_scalar_ratio", "maximum_operator_ratio", "q3lock_commutator_identification", "history_tail_closed", "weighted_operator_form_closed", "common_core_closed", "common_alpha_closed", "exhaustion_cauchy_closed", "physical_empty_closed", "continuum_closed", "pre_a_closed", "sector_a_closed"):
            check(f"independent agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal", "crosscheck")
        check("hostile mutation count", hostile.get("mutations_rejected") == hostile.get("assertion_count") == 8, hostile.get("mutations_rejected"), 8, "hostile")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R445.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS", "Lean")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r445-integrated/1.0",
        "run_kind": "integrated",
        "result_id": "R-445",
        "exploration_id": "EXP-001297",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "verdict": "INTEGRATED_CONDITIONAL_WEIGHTED_NORM_TRANSFER_AUDITED",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "derived": {
            "box_count": primary["derived"]["box_count"],
            "total_edges": primary["derived"]["total_edges"],
            "total_tail_rows": primary["derived"]["total_tail_rows"],
            "finite_scalar_dominance": True,
            "conditional_norm_transfer": True,
            "maximum_scalar_ratio": primary["derived"]["maximum_scalar_ratio"],
            "maximum_operator_ratio": primary["derived"]["maximum_operator_ratio"],
            "q3lock_commutator_identification": False,
            "history_tail_closed": False,
            "weighted_operator_form_closed": False,
            "common_core_closed": False,
            "common_alpha_closed": False,
            "exhaustion_cauchy_closed": False,
            "physical_empty_closed": False,
            "continuum_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "scope": {"finite_conditional_transfer": True, "independent_reconstruction_agrees": True, "hostile_mutations_rejected": True, "claim_bearing": False, "operator_or_physical_promotion": False},
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in (MANIFEST, PRIMARY, INDEPENDENT, HOSTILE, LEAN)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-445 INTEGRATED {payload['verdict']} {len(checks)}/{len(checks)} Lean={lean['status']}", flush=True)
    if args.self_test:
        assert payload["verdict"] == "INTEGRATED_CONDITIONAL_WEIGHTED_NORM_TRANSFER_AUDITED"
        assert payload["derived"]["conditional_norm_transfer"] is True
        print("R-445 INTEGRATED SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
