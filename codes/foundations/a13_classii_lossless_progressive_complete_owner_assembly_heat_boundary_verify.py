#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-104 package."""

from __future__ import annotations

__version__ = "1.0.0"
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
from fractions import Fraction
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_lossless_progressive_complete_owner_assembly_heat_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_lossless_progressive_complete_owner_assembly_heat_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-lossless-progressive-complete-owner-assembly-heat-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-lossless-progressive-complete-owner-assembly-heat-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-lossless-progressive-complete-owner-assembly-heat-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-lossless-progressive-complete-owner-assembly-heat-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-lossless-progressive-complete-owner-assembly-heat-boundary/result.json"

# Pinned test-oracle counts.  The scripts derive every mathematical value.
PRIMARY_ASSERTION_ORACLE = 93
INDEPENDENT_ASSERTION_ORACLE = 66

AUTHORITY_MANIFESTS = {
    "r079": "classii_full_safe_packet_frame_current_doob_manifest.json",
    "r081": "classii_cartan_tail_adapted_near_temporal_reduction_manifest.json",
    "r083": "classii_controlled_polynomial_cfar_linear_pf_forest_manifest.json",
    "r089": "classii_progressive_covariance_compression_rational_mean_spectral_boundary_manifest.json",
    "r091": "classii_projected_cartan_full_frame_temporal_boundary_manifest.json",
    "r093": "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r099": "classii_extended_state_cartan_doob_rational_recovery_manifest.json",
    "r100": "classii_owner_gauge_heat_centered_covariance_debt_reduction_manifest.json",
    "r101": "classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction_manifest.json",
    "r102": "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
    "r103": "classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
}

EXPECTED_MODULES = {
    "cartan_far": ["cartan_output"],
    "linear_near": ["linear_rows", "linear_heat_trace_forest"],
    "rational_raw_wick_residual": [
        "raw_wick_future_residual",
        "rational_heat_trace_forest",
        "full_wick_secant",
    ],
    "rational_unshifted_current": ["current_u3", "current_u4", "current_u5"],
    "rational_shifted_current": ["future_current", "terminal_square"],
    "conditional_low": ["conditional_low"],
    "complete_low": ["complete_low"],
    "paid_collar": ["r078_paid_difference"],
}

EXPECTED_REFUNDS = {
    "raw_q_taylor_u1",
    "raw_q_taylor_u2",
    "r076_base_cubic",
    "r086_tg_low_current",
    "r086_q_orientations",
    "second_r094_secant",
    "appended_r063_forest",
    "extra_q_r_schur_reserve",
}

PRIMARY_LOAD_BEARING = (
    "pure_kernel_fixture_values",
    "douglas_cost_equality_mutant_rejected",
    "doob_predictable_cross_mean_zero",
    "doob_product_identity_in_expectation",
    "doob_pathwise_equality_mutant_rejected",
    "terminal_covariance_matched",
    "noncausal_mixed_correlation_changed",
    "noncausal_l2_distance_two",
    "seven_near_modules",
    "eight_reg_modules",
    "module_table_complete",
    "atomic_owner_uniqueness",
    "cartan_output_once",
    "terminal_square_nested_in_shifted",
    "anticipative_heat_wick_defect",
    "source_coefficient",
    "gap_coefficient",
    "assembly_identity_from_components",
)

INDEPENDENT_LOAD_BEARING = (
    "pure_kernel_fixture_values",
    "douglas_cost_equality_mutant_rejected",
    "doob_predictable_cross_mean_zero",
    "doob_product_identity_in_expectation",
    "doob_pathwise_equality_mutant_rejected",
    "terminal_covariance_matched",
    "noncausal_mixed_correlation_changed",
    "noncausal_l2_distance_two",
    "seven_near_modules",
    "eight_reg_modules",
    "module_table_complete",
    "atomic_owner_uniqueness",
    "cartan_output_once",
    "terminal_square_nested_in_shifted",
    "same_root_g4_heat_defect_twelve",
    "same_root_psd_zero_defect_guard",
    "source_weight_9_20",
    "gap_weight_9_10",
    "assembly_identity_from_components",
)

