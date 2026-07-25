#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-090 A13 boundary package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

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

import pdfplumber
from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER-NOGO-RATIONAL-FOREST-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_cartan_excess_tail_rational_forest_nonduplication_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_cartan_excess_tail_rational_forest_nonduplication_boundary_independent.py"
MANIFEST = CLAIM_DIR / "classii_global_unprojected_cartan_ledger_nogo_rational_forest_boundary_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-cartan-excess-tail-rational-forest-nonduplication/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-cartan-excess-tail-rational-forest-nonduplication/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-cartan-excess-tail-rational-forest-nonduplication/result.json"
EXPECTED_PRIMARY = 57
EXPECTED_INDEPENDENT = 52
CHILD_TIMEOUT_SECONDS = 120


AUTHORITY = {
    "r063_wick": (
        CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
        CLAIM_DIR / "runs/2026-07-22-integrated-balanced-coefficient-jet-continuum/result.json",
    ),
    "r079_current": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r089_boundary": (
        CLAIM_DIR / "classii_progressive_covariance_compression_rational_mean_spectral_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-progressive-covariance-compression-rational-mean-spectral-boundary/result.json",
    ),
}


SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-090", RESULT_ID, "projected CFAR")),
    "roadmap": (REPO / "ROADMAP.md", ("R-090", "H_C", "H_N", "H_A")),
    "gates": (REPO / "claims/GATES.md", ("R-090", "projected", "nonduplicating")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "R-090", "Sector A remains open")),
    "claim": (CLAIM_DIR / "claim.md", ("R-090", RESULT_ID, "unprojected")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-090", "Global unprojected", "H_C")),
    "todo": (REPO / "todo/todo.json", ("R-090", "H_C", "Sector A remains open")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-090", "H_C", "H_N", "H_A")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-090", "unprojected", "projected CFAR")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-090", "H_C", "Sector A remains open")),
    "sector": (REPO / "theory/sectors/A.md", ("GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER", "RATIONAL-FOREST-DISJOINTNESS")),
    "negative_registry": (
        REPO / "negative-results/registry.md",
        (
            "NG-2026-07-25-A13-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER",
            "AUDIT-2026-07-25-A13-R089-RATIONAL-FOREST-DISJOINTNESS",
        ),
    ),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000150", "EXP-000158", "R-090")),
    "changelog": (REPO / "CHANGELOG.md", ("R-090", "unprojected Cartan")),
}


NOTE_TOKENS = (
    "Exact conservative Cartan compression",
    "Theorem 2.1 (conservative coefficient identity)",
    "The global unprojected Sobolev ledger fails",
    "Theorem 3.1 (uniform no-go for every positive exponent)",
    "current-root first Gaussian chaos",
    "Rational conditioning correction and raw endpoint sign",
    "Forest nonduplication and canonical rational target",
    "Complete packet and the remaining proof architecture",
    "Attempt and evidence map",
    "Devil's-advocate review",
    "Executable verification and no-overclaim statement",
)


PDF_TOKENS = (
    "Global unprojected Cartan",
    "conservative coefficient identity",
    "uniform no-go for every positive exponent",
    "Rational conditioning correction",
    "Forest nonduplication",
    "remaining proof architecture",
    "Attempt and evidence map",
    "Result footer",
)


TEST_ORACLES = {
    "raw_factor": Fraction(-35840, 13689),
    "shell_prefactor": Fraction(9, 10),
    "ou_integral": Fraction(1, 4),
    "conditional_outside": 2.525135276160981,
    "conditional_inside": 0.2911250947727931,
}


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
        [sys.executable, str(path)], cwd=REPO, capture_output=True, text=True,
        timeout=CHILD_TIMEOUT_SECONDS, check=False,
    )


