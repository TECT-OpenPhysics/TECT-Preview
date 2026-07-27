#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-103 regular H_N/REG package."""

from __future__ import annotations

__version__ = "1.0.1"
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
RESULT_ID = "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_regular_complete_packet_ownership_hn_reg_closure.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_regular_complete_packet_ownership_hn_reg_closure_independent.py"
NOTE = CLAIM_DIR / "notes/classii-regular-complete-packet-ownership-hn-reg-closure-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-regular-complete-packet-ownership-hn-reg-closure-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-closure/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-regular-complete-packet-ownership-hn-reg-closure/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-regular-complete-packet-ownership-hn-reg-closure/result.json"

AUTHORITY_MANIFESTS = {
    "r063": "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r071": "classii_one_form_sobolev_linear_closure_manifest.json",
    "r076": "classii_signed_transport_besov_bregman_resonance_manifest.json",
    "r078": "classii_hessian_difference_safe_packet_doob_bracket_manifest.json",
    "r079": "classii_full_safe_packet_frame_current_doob_manifest.json",
    "r080": "classii_low_object_far_square_progressive_boundary_manifest.json",
    "r083": "classii_controlled_polynomial_cfar_linear_pf_forest_manifest.json",
    "r084": "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json",
    "r085": "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
    "r086": "classii_rational_translated_wick_payload_comparable_reduction_manifest.json",
    "r088": "classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json",
    "r091": "classii_projected_cartan_full_frame_temporal_boundary_manifest.json",
    "r092": "classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
    "r093": "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r094": "classii_root_local_gram_secant_feedback_boundary_manifest.json",
    "r096": "classii_low_hermite_wick_predictable_baseline_reduction_manifest.json",
    "r097": "classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json",
    "r099": "classii_extended_state_cartan_doob_rational_recovery_manifest.json",
    "r100": "classii_owner_gauge_heat_centered_covariance_debt_reduction_manifest.json",
    "r101": "classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction_manifest.json",
    "r102": "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
}

EXPECTED_MODULES = {
    "cartan_far": ["cartan_output"],
    "linear_near": ["linear_rows", "linear_heat_trace_forest"],
    "rational_raw_wick_residual": ["raw_wick_future_residual", "rational_heat_trace_forest", "full_wick_secant"],
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

NOTE_TOKENS = (
    "R-103",
    "evidence-anchor: theorem-4.1-regular-complete-owner-partition",
    "evidence-anchor: theorem-5.1-complete-regular-hn-closure",
    "evidence-anchor: theorem-6.1-regular-reg-closure",
    "1/3520",
    "3/800",
    "1/3080",
    "3/700",
    "197/440",
    "3/25",
    "standalone R-085 averaged Cartan atom (4.11) is not proved",
    "superseded as necessary premises for regular REG",
    "progressive/revisit H_A",
    "T4 / T4; no promotion",
)

EXPLORATIONS = {"EXP-000258": "advanced", "EXP-000259": "advanced"}


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
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return None if match is None else match.group(1)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value)


def result_passes(record: dict[str, Any]) -> bool:
    total = record.get("assertions_total")
    current = (
        str(record.get("status", "")).upper() == "PASS"
        and isinstance(total, int)
        and total > 0
        and record.get("assertions_passed") == total
        and record.get("assertions_failed", 0) == 0
    )
    summary = record.get("summary", {}) if isinstance(record.get("summary"), dict) else {}
    legacy_total = summary.get("total")
    legacy = (
        isinstance(legacy_total, int)
        and legacy_total > 0
        and summary.get("passed") == legacy_total
        and summary.get("failed") == 0
        and str(record.get("verdict", "")).upper().endswith("-PASS")
    )
    return current or legacy


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


