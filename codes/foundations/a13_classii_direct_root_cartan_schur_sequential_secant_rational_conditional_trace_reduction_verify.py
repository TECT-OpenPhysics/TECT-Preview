#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-088 A13 package."""

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

import pdfplumber
from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-DIRECT-ROOT-CARTAN-SCHUR-SEQUENTIAL-SECANT-RATIONAL-CONDITIONAL-TRACE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_independent.py"
MANIFEST = CLAIM_DIR / "classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-reduction-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-direct-root-cartan-schur-sequential-secant-rational-conditional-trace/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-direct-root-cartan-schur-sequential-secant-rational-conditional-trace/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-direct-root-cartan-schur-sequential-secant-rational-conditional-trace/result.json"
EXPECTED_PRIMARY = 66
EXPECTED_INDEPENDENT = 95
EXPECTED_PAGES = 11
CHILD_TIMEOUT_SECONDS = 120


AUTHORITY = {
    "r084_root_diagonal": (
        CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-root-diagonal-cartan-ou-linear-pf-absorption/result.json",
    ),
    "r085_boundary": (
        CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json",
    ),
    "r087_reduction": (
        CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json",
    ),
}


SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-088", RESULT_ID, "16.30295538482827", "Sector A remains open")),
    "roadmap": (REPO / "ROADMAP.md", ("R-088", "sequential", "OVERLAP", "Sector A remains open")),
    "gates": (REPO / "claims/GATES.md", ("R-088", "s>0", "same-root")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "16.30295538482827", "Sector A remains open")),
    "claim": (CLAIM_DIR / "claim.md", ("R-088", RESULT_ID, "conditional")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-088", "Direct-root", "controlled-shell one-use")),
    "todo": (REPO / "todo/todo.json", ("R-088", "sequential", "Sector A remains open")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-088", "sequential", "OVERLAP")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-088", "16.30295538482827", "Sector A remains open")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-088", "16.30295538482827", "Sector A remains open")),
    "sector": (REPO / "theory/sectors/A.md", ("RATIONAL-STANDALONE-ETA-DEBT-AND-K-HEAT",)),
    "negative_registry": (
        REPO / "negative-results/registry.md",
        (
            "AUDIT-2026-07-25-A13-R085-CARTAN-OUTER-WEIGHT-NORMALIZATION",
            "NG-2026-07-25-A13-RATIONAL-STANDALONE-ETA-DEBT-AND-K-HEAT",
        ),
    ),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000131", "EXP-000138", "EXP-000139", "EXP-000140", "R-088")),
    "changelog": (REPO / "CHANGELOG.md", ("R-088", "Direct-root Cartan Schur")),
}


NOTE_TOKENS = (
    "Exact target and normalization audit",
    "Direct-root nonorthogonal Schur theorem",
    "Exact sequential Cartan secant",
    "Quartic Besov one-use payload",
    "Rational completion as a conditional packet",
    "Matrix-fractional heat boundary",
    "AUDIT-2026-07-25-A13-R085-CARTAN-OUTER-WEIGHT-NORMALIZATION",
    "NG-2026-07-25-A13-RATIONAL-STANDALONE-ETA-DEBT-AND-K-HEAT",
    "Attempt and evidence map",
    "Devil's-advocate review",
    "No-overclaim statement",
)


PDF_TOKENS = (
    "Direct-root Cartan Schur",
    "normalization audit",
    "Exact sequential Cartan secant",
    "Quartic Besov",
    "conditional moment criterion",
    "Matrix-fractional heat boundary",
    "Attempt and evidence map",
    "Result footer",
)


REQUIRED_FALSE = (
    "production_sequential_secant_to_quartic_bridge",
    "direct_integrated_cartan_cfar",
    "coefficient_dominant_rational_causal_packet",
    "rational_shifted_hessian_form_bound",
    "complete_regular_packet_lower_bound",
    "overlap_uniform_bound",
    "controlled_shell_one_use",
    "nelson_bound",
    "interacting_measure",
    "sector_a_closure",
    "tier_promotion",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})


def run_child(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=CHILD_TIMEOUT_SECONDS,
        check=False,
    )


