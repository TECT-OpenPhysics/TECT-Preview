#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-099 A13 package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

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
RESULT_ID = "A13-CLASSII-EXTENDED-STATE-CARTAN-DOOB-RATIONAL-RECOVERY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_extended_state_cartan_doob_rational_recovery.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_extended_state_cartan_doob_rational_recovery_independent.py"
NOTE = CLAIM_DIR / "notes/classii-extended-state-cartan-doob-rational-recovery-260727-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-extended-state-cartan-doob-rational-recovery-260727-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_extended_state_cartan_doob_rational_recovery_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-27-primary-extended-state-cartan-doob-rational-recovery/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-27-independent-extended-state-cartan-doob-rational-recovery/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-27-integrated-extended-state-cartan-doob-rational-recovery/result.json"

AUTHORITY = {
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
    "r087": (
        CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json",
    ),
    "r092": (
        CLAIM_DIR / "classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-normalized-cartan-perspective-covariance-frontier/result.json",
    ),
    "r097": (
        CLAIM_DIR / "classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-global-gram-terminalization-covariance-deficit-reduction/result.json",
    ),
    "r098": (
        CLAIM_DIR / "classii_signed_first_cartan_rational_ridge_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-signed-first-cartan-rational-ridge-boundary/result.json",
    ),
}

