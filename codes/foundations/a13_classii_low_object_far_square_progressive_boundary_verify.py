#!/usr/bin/env python3
"""Fail-closed integrated verifier for R-080."""

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
RESULT_ID = "A13-CLASSII-LOW-OBJECT-FAR-SQUARE-PROGRESSIVE-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_low_object_far_square_progressive_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_low_object_far_square_progressive_boundary_independent.py"
MANIFEST = CLAIM_DIR / "classii_low_object_far_square_progressive_boundary_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-low-object-far-square-progressive-boundary-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-low-object-far-square-progressive-boundary/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-low-object-far-square-progressive-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-low-object-far-square-progressive-boundary/result.json"
EXPECTED_PRIMARY = 51
EXPECTED_INDEPENDENT = 35
CHILD_TIMEOUT_SECONDS = 120

AUTHORITY = {
    "r066_backward_heat": {
        "manifest": CLAIM_DIR / "classii_backward_heat_martingale_square_coupled_cartan_reduction_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-23-integrated-backward-heat-martingale-square-coupled-cartan-reduction/result.json",
    },
    "r075_graph_recovery": {
        "manifest": CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-24-integrated-principal-taylor-oneform-graph-recovery/result.json",
    },
    "r078_hessian_packet": {
        "manifest": CLAIM_DIR / "classii_hessian_difference_safe_packet_doob_bracket_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-25-integrated-hessian-difference-safe-packet-doob-bracket/result.json",
    },
    "r079_full_current": {
        "manifest": CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    },
}

SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-080", RESULT_ID)),
    "negative": (
        REPO / "negative-results/registry.md",
        (
            "NG-2026-07-25-A13-TARGET-HEAT-ROOT-SHELL-GAP",
            "NG-2026-07-25-A13-NEAR-WIDTH-AND-ROOTWISE-POSITIVITY",
            "NG-2026-07-25-A13-REGULAR-GRAPH-PROGRESSIVE-REVISIT",
        ),
    ),
    "roadmap": (REPO / "ROADMAP.md", ("R-080", "FULL-PROGRESSIVE-REVISIT-EXTENSION")),
    "gates": (REPO / "claims/GATES.md", ("R-080", "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "FULL-PROGRESSIVE-REVISIT-EXTENSION")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-080", "progressive/revisit")),
    "todo": (REPO / "todo/todo.json", ("R-080", "FULL-PROGRESSIVE-REVISIT-EXTENSION")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-080", "FULL-PROGRESSIVE-REVISIT-EXTENSION")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-080", "progressive/revisit")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-080", "progressive/revisit")),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000081", "three missing inputs")),
}

NOTE_TOKENS = (
    "Theorem 3.1 (regular conditional-low absorption)",
    "Theorem 3.2 (regular complete-low absorption)",
    "Far region: exact square completion",
    "Why heat projection does not manufacture spatial gap",
    "Near region: predictable payload, hidden coefficient",
    "Progressive revisits: a separate theorem is mandatory",
    "Conditional Theorem 8.1",
    "No regular near/far production bound",
)
PDF_TOKENS = (
    "Regular low-object absorption",
    "regular conditional-low absorption",
    "exact square completion",
    "hidden coefficient",
    "Progressive revisits",
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
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=CHILD_TIMEOUT_SECONDS,
        check=False,
    )


def row_group(record: dict[str, Any]) -> list[dict[str, Any]] | None:
    for key in ("assertions", "cross_assertions", "integrated_assertions"):
        value = record.get(key)
        if isinstance(value, list) and value:
            return value
    return None


def aggregate_count(record: dict[str, Any]) -> int | None:
    for key in ("aggregate_assertions", "aggregate_assertion_count"):
        if isinstance(record.get(key), int):
            return record[key]
    summary = record.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("total"), int):
        return summary["total"]
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
        signals.append(
            isinstance(summary.get("passed"), int)
            and summary.get("passed") == summary.get("total")
            and summary.get("total", 0) > 0
            and summary.get("failed", 0) == 0
        )
    return bool(signals) and all(signals)


