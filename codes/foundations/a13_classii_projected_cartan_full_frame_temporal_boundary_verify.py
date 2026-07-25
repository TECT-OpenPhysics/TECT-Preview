#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-091 A13 boundary package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

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
RESULT_ID = "A13-CLASSII-PROJECTED-CARTAN-FULL-FRAME-SCHUR-JENSEN-TEMPORAL-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM

PRIMARY = REPO / "codes/foundations/a13_classii_projected_cartan_full_frame_temporal_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_projected_cartan_full_frame_temporal_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-projected-cartan-full-frame-temporal-boundary-260725-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-projected-cartan-full-frame-temporal-boundary-260725-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_projected_cartan_full_frame_temporal_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-25-primary-projected-cartan-full-frame-temporal-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-25-independent-projected-cartan-full-frame-temporal-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-projected-cartan-full-frame-temporal-boundary/result.json"

AUTHORITY = {
    "r079_current": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r084_linear": (
        CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-root-diagonal-cartan-ou-linear-pf-absorption/result.json",
    ),
    "r087_spatial_core": (
        CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json",
    ),
    "r089_progressive": (
        CLAIM_DIR / "classii_progressive_covariance_compression_rational_mean_spectral_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-progressive-covariance-compression-rational-mean-spectral-boundary/result.json",
    ),
    "r090_boundary": (
        CLAIM_DIR / "classii_global_unprojected_cartan_ledger_nogo_rational_forest_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-excess-tail-rational-forest-nonduplication/result.json",
    ),
}

