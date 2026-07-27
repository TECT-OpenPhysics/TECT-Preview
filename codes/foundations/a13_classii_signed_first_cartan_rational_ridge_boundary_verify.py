#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-098 A13 package."""

from __future__ import annotations

__version__ = "1.0.2"
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
RESULT_ID = "A13-CLASSII-SIGNED-FIRST-CARTAN-RATIONAL-RIDGE-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_signed_first_cartan_rational_ridge_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_signed_first_cartan_rational_ridge_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-signed-first-cartan-rational-ridge-boundary-260727-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-signed-first-cartan-rational-ridge-boundary-260727-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_signed_first_cartan_rational_ridge_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-27-primary-signed-first-cartan-rational-ridge-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-27-independent-signed-first-cartan-rational-ridge-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-27-integrated-signed-first-cartan-rational-ridge-boundary/result.json"

AUTHORITY = {
    "r066": (
        CLAIM_DIR / "classii_backward_heat_martingale_square_coupled_cartan_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-23-integrated-backward-heat-martingale-square-coupled-cartan-reduction/result.json",
    ),
    "r079": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r085": (
        CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json",
    ),
    "r088": (
        CLAIM_DIR / "classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-direct-root-cartan-schur-sequential-secant-rational-conditional-trace/result.json",
    ),
    "r092": (
        CLAIM_DIR / "classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-normalized-cartan-perspective-covariance-frontier/result.json",
    ),
    "r093": (
        CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-augmented-perspective-gibbs-gap-information-boundary/result.json",
    ),
    "r096": (
        CLAIM_DIR / "classii_low_hermite_wick_predictable_baseline_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-low-hermite-wick-predictable-baseline-reduction/result.json",
    ),
    "r097": (
        CLAIM_DIR / "classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-global-gram-terminalization-covariance-deficit-reduction/result.json",
    ),
}

