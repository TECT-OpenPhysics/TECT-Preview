#!/usr/bin/env python3
"""One-command verifier for the A12 sharp-cube budget obstruction.

Version: 1.0.0 (first issued 2026-07-21; this version 2026-07-21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-21"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_sharp_cube_budget_obstruction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-21-integrated-sharp-cube-obstruction" / "result.json"
PRIMARY = REPO / "codes" / "foundations" / "a12_classii_sharp_cube_budget_obstruction.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a12_classii_sharp_cube_budget_obstruction_independent.py"
BASELINE = REPO / "codes" / "foundations" / "a12_classii_source_square_reduction_verify.py"
PRIMARY_OUTPUT = CLAIM / "runs" / "2026-07-21-primary-sharp-cube-obstruction" / "result.json"
INDEPENDENT_OUTPUT = CLAIM / "runs" / "2026-07-21-independent-sharp-cube-obstruction" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def execute(script: Path, manifest: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    baseline_execution = subprocess.run(
        [sys.executable, str(BASELINE)], cwd=REPO, capture_output=True, text=True
    )
    primary_execution = execute(PRIMARY, manifest_path, PRIMARY_OUTPUT)
    independent_execution = execute(INDEPENDENT, manifest_path, INDEPENDENT_OUTPUT)

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8")) if PRIMARY_OUTPUT.exists() else {}
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8")) if INDEPENDENT_OUTPUT.exists() else {}
    rows: list[dict[str, Any]] = []

    add(rows, "baseline_A12_exit_zero", baseline_execution.returncode == 0, baseline_execution.returncode, 0)
    add(rows, "baseline_A12_integrated_marker", "A12-CLASSII-SOURCE-SQUARE-REDUCTION-INTEGRATED-PASS" in baseline_execution.stdout, baseline_execution.stdout[-500:], "contains baseline integrated PASS marker")
    add(rows, "primary_exit_zero", primary_execution["returncode"] == 0, primary_execution["returncode"], 0)
    add(rows, "independent_exit_zero", independent_execution["returncode"] == 0, independent_execution["returncode"], 0)
    add(rows, "primary_has_no_failures", primary.get("failures") == [], primary.get("failures"), [])
    add(rows, "independent_has_no_failures", independent.get("failures") == [], independent.get("failures"), [])
    add(rows, "claim_ids_match", primary.get("claim_id") == independent.get("claim_id") == "A12-CLASSII-SOURCE-SQUARE-REDUCTION", [primary.get("claim_id"), independent.get("claim_id")], "A12-CLASSII-SOURCE-SQUARE-REDUCTION")

    primary_h = primary.get("exact_theorem", {}).get("H6_lower")
    independent_h = independent.get("sharp_asymptotic", {}).get("H6_lower")
    add(rows, "sharp_H6_lower_matches", primary_h == independent_h == "786432", [primary_h, independent_h], "786432")
    primary_finite = Decimal(primary.get("finite_rational_witness", {}).get("elementary_H6_lower_decimal", "NaN"))
    independent_finite = Decimal(independent.get("finite_countercertificate", {}).get("elementary_H6_lower_decimal", "NaN"))
    add(rows, "finite_countercertificate_matches", primary_finite == independent_finite, str(primary_finite), str(independent_finite))

    target = Decimal(primary.get("budget", {}).get("H6_target", "NaN"))
    independent_target = Decimal(independent.get("finite_countercertificate", {}).get("production_target", "NaN"))
    add(rows, "production_target_matches", abs(target - independent_target) < Decimal("1e-12"), str(target), str(independent_target))
    add(rows, "finite_countercertificate_fires_target", primary_finite > target, str(primary_finite), f">{target}")
    add(rows, "sharp_lower_fires_target", Decimal(primary_h or "NaN") > target, primary_h, f">{target}")

    negative_tag = manifest["consequence"]["negative_result"]
    add(rows, "negative_result_tag_matches", primary.get("negative_result") == independent.get("negative_result") == negative_tag, [primary.get("negative_result"), independent.get("negative_result")], negative_tag)
    next_gate = manifest["consequence"]["next_gate"]
    add(rows, "next_gate_matches", primary.get("next_gate") == independent.get("next_gate") == next_gate, [primary.get("next_gate"), independent.get("next_gate")], next_gate)
    add(rows, "next_gate_retains_exact_B_and_shell", "COEFFICIENT-AWARE" in next_gate and "SHELL-LOCALISED" in next_gate, next_gate, "coefficient-aware and shell-localised")

    gauge = primary.get("gauge_null", {})
    tolerance = Decimal(str(manifest["audit"]["gauge_tolerance"]))
    add(rows, "primary_gauge_null", Decimal(str(gauge.get("B_null_error", "NaN"))) < tolerance, gauge.get("B_null_error"), f"<{tolerance}")
    independent_gauge = independent.get("gauge_current_errors", {})
    add(rows, "independent_gauge_currents_null", max(Decimal(str(independent_gauge.get(key, "NaN"))) for key in ("maximum_density_derivative", "maximum_J_current", "maximum_K_current")) < tolerance, independent_gauge, f"all <{tolerance}")

    for key in ("primary", "independent", "verifier"):
        source = manifest["sources"][key]
        add(rows, f"integrated_source_{key}_hash", sha256(REPO / source["path"]) == source["sha256"], sha256(REPO / source["path"]), source["sha256"])

    add(rows, "tier_remains_scoped_T4", manifest["consequence"]["tier_after"] == "T4", manifest["consequence"]["tier_after"], "T4")
    add(rows, "exact_B_source_remains_open", manifest["consequence"]["exact_B_source_status"] == "OPEN", manifest["consequence"]["exact_B_source_status"], "OPEN")

    failures = [row for row in rows if row["status"] != "PASS"]
    child_assertions = int(primary.get("assertion_count", 0)) + int(independent.get("assertion_count", 0))
    total_assertions = child_assertions + len(rows)
    result = {
        "schema": "tect/a12-classii-sharp-cube-budget-obstruction-integrated-result/1.0",
        "claim_id": "A12-CLASSII-SOURCE-SQUARE-REDUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "conclusion": "The separated H6 and coefficient-blind scalar-envelope routes cannot meet the production source-only budget; the exact-B shell-localised source remains open because B(X) JX=0.",
        "child_execution": {
            "baseline_A12": {
                "returncode": baseline_execution.returncode,
                "stdout": baseline_execution.stdout,
                "stderr": baseline_execution.stderr,
            },
            "primary": primary_execution,
            "independent": independent_execution,
        },
        "primary_result": primary,
        "independent_result": independent,
        "cross_assertion_count": len(rows),
        "cross_assertions": rows,
        "assertion_count": total_assertions,
        "negative_result": negative_tag,
        "next_gate": next_gate,
        "failures": failures,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if baseline_execution.stdout:
        print(baseline_execution.stdout, end="")
    if primary_execution["stdout"]:
        print(primary_execution["stdout"], end="")
    if independent_execution["stdout"]:
        print(independent_execution["stdout"], end="")
    if failures:
        print(f"ASSERTS: {total_assertions - len(failures)}/{total_assertions}")
        for failure in failures:
            print(f"  FAIL {failure['name']}: {failure['actual']} expected {failure['expected']}")
        return 1
    print(f"ASSERTS: {total_assertions}/{total_assertions}")
    print("A12-CLASSII-SHARP-CUBE-BUDGET-OBSTRUCTION-INTEGRATED-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    manifest = arguments.manifest if arguments.manifest.is_absolute() else REPO / arguments.manifest
    output = arguments.output if arguments.output.is_absolute() else REPO / arguments.output
    return run(manifest, output)


if __name__ == "__main__":
    raise SystemExit(main())
