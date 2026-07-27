#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-092 A13 frontier package."""

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
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-NORMALIZED-CARTAN-COMPENSATED-PERSPECTIVE-TRIANGULAR-COVARIANCE-FRONTIER"
CLAIM_DIR = REPO / "claims" / CLAIM

PRIMARY = REPO / "codes/foundations/a13_classii_normalized_cartan_perspective_covariance_frontier.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_normalized_cartan_perspective_covariance_frontier_independent.py"
NOTE = CLAIM_DIR / "notes/classii-normalized-cartan-perspective-triangular-covariance-frontier-260725-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-normalized-cartan-perspective-triangular-covariance-frontier-260725-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_normalized_cartan_perspective_covariance_frontier_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-25-primary-normalized-cartan-perspective-covariance-frontier/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-25-independent-normalized-cartan-perspective-covariance-frontier/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-normalized-cartan-perspective-covariance-frontier/result.json"

AUTHORITY = {
    "r075_current_graph": (
        CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-principal-taylor-oneform-graph-recovery/result.json",
    ),
    "r079_current_doob": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r084_linear_pf": (
        CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-root-diagonal-cartan-ou-linear-pf-absorption/result.json",
    ),
    "r087_spatial_core": (
        CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json",
    ),
    "r089_progressive_trace": (
        CLAIM_DIR / "classii_progressive_covariance_compression_rational_mean_spectral_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-progressive-covariance-compression-rational-mean-spectral-boundary/result.json",
    ),
    "r090_audited_boundary": (
        CLAIM_DIR / "classii_global_unprojected_cartan_ledger_nogo_rational_forest_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-excess-tail-rational-forest-nonduplication/result.json",
    ),
    "r091_temporal_boundary": (
        CLAIM_DIR / "classii_projected_cartan_full_frame_temporal_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-projected-cartan-full-frame-temporal-boundary/result.json",
    ),
}

NEGATIVE_RESULTS = (
    "AUDIT-2026-07-25-A13-R090-CONSERVATIVE-TRANSPOSE",
    "NG-2026-07-25-A13-SCALAR-SUPEREXPONENTIAL-VECTOR-UNIFORMITY",
    "NG-2026-07-25-A13-PERSPECTIVE-INNOVATION-TERMWISE-POSITIVITY",
    "NG-2026-07-25-A13-TERMINAL-POLAR-CAUSAL-PROMOTION",
    "NG-2026-07-25-A13-NEGATIVE-FLOW-CAT0-SHORTCUT",
)

