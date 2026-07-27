#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-102 A13 package."""

from __future__ import annotations

__version__ = "1.0.3"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_full_hessian_laplace_wick_future_feedback_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_full_hessian_laplace_wick_future_feedback_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-full-hessian-laplace-wick-future-feedback-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-full-hessian-laplace-wick-future-feedback-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-full-hessian-laplace-wick-future-feedback-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-full-hessian-laplace-wick-future-feedback-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-full-hessian-laplace-wick-future-feedback-boundary/result.json"

AUTHORITY = {
    "a1": (
        REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
        REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/runs/2026-07-17-reference-functional-closure/result.json",
    ),
    "r050": (
        REPO / "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/classii_k_composite_manifest.json",
        REPO / "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/runs/2026-07-20-integrated-k-composite/result.json",
    ),
    "r071": (
        CLAIM_DIR / "classii_one_form_sobolev_linear_closure_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-one-form-sobolev-linear-closure/result.json",
    ),
    "r075": (
        CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-principal-taylor-oneform-graph-recovery/result.json",
    ),
    "r076": (
        CLAIM_DIR / "classii_signed_transport_besov_bregman_resonance_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-signed-transport-besov-bregman-resonance/result.json",
    ),
    "r078": (
        CLAIM_DIR / "classii_hessian_difference_safe_packet_doob_bracket_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-hessian-difference-safe-packet-doob-bracket/result.json",
    ),
    "r080": (
        CLAIM_DIR / "classii_low_object_far_square_progressive_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-low-object-far-square-progressive-boundary/result.json",
    ),
    "r086": (
        CLAIM_DIR / "classii_rational_translated_wick_payload_comparable_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-rational-translated-wick-payload-comparable-reduction/result.json",
    ),
    "r092": (
        CLAIM_DIR / "classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-normalized-cartan-perspective-covariance-frontier/result.json",
    ),
    "r096": (
        CLAIM_DIR / "classii_low_hermite_wick_predictable_baseline_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-low-hermite-wick-predictable-baseline-reduction/result.json",
    ),
    "r099": (
        CLAIM_DIR / "classii_extended_state_cartan_doob_rational_recovery_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-extended-state-cartan-doob-rational-recovery/result.json",
    ),
    "r100": (
        CLAIM_DIR / "classii_owner_gauge_heat_centered_covariance_debt_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-owner-gauge-heat-centered-covariance-debt-reduction/result.json",
    ),
    "r101": (
        CLAIM_DIR / "classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-raw-wick-heat-baseline-orthogonality-rational-current-reduction/result.json",
    ),
}

EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(250, 258))
EXPLORATION_VERDICTS = {
    "EXP-000250": "advanced",
    "EXP-000251": "advanced",
    "EXP-000252": "advanced",
    "EXP-000253": "failed",
    "EXP-000254": "failed",
    "EXP-000255": "failed",
    "EXP-000256": "advanced",
    "EXP-000257": "advanced",
}
NEGATIVE_IDS = (
    "NG-2026-07-28-A13-GLOBAL-TO-PREDICTABLE-CURRENT-BRIDGE",
    "NG-2026-07-28-A13-FULL-HESSIAN-CARTAN-CHAIN-PRIMITIVE",
)
NOTE_TOKENS = (
    "R-102",
    "evidence-anchor: theorem-2.1-full-hessian-owner-recombination",
    "evidence-anchor: lemma-3.1-uniform-second-hessian",
    "evidence-anchor: theorem-4.1-all-psd-laplace-wick",
    "evidence-anchor: theorem-6.1-active-kernel-heat-geometry",
    "evidence-anchor: theorem-7.1-global-current-cross-doob",
    "evidence-anchor: proposition-8.1-future-feedback-bridge-counterfixture",
    "evidence-anchor: theorem-9.2-regular-future-insertion-current-closure",
    "finite $j<k$ sums",
    "\\emph{whole product}",
    "X^{9/14}\\overline Y^{2/7}",
    "X^{1/7}\\overline Y^{19/42}",
    "2^{-k/14}",
    "17/42",
    "move the triangle inequality inside each expectation",
    "EXP-000250--EXP-000257",
    "T4 / T4; no promotion",
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
    return re.sub(r"\s+", " ", value)


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
    shared_load_bearing = (
        "owner_recombination",
        "finite_double_sum_swap",
        "finite_whole_product_conditioning",
        "deterministic_heat_semigroup_composition",
        "derivative_spatial_holder",
        "derivative_young_slack",
        "derivative_gaussian_moment",
        "first_coefficient_spatial_holder",
        "first_coefficient_interpolation",
        "first_coefficient_shell_holder",
        "second_coefficient_spatial_holder",
        "second_coefficient_interpolation",
        "second_coefficient_shell_holder",
        "coefficient_shell_decay",
        "coefficient_x_power",
        "coefficient_y_power",
        "coefficient_young_slack",
        "coefficient_gaussian_moment",
        "coefficient_eta_power",
        "coefficient_zeta_power",
        "canonical_x_high_shell_sum",
        "high_prefix_derivative_no_additive_constant",
        "fixed_low_branch_retained",
        "fixed_low_x_power",
        "fixed_low_y_power",
        "fixed_low_young_slack",
        "fixed_low_gaussian_moment",
        "fixed_low_eta_power",
        "fixed_low_zeta_power",
        "fixed_low_decay_power",
        "jensen_control_tangent_increments_vanish",
        "jensen_nonlinear_innovation_gap",
        "jensen_current_is_negative",
        "two_root_first_bracket",
        "two_root_second_bracket",
        "full_remainder_one_form_curl",
    )
    primary_only = (
        "mixed_direction_second_hessian_identity",
        "finite_polynomial_degree",
        "singular_determinant_lemma",
        "singular_mean_woodbury",
        "singular_covariance_woodbury",
        "singular_W1_tilt_identity",
        "singular_W2_tilt_identity",
        "active_lower_bound",
        "active_upper_bound",
        "kernel_limit_constant",
    )
    independent_aliases = {
        "owner_recombination": "owner_recombination",
        "full_remainder_one_form_curl": "full_remainder_one_form_curl",
    }
    for name in shared_load_bearing:
        for label, record in (("primary", primary), ("independent", independent)):
            lookup = independent_aliases.get(name, name) if label == "independent" else name
            row = assertion(record, lookup)
            add("load_bearing", f"{label}_{name}", row.get("status") == "PASS", row.get("status"), "PASS")
    for name in primary_only:
        row = assertion(primary, name)
        add("load_bearing", f"primary_{name}", row.get("status") == "PASS", row.get("status"), "PASS")

    imports = imported_roots(INDEPENDENT)
    forbidden = sorted(imports & {"numpy", "sympy", "scipy"})
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    add("independence", "independent_forbidden_imports", not forbidden, forbidden, [])
    add("independence", "independent_no_primary_import", PRIMARY.stem not in independent_text, PRIMARY.stem if PRIMARY.stem in independent_text else "absent", "absent")
    add("independence", "independent_fraction_engine", "from fractions import Fraction" in independent_text, "Fraction" if "from fractions import Fraction" in independent_text else "missing", "Fraction")

    primary_chronological = primary.get("diagnostics", {}).get("chronological_closure", {})
    independent_chronological = independent.get("diagnostics", {}).get("chronological_closure", {})
    for key, expected in (
        ("derivative_slack", "1/6"),
        ("coefficient_shell_decay", "-1/14"),
        ("coefficient_x_power", "9/14"),
        ("coefficient_y_power", "2/7"),
        ("coefficient_slack", "1/14"),
        ("required_gaussian_moment", "14/1"),
        ("eta_power", "9/1"),
        ("zeta_power", "4/1"),
        ("high_prefix_derivative_x_power", "1/2"),
        ("fixed_low_x_power", "1/7"),
        ("fixed_low_y_power", "19/42"),
        ("fixed_low_slack", "17/42"),
        ("fixed_low_required_gaussian_moment", "42/17"),
        ("fixed_low_eta_power", "6/17"),
        ("fixed_low_zeta_power", "19/17"),
        ("fixed_low_decay_power", "3/17"),
    ):
        actual = [primary_chronological.get(key), independent_chronological.get(key)]
        add("cross_route", f"chronological_{key}", actual == [expected, expected], actual, [expected, expected])
    primary_scalar = primary.get("diagnostics", {}).get("scalar_owner", {})
    independent_scalar = independent.get("diagnostics", {}).get("scalar_owner", {})
    for primary_key, independent_key, expected in (
        ("full_ridge", "full", "40/81"),
        ("cubic_ridge", "cubic", "-25/81"),
        ("balanced_ridge", "balanced", "65/81"),
        ("full_shift_derivative", "full_shift_derivative", "-70/27"),
        ("balanced_shift_derivative", "balanced_shift_derivative", "-95/27"),
    ):
        actual = [primary_scalar.get(primary_key), independent_scalar.get(independent_key)]
        add("cross_route", f"scalar_{primary_key}", actual == [expected, expected], actual, [expected, expected])
    for diagnostic, key, expected in (
        ("future_feedback", "jensen_current_sqrt_2_over_pi_factor", "-5087809298589293093756/67965137546788211215457205"),
        ("cartan_boundary", "full_remainder_one_form_curl", "-40/729"),
    ):
        actual = [
            primary.get("diagnostics", {}).get(diagnostic, {}).get(key),
            independent.get("diagnostics", {}).get(diagnostic, {}).get(key),
        ]
        add("cross_route", f"{diagnostic}_{key}", actual == [expected, expected], actual, [expected, expected])

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
    for negative_id in NEGATIVE_IDS:
        add("proof_note", f"note_{negative_id}", negative_id in note_scan, negative_id if negative_id in note_scan else "missing", negative_id)
    add("proof_note", "note_no_replacement", "\ufffd" not in note_text, note_text.count("\ufffd"), 0)
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
    add("proof_pdf", "pdf_page_count", pdf_page_count == 17, pdf_page_count, 17)
    add("proof_pdf", "pdf_no_fields", pdf_fields == 0, pdf_fields, 0)
    add("proof_pdf", "pdf_title", "Full-Hessian heat representation" in pdf_scan, "title" if "Full-Hessian heat representation" in pdf_scan else "missing", "title")
    add("proof_pdf", "pdf_footer", "R-102" in pdf_scan and "regular K_R closes" in pdf_scan and "Sector-A closure" in pdf_scan, ["R-102" in pdf_scan, "regular K_R closes" in pdf_scan, "Sector-A closure" in pdf_scan], [True, True, True])
    proof_pdf = manifest.get("proof_pdf", {}) if isinstance(manifest.get("proof_pdf"), dict) else {}
    add("proof_pdf", "manifest_pdf_path", proof_pdf.get("path") == repo_path(PDF), proof_pdf.get("path"), repo_path(PDF))
    add("proof_pdf", "manifest_pdf_hash", PDF.is_file() and proof_pdf.get("sha256") == digest(PDF), proof_pdf.get("sha256"), digest(PDF) if PDF.is_file() else "file")
    add("proof_pdf", "manifest_pdf_pages", proof_pdf.get("pages") == 17, proof_pdf.get("pages"), 17)
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
        add("explorations", f"{exploration}_result_ref", "R-102" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), "contains R-102")
    registry_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        add("negative_registry", negative_id, negative_id in registry_text, negative_id if negative_id in registry_text else "missing", negative_id)

    surface_tokens = {
        "results_ledger": (REPO / "RESULTS-LEDGER.md", ("R-102", "`X^(1/7)(1+Y)^(19/42)`", "regular `K_R` closes")),
        "claim_card": (CLAIM_DIR / "claim.md", (RESULT_ID, "EXP-000257", "`X^(1/7)(1+Y)^(19/42)`")),
        "roadmap": (REPO / "ROADMAP.md", ("R-102", "`X^(1/7)(1+Y)^(19/42)`", "complete `H_N`")),
        "todo": (REPO / "TODO.md", ("T-050", "`X^(1/7)(1+Y)^(19/42)`", "regular K_R")),
        "changelog": (REPO / "CHANGELOG.md", ("R-102", "future-insertion", "`X^(1/7)(1+Y)^(19/42)`")),
        "proof_map": (REPO / "theory/proof-evidence-map.md", ("R-102", "EXP-000257", NEGATIVE_IDS[0], NEGATIVE_IDS[1])),
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
    status_statement = status.get("statement", "")
    add(
        "surfaces",
        "status_statement_r102",
        "R-102" in status_statement and "X^(1/7)(1+Y)^(19/42)" in status_statement,
        ["R-102" in status_statement, "X^(1/7)(1+Y)^(19/42)" in status_statement],
        [True, True],
    )
    status_command = status.get("reproduction", {}).get("command", "")
    canonical_command = manifest.get("run_contract", {}).get("command", "")
    add("surfaces", "status_reproduction", status_command == canonical_command, status_command, canonical_command)
    status_falsifier = status.get("falsifier", "")
    frontier_actual = [
        "complete H_N and REG" in status.get("next_action", ""),
        "Sector A remain open" in status_statement,
        "EXP-000257" in status_falsifier,
        all(token in status_falsifier for token in ("106/106", "79/79", "339/339", "524/524")),
        all(token in status_falsifier for token in ("19/42", "17/42", "42/17")),
    ]
    add("surfaces", "status_frontier", all(frontier_actual), frontier_actual, [True] * 5)
    add("surfaces", "status_explorations", "EXP-000250--EXP-000257" in status.get("notes", ""), status.get("notes", "")[-160:], "EXP-000250--EXP-000257")

    contract = manifest.get("run_contract", {}) if isinstance(manifest.get("run_contract"), dict) else {}
    add("contract", "primary_count", contract.get("primary_assertions") == primary.get("assertions_total") == 106, contract.get("primary_assertions"), 106)
    add("contract", "independent_count", contract.get("independent_assertions") == independent.get("assertions_total") == 79, contract.get("independent_assertions"), 79)
    expected_schemas = {
        "primary": primary.get("schema"),
        "independent": independent.get("schema"),
        "integrated": "tect/a13-full-hessian-laplace-wick-future-feedback-boundary-integrated/1.0",
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
        "full_hessian_owner_recombination": True,
        "all_psd_laplace_wick_representation": True,
        "regular_future_insertion_current_bound": True,
        "regular_k_r_lower_form": True,
        "terminal_square_fully_reserved": True,
        "full_frame_posterior_covariance_bracket": False,
        "complete_h_n": False,
        "reg": False,
        "arbitrary_progressive_revisit": False,
        "full_overlap_src": False,
        "nelson": False,
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
        "schema": "tect/a13-full-hessian-laplace-wick-future-feedback-boundary-integrated/1.0",
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
            "R-102 proves the future-insertion current estimate and K_R lower form only at finite cutoff and "
            "fixed floor for the regular annular mutually orthogonal strict-past no-revisit class with "
            "deterministic PSD target and future heat. Both the high-prefix and fixed-low derivative "
            "coefficient branches are retained; random control-dependent heat is excluded. The full-frame "
            "posterior bracket, complete H_N, REG, arbitrary progression, OVERLAP_src, Nelson, removals, "
            "measure construction, Sector A, and T5--T7 remain open."
        ),
    }
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed", "run_summary")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
