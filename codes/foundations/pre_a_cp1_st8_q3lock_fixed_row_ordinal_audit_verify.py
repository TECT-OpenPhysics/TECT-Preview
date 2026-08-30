#!/usr/bin/env python3
"""Integrated verifier for the R-432 finite row-ordinal correction."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-fixed-row-ordinal-audit-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_fixed_row_ordinal_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_fixed_row_ordinal_audit_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_fixed_row_ordinal_audit_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R432.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-fixed_row_ordinal_audit/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-fixed_row_ordinal_audit/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-fixed_row_ordinal_audit/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-fixed_row_ordinal_audit/integrated.json"
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
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["row_contract"]
    failure = json.loads((ROOT / manifest["upstream_authority"]["r426_manifest"]).read_text(encoding="utf-8"))["failure_contract"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-432" and manifest["exploration_id"] == "EXP-001277" and manifest["claim_bearing"] is False and manifest["status"] == "ROW_INDEX_CONTRACT_CORRECTED", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-432/EXP-001277/false/ROW_INDEX_CONTRACT_CORRECTED", "provenance")
    check("fixed emission contract", contract["target_emission_ordinal"] == 7 and contract["target_parent_coordinate"] == 6 and contract["historical_subtract_one_ordinal"] == 6 and contract["comparison_tolerance"] == "5e-7", contract, "ordinal 7 -> parent 6; tolerance 5e-7", "row contract")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-432 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct R-432 source hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared theorem markers", "Lean")
    check("Lean policy", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean finite scalar file", "Lean")

    outputs: dict[str, str] = {}
    for script, expected, extra in ((PRIMARY, PRIMARY_OUTPUT, ["--self-test"]), (INDEPENDENT, INDEPENDENT_OUTPUT, []), (HOSTILE, HOSTILE_OUTPUT, [])):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = command([sys.executable, "-X", "utf8", str(script), *extra], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R432.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1800:], "exit 0 without errors", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    p = primary["derived"]
    i = independent["derived"]
    tol = Decimal(str(contract["comparison_tolerance"]))
    check("primary corrected row", primary["verdict"] == manifest["status"] and p["target_emission_ordinal"] == 7 and p["target_parent_coordinate"] == 6 and abs(Decimal(str(p["corrected_direct_residual_gap"])) - Decimal(str(failure["direct_residual_gap"]))) <= Decimal("1e-12") and Decimal(str(p["r422_mismatch"])) > tol and p["original_source_interval_certified"] is False, {key: p[key] for key in ("target_emission_ordinal", "target_parent_coordinate", "corrected_direct_residual_gap", "r422_mismatch", "original_source_interval_certified")}, "correct target and preserved finite mismatch", "primary")
    check("primary historical lane diagnosis", Decimal(str(p["historical_wrong_row_gap"])) != Decimal(str(p["corrected_direct_residual_gap"])) and abs(Decimal(str(p["r430_independent_gap"])) - Decimal(str(p["historical_wrong_row_gap"]))) <= tol, {key: p[key] for key in ("historical_wrong_row_gap", "r430_independent_gap")}, "ordinal 6 is a different row", "row correction")
    check("independent corrected row", independent["verdict"] == "INDEPENDENT_ROW_INDEX_CORRECTION" and i["target_emission_ordinal"] == 7 and i["target_parent_coordinate"] == 6 and abs(Decimal(str(i["target_gap"])) - Decimal(str(failure["direct_residual_gap"]))) <= tol and Decimal(str(i["r422_mismatch"])) > tol and i["original_source_interval_certified"] is False, {key: i[key] for key in ("target_emission_ordinal", "target_parent_coordinate", "target_gap", "r422_mismatch", "original_source_interval_certified")}, "independent target reproduction", "independent")
    check("independent and primary agreement", abs(Decimal(str(p["corrected_direct_residual_gap"])) - Decimal(str(i["target_gap"]))) <= tol, [p["corrected_direct_residual_gap"], i["target_gap"]], f"within {tol}", "independence")
    check("hostile controls", hostile["verdict"] == "PASS" and hostile["controls"]["all_mutations_rejected"] is True and hostile["controls"]["original_source_interval_certified"] is False and hostile["controls"]["residual_reuse_closed"] is False, hostile["controls"], "all ordinal/status/promotion mutations rejected", "hostile")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r432-integrated/1.0",
        "result_id": "R-432",
        "exploration_id": "EXP-001277",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "integrated",
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "target_emission_ordinal": p["target_emission_ordinal"],
            "target_parent_coordinate": p["target_parent_coordinate"],
            "corrected_direct_residual_gap": p["corrected_direct_residual_gap"],
            "r422_mismatch": p["r422_mismatch"],
            "historical_wrong_row_gap": p["historical_wrong_row_gap"],
            "original_source_interval_certified": False,
            "residual_reuse_closed": False,
            "r426_route_failure_preserved": True,
            "lean": "PASS",
            "outputs": outputs,
        },
        "source_hashes": hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-432 INTEGRATED {len(checks)}/{len(checks)} row-contract PASS; target ordinal 7 reproduced; historical ordinal-6 sensitivity rejected; Lean PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
