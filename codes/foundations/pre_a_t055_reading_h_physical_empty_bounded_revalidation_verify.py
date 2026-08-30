#!/usr/bin/env python3
"""Integrate the R-427 primary, independent, hostile and Lean lanes."""

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
SLUG = "pre-a-t055-reading-h-physical-empty-bounded-revalidation"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_t055_reading_h_physical_empty_bounded_revalidation.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_t055_reading_h_physical_empty_bounded_revalidation_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_t055_reading_h_physical_empty_bounded_revalidation_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R427.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-hostile-{SLUG}/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-integrated-{SLUG}/integrated.json"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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
    check("manifest identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]] == ["R-427", "EXP-001272", False], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], ["R-427", "EXP-001272", False], "provenance")
    check("test card identity", manifest["test_card_id"] == "PA-T055-READING-H-PHYSICAL-EMPTY-BOUNDED-TEST-REVALIDATION", manifest["test_card_id"], "PA-T055-READING-H-PHYSICAL-EMPTY-BOUNDED-TEST-REVALIDATION", "provenance")
    check("same R-420 contract is locked", manifest["revalidation"]["base_result_id"] == "R-420" and manifest["revalidation"]["same_contract_identity"] is True and manifest["revalidation"]["same_required_field_count"] == 15, manifest["revalidation"], "R-420/15/identity-locked", "contract")
    check("common owner remains blocked", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and owner["finite_evaluation_allowed"] is False, [owner["field_status"], owner["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", False], "contract")
    check("E slot remains blocked", branch["preregistered_slot"] is True and branch["admitted"] is False and branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED", [branch["preregistered_slot"], branch["admitted"], branch["admission_status"]], [True, False, "BLOCKED_NOT_INSTANTIATED"], "contract")
    check("fifteen-field matrix is complete", len(owner["required_fixed_fields"]) == 15 and set(owner["required_fixed_fields"]) == set(owner["field_matrix"]), len(owner["required_fixed_fields"]), 15, "contract")
    check("three verdicts are blocked", all(verdicts[name]["status"] == "BLOCKED_NOT_EVALUATED" for name in ("sign", "reading_h_stationarity", "symmetry_projected_transverse_stability")), {name: verdicts[name]["status"] for name in verdicts}, "three BLOCKED_NOT_EVALUATED statuses", "verdict")

    source_hashes: dict[str, str] = {}
    for authority in manifest["authority_inputs"]:
        path = ROOT / authority["path"]
        check(f"authority present {authority['id']}", path.is_file(), str(path), True, "authority")
        actual = sha256(path)
        source_hashes[authority["id"]] = actual
        check(f"authority hash {authority['id']}", actual == authority["sha256"], actual, authority["sha256"], "authority")

    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("R-427 artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-427 artifacts", "provenance")
    artifact_hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(artifact_hashes.values())) == len(artifact_hashes), artifact_hashes, "distinct hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    check("Lean theorem markers", all(marker in lean_text for marker in ("evaluation_requires_owner_and_empty", "three_blocked", "preregistered_slot_is_not_admission")), True, True, "Lean")
    check("Lean has no physical promotion", all(token not in lean_text for token in ("Yang-Mills", "mass gap", "Sector-A", "Pre-A")), True, True, "Lean")

    child_outputs: dict[str, str] = {}
    for script, output in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and output.is_file():
            child_outputs[script.name] = f"reused {output.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, child_outputs[script.name], "existing output", "executables")
        else:
            result = command([sys.executable, "-X", "utf8", str(script), "--output", str(output)], ROOT)
            child_outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and output.is_file(), child_outputs[script.name][-1200:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R427.lean"], ROOT / "verification/lean")
    child_outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, child_outputs["lean"][-1200:], "exit 0", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary BLOCKED", primary["verdict"] == "BLOCKED", primary["verdict"], "BLOCKED", "executables")
    check("independent BLOCKED", independent["verdict"] == "BLOCKED", independent["verdict"], "BLOCKED", "executables")
    check("hostile PASS", hostile["verdict"] == "PASS", hostile["verdict"], "PASS", "hostile")
    p, i = primary["derived"], independent["derived"]
    for field in ("contract_identity", "owner_contract_status", "physical_empty_slot", "required_field_count", "sign_status", "stationarity_status", "transverse_stability_status", "numeric_evaluation", "blocker_count"):
        check(f"primary-independent {field}", p[field] == i[field], [p[field], i[field]], "exact agreement", "independence")
    check("primary-independent authority hashes", primary["source_hashes"] == independent["source_hashes"], True, True, "independence")
    check("primary-independent no numeric evaluation", p["numeric_evaluation"] is False and i["numeric_evaluation"] is False, [p["numeric_evaluation"], i["numeric_evaluation"]], [False, False], "scope")
    check("hostile all mutations rejected", hostile["controls"]["all_mutations_rejected"] is True and all(row["status"] == "PASS" for row in hostile["assertions"]), hostile["controls"], True, "hostile")
    check("hostile mutation count", len(hostile["assertions"]) == 8, len(hostile["assertions"]), 8, "hostile")

    payload = {
        "schema": "tect/pre-a-t055-physical-empty-bounded-revalidation-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["test_card_id"],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["card_id"],
        "verdict": "BLOCKED",
        "assertion_count": len(checks),
        "assertions": checks,
        "source_hashes": source_hashes,
        "artifact_hashes": artifact_hashes,
        "derived": {
            "primary": p,
            "independent": i,
            "hostile": hostile["controls"],
            "lean": "PASS",
            "numeric_evaluation": False,
            "command_outputs": child_outputs,
        },
        "evidence_level": manifest["evidence_level"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "blockers": manifest["blockers"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    if args.self_test:
        assert payload["verdict"] == "BLOCKED"
        assert payload["derived"]["numeric_evaluation"] is False
        print(f"R-427 INTEGRATED SELFTEST: PASS ({len(checks)}/{len(checks)} checks; three verdicts blocked; Lean PASS)")
        return 0
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-427 INTEGRATED BLOCKED {len(checks)}/{len(checks)} checks; sign=BLOCKED_NOT_EVALUATED stationarity=BLOCKED_NOT_EVALUATED transverse=BLOCKED_NOT_EVALUATED Lean=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
