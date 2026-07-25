#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-082 A13 reduction package."""

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
RESULT_ID = "A13-CLASSII-STOPPED-CURRENT-FAR-COMPLETE-CURRENT-NEAR-COORDINATE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_stopped_current_far_complete_current_near_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_stopped_current_far_complete_current_near_reduction_independent.py"
MANIFEST = CLAIM_DIR / "classii_stopped_current_far_complete_current_near_reduction_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-stopped-current-far-complete-current-near-coordinate-reduction-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-stopped-current-far-complete-current-near/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-stopped-current-far-complete-current-near/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-stopped-current-far-complete-current-near/result.json"
EXPECTED_PRIMARY = 54
EXPECTED_INDEPENDENT = 52
EXPECTED_PAGES = 12
CHILD_TIMEOUT_SECONDS = 120

AUTHORITY = {
    "r050_current": (
        REPO / "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/classii_k_composite_manifest.json",
        REPO / "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/runs/2026-07-20-integrated-k-composite/result.json",
    ),
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
    "r080_far_square": (
        CLAIM_DIR / "classii_low_object_far_square_progressive_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-low-object-far-square-progressive-boundary/result.json",
    ),
    "r081_cartan_tail": (
        CLAIM_DIR / "classii_cartan_tail_adapted_near_temporal_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-tail-adapted-near-temporal-reduction/result.json",
    ),
}

SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-082", RESULT_ID, "uncontrolled production FAR")),
    "roadmap": (REPO / "ROADMAP.md", ("R-082", "controlled CFAR", "Pauli--Fierz")),
    "gates": (REPO / "claims/GATES.md", ("R-082", "stopped-current", "heat-lifted")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "54/54", "52/52", "Sector A remains open")),
    "claim": (CLAIM_DIR / "claim.md", ("R-082", RESULT_ID, "support-refined", "Controlled FAR")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-082", "stopped-current", "Pauli--Fierz")),
    "todo": (REPO / "todo/todo.json", ("R-082", "controlled CFAR", "Sector A remains open")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-082", "C^T C", "controlled FAR")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-082", "stopped-current", "heat-lifted")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-082", "Pauli--Fierz", "Controlled CFAR")),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000092", "EXP-000100", "R-082")),
    "changelog": (REPO / "CHANGELOG.md", ("R-082", "stopped-current FAR")),
}

