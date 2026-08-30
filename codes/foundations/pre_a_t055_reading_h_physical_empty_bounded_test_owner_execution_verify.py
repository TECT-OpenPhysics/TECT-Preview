#!/usr/bin/env python3
"""Integrated verifier for the R-441 physical-empty owner refresh."""

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
SLUG = "pre-a-t055-reading-h-physical-empty-bounded-test-owner-execution"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_t055_reading_h_physical_empty_bounded_test_owner_execution.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_t055_reading_h_physical_empty_bounded_test_owner_execution_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_t055_reading_h_physical_empty_bounded_test_owner_execution_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R441.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-hostile-{SLUG}" / "hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-integrated-{SLUG}" / "integrated.json"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    owner = manifest["owner_contract"]
    branch = manifest["physical_empty_branch_E"]
    verdicts = manifest["verdicts"]
    check("manifest identity", [manifest["result_id"], manifest["exploration_id"], manifest["status"], manifest["claim_bearing"]] == ["R-441", "EXP-001286", "BLOCKED", False], [manifest["result_id"], manifest["exploration_id"], manifest["status"], manifest["claim_bearing"]], ["R-441", "EXP-001286", "BLOCKED", False], "provenance")
    check("owner orientation", owner["comparison_orientation"] == "F_total[G_*] - F_total[E]", owner["comparison_orientation"], "F_total[G_*] - F_total[E]", "contract")
    check("fifteen-field lock", len(owner["required_fixed_fields"]) == 15 and set(owner["required_fixed_fields"]) == set(owner["field_matrix"]), len(owner["required_fixed_fields"]), 15, "contract")
    check("common owner absent", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and owner["finite_evaluation_allowed"] is False, [owner["field_status"], owner["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", False], "contract")
    check("E preregistered but not admitted", branch["preregistered_slot"] is True and branch["admitted"] is False and branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED", [branch["preregistered_slot"], branch["admitted"], branch["admission_status"]], [True, False, "BLOCKED_NOT_INSTANTIATED"], "E")
    check("zero alias forbidden", branch["zero_reference_identification"] == "FORBIDDEN" and branch["p1_zero_reference_alias"] == "NOT_ACCEPTED", [branch["zero_reference_identification"], branch["p1_zero_reference_alias"]], ["FORBIDDEN", "NOT_ACCEPTED"], "E")
    check("all requested verdicts blocked", all(item["status"] == "BLOCKED_NOT_EVALUATED" for item in verdicts.values()), {key: item["status"] for key, item in verdicts.items()}, "three BLOCKED_NOT_EVALUATED statuses", "verdict")
    check("no finite evaluation", owner["finite_evaluation_allowed"] is False and branch["supplied_fields"] == [], [owner["finite_evaluation_allowed"], branch["supplied_fields"]], [False, []], "stop")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-441 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = ["fixed_field_count", "empty_branch_slot", "blocked_status_scope", "finite_owner_scope"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared theorem markers", "Lean")
    check("Lean policy", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean finite scope file", "Lean")
    outputs: dict[str, str] = {}
    for script, expected in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = command([sys.executable, "-X", "utf8", str(script), "--self-test"], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R441.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1800:], "exit 0 without errors", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    p = primary["derived"]
    i = independent["derived"]
    check("primary blocked verdict", primary["verdict"] == "BLOCKED_NOT_EVALUATED" and p["sign"] == "BLOCKED_NOT_EVALUATED" and p["reading_h_stationarity"] == "BLOCKED_NOT_EVALUATED" and p["symmetry_projected_transverse_stability"] == "BLOCKED_NOT_EVALUATED" and p["E_preregistered"] is True and p["E_admitted"] is False, {key: p[key] for key in ("comparison", "sign", "reading_h_stationarity", "symmetry_projected_transverse_stability", "E_preregistered", "E_admitted")}, "three blocked verdicts and E not admitted", "primary")
    check("independent blocked control", independent["verdict"] == "INDEPENDENT_BLOCKED_INPUT_CONTROL" and i["E_preregistered"] is True and i["E_admitted"] is False and independent["scope"]["numeric_evaluation"] is False, i, "reversed-field independent blocker", "independent")
    check("hostile controls", hostile["verdict"] == "HOSTILE_MUTATIONS_REJECTED" and hostile["assertion_count"] == 7 and hostile["scope"]["physical_promotion_rejected"] is True, hostile["scope"], "seven mutations rejected", "hostile")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r434-integrated/1.0",
        "result_id": "R-441",
        "exploration_id": "EXP-001286",
        "claim_id": manifest["card_id"],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "integrated",
        "verdict": "BLOCKED_NOT_EVALUATED",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"comparison": "F_total[G_*] - F_total[E]", "sign": "BLOCKED_NOT_EVALUATED", "reading_h_stationarity": "BLOCKED_NOT_EVALUATED", "symmetry_projected_transverse_stability": "BLOCKED_NOT_EVALUATED", "E_preregistered": True, "E_admitted": False, "primary_assertions": primary["assertion_count"], "independent_assertions": independent["assertion_count"], "hostile_assertions": hostile["assertion_count"], "lean": "PASS", "outputs": outputs},
        "scope": {"owner_input_audit_executed": True, "physical_empty_branch_preregistered": True, "physical_empty_branch_admitted": False, "all_three_quantities_evaluated": False, "claim_bearing": False, "yang_mills_promoted": False, "mass_gap_promoted": False},
        "source_hashes": hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-441 INTEGRATED BLOCKED_NOT_EVALUATED {len(checks)}/{len(checks)}; E preregistered, not admitted; Lean=PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
