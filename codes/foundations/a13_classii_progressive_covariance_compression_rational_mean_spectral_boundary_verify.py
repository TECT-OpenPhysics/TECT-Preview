#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-089 A13 package."""

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
RESULT_ID = "A13-CLASSII-PROGRESSIVE-COVARIANCE-COMPRESSION-RATIONAL-MEAN-SPECTRAL-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_progressive_covariance_compression_rational_mean_spectral_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_progressive_covariance_compression_rational_mean_spectral_boundary_independent.py"
MANIFEST = CLAIM_DIR / "classii_progressive_covariance_compression_rational_mean_spectral_boundary_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-progressive-covariance-compression-rational-mean-spectral-boundary-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-progressive-covariance-compression-rational-mean-spectral-boundary/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-progressive-covariance-compression-rational-mean-spectral-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-progressive-covariance-compression-rational-mean-spectral-boundary/result.json"
EXPECTED_PRIMARY = 56
EXPECTED_INDEPENDENT = 44
CHILD_TIMEOUT_SECONDS = 120


AUTHORITY = {
    "a8_cm_symbol": (
        REPO / "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/classii_decoupled_nelson_manifest.json",
        REPO / "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/runs/2026-07-20-integrated-decoupled-nelson/result.json",
    ),
    "r087_core": (
        CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json",
    ),
    "r088_reduction": (
        CLAIM_DIR / "classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-direct-root-cartan-schur-sequential-secant-rational-conditional-trace/result.json",
    ),
}


SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-089", RESULT_ID, "Sector A remains open")),
    "roadmap": (REPO / "ROADMAP.md", ("R-089", "coefficient-tail", "same-root", "OVERLAP")),
    "gates": (REPO / "claims/GATES.md", ("R-089", "progressive covariance", "same-root")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "R-089", "Sector A remains open")),
    "claim": (CLAIM_DIR / "claim.md", ("R-089", RESULT_ID, "mean-spectral")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-089", "Progressive covariance", "R-090")),
    "todo": (REPO / "todo/todo.json", ("R-089", "coefficient-tail", "Sector A remains open")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-089", "coefficient-tail", "OVERLAP")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-089", "progressive covariance", "Sector A remains open")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-089", "coefficient-tail", "Sector A remains open")),
    "sector": (REPO / "theory/sectors/A.md", ("RATIONAL-ETA-MEAN-SPECTRAL-CLOSURE",)),
    "negative_registry": (
        REPO / "negative-results/registry.md",
        (
            "AUDIT-2026-07-25-A13-R088-PROGRESSIVE-TERMINAL-CM-BRIDGE",
            "AUDIT-2026-07-25-A13-OVERLAP-NELSON-CHAIN",
            "NG-2026-07-25-A13-PURE-QUARTIC-CARTAN-HOMOGENEITY",
            "NG-2026-07-25-A13-RATIONAL-ETA-MEAN-SPECTRAL-CLOSURE",
        ),
    ),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000141", "EXP-000149", "R-089")),
    "changelog": (REPO / "CHANGELOG.md", ("R-089", "progressive covariance compression")),
}


NOTE_TOKENS = (
    "Global progressive covariance compression",
    "Theorem 2.1 (pathwise global contraction)",
    "Hilbert martingale and spatial ledgers",
    "General progressive quartic terminal bridge",
    "Direct integrated Cartan Fourier trace",
    "Theorem 3.1 (exact trace and two-tail bound)",
    "A subcritical quartic route and its exact boundary",
    "Exact no-go for a pure homogeneous quartic bridge",
    "Rational Taylor-coordinate normal form",
    "Theorem 5.1 (mean-spectral criterion)",
    "Production scalar obstruction",
    "OVERLAP--Nelson equivalence and corrected order",
    "Attempt and evidence map",
    "Devil's-advocate review",
    "Executable verification and no-overclaim statement",
)


PDF_TOKENS = (
    "Progressive covariance compression",
    "pathwise global contraction",
    "Direct integrated Cartan Fourier trace",
    "exact trace and two-tail bound",
    "pure homogeneous quartic bridge",
    "Rational Taylor-coordinate normal form",
    "mean-spectral criterion",
    "Nelson equivalence",
    "Attempt and evidence map",
    "Result footer",
)


REQUIRED_FALSE = (
    "nonlinear_cartan_coefficient_tail_energy",
    "complete_same_root_rational_packet",
    "complete_regular_packet_lower_bound",
    "uniform_overlap_bound",
    "nelson_bound",
    "interacting_measure",
    "sector_a_closure",
    "tier_promotion",
)