NEGATIVE_RESULTS = (
    "NG-2026-07-27-A13-PROGRESSIVE-REVISIT-CARTAN-MIXED-PAYLOAD",
    "NG-2026-07-27-A13-ABSOLUTE-LAST-ROOT-FRAME-TRANSFER",
)
EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(226, 234))
EXPLORATION_VERDICTS = {
    "EXP-000226": "advanced",
    "EXP-000227": "failed",
    "EXP-000228": "failed",
    "EXP-000229": "advanced",
    "EXP-000230": "advanced",
    "EXP-000231": "failed",
    "EXP-000232": "advanced",
    "EXP-000233": "inconclusive",
}
NOTE_TOKENS = (
    "R-099",
    "evidence-anchor: theorem-3.1-extended-state-cartan-telescope",
    "The heat-change bracket is mandatory",
    "D_z(\\Delta F_S)(0)={4S\\over e}",
    "evidence-anchor: theorem-4.1-progressive-revisit-mixed-payload-no-go",
    "does not exclude an $\\eta X$ allowance",
    "evidence-anchor: theorem-5.1-causal-doob-hardy-one-use",
    "h_k-\\E_{j_0-1}h_k",
    "defect in R-098",
    "evidence-anchor: theorem-6.1-complete-frame-ordered-reveal",
    "does not identify it literally with the R-097 $J_B$ or the R-063 forest",
    "need not be injective",
    "no general sign guarantee",
    "evidence-anchor: theorem-7.1-rational-five-family-two-sided-form",
    "B=B^T\\succeq0",
    "evidence-anchor: theorem-8.1-payment-gauge-identity",
    "S_R+{1\\over2}\\mathfrak C_{\\rm post}-P_R-\\E W_0",
    "NG-2026-07-27-A13-PROGRESSIVE-REVISIT-CARTAN-MIXED-PAYLOAD",
    "NG-2026-07-27-A13-ABSOLUTE-LAST-ROOT-FRAME-TRANSFER",
    "Sector-A closure",
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return None if match is None else match.group(1)


def result_passes(record: dict[str, Any]) -> bool:
    total = record.get("assertions_total")
    failed = record.get("assertions_failed")
    return bool(
        record.get("status") == "PASS"
        and isinstance(total, int)
        and total > 0
        and record.get("assertions_passed") == total
        and (failed is None or failed == 0)
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

    # Fresh execution of both independent routes.
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
        add("execution", f"{label}_fresh_result", result_path.exists(), repo_path(result_path), "fresh atomic output")
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
        "complete_edge_telescope_0",
        "extended_state_closed_loop_zero",
        "drop_heat_compensator_mutant_fails",
        "trace_free_cubic_heat_derivative_exact",
        "missing_factor_two_mutant_rejected",
        "production_harmonic_coefficient_positive",
        "mixed_payload_ratio_diverges",
        "distinct_root_hs_direct_sum",
        "last_root_identity_1",
        "weighted_hardy_bound",
        "variance_corollary",
        "hoeffding_owned_at_max_support",
        "coordinate_influences_count_support_size",
        "dyadic_support_weight_not_divergent",
        "hardy_constant_one_sharp_limit",
        "spatial_decay_r6",
        "frame_reveal_identity_1",
        "quadratic_covariance_chain_3",
        "cross_doob_terminal_identity",
        "same_level_frame_mutant_diverges",
        "absolute_secant_square_not_budgeted",
        "family_5_moment_available",
        "young_family_5_sample_4",
        "exact_identity_15",
        "omit_payment_mutant_rejected",
        "shifted_negative_11.0",
        "lower_only_mutant_unbounded",
    )
    for name in primary_names:
        row = assertion(primary, name)
        add("primary_certificates", f"primary_{name}", row.get("status") == "PASS", row.get("actual"), "PASS")

    independent_names = (
        "no_numerical_package_import",
        "does_not_import_primary",
        "complete_exact_0",
        "source_defect_exact_2",
        "drop_heat_mutant_nonzero",
        "d_delta_f_exact",
        "wrong_generator_factor_rejected",
        "nonzero_harmonic_exact",
        "ratio_strict_growth",
        "last_root_exact_1",
        "weighted_cauchy_bound_exact",
        "variance_corollary_exact",
        "max_support_ownership",
        "coordinate_membership_multiplicity",
        "weighted_membership_still_summable",
        "sharp_ratio_exceeds_nine_tenths",
        "spatial_exponents_exact",
        "frame_identity_1",
        "quadratic_chain_3",
        "cross_doob_exact",
        "xi_fourth_moment_four",
        "frame_shift_ratio_exponential",
        "square_growth_32",
        "family_available_5",
        "young_numeric_5",
        "non_diagonal_fraction_identity",
        "omit_payment_mutant_rejected",
        "taylor_remainder_minus_sixteen",
        "shifted_11/1",
        "lower_only_not_enough",
    )
    for name in independent_names:
        row = assertion(independent, name)
        add("independent_certificates", f"independent_{name}", row.get("status") == "PASS", row.get("actual"), "PASS")

    # Independence and source metadata.
    roots_independent = imported_roots(INDEPENDENT)
    add("independence", "independent_forbidden_packages_absent", roots_independent.isdisjoint({"numpy", "scipy", "sympy", "mpmath"}), sorted(roots_independent), "no numerical packages")
    add("independence", "independent_primary_import_absent", "a13_classii_extended_state_cartan_doob_rational_recovery" not in roots_independent, sorted(roots_independent), "primary absent")
    for label, path in (("primary", PRIMARY), ("independent", INDEPENDENT), ("verifier", Path(__file__).resolve())):
        add("source", f"{label}_exists", path.is_file(), repo_path(path), "file")
        add("source", f"{label}_version", source_version(path) is not None, source_version(path), "declared")

    # Manifest and authority pinning. Missing manifest still contributes a fixed count in --count-only mode.
    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest", "manifest_json", False, repr(error), "valid JSON")
    else:
        add("manifest", "manifest_json", True, "valid JSON", "valid JSON")
    add("manifest", "manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest", "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "manifest_tier_stays_t4", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest", "manifest_proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    sources = manifest.get("sources", {}) if isinstance(manifest.get("sources"), dict) else {}
    for label, path in (("primary", PRIMARY), ("independent", INDEPENDENT), ("verifier", Path(__file__).resolve()), ("proof_note", NOTE)):
        entry = sources.get(label, {}) if isinstance(sources.get(label), dict) else {}
        add("manifest", f"manifest_{label}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
        add("manifest", f"manifest_{label}_hash", path.is_file() and entry.get("sha256") == digest(path), entry.get("sha256"), digest(path) if path.is_file() else "file")
        expected_version = "1.0" if label == "proof_note" else source_version(path)
        add("manifest", f"manifest_{label}_version", entry.get("version") == expected_version, entry.get("version"), expected_version)
    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        authority_entry = manifest.get("authority", {}).get(label, {}) if isinstance(manifest.get("authority"), dict) else {}
        for kind, path in (("manifest", authority_manifest), ("result", authority_result)):
            entry = authority_entry.get(kind, {}) if isinstance(authority_entry, dict) else {}
            add("authority", f"{label}_{kind}_exists", path.is_file(), repo_path(path), "file")
            add("authority", f"{label}_{kind}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
            add("authority", f"{label}_{kind}_hash", path.is_file() and entry.get("sha256") == digest(path), entry.get("sha256"), digest(path) if path.is_file() else "file")
        try:
            authority_record = load_json(authority_result)
        except Exception as error:
            add("authority", f"{label}_result_pass", False, repr(error), "PASS")
        else:
            add("authority", f"{label}_result_pass", result_passes(authority_record), authority_record.get("status"), "PASS")

    # Note and PDF release surface.
    note_text = NOTE.read_text(encoding="utf-8") if NOTE.is_file() else ""
    add("proof_note", "note_exists", NOTE.is_file(), repo_path(NOTE), "file")
    for index, token in enumerate(NOTE_TOKENS):
        add("proof_note", f"note_token_{index:02d}", token in note_text, token if token in note_text else "missing", token)
    add("proof_note", "note_no_unicode_replacement", "\ufffd" not in note_text, note_text.count("\ufffd"), 0)
    add("proof_note", "note_no_documentclass", "\\documentclass" not in note_text, "fragment", "fragment")
    add("proof_pdf", "pdf_exists", PDF.is_file(), repo_path(PDF), "file")
    if PDF.is_file():
        reader = PdfReader(PDF)
        pdf_text = "\n".join((page.extract_text() or "") for page in reader.pages)
        page_count = len(reader.pages)
        field_count = len(reader.get_fields() or {})
        add("proof_pdf", "pdf_page_count", page_count == 10, page_count, 10)
        add("proof_pdf", "pdf_no_form_fields", field_count == 0, field_count, 0)
        add("proof_pdf", "pdf_title_text", "Extended-state Cartan telescope" in pdf_text, "title" if "Extended-state Cartan telescope" in pdf_text else "missing", "title")
        add("proof_pdf", "pdf_footer_text", "R-099" in pdf_text and "Sector-A closure" in pdf_text, ["R-099" in pdf_text, "Sector-A closure" in pdf_text], [True, True])
    else:
        for name, expected in (("pdf_page_count", 10), ("pdf_no_form_fields", 0), ("pdf_title_text", "title"), ("pdf_footer_text", [True, True])):
            add("proof_pdf", name, False, "missing PDF", expected)
    proof_pdf = manifest.get("proof_pdf", {}) if isinstance(manifest.get("proof_pdf"), dict) else {}
    add("proof_pdf", "manifest_pdf_path", proof_pdf.get("path") == repo_path(PDF), proof_pdf.get("path"), repo_path(PDF))
    add("proof_pdf", "manifest_pdf_hash", PDF.is_file() and proof_pdf.get("sha256") == digest(PDF), proof_pdf.get("sha256"), digest(PDF) if PDF.is_file() else "file")
    add("proof_pdf", "manifest_pdf_pages", proof_pdf.get("pages") == 10, proof_pdf.get("pages"), 10)
    add("proof_pdf", "manifest_pdf_overfull_zero", proof_pdf.get("overfull_hbox_count") == 0, proof_pdf.get("overfull_hbox_count"), 0)
    add("proof_pdf", "manifest_pdf_visual_qa", proof_pdf.get("visual_qa") == "PASS", proof_pdf.get("visual_qa"), "PASS")

    # Negative registry and exploration ledger.
    registry_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative in NEGATIVE_RESULTS:
        anchor = negative.lower()
        add("negative_results", f"negative_{anchor}_id", negative in registry_text, negative if negative in registry_text else "missing", negative)
        add("negative_results", f"negative_{anchor}_anchor", f'<a id="{anchor}"></a>' in registry_text, anchor, "anchor")
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
        add("explorations", f"{exploration}_result_ref", "R-099" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), "contains R-099")

    # Public surfaces and current frontier.
    surface_tokens = {
        "results_ledger": (REPO / "RESULTS-LEDGER.md", ("R-099", RESULT_ID, "causal Doob")),
        "claim_card": (CLAIM_DIR / "claim.md", (RESULT_ID, "EXP-000226", "EXP-000234")),
        "sector_a": (REPO / "theory/sectors/A.md", NEGATIVE_RESULTS),
        "proof_map": (REPO / "theory/proof-evidence-map.md", ("R-099", "EXP-000234")),
    }
    for label, (path, tokens) in surface_tokens.items():
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
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
    add("surfaces", "status_reproduction_command", "extended_state_cartan_doob_rational_recovery_verify.py" in status.get("reproduction", {}).get("command", ""), status.get("reproduction", {}).get("command"), "R-099 verifier")
    add("surfaces", "status_tier_t4", status.get("tier") == "T4", status.get("tier"), "T4")
    status_boundary = {
        "sector_open": "Sector A remain open" in status.get("statement", ""),
        "r099_scope": "R-099" in status.get("scope", ""),
        "r099_falsifier": "R-099" in status.get("falsifier", ""),
        "correction_record": "EXP-000234" in status.get("notes", ""),
    }
    add("surfaces", "status_sector_open", all(status_boundary.values()), status_boundary, {key: True for key in status_boundary})
    try:
        theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    except Exception as error:
        theorem_map = {}
        add("surfaces", "theorem_map_json", False, repr(error), "valid JSON")
    else:
        add("surfaces", "theorem_map_json", True, "valid JSON", "valid JSON")
    theorem_text = json.dumps(theorem_map, sort_keys=True)
    add("surfaces", "theorem_map_r099", "R-099" in theorem_text, "R-099" if "R-099" in theorem_text else "missing", "R-099")

    # Manifest run contract and honest consequence flags.
    contract = manifest.get("run_contract", {}) if isinstance(manifest.get("run_contract"), dict) else {}
    add("contract", "primary_count", contract.get("primary_assertions") == primary.get("assertions_total"), contract.get("primary_assertions"), primary.get("assertions_total"))
    add("contract", "independent_count", contract.get("independent_assertions") == independent.get("assertions_total"), contract.get("independent_assertions"), independent.get("assertions_total"))
    # Twelve fixed consequence checks follow.
    consequence = manifest.get("consequence", {}) if isinstance(manifest.get("consequence"), dict) else {}
    consequence_expectations = {
        "extended_state_signed_telescope": True,
        "progressive_terminal_mixed_only_extension": False,
        "causal_doob_hardy_one_use": True,
        "complete_frame_ordered_reveal": True,
        "absolute_frame_square_transfer": False,
        "rational_five_family_two_sided_form": True,
        "payment_gauge_identity": True,
        "production_posterior_lower_form": False,
        "rational_shifted_hessian_form": False,
        "complete_h_n": False,
        "full_overlap_src": False,
        "sector_a_closure": False,
    }
    for key, expected in consequence_expectations.items():
        add("consequence", key, consequence.get(key) is expected, consequence.get(key), expected)
    final_integrated_count = len(rows) + 1
    add("contract", "integrated_count", contract.get("integrated_assertions") == final_integrated_count, contract.get("integrated_assertions"), final_integrated_count)

    passed = sum(row["status"] == "PASS" for row in rows)
    if count_only:
        print(f"INTEGRATED ASSERTIONS PLANNED: {len(rows)}")
        print(f"CURRENT PASS: {passed}/{len(rows)}")
        return 0
    payload = {
        "schema": "tect/a13-extended-state-cartan-doob-rational-recovery-integrated/1.0",
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
            "The exact R-099 advances and scoped route exclusions pass. The production "
            "posterior/source-action lower form, rational (6.5), H_N, REG, OVERLAP_src, "
            "Nelson, measure construction, and Sector-A closure remain open."
        ),
    }
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed", "run_summary")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