def record_passes(record: dict[str, Any]) -> bool:
    assertions = record.get("assertions")
    names = [row.get("name") for row in assertions] if isinstance(assertions, list) else []
    return bool(
        record.get("status") == "PASS"
        and isinstance(assertions, list)
        and assertions
        and all(isinstance(row, dict) and row.get("status") == "PASS" for row in assertions)
        and len(assertions) == record.get("assertions_total") == record.get("assertions_passed")
        and len(names) == len(set(names))
    )


def authority_passes(record: dict[str, Any]) -> bool:
    if record.get("status") == "PASS":
        assertions = record.get("assertions")
        return bool(
            assertions
            and all(row.get("status") == "PASS" for row in assertions)
            and record.get("assertions_passed") == record.get("assertions_total") == len(assertions)
        )
    if str(record.get("verdict", "")).endswith("PASS"):
        summary = record.get("summary", {})
        if summary:
            return bool(summary.get("total") and summary.get("failed") == 0 and summary.get("passed") == summary.get("total"))
        aggregate = record.get("assertion_summary", {}).get("aggregate", {})
        return bool(aggregate.get("total") and aggregate.get("passed") == aggregate.get("total"))
    return False


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else None


def assertion_actual(record: dict[str, Any], name: str) -> Any:
    for row in record.get("assertions", []):
        if row.get("name") == name:
            return row.get("actual")
    return None


