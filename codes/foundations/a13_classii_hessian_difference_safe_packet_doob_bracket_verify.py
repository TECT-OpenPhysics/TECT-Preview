#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-078 Hessian/Doob reduction."""

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

import pdfplumber
from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-HESSIAN-DIFFERENCE-SAFE-PACKET-DOOB-BRACKET-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
MANIFEST = CLAIM_DIR / "classii_hessian_difference_safe_packet_doob_bracket_manifest.json"
PRIMARY = REPO / "codes/foundations/a13_classii_hessian_difference_safe_packet_doob_bracket.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_hessian_difference_safe_packet_doob_bracket_independent.py"
NOTE = CLAIM_DIR / "notes/classii-hessian-difference-safe-packet-doob-bracket-reduction-260725-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-hessian-difference-safe-packet-doob-bracket-reduction-260725-v1.0.pdf"
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-hessian-difference-safe-packet-doob-bracket/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-hessian-difference-safe-packet-doob-bracket/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-hessian-difference-safe-packet-doob-bracket/result.json"

EXPECTED_PRIMARY_ASSERTIONS = 33
EXPECTED_INDEPENDENT_ASSERTIONS = 24
# Set to the observed fail-closed row count after the first complete package run.
EXPECTED_INTEGRATED_ASSERTIONS = 176
CHILD_TIMEOUT_SECONDS = 120

AUTHORITY_PATHS = {
    "a1_production": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "r050_k_composite": REPO / "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/classii_k_composite_manifest.json",
    "r063_balanced_jet": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r066_backward_heat": CLAIM_DIR / "classii_backward_heat_martingale_square_coupled_cartan_reduction_manifest.json",
    "r069_endpoint_lift": CLAIM_DIR / "classii_endpoint_lifted_schur_causal_grouping_reduction_manifest.json",
    "r070_wick_doob": CLAIM_DIR / "classii_wick_doob_terminal_resolvent_reduction_manifest.json",
    "r073_off_diagonal": CLAIM_DIR / "classii_off_diagonal_telescope_critical_phase_root_reduction_manifest.json",
    "r075_invariant_current": CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
    "r076_signed_transport": CLAIM_DIR / "classii_signed_transport_besov_bregman_resonance_manifest.json",
    "r077_causal_packet": CLAIM_DIR / "classii_causal_packet_payload_resonance_manifest.json",
}

AUTHORITY_RESULTS = {
    "r050_k_composite": REPO / "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/runs/2026-07-20-integrated-k-composite/result.json",
    "r063_balanced_jet": CLAIM_DIR / "runs/2026-07-22-integrated-balanced-coefficient-jet-continuum/result.json",
    "r066_backward_heat": CLAIM_DIR / "runs/2026-07-23-integrated-backward-heat-martingale-square-coupled-cartan-reduction/result.json",
    "r069_endpoint_lift": CLAIM_DIR / "runs/2026-07-24-integrated-endpoint-lifted-schur-causal-grouping-reduction/result.json",
    "r070_wick_doob": CLAIM_DIR / "runs/2026-07-24-integrated-wick-doob-terminal-resolvent-reduction/result.json",
    "r073_off_diagonal": CLAIM_DIR / "runs/2026-07-24-integrated-off-diagonal-telescope-critical-phase-root-reduction/result.json",
    "r075_invariant_current": CLAIM_DIR / "runs/2026-07-24-integrated-principal-taylor-oneform-graph-recovery/result.json",
    "r076_signed_transport": CLAIM_DIR / "runs/2026-07-24-integrated-signed-transport-besov-bregman-resonance/result.json",
    "r077_causal_packet": CLAIM_DIR / "runs/2026-07-25-integrated-causal-packet-payload-resonance/result.json",
}

