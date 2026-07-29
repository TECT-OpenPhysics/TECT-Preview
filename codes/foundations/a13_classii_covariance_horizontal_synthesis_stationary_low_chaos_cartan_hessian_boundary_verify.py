#!/usr/bin/env python3
"""Integrated fail-closed verifier for the scoped R-120 A13 result."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-29"
__version_issued__ = "2026-07-29"

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-COVARIANCE-HORIZONTAL-SYNTHESIS-STATIONARY-LOW-CHAOS-CARTAN-HESSIAN-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian-boundary-260729-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian-boundary-260729-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-29-primary-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-29-independent-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-29-integrated-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian/result.json"

PRIMARY_SCHEMA = "tect/a13-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian-primary/1.0"
INDEPENDENT_SCHEMA = "tect/a13-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian-independent/1.0"
INTEGRATED_SCHEMA = "tect/a13-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian-integrated/1.0"
PRIMARY_ASSERTIONS = 68
INDEPENDENT_ASSERTIONS = 59

AUTHORITY_PATHS = {
    "a1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "a8": REPO / "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/classii_decoupled_nelson_manifest.json",
    "r063": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r068": CLAIM_DIR / "classii_tip_safe_grouped_harvest_carleson_reduction_manifest.json",
    "r082": CLAIM_DIR / "classii_stopped_current_far_complete_current_near_reduction_manifest.json",
    "r089": CLAIM_DIR / "classii_progressive_covariance_compression_rational_mean_spectral_boundary_manifest.json",
    "r092": CLAIM_DIR / "classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
    "r102": CLAIM_DIR / "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
    "r104": CLAIM_DIR / "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "r116": CLAIM_DIR / "classii_one_fresh_root_owner_quotient_wick_nullcone_boundary_manifest.json",
    "r118": CLAIM_DIR / "classii_revisit_quotient_operator_carleson_signed_score_boundary_manifest.json",
    "r119": CLAIM_DIR / "classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_manifest.json",
}

NOTE_TOKENS = (
    "R-120 conclusion",
    "A13-CLASSII-COVARIANCE-HORIZONTAL-SYNTHESIS-STATIONARY-",
    "Theorem 3.1 (lossless quotient and physical $H^2$ control)",
    "Theorem 4.1 (two-derivative multiplier extension)",
    "Theorem 5.2 (stationary six-row A1 raw-current pass)",
    "Theorem 7.1 (current-Hessian identity)",
    "Theorem 8.1 (exact rational zeroth-order Hessian)",
    "companion as observed",
    "68/68 assertions",
    "59/59",
    "Sector-A closure remain open",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def payload_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": INTEGRATED_SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "children": {
                "primary": {"path": relative(PRIMARY_RESULT), "sha256": digest(PRIMARY_RESULT)},
                "independent": {"path": relative(INDEPENDENT_RESULT), "sha256": digest(INDEPENDENT_RESULT)},
            },
            "no_overclaim": (
                "Integrated PASS certifies R-120's scoped analytic lemmas and exact finite fixtures: "
                "covariance-horizontal H2/L6 synthesis, the conditional variable-multiplier theorem, "
                "stationary six-row raw-current cancellation, and linear/rational Hessian algebra. "
                "It does not certify an owner-complete adapted packet, D0/D1, an observed +40/729 "
                "companion, the global one-use inequality, Nelson, or Sector A closure."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r120-child-") as directory:
        output = Path(directory) / "result.json"
        try:
            process = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except (subprocess.TimeoutExpired, OSError) as error:
            return {"status": "EXECUTION_ERROR", "error": str(error)}, "", str(error)
        if process.returncode != 0:
            return {"status": "EXECUTION_ERROR", "returncode": process.returncode}, process.stdout, process.stderr
        if not output.is_file():
            return {"status": "MISSING_OUTPUT"}, process.stdout, process.stderr
        return load_json(output), process.stdout, process.stderr


def child_contract(
    audit: Audit,
    name: str,
    fresh: dict[str, Any],
    stored: dict[str, Any],
    schema: str,
    assertions: int,
) -> None:
    audit.check("child", f"{name}_status", fresh.get("status") == "PASS", fresh.get("status"), "PASS")
    audit.check("child", f"{name}_schema", fresh.get("schema") == schema, fresh.get("schema"), schema)
    audit.check("child", f"{name}_result_id", fresh.get("result_id") == RESULT_ID, fresh.get("result_id"), RESULT_ID)
    audit.check("child", f"{name}_assertions", fresh.get("assertions_total") == assertions, fresh.get("assertions_total"), assertions)
    audit.check("child", f"{name}_all_passed", fresh.get("assertions_passed") == assertions, fresh.get("assertions_passed"), assertions)
    audit.check("child", f"{name}_deterministic_payload", fresh == stored, payload_digest(fresh), payload_digest(stored))


def verify_manifest(audit: Audit, manifest: dict[str, Any], pages: int, fields: Any) -> None:
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "claim_id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    status = str(manifest.get("status", ""))
    audit.check("manifest", "tier_boundary", "T4" in status and "SECTOR A OPEN" in status, status, "T4 ... SECTOR A OPEN")

    authorities = manifest.get("authority", {})
    for name, path in AUTHORITY_PATHS.items():
        entry = authorities.get(name, {}).get("manifest", {}) if isinstance(authorities, dict) else {}
        expected = {"path": relative(path), "sha256": digest(path)}
        audit.check("authority", name, entry == expected, entry, expected)

    sources = manifest.get("sources", {})
    for name, path in {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": VERIFIER, "proof_note": NOTE}.items():
        entry = sources.get(name, {}) if isinstance(sources, dict) else {}
        expected = {"path": relative(path), "sha256": digest(path)}
        ok = entry.get("path") == expected["path"] and entry.get("sha256") == expected["sha256"]
        audit.check("manifest", f"source_{name}", ok, entry, expected)

    children = manifest.get("child_results", {})
    for name, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        entry = children.get(name, {}) if isinstance(children, dict) else {}
        expected = {"path": relative(path), "sha256": digest(path)}
        ok = entry.get("path") == expected["path"] and entry.get("sha256") == expected["sha256"]
        audit.check("manifest", f"child_{name}", ok, entry, expected)

    pdf_entry = manifest.get("proof_pdf", {})
    expected_pdf = {"path": relative(PDF), "sha256": digest(PDF), "pages": pages, "size_bytes": PDF.stat().st_size}
    pdf_ok = all(pdf_entry.get(key) == value for key, value in expected_pdf.items())
    audit.check("manifest", "proof_pdf", pdf_ok, pdf_entry, expected_pdf)
    audit.check("manifest", "pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS", pdf_entry.get("visual_qa"), "PASS")
    audit.check("manifest", "pdf_form_check", pdf_entry.get("form_check") == "PASS", pdf_entry.get("form_check"), "PASS")

    contract = manifest.get("run_contract", {})
    expected_contract = {
        "primary_schema": PRIMARY_SCHEMA,
        "independent_schema": INDEPENDENT_SCHEMA,
        "integrated_schema": INTEGRATED_SCHEMA,
        "primary_assertions": PRIMARY_ASSERTIONS,
        "independent_assertions": INDEPENDENT_ASSERTIONS,
    }
    for key, expected in expected_contract.items():
        audit.check("contract", key, contract.get(key) == expected, contract.get(key), expected)
    audit.check("contract", "integrated_assertions_declared", isinstance(contract.get("integrated_assertions"), int) and contract.get("integrated_assertions", 0) > 0, contract.get("integrated_assertions"), ">0")

    consequence = manifest.get("consequence", {})
    expected_consequence = {
        "covariance_horizontal_h2_l6_synthesis": True,
        "variable_multiplier_theorem_under_derivative_bounds": True,
        "stationary_six_row_raw_current_low_chaos": True,
        "linear_hessian_identity": True,
        "rational_raw_q_hessian_identity": True,
        "fixed_21_matrix_flattening": True,
        "adapted_d0_d1": False,
        "cartan_companion_observed": False,
        "complete_owner_reconstruction": False,
        "one_use_source_sextic_aggregation": False,
        "full_overlap_src": False,
        "nelson": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    for key, expected in expected_consequence.items():
        audit.check("consequence", key, consequence.get(key) is expected, consequence.get(key), expected)

    audit.check("pdf", "page_count", pages == pdf_entry.get("pages"), pages, pdf_entry.get("pages"))
    audit.check("pdf", "no_acroform_fields", not fields, bool(fields), False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=120)
    arguments = parser.parse_args()
    audit = Audit()

    required = [PRIMARY, INDEPENDENT, VERIFIER, NOTE, PDF, MANIFEST, PRIMARY_RESULT, INDEPENDENT_RESULT, *AUTHORITY_PATHS.values()]
    for path in required:
        audit.check("filesystem", relative(path), path.is_file(), path.is_file(), True)

    if any(not path.is_file() for path in required):
        payload = audit.finish({"error": "required file missing"})
        atomic_json(arguments.output, payload)
        print(f"R-120 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
        return 1

    fresh_primary, primary_stdout, primary_stderr = execute_child(PRIMARY, arguments.timeout)
    fresh_independent, independent_stdout, independent_stderr = execute_child(INDEPENDENT, arguments.timeout)
    stored_primary = load_json(PRIMARY_RESULT)
    stored_independent = load_json(INDEPENDENT_RESULT)
    child_contract(audit, "primary", fresh_primary, stored_primary, PRIMARY_SCHEMA, PRIMARY_ASSERTIONS)
    child_contract(audit, "independent", fresh_independent, stored_independent, INDEPENDENT_SCHEMA, INDEPENDENT_ASSERTIONS)

    primary_diag = fresh_primary.get("diagnostics", {})
    independent_diag = fresh_independent.get("diagnostics", {})
    horizontal = primary_diag.get("horizontal_synthesis", {})
    stationary = primary_diag.get("stationary_low_chaos", {})
    cartan = primary_diag.get("cartan", {})
    independent_hessian = independent_diag.get("rational_hessian", {})
    audit.check("cross", "l6_constant", horizontal.get("l6_constant") == 32, horizontal.get("l6_constant"), 32)
    audit.check("cross", "cm_constant", abs(float(horizontal.get("c_cm", 0.0)) - 9.228111768509862) < 5e-14, horizontal.get("c_cm"), 9.228111768509862)
    audit.check("cross", "six_row_parity", stationary.get("six_row_coefficient_parity_verified") is True, stationary.get("six_row_coefficient_parity_verified"), True)
    audit.check("cross", "adapted_open", stationary.get("adapted_future_feedback") == "open D0,D1", stationary.get("adapted_future_feedback"), "open D0,D1")
    audit.check("cross", "companion_not_observed", cartan.get("companion_observed") is False, cartan.get("companion_observed"), False)
    audit.check("cross", "independent_r102_curl", independent_hessian.get("isolated_r102_curl") == "-40/729", independent_hessian.get("isolated_r102_curl"), "-40/729")
    audit.check("cross", "independent_basis", independent_hessian.get("absolute_sum") == "7/2 I", independent_hessian.get("absolute_sum"), "7/2 I")

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        audit.check("note", token[:48], token in note_text, token in note_text, True)

    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    fields = reader.get_fields()
    manifest = load_json(MANIFEST)
    verify_manifest(audit, manifest, pages, fields)

    # This assertion is intentionally last: the manifest declares the exact
    # total computed before this final self-consistency row is appended.
    declared_total = manifest.get("run_contract", {}).get("integrated_assertions")
    final_total = len(audit.rows) + 1
    audit.check("contract", "integrated_assertions", declared_total == final_total, declared_total, final_total)

    diagnostics = {
        "primary_stdout": primary_stdout.strip(),
        "primary_stderr": primary_stderr.strip(),
        "independent_stdout": independent_stdout.strip(),
        "independent_stderr": independent_stderr.strip(),
        "pdf_pages": pages,
        "pdf_fields": bool(fields),
        "companion_observed": False,
        "adapted_d0_d1": "open",
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-120 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}; children {PRIMARY_ASSERTIONS}/{PRIMARY_ASSERTIONS}, {INDEPENDENT_ASSERTIONS}/{INDEPENDENT_ASSERTIONS}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