def main() -> int:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    try:
        manifest = load_json(MANIFEST)
    except Exception as exc:
        manifest = {}
        failures.append(f"manifest: {exc}")

    children = (
        ("primary", PRIMARY, PRIMARY_OUTPUT, EXPECTED_PRIMARY),
        ("independent", INDEPENDENT, INDEPENDENT_OUTPUT, EXPECTED_INDEPENDENT),
    )
    records: dict[str, dict[str, Any]] = {}
    for label, script, output, expected in children:
        try:
            completed = run_child(script)
        except Exception as exc:
            completed = None
            failures.append(f"{label} execution: {exc}")
        combined = "" if completed is None else completed.stdout + completed.stderr
        marker = f"[R-090 {label}] {expected}/{expected} PASS"
        add(rows, f"{label}_exit_zero", completed is not None and completed.returncode == 0, None if completed is None else completed.returncode, 0)
        add(rows, f"{label}_marker", marker in combined, combined.strip(), marker)
        add(rows, f"{label}_result_exists", output.exists(), str(output.relative_to(REPO)), "exists")
        try:
            record = load_json(output)
        except Exception as exc:
            record = {}
            failures.append(f"{label} result: {exc}")
        records[label] = record
        add(rows, f"{label}_record_passes", record_passes(record), record.get("status"), "PASS with unique passing rows")
        add(rows, f"{label}_count", record.get("assertions_total") == expected, record.get("assertions_total"), expected)
        add(rows, f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add(rows, f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    primary = records.get("primary", {})
    independent = records.get("independent", {})
    add(rows, "primary_schema", primary.get("schema") == "tect/a13-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-primary/1.0", primary.get("schema"), "primary/1.0")
    add(rows, "independent_schema", independent.get("schema") == "tect/a13-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-independent/1.0", independent.get("schema"), "independent/1.0")

    primary_names = {row.get("name") for row in primary.get("assertions", []) if isinstance(row, dict)}
    independent_names = {row.get("name") for row in independent.get("assertions", []) if isinstance(row, dict)}
    required_primary = {
        "cartan_b_equals_gradient_c", "cartan_fourier_single_coefficient_compression",
        "cartan_fourier_trace_is_q_squared_c_squared", "cartan_conservative_shell_prefactor",
        "production_scalar_hessian_at_one", "ou_first_chaos_integral",
        "r089_switch_conditional_variance_plus_not_one", "r089_switch_unconditional_covariance_matched",
        "raw_endpoint_expectation_exact_factor", "forest_reconstruction_exact",
        "adding_lower_forest_double_counts", "full_packet_cross_nonduplication",
        "all_downstream_flags_false",
    }
    required_independent = {
        "independent_cartan_fourier_compression", "independent_cartan_trace_compression",
        "independent_power_cancellation_s_1/3", "independent_ou_integral",
        "diagonal_not_cfar_counterexample", "independent_conditional_variance_outside_not_one",
        "independent_unconditional_variance_recombined", "independent_raw_endpoint_exact_factor",
        "independent_raw_endpoint_quadrature", "independent_smooth_endpoint_converges_toward_sharp",
        "independent_forest_reconstructs_product", "independent_full_packet_polarization",
        "independent_no_overclaim",
    }
    add(rows, "primary_required_rows", required_primary.issubset(primary_names), sorted(required_primary - primary_names), [])
    add(rows, "independent_required_rows", required_independent.issubset(independent_names), sorted(required_independent - independent_names), [])

    p_cartan = primary.get("cartan", {})
    add(rows, "cartan_conservative_identity", p_cartan.get("identity") == "b=spatial-gradient(c)", p_cartan.get("identity"), "b=spatial-gradient(c)")
    add(rows, "cartan_fourier_identity", "i*q_i" in str(p_cartan.get("fourier_identity")), p_cartan.get("fourier_identity"), "i*q_i compression")
    add(rows, "cartan_lp_convention", "2^(m+1)" in str(p_cartan.get("lp_upper_support_convention")), p_cartan.get("lp_upper_support_convention"), "upper support pinned")
    add(rows, "cartan_shell_prefactor", Fraction(str(p_cartan.get("conservative_shell_prefactor_without_kappa0_over_P"))) == TEST_ORACLES["shell_prefactor"], p_cartan.get("conservative_shell_prefactor_without_kappa0_over_P"), str(TEST_ORACLES["shell_prefactor"]))
    add(rows, "cartan_global_ledger_false", p_cartan.get("global_sobolev_ledger_3_12") is False, p_cartan.get("global_sobolev_ledger_3_12"), False)
    add(rows, "cartan_cfar_not_refuted", p_cartan.get("direct_far_cfar_refuted") is False, p_cartan.get("direct_far_cfar_refuted"), False)
    add(rows, "cartan_current_root_named", "current-root" in str(p_cartan.get("obstructing_chaos")), p_cartan.get("obstructing_chaos"), "current-root")
    add(rows, "ou_integral_primary", Fraction(str(assertion_actual(primary, "ou_first_chaos_integral"))) == TEST_ORACLES["ou_integral"], assertion_actual(primary, "ou_first_chaos_integral"), str(TEST_ORACLES["ou_integral"]))
    add(rows, "ou_integral_independent", abs(float(independent.get("ou_integral", "nan")) - float(TEST_ORACLES["ou_integral"])) < 1e-14, independent.get("ou_integral"), float(TEST_ORACLES["ou_integral"]))

    p_rational = primary.get("rational", {})
    i_rational = independent.get("raw_endpoint", {})
    p_variances = p_rational.get("conditional_variances", {})
    i_variances = independent.get("conditional_variances", {})
    add(rows, "conditional_outside_primary", abs(float(p_variances.get("event_abs_G_ge_1", float("nan"))) - TEST_ORACLES["conditional_outside"]) < 2e-14, p_variances.get("event_abs_G_ge_1"), TEST_ORACLES["conditional_outside"])
    add(rows, "conditional_inside_primary", abs(float(p_variances.get("event_abs_G_lt_1", float("nan"))) - TEST_ORACLES["conditional_inside"]) < 2e-14, p_variances.get("event_abs_G_lt_1"), TEST_ORACLES["conditional_inside"])
    add(rows, "conditional_outside_cross", abs(float(i_variances.get("event_abs_G_ge_1", "nan")) - float(p_variances.get("event_abs_G_ge_1", "nan"))) < 2e-14, [p_variances.get("event_abs_G_ge_1"), i_variances.get("event_abs_G_ge_1")], "cross match")
    add(rows, "conditional_inside_cross", abs(float(i_variances.get("event_abs_G_lt_1", "nan")) - float(p_variances.get("event_abs_G_lt_1", "nan"))) < 2e-14, [p_variances.get("event_abs_G_lt_1"), i_variances.get("event_abs_G_lt_1")], "cross match")
    p_raw_factor = Fraction(str(p_rational.get("raw_endpoint_expectation_factor_before_phi_per_c1e")))
    i_raw_factor = Fraction(str(i_rational.get("exact_factor_before_phi_per_c1e")))
    add(rows, "raw_factor_cross", p_raw_factor == i_raw_factor == TEST_ORACLES["raw_factor"], [str(p_raw_factor), str(i_raw_factor)], str(TEST_ORACLES["raw_factor"]))
    expected_normalized = float(TEST_ORACLES["raw_factor"]) * math.exp(-0.5) / math.sqrt(2 * math.pi)
    add(rows, "raw_expectation_primary", abs(float(p_rational.get("raw_endpoint_expectation_per_c1e", float("nan"))) - expected_normalized) < 2e-15, p_rational.get("raw_endpoint_expectation_per_c1e"), expected_normalized)
    add(rows, "raw_expectation_independent", abs(float(i_rational.get("quadrature_per_c1e", "nan")) - expected_normalized) < 2e-15, i_rational.get("quadrature_per_c1e"), expected_normalized)
    add(rows, "forest_not_additional", p_rational.get("lower_forest_is_additional_to_unexpanded_product") is False, p_rational.get("lower_forest_is_additional_to_unexpanded_product"), False)
    add(rows, "canonical_assembly_wording", all(token in str(p_rational.get("canonical_assembly")) for token in ("reconstructs", "R-066/R-070", "R-079", "No separate")), p_rational.get("canonical_assembly"), "nonduplicating assembly")

    for label, record in records.items():
        flags = record.get("claims_not_established", record.get("unproved", {}))
        add(rows, f"{label}_downstream_false", bool(flags) and all(value is False for value in flags.values()), flags, "all false")

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
    add(rows, "note_chain_rule", all(token in note_text for token in ("b_{A,j,i}=\\partial_i c_{A,j}", "iq_i\\widehat c", "9\\kappa_0\\over10P")), "conservative proof present", "present")
    add(rows, "note_nogo_repairs", all(token in note_text for token in ("fixed active shell", "current-root", "Gaussian convolution is injective", "antipodal", "1/4")), "hostile-audit repairs present", "present")
    add(rows, "note_scope_firewall", all(token in note_text for token in ("does not refute R-089 (3.9)", "not a torus/A1", "Tier stays T4")), "no-overclaim boundary present", "present")
    add(rows, "note_rational_exact", all(token in note_text for token in ("35840\\over13689", "0.633518209275045", "R-063", "R-079")), "rational and forest proof present", "present")
    add(rows, "note_modular_frontier", all(token in note_text for token in ("H_C", "H_N", "H_A", "not asserted to be a pairwise-logically-independent theorem")), "qualified modular frontier present", "present")

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
    add(rows, "pdf_page_range", 7 <= pages <= 20, pages, "7..20")
    add(rows, "pdf_not_encrypted", not encrypted, encrypted, False)
    add(rows, "pdf_no_forms", not has_forms, has_forms, False)
    for index, token in enumerate(PDF_TOKENS, start=1):
        add(rows, f"pdf_token_{index}", token in pdf_text, token if token in pdf_text else None, token)
    add(rows, "pdf_no_text_debris", "qquad" not in pdf_text and "�" not in pdf_text, {"qquad": pdf_text.count("qquad"), "replacement": pdf_text.count("�")}, {"qquad": 0, "replacement": 0})
    pdf_pin = manifest.get("proof_pdf", {})
    add(rows, "pdf_hash", PDF.exists() and pdf_pin.get("sha256") == digest(PDF), pdf_pin.get("sha256"), None if not PDF.exists() else digest(PDF))
    add(rows, "pdf_size", PDF.exists() and pdf_pin.get("size_bytes") == PDF.stat().st_size, pdf_pin.get("size_bytes"), None if not PDF.exists() else PDF.stat().st_size)
    add(rows, "pdf_manifest_pages", pdf_pin.get("pages") == pages and pages > 0, pdf_pin.get("pages"), pages)
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
    add(rows, "status_t4", status_record.get("tier") == "T4" and status_record.get("t7_candidate") is False, {"tier": status_record.get("tier"), "t7": status_record.get("t7_candidate")}, {"tier": "T4", "t7": False})
    add(rows, "status_open_gates", set(status_record.get("open_gates", [])) == expected_gates, status_record.get("open_gates"), sorted(expected_gates))
    expected_command = f"python {Path(__file__).resolve().relative_to(REPO).as_posix()}"
    add(rows, "status_reproduction", status_record.get("reproduction", {}).get("command") == expected_command, status_record.get("reproduction", {}).get("command"), expected_command)
    status_firewall = str(status_record.get("no_overclaim", ""))
    add(rows, "status_no_overclaim", all(token.lower() in status_firewall.lower() for token in ("R-090", "projected CFAR", "H_N", "H_A", "Sector A", "remain open")), status_record.get("no_overclaim"), "explicit open frontier")

    consequence = manifest.get("consequence", {})
    required_true = (
        "cartan_conservative_single_coefficient_trace",
        "global_unprojected_sobolev_ledger_nogo_all_positive_s",
        "r089_conditional_covariance_attribution_corrected",
        "local_raw_rational_endpoint_negative",
        "r063_forest_nonduplication_rule",
        "r079_canonical_rational_temporal_target",
    )
    for key in required_true:
        add(rows, f"manifest_true_{key}", consequence.get(key) is True, consequence.get(key), True)
    for key in ("projected_cartan_cfar", "complete_signed_near", "progressive_assembly", "uniform_overlap", "nelson", "sector_a_closure"):
        add(rows, f"manifest_false_{key}", consequence.get(key) is False, consequence.get(key), False)
    negative_ids = {
        "NG-2026-07-25-A13-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER",
        "AUDIT-2026-07-25-A13-R089-RATIONAL-FOREST-DISJOINTNESS",
    }
    add(rows, "manifest_negative_ids", set(manifest.get("negative_results", [])) == negative_ids, manifest.get("negative_results"), sorted(negative_ids))
    add(rows, "manifest_explorations", manifest.get("explorations") == [f"EXP-{number:06d}" for number in range(150, 159)], manifest.get("explorations"), "EXP-000150..EXP-000158")
    add(rows, "manifest_proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add(rows, "manifest_tier_unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add(rows, "manifest_no_overclaim", all(token in str(manifest.get("no_overclaim", "")) for token in ("unprojected", "projected CFAR", "H_N", "H_A", "Sector-A closure")), manifest.get("no_overclaim"), "explicit boundary")

    run_contract = manifest.get("run_contract", {})
    add(rows, "manifest_run_counts", run_contract.get("primary_assertions") == EXPECTED_PRIMARY and run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT, run_contract, [EXPECTED_PRIMARY, EXPECTED_INDEPENDENT])

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-integrated/1.0",
        "claim_id": CLAIM,
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
        "proved_scope": "exact conservative Cartan trace; global unprojected Sobolev-ledger no-go; rational conditional-covariance correction and local raw endpoint sign; R-063/R-079 forest nonduplication boundary",
        "open_scope": "projected Cartan CFAR H_C, complete signed NEAR H_N, progressive assembly H_A, REG, uniform OVERLAP, Nelson, interacting measure, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    if payload["pass"]:
        print(f"[R-090 integrated] {passed}/{len(rows)} PASS; aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}")
        return 0
    failed_names = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-090 integrated] {passed}/{len(rows)} PASS; failed={failed_names}; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