AUTHORITY_RESULT_CONTRACTS = {
    "r050_k_composite": {"schema": "tect/a6-classii-k-composite-integrated-result/1.0", "claim": "A6-CLASSII-K-COMPOSITE-DEFINITION", "result_id": None, "integrated": 19, "aggregate": 64},
    "r063_balanced_jet": {"schema": "tect/a13-balanced-coefficient-jet-continuum-integrated-result/1.0", "claim": CLAIM, "result_id": "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-AND-A7-RECONSTRUCTION", "integrated": 48, "aggregate": 109},
    "r066_backward_heat": {"schema": "tect/a13-backward-heat-martingale-square-coupled-cartan-integrated-result/1.0", "claim": CLAIM, "result_id": "A13-CLASSII-BACKWARD-HEAT-MARTINGALE-SQUARE-COUPLED-CARTAN-REDUCTION", "integrated": 65, "aggregate": 103},
    "r069_endpoint_lift": {"schema": "tect/a13-endpoint-lifted-schur-causal-integrated-result/1.0", "claim": CLAIM, "result_id": "A13-CLASSII-ENDPOINT-LIFTED-SCHUR-CAUSAL-GROUPING-REDUCTION", "integrated": 70, "aggregate": 112},
    "r070_wick_doob": {"schema": "tect/a13-wick-doob-terminal-resolvent-integrated/1.0", "claim": CLAIM, "result_id": "A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION", "integrated": 47, "aggregate": 85},
    "r073_off_diagonal": {"schema": "tect/a13-off-diagonal-telescope-critical-phase-root-integrated/1.0", "claim": CLAIM, "result_id": "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-REDUCTION", "integrated": 51, "aggregate": 113},
    "r075_invariant_current": {"schema": "tect/a13-principal-taylor-oneform-graph-recovery-integrated/1.0", "claim": CLAIM, "result_id": "A13-CLASSII-PRINCIPAL-TAYLOR-ONE-FORM-GRAPH-RECOVERY-REDUCTION", "integrated": 76, "aggregate": 132},
    "r076_signed_transport": {"schema": "tect/a13-signed-transport-besov-bregman-resonance-integrated/1.0", "claim": CLAIM, "result_id": "A13-CLASSII-SIGNED-TRANSPORT-BESOV-BREGMAN-RESONANCE-REDUCTION", "integrated": 92, "aggregate": 131},
    "r077_causal_packet": {"schema": "tect/a13-causal-packet-payload-integrated/1.0", "claim": None, "result_id": "A13-CLASSII-CAUSAL-PACKET-PAYLOAD-RESONANCE-REDUCTION", "integrated": 110, "aggregate": 171},
}

SURFACE_CONTRACTS = {
    "claim": (CLAIM_DIR / "claim.md", [RESULT_ID, "Hessian-difference", "30/7", "60/19"]),
    "status": (CLAIM_DIR / "status.json", [RESULT_ID, "weighted innovation", "R-078"]),
    "roadmap": (REPO / "ROADMAP.md", [RESULT_ID, "A^2 DA", "future-control innovation"]),
    "gates": (REPO / "claims/GATES.md", [RESULT_ID, "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET"]),
    "results": (REPO / "RESULTS-LEDGER.md", ["R-078", "Hessian-difference", "60/19"]),
    "negative": (REPO / "negative-results/registry.md", ["AUDIT-2026-07-25-A13-R077-PACKET-DEFINITION", "NG-2026-07-25-A13-AHIGH-ABSOLUTE-AND-AUTOMATIC-BRACKET", "AUDIT-2026-07-25-A13-R078-PRE-RELEASE-PACKET-TO-BRACKET-ATTRIBUTION"]),
    "todo": (REPO / "todo/todo.json", ["A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET", "R-078"]),
    "changelog": (REPO / "changelog/log.jsonl", ["Prove A13 Hessian-difference safe-packet and Doob-bracket reduction", "Narrow R-078 packet-to-bracket attribution before release", "R-078"]),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", [RESULT_ID, "Hessian-difference", "full-packet reconstruction"]),
    "sector_a": (REPO / "theory/sectors/A.md", [CLAIM, "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET"]),
    "main_line": (REPO / "theory/main-proof-line.md", ["R-078", "30/7", "future-control"]),
    "proof_map": (REPO / "theory/proof-evidence-map.md", ["R-078", "Hessian-difference", "weighted innovation"]),
    "exploration": (REPO / "explorations/log.jsonl", ["R-078", "EXP-000068", "automatic bracket", "EXP-000069", "full safe-packet decomposition"]),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ["R-078", "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET"]),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ["R-078", "A^2 DA"]),
}

