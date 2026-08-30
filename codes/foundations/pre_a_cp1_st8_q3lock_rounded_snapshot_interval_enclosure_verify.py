#!/usr/bin/env python3
"""Integrated verifier for the R-431 rounded-snapshot interval certificate."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-rounded-snapshot-interval-enclosure-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rounded_snapshot_interval_enclosure.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rounded_snapshot_interval_enclosure_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_rounded_snapshot_interval_enclosure_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R431.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-rounded_snapshot_interval_enclosure/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-rounded_snapshot_interval_enclosure/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-rounded_snapshot_interval_enclosure/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-rounded_snapshot_interval_enclosure/integrated.json"
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
    contract = manifest["interval_contract"]
    oracle = manifest["test_oracles"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-431" and manifest["exploration_id"] == "EXP-001276" and manifest["claim_bearing"] is False and manifest["status"] == "ROUNDED_SNAPSHOT_INTERVAL_CERTIFIED", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-431/EXP-001276/false/ROUNDED_SNAPSHOT_INTERVAL_CERTIFIED", "provenance")
    check("fixed row", contract["fixed_row"] == {"volume": 2, "cutoff_dimension": 16, "beta": "8", "orientation": "right", "conditional_row_index": 7, "core_size": 7, "tail_size": 9}, contract["fixed_row"], "V2/d16/beta8/right/row7/core7/tail9", "fixture")
    check("immutable tolerance", contract["comparison_tolerance"] == "5e-7", contract["comparison_tolerance"], "5e-7", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-431 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
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
    lean = command([str(LAKE), "env", "lean", "Tect/R431.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1800:], "exit 0 without errors", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    lower_threshold = Decimal(str(oracle["r422_lower_separation_threshold"]))
    upper_threshold = Decimal(str(oracle["r426_upper_separation_threshold"]))
    max_width = Decimal(str(contract["maximum_bracket_width"]))
    p = primary["derived"]
    i = independent["derived"]
    check("primary interval certificate", primary["verdict"] == manifest["status"] and Decimal(str(p["lower_probe"])) > lower_threshold and Decimal(str(p["upper_endpoint"])) < upper_threshold and Decimal(str(p["bracket_width"])) <= max_width and p["original_source_interval_certified"] is False, {key: p[key] for key in ("lower_probe", "upper_endpoint", "bracket_width", "original_source_interval_certified")}, "lower/upper thresholds and source boundary", "primary")
    check("independent interval certificate", independent["verdict"] == "INDEPENDENT_ROUNDED_SNAPSHOT_INTERVAL" and Decimal(str(i["lower_probe"])) > lower_threshold and Decimal(str(i["upper_endpoint"])) < upper_threshold and Decimal(str(i["bracket_width"])) <= max_width and i["original_source_interval_certified"] is False, {key: i[key] for key in ("lower_probe", "upper_endpoint", "bracket_width", "original_source_interval_certified")}, "independent lower/upper thresholds", "independent")
    check("independent bracket agreement", abs(Decimal(str(p["upper_endpoint"])) - Decimal(str(i["upper_endpoint"]))) <= Decimal("2e-10"), [p["upper_endpoint"], i["upper_endpoint"]], "<=2e-10", "independence")
    check("hostile controls", hostile["verdict"] == "PASS" and hostile["controls"]["all_mutations_rejected"] is True and hostile["controls"]["rounded_snapshot_interval_certified"] is True and hostile["controls"]["original_source_interval_certified"] is False and hostile["controls"]["residual_reuse_closed_for_original_source"] is False, hostile["controls"], "all mutations rejected and source boundary retained", "hostile")

    payload = {
        "schema": "tect/pre-a-r431-integrated/1.0",
        "result_id": "R-431",
        "exploration_id": "EXP-001276",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "integrated",
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "fixed_row": contract["fixed_row"],
            "primary_bracket": [p["lower_probe"], p["upper_endpoint"]],
            "independent_bracket": [i["lower_probe"], i["upper_endpoint"]],
            "primary_bracket_width": p["bracket_width"],
            "independent_bracket_width": i["bracket_width"],
            "r422_separation_margin": p["r422_separation_margin_lower"],
            "r426_direct_separation_margin": p["r426_separation_margin_upper"],
            "original_source_interval_certified": False,
            "residual_reuse_closed_for_original_source": False,
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
    print(f"R-431 INTEGRATED {len(checks)}/{len(checks)} interval PASS; source enclosure remains open; Lean PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
