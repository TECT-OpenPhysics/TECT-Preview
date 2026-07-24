#!/usr/bin/env python3
"""Fail-closed integrated verifier for R-081."""

from __future__ import annotations

__version__ = "1.0.2"
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
RESULT_ID = "A13-CLASSII-CARTAN-TAIL-ADAPTED-NEAR-TEMPORAL-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_cartan_tail_adapted_near_temporal_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_cartan_tail_adapted_near_temporal_reduction_independent.py"
MANIFEST = CLAIM_DIR / "classii_cartan_tail_adapted_near_temporal_reduction_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-cartan-tail-adapted-near-temporal-reduction-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-cartan-tail-adapted-near-temporal-reduction/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-cartan-tail-adapted-near-temporal-reduction/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-cartan-tail-adapted-near-temporal-reduction/result.json"
EXPECTED_PRIMARY = 60
EXPECTED_INDEPENDENT = 47
EXPECTED_PAGES = 11
CHILD_TIMEOUT_SECONDS = 120

AUTHORITY = {
    "r063_balanced_jet": (
        CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
        CLAIM_DIR / "runs/2026-07-22-integrated-balanced-coefficient-jet-continuum/result.json",
    ),
    "r075_graph_recovery": (
        CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-principal-taylor-oneform-graph-recovery/result.json",
    ),
    "r079_full_current": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r080_boundary": (
        CLAIM_DIR / "classii_low_object_far_square_progressive_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-low-object-far-square-progressive-boundary/result.json",
    ),
}

SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-081", RESULT_ID)),
    "negative": (
        REPO / "negative-results/registry.md",
        (
            "NG-2026-07-25-A13-ROOTWISE-DETERMINISTIC-FAR-AND-HALF-DERIVATIVE",
            "NG-2026-07-25-A13-ABSOLUTE-CONTROL-CONTROL-PAIR-HIGH",
            "NG-2026-07-25-A13-NONLINEAR-COEFFICIENT-DJA-FACTORISATION",
            "NG-2026-07-25-A13-ONESHOT-GRAPH-PROGRESSIVE-NONDENSITY",
        ),
    ),
    "roadmap": (REPO / "ROADMAP.md", ("R-081", "root-resolved FAR", "overlap-stable")),
    "gates": (REPO / "claims/GATES.md", ("R-081", "ROOT-RESOLVED", "overlap-stable")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "R-081", "60/60", "47/47")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-081", "Cartan", "non-density")),
    "todo": (REPO / "todo/todo.json", ("R-081", "root-resolved FAR", "overlap-stable")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-081", "classii-cartan-tail-adapted-near-temporal-reduction")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-081", "Cartan", "overlap-stable")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-081", "Cartan", "progressive-dense")),
    "claim": (CLAIM_DIR / "claim.md", (RESULT_ID, "R-081", "root-resolved FAR", "overlap-stable")),
    "changelog": (REPO / "CHANGELOG.md", ("R-081", "Cartan tail")),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000082", "EXP-000089", "EXP-000090", "EXP-000091", "R-081")),
}

NOTE_TOKENS = (
    "Theorem 3.1 (production current split)",
    "Theorem 4.1 (relative-gap current tail)",
    "Fixed-coefficient injection and the half-derivative endpoint",
    "NEAR: vector budget and nonlinear factorisation boundary",
    "Theorem 8.1 (strict-past temporal factorisation)",
    "Exact non-density of the one-shot graph",
    "No root-resolved FAR theorem",
)
PDF_TOKENS = (
    "Cartan current tails",
    "relative-gap current tail",
    "half-derivative endpoint",
    "explicitly factorised first-order NEAR martingale response",
    "non-density of the one-shot graph",
    "Result footer",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})


def run_child(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(path)], cwd=REPO, capture_output=True, text=True, timeout=CHILD_TIMEOUT_SECONDS, check=False)


def row_group(record: dict[str, Any]) -> list[dict[str, Any]] | None:
    for key in ("assertions", "cross_assertions", "integrated_assertions"):
        value = record.get(key)
        if isinstance(value, list) and value:
            return value
    return None