NOTE_TOKENS = [
    RESULT_ID,
    "Exact Hessian-difference transport",
    "Sharpened quadratic-payload Besov theorem",
    "Canonical complete-companion packet",
    "Exact bilinear innovation-bracket lemma",
    "Why the remaining absolute routes fail",
    "AUDIT-2026-07-25-A13-R077-PACKET-DEFINITION",
    "NG-2026-07-25-A13-AHIGH-ABSOLUTE-",
    "PRE-RELEASE-PACKET-TO-",
    "Devil's-advocate review",
    "Result footer",
]

PDF_TOKENS = [
    "HESSIAN-DIFFERENCE-SAFE-PACKET-DOOB-BRACKET",
    "Exact Hessian-difference transport",
    "Sharpened quadratic-payload Besov theorem",
    "Exact bilinear innovation-bracket lemma",
    "weighted innovation-Carleson",
    "Result footer",
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_child(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)], cwd=REPO, capture_output=True, text=True,
        timeout=CHILD_TIMEOUT_SECONDS, check=False,
    )


def normalized_pdf_text(path: Path) -> str:
    with pdfplumber.open(path) as document:
        text = "\n".join(page.extract_text() or "" for page in document.pages)
    return re.sub(r"\s+", " ", text)


def integrated_pass(record: dict[str, Any]) -> bool:
    """Normalize issued predecessor PASS schemas without accepting contradictions."""
    if "failures" in record:
        failures = record["failures"]
        if not isinstance(failures, list) or failures:
            return False
    if "failure_stage" in record and record["failure_stage"] is not None:
        return False
    row_group_seen = False
    for key in ("assertions", "cross_assertions", "integrated_assertions"):
        if key not in record:
            continue
        row_group_seen = True
        group = record[key]
        if not isinstance(group, list) or not group:
            return False
        if not all(isinstance(row, dict) and row.get("status") == "PASS" for row in group):
            return False
    if not row_group_seen:
        return False
    positive_signal = False
    summary = record.get("summary")
    if summary is not None:
        if not isinstance(summary, dict):
            return False
        if "verdict" in summary:
            if summary.get("verdict") != "PASS":
                return False
            positive_signal = True
        if any(key in summary for key in ("failed", "passed", "total")):
            counts_valid = isinstance(summary.get("passed"), int) and summary.get("passed") == summary.get("total") and summary.get("total", 0) > 0
            failure_valid = "failed" not in summary or summary.get("failed") == 0
            if not (counts_valid and failure_valid):
                return False
            positive_signal = True
    assertion_summary = record.get("assertion_summary")
    if assertion_summary is not None:
        if not isinstance(assertion_summary, dict):
            return False
        if not (isinstance(assertion_summary.get("integrated_total"), int) and assertion_summary.get("integrated_total", 0) > 0 and assertion_summary.get("integrated_passed") == assertion_summary.get("integrated_total")):
            return False
        positive_signal = True
    if "verdict" in record:
        verdict = record["verdict"]
        if not (verdict == "PASS" or (isinstance(verdict, str) and verdict.endswith("-PASS"))):
            return False
        positive_signal = True
    if "status" in record:
        if record["status"] != "PASS":
            return False
        positive_signal = True
    if "pass" in record:
        if record["pass"] is not True:
            return False
        positive_signal = True
    return positive_signal


def predecessor_rows(record: dict[str, Any]) -> list[dict[str, Any]] | None:
    for key in ("assertions", "cross_assertions", "integrated_assertions"):
        value = record.get(key)
        if isinstance(value, list):
            return value
    return None


def predecessor_aggregate(record: dict[str, Any]) -> int | None:
    for key in ("aggregate_assertions", "aggregate_assertion_count"):
        value = record.get(key)
        if isinstance(value, int):
            return value
    summary = record.get("summary")
    if isinstance(summary, dict):
        for key in ("aggregate_assertions", "total"):
            value = summary.get(key)
            if isinstance(value, int):
                return value
    assertion_summary = record.get("assertion_summary")
    if isinstance(assertion_summary, dict) and isinstance(assertion_summary.get("aggregate_total"), int):
        return assertion_summary["aggregate_total"]
    return None


