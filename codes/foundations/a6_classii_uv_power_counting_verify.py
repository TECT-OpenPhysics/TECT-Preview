#!/usr/bin/env python3
"""One-command verifier for A6 primary and non-importing independent audits."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A6-CLASSII-UV-POWER-COUNTING"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = __claims__[0]
CLAIM_DIR = REPO / "claims" / CLAIM
MANIFEST = CLAIM_DIR / "classii_uv_power_counting_manifest.json"
PRIMARY = REPO / "codes" / "foundations" / "a6_classii_uv_power_counting.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a6_classii_uv_power_counting_independent.py"
PRIMARY_RESULT = CLAIM_DIR / "runs" / "2026-07-20-primary-classii-uv" / "result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs" / "2026-07-20-independent-classii-uv" / "result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-integrated-classii-uv" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def row_at(result: dict[str, Any], cutoff: int) -> dict[str, Any]:
    matches = [row for row in result["cutoff_rows"] if int(row["cutoff"]) == cutoff]
    if len(matches) != 1:
        raise AssertionError(f"expected one cutoff {cutoff} row, got {len(matches)}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    primary_run = subprocess.run(
        [sys.executable, str(PRIMARY), "--output", str(PRIMARY_RESULT)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    independent_run = subprocess.run(
        [sys.executable, str(INDEPENDENT), "--output", str(INDEPENDENT_RESULT)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    primary_result = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8")) if PRIMARY_RESULT.exists() else {}
    independent_result = json.loads(INDEPENDENT_RESULT.read_text(encoding="utf-8")) if INDEPENDENT_RESULT.exists() else {}
    assertions: list[dict[str, Any]] = []

    add("primary_subprocess_passes", primary_run.returncode == 0, primary_run.returncode, 0, assertions)
    add("independent_subprocess_passes", independent_run.returncode == 0, independent_run.returncode, 0, assertions)
    add("primary_verdict_passes", primary_result.get("verdict") == "A6-CLASSII-UV-PRIMARY-PASS", primary_result.get("verdict"), "A6-CLASSII-UV-PRIMARY-PASS", assertions)
    add("independent_verdict_passes", independent_result.get("verdict") == "A6-CLASSII-UV-INDEPENDENT-PASS", independent_result.get("verdict"), "A6-CLASSII-UV-INDEPENDENT-PASS", assertions)

    for key, path in (("primary_audit", PRIMARY), ("independent_audit", INDEPENDENT), ("one_command_verifier", Path(__file__).resolve())):
        expected_hash = manifest["authority"][key]["sha256"]
        add(f"{key}_hash_matches", sha256(path) == expected_hash, sha256(path), expected_hash, assertions)

    if primary_result and independent_result:
        primary_delta = float(primary_result["derived"]["delta_cube"])
        independent_delta = float(independent_result["derived"]["delta_cube"])
        delta_error = abs(primary_delta - independent_delta) / primary_delta
        add("independent_cube_coefficients_agree", delta_error < float(manifest["integrated_audit"]["cube_coefficient_relative_tolerance"]), delta_error, manifest["integrated_audit"]["cube_coefficient_relative_tolerance"], assertions)

        common_cutoff = int(manifest["integrated_audit"]["common_cutoff"])
        primary_common = row_at(primary_result, common_cutoff)
        independent_common = row_at(independent_result, common_cutoff)
        primary_energy = float(primary_common["moments"]["classii_energy_density_expectation"])
        independent_energy = float(independent_common["moments"]["classii_energy_density_expectation"])
        energy_error = abs(primary_energy - independent_energy) / primary_energy
        add("common_cutoff_ClassII_expectations_agree", energy_error < float(manifest["integrated_audit"]["common_energy_relative_tolerance"]), energy_error, manifest["integrated_audit"]["common_energy_relative_tolerance"], assertions)

        primary_counterterm = primary_result["derived"]["counterterm_test_values"]
        independent_counterterm = independent_result["derived"]["counterterm_test_values"]
        counterterm_error = max(
            abs(float(left) - float(right)) / max(1.0, abs(float(left)))
            for left, right in zip(primary_counterterm, independent_counterterm)
        )
        add("counterterm_function_reconstruction_agrees", counterterm_error < float(manifest["integrated_audit"]["counterterm_relative_tolerance"]), counterterm_error, manifest["integrated_audit"]["counterterm_relative_tolerance"], assertions)
        add("both_routes_find_positive_linear_growth", float(primary_result["derived"]["predicted_classii_energy_density_slope"]) > 0.0 and float(independent_result["derived"]["classii_energy_increment"]) > 0.0, {"primary": primary_result["derived"]["predicted_classii_energy_density_slope"], "independent": independent_result["derived"]["classii_energy_increment"]}, "both positive", assertions)

    add("complex_covariance_factor_two_is_explicit", "2 A(k)^-1" in manifest["convention"]["complex_mode_covariance"], manifest["convention"]["complex_mode_covariance"], "explicit factor 2", assertions)
    add("bare_route_negative_result_is_scope_limited", "renormalised Class-II measure nonexistence" in manifest["honesty_boundary"]["excluded"], manifest["honesty_boundary"]["excluded"], "nonexistence not claimed", assertions)

    passed = sum(row["status"] == "PASS" for row in assertions)
    primary_total = int(primary_result.get("assertion_summary", {}).get("total", 0))
    independent_total = int(independent_result.get("assertion_summary", {}).get("total", 0))
    verdict = "A6-CLASSII-UV-POWER-COUNTING-INTEGRATED-PASS" if passed == len(assertions) else "A6-CLASSII-UV-POWER-COUNTING-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a6-classii-uv-integrated-result/1.0",
        "claim_id": CLAIM,
        "script_version": __version__,
        "verdict": verdict,
        "subprocesses": {
            "primary": {"returncode": primary_run.returncode, "stdout": primary_run.stdout, "stderr": primary_run.stderr},
            "independent": {"returncode": independent_run.returncode, "stdout": independent_run.stdout, "stderr": independent_run.stderr},
        },
        "source_reports": {
            "manifest_sha256": sha256(MANIFEST),
            "primary_sha256": sha256(PRIMARY),
            "independent_sha256": sha256(INDEPENDENT),
            "verifier_sha256": sha256(Path(__file__).resolve()),
            "primary_result_sha256": sha256(PRIMARY_RESULT) if PRIMARY_RESULT.exists() else None,
            "independent_result_sha256": sha256(INDEPENDENT_RESULT) if INDEPENDENT_RESULT.exists() else None,
        },
        "assertions": assertions,
        "assertion_summary": {
            "integrated_passed": passed,
            "integrated_total": len(assertions),
            "primary_total": primary_total,
            "independent_total": independent_total,
            "aggregate_total": primary_total + independent_total + len(assertions),
        },
        "failures": [row["name"] for row in assertions if row["status"] != "PASS"],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: primary ({primary_result.get('assertion_summary', {}).get('passed', 0)}/{primary_total})" if primary_run.returncode == 0 else "FAIL: primary")
    print(f"PASS: independent ({independent_result.get('assertion_summary', {}).get('passed', 0)}/{independent_total})" if independent_run.returncode == 0 else "FAIL: independent")
    print(f"ASSERTS: {primary_total + independent_total + len(assertions)}/{primary_total + independent_total + len(assertions)}" if passed == len(assertions) and primary_run.returncode == independent_run.returncode == 0 else f"INTEGRATED ASSERTS: {passed}/{len(assertions)}")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if verdict.endswith("INTEGRATED-PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