NOTE_TOKENS = (
    "Theorem 3.2 (FAR wedge as a stopped square)",
    "The uncontrolled FAR channel closes",
    "Lemma 6.1 (orthogonal causal Carleson summation)",
    "Theorem 7.1 (global Pauli--Fierz square)",
    "Theorem 8.1 (conditional square--trace identity)",
    "Evidence map: successes, failed routes, and reuse",
    "No controlled FAR theorem",
)
PDF_TOKENS = (
    "Stopped-current FAR",
    "stopped square",
    "support-refined R-050 tail",
    "orthogonal causal Carleson",
    "global Pauli",
    "conditional square",
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
        signals.append(verdict == "PASS" or (isinstance(verdict, str) and "PASS" in verdict and "FAIL" not in verdict))
    return bool(signals) and all(signals)


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

    for label, child_path, marker, expected_count in (
        ("primary", PRIMARY, f"[R-082 primary] {EXPECTED_PRIMARY}/{EXPECTED_PRIMARY} PASS", EXPECTED_PRIMARY),
        ("independent", INDEPENDENT, f"[R-082 independent] {EXPECTED_INDEPENDENT}/{EXPECTED_INDEPENDENT} PASS", EXPECTED_INDEPENDENT),
    ):
        try:
            completed = run_child(child_path)
        except Exception as exc:
            completed = None
            failures.append(f"{label} execution: {exc}")
        add(rows, f"{label}_child_exit_zero", completed is not None and completed.returncode == 0, None if completed is None else completed.returncode, 0)
        output_text = "" if completed is None else (completed.stdout + completed.stderr)
        add(rows, f"{label}_child_marker", marker in output_text, output_text.strip(), marker)
        result_path = PRIMARY_OUTPUT if label == "primary" else INDEPENDENT_OUTPUT
        add(rows, f"{label}_result_exists", result_path.exists(), str(result_path.relative_to(REPO)), "exists")
        try:
            record = load_json(result_path)
        except Exception as exc:
            record = {}
            failures.append(f"{label} result: {exc}")
        add(rows, f"{label}_record_passes", record_passes(record), record.get("status"), "PASS with all rows")
        add(rows, f"{label}_assertion_count", record.get("assertions_total") == expected_count, record.get("assertions_total"), expected_count)
        add(rows, f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    primary_record = load_json(PRIMARY_OUTPUT) if PRIMARY_OUTPUT.exists() else {}
    independent_record = load_json(INDEPENDENT_OUTPUT) if INDEPENDENT_OUTPUT.exists() else {}
    add(rows, "primary_schema", primary_record.get("schema") == "tect/a13-stopped-current-far-complete-current-near-primary/1.0", primary_record.get("schema"), "tect/a13-stopped-current-far-complete-current-near-primary/1.0")
    add(rows, "independent_schema", independent_record.get("schema") == "tect/a13-stopped-current-far-complete-current-near-independent/1.0", independent_record.get("schema"), "tect/a13-stopped-current-far-complete-current-near-independent/1.0")

    add(rows, "manifest_claim_id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add(rows, "manifest_result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_tier_boundary", "T4" in str(manifest.get("status")) and "OPEN" in str(manifest.get("status")), manifest.get("status"), "T4 with open gates")

    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        add(rows, f"{label}_manifest_exists", authority_manifest.exists(), str(authority_manifest.relative_to(REPO)), "exists")
        add(rows, f"{label}_result_exists", authority_result.exists(), str(authority_result.relative_to(REPO)), "exists")
        authority_pin = manifest.get("authority", {}).get(label, {})
        if authority_manifest.exists():
            add(rows, f"{label}_manifest_hash", authority_pin.get("manifest", {}).get("sha256") == digest(authority_manifest), authority_pin.get("manifest", {}).get("sha256"), digest(authority_manifest))
        else:
            add(rows, f"{label}_manifest_hash", False, None, "existing pinned file")
        if authority_result.exists():
            add(rows, f"{label}_result_hash", authority_pin.get("result", {}).get("sha256") == digest(authority_result), authority_pin.get("result", {}).get("sha256"), digest(authority_result))
            try:
                authority_record = load_json(authority_result)
            except Exception:
                authority_record = {}
            add(rows, f"{label}_result_passes", record_passes(authority_record), authority_record.get("status", authority_record.get("verdict")), "PASS")
        else:
            add(rows, f"{label}_result_hash", False, None, "existing pinned file")
            add(rows, f"{label}_result_passes", False, None, "PASS")

    source_entries = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "proof_note": NOTE,
    }
    for label, path in source_entries.items():
        pin = manifest.get("sources", {}).get(label, {})
        add(rows, f"{label}_source_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        add(rows, f"{label}_source_hash", path.exists() and pin.get("sha256") == digest(path), pin.get("sha256"), None if not path.exists() else digest(path))
        if label != "proof_note":
            add(rows, f"{label}_source_version", path.exists() and pin.get("version") == source_version(path), pin.get("version"), None if not path.exists() else source_version(path))

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    for index, token in enumerate(NOTE_TOKENS, start=1):
        add(rows, f"note_token_{index}", token in note_text, token if token in note_text else None, token)
    control_chars = [ord(char) for char in note_text if ord(char) < 32 and char not in "\t\n\r"]
    add(rows, "note_control_character_scan", not control_chars, control_chars, [])

    pdf_pin = manifest.get("proof_pdf", {})
    add(rows, "pdf_exists", PDF.exists(), str(PDF.relative_to(REPO)), "exists")
    add(rows, "pdf_hash", PDF.exists() and pdf_pin.get("sha256") == digest(PDF), pdf_pin.get("sha256"), None if not PDF.exists() else digest(PDF))
    try:
        reader = PdfReader(str(PDF))
        page_count = len(reader.pages)
        encrypted = reader.is_encrypted
        forms = bool(reader.get_fields())
    except Exception as exc:
        page_count, encrypted, forms = -1, True, True
        failures.append(f"pypdf: {exc}")
    add(rows, "pdf_page_count", page_count == EXPECTED_PAGES, page_count, EXPECTED_PAGES)
    add(rows, "pdf_not_encrypted", not encrypted, encrypted, False)
    add(rows, "pdf_has_no_forms", not forms, forms, False)
    add(rows, "pdf_manifest_visual_qa", pdf_pin.get("visual_qa") == "PASS", pdf_pin.get("visual_qa"), "PASS")
    add(rows, "pdf_manifest_overfull_zero", pdf_pin.get("overfull_hbox_count") == 0, pdf_pin.get("overfull_hbox_count"), 0)
    try:
        with pdfplumber.open(PDF) as document:
            pdf_text = "\n".join(page.extract_text() or "" for page in document.pages)
    except Exception as exc:
        pdf_text = ""
        failures.append(f"pdfplumber: {exc}")
    for index, token in enumerate(PDF_TOKENS, start=1):
        add(rows, f"pdf_token_{index}", token.lower() in pdf_text.lower(), token if token.lower() in pdf_text.lower() else None, token)
    add(rows, "pdf_no_literal_markup_debris", not any(token in pdf_text for token in ("qquad", "le3", "^^H", "textbackslash")), [token for token in ("qquad", "le3", "^^H", "textbackslash") if token in pdf_text], [])

    for label, (path, tokens) in SURFACES.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        add(rows, f"surface_{label}", path.exists() and all(token in text for token in tokens), [token for token in tokens if token not in text], "all tokens present")

    run_contract = manifest.get("run_contract", {})
    add(rows, "manifest_primary_count", run_contract.get("primary_assertions") == EXPECTED_PRIMARY, run_contract.get("primary_assertions"), EXPECTED_PRIMARY)
    add(rows, "manifest_independent_count", run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT, run_contract.get("independent_assertions"), EXPECTED_INDEPENDENT)

    required_false = {
        "controlled_far_stopped_current_bound",
        "production_far_complete_root_resolved_tail",
        "production_near_complete_signed_packet",
        "overlap_stable_progressive_packet_bound",
        "controlled_shell_one_use",
        "nelson_bound",
        "interacting_measure",
        "sector_a_closure",
        "tier_promotion",
    }
    for label, record in (("primary", primary_record), ("independent", independent_record), ("manifest", manifest)):
        flags = record.get("claims_not_established", {})
        add(rows, f"{label}_honesty_keys", required_false.issubset(flags), sorted(required_false - set(flags)), [])
        add(rows, f"{label}_honesty_false", all(flags.get(key) is False for key in required_false), {key: flags.get(key) for key in sorted(required_false)}, "all false")

    expected_integrated = run_contract.get("integrated_assertions")
    expected_aggregate = run_contract.get("aggregate_assertions")
    final_integrated_count = len(rows) + 2
    final_aggregate_count = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + final_integrated_count
    add(rows, "manifest_integrated_count", expected_integrated == final_integrated_count, expected_integrated, final_integrated_count)
    add(rows, "manifest_aggregate_count", expected_aggregate == final_aggregate_count, expected_aggregate, final_aggregate_count)

    passed = sum(row["status"] == "PASS" for row in rows)
    status = "PASS" if passed == len(rows) and not failures else "FAIL"
    payload: dict[str, Any] = {
        "schema": "tect/a13-stopped-current-far-complete-current-near-integrated/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": status,
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "aggregate_assertions": EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + len(rows),
        "integrated_assertions": rows,
        "failures": failures,
        "honesty_boundary": "R-082 proves the exact stopped-current representation, cutoff-uniform uncontrolled FAR, a conditional orthogonal Carleson summation lemma, the global complete-current Pauli--Fierz Gram coordinate, heat lifting, conditional covariance identity, and signed edge bookkeeping. Controlled CFAR, complete signed NEAR, overlap-stable progression, one-use, Nelson, a measure theorem, and Sector-A closure remain open.",
        "claims_not_established": {key: False for key in sorted(required_false)},
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-082 integrated] {passed}/{len(rows)} {status}; aggregate {payload['aggregate_assertions']}/{payload['aggregate_assertions']} {'PASS' if status == 'PASS' else 'FAIL'}")
    if failures:
        for failure in failures:
            print(f"  failure: {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