# Independently readable verifier oracles, never inputs to the child programs.
TEST_ORACLES = {
    "harmonic_32": 1.6847655411296273e-11,
    "harmonic_energy": 1.4532786834318367e-19,
    "bridge_constant": 134.87478132717905,
    "adapted_factor": float(Fraction(-688, 13689)),
    "scalar_remainder": float(Fraction(-1, 432)),
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
    if record.get("status") == "PASS" and record.get("pass") is True:
        assertions = record.get("assertions")
        return bool(assertions and all(row.get("status") == "PASS" for row in assertions))
    if str(record.get("verdict", "")).endswith("PASS"):
        summary = record.get("assertion_summary", {}).get("aggregate", {})
        return summary.get("passed") == summary.get("total") and bool(summary.get("total"))
    return False


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else None


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
        marker = f"[R-089 {label}] {expected}/{expected} PASS"
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
    add(rows, "primary_schema", primary.get("schema") == "tect/a13-progressive-covariance-compression-rational-mean-spectral-boundary-primary/1.0", primary.get("schema"), "primary/1.0")
    add(rows, "independent_schema", independent.get("schema") == "tect/a13-progressive-covariance-compression-rational-mean-spectral-boundary-independent/1.0", independent.get("schema"), "independent/1.0")

    primary_names = {row.get("name") for row in primary.get("assertions", []) if isinstance(row, dict)}
    independent_names = {row.get("name") for row in independent.get("assertions", []) if isinstance(row, dict)}
    required_primary = {
        "global_covariance_identity_exact", "global_douglas_exact", "martingale_parseval_fixture",
        "cartan_fourier_trace_identity_fixture", "cartan_scalar_harmonic_32_exact_positive",
        "conditional_taylor_coordinate_identity", "production_scalar_remainder_negative",
        "adapted_covariance_defect_exact_factor", "all_downstream_flags_false",
    }
    required_independent = {
        "independent_repeat_no_multiplicity", "independent_martingale_parseval",
        "independent_cartan_fourier_trace", "independent_harmonic_32_match",
        "independent_conditional_identity_random", "independent_eta_cannot_repair_negative_L",
        "independent_adapted_same_root_negative", "independent_downstream_false",
    }
    add(rows, "primary_required_rows", required_primary.issubset(primary_names), sorted(required_primary - primary_names), [])
    add(rows, "independent_required_rows", required_independent.issubset(independent_names), sorted(required_independent - independent_names), [])

    compression = primary.get("progressive_compression", {})
    add(rows, "compression_operator_identity", compression.get("operator_identity") == "T T^*=C", compression.get("operator_identity"), "T T^*=C")
    add(rows, "compression_terminal_progressive", compression.get("terminal_quartic_bridge_general_progressive") is True, compression.get("terminal_quartic_bridge_general_progressive"), True)
    add(rows, "compression_packet_not_closed", compression.get("complete_packet_overlap") is False, compression.get("complete_packet_overlap"), False)
    primary_ratios = [float(value) for value in compression.get("random_compression_ratios", [])]
    independent_ratios = [float(value) for value in independent.get("compression_ratios", [])]
    add(rows, "primary_compression_ratios", len(primary_ratios) == 3 and max(primary_ratios, default=2.0) <= 1.0 + 1e-12, primary_ratios, "three ratios <=1")
    add(rows, "independent_compression_ratios", len(independent_ratios) == 4 and max(independent_ratios, default=2.0) <= 1.0 + 1e-12, independent_ratios, "four ratios <=1")
    polar_residuals = [abs(float(value)) for value in independent.get("polar_residuals", [])]
    add(rows, "independent_polar_residuals", len(polar_residuals) == 4 and max(polar_residuals, default=1.0) < 2e-11, polar_residuals, "four residuals <2e-11")
    add(rows, "repeat_fixture_saturates", abs(float(compression.get("revisit_fixture_ratio", -1)) - 1.0) < 1e-14, compression.get("revisit_fixture_ratio"), 1.0)

    core = primary.get("core_equivalence", {})
    add(rows, "core_q", core.get("q") == "10/9", core.get("q"), "10/9")
    add(rows, "core_energy", core.get("energy_coefficient") == "9/20", core.get("energy_coefficient"), "9/20")
    add(rows, "core_statement", "iff" in str(core.get("statement")) and "Nelson" in str(core.get("statement")), core.get("statement"), "OVERLAP iff Nelson")

    p_cartan = primary.get("cartan", {})
    i_cartan = independent.get("cartan", {})
    p_harmonic = float(p_cartan.get("harmonic_32_decimal", float("nan")))
    i_harmonic = float(i_cartan.get("harmonic_32", "nan"))
    p_energy = float(p_cartan.get("harmonic_32_energy_decimal", float("nan")))
    i_energy = float(i_cartan.get("harmonic_energy", "nan"))
    p_bridge = float(p_cartan.get("bridge_direct_schur_constant", float("nan")))
    add(rows, "cartan_harmonic_cross", abs(p_harmonic - i_harmonic) < 1e-24 and abs(p_harmonic - TEST_ORACLES["harmonic_32"]) < 1e-24, [p_harmonic, i_harmonic], TEST_ORACLES["harmonic_32"])
    add(rows, "cartan_energy_cross", abs(p_energy - i_energy) < 1e-31 and abs(p_energy - TEST_ORACLES["harmonic_energy"]) < 1e-31, [p_energy, i_energy], TEST_ORACLES["harmonic_energy"])
    add(rows, "cartan_bridge_constant", abs(p_bridge - TEST_ORACLES["bridge_constant"]) < 1e-11, p_bridge, TEST_ORACLES["bridge_constant"])
    add(rows, "cartan_trace_form", "lambda_p" in str(p_cartan.get("full_cross_k_fourier_trace")), p_cartan.get("full_cross_k_fourier_trace"), "full root Fourier trace")
    add(rows, "cartan_two_tail_form", "Lambda_0" in str(p_cartan.get("two_tail_reduction")) and "Lambda_1" in str(p_cartan.get("two_tail_reduction")), p_cartan.get("two_tail_reduction"), "two coefficient tails")
    add(rows, "pure_quartic_false", p_cartan.get("pure_quartic_homogeneous_bridge") is False, p_cartan.get("pure_quartic_homogeneous_bridge"), False)
    ledger = p_cartan.get("strong_quartic_ledger", {})
    for key, expected in (("x", "5/16"), ("y", "9/16"), ("slack", "1/8"), ("model_moment", "8"), ("eta_loss", "5/2"), ("zeta_loss", "9/2")):
        add(rows, f"quartic_ledger_{key}", ledger.get(key) == expected, ledger.get(key), expected)

    p_rational = primary.get("rational", {})
    i_rational = independent.get("rational", {})
    p_remainder = float(Fraction(str(p_rational.get("normalized_scalar_remainder", "0"))))
    i_remainder = float(i_rational.get("remainder_minus_half", "nan"))
    p_factor = float(Fraction(str(p_rational.get("adapted_covariance_defect_factor", "0"))))
    i_factor = float(i_rational.get("adapted_factor", "nan"))
    add(rows, "rational_coordinate_formula", "(c+mu)^T L(c+mu)" in str(p_rational.get("conditional_taylor_coordinate")), p_rational.get("conditional_taylor_coordinate"), "Taylor-coordinate diagonalisation")
    add(rows, "rational_spectral_iff", p_rational.get("covariance_matched_universal_nonnegative_iff") == "L psd and B_T+2eta I psd", p_rational.get("covariance_matched_universal_nonnegative_iff"), "L psd and B_T+2eta I psd")
    add(rows, "rational_eta_no_repair", p_rational.get("eta_repairs_negative_L_mean_channel") is False, p_rational.get("eta_repairs_negative_L_mean_channel"), False)
    add(rows, "rational_full_forest_possible", p_rational.get("full_same_root_forest_may_cancel") is True, p_rational.get("full_same_root_forest_may_cancel"), True)
    add(rows, "rational_remainder_cross", abs(p_remainder - i_remainder) < 1e-15 and abs(p_remainder - TEST_ORACLES["scalar_remainder"]) < 1e-15, [p_remainder, i_remainder], TEST_ORACLES["scalar_remainder"])
    add(rows, "rational_adapted_factor_cross", abs(p_factor - i_factor) < 1e-14 and abs(p_factor - TEST_ORACLES["adapted_factor"]) < 1e-14, [p_factor, i_factor], TEST_ORACLES["adapted_factor"])
    add(rows, "rational_production_L_negative", float(Fraction(str(p_rational.get("production_L", "0")))) < 0.0, p_rational.get("production_L"), "<0")
    add(rows, "rational_independent_residual", float(i_rational.get("identity_max_residual", 1.0)) < 5e-12, i_rational.get("identity_max_residual"), "<5e-12")

    for label, record in records.items():
        open_flags = record.get("claims_not_established", {})
        add(rows, f"{label}_downstream_false", bool(open_flags) and all(value is False for value in open_flags.values()), open_flags, "all false")

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
    add(rows, "note_douglas_identity", all(token in note_text for token in ("C_J=T_JT_J^*", "C_J^{\\dagger/2}T_Jv", "range overlap", "revisit")), "global compression proof present", "present")
    add(rows, "note_martingale_ledger", "martingale differences are orthogonal" in note_text.lower() and all(token in note_text for token in ("0<s\\le2", "2^{-2sC}")), "martingale spatial ledger present", "present")
    add(rows, "note_cartan_exact_boundary", all(token in note_text for token in ("No output orthogonality", "\\mathfrak E_s", "not (3.12)")), "Cartan reduction boundary present", "present")
    add(rows, "note_rational_fixture", all(token in note_text for token in ("L/e=-1/432", "688\\over13689", "Smooth bounded even")), "production rational fixtures present", "present")
    add(rows, "note_overlap_order", all(token in note_text for token in ("complete temporal packets", "full OVERLAP", "R-087 CORE", "Nelson")), "corrected implication order present", "present")
    add(rows, "note_honesty", all(token in note_text for token in ("does not prove", "Sector-A closure", "stays T4", "No tier promotion")), "no-overclaim firewall present", "present")

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
    add(rows, "pdf_page_range", 6 <= pages <= 20, pages, "6..20")
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
    add(rows, "status_no_overclaim", all(token in str(status_record.get("no_overclaim", "")) for token in ("R-089", "coefficient-tail", "same-root", "Sector-A closure", "remain open")), status_record.get("no_overclaim"), "explicit open frontier")

    claims_not = manifest.get("claims_not_established", {})
    add(rows, "manifest_open_flags", set(REQUIRED_FALSE).issubset(claims_not) and all(value is False for value in claims_not.values()), claims_not, "all required values false")
    consequence = manifest.get("consequence", {})
    required_true = (
        "global_progressive_covariance_compression", "hilbert_martingale_one_use",
        "weighted_spatial_terminal_ledger", "general_progressive_quartic_terminal_bridge",
        "direct_integrated_cartan_fourier_trace", "rational_taylor_coordinate_identity",
        "rational_mean_spectral_criterion", "overlap_nelson_equivalence",
    )
    for key in required_true:
        add(rows, f"manifest_true_{key}", consequence.get(key) is True, consequence.get(key), True)
    add(rows, "manifest_coefficient_energy_false", consequence.get("nonlinear_cartan_coefficient_tail_energy") is False, consequence.get("nonlinear_cartan_coefficient_tail_energy"), False)
    add(rows, "manifest_rational_forest_false", consequence.get("complete_same_root_rational_packet") is False, consequence.get("complete_same_root_rational_packet"), False)
    negative_ids = {
        "AUDIT-2026-07-25-A13-R088-PROGRESSIVE-TERMINAL-CM-BRIDGE",
        "AUDIT-2026-07-25-A13-OVERLAP-NELSON-CHAIN",
        "NG-2026-07-25-A13-PURE-QUARTIC-CARTAN-HOMOGENEITY",
        "NG-2026-07-25-A13-RATIONAL-ETA-MEAN-SPECTRAL-CLOSURE",
    }
    add(rows, "manifest_negative_ids", set(manifest.get("negative_results", [])) == negative_ids, manifest.get("negative_results"), sorted(negative_ids))
    add(rows, "manifest_proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add(rows, "manifest_tier_unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add(rows, "manifest_no_overclaim", all(token in str(manifest.get("no_overclaim", "")) for token in ("coefficient-tail", "same-root", "OVERLAP", "Sector-A closure")), manifest.get("no_overclaim"), "explicit open-scope firewall")

    run_contract = manifest.get("run_contract", {})
    expected_integrated = len(rows) + 1
    expected_aggregate = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + expected_integrated
    add(
        rows, "manifest_run_counts",
        run_contract.get("primary_assertions") == EXPECTED_PRIMARY
        and run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT
        and run_contract.get("integrated_assertions") == expected_integrated
        and run_contract.get("aggregate_assertions") == expected_aggregate,
        run_contract, [EXPECTED_PRIMARY, EXPECTED_INDEPENDENT, expected_integrated, expected_aggregate],
    )

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-progressive-covariance-compression-rational-mean-spectral-boundary-integrated/1.0",
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
            "primary": EXPECTED_PRIMARY, "independent": EXPECTED_INDEPENDENT,
            "integrated": len(rows), "aggregate": EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + len(rows),
        },
        "proved_scope": "global progressive terminal covariance compression and martingale ledger; complete-cross-shell Cartan Fourier trace reduction; rational Taylor-coordinate spectral boundary; OVERLAP--Nelson equivalence",
        "open_scope": "nonlinear Cartan coefficient-tail energy, complete same-root rational heat/forest packet, REG, uniform OVERLAP, Nelson, interacting measure, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    if payload["pass"]:
        print(f"[R-089 integrated] {passed}/{len(rows)} PASS; aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}")
        return 0
    failed_names = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-089 integrated] {passed}/{len(rows)} PASS; failed={failed_names}; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
