#!/usr/bin/env python3
"""Fail-closed integrated verifier for the A9 commutator no-go package."""

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
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-21"
__claims__ = ["A9-CLASSII-SMART-PATH-CANCELLATION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM_ID = __claims__[0]
DEFAULT_MANIFEST = REPO / "claims" / CLAIM_ID / "tilted_commutator_nogo_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM_ID / "runs" / "2026-07-21-integrated-tilted-commutator-nogo" / "result.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_AUTHORITY = {
    "production_functional_manifest": (
        "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/"
        "production_functional_manifest.json"
    ),
    "a7_manifest": (
        "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/"
        "classii_renormalised_energy_manifest.json"
    ),
    "historical_a9_manifest": (
        "claims/A9-CLASSII-SMART-PATH-CANCELLATION/"
        "classii_smart_path_manifest.json"
    ),
    "primary_audit": "codes/foundations/a9_tilted_commutator_nogo.py",
    "independent_audit": "codes/foundations/a9_tilted_commutator_nogo_independent.py",
    "one_command_verifier": "codes/foundations/a9_tilted_commutator_nogo_verify.py",
    "proof_note": (
        "claims/A9-CLASSII-SMART-PATH-CANCELLATION/notes/"
        "classii-tilted-commutator-nogo-260721-v1.0.tex.txt"
    ),
    "proof_pdf": (
        "claims/A9-CLASSII-SMART-PATH-CANCELLATION/notes/"
        "classii-tilted-commutator-nogo-260721-v1.0.pdf"
    ),
}
SCRIPT_AUTHORITIES = {
    "primary_audit", "independent_audit", "one_command_verifier"
}


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
                if (
                    isinstance(target, ast.Name)
                    and target.id == "__version__"
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    return node.value.value
    return None


def add(name: str, passed: bool, actual: Any, expected: Any,
        rows: list[dict[str, Any]]) -> None:
    rows.append({
        "name": name,
        "status": "PASS" if bool(passed) else "FAIL",
        "actual": actual,
        "expected": expected,
    })


def validate_manifest(
    manifest: dict[str, Any],
) -> tuple[list[str], dict[str, dict[str, str]]]:
    errors: list[str] = []
    hashes: dict[str, dict[str, str]] = {}
    if manifest.get("schema") != "tect/a9-tilted-commutator-nogo/1.0":
        errors.append("manifest schema mismatch")
    if manifest.get("package_version") != "1.0.0":
        errors.append("package version mismatch")
    if manifest.get("claim_id") != CLAIM_ID:
        errors.append("claim id mismatch")
    if manifest.get("status") != "FORMER-GATE-FALSIFIED@INFINITESIMAL-COMMUTATOR-BOUND":
        errors.append("negative-result status mismatch")
    if manifest.get("falsified_gate") != "A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND":
        errors.append("falsified gate mismatch")
    if manifest.get("corrected_gate") != "A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND":
        errors.append("corrected gate mismatch")

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
        hashes[name] = {
            "path": expected_path,
            "expected": expected_hash,
            "actual": actual_hash,
        }
        if actual_hash != expected_hash:
            errors.append(f"{name}: authority hash mismatch")
        if name in SCRIPT_AUTHORITIES and literal_version(path) != record.get("version"):
            errors.append(f"{name}: version mismatch")

    schemas = {
        "production_functional_manifest": "tect/a1-production-functional-realisation/1.0",
        "a7_manifest": "tect/a7-classii-renormalised-energy/1.1",
        "historical_a9_manifest": "tect/a9-classii-smart-path-cancellation/1.0",
    }
    for name, expected_schema in schemas.items():
        try:
            upstream = json.loads(
                (REPO / EXPECTED_AUTHORITY[name]).read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            errors.append(f"{name}: invalid upstream JSON")
            continue
        if (
            upstream.get("schema") != expected_schema
            or authority[name].get("schema") != expected_schema
        ):
            errors.append(f"{name}: schema mismatch")

    pdf = authority.get("proof_pdf", {})
    if not isinstance(pdf.get("pages"), int) or pdf.get("pages", 0) <= 0:
        errors.append("proof PDF page count invalid")
    if (
        pdf.get("form_check") != "PASS"
        or pdf.get("overfull_hbox") != 0
        or pdf.get("visual_qa") != "PASS"
    ):
        errors.append("proof PDF QA contract not closed")

    audit = manifest.get("audit", {})
    independent = manifest.get("independent_audit", {})
    if not 0.0 < float(audit.get("epsilon", 0.0)) < 1.0 / 3.0:
        errors.append("primary witness must stay uniformly away from zero")
    if audit.get("phase_grid", 0) < 64:
        errors.append("primary phase grid too small")
    if independent.get("phase_grid", 0) < 128:
        errors.append("independent phase grid too small")
    if (
        audit.get("eta_test") != independent.get("eta_test")
        or audit.get("epsilon") != independent.get("epsilon")
    ):
        errors.append("witness mismatch across routes")
    if audit.get("dyadic_projector") != "P_prev=1_[abs(q)<K], P_top=1_[abs(q)<2K]":
        errors.append("sharp radial dyadic projector is not pinned")
    if audit.get("covariance_contraction_power") != 2:
        errors.append("covariance contraction power mismatch")
    expected_power_inputs = {
        "spatial_dimension": 3,
        "covariance_symbol_order": 4,
        "witness_amplitude_power": 1,
        "gradient_order": 1,
        "biharmonic_order": 2,
        "mass_degree": 2,
        "quartic_degree": 4,
        "sextic_degree": 6,
    }
    if audit.get("power_counting_inputs") != expected_power_inputs:
        errors.append("analytic power-counting inputs mismatch")

    necessary_budget = manifest.get("necessary_budget", {})
    tradeoff = necessary_budget.get("retained_frozen_tradeoff", "")
    budget_status = necessary_budget.get("status", "")
    if "[(c_C-theta*c_F)_+]^2/(4*c_H*c_6)" not in tradeoff:
        errors.append("theta-budget tradeoff is not pinned")
    if "not an absolute lower bound" not in tradeoff:
        errors.append("theta qualification is missing")
    if "all-field relative bound is OPEN" not in budget_status:
        errors.append("corrected-gate open-status firewall is missing")

    integrated = manifest.get("integrated_audit", {})
    expected_counts = {
        "primary_assertions": 24,
        "independent_assertions": 17,
        "cross_assertions": 15,
        "expected_aggregate_assertions": 56,
    }
    for key, expected in expected_counts.items():
        if integrated.get(key) != expected:
            errors.append(f"{key} mismatch")
    contract = manifest.get("run_contract", {})
    expected_schemas = {
        "primary_result_schema":
            "tect/a9-tilted-commutator-nogo-primary-result/1.0",
        "independent_result_schema":
            "tect/a9-tilted-commutator-nogo-independent-result/1.0",
        "integrated_result_schema":
            "tect/a9-tilted-commutator-nogo-integrated-result/1.0",
    }
    for key, expected in expected_schemas.items():
        if contract.get(key) != expected:
            errors.append(f"{key} mismatch")

    boundary = manifest.get("honesty_boundary", [])
    if not any("does not falsify the A9 T5 theorem" in item for item in boundary):
        errors.append("A9 scope firewall missing")
    if not any("does not prove or disprove the full A7 Nelson bound" in item for item in boundary):
        errors.append("A7 Nelson scope firewall missing")
    return errors, hashes


def run_child(script: Path, manifest: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, str(script), "--manifest", str(manifest),
         "--output", str(output)],
        cwd=REPO, text=True, capture_output=True, check=False,
    )
    record: dict[str, Any] = {
        "command": [sys.executable, str(script), "--manifest", str(manifest),
                    "--output", str(output)],
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }
    try:
        record["result"] = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record["result"] = None
        record["load_error"] = str(exc)
    return record


def relative_error(left: float, right: float) -> float:
    return abs(left - right) / max(1.0, abs(left), abs(right))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_hash = sha256(args.manifest)
    preflight_errors, authority_hashes = validate_manifest(manifest)
    if preflight_errors:
        print("A9-TILTED-COMMUTATOR-NOGO-PREFLIGHT-FAIL")
        for error in preflight_errors:
            print(f"PREFLIGHT: {error}")
        return 1

    authority = manifest["authority"]
    with tempfile.TemporaryDirectory(prefix="tect-a9-commutator-nogo-") as td:
        root = Path(td)
        primary_process = run_child(
            REPO / authority["primary_audit"]["path"],
            args.manifest, root / "primary.json"
        )
        independent_process = run_child(
            REPO / authority["independent_audit"]["path"],
            args.manifest, root / "independent.json"
        )
        primary = primary_process.get("result")
        independent = independent_process.get("result")
    if not isinstance(primary, dict) or not isinstance(independent, dict):
        print("A9-TILTED-COMMUTATOR-NOGO-INTEGRATED-FAIL")
        print("Child result missing or malformed")
        return 1

    assertions: list[dict[str, Any]] = []
    integrated = manifest["integrated_audit"]
    p_summary = primary.get("assertion_summary", {})
    i_summary = independent.get("assertion_summary", {})
    add("primary_process_exits_zero", primary_process["returncode"] == 0,
        primary_process["returncode"], 0, assertions)
    add("independent_process_exits_zero",
        independent_process["returncode"] == 0,
        independent_process["returncode"], 0, assertions)
    contract = manifest["run_contract"]
    add("primary_result_contract_is_exact",
        primary.get("schema") == contract["primary_result_schema"]
        and primary.get("verdict")
        == "A9-TILTED-COMMUTATOR-NOGO-PRIMARY-PASS"
        and p_summary == {
            "passed": integrated["primary_assertions"],
            "total": integrated["primary_assertions"],
        },
        {"schema": primary.get("schema"), "verdict": primary.get("verdict"),
         "summary": p_summary}, "pinned primary result contract", assertions)
    add("independent_result_contract_is_exact",
        independent.get("schema") == contract["independent_result_schema"]
        and independent.get("verdict")
        == "A9-TILTED-COMMUTATOR-NOGO-INDEPENDENT-PASS"
        and i_summary == {
            "passed": integrated["independent_assertions"],
            "total": integrated["independent_assertions"],
        },
        {"schema": independent.get("schema"),
         "verdict": independent.get("verdict"), "summary": i_summary},
        "pinned independent result contract", assertions)
    add("children_bind_the_same_manifest",
        primary.get("manifest_sha256") == manifest_hash
        and independent.get("manifest_sha256") == manifest_hash,
        [primary.get("manifest_sha256"), independent.get("manifest_sha256")],
        manifest_hash, assertions)
    add("independent_route_declares_no_primary_import",
        independent.get("environment", {}).get("imports_primary") is False,
        independent.get("environment", {}).get("imports_primary"),
        False, assertions)

    p_derived = primary["derived"]
    i_derived = independent["derived"]
    tolerance = float(integrated["numeric_relative_tolerance"])
    comparisons = [
        ("sextic_moment", p_derived["m6"], i_derived["averages"]["m6"]),
        ("commutator_coefficient", -p_derived["c_commutator"],
         i_derived["expected_normalized_commutator"]),
        ("entropy_coefficient", p_derived["c_entropy"],
         i_derived["entropy_coefficient"]),
        ("optimal_amplitude", p_derived["t_optimal"],
         i_derived["t_optimal"]),
        ("eta_threshold", p_derived["eta_min"], i_derived["eta_min"]),
        ("violation_margin", p_derived["violation_margin_per_volume_K6"],
         i_derived["violation_margin_per_volume_K6"]),
        ("frozen_compensation_ratio", p_derived["theta_ray"],
         i_derived["theta_ray"]),
    ]
    for key, left, right in comparisons:
        error = relative_error(float(left), float(right))
        add(f"cross_route_{key}_agrees", error < tolerance,
            {"left": left, "right": right, "relative_error": error},
            tolerance, assertions)

    add("negative_result_has_strict_test_eta_margin",
        p_derived["eta_test"] < p_derived["eta_min"]
        and p_derived["violation_margin_per_volume_K6"] > 0.0,
        {
            "eta_test": p_derived["eta_test"],
            "eta_min": p_derived["eta_min"],
            "margin": p_derived["violation_margin_per_volume_K6"],
        },
        "strict violation", assertions)
    budget = manifest["necessary_budget"]
    add("corrected_gate_and_theta_budget_are_scope_safe",
        "covariance-normal frozen shell energy"
        in manifest["corrected_statement"]
        and "not an absolute lower bound"
        in budget["retained_frozen_tradeoff"]
        and "all-field relative bound is OPEN" in budget["status"],
        {
            "statement": manifest["corrected_statement"],
            "tradeoff": budget["retained_frozen_tradeoff"],
            "status": budget["status"],
        },
        "retained energy, qualified theta tradeoff, and OPEN firewall",
        assertions)

    failures = [row for row in assertions if row["status"] != "PASS"]
    aggregate = (
        int(p_summary.get("passed", 0))
        + int(i_summary.get("passed", 0))
        + len(assertions) - len(failures)
    )
    expected_aggregate = integrated["expected_aggregate_assertions"]
    verdict = (
        "A9-TILTED-COMMUTATOR-NOGO-INTEGRATED-PASS"
        if not failures and aggregate == expected_aggregate
        else "A9-TILTED-COMMUTATOR-NOGO-INTEGRATED-FAIL"
    )
    output = {
        "schema": "tect/a9-tilted-commutator-nogo-integrated-result/1.0",
        "claim_id": CLAIM_ID,
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": manifest_hash,
        "authority_hashes": authority_hashes,
        "child_processes": {
            "primary": primary_process,
            "independent": independent_process,
        },
        "cross_assertions": assertions,
        "assertion_summary": {
            "primary_passed": p_summary.get("passed"),
            "independent_passed": i_summary.get("passed"),
            "cross_passed": len(assertions) - len(failures),
            "aggregate_passed": aggregate,
            "aggregate_total": expected_aggregate,
        },
        "derived": {
            "eta_min": p_derived["eta_min"],
            "eta_test": p_derived["eta_test"],
            "violation_margin_per_volume_K6":
                p_derived["violation_margin_per_volume_K6"],
            "theta_ray": p_derived["theta_ray"],
            "corrected_gate": manifest["corrected_gate"],
        },
        "failures": failures,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "git_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=REPO, text=True,
                stderr=subprocess.DEVNULL
            ).strip(),
            "deterministic": True,
        },
        "not_closed_here": manifest["not_closed_here"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: primary ({p_summary.get('passed')}/{p_summary.get('total')})")
    print(f"PASS: independent ({i_summary.get('passed')}/{i_summary.get('total')})")
    print(f"ASSERTS: {aggregate}/{expected_aggregate}")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if verdict.endswith("-PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
