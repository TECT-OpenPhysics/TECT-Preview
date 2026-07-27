#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-101 A13 package."""

from __future__ import annotations

__version__ = "1.0.2"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import ast
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RAW-WICK-HEAT-BASELINE-ORTHOGONALITY-RATIONAL-CURRENT-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction_independent.py"
NOTE = CLAIM_DIR / "notes/classii-raw-wick-heat-baseline-orthogonality-rational-current-reduction-260727-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-raw-wick-heat-baseline-orthogonality-rational-current-reduction-260727-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-27-primary-raw-wick-heat-baseline-orthogonality-rational-current-reduction/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-27-independent-raw-wick-heat-baseline-orthogonality-rational-current-reduction/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-27-integrated-raw-wick-heat-baseline-orthogonality-rational-current-reduction/result.json"

AUTHORITY = {
    "a1": (
        REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
        REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/runs/2026-07-17-reference-functional-closure/result.json",
    ),
    "r063": (
        CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
        CLAIM_DIR / "runs/2026-07-22-integrated-balanced-coefficient-jet-continuum/result.json",
    ),
    "r071": (
        CLAIM_DIR / "classii_one_form_sobolev_linear_closure_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-one-form-sobolev-linear-closure/result.json",
    ),
    "r076": (
        CLAIM_DIR / "classii_signed_transport_besov_bregman_resonance_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-signed-transport-besov-bregman-resonance/result.json",
    ),
    "r083": (
        CLAIM_DIR / "classii_controlled_polynomial_cfar_linear_pf_forest_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-controlled-polynomial-cfar-linear-pf-forest/result.json",
    ),
    "r084": (
        CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-root-diagonal-cartan-ou-linear-pf-absorption/result.json",
    ),
    "r085": (
        CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json",
    ),
    "r094": (
        CLAIM_DIR / "classii_root_local_gram_secant_feedback_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-root-local-gram-secant-feedback-boundary/result.json",
    ),
    "r096": (
        CLAIM_DIR / "classii_low_hermite_wick_predictable_baseline_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-low-hermite-wick-predictable-baseline-reduction/result.json",
    ),
    "r097": (
        CLAIM_DIR / "classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-global-gram-terminalization-covariance-deficit-reduction/result.json",
    ),
    "r100": (
        CLAIM_DIR / "classii_owner_gauge_heat_centered_covariance_debt_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-owner-gauge-heat-centered-covariance-debt-reduction/result.json",
    ),
}

EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(243, 250))
EXPLORATION_VERDICTS = {
    "EXP-000243": "advanced",
    "EXP-000244": "advanced",
    "EXP-000245": "advanced",
    "EXP-000246": "failed",
    "EXP-000247": "inconclusive",
    "EXP-000248": "advanced",
    "EXP-000249": "advanced",
}
NOTE_TOKENS = (
    "R-101",
    "evidence-anchor: theorem-3.1-moving-raw-wick-heat-baseline-orthogonality",
    "\\E_{j-1}\\langle L_j,\\Delta Q_{j,i}\\rangle=0",
    "evidence-anchor: theorem-4.1-cross-doob-raw-wick-terminalization",
    "B(Z_*)-B(Z_j)",
    "evidence-anchor: lemma-5.1-exact-derivative-current-remainder",
    "B_+(C+b)-B_-C",
    "evidence-anchor: theorem-6.1-rational-current-frontier-reduction",
    "\\mathcal K_R=G^TLc+{1\\over2}c^TB_1c",
    "evidence-anchor: lemma-7.1-production-rational-range-domination",
    "heat-lifted coefficient-balanced rational-current Carleson gate",
    "P_{\\Sigma_{\\rm tar}}B_R",
    "uniformly over the admissible target-heat family",
    "{65\\over81}",
    "{13\\over12}",
    "EXP-000243--EXP-000249",
    "T4 / T4; no promotion",
    "Sector-A closure",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_whitespace(value: str) -> str:
    """Make semantic token checks insensitive to harmless line wrapping."""
    return re.sub(r"\s+", " ", value)


def numeric(value: Any) -> float:
    """Decode a JSON number or an exact Fraction string without importing a child."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(Fraction(value))
    raise TypeError(f"not a numeric value: {value!r}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return None if match is None else match.group(1)


def result_passes(record: dict[str, Any]) -> bool:
    status = str(record.get("status", "")).upper()
    total = record.get("assertions_total")
    passed = record.get("assertions_passed")
    failed = record.get("assertions_failed")
    if status == "PASS" and isinstance(total, int) and total > 0:
        return passed == total and (failed is None or failed == 0)
    if str(record.get("verdict", "")).upper().endswith("PASS") or record.get("pass") is True:
        return True
    summary = record.get("summary", {})
    if not isinstance(summary, dict):
        return False
    if summary.get("failed") == 0 and summary.get("passed", 0) > 0:
        return True
    return (
        str(summary.get("verdict", "")).upper().endswith("PASS")
        and isinstance(summary.get("total"), int)
        and summary.get("total", 0) > 0
        and summary.get("passed") == summary.get("total")
    )


def assertion(record: dict[str, Any], name: str) -> dict[str, Any]:
    for row in record.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row
    return {}


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def main() -> int:
    count_only = "--count-only" in sys.argv
    rows: list[dict[str, Any]] = []

    def add(group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    records: dict[str, dict[str, Any]] = {}
    for label, script, result_path in (
        ("primary", PRIMARY, PRIMARY_RESULT),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT),
    ):
        result_path.unlink(missing_ok=True)
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=180,
        )
        add("execution", f"{label}_process_exit", completed.returncode == 0, completed.returncode, 0)
        add("execution", f"{label}_fresh_result", result_path.is_file(), repo_path(result_path), "fresh atomic output")
        try:
            record = load_json(result_path)
        except Exception as error:
            record = {}
            add("execution", f"{label}_result_json", False, repr(error), "valid JSON")
        else:
            add("execution", f"{label}_result_json", True, "valid JSON", "valid JSON")
        records[label] = record
        add("execution", f"{label}_passes", result_passes(record), record.get("status"), "PASS")
        add("execution", f"{label}_claim_id", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add("execution", f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    primary = records["primary"]
    independent = records["independent"]
    primary_names = (
        "probability_mass",
        "moving_L_cross_1",
        "moving_L_cross_2",
        "moving_L_cross_3",
        "terminal_raw_wick_identity",
        "nonzero_fixed_low_endpoint",
        "nonzero_low_terminal_identity",
        "correlated_value_gradient_breaks_centering",
        "gradient_dependent_coefficient_breaks_centering",
        "K_identity_0",
        "K_regroup_0",
        "matched_endpoint_telescope",
        "zero_low_endpoint_nonnegative",
        "cross_family_partition",
        "shifted_current_nontrivial",
        "alpha_derived",
        "c0_derived",
        "c1_derived",
        "production_floor_derived",
        "near_floor_pure_doublet_oracle",
        "scalar_full_remainder",
        "scalar_base_cubic",
        "scalar_balanced_remainder",
        "zero_heat_square_leading_coefficient",
        "balanced_schur_divergence_coefficient",
        "rational_range_identity_0",
        "rational_range_domination_0",
    )
    independent_names = (
        "probability_mass",
        "moving_heat_baseline_1",
        "moving_heat_baseline_2",
        "moving_heat_baseline_3",
        "terminal_raw_wick",
        "nonzero_fixed_low_endpoint",
        "nonzero_low_terminal_identity",
        "correlated_value_gradient_cross",
        "direct_gradient_coefficient_cross",
        "two_site_same_point_covariance_zero",
        "two_site_nonlocal_cross",
        "same_root_control_cross",
        "raw_plus_current_partition",
        "exact_regroup",
        "matched_endpoint_telescope",
        "zero_low_endpoint_nonnegative",
        "current_cross_partition",
        "shifted_current_is_not_algebraically_zero",
        "alpha",
        "c0",
        "c1",
        "production_floor",
        "production_p_mass",
        "near_floor_pure_doublet_oracle",
        "scalar_full_remainder",
        "scalar_base_cubic",
        "scalar_balanced_remainder",
        "zero_heat_square_leading_coefficient",
        "balanced_schur_divergence_coefficient",
        "rational_range_identity_0",
        "rational_range_domination_0",
    )
    for label, record, names in (
        ("primary", primary, primary_names),
        ("independent", independent, independent_names),
    ):
        for name in names:
            row = assertion(record, name)
            add("load_bearing", f"{label}_{name}", row.get("status") == "PASS", row.get("status"), "PASS")

    imports = imported_roots(INDEPENDENT)
    forbidden = sorted(imports & {"numpy", "sympy", PRIMARY.stem})
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    add("independence", "independent_forbidden_imports", not forbidden, forbidden, [])
    add("independence", "independent_no_primary_text_import", PRIMARY.stem not in independent_text, PRIMARY.stem if PRIMARY.stem in independent_text else "absent", "absent")
    add("independence", "independent_fraction_engine", "from fractions import Fraction" in independent_text and "import numpy" not in independent_text, "Fraction without NumPy", "Fraction without NumPy")

    primary_constants = primary.get("diagnostics", {}).get("production_constants", {})
    independent_constants = independent.get("diagnostics", {}).get("production_constants", {})
    for key, absolute_tolerance in (
        ("p_mass", 1.0e-14),
        ("floor", 1.0e-27),
        ("alpha", 1.0e-14),
        ("c0", 1.0e-16),
        ("c1", 1.0e-16),
    ):
        try:
            primary_value = numeric(primary_constants.get(key))
            independent_value = numeric(independent_constants.get(key))
            agrees = math.isclose(primary_value, independent_value, rel_tol=1.0e-14, abs_tol=absolute_tolerance)
        except (TypeError, ValueError, ZeroDivisionError) as error:
            primary_value = primary_constants.get(key)
            independent_value = independent_constants.get(key)
            agrees = False
        add(
            "cross_route",
            f"production_{key}_agrees",
            agrees,
            [primary_value, independent_value],
            "primary and exact independent agree",
        )

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest", "manifest_json", False, repr(error), "valid JSON")
    else:
        add("manifest", "manifest_json", True, "valid JSON", "valid JSON")
    add("manifest", "manifest_result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "manifest_tier_t4", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest", "manifest_proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    sources = manifest.get("sources", {}) if isinstance(manifest.get("sources"), dict) else {}
    for label, path in (("primary", PRIMARY), ("independent", INDEPENDENT), ("verifier", Path(__file__).resolve()), ("proof_note", NOTE)):
        entry = sources.get(label, {}) if isinstance(sources.get(label), dict) else {}
        add("manifest", f"manifest_{label}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
        expected_hash = digest(path) if path.is_file() else "file"
        add("manifest", f"manifest_{label}_hash", path.is_file() and entry.get("sha256") == expected_hash, entry.get("sha256"), expected_hash)
        expected_version = "1.0" if label == "proof_note" else source_version(path)
        add("manifest", f"manifest_{label}_version", entry.get("version") == expected_version, entry.get("version"), expected_version)

    authority_root = manifest.get("authority", {}) if isinstance(manifest.get("authority"), dict) else {}
    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        authority_entry = authority_root.get(label, {}) if isinstance(authority_root.get(label), dict) else {}
        for kind, path in (("manifest", authority_manifest), ("result", authority_result)):
            entry = authority_entry.get(kind, {}) if isinstance(authority_entry, dict) else {}
            add("authority", f"{label}_{kind}_exists", path.is_file(), repo_path(path), "file")
            add("authority", f"{label}_{kind}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
            expected_hash = digest(path) if path.is_file() else "file"
            add("authority", f"{label}_{kind}_hash", path.is_file() and entry.get("sha256") == expected_hash, entry.get("sha256"), expected_hash)
        try:
            authority_record = load_json(authority_result)
        except Exception as error:
            add("authority", f"{label}_result_pass", False, repr(error), "PASS")
        else:
            add("authority", f"{label}_result_pass", result_passes(authority_record), authority_record.get("status", authority_record.get("verdict")), "PASS")

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.is_file() else ""
    note_scan = normalized_whitespace(note_text)
    add("proof_note", "note_exists", NOTE.is_file(), repo_path(NOTE), "file")
    for index, token in enumerate(NOTE_TOKENS):
        add("proof_note", f"note_token_{index:02d}", token in note_scan, token if token in note_scan else "missing", token)
    add("proof_note", "note_no_replacement", "\ufffd" not in note_text, note_text.count("\ufffd"), 0)
    add("proof_note", "note_no_bare_qquad", "qquad" not in note_text.replace("\\qquad", ""), "clean" if "qquad" not in note_text.replace("\\qquad", "") else "bare qquad", "clean")
    add("proof_note", "note_fragment", "\\documentclass" not in note_text, "fragment", "fragment")

    add("proof_pdf", "pdf_exists", PDF.is_file(), repo_path(PDF), "file")
    pdf_page_count = 0
    pdf_text = ""
    pdf_fields = -1
    if PDF.is_file():
        reader = PdfReader(PDF)
        pdf_page_count = len(reader.pages)
        pdf_text = "\n".join((page.extract_text() or "") for page in reader.pages)
        pdf_fields = len(reader.get_fields() or {})
    pdf_scan = normalized_whitespace(pdf_text)
    add("proof_pdf", "pdf_page_count", pdf_page_count == 11, pdf_page_count, 11)
    add("proof_pdf", "pdf_no_fields", pdf_fields == 0, pdf_fields, 0)
    add("proof_pdf", "pdf_title", "Raw-Wick heat-baseline orthogonality" in pdf_scan, "title" if "Raw-Wick heat-baseline orthogonality" in pdf_scan else "missing", "title")
    add("proof_pdf", "pdf_footer", "R-101" in pdf_scan and "Sector-A closure" in pdf_scan, ["R-101" in pdf_scan, "Sector-A closure" in pdf_scan], [True, True])
    proof_pdf = manifest.get("proof_pdf", {}) if isinstance(manifest.get("proof_pdf"), dict) else {}
    add("proof_pdf", "manifest_pdf_path", proof_pdf.get("path") == repo_path(PDF), proof_pdf.get("path"), repo_path(PDF))
    add("proof_pdf", "manifest_pdf_hash", PDF.is_file() and proof_pdf.get("sha256") == digest(PDF), proof_pdf.get("sha256"), digest(PDF) if PDF.is_file() else "file")
    add("proof_pdf", "manifest_pdf_pages", proof_pdf.get("pages") == 11, proof_pdf.get("pages"), 11)
    add("proof_pdf", "manifest_pdf_form", proof_pdf.get("form_check") == "PASS", proof_pdf.get("form_check"), "PASS")
    add("proof_pdf", "manifest_pdf_overfull", proof_pdf.get("overfull_hbox_count") == 0, proof_pdf.get("overfull_hbox_count"), 0)
    add("proof_pdf", "manifest_pdf_visual_qa", proof_pdf.get("visual_qa") == "PASS", proof_pdf.get("visual_qa"), "PASS")

    exploration_rows: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("id") in EXPLORATIONS:
            exploration_rows[record["id"]] = record
    for exploration in EXPLORATIONS:
        record = exploration_rows.get(exploration, {})
        add("explorations", f"{exploration}_present", bool(record), record.get("id"), exploration)
        add("explorations", f"{exploration}_verdict", record.get("verdict") == EXPLORATION_VERDICTS[exploration], record.get("verdict"), EXPLORATION_VERDICTS[exploration])
        add("explorations", f"{exploration}_result_ref", "R-101" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), "contains R-101")

    surface_tokens = {
        "results_ledger": (REPO / "RESULTS-LEDGER.md", ("R-101", RESULT_ID, "Cross-Doob terminalization")),
        "claim_card": (CLAIM_DIR / "claim.md", (RESULT_ID, "EXP-000243", "EXP-000248", "coefficient-balanced rational-current")),
        "gates": (REPO / "claims/GATES.md", ("R-101", "coefficient-balanced rational-current")),
        "roadmap": (REPO / "ROADMAP.md", ("R-080--R-101", "K_R")),
        "todo": (REPO / "TODO.md", ("R-101", "coefficient-balanced rational-current")),
        "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-101", "classii-raw-wick-heat-baseline-orthogonality-rational-current-reduction")),
        "proof_map": (REPO / "theory/proof-evidence-map.md", ("R-101", "EXP-000247")),
    }
    for label, (path, tokens) in surface_tokens.items():
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        text_scan = normalized_whitespace(text)
        add("surfaces", f"{label}_exists", path.is_file(), repo_path(path), "file")
        for index, token in enumerate(tokens):
            add("surfaces", f"{label}_token_{index}", token in text_scan, token if token in text_scan else "missing", token)

    try:
        status = load_json(CLAIM_DIR / "status.json")
    except Exception as error:
        status = {}
        add("surfaces", "status_json", False, repr(error), "valid JSON")
    else:
        add("surfaces", "status_json", True, "valid JSON", "valid JSON")
    add("surfaces", "status_tier", status.get("tier") == "T4", status.get("tier"), "T4")
    add("surfaces", "status_statement_r101", "R-101" in status.get("statement", ""), "R-101" if "R-101" in status.get("statement", "") else "missing", "R-101")
    status_command = status.get("reproduction", {}).get("command", "")
    canonical_command = manifest.get("run_contract", {}).get("command", "")
    add("surfaces", "status_reproduction", status_command == canonical_command, status_command, canonical_command)
    add("surfaces", "status_frontier", "coefficient-balanced rational-current" in status.get("next_action", "") and "Sector A remain open" in status.get("statement", ""), ["coefficient-balanced rational-current" in status.get("next_action", ""), "Sector A remain open" in status.get("statement", "")], [True, True])
    add("surfaces", "status_explorations", "EXP-000243--EXP-000249" in status.get("notes", ""), status.get("notes", "")[-140:], "EXP-000243--EXP-000249")

    contract = manifest.get("run_contract", {}) if isinstance(manifest.get("run_contract"), dict) else {}
    add("contract", "primary_count", contract.get("primary_assertions") == primary.get("assertions_total"), contract.get("primary_assertions"), primary.get("assertions_total"))
    add("contract", "independent_count", contract.get("independent_assertions") == independent.get("assertions_total"), contract.get("independent_assertions"), independent.get("assertions_total"))
    expected_schemas = {
        "primary": primary.get("schema"),
        "independent": independent.get("schema"),
        "integrated": "tect/a13-raw-wick-heat-baseline-orthogonality-rational-current-reduction-integrated/1.0",
    }
    for label, expected_schema in expected_schemas.items():
        add("contract", f"{label}_schema", contract.get(f"{label}_schema") == expected_schema, contract.get(f"{label}_schema"), expected_schema)
    expected_outputs = {
        "primary": repo_path(PRIMARY_RESULT),
        "independent": repo_path(INDEPENDENT_RESULT),
        "integrated": repo_path(OUTPUT),
    }
    for label, expected_output in expected_outputs.items():
        add("contract", f"{label}_output", contract.get(f"{label}_output") == expected_output, contract.get(f"{label}_output"), expected_output)
    consequence = manifest.get("consequence", {}) if isinstance(manifest.get("consequence"), dict) else {}
    consequence_expectations = {
        "moving_raw_wick_heat_baseline_orthogonality": True,
        "cross_doob_raw_wick_reduction": True,
        "exact_derivative_current_remainder": True,
        "control_square_endpoint_telescope": True,
        "rational_current_frontier_reduction": True,
        "production_rational_range_domination": True,
        "coefficient_balanced_rational_current_bound": False,
        "complete_h_n": False,
        "reg": False,
        "full_overlap_src": False,
        "sector_a_closure": False,
    }
    for key, expected in consequence_expectations.items():
        add("consequence", key, consequence.get(key) is expected, consequence.get(key), expected)
    final_integrated_count = len(rows) + 2
    add("contract", "integrated_count", contract.get("integrated_assertions") == final_integrated_count, contract.get("integrated_assertions"), final_integrated_count)
    expected_aggregate = primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + final_integrated_count
    add("contract", "aggregate_count", contract.get("aggregate_assertions") == expected_aggregate, contract.get("aggregate_assertions"), expected_aggregate)

    passed = sum(row["status"] == "PASS" for row in rows)
    if count_only:
        print(f"INTEGRATED ASSERTIONS PLANNED: {len(rows)}")
        print(f"CURRENT PASS: {passed}/{len(rows)}")
        return 0
    payload = {
        "schema": "tect/a13-raw-wick-heat-baseline-orthogonality-rational-current-reduction-integrated/1.0",
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "assertions": rows,
        "source_hashes": {
            "primary": digest(PRIMARY),
            "independent": digest(INDEPENDENT),
            "verifier": digest(Path(__file__).resolve()),
            "proof_note": digest(NOTE),
            "proof_pdf": digest(PDF),
            "manifest": digest(MANIFEST),
        },
        "authority_hashes": {
            label: {"manifest": digest(paths[0]), "result": digest(paths[1])}
            for label, paths in AUTHORITY.items()
        },
        "run_summary": {
            "primary": primary.get("assertions_total"),
            "independent": independent.get("assertions_total"),
            "integrated": len(rows),
            "aggregate": primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + len(rows),
        },
        "no_overclaim": (
            "R-101 certifies moving raw-Wick heat-baseline orthogonality, cross-Doob terminalization, "
            "the derivative-current telescope, and the rational K_R reduction in the regular strict-past "
            "class. The coefficient-balanced K_R bound, H_N, REG, progressive H_A, OVERLAP_src, Nelson, "
            "measure construction, and Sector A remain open."
        ),
    }
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed", "run_summary")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
