#!/usr/bin/env python3
"""Fail-closed integrated verifier for the A9 smart-path reduction."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A9-CLASSII-SMART-PATH-CANCELLATION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM_ID = __claims__[0]
DEFAULT_MANIFEST = REPO / "claims" / CLAIM_ID / "classii_smart_path_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM_ID / "runs" / "2026-07-20-integrated-smart-path" / "result.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_AUTHORITY = {
    "production_functional_manifest": "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "a7_manifest": "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
    "a8_manifest": "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/classii_decoupled_nelson_manifest.json",
    "primary_audit": "codes/foundations/a9_classii_smart_path_cancellation.py",
    "independent_audit": "codes/foundations/a9_classii_smart_path_cancellation_independent.py",
    "one_command_verifier": "codes/foundations/a9_classii_smart_path_cancellation_verify.py",
    "proof_note": "claims/A9-CLASSII-SMART-PATH-CANCELLATION/notes/classii-smart-path-cancellation-260720-v1.0.tex.txt",
    "proof_pdf": "claims/A9-CLASSII-SMART-PATH-CANCELLATION/notes/classii-smart-path-cancellation-260720-v1.0.pdf",
}
SCRIPT_AUTHORITIES = {"primary_audit", "independent_audit", "one_command_verifier"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def literal_version(path: Path) -> str | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    return None


def validate_manifest(manifest: dict[str, Any]) -> tuple[list[str], dict[str, dict[str, str]]]:
    errors: list[str] = []
    hashes: dict[str, dict[str, str]] = {}
    if manifest.get("schema") != "tect/a9-classii-smart-path-cancellation/1.0":
        errors.append("manifest schema mismatch")
    if manifest.get("package_version") != "1.0.0":
        errors.append("package version mismatch")
    if manifest.get("claim_id") != CLAIM_ID:
        errors.append("claim id mismatch")
    if manifest.get("status") != "T5 CLOSED@EXACT-INTERPOLATION-AND-NONCENTRAL-FROZEN-SHELL":
        errors.append("scoped T5 status mismatch")
    authority = manifest.get("authority")
    if not isinstance(authority, dict) or set(authority) != set(EXPECTED_AUTHORITY):
        errors.append("authority set mismatch")
        return errors, hashes
    for name, expected_path in EXPECTED_AUTHORITY.items():
        record = authority.get(name)
        if not isinstance(record, dict) or record.get("path") != expected_path:
            errors.append(f"{name}: path mismatch")
            continue
        expected_hash = record.get("sha256")
        if not isinstance(expected_hash, str) or not HEX64.fullmatch(expected_hash):
            errors.append(f"{name}: invalid SHA-256")
            continue
        path = (REPO / expected_path).resolve()
        try:
            path.relative_to(REPO.resolve())
        except ValueError:
            errors.append(f"{name}: path escapes repository")
            continue
        if not path.is_file():
            errors.append(f"{name}: file missing")
            continue
        actual_hash = sha256(path)
        hashes[name] = {"path": expected_path, "expected": expected_hash, "actual": actual_hash}
        if actual_hash != expected_hash:
            errors.append(f"{name}: authority hash mismatch")
        if name in SCRIPT_AUTHORITIES and literal_version(path) != record.get("version"):
            errors.append(f"{name}: version mismatch")

    schemas = {
        "production_functional_manifest": "tect/a1-production-functional-realisation/1.0",
        "a7_manifest": "tect/a7-classii-renormalised-energy/1.1",
        "a8_manifest": "tect/a8-classii-decoupled-nelson/1.0",
    }
    for name, expected_schema in schemas.items():
        try:
            upstream = json.loads((REPO / EXPECTED_AUTHORITY[name]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"{name}: invalid upstream JSON")
            continue
        if upstream.get("schema") != expected_schema or authority[name].get("schema") != expected_schema:
            errors.append(f"{name}: schema mismatch")

    pdf = authority.get("proof_pdf", {})
    if not isinstance(pdf.get("pages"), int) or pdf.get("pages", 0) <= 0:
        errors.append("proof PDF page count invalid")
    if pdf.get("form_check") != "PASS" or pdf.get("overfull_hbox") != 0 or pdf.get("visual_qa") != "PASS":
        errors.append("proof PDF QA contract not closed")

    audit = manifest.get("audit", {})
    independent = manifest.get("independent_audit", {})
    tolerance_contracts = [
        (audit.get("matrix_tolerance"), 1e-8, "primary matrix"),
        (audit.get("derivative_tolerance"), 1e-6, "primary derivative"),
        (audit.get("partition_tolerance"), 5e-5, "primary partition"),
        (audit.get("trace_tolerance"), 1e-8, "primary trace"),
        (independent.get("tolerance"), 1e-9, "independent algebra"),
        (independent.get("derivative_tolerance"), 2e-5, "independent quadrature"),
    ]
    for value, ceiling, label in tolerance_contracts:
        if not isinstance(value, (int, float)) or not 0.0 < float(value) <= ceiling:
            errors.append(f"{label} tolerance outside contract")
    if audit.get("partition_quadrature_order", 0) <= audit.get("coarse_partition_quadrature_order", 0):
        errors.append("primary quadrature refinement missing")
    if independent.get("quadrature_order", 0) <= independent.get("coarse_quadrature_order", 0):
        errors.append("independent quadrature refinement missing")
    integrated = manifest.get("integrated_audit", {})
    expected_counts = {"primary_assertions": 24, "independent_assertions": 17, "cross_assertions": 17, "expected_aggregate_assertions": 58}
    for key, expected in expected_counts.items():
        if integrated.get(key) != expected:
            errors.append(f"{key} mismatch")
    contract = manifest.get("run_contract", {})
    expected_schemas = {
        "primary_result_schema": "tect/a9-classii-smart-path-primary-result/1.0",
        "independent_result_schema": "tect/a9-classii-smart-path-independent-result/1.0",
        "integrated_result_schema": "tect/a9-classii-smart-path-integrated-result/1.0",
    }
    for key, expected in expected_schemas.items():
        if contract.get(key) != expected:
            errors.append(f"{key} mismatch")
    if manifest.get("open_followup") != "A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND":
        errors.append("residual gate mismatch")
    excluded = manifest.get("honesty_boundary", {}).get("excluded", [])
    if not any("tilted-law" in item for item in excluded) or not any("full self-coupled" in item for item in excluded):
        errors.append("scope firewall incomplete")
    return errors, hashes


def run_child(script: Path, manifest: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    record: dict[str, Any] = {
        "command": [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)],
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }
    try:
        record["result"] = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record["load_error"] = str(exc)
        record["result"] = None
    return record


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_hash = sha256(args.manifest)
    preflight_errors, authority_hashes = validate_manifest(manifest)
    if preflight_errors:
        print("A9-CLASSII-SMART-PATH-PREFLIGHT-FAIL")
        for error in preflight_errors:
            print(f"PREFLIGHT: {error}")
        return 1

    authority = manifest["authority"]
    with tempfile.TemporaryDirectory(prefix="tect-a9-smart-path-") as temporary:
        root = Path(temporary)
        primary_process = run_child(REPO / authority["primary_audit"]["path"], args.manifest, root / "primary.json")
        independent_process = run_child(REPO / authority["independent_audit"]["path"], args.manifest, root / "independent.json")
        primary = primary_process.get("result")
        independent = independent_process.get("result")
    if not isinstance(primary, dict) or not isinstance(independent, dict):
        print("A9-CLASSII-SMART-PATH-INTEGRATED-FAIL")
        print("Child result missing or malformed")
        return 1

    assertions: list[dict[str, Any]] = []
    integrated = manifest["integrated_audit"]
    contract = manifest["run_contract"]
    p_summary = primary.get("assertion_summary", {})
    i_summary = independent.get("assertion_summary", {})
    add("primary_result_contract", primary.get("schema") == contract["primary_result_schema"] and primary.get("claim_id") == CLAIM_ID and primary.get("script_version") == authority["primary_audit"]["version"] and primary.get("manifest_sha256") == manifest_hash and primary.get("verdict") == "A9-CLASSII-SMART-PATH-PRIMARY-PASS", {key: primary.get(key) for key in ("schema", "claim_id", "script_version", "manifest_sha256", "verdict")}, "exact", assertions)
    add("independent_result_contract", independent.get("schema") == contract["independent_result_schema"] and independent.get("claim_id") == CLAIM_ID and independent.get("script_version") == authority["independent_audit"]["version"] and independent.get("manifest_sha256") == manifest_hash and independent.get("verdict") == "A9-CLASSII-SMART-PATH-INDEPENDENT-PASS", {key: independent.get(key) for key in ("schema", "claim_id", "script_version", "manifest_sha256", "verdict")}, "exact", assertions)
    add("primary_assertion_count", p_summary.get("passed") == integrated["primary_assertions"] and p_summary.get("total") == integrated["primary_assertions"], p_summary, integrated["primary_assertions"], assertions)
    add("independent_assertion_count", i_summary.get("passed") == integrated["independent_assertions"] and i_summary.get("total") == integrated["independent_assertions"], i_summary, integrated["independent_assertions"], assertions)

    p = primary["derived"]
    i = independent["derived"]
    add("physical_beta_B_oracle", abs(float(p["physical_constants"]["beta_B"]) - float(manifest["oracles"]["beta_B"])) <= 1e-14, p["physical_constants"]["beta_B"], manifest["oracles"]["beta_B"], assertions)
    add("physical_c_symbol_oracle", abs(float(p["physical_constants"]["c_symbol"]) - float(manifest["oracles"]["c_symbol"])) <= 1e-14, p["physical_constants"]["c_symbol"], manifest["oracles"]["c_symbol"], assertions)
    add("primary_common_even_identity", max(abs(float(value)) for value in p["local_cross_covariances"]) < manifest["audit"]["even_tolerance"], p["local_cross_covariances"], "zero", assertions)
    add("primary_interpolation_derivative", max(float(row["raw_cancel_error"]) for row in p["interpolation"]) < manifest["audit"]["partition_tolerance"], p["interpolation"], manifest["audit"]["partition_tolerance"], assertions)
    primary_convergence = next(row for row in primary["assertions"] if row["name"] == "IBP_quadrature_error_contracts_at_higher_order")
    add("primary_quadrature_refinement", primary_convergence["status"] == "PASS", primary_convergence, "PASS", assertions)
    add("primary_noncentral_shell", p["noncentral_shell"]["absolute_error"] < manifest["audit"]["quadrature_tolerance"] and p["noncentral_shell"]["source_remainder"] <= 0.0 and p["noncentral_shell"]["bound_gap"] >= 0.0, p["noncentral_shell"], "formula, source sign, HS ceiling", assertions)
    add("independent_common_even_identity", max(abs(float(value)) for value in i["parity"]) < manifest["independent_audit"]["tolerance"], i["parity"], "zero", assertions)
    add("independent_interpolation_derivative", max(float(row["raw_cancelled_error"]) for row in i["interpolation"]) < manifest["independent_audit"]["derivative_tolerance"], i["interpolation"], manifest["independent_audit"]["derivative_tolerance"], assertions)
    independent_convergence = next(row for row in independent["assertions"] if row["name"] == "independent_IBP_quadrature_convergence")
    add("independent_quadrature_refinement", independent_convergence["status"] == "PASS", independent_convergence, "PASS", assertions)
    add("independent_noncentral_shell", i["noncentral_shell"]["error"] < manifest["independent_audit"]["derivative_tolerance"] and i["noncentral_shell"]["source_part"] <= 0.0 and i["noncentral_shell"]["ceiling_gap"] >= 0.0, i["noncentral_shell"], "formula, source sign, HS ceiling", assertions)
    add("deterministic_shift_positivity", i["deterministic_shift"]["exact"] >= 0.0 and i["deterministic_shift"]["error"] < manifest["independent_audit"]["tolerance"], i["deterministic_shift"], "nonnegative exact", assertions)
    add("odd_regulator_negative_control", max(abs(float(value)) for value in i["odd_control"]["parity"]) > manifest["independent_audit"]["negative_control_floor"] and abs(float(i["odd_control"]["result"]["cancelled"]) - float(i["odd_control"]["result"]["without_divergence"])) > manifest["independent_audit"]["negative_control_floor"], i["odd_control"], "parity and omitted-divergence gaps", assertions)
    add("tilted_gate_scope_firewall", manifest["open_followup"] == "A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND" and any("full self-coupled" in item for item in manifest["honesty_boundary"]["excluded"]), {"gate": manifest["open_followup"], "excluded": manifest["honesty_boundary"]["excluded"]}, "named open gate and exclusion", assertions)

    primary_total = int(p_summary.get("total", 0))
    independent_total = int(i_summary.get("total", 0))
    cross_passed = sum(row["status"] == "PASS" for row in assertions)
    aggregate_passed = int(p_summary.get("passed", 0)) + int(i_summary.get("passed", 0)) + cross_passed
    aggregate_total = primary_total + independent_total + len(assertions)
    counts_ok = (
        primary_total == integrated["primary_assertions"]
        and independent_total == integrated["independent_assertions"]
        and len(assertions) == integrated["cross_assertions"]
        and aggregate_total == integrated["expected_aggregate_assertions"]
    )
    failures = [row for row in assertions if row["status"] != "PASS"]
    all_pass = (
        primary_process["returncode"] == 0
        and independent_process["returncode"] == 0
        and not primary.get("failures")
        and not independent.get("failures")
        and not failures
        and counts_ok
        and aggregate_passed == aggregate_total
    )
    verdict = "A9-CLASSII-SMART-PATH-INTEGRATED-PASS" if all_pass else "A9-CLASSII-SMART-PATH-INTEGRATED-FAIL"
    output = {
        "schema": contract["integrated_result_schema"],
        "claim_id": CLAIM_ID,
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": manifest_hash,
        "scope": manifest["scope"],
        "preflight": {"status": "PASS", "errors": [], "authority_hashes": authority_hashes},
        "subprocesses": {
            "primary": {key: value for key, value in primary_process.items() if key != "result"},
            "independent": {key: value for key, value in independent_process.items() if key != "result"},
        },
        "assertions": assertions,
        "assertion_summary": {
            "primary": p_summary,
            "independent": i_summary,
            "cross": {"passed": cross_passed, "total": len(assertions)},
            "aggregate": {"passed": aggregate_passed, "total": aggregate_total},
            "count_contract": counts_ok,
        },
        "key_results": {
            "physical_constants": p["physical_constants"],
            "primary_interpolation": p["interpolation"],
            "primary_noncentral_shell": p["noncentral_shell"],
            "independent_interpolation": i["interpolation"],
            "independent_noncentral_shell": i["noncentral_shell"],
            "deterministic_shift": i["deterministic_shift"],
            "odd_control": i["odd_control"],
        },
        "failures": failures,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: primary ({p_summary.get('passed', 0)}/{primary_total})")
    print(f"PASS: independent ({i_summary.get('passed', 0)}/{independent_total})")
    print(f"ASSERTS: {aggregate_passed}/{aggregate_total}")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
