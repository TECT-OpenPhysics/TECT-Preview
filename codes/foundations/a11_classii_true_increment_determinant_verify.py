#!/usr/bin/env python3
"""Fail-closed one-command verifier for the A11 true-increment package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
CLAIM = "A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION"
DEFAULT_MANIFEST = ROOT / "claims" / CLAIM / "classii_true_increment_determinant_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / CLAIM / "runs" / "2026-07-21-integrated-true-increment" / "result.json"
HEX = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_AUTHORITY = {
    "production_functional_manifest": "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "a6_uv_manifest": "claims/A6-CLASSII-UV-POWER-COUNTING/classii_uv_power_counting_manifest.json",
    "a7_composite_manifest": "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
    "a9_smart_path_manifest": "claims/A9-CLASSII-SMART-PATH-CANCELLATION/classii_smart_path_manifest.json",
    "a10_structural_manifest": "claims/A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION/classii_relative_structural_reduction_manifest.json",
    "primary_audit": "codes/foundations/a11_classii_true_increment_determinant.py",
    "independent_audit": "codes/foundations/a11_classii_true_increment_determinant_independent.py",
    "one_command_verifier": "codes/foundations/a11_classii_true_increment_determinant_verify.py",
    "proof_note": "claims/A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION/notes/classii-true-increment-determinant-260721-v1.0.tex.txt",
    "proof_pdf": "claims/A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION/notes/classii-true-increment-determinant-260721-v1.0.pdf",
}
SCRIPT_KEYS = {"primary_audit", "independent_audit", "one_command_verifier"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def script_version(path: Path) -> str | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__" and isinstance(node.value.value, str):
                    return node.value.value
    return None


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def relative(left: float, right: float) -> float:
    return abs(left - right) / max(abs(left), abs(right), 1e-30)


def validate_manifest(manifest: dict[str, Any]) -> tuple[list[str], dict[str, dict[str, str]]]:
    errors: list[str] = []
    hashes: dict[str, dict[str, str]] = {}
    if manifest.get("schema") != "tect/a11-classii-true-increment-determinant/1.0":
        errors.append("manifest schema mismatch")
    if manifest.get("package_version") != "1.0.0":
        errors.append("package version mismatch")
    if manifest.get("claim_id") != CLAIM:
        errors.append("claim id mismatch")
    if manifest.get("status") != "T4 PROVED-STRUCTURAL-REDUCTION@FIXED-FLOOR-FINITE-CUTOFF":
        errors.append("status mismatch")
    authority = manifest.get("authority", {})
    if set(authority) != set(EXPECTED_AUTHORITY):
        errors.append("authority set mismatch")
        return errors, hashes
    for key, expected_path in EXPECTED_AUTHORITY.items():
        item = authority.get(key, {})
        if item.get("path") != expected_path:
            errors.append(f"{key}: path mismatch")
            continue
        expected_hash = item.get("sha256")
        if not isinstance(expected_hash, str) or not HEX.fullmatch(expected_hash):
            errors.append(f"{key}: invalid SHA-256")
            continue
        path = ROOT / expected_path
        if not path.is_file():
            errors.append(f"{key}: missing file")
            continue
        actual_hash = sha256(path)
        hashes[key] = {"path": expected_path, "expected": expected_hash, "actual": actual_hash}
        if expected_hash != actual_hash:
            errors.append(f"{key}: hash mismatch")
        if key in SCRIPT_KEYS and script_version(path) != item.get("version"):
            errors.append(f"{key}: version mismatch")
    if manifest.get("route_disposition", {}).get("past_energy_upper_form") != "REFUTED":
        errors.append("past-energy route not refuted")
    if manifest.get("route_disposition", {}).get("true_increment") != "ACTIVE":
        errors.append("true-increment route not active")
    expected_open = ["A11-CLASSII-ADAPTED-SOURCE-SQUARE-BOUND", "A11-CLASSII-TRUE-INCREMENT-STABILISED-LOG-LAPLACE"]
    if manifest.get("open_followups") != expected_open:
        errors.append("open gate order mismatch")
    true_increment = manifest.get("true_increment", {})
    if true_increment.get("relative_variable") != "theta*I_j+C_j" or true_increment.get("legacy_relative_variable") != "theta*Q_j^fr+C_j":
        errors.append("relative-variable firewall mismatch")
    pdf = authority.get("proof_pdf", {})
    if pdf.get("form_check") != "PASS" or pdf.get("visual_qa") != "PASS" or pdf.get("overfull_hbox") != 0 or not isinstance(pdf.get("pages"), int) or pdf.get("pages", 0) <= 0:
        errors.append("proof PDF QA contract open")
    expected_counts = {"primary_assertions": 24, "independent_assertions": 18, "cross_assertions": 16, "expected_aggregate_assertions": 58}
    if manifest.get("integrated_audit") != {**expected_counts, "numeric_relative_tolerance": 0.08}:
        errors.append("integrated audit contract mismatch")
    return errors, hashes


def run_child(script: Path, manifest: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run([sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)], cwd=ROOT, text=True, capture_output=True, check=False)
    try:
        result = json.loads(output.read_text(encoding="utf-8"))
        load_error = None
    except (OSError, json.JSONDecodeError) as exc:
        result = None
        load_error = str(exc)
    return {"returncode": process.returncode, "stdout": process.stdout, "stderr": process.stderr, "result": result, "load_error": load_error}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    manifest = json.loads(options.manifest.read_text(encoding="utf-8"))
    errors, hashes = validate_manifest(manifest)
    rows: list[dict[str, Any]] = []
    add(rows, "manifest_preflight", not errors, errors, [])

    run_paths = manifest["run_contract"]
    primary_output = ROOT / run_paths["primary_result_path"]
    independent_output = ROOT / run_paths["independent_result_path"]
    primary_run = run_child(ROOT / EXPECTED_AUTHORITY["primary_audit"], options.manifest, primary_output)
    independent_run = run_child(ROOT / EXPECTED_AUTHORITY["independent_audit"], options.manifest, independent_output)
    primary = primary_run.get("result") or {}
    independent = independent_run.get("result") or {}
    integrated = manifest["integrated_audit"]
    tolerance = float(integrated["numeric_relative_tolerance"])

    add(rows, "primary_exit_zero", primary_run["returncode"] == 0, primary_run["returncode"], 0)
    add(rows, "independent_exit_zero", independent_run["returncode"] == 0, independent_run["returncode"], 0)
    add(rows, "primary_contract", primary.get("schema") == run_paths["primary_result_schema"] and primary.get("verdict") == "A11-CLASSII-TRUE-INCREMENT-PRIMARY-PASS" and primary.get("assertion_count") == integrated["primary_assertions"], {"schema": primary.get("schema"), "verdict": primary.get("verdict"), "count": primary.get("assertion_count")}, {"schema": run_paths["primary_result_schema"], "count": integrated["primary_assertions"]})
    add(rows, "independent_contract", independent.get("schema") == run_paths["independent_result_schema"] and independent.get("verdict") == "A11-CLASSII-TRUE-INCREMENT-INDEPENDENT-PASS" and independent.get("assertion_count") == integrated["independent_assertions"], {"schema": independent.get("schema"), "verdict": independent.get("verdict"), "count": independent.get("assertion_count")}, {"schema": run_paths["independent_result_schema"], "count": integrated["independent_assertions"]})

    p_derived = primary.get("derived", {})
    i_derived = independent.get("derived", {})
    add(rows, "cross_kappa", relative(float(p_derived.get("predicted_classii_energy_density_slope", float("nan"))), float(i_derived.get("predicted_classii_energy_density_slope", float("nan")))) <= tolerance, {"primary": p_derived.get("predicted_classii_energy_density_slope"), "independent": i_derived.get("predicted_classii_energy_density_slope")}, f"relative <= {tolerance}")
    add(rows, "cross_terminal_slope", relative(float(p_derived.get("terminal_energy_slope", float("nan"))), float(i_derived.get("terminal_energy_slope", float("nan")))) <= tolerance, {"primary": p_derived.get("terminal_energy_slope"), "independent": i_derived.get("terminal_energy_slope")}, f"relative <= {tolerance}")
    add(rows, "cross_dyadic_ratio", relative(float(p_derived.get("dyadic_past_energy_ratio", float("nan"))), float(i_derived.get("dyadic_past_energy_ratio", float("nan")))) <= tolerance, {"primary": p_derived.get("dyadic_past_energy_ratio"), "independent": i_derived.get("dyadic_past_energy_ratio")}, f"relative <= {tolerance}")
    add(rows, "cross_no_go_sign", float(p_derived.get("dyadic_past_energy_ratio", 0.0)) > 0.0 and float(i_derived.get("dyadic_past_energy_ratio", 0.0)) > 0.0, {"primary": p_derived.get("dyadic_past_energy_ratio"), "independent": i_derived.get("dyadic_past_energy_ratio")}, "both positive")
    add(rows, "cross_determinant_formula", float(p_derived.get("determinant", {}).get("quadrature_error", 1.0)) < 1e-10 and float(i_derived.get("determinant", {}).get("error", 1.0)) < 1e-10, {"primary": p_derived.get("determinant", {}).get("quadrature_error"), "independent": i_derived.get("determinant", {}).get("error")}, "both <1e-10")
    add(rows, "cross_positive_source", float(p_derived.get("determinant", {}).get("source_part", 0.0)) > 0.0 and float(i_derived.get("determinant", {}).get("source", 0.0)) > 0.0, {"primary": p_derived.get("determinant", {}).get("source_part"), "independent": i_derived.get("determinant", {}).get("source")}, "both positive")
    add(rows, "cross_true_increment_telescope", float(p_derived.get("spectral_telescope", {}).get("true_increment_identity_error", 1.0)) < 1e-12 and float(i_derived.get("algebra", {}).get("true_error", 1.0)) < 1e-12, {"primary": p_derived.get("spectral_telescope", {}).get("true_increment_identity_error"), "independent": i_derived.get("algebra", {}).get("true_error")}, "both <1e-12")

    independent_source = (ROOT / EXPECTED_AUTHORITY["independent_audit"]).read_text(encoding="utf-8")
    forbidden = ("import a11_classii_true_increment_determinant", "from a11_classii_true_increment_determinant", "import a6_classii_uv_power_counting", "import a10_classii_relative_structural_reduction")
    add(rows, "independent_route_nonimporting", not any(token in independent_source for token in forbidden), [token for token in forbidden if token in independent_source], [])
    proof_text = (ROOT / EXPECTED_AUTHORITY["proof_note"]).read_text(encoding="utf-8") if (ROOT / EXPECTED_AUTHORITY["proof_note"]).is_file() else ""
    required_tokens = ("F-2026-07-21-A10-PAST-ENERGY-UPPER-FORM", "I_j", "det{}_2", "A11-CLASSII-ADAPTED-SOURCE-SQUARE-BOUND", "theta I_j", "does not prove the source-square bound")
    add(rows, "proof_note_boundary_tokens", all(token in proof_text for token in required_tokens), [token for token in required_tokens if token not in proof_text], [])
    pdf = manifest["authority"]["proof_pdf"]
    add(rows, "proof_pdf_QA_closed", pdf.get("pages", 0) > 0 and pdf.get("form_check") == "PASS" and pdf.get("overfull_hbox") == 0 and pdf.get("visual_qa") == "PASS", pdf, "closed PDF QA")
    add(rows, "route_firewall", manifest["route_disposition"] == {"past_energy_upper_form": "REFUTED", "true_increment": "ACTIVE"}, manifest["route_disposition"], "upper form refuted; true increment active")

    cross_count = len(rows)
    aggregate = int(primary.get("assertion_count", 0)) + int(independent.get("assertion_count", 0)) + cross_count
    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    if cross_count != integrated["cross_assertions"]:
        failures.append("cross_assertion_count")
    if aggregate != integrated["expected_aggregate_assertions"]:
        failures.append("aggregate_assertion_count")
    payload = {
        "schema": run_paths["integrated_result_schema"],
        "claim_id": CLAIM,
        "version": __version__,
        "verdict": "A11-CLASSII-TRUE-INCREMENT-INTEGRATED-PASS" if not failures else "FAIL",
        "git_commit": commit(),
        "platform": platform.platform(),
        "authority_hashes": hashes,
        "child_runs": {"primary": {key: primary_run[key] for key in ("returncode", "stdout", "stderr", "load_error")}, "independent": {key: independent_run[key] for key in ("returncode", "stdout", "stderr", "load_error")}},
        "assertions": rows,
        "cross_assertion_count": cross_count,
        "aggregate_assertion_count": aggregate,
        "failures": failures,
        "proof_order": manifest["proof_order"],
        "open_followups": manifest["open_followups"],
    }
    atomic_json(options.output, payload)
    print(f"PASS: primary ({primary.get('assertion_count', 0)}/{integrated['primary_assertions']})" if primary_run["returncode"] == 0 else "FAIL: primary")
    print(f"PASS: independent ({independent.get('assertion_count', 0)}/{integrated['independent_assertions']})" if independent_run["returncode"] == 0 else "FAIL: independent")
    print(f"ASSERTS: {aggregate}/{integrated['expected_aggregate_assertions']}")
    print(payload["verdict"])
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
