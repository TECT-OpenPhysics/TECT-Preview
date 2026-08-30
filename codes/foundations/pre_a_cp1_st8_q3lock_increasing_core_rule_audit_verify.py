#!/usr/bin/env python3
"""Integrated verifier for the finite R-439 adaptive support package."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-increasing-core-rule-audit-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_increasing_core_rule_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_increasing_core_rule_audit_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_increasing_core_rule_audit_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R439.lean"
SLUG = "increasing_core_rule_audit"
RUN_ROOT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
PRIMARY_OUTPUT = RUN_ROOT / f"2026-08-30-primary-{SLUG}" / "primary.json"
INDEPENDENT_OUTPUT = RUN_ROOT / f"2026-08-30-independent-{SLUG}" / "independent.json"
HOSTILE_OUTPUT = RUN_ROOT / f"2026-08-30-hostile-{SLUG}" / "hostile.json"
INTEGRATED_OUTPUT = RUN_ROOT / f"2026-08-30-integrated-{SLUG}" / "integrated.json"
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


def normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(normalised_bytes(path)).hexdigest()


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
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-439" and manifest["exploration_id"] == "EXP-001284" and manifest["claim_bearing"] is False and manifest["status"] == "INCREASING_CORE_RULE_AUDITED", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-439 finite non-claiming identity", "provenance")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-439 artifacts", "provenance")
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
            completed = command([os.fspath(Path(sys.executable)), "-X", "utf8", os.fspath(script), "--self-test"], ROOT)
            outputs[script.name] = (completed.stdout + completed.stderr).strip()
            check(f"run {script.name}", completed.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")

    lean = command([os.fspath(LAKE), "env", "lean", "Tect/R439.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1200:], "exit 0 without errors", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    expected_supports = [{"core": case["expected_core"], "tail": case["expected_tail"]} for case in manifest["cases"]]
    primary_supports = [{"core": case["core"], "tail": case["tail"]} for case in primary["derived"]["cases"]]
    independent_supports = [{"core": case["core"], "tail": case["tail"]} for case in independent["derived"]["cases"]]
    check("primary adaptive rule", primary["verdict"] == "INCREASING_CORE_RULE_AUDITED" and primary["assertion_count"] >= 1 and primary["derived"]["all_coordinates_unambiguous"] is True and primary["derived"]["increasing_core_tail_modulus_closed"] is False, [primary["verdict"], primary["assertion_count"], primary["derived"]["all_coordinates_unambiguous"], primary["derived"]["increasing_core_tail_modulus_closed"]], "finite rule and no uniform promotion", "primary")
    check("primary supports", primary_supports == expected_supports and primary["derived"]["raw_index_nested"] is False and primary["derived"]["core_cardinality_monotone"] is False, primary_supports, expected_supports, "primary")
    check("independent adaptive control", independent["verdict"] == "INDEPENDENT_ADAPTIVE_RULE_CONTROL" and independent["assertion_count"] >= 1 and independent["derived"]["all_coordinates_unambiguous"] is True, [independent["verdict"], independent["assertion_count"]], "finite independent rule control", "independent")
    check("independent supports", independent_supports == expected_supports and independent["derived"]["raw_index_nested"] is False and independent["derived"]["core_cardinality_monotone"] is False, independent_supports, expected_supports, "independent")
    check("hostile controls", hostile["verdict"] == "HOSTILE_MUTATIONS_REJECTED" and hostile["assertion_count"] == len(hostile["mutations"]) + 1 and hostile["scope"]["hostile_mutations_rejected"] and hostile["scope"]["uniform_promotion_rejected"] and hostile["scope"]["physical_promotion_rejected"], hostile["scope"], "all hostile mutations rejected", "hostile")
    closed_flags = [key for key, value in manifest["scope"].items() if key.endswith("_closed") and value]
    check("scope firewall", not closed_flags and manifest["scope"]["cutoff_adaptive_core_rule_defined"] and manifest["scope"]["directed_threshold_classification_certified"] and manifest["scope"]["all_coordinates_unambiguous"] and manifest["scope"]["no_new_negative_result"] and manifest["scope"]["no_tier_change"], [closed_flags, manifest["scope"]["cutoff_adaptive_core_rule_defined"], manifest["scope"]["all_coordinates_unambiguous"]], "all finite flags true and promotion flags false", "scope")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r439-integrated/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-439",
        "exploration_id": "EXP-001284",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "integrated",
        "verdict": "INCREASING_CORE_RULE_AUDITED",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"core_cardinalities": primary["derived"]["core_cardinalities"], "raw_index_nested": primary["derived"]["raw_index_nested"], "core_cardinality_monotone": primary["derived"]["core_cardinality_monotone"], "primary_assertions": primary["assertion_count"], "independent_assertions": independent["assertion_count"], "hostile_assertions": hostile["assertion_count"], "all_coordinates_unambiguous": True, "lean": "PASS", "outputs": outputs},
        "source_hashes": hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-439 INTEGRATED INCREASING_CORE_RULE_AUDITED {len(checks)}/{len(checks)} core_cardinalities={primary['derived']['core_cardinalities']} nested={primary['derived']['raw_index_nested']} Lean=PASS", flush=True)
    if args.self_test:
        assert payload["verdict"] == "INCREASING_CORE_RULE_AUDITED"
        assert payload["derived"]["lean"] == "PASS"
        print("R-439 INTEGRATED SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