NOTE_TOKENS = (
    "R-091",
    "lossless output-gap extraction",
    "\\mathcal B_\\gamma^{\\rm out}",
    "2^{-2\\gamma(C-5)}",
    "NG-2026-07-25-A13-PROJECTED-CARTAN-CUMULATIVE-Z6-MAJORANT",
    "exact saturated scalar trace decreases like $N^{-4}$",
    "h_{2n}=(-r)^n",
    "superexponential in the gap",
    "conditional full-frame identity",
    "2\\eta B_1(B_1+2\\eta I)^{-1}-B_0",
    "NG-2026-07-25-A13-FULL-FRAME-CONDITIONAL-POSITIVITY",
    "Same-root Schur--Jensen residual",
    "r_C&=\\mathbb E[(C-\\widehat C)^T",
    "-{3708\\over21125P}e\\varphi(1)",
    "terminal paid split",
    "AUDIT-2026-07-25-A13-REG-OVERLAP-TEMPORAL-SCOPE",
    "CORE, OVERLAP, and REG are not interchangeable",
    "is a sufficient proof architecture",
    "No projected CFAR",
    "Tier stays T4",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return None if match is None else match.group(1)


def authority_passes(record: dict[str, Any]) -> bool:
    status = str(record.get("status", record.get("verdict", ""))).upper()
    passed = record.get("assertions_passed", record.get("passed"))
    total = record.get("assertions_total", record.get("total"))
    return "PASS" in status and (passed is None or total is None or passed == total)


def assertion_actual(record: dict[str, Any], name: str) -> Any:
    for row in record.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row.get("actual")
    return None


def main() -> int:
    rows: list[dict[str, Any]] = []

    def add(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    # Execute both evidence routes before reading their artefacts.
    for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=180,
        )
        add(f"{label}_process_exit", completed.returncode == 0, completed.returncode, 0)

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest_load", False, repr(error), "valid JSON")
    else:
        add("manifest_load", True, "valid JSON", "valid JSON")

    records: dict[str, dict[str, Any]] = {}
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        try:
            records[label] = load_json(path)
        except Exception as error:
            records[label] = {}
            add(f"{label}_result_load", False, repr(error), "valid JSON")
        else:
            add(f"{label}_result_load", True, "valid JSON", "valid JSON")

    expected_counts = {
        "primary": manifest.get("run_contract", {}).get("primary_assertions"),
        "independent": manifest.get("run_contract", {}).get("independent_assertions"),
    }
    for label, record in records.items():
        expected = expected_counts[label]
        add(f"{label}_status", record.get("status") == "PASS", record.get("status"), "PASS")
        add(f"{label}_passed_total", record.get("assertions_passed") == record.get("assertions_total"), [record.get("assertions_passed"), record.get("assertions_total")], "equal")
        add(f"{label}_manifest_count", isinstance(expected, int) and record.get("assertions_total") == expected, record.get("assertions_total"), expected)
        add(f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add(f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    primary = records.get("primary", {})
    independent = records.get("independent", {})
    add("primary_schema", primary.get("schema") == "tect/a13-projected-cartan-full-frame-temporal-boundary-primary/1.0", primary.get("schema"), "primary/1.0")
    add("independent_schema", independent.get("schema") == "tect/a13-projected-cartan-full-frame-temporal-boundary-independent/1.0", independent.get("schema"), "independent/1.0")

    primary_names = {row.get("name") for row in primary.get("assertions", []) if isinstance(row, dict)}
    independent_names = {row.get("name") for row in independent.get("assertions", []) if isinstance(row, dict)}
    required_primary = {
        "output_gap_ledger_C_10",
        "order_two_weighted_margin",
        "order_three_weighted_margin",
        "rare_value_majorant_power",
        "rare_mixed_budget_power",
        "scalar_series_closed_form",
        "scalar_tail_closed_form",
        "first_variation_harmonic_n_8",
        "first_variation_tail_upper_R2",
        "q_shift_upper_gap_five",
        "conditional_full_frame_matrix_identity",
        "conditional_full_frame_schur_minimum",
        "same_root_jensen_completion",
        "full_frame_exact_loss_factor",
        "terminal_paid_split_nonduplication",
        "temporal_future_cross_is_load_bearing",
        "all_downstream_flags_false",
    }
    required_independent = {
        "independent_output_gap_ledger",
        "independent_z6_rare_powers",
        "independent_scalar_fourier_coefficients",
        "independent_scalar_rare_tail_slope_minus_four",
        "independent_first_variation_harmonics",
        "independent_first_variation_tail_bound",
        "independent_q_shift_upper",
        "independent_conditional_full_frame",
        "independent_same_root_jensen",
        "independent_fixed_eta_positivity_fails",
        "independent_local_full_frame_quadrature",
        "independent_terminal_nonduplication",
        "independent_no_overclaim",
    }
    add("primary_required_rows", required_primary.issubset(primary_names), sorted(required_primary - primary_names), [])
    add("independent_required_rows", required_independent.issubset(independent_names), sorted(required_independent - independent_names), [])

    p_cartan = primary.get("projected_cartan", {})
    i_scalar = independent.get("scalar", {})
    add("cartan_safe_gap", p_cartan.get("safe_principal_gap") == 5, p_cartan.get("safe_principal_gap"), 5)
    add("cartan_gap_exponent", Fraction(str(p_cartan.get("gap_exponent"))) == Fraction(7, 6), p_cartan.get("gap_exponent"), "7/6")
    add("cartan_weighted_margins", p_cartan.get("weighted_margins") == ["13/30", "37/30"], p_cartan.get("weighted_margins"), ["13/30", "37/30"])
    add("cartan_z_majorant_power", Fraction(str(p_cartan.get("z_majorant_rare_power"))) == 3, p_cartan.get("z_majorant_rare_power"), 3)
    add("cartan_exact_not_refuted", p_cartan.get("exact_cartan_refuted") is False, p_cartan.get("exact_cartan_refuted"), False)
    add("cartan_one_use_not_claimed", p_cartan.get("z_majorant_proves_one_use") is False, p_cartan.get("z_majorant_proves_one_use"), False)
    add("scalar_rare_last_slope", abs(float(i_scalar.get("rare_log2_slopes", [999])[-1]) + 4) < 3e-6, i_scalar.get("rare_log2_slopes", [None])[-1], "near -4")
    add("scalar_tail_ratios_below_one", all(float(value) < 1 for value in i_scalar.get("first_variation_tail_ratios", [])) and bool(i_scalar.get("first_variation_tail_ratios")), i_scalar.get("first_variation_tail_ratios"), "all <1")

    p_frame = primary.get("full_frame", {})
    i_frame = independent.get("full_frame", {})
    add("frame_universal_positivity_false", p_frame.get("universal_fixed_eta_positivity") is False, p_frame.get("universal_fixed_eta_positivity"), False)
    add("frame_local_post_paid_false", p_frame.get("local_fixture_is_post_paid_counterexample") is False, p_frame.get("local_fixture_is_post_paid_counterexample"), False)
    add("frame_local_loss_negative", float(p_frame.get("local_expected_loss_per_floor", 1)) < 0, p_frame.get("local_expected_loss_per_floor"), "<0")
    add("frame_quadrature_cross", abs(float(i_frame.get("local_quadrature", "nan")) - float(i_frame.get("local_exact", "nan"))) < 2e-14, [i_frame.get("local_quadrature"), i_frame.get("local_exact")], "cross match")

    p_temporal = primary.get("temporal", {})
    add("terminal_split_closed", p_temporal.get("terminal_split_algebra_closed") is True, p_temporal.get("terminal_split_algebra_closed"), True)
    add("progressive_mapping_open", p_temporal.get("progressive_projection_mapping_closed") is False, p_temporal.get("progressive_projection_mapping_closed"), False)
    add("temporal_overlap_open", p_temporal.get("overlap_stable_temporal_extension_closed") is False, p_temporal.get("overlap_stable_temporal_extension_closed"), False)
    add("future_feedback_retained", p_temporal.get("future_feedback_cross_retained") is True, p_temporal.get("future_feedback_cross_retained"), True)

    for label, record in records.items():
        flags = record.get("claims_not_established", record.get("unproved", {}))
        add(f"{label}_downstream_false", bool(flags) and all(value is False for value in flags.values()), flags, "all false")

    add("manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest_t4_open", "T4" in str(manifest.get("status")) and "OPEN" in str(manifest.get("status")), manifest.get("status"), "T4 with open gates")

    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        pin = manifest.get("authority", {}).get(label, {})
        add(f"{label}_manifest_exists", authority_manifest.exists(), str(authority_manifest.relative_to(REPO)), "exists")
        add(f"{label}_manifest_hash", authority_manifest.exists() and pin.get("manifest", {}).get("sha256") == digest(authority_manifest), pin.get("manifest", {}).get("sha256"), None if not authority_manifest.exists() else digest(authority_manifest))
        add(f"{label}_result_exists", authority_result.exists(), str(authority_result.relative_to(REPO)), "exists")
        add(f"{label}_result_hash", authority_result.exists() and pin.get("result", {}).get("sha256") == digest(authority_result), pin.get("result", {}).get("sha256"), None if not authority_result.exists() else digest(authority_result))
        try:
            authority_record = load_json(authority_result)
        except Exception:
            authority_record = {}
        add(f"{label}_result_passes", authority_passes(authority_record), authority_record.get("status", authority_record.get("verdict")), "PASS")

    source_entries = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "proof_note": NOTE,
    }
    for label, path in source_entries.items():
        pin = manifest.get("sources", {}).get(label, {})
        add(f"{label}_source_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        add(f"{label}_source_hash", path.exists() and pin.get("sha256") == digest(path), pin.get("sha256"), None if not path.exists() else digest(path))
        if label != "proof_note":
            add(f"{label}_source_version", path.exists() and pin.get("version") == source_version(path), pin.get("version"), None if not path.exists() else source_version(path))

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    for index, token in enumerate(NOTE_TOKENS, start=1):
        add(f"note_token_{index}", token in note_text, token if token in note_text else None, token)
    control_chars = [ord(character) for character in note_text if ord(character) < 32 and character not in "\t\n\r"]
    add("note_no_control_chars", not control_chars, control_chars, [])
    add("note_no_literal_qquad", "qquad" not in note_text.replace("\\qquad", ""), "literal qquad absent", "absent")
    add("note_scope_firewall", all(token in note_text for token in ("proof-method no-go", "not a post-paid", "Tier stays T4")), "scope tokens", "present")

    pdf_pin = manifest.get("proof_pdf", {})
    add("pdf_exists", PDF.exists(), str(PDF.relative_to(REPO)), "exists")
    if PDF.exists():
        reader = PdfReader(str(PDF))
        pdf_pages = len(reader.pages)
        pdf_fields = reader.get_fields() or {}
        add("pdf_hash", pdf_pin.get("sha256") == digest(PDF), pdf_pin.get("sha256"), digest(PDF))
        add("pdf_pages", pdf_pages == pdf_pin.get("pages") == 11, [pdf_pages, pdf_pin.get("pages")], 11)
        add("pdf_size", PDF.stat().st_size == pdf_pin.get("size_bytes"), PDF.stat().st_size, pdf_pin.get("size_bytes"))
        add("pdf_unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
        add("pdf_no_forms", not pdf_fields, sorted(pdf_fields), [])
        add("pdf_form_check", pdf_pin.get("form_check") == "PASS", pdf_pin.get("form_check"), "PASS")
        add("pdf_overfull_zero", pdf_pin.get("overfull_hbox_count") == 0, pdf_pin.get("overfull_hbox_count"), 0)
        add("pdf_visual_qa", pdf_pin.get("visual_qa") == "PASS", pdf_pin.get("visual_qa"), "PASS")
    else:
        for name in ("pdf_hash", "pdf_pages", "pdf_size", "pdf_unencrypted", "pdf_no_forms", "pdf_form_check", "pdf_overfull_zero", "pdf_visual_qa"):
            add(name, False, None, "PDF required")

    registry_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    gates_text = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    status_text = (CLAIM_DIR / "status.json").read_text(encoding="utf-8")
    for token in (
        "NG-2026-07-25-A13-PROJECTED-CARTAN-CUMULATIVE-Z6-MAJORANT",
        "NG-2026-07-25-A13-FULL-FRAME-CONDITIONAL-POSITIVITY",
        "AUDIT-2026-07-25-A13-REG-OVERLAP-TEMPORAL-SCOPE",
    ):
        add(f"registry_{token.split('A13-')[-1].lower()}", token in registry_text, token if token in registry_text else None, token)
    add("results_ledger_r091", "R-091" in results_text and RESULT_ID in results_text, "R-091" if "R-091" in results_text else None, "R-091 and result ID")
    add("gates_r091", "R-091" in gates_text and "saturation-aware" in gates_text, "gate update", "R-091 saturation-aware target")
    add("roadmap_r091", "R-091" in roadmap_text and "Schur--Carleson" in roadmap_text, "roadmap update", "R-091 Schur--Carleson target")
    add("changelog_r091", "R-091" in changelog_text and RESULT_ID in changelog_text, "changelog update", "R-091 and result ID")
    add("status_r091", "R-091" in status_text and RESULT_ID in status_text, "status update", "R-091 and result ID")

    negative_results = set(manifest.get("negative_results", []))
    add("manifest_negative_z6", "NG-2026-07-25-A13-PROJECTED-CARTAN-CUMULATIVE-Z6-MAJORANT" in negative_results, sorted(negative_results), "Z6 no-go")
    add("manifest_negative_positivity", "NG-2026-07-25-A13-FULL-FRAME-CONDITIONAL-POSITIVITY" in negative_results, sorted(negative_results), "positivity no-go")
    add("manifest_temporal_audit", "AUDIT-2026-07-25-A13-REG-OVERLAP-TEMPORAL-SCOPE" in negative_results, sorted(negative_results), "temporal audit")
    manifest_flags = manifest.get("claims_not_established", {})
    add("manifest_downstream_false", bool(manifest_flags) and all(value is False for value in manifest_flags.values()), manifest_flags, "all false")
    add("manifest_no_promotion", manifest.get("tier_before") == manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])

    expected_integrated = manifest.get("run_contract", {}).get("integrated_assertions")
    final_integrated_count = len(rows) + 2  # this row plus aggregate_manifest_count
    add("integrated_manifest_count", isinstance(expected_integrated, int) and final_integrated_count == expected_integrated, final_integrated_count, expected_integrated)

    passed = sum(row["status"] == "PASS" for row in rows)
    aggregate = primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + len(rows)
    expected_aggregate = manifest.get("run_contract", {}).get("aggregate_assertions")
    aggregate_matches = isinstance(expected_aggregate, int) and aggregate + 1 == expected_aggregate
    add("aggregate_manifest_count", aggregate_matches, aggregate + 1, expected_aggregate)
    passed = sum(row["status"] == "PASS" for row in rows)

    payload = {
        "schema": "tect/a13-projected-cartan-full-frame-temporal-boundary-integrated/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "aggregate_assertions": primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + len(rows),
        "assertions": rows,
        "records": {
            "primary": str(PRIMARY_RESULT.relative_to(REPO)),
            "independent": str(INDEPENDENT_RESULT.relative_to(REPO)),
        },
        "manifest": str(MANIFEST.relative_to(REPO)),
        "proof_pdf": str(PDF.relative_to(REPO)),
        "claims_not_established": manifest_flags,
    }
    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(
            f"[R-091 integrated] {passed}/{len(rows)} PASS; "
            f"aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}"
        )
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-091 integrated] {passed}/{len(rows)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