def run() -> int:
    rows: list[dict[str, Any]] = []
    required = [MANIFEST, PRIMARY, INDEPENDENT, NOTE, PDF, *AUTHORITY_PATHS.values(), *AUTHORITY_RESULTS.values()]
    for path in required:
        add(rows, f"exists_{path.name}", path.exists(), path.exists(), True)
    if not all(path.exists() for path in required):
        passed = sum(row["status"] == "PASS" for row in rows)
        print(f"[R-078 integrated] {passed}/{len(rows)} FAIL -- missing required files")
        return 1

    manifest = load_json(MANIFEST)
    primary_process = run_child(PRIMARY)
    independent_process = run_child(INDEPENDENT)
    add(rows, "primary_exit_zero", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "independent_exit_zero", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "primary_sentinel", "33/33 PASS" in primary_process.stdout, primary_process.stdout.strip(), "contains 33/33 PASS")
    add(rows, "independent_sentinel", "24/24 PASS" in independent_process.stdout, independent_process.stdout.strip(), "contains 24/24 PASS")
    add(rows, "primary_output_exists", PRIMARY_OUTPUT.exists(), PRIMARY_OUTPUT.exists(), True)
    add(rows, "independent_output_exists", INDEPENDENT_OUTPUT.exists(), INDEPENDENT_OUTPUT.exists(), True)
    if not PRIMARY_OUTPUT.exists() or not INDEPENDENT_OUTPUT.exists():
        return 1

    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    expected_children = (
        ("primary", primary, EXPECTED_PRIMARY_ASSERTIONS, "tect/a13-hessian-safe-packet-doob-primary/1.0"),
        ("independent", independent, EXPECTED_INDEPENDENT_ASSERTIONS, "tect/a13-hessian-safe-packet-doob-independent/1.0"),
    )
    for label, payload, expected, schema in expected_children:
        add(rows, f"{label}_schema", payload.get("schema") == schema, payload.get("schema"), schema)
        add(rows, f"{label}_result_id", payload.get("result_id") == RESULT_ID, payload.get("result_id"), RESULT_ID)
        add(rows, f"{label}_claim_id", payload.get("claim_id") == CLAIM, payload.get("claim_id"), CLAIM)
        add(rows, f"{label}_source_version", payload.get("source_version") == "1.0.0", payload.get("source_version"), "1.0.0")
        add(rows, f"{label}_status", payload.get("status") == "PASS", payload.get("status"), "PASS")
        add(rows, f"{label}_assertions_passed", payload.get("assertions_passed") == expected, payload.get("assertions_passed"), expected)
        add(rows, f"{label}_assertions_total", payload.get("assertions_total") == expected, payload.get("assertions_total"), expected)
        assertion_rows = payload.get("assertions", [])
        add(rows, f"{label}_row_count", len(assertion_rows) == expected, len(assertion_rows), expected)
        add(rows, f"{label}_all_rows_pass", all(row.get("status") == "PASS" for row in assertion_rows), sum(row.get("status") == "PASS" for row in assertion_rows), expected)
        no_claims = payload.get("claims_not_established", {})
        add(rows, f"{label}_no_overclaim_flags", bool(no_claims) and all(value is False for value in no_claims.values()), no_claims, "all false")

    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    forbidden_import = re.search(r"(?:from|import)\s+a13_classii_hessian_difference_safe_packet_doob_bracket(?:\s|$)", independent_source)
    add(rows, "independent_does_not_import_primary", forbidden_import is None and independent.get("imports_primary") is False, {"source_import": bool(forbidden_import), "reported": independent.get("imports_primary")}, {"source_import": False, "reported": False})

    primary_exp = primary.get("exponents", {})
    independent_exp = independent.get("exponents", {})
    cross_fields = {
        "payload_x": ("payload_x", "payload_x"),
        "payload_y": ("payload_y", "payload_y"),
        "payload_slack": ("payload_slack", "payload_slack"),
        "payload_moment": ("payload_moment", "payload_moment"),
        "high_x": ("high_u_x", "high_x"),
        "high_y": ("high_u_y", "high_y"),
        "high_slack": ("high_u_slack", "high_slack"),
        "high_moment": ("high_u_moment", "high_moment"),
    }
    for label, (primary_key, independent_key) in cross_fields.items():
        actual = (primary_exp.get(primary_key), independent_exp.get(independent_key))
        add(rows, f"cross_{label}", actual[0] == actual[1], actual, "equal")
    exact_oracles = {
        "payload_x": "2/5", "payload_y": "11/30", "payload_slack": "7/30",
        "payload_moment": "30/7", "payload_eta": "12/7", "payload_zeta": "11/7",
        "high_u_x": "11/40", "high_u_y": "49/120", "high_u_slack": "19/60",
        "high_u_moment": "60/19", "high_u_eta": "33/38", "high_u_zeta": "49/38",
    }
    for key, oracle in exact_oracles.items():
        add(rows, f"primary_exact_{key}", primary_exp.get(key) == oracle, primary_exp.get(key), oracle)

    for key in ("direct_minus_cubic", "direct_minus_hessian", "d_a_difference", "d_x_difference"):
        add(rows, f"hessian_identity_{key}", primary.get("hessian_identity", {}).get(key) == "0", primary.get("hessian_identity", {}).get(key), "0")
    endpoint = primary.get("endpoint_packet", {})
    add(rows, "endpoint_master_identity", abs(float(endpoint.get("master_error", 1.0))) < 1.0e-12, endpoint.get("master_error"), 0.0)
    add(rows, "endpoint_companion_reassembly", abs(float(endpoint.get("p_reassembly_error", 1.0))) < 1.0e-12, endpoint.get("p_reassembly_error"), 0.0)
    add(rows, "endpoint_metric_positive", float(endpoint.get("q_min_eigenvalue", -1.0)) > 0.0, endpoint.get("q_min_eigenvalue"), ">0")
    for key in ("bracket_error", "product_error", "square_function_error"):
        add(rows, f"doob_{key}", abs(float(primary.get("doob", {}).get(key, 1.0))) < 1.0e-12, primary.get("doob", {}).get(key), 0.0)
    add(rows, "doob_square_nonzero", float(primary.get("doob", {}).get("square_sum", 0.0)) > 0.0, primary.get("doob", {}).get("square_sum"), ">0")
    add(rows, "primary_anti_centering_negative", float(primary.get("anti_centering", {}).get("charged_value", 1.0)) < 0.0, primary.get("anti_centering", {}).get("charged_value"), "<0")
    add(rows, "independent_anti_centering_negative", float(independent.get("anti_centering", {}).get("charged", 1.0)) < 0.0, independent.get("anti_centering", {}).get("charged"), "<0")
    add(rows, "independent_low_mode", abs(float(independent.get("anti_centering", {}).get("carrier_real", 0.0)) - 1.0) < 1.0e-12, independent.get("anti_centering", {}).get("carrier_real"), 1.0)

    for key, path in AUTHORITY_PATHS.items():
        entry = manifest.get("authority", {}).get(key, {})
        relative = path.relative_to(REPO).as_posix()
        add(rows, f"authority_path_{key}", entry.get("path") == relative, entry.get("path"), relative)
        add(rows, f"authority_hash_{key}", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))

    for key, path in AUTHORITY_RESULTS.items():
        entry = manifest.get("authority_results", {}).get(key, {})
        relative = path.relative_to(REPO).as_posix()
        add(rows, f"authority_result_path_{key}", entry.get("path") == relative, entry.get("path"), relative)
        add(rows, f"authority_result_hash_{key}", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))
        report = load_json(path)
        contract = AUTHORITY_RESULT_CONTRACTS[key]
        assertion_rows = predecessor_rows(report)
        claim_values = [report[field] for field in ("claim", "claim_id") if field in report]
        valid_claim = contract["claim"] is None or (bool(claim_values) and all(value == contract["claim"] for value in claim_values))
        valid_manifest = "manifest_sha256" not in report or report.get("manifest_sha256") == digest(AUTHORITY_PATHS[key])
        valid = (
            integrated_pass(report)
            and report.get("schema") == contract["schema"]
            and (contract["result_id"] is None or report.get("result_id") == contract["result_id"])
            and valid_claim
            and isinstance(assertion_rows, list)
            and len(assertion_rows) == contract["integrated"]
            and predecessor_aggregate(report) == contract["aggregate"]
            and valid_manifest
            and ("assertion_count" not in report or report.get("assertion_count") == contract["integrated"])
            and ("passed_assertions" not in report or report.get("passed_assertions") == contract["integrated"])
            and ("assertions_passed" not in report or report.get("assertions_passed") == contract["integrated"])
            and ("assertions_total" not in report or report.get("assertions_total") == contract["integrated"])
        )
        actual_contract = {"schema": report.get("schema"), "result_id": report.get("result_id"), "claim": claim_values, "rows": len(assertion_rows or []), "aggregate": predecessor_aggregate(report), "manifest": valid_manifest, "pass": integrated_pass(report)}
        add(rows, f"authority_result_contract_{key}", valid, actual_contract, contract)

    sources = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": Path(__file__).resolve(), "proof_note": NOTE}
    for key, path in sources.items():
        entry = manifest.get("sources", {}).get(key, {})
        relative = path.relative_to(REPO).as_posix()
        add(rows, f"source_path_{key}", entry.get("path") == relative, entry.get("path"), relative)
        add(rows, f"source_hash_{key}", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))

    pdf_entry = manifest.get("proof_pdf", {})
    relative_pdf = PDF.relative_to(REPO).as_posix()
    add(rows, "pdf_manifest_path", pdf_entry.get("path") == relative_pdf, pdf_entry.get("path"), relative_pdf)
    add(rows, "pdf_manifest_hash", pdf_entry.get("sha256") == digest(PDF), pdf_entry.get("sha256"), digest(PDF))
    reader = PdfReader(PDF)
    add(rows, "pdf_page_count", len(reader.pages) == 9 and pdf_entry.get("pages") == 9, {"actual": len(reader.pages), "manifest": pdf_entry.get("pages")}, 9)
    add(rows, "pdf_size", PDF.stat().st_size > 100_000 and pdf_entry.get("size_bytes") == PDF.stat().st_size, {"actual": PDF.stat().st_size, "manifest": pdf_entry.get("size_bytes")}, ">100000 and exact manifest")
    add(rows, "pdf_form_none", not (reader.get_fields() or {}) and pdf_entry.get("form_check") == "PASS", {"fields": len(reader.get_fields() or {}), "manifest": pdf_entry.get("form_check")}, {"fields": 0, "manifest": "PASS"})
    pdf_text = normalized_pdf_text(PDF)
    add(rows, "pdf_required_tokens", all(token in pdf_text for token in PDF_TOKENS), {token: token in pdf_text for token in PDF_TOKENS}, "all true")
    add(rows, "pdf_no_literal_debris", all(token not in pdf_text.lower() for token in ("qquad", "undefined", "overfull")), {token: token in pdf_text.lower() for token in ("qquad", "undefined", "overfull")}, "all false")
    add(rows, "pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS" and "nine pages" in pdf_entry.get("visual_qa_note", "").lower(), {"status": pdf_entry.get("visual_qa"), "note": pdf_entry.get("visual_qa_note")}, "PASS and nine-page note")

    note_text = NOTE.read_text(encoding="utf-8")
    add(rows, "note_required_tokens", all(token in note_text for token in NOTE_TOKENS), {token: token in note_text for token in NOTE_TOKENS}, "all true")
    bare_qquad = re.search(r"(?<!\\)qquad", note_text)
    add(rows, "note_no_bare_qquad", bare_qquad is None, bool(bare_qquad), False)
    add(rows, "note_no_overfull_marker", "Overfull \\hbox" not in note_text, "Overfull \\hbox" in note_text, False)

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-classii-hessian-difference-safe-packet-doob-bracket-reduction/1.0", manifest.get("schema"), "tect/a13-classii-hessian-difference-safe-packet-doob-bracket-reduction/1.0")
    add(rows, "manifest_version", manifest.get("package_version") == __version__, manifest.get("package_version"), __version__)
    add(rows, "manifest_result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_tier_boundary", "T4" in manifest.get("status", "") and "OPEN" in manifest.get("status", ""), manifest.get("status"), "contains T4 and OPEN")
    not_established = manifest.get("claims_not_established", {})
    add(rows, "manifest_no_overclaim_flags", bool(not_established) and all(value is False for value in not_established.values()), not_established, "all false")
    successor = "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET"
    add(rows, "manifest_successor", manifest.get("consequence", {}).get("next_subgate") == successor, manifest.get("consequence", {}).get("next_subgate"), successor)
    run_contract = manifest.get("run_contract", {})
    add(rows, "manifest_primary_count", run_contract.get("primary_assertions") == EXPECTED_PRIMARY_ASSERTIONS, run_contract.get("primary_assertions"), EXPECTED_PRIMARY_ASSERTIONS)
    add(rows, "manifest_independent_count", run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT_ASSERTIONS, run_contract.get("independent_assertions"), EXPECTED_INDEPENDENT_ASSERTIONS)
    if EXPECTED_INTEGRATED_ASSERTIONS:
        add(rows, "manifest_integrated_count", run_contract.get("integrated_assertions") == EXPECTED_INTEGRATED_ASSERTIONS, run_contract.get("integrated_assertions"), EXPECTED_INTEGRATED_ASSERTIONS)
        expected_aggregate = EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS + EXPECTED_INTEGRATED_ASSERTIONS
        add(rows, "manifest_aggregate_count", run_contract.get("aggregate_assertions") == expected_aggregate, run_contract.get("aggregate_assertions"), expected_aggregate)

    for label, (path, tokens) in SURFACE_CONTRACTS.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        add(rows, f"surface_{label}", path.exists() and all(token in text for token in tokens), {"exists": path.exists(), **{token: token in text for token in tokens}}, "exists and all true")

    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    aggregate = EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS + total
    payload = {
        "schema": "tect/a13-hessian-safe-packet-doob-integrated/1.0",
        "result_id": RESULT_ID,
        "claim_id": CLAIM,
        "version": __version__,
        "status": "PASS" if passed == total else "FAIL",
        "assertions_passed": passed,
        "assertions_total": total,
        "aggregate_assertions": aggregate,
        "assertions": rows,
        "authority_hashes": {key: digest(path) for key, path in AUTHORITY_PATHS.items()},
        "authority_result_hashes": {key: digest(path) for key, path in AUTHORITY_RESULTS.items()},
        "source_hashes": {key: digest(path) for key, path in sources.items()},
        "manifest_sha256": digest(MANIFEST),
        "child_runs": {"primary": primary, "independent": independent},
        "child_outputs": {"primary": PRIMARY_OUTPUT.relative_to(REPO).as_posix(), "independent": INDEPENDENT_OUTPUT.relative_to(REPO).as_posix()},
        "pdf_contract": {"pages": len(reader.pages), "size_bytes": PDF.stat().st_size, "form_fields": len(reader.get_fields() or {}), "visual_qa": pdf_entry.get("visual_qa")},
        "honesty_boundary": manifest.get("honesty_boundary"),
        "source_sha256": digest(Path(__file__).resolve()),
    }
    atomic_json(OUTPUT, payload)
    if passed == total:
        print(f"[R-078 integrated] {passed}/{total} PASS; aggregate {aggregate}/{aggregate} PASS")
    else:
        print(f"[R-078 integrated] {passed}/{total} FAIL; aggregate {passed + EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS}/{aggregate}")
        for row in rows:
            if row["status"] != "PASS":
                print(f"FAIL {row['name']}: actual={row['actual']!r} expected={row['expected']!r}")
    print(f"result: {OUTPUT.relative_to(REPO).as_posix()}")
    exact_count = not EXPECTED_INTEGRATED_ASSERTIONS or total == EXPECTED_INTEGRATED_ASSERTIONS
    return 0 if passed == total and exact_count else 1


if __name__ == "__main__":
    raise SystemExit(run())