NOTE_TOKENS = (
    "R-104",
    "evidence-anchor: theorem-3.1-lossless-complete-owner-temporalisation",
    "evidence-anchor: proposition-6.1-anticipative-heat-nogo",
    "evidence-anchor: theorem-7.1-lossless-h-a-assembly",
    r"H_A^{\rm asm}",
    r"\mathfrak D_{\rm CM}",
    "representation-preserving subdivision",
    "Cartan FAR",
    "same-root PSD",
    r"\mathrm{OVERLAP}_{\rm src}",
    "T4 / T4; no promotion",
)

EXPLORATIONS = {
    "EXP-000260": "advanced",
    "EXP-000261": "failed",
    "EXP-000262": "advanced",
}
NEGATIVE_ID = "NG-2026-07-28-A13-ANTICIPATIVE-RANDOM-HEAT-CONDITIONING"


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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def source_version(path: Path) -> str | None:
    match = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return None if match is None else match.group(1)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value)


def result_passes(record: dict[str, Any]) -> bool:
    total = record.get("assertions_total")
    return (
        str(record.get("status", "")).upper() == "PASS"
        and isinstance(total, int)
        and total > 0
        and record.get("assertions_passed") == total
        and record.get("assertions_failed", 0) == 0
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


def authority_result_path(manifest_path: Path) -> Path | None:
    manifest = load_json(manifest_path)
    contract = manifest.get("run_contract", {})
    output = contract.get("integrated_output") if isinstance(contract, dict) else None
    return REPO / output if output else None


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
    for label, script, result_path, expected_count in (
        ("primary", PRIMARY, PRIMARY_RESULT, PRIMARY_ASSERTION_ORACLE),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT, INDEPENDENT_ASSERTION_ORACLE),
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
        add("execution", f"{label}_assertion_count", record.get("assertions_total") == expected_count, record.get("assertions_total"), expected_count)

    primary = records["primary"]
    independent = records["independent"]
    for name in PRIMARY_LOAD_BEARING:
        row = assertion(primary, name)
        add("load_bearing", f"primary_{name}", row.get("status") == "PASS", row.get("status"), "PASS")
    for name in INDEPENDENT_LOAD_BEARING:
        row = assertion(independent, name)
        add("load_bearing", f"independent_{name}", row.get("status") == "PASS", row.get("status"), "PASS")

    primary_diag = primary.get("diagnostics", {}) if isinstance(primary.get("diagnostics"), dict) else {}
    independent_diag = independent.get("diagnostics", {}) if isinstance(independent.get("diagnostics"), dict) else {}
    primary_assembly = primary_diag.get("assembly", {})
    independent_assembly = independent_diag.get("assembly", {})
    expected_components = ["0", "0", "0", "()", "()", "0", "()", "True"]
    add(
        "cross_route",
        "assembly_components",
        primary_assembly.get("components") == independent_assembly.get("components") == expected_components,
        [primary_assembly.get("components"), independent_assembly.get("components")],
        [expected_components, expected_components],
    )
    add(
        "cross_route",
        "assembly_identity",
        primary_assembly.get("identity_from_components") is True
        and independent_assembly.get("identity_from_components") is True,
        [primary_assembly.get("identity_from_components"), independent_assembly.get("identity_from_components")],
        [True, True],
    )
    add(
        "cross_route",
        "douglas_direction",
        primary_assembly.get("douglas_cost_direction") is True
        and independent_assembly.get("douglas_cost_direction") is True,
        [primary_assembly.get("douglas_cost_direction"), independent_assembly.get("douglas_cost_direction")],
        [True, True],
    )
    primary_modules = primary_diag.get("ownership", {}).get("modules", {})
    independent_modules = independent_diag.get("owners", {}).get("modules", {})
    add("cross_route", "primary_module_map", primary_modules == EXPECTED_MODULES, primary_modules, EXPECTED_MODULES)
    add("cross_route", "independent_module_map", independent_modules == EXPECTED_MODULES, independent_modules, EXPECTED_MODULES)
    primary_near = set(primary_diag.get("ownership", {}).get("near_modules", []))
    independent_near = set(independent_diag.get("owners", {}).get("near_modules", []))
    expected_near = set(EXPECTED_MODULES) - {"cartan_far"}
    add("cross_route", "seven_near_sets", primary_near == independent_near == expected_near, [sorted(primary_near), sorted(independent_near)], sorted(expected_near))
    primary_refunds = set(primary_diag.get("ownership", {}).get("refunds", []))
    independent_refunds = set(independent_diag.get("owners", {}).get("refunded", []))
    add("cross_route", "refund_sets", primary_refunds == independent_refunds == EXPECTED_REFUNDS, [sorted(primary_refunds), sorted(independent_refunds)], sorted(EXPECTED_REFUNDS))
    add("cross_route", "terminal_square_internal", "terminal_square" in EXPECTED_MODULES["rational_shifted_current"], EXPECTED_MODULES["rational_shifted_current"], "contains terminal_square")

    primary_var = primary_diag.get("variational", {})
    independent_var = independent_diag.get("variational", {})
    primary_kernel = primary_diag.get("douglas", {}).get("pure_kernel", {})
    independent_kernel = independent_diag.get("matrix_fixtures", {}).get("pure_kernel", {})
    primary_expected_slack = Fraction(primary_var.get("source_coefficient", "0")) * (
        Fraction(str(primary_kernel.get("control_cost", 0)))
        - Fraction(str(primary_kernel.get("source_cost", 0)))
    )
    independent_expected_slack = Fraction(independent_var.get("source_weight", "0")) * (
        Fraction(independent_kernel.get("control_cost", "0"))
        - Fraction(independent_kernel.get("minimal_cost", "0"))
    )
    actual_slacks = [
        primary_assembly.get("physical_source_cost_slack_strict_fixture"),
        independent_assembly.get("physical_source_cost_slack_strict_fixture"),
    ]
    expected_slacks = [str(primary_expected_slack), str(independent_expected_slack)]
    add(
        "cross_route",
        "strict_slack_fixture",
        actual_slacks == expected_slacks and primary_expected_slack == independent_expected_slack > 0,
        actual_slacks,
        expected_slacks,
    )
    add("cross_route", "source_weight", [primary_var.get("source_coefficient"), independent_var.get("source_weight")] == ["9/20", "9/20"], [primary_var.get("source_coefficient"), independent_var.get("source_weight")], ["9/20", "9/20"])
    add("cross_route", "gap_weight", [primary_var.get("gap_coefficient"), independent_var.get("gap_weight")] == ["9/10", "9/10"], [primary_var.get("gap_coefficient"), independent_var.get("gap_weight")], ["9/10", "9/10"])
    add("cross_route", "assembly_metadata", primary_var.get("exact_h_a_packet_assembly") is True and independent_var.get("exact_h_a_packet_assembly") is True, [primary_var.get("exact_h_a_packet_assembly"), independent_var.get("exact_h_a_packet_assembly")], [True, True])
    add("cross_route", "overlap_open", primary_var.get("full_overlap_src") is False and independent_var.get("overlap_src") is False, [primary_var.get("full_overlap_src"), independent_var.get("overlap_src")], [False, False])
    add("cross_route", "nelson_open", primary_var.get("nelson") is False and independent_var.get("nelson") is False, [primary_var.get("nelson"), independent_var.get("nelson")], [False, False])
    add("cross_route", "ownerwise_subdivision_not_claimed", independent_var.get("ownerwise_subdivision_invariance") is False, independent_var.get("ownerwise_subdivision_invariance"), False)
    add("cross_route", "r103_visitwise_not_extended", independent_var.get("visitwise_r103_extension") is False, independent_var.get("visitwise_r103_extension"), False)
    add("cross_route", "sector_a_open", independent_var.get("sector_a") is False, independent_var.get("sector_a"), False)

    imports = imported_roots(INDEPENDENT)
    forbidden_imports = sorted(imports & {"numpy", "sympy", "scipy"})
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    add("independence", "forbidden_imports", not forbidden_imports, forbidden_imports, [])
    add("independence", "no_primary_import", PRIMARY.stem not in independent_text, PRIMARY.stem if PRIMARY.stem in independent_text else "absent", "absent")
    add("independence", "fraction_engine", "from fractions import Fraction" in independent_text, "Fraction" if "from fractions import Fraction" in independent_text else "missing", "Fraction")

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest", "manifest_json", False, repr(error), "valid JSON")
    else:
        add("manifest", "manifest_json", True, "valid JSON", "valid JSON")
    add("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "tier_t4", [manifest.get("tier_before"), manifest.get("tier_after")] == ["T4", "T4"], [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest", "proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)

    sources = manifest.get("sources", {}) if isinstance(manifest.get("sources"), dict) else {}
    for label, path in (
        ("primary", PRIMARY),
        ("independent", INDEPENDENT),
        ("verifier", Path(__file__).resolve()),
        ("proof_note", NOTE),
    ):
        entry = sources.get(label, {}) if isinstance(sources.get(label), dict) else {}
        add("manifest", f"{label}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
        expected_hash = digest(path) if path.is_file() else "file"
        add("manifest", f"{label}_hash", path.is_file() and entry.get("sha256") == expected_hash, entry.get("sha256"), expected_hash)
        expected_version = "1.0" if label == "proof_note" else source_version(path)
        add("manifest", f"{label}_version", entry.get("version") == expected_version, entry.get("version"), expected_version)

    authority_root = manifest.get("authority", {}) if isinstance(manifest.get("authority"), dict) else {}
    for label, filename in AUTHORITY_MANIFESTS.items():
        path = CLAIM_DIR / filename
        entry = authority_root.get(label, {}) if isinstance(authority_root.get(label), dict) else {}
        manifest_entry = entry.get("manifest", {}) if isinstance(entry.get("manifest"), dict) else {}
        add("authority", f"{label}_manifest_exists", path.is_file(), repo_path(path), "file")
        add("authority", f"{label}_manifest_path", manifest_entry.get("path") == repo_path(path), manifest_entry.get("path"), repo_path(path))
        add("authority", f"{label}_manifest_hash", path.is_file() and manifest_entry.get("sha256") == digest(path), manifest_entry.get("sha256"), digest(path) if path.is_file() else "file")
        try:
            result_path = authority_result_path(path)
        except Exception as error:
            result_path = None
            add("authority", f"{label}_manifest_contract", False, repr(error), "readable")
        else:
            add("authority", f"{label}_manifest_contract", True, "readable", "readable")
        result_entry = entry.get("result") if isinstance(entry, dict) else None
        if result_path is None:
            add("authority", f"{label}_grandfathered_result", result_entry is None, result_entry, None)
        else:
            result_entry = result_entry if isinstance(result_entry, dict) else {}
            add("authority", f"{label}_result_exists", result_path.is_file(), repo_path(result_path), "file")
            add("authority", f"{label}_result_path", result_entry.get("path") == repo_path(result_path), result_entry.get("path"), repo_path(result_path))
            add("authority", f"{label}_result_hash", result_path.is_file() and result_entry.get("sha256") == digest(result_path), result_entry.get("sha256"), digest(result_path) if result_path.is_file() else "file")
            try:
                authority_record = load_json(result_path)
            except Exception as error:
                add("authority", f"{label}_result_pass", False, repr(error), "PASS")
            else:
                add("authority", f"{label}_result_pass", result_passes(authority_record), authority_record.get("status"), "PASS")

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.is_file() else ""
    note_scan = normalized(note_text)
    add("proof_note", "exists", NOTE.is_file(), repo_path(NOTE), "file")
    for index, token in enumerate(NOTE_TOKENS):
        add("proof_note", f"token_{index:02d}", token in note_scan, token if token in note_scan else "missing", token)
    add("proof_note", "no_replacement", "\ufffd" not in note_text, note_text.count("\ufffd"), 0)
    add("proof_note", "fragment", "\\documentclass" not in note_text, "fragment", "fragment")

    add("proof_pdf", "exists", PDF.is_file(), repo_path(PDF), "file")
    page_count = 0
    fields = -1
    nonempty_pages = 0
    pdf_text = ""
    if PDF.is_file():
        reader = PdfReader(PDF)
        page_count = len(reader.pages)
        fields = len(reader.get_fields() or {})
        page_texts = [(page.extract_text() or "") for page in reader.pages]
        nonempty_pages = sum(bool(value.strip()) for value in page_texts)
        pdf_text = normalized("\n".join(page_texts))
    add("proof_pdf", "page_count_positive", page_count > 0, page_count, ">0")
    add("proof_pdf", "all_pages_nonempty", nonempty_pages == page_count and page_count > 0, nonempty_pages, page_count)
    add("proof_pdf", "no_fields", fields == 0, fields, 0)
    add("proof_pdf", "title", "Fixed-chart progressive complete-owner assembly" in pdf_text, "present" if "Fixed-chart progressive complete-owner assembly" in pdf_text else "missing", "present")
    footer_tokens = ("R-104", "ALGEBRAIC-ENDPOINT-IDENTITY", "Sector-A closure")
    add("proof_pdf", "scope_footer", all(token in pdf_text for token in footer_tokens), [token in pdf_text for token in footer_tokens], [True, True, True])
    proof_pdf = manifest.get("proof_pdf", {}) if isinstance(manifest.get("proof_pdf"), dict) else {}
    add("proof_pdf", "manifest_path", proof_pdf.get("path") == repo_path(PDF), proof_pdf.get("path"), repo_path(PDF))
    add("proof_pdf", "manifest_hash", PDF.is_file() and proof_pdf.get("sha256") == digest(PDF), proof_pdf.get("sha256"), digest(PDF) if PDF.is_file() else "file")
    add("proof_pdf", "manifest_pages", proof_pdf.get("pages") == page_count and page_count > 0, proof_pdf.get("pages"), page_count)
    add("proof_pdf", "manifest_form", proof_pdf.get("form_check") == "PASS", proof_pdf.get("form_check"), "PASS")
    add("proof_pdf", "manifest_overfull", proof_pdf.get("overfull_hbox_count") == 0, proof_pdf.get("overfull_hbox_count"), 0)
    add("proof_pdf", "manifest_visual_qa", proof_pdf.get("visual_qa") == "PASS", proof_pdf.get("visual_qa"), "PASS")

    exploration_rows: dict[str, dict[str, Any]] = {}
    exploration_path = REPO / "explorations/log.jsonl"
    for line in exploration_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("id") in EXPLORATIONS:
            exploration_rows[record["id"]] = record
    for exploration, verdict in EXPLORATIONS.items():
        record = exploration_rows.get(exploration, {})
        add("explorations", f"{exploration}_present", bool(record), record.get("id"), exploration)
        add("explorations", f"{exploration}_verdict", record.get("verdict") == verdict, record.get("verdict"), verdict)
        add("explorations", f"{exploration}_result_ref", "R-104" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), "contains R-104")

    negative_text = normalized((REPO / "negative-results/registry.md").read_text(encoding="utf-8"))
    for index, token in enumerate((NEGATIVE_ID, "anticipative heat", "G^2", "(G^2-3)^2")):
        add("negative", f"token_{index}", token in negative_text, token if token in negative_text else "missing", token)

    surface_tokens = {
        "results_ledger": (REPO / "RESULTS-LEDGER.md", ("R-104", "Douglas-slack", "OVERLAP_src")),
        "claim_card": (CLAIM_DIR / "claim.md", (RESULT_ID, "R-104", "EXP-000262")),
        "gates": (REPO / "claims/GATES.md", ("R-104", "FIXED-CHART", "OVERLAP_src")),
        "roadmap": (REPO / "ROADMAP.md", ("R-104", "fixed-chart", "OVERLAP_src")),
        "todo": (REPO / "TODO.md", ("T-050", "R-104", "OVERLAP_src")),
        "changelog": (REPO / "CHANGELOG.md", ("R-104", "fixed-chart", "Douglas")),
        "proof_map": (REPO / "theory/proof-evidence-map.md", ("R-104", "EXP-000260", "EXP-000262")),
        "main_proof": (REPO / "theory/main-proof-line.md", ("R-104", "fixed source chart", "OVERLAP_src")),
        "sector_readme": (REPO / "theory/sector-A-foundation/README.md", ("R-104", "fixed source chart", "Sector A remains open")),
        "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("1.7.7", "R-104", "OVERLAP_src")),
    }
    for label, (path, tokens) in surface_tokens.items():
        text = normalized(path.read_text(encoding="utf-8")) if path.is_file() else ""
        add("surfaces", f"{label}_exists", path.is_file(), repo_path(path), "file")
        for index, token in enumerate(tokens):
            add("surfaces", f"{label}_token_{index}", token in text, token if token in text else "missing", token)

    try:
        status = load_json(CLAIM_DIR / "status.json")
    except Exception as error:
        status = {}
        add("surfaces", "status_json", False, repr(error), "valid JSON")
    else:
        add("surfaces", "status_json", True, "valid JSON", "valid JSON")
    add("surfaces", "status_tier", status.get("tier") == "T4", status.get("tier"), "T4")
    status_scan = normalized(json.dumps(status, ensure_ascii=False))
    for token in ("R-104", "fixed-chart", "Douglas", "OVERLAP_src", "EXP-000262"):
        add("surfaces", f"status_{re.sub('[^a-z0-9]+', '_', token.lower()).strip('_')}", token in status_scan, token if token in status_scan else "missing", token)

    contract = manifest.get("run_contract", {}) if isinstance(manifest.get("run_contract"), dict) else {}
    canonical_command = contract.get("command", "")
    add("surfaces", "status_reproduction", status.get("reproduction", {}).get("command") == canonical_command, status.get("reproduction", {}).get("command"), canonical_command)
    add("contract", "primary_count", contract.get("primary_assertions") == primary.get("assertions_total") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent_count", contract.get("independent_assertions") == independent.get("assertions_total") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    for label, expected_schema in (
        ("primary", primary.get("schema")),
        ("independent", independent.get("schema")),
        ("integrated", "tect/a13-lossless-progressive-complete-owner-assembly-heat-boundary-integrated/1.0"),
    ):
        add("contract", f"{label}_schema", contract.get(f"{label}_schema") == expected_schema, contract.get(f"{label}_schema"), expected_schema)
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT), ("integrated", OUTPUT)):
        add("contract", f"{label}_output", contract.get(f"{label}_output") == repo_path(path), contract.get(f"{label}_output"), repo_path(path))

    consequence = manifest.get("consequence", {}) if isinstance(manifest.get("consequence"), dict) else {}
    consequence_expectations = {
        "fixed_chart_owner_defect_zero": True,
        "representation_preserving_subdivision_total_invariance": True,
        "ownerwise_subdivision_invariance": False,
        "physical_source_action_douglas_slack_identity": True,
        "douglas_slack_nonnegative": True,
        "exact_h_a_packet_assembly": True,
        "anticipative_heat_general_extension": False,
        "r103_visitwise_estimates_extended": False,
        "full_overlap_src": False,
        "nelson": False,
        "sector_a_closure": False,
    }
    for key, expected in consequence_expectations.items():
        add("consequence", key, consequence.get(key) is expected, consequence.get(key), expected)

    not_established = manifest.get("claims_not_established", {}) if isinstance(manifest.get("claims_not_established"), dict) else {}
    for key in ("full_overlap_src", "nelson", "cutoff_removal", "floor_removal", "interacting_measure", "sector_a_closure", "tier_promotion"):
        add("no_overclaim", key, not_established.get(key) is False, not_established.get(key), False)

    final_integrated_count = len(rows) + 2
    add("contract", "integrated_count", contract.get("integrated_assertions") == final_integrated_count, contract.get("integrated_assertions"), final_integrated_count)
    aggregate = primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + final_integrated_count
    add("contract", "aggregate_count", contract.get("aggregate_assertions") == aggregate, contract.get("aggregate_assertions"), aggregate)

    passed = sum(row["status"] == "PASS" for row in rows)
    if count_only:
        print(f"INTEGRATED ASSERTIONS PLANNED: {len(rows)}")
        print(f"CURRENT PASS: {passed}/{len(rows)}")
        return 0

    payload = {
        "schema": "tect/a13-lossless-progressive-complete-owner-assembly-heat-boundary-integrated/1.0",
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
            "proof_note": digest(NOTE) if NOTE.is_file() else None,
            "proof_pdf": digest(PDF) if PDF.is_file() else None,
            "manifest": digest(MANIFEST) if MANIFEST.is_file() else None,
        },
        "run_summary": {
            "primary": primary.get("assertions_total"),
            "independent": independent.get("assertions_total"),
            "integrated": len(rows),
            "aggregate": primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + len(rows),
        },
        "no_overclaim": (
            "R-104 proves only zero fixed-chart endpoint-owner defect, recombined-total invariance under "
            "representation-preserving subdivision, and the exact nonnegative Douglas-slack relation between "
            "physical and source actions in the declared predictable deterministic-PSD-heat scope. It proves "
            "no per-subvisit estimate, arbitrary anticipative-heat extension, uniform OVERLAP_src lower bound, "
            "Nelson estimate, removal, interacting measure, tier promotion, or Sector A closure."
        ),
    }
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed", "run_summary")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
