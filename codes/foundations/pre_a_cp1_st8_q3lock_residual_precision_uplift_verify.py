#!/usr/bin/env python3
"""Integrated verifier for the R-429 Decimal precision uplift."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-residual-precision-uplift-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_precision_uplift.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_precision_uplift_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_precision_uplift_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R429.lean"
SLUG = "residual_precision_uplift"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-hostile-{SLUG}" / "hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-integrated-{SLUG}" / "integrated.json"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-429" and manifest["exploration_id"] == "EXP-001274" and manifest["claim_bearing"] is False and manifest["status"] == "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-429/EXP-001274/false/ROUNDED_INPUT_ALGEBRAIC_BOUNDARY", "provenance")
    scope = manifest["scope"]
    true_keys = {"rounded_input_precision_uplift_closed", "basis_invariant_rounded_input_closed", "rounded_input_mismatch_reproduced", "r426_route_failure_preserved", "no_new_negative_result", "no_tier_change", "no_pdf"}
    closed_false = {key for key, value in scope.items() if key.endswith("_closed") and key not in true_keys}
    check("scope firewall", all(scope.get(key) is True for key in true_keys) and all(scope.get(key) is False for key in closed_false) and scope["upstream_source_precision_certified"] is False and scope["exact_original_input_certified"] is False and scope["residual_reuse_closed"] is False, {key: scope[key] for key in sorted(scope)}, "rounded-input finite diagnostic only", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-429 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared theorem markers", "Lean")
    check("Lean source policy", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean finite scalar file", "Lean")
    outputs: dict[str, str] = {}
    for script, expected in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = run_command([sys.executable, "-X", "utf8", str(script), "--self-test"], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lake = LAKE if LAKE.is_file() else Path("C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe")
    lean = run_command([str(lake), "env", "lean", "Tect/R429.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1800:], "exit 0 without errors", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    p = primary["derived"]
    i = independent["derived"]
    tolerance = Decimal(str(manifest["diagnostic_contract"]["thresholds"]["comparison_tolerance"]))
    agreement = Decimal(str(p["basis_gap_agreement_decimal"]))
    check("primary rounded-input boundary", primary["result_id"] == "R-429" and primary["verdict"] == "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY" and p["fixed_row"] == {"volume": 2, "cutoff_dimension": 16, "beta": "8", "orientation": "right", "conditional_row_index": 7, "core_size": 7, "tail_size": 9}, [primary["result_id"], primary["verdict"], p["fixed_row"]], "fixed R-426 row with rounded-input boundary", "outputs")
    check("basis-invariant Decimal separation", agreement <= Decimal(str(manifest["diagnostic_contract"]["thresholds"]["basis_gap_agreement_tolerance"])) and Decimal(str(p["mismatch_r422_decimal"])) > tolerance and Decimal(str(p["mismatch_direct_decimal"])) > tolerance, {key: p[key] for key in ("invariant_gap_decimal", "basis_gap_agreement_decimal", "mismatch_r422_decimal", "mismatch_direct_decimal")}, "agreement <= 1e-50 and mismatches > 5e-7", "precision")
    check("independent Decimal control", independent["result_id"] == "R-429" and independent["verdict"] == "PASS" and Decimal(str(i["mismatch_r422_decimal"])) > tolerance and i["residual_reuse_closed"] is False and i["r426_route_failure_preserved"] is True, i, "independent rounded-input mismatch and preserved boundary", "independent")
    check("primary-independent gap agreement", abs(Decimal(str(p["invariant_gap_decimal"])) - Decimal(str(i["invariant_gap_decimal"]))) <= Decimal(str(manifest["diagnostic_contract"]["thresholds"]["basis_gap_agreement_tolerance"])), [p["invariant_gap_decimal"], i["invariant_gap_decimal"]], "<=1e-50", "precision")
    check("hostile control", hostile["result_id"] == "R-429" and hostile["verdict"] == "PASS" and hostile["controls"]["all_mutations_rejected"] is True and hostile["controls"]["rounded_input_boundary_preserved"] is True and hostile["controls"]["precision_promotion"] is False, hostile["controls"], "all mutations rejected and no promotion", "hostile")
    payload: dict[str, Any] = {"schema": "tect/pre-a-r429-integrated/1.0", "result_id": "R-429", "exploration_id": "EXP-001274", "claim_id": manifest["claim_ids"][0], "manifest": MANIFEST.relative_to(ROOT).as_posix(), "run_kind": "integrated", "verdict": "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY", "assertion_count": len(checks), "assertions": checks, "derived": {"fixed_row": p["fixed_row"], "invariant_gap_decimal": p["invariant_gap_decimal"], "basis_gap_agreement_decimal": p["basis_gap_agreement_decimal"], "mismatch_r422_decimal": p["mismatch_r422_decimal"], "mismatch_direct_decimal": p["mismatch_direct_decimal"], "independent_gap_decimal": i["invariant_gap_decimal"], "hostile_mutation_count": hostile["controls"]["mutation_count"], "lean": "PASS", "outputs": outputs, "rounded_input_mismatch_reproduced": True, "residual_reuse_closed": False, "r426_route_failure_preserved": True, "upstream_source_precision_certified": False}, "source_hashes": hashes, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"]}
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-429 INTEGRATED ROUNDED_INPUT_ALGEBRAIC_BOUNDARY {len(checks)}/{len(checks)} gap={p['invariant_gap_decimal']} mismatch={p['mismatch_r422_decimal']} Lean=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
