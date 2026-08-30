#!/usr/bin/env python3
"""Integrated verifier for the additive R-456 weighted transfer interface."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-weighted-transfer-operator-defect-resolvent-manifest.json"
PRIMARY = ROOT / "verification/scripts/pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R456.lean"
LEAN_ROOT = ROOT / "verification/lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))
DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent/integrated.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict[str, Any]:
    if not LAKE.is_file():
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R456.lean", "output": "pinned direct lake executable not found"}
    process = subprocess.run(
        [str(LAKE), "env", "lean", "Tect/R456.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R456.lean", "returncode": process.returncode, "output": output[-3000:]}


def run(output: Path = DEFAULT, skip_lean: bool = False) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"], manifest["status"]] == ["R-456", "EXP-001329", "T-054", False, "T0", "CONDITIONAL_WEIGHTED_TRANSFER_OPERATOR_RESOLVENT_AUDITED"], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"], manifest["status"]], "R-456/EXP-001329/T-054/false/T0/status", "provenance")
    check("method firewall", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true", "method")
    contract = manifest["weighted_contract"]
    check("weighted contract", all(value is True for key, value in contract.items() if key != "path_order") and contract["path_order"] == "K_R through K_(j+1) acts on a term born at j", contract, "all declared weighted conditions", "contract")
    scope = manifest["scope"]
    closed = ("positive_weight_contract_closed", "weighted_row_sum_step_closed", "diagonal_conjugation_closed", "weighted_path_product_bound_closed", "weighted_vector_defect_convolution_closed", "weighted_geometric_defect_envelope_closed", "nonresonant_closed_form_closed", "resonant_closed_form_closed", "two_base_less_than_one_threshold_closed")
    open_keys = [key for key, value in scope.items() if key.endswith("_closed") and key not in closed and value is False]
    check("closed abstract scope", all(scope[key] is True for key in closed), {key: scope[key] for key in closed}, "all true", "scope")
    check("downstream scope firewall", len(open_keys) >= 15 and scope["actual_q3_history_closed"] is False and scope["source_owned_transfer_closed"] is False and scope["pre_a_closed"] is False and scope["sector_a_closed"] is False, open_keys, "owner and downstream scopes remain open", "scope")
    check("no tier/negative/pdf mutation", scope["no_new_negative_result"] and scope["no_tier_change"] and scope["no_pdf"], [scope["no_new_negative_result"], scope["no_tier_change"], scope["no_pdf"]], [True, True, True], "scope")
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    declarations = manifest["lean_crosscheck"]["declarations"]
    check("Lean markers", all(re.search(rf"(?m)^\s*theorem\s+{re.escape(marker)}\b", lean_source) for marker in declarations), declarations, "all theorem declarations present", "Lean")
    check("Lean forbidden tokens", not any(re.search(rf"\b{re.escape(token)}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "clean", "forbidden absent", "Lean")
    for name, path in {"manifest": MANIFEST, "primary": PRIMARY, "independent": INDEPENDENT, "hostile": HOSTILE, "integrated": Path(__file__)}.items():
        check(f"artifact {name}", path.is_file(), str(path), True, "artifacts")

    with tempfile.TemporaryDirectory(prefix="r456-integrated-") as directory:
        temp = Path(directory)
        primary_process, primary = child(PRIMARY, temp / "primary.json")
        independent_process, independent = child(INDEPENDENT, temp / "independent.json")
        hostile_process, hostile = child(HOSTILE, temp / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == manifest["status"], primary_process.stdout + primary_process.stderr, manifest["status"], "children")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == manifest["status"], independent_process.stdout + independent_process.stderr, manifest["status"], "children")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile_process.stdout + hostile_process.stderr, "HOSTILE_MUTATIONS_REJECTED", "children")
        expected_patterns = ["zero", "diagonal", "permutation", "averaging", "triangular", "alternating", "ramp-four"]
        expected_weights = ["unit", "dyadic", "affine", "geometric", "alternating"]
        check("primary coverage", primary.get("derived", {}).get("radius_rows_per_pair") == 17 and primary.get("derived", {}).get("pair_count") == 46 and primary.get("derived", {}).get("dimensions") == [1, 2, 3] and primary.get("derived", {}).get("weight_patterns") == expected_weights and primary.get("derived", {}).get("matrix_patterns") == expected_patterns and primary.get("derived", {}).get("path_checks") == 77280, primary.get("derived", {}), "17 rows, 46 pairs, dimensions 1/2/3, 5 weights, 7 patterns, 77280 paths", "children")
        check("independent coverage", independent.get("derived", {}).get("radius_rows_per_pair") == 17 and independent.get("derived", {}).get("pair_count") == 46 and independent.get("derived", {}).get("dimensions") == [1, 2, 3] and independent.get("derived", {}).get("weight_patterns") == expected_weights and independent.get("derived", {}).get("matrix_patterns") == expected_patterns and independent.get("derived", {}).get("path_checks") == 77280, independent.get("derived", {}), "17 rows, 46 pairs, dimensions 1/2/3, 5 weights, 7 patterns, 77280 paths", "children")
        check("hostile count", hostile.get("mutation_count") == 22 and len(hostile.get("mutations_rejected", [])) == 22, hostile.get("mutation_count"), 22, "hostile")
        check("independence", "pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent.py" not in INDEPENDENT.read_text(encoding="utf-8"), True, "no primary import", "independence")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R456.lean"} if skip_lean else lean_run()
    check("Lean source-only mode", True, lean["status"], "SKIPPED", "Lean") if skip_lean else check("Lean run", lean["status"] == "PASS", lean, "PASS", "Lean")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "source_hashes": {"manifest": sha(MANIFEST), "primary": sha(PRIMARY), "independent": sha(INDEPENDENT), "hostile": sha(HOSTILE), "integrated": sha(Path(__file__)), "lean": sha(LEAN)},
        "derived": {
            "positive_weight_contract_closed": True,
            "weighted_row_sum_step_closed": True,
            "diagonal_conjugation_closed": True,
            "weighted_path_product_bound_closed": True,
            "weighted_vector_defect_convolution_closed": True,
            "weighted_geometric_defect_envelope_closed": True,
            "nonresonant_closed_form_closed": True,
            "resonant_closed_form_closed": True,
            "two_base_less_than_one_threshold_closed": True,
            "primary_assertions": primary.get("assertion_count"),
            "independent_assertions": independent.get("assertion_count"),
            "hostile_mutations_rejected": hostile.get("mutation_count"),
            "path_checks": primary.get("derived", {}).get("path_checks"),
            "diagonal_conjugation_checks": primary.get("derived", {}).get("diagonal_conjugation_checks"),
            "actual_q3_history_closed": False,
            "source_owned_transfer_closed": False,
            "source_owned_weight_packet_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    save(output, payload)
    print(f"R-456 INTEGRATED PASS {len(checks)}/{len(checks)} Lean={lean['status']}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    run(args.output, skip_lean=args.skip_lean)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
