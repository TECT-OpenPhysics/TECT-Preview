#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-077 causal-packet reduction."""

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
RESULT_ID = "A13-CLASSII-CAUSAL-PACKET-PAYLOAD-RESONANCE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
MANIFEST = CLAIM_DIR / "classii_causal_packet_payload_resonance_manifest.json"
PRIMARY = REPO / "codes/foundations/a13_classii_causal_packet_payload_resonance.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_causal_packet_payload_resonance_independent.py"
NOTE = CLAIM_DIR / "notes/classii-causal-packet-payload-resonance-reduction-260725-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-causal-packet-payload-resonance-reduction-260725-v1.0.pdf"
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-causal-packet-payload-resonance/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-causal-packet-payload-resonance/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-causal-packet-payload-resonance/result.json"

EXPECTED_PRIMARY_ASSERTIONS = 35
EXPECTED_INDEPENDENT_ASSERTIONS = 26
# Patched to the observed fail-closed row count after the first complete run.
EXPECTED_INTEGRATED_ASSERTIONS = 110
CHILD_TIMEOUT_SECONDS = 120

AUTHORITY_PATHS = {
    "a1_production": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "r063_balanced_jet": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r066_backward_heat": CLAIM_DIR / "classii_backward_heat_martingale_square_coupled_cartan_reduction_manifest.json",
    "r069_endpoint_lift": CLAIM_DIR / "classii_endpoint_lifted_schur_causal_grouping_reduction_manifest.json",
    "r073_off_diagonal": CLAIM_DIR / "classii_off_diagonal_telescope_critical_phase_root_reduction_manifest.json",
    "r075_invariant_current": CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
    "r076_signed_transport": CLAIM_DIR / "classii_signed_transport_besov_bregman_resonance_manifest.json",
}

SURFACE_CONTRACTS = {
    "claim": (
        CLAIM_DIR / "claim.md",
        [RESULT_ID, "complete fresh-Gaussian Doob packets", "35/35", "26/26"],
    ),
    "status": (
        CLAIM_DIR / "status.json",
        [RESULT_ID, "coefficient-dominant high-high-to-low", "R-077"],
    ),
    "roadmap": (
        REPO / "ROADMAP.md",
        [RESULT_ID, "payload-comparable", "coefficient-dominant"],
    ),
    "gates": (
        REPO / "claims/GATES.md",
        [RESULT_ID, "A13-CLASSII-COEFFICIENT-DOMINANT-HIGH-HIGH-SIGNED-PACKET"],
    ),
    "results": (
        REPO / "RESULTS-LEDGER.md",
        ["R-077", "Causal Doob packets", "fifteenth moment"],
    ),
    "negative": (
        REPO / "negative-results/registry.md",
        ["AUDIT-2026-07-25-A13-R076-ROOT-TAXONOMY", "Wick contraction", "raw monomial"],
    ),
    "todo": (
        REPO / "todo/todo.json",
        ["A13-CLASSII-COEFFICIENT-DOMINANT-HIGH-HIGH-SIGNED-PACKET", "R-077"],
    ),
    "changelog": (
        REPO / "changelog/log.jsonl",
        ["Prove A13 causal Doob-packet and payload-comparable resonance reduction", "R-077"],
    ),
    "lineage": (
        CLAIM_DIR / "lineage-narrative.md",
        [RESULT_ID, "Doob", "high-high-to-low"],
    ),
    "sector_a": (
        REPO / "theory/sectors/A.md",
        [RESULT_ID, "coefficient-dominant"],
    ),
    "proof_map": (
        REPO / "theory/proof-evidence-map.md",
        ["R-077", "payload-comparable", "coefficient-dominant"],
    ),
    "exploration": (
        REPO / "explorations/log.jsonl",
        ["R-077", "pair-high", "Doob packet"],
    ),
}

NOTE_TOKENS = [
    RESULT_ID,
    "Canonical complete-packet Doob decomposition",
    "Why the complete Wick forest must stay inside the packet",
    "Payload-comparable resonance theorem",
    "The exact coefficient-dominant residual",
    "AUDIT-2026-07-25-A13-R076-ROOT-TAXONOMY",
    "Devil's-advocate review",
    "Result footer",
]