def record_passes(record: dict[str, Any]) -> bool:
    rows = record.get("assertions")
    names = [row.get("name") for row in rows] if isinstance(rows, list) else []
    return (
        record.get("status") == "PASS"
        and isinstance(rows, list)
        and bool(rows)
        and all(isinstance(row, dict) and row.get("status") == "PASS" for row in rows)
        and len(rows) == record.get("assertions_total") == record.get("assertions_passed")
        and len(names) == len(set(names))
    )


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else None


def authority_passes(record: dict[str, Any]) -> bool:
    assertion_rows = record.get("assertions") or record.get("integrated_assertions") or record.get("cross_assertions")
    verdict = record.get("status") == "PASS" and record.get("pass") is True
    return bool(
        verdict
        and isinstance(assertion_rows, list)
        and assertion_rows
        and all(row.get("status") == "PASS" for row in assertion_rows)
        and len(assertion_rows) == record.get("assertions_total") == record.get("assertions_passed")
    )


def main() -> int:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    try:
        manifest = load_json(MANIFEST)
    except Exception as exc:
        manifest = {}
        failures.append(f"manifest: {exc}")

    child_specs = (
        ("primary", PRIMARY, PRIMARY_OUTPUT, f"[R-088 primary] {EXPECTED_PRIMARY}/{EXPECTED_PRIMARY} PASS", EXPECTED_PRIMARY),
        ("independent", INDEPENDENT, INDEPENDENT_OUTPUT, f"[R-088 independent] {EXPECTED_INDEPENDENT}/{EXPECTED_INDEPENDENT} PASS", EXPECTED_INDEPENDENT),
    )
    records: dict[str, dict[str, Any]] = {}
    for label, child, output, marker, expected_count in child_specs:
        try:
            completed = run_child(child)
        except Exception as exc:
            completed = None
            failures.append(f"{label} execution: {exc}")
        output_text = "" if completed is None else completed.stdout + completed.stderr
        add(rows, f"{label}_exit_zero", completed is not None and completed.returncode == 0, None if completed is None else completed.returncode, 0)
        add(rows, f"{label}_marker", marker in output_text, output_text.strip(), marker)
        add(rows, f"{label}_result_exists", output.exists(), str(output.relative_to(REPO)), "exists")
        try:
            record = load_json(output)
        except Exception as exc:
            record = {}
            failures.append(f"{label} result: {exc}")
        records[label] = record
        add(rows, f"{label}_record_passes", record_passes(record), record.get("status"), "PASS with all rows")
        add(rows, f"{label}_count", record.get("assertions_total") == expected_count, record.get("assertions_total"), expected_count)
        add(rows, f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)
        add(rows, f"{label}_claim_id", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)

    primary = records.get("primary", {})
    independent = records.get("independent", {})
    add(rows, "primary_schema", primary.get("schema") == "tect/a13-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-primary/1.0", primary.get("schema"), "primary/1.0")
    add(rows, "independent_schema", independent.get("schema") == "tect/a13-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-independent/1.0", independent.get("schema"), "independent/1.0")
    primary_names = {row.get("name") for row in primary.get("assertions", []) if isinstance(row, dict)}
    independent_names = {row.get("name") for row in independent.get("assertions", []) if isinstance(row, dict)}
    required_primary_names = {
        "sequential_three_channel_identity",
        "sequential_shell_telescope",
        "three_channel_tame_fixture_1",
        "hs_envelope_fixture",
        "hypothetical_secant_ansatz_exponent",
        "standalone_debt_fixed_target_covariance_growth",
        "centered_matched_square_variance_cancels_debt",
    }
    required_independent_names = {
        "sequential_finite_difference_1",
        "sequential_telescope_1",
        "hypothetical_secant_ansatz_exponent",
        "standalone_debt_fixed_target_covariance_growth",
        "centered_matched_square_variance_cancels_debt",
        "conditional_rational_1",
        "pointwise_trace_null_1",
        "jensen_identity_1",
    }
    add(rows, "primary_required_rows", required_primary_names.issubset(primary_names), sorted(required_primary_names - primary_names), [])
    add(rows, "independent_required_rows", required_independent_names.issubset(independent_names), sorted(required_independent_names - independent_names), [])

    p_direct = primary.get("direct_cartan", {})
    i_direct = independent.get("direct_cartan", {})
    direct_specs = (
        ("s", "7/12"),
        ("eta", "7/12"),
        ("threshold", "s>0"),
        ("gap_factor", "2^(-7C/6)"),
        ("ledger", "sum_k q_k"),
        ("old_qmod_direct_growth", "N^5"),
        ("hypothetical_secant_ansatz_scaling", "N^(-5/6) under unproved toy ansatz"),
        ("quartic_besov_range", "0<s<1"),
    )
    for key, expected in direct_specs:
        add(rows, f"cross_direct_{key}", p_direct.get(key) == i_direct.get(key) == expected, [p_direct.get(key), i_direct.get(key)], expected)
    try:
        p_constant = float(p_direct.get("constant", float("nan")))
        i_constant = float(i_direct.get("constant", float("nan")))
    except Exception:
        p_constant = i_constant = float("nan")
    add(rows, "cross_direct_constant", abs(p_constant - i_constant) < 1e-13 and abs(p_constant - 16.30295538482827) < 1e-13, [p_constant, i_constant], 16.30295538482827)
    add(rows, "primary_r085_retained", p_direct.get("r085_weighted_theorem_retained") is True, p_direct.get("r085_weighted_theorem_retained"), True)
    add(rows, "primary_sequential_identity", p_direct.get("sequential_secant_identity") is True, p_direct.get("sequential_secant_identity"), True)
    add(rows, "primary_quartic_payload", "X^(1/2) Y_A^(1/2)" in str(p_direct.get("quartic_payload")), p_direct.get("quartic_payload"), "critical pure-control payload")
    for key, threshold in (
        ("max_finite_difference_residual", 2e-8),
        ("max_sequential_identity_residual", 2e-12),
        ("max_telescope_residual", 2e-12),
    ):
        try:
            value = float(i_direct.get(key, float("inf")))
        except Exception:
            value = float("inf")
        add(rows, f"independent_{key}", value < threshold, value, f"<{threshold}")
    try:
        schur_ratio = float(i_direct.get("max_random_schur_ratio", float("inf")))
        cauchy_residual = float(i_direct.get("max_weighted_cauchy_residual", float("inf")))
    except Exception:
        schur_ratio = cauchy_residual = float("inf")
    direct_s = float(Fraction(str(p_direct.get("s", "0"))))
    direct_bound = p_constant * 2.0 ** (-2.0 * direct_s * 5)
    add(rows, "independent_random_schur", schur_ratio <= direct_bound + 1e-12, schur_ratio, f"<={direct_bound}")
    add(rows, "independent_weighted_cauchy", cauchy_residual <= 0.0, cauchy_residual, "<=0")

    p_rational = primary.get("rational", {})
    i_rational = independent.get("rational", {})
    add(rows, "rational_pointwise_null", p_rational.get("pointwise_null") == "G^T K_eta G/2-K_eta:Q/2-D_eta=0", p_rational.get("pointwise_null"), "exact null")
    add(rows, "rational_conditional_formula", p_rational.get("conditional_formula") == "square(mu)+M_eta:mu mu^T/2+L:(V-Gamma)/2", p_rational.get("conditional_formula"), "conditional formula")
    add(rows, "rational_centered_matched", p_rational.get("centered_covariance_matched") == "E[P|H]=c^T B_1 c/2", p_rational.get("centered_covariance_matched"), "centered covariance-matched closure")
    add(rows, "rational_jensen_psd", p_rational.get("matrix_fractional_jensen_psd") is True, p_rational.get("matrix_fractional_jensen_psd"), True)
    add(rows, "rational_wick_signed", p_rational.get("wick_contraction_signed") is True, p_rational.get("wick_contraction_signed"), True)
    add(rows, "rational_centered_matched_variance_cancellation", i_rational.get("centered_covariance_matched_square_variance_cancels_debt") is True, i_rational.get("centered_covariance_matched_square_variance_cancels_debt"), True)
    add(rows, "rational_adapted_fixture_negative", i_rational.get("same_root_adapted_fixture_negative") is True, i_rational.get("same_root_adapted_fixture_negative"), True)
    for key, threshold in (
        ("max_conditional_residual", 2e-12),
        ("max_pointwise_null_residual", 2e-12),
        ("max_jensen_identity_residual", 2e-12),
    ):
        try:
            value = float(i_rational.get(key, float("inf")))
        except Exception:
            value = float("inf")
        add(rows, f"independent_{key}", value < threshold, value, f"<{threshold}")
    try:
        min_jensen = float(i_rational.get("min_jensen_eigenvalue", float("-inf")))
    except Exception:
        min_jensen = float("-inf")
    add(rows, "independent_jensen_psd", min_jensen > -2e-10, min_jensen, ">-2e-10")

    negative_ids = {
        "AUDIT-2026-07-25-A13-R085-CARTAN-OUTER-WEIGHT-NORMALIZATION",
        "NG-2026-07-25-A13-RATIONAL-STANDALONE-ETA-DEBT-AND-K-HEAT",
    }
    add(rows, "primary_negative_ids", set(primary.get("negative_results", [])) == negative_ids, primary.get("negative_results"), sorted(negative_ids))
    add(rows, "independent_negative_ids", set(independent.get("negative_results", [])) == negative_ids, independent.get("negative_results"), sorted(negative_ids))
    primary_open = primary.get("claims_not_established", {})
    independent_open = independent.get("claims_not_established", {})
    add(rows, "primary_open_flags_false", set(REQUIRED_FALSE).issubset(primary_open) and all(value is False for value in primary_open.values()), primary_open, "all values false and required keys present")
    add(rows, "independent_open_flags_false", set(REQUIRED_FALSE).issubset(independent_open) and all(value is False for value in independent_open.values()), independent_open, "all values false and required keys present")

    add(rows, "manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add(rows, "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_t4_open", "T4" in str(manifest.get("status")) and "OPEN" in str(manifest.get("status")), manifest.get("status"), "T4 with open gates")

    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        pin = manifest.get("authority", {}).get(label, {})
        add(rows, f"{label}_manifest_exists", authority_manifest.exists(), str(authority_manifest.relative_to(REPO)), "exists")
        add(rows, f"{label}_manifest_hash", authority_manifest.exists() and pin.get("manifest", {}).get("sha256") == digest(authority_manifest), pin.get("manifest", {}).get("sha256"), None if not authority_manifest.exists() else digest(authority_manifest))
        add(rows, f"{label}_result_exists", authority_result.exists(), str(authority_result.relative_to(REPO)), "exists")
        add(rows, f"{label}_result_hash", authority_result.exists() and pin.get("result", {}).get("sha256") == digest(authority_result), pin.get("result", {}).get("sha256"), None if not authority_result.exists() else digest(authority_result))
        try:
            authority_record = load_json(authority_result)
        except Exception:
            authority_record = {}
        add(rows, f"{label}_result_passes", authority_passes(authority_record), authority_record.get("status", authority_record.get("verdict")), "PASS")

    source_entries = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": Path(__file__).resolve(), "proof_note": NOTE}
    for label, path in source_entries.items():
        pin = manifest.get("sources", {}).get(label, {})
        add(rows, f"{label}_source_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        add(rows, f"{label}_source_hash", path.exists() and pin.get("sha256") == digest(path), pin.get("sha256"), None if not path.exists() else digest(path))
        if label != "proof_note":
            add(rows, f"{label}_source_version", path.exists() and pin.get("version") == source_version(path), pin.get("version"), None if not path.exists() else source_version(path))

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    for index, token in enumerate(NOTE_TOKENS, start=1):
        add(rows, f"note_token_{index}", token in note_text, token if token in note_text else None, token)
    control_chars = [ord(character) for character in note_text if ord(character) < 32 and character not in "\t\n\r"]
    add(rows, "note_no_control_chars", not control_chars, control_chars, [])
    add(rows, "note_exact_normalization", all(token in note_text for token in ("no outer", "sum_kq_k", "s>0", "16.30295538482827")), "normalization language present", "present")
    add(rows, "note_honesty_boundary", all(token in note_text for token in ("expectation inside", "same-root", "Sector-A closure", "Tier stays T4")), "open production boundaries present", "present")
    add(rows, "note_ou_atom_mapping", "v_{A,j,k,t}:=P_t^{(j)}u_{A,j,k,t}" in note_text and "Q_{j,C}\\sum_{k\\le j}v_{A,j,k,t}" in note_text, "OU action absorbed consistently", "present")
    add(rows, "note_high_high_low_sum", all(token in note_text for token in ("high--high-to-low", "sum_{n\\le j+c}2^{sn}", "including high--high-to-low outputs")), "geometric low-output sum present", "present")
    add(rows, "note_toy_ansatz_firewall", all(token in note_text for token in ("unproved toy ansatz", "not evidence for the production atom", "precisely the open far-frequency")), "toy arithmetic expressly non-evidentiary", "present")
    add(rows, "note_fixed_dimension_debt", all(token in note_text for token in ("d=6", "Gamma_N=\\rho_N I_6", "target dimension fixed")), "fixed-dimension covariance fixture present", "present")
    add(rows, "note_rational_hypotheses", all(token in note_text for token in ("Let $\\eta>0$", "symmetric positive semidefinite", "positive definite", "displayed product is integrable")), "structural and integrability hypotheses present", "present")
    add(rows, "note_terminal_class_boundary", all(token in note_text for token in ("regular orthogonal no-revisit one-shot", "R-079 (6.4)", "general progressive revisiting control")), "terminal bridge restricted to accepted class", "present")
    add(rows, "note_no_literal_markup_debris", ",qquad" not in note_text and "¨" not in note_text, {"comma_qquad": note_text.count(",qquad"), "diaeresis": note_text.count("¨")}, {"comma_qquad": 0, "diaeresis": 0})

    pdf_text = ""
    pages = 0
    encrypted = True
    has_forms = True
    try:
        reader = PdfReader(str(PDF))
        pages = len(reader.pages)
        encrypted = reader.is_encrypted
        has_forms = bool(reader.get_fields())
        with pdfplumber.open(PDF) as document:
            pdf_text = "\n".join((page.extract_text() or "") for page in document.pages)
    except Exception as exc:
        failures.append(f"pdf: {exc}")
    add(rows, "pdf_exists", PDF.exists(), str(PDF.relative_to(REPO)), "exists")
    add(rows, "pdf_pages", pages == EXPECTED_PAGES, pages, EXPECTED_PAGES)
    add(rows, "pdf_not_encrypted", not encrypted, encrypted, False)
    add(rows, "pdf_no_forms", not has_forms, has_forms, False)
    for index, token in enumerate(PDF_TOKENS, start=1):
        add(rows, f"pdf_token_{index}", token in pdf_text, token if token in pdf_text else None, token)
    add(rows, "pdf_no_text_debris", "qquad" not in pdf_text and "�" not in pdf_text, {"qquad": pdf_text.count("qquad"), "replacement": pdf_text.count("�")}, {"qquad": 0, "replacement": 0})
    pdf_pin = manifest.get("proof_pdf", {})
    add(rows, "pdf_hash", PDF.exists() and pdf_pin.get("sha256") == digest(PDF), pdf_pin.get("sha256"), None if not PDF.exists() else digest(PDF))
    add(rows, "pdf_size", PDF.exists() and pdf_pin.get("size_bytes") == PDF.stat().st_size, pdf_pin.get("size_bytes"), None if not PDF.exists() else PDF.stat().st_size)
    add(rows, "pdf_manifest_pages", pdf_pin.get("pages") == EXPECTED_PAGES, pdf_pin.get("pages"), EXPECTED_PAGES)
    add(rows, "pdf_visual_qa", pdf_pin.get("visual_qa") == "PASS", pdf_pin.get("visual_qa"), "PASS")
    add(rows, "pdf_overfull_zero", pdf_pin.get("overfull_hbox_count") == 0, pdf_pin.get("overfull_hbox_count"), 0)

    for label, (path, tokens) in SURFACES.items():
        surface_text = path.read_text(encoding="utf-8") if path.exists() else ""
        add(rows, f"surface_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        add(rows, f"surface_{label}_tokens", all(token in surface_text for token in tokens), [token for token in tokens if token not in surface_text], [])

    try:
        status_record = load_json(CLAIM_DIR / "status.json")
    except Exception as exc:
        status_record = {}
        failures.append(f"status: {exc}")
    expected_gates = {
        "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET",
        "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION",
        "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE",
    }
    add(rows, "status_tier_stays_t4", status_record.get("tier") == "T4" and status_record.get("t7_candidate") is False, {"tier": status_record.get("tier"), "t7": status_record.get("t7_candidate")}, {"tier": "T4", "t7": False})
    add(rows, "status_open_gates_exact", set(status_record.get("open_gates", [])) == expected_gates, status_record.get("open_gates"), sorted(expected_gates))
    add(rows, "status_reproduction_command", status_record.get("reproduction", {}).get("command") == f"python {Path(__file__).resolve().relative_to(REPO).as_posix()}", status_record.get("reproduction", {}).get("command"), f"python {Path(__file__).resolve().relative_to(REPO).as_posix()}")
    add(rows, "status_no_overclaim_complete", all(token in str(status_record.get("no_overclaim", "")) for token in ("R-088", "production sequential", "same-root", "Sector-A closure", "remain open")), "structured no-overclaim boundary", "present")

    claims_not = manifest.get("claims_not_established", {})
    add(rows, "manifest_open_flags_false", set(REQUIRED_FALSE).issubset(claims_not) and all(value is False for value in claims_not.values()), claims_not, "all values false and required keys present")
    consequence = manifest.get("consequence", {})
    add(rows, "manifest_direct_schur_true", consequence.get("direct_root_unweighted_schur") is True and consequence.get("direct_root_threshold") == "s>0", {"proved": consequence.get("direct_root_unweighted_schur"), "threshold": consequence.get("direct_root_threshold")}, "proved for s>0")
    add(rows, "manifest_weighted_theorem_retained", consequence.get("r085_weighted_theorem_retained") is True, consequence.get("r085_weighted_theorem_retained"), True)
    add(rows, "manifest_sequential_identity_true", consequence.get("sequential_cartan_secant_identity") is True, consequence.get("sequential_cartan_secant_identity"), True)
    add(rows, "manifest_quartic_payload_true", consequence.get("quartic_besov_payload") is True, consequence.get("quartic_besov_payload"), True)
    add(rows, "manifest_rational_null_true", consequence.get("rational_pointwise_square_wick_debt_null_identity") is True, consequence.get("rational_pointwise_square_wick_debt_null_identity"), True)
    add(rows, "manifest_conditional_criterion_true", consequence.get("rational_conditional_moment_criterion") is True, consequence.get("rational_conditional_moment_criterion"), True)
    add(rows, "manifest_centered_branch_true", consequence.get("centered_covariance_matched_branch") is True, consequence.get("centered_covariance_matched_branch"), True)
    add(rows, "manifest_production_bridge_false", consequence.get("production_sequential_secant_to_quartic_bridge") is False, consequence.get("production_sequential_secant_to_quartic_bridge"), False)
    add(rows, "manifest_same_root_packet_false", consequence.get("complete_same_root_rational_packet") is False, consequence.get("complete_same_root_rational_packet"), False)
    add(rows, "manifest_negative_registered", set(manifest.get("negative_results", [])) == negative_ids, manifest.get("negative_results"), sorted(negative_ids))
    add(rows, "manifest_proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add(rows, "manifest_tier_unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add(rows, "manifest_no_overclaim", all(token in str(manifest.get("no_overclaim", "")) for token in ("toy ansatz", "production sequential", "same-root", "Sector-A closure")), manifest.get("no_overclaim"), "explicit open-scope firewall")

    run_contract = manifest.get("run_contract", {})
    expected_integrated = len(rows) + 1
    expected_aggregate = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + expected_integrated
    add(
        rows,
        "manifest_run_counts",
        run_contract.get("primary_assertions") == EXPECTED_PRIMARY
        and run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT
        and run_contract.get("integrated_assertions") == expected_integrated
        and run_contract.get("aggregate_assertions") == expected_aggregate,
        run_contract,
        [EXPECTED_PRIMARY, EXPECTED_INDEPENDENT, expected_integrated, expected_aggregate],
    )

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-integrated/1.0",
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) and not failures else "FAIL",
        "pass": passed == len(rows) and not failures,
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "aggregate_assertions": EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + len(rows),
        "assertions": rows,
        "failures": failures,
        "cross_summary": {
            "primary": EXPECTED_PRIMARY,
            "independent": EXPECTED_INDEPENDENT,
            "integrated": len(rows),
            "aggregate": EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + len(rows),
        },
        "proved_scope": "manifest-pinned R-088 direct-root unweighted Schur theorem, exact sequential Cartan secant, quartic Besov payload, rational pointwise cancellation and conditional moment criterion",
        "open_scope": "production sequential Cartan bridge or direct CFAR, complete same-root rational packet, REG, OVERLAP, controlled-shell one-use, Nelson, measure, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    if payload["pass"]:
        print(f"[R-088 integrated] {passed}/{len(rows)} PASS; aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}")
        return 0
    failed_names = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-088 integrated] {passed}/{len(rows)} PASS; failed={failed_names}; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
