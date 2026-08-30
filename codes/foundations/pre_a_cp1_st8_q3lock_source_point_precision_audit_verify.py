#!/usr/bin/env python3
"""Integrated verifier for the R-430 source-point precision audit."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-source-point-precision-audit-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_source_point_precision_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_source_point_precision_audit_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_source_point_precision_audit_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R430.lean"
SLUG = "source_point_precision_audit"
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


def command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-430" and manifest["exploration_id"] == "EXP-001275" and manifest["claim_bearing"] is False and manifest["status"] == "SOURCE_POINT_AUDIT_NO_INTERVAL", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-430/EXP-001275/false/SOURCE_POINT_AUDIT_NO_INTERVAL", "provenance")
    scope = manifest["scope"]
    check("scope firewall", scope["source_point_precision_executed"] is True and scope["source_point_residual_recomputed"] is True and scope["source_gap_separation_observed"] is True and scope["source_interval_certified"] is False and scope["exact_original_input_certified"] is False and scope["residual_reuse_closed"] is False and scope["r426_route_failure_preserved"] is True and scope["no_new_negative_result"] is True and scope["no_tier_change"] is True, {key: scope[key] for key in sorted(scope)}, "finite source point only", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-430 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared theorem markers", "Lean")
    check("Lean policy", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean finite scalar file", "Lean")
    outputs: dict[str, str] = {}
    for script, expected in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = command([sys.executable, "-X", "utf8", str(script), "--self-test"], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R430.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1800:], "exit 0 without errors", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    comparison = Decimal(str(thresholds["comparison_tolerance"]))
    p = primary["derived"]
    i = independent["derived"]
    check("primary source audit", primary["verdict"] == "SOURCE_POINT_AUDIT_NO_INTERVAL" and p["source_interval_certified"] is False and p["exact_original_input_certified"] is False and Decimal(str(p["mismatch_r422_decimal"])) > comparison and Decimal(str(p["mismatch_direct_decimal"])) > comparison, {key: p[key] for key in ("source_residual_gap_decimal", "mismatch_r422_decimal", "mismatch_direct_decimal", "source_interval_certified", "exact_original_input_certified")}, "positive point gap with both fixed-reference mismatches > tolerance and no interval", "primary")
    check("independent source sensitivity", independent["verdict"] == "INDEPENDENT_SOURCE_SENSITIVITY_CONTROL" and i["source_interval_certified"] is False and Decimal(str(i["mismatch_r422"])) > comparison and Decimal(str(i["source_point_gap_difference"])) > comparison, {key: i[key] for key in ("source_residual_gap_double", "primary_mpmath_gap", "source_point_gap_difference", "mismatch_r422")}, "independent mismatch and sensitivity recorded without promotion", "independent")
    check("hostile controls", hostile["verdict"] == "PASS" and hostile["controls"]["all_mutations_rejected"] is True and hostile["controls"]["source_interval_certified"] is False and hostile["controls"]["exact_original_input_certified"] is False and hostile["controls"]["residual_reuse_closed"] is False, hostile["controls"], "all mutations rejected and point boundary preserved", "hostile")
    payload: dict[str, Any] = {"schema": "tect/pre-a-r430-integrated/1.0", "result_id": "R-430", "exploration_id": "EXP-001275", "claim_id": manifest["claim_ids"][0], "manifest": MANIFEST.relative_to(ROOT).as_posix(), "run_kind": "integrated", "verdict": "SOURCE_POINT_AUDIT_NO_INTERVAL", "assertion_count": len(checks), "assertions": checks, "derived": {"fixed_row": p["fixed_row"], "mpmath_source_gap": p["source_residual_gap_decimal"], "independent_double_gap": i["source_residual_gap_double"], "r422_mismatch_mpmath": p["mismatch_r422_decimal"], "direct_mismatch_mpmath": p["mismatch_direct_decimal"], "independent_source_point_difference": i["source_point_gap_difference"], "hostile_mutation_count": hostile["controls"]["mutation_count"], "lean": "PASS", "outputs": outputs, "source_interval_certified": False, "exact_original_input_certified": False, "residual_reuse_closed": False, "r426_route_failure_preserved": True}, "source_hashes": hashes, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"]}
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-430 INTEGRATED SOURCE_POINT_AUDIT_NO_INTERVAL {len(checks)}/{len(checks)} mpmath_gap={p['source_residual_gap_decimal']} independent_double_gap={i['source_residual_gap_double']} Lean=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