def normalized_pdf_text(path: Path) -> str:
    with pdfplumber.open(path) as document:
        text = "\n".join(page.extract_text() or "" for page in document.pages)
    return re.sub(r"\s+", " ", text)


def main() -> int:
    rows: list[dict[str, Any]] = []
    authority_files = [entry[key] for entry in AUTHORITY.values() for key in ("manifest", "result")]
    required = [PRIMARY, INDEPENDENT, MANIFEST, NOTE, PDF, *authority_files]
    for path in required:
        label = path.relative_to(REPO).as_posix().replace("/", "__")
        add(rows, f"exists_{label}", path.exists(), path.exists(), True)
    if not all(path.exists() for path in required):
        print("[R-080 integrated] FAIL -- missing required files")
        return 1

    manifest = load_json(MANIFEST)
    primary_process = run_child(PRIMARY)
    independent_process = run_child(INDEPENDENT)
    add(rows, "primary_exit_zero", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "independent_exit_zero", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "primary_sentinel", "51/51 PASS" in primary_process.stdout, primary_process.stdout.strip(), "contains 51/51 PASS")
    add(rows, "independent_sentinel", "35/35 PASS" in independent_process.stdout, independent_process.stdout.strip(), "contains 35/35 PASS")
    add(rows, "primary_output_exists", PRIMARY_OUTPUT.exists(), PRIMARY_OUTPUT.exists(), True)
    add(rows, "independent_output_exists", INDEPENDENT_OUTPUT.exists(), INDEPENDENT_OUTPUT.exists(), True)
    if not PRIMARY_OUTPUT.exists() or not INDEPENDENT_OUTPUT.exists():
        return 1

    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    children = (
        ("primary", primary, EXPECTED_PRIMARY, "tect/a13-low-object-far-square-progressive-boundary-primary/1.0"),
        ("independent", independent, EXPECTED_INDEPENDENT, "tect/a13-low-object-far-square-progressive-boundary-independent/1.0"),
    )
    for label, record, expected, schema in children:
        add(rows, f"{label}_schema", record.get("schema") == schema, record.get("schema"), schema)
        add(rows, f"{label}_result", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)
        add(rows, f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add(rows, f"{label}_version", record.get("source_version") == __version__, record.get("source_version"), __version__)
        add(rows, f"{label}_status", record.get("status") == "PASS", record.get("status"), "PASS")
        add(rows, f"{label}_passed", record.get("assertions_passed") == expected, record.get("assertions_passed"), expected)
        add(rows, f"{label}_total", record.get("assertions_total") == expected, record.get("assertions_total"), expected)
        child_rows = record.get("assertions", [])
        add(rows, f"{label}_row_count", len(child_rows) == expected, len(child_rows), expected)
        add(rows, f"{label}_rowwise_pass", all(row.get("status") == "PASS" for row in child_rows), sum(row.get("status") == "PASS" for row in child_rows), expected)
        no_claims = record.get("claims_not_established", {})
        add(rows, f"{label}_no_overclaim", bool(no_claims) and all(value is False for value in no_claims.values()), no_claims, "all false")
    add(rows, "independent_non_importing", "No import from the primary" in independent.get("independence", ""), independent.get("independence"), "non-importing declaration")

    for key, contract in AUTHORITY.items():
        manifest_contract = manifest.get("authority", {}).get(key, {})
        for label, path in (("manifest", contract["manifest"]), ("result", contract["result"])):
            entry = manifest_contract.get(label, {})
            relative = path.relative_to(REPO).as_posix()
            add(rows, f"authority_{key}_{label}_path", entry.get("path") == relative, entry.get("path"), relative)
            add(rows, f"authority_{key}_{label}_hash", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))
        authority_result = load_json(contract["result"])
        group = row_group(authority_result) or []
        observed = {
            "schema": authority_result.get("schema"),
            "result_id": authority_result.get("result_id"),
            "rows": len(group),
            "aggregate": aggregate_count(authority_result),
            "pass": record_passes(authority_result),
        }
        expected_contract = manifest_contract.get("contract", {})
        add(rows, f"authority_{key}_contract", observed == expected_contract, observed, expected_contract)

    sources = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": Path(__file__).resolve(), "proof_note": NOTE}
    for key, path in sources.items():
        entry = manifest.get("sources", {}).get(key, {})
        relative = path.relative_to(REPO).as_posix()
        add(rows, f"source_{key}_path", entry.get("path") == relative, entry.get("path"), relative)
        add(rows, f"source_{key}_hash", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))

    pdf_entry = manifest.get("proof_pdf", {})
    reader = PdfReader(PDF)
    fields = reader.get_fields() or {}
    add(rows, "pdf_path", pdf_entry.get("path") == PDF.relative_to(REPO).as_posix(), pdf_entry.get("path"), PDF.relative_to(REPO).as_posix())
    add(rows, "pdf_hash", pdf_entry.get("sha256") == digest(PDF), pdf_entry.get("sha256"), digest(PDF))
    add(rows, "pdf_pages", len(reader.pages) == 9 and pdf_entry.get("pages") == 9, {"actual": len(reader.pages), "manifest": pdf_entry.get("pages")}, 9)
    add(rows, "pdf_size", PDF.stat().st_size > 100_000 and pdf_entry.get("size_bytes") == PDF.stat().st_size, {"actual": PDF.stat().st_size, "manifest": pdf_entry.get("size_bytes")}, ">100000 and exact")
    add(rows, "pdf_forms", not fields and pdf_entry.get("form_check") == "PASS", {"fields": len(fields), "manifest": pdf_entry.get("form_check")}, {"fields": 0, "manifest": "PASS"})
    add(rows, "pdf_overfull", pdf_entry.get("overfull_hbox_count") == 0, pdf_entry.get("overfull_hbox_count"), 0)
    pdf_text = normalized_pdf_text(PDF)
    add(rows, "pdf_tokens", all(token in pdf_text for token in PDF_TOKENS), {token: token in pdf_text for token in PDF_TOKENS}, "all true")
    add(rows, "pdf_no_debris", all(token not in pdf_text.lower() for token in ("qquad", "undefined", "overfull")), {token: token in pdf_text.lower() for token in ("qquad", "undefined", "overfull")}, "all false")
    add(rows, "pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS" and "nine pages" in pdf_entry.get("visual_qa_note", "").lower(), pdf_entry.get("visual_qa_note"), "PASS and nine-page note")

    note_text = NOTE.read_text(encoding="utf-8")
    for index, token in enumerate(NOTE_TOKENS, 1):
        add(rows, f"note_token_{index}", token in note_text, token in note_text, True)
    add(rows, "note_no_bare_qquad", re.search(r"(?<!\\)qquad", note_text) is None, bool(re.search(r"(?<!\\)qquad", note_text)), False)
    add(rows, "note_no_overfull_marker", "Overfull \\hbox" not in note_text, "Overfull \\hbox" in note_text, False)

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-classii-low-object-far-square-progressive-boundary/1.0", manifest.get("schema"), "tect/a13-classii-low-object-far-square-progressive-boundary/1.0")
    add(rows, "manifest_version", manifest.get("package_version") == __version__, manifest.get("package_version"), __version__)
    add(rows, "manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add(rows, "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_t4_open", "T4" in manifest.get("status", "") and "OPEN" in manifest.get("status", ""), manifest.get("status"), "contains T4 and OPEN")
    add(rows, "manifest_scope_no_revisit", "no-revisit" in manifest.get("scope", "").lower(), manifest.get("scope"), "contains no-revisit")
    add(rows, "manifest_progressive_gate", manifest.get("consequence", {}).get("progressive_gate") == "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION", manifest.get("consequence", {}).get("progressive_gate"), "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION")
    no_established = manifest.get("claims_not_established", {})
    add(rows, "manifest_no_overclaim", bool(no_established) and all(value is False for value in no_established.values()), no_established, "all false")
    add(rows, "manifest_negative_records", set(manifest.get("consequence", {}).get("negative_records", [])) == {
        "NG-2026-07-25-A13-TARGET-HEAT-ROOT-SHELL-GAP",
        "NG-2026-07-25-A13-NEAR-WIDTH-AND-ROOTWISE-POSITIVITY",
        "NG-2026-07-25-A13-REGULAR-GRAPH-PROGRESSIVE-REVISIT",
    }, manifest.get("consequence", {}).get("negative_records"), "exact three records")

    for label, (path, tokens) in SURFACES.items():
        surface_text = path.read_text(encoding="utf-8") if path.exists() else ""
        add(rows, f"surface_{label}", path.exists() and all(token in surface_text for token in tokens), {"exists": path.exists(), **{token: token in surface_text for token in tokens}}, "exists and all true")

    evidence_paths = manifest.get("evidence_paths", [])
    for index, relative in enumerate(evidence_paths, 1):
        path_text = relative.split("#", 1)[0]
        add(rows, f"evidence_path_{index}", (REPO / path_text).exists(), path_text, "exists")

    run_contract = manifest.get("run_contract", {})
    add(rows, "manifest_primary_count", run_contract.get("primary_assertions") == EXPECTED_PRIMARY, run_contract.get("primary_assertions"), EXPECTED_PRIMARY)
    add(rows, "manifest_independent_count", run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT, run_contract.get("independent_assertions"), EXPECTED_INDEPENDENT)
    expected_integrated = run_contract.get("integrated_assertions")
    expected_aggregate = run_contract.get("aggregate_assertions")
    add(rows, "manifest_integrated_count", isinstance(expected_integrated, int) and expected_integrated == len(rows) + 2, expected_integrated, len(rows) + 2)
    add(rows, "manifest_aggregate_count", isinstance(expected_integrated, int) and expected_aggregate == EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + expected_integrated, expected_aggregate, None if not isinstance(expected_integrated, int) else EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + expected_integrated)

    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    aggregate = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + total
    payload = {
        "schema": "tect/a13-low-object-far-square-progressive-boundary-integrated/1.0",
        "result_id": RESULT_ID,
        "claim_id": CLAIM,
        "version": __version__,
        "status": "PASS" if passed == total else "FAIL",
        "assertions_passed": passed,
        "assertions_total": total,
        "aggregate_assertions": aggregate,
        "assertions": rows,
        "authority_hashes": {key: digest(contract["manifest"]) for key, contract in AUTHORITY.items()},
        "authority_result_hashes": {key: digest(contract["result"]) for key, contract in AUTHORITY.items()},
        "source_hashes": {key: digest(path) for key, path in sources.items()},
        "manifest_sha256": digest(MANIFEST),
        "child_outputs": {
            "primary": PRIMARY_OUTPUT.relative_to(REPO).as_posix(),
            "independent": INDEPENDENT_OUTPUT.relative_to(REPO).as_posix(),
        },
        "pdf_contract": {"pages": len(reader.pages), "size_bytes": PDF.stat().st_size, "form_fields": len(fields), "visual_qa": pdf_entry.get("visual_qa")},
        "honesty_boundary": manifest.get("honesty_boundary"),
        "claims_not_established": no_established,
        "source_sha256": digest(Path(__file__).resolve()),
    }
    atomic_json(OUTPUT, payload)
    if passed == total:
        print(f"[R-080 integrated] {passed}/{total} PASS; aggregate {aggregate}/{aggregate} PASS")
    else:
        print(f"[R-080 integrated] {passed}/{total} FAIL")
        for row in rows:
            if row["status"] != "PASS":
                print(f"FAIL {row['name']}: actual={row['actual']!r} expected={row['expected']!r}")
    print(f"result: {OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