def record_passes(record: dict[str, Any]) -> bool:
    if isinstance(record.get("failures"), list) and record["failures"]:
        return False
    if record.get("failure_stage") is not None:
        return False
    rows = row_group(record)
    if not rows or not all(isinstance(row, dict) and row.get("status") == "PASS" for row in rows):
        return False
    signals: list[bool] = []
    if "status" in record:
        signals.append(record.get("status") == "PASS")
    if "pass" in record:
        signals.append(record.get("pass") is True)
    if "verdict" in record:
        verdict = record.get("verdict")
        signals.append(verdict == "PASS" or (isinstance(verdict, str) and verdict.endswith("-PASS")))
    summary = record.get("summary")
    if isinstance(summary, dict) and any(key in summary for key in ("passed", "total", "failed")):
        signals.append(isinstance(summary.get("passed"), int) and summary.get("passed") == summary.get("total") and summary.get("total", 0) > 0 and summary.get("failed", 0) == 0)
    return bool(signals) and all(signals)


def normalized_pdf_text(path: Path) -> str:
    with pdfplumber.open(path) as document:
        text = "\n".join(page.extract_text() or "" for page in document.pages)
    return re.sub(r"\s+", " ", text)


def main() -> int:
    rows: list[dict[str, Any]] = []
    authority_files = [path for pair in AUTHORITY.values() for path in pair]
    required = [PRIMARY, INDEPENDENT, Path(__file__), MANIFEST, NOTE, PDF, *authority_files]
    for path in required:
        add(rows, f"exists_{path.relative_to(REPO).as_posix().replace('/', '__')}", path.exists(), path.exists(), True)
    if not all(path.exists() for path in required):
        print("[R-081 integrated] FAIL -- missing required files")
        return 1

    manifest = load_json(MANIFEST)
    primary_process = run_child(PRIMARY)
    independent_process = run_child(INDEPENDENT)
    add(rows, "primary_exit_zero", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "independent_exit_zero", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "primary_sentinel", "60/60 PASS" in primary_process.stdout, primary_process.stdout.strip(), "contains 60/60 PASS")
    add(rows, "independent_sentinel", "47/47 PASS" in independent_process.stdout, independent_process.stdout.strip(), "contains 47/47 PASS")
    add(rows, "primary_output_exists", PRIMARY_OUTPUT.exists(), PRIMARY_OUTPUT.exists(), True)
    add(rows, "independent_output_exists", INDEPENDENT_OUTPUT.exists(), INDEPENDENT_OUTPUT.exists(), True)
    if not PRIMARY_OUTPUT.exists() or not INDEPENDENT_OUTPUT.exists():
        return 1

    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    children = (
        ("primary", primary, EXPECTED_PRIMARY, "tect/a13-cartan-tail-adapted-near-temporal-primary/1.0"),
        ("independent", independent, EXPECTED_INDEPENDENT, "tect/a13-cartan-tail-adapted-near-temporal-independent/1.0"),
    )
    for label, record, expected, schema in children:
        add(rows, f"{label}_schema", record.get("schema") == schema, record.get("schema"), schema)
        add(rows, f"{label}_result", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)
        add(rows, f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add(rows, f"{label}_version", record.get("source_version") == __version__, record.get("source_version"), __version__)
        add(rows, f"{label}_status", record.get("status") == "PASS", record.get("status"), "PASS")
        add(rows, f"{label}_count", record.get("assertions_total") == expected, record.get("assertions_total"), expected)
        add(rows, f"{label}_all_rows_pass", record_passes(record), record_passes(record), True)
        not_established = record.get("claims_not_established", {})
        add(rows, f"{label}_honesty_flags_present", isinstance(not_established, dict) and len(not_established) >= 9, len(not_established) if isinstance(not_established, dict) else None, ">=9")
        add(rows, f"{label}_honesty_flags_false", isinstance(not_established, dict) and all(value is False for value in not_established.values()), not_established, "all false")

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-classii-cartan-tail-adapted-near-temporal-reduction/1.0", manifest.get("schema"), "tect/a13-classii-cartan-tail-adapted-near-temporal-reduction/1.0")
    add(rows, "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add(rows, "manifest_tier_boundary", "T4" in str(manifest.get("status")) and "OPEN" in str(manifest.get("status")), manifest.get("status"), "T4 and OPEN")

    source_map = manifest.get("sources", {})
    for label, path in (("primary", PRIMARY), ("independent", INDEPENDENT), ("verifier", Path(__file__)), ("proof_note", NOTE)):
        entry = source_map.get(label, {})
        add(rows, f"manifest_{label}_path", entry.get("path") == path.relative_to(REPO).as_posix(), entry.get("path"), path.relative_to(REPO).as_posix())
        add(rows, f"manifest_{label}_hash", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))

    pdf_entry = manifest.get("proof_pdf", {})
    reader = PdfReader(PDF)
    add(rows, "pdf_pages", len(reader.pages) == EXPECTED_PAGES, len(reader.pages), EXPECTED_PAGES)
    add(rows, "pdf_no_forms", reader.get_fields() in (None, {}), reader.get_fields(), None)
    add(rows, "pdf_manifest_hash", pdf_entry.get("sha256") == digest(PDF), pdf_entry.get("sha256"), digest(PDF))
    add(rows, "pdf_manifest_size", pdf_entry.get("size_bytes") == PDF.stat().st_size, pdf_entry.get("size_bytes"), PDF.stat().st_size)
    add(rows, "pdf_manifest_pages", pdf_entry.get("pages") == EXPECTED_PAGES, pdf_entry.get("pages"), EXPECTED_PAGES)
    add(rows, "pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS", pdf_entry.get("visual_qa"), "PASS")
    pdf_text = normalized_pdf_text(PDF)
    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        add(rows, f"note_token_{hashlib.sha1(token.encode()).hexdigest()[:10]}", token in note_text, token, "present")
    for token in PDF_TOKENS:
        add(rows, f"pdf_token_{hashlib.sha1(token.encode()).hexdigest()[:10]}", token in pdf_text, token, "present")
    add(rows, "pdf_no_literal_qquad", "qquad" not in pdf_text and "le3" not in pdf_text, ["qquad" in pdf_text, "le3" in pdf_text], [False, False])

    authority_manifest = manifest.get("authority", {})
    for label, (manifest_path, result_path) in AUTHORITY.items():
        contract = authority_manifest.get(label, {})
        add(rows, f"authority_{label}_manifest_hash", contract.get("manifest", {}).get("sha256") == digest(manifest_path), contract.get("manifest", {}).get("sha256"), digest(manifest_path))
        add(rows, f"authority_{label}_result_hash", contract.get("result", {}).get("sha256") == digest(result_path), contract.get("result", {}).get("sha256"), digest(result_path))
        authority_result = load_json(result_path)
        add(rows, f"authority_{label}_passes", record_passes(authority_result), record_passes(authority_result), True)

    for label, (path, tokens) in SURFACES.items():
        exists = path.exists()
        add(rows, f"surface_{label}_exists", exists, exists, True)
        content = path.read_text(encoding="utf-8") if exists else ""
        for token in tokens:
            add(rows, f"surface_{label}_{hashlib.sha1(token.encode()).hexdigest()[:10]}", token in content, token, "present")

    claims_not_established = manifest.get("claims_not_established", {})
    add(rows, "manifest_honesty_flags_present", isinstance(claims_not_established, dict) and len(claims_not_established) >= 11, len(claims_not_established) if isinstance(claims_not_established, dict) else None, ">=11")
    add(rows, "manifest_honesty_flags_false", isinstance(claims_not_established, dict) and all(value is False for value in claims_not_established.values()), claims_not_established, "all false")
    honesty = str(manifest.get("honesty_boundary", ""))
    for token in ("root-resolved FAR", "adapted NEAR", "overlap-stable", "one-use", "Nelson", "Sector-A"):
        add(rows, f"honesty_{token.replace(' ', '_')}", token in honesty, token, "present")

    run_contract = manifest.get("run_contract", {})
    add(rows, "run_contract_primary_count", run_contract.get("primary_assertions") == EXPECTED_PRIMARY, run_contract.get("primary_assertions"), EXPECTED_PRIMARY)
    add(rows, "run_contract_independent_count", run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT, run_contract.get("independent_assertions"), EXPECTED_INDEPENDENT)
    prospective_integrated = len(rows) + 2
    prospective_aggregate = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + prospective_integrated
    add(rows, "run_contract_integrated_count", run_contract.get("integrated_assertions") == prospective_integrated, run_contract.get("integrated_assertions"), prospective_integrated)
    add(rows, "run_contract_aggregate_count", run_contract.get("aggregate_assertions") == prospective_aggregate, run_contract.get("aggregate_assertions"), prospective_aggregate)

    passed = sum(row["status"] == "PASS" for row in rows)
    aggregate = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + len(rows)
    payload: dict[str, Any] = {
        "schema": "tect/a13-cartan-tail-adapted-near-temporal-integrated/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "integrated_assertions": rows,
        "aggregate_assertions": aggregate,
        "child_assertions": {"primary": EXPECTED_PRIMARY, "independent": EXPECTED_INDEPENDENT},
        "manifest_sha256": digest(MANIFEST),
        "pdf_sha256": digest(PDF),
        "honesty_boundary": honesty,
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-081 integrated] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}; aggregate {aggregate}/{aggregate if passed == len(rows) else '?'}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