PDF_TOKENS = [
    "CAUSAL-PACKET-PAYLOAD-RESONANCE",
    "Canonical complete-packet Doob decomposition",
    "Payload-comparable resonance theorem",
    "coefficient-dominant residual",
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
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_child(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=CHILD_TIMEOUT_SECONDS,
        check=False,
    )


def normalized_pdf_text(path: Path) -> str:
    with pdfplumber.open(path) as document:
        text = "\n".join(page.extract_text() or "" for page in document.pages)
    replacements = {"ﬃ": "ffi", "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "–": "-", "—": "-"}
    for source, target in replacements.items():
        text = text.replace(source, target)
    return re.sub(r"\s+", " ", text)


def manifest_hash(manifest: dict[str, Any], group: str, key: str) -> str | None:
    entry = manifest.get(group, {}).get(key, {})
    return entry.get("sha256") if isinstance(entry, dict) else None


def run() -> int:
    rows: list[dict[str, Any]] = []
    required = [MANIFEST, PRIMARY, INDEPENDENT, NOTE, PDF, *AUTHORITY_PATHS.values()]
    for path in required:
        add(rows, f"exists_{path.name}", path.exists(), path.exists(), True)
    if not all(path.exists() for path in required):
        passed = sum(row["status"] == "PASS" for row in rows)
        print(f"[R-077 integrated] {passed}/{len(rows)} FAIL -- missing required files")
        return 1

    manifest = load_json(MANIFEST)
    primary_process = run_child(PRIMARY)
    independent_process = run_child(INDEPENDENT)
    add(rows, "primary_exit_zero", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "independent_exit_zero", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "primary_sentinel", "35/35 PASS" in primary_process.stdout, primary_process.stdout.strip(), "contains 35/35 PASS")
    add(rows, "independent_sentinel", "26/26 PASS" in independent_process.stdout, independent_process.stdout.strip(), "contains 26/26 PASS")
    add(rows, "primary_output_exists", PRIMARY_OUTPUT.exists(), PRIMARY_OUTPUT.exists(), True)
    add(rows, "independent_output_exists", INDEPENDENT_OUTPUT.exists(), INDEPENDENT_OUTPUT.exists(), True)
    if not PRIMARY_OUTPUT.exists() or not INDEPENDENT_OUTPUT.exists():
        passed = sum(row["status"] == "PASS" for row in rows)
        print(f"[R-077 integrated] {passed}/{len(rows)} FAIL -- child output missing")
        return 1

    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    add(rows, "primary_schema", primary.get("schema") == "tect/a13-causal-packet-payload-primary/1.0", primary.get("schema"), "tect/a13-causal-packet-payload-primary/1.0")
    add(rows, "independent_schema", independent.get("schema") == "tect/a13-causal-packet-payload-independent/1.0", independent.get("schema"), "tect/a13-causal-packet-payload-independent/1.0")
    for label, payload, expected in (
        ("primary", primary, EXPECTED_PRIMARY_ASSERTIONS),
        ("independent", independent, EXPECTED_INDEPENDENT_ASSERTIONS),
    ):
        add(rows, f"{label}_status", payload.get("status") == "PASS", payload.get("status"), "PASS")
        add(rows, f"{label}_assertions_passed", payload.get("assertions_passed") == expected, payload.get("assertions_passed"), expected)
        add(rows, f"{label}_assertions_total", payload.get("assertions_total") == expected, payload.get("assertions_total"), expected)
        add(rows, f"{label}_all_rows_pass", all(row.get("status") == "PASS" for row in payload.get("assertions", [])), sum(row.get("status") == "PASS" for row in payload.get("assertions", [])), expected)

    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    forbidden_import = re.search(r"(?:from|import)\s+a13_classii_causal_packet_payload_resonance(?:\s|$)", independent_source)
    add(rows, "independent_does_not_import_primary", forbidden_import is None and independent.get("imports_primary") is False, {"source_import": bool(forbidden_import), "reported": independent.get("imports_primary")}, {"source_import": False, "reported": False})

    primary_ledger = primary.get("ledger", {})
    independent_ledger = independent.get("ledger", {})
    cross_fields = {
        "s": ("s", "s"),
        "x_power": ("x_power", "h2_power"),
        "y_power": ("y_power", "l6_power"),
        "slack": ("slack", "remainder"),
        "moment": ("moment", "moment"),
        "pair_theta": ("pair_theta", "pair_theta"),
        "pair_x_power": ("pair_x_power", "pair_h2"),
        "pair_y_power": ("pair_y_power", "pair_l6"),
        "pair_slack": ("pair_slack", "pair_remainder"),
        "pair_moment": ("pair_moment", "pair_moment"),
    }
    for label, (primary_key, independent_key) in cross_fields.items():
        actual = (primary_ledger.get(primary_key), independent_ledger.get(independent_key))
        add(rows, f"cross_{label}", actual[0] == actual[1], actual, "equal")

    for key in (
        "phi1_decomposition",
        "phi2_decomposition",
        "fresh_11_center",
        "fresh_21_center",
        "fresh_22_center",
        "baseline1_heat_error",
        "baseline2_heat_error",
        "total_fresh_expectation",
        "total_tower_error",
    ):
        actual = primary.get("doob", {}).get(key)
        add(rows, f"primary_doob_{key}", actual == "0", actual, "0")
    add(rows, "primary_forest_p3_p1", primary.get("forest", {}).get("p3_p1_error") == "0", primary.get("forest", {}).get("p3_p1_error"), "0")
    add(rows, "primary_forest_p4_lower", primary.get("forest", {}).get("p4_lower_error") == "0", primary.get("forest", {}).get("p4_lower_error"), "0")
    add(rows, "primary_forest_p1_nonzero", primary.get("forest", {}).get("p1_nonzero") is True, primary.get("forest", {}).get("p1_nonzero"), True)
    add(rows, "primary_forest_sigma_q_nonzero", primary.get("forest", {}).get("sigma_q_nonzero") is True, primary.get("forest", {}).get("sigma_q_nonzero"), True)
    add(rows, "primary_partition_exhaustive", primary.get("geometric_partition", {}).get("assignment_errors") == 0, primary.get("geometric_partition", {}).get("assignment_errors"), 0)
    add(rows, "primary_partition_orientations", primary.get("geometric_partition", {}).get("low_count", 0) > 0 and primary.get("geometric_partition", {}).get("high_count", 0) > 0, {"low": primary.get("geometric_partition", {}).get("low_count"), "high": primary.get("geometric_partition", {}).get("high_count")}, "both positive")
    add(rows, "primary_high_high_residual", primary.get("high_high_low", {}).get("nonzero") is True, primary.get("high_high_low", {}).get("zero_mode"), "nonzero")
    add(rows, "independent_tree_center", max(abs(float(value)) for value in independent.get("doob_tree", {}).values()) < 1.0e-12, independent.get("doob_tree"), "all < 1e-12")
    add(rows, "independent_partition_exhaustive", independent.get("dyadic", {}).get("assignment_errors") == 0, independent.get("dyadic", {}).get("assignment_errors"), 0)
    add(rows, "independent_high_high_residual", abs(independent.get("high_high_low", {}).get("zero_mode_real", 0.0) - 1.0) < 1.0e-12, independent.get("high_high_low", {}), "unit zero mode")

    authority_manifest = manifest.get("authority", {})
    for key, path in AUTHORITY_PATHS.items():
        entry = authority_manifest.get(key, {})
        add(rows, f"authority_path_{key}", entry.get("path") == path.relative_to(REPO).as_posix(), entry.get("path"), path.relative_to(REPO).as_posix())
        add(rows, f"authority_hash_{key}", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))

    sources = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "proof_note": NOTE,
    }
    for key, path in sources.items():
        entry = manifest.get("sources", {}).get(key, {})
        add(rows, f"source_path_{key}", entry.get("path") == path.relative_to(REPO).as_posix(), entry.get("path"), path.relative_to(REPO).as_posix())
        add(rows, f"source_hash_{key}", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))

    pdf_entry = manifest.get("proof_pdf", {})
    add(rows, "pdf_manifest_path", pdf_entry.get("path") == PDF.relative_to(REPO).as_posix(), pdf_entry.get("path"), PDF.relative_to(REPO).as_posix())
    add(rows, "pdf_manifest_hash", pdf_entry.get("sha256") == digest(PDF), pdf_entry.get("sha256"), digest(PDF))
    reader = PdfReader(PDF)
    add(rows, "pdf_page_count", len(reader.pages) == 8 and pdf_entry.get("pages") == 8, {"actual": len(reader.pages), "manifest": pdf_entry.get("pages")}, 8)
    add(rows, "pdf_size", PDF.stat().st_size > 90_000 and pdf_entry.get("size_bytes") == PDF.stat().st_size, {"actual": PDF.stat().st_size, "manifest": pdf_entry.get("size_bytes")}, ">90000 and exact manifest")
    add(rows, "pdf_form_none", not (reader.get_fields() or {}) and pdf_entry.get("form_check") == "PASS", {"fields": len(reader.get_fields() or {}), "manifest": pdf_entry.get("form_check")}, {"fields": 0, "manifest": "PASS"})
    pdf_text = normalized_pdf_text(PDF)
    add(rows, "pdf_required_tokens", all(token in pdf_text for token in PDF_TOKENS), {token: token in pdf_text for token in PDF_TOKENS}, "all true")
    add(rows, "pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS" and "eight pages" in pdf_entry.get("visual_qa_note", "").lower(), {"status": pdf_entry.get("visual_qa"), "note": pdf_entry.get("visual_qa_note")}, "PASS and eight-page note")

    note_text = NOTE.read_text(encoding="utf-8")
    add(rows, "note_required_tokens", all(token in note_text for token in NOTE_TOKENS), {token: token in note_text for token in NOTE_TOKENS}, "all true")
    add(rows, "note_no_overfull_marker", "Overfull \\hbox" not in note_text, "Overfull \\hbox" in note_text, False)

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-classii-causal-packet-payload-resonance-reduction/1.0", manifest.get("schema"), "tect/a13-classii-causal-packet-payload-resonance-reduction/1.0")
    add(rows, "manifest_version", manifest.get("package_version") == __version__, manifest.get("package_version"), __version__)
    add(rows, "manifest_result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_tier_boundary", "T4" in manifest.get("status", "") and "OPEN" in manifest.get("status", ""), manifest.get("status"), "contains T4 and OPEN")
    not_established = manifest.get("claims_not_established", {})
    add(rows, "manifest_no_overclaim_flags", bool(not_established) and all(value is False for value in not_established.values()), not_established, "all false")
    add(rows, "manifest_successor", manifest.get("consequence", {}).get("next_subgate") == "A13-CLASSII-COEFFICIENT-DOMINANT-HIGH-HIGH-SIGNED-PACKET", manifest.get("consequence", {}).get("next_subgate"), "A13-CLASSII-COEFFICIENT-DOMINANT-HIGH-HIGH-SIGNED-PACKET")
    run_contract = manifest.get("run_contract", {})
    add(rows, "manifest_primary_count", run_contract.get("primary_assertions") == EXPECTED_PRIMARY_ASSERTIONS, run_contract.get("primary_assertions"), EXPECTED_PRIMARY_ASSERTIONS)
    add(rows, "manifest_independent_count", run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT_ASSERTIONS, run_contract.get("independent_assertions"), EXPECTED_INDEPENDENT_ASSERTIONS)
    if EXPECTED_INTEGRATED_ASSERTIONS:
        add(rows, "manifest_integrated_count", run_contract.get("integrated_assertions") == EXPECTED_INTEGRATED_ASSERTIONS, run_contract.get("integrated_assertions"), EXPECTED_INTEGRATED_ASSERTIONS)

    for label, (path, tokens) in SURFACE_CONTRACTS.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        add(rows, f"surface_{label}", path.exists() and all(token in text for token in tokens), {"exists": path.exists(), **{token: token in text for token in tokens}}, "exists and all true")

    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    aggregate = EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS + total
    payload = {
        "schema": "tect/a13-causal-packet-payload-integrated/1.0",
        "result_id": RESULT_ID,
        "version": __version__,
        "status": "PASS" if passed == total else "FAIL",
        "assertions_passed": passed,
        "assertions_total": total,
        "aggregate_assertions": aggregate,
        "assertions": rows,
        "authority_hashes": {key: digest(path) for key, path in AUTHORITY_PATHS.items()},
        "source_hashes": {key: digest(path) for key, path in sources.items()},
        "manifest_sha256": digest(MANIFEST),
        "child_runs": {"primary": primary, "independent": independent},
        "child_outputs": {
            "primary": PRIMARY_OUTPUT.relative_to(REPO).as_posix(),
            "independent": INDEPENDENT_OUTPUT.relative_to(REPO).as_posix(),
        },
        "pdf_contract": {
            "pages": len(reader.pages),
            "size_bytes": PDF.stat().st_size,
            "form_fields": len(reader.get_fields() or {}),
            "visual_qa": pdf_entry.get("visual_qa"),
        },
        "honesty_boundary": manifest.get("honesty_boundary"),
        "source_sha256": digest(Path(__file__).resolve()),
    }
    atomic_json(OUTPUT, payload)
    if passed == total:
        print(f"[R-077 integrated] {passed}/{total} PASS; aggregate {aggregate}/{aggregate} PASS")
    else:
        print(f"[R-077 integrated] {passed}/{total} FAIL; aggregate {passed + EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS}/{aggregate}")
        for row in rows:
            if row["status"] != "PASS":
                print(f"FAIL {row['name']}: actual={row['actual']!r} expected={row['expected']!r}")
    print(f"result: {OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if passed == total and (not EXPECTED_INTEGRATED_ASSERTIONS or total == EXPECTED_INTEGRATED_ASSERTIONS) else 1


if __name__ == "__main__":
    raise SystemExit(run())
