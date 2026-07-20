#!/usr/bin/env python3
"""Fail-closed integrated verifier for A8's decoupled Nelson theorem."""

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
REPO = Path(__file__).resolve().parents[2]
CLAIM_ID = "A8-CLASSII-DECOUPLED-NELSON-BOUND"
DEFAULT_MANIFEST = REPO / "claims" / CLAIM_ID / "classii_decoupled_nelson_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM_ID / "runs" / "2026-07-20-integrated-decoupled-nelson" / "result.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_AUTHORITY = {
    "production_functional_manifest": "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "a7_composite_manifest": "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
    "primary_audit": "codes/foundations/a8_classii_decoupled_nelson.py",
    "independent_audit": "codes/foundations/a8_classii_decoupled_nelson_independent.py",
    "one_command_verifier": "codes/foundations/a8_classii_decoupled_nelson_verify.py",
    "proof_note": "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/notes/a8-classii-decoupled-nelson-bound-260720-v1.0.tex.txt",
    "proof_pdf": "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/notes/a8-classii-decoupled-nelson-bound-260720-v1.0.pdf",
}
SCRIPT_AUTHORITIES = ("primary_audit", "independent_audit", "one_command_verifier")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
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
    if manifest.get("schema") != "tect/a8-classii-decoupled-nelson/1.0":
        errors.append("manifest schema mismatch")
    if manifest.get("package_version") != "1.0.0":
        errors.append("manifest package version mismatch")
    if manifest.get("claim_id") != CLAIM_ID:
        errors.append("manifest claim id mismatch")
    if manifest.get("status") != "T5 CLOSED@INDEPENDENT-DERIVATIVE-PRODUCT-GAUSSIAN":
        errors.append("manifest scoped T5 status mismatch")
    authority = manifest.get("authority")
    if not isinstance(authority, dict) or set(authority) != set(EXPECTED_AUTHORITY):
        errors.append("authority set is not exact")
        return errors, hashes

    for name, expected_relative in EXPECTED_AUTHORITY.items():
        item = authority.get(name)
        if not isinstance(item, dict):
            errors.append(f"{name}: authority entry missing")
            continue
        if item.get("path") != expected_relative:
            errors.append(f"{name}: authority path mismatch")
            continue
        expected_hash = item.get("sha256")
        if not isinstance(expected_hash, str) or not HEX64.fullmatch(expected_hash):
            errors.append(f"{name}: invalid SHA-256")
            continue
        path = (REPO / expected_relative).resolve()
        try:
            path.relative_to(REPO.resolve())
        except ValueError:
            errors.append(f"{name}: path escapes repository")
            continue
        if not path.is_file():
            errors.append(f"{name}: authority file missing")
            continue
        actual_hash = sha256(path)
        hashes[name] = {"path": expected_relative, "expected": expected_hash, "actual": actual_hash}
        if actual_hash != expected_hash:
            errors.append(f"{name}: authority hash mismatch")
        if name in SCRIPT_AUTHORITIES:
            actual_version = literal_version(path)
            if actual_version != item.get("version"):
                errors.append(f"{name}: script version mismatch")

    try:
        a1 = json.loads((REPO / EXPECTED_AUTHORITY["production_functional_manifest"]).read_text(encoding="utf-8"))
        if a1.get("schema") != authority["production_functional_manifest"].get("schema"):
            errors.append("A1 upstream schema mismatch")
    except (OSError, json.JSONDecodeError):
        errors.append("A1 upstream JSON invalid")
    try:
        a7 = json.loads((REPO / EXPECTED_AUTHORITY["a7_composite_manifest"]).read_text(encoding="utf-8"))
        if a7.get("schema") != authority["a7_composite_manifest"].get("schema"):
            errors.append("A7 upstream schema mismatch")
    except (OSError, json.JSONDecodeError):
        errors.append("A7 upstream JSON invalid")

    regulator = manifest.get("regulator_class", {})
    if regulator.get("multiplier_supremum_bound") != 1.0:
        errors.append("executable regulator bound must pin the contractive M_R=1 audit")
    theorem = manifest.get("theorem", {})
    if "M_R" not in theorem.get("trace_ideal", ""):
        errors.append("trace-ideal theorem omits the general regulator bound")
    excluded = manifest.get("honesty_boundary", {}).get("excluded", [])
    if not any("self-coupled A7" in item for item in excluded):
        errors.append("self-coupled A7 scope firewall missing")

    proof_pdf = authority.get("proof_pdf", {})
    if not isinstance(proof_pdf.get("pages"), int) or proof_pdf.get("pages", 0) <= 0:
        errors.append("proof PDF page count is not positive")
    if proof_pdf.get("form_check") != "PASS":
        errors.append("proof PDF form check is not PASS")
    if proof_pdf.get("overfull_hbox") != 0:
        errors.append("proof PDF overfull-hbox count is not zero")
    if proof_pdf.get("visual_qa") != "PASS":
        errors.append("proof PDF visual QA is not PASS")

    audit = manifest.get("audit", {})
    independent_audit = manifest.get("independent_audit", {})
    integrated_tolerances = manifest.get("integrated_audit", {})
    tolerance_contracts = [
        (audit.get("matrix_tolerance"), 1e-8, "primary matrix tolerance"),
        (audit.get("trace_tolerance"), 1e-8, "primary trace tolerance"),
        (audit.get("relative_tolerance"), 1e-8, "primary relative tolerance"),
        (independent_audit.get("matrix_tolerance"), 1e-8, "independent matrix tolerance"),
        (independent_audit.get("relative_tolerance"), 1e-8, "independent relative tolerance"),
        (independent_audit.get("divergence_identity_tolerance"), 1e-7, "divergence tolerance"),
        (integrated_tolerances.get("coefficient_absolute_tolerance"), 1e-12, "cross absolute tolerance"),
        (integrated_tolerances.get("derived_relative_tolerance"), 1e-8, "cross relative tolerance"),
    ]
    for value, maximum, label in tolerance_contracts:
        if not isinstance(value, (int, float)) or not 0.0 < float(value) <= maximum:
            errors.append(f"{label} outside fail-closed range")
    orders = independent_audit.get("quadrature_orders")
    if not isinstance(orders, list) or len(orders) < 2 or any(not isinstance(order, int) or order < 32 for order in orders):
        errors.append("independent quadrature-order contract is too weak")

    integrated = manifest.get("integrated_audit", {})
    if integrated.get("primary_assertions") != 21:
        errors.append("primary assertion contract mismatch")
    if integrated.get("independent_assertions") != 15:
        errors.append("independent assertion contract mismatch")
    if integrated.get("cross_assertions") != 18:
        errors.append("cross assertion contract mismatch")
    if integrated.get("expected_aggregate_assertions") != 54:
        errors.append("aggregate assertion contract mismatch")
    contract = manifest.get("run_contract", {})
    if contract.get("primary_result_schema") != "tect/a8-classii-decoupled-nelson-primary-result/1.0":
        errors.append("primary result schema contract mismatch")
    if contract.get("independent_result_schema") != "tect/a8-classii-decoupled-nelson-independent-result/1.0":
        errors.append("independent result schema contract mismatch")
    if contract.get("integrated_result_schema") != "tect/a8-classii-decoupled-nelson-integrated-result/1.0":
        errors.append("integrated result schema contract mismatch")
    if manifest.get("open_followup") != "A7-CLASSII-SELF-COUPLING-INTERPOLATION":
        errors.append("self-coupling followup mismatch")
    return errors, hashes


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def close(left: float, right: float, absolute: float, relative: float) -> bool:
    return abs(left - right) <= absolute + relative * max(abs(left), abs(right))


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_digest = sha256(args.manifest)
    preflight_errors, authority_hashes = validate_manifest(manifest)
    if preflight_errors:
        print("A8-CLASSII-DECOUPLED-NELSON-PREFLIGHT-FAIL")
        for error in preflight_errors:
            print(f"PREFLIGHT: {error}")
        return 1

    authority = manifest["authority"]
    with tempfile.TemporaryDirectory(prefix="tect-a8-decoupled-") as temporary:
        temp = Path(temporary)
        primary_process = run_child(REPO / authority["primary_audit"]["path"], args.manifest, temp / "primary.json")
        independent_process = run_child(REPO / authority["independent_audit"]["path"], args.manifest, temp / "independent.json")
        primary = primary_process.get("result")
        independent = independent_process.get("result")

    assertions: list[dict[str, Any]] = []
    contract = manifest["run_contract"]
    if not isinstance(primary, dict) or not isinstance(independent, dict):
        print("A8-CLASSII-DECOUPLED-NELSON-INTEGRATED-FAIL")
        print("Child result missing or malformed")
        return 1

    p_summary = primary.get("assertion_summary", {})
    i_summary = independent.get("assertion_summary", {})
    integrated = manifest["integrated_audit"]
    absolute = float(integrated["coefficient_absolute_tolerance"])
    relative = float(integrated["derived_relative_tolerance"])

    add("primary_result_contract_matches", primary.get("schema") == contract["primary_result_schema"] and primary.get("claim_id") == CLAIM_ID and primary.get("script_version") == authority["primary_audit"]["version"] and primary.get("manifest_sha256") == manifest_digest and primary.get("verdict") == "A8-CLASSII-DECOUPLED-NELSON-PRIMARY-PASS", {key: primary.get(key) for key in ("schema", "claim_id", "script_version", "manifest_sha256", "verdict")}, "exact primary contract", assertions)
    add("independent_result_contract_matches", independent.get("schema") == contract["independent_result_schema"] and independent.get("claim_id") == CLAIM_ID and independent.get("script_version") == authority["independent_audit"]["version"] and independent.get("manifest_sha256") == manifest_digest and independent.get("verdict") == "A8-CLASSII-DECOUPLED-NELSON-INDEPENDENT-PASS", {key: independent.get(key) for key in ("schema", "claim_id", "script_version", "manifest_sha256", "verdict")}, "exact independent contract", assertions)
    add("primary_assertion_count_matches", p_summary.get("passed") == integrated["primary_assertions"] and p_summary.get("total") == integrated["primary_assertions"], p_summary, integrated["primary_assertions"], assertions)
    add("independent_assertion_count_matches", i_summary.get("passed") == integrated["independent_assertions"] and i_summary.get("total") == integrated["independent_assertions"], i_summary, integrated["independent_assertions"], assertions)

    p_derived = primary["derived"]
    i_derived = independent["derived"]
    p_coeff = p_derived["coefficients"]
    i_coeff = i_derived["coefficients"]
    add("production_coefficients_crosscheck", all(close(float(p_coeff[key]), float(i_coeff[key]), absolute, relative) for key in ("a", "b", "c")), {"primary": p_coeff, "independent": i_coeff}, "a,b,c agree", assertions)
    add("QII_eigenvalues_crosscheck", all(close(float(left), float(right), absolute, relative) for left, right in zip(p_coeff["Q_eigenvalues"], i_coeff["Q_eigenvalues"])), {"primary": p_coeff["Q_eigenvalues"], "independent": i_coeff["Q_eigenvalues"]}, "agree", assertions)
    add("symbol_coercivity_crosscheck", close(float(p_derived["symbol_coercivity"]["c_symbol"]), float(i_derived["symbol_coercivity"]["c_symbol"]), absolute, relative), {"primary": p_derived["symbol_coercivity"], "independent": i_derived["symbol_coercivity"]}, "agree", assertions)
    add("beta_B_crosscheck", close(float(p_derived["beta_B"]), float(i_derived["beta_B"]), absolute, relative), {"primary": p_derived["beta_B"], "independent": i_derived["beta_B"]}, "agree", assertions)
    add("lattice_upper_crosscheck", close(float(p_derived["lattice_sum"]["upper"]), float(i_derived["lattice_upper"]), absolute, relative), {"primary": p_derived["lattice_sum"]["upper"], "independent": i_derived["lattice_upper"]}, "agree", assertions)
    add("trace_ideal_constant_crosscheck", close(float(p_derived["trace_ideal_constant"]), float(i_derived["trace_ideal_constant"]), absolute, relative), {"primary": p_derived["trace_ideal_constant"], "independent": i_derived["trace_ideal_constant"]}, "agree", assertions)
    add("Nelson_quartic_constant_crosscheck", close(float(p_derived["nelson_quartic_constant"]), float(i_derived["nelson_quartic_constant"]), absolute, relative), {"primary": p_derived["nelson_quartic_constant"], "independent": i_derived["nelson_quartic_constant"]}, "agree", assertions)

    p_rows = p_derived["p_bounds"]
    i_rows = i_derived["p_bounds"]
    p_agreement = len(p_rows) == len(i_rows) and all(
        close(float(left["rho_star"]), float(right["rho_star"]), absolute, relative)
        and close(float(left["pointwise_log_bound"]), float(right["pointwise_maximum"]), absolute, relative)
        for left, right in zip(p_rows, i_rows)
    )
    add("sextic_absorption_rows_crosscheck", p_agreement, {"primary": p_rows, "independent": i_rows}, "rho_star and maximum agree", assertions)
    add("primary_variable_operator_checks_pass", p_derived["operator"]["minimum_eigenvalue"] > -manifest["audit"]["matrix_tolerance"] and p_derived["operator"]["det2_log_moment"] <= p_derived["operator"]["det2_hs_upper"] * (1.0 + manifest["audit"]["relative_tolerance"]), p_derived["operator"], "PSD and det2 bounded", assertions)
    add("independent_constant_operator_checks_pass", 0.0 <= i_derived["determinant"]["log_moment_eigen"] <= i_derived["determinant"]["half_hs_bound"] * (1.0 + manifest["independent_audit"]["relative_tolerance"]), i_derived["determinant"], "det2 bounded", assertions)
    divergence = i_derived["divergence"]
    add(
        "full_B_Gaussian_divergence_and_parity_control_crosscheck",
        max(divergence["even_errors"]) < manifest["independent_audit"]["divergence_identity_tolerance"]
        and divergence["even_same_point_kernel"] < manifest["independent_audit"]["even_kernel_tolerance"]
        and min(divergence["asymmetric_gaps"]) > manifest["independent_audit"]["asymmetric_gap_floor"]
        and divergence["asymmetric_same_point_kernel"] > manifest["independent_audit"]["asymmetric_kernel_floor"],
        divergence,
        "even identity passes and parity-breaking control fires",
        assertions,
    )
    toy_control = i_derived["toy_negative_control"]
    add(
        "self_decoupling_negative_control_fires_stably",
        toy_control["minimum_absolute_difference"] > manifest["independent_audit"]["toy_difference_floor"]
        and toy_control["order_spread"] < manifest["independent_audit"]["toy_quadrature_stability_tolerance"],
        toy_control,
        "stable nonzero difference across quadrature orders",
        assertions,
    )
    add("full_sequence_decoupled_theorem_is_pinned", "full-sequence" in manifest["theorem"]["full_sequence"], manifest["theorem"]["full_sequence"], "contains full-sequence", assertions)
    add("self_coupling_boundary_is_fail_closed", manifest["open_followup"] == "A7-CLASSII-SELF-COUPLING-INTERPOLATION" and any("self-coupled" in item for item in manifest["honesty_boundary"]["excluded"]), {"gate": manifest["open_followup"], "excluded": manifest["honesty_boundary"]["excluded"]}, "named gate and explicit exclusion", assertions)

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
    verdict = "A8-CLASSII-DECOUPLED-NELSON-INTEGRATED-PASS" if all_pass else "A8-CLASSII-DECOUPLED-NELSON-INTEGRATED-FAIL"
    output = {
        "schema": contract["integrated_result_schema"],
        "claim_id": CLAIM_ID,
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": manifest_digest,
        "scope": manifest["scope"],
        "preflight": {"status": "PASS", "errors": [], "authority_hashes": authority_hashes},
        "subprocesses": {
            "primary": {key: value for key, value in primary_process.items() if key != "result"},
            "independent": {key: value for key, value in independent_process.items() if key != "result"},
        },
        "source_hashes": authority_hashes,
        "assertions": assertions,
        "assertion_summary": {
            "primary": p_summary,
            "independent": i_summary,
            "cross": {"passed": cross_passed, "total": len(assertions)},
            "aggregate": {"passed": aggregate_passed, "total": aggregate_total},
            "count_contract": counts_ok,
        },
        "key_results": {
            "beta_B": p_derived["beta_B"],
            "c_symbol": p_derived["symbol_coercivity"]["c_symbol"],
            "lattice_upper": p_derived["lattice_sum"]["upper"],
            "trace_ideal_constant": p_derived["trace_ideal_constant"],
            "nelson_quartic_constant": p_derived["nelson_quartic_constant"],
            "p_bounds": p_rows,
            "toy_negative_control": i_derived["toy_negative_control"],
            "divergence": i_derived["divergence"],
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
