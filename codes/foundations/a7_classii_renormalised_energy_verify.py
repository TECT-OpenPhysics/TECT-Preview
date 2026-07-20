#!/usr/bin/env python3
"""Fail-closed integrated verifier for the A7 Class-II energy composite."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

__version__ = "1.0.1"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE"]

REPO = Path(__file__).resolve().parents[2]
CLAIM_DIR = REPO / "claims" / __claims__[0]
DEFAULT_MANIFEST = CLAIM_DIR / "classii_renormalised_energy_manifest.json"
DEFAULT_PRIMARY = REPO / "codes" / "foundations" / "a7_classii_renormalised_energy.py"
DEFAULT_INDEPENDENT = REPO / "codes" / "foundations" / "a7_classii_renormalised_energy_independent.py"
DEFAULT_PRIMARY_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-primary-renormalised-energy" / "result.json"
DEFAULT_INDEPENDENT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-independent-renormalised-energy" / "result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-integrated-renormalised-energy" / "result.json"

AUTHORITY_CONTRACT: dict[str, dict[str, str]] = {
    "production_functional_manifest": {
        "path": "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
        "schema": "tect/a1-production-functional-realisation/1.0",
    },
    "a6_uv_source": {
        "path": "codes/foundations/a6_classii_uv_power_counting.py",
        "version": "1.0.2",
    },
    "a6_k_composite_manifest": {
        "path": "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/classii_k_composite_manifest.json",
        "schema": "tect/a6-classii-k-composite/1.0",
    },
    "primary_audit": {
        "path": "codes/foundations/a7_classii_renormalised_energy.py",
        "version": "1.0.1",
    },
    "independent_audit": {
        "path": "codes/foundations/a7_classii_renormalised_energy_independent.py",
        "version": "1.0.1",
    },
    "one_command_verifier": {
        "path": "codes/foundations/a7_classii_renormalised_energy_verify.py",
        "version": "1.0.1",
    },
    "proof_note": {
        "path": "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/notes/classii-renormalised-energy-composite-260720-v1.0.tex.txt",
        "version": "1.0",
    },
    "proof_pdf": {
        "path": "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/notes/classii-renormalised-energy-composite-260720-v1.0.pdf",
        "version": "1.0",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def python_version(path: Path) -> str | None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return node.value.value
    return None


def inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO.resolve())
        return True
    except ValueError:
        return False


def validate_manifest_contract(manifest: dict[str, Any]) -> tuple[list[str], dict[str, dict[str, str]]]:
    errors: list[str] = []
    hashes: dict[str, dict[str, str]] = {}
    if manifest.get("schema") != "tect/a7-classii-renormalised-energy/1.1":
        errors.append("manifest schema must be tect/a7-classii-renormalised-energy/1.1")
    if manifest.get("package_version") != "1.0.1":
        errors.append("package_version must be 1.0.1")
    if manifest.get("claim_id") != __claims__[0]:
        errors.append("manifest claim_id mismatch")

    authority = manifest.get("authority")
    if not isinstance(authority, dict):
        return errors + ["authority must be an object"], hashes
    if set(authority) != set(AUTHORITY_CONTRACT):
        errors.append(
            "authority keys mismatch: "
            + repr({"actual": sorted(authority), "expected": sorted(AUTHORITY_CONTRACT)})
        )

    for key, contract in AUTHORITY_CONTRACT.items():
        entry = authority.get(key)
        if not isinstance(entry, dict):
            errors.append(f"missing authority entry: {key}")
            continue
        if entry.get("path") != contract["path"]:
            errors.append(f"{key} path mismatch")
            continue
        digest = entry.get("sha256")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            errors.append(f"{key} has invalid SHA-256")
            continue
        path = REPO / entry["path"]
        if not inside_repo(path) or not path.is_file():
            errors.append(f"{key} path is absent or outside repository")
            continue
        actual = sha256(path)
        hashes[key] = {"actual": actual, "expected": digest}
        if actual != digest:
            errors.append(f"{key} SHA-256 mismatch")

        expected_version = contract.get("version")
        if expected_version is not None:
            if entry.get("version") != expected_version:
                errors.append(f"{key} manifest version mismatch")
            if path.suffix == ".py" and python_version(path) != expected_version:
                errors.append(f"{key} source version mismatch")
            if key == "proof_note":
                header = path.read_text(encoding="utf-8").splitlines()[:12]
                if not any(f"Version: v{expected_version}" in line for line in header):
                    errors.append("proof_note header version mismatch")

        expected_schema = contract.get("schema")
        if expected_schema is not None:
            try:
                actual_schema = json.loads(path.read_text(encoding="utf-8")).get("schema")
            except (OSError, json.JSONDecodeError):
                actual_schema = None
            if actual_schema != expected_schema:
                errors.append(f"{key} upstream schema mismatch")

    integrated = manifest.get("integrated_audit", {})
    expected_counts = {
        "primary_assertions": 29,
        "independent_assertions": 17,
        "cross_assertions": 28,
        "expected_aggregate_assertions": 74,
    }
    if any(integrated.get(key) != value for key, value in expected_counts.items()):
        errors.append("integrated assertion-count contract mismatch")

    expected_run_contract = {
        "schema": "tect/a7-classii-renormalised-energy-run-contract/1.0",
        "primary_result_schema": "tect/a7-classii-renormalised-energy-primary-result/1.1",
        "independent_result_schema": "tect/a7-classii-renormalised-energy-independent-result/1.1",
        "integrated_result_schema": "tect/a7-classii-renormalised-energy-integrated-result/1.1",
    }
    if manifest.get("run_contract") != expected_run_contract:
        errors.append("run_contract mismatch")

    independent_keys = {
        "seed",
        "conditional_cutoff",
        "conditional_samples",
        "asymptotic_cutoffs",
        "variance_cutoffs",
        "variance_reference_cutoff",
        "determinant_cutoff",
        "parity_cutoff",
        "parity_tolerance",
    }
    independent = manifest.get("independent_audit")
    if not isinstance(independent, dict) or set(independent) != independent_keys:
        errors.append("independent_audit configuration mismatch")
    return errors, hashes


def run(script: Path, manifest: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


def load_result(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"{type(exc).__name__}: {exc}"
    return value if isinstance(value, dict) else {}, None


def child_contract(
    result: dict[str, Any],
    *,
    role: str,
    schema: str,
    version: str,
    verdict: str,
    manifest_digest: str,
    script_digest: str,
    config: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    run_record = result.get("run", {})
    actual = {
        "schema": result.get("schema"),
        "claim_id": result.get("claim_id"),
        "script_version": result.get("script_version"),
        "verdict": result.get("verdict"),
        "run_role": run_record.get("role"),
        "run_manifest_sha256": run_record.get("manifest_sha256"),
        "run_script_sha256": run_record.get("script_sha256"),
        "run_config_sha256": run_record.get("config_sha256"),
    }
    expected = {
        "schema": schema,
        "claim_id": __claims__[0],
        "script_version": version,
        "verdict": verdict,
        "run_role": role,
        "run_manifest_sha256": manifest_digest,
        "run_script_sha256": script_digest,
        "run_config_sha256": object_sha256(config),
    }
    return actual == expected, {"actual": actual, "expected": expected}


def write_preflight_failure(
    output_path: Path,
    manifest: dict[str, Any],
    manifest_digest: str,
    errors: list[str],
    hashes: dict[str, dict[str, str]],
) -> None:
    output = {
        "schema": "tect/a7-classii-renormalised-energy-integrated-result/1.1",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": "A7-CLASSII-RENORMALISED-ENERGY-INTEGRATED-FAIL",
        "manifest_sha256": manifest_digest,
        "scope": manifest.get("scope"),
        "preflight": {"status": "FAIL", "errors": errors, "authority_hashes": hashes},
        "assertions": [],
        "assertion_summary": {
            "cross": {"passed": 0, "total": 0},
            "aggregate": {"passed": 0, "total": 0},
        },
        "failures": ["manifest_preflight"],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "not_closed_here": manifest.get("honesty_boundary", {}).get("excluded", []),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--primary-script", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--independent-script", type=Path, default=DEFAULT_INDEPENDENT)
    parser.add_argument("--primary-output", type=Path, default=DEFAULT_PRIMARY_OUTPUT)
    parser.add_argument("--independent-output", type=Path, default=DEFAULT_INDEPENDENT_OUTPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        manifest = {}
        manifest_digest = ""
        errors = [f"manifest load failed: {type(exc).__name__}: {exc}"]
        write_preflight_failure(args.output, manifest, manifest_digest, errors, {})
        print("A7-CLASSII-RENORMALISED-ENERGY-INTEGRATED-FAIL")
        print(f"Evidence: {args.output.resolve()}")
        return 1

    manifest_digest = sha256(args.manifest)
    preflight_errors, authority_hashes = validate_manifest_contract(manifest)
    if args.primary_script.resolve() != (REPO / AUTHORITY_CONTRACT["primary_audit"]["path"]).resolve():
        preflight_errors.append("primary CLI path differs from authority path")
    if args.independent_script.resolve() != (REPO / AUTHORITY_CONTRACT["independent_audit"]["path"]).resolve():
        preflight_errors.append("independent CLI path differs from authority path")
    if preflight_errors:
        write_preflight_failure(
            args.output,
            manifest,
            manifest_digest,
            preflight_errors,
            authority_hashes,
        )
        print("A7-CLASSII-RENORMALISED-ENERGY-INTEGRATED-FAIL")
        for error in preflight_errors:
            print(f"PREFLIGHT: {error}")
        print(f"Evidence: {args.output.resolve()}")
        return 1

    primary_process = run(args.primary_script, args.manifest, args.primary_output)
    independent_process = run(args.independent_script, args.manifest, args.independent_output)
    primary, primary_load_error = load_result(args.primary_output)
    independent, independent_load_error = load_result(args.independent_output)
    assertions: list[dict[str, Any]] = []

    add(
        "primary_subprocess_exits_zero",
        primary_process["returncode"] == 0 and primary_load_error is None,
        {"process": primary_process, "load_error": primary_load_error},
        "returncode 0 and valid JSON",
        assertions,
    )
    add(
        "independent_subprocess_exits_zero",
        independent_process["returncode"] == 0 and independent_load_error is None,
        {"process": independent_process, "load_error": independent_load_error},
        "returncode 0 and valid JSON",
        assertions,
    )

    primary_ok, primary_contract = child_contract(
        primary,
        role="primary",
        schema=manifest["run_contract"]["primary_result_schema"],
        version=manifest["authority"]["primary_audit"]["version"],
        verdict="A7-CLASSII-RENORMALISED-ENERGY-PRIMARY-PASS",
        manifest_digest=manifest_digest,
        script_digest=authority_hashes["primary_audit"]["actual"],
        config={"audit": manifest["audit"]},
    )
    add("primary_result_contract_matches", primary_ok, primary_contract["actual"], primary_contract["expected"], assertions)
    independent_ok, independent_contract = child_contract(
        independent,
        role="independent",
        schema=manifest["run_contract"]["independent_result_schema"],
        version=manifest["authority"]["independent_audit"]["version"],
        verdict="A7-CLASSII-RENORMALISED-ENERGY-INDEPENDENT-PASS",
        manifest_digest=manifest_digest,
        script_digest=authority_hashes["independent_audit"]["actual"],
        config={"independent_audit": manifest["independent_audit"]},
    )
    add(
        "independent_result_contract_matches",
        independent_ok,
        independent_contract["actual"],
        independent_contract["expected"],
        assertions,
    )

    expected_primary = int(manifest["integrated_audit"]["primary_assertions"])
    expected_independent = int(manifest["integrated_audit"]["independent_assertions"])
    add(
        "primary_assertions_all_pass",
        primary.get("assertion_summary", {}).get("passed")
        == primary.get("assertion_summary", {}).get("total")
        == expected_primary,
        primary.get("assertion_summary"),
        {"passed": expected_primary, "total": expected_primary},
        assertions,
    )
    add(
        "independent_assertions_all_pass",
        independent.get("assertion_summary", {}).get("passed")
        == independent.get("assertion_summary", {}).get("total")
        == expected_independent,
        independent.get("assertion_summary"),
        {"passed": expected_independent, "total": expected_independent},
        assertions,
    )
    add(
        "both_failure_lists_are_empty",
        not primary.get("failures") and not independent.get("failures"),
        {"primary": primary.get("failures"), "independent": independent.get("failures")},
        "both empty",
        assertions,
    )

    ready = (
        primary_process["returncode"] == 0
        and independent_process["returncode"] == 0
        and primary_ok
        and independent_ok
        and "derived" in primary
        and "derived" in independent
    )
    if ready:
        p_stability = primary["derived"]["stability_threshold"]
        i_derived = independent["derived"]
        add("coefficient_a_crosscheck", abs(p_stability["a"] - i_derived["coefficients"]["a"]) < 1.0e-15, [p_stability["a"], i_derived["coefficients"]["a"]], "absolute error <1e-15", assertions)
        add("coefficient_b_crosscheck", abs(p_stability["b"] - i_derived["coefficients"]["b"]) < 1.0e-15, [p_stability["b"], i_derived["coefficients"]["b"]], "absolute error <1e-15", assertions)
        add("coefficient_c_crosscheck", abs(p_stability["c"] - i_derived["coefficients"]["c"]) < 1.0e-15, [p_stability["c"], i_derived["coefficients"]["c"]], "absolute error <1e-15", assertions)
        add("sharp_mass_threshold_crosscheck", abs(p_stability["h"] - i_derived["h"]) < 1.0e-15, [p_stability["h"], i_derived["h"]], "absolute error <1e-15", assertions)
        add("family_mass_slope_crosscheck", abs(p_stability["family_mass_slope"] - i_derived["family_mass_slope"]) < 1.0e-15, [p_stability["family_mass_slope"], i_derived["family_mass_slope"]], "absolute error <1e-15", assertions)

        p_asymptotic = primary["derived"]["counterterm_asymptotics"][-1]
        i_asymptotic = independent["derived"]["counterterm_asymptotics"][-1]
        add("counterterm_targets_crosscheck", abs(p_asymptotic["target"] - i_asymptotic["target"]) < 1.0e-15, [p_asymptotic["target"], i_asymptotic["target"]], "same delta*W target", assertions)
        add("primary_counterterm_asymptotic_passes", p_asymptotic["relative_error"] < 0.03, p_asymptotic, "<0.03", assertions)
        add("independent_counterterm_asymptotic_passes", i_asymptotic["relative_error"] < 0.03, i_asymptotic, "<0.03", assertions)
        add("conditional_MC_checks_are_statistically_consistent", primary["derived"]["conditional_monte_carlo"]["z_score"] < 5.5 and i_derived["conditional_mc"]["z_score"] < 5.5, {"primary": primary["derived"]["conditional_monte_carlo"]["z_score"], "independent": i_derived["conditional_mc"]["z_score"]}, "both z<5.5", assertions)
        add("both_variance_audits_show_decaying_tails", all(value < -0.5 for value in primary["derived"]["centered_gradient_variance"]["tail_slopes"].values()) and all(value < -0.5 for value in i_derived["variance"]["tail_slopes"].values()), {"primary": primary["derived"]["centered_gradient_variance"]["tail_slopes"], "independent": i_derived["variance"]["tail_slopes"]}, "all slopes <-0.5", assertions)
        add("plane_wave_null_negative_control_crosschecks", primary["derived"]["plane_wave_negative_control"]["W"] > 0.0 and i_derived["plane_wave_W"] > 0.0 and i_derived["plane_wave_max_current"] < 1.0e-14, {"primary": primary["derived"]["plane_wave_negative_control"], "independent_W": i_derived["plane_wave_W"], "independent_current": i_derived["plane_wave_max_current"]}, "zero current and positive W", assertions)
        add("frozen_determinant_HS_checks_crosscheck", primary["derived"]["frozen_background_determinant"]["rows"][-1]["normal_ordered_log_partition"] > 0.0 and 0.0 < i_derived["determinant"]["remainder"] <= i_derived["determinant"]["half_hs_bound"], {"primary": primary["derived"]["frozen_background_determinant"]["rows"][-1], "independent": i_derived["determinant"]}, "positive and HS bounded", assertions)
    else:
        for name in (
            "coefficient_a_crosscheck",
            "coefficient_b_crosscheck",
            "coefficient_c_crosscheck",
            "sharp_mass_threshold_crosscheck",
            "family_mass_slope_crosscheck",
            "counterterm_targets_crosscheck",
            "primary_counterterm_asymptotic_passes",
            "independent_counterterm_asymptotic_passes",
            "conditional_MC_checks_are_statistically_consistent",
            "both_variance_audits_show_decaying_tails",
            "plane_wave_null_negative_control_crosschecks",
            "frozen_determinant_HS_checks_crosscheck",
        ):
            add(name, False, "child result unavailable", "valid child results", assertions)

    for key in AUTHORITY_CONTRACT:
        row = authority_hashes[key]
        add(
            f"authority_{key}_hash_matches",
            row["actual"] == row["expected"],
            row["actual"],
            row["expected"],
            assertions,
        )
    add(
        "manifest_excludes_interacting_measure_closure",
        any("Gibbs measure" in item for item in manifest["honesty_boundary"]["excluded"]),
        manifest["honesty_boundary"]["excluded"],
        "explicit exclusion",
        assertions,
    )

    cross_passed = sum(row["status"] == "PASS" for row in assertions)
    primary_total = int(primary.get("assertion_summary", {}).get("total", 0))
    independent_total = int(independent.get("assertion_summary", {}).get("total", 0))
    aggregate_passed = (
        int(primary.get("assertion_summary", {}).get("passed", 0))
        + int(independent.get("assertion_summary", {}).get("passed", 0))
        + cross_passed
    )
    aggregate_total = primary_total + independent_total + len(assertions)
    counts_ok = (
        primary_total == expected_primary
        and independent_total == expected_independent
        and len(assertions) == int(manifest["integrated_audit"]["cross_assertions"])
        and aggregate_total == int(manifest["integrated_audit"]["expected_aggregate_assertions"])
    )
    all_pass = aggregate_passed == aggregate_total and counts_ok
    verdict = (
        "A7-CLASSII-RENORMALISED-ENERGY-INTEGRATED-PASS"
        if all_pass
        else "A7-CLASSII-RENORMALISED-ENERGY-INTEGRATED-FAIL"
    )
    failures = [row["name"] for row in assertions if row["status"] != "PASS"]
    failures.extend(primary.get("failures", []))
    failures.extend(independent.get("failures", []))
    if not counts_ok:
        failures.append("integrated_count_contract")

    output = {
        "schema": manifest["run_contract"]["integrated_result_schema"],
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": manifest_digest,
        "scope": manifest["scope"],
        "preflight": {
            "status": "PASS",
            "errors": [],
            "authority_hashes": authority_hashes,
        },
        "subprocesses": {"primary": primary_process, "independent": independent_process},
        "source_hashes": authority_hashes,
        "assertions": assertions,
        "assertion_summary": {
            "primary": primary.get("assertion_summary"),
            "independent": independent.get("assertion_summary"),
            "cross": {"passed": cross_passed, "total": len(assertions)},
            "aggregate": {"passed": aggregate_passed, "total": aggregate_total},
            "count_contract": counts_ok,
        },
        "failures": failures,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: primary ({primary.get('assertion_summary', {}).get('passed', 0)}/{primary_total})")
    print(f"PASS: independent ({independent.get('assertion_summary', {}).get('passed', 0)}/{independent_total})")
    print(f"ASSERTS: {aggregate_passed}/{aggregate_total}")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
