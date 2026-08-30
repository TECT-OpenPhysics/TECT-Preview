#!/usr/bin/env python3
"""Integrated verifier for the R-428 residual-basis conditioning diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-residual-basis-conditioning-diagnostic-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_basis_conditioning_diagnostic.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_basis_conditioning_diagnostic_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_basis_conditioning_diagnostic_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R428.lean"
SLUG = "residual_basis_conditioning_diagnostic"
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
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


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

    check(
        "manifest identity",
        manifest["result_id"] == "R-428" and manifest["exploration_id"] == "EXP-001273" and manifest["claim_bearing"] is False and manifest["status"] == "INCONCLUSIVE_CONDITIONING",
        [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]],
        "R-428/EXP-001273/false/INCONCLUSIVE_CONDITIONING",
        "provenance",
    )
    scope = manifest["scope"]
    expected_true = {"finite_conditioning_diagnostic_closed", "fixed_row_reconstructed", "basis_projector_crosswalk_closed", "r426_route_failure_preserved", "no_new_negative_result", "no_tier_change", "no_pdf"}
    expected_false = {key for key, value in scope.items() if key.endswith("_closed") and key not in expected_true}
    check("scope firewall", all(scope.get(key) is True for key in expected_true) and all(scope.get(key) is False for key in expected_false), {key: scope[key] for key in sorted(scope)}, "finite diagnostic only; no proof promotion", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-428 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared theorem markers", "Lean")
    check("Lean source policy", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean finite scalar file", "Lean")

    outputs: dict[str, str] = {}
    for script, expected, extra in ((PRIMARY, PRIMARY_OUTPUT, ["--self-test"]), (INDEPENDENT, INDEPENDENT_OUTPUT, ["--self-test"]), (HOSTILE, HOSTILE_OUTPUT, ["--self-test"])):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = run_command([sys.executable, "-X", "utf8", str(script), *extra], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lake = LAKE if LAKE.is_file() else Path("C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe")
    lean = run_command([str(lake), "env", "lean", "Tect/R428.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1800:], "exit 0 without errors", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    derived = primary["derived"]
    row = derived["fixed_row"]
    check("primary inconclusive diagnostic", primary["result_id"] == "R-428" and primary["verdict"] == "INCONCLUSIVE_CONDITIONING" and row["volume"] == 2 and row["cutoff_dimension"] == 16 and row["beta"] == "8" and row["orientation"] == "right" and row["conditional_row_index"] == 7, [primary["result_id"], primary["verdict"], row], "fixed R-426 row with inconclusive conditioning verdict", "outputs")
    check("primary predicates", derived["pi_dynamic_range"] > float(thresholds["dynamic_range_floor"]) and derived["conditioning_amplification_budget"] > float(thresholds["comparison_tolerance"]) and derived["basis_gap_spread"] > float(thresholds["comparison_tolerance"]) and derived["recomputed_mismatch"] > float(thresholds["comparison_tolerance"]), derived, "all conditioning predicates exceed fixed comparison tolerance", "conditioning")
    check("crosswalk and failure boundary", derived["projector_distance_two"] <= float(thresholds["projector_tolerance"]) and derived["cross_gram_singular_min"] >= 1.0 - float(thresholds["cross_gram_tolerance"]) and derived["cross_gram_singular_max"] <= 1.0 + float(thresholds["cross_gram_tolerance"]) and derived["r426_route_failure_preserved"] is True and derived["residual_reuse_closed"] is False and derived["precision_certified"] is False, derived, "finite crosswalk passes; no precision-certified repair", "scope")
    check("independent control", independent["result_id"] == "R-428" and independent["verdict"] == "PASS" and independent["derived"]["classification"] == "INCONCLUSIVE_CONDITIONING" and independent["derived"]["r426_route_failure_preserved"] is True, independent["derived"], "independent classification and preserved boundary", "independent")
    check("hostile control", hostile["result_id"] == "R-428" and hostile["verdict"] == "PASS" and hostile["controls"]["all_mutations_rejected"] is True and hostile["controls"]["r426_route_failure_preserved"] is True and hostile["controls"]["physical_promotion"] is False, hostile["controls"], "all hostile mutations rejected", "hostile")
    check("fixed parent contract", abs(float(derived["r422_residual_gap"]) - float(target["r422_residual_gap"])) <= float(thresholds["reconstruction_tolerance"]) and abs(float(derived["r426_direct_residual_gap"]) - float(target["r426_direct_residual_gap"])) <= float(thresholds["reconstruction_tolerance"]), [derived["r422_residual_gap"], derived["r426_direct_residual_gap"]], "within declared reconstruction tolerance", "reconstruction")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r428-integrated/1.0",
        "result_id": "R-428",
        "exploration_id": "EXP-001273",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "integrated",
        "verdict": "INCONCLUSIVE_CONDITIONING",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "fixed_row": row,
            "primary_classification": derived["classification"],
            "independent_classification": independent["derived"]["classification"],
            "hostile_mutation_count": hostile["controls"]["mutation_count"],
            "lean": "PASS",
            "outputs": outputs,
            "r426_route_failure_preserved": True,
            "residual_reuse_closed": False,
            "precision_certified": False,
        },
        "source_hashes": hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-428 INTEGRATED INCONCLUSIVE_CONDITIONING {len(checks)}/{len(checks)} row=V2/d16/beta8/right/7 Lean=PASS residual_reuse_closed=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