NOTE_TOKENS = (
    "R-092",
    "The actual R-084/R-089 current coefficient instead is",
    "Exact two-field output trace and the transpose audit",
    "AUDIT-2026-07-25-A13-R090-CONSERVATIVE-TRANSPOSE",
    "32\\kappa_1",
    "1-2^{-61/30}",
    "2^{-7j/30}",
    "29/30",
    "\\widetilde{\\mathcal C}_k",
    "weighted conditional-covariance deficit",
    "-{623\\over5440}",
    "-{1\\over4}",
    "entropy-union",
    "\\mathcal F_h",
    "q=10/9",
    "Complete signed NEAR",
    "Sector A remain open",
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
    legacy_pass = record.get("pass") is True
    return ("PASS" in status or legacy_pass) and (passed is None or total is None or passed == total)


def assertion_actual(record: dict[str, Any], name: str) -> Any:
    for row in record.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row.get("actual")
    return None


def main() -> int:
    count_only = "--count-only" in sys.argv
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
        add(
            f"{label}_passed_total",
            record.get("assertions_passed") == record.get("assertions_total"),
            [record.get("assertions_passed"), record.get("assertions_total")],
            "equal",
        )
        add(
            f"{label}_manifest_count",
            isinstance(expected, int) and record.get("assertions_total") == expected,
            record.get("assertions_total"),
            expected,
        )
        add(f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add(f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)
        add(f"{label}_version", record.get("version") == "1.2.0", record.get("version"), "1.2.0")

    primary = records.get("primary", {})
    independent = records.get("independent", {})
    add(
        "primary_schema",
        primary.get("schema") == "tect/a13-normalized-cartan-perspective-covariance-frontier-primary/1.0",
        primary.get("schema"),
        "primary/1.0",
    )
    add(
        "independent_schema",
        independent.get("schema") == "tect/a13-normalized-cartan-perspective-covariance-frontier-independent/1.0",
        independent.get("schema"),
        "independent/1.0",
    )

    primary_names = {row.get("name") for row in primary.get("assertions", []) if isinstance(row, dict)}
    independent_names = {row.get("name") for row in independent.get("assertions", []) if isinstance(row, dict)}
    required_primary = {
        "transpose_audit_endpoint_gradient",
        "transpose_audit_current_not_gradient",
        "transpose_audit_defect_identity",
        "coefficient_poincare_constant",
        "two_tail_gradient_constant",
        "two_tail_root_weight_identity",
        "b_denominator_exponent",
        "gradient_denominator_exponent",
        "control_product_gn_alpha_1_3",
        "control_a_da_outer_da_14_15",
        "control_a_du_outer_da_23_30",
        "control_a_da_outer_du_4_15",
        "root_surplus_7_30",
        "worst_control_total_29_30",
        "young_slack_1_30",
        "regular_hc_exponent_prefix_gate",
        "matrix_perspective_telescope",
        "augmented_perspective_partition",
        "frozen_augmented_density_zero",
        "moment_matched_one_reveal_nonnegative",
        "weighted_conditional_covariance_defect",
        "fixture_expectation",
        "fixture_frame_positive",
        "covariance_union_cm_contraction",
        "covariance_union_trace",
        "triangular_entropy_identity",
        "kernel_loop_fibre_surplus",
        "entropy_union_nelson_coefficient",
        "negative_flow_defect_integral",
        "cat0_scaled_reset_negative",
        "all_downstream_flags_false",
    }
    required_independent = {
        "independent_transpose_defect",
        "independent_coefficient_poincare",
        "independent_two_tail_gradient",
        "independent_b_denominator_exponent",
        "independent_gradient_denominator_exponent",
        "independent_product_gn_alpha",
        "independent_a_da_outer_da",
        "independent_a_du_outer_da",
        "independent_a_da_outer_du",
        "independent_young_slack",
        "independent_regular_hc_gate",
        "independent_perspective_telescope",
        "independent_augmented_partition",
        "independent_frozen_augmented_zero",
        "independent_weighted_covariance_defect",
        "independent_fixture_average",
        "independent_covariance_union",
        "independent_covariance_contraction",
        "independent_covariance_trace",
        "independent_polar_noncausal",
        "independent_kernel_loop_fibre_entropy",
        "independent_entropy_nelson_coefficient",
        "independent_negative_flow_liouville",
        "independent_cat0_reset",
        "independent_no_overclaim",
    }
    add("primary_required_rows", required_primary.issubset(primary_names), sorted(required_primary - primary_names), [])
    add("independent_required_rows", required_independent.issubset(independent_names), sorted(required_independent - independent_names), [])

    derived = primary.get("derived", {})
    for name, expected in (
        ("coefficient_poincare_constant", "16"),
        ("two_tail_gradient_constant", "32"),
        ("b_denominator_exponent", "1/30"),
        ("gradient_denominator_exponent", "61/30"),
        ("root_surplus", "7/30"),
        ("worst_control_total", "29/30"),
        ("regular_hc_gap", "2^(-(C-5)/2)"),
    ):
        add(f"derived_{name}", derived.get(name) == expected, derived.get(name), expected)
    add(
        "weighted_covariance_fixture",
        assertion_actual(primary, "weighted_conditional_covariance_defect") == "-1/4",
        assertion_actual(primary, "weighted_conditional_covariance_defect"),
        "-1/4",
    )
    add(
        "all_residual_fixture",
        assertion_actual(primary, "fixture_expectation") == "-623/5440",
        assertion_actual(primary, "fixture_expectation"),
        "-623/5440",
    )
    add(
        "entropy_coefficient",
        assertion_actual(primary, "entropy_union_nelson_coefficient") == "9/10",
        assertion_actual(primary, "entropy_union_nelson_coefficient"),
        "9/10",
    )

    for label, record in records.items():
        flags = record.get("claims_not_established", {})
        add(f"{label}_downstream_false", bool(flags) and all(value is False for value in flags.values()), flags, "all false")
    expected_downstream_keys = {
        "general_progressive_revisit_h_c",
        "complete_signed_h_n",
        "progressive_revisit_h_a",
        "full_reg_packet",
        "uniform_overlap",
        "nelson",
        "interacting_measure",
        "floor_removal",
        "sector_a_closure",
        "tier_promotion",
    }
    primary_flag_keys = set(primary.get("claims_not_established", {}))
    independent_flag_keys = set(independent.get("claims_not_established", {}))
    add(
        "downstream_flag_keys_aligned",
        primary_flag_keys == independent_flag_keys == expected_downstream_keys,
        [sorted(primary_flag_keys), sorted(independent_flag_keys)],
        sorted(expected_downstream_keys),
    )

    add("manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(
        "manifest_t4_open",
        "T4" in str(manifest.get("status")) and "OPEN" in str(manifest.get("status")),
        manifest.get("status"),
        "T4 with open gates",
    )
    add(
        "manifest_regular_scope",
        "REGULAR" in str(manifest.get("status")) and "PROGRESSIVE" in str(manifest.get("status")),
        manifest.get("status"),
        "regular closure with progressive open",
    )

    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        pin = manifest.get("authority", {}).get(label, {})
        add(f"{label}_manifest_exists", authority_manifest.exists(), str(authority_manifest.relative_to(REPO)), "exists")
        add(
            f"{label}_manifest_hash",
            authority_manifest.exists() and pin.get("manifest", {}).get("sha256") == digest(authority_manifest),
            pin.get("manifest", {}).get("sha256"),
            None if not authority_manifest.exists() else digest(authority_manifest),
        )
        add(f"{label}_result_exists", authority_result.exists(), str(authority_result.relative_to(REPO)), "exists")
        add(
            f"{label}_result_hash",
            authority_result.exists() and pin.get("result", {}).get("sha256") == digest(authority_result),
            pin.get("result", {}).get("sha256"),
            None if not authority_result.exists() else digest(authority_result),
        )
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
        add(
            f"{label}_source_hash",
            path.exists() and pin.get("sha256") == digest(path),
            pin.get("sha256"),
            None if not path.exists() else digest(path),
        )
        if label != "proof_note":
            add(
                f"{label}_source_version",
                path.exists() and pin.get("version") == source_version(path),
                pin.get("version"),
                None if not path.exists() else source_version(path),
            )

    independent_text = INDEPENDENT.read_text(encoding="utf-8") if INDEPENDENT.exists() else ""
    add(
        "independent_no_primary_import",
        "a13_classii_normalized_cartan_perspective_covariance_frontier import" not in independent_text,
        "primary import absent" if "a13_classii_normalized_cartan_perspective_covariance_frontier import" not in independent_text else "present",
        "absent",
    )

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    for index, token in enumerate(NOTE_TOKENS, start=1):
        add(f"note_token_{index}", token in note_text, token if token in note_text else None, token)
    control_chars = [ord(character) for character in note_text if ord(character) < 32 and character not in "\t\n\r"]
    add("note_no_control_chars", not control_chars, control_chars, [])
    bare_spacing = re.findall(r"(?<!\\)\bq?quad\b", note_text)
    add("note_no_bare_spacing_tokens", not bare_spacing, bare_spacing, [])
    add(
        "note_scope_firewall",
        all(token in note_text for token in ("regular one-shot Cartan", "Complete signed NEAR", "Sector A remain open", "Tier stays T4")),
        "scope tokens",
        "present",
    )

    pdf_pin = manifest.get("proof_pdf", {})
    add("pdf_exists", PDF.exists(), str(PDF.relative_to(REPO)), "exists")
    if PDF.exists():
        reader = PdfReader(str(PDF))
        pdf_pages = len(reader.pages)
        pdf_fields = reader.get_fields() or {}
        trailer_text = str(reader.trailer)
        add("pdf_hash", pdf_pin.get("sha256") == digest(PDF), pdf_pin.get("sha256"), digest(PDF))
        add("pdf_pages", pdf_pages == pdf_pin.get("pages") == 15, [pdf_pages, pdf_pin.get("pages")], 15)
        add("pdf_size", PDF.stat().st_size == pdf_pin.get("size_bytes"), PDF.stat().st_size, pdf_pin.get("size_bytes"))
        add("pdf_unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
        add("pdf_no_forms", not pdf_fields, sorted(pdf_fields), [])
        add("pdf_no_javascript", "/JavaScript" not in trailer_text and "/JS" not in trailer_text, "absent", "absent")
        add("pdf_form_check", pdf_pin.get("form_check") == "PASS", pdf_pin.get("form_check"), "PASS")
        add("pdf_overfull_zero", pdf_pin.get("overfull_hbox_count") == 0, pdf_pin.get("overfull_hbox_count"), 0)
        add("pdf_visual_qa", pdf_pin.get("visual_qa") == "PASS", pdf_pin.get("visual_qa"), "PASS")
    else:
        for name in (
            "pdf_hash",
            "pdf_pages",
            "pdf_size",
            "pdf_unencrypted",
            "pdf_no_forms",
            "pdf_no_javascript",
            "pdf_form_check",
            "pdf_overfull_zero",
            "pdf_visual_qa",
        ):
            add(name, False, None, "PDF required")

    registry_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    gates_text = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    status_text = (CLAIM_DIR / "status.json").read_text(encoding="utf-8")
    sector_readme = (REPO / "theory/sector-A-foundation/README.md").read_text(encoding="utf-8")
    main_line = (REPO / "theory/main-proof-line.md").read_text(encoding="utf-8")
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    exploration_text = (REPO / "explorations/log.jsonl").read_text(encoding="utf-8")

    for token in NEGATIVE_RESULTS:
        add(f"registry_{token.lower()}", token in registry_text, token if token in registry_text else None, token)
    add("results_ledger_r092", "R-092" in results_text and RESULT_ID in results_text, "R-092 surface", "R-092 and result ID")
    add("gates_r092", "R-092" in gates_text and "weighted conditional-" in gates_text and "covariance deficit" in gates_text, "gate surface", "R-092 weighted covariance target")
    add("roadmap_r092", "R-092" in roadmap_text and "entropy" in roadmap_text, "roadmap surface", "R-092 entropy frontier")
    add("changelog_r092", "R-092 normalized Cartan closure" in changelog_text and "hostile-review mixed branches" in changelog_text, "changelog surface", "R-092 normalized closure and hostile-review repair")
    add("status_r092", "R-092" in status_text and RESULT_ID in status_text, "status surface", "R-092 and result ID")
    add("todo_t050_r092", "T-050" in todo_text and "R-092" in todo_text, "TODO surface", "T-050 and R-092")
    add("sector_readme_r092", "R-092" in sector_readme and "regular" in sector_readme, "sector README", "R-092 regular closure")
    add("main_line_r092", "R-092" in main_line and "H_N" in main_line, "main proof line", "R-092 H_N frontier")
    add("theorem_map_version", theorem_map.get("version") == "1.7.1", theorem_map.get("version"), "1.7.1")
    frontier = theorem_map.get("active_frontier", {}).get("success_condition", "")
    add("theorem_map_frontier", "R-092" in frontier and "Sector A remains open" in frontier, frontier, "R-092 with open Sector A")
    expected_explorations = [f"EXP-{number:06d}" for number in range(167, 180)]
    add(
        "exploration_log_r092",
        all(token in exploration_text for token in expected_explorations),
        [token for token in expected_explorations if token in exploration_text],
        expected_explorations,
    )

    manifest_negative = set(manifest.get("negative_results", []))
    for token in NEGATIVE_RESULTS:
        add(f"manifest_negative_{token.lower()}", token in manifest_negative, sorted(manifest_negative), token)
    add("manifest_negative_exact_set", manifest_negative == set(NEGATIVE_RESULTS), sorted(manifest_negative), sorted(NEGATIVE_RESULTS))
    add("manifest_explorations", manifest.get("explorations") == expected_explorations, manifest.get("explorations"), expected_explorations)

    consequence = manifest.get("consequence", {})
    add("manifest_regular_hc_closed", consequence.get("regular_one_shot_cartan_h_c") is True, consequence.get("regular_one_shot_cartan_h_c"), True)
    add("manifest_progressive_open", consequence.get("general_progressive_revisit_cartan") is False, consequence.get("general_progressive_revisit_cartan"), False)
    add("manifest_hn_open", consequence.get("complete_signed_h_n") is False, consequence.get("complete_signed_h_n"), False)
    add("manifest_ha_open", consequence.get("progressive_revisit_h_a") is False, consequence.get("progressive_revisit_h_a"), False)
    manifest_flags = manifest.get("claims_not_established", {})
    add("manifest_downstream_false", bool(manifest_flags) and all(value is False for value in manifest_flags.values()), manifest_flags, "all false")
    add("manifest_no_promotion", manifest.get("tier_before") == manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])

    expected_integrated = manifest.get("run_contract", {}).get("integrated_assertions")
    final_integrated_count = len(rows) + 2
    add(
        "integrated_manifest_count",
        isinstance(expected_integrated, int) and final_integrated_count == expected_integrated,
        final_integrated_count,
        expected_integrated,
    )

    aggregate = primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + len(rows)
    expected_aggregate = manifest.get("run_contract", {}).get("aggregate_assertions")
    add(
        "aggregate_manifest_count",
        isinstance(expected_aggregate, int) and aggregate + 1 == expected_aggregate,
        aggregate + 1,
        expected_aggregate,
    )

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-normalized-cartan-perspective-covariance-frontier-integrated/1.0",
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

    if count_only:
        print(f"integrated_assertions={len(rows)} aggregate_assertions={payload['aggregate_assertions']}")
        return 0

    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(
            f"[R-092 integrated] {passed}/{len(rows)} PASS; "
            f"aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}"
        )
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-092 integrated] {passed}/{len(rows)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