def authority_paths(manifest_path: Path) -> tuple[Path, Path | None]:
    manifest = load_json(manifest_path)
    contract = manifest.get("run_contract", {})
    output = contract.get("integrated_output") if isinstance(contract, dict) else None
    return manifest_path, (REPO / output if output else None)


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
        ("primary", PRIMARY, PRIMARY_RESULT, 137),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT, 69),
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
    for name in (
        "atomic_owner_uniqueness",
        "seven_near_modules",
        "near_atomic_owner_uniqueness",
        "eta_star",
        "zeta_star",
        "eta_module_share",
        "zeta_module_share",
        "eta_simplex",
        "zeta_simplex",
        "source_reserve",
        "sextic_reserve",
        "cartan_separation_admissible",
        "gap_c15",
    ):
        row = assertion(primary, name)
        add("load_bearing", f"primary_{name}", row.get("status") == "PASS", row.get("status"), "PASS")
    for seed in (1, 2, 4, 7):
        for stem in (
            "endpoint_reassembly",
            "raw_factor_mutant_rejected",
            "shifted_sign_mutant_rejected",
            "square_factor_mutant_rejected",
        ):
            name = f"{stem}_seed_{seed}"
            row = assertion(primary, name)
            add("load_bearing", f"primary_{name}", row.get("status") == "PASS", row.get("status"), "PASS")
    for name in (
        "singular_psd_endpoint_reassembly",
        "singular_psd_rank",
        "singular_psd_terminal_square_nonnegative",
        "zero_psd_endpoint_reassembly",
        "zero_psd_rank",
        "zero_psd_terminal_square_nonnegative",
        "r088_comparison_formula",
        "r093_action_formula",
    ):
        row = assertion(primary, name)
        add("load_bearing", f"primary_{name}", row.get("status") == "PASS", row.get("status"), "PASS")
    for name in (
        "owner_injection",
        "near_owner_injection",
        "required_owner_coverage",
        "eta_piece_sum",
        "zeta_piece_sum",
        "eta_piece_exact",
        "zeta_piece_exact",
        "eta_near_piece_sum",
        "zeta_near_piece_sum",
        "eta_near_piece_exact",
        "zeta_near_piece_exact",
        "source_reserve_exact",
        "sextic_reserve_exact",
        "derived_cartan_separation",
        "derived_gap",
    ):
        row = assertion(independent, name)
        add("load_bearing", f"independent_{name}", row.get("status") == "PASS", row.get("status"), "PASS")
    for seed in (3, 5, 8, 13, 21):
        for stem in (
            "scalar_endpoint",
            "scalar_raw_factor_mutant",
            "scalar_shifted_sign_mutant",
            "scalar_square_factor_mutant",
        ):
            name = f"{stem}_{seed}"
            row = assertion(independent, name)
            add("load_bearing", f"independent_{name}", row.get("status") == "PASS", row.get("status"), "PASS")
    for name in (
        "scalar_zero_psd_endpoint",
        "scalar_zero_psd_square",
        "independent_r088_comparison_formula",
        "independent_r093_action_formula",
    ):
        row = assertion(independent, name)
        add("load_bearing", f"independent_{name}", row.get("status") == "PASS", row.get("status"), "PASS")

    primary_diag = primary.get("diagnostics", {})
    independent_diag = independent.get("diagnostics", {})
    add("cross_route", "module_partition", primary_diag.get("atomic_owners") == EXPECTED_MODULES, primary_diag.get("atomic_owners"), EXPECTED_MODULES)
    expected_atoms = {atom for atoms in EXPECTED_MODULES.values() for atom in atoms}
    add("cross_route", "independent_owner_partition", set(independent_diag.get("atomic_owners", [])) == expected_atoms, independent_diag.get("atomic_owners"), sorted(expected_atoms))
    add("cross_route", "primary_refunds", set(primary_diag.get("refunded", [])) == EXPECTED_REFUNDS, primary_diag.get("refunded"), sorted(EXPECTED_REFUNDS))
    add("cross_route", "independent_refunds", set(independent_diag.get("forbidden", [])) == EXPECTED_REFUNDS, independent_diag.get("forbidden"), sorted(EXPECTED_REFUNDS))
    for primary_key, independent_key, expected in (
        ("eta_star", "eta", "1/440"),
        ("zeta_star", "zeta", "3/100"),
        ("eta_each", "eta_piece", "1/3520"),
        ("zeta_each", "zeta_piece", "3/800"),
        ("eta_near_each", "eta_near_piece", "1/3080"),
        ("zeta_near_each", "zeta_near_piece", "3/700"),
        ("source_reserve", "source_reserve", "197/440"),
        ("sextic_reserve", "sextic_reserve", "3/25"),
    ):
        actual = [primary_diag.get("budget", {}).get(primary_key), independent_diag.get("budget", {}).get(independent_key)]
        add("cross_route", f"budget_{primary_key}", actual == [expected, expected], actual, [expected, expected])
    primary_endpoint = primary_diag.get("endpoint_cases", [])
    independent_endpoint = independent_diag.get("endpoint_rows", [])
    add("cross_route", "endpoint_case_counts", [len(primary_endpoint), len(independent_endpoint)] == [4, 5], [len(primary_endpoint), len(independent_endpoint)], [4, 5])
    add("cross_route", "terminal_square_reserved", "terminal_square" in EXPECTED_MODULES["rational_shifted_current"], EXPECTED_MODULES["rational_shifted_current"], "contains terminal_square")

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
        manifest_entry = entry.get("manifest", {}) if isinstance(entry, dict) else {}
        add("authority", f"{label}_manifest_exists", path.is_file(), repo_path(path), "file")
        add("authority", f"{label}_manifest_path", manifest_entry.get("path") == repo_path(path), manifest_entry.get("path"), repo_path(path))
        add("authority", f"{label}_manifest_hash", path.is_file() and manifest_entry.get("sha256") == digest(path), manifest_entry.get("sha256"), digest(path) if path.is_file() else "file")
        try:
            _, result_path = authority_paths(path)
        except Exception as error:
            result_path = None
            add("authority", f"{label}_manifest_contract", False, repr(error), "readable")
        else:
            add("authority", f"{label}_manifest_contract", True, "readable", "readable")
        result_entry = entry.get("result") if isinstance(entry, dict) else None
        if result_path is None:
            add("authority", f"{label}_grandfathered_result", result_entry is None, result_entry, None)
        else:
            add("authority", f"{label}_result_exists", result_path.is_file(), repo_path(result_path), "file")
            result_entry = result_entry if isinstance(result_entry, dict) else {}
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
    pdf_text = ""
    if PDF.is_file():
        reader = PdfReader(PDF)
        page_count = len(reader.pages)
        fields = len(reader.get_fields() or {})
        pdf_text = normalized("\n".join((page.extract_text() or "") for page in reader.pages))
    add("proof_pdf", "nonempty_pages", page_count > 0, page_count, ">0")
    add("proof_pdf", "no_fields", fields == 0, fields, 0)
    add("proof_pdf", "title", "Regular complete-packet ownership" in pdf_text, "present" if "Regular complete-packet ownership" in pdf_text else "missing", "present")
    add("proof_pdf", "scope_footer", all(token in pdf_text for token in ("R-103", "complete regular", "Sector-A closure")), [token in pdf_text for token in ("R-103", "complete regular", "Sector-A closure")], [True, True, True])
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
        add("explorations", f"{exploration}_result_ref", "R-103" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), "contains R-103")

    surface_tokens = {
        "results_ledger": (REPO / "RESULTS-LEDGER.md", ("R-103", "complete regular H_N", "progressive/revisit")),
        "claim_card": (CLAIM_DIR / "claim.md", (RESULT_ID, "EXP-000259", "complete regular")),
        "roadmap": (REPO / "ROADMAP.md", ("R-103", "complete regular `H_N` and `REG`", "progressive/revisit")),
        "todo": (REPO / "TODO.md", ("T-050", "R-103", "progressive/revisit")),
        "changelog": (REPO / "CHANGELOG.md", ("R-103", "complete-owner", "progressive/revisit")),
        "proof_map": (REPO / "theory/proof-evidence-map.md", ("R-103", "EXP-000258", "EXP-000259")),
        "main_proof": (REPO / "theory/main-proof-line.md", ("R-103", "complete regular", "progressive/revisit")),
        "sector_readme": (REPO / "theory/sector-A-foundation/README.md", ("R-103", "complete regular", "progressive/revisit")),
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
    for token in ("R-103", "complete regular H_N", "progressive/revisit H_A", "EXP-000259"):
        add("surfaces", f"status_{re.sub('[^a-z0-9]+', '_', token.lower()).strip('_')}", token in status_scan, token if token in status_scan else "missing", token)
    canonical_command = manifest.get("run_contract", {}).get("command", "")
    add("surfaces", "status_reproduction", status.get("reproduction", {}).get("command") == canonical_command, status.get("reproduction", {}).get("command"), canonical_command)

    contract = manifest.get("run_contract", {}) if isinstance(manifest.get("run_contract"), dict) else {}
    add("contract", "primary_count", contract.get("primary_assertions") == primary.get("assertions_total") == 137, contract.get("primary_assertions"), 137)
    add("contract", "independent_count", contract.get("independent_assertions") == independent.get("assertions_total") == 69, contract.get("independent_assertions"), 69)
    for label, expected_schema in (
        ("primary", primary.get("schema")),
        ("independent", independent.get("schema")),
        ("integrated", "tect/a13-regular-complete-packet-ownership-hn-reg-closure-integrated/1.0"),
    ):
        add("contract", f"{label}_schema", contract.get(f"{label}_schema") == expected_schema, contract.get(f"{label}_schema"), expected_schema)
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT), ("integrated", OUTPUT)):
        add("contract", f"{label}_output", contract.get(f"{label}_output") == repo_path(path), contract.get(f"{label}_output"), repo_path(path))
    consequence = manifest.get("consequence", {}) if isinstance(manifest.get("consequence"), dict) else {}
    consequence_expectations = {
        "complete_owner_partition_regular": True,
        "complete_h_n_regular": True,
        "reg_regular": True,
        "terminal_square_reserved": True,
        "naked_posterior_covariance_bracket": False,
        "standalone_r085_4_11": False,
        "standalone_old_6_5": False,
        "arbitrary_progressive_revisit_h_a": False,
        "full_overlap_src": False,
        "nelson": False,
        "sector_a_closure": False,
    }
    for key, expected in consequence_expectations.items():
        add("consequence", key, consequence.get(key) is expected, consequence.get(key), expected)

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
        "schema": "tect/a13-regular-complete-packet-ownership-hn-reg-closure-integrated/1.0",
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
            "R-103 proves the complete-owner lower form, complete H_N, and REG only for the finite-cutoff, "
            "fixed-floor, deterministic-PSD-heat regular annular mutually orthogonal strict-past no-revisit "
            "class. It does not prove naked posterior-bracket positivity, standalone R-085 (4.11), old "
            "(6.5), arbitrary progressive/revisit H_A, OVERLAP_src, Nelson, removals, a measure, T5--T7, "
            "or Sector A closure."
        ),
    }
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed", "run_summary")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