NEGATIVE_RESULTS = (
    "NG-2026-07-27-A13-NONNEGATIVE-PER-SUBVISIT-CARTAN-ATOMIZATION",
)
EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(221, 226))
EXPLORATION_VERDICTS = {
    "EXP-000221": "advanced",
    "EXP-000222": "failed",
    "EXP-000223": "advanced",
    "EXP-000224": "failed",
    "EXP-000225": "inconclusive",
}
NOTE_TOKENS = (
    "R-098",
    "evidence-anchor: theorem-2.1-payment-split-superadditivity",
    "matching split of the matrix payment",
    "evidence-anchor: theorem-3.1-rational-ridge-deficit",
    "evidence-anchor: theorem-4.1-rational-standalone-recovery",
    "requires an \\emph{upper} form bound",
    "evidence-anchor: exact-rational-production-fibre-sign",
    "evidence-anchor: theorem-6.1-cartan-reverse-visit",
    "same fixed target heat and the same root derivative",
    "\\tag{6.7a}",
    "-{8\\over3^{k+1}}",
    "evidence-anchor: corollary-6.2-nonnegative-per-subvisit-no-go",
    "not yet an ANOVA decomposition",
    "2\\kappa_K^2",
    "NG-2026-07-27-A13-NONNEGATIVE-PER-SUBVISIT-CARTAN-ATOMIZATION",
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
    passed = record.get("assertions_passed")
    if record.get("status") == "PASS" and isinstance(total, int) and total > 0:
        failed = record.get("assertions_failed", 0)
        return passed == total and failed == 0
    verdict = str(record.get("verdict", "")).upper()
    for key in ("assertion_summary", "summary"):
        summary = record.get(key, {})
        if (
            isinstance(summary, dict)
            and isinstance(summary.get("total"), int)
            and summary.get("total", 0) > 0
            and summary.get("passed") == summary.get("total")
            and summary.get("failed") == 0
            and (verdict == "PASS" or verdict.endswith("-PASS"))
        ):
            return True
    return False


def result_total(record: dict[str, Any]) -> int:
    total = record.get("assertions_total")
    if isinstance(total, int):
        return total
    summary = record.get("assertion_summary", {})
    return summary.get("total", 0) if isinstance(summary, dict) else 0


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
        add("execution", f"{label}_fresh_result", result_path.exists(), repo_path(result_path), "fresh atomic output")
        try:
            record = load_json(result_path)
        except Exception as error:
            record = {}
            add("execution", f"{label}_result_load", False, repr(error), "valid JSON")
        else:
            add("execution", f"{label}_result_load", True, "valid JSON", "valid JSON")
        records[label] = record
        add("execution", f"{label}_result_pass", result_passes(record), record.get("status", record.get("verdict")), "all assertions PASS")
        add("execution", f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add("execution", f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    primary = records["primary"]
    independent = records["independent"]
    for name in (
        "payment_split_superadditivity_0",
        "same_payment_reuse_mutant_fails",
        "b_minus_exact",
        "three_atom_cpost_exact",
        "three_atom_gamma_one",
        "three_atom_q_zero_by_symmetry",
        "three_atom_r_zero_by_symmetry",
        "ridge_stationarity",
        "ridge_objective_identity",
        "standalone_f65_recovery",
        "unshifted_sign_mutant_fails",
        "half_epsilon_correct_power_2",
        "half_epsilon_k_plus_two_mutant_2",
        "finite_floor_radial_identity_eps_0.5_A_31.0_theta_0.71",
        "reverse_cancellation_A_11.0",
        "atom_square_scales_A2_11.0",
        "per_subvisit_ratio_grows_512",
        "frame_factor_three_envelope_holds",
        "drop_factor_three_mutant_fails",
        "resampling_equals_twice_conditional_variance",
        "two_root_interaction_counted_twice",
        "hardy_closed_form_7",
        "remove_k_smoothing_mutant_fails",
    ):
        row = assertion(primary, name)
        add("primary_certificates", f"primary_{name}", row.get("status") == "PASS", row.get("actual"), "PASS")
    for name in (
        "strict_gap_exact",
        "fractional_square_exact",
        "same_payment_reuse_mutant_rejected",
        "b_minus_exact",
        "selector_gamma_one",
        "selector_q_zero",
        "selector_r_zero",
        "selector_sign_direct",
        "full_frame_cpost_exact",
        "stationarity_exact",
        "objective_at_minimum",
        "owner_identity_exact_value",
        "unshifted_sign_mutant_rejected",
        "half_epsilon_exact_2",
        "wrong_power_mutant_2",
        "finite_floor_current_eps_0.7_A_17.0_theta_0.93",
        "same_heat_root_signed_cancellation",
        "distinct_heat_mutant_not_cancelled",
        "time_and_sine_half_factors_exact",
        "polarization_factor_three_holds",
        "deleted_factor_three_rejected",
        "independent_resample_identity",
        "hoeffding_multiplicity_identity",
        "hardy_trap_j0_2_k_7",
        "hardy_prefactor_retained",
        "include_j_equal_k_mutant_rejected",
    ):
        row = assertion(independent, name)
        add("independent_certificates", f"independent_{name}", row.get("status") == "PASS", row.get("actual"), "PASS")

    primary_diag = primary.get("diagnostics", {})
    independent_diag = independent.get("diagnostics", {})
    add("crosscheck", "rational_sign_matches", primary_diag.get("rational_three_atom_cpost_without_e_over_p") == independent_diag.get("rational_cpost_without_e_over_p") == "-112/4225", [primary_diag.get("rational_three_atom_cpost_without_e_over_p"), independent_diag.get("rational_cpost_without_e_over_p")], ["-112/4225", "-112/4225"])
    add("crosscheck", "full_frame_sign_matches", primary_diag.get("full_frame_three_atom_cpost_without_e_over_p") == independent_diag.get("full_frame_cpost_without_e_over_p") == "-1236/21125", [primary_diag.get("full_frame_three_atom_cpost_without_e_over_p"), independent_diag.get("full_frame_cpost_without_e_over_p")], ["-1236/21125", "-1236/21125"])
    add("crosscheck", "frame_constant_matches", abs(float(primary_diag.get("frame_secant_constant", 0.0)) - float(independent_diag.get("frame_secant_constant", 1.0))) < 1.0e-14, [primary_diag.get("frame_secant_constant"), independent_diag.get("frame_secant_constant")], "within 1e-14")
    add("crosscheck", "primary_fourier_error_small", float(primary_diag.get("maximum_cartan_fourier_error", 1.0)) < 2.0e-12, primary_diag.get("maximum_cartan_fourier_error"), "<2e-12")
    add("crosscheck", "independent_fourier_error_small", float(independent_diag.get("maximum_fourier_error", 1.0)) < 2.0e-12, independent_diag.get("maximum_fourier_error"), "<2e-12")
    add("crosscheck", "primary_floor_error_small", float(primary_diag.get("maximum_finite_floor_radial_error", 1.0)) < 2.0e-9, primary_diag.get("maximum_finite_floor_radial_error"), "<2e-9")
    add("crosscheck", "independent_floor_error_small", float(independent_diag.get("maximum_finite_floor_radial_error", 1.0)) < 3.0e-9, independent_diag.get("maximum_finite_floor_radial_error"), "<3e-9")

    roots = imported_roots(INDEPENDENT) if INDEPENDENT.exists() else set()
    add("independence", "independent_no_numpy", "numpy" not in roots, sorted(roots), "no numpy")
    add("independence", "independent_no_scipy", "scipy" not in roots, sorted(roots), "no scipy")
    add("independence", "independent_no_sympy", "sympy" not in roots, sorted(roots), "no sympy")
    add("independence", "independent_no_primary_import", "a13_classii_signed_first_cartan_rational_ridge_boundary" not in roots, sorted(roots), "primary module absent")
    add("independence", "independent_no_primary_result_read", "primary-signed-first-cartan" not in INDEPENDENT.read_text(encoding="utf-8"), False, False)

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest", "manifest_load", False, repr(error), "valid JSON")
    else:
        add("manifest", "manifest_load", True, "valid JSON", "valid JSON")

    authority_manifest = manifest.get("authority", {})
    for label, (manifest_path, result_path) in AUTHORITY.items():
        for kind, path in (("manifest", manifest_path), ("result", result_path)):
            expected_hash = authority_manifest.get(label, {}).get(kind, {}).get("sha256")
            actual_hash = digest(path) if path.exists() else None
            add("authority", f"authority_{label}_{kind}_exists", path.exists(), repo_path(path), "exists")
            add("authority", f"authority_{label}_{kind}_hash", actual_hash == expected_hash, actual_hash, expected_hash)
        try:
            authority_result = load_json(result_path)
        except Exception as error:
            add("authority", f"authority_{label}_pass", False, repr(error), "accepted PASS")
        else:
            add("authority", f"authority_{label}_pass", result_passes(authority_result), authority_result.get("status", authority_result.get("verdict")), "accepted PASS")

    source_paths = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "proof_note": NOTE,
    }
    manifest_sources = manifest.get("sources", {})
    for label, path in source_paths.items():
        entry = manifest_sources.get(label, {})
        add("hashes", f"source_{label}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
        add("hashes", f"source_{label}_hash", path.exists() and entry.get("sha256") == digest(path), entry.get("sha256"), digest(path) if path.exists() else None)
        if label != "proof_note":
            add("hashes", f"source_{label}_version", entry.get("version") == source_version(path), entry.get("version"), source_version(path))

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    note_words = " ".join(note_text.split())
    for index, token in enumerate(NOTE_TOKENS):
        token_words = " ".join(token.split())
        add("note", f"note_token_{index:02d}", token_words in note_words, token_words in note_words, True)
    add("note", "floorless_homogeneity_shortcut_not_asserted", "homogeneity gives" not in note_text, "homogeneity gives" in note_text, False)
    add("note", "note_english_only", not any(0xAC00 <= ord(character) <= 0xD7AF for character in note_text), "Hangul present" if any(0xAC00 <= ord(character) <= 0xD7AF for character in note_text) else "English only", "English only")

    try:
        reader = PdfReader(PDF)
        pdf_pages = len(reader.pages)
        page_lengths = [len((page.extract_text() or "").strip()) for page in reader.pages]
        pdf_forms = bool(reader.get_fields())
        pdf_encrypted = reader.is_encrypted
        root_text = str(reader.trailer.get("/Root", {}))
        extracted_text = " ".join((page.extract_text() or "") for page in reader.pages)
    except Exception as error:
        pdf_pages, page_lengths, pdf_forms, pdf_encrypted, root_text, extracted_text = 0, [], True, True, "/JavaScript", ""
        add("pdf", "pdf_load", False, repr(error), "readable PDF")
    else:
        add("pdf", "pdf_load", True, "readable PDF", "readable PDF")
    pdf_entry = manifest.get("proof_pdf", {})
    add("pdf", "pdf_pages", pdf_pages == pdf_entry.get("pages") and pdf_pages == 9, pdf_pages, 9)
    add("pdf", "pdf_nonblank_pages", bool(page_lengths) and min(page_lengths) > 100, page_lengths, "each page >100 characters")
    add("pdf", "pdf_no_forms", not pdf_forms, pdf_forms, False)
    add("pdf", "pdf_not_encrypted", not pdf_encrypted, pdf_encrypted, False)
    add("pdf", "pdf_no_javascript", "/JavaScript" not in root_text and "/JS" not in root_text, [token for token in ("/JavaScript", "/JS") if token in root_text], [])
    add("pdf", "pdf_no_literal_qquad", "qquad" not in extracted_text, "qquad" in extracted_text, False)
    add("pdf", "pdf_hash", PDF.exists() and pdf_entry.get("sha256") == digest(PDF), pdf_entry.get("sha256"), digest(PDF) if PDF.exists() else None)
    add("pdf", "pdf_size", PDF.exists() and pdf_entry.get("size_bytes") == PDF.stat().st_size, pdf_entry.get("size_bytes"), PDF.stat().st_size if PDF.exists() else None)
    add("pdf", "pdf_overfull", pdf_entry.get("overfull_hbox_count") == 0, pdf_entry.get("overfull_hbox_count"), 0)
    add("pdf", "pdf_form_check", pdf_entry.get("form_check") == "PASS", pdf_entry.get("form_check"), "PASS")
    add("pdf", "pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS", pdf_entry.get("visual_qa"), "PASS")

    surfaces = {
        "results": REPO / "RESULTS-LEDGER.md",
        "negative": REPO / "negative-results/registry.md",
        "claim_status": CLAIM_DIR / "status.json",
        "claim_card": CLAIM_DIR / "claim.md",
        "claims": REPO / "CLAIMS.md",
        "proof_map": REPO / "theory/proof-evidence-map.md",
        "changelog": REPO / "CHANGELOG.md",
        "todo": REPO / "TODO.md",
    }
    surface_text = {label: path.read_text(encoding="utf-8") if path.exists() else "" for label, path in surfaces.items()}
    add("surfaces", "results_r098_anchor", "R-098" in surface_text["results"] and '<a id="r-098"></a>' in surface_text["results"], "R-098" in surface_text["results"], True)
    negative_anchor = NEGATIVE_RESULTS[0].lower()
    add("surfaces", "negative_r098_anchor", NEGATIVE_RESULTS[0] in surface_text["negative"] and f'<a id="{negative_anchor}"></a>' in surface_text["negative"], NEGATIVE_RESULTS[0] in surface_text["negative"], True)
    for label in ("claim_status", "claim_card", "claims", "proof_map", "changelog"):
        if label == "claims":
            present = CLAIM in surface_text[label] and "A13-CLASSII-FULL-FRAME-POSTERIOR-COVARIANCE-BRACKET" in surface_text[label]
        else:
            present = "R-098" in surface_text[label] or RESULT_ID in surface_text[label]
        add("surfaces", f"surface_{label}_r098", present, present, True)
    add("surfaces", "todo_t050_present", "T-050" in surface_text["todo"], "T-050" in surface_text["todo"], True)

    exploration_path = REPO / "explorations/log.jsonl"
    exploration_records: dict[str, dict[str, Any]] = {}
    if exploration_path.exists():
        for line in exploration_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                if record.get("id") in EXPLORATIONS:
                    exploration_records[record["id"]] = record
    for exploration_id in EXPLORATIONS:
        record = exploration_records.get(exploration_id, {})
        add("explorations", f"exploration_{exploration_id}_exists", bool(record), bool(record), True)
        add("explorations", f"exploration_{exploration_id}_verdict", record.get("verdict") == EXPLORATION_VERDICTS[exploration_id], record.get("verdict"), EXPLORATION_VERDICTS[exploration_id])
        add("explorations", f"exploration_{exploration_id}_result_ref", "R-098" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), ["R-098"])
    add("explorations", "failed_route_has_new_negative", NEGATIVE_RESULTS[0] in exploration_records.get("EXP-000222", {}).get("formal_refs", {}).get("negatives", []), exploration_records.get("EXP-000222", {}).get("formal_refs", {}).get("negatives", []), [NEGATIVE_RESULTS[0]])

    consequence = manifest.get("consequence", {})
    add("manifest", "manifest_schema", manifest.get("schema") == "tect/a13-signed-first-cartan-rational-ridge-boundary/1.0", manifest.get("schema"), "tect/a13-signed-first-cartan-rational-ridge-boundary/1.0")
    add("manifest", "manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest", "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "manifest_ledger", consequence.get("result_ledger_id") == "R-098", consequence.get("result_ledger_id"), "R-098")
    for key in ("payment_split_superadditivity", "rational_ridge_normal_form", "standalone_recovery_identity", "same_heat_root_signed_refinement_cancellation", "finite_floor_radial_identity", "bare_resampling_hardy_mass"):
        add("manifest", f"manifest_proved_{key}", consequence.get(key) is True, consequence.get(key), True)
    for key in ("production_posterior_lower_form", "cartan_one_use", "rational_shifted_hessian_form", "complete_h_n", "reg", "arbitrary_progressive_revisit", "full_overlap_src", "nelson", "interacting_measure", "sector_a_closure"):
        add("manifest", f"manifest_open_{key}", consequence.get(key) is False, consequence.get(key), False)
    add("manifest", "manifest_scope_distinct_temporal_not_refuted", consequence.get("distinct_temporal_root_heat_no_go") is False, consequence.get("distinct_temporal_root_heat_no_go"), False)
    add("manifest", "manifest_tier_stable", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest", "manifest_negative_set", manifest.get("negative_results") == list(NEGATIVE_RESULTS), manifest.get("negative_results"), list(NEGATIVE_RESULTS))
    add("manifest", "manifest_exploration_set", manifest.get("explorations") == list(EXPLORATIONS), manifest.get("explorations"), list(EXPLORATIONS))

    contract = manifest.get("run_contract", {})
    primary_total = result_total(primary)
    independent_total = result_total(independent)
    add("contract", "primary_count_contract", primary_total == contract.get("primary_assertions") == 138, primary_total, 138)
    add("contract", "independent_count_contract", independent_total == contract.get("independent_assertions") == 111, independent_total, 111)
    final_integrated_total = len(rows) + 2
    add("contract", "integrated_count_contract", count_only or final_integrated_total == contract.get("integrated_assertions"), final_integrated_total, contract.get("integrated_assertions"))
    final_aggregate = primary_total + independent_total + final_integrated_total
    add("contract", "aggregate_count_contract", count_only or final_aggregate == contract.get("aggregate_assertions"), final_aggregate, contract.get("aggregate_assertions"))

    failures = [row for row in rows if row["status"] != "PASS"]
    groups: dict[str, dict[str, int]] = {}
    for row in rows:
        summary = groups.setdefault(row["group"], {"total": 0, "passed": 0, "failed": 0})
        summary["total"] += 1
        summary["passed" if row["status"] == "PASS" else "failed"] += 1
    payload = {
        "schema": "tect/a13-signed-first-cartan-rational-ridge-boundary-integrated/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertion_groups": groups,
        "assertions": rows,
        "failures": [row["name"] for row in failures],
        "assertion_summary": {
            "primary": primary_total,
            "independent": independent_total,
            "integrated": len(rows),
            "aggregate": primary_total + independent_total + len(rows),
        },
        "boundary": {
            "payment_split_superadditivity": True,
            "rational_ridge_normal_form": True,
            "refinement_stable_nonnegative_per_subvisit_atomization": False,
            "production_posterior_lower_form": False,
            "cartan_one_use_4_11": False,
            "rational_shifted_hessian_form_6_5": False,
            "complete_h_n": False,
            "reg": False,
            "nelson": False,
            "sector_a_closure": False,
        },
    }
    atomic_json(OUTPUT, payload)
    if count_only:
        print(f"R-098 COUNT-ONLY integrated={len(rows)} aggregate={primary_total + independent_total + len(rows)}")
        return 0
    print(f"R-098 INTEGRATED {'PASS' if not failures else 'FAIL'}: {len(rows) - len(failures)}/{len(rows)}; aggregate={primary_total + independent_total + len(rows)}")
    if failures:
        print("failures=" + ",".join(row["name"] for row in failures))
    print(f"output={repo_path(OUTPUT)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
